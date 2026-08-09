"""Deterministic evaluator for live Agent A outputs.

The evaluator checks business invariants rather than wording so different Copilot
models/prompts can be compared without brittle golden-text matching.
"""
from __future__ import annotations

from typing import Any


def evaluate_agent_a(context: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    if artifact.get("stage") != "OPPORTUNITIES":
        failures.append("stage_must_be_opportunities")
    if artifact.get("site_id") != context.get("building_id"):
        failures.append("site_id_must_match_context")

    source_defs = {d.get("deficiency_id"): d for d in context.get("deficiencies", []) if d.get("deficiency_id")}
    opportunities = artifact.get("opportunities") or []
    by_def: dict[str, list[dict[str, Any]]] = {}
    for opp in opportunities:
        did = opp.get("source_deficiency_id")
        by_def.setdefault(did, []).append(opp)
        if did not in source_defs:
            failures.append(f"unknown_source_deficiency:{did}")
            continue
        if opp.get("site_id") != context.get("building_id"):
            failures.append(f"opportunity_site_mismatch:{did}")
        if did not in (opp.get("source_lineage") or []):
            failures.append(f"missing_deficiency_lineage:{did}")

        source = source_defs[did]
        # Source facts must be preserved when populated in both source and output.
        comparisons = {
            "component_id": source.get("component_id"),
            "uniformat_code": source.get("uniformat_code"),
            "condition_rating": source.get("condition_rating"),
            "intervention_horizon": source.get("intervention_horizon"),
            "source_cost": source.get("source_total_cost"),
            "observation": source.get("observation"),
            "source_proposed_corrective_action": source.get("proposed_corrective_action"),
        }
        for field, expected in comparisons.items():
            if expected is not None and opp.get(field) != expected:
                failures.append(f"source_fact_changed:{did}:{field}")

    # V0.3 reference expectation: one normalized opportunity per deficiency.
    for did in source_defs:
        count = len(by_def.get(did, []))
        if count != 1:
            failures.append(f"expected_one_opportunity_per_deficiency:{did}:{count}")

    # Agent A must not own downstream concepts.
    forbidden_keys = {
        "work_packages", "clusters", "indexed_cost", "indirect_costs",
        "total_estimated_cost", "recommendations", "executive_summary",
    }
    def walk(value: Any, path: str = "root") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_keys:
                    failures.append(f"downstream_concept_present:{path}.{key}")
                walk(child, f"{path}.{key}")
        elif isinstance(value, list):
            for i, child in enumerate(value):
                walk(child, f"{path}[{i}]")
    walk(artifact)

    # Contextual records may be cited but should not suppress deficiencies at A.
    if context.get("projects") and len(opportunities) < len(source_defs):
        failures.append("project_context_suppressed_deficiency")
    if context.get("initiatives") and len(opportunities) < len(source_defs):
        failures.append("initiative_context_suppressed_deficiency")

    # Accessibility unknown must never be converted by Agent A into a factual claim.
    unknown_accessibility = [a for a in context.get("accessibility", []) if a.get("compliance_status") == "unknown"]
    if unknown_accessibility:
        text = str(artifact).lower()
        for a in unknown_accessibility:
            cid = str(a.get("criterion_id") or "").lower()
            if cid and cid in text and "non_compliant" in text:
                warnings.append(f"review_unknown_accessibility_representation:{a.get('accessibility_assessment_id')}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "metrics": {
            "source_deficiency_count": len(source_defs),
            "opportunity_count": len(opportunities),
            "traceability_coverage": 0 if not source_defs else sum(1 for d in source_defs if len(by_def.get(d, [])) == 1) / len(source_defs),
        },
    }
