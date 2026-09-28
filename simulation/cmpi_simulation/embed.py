"""Embedding wrapper around sentence-transformers/all-MiniLM-L12-v2."""

from functools import lru_cache

import numpy as np

from .config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a batch of texts and return an L2-normalised float32 ndarray of shape (N, D)."""
    model = _model()
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return embeddings.astype(np.float32)


def embed_documents(corpus: dict) -> np.ndarray:
    """Build the per-doc text and embed it.

    Per-doc text construction: title (if present) followed by body, separated by a newline. This
    matches what a real production pipeline would feed into the embedder.
    """
    docs = corpus["documents"]
    # Sort by doc_id to make the row order deterministic; downstream code uses doc_id-keyed labels.
    docs_sorted = sorted(docs, key=lambda d: d["doc_id"])
    texts = []
    for d in docs_sorted:
        title = d["title"]
        body = d["body"]
        text = f"{title}\n\n{body}" if title else body
        texts.append(text)
    return embed_texts(texts)
