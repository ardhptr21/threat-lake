# ThreatLake

Multi-source Cyber Threat Intelligence data lakehouse for vulnerability prioritization.

## What is implemented

- NVD, CISA KEV, GitHub Advisory, GitHub Events, and ExploitDB ingestion producers.
- Bronze, Silver, and Gold streaming processors.
- Rule-based priority scoring engine.
- Airflow DAG for ingestion orchestration and lake maintenance.
- Dockerfiles and `docker-compose.yml` for the full stack.
- SQL assets for Iceberg-style bronze/silver/gold tables and derived views.

## Quick start

```bash
docker compose up -d --build
```

The stack exposes:

- Airflow UI on `http://localhost:8080`
- Superset on `http://localhost:8088`
- Trino on `http://localhost:8081`
- MinIO console on `http://localhost:9001`

## Notes

- All ingestion jobs can run in live mode against the upstream APIs or in offline demo mode with embedded sample records.
- The Spark jobs are written for Spark Structured Streaming with Kafka and Iceberg-compatible table targets.
- The repository is designed to be runnable locally with Docker Compose, but some upstream services may still need credentials for full production access.

