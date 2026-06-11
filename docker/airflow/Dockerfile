FROM apache/airflow:2.10.2-python3.12

USER root

WORKDIR /opt/threatlake

COPY pyproject.toml README.md /opt/threatlake/
COPY threatlake /opt/threatlake/threatlake
COPY ingestion /opt/threatlake/ingestion
COPY streaming /opt/threatlake/streaming
COPY airflow /opt/threatlake/airflow
COPY sql /opt/threatlake/sql
COPY docs /opt/threatlake/docs

RUN chown -R airflow:0 /opt/threatlake

USER airflow

RUN pip install --no-cache-dir /opt/threatlake

CMD ["airflow", "webserver"]
