from cmpi_simulation import verify


def test_split_sentences_basic():
    body = "First sentence. Second sentence! Third sentence?"
    assert verify.split_sentences(body) == ["First sentence.", "Second sentence!", "Third sentence?"]


def test_split_sentences_handles_initials():
    body = "Mr. Smith arrived. He spoke briefly."
    out = verify.split_sentences(body)
    assert len(out) == 2
    assert "Mr. Smith arrived" in out[0]


def test_first_occurrence_slot_in_title():
    """Titled doc: entity in title → slot 1 (title and first body sentence are collapsed)."""
    title = "Norvik unveils package"
    body = "The announcement was made on Tuesday."
    assert verify.first_occurrence_slot(title=title, body=body, name="Norvik") == 1


def test_first_occurrence_slot_in_first_body_sentence_titled():
    """Titled doc: entity not in title, but in body sentence 1 → still slot 1."""
    title = "Government announces package"
    body = "Aleksander Norvik unveiled the plan. The package will run for five years."
    assert verify.first_occurrence_slot(title=title, body=body, name="Aleksander Norvik") == 1


def test_first_occurrence_slot_in_second_body_sentence_titled():
    title = "Government announces package"
    body = "The announcement was made today. Aleksander Norvik unveiled it. Details follow."
    assert verify.first_occurrence_slot(title=title, body=body, name="Aleksander Norvik") == 2


def test_first_occurrence_slot_in_first_sentence_titleless():
    body = "Aleksander Norvik just announced the deal. More to come."
    assert verify.first_occurrence_slot(title=None, body=body, name="Aleksander Norvik") == 1


def test_first_occurrence_slot_in_second_sentence_titleless():
    body = "The announcement broke this morning. Aleksander Norvik is at the centre."
    assert verify.first_occurrence_slot(title=None, body=body, name="Aleksander Norvik") == 2


def test_first_occurrence_slot_absent():
    body = "The announcement was made. Officials confirmed the details."
    assert verify.first_occurrence_slot(title=None, body=body, name="Aleksander Norvik") is None


def test_verify_placement_slot1_titled_passes_title_only():
    title = "Norvik unveils package"
    body = "Officials confirmed details. More to follow."
    ok, reason = verify.verify_placement(title=title, body=body, name="Norvik", expected="slot1")
    assert ok and reason == ""


def test_verify_placement_slot2_fails_when_in_slot1():
    title = "Norvik announces package"
    body = "Details emerged on Tuesday."
    ok, reason = verify.verify_placement(title=title, body=body, name="Norvik", expected="slot2")
    assert not ok and "slot 1" in reason


def test_verify_placement_none_fails_when_present():
    body = "Norvik visited the plant."
    ok, reason = verify.verify_placement(title=None, body=body, name="Norvik", expected="none")
    assert not ok
