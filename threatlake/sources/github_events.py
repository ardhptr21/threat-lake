from __future__ import annotations

from typing import Any

from .base import fetch_json_or_sample, sample_github_events


def fetch_github_events(api_url: str, timeout: int, token: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ThreatLake/0.1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {"per_page": limit}
    return fetch_json_or_sample(api_url, sample_github_events, timeout=timeout, headers=headers, params=params)

