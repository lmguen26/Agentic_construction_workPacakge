from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.pipeline_orchestrator import advance_run, prepare_run, publish_spa, run_reference_mode

DEFAULT_PORTFOLIO = ROOT / "examples" / "synthetic_portfolio" / "portfolio.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manifest-driven building pipeline orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser("prepare", help="Prepare a run and create the next Copilot stage request")
    p_prepare.add_argument("manifest", type=Path)
    p_prepare.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)

    p_advance = sub.add_parser("advance", help="Validate the waiting stage artifact and advance the run")
    p_advance.add_argument("run_dir", type=Path)

    p_publish = sub.add_parser("publish", help="Generate the versioned review SPA from completed artifacts")
    p_publish.add_argument("run_dir", type=Path)

    p_reference = sub.add_parser("reference", help="Run the complete deterministic reference pipeline")
    p_reference.add_argument("manifest", type=Path)
    p_reference.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)

    args = parser.parse_args()

    if args.command == "prepare":
        result = prepare_run(load_json(args.portfolio), load_json(args.manifest))
    elif args.command == "advance":
        result = advance_run(args.run_dir)
    elif args.command == "publish":
        result = {"spa_path": str(publish_spa(args.run_dir))}
    else:
        result = run_reference_mode(load_json(args.portfolio), load_json(args.manifest))

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
