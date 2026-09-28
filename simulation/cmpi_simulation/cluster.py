"""Clustering algorithms and partition-similarity metric.

Three algorithms:
    leader_follower(embeddings, arrival_order, threshold) → labels
    kmeans(embeddings, k, random_state) → labels
    leiden(embeddings, threshold, random_state) → labels

Plus the ARI wrapper from sklearn.
"""

import igraph as ig
import leidenalg
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score


def leader_follower(*, embeddings: np.ndarray, arrival_order: list[int], threshold: float) -> list[int]:
    """Online single-pass leader-follower clustering.

    Documents arrive in `arrival_order`. For each, compute cosine similarity to every active centroid
    (centroids are normalised running averages of assigned member vectors). Assign to the best-matching
    centroid if max similarity > threshold; else seed a new cluster.

    Returns labels in original (pre-arrival-permutation) document index order.
    """
    n = embeddings.shape[0]
    labels = [-1] * n
    centroids: list[np.ndarray] = []
    centroid_counts: list[int] = []

    # Pre-normalise the input embeddings (caller may already have done this; idempotent).
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embs = embeddings / norms

    for doc_idx in arrival_order:
        x = embs[doc_idx]
        if not centroids:
            centroids.append(x.copy())
            centroid_counts.append(1)
            labels[doc_idx] = 0
            continue
        sims = np.array([float(np.dot(x, c)) for c in centroids])
        best = int(np.argmax(sims))
        if sims[best] > threshold:
            count = centroid_counts[best]
            new_centroid = (centroids[best] * count + x) / (count + 1)
            new_centroid /= max(np.linalg.norm(new_centroid), 1e-12)
            centroids[best] = new_centroid
            centroid_counts[best] = count + 1
            labels[doc_idx] = best
        else:
            centroids.append(x.copy())
            centroid_counts.append(1)
            labels[doc_idx] = len(centroids) - 1

    return labels


def kmeans(*, embeddings: np.ndarray, k: int, random_state: int = 0) -> list[int]:
    """Standard scikit-learn KMeans with n_init=10."""
    model = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    return model.fit_predict(embeddings).tolist()


def leiden(*, embeddings: np.ndarray, threshold: float, random_state: int = 0) -> list[int]:
    """Offline graph-partitioning clustering via Leiden + Surprise.

    Build an undirected weighted graph over all documents: every pair with cosine
    similarity >= `threshold` becomes an edge weighted by that similarity. Run
    Leiden (Traag, Waltman & van Eck, 2019) with the Surprise quality function
    (Traag, Aldecoa & Delvenne, 2015), which is well-suited to many small
    communities. Method follows Trilling & van Hoof (2020).

    Returns labels in the input embedding row order.
    """
    n = embeddings.shape[0]
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embs = embeddings / norms
    sim = embs @ embs.T
    np.fill_diagonal(sim, 0.0)
    iu, ju = np.triu_indices(n, k=1)
    weights_all = sim[iu, ju]
    # SurpriseVertexPartition rejects negative weights, and negative cosine similarity
    # is not a meaningful indicator of "same story" anyway, so any edge below the
    # admission threshold OR below zero is dropped.
    keep = (weights_all >= threshold) & (weights_all > 0)
    edges = list(zip(iu[keep].tolist(), ju[keep].tolist(), strict=True))
    weights = weights_all[keep].astype(float).tolist()
    g = ig.Graph(n=n, edges=edges, directed=False)
    if not edges:
        return list(range(n))
    g.es["weight"] = weights
    part = leidenalg.find_partition(
        g,
        leidenalg.SurpriseVertexPartition,
        weights="weight",
        seed=int(random_state),
    )
    return list(part.membership)


def adjusted_rand_index(true_labels: list[int], recovered: list[int]) -> float:
    """Wrapper around sklearn.metrics.adjusted_rand_score for naming consistency."""
    return float(adjusted_rand_score(true_labels, recovered))
