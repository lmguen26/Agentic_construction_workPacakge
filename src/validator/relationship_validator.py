from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AssociationIssue:
    severity: str
    code: str
    message: str
    record_type: str
    record_id: str | None = None


def _ids(records: list[dict[str, Any]], key: str) -> set[str]:
    return {str(r[key]) for r in records if r.get(key) is not None}


def validate_relationships(portfolio: dict[str, Any]) -> list[AssociationIssue]:
    issues: list[AssociationIssue] = []

    buildings = portfolio.get("buildings", [])
    service_points = portfolio.get("service_points", [])
    occupancies = portfolio.get("occupancies", [])
    components = portfolio.get("components", [])
    deficiencies = portfolio.get("deficiencies", [])
    leases = portfolio.get("leases", [])
    initiatives = portfolio.get("initiatives", [])
    projects = portfolio.get("projects", [])

    building_ids = _ids(buildings, "building_id")
    service_point_ids = _ids(service_points, "service_point_id")
    occupancy_ids = _ids(occupancies, "occupancy_id")
    component_ids = _ids(components, "component_id")

    for occ in occupancies:
        rid = occ.get("occupancy_id")
        if occ.get("building_id") not in building_ids:
            issues.append(AssociationIssue("ERROR", "OCC_BUILDING_NOT_FOUND", "Occupancy references an unknown building.", "occupancy", rid))
        if occ.get("service_point_id") not in service_point_ids:
            issues.append(AssociationIssue("ERROR", "OCC_SERVICE_POINT_NOT_FOUND", "Occupancy references an unknown service point.", "occupancy", rid))

    for component in components:
        if component.get("building_id") not in building_ids:
            issues.append(AssociationIssue("ERROR", "COMPONENT_BUILDING_NOT_FOUND", "Component references an unknown building.", "component", component.get("component_id")))

    for deficiency in deficiencies:
        rid = deficiency.get("deficiency_id")
        if deficiency.get("building_id") not in building_ids:
            issues.append(AssociationIssue("ERROR", "DEF_BUILDING_NOT_FOUND", "Deficiency references an unknown building.", "deficiency", rid))
        component_id = deficiency.get("component_id")
        if component_id is not None and component_id not in component_ids:
            issues.append(AssociationIssue("ERROR", "DEF_COMPONENT_NOT_FOUND", "Deficiency references an unknown component.", "deficiency", rid))

    for lease in leases:
        rid = lease.get("lease_id")
        if lease.get("building_id") not in building_ids:
            issues.append(AssociationIssue("ERROR", "LEASE_BUILDING_NOT_FOUND", "Lease references an unknown building.", "lease", rid))
        if lease.get("service_point_id") not in service_point_ids:
            issues.append(AssociationIssue("ERROR", "LEASE_SERVICE_POINT_NOT_FOUND", "Lease references an unknown service point.", "lease", rid))
        if lease.get("occupancy_id") not in occupancy_ids:
            issues.append(AssociationIssue("ERROR", "LEASE_OCCUPANCY_NOT_FOUND", "Lease references an unknown occupancy.", "lease", rid))
        else:
            matching = [o for o in occupancies if o.get("occupancy_id") == lease.get("occupancy_id")]
            if matching:
                occ = matching[0]
                if occ.get("building_id") != lease.get("building_id") or occ.get("service_point_id") != lease.get("service_point_id"):
                    issues.append(AssociationIssue("ERROR", "LEASE_OCCUPANCY_MISMATCH", "Lease building/service point does not match its occupancy relationship.", "lease", rid))

    for record_type, records in (("initiative", initiatives), ("project", projects)):
        for record in records:
            rid = record.get(f"{record_type}_id")
            if record.get("building_id") not in building_ids:
                issues.append(AssociationIssue("ERROR", f"{record_type.upper()}_BUILDING_NOT_FOUND", f"{record_type.title()} references an unknown building.", record_type, rid))
            service_point_id = record.get("service_point_id")
            if service_point_id is not None and service_point_id not in service_point_ids:
                issues.append(AssociationIssue("ERROR", f"{record_type.upper()}_SERVICE_POINT_NOT_FOUND", f"{record_type.title()} references an unknown service point.", record_type, rid))

    # Detect potentially ambiguous active multi-occupant buildings. This is not an error.
    by_building: dict[str, list[dict[str, Any]]] = {}
    for occ in occupancies:
        if occ.get("occupancy_end_date") is None:
            by_building.setdefault(str(occ.get("building_id")), []).append(occ)
    for building_id, active in by_building.items():
        if len(active) > 1:
            issues.append(AssociationIssue("INFO", "MULTI_OCCUPANT_BUILDING", f"Building has {len(active)} active service-point occupancies; downstream lease and business-context joins must remain service-point aware.", "building", building_id))

    return issues
