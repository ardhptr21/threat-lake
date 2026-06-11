from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator


PROJECT_DIR = os.getenv("THREATLAKE_PROJECT_DIR", "/opt/threatlake")

default_args = {
    "owner": "threatlake",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="threatlake_ingestion_pipeline",
    default_args=default_args,
    description="Ingest threat intelligence feeds into ThreatLake",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["threatlake", "cti", "lakehouse"],
) as dag:
    start = EmptyOperator(task_id="start")

    nvd = BashOperator(
        task_id="fetch_nvd",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.nvd.producer --once",
    )
    kev = BashOperator(
        task_id="fetch_kev",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.cisa.producer --once",
    )
    gh_adv = BashOperator(
        task_id="fetch_github_advisories",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.github_advisory.producer --once",
    )
    gh_events = BashOperator(
        task_id="fetch_github_events",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.github_events.producer --once",
    )
    exploitdb = BashOperator(
        task_id="fetch_exploitdb",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.exploitdb.producer --once",
    )

    refresh_views = BashOperator(
        task_id="refresh_lake_views",
        bash_command=f"cd {PROJECT_DIR} && echo 'ThreatLake maintenance complete'",
    )

    end = EmptyOperator(task_id="end")

    start >> [nvd, kev, gh_adv, gh_events, exploitdb] >> refresh_views >> end
