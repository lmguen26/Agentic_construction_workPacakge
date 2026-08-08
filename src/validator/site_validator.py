from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_REQUIRED_SOURCES = [
    "site_master",
    "deficiencies",
    "asset_context",
    "lease_or_retention",
    "cost_index",
    "project_constraints",
    "accessibility",
    "energy_or_sustainability",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_site_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    site_id = str(manifest.get("site_id", "")).strip()
    required = manifest.get("required_sources", DEFAULT_REQUIRED_SOURCES)
    sources = manifest.get("sources", {})

    checks = []
    missing = []

    for source_name in required:
        source = sources.get(source_name)
        present = bool(source and source.get("present") is True)
        record_count = int(source.get("record_count", 0)) if source else 0
        valid = present and record_count > 0
        checks.append(
            {
                "source": source_name,
                "present": present,
                "record_count": record_count,
                "valid": valid,
            }
        )
        if not valid:
            missing.append(source_name)

    errors = []
    if not site_id:
        errors.append("site_id is required")

    status = "VALIDATED" if not errors and not missing else "BLOCKED"
    return {
        "site_id": site_id or "UNKNOWN",
        "stage": status,
        "validator": "deterministic-site-validator-v0.1",
        "checks": checks,
        "missing_sources": missing,
        "errors": errors,
        "ready_for_agent_a": status == "VALIDATED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate source completeness for one site.")
    parser.add_argument("manifest", type=Path, help="Path to source manifest JSON")
    parser.add_argument("--output", type=Path, default=Path("site_validation.json"))
    args = parser.parse_args()

    result = validate_site_manifest(load_json(args.manifest))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["stage"] == "VALIDATED" else 2)


if __name__ == "__main__":
    main()
