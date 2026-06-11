from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from pyspark.sql import SparkSession

from threatlake.kafka import create_producer
from threatlake.settings import ThreatLakeSettings
from threatlake.storage import LocalStorage


def build_spark(app_name: str) -> SparkSession:
    builder = SparkSession.builder.appName(app_name)
    
    # Use environment variables for Spark configuration
    # Packages and configuration are handled via environment variables like:
    # SPARK_JARS_PACKAGES, PYSPARK_SUBMIT_ARGS, etc.
    
    # Force some critical configs that might be missed
    catalog = os.getenv("ICEBERG_CATALOG", "threatlake")
    builder = (
        builder
        .config("spark.sql.catalogImplementation", "hive")
        .config("spark.sql.catalog.defaultCatalog", catalog)
        .config("spark.sql.defaultCatalog", catalog)
        .config("spark.sql.session.timeZone", "UTC")
    )
    
    return builder.getOrCreate()


def json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


def publish_to_kafka(settings: ThreatLakeSettings, topic: str, records: Iterable[dict[str, Any]]) -> None:
    producer = create_producer(settings.kafka_bootstrap_servers)
    for record in records:
        key = str(record.get("cve_id") or record.get("source_id") or record.get("bronze_id") or record.get("gold_id") or record.get("id") or "")
        producer.send(topic, key=key, value=record)
    producer.flush()


def append_to_iceberg(spark, table: str, records: Iterable[dict[str, Any]]) -> None:
    items = list(records)
    if not items:
        return
    df = spark.createDataFrame(items)
    df.write.format("iceberg").mode("append").saveAsTable(table)


def write_local_dataset(base_dir: str, layer: str, records: Iterable[dict[str, Any]]) -> None:
    storage = LocalStorage(base_dir)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for record in records:
        identifier = record.get("cve_id") or record.get("source_id") or record.get("bronze_id") or record.get("gold_id") or "record"
        storage.write_json(f"{layer}/{identifier}-{stamp}.json", record)
