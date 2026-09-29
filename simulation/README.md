# CMPI clustering-sensitivity simulation

Code and data for the Supplementary of Mastitsky et al. (2026), *A
generalisable framework for context-aware measurement of media presence*.
The pipeline generates synthetic news corpora with known story partitions
and sweeps three clustering algorithms (leader–follower, Leiden, $k$-means)
against two salience functions, comparing the Context-Aware Media Presence
Index (CMPI) with its ground-truth (oracle) value. See the Supplementary for
the design and findings.

## Layout

```
cmpi_simulation/   Python package (corpus generation, clustering, salience, CMPI, figures)
tests/             pytest suite for the package
data/              results CSVs and two index files (see below)
data_large/        the 20 synthetic corpora used in the Supplementary (one JSON per replicate and day type)
figures/           Figures A and B of the Supplementary (PNG and PDF)
```

The two index files in `data/`:

- `llm_configs.json`: the LLM settings used to generate the corpora
  (`gemma3:12b`, temperature 1.0, top-p 0.9, …).
- `corpora.json`: which corpus file belongs to which replicate and day type,
  and which LLM settings produced it. The pipeline uses it to reuse the
  included corpora instead of generating new ones.

All paths are relative to this directory and set in `cmpi_simulation/config.py`.
The figures use the Noto Sans font bundled in [`../analysis/fonts/`](../analysis/fonts),
so they don't depend on the fonts installed on your system.

## Reproducing the Supplementary's results

Requires [`uv`](https://docs.astral.sh/uv/). It installs Python 3.11 and the
exact package versions pinned in `uv.lock`.

```bash
uv sync --frozen
uv run --frozen python -m cmpi_simulation.run
```

This re-runs every clustering, CMPI and ARI computation on the included
corpora and rewrites `data/per_cell.csv`, `data/results.csv` and the two
figures. The results files are identical to the included ones, value for
value. The first run downloads the sentence-embedding model
(`sentence-transformers/all-MiniLM-L12-v2`) from Hugging Face.

Run the tests with `uv run --frozen pytest`.

## Generating new corpora

The corpora were generated with a local [Ollama](https://ollama.com) model
(`gemma3:12b`) sampled at temperature 1.0, so their texts cannot be
regenerated word for word; this is why they are included. To generate a
fresh set, back up `data_large/` and `data/corpora.json`, delete them, and
run the command above with Ollama running and `ollama pull gemma3:12b` done.
Generation took 2–3 hours on an Apple M3 Pro. The new texts will differ,
but their structure (cluster sizes, placement of mentions) and the resulting
CMPI distributions follow the same design.
