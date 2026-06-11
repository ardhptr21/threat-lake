from __future__ import annotations

from .base import fetch_json_or_sample, sample_kev


def fetch_kev(feed_url: str, timeout: int) -> list[dict[str, object]]:
    payload = fetch_json_or_sample(feed_url, sample_kev, timeout=timeout)
    return payload.get("vulnerabilities", payload)
