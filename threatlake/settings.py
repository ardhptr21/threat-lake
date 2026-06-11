from __future__ import annotations

from dataclasses import dataclass
import os


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value in (None, "") else value


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return int(value)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ThreatLakeSettings:
    kafka_bootstrap_servers: str = "kafka:9092"
    raw_topic_prefix: str = "threatlake.raw"
    bronze_topic: str = "threatlake.bronze"
    silver_topic: str = "threatlake.silver"
    gold_topic: str = "threatlake.gold"
    s3_endpoint_url: str = "http://minio:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "threatlake"
    s3_region: str = "ap-southeast-1"
    local_data_dir: str = "/data"
    nvd_api_url: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    kev_feed_url: str = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    github_advisory_url: str = "https://api.github.com/advisories"
    github_events_url: str = "https://api.github.com/events"
    exploitdb_feed_url: str = "https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv"
    api_timeout_seconds: int = 30
    demo_mode: bool = False
    batch_size: int = 500
    poll_interval_seconds: int = 300

    @classmethod
    def from_env(cls) -> "ThreatLakeSettings":
        return cls(
            kafka_bootstrap_servers=_env("KAFKA_BOOTSTRAP_SERVERS", cls.kafka_bootstrap_servers),
            raw_topic_prefix=_env("THREATLAKE_RAW_TOPIC_PREFIX", cls.raw_topic_prefix),
            bronze_topic=_env("THREATLAKE_BRONZE_TOPIC", cls.bronze_topic),
            silver_topic=_env("THREATLAKE_SILVER_TOPIC", cls.silver_topic),
            gold_topic=_env("THREATLAKE_GOLD_TOPIC", cls.gold_topic),
            s3_endpoint_url=_env("S3_ENDPOINT_URL", cls.s3_endpoint_url),
            s3_access_key=_env("S3_ACCESS_KEY", cls.s3_access_key),
            s3_secret_key=_env("S3_SECRET_KEY", cls.s3_secret_key),
            s3_bucket=_env("S3_BUCKET", cls.s3_bucket),
            s3_region=_env("AWS_REGION", cls.s3_region),
            local_data_dir=_env("LOCAL_DATA_DIR", cls.local_data_dir),
            nvd_api_url=_env("NVD_API_URL", cls.nvd_api_url),
            kev_feed_url=_env("KEV_FEED_URL", cls.kev_feed_url),
            github_advisory_url=_env("GITHUB_ADVISORY_URL", cls.github_advisory_url),
            github_events_url=_env("GITHUB_EVENTS_URL", cls.github_events_url),
            exploitdb_feed_url=_env("EXPLOITDB_FEED_URL", cls.exploitdb_feed_url),
            api_timeout_seconds=_env_int("API_TIMEOUT_SECONDS", cls.api_timeout_seconds),
            demo_mode=_env_bool("DEMO_MODE", cls.demo_mode),
            batch_size=_env_int("BATCH_SIZE", cls.batch_size),
            poll_interval_seconds=_env_int("POLL_INTERVAL_SECONDS", cls.poll_interval_seconds),
        )

