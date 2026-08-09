"""Semantic evaluators for A->E agent artifacts.

The evaluator checks required evidence, lineage and prohibited behaviors. It does not
compare exact prose, so prompts/models can evolve without invalidating the test suite.
"""
from __future__ import annotations

from typing import Any


def _walk(value: Any):
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _walk(v)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


def contains_token(artifact: Any, token: str) -> bool:
    token = token.lower()
    return any(token in str(v).lower() for v in _walk(artifact))


def evaluate_lineage(source_ids: list[str], artifact: dict[str, Any]) -> list[str]:
    failures = []
    for source_id in source_ids:
        if not contains_token(artifact, source_id):
            failures.append(f"Missing lineage/reference: {source_id}")
    return failures


def evaluate_accessibility_uncertainty(site_context: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    failures = []
    unknown_ids = [
        r.get("accessibility_assessment_id")
        for r in site_context.get("accessibility", [])
        if r.get("compliance_status") == "unknown"
    ]
    for assessment_id in filter(None, unknown_ids):
        # The downstream artifact must keep the record visible and must not assert it is non-compliant.
        if not contains_token(artifact, assessment_id):
            failures.append(f"Unknown accessibility assessment lost: {assessment_id}")
        text = str(artifact).lower()
        if assessment_id.lower() in text and f"{assessment_id.lower()} non_compliant" in text:
            failures.append(f"Unknown converted to non_compliant: {assessment_id}")
    return failures


def evaluate_multi_occupant(site_context: dict[str, Any], artifact: dict[str, Any]) -> list[str]:
    failures = []
    active_occ = [o for o in site_context.get("occupancies", []) if o.get("is_current") or o.get("occupancy_status") == "active"]
    if len(active_occ) > 1:
        for occ in active_occ:
            if not contains_token(artifact, occ.get("occupancy_id", "")):
                failures.append(f"Occupancy relation lost: {occ.get('occupancy_id')}")
            if not contains_token(artifact, occ.get("service_point_id", "")):
                failures.append(f"Service point relation lost: {occ.get('service_point_id')}")
    return failures


def evaluate_project_overlap(site_context: dict[str, Any], artifact_t: dict[str, Any]) -> list[str]:
    failures = []
    active_projects = [p for p in site_context.get("projects", []) if p.get("project_status") in {"active", "approved", "planned"}]
    if active_projects:
        for project in active_projects:
            pid = project.get("project_id")
            if pid and not contains_token(artifact_t, pid):
                failures.append(f"Existing project not surfaced: {pid}")
    return failures


def evaluate_lease_constraint(site_context: dict[str, Any], artifact_t: dict[str, Any]) -> list[str]:
    failures = []
    active_leases = [l for l in site_context.get("leases", []) if l.get("lease_status") in {"active", "current"}]
    for lease in active_leases:
        lid = lease.get("lease_id")
        if lid and not contains_token(artifact_t, lid):
            failures.append(f"Active lease constraint not surfaced: {lid}")
    return failures


def evaluate_stage_ownership(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    failures = []
    b = artifacts.get("B", {})
    e = artifacts.get("E", {})
    if b and not contains_token(b, "work_package"):
        failures.append("Agent B artifact does not appear to own work-package creation")
    if e and contains_token(e, "new_work_package_created_by_e"):
        failures.append("Agent E created a new work package; E must summarize only")
    return failures


def evaluate_reference_run(site_context: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    deficiency_ids = [d.get("deficiency_id") for d in site_context.get("deficiencies", []) if d.get("deficiency_id")]
    for stage in ["A", "B", "C", "T", "E"]:
        if stage in artifacts:
            failures.extend(evaluate_lineage(deficiency_ids, artifacts[stage]))
    failures.extend(evaluate_multi_occupant(site_context, artifacts.get("T", {})))
    failures.extend(evaluate_accessibility_uncertainty(site_context, artifacts.get("T", {})))
    failures.extend(evaluate_project_overlap(site_context, artifacts.get("T", {})))
    failures.extend(evaluate_lease_constraint(site_context, artifacts.get("T", {})))
    failures.extend(evaluate_stage_ownership(artifacts))
    return failures
