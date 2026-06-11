from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from threatlake.kafka import create_producer
from threatlake.models import RawRecord
from threatlake.settings import ThreatLakeSettings
from threatlake.storage import LocalStorage


Fetcher = Callable[[ThreatLakeSettings], list[dict[str, Any]] | dict[str, Any]]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _infer_source_id(item: dict[str, Any], fallback: str) -> str:
    cve = item.get("cve")
    if isinstance(cve, dict) and cve.get("id"):
        return str(cve["id"])
    for key in ("source_id", "id", "cve_id", "cveId", "cveID", "ghsa_id", "ghsaId"):
        if item.get(key):
            return str(item[key])
    if item.get("cve"):
        return str(item["cve"])
    return fallback


@dataclass(slots=True)
class SourceContext:
    settings: ThreatLakeSettings
    source_name: str
    topic_name: str
    fetcher: Fetcher


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--once", action="store_true", help="Run one fetch-and-publish cycle and exit")
    parser.add_argument("--interval", type=int, default=None, help="Polling interval in seconds")
    parser.add_argument("--write-local", action="store_true", help="Write records to local storage instead of Kafka")
    parser.add_argument("--output-dir", default=None, help="Local output directory")
    return parser


def _records_from_payload(source: str, payload: list[dict[str, Any]] | dict[str, Any]) -> list[RawRecord]:
    if isinstance(payload, list):
        return [RawRecord(source=source, payload=item, source_id=_infer_source_id(item, str(idx))) for idx, item in enumerate(payload)]
    return [RawRecord(source=source, payload=payload, source_id=_infer_source_id(payload, source))]


def publish_records(
    ctx: SourceContext,
    records: Iterable[RawRecord],
    *,
    write_local: bool = False,
    output_dir: str | None = None,
) -> None:
    if write_local:
        storage = LocalStorage(output_dir or ctx.settings.local_data_dir)
        for record in records:
            storage.write_json(f"raw/{ctx.source_name}/{record.source_id or 'record'}.json", record.to_dict())
        return

    producer = create_producer(ctx.settings.kafka_bootstrap_servers)
    for record in records:
        key = record.source_id or record.payload.get("id") or utcnow()
        producer.send(ctx.topic_name, key=str(key), value=record.to_dict())
    producer.flush()


def run_source(ctx: SourceContext, *, once: bool = False, interval: int | None = None, write_local: bool = False, output_dir: str | None = None) -> None:
    poll_interval = interval or ctx.settings.poll_interval_seconds
    while True:
        payload = ctx.fetcher(ctx.settings)
        records = _records_from_payload(ctx.source_name, payload)
        publish_records(ctx, records, write_local=write_local, output_dir=output_dir)
        if once:
            return
        time.sleep(poll_interval)
