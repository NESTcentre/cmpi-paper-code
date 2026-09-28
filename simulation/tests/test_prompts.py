from cmpi_simulation import prompts


def test_primary_prompt_titled_slot1_mentions_entity():
    p = prompts.primary_prompt(
        is_titled=True,
        placement_profile="slot1",
        story_angle="Norvik unveils defence package.",
        sub_story_focus=None,
        parent_event_context=None,
        entity_name="Aleksander Norvik",
    )
    assert "Aleksander Norvik" in p
    assert "title" in p.lower()
    assert "first sentence" in p.lower() or "first body sentence" in p.lower()


def test_primary_prompt_titleless_excludes_title_instructions():
    p = prompts.primary_prompt(
        is_titled=False,
        placement_profile="slot1",
        story_angle="Norvik just announced the deal.",
        sub_story_focus=None,
        parent_event_context=None,
        entity_name="Aleksander Norvik",
    )
    assert "Do not include a title" in p or "no title" in p.lower()


def test_primary_prompt_no_mention_excludes_name():
    p = prompts.primary_prompt(
        is_titled=True,
        placement_profile="none",
        story_angle="A wildfire spreads in southern Greece.",
        sub_story_focus=None,
        parent_event_context=None,
        entity_name="Aleksander Norvik",
    )
    assert "must not mention" in p.lower() or "do not mention" in p.lower()


def test_primary_prompt_slot2_specifies_second_sentence():
    p = prompts.primary_prompt(
        is_titled=True,
        placement_profile="slot2",
        story_angle="Parliament approves emergency budget.",
        sub_story_focus=None,
        parent_event_context=None,
        entity_name="Aleksander Norvik",
    )
    assert "second" in p.lower() and "sentence" in p.lower()


def test_primary_prompt_includes_parent_event_when_given():
    p = prompts.primary_prompt(
        is_titled=True,
        placement_profile="slot1",
        story_angle="Norvik addresses parliament.",
        sub_story_focus="parliamentary address",
        parent_event_context="Veridia airspace incursion crisis",
        entity_name="Aleksander Norvik",
    )
    assert "airspace incursion" in p


def test_diagnostic_prompt_cites_previous_failure():
    diag = prompts.diagnostic_prompt(
        is_titled=True,
        placement_profile="slot2",
        story_angle="Parliament approves budget.",
        sub_story_focus=None,
        parent_event_context=None,
        entity_name="Aleksander Norvik",
        previous_draft="Aleksander Norvik addressed parliament. Details follow.",
        failure_reason="Expected slot 2; first occurrence is at slot 1.",
    )
    assert "Aleksander Norvik" in diag
    assert "previous" in diag.lower() or "before" in diag.lower()
    assert "second" in diag.lower()
