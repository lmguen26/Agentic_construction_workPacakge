from src.evaluation.agent_a_live_evaluator import evaluate_agent_a


def context():
    return {
        "building_id": "BLDG-T1",
        "deficiencies": [{
            "deficiency_id": "DEF-T1",
            "component_id": "CMP-T1",
            "uniformat_code": "D3050",
            "condition_rating": "poor",
            "intervention_horizon": "0-2 years",
            "source_total_cost": 100000,
            "observation": "Observed issue",
            "proposed_corrective_action": "Replace equipment",
        }],
        "projects": [],
        "initiatives": [],
        "accessibility": [],
    }


def valid_artifact():
    return {
        "site_id": "BLDG-T1",
        "stage": "OPPORTUNITIES",
        "source_context_id": "test-context",
        "opportunities": [{
            "opportunity_id": "OPP-DEF-T1",
            "source_deficiency_id": "DEF-T1",
            "site_id": "BLDG-T1",
            "component_id": "CMP-T1",
            "title": "Normalized equipment renewal opportunity",
            "description": "Normalized description",
            "action_type": "replacement",
            "system": "HVAC",
            "uniformat_code": "D3050",
            "location": None,
            "condition_rating": "poor",
            "intervention_horizon": "0-2 years",
            "source_cost": 100000,
            "observation": "Observed issue",
            "source_proposed_corrective_action": "Replace equipment",
            "source_lineage": ["DEF-T1", "CMP-T1"],
            "facts_used": ["DEF-T1", "CMP-T1"],
            "interpretation": "Renewal should be considered downstream.",
            "assumptions": [],
            "exceptions": []
        }],
        "stage_exceptions": []
    }


def test_valid_agent_a_output_passes():
    result = evaluate_agent_a(context(), valid_artifact())
    assert result["status"] == "PASS"
    assert result["metrics"]["traceability_coverage"] == 1


def test_changed_source_cost_fails():
    artifact = valid_artifact()
    artifact["opportunities"][0]["source_cost"] = 125000
    result = evaluate_agent_a(context(), artifact)
    assert result["status"] == "FAIL"
    assert "source_fact_changed:DEF-T1:source_cost" in result["failures"]


def test_work_package_creation_fails():
    artifact = valid_artifact()
    artifact["work_packages"] = []
    result = evaluate_agent_a(context(), artifact)
    assert result["status"] == "FAIL"
    assert any("downstream_concept_present" in x for x in result["failures"])
