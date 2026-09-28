import math

from cmpi_simulation import cmpi


def test_cmpi_zero_when_all_clusters_absent():
    clusters = [{"size": 10, "salience": 0.0} for _ in range(10)]
    assert cmpi.compute_cmpi(clusters, total_n=100) == 0.0


def test_cmpi_low_day_paper_salience():
    """Manual reproduction of the spec's worked example: low-CMPI day."""
    clusters = [
        {"size": 25, "salience": 1.0},
        {"size": 15, "salience": 1.0},
    ] + [{"size": s, "salience": 0.0} for s in (15, 10, 10, 5, 5, 5, 5, 5)]
    expected = (math.log(26) + math.log(16)) / math.log(101)
    assert abs(cmpi.compute_cmpi(clusters, total_n=100) - expected) < 1e-9


def test_cmpi_high_day_paper_salience():
    clusters = [{"size": 5, "salience": 1.0} for _ in range(8)] + [
        {"size": 30, "salience": 0.0},
        {"size": 30, "salience": 0.0},
    ]
    expected = 8 * math.log(6) / math.log(101)
    assert abs(cmpi.compute_cmpi(clusters, total_n=100) - expected) < 1e-9


def test_cmpi_high_to_low_ratio_around_2_36():
    low = (math.log(26) + math.log(16)) / math.log(101)
    high = 8 * math.log(6) / math.log(101)
    assert abs(high / low - 2.36) < 0.05


def test_cmpi_alt_salience_is_around_0_92x_paper():
    """Alt salience uniformly shrinks every protagonist cluster's salience to ~0.92."""
    clusters_paper = [
        {"size": 25, "salience": 1.0},
        {"size": 15, "salience": 1.0},
    ] + [{"size": s, "salience": 0.0} for s in (15, 10, 10, 5, 5, 5, 5, 5)]
    clusters_alt = [
        {"size": 25, "salience": 0.92},
        {"size": 15, "salience": 0.92},
    ] + [{"size": s, "salience": 0.0} for s in (15, 10, 10, 5, 5, 5, 5, 5)]
    paper = cmpi.compute_cmpi(clusters_paper, total_n=100)
    alt = cmpi.compute_cmpi(clusters_alt, total_n=100)
    assert abs(alt / paper - 0.92) < 1e-9
