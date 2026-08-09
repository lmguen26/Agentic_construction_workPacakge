import json
from pathlib import Path

from src.evaluation.behavior_evaluator import evaluate_reference_run
from src.evaluation.reference_fixture_builder import build_reference_artifacts, build_validated_context


ARCHETYPES = Path("examples/archetypes/archetypes.json")


def load_portfolio():
    return json.loads(ARCHETYPES.read_text(encoding="utf-8"))


def test_all_non_blocked_archetypes_generate_a_to_e_and_preserve_lineage():
    portfolio = load_portfolio()
    for item in portfolio["archetypes"]:
        bid = item["building_id"]
        context = build_validated_context(portfolio, bid)
        artifacts = build_reference_artifacts(context)
        if bid == "BLDG-A8":
            assert context["data_quality"]["status"] == "BLOCKED"
            assert artifacts == {}
            continue
        assert set(artifacts) == {"A", "B", "C", "T", "E"}
        assert all(artifact["building_id"] == bid for artifact in artifacts.values())
        assert evaluate_reference_run(context, artifacts) == []


def test_lease_expiry_and_strategic_context_drive_review_not_unconditional_commitment():
    portfolio = load_portfolio()
    context = build_validated_context(portfolio, "BLDG-A2")
    artifacts = build_reference_artifacts(context)
    recommendation = artifacts["T"]["recommendations"][0]
    assert recommendation["recommended_action"] == "major_capital_review_before_commitment"
    assert any("LEASE-A2" in c for c in recommendation["constraints"])
    assert any("CTX-A2" in c for c in recommendation["constraints"])
    assert any("2_TO_5_YEARS" in c for c in recommendation["constraints"])
    assert recommendation["human_review_required"] is True


def test_multi_service_point_context_remains_explicit_through_strategy_stage():
    portfolio = load_portfolio()
    context = build_validated_context(portfolio, "BLDG-A3")
    artifacts = build_reference_artifacts(context)
    evidence = artifacts["T"]["recommendations"][0]["occupancy_evidence"]
    assert any("OCC-A3A" in x and "SP-A3A" in x for x in evidence)
    assert any("OCC-A3B" in x and "SP-A3B" in x for x in evidence)
    assert any("LEASE-A3" in c for c in artifacts["T"]["recommendations"][0]["constraints"])


def test_future_initiative_and_active_project_are_not_ignored():
    portfolio = load_portfolio()
    c5 = build_validated_context(portfolio, "BLDG-A5")
    a5 = build_reference_artifacts(c5)
    assert a5["T"]["recommendations"][0]["recommended_action"] == "consider_bundle_or_defer_with_initiative"
    assert "INIT-A5" in str(a5["B"])

    c6 = build_validated_context(portfolio, "BLDG-A6")
    a6 = build_reference_artifacts(c6)
    assert a6["T"]["recommendations"][0]["recommended_action"] == "coordinate_and_avoid_duplicate_scope"
    assert "PRJ-A6" in str(a6["B"])


def test_accessibility_unknown_is_preserved_as_unknown():
    portfolio = load_portfolio()
    context = build_validated_context(portfolio, "BLDG-A7")
    artifacts = build_reference_artifacts(context)
    evidence = artifacts["T"]["recommendations"][0]["accessibility_evidence"]
    assert "ACC-A7-1 non_compliant" in evidence
    assert "ACC-A7-2 unknown" in evidence


def test_high_fci_forces_strategy_review():
    portfolio = load_portfolio()
    context = build_validated_context(portfolio, "BLDG-A4")
    artifacts = build_reference_artifacts(context)
    recommendation = artifacts["T"]["recommendations"][0]
    assert recommendation["fci"] == 0.35
    assert recommendation["recommended_action"] == "strategy_review_due_to_high_condition_burden"
    assert recommendation["human_review_required"] is True
