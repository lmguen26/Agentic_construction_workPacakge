"""Evaluate a saved live Agent A artifact against its synthetic site context."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.context.site_context_builder import build_site_context
from src.evaluation.agent_a_live_evaluator import evaluate_agent_a


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("building_id")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--portfolio", type=Path, default=Path("examples/archetypes/archetypes.json"))
    args = parser.parse_args()

    portfolio = json.loads(args.portfolio.read_text(encoding="utf-8"))
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    context = build_site_context(portfolio, args.building_id)
    result = evaluate_agent_a(context, artifact)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
