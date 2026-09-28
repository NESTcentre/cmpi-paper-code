from cmpi_simulation import topics


def test_low_cmpi_day_has_ten_clusters():
    catalogue = topics.CATALOGUE["low_cmpi"]
    assert len(catalogue) == 10
    assert sum(1 for c in catalogue if c["protagonist"]) == 2
    assert sum(1 for c in catalogue if not c["protagonist"]) == 8


def test_high_cmpi_day_has_ten_clusters():
    catalogue = topics.CATALOGUE["high_cmpi"]
    assert len(catalogue) == 10
    assert sum(1 for c in catalogue if c["protagonist"]) == 8
    assert sum(1 for c in catalogue if not c["protagonist"]) == 2


def test_high_cmpi_protagonist_clusters_are_topically_independent():
    """High-day protagonist clusters are 8 independent stories about the protagonist
    (not sub-stories of one parent event), so a fixed-threshold clusterer can recover
    each cluster cleanly. Each cluster's parent_event is "none" and themes are diverse."""
    catalogue = topics.CATALOGUE["high_cmpi"]
    prot = [c for c in catalogue if c["protagonist"]]
    assert all(c["parent_event"] == "none" for c in prot)
    assert len({c["theme"] for c in prot}) >= 6, "Protagonist clusters should span multiple themes"


def test_at_least_two_thematic_overlap_pairs():
    """Each day catalogue must contain at least 2 protagonist–non-protagonist pairs in the same theme."""
    for day in ("low_cmpi", "high_cmpi"):
        catalogue = topics.CATALOGUE[day]
        prot_themes = {c["theme"] for c in catalogue if c["protagonist"]}
        non_prot_themes = [c["theme"] for c in catalogue if not c["protagonist"]]
        overlap = sum(1 for t in non_prot_themes if t in prot_themes)
        assert overlap >= 2, f"Day {day} has only {overlap} thematic-overlap pairs; need at least 2"


def test_each_cluster_has_unique_story_angle():
    for day in ("low_cmpi", "high_cmpi"):
        angles = [c["story_angle"] for c in topics.CATALOGUE[day]]
        assert len(angles) == len(set(angles)), f"Duplicate story angles in {day}"
