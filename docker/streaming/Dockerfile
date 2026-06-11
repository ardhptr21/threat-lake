FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PATH="/usr/lib/jvm/java-17-openjdk-amd64/bin:${PATH}"

COPY pyproject.toml README.md /app/
COPY threatlake /app/threatlake
COPY ingestion /app/ingestion
COPY streaming /app/streaming
COPY airflow /app/airflow
COPY sql /app/sql
COPY docs /app/docs

RUN pip install .

CMD ["python", "-m", "threatlake.bootstrap"]
