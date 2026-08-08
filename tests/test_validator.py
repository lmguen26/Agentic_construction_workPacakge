from src.validator.site_validator import validate_site_manifest


def test_valid_manifest_passes():
    manifest = {
        "site_id": "SITE-1",
        "required_sources": ["a", "b"],
        "sources": {
            "a": {"present": True, "record_count": 1},
            "b": {"present": True, "record_count": 2},
        },
    }
    result = validate_site_manifest(manifest)
    assert result["stage"] == "VALIDATED"
    assert result["ready_for_agent_a"] is True


def test_missing_source_blocks_pipeline():
    manifest = {
        "site_id": "SITE-1",
        "required_sources": ["a", "b"],
        "sources": {"a": {"present": True, "record_count": 1}},
    }
    result = validate_site_manifest(manifest)
    assert result["stage"] == "BLOCKED"
    assert "b" in result["missing_sources"]
