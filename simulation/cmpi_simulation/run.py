"""Top-level orchestration.

Steps:
    1. Register the LLM config, get its UUID.
    2. For each (replicate, day_type), generate the corpus (or reuse cached).
       Generation uses bounded async concurrency via OllamaAsyncClient.
    3. For each (replicate, day_type, algorithm, parameter), run the pipeline cell.
    4. Write per-cell results to data/per_cell.csv (long format).
"""

import asyncio
import csv
import logging
from pathlib import Path

from . import config as cfg
from . import generate, llm_client, pipeline, registries

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

PER_CELL_CSV = cfg.DATA_DIR / "per_cell.csv"


def _load_corpus(corpus_uuid: str) -> dict:
    import json

    path = cfg.DATA_LARGE_DIR / f"{corpus_uuid}.json"
    return json.loads(path.read_text())


async def _ensure_corpus(*, replicate_index: int, day_type: str, llm, llm_options: dict, llm_config_uuid: str) -> dict:
    existing = registries.lookup_corpus(replicate_index=replicate_index, day_type=day_type)
    if existing is not None:
        log.info("Reusing cached corpus %s (rep=%d day=%s)", existing["corpus_uuid"], replicate_index, day_type)
        return _load_corpus(existing["corpus_uuid"])
    log.info("Generating fresh corpus (rep=%d day=%s)", replicate_index, day_type)
    return await generate.generate_corpus_for_day(
        replicate_index=replicate_index,
        day_type=day_type,
        llm=llm,
        llm_options=llm_options,
        llm_config_uuid=llm_config_uuid,
    )


async def main() -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    cfg.DATA_LARGE_DIR.mkdir(parents=True, exist_ok=True)

    llm_config_uuid = registries.register_llm_config(cfg.DEFAULT_LLM_CONFIG)
    log.info("LLM config UUID: %s", llm_config_uuid)

    llm = llm_client.OllamaAsyncClient()

    rows: list[dict] = []
    for replicate_index in range(cfg.N_REPLICATES):
        for day_type in ("low_cmpi", "high_cmpi"):
            corpus = await _ensure_corpus(
                replicate_index=replicate_index,
                day_type=day_type,
                llm=llm,
                llm_options=cfg.DEFAULT_LLM_CONFIG,
                llm_config_uuid=llm_config_uuid,
            )
            # Oracle row.
            oracle = pipeline.run_oracle(corpus=corpus)
            rows.append({
                "replicate_index": replicate_index,
                "day_type": day_type,
                "algorithm": "oracle",
                "parameter": "",
                **oracle,
            })
            # LFA grid.
            for thr in cfg.LFA_THRESHOLD_GRID:
                m = pipeline.run_cell(corpus=corpus, algorithm="lfa", parameter=thr)
                rows.append({
                    "replicate_index": replicate_index,
                    "day_type": day_type,
                    "algorithm": "lfa",
                    "parameter": thr,
                    **m,
                })
            # K-means grid.
            for k in cfg.KMEANS_K_GRID:
                m = pipeline.run_cell(corpus=corpus, algorithm="kmeans", parameter=k)
                rows.append({
                    "replicate_index": replicate_index,
                    "day_type": day_type,
                    "algorithm": "kmeans",
                    "parameter": k,
                    **m,
                })
            # Leiden grid.
            for thr in cfg.LEIDEN_THRESHOLD_GRID:
                m = pipeline.run_cell(corpus=corpus, algorithm="leiden", parameter=thr)
                rows.append({
                    "replicate_index": replicate_index,
                    "day_type": day_type,
                    "algorithm": "leiden",
                    "parameter": thr,
                    **m,
                })

    PER_CELL_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PER_CELL_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["replicate_index", "day_type", "algorithm", "parameter", "recovered_K", "ari", "cmpi_paper", "cmpi_alt"],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    log.info("Wrote %d per-cell rows to %s", len(rows), PER_CELL_CSV)

    # Aggregate.
    from . import aggregate as agg_mod
    agg_mod.aggregate(per_cell_path=PER_CELL_CSV, out_path=cfg.RESULTS_CSV_PATH)
    log.info("Wrote aggregated results to %s", cfg.RESULTS_CSV_PATH)

    # Figures.
    from . import figures as fig_mod
    cfg.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig_mod.figure_a(results_path=cfg.RESULTS_CSV_PATH, out_path=cfg.FIGURES_DIR / "figure_a.png")
    fig_mod.figure_b(results_path=cfg.RESULTS_CSV_PATH, out_path=cfg.FIGURES_DIR / "figure_b.png")
    log.info("Wrote figures to %s", cfg.FIGURES_DIR)


if __name__ == "__main__":
    asyncio.run(main())
