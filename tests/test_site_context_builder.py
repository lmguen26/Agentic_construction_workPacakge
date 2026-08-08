import json
from pathlib import Path

from src.context.site_context_builder import build_site_context, detention_band


PORTFOLIO = Path("examples/synthetic_portfolio/portfolio.json")


def load_portfolio():
    return json.loads(PORTFOLIO.read_text(encoding="utf-8"))


def test_detention_bands():
    assert detention_band(1.5) == "LT_2_YEARS"
    assert detention_band(2) == "2_TO_5_YEARS"
    assert detention_band(5) == "2_TO_5_YEARS"
    assert detention_band(5.1) == "GT_5_YEARS"
    assert detention_band(None) == "UNKNOWN"


def test_owned_building_context():
    context = build_site_context(load_portfolio(), "BLDG-001")
    assert context["data_quality"]["status"] == "VALIDATED"
    assert context["derived_facts"]["calculated_replacement_value"] == 7_400_000
    assert context["derived_facts"]["detention_horizon_years"] == 10
    assert context["derived_facts"]["detention_band"] == "GT_5_YEARS"
    assert len(context["deficiencies"]) == 2


def test_leased_building_context_preserves_lease_relation():
    context = build_site_context(load_portfolio(), "BLDG-002")
    assert context["derived_facts"]["active_lease_count"] == 1
    assert context["derived_facts"]["earliest_active_lease_end_date"] == "2028-06-30"
    assert context["leases"][0]["service_point_id"] == "SP-002"
    assert context["leases"][0]["occupancy_id"] == "OCC-002"


def test_multi_occupant_building_is_not_flattened():
    context = build_site_context(load_portfolio(), "BLDG-003")
    assert context["derived_facts"]["active_service_point_count"] == 2
    assert len(context["service_points"]) == 2
    assert any("MULTI_OCCUPANT_BUILDING" in w for w in context["data_quality"]["warnings"])
