"""Build a canonical per-building context before any LLM agent runs.

Synthetic reference implementation. The builder performs deterministic filtering,
derivation and relationship checks; it does not make investment recommendations.
"""
from __future__ import annotations

from datetime import date
from typing import Any


def _rows(portfolio: dict[str, Any], key: str, building_id: str) -> list[dict[str, Any]]:
    return [r for r in portfolio.get(key, []) if r.get("building_id") == building_id]


def detention_band(years: float | None) -> str:
    if years is None:
        return "UNKNOWN"
    if years < 2:
        return "LT_2_YEARS"
    if years <= 5:
        return "2_TO_5_YEARS"
    return "GT_5_YEARS"


def build_site_context(portfolio: dict[str, Any], building_id: str) -> dict[str, Any]:
    buildings = [b for b in portfolio.get("buildings", []) if b.get("building_id") == building_id]
    if len(buildings) != 1:
        raise ValueError(f"Expected exactly one building for {building_id}; found {len(buildings)}")
    building = buildings[0]

    occupancies = _rows(portfolio, "occupancies", building_id)
    service_point_ids = {o.get("service_point_id") for o in occupancies if o.get("service_point_id")}
    service_points = [s for s in portfolio.get("service_points", []) if s.get("service_point_id") in service_point_ids]
    leases = _rows(portfolio, "leases", building_id)
    strategic_context = _rows(portfolio, "strategic_context", building_id)

    active_occupancies = [o for o in occupancies if o.get("is_current") is True or o.get("occupancy_status") == "active"]
    active_leases = [l for l in leases if l.get("lease_status") in {"active", "current"}]
    lease_end_dates = sorted([l["lease_end_date"] for l in active_leases if l.get("lease_end_date")])

    strategy_rows = _rows(portfolio, "asset_strategy", building_id)
    strategy = strategy_rows[0] if strategy_rows else None
    horizon = strategy.get("detention_horizon_years") if strategy else None
    if horizon is None:
        horizon = building.get("detention_horizon_years")

    area = building.get("gross_area_sqft")
    unit_replacement = building.get("replacement_cost_per_sqft")
    calculated_replacement = None
    if isinstance(area, (int, float)) and isinstance(unit_replacement, (int, float)):
        calculated_replacement = round(area * unit_replacement, 2)

    exceptions: list[dict[str, Any]] = []
    warnings: list[str] = []
    if len(active_occupancies) > 1:
        warnings.append("MULTI_OCCUPANT_BUILDING: preserve service_point_id/occupancy_id for business and lease decisions.")
    if strategic_context:
        warnings.append("STRATEGIC_CONTEXT_AVAILABLE: qualitative structured context is available for Agent T/E; treat it as contextual evidence, not authoritative replacement for structured source facts.")

    for lease in leases:
        if lease.get("service_point_id") not in service_point_ids:
            exceptions.append({"code": "LEASE_SERVICE_POINT_MISMATCH", "lease_id": lease.get("lease_id")})
        occ_id = lease.get("occupancy_id")
        if occ_id and occ_id not in {o.get("occupancy_id") for o in occupancies}:
            exceptions.append({"code": "LEASE_OCCUPANCY_MISMATCH", "lease_id": lease.get("lease_id")})

    status = "REVIEW_REQUIRED" if exceptions else "VALIDATED"

    return {
        "context_version": "0.2",
        "generated_at": date.today().isoformat(),
        "building_id": building_id,
        "building": building,
        "service_points": service_points,
        "occupancies": occupancies,
        "deficiencies": _rows(portfolio, "deficiencies", building_id),
        "components": _rows(portfolio, "components", building_id),
        "accessibility": _rows(portfolio, "accessibility", building_id),
        "initiatives": _rows(portfolio, "initiatives", building_id),
        "projects": _rows(portfolio, "projects", building_id),
        "leases": leases,
        "asset_strategy": strategy,
        "strategic_context": strategic_context,
        "risks": _rows(portfolio, "risks", building_id),
        "energy_performance": _rows(portfolio, "energy_performance", building_id),
        "maintenance_history": _rows(portfolio, "maintenance_history", building_id),
        "space_utilization": _rows(portfolio, "space_utilization", building_id),
        "spatial_references": _rows(portfolio, "spatial_references", building_id),
        "derived_facts": {
            "calculated_replacement_value": calculated_replacement,
            "active_service_point_count": len(active_occupancies),
            "active_lease_count": len(active_leases),
            "earliest_active_lease_end_date": lease_end_dates[0] if lease_end_dates else None,
            "detention_horizon_years": horizon,
            "detention_band": detention_band(horizon),
            "strategic_context_available": bool(strategic_context),
        },
        "data_quality": {
            "status": status,
            "association_exceptions": exceptions,
            "warnings": warnings,
        },
        "source_lineage": portfolio.get("source_lineage", []),
    }
