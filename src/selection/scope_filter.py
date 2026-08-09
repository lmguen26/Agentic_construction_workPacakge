from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class SelectionScope:
    region_ids: tuple[str, ...] = ()
    branch_ids: tuple[str, ...] = ()
    site_ids: tuple[str, ...] = ()
    building_ids: tuple[str, ...] = ()


def _selected(value: Any, allowed: set[str]) -> bool:
    return not allowed or str(value or "") in allowed


def filter_buildings(buildings: Iterable[dict[str, Any]], scope: SelectionScope) -> list[dict[str, Any]]:
    """Filter buildings using cumulative hierarchical filters.

    Empty selections mean 'all' for that dimension. Filters combine with AND.
    The building remains the final execution unit.
    """
    regions = set(scope.region_ids)
    branches = set(scope.branch_ids)
    sites = set(scope.site_ids)
    building_ids = set(scope.building_ids)
    return [
        b for b in buildings
        if _selected(b.get("region_id"), regions)
        and _selected(b.get("branch_id"), branches)
        and _selected(b.get("site_id"), sites)
        and _selected(b.get("building_id"), building_ids)
    ]


def available_values(buildings: Iterable[dict[str, Any]], field: str, scope: SelectionScope | None = None) -> list[str]:
    rows = list(buildings)
    if scope is not None:
        rows = filter_buildings(rows, scope)
    return sorted({str(b.get(field)) for b in rows if b.get(field) not in (None, "")})


def describe_scope(scope: SelectionScope) -> dict[str, list[str]]:
    return {
        "region_ids": list(scope.region_ids),
        "branch_ids": list(scope.branch_ids),
        "site_ids": list(scope.site_ids),
        "building_ids": list(scope.building_ids),
    }
