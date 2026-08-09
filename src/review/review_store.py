from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def persist_review(review: dict[str, Any], store_dir: Path) -> Path:
    """Persist a review as an immutable JSON record and append an audit-index entry.

    Existing review files are never overwritten. A duplicate review_id is rejected.
    """
    required = ["review_id", "building_id", "reviewer_id", "review_started_at", "review_status", "work_package_reviews"]
    missing = [k for k in required if not review.get(k)]
    if missing:
        raise ValueError(f"Missing required review fields: {', '.join(missing)}")

    store_dir.mkdir(parents=True, exist_ok=True)
    review_id = str(review["review_id"])
    building_id = str(review["building_id"])
    safe_review_id = "".join(c for c in review_id if c.isalnum() or c in "-_")
    record_path = store_dir / f"{building_id}__{safe_review_id}.review.json"
    if record_path.exists():
        raise FileExistsError(f"Review already exists: {record_path}")

    envelope = {
        "stored_at": _utc_now(),
        "record_hash_sha256": _digest(review),
        "review": review,
    }
    record_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")

    index_path = store_dir / "review_audit_index.jsonl"
    index_entry = {
        "stored_at": envelope["stored_at"],
        "building_id": building_id,
        "review_id": review_id,
        "reviewer_id": review["reviewer_id"],
        "review_status": review["review_status"],
        "review_started_at": review["review_started_at"],
        "review_completed_at": review.get("review_completed_at"),
        "completion_confirmed": bool(review.get("completion_confirmed")),
        "record_hash_sha256": envelope["record_hash_sha256"],
        "record_file": record_path.name,
    }
    with index_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

    return record_path
