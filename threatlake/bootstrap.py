from __future__ import annotations

import os
from pathlib import Path

from streaming.common import build_spark


def render_sql(path: Path, catalog: str, namespace: str) -> str:
    text = path.read_text(encoding="utf-8")
    return text.replace("${CATALOG}", catalog).replace("${NAMESPACE}", namespace)


def split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    buffer: list[str] = []
    for raw_line in sql_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        buffer.append(line)
        if line.endswith(";"):
            statement = " ".join(buffer).rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []
    trailing = " ".join(buffer).strip()
    if trailing:
        statements.append(trailing)
    return statements


def run_bootstrap(sql_dir: str | Path | None = None) -> None:
    catalog = os.getenv("ICEBERG_CATALOG", "threatlake")
    namespace = os.getenv("ICEBERG_NAMESPACE", "default")
    base_dir = Path(sql_dir or os.getenv("THREATLAKE_SQL_DIR", "/app/sql"))
    
    # Use Hadoop catalog for bootstrap to avoid Hive metastore sync issues
    from pyspark.sql import SparkSession
    s3_endpoint = os.getenv("S3_ENDPOINT_URL", "http://minio:9000").replace("http://", "").replace("https://", "")
    warehouse = os.getenv("ICEBERG_WAREHOUSE", "s3a://threatlake/warehouse")
    
    spark = (
        SparkSession.builder
        .appName("threatlake-bootstrap")
        .config("spark.jars.packages", os.getenv("SPARK_JARS_PACKAGES", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.6.1,org.apache.iceberg:iceberg-aws-bundle:1.6.1,org.apache.hadoop:hadoop-aws:3.3.4"))
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
        .config(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog}.type", "hadoop")
        .config(f"spark.sql.catalog.{catalog}.warehouse", warehouse)
        .config("spark.hadoop.fs.s3a.endpoint", f"http://{s3_endpoint}")
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("S3_ACCESS_KEY", "minioadmin"))
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("S3_SECRET_KEY", "minioadmin"))
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .getOrCreate()
    )
    for sql_file in sorted((base_dir / "bronze").glob("*.sql")):
        for statement in split_sql_statements(render_sql(sql_file, catalog, namespace)):
            spark.sql(statement)
    for sql_file in sorted((base_dir / "silver").glob("*.sql")):
        for statement in split_sql_statements(render_sql(sql_file, catalog, namespace)):
            spark.sql(statement)
    for sql_file in sorted((base_dir / "gold").glob("*.sql")):
        for statement in split_sql_statements(render_sql(sql_file, catalog, namespace)):
            spark.sql(statement)
    spark.stop()


def main() -> None:
    run_bootstrap()


if __name__ == "__main__":
    main()
