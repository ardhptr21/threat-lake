from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from pyspark.sql.functions import col, from_json
from pyspark.sql.types import BooleanType, DoubleType, IntegerType, StringType, StructField, StructType

from streaming.common import append_to_iceberg, build_spark, publish_to_kafka, write_local_dataset
from threatlake.settings import ThreatLakeSettings
from threatlake.transform import (
    normalize_kev,
    normalize_nvd,
    normalize_exploitdb,
    normalize_github_advisories,
    normalize_github_events,
)


BRONZE_SCHEMA = StructType(
    [
        StructField("bronze_id", StringType(), nullable=True),
        StructField("source", StringType(), nullable=False),
        StructField("source_id", StringType(), nullable=True),
        StructField("topic", StringType(), nullable=True),
        StructField("fetched_at", StringType(), nullable=True),
        StructField("bronze_at", StringType(), nullable=True),
        StructField("payload", StringType(), nullable=True),
    ]
)


def _normalize_record(source: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    if source == "nvd":
        return [item.to_dict() for item in normalize_nvd(payload)]
    if source == "cisa_kev":
        return [item.to_dict() for item in normalize_kev(payload)]
    if source == "github_advisory":
        return [item.to_dict() for item in normalize_github_advisories([payload])]
    if source == "github_events":
        return [item.to_dict() for item in normalize_github_events([payload])]
    if source == "exploitdb":
        return [item.to_dict() for item in normalize_exploitdb([payload])]
    return []


def _silver_batch(settings: ThreatLakeSettings, batch_df, batch_id: int) -> None:
    spark = batch_df.sparkSession
    rows = batch_df.select("bronze_id", "source", "source_id", "payload", "bronze_at").collect()
    normalized: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        payload = json.loads(row.payload)
        for item in _normalize_record(row.source, payload):
            item["silver_id"] = row.bronze_id
            item["bronze_id"] = row.bronze_id
            item["silver_at"] = now
            item["source"] = row.source
            item["references_json"] = json.dumps(item.get("references", []), ensure_ascii=False, default=str)
            item["raw_sources_json"] = json.dumps(item.get("raw_sources", []), ensure_ascii=False, default=str)
            item["extras_json"] = json.dumps(item.get("extras", {}), ensure_ascii=False, default=str)
            item.pop("references", None)
            item.pop("raw_sources", None)
            item.pop("extras", None)
            normalized.append(item)
    if not normalized:
        return
    append_to_iceberg(spark, f"{os.getenv('ICEBERG_CATALOG', 'threatlake')}.{os.getenv('ICEBERG_NAMESPACE', 'default')}.silver_vulnerabilities", normalized)
    if settings.demo_mode or os.getenv("THREATLAKE_WRITE_LOCAL", "").lower() in {"1", "true", "yes"}:
        write_local_dataset(settings.local_data_dir, "silver", normalized)
    else:
        publish_to_kafka(settings, settings.silver_topic, normalized)


def main() -> None:
    settings = ThreatLakeSettings.from_env()
    spark = build_spark("threatlake-silver-processor")
    stream_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.kafka_bootstrap_servers)
        .option("subscribe", settings.bronze_topic)
        .option("startingOffsets", "latest")
        .load()
        .select(col("value").cast("string").alias("payload"))
    )
    parsed = stream_df.select(from_json(col("payload"), BRONZE_SCHEMA).alias("data")).select("data.*")
    (
        parsed.writeStream.foreachBatch(lambda df, batch_id: _silver_batch(settings, df, batch_id))
        .option("checkpointLocation", os.getenv("SILVER_CHECKPOINT", "/tmp/threatlake/silver"))
        .start()
        .awaitTermination()
    )


if __name__ == "__main__":
    main()
