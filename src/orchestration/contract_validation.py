from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_BY_STAGE = {
    "OPPORTUNITIES": ROOT / "contracts" / "opportunities.schema.json",
    "CLUSTERED": ROOT / "contracts" / "workpackages.schema.json",
    "COSTED": ROOT / "contracts" / "costed-workpackages.schema.json",
    "RECOMMENDED": ROOT / "contracts" / "recommendations.schema.json",
    "SUMMARIZED": ROOT / "contracts" / "building-summary.schema.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_artifact(artifact: dict[str, Any], expected_stage: str) -> list[str]:
    """Validate an artifact against the canonical JSON Schema.

    `jsonschema` is optional at import time so the desktop app can still open in a
    minimal Python environment. Live pipeline advancement, however, should install
    requirements and use full schema validation.
    """
    errors: list[str] = []
    actual_stage = artifact.get("stage")
    if actual_stage != expected_stage:
        errors.append(f"stage mismatch: expected {expected_stage}, got {actual_stage!r}")

    building_id = artifact.get("building_id")
    if not isinstance(building_id, str) or not building_id.strip():
        errors.append("building_id is required")

    schema_path = SCHEMA_BY_STAGE.get(expected_stage)
    if schema_path is None:
        return errors

    try:
        import jsonschema  # type: ignore
    except ImportError:
        errors.append(
            "jsonschema package is not installed; install requirements before live contract validation"
        )
        return errors

    schema = _load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(artifact), key=lambda e: list(e.absolute_path)):
        location = ".".join(str(x) for x in error.absolute_path) or "root"
        errors.append(f"{location}: {error.message}")
    return errors
