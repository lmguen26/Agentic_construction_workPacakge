from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cost_package(base_cost: float, years: float, annual_index_rate: float, indirect_rate: float, contingency_rate: float) -> dict:
    factor = (1 + annual_index_rate) ** years
    indexed = round(base_cost * factor, 2)
    indirect = round(indexed * indirect_rate, 2)
    contingency = round((indexed + indirect) * contingency_rate, 2)
    total = round(indexed + indirect + contingency, 2)
    return {
        "direct_cost": round(base_cost, 2),
        "indexation_factor": round(factor, 6),
        "indexed_direct_cost": indexed,
        "indirect_cost": indirect,
        "indirect_costs": [{"type": "aggregate_indirect", "rate": indirect_rate, "amount": indirect}],
        "contingency": contingency,
        "total_cost": total,
        "calculation_trace": [
            f"indexation=(1+{annual_index_rate})^{years}",
            f"indirect={indirect_rate} x indexed_direct_cost",
            f"contingency={contingency_rate} x (indexed_direct_cost + indirect_cost)",
        ],
        "assumptions": [],
        "exceptions": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workpackages", type=Path)
    parser.add_argument("rules", type=Path)
    parser.add_argument("--output", type=Path, default=Path("work_packages_costed.json"))
    args = parser.parse_args()

    payload = load_json(args.workpackages)
    rules_payload = load_json(args.rules)
    rules = rules_payload["costing"]
    rule_version = rules_payload.get("version") or rules.get("version") or "unknown"
    result = {
        "building_id": payload["building_id"],
        "site_id": payload.get("site_id"),
        "stage": "COSTED",
        "cost_basis": rules,
        "calculation_date": None,
        "calculation_rule_versions": [str(rule_version)],
        "work_packages": [],
        "stage_exceptions": [],
    }

    for wp in payload["work_packages"]:
        base_cost = float(wp.get("base_cost") or 0)
        years = float(wp.get("intervention_horizon_years") or 0)
        cost = cost_package(base_cost, years, rules["annual_index_rate"], rules["indirect_cost_rate"], rules["contingency_rate"])
        result["work_packages"].append({**wp, **cost})

    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
