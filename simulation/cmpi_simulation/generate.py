"""Per-day corpus generation: per-cluster canonical-plus-platform-variants flow.

Each ground-truth cluster is generated as ONE canonical wire-service brief plus
(size - 1) platform-style rewrites of the canonical (Telegram, VK, OK, Twitter,
wire-service brief, blog). This reproduces the cross-platform repost pattern
observed in real production semantic groups and gives clusters tight intra-cluster
cohesion that the embedder + leader-follower can recover at a fixed threshold.

is_titled and placement_profile are drawn once per cluster; canonical and variants
inherit them. Concurrency: bounded by asyncio.Semaphore(cfg.OLLAMA_CONCURRENCY).
The Ollama daemon must be started with OLLAMA_NUM_PARALLEL >= that for parallelism
to materialise.

Verify-and-retry policy. After generation, each document is verified for
protagonist placement: the slot of the protagonist's first occurrence is compared
to the slot drawn for the cluster. A document whose first mention falls in the
wrong slot triggers up to N_RETRIES_PER_PROMPT (default 3) same-prompt retries,
followed by N_DIAGNOSTIC_RETRIES (default 1) diagnostic retries that reformulate
the prompt with the slot constraint emphasised. If all attempts still fail for a
variant, the variant falls through the remaining five platform styles in turn
(see generate_variant) and picks the first that produces a valid document. The
full ten-replicate run produced no aborts under this fallback chain.
"""

import asyncio
import datetime as dt
import json
import logging
from typing import Optional

import numpy as np

from . import config as cfg
from . import prompts, registries, retry, topics

log = logging.getLogger(__name__)


def _placement_profile_draw(rng: np.random.Generator) -> str:
    profiles = list(cfg.PLACEMENT_PROBABILITIES.keys())
    weights = list(cfg.PLACEMENT_PROBABILITIES.values())
    return rng.choice(profiles, p=weights).item()


def _is_titled_draw(rng: np.random.Generator) -> bool:
    return bool(rng.random() < cfg.P_TITLED)


def _build_cluster_specs(day_type: str, rng: np.random.Generator) -> list[dict]:
    """Build 10 cluster-level specs. is_titled and placement_profile are drawn
    once per cluster; all docs in the cluster inherit them."""
    catalogue = topics.CATALOGUE[day_type]
    day_cfg = cfg.DAY_CONFIGS[day_type]
    sizes = list(day_cfg["protagonist_cluster_sizes"]) + list(day_cfg["non_protagonist_cluster_sizes"])

    specs: list[dict] = []
    for size, cluster in zip(sizes, catalogue, strict=True):
        is_titled = _is_titled_draw(rng)
        placement_profile = _placement_profile_draw(rng) if cluster["protagonist"] else "none"
        specs.append({
            "true_cluster": cluster["cluster_index"],
            "size": int(size),
            "story_angle": cluster["story_angle"],
            "sub_story_focus": cluster.get("sub_story_focus"),
            "parent_event": cluster.get("parent_event", "none"),
            "is_titled": is_titled,
            "placement_profile": placement_profile,
            "entity_present": cluster["protagonist"],
        })
    assert len(specs) == 10
    return specs


def _parent_event_context(parent_event: str) -> Optional[str]:
    if parent_event == "none":
        return None
    return parent_event


def _canonical_text(spec: dict, canonical: dict) -> str:
    """Reconstruct the canonical doc as a single string for variant prompts to rewrite."""
    if spec["is_titled"] and canonical["title"]:
        return f"TITLE: {canonical['title']}\n\n{canonical['body']}"
    return canonical["body"]


async def generate_corpus_for_day(
    *,
    replicate_index: int,
    day_type: str,
    llm,
    llm_options: dict,
    llm_config_uuid: str,
) -> dict:
    """Generate one cached corpus for (replicate_index, day_type).

    `llm` must implement AsyncLLMClient. Returns the on-disk corpus dict (also writes
    it to disk and registers it).
    """
    rng = np.random.default_rng(seed=(replicate_index * 1000 + (0 if day_type == "low_cmpi" else 1)))
    cluster_specs = _build_cluster_specs(day_type, rng)
    sem = asyncio.Semaphore(cfg.OLLAMA_CONCURRENCY)

    # ----- Phase 1: canonicals (one per cluster) -----
    async def _gen_canonical(spec: dict) -> dict:
        primary = prompts.primary_prompt(
            is_titled=spec["is_titled"],
            placement_profile=spec["placement_profile"],
            story_angle=spec["story_angle"],
            sub_story_focus=spec["sub_story_focus"],
            parent_event_context=_parent_event_context(spec["parent_event"]),
            entity_name=cfg.ENTITY_NAME,
        )

        def diag_builder(draft: str, reason: str, _spec=spec) -> str:
            return prompts.diagnostic_prompt(
                is_titled=_spec["is_titled"],
                placement_profile=_spec["placement_profile"],
                story_angle=_spec["story_angle"],
                sub_story_focus=_spec["sub_story_focus"],
                parent_event_context=_parent_event_context(_spec["parent_event"]),
                entity_name=cfg.ENTITY_NAME,
                previous_draft=draft,
                failure_reason=reason,
            )

        async with sem:
            return await retry.generate_doc_with_retries_async(
                llm=llm,
                primary_prompt=primary,
                diagnostic_prompt_builder=diag_builder,
                options=llm_options,
                is_titled=spec["is_titled"],
                placement_profile=spec["placement_profile"],
                entity_name=cfg.ENTITY_NAME,
                n_same_prompt_retries=cfg.N_SAME_PROMPT_RETRIES,
                n_diagnostic_retries=cfg.N_DIAGNOSTIC_RETRIES,
            )

    canonical_tasks = [asyncio.create_task(_gen_canonical(s)) for s in cluster_specs]
    canonical_results = await asyncio.gather(*canonical_tasks)

    for spec, c in zip(cluster_specs, canonical_results):
        if not c["accepted"]:
            raise RuntimeError(
                f"Cluster {spec['true_cluster']} canonical generation failed after retries; "
                f"aborting replicate {replicate_index} day {day_type}."
            )

    # ----- Phase 2: variants (size - 1 per cluster, cycled through PLATFORM_STYLES) -----
    async def _try_one_platform(spec: dict, canonical_text: str, platform: dict) -> dict:
        """One full retry cycle with a given platform style. Tagged with platform name."""
        primary = prompts.variant_prompt(
            canonical_text=canonical_text,
            platform_instruction=platform["instruction"],
            is_titled=spec["is_titled"],
            placement_profile=spec["placement_profile"],
            entity_name=cfg.ENTITY_NAME,
        )

        def diag_builder(draft: str, reason: str, _spec=spec, _can=canonical_text, _p=platform) -> str:
            return prompts.variant_diagnostic_prompt(
                canonical_text=_can,
                platform_instruction=_p["instruction"],
                is_titled=_spec["is_titled"],
                placement_profile=_spec["placement_profile"],
                entity_name=cfg.ENTITY_NAME,
                previous_draft=draft,
                failure_reason=reason,
            )

        async with sem:
            result = await retry.generate_doc_with_retries_async(
                llm=llm,
                primary_prompt=primary,
                diagnostic_prompt_builder=diag_builder,
                options=llm_options,
                is_titled=spec["is_titled"],
                placement_profile=spec["placement_profile"],
                entity_name=cfg.ENTITY_NAME,
                n_same_prompt_retries=cfg.N_SAME_PROMPT_RETRIES,
                n_diagnostic_retries=cfg.N_DIAGNOSTIC_RETRIES,
            )
        result["platform"] = platform["name"]
        return result

    async def _gen_variant(spec: dict, canonical_text: str, variant_idx: int) -> dict:
        """Generate one variant. If the first platform's retry cycle fails, fall back through
        the remaining platforms in PLATFORM_STYLES order before raising."""
        n = len(cfg.PLATFORM_STYLES)
        result = None
        for offset in range(n):
            platform = cfg.PLATFORM_STYLES[(variant_idx + offset) % n]
            attempt = await _try_one_platform(spec, canonical_text, platform)
            if result is None:
                result = attempt  # remember the first attempt for accounting
            else:
                attempt["call_count"] += result["call_count"]
                result = attempt
            if attempt["accepted"]:
                return result
        return result  # all platforms failed; caller decides what to do

    canonical_bodies = [_canonical_text(s, c) for s, c in zip(cluster_specs, canonical_results)]

    variant_results_per_cluster: list[list[dict]] = []
    for spec, canonical_text in zip(cluster_specs, canonical_bodies):
        n_variants = spec["size"] - 1
        tasks = [asyncio.create_task(_gen_variant(spec, canonical_text, i)) for i in range(n_variants)]
        variant_results_per_cluster.append(await asyncio.gather(*tasks))

    # All variants now attempt every platform via _gen_variant's internal fallback loop.
    # If a variant is still not accepted after exhausting all platforms, abort.
    redraws = 0
    for cluster_idx, (spec, variants) in enumerate(zip(cluster_specs, variant_results_per_cluster)):
        for v_idx, v in enumerate(variants):
            if not v["accepted"]:
                raise RuntimeError(
                    f"Cluster {spec['true_cluster']} variant {v_idx} (placement={spec['placement_profile']}) "
                    f"failed across all {len(cfg.PLATFORM_STYLES)} platform styles; "
                    f"aborting replicate {replicate_index} day {day_type}."
                )
            # Track how often we had to fall back to a non-canonical platform index.
            expected_platform = cfg.PLATFORM_STYLES[v_idx % len(cfg.PLATFORM_STYLES)]["name"]
            if v["platform"] != expected_platform:
                redraws += 1

    # ----- Assemble documents (cluster-grouped, canonical first) -----
    documents: list[dict] = []
    total_calls = 0
    diag_count = 0
    for spec, canonical, variants in zip(cluster_specs, canonical_results, variant_results_per_cluster):
        first_slot = None if spec["placement_profile"] == "none" else int(spec["placement_profile"][-1])
        total_calls += canonical["call_count"]
        if canonical["used_diagnostic"]:
            diag_count += 1
        documents.append({
            "doc_id": registries.new_corpus_uuid(),
            "arrival_index": -1,
            "true_cluster": spec["true_cluster"],
            "is_titled": spec["is_titled"],
            "title": canonical["title"],
            "body": canonical["body"],
            "sentences": canonical["sentences"],
            "placement_profile": spec["placement_profile"],
            "platform": "canonical",
            "entity_present": spec["entity_present"],
            "first_slot": first_slot,
        })
        for v in variants:
            total_calls += v["call_count"]
            if v["used_diagnostic"]:
                diag_count += 1
            documents.append({
                "doc_id": registries.new_corpus_uuid(),
                "arrival_index": -1,
                "true_cluster": spec["true_cluster"],
                "is_titled": spec["is_titled"],
                "title": v["title"],
                "body": v["body"],
                "sentences": v["sentences"],
                "placement_profile": spec["placement_profile"],
                "platform": v["platform"],
                "entity_present": spec["entity_present"],
                "first_slot": first_slot,
            })

    assert len(documents) == 100, f"Expected 100 docs, got {len(documents)}"

    perm = rng.permutation(len(documents))
    for new_pos, original_pos in enumerate(perm, start=1):
        documents[original_pos]["arrival_index"] = int(new_pos)

    corpus_uuid = registries.new_corpus_uuid()
    corpus = {
        "metadata": {
            "corpus_uuid": corpus_uuid,
            "replicate_index": replicate_index,
            "day_type": day_type,
            "llm_config_uuid": llm_config_uuid,
            "generation_timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "retry_stats": {
                "total_llm_calls": total_calls,
                "diagnostic_retries": diag_count,
                "redraws_after_diagnostic_failure": redraws,
            },
        },
        "documents": documents,
    }

    cfg.DATA_LARGE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = cfg.DATA_LARGE_DIR / f"{corpus_uuid}.json"
    out_path.write_text(json.dumps(corpus, indent=2) + "\n")
    registries.register_corpus({
        "corpus_uuid": corpus_uuid,
        "replicate_index": replicate_index,
        "day_type": day_type,
        "llm_config_uuid": llm_config_uuid,
        "generation_timestamp_utc": corpus["metadata"]["generation_timestamp_utc"],
        "retry_stats": corpus["metadata"]["retry_stats"],
    })
    return corpus
