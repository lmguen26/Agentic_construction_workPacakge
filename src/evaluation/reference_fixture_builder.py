"""Materialize synthetic canonical contexts and reference A->E artifacts.

These are golden behavioral fixtures, not production recommendations. They exist to
exercise contracts, lineage, stage ownership and evaluator logic before real source
schemas are available.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.context.site_context_builder import build_site_context
from src.quality.data_quality_gate import evaluate_site


def _source_ref(context: dict[str, Any]) -> list[str]:
    return [d["deficiency_id"] for d in context.get("deficiencies", []) if d.get("deficiency_id")]


def build_validated_context(portfolio: dict[str, Any], building_id: str) -> dict[str, Any]:
    context = build_site_context(portfolio, building_id)
    gate = evaluate_site(portfolio, building_id)
    context["data_quality"]["status"] = gate["gate_status"]
    context["data_quality"]["source_results"] = gate["results"]
    return context


def build_reference_artifacts(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if context.get("data_quality", {}).get("status") == "BLOCKED":
        return {}

    bid = context["building_id"]
    site_id = (context.get("building") or {}).get("site_id")
    deficiency_ids = _source_ref(context)
    opportunity_ids = [f"OPP-{x}" for x in deficiency_ids]
    wp_id = f"WP-{bid}-001"

    opportunities = []
    for oid, did in zip(opportunity_ids, deficiency_ids):
        source = next(d for d in context.get("deficiencies", []) if d.get("deficiency_id") == did)
        opportunities.append({
            "opportunity_id": oid,
            "source_deficiency_id": did,
            "building_id": bid,
            "site_id": site_id,
            "component_id": source.get("component_id"),
            "title": source.get("title") or f"Opportunity {did}",
            "description": source.get("description") or source.get("observation") or "Synthetic normalized opportunity",
            "action_type": source.get("action_type"),
            "system": None,
            "uniformat_code": source.get("uniformat_code"),
            "location": source.get("location"),
            "condition_rating": source.get("condition_rating"),
            "intervention_horizon": source.get("intervention_horizon"),
            "source_cost": source.get("source_total_cost"),
            "observation": source.get("observation"),
            "source_proposed_corrective_action": source.get("proposed_corrective_action"),
            "source_lineage": [did] + ([source.get("component_id")] if source.get("component_id") else []),
            "facts_used": [did],
            "interpretation": "Synthetic reference normalization only.",
            "assumptions": [],
            "exceptions": [],
        })

    a = {
        "building_id": bid,
        "site_id": site_id,
        "stage": "OPPORTUNITIES",
        "source_context_id": f"{bid}.site_context.json",
        "agent_version": "synthetic-reference-0.3",
        "rule_versions": [],
        "opportunities": opportunities,
        "stage_exceptions": [],
    }

    overlap_notes = []
    if context.get("initiatives"):
        overlap_notes.extend([f"initiative_overlap_candidate:{x.get('initiative_id')}" for x in context["initiatives"]])
    if context.get("projects"):
        overlap_notes.extend([f"existing_project_overlap:{x.get('project_id')}" for x in context["projects"]])

    base_cost = sum(float(d.get("source_total_cost") or 0) for d in context.get("deficiencies", []))
    b = {
        "building_id": bid,
        "site_id": site_id,
        "stage": "CLUSTERED",
        "rule_versions": ["synthetic-reference-0.3"],
        "work_packages": [{
            "work_package_id": wp_id,
            "title": f"Synthetic reference work package for {bid}",
            "opportunity_ids": opportunity_ids,
            "source_deficiency_ids": deficiency_ids,
            "cluster_ids": [f"CL-{bid}-001"],
            "bundle_type": "bundle" if len(opportunity_ids) > 1 else "standalone",
            "rationale": "Synthetic reference grouping for behavioral testing",
            "bundling_rationale": "Synthetic reference grouping for behavioral testing",
            "blending_rationale": "; ".join(overlap_notes) if overlap_notes else None,
            "proposed_scope": "Synthetic scope preserving all source opportunities.",
            "intervention_horizon": None,
            "intervention_horizon_years": 0,
            "base_cost": base_cost,
            "dependencies": overlap_notes,
            "conflicts": [],
            "assumptions": [],
            "exceptions": [],
        }],
        "stage_exceptions": [],
    }

    c = {
        "building_id": bid,
        "site_id": site_id,
        "stage": "COSTED",
        "cost_basis": {"type": "synthetic_reference_no_escalation"},
        "calculation_date": None,
        "calculation_rule_versions": ["synthetic-reference-0.3"],
        "work_packages": [{
            **b["work_packages"][0],
            "direct_cost": base_cost,
            "base_cost_date": None,
            "indexation_factor": 1.0,
            "index_reference": "synthetic_reference_no_escalation",
            "indexed_direct_cost": base_cost,
            "indirect_cost": 0.0,
            "indirect_costs": [],
            "contingency": 0.0,
            "total_cost": base_cost,
            "calculation_trace": ["Synthetic reference: no indexation or indirect cost applied."],
            "assumptions": [],
            "exceptions": [],
        }],
        "stage_exceptions": [],
    }

    constraints = []
    constraints.extend([f"lease:{x.get('lease_id')} end:{x.get('lease_end_date')}" for x in context.get("leases", [])])
    constraints.extend([f"project:{x.get('project_id')}" for x in context.get("projects", [])])
    constraints.extend([f"initiative:{x.get('initiative_id')}" for x in context.get("initiatives", [])])
    constraints.extend([f"strategic_context:{x.get('strategic_context_id')}" for x in context.get("strategic_context", [])])
    constraints.append(f"detention_band:{context.get('derived_facts', {}).get('detention_band')}")

    accessibility_evidence = [
        f"{x.get('accessibility_assessment_id')} {x.get('compliance_status')}"
        for x in context.get("accessibility", [])
    ]
    occupancy_evidence = [
        f"{x.get('occupancy_id')} service_point:{x.get('service_point_id')}"
        for x in context.get("occupancies", [])
    ]

    recommended_action = "proceed_with_review"
    if context.get("projects"):
        recommended_action = "coordinate_and_avoid_duplicate_scope"
    elif context.get("initiatives"):
        recommended_action = "consider_bundle_or_defer_with_initiative"
    elif context.get("leases") and context.get("derived_facts", {}).get("detention_band") in {"LT_2_YEARS", "2_TO_5_YEARS"}:
        recommended_action = "major_capital_review_before_commitment"
    strategy = context.get("asset_strategy") or {}
    if float(strategy.get("fci") or 0) >= 0.30:
        recommended_action = "strategy_review_due_to_high_condition_burden"

    evidence_lineage = deficiency_ids + [
        x.get("lease_id") for x in context.get("leases", []) if x.get("lease_id")
    ] + [
        x.get("project_id") for x in context.get("projects", []) if x.get("project_id")
    ] + [
        x.get("initiative_id") for x in context.get("initiatives", []) if x.get("initiative_id")
    ] + [
        x.get("strategic_context_id") for x in context.get("strategic_context", []) if x.get("strategic_context_id")
    ]

    t = {
        "building_id": bid,
        "site_id": site_id,
        "stage": "RECOMMENDED",
        "rule_versions": ["synthetic-reference-0.3"],
        "recommendations": [{
            "recommendation_id": f"REC-{bid}-001",
            "work_package_id": wp_id,
            "recommended_action": recommended_action,
            "timing": None,
            "rationale": "Synthetic reference recommendation for behavioral testing.",
            "dependencies": [],
            "constraints": constraints,
            "risks": [],
            "alternatives": [],
            "assumptions": [],
            "exceptions": [],
            "evidence_lineage": evidence_lineage,
            "human_review_required": bool(context.get("leases") or context.get("initiatives") or context.get("projects") or float(strategy.get("fci") or 0) >= 0.30),
            "accessibility_evidence": accessibility_evidence,
            "occupancy_evidence": occupancy_evidence,
            "fci": strategy.get("fci"),
        }],
        "stage_exceptions": [],
    }

    e = {
        "building_id": bid,
        "site_id": site_id,
        "stage": "SUMMARIZED",
        "executive_summary": f"Reference summary for {bid}",
        "work_package_summary": [{
            "work_package_id": wp_id,
            "recommendation_id": f"REC-{bid}-001",
            "recommended_action": recommended_action,
            "source_deficiency_ids": deficiency_ids,
        }],
        "deferred_or_rejected_work_packages": [],
        "major_cost_summary": {"total_cost": base_cost},
        "timing_summary": None,
        "key_dependencies": constraints,
        "key_risks": [],
        "key_decisions": [recommended_action],
        "unresolved_exceptions": context.get("data_quality", {}).get("association_exceptions", []),
        "human_reviews_required": [wp_id] if t["recommendations"][0]["human_review_required"] else [],
        "data_quality_notes": context.get("data_quality", {}).get("warnings", []),
        "source_artifact_version": "synthetic-reference-0.3",
    }
    return {"A": a, "B": b, "C": c, "T": t, "E": e}


def materialize(archetypes_file: Path, output_dir: Path) -> None:
    portfolio = json.loads(archetypes_file.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in portfolio["archetypes"]:
        building_id = item["building_id"]
        building_dir = output_dir / building_id
        building_dir.mkdir(parents=True, exist_ok=True)
        context = build_validated_context(portfolio, building_id)
        (building_dir / "site_context.json").write_text(json.dumps(context, indent=2), encoding="utf-8")
        artifacts = build_reference_artifacts(context)
        for stage, artifact in artifacts.items():
            (building_dir / f"stage_{stage}.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        (building_dir / "run_status.json").write_text(json.dumps({
            "building_id": building_id,
            "data_quality_status": context["data_quality"]["status"],
            "stages_generated": list(artifacts.keys()),
            "blocked_before_agent_a": not bool(artifacts),
        }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    materialize(Path("examples/archetypes/archetypes.json"), Path("examples/archetypes/reference_runs"))
