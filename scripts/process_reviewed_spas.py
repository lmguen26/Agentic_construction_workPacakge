from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from src.review.extract_spa_feedback import extract_reviewed_spa

ROOT = Path(__file__).resolve().parents[1]
EXCHANGE = ROOT / "spa_exchange"
REVIEWED = EXCHANGE / "reviewed"
EXTRACTED = EXCHANGE / "extracted"
ARCHIVED = EXCHANGE / "archived"
INDEX = EXCHANGE / "processing_index.jsonl"


def process_file(path: Path) -> dict:
    extracted = extract_reviewed_spa(path)
    feedback = extracted["review_feedback"]
    building_id = feedback.get("building_id") or "UNKNOWN"
    artifact_version = feedback.get("source_artifact_version") or "unknown"

    EXTRACTED.mkdir(parents=True, exist_ok=True)
    out = EXTRACTED / f"{building_id}.datasheet.{artifact_version}.review_feedback.json"
    out.write_text(json.dumps(feedback, indent=2, ensure_ascii=False), encoding="utf-8")

    record = {
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "source_spa": str(path.relative_to(ROOT)),
        "feedback_file": str(out.relative_to(ROOT)),
        "building_id": building_id,
        "artifact_version": artifact_version,
        "review_id": feedback.get("review_id"),
        "reviewer_id": feedback.get("reviewer_id"),
        "status": feedback.get("review_status"),
    }
    with INDEX.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def main() -> int:
    REVIEWED.mkdir(parents=True, exist_ok=True)
    files = sorted(REVIEWED.glob("*.html"))
    if not files:
        print("No reviewed SPA files found.")
        return 0

    failures = 0
    for path in files:
        try:
            record = process_file(path)
            print(json.dumps(record, ensure_ascii=False))
        except Exception as exc:
            failures += 1
            print(json.dumps({"source_spa": str(path), "error": str(exc)}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
