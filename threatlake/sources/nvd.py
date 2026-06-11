from __future__ import annotations

from .base import fetch_json_or_sample, sample_nvd


def fetch_nvd(api_url: str, timeout: int, api_key: str | None = None, results_per_page: int = 2000) -> list[dict[str, object]]:
    headers = {"User-Agent": "ThreatLake/0.1"}
    if api_key:
        headers["apiKey"] = api_key
    params = {"resultsPerPage": results_per_page}
    payload = fetch_json_or_sample(api_url, sample_nvd, timeout=timeout, headers=headers, params=params)
    return payload.get("vulnerabilities", payload)
