import json
from pathlib import Path

import pytest

from src.review.review_store import persist_review


def _review():
    return {
        "review_id": "REV-BLDG-001-001",
        "building_id": "BLDG-001",
        "reviewer_id": "reviewer-123",
        "review_started_at": "2026-08-09T12:00:00Z",
        "review_completed_at": "2026-08-09T12:30:00Z",
        "review_status": "COMPLETED",
        "completion_confirmed": True,
        "work_package_reviews": [
            {
                "work_package_id": "WP-BLDG-001-001",
                "decision": "APPROVE",
                "reviewed_at": "2026-08-09T12:25:00Z",
                "completion_confirmed": True,
            }
        ],
        "audit_events": [],
    }


def test_persist_review_is_immutable_and_indexed(tmp_path: Path):
    review = _review()
    path = persist_review(review, tmp_path)
    assert path.exists()
    envelope = json.loads(path.read_text(encoding="utf-8"))
    assert envelope["review"]["reviewer_id"] == "reviewer-123"
    assert len(envelope["record_hash_sha256"]) == 64
    index_lines = (tmp_path / "review_audit_index.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(index_lines) == 1
    assert json.loads(index_lines[0])["review_id"] == review["review_id"]
    with pytest.raises(FileExistsError):
        persist_review(review, tmp_path)
