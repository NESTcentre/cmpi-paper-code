"""LLM-config and corpus registries.

Both are simple JSON dicts on disk. Identifiers are UUIDs.

LLM-config registry (data/llm_configs.json):
    { "<uuid>": { ... config dict ... }, ... }

Corpus registry (data/corpora.json):
    { "<corpus_uuid>": { replicate_index, day_type, llm_config_uuid,
                          generation_timestamp_utc, retry_stats }, ... }

Identical config dicts collapse to the same UUID via deterministic hashing of the canonical form.
"""

import hashlib
import json
import uuid
from typing import Optional

from .config import CORPORA_REGISTRY_PATH, LLM_CONFIGS_PATH


def _ensure_parent(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def _load(path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path, data: dict) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _config_uuid(cfg: dict) -> str:
    """Deterministic UUIDv5 from canonical JSON of cfg, so identical configs collapse to one entry."""
    canonical = json.dumps(cfg, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).digest()
    return str(uuid.UUID(bytes=digest[:16], version=5))


def register_llm_config(cfg: dict) -> str:
    """Register an LLM config and return its UUID. Idempotent: same cfg always returns same UUID."""
    registry = _load(LLM_CONFIGS_PATH)
    cfg_uuid = _config_uuid(cfg)
    if cfg_uuid not in registry:
        registry[cfg_uuid] = cfg
        _save(LLM_CONFIGS_PATH, registry)
    return cfg_uuid


def get_llm_config(cfg_uuid: str) -> dict:
    registry = _load(LLM_CONFIGS_PATH)
    return registry[cfg_uuid]


def register_corpus(entry: dict) -> None:
    """Register a corpus entry. Keyed by entry['corpus_uuid']."""
    registry = _load(CORPORA_REGISTRY_PATH)
    registry[entry["corpus_uuid"]] = entry
    _save(CORPORA_REGISTRY_PATH, registry)


def lookup_corpus(*, replicate_index: int, day_type: str) -> Optional[dict]:
    """Find a corpus entry matching (replicate_index, day_type), or None."""
    registry = _load(CORPORA_REGISTRY_PATH)
    for entry in registry.values():
        if entry["replicate_index"] == replicate_index and entry["day_type"] == day_type:
            return entry
    return None


def new_corpus_uuid() -> str:
    """Mint a fresh UUID for a new corpus."""
    return str(uuid.uuid4())
