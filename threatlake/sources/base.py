from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any, Callable

from ..http import get_json, get_text


@dataclass(slots=True)
class FetchResult:
    source: str
    records: list[dict[str, Any]]
    raw: dict[str, Any] | list[dict[str, Any]]


def _sample_nvd() -> dict[str, Any]:
    return {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-2026-12345",
                    "published": "2026-01-15T12:00:00Z",
                    "descriptions": [{"lang": "en", "value": "Demo NVD vulnerability."}],
                    "metrics": {
                        "cvssMetricV31": [
                            {"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}
                        ]
                    },
                    "weaknesses": [{"description": [{"value": "CWE-79"}]}],
                    "references": [{"url": "https://example.com/nvd"}],
                }
            }
        ]
    }


def _sample_kev() -> dict[str, Any]:
    return {
        "vulnerabilities": [
            {
                "cveID": "CVE-2026-12345",
                "vendorProject": "DemoVendor",
                "product": "DemoProduct",
                "dateAdded": "2026-01-20",
                "dueDate": "2026-02-01",
                "shortDescription": "Demo KEV record.",
            }
        ]
    }


def _sample_github_advisories() -> list[dict[str, Any]]:
    return [
        {
            "ghsa_id": "GHSA-demo-1",
            "cve_id": "CVE-2026-12345",
            "published_at": "2026-01-18T00:00:00Z",
            "severity": "critical",
            "summary": "Demo advisory.",
            "exploitable": True,
            "repository": "example/repo",
        }
    ]


def _sample_github_events() -> list[dict[str, Any]]:
    return [
        {"type": "PushEvent", "cve_id": "CVE-2026-12345"},
        {"type": "ReleaseEvent", "cve_id": "CVE-2026-12345"},
    ]


def _sample_exploitdb() -> list[dict[str, Any]]:
    return [
        {
            "id": "EDB-00001",
            "cve": "CVE-2026-12345",
            "title": "Demo exploit",
            "date": "2026-01-22",
        }
    ]


def fetch_json_or_sample(
    url: str,
    sample_factory: Callable[[], Any],
    timeout: int,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    allow_sample: bool = True,
) -> Any:
    try:
        return get_json(url, timeout=timeout, headers=headers, params=params)
    except Exception:
        if not allow_sample:
            raise
        return sample_factory()


def fetch_text_or_sample(
    url: str,
    sample_factory: Callable[[], str],
    timeout: int,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    allow_sample: bool = True,
) -> str:
    try:
        return get_text(url, timeout=timeout, headers=headers, params=params)
    except Exception:
        if not allow_sample:
            raise
        return sample_factory()


def parse_csv_records(text: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def sample_nvd() -> dict[str, Any]:
    return _sample_nvd()


def sample_kev() -> dict[str, Any]:
    return _sample_kev()


def sample_github_advisories() -> list[dict[str, Any]]:
    return _sample_github_advisories()


def sample_github_events() -> list[dict[str, Any]]:
    return _sample_github_events()


def sample_exploitdb() -> list[dict[str, Any]]:
    return _sample_exploitdb()

