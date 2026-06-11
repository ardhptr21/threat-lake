from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from pyspark.sql.functions import col, current_timestamp, from_json, lit
from pyspark.sql.types import StringType, StructField, StructType

from streaming.common import append_to_iceberg, build_spark, publish_to_kafka, write_local_dataset
from threatlake.settings import ThreatLakeSettings


RAW_SCHEMA = StructType(
    [
        StructField("source", StringType(), nullable=False),
        StructField("payload", StringType(), nullable=False),
        StructField("fetched_at", StringType(), nullable=True),
        StructField("source_id", StringType(), nullable=True),
    ]
)


def _bronze_batch(settings: ThreatLakeSettings, batch_df, batch_id: int) -> None:
    spark = batch_df.sparkSession
    rows = batch_df.select("topic", "source", "payload", "fetched_at", "source_id").collect()
    records: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        payload = json.loads(row.payload)
        bronze_record = {
            "bronze_id": str(uuid.uuid4()),
            "source": row.source,
            "source_id": row.source_id,
            "topic": row.topic,
            "fetched_at": row.fetched_at,
            "bronze_at": now,
            "payload": json.dumps(payload, ensure_ascii=False, default=str),
        }
        records.append(bronze_record)
    if not records:
        return
    append_to_iceberg(spark, f"{os.getenv('ICEBERG_CATALOG', 'threatlake')}.{os.getenv('ICEBERG_NAMESPACE', 'default')}.bronze_events", records)
    if settings.demo_mode or os.getenv("THREATLAKE_WRITE_LOCAL", "").lower() in {"1", "true", "yes"}:
        write_local_dataset(settings.local_data_dir, "bronze", records)
    else:
        publish_to_kafka(settings, settings.bronze_topic, records)


def main() -> None:
    settings = ThreatLakeSettings.from_env()
    spark = build_spark("threatlake-bronze-writer")
    topics_pattern = r"^threatlake\.raw\..+$"
    stream_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.kafka_bootstrap_servers)
        .option("subscribePattern", topics_pattern)
        .option("startingOffsets", "latest")
        .load()
        .select(
            col("topic").alias("topic"),
            col("value").cast("string").alias("payload"),
        )
    )
    parsed = stream_df.select(
        col("topic"),
        from_json(col("payload"), RAW_SCHEMA).alias("data"),
    ).select(
        col("topic"),
        col("data.source").alias("source"),
        col("data.payload").alias("payload"),
        col("data.fetched_at").alias("fetched_at"),
        col("data.source_id").alias("source_id"),
    )
    (
        parsed.writeStream.foreachBatch(lambda df, batch_id: _bronze_batch(settings, df, batch_id))
        .option("checkpointLocation", os.getenv("BRONZE_CHECKPOINT", "/tmp/threatlake/bronze"))
        .start()
        .awaitTermination()
    )


if __name__ == "__main__":
    main()
