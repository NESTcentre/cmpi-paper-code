import json
from pathlib import Path

import pytest

from cmpi_simulation import registries


@pytest.fixture
def tmp_registry_paths(tmp_path: Path, monkeypatch):
    """Redirect the registry paths to a tmp dir."""
    llm_path = tmp_path / "llm_configs.json"
    corpora_path = tmp_path / "corpora.json"
    monkeypatch.setattr(registries, "LLM_CONFIGS_PATH", llm_path)
    monkeypatch.setattr(registries, "CORPORA_REGISTRY_PATH", corpora_path)
    return llm_path, corpora_path


def test_register_llm_config_roundtrip(tmp_registry_paths):
    cfg = {"model": "gemma3:4b", "temperature": 0.8}
    uuid_a = registries.register_llm_config(cfg)
    assert isinstance(uuid_a, str) and len(uuid_a) >= 32
    # Same config → same UUID (idempotent for identical dicts).
    uuid_b = registries.register_llm_config(cfg)
    assert uuid_a == uuid_b


def test_register_llm_config_distinct_for_different_configs(tmp_registry_paths):
    cfg1 = {"model": "gemma3:4b", "temperature": 0.8}
    cfg2 = {"model": "gemma3:4b", "temperature": 0.5}
    assert registries.register_llm_config(cfg1) != registries.register_llm_config(cfg2)


def test_get_llm_config_returns_recorded(tmp_registry_paths):
    cfg = {"model": "gemma3:4b", "temperature": 0.8}
    uuid = registries.register_llm_config(cfg)
    assert registries.get_llm_config(uuid) == cfg


def test_corpus_registry_register_and_lookup(tmp_registry_paths):
    entry = {
        "corpus_uuid": "abc-123",
        "replicate_index": 0,
        "day_type": "low_cmpi",
        "llm_config_uuid": "llm-uuid",
        "generation_timestamp_utc": "2026-05-04T12:00:00Z",
        "retry_stats": {"total_llm_calls": 100, "diagnostic_retries": 0, "redraws_after_diagnostic_failure": 0},
    }
    registries.register_corpus(entry)
    looked_up = registries.lookup_corpus(replicate_index=0, day_type="low_cmpi")
    assert looked_up == entry


def test_corpus_registry_returns_none_when_missing(tmp_registry_paths):
    assert registries.lookup_corpus(replicate_index=99, day_type="high_cmpi") is None


def test_llm_configs_file_is_human_readable(tmp_registry_paths):
    llm_path, _ = tmp_registry_paths
    registries.register_llm_config({"model": "gemma3:4b", "temperature": 0.8})
    raw = llm_path.read_text()
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)
    # Pretty-printed (some indentation expected).
    assert "\n" in raw
