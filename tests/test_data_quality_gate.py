import json
from datetime import date
from pathlib import Path

from src.quality.data_quality_gate import evaluate_site


PORTFOLIO = Path("examples/archetypes/archetypes.json")


def load_portfolio():
    return json.loads(PORTFOLIO.read_text(encoding="utf-8"))


def result_for(report, source):
    return next(r for r in report["results"] if r["source"] == source)


def test_owned_site_lease_is_not_applicable():
    report = evaluate_site(load_portfolio(), "BLDG-A1", today=date(2026, 8, 8))
    assert result_for(report, "leases")["status"] == "NOT_APPLICABLE"


def test_leased_site_requires_lease():
    report = evaluate_site(load_portfolio(), "BLDG-A2", today=date(2026, 8, 8))
    assert result_for(report, "leases")["status"] == "COMPLETE"


def test_optional_strategic_context_never_blocks():
    report = evaluate_site(load_portfolio(), "BLDG-A1", today=date(2026, 8, 8))
    ctx = result_for(report, "strategic_context")
    assert ctx["status"] == "MISSING"
    assert ctx["severity"] == "INFORMATIONAL"


def test_multi_occupant_site_is_not_blocked_by_multi_occupancy_itself():
    report = evaluate_site(load_portfolio(), "BLDG-A3", today=date(2026, 8, 8))
    assert result_for(report, "associations")["status"] == "COMPLETE"


def test_association_conflict_blocks_pipeline():
    report = evaluate_site(load_portfolio(), "BLDG-A8", today=date(2026, 8, 8))
    assoc = result_for(report, "associations")
    assert assoc["status"] == "CONFLICT"
    assert assoc["severity"] == "BLOCKING"
    assert report["gate_status"] == "BLOCKED"


def test_missing_component_data_warns_but_does_not_block():
    report = evaluate_site(load_portfolio(), "BLDG-A5", today=date(2026, 8, 8))
    components = result_for(report, "components")
    assert components["status"] == "MISSING"
    assert components["severity"] == "WARNING"
    assert report["gate_status"] == "REVIEW_REQUIRED"
