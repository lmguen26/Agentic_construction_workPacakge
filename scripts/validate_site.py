from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.quality.data_quality_gate import evaluate_site


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Data Quality Gate for one building.")
    parser.add_argument("building_id")
    parser.add_argument("--portfolio", default="examples/synthetic_portfolio/portfolio.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    portfolio = json.loads(Path(args.portfolio).read_text(encoding="utf-8"))
    result = evaluate_site(portfolio, args.building_id)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    return 2 if result.get("gate_status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
