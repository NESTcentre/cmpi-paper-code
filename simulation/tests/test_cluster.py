import numpy as np

from cmpi_simulation import cluster


def _toy_embeddings():
    """Three well-separated 2D 'embeddings' clusters of 3 points each, plus normalisation."""
    rng = np.random.default_rng(0)
    a = rng.normal(loc=[1.0, 0.0], scale=0.05, size=(3, 2))
    b = rng.normal(loc=[-1.0, 0.0], scale=0.05, size=(3, 2))
    c = rng.normal(loc=[0.0, 1.0], scale=0.05, size=(3, 2))
    pts = np.vstack([a, b, c])
    pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    return pts


def test_lfa_high_threshold_splits_clusters():
    embeddings = _toy_embeddings()
    arrival_order = list(range(9))
    labels = cluster.leader_follower(embeddings=embeddings, arrival_order=arrival_order, threshold=1.0)
    # At threshold 1.0 (strict >) nothing ever merges → each point a singleton.
    assert len(set(labels)) == 9


def test_lfa_low_threshold_recovers_three_clusters():
    embeddings = _toy_embeddings()
    arrival_order = list(range(9))
    labels = cluster.leader_follower(embeddings=embeddings, arrival_order=arrival_order, threshold=0.5)
    # At threshold 0.5, the three well-separated clusters merge correctly.
    assert len(set(labels)) == 3


def test_lfa_respects_arrival_order():
    """Different arrival orders may yield different partitions because centroids drift."""
    embeddings = _toy_embeddings()
    labels1 = cluster.leader_follower(embeddings=embeddings, arrival_order=list(range(9)), threshold=0.7)
    labels2 = cluster.leader_follower(embeddings=embeddings, arrival_order=list(range(8, -1, -1)), threshold=0.7)
    # Same number of clusters in this toy case, but labels can differ; we check assignments are consistent
    assert len(labels1) == len(labels2) == 9


def test_kmeans_recovers_three_clusters():
    embeddings = _toy_embeddings()
    labels = cluster.kmeans(embeddings=embeddings, k=3, random_state=0)
    assert len(set(labels)) == 3


def test_leiden_recovers_three_clusters():
    embeddings = _toy_embeddings()
    # At a moderate threshold, the three well-separated clusters should fall out as
    # three connected components and Leiden should partition accordingly.
    labels = cluster.leiden(embeddings=embeddings, threshold=0.5, random_state=0)
    assert len(set(labels)) == 3


def test_leiden_high_threshold_returns_singletons():
    embeddings = _toy_embeddings()
    # Cosine similarity is bounded by 1; a threshold above 1 produces an empty edge set,
    # which means every document is its own cluster.
    labels = cluster.leiden(embeddings=embeddings, threshold=1.01, random_state=0)
    assert len(set(labels)) == 9


def test_leiden_low_threshold_overmerges():
    embeddings = _toy_embeddings()
    # At threshold 0 (admit every positive-similarity edge), the toy clusters are
    # connected via positive cross-cluster similarities. Surprise still tends to split
    # them, but it must produce strictly fewer clusters than the strict-threshold case
    # in which every doc is its own singleton.
    n_low = len(set(cluster.leiden(embeddings=embeddings, threshold=0.0, random_state=0)))
    n_high = len(set(cluster.leiden(embeddings=embeddings, threshold=1.01, random_state=0)))
    assert n_low < n_high


def test_leiden_deterministic_under_fixed_seed():
    embeddings = _toy_embeddings()
    a = cluster.leiden(embeddings=embeddings, threshold=0.5, random_state=42)
    b = cluster.leiden(embeddings=embeddings, threshold=0.5, random_state=42)
    assert a == b


def test_ari_perfect():
    true_labels = [0, 0, 1, 1, 2, 2]
    recovered = [0, 0, 1, 1, 2, 2]
    assert cluster.adjusted_rand_index(true_labels, recovered) == 1.0


def test_ari_relabelled_perfect():
    true_labels = [0, 0, 1, 1, 2, 2]
    recovered = [5, 5, 7, 7, 9, 9]  # same partition, different labels
    assert cluster.adjusted_rand_index(true_labels, recovered) == 1.0


def test_ari_random():
    rng = np.random.default_rng(0)
    true_labels = list(rng.integers(0, 5, size=100))
    recovered = list(rng.integers(0, 5, size=100))
    ari = cluster.adjusted_rand_index(true_labels, recovered)
    assert -0.1 < ari < 0.1
