from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.review.review_store import persist_review


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist an exported human review JSON as an immutable audit record.")
    parser.add_argument("review_file", type=Path)
    parser.add_argument("--store", type=Path, default=Path("data/reviews"))
    args = parser.parse_args()

    review = json.loads(args.review_file.read_text(encoding="utf-8"))
    path = persist_review(review, args.store)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
