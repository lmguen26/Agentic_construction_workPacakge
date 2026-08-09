"""Extract machine-readable context and review metadata from a reviewed HTML SPA.

The SPA is treated as a portable review package. Agents should consume the embedded
JSON payloads rather than scrape rendered HTML text.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _extract_script_json(html_text: str, element_id: str) -> dict[str, Any]:
    pattern = rf'<script[^>]*id=["\']{re.escape(element_id)}["\'][^>]*>(.*?)</script>'
    match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise ValueError(f"Embedded JSON block not found: {element_id}")
    raw = match.group(1).strip().replace("<\\/", "</")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"Embedded JSON block {element_id} must contain an object")
    return value


def extract_review_package(html_path: Path) -> dict[str, Any]:
    text = html_path.read_text(encoding="utf-8")
    context = _extract_script_json(text, "site-context")
    review = _extract_script_json(text, "review-metadata")
    return {
        "package_type": "REVIEWED_BUILDING_DATASHEET",
        "building_id": context.get("building_id"),
        "site_context": context,
        "review_metadata": review,
        "source_html": html_path.name,
    }


def review_to_feedback(review_package: dict[str, Any]) -> dict[str, Any]:
    review = review_package["review_metadata"]
    wp_feedback = []
    for item in review.get("work_package_reviews", []):
        decision = item.get("decision", "NOT_REVIEWED")
        requested_actions: list[str] = []
        if item.get("scope_change_requested"):
            requested_actions.append("REVIEW_SCOPE")
        if item.get("cost_review_required"):
            requested_actions.append("RECALCULATE_COST")
        if item.get("timing_review_required"):
            requested_actions.append("REVIEW_TIMING")
        if item.get("risk_review_required"):
            requested_actions.append("REVIEW_RISK")
        if decision == "RETURN_FOR_REVISION":
            requested_actions.append("REVISE_WORK_PACKAGE")
        elif decision == "APPROVE_WITH_CHANGES":
            requested_actions.append("APPLY_APPROVED_CHANGES")
        elif decision == "DEFER":
            requested_actions.append("REVIEW_DEFERRAL")
        elif decision == "REJECT":
            requested_actions.append("PRESERVE_REJECTION_AND_REVIEW_ALTERNATIVE")

        wp_feedback.append({
            "work_package_id": item.get("work_package_id"),
            "decision": decision,
            "reviewer_comment": item.get("reviewer_comment"),
            "scope_change_requested": bool(item.get("scope_change_requested")),
            "cost_review_required": bool(item.get("cost_review_required")),
            "timing_review_required": bool(item.get("timing_review_required")),
            "risk_review_required": bool(item.get("risk_review_required")),
            "requested_actions": requested_actions,
            "authoritative_fact_change_requested": False,
            "requires_source_update": False,
            "requires_human_escalation": decision == "NOT_REVIEWED",
        })

    revision_items = [x for x in wp_feedback if x["decision"] not in {"APPROVE"}]
    if any(x["requires_human_escalation"] for x in wp_feedback):
        status = "HUMAN_ESCALATION_REQUIRED"
    elif not revision_items:
        status = "NO_REVISION_REQUIRED"
    elif len(revision_items) == len(wp_feedback):
        status = "REVISION_REQUIRED"
    else:
        status = "PARTIAL_REVISION_REQUIRED"

    return {
        "feedback_id": f"FDBK-{review.get('review_id') or 'UNKNOWN'}",
        "building_id": review_package.get("building_id"),
        "pipeline_run_id": review.get("pipeline_run_id"),
        "source_review_id": review.get("review_id"),
        "source_artifact_version": review.get("artifact_version"),
        "reviewer_id": review.get("reviewer_id"),
        "review_completed_at": review.get("review_completed_at"),
        "feedback_status": status,
        "overall_comment": review.get("overall_comment"),
        "work_package_feedback": wp_feedback,
        "agent_revision_constraints": {
            "preserve_source_facts": True,
            "preserve_original_work_package_ids": True,
            "allow_new_work_package_version": True,
            "prohibit_silent_scope_change": True,
            "prohibit_silent_cost_change": True,
        },
    }
