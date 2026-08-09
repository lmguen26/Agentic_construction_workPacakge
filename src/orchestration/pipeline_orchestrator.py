from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.context.site_context_builder import build_site_context
from src.evaluation.reference_fixture_builder import build_reference_artifacts
from src.orchestration.contract_validation import validate_artifact
from src.quality.data_quality_gate import evaluate_site
from src.spa.building_datasheet import render_building_datasheet

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "data" / "runs"
SPA_GENERATED_DIR = ROOT / "spa_exchange" / "generated"

STAGE_SEQUENCE = [
    ("A", "opportunity_normalization", "OPPORTUNITIES", "agent-a-opportunity", "opportunities.json"),
    ("B", "bundling_blending", "CLUSTERED", "agent-b-workpackage", "work_packages.json"),
    ("C", "costing", "COSTED", "agent-c-cost", "costed_work_packages.json"),
    ("T", "recommendation", "RECOMMENDED", "agent-t-strategy", "recommendations.json"),
    ("E", "executive_summary", "SUMMARIZED", "agent-e-summary", "building_summary.json"),
]


@dataclass(frozen=True)
class StageSpec:
    code: str
    module: str
    stage: str
    agent: str
    filename: str


SPECS = [StageSpec(*row) for row in STAGE_SEQUENCE]
DEPENDENCIES = {"B": "A", "C": "B", "T": "C", "E": "T"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_analysis_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def enabled_specs(manifest: dict[str, Any]) -> list[StageSpec]:
    modules = manifest.get("modules") or {}
    return [spec for spec in SPECS if bool(modules.get(spec.module))]


def validate_manifest_dependencies(manifest: dict[str, Any]) -> list[str]:
    """Protect Custom profiles from impossible stage combinations."""
    enabled = {spec.code for spec in enabled_specs(manifest)}
    errors: list[str] = []
    for child, parent in DEPENDENCIES.items():
        if child in enabled and parent not in enabled:
            errors.append(f"Stage {child} requires enabled upstream stage {parent}")
    if manifest.get("profile_id") == "LEVEL_0_VALIDATION" and enabled:
        errors.append("LEVEL_0_VALIDATION must not enable A/B/C/T/E stages")
    return errors


def _model_hint(spec: StageSpec) -> str:
    if spec.code == "C":
        return "Deterministic Python is authoritative for cost arithmetic; use the agent only for bounded interpretation of approved cost outputs."
    return "Use a strong structured-reasoning model; Claude Opus is preferred when available for high-consequence or early validation runs."


def _stage_request(spec: StageSpec, run_dir: Path, state: dict[str, Any]) -> dict[str, Any]:
    previous = state.get("last_completed_stage")
    inputs = ["site_context.json", "analysis_manifest.json"]
    if previous:
        prev = next((s for s in SPECS if s.code == previous), None)
        if prev:
            inputs.append(f"artifacts/{prev.filename}")
    return {
        "request_version": "0.3",
        "run_id": state["run_id"],
        "building_id": state["building_id"],
        "analysis_id": state["analysis_id"],
        "requested_stage_code": spec.code,
        "expected_stage": spec.stage,
        "copilot_agent": spec.agent,
        "model_selection_hint": _model_hint(spec),
        "required_inputs": inputs,
        "output_path": f"artifacts/{spec.filename}",
        "contract_path": {
            "A": "contracts/opportunities.schema.json",
            "B": "contracts/workpackages.schema.json",
            "C": "contracts/costed-workpackages.schema.json",
            "T": "contracts/recommendations.schema.json",
            "E": "contracts/building-summary.schema.json",
        }[spec.code],
        "instructions": [
            "Use only the requested specialist agent/stage.",
            "Read the analysis manifest and only use enabled capabilities.",
            "Preserve building_id and source/upstream lineage.",
            "Write JSON only to the declared output path.",
            "Do not advance to the next stage yourself; Python validation controls progression.",
        ],
        "created_at": _utc_now(),
        "run_directory": str(run_dir),
    }


def _new_state(manifest: dict[str, Any], quality: dict[str, Any], config_errors: list[str]) -> dict[str, Any]:
    analysis_id = manifest["analysis_id"]
    bid = manifest["building_id"]
    if config_errors:
        status = "CONFIGURATION_INVALID"
    elif quality.get("gate_status") == "BLOCKED":
        status = "BLOCKED"
    else:
        status = "PREPARED"
    return {
        "run_id": f"RUN-{_safe_analysis_id(analysis_id)}",
        "analysis_id": analysis_id,
        "building_id": bid,
        "profile_id": manifest["profile_id"],
        "effort": manifest["effort"],
        "status": status,
        "configuration_errors": config_errors,
        "data_quality_status": quality.get("gate_status"),
        "enabled_stages": [s.code for s in enabled_specs(manifest)],
        "last_completed_stage": None,
        "waiting_for_stage": None,
        "completed_stages": [],
        "stage_validation": {},
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
        "spa_path": None,
    }


def prepare_run(portfolio: dict[str, Any], manifest: dict[str, Any], runs_dir: Path = RUNS_DIR) -> dict[str, Any]:
    bid = manifest["building_id"]
    quality = evaluate_site(portfolio, bid)
    config_errors = validate_manifest_dependencies(manifest)
    context = build_site_context(portfolio, bid)
    context["data_quality_gate"] = quality
    context["analysis_manifest"] = manifest
    context["pipeline_run_id"] = f"RUN-{_safe_analysis_id(manifest['analysis_id'])}"

    run_dir = runs_dir / bid / _safe_analysis_id(manifest["analysis_id"])
    run_dir.mkdir(parents=True, exist_ok=True)
    _write_json(run_dir / "analysis_manifest.json", manifest)
    _write_json(run_dir / "site_context.json", context)
    _write_json(run_dir / "data_quality_gate.json", quality)

    state = _new_state(manifest, quality, config_errors)
    if state["status"] == "PREPARED":
        specs = enabled_specs(manifest)
        if specs:
            state["waiting_for_stage"] = specs[0].code
            state["status"] = "WAITING_FOR_AGENT"
            _write_json(run_dir / "next_stage_request.json", _stage_request(specs[0], run_dir, state))
        else:
            state["status"] = "READY_TO_PUBLISH"
    _write_json(run_dir / "run_state.json", state)
    return {"run_dir": str(run_dir), "state": state, "quality": quality}


def _find_spec(code: str) -> StageSpec:
    for spec in SPECS:
        if spec.code == code:
            return spec
    raise ValueError(f"Unknown stage code: {code}")


def _next_enabled_spec(manifest: dict[str, Any], completed_code: str) -> StageSpec | None:
    specs = enabled_specs(manifest)
    for idx, spec in enumerate(specs):
        if spec.code == completed_code:
            return specs[idx + 1] if idx + 1 < len(specs) else None
    return None


def _merge_for_spa(context: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    merged = dict(context)
    artifacts_dir = run_dir / "artifacts"
    candidates = {
        "opportunities": "opportunities.json",
        "work_packages": "work_packages.json",
        "costed_work_packages": "costed_work_packages.json",
        "recommendations": "recommendations.json",
        "building_summary": "building_summary.json",
    }
    loaded: dict[str, dict[str, Any]] = {}
    for key, filename in candidates.items():
        path = artifacts_dir / filename
        if path.exists():
            loaded[key] = _read_json(path)

    if "opportunities" in loaded:
        merged["opportunities"] = loaded["opportunities"].get("opportunities", [])
    if "work_packages" in loaded:
        merged["work_packages"] = loaded["work_packages"].get("work_packages", [])
    if "costed_work_packages" in loaded:
        merged["costed_work_packages"] = loaded["costed_work_packages"].get("work_packages", [])
    if "recommendations" in loaded:
        merged["recommendations"] = loaded["recommendations"].get("recommendations", [])
    if "building_summary" in loaded:
        merged["building_summary"] = loaded["building_summary"]

    by_id = {wp.get("work_package_id"): dict(wp) for wp in merged.get("work_packages", [])}
    for wp in merged.get("costed_work_packages", []):
        by_id.setdefault(wp.get("work_package_id"), {}).update(wp)
    rec_by_id = {r.get("work_package_id"): r for r in merged.get("recommendations", [])}
    recommended = []
    for wp_id, wp in by_id.items():
        item = dict(wp)
        rec = rec_by_id.get(wp_id)
        if rec:
            item["recommendation_id"] = rec.get("recommendation_id")
            item["recommended_action"] = rec.get("recommended_action")
            item["recommendation_rationale"] = rec.get("rationale")
            item["timing"] = rec.get("timing")
            item["human_review_required"] = rec.get("human_review_required")
        recommended.append(item)
    if recommended:
        merged["recommended_work_packages"] = recommended
    return merged


def publish_spa(run_dir: Path, spa_dir: Path | None = None) -> Path:
    state = _read_json(run_dir / "run_state.json")
    if state.get("status") not in {"READY_TO_PUBLISH", "SPA_GENERATED", "COMPLETED"}:
        raise ValueError(f"Run is not ready to publish; current status={state.get('status')}")
    context = _read_json(run_dir / "site_context.json")
    merged = _merge_for_spa(context, run_dir)
    merged["pipeline_run_id"] = state["run_id"]
    merged["artifact_version"] = "v1.0"
    target_dir = spa_dir or SPA_GENERATED_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output = target_dir / f"{state['building_id']}.datasheet.v1.0.html"
    render_building_datasheet(merged, output)
    state["spa_path"] = str(output)
    state["status"] = "SPA_GENERATED"
    state["updated_at"] = _utc_now()
    _write_json(run_dir / "run_state.json", state)
    return output


def advance_run(run_dir: Path) -> dict[str, Any]:
    state = _read_json(run_dir / "run_state.json")
    manifest = _read_json(run_dir / "analysis_manifest.json")
    if state.get("status") in {"BLOCKED", "CONFIGURATION_INVALID"}:
        return state

    waiting = state.get("waiting_for_stage")
    if not waiting:
        if state.get("status") in {"READY_TO_PUBLISH", "SPA_GENERATED", "COMPLETED"}:
            return state
        raise ValueError("Run has no waiting stage")

    spec = _find_spec(waiting)
    artifact_path = run_dir / "artifacts" / spec.filename
    if not artifact_path.exists():
        state["status"] = "WAITING_FOR_AGENT"
        state["updated_at"] = _utc_now()
        _write_json(run_dir / "run_state.json", state)
        return state

    artifact = _read_json(artifact_path)
    errors = validate_artifact(artifact, spec.stage)
    if artifact.get("building_id") != state["building_id"]:
        errors.append("artifact building_id does not match run building_id")

    state["stage_validation"][spec.code] = {
        "validated_at": _utc_now(),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "artifact": str(artifact_path),
    }
    if errors:
        state["status"] = "STAGE_VALIDATION_FAILED"
        state["updated_at"] = _utc_now()
        _write_json(run_dir / "run_state.json", state)
        return state

    if spec.code not in state["completed_stages"]:
        state["completed_stages"].append(spec.code)
    state["last_completed_stage"] = spec.code
    next_spec = _next_enabled_spec(manifest, spec.code)
    if next_spec:
        state["waiting_for_stage"] = next_spec.code
        state["status"] = "WAITING_FOR_AGENT"
        _write_json(run_dir / "next_stage_request.json", _stage_request(next_spec, run_dir, state))
    else:
        state["waiting_for_stage"] = None
        state["status"] = "READY_TO_PUBLISH"
        request = run_dir / "next_stage_request.json"
        if request.exists():
            request.unlink()
    state["updated_at"] = _utc_now()
    _write_json(run_dir / "run_state.json", state)
    return state


def run_reference_mode(portfolio: dict[str, Any], manifest: dict[str, Any], runs_dir: Path = RUNS_DIR, spa_dir: Path | None = None) -> dict[str, Any]:
    """Exercise orchestration using deterministic synthetic A-E fixtures.

    This verifies control flow and contracts only. It is not a substitute for live
    semantic agents and must never be interpreted as a production recommendation.
    """
    prepared = prepare_run(portfolio, manifest, runs_dir=runs_dir)
    run_dir = Path(prepared["run_dir"])
    state = prepared["state"]
    if state["status"] in {"BLOCKED", "CONFIGURATION_INVALID"}:
        return prepared

    context = _read_json(run_dir / "site_context.json")
    refs = build_reference_artifacts(context)
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    for spec in enabled_specs(manifest):
        ref = refs.get(spec.code)
        if ref is None:
            raise ValueError(f"Reference fixture unavailable for enabled stage {spec.code}")
        _write_json(artifacts_dir / spec.filename, ref)
        state = advance_run(run_dir)
        if state.get("status") == "STAGE_VALIDATION_FAILED":
            break

    if state.get("status") == "READY_TO_PUBLISH":
        spa = publish_spa(run_dir, spa_dir=spa_dir)
        state = _read_json(run_dir / "run_state.json")
        state["status"] = "COMPLETED"
        state["updated_at"] = _utc_now()
        _write_json(run_dir / "run_state.json", state)
        return {"run_dir": str(run_dir), "state": state, "spa_path": str(spa)}
    return {"run_dir": str(run_dir), "state": state}
