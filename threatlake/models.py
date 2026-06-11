from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RawRecord:
    source: str
    payload: dict[str, Any]
    fetched_at: datetime = field(default_factory=utcnow)
    source_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "payload": self.payload,
            "fetched_at": self.fetched_at.isoformat(),
            "source_id": self.source_id,
        }


@dataclass(slots=True)
class NormalizedVulnerability:
    cve_id: str
    source: str
    published_at: str | None = None
    vendor: str | None = None
    product: str | None = None
    severity: str | None = None
    cvss_score: float | None = None
    cwe: str | None = None
    summary: str | None = None
    kev_status: bool = False
    exploit_available: bool = False
    advisory_activity: int = 0
    references: list[str] = field(default_factory=list)
    raw_sources: list[str] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PrioritizedVulnerability(NormalizedVulnerability):
    priority_score: int = 0
    risk_level: str = "Low"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

