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


def _source_ref(context: dict[str, Any]) -> list[str]:
    return [d["deficiency_id"] for d in context.get("deficiencies", []) if d.get("deficiency_id")]


def build_reference_artifacts(context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if context.get("data_quality", {}).get("status") == "BLOCKED":
        return {}

    bid = context["building_id"]
    deficiency_ids = _source_ref(context)
    opportunity_ids = [f"OPP-{x}" for x in deficiency_ids]
    wp_id = f"WP-{bid}-001"

    a = {
        "pipeline_state": "OPPORTUNITIES",
        "site_id": bid,
        "opportunities": [
            {"opportunity_id": oid, "source_deficiency_id": did, "site_id": bid, "source_lineage": [did]}
            for oid, did in zip(opportunity_ids, deficiency_ids)
        ],
    }

    overlap_notes = []
    if context.get("initiatives"):
        overlap_notes.extend([f"initiative_overlap_candidate:{x.get('initiative_id')}" for x in context["initiatives"]])
    if context.get("projects"):
        overlap_notes.extend([f"existing_project_overlap:{x.get('project_id')}" for x in context["projects"]])

    b = {
        "pipeline_state": "CLUSTERED",
        "site_id": bid,
        "work_packages": [{
            "work_package_id": wp_id,
            "included_opportunity_ids": opportunity_ids,
            "source_deficiency_ids": deficiency_ids,
            "bundling_rationale": "Synthetic reference grouping for behavioral testing",
            "blending_rationale": overlap_notes,
        }],
    }

    base_cost = sum(float(d.get("source_total_cost") or 0) for d in context.get("deficiencies", []))
    c = {
        "pipeline_state": "COSTED",
        "site_id": bid,
        "costed_work_packages": [{
            "work_package_id": wp_id,
            "source_deficiency_ids": deficiency_ids,
            "base_cost": base_cost,
            "indexed_cost": base_cost,
            "indirect_costs": [],
            "total_estimated_cost": base_cost,
            "calculation_rule_versions": ["synthetic-reference-0.2.2"],
        }],
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

    recommendation = "proceed_with_review"
    if context.get("projects"):
        recommendation = "coordinate_and_avoid_duplicate_scope"
    elif context.get("initiatives"):
        recommendation = "consider_bundle_or_defer_with_initiative"
    elif context.get("leases") and context.get("derived_facts", {}).get("detention_band") in {"LT_2_YEARS", "2_TO_5_YEARS"}:
        recommendation = "major_capital_review_before_commitment"
    strategy = context.get("asset_strategy") or {}
    if float(strategy.get("fci") or 0) >= 0.30:
        recommendation = "strategy_review_due_to_high_condition_burden"

    t = {
        "pipeline_state": "RECOMMENDED",
        "site_id": bid,
        "recommendations": [{
            "recommendation_id": f"REC-{bid}-001",
            "work_package_id": wp_id,
            "source_deficiency_ids": deficiency_ids,
            "recommendation": recommendation,
            "constraints": constraints,
            "accessibility_evidence": accessibility_evidence,
            "occupancy_evidence": occupancy_evidence,
            "fci": strategy.get("fci"),
            "human_review_required": bool(context.get("leases") or context.get("initiatives") or context.get("projects") or float(strategy.get("fci") or 0) >= 0.30),
        }],
    }

    e = {
        "pipeline_state": "SUMMARIZED",
        "site_id": bid,
        "executive_summary": f"Reference summary for {bid}",
        "recommended_work_packages": [{"work_package_id": wp_id, "recommendation_id": f"REC-{bid}-001", "source_deficiency_ids": deficiency_ids}],
        "unresolved_exceptions": context.get("data_quality", {}).get("association_exceptions", []),
    }
    return {"A": a, "B": b, "C": c, "T": t, "E": e}


def materialize(archetypes_file: Path, output_dir: Path) -> None:
    portfolio = json.loads(archetypes_file.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in portfolio["archetypes"]:
        building_id = item["building_id"]
        site_dir = output_dir / building_id
        site_dir.mkdir(parents=True, exist_ok=True)
        context = build_site_context(portfolio, building_id)
        (site_dir / "site_context.json").write_text(json.dumps(context, indent=2), encoding="utf-8")
        artifacts = build_reference_artifacts(context)
        for stage, artifact in artifacts.items():
            (site_dir / f"stage_{stage}.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")


if __name__ == "__main__":
    materialize(Path("examples/archetypes/archetypes.json"), Path("examples/archetypes/reference_runs"))
