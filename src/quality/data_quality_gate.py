"""Deterministic per-site data quality gate for V0.2.1."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Any

STATUSES = {"COMPLETE", "PARTIAL", "CONFLICT", "STALE", "NOT_APPLICABLE", "MISSING"}
SEVERITIES = {"BLOCKING", "WARNING", "INFORMATIONAL"}


@dataclass
class QualityResult:
    source: str
    status: str
    severity: str
    reason: str
    record_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _rows(portfolio: dict[str, Any], key: str, building_id: str) -> list[dict[str, Any]]:
    return [r for r in portfolio.get(key, []) if r.get("building_id") == building_id]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def evaluate_site(portfolio: dict[str, Any], building_id: str, today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    buildings = [b for b in portfolio.get("buildings", []) if b.get("building_id") == building_id]
    if len(buildings) != 1:
        return {
            "building_id": building_id,
            "gate_status": "BLOCKED",
            "results": [QualityResult("buildings", "CONFLICT", "BLOCKING", f"Expected exactly one building record, found {len(buildings)}", len(buildings)).to_dict()],
        }

    building = buildings[0]
    ownership = building.get("ownership_type")
    results: list[QualityResult] = []

    # Core domains
    results.append(QualityResult("buildings", "COMPLETE", "INFORMATIONAL", "Single authoritative building record found", 1))

    occupancies = _rows(portfolio, "occupancies", building_id)
    results.append(QualityResult("occupancies", "COMPLETE" if occupancies else "MISSING", "BLOCKING" if not occupancies else "INFORMATIONAL", "Occupancy relationship records are required for service-point association", len(occupancies)))

    deficiencies = _rows(portfolio, "deficiencies", building_id)
    results.append(QualityResult("deficiencies", "COMPLETE" if deficiencies else "MISSING", "BLOCKING" if not deficiencies else "INFORMATIONAL", "Deficiencies are the primary work-generation source", len(deficiencies)))

    components = _rows(portfolio, "components", building_id)
    results.append(QualityResult("components", "COMPLETE" if components else "MISSING", "WARNING" if not components else "INFORMATIONAL", "Component data enriches deficiency interpretation but is not universally required", len(components)))

    accessibility = _rows(portfolio, "accessibility", building_id)
    results.append(QualityResult("accessibility", "COMPLETE" if accessibility else "MISSING", "WARNING" if not accessibility else "INFORMATIONAL", "Accessibility is optional but valuable", len(accessibility)))

    initiatives = _rows(portfolio, "initiatives", building_id)
    results.append(QualityResult("initiatives", "COMPLETE" if initiatives else "MISSING", "INFORMATIONAL", "No future initiative is acceptable but should be explicit", len(initiatives)))

    projects = _rows(portfolio, "projects", building_id)
    results.append(QualityResult("projects", "COMPLETE" if projects else "MISSING", "INFORMATIONAL", "No current project is acceptable but should be explicit", len(projects)))

    leases = _rows(portfolio, "leases", building_id)
    if ownership == "owned":
        results.append(QualityResult("leases", "NOT_APPLICABLE" if not leases else "PARTIAL", "INFORMATIONAL" if not leases else "WARNING", "Owned building normally does not require lease records", len(leases)))
    else:
        results.append(QualityResult("leases", "COMPLETE" if leases else "MISSING", "BLOCKING" if not leases else "INFORMATIONAL", "Lease data is required for leased or mixed sites", len(leases)))

    strategy = _rows(portfolio, "asset_strategy", building_id)
    results.append(QualityResult("asset_strategy", "COMPLETE" if strategy else "MISSING", "WARNING" if not strategy else "INFORMATIONAL", "Detention horizon and ownership strategy materially affect recommendations", len(strategy)))

    strategic_context = _rows(portfolio, "strategic_context", building_id)
    results.append(QualityResult("strategic_context", "COMPLETE" if strategic_context else "MISSING", "INFORMATIONAL", "Structured strategic context is optional but high-value", len(strategic_context)))

    # Relationship conflicts
    service_point_ids = {o.get("service_point_id") for o in occupancies if o.get("service_point_id")}
    occupancy_ids = {o.get("occupancy_id") for o in occupancies if o.get("occupancy_id")}
    conflict_count = 0
    for lease in leases:
        if lease.get("service_point_id") not in service_point_ids:
            conflict_count += 1
        if lease.get("occupancy_id") and lease.get("occupancy_id") not in occupancy_ids:
            conflict_count += 1
    if conflict_count:
        results.append(QualityResult("associations", "CONFLICT", "BLOCKING", f"Detected {conflict_count} lease/occupancy association conflicts", conflict_count))
    else:
        results.append(QualityResult("associations", "COMPLETE", "INFORMATIONAL", "No blocking relationship conflicts detected", 0))

    # Simple staleness example for deficiency inspections (> 5 years)
    stale = 0
    for d in deficiencies:
        inspected = _parse_date(d.get("inspection_date"))
        if inspected and (today - inspected).days > 365 * 5:
            stale += 1
    if stale:
        results.append(QualityResult("deficiency_freshness", "STALE", "WARNING", f"{stale} deficiency records are older than five years", stale))
    elif deficiencies:
        results.append(QualityResult("deficiency_freshness", "COMPLETE", "INFORMATIONAL", "Deficiency inspection dates are within the reference freshness threshold", len(deficiencies)))

    if any(r.severity == "BLOCKING" and r.status in {"MISSING", "CONFLICT", "STALE"} for r in results):
        gate = "BLOCKED"
    elif any(r.severity == "WARNING" and r.status in {"MISSING", "PARTIAL", "CONFLICT", "STALE"} for r in results):
        gate = "REVIEW_REQUIRED"
    else:
        gate = "VALIDATED"

    return {"building_id": building_id, "gate_status": gate, "results": [r.to_dict() for r in results]}
