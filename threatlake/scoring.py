from __future__ import annotations

import math

from .models import NormalizedVulnerability, PrioritizedVulnerability

CVSS_WEIGHT = 4.0
KEV_WEIGHT = 30.0
EXPLOIT_WEIGHT = 20.0
ADVISORY_WEIGHT = 10.0


def classify_risk(score: float) -> str:
    if score >= 90:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def _bounded(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def score_vulnerability(vuln: NormalizedVulnerability) -> PrioritizedVulnerability:
    cvss_component = _bounded((vuln.cvss_score or 0.0) * CVSS_WEIGHT, 0.0, 40.0)
    kev_component = KEV_WEIGHT if vuln.kev_status else 0.0
    exploit_component = EXPLOIT_WEIGHT if vuln.exploit_available else 0.0
    advisory_component = _bounded(float(vuln.advisory_activity) * 2.0, 0.0, ADVISORY_WEIGHT)
    total = int(math.ceil(_bounded(cvss_component + kev_component + exploit_component + advisory_component)))
    return PrioritizedVulnerability(
        **vuln.to_dict(),
        priority_score=total,
        risk_level=classify_risk(total),
    )
