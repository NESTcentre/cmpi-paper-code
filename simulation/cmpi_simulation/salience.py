"""Per-doc and cluster-level salience under both definitions.

A "doc" here is a dict carrying at minimum `entity_present: bool`. Alt-salience also requires
`first_slot: int | None`. Cluster-level salience is the mean of per-doc salience over all docs
(mentioning or not).
"""

from typing import Optional


def per_doc_paper_salience(*, entity_present: bool) -> float:
    """Paper-style per-doc salience: 1.0 if entity present, else 0.0."""
    return 1.0 if entity_present else 0.0


def per_doc_alt_salience(*, first_slot: Optional[int]) -> float:
    """Position-weighted per-doc salience: 1/i for first-occurrence slot i, or 0 if absent."""
    if first_slot is None:
        return 0.0
    return 1.0 / first_slot


def cluster_paper_salience(docs: list[dict]) -> float:
    """Cluster-level paper salience: mean per-doc paper salience = m_k/n_k."""
    if not docs:
        return 0.0
    return sum(per_doc_paper_salience(entity_present=d["entity_present"]) for d in docs) / len(docs)


def cluster_alt_salience(docs: list[dict]) -> float:
    """Cluster-level alt salience: mean per-doc alt salience over all docs in the cluster."""
    if not docs:
        return 0.0
    return sum(per_doc_alt_salience(first_slot=d.get("first_slot")) for d in docs) / len(docs)
