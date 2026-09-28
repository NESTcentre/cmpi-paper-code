"""Per-cell pipeline: corpus → embed → cluster → CMPI/ARI under both salience definitions.

A 'cell' is one (corpus, algorithm, parameter) tuple. This module returns a dict of metrics for each.
"""

import numpy as np
from sklearn.decomposition import PCA

from . import cluster as cluster_mod
from . import config as cfg
from . import embed as embed_mod
from . import salience as salience_mod
from . import cmpi as cmpi_mod


def _docs_by_cluster(docs: list[dict], labels: list[int], doc_order_doc_ids: list[str]) -> dict[int, list[dict]]:
    """Group docs by recovered cluster label, using `doc_order_doc_ids` to map labels[i] back to docs."""
    id_to_label = dict(zip(doc_order_doc_ids, labels, strict=True))
    grouped: dict[int, list[dict]] = {}
    for d in docs:
        label = id_to_label[d["doc_id"]]
        grouped.setdefault(label, []).append(d)
    return grouped


def _cluster_metrics_for_partition(docs: list[dict], grouped: dict[int, list[dict]], total_n: int) -> dict:
    """Given a partition (grouped docs), compute CMPI under both salience definitions."""
    paper_clusters = []
    alt_clusters = []
    for _, members in grouped.items():
        size = len(members)
        paper_clusters.append({"size": size, "salience": salience_mod.cluster_paper_salience(members)})
        alt_clusters.append({"size": size, "salience": salience_mod.cluster_alt_salience(members)})
    return {
        "cmpi_paper": cmpi_mod.compute_cmpi(paper_clusters, total_n=total_n),
        "cmpi_alt": cmpi_mod.compute_cmpi(alt_clusters, total_n=total_n),
        "recovered_K": len(grouped),
    }


def run_cell(*, corpus: dict, algorithm: str, parameter: float | int) -> dict:
    """Run one (algorithm, parameter) cell on a corpus.

    Returns: {recovered_K, ARI, cmpi_paper, cmpi_alt}.
    """
    docs = corpus["documents"]
    docs_sorted = sorted(docs, key=lambda d: d["doc_id"])
    doc_ids = [d["doc_id"] for d in docs_sorted]
    embeddings = embed_mod.embed_documents(corpus)
    true_labels = [d["true_cluster"] for d in docs_sorted]

    if algorithm == "lfa":
        # LFA needs an arrival-order-derived index permutation over the docs_sorted axis.
        sorted_id_to_pos = {doc_id: i for i, doc_id in enumerate(doc_ids)}
        ordered_doc_ids = [d["doc_id"] for d in sorted(docs, key=lambda d: d["arrival_index"])]
        arrival_order = [sorted_id_to_pos[doc_id] for doc_id in ordered_doc_ids]
        labels = cluster_mod.leader_follower(
            embeddings=embeddings, arrival_order=arrival_order, threshold=float(parameter)
        )
    elif algorithm == "kmeans":
        # PCA-reduce embeddings before k-means to mitigate curse of dimensionality.
        # See cfg.KMEANS_PCA_COMPONENTS for the chosen number of components.
        pca = PCA(n_components=cfg.KMEANS_PCA_COMPONENTS, random_state=0)
        reduced = pca.fit_transform(embeddings)
        labels = cluster_mod.kmeans(embeddings=reduced, k=int(parameter), random_state=0)
    elif algorithm == "leiden":
        labels = cluster_mod.leiden(embeddings=embeddings, threshold=float(parameter), random_state=0)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    grouped = _docs_by_cluster(docs, labels, doc_ids)
    metrics = _cluster_metrics_for_partition(docs, grouped, total_n=len(docs))
    metrics["ari"] = cluster_mod.adjusted_rand_index(true_labels, labels)
    return metrics


def run_oracle(*, corpus: dict) -> dict:
    """Compute CMPI under the true (ground-truth) partition. ARI is trivially 1.0."""
    docs = corpus["documents"]
    grouped: dict[int, list[dict]] = {}
    for d in docs:
        grouped.setdefault(d["true_cluster"], []).append(d)
    metrics = _cluster_metrics_for_partition(docs, grouped, total_n=len(docs))
    metrics["ari"] = 1.0
    return metrics
