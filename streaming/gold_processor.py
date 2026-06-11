from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from pyspark.sql.functions import col, from_json
from pyspark.sql.types import BooleanType, DoubleType, IntegerType, StringType, StructField, StructType

from streaming.common import append_to_iceberg, build_spark, publish_to_kafka, write_local_dataset
from threatlake.models import NormalizedVulnerability
from threatlake.scoring import score_vulnerability
from threatlake.settings import ThreatLakeSettings


SILVER_SCHEMA = StructType(
    [
        StructField("cve_id", StringType(), nullable=False),
        StructField("source", StringType(), nullable=False),
        StructField("published_at", StringType(), nullable=True),
        StructField("vendor", StringType(), nullable=True),
        StructField("product", StringType(), nullable=True),
        StructField("severity", StringType(), nullable=True),
        StructField("cvss_score", DoubleType(), nullable=True),
        StructField("cwe", StringType(), nullable=True),
        StructField("summary", StringType(), nullable=True),
        StructField("kev_status", BooleanType(), nullable=True),
        StructField("exploit_available", BooleanType(), nullable=True),
        StructField("advisory_activity", IntegerType(), nullable=True),
        StructField("references_json", StringType(), nullable=True),
        StructField("raw_sources_json", StringType(), nullable=True),
        StructField("extras_json", StringType(), nullable=True),
        StructField("silver_id", StringType(), nullable=True),
        StructField("bronze_id", StringType(), nullable=True),
        StructField("silver_at", StringType(), nullable=True),
    ]
)


def _gold_batch(settings: ThreatLakeSettings, batch_df, batch_id: int) -> None:
    spark = batch_df.sparkSession
    rows = batch_df.collect()
    results: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        record = NormalizedVulnerability(
            cve_id=row.cve_id,
            source=row.source,
            published_at=row.published_at,
            vendor=row.vendor,
            product=row.product,
            severity=row.severity,
            cvss_score=row.cvss_score,
            cwe=row.cwe,
            summary=row.summary,
            kev_status=bool(row.kev_status) if row.kev_status is not None else False,
            exploit_available=bool(row.exploit_available) if row.exploit_available is not None else False,
            advisory_activity=int(row.advisory_activity or 0),
            references=json.loads(row.references_json) if row.references_json else [],
            raw_sources=json.loads(row.raw_sources_json) if row.raw_sources_json else [],
            extras=json.loads(row.extras_json) if row.extras_json else {},
        )
        scored = score_vulnerability(record).to_dict()
        scored["gold_id"] = row.cve_id
        scored["silver_id"] = row.silver_id
        scored["bronze_id"] = row.bronze_id
        scored["gold_at"] = now
        scored["references_json"] = json.dumps(scored.get("references", []), ensure_ascii=False, default=str)
        scored["raw_sources_json"] = json.dumps(scored.get("raw_sources", []), ensure_ascii=False, default=str)
        scored["extras_json"] = json.dumps(scored.get("extras", {}), ensure_ascii=False, default=str)
        scored.pop("references", None)
        scored.pop("raw_sources", None)
        scored.pop("extras", None)
        results.append(scored)
    if not results:
        return
    append_to_iceberg(spark, f"{os.getenv('ICEBERG_CATALOG', 'threatlake')}.{os.getenv('ICEBERG_NAMESPACE', 'default')}.gold_prioritized_vulnerabilities", results)
    if settings.demo_mode or os.getenv("THREATLAKE_WRITE_LOCAL", "").lower() in {"1", "true", "yes"}:
        write_local_dataset(settings.local_data_dir, "gold", results)
    else:
        publish_to_kafka(settings, settings.gold_topic, results)


def main() -> None:
    settings = ThreatLakeSettings.from_env()
    spark = build_spark("threatlake-gold-processor")
    stream_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.kafka_bootstrap_servers)
        .option("subscribe", settings.silver_topic)
        .option("startingOffsets", "latest")
        .load()
        .select(col("value").cast("string").alias("payload"))
    )
    parsed = stream_df.select(from_json(col("payload"), SILVER_SCHEMA).alias("data")).select("data.*")
    (
        parsed.writeStream.foreachBatch(lambda df, batch_id: _gold_batch(settings, df, batch_id))
        .option("checkpointLocation", os.getenv("GOLD_CHECKPOINT", "/tmp/threatlake/gold"))
        .start()
        .awaitTermination()
    )


if __name__ == "__main__":
    main()
