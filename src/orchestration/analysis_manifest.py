from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = ROOT / "profiles"

PROFILE_FILES = {
    "LEVEL_0_VALIDATION": PROFILE_DIR / "level-0-validation.json",
    "LEVEL_1_WORK_PACKAGES": PROFILE_DIR / "level-1-work-packages.json",
    "LEVEL_2_STRATEGIC": PROFILE_DIR / "level-2-strategic.json",
    "LEVEL_3_ADVANCED": PROFILE_DIR / "level-3-advanced.json",
}


def load_profile(profile_id: str) -> dict[str, Any]:
    if profile_id not in PROFILE_FILES:
        raise ValueError(f"Unknown profile: {profile_id}")
    return json.loads(PROFILE_FILES[profile_id].read_text(encoding="utf-8"))


def build_manifest(
    building_id: str,
    profile_id: str,
    effort: str | None = None,
    requested_by: str | None = None,
    module_overrides: dict[str, bool] | None = None,
    applicability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if profile_id == "CUSTOM":
        modules = dict(module_overrides or {})
        default_effort = effort or "STANDARD"
    else:
        profile = load_profile(profile_id)
        modules = dict(profile["modules"])
        modules.update(module_overrides or {})
        default_effort = effort or profile.get("default_effort", "STANDARD")

    stamp = datetime.now(timezone.utc).isoformat()
    safe_stamp = stamp.replace(":", "").replace("+00:00", "Z")
    return {
        "analysis_id": f"AN-{building_id}-{safe_stamp}",
        "building_id": building_id,
        "profile_id": profile_id,
        "effort": default_effort,
        "requested_at": stamp,
        "requested_by": requested_by,
        "modules": modules,
        "module_applicability": applicability or {},
        "pipeline_version": "0.3",
        "rule_versions": [],
        "notes": None,
    }
