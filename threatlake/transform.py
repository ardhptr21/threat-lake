from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

from .models import NormalizedVulnerability


def _stringify(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _parse_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value).astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def normalize_nvd(raw: dict[str, Any] | list[dict[str, Any]]) -> list[NormalizedVulnerability]:
    if isinstance(raw, list):
        vulnerabilities = raw
    else:
        vulnerabilities = raw.get("vulnerabilities") or [raw]
    results: list[NormalizedVulnerability] = []
    for item in vulnerabilities:
        cve = item.get("cve") or {}
        metrics = cve.get("metrics") or {}
        cvss_score = None
        severity = None
        for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            metric_list = metrics.get(metric_key) or []
            if metric_list:
                first = metric_list[0]
                data = first.get("cvssData") or {}
                cvss_score = data.get("baseScore")
                severity = data.get("baseSeverity") or first.get("baseSeverity")
                break
        descriptions = cve.get("descriptions") or []
        summary = next((d.get("value") for d in descriptions if d.get("lang") == "en"), None)
        cwe = None
        weaknesses = cve.get("weaknesses") or []
        if weaknesses:
            first_weakness = weaknesses[0]
            descriptions_list = first_weakness.get("description") or []
            if descriptions_list:
                cwe = descriptions_list[0].get("value")
        references = [ref.get("url") for ref in cve.get("references", []) if ref.get("url")]
        cve_id = cve.get("id") or "UNKNOWN-CVE"
        results.append(
            NormalizedVulnerability(
                cve_id=cve_id,
                source="nvd",
                published_at=_parse_datetime(cve.get("published")),
                severity=_stringify(severity),
                cvss_score=float(cvss_score) if cvss_score is not None else None,
                cwe=cwe,
                summary=summary,
                references=references,
                raw_sources=["nvd"],
                extras={"raw_id": cve_id},
            )
        )
    return results


def normalize_kev(raw: dict[str, Any] | list[dict[str, Any]]) -> list[NormalizedVulnerability]:
    if isinstance(raw, list):
        vulns = raw
    else:
        vulns = raw.get("vulnerabilities") or [raw]
    results: list[NormalizedVulnerability] = []
    for item in vulns:
        cve_id = item.get("cveID") or item.get("cveId") or "UNKNOWN-CVE"
        results.append(
            NormalizedVulnerability(
                cve_id=cve_id,
                source="cisa_kev",
                published_at=_parse_datetime(item.get("dateAdded") or item.get("dateUpdated")),
                vendor=_stringify(item.get("vendorProject")),
                product=_stringify(item.get("product")),
                summary=_stringify(item.get("shortDescription") or item.get("notes")),
                kev_status=True,
                raw_sources=["cisa_kev"],
                extras={
                    "due_date": item.get("dueDate"),
                    "known_ransomware_campaign_use": item.get("knownRansomwareCampaignUse"),
                },
            )
        )
    return results


def normalize_github_advisories(raw: list[dict[str, Any]]) -> list[NormalizedVulnerability]:
    results: list[NormalizedVulnerability] = []
    for item in raw:
        cve_id = item.get("cve_id") or item.get("cveId") or item.get("cve") or "UNKNOWN-CVE"
        results.append(
            NormalizedVulnerability(
                cve_id=cve_id,
                source="github_advisory",
                published_at=_parse_datetime(item.get("published_at") or item.get("publishedAt")),
                severity=_stringify(item.get("severity")),
                summary=_stringify(item.get("summary") or item.get("description")),
                exploit_available=bool(item.get("exploitable")),
                raw_sources=["github_advisory"],
                extras={
                    "advisory_id": item.get("ghsa_id") or item.get("ghsaId") or item.get("id"),
                    "repository": item.get("repository"),
                },
            )
        )
    return results


def normalize_github_events(raw: list[dict[str, Any]]) -> list[NormalizedVulnerability]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "types": set()})
    for item in raw:
        cve_id = item.get("cve_id") or item.get("cveId") or item.get("issue", {}).get("title") or "UNKNOWN-CVE"
        grouped[cve_id]["count"] += 1
        grouped[cve_id]["types"].add(item.get("type") or item.get("event_type") or "unknown")
    results: list[NormalizedVulnerability] = []
    for cve_id, aggregate in grouped.items():
        results.append(
            NormalizedVulnerability(
                cve_id=cve_id,
                source="github_events",
                advisory_activity=int(aggregate["count"]),
                raw_sources=["github_events"],
                extras={"event_types": sorted(aggregate["types"])},
            )
        )
    return results


def normalize_exploitdb(raw: list[dict[str, Any]]) -> list[NormalizedVulnerability]:
    results: list[NormalizedVulnerability] = []
    for item in raw:
        cve_id = item.get("cve") or item.get("cve_id") or "UNKNOWN-CVE"
        results.append(
            NormalizedVulnerability(
                cve_id=cve_id,
                source="exploitdb",
                published_at=_parse_datetime(item.get("date") or item.get("publication_date")),
                exploit_available=True,
                summary=_stringify(item.get("title") or item.get("description")),
                raw_sources=["exploitdb"],
                extras={
                    "exploit_id": item.get("id"),
                    "exploit_type": item.get("type"),
                },
            )
        )
    return results


def merge_vulnerabilities(records: Iterable[NormalizedVulnerability]) -> list[NormalizedVulnerability]:
    merged: dict[str, NormalizedVulnerability] = {}
    for record in records:
        current = merged.get(record.cve_id)
        if current is None:
            merged[record.cve_id] = record
            continue
        merged[record.cve_id] = NormalizedVulnerability(
            cve_id=record.cve_id,
            source="joined",
            published_at=current.published_at or record.published_at,
            vendor=current.vendor or record.vendor,
            product=current.product or record.product,
            severity=current.severity or record.severity,
            cvss_score=current.cvss_score if current.cvss_score is not None else record.cvss_score,
            cwe=current.cwe or record.cwe,
            summary=current.summary or record.summary,
            kev_status=current.kev_status or record.kev_status,
            exploit_available=current.exploit_available or record.exploit_available,
            advisory_activity=current.advisory_activity + record.advisory_activity,
            references=sorted(set(current.references + record.references)),
            raw_sources=sorted(set(current.raw_sources + record.raw_sources)),
            extras={**record.extras, **current.extras},
        )
    return list(merged.values())
