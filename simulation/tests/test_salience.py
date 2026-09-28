from cmpi_simulation import salience


def test_per_doc_paper_salience_present():
    assert salience.per_doc_paper_salience(entity_present=True) == 1.0


def test_per_doc_paper_salience_absent():
    assert salience.per_doc_paper_salience(entity_present=False) == 0.0


def test_per_doc_alt_salience_slot1():
    assert salience.per_doc_alt_salience(first_slot=1) == 1.0


def test_per_doc_alt_salience_slot2():
    assert salience.per_doc_alt_salience(first_slot=2) == 0.5


def test_per_doc_alt_salience_slot3():
    assert abs(salience.per_doc_alt_salience(first_slot=3) - (1 / 3)) < 1e-9


def test_per_doc_alt_salience_absent():
    assert salience.per_doc_alt_salience(first_slot=None) == 0.0


def test_cluster_paper_salience_uniform_protagonist():
    """All 10 docs mention the entity → cluster paper-salience = 1.0."""
    docs = [{"entity_present": True} for _ in range(10)]
    assert salience.cluster_paper_salience(docs) == 1.0


def test_cluster_paper_salience_partial():
    """2 of 10 docs mention → 0.2."""
    docs = [{"entity_present": True}] * 2 + [{"entity_present": False}] * 8
    assert salience.cluster_paper_salience(docs) == 0.2


def test_cluster_paper_salience_zero():
    docs = [{"entity_present": False} for _ in range(10)]
    assert salience.cluster_paper_salience(docs) == 0.0


def test_cluster_alt_salience_all_slot1():
    docs = [{"entity_present": True, "first_slot": 1}] * 10
    assert salience.cluster_alt_salience(docs) == 1.0


def test_cluster_alt_salience_mixed():
    docs = (
        [{"entity_present": True, "first_slot": 1}] * 8
        + [{"entity_present": True, "first_slot": 2}] * 1
        + [{"entity_present": True, "first_slot": 3}] * 1
    )
    expected = (8 * 1.0 + 1 * 0.5 + 1 * (1 / 3)) / 10
    assert abs(salience.cluster_alt_salience(docs) - expected) < 1e-9


def test_cluster_alt_salience_empty_cluster():
    """An empty cluster yields 0 (degenerate; should never occur in the simulation but defined for safety)."""
    assert salience.cluster_alt_salience([]) == 0.0
