from __future__ import annotations

import json
from typing import Any, Iterable

from kafka import KafkaConsumer, KafkaProducer


def create_producer(bootstrap_servers: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value, ensure_ascii=False, default=str).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8") if isinstance(value, str) else value,
        linger_ms=100,
        retries=5,
        api_version=(2, 5, 0),
    )


def create_consumer(
    bootstrap_servers: str,
    topics: Iterable[str],
    group_id: str,
    auto_offset_reset: str = "latest",
) -> KafkaConsumer:
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        key_deserializer=lambda value: value.decode("utf-8") if value else None,
        api_version=(2, 5, 0),
    )
    return consumer

