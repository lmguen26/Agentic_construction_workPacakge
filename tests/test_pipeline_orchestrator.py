import json
from pathlib import Path

from src.orchestration.analysis_manifest import build_manifest
from src.orchestration.pipeline_orchestrator import prepare_run, run_reference_mode


PORTFOLIO = Path("examples/synthetic_portfolio/portfolio.json")


def load_portfolio():
    return json.loads(PORTFOLIO.read_text(encoding="utf-8"))


def test_prepare_level_1_creates_waiting_agent_a_request(tmp_path):
    manifest = build_manifest("BLDG-001", "LEVEL_1_WORK_PACKAGES")
    result = prepare_run(load_portfolio(), manifest, runs_dir=tmp_path)
    state = result["state"]
    run_dir = Path(result["run_dir"])

    assert state["building_id"] == "BLDG-001"
    assert state["status"] == "WAITING_FOR_AGENT"
    assert state["waiting_for_stage"] == "A"
    assert (run_dir / "site_context.json").exists()
    request = json.loads((run_dir / "next_stage_request.json").read_text(encoding="utf-8"))
    assert request["requested_stage_code"] == "A"
    assert request["expected_stage"] == "OPPORTUNITIES"


def test_level_0_prepares_without_agent_stage(tmp_path):
    manifest = build_manifest("BLDG-001", "LEVEL_0_VALIDATION")
    result = prepare_run(load_portfolio(), manifest, runs_dir=tmp_path)
    state = result["state"]
    run_dir = Path(result["run_dir"])

    assert state["enabled_stages"] == []
    assert state["status"] == "READY_TO_PUBLISH"
    assert not (run_dir / "next_stage_request.json").exists()


def test_reference_level_1_completes_and_generates_spa(tmp_path, monkeypatch):
    manifest = build_manifest("BLDG-001", "LEVEL_1_WORK_PACKAGES")

    import src.orchestration.pipeline_orchestrator as po
    real_publish = po.publish_spa
    monkeypatch.setattr(po, "publish_spa", lambda run_dir: real_publish(run_dir, tmp_path / "spa"))

    result = run_reference_mode(load_portfolio(), manifest, runs_dir=tmp_path / "runs")
    assert result["state"]["status"] == "COMPLETED"
    assert result["state"]["completed_stages"] == ["A", "B", "C", "T", "E"]
    assert Path(result["spa_path"]).exists()
