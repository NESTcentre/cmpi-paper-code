from cmpi_simulation import retry


class StubLLM:
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.calls = 0

    def generate(self, *, prompt: str, options: dict) -> str:
        self.calls += 1
        return self._responses.pop(0)


def _parse(raw: str):
    """Helper mirror of retry.parse_response for test setup; defined inline for readability."""
    if raw.startswith("TITLE:"):
        # First line is the title, remainder is the body after a blank line.
        head, _, rest = raw.partition("\n")
        return head[len("TITLE:"):].strip(), rest.strip()
    return None, raw.strip()


def test_first_attempt_succeeds():
    llm = StubLLM([
        "TITLE: Norvik unveils package\n\nAleksander Norvik announced the deal. Details follow."
    ])
    result = retry.generate_doc_with_retries(
        llm=llm,
        primary_prompt="primary",
        diagnostic_prompt_builder=lambda draft, reason: "diagnostic",
        options={"model": "gemma3:4b"},
        is_titled=True,
        placement_profile="slot1",
        entity_name="Aleksander Norvik",
        n_same_prompt_retries=3,
        n_diagnostic_retries=1,
    )
    assert result["accepted"] is True
    assert result["call_count"] == 1
    assert "Aleksander Norvik" in result["body"]


def test_succeeds_on_third_same_prompt_retry():
    llm = StubLLM([
        # Bad: entity in slot 2 (we asked slot 1)
        "TITLE: Government acts\n\nThe move came on Tuesday. Aleksander Norvik confirmed.",
        "TITLE: Government acts\n\nThe move came on Tuesday. Aleksander Norvik confirmed.",
        # Good
        "TITLE: Norvik unveils package\n\nAleksander Norvik announced the deal. Details follow.",
    ])
    result = retry.generate_doc_with_retries(
        llm=llm,
        primary_prompt="primary",
        diagnostic_prompt_builder=lambda draft, reason: "diagnostic",
        options={"model": "gemma3:4b"},
        is_titled=True,
        placement_profile="slot1",
        entity_name="Aleksander Norvik",
        n_same_prompt_retries=3,
        n_diagnostic_retries=1,
    )
    assert result["accepted"] is True
    assert result["call_count"] == 3


def test_diagnostic_retry_used_after_three_same_prompt_failures():
    llm = StubLLM([
        # 4 bad
        "TITLE: A\n\nThe move came. Aleksander Norvik confirmed.",
        "TITLE: A\n\nThe move came. Aleksander Norvik confirmed.",
        "TITLE: A\n\nThe move came. Aleksander Norvik confirmed.",
        # diagnostic-retry succeeds
        "TITLE: Norvik unveils\n\nAleksander Norvik announced. Details follow.",
    ])
    result = retry.generate_doc_with_retries(
        llm=llm,
        primary_prompt="primary",
        diagnostic_prompt_builder=lambda draft, reason: "diagnostic",
        options={"model": "gemma3:4b"},
        is_titled=True,
        placement_profile="slot1",
        entity_name="Aleksander Norvik",
        n_same_prompt_retries=3,
        n_diagnostic_retries=1,
    )
    assert result["accepted"] is True
    assert result["call_count"] == 4
    assert result["used_diagnostic"] is True


def test_complete_failure_returns_rejected():
    llm = StubLLM(["TITLE: A\n\nThe move. Aleksander Norvik."] * 5)
    result = retry.generate_doc_with_retries(
        llm=llm,
        primary_prompt="primary",
        diagnostic_prompt_builder=lambda draft, reason: "diagnostic",
        options={"model": "gemma3:4b"},
        is_titled=True,
        placement_profile="slot1",
        entity_name="Aleksander Norvik",
        n_same_prompt_retries=3,
        n_diagnostic_retries=1,
    )
    assert result["accepted"] is False
    assert result["call_count"] == 4  # 3 same-prompt + 1 diagnostic
