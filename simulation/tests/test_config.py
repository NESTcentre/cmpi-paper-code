from cmpi_simulation import config


def test_day_configs_have_correct_totals():
    for day_name, cfg in config.DAY_CONFIGS.items():
        assert sum(cfg["protagonist_cluster_sizes"]) + sum(cfg["non_protagonist_cluster_sizes"]) == 100, day_name
        assert len(cfg["protagonist_cluster_sizes"]) + len(cfg["non_protagonist_cluster_sizes"]) == 10, day_name


def test_low_cmpi_day_total_mentions_equal_40():
    cfg = config.DAY_CONFIGS["low_cmpi"]
    # m_k/n_k = 1.0 for all protagonist clusters → mentions == sum of sizes
    assert sum(cfg["protagonist_cluster_sizes"]) == 40


def test_high_cmpi_day_total_mentions_equal_40():
    cfg = config.DAY_CONFIGS["high_cmpi"]
    assert sum(cfg["protagonist_cluster_sizes"]) == 40


def test_placement_probabilities_sum_to_one():
    probs = config.PLACEMENT_PROBABILITIES
    assert abs(sum(probs.values()) - 1.0) < 1e-9


def test_lfa_threshold_grid():
    assert config.LFA_THRESHOLD_GRID == [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]


def test_kmeans_k_grid():
    assert config.KMEANS_K_GRID == [5, 7, 10, 13, 15, 20]


def test_leiden_threshold_grid():
    assert config.LEIDEN_THRESHOLD_GRID == [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]


def test_replicate_count():
    assert config.N_REPLICATES == 10
