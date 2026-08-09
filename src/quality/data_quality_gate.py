"""Deterministic per-building data quality gate.

The gate validates source readiness and critical identity relationships before agents
run. It supports a simple legacy building-level ownership field and, when available,
a more precise premises/building-portion tenure model.
"""
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


def _active(row: dict[str, Any], today: date) -> bool:
    if row.get("is_current") is True:
        return True
    if row.get("occupancy_status") in {"active", "current"}:
        return True
    start = _parse_date(row.get("occupancy_start_date") or row.get("valid_from"))
    end = _parse_date(row.get("occupancy_end_date") or row.get("valid_to"))
    return (start is None or start <= today) and (end is None or end >= today)


def evaluate_site(portfolio: dict[str, Any], building_id: str, today: date | None = None) -> dict[str, Any]:
    """Evaluate one physical building/premises analysis unit.

    The function name is retained for compatibility; `building_id` is the atomic
    analysis identity. `site_id` is parent context only.
    """
    today = today or date.today()
    buildings = [b for b in portfolio.get("buildings", []) if b.get("building_id") == building_id]
    if len(buildings) != 1:
        return {
            "building_id": building_id,
            "gate_status": "BLOCKED",
            "results": [QualityResult("buildings", "CONFLICT", "BLOCKING", f"Expected exactly one building record, found {len(buildings)}", len(buildings)).to_dict()],
        }

    building = buildings[0]
    site_id = building.get("site_id")
    ownership = building.get("ownership_type")
    results: list[QualityResult] = []

    results.append(QualityResult("buildings", "COMPLETE", "INFORMATIONAL", "Single authoritative physical building record found", 1))

    occupancies = _rows(portfolio, "occupancies", building_id)
    results.append(QualityResult("occupancies", "COMPLETE" if occupancies else "MISSING", "BLOCKING" if not occupancies else "INFORMATIONAL", "Temporal occupancy relationships are required for business/transit association", len(occupancies)))

    service_points = portfolio.get("service_points", [])
    authoritative_service_point_ids = {s.get("service_point_id") for s in service_points if s.get("service_point_id")}
    occupancy_service_point_ids = {o.get("service_point_id") for o in occupancies if o.get("service_point_id")}
    missing_service_points = sorted(x for x in occupancy_service_point_ids if authoritative_service_point_ids and x not in authoritative_service_point_ids)
    if missing_service_points:
        results.append(QualityResult("service_point_associations", "CONFLICT", "BLOCKING", f"Occupancy references unknown service point(s): {', '.join(missing_service_points)}", len(missing_service_points)))
    elif occupancies:
        results.append(QualityResult("service_point_associations", "COMPLETE", "INFORMATIONAL", "Occupancy service-point/transit references resolve to known business identities", len(occupancy_service_point_ids)))

    site_mismatch = [o for o in occupancies if site_id and o.get("site_id") and o.get("site_id") != site_id]
    if site_mismatch:
        results.append(QualityResult("site_building_occupancy", "CONFLICT", "BLOCKING", "One or more occupancy records point to a different parent site than the selected building", len(site_mismatch)))

    active_by_service_point: dict[str, int] = {}
    for occ in occupancies:
        sp = occ.get("service_point_id")
        if sp and _active(occ, today):
            active_by_service_point[sp] = active_by_service_point.get(sp, 0) + 1
    multi_active = [sp for sp, count in active_by_service_point.items() if count > 1]
    if multi_active:
        results.append(QualityResult("temporal_occupancy", "PARTIAL", "WARNING", "One or more service points/transits have multiple active occupancy records. This may be valid but requires confirmation of the business rule.", len(multi_active)))
    elif occupancies:
        results.append(QualityResult("temporal_occupancy", "COMPLETE", "INFORMATIONAL", "No ambiguous simultaneous occupancy pattern detected under the reference rule", len(active_by_service_point)))

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

    premises = _rows(portfolio, "premises", building_id)
    tenure_types = {str(p.get("tenure_type") or "").lower() for p in premises if p.get("tenure_type")}
    if premises:
        results.append(QualityResult("premises", "COMPLETE", "INFORMATIONAL", "Premises/building-portion records provide the authoritative tenure layer for this building", len(premises)))
        leased_scope_exists = bool(tenure_types & {"leased", "tenant", "lease"})
        owned_scope_exists = bool(tenure_types & {"owned", "owner", "owner_occupied"})
        if leased_scope_exists and owned_scope_exists:
            results.append(QualityResult("tenure", "PARTIAL", "INFORMATIONAL", "Mixed owned/leased tenure detected; lease applicability must be resolved by premises/occupancy rather than building-wide tenure", len(premises)))
    else:
        leased_scope_exists = ownership in {"leased", "mixed"}
        owned_scope_exists = ownership in {"owned", "mixed"}
        results.append(QualityResult("premises", "MISSING", "INFORMATIONAL", "No explicit premises/building-portion layer; using legacy building-level ownership_type where available", 0))

    leases = _rows(portfolio, "leases", building_id)
    if leased_scope_exists:
        results.append(QualityResult("leases", "COMPLETE" if leases else "MISSING", "BLOCKING" if not leases else "INFORMATIONAL", "Lease data is required because leased physical scope exists", len(leases)))
    elif owned_scope_exists and not leased_scope_exists:
        results.append(QualityResult("leases", "NOT_APPLICABLE" if not leases else "PARTIAL", "INFORMATIONAL" if not leases else "WARNING", "No leased physical scope is identified; unexpected lease records require review", len(leases)))
    else:
        results.append(QualityResult("leases", "PARTIAL" if leases else "MISSING", "WARNING", "Tenure could not be determined conclusively; lease applicability requires review", len(leases)))

    strategy = _rows(portfolio, "asset_strategy", building_id)
    results.append(QualityResult("asset_strategy", "COMPLETE" if strategy else "MISSING", "WARNING" if not strategy else "INFORMATIONAL", "Detention horizon and ownership strategy materially affect recommendations", len(strategy)))

    strategic_context = _rows(portfolio, "strategic_context", building_id)
    results.append(QualityResult("strategic_context", "COMPLETE" if strategic_context else "MISSING", "INFORMATIONAL", "Structured strategic context is optional but high-value", len(strategic_context)))

    occupancy_ids = {o.get("occupancy_id") for o in occupancies if o.get("occupancy_id")}
    premises_ids = {p.get("premises_id") for p in premises if p.get("premises_id")}
    premises_by_id = {p.get("premises_id"): p for p in premises if p.get("premises_id")}
    conflict_count = 0
    conflict_reasons: list[str] = []
    for lease in leases:
        if lease.get("service_point_id") and lease.get("service_point_id") not in occupancy_service_point_ids:
            conflict_count += 1
            conflict_reasons.append(f"lease {lease.get('lease_id')} service point not present in building occupancy")
        if lease.get("occupancy_id") and lease.get("occupancy_id") not in occupancy_ids:
            conflict_count += 1
            conflict_reasons.append(f"lease {lease.get('lease_id')} occupancy not found")
        pid = lease.get("premises_id")
        if pid and premises_ids and pid not in premises_ids:
            conflict_count += 1
            conflict_reasons.append(f"lease {lease.get('lease_id')} premises not found")
        if pid and pid in premises_by_id:
            tenure = str(premises_by_id[pid].get("tenure_type") or "").lower()
            if tenure in {"owned", "owner", "owner_occupied"}:
                conflict_count += 1
                conflict_reasons.append(f"lease {lease.get('lease_id')} references explicitly owned premises {pid}")

    if conflict_count:
        results.append(QualityResult("associations", "CONFLICT", "BLOCKING", f"Detected {conflict_count} lease/occupancy/premises association conflict(s): {'; '.join(conflict_reasons)}", conflict_count))
    else:
        results.append(QualityResult("associations", "COMPLETE", "INFORMATIONAL", "No blocking lease/occupancy/premises relationship conflicts detected", 0))

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

    return {"building_id": building_id, "site_id": site_id, "gate_status": gate, "results": [r.to_dict() for r in results]}
