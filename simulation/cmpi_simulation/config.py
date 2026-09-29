"""Configuration constants for the clustering-sensitivity simulation.

All design parameters live here. No I/O, no logic — just data.
"""

from pathlib import Path

# Output paths, relative to the project directory (the one containing this package).
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DATA_LARGE_DIR = REPO_ROOT / "data_large"
FIGURES_DIR = REPO_ROOT / "figures"
# Noto Sans, shared with the R analysis so all figures use the same font.
FONTS_DIR = REPO_ROOT.parent / "analysis" / "fonts"

LLM_CONFIGS_PATH = DATA_DIR / "llm_configs.json"
CORPORA_REGISTRY_PATH = DATA_DIR / "corpora.json"
RESULTS_CSV_PATH = DATA_DIR / "results.csv"

# Entity. Fictional, unique surface form.
ENTITY_NAME = "Aleksander Norvik"
ENTITY_COUNTRY = "Veridia"
ENTITY_ROLE = "Prime Minister"

# Day configurations (cluster size lists).
DAY_CONFIGS = {
    "low_cmpi": {
        "protagonist_cluster_sizes": [25, 15],
        "non_protagonist_cluster_sizes": [15, 10, 10, 5, 5, 5, 5, 5],
    },
    "high_cmpi": {
        "protagonist_cluster_sizes": [5, 5, 5, 5, 5, 5, 5, 5],
        "non_protagonist_cluster_sizes": [30, 30],
    },
}

# Placement-profile probabilities (per-doc, independent).
PLACEMENT_PROBABILITIES = {
    "slot1": 0.85,
    "slot2": 0.12,
    "slot3": 0.03,
}

# Doc-type probability (titled vs title-less). Drawn once per cluster: all docs in a cluster
# share the same title flag, so platform variants preserve the canonical's structure.
P_TITLED = 0.30

# Replicate count.
N_REPLICATES = 10

# Param grids.
LFA_THRESHOLD_GRID = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
KMEANS_K_GRID = [5, 7, 10, 13, 15, 20]
LEIDEN_THRESHOLD_GRID = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]

# K-means runs on PCA-reduced embeddings to mitigate the curse of dimensionality.
# The 384-dim sentence-transformer embeddings on ~100 documents per corpus would
# otherwise leave documents sparsely distributed in a high-dimensional space,
# which degrades k-means performance. n_components = 15 preserves ~89% of the
# variance on average across the synthetic corpora; see scripts/pca_diagnostic.py.
KMEANS_PCA_COMPONENTS = 15

# Embedding model.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"

# Default LLM sampling configuration. Stored in the registry under a UUID at first use.
DEFAULT_LLM_CONFIG = {
    "model": "gemma3:12b",
    "temperature": 1.0,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "num_predict": 150,
    "num_ctx": 1024,
}

# Concurrent LLM dispatch. Ollama daemon must be started with OLLAMA_NUM_PARALLEL >= this.
OLLAMA_CONCURRENCY = 4

# Platform-style variants. Within each cluster the first doc is the canonical (a wire-service
# brief generated from scratch); the rest are stylistic rewrites of the canonical that simulate
# the cross-platform repost pattern observed in real production semantic groups (Telegram +
# VK + OK + Twitter + blog reposts of the same story). All variants keep 3 to 4 short
# sentences so generated docs fit comfortably inside the embedder's 128-token context.
PLATFORM_STYLES = [
    {
        "name": "telegram",
        "instruction": (
            "Rewrite the article as a Telegram channel post: 3 to 4 short sentences, include "
            "1 to 2 emoji, finish with one or two hashtags and a short channel signature like "
            "'@channel_name'. Keep the same factual content; do not introduce new events."
        ),
    },
    {
        "name": "vk",
        "instruction": (
            "Rewrite the article as a VK community post: 3 to 4 short sentences in casual "
            "social-media phrasing, optionally a 'club' tag. Keep the same factual content."
        ),
    },
    {
        "name": "ok",
        "instruction": (
            "Rewrite the article as an Odnoklassniki post: 3 to 4 short sentences, "
            "blunt and somewhat opinionated tone. Keep the same factual content."
        ),
    },
    {
        "name": "wire_brief",
        "instruction": (
            "Rewrite the article as a wire-service brief: 3 to 4 short factual sentences in "
            "neutral journalistic register, no editorialising, no emoji or hashtags."
        ),
    },
    {
        "name": "twitter",
        "instruction": (
            "Rewrite the article as a Twitter thread fragment: 3 to 4 short sentences, "
            "abbreviations are fine, include 1 to 2 hashtags. Keep the same factual content."
        ),
    },
    {
        "name": "blog",
        "instruction": (
            "Rewrite the article as an opinionated independent blog snippet: 3 to 4 short "
            "sentences with a clear take or angle, but the same underlying facts."
        ),
    },
]

# Per-document divergence injections (reserved for future use).
#
# These lists feed the optional `journalist_persona`, `secondary_actor`, and
# `supplementary_fact` parameters of `prompts.primary_prompt` / `prompts.variant_prompt`,
# which inject per-document content variation to prevent near-identical text across
# sub-stories of the same parent event. The current `generate.py` does NOT draw from
# these lists — every cluster's `parent_event` is "none" in `topics.CATALOGUE`, so the
# anti-mode-collapse mechanism is not needed in the current design. The lists are kept
# here so the mechanism can be activated by passing draws through `generate.py` if a
# future variant of the catalogue introduces shared parent events.

JOURNALIST_PERSONAS = [
    "defence correspondent focusing on military operational specifics and procurement detail",
    "foreign-affairs correspondent focusing on diplomatic and bilateral implications",
    "political correspondent focusing on parliamentary dynamics and party-political reaction",
    "regional correspondent focusing on local economic and social impact",
    "wire-service general reporter using neutral, factual register",
    "economics correspondent focusing on fiscal and market reaction",
    "security and intelligence correspondent focusing on classified-source analysis",
]

# Plausible Veridian / EU / NATO secondary actors. None are named "Aleksander Norvik" — the
# protagonist is injected separately via the placement clause when present.
SECONDARY_ACTORS = [
    "Defence Minister Inga Vahl",
    "Foreign Minister Petras Kasper",
    "Chief of General Staff Lt Gen Ainars Krūmiņš",
    "Opposition leader Mihkel Tormi",
    "Parliamentary speaker Eva Lindqvist",
    "EU High Representative Karolina Petrov",
    "Treasury Secretary Dr Liisa Tamm",
    "Provincial Governor of Vidlands Ivars Birkenfeld",
    "Veridian Ambassador to NATO Magnus Ojārs",
    "Industry analyst Helena Kaarna",
    "Intelligence Committee chair Senator Toomas Larsen",
]

SUPPLEMENTARY_FACTS = [
    "The announcement was made shortly after 11:00 local time.",
    "Veridia's defence GDP share is 2.7%, above the NATO target of 2%.",
    "The cost is to be funded from the existing 2026 defence reserve.",
    "Three opposition parties walked out before the vote.",
    "Press attendance was restricted to accredited national media.",
    "A follow-up briefing is scheduled for 16:00 the same day.",
    "Trade volumes between Veridia and the affected region exceed €4 billion annually.",
    "The 2nd Mechanised Brigade is deployed in eastern Vidlands province.",
    "The Verithall constituency holds parliamentary elections in eight months.",
    "Border crossings at Velgrad and Stamvik remain operational under enhanced screening.",
    "Sources close to the matter requested anonymity to discuss internal deliberations.",
    "An emergency cabinet session was convened the previous evening.",
]

# Verify-and-retry parameters.
N_SAME_PROMPT_RETRIES = 3
N_DIAGNOSTIC_RETRIES = 1
