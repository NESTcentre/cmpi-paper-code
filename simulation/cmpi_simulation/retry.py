"""Verify-and-retry orchestration for one document.

Algorithm:
    1. Up to N_SAME_PROMPT_RETRIES same-prompt attempts.
    2. Up to N_DIAGNOSTIC_RETRIES diagnostic-prompt retries (with the previous failure cited).
    3. If still failing, the doc is rejected.
"""

from typing import Callable

from .verify import split_sentences, verify_placement


def parse_response(raw: str) -> tuple[str | None, str]:
    """Split a raw LLM response into (title, body).

    Title is detected by a leading 'TITLE:' line. If absent, title is None and the entire response
    is the body.
    """
    raw = raw.strip()
    if raw.startswith("TITLE:"):
        head, _, rest = raw.partition("\n")
        title = head[len("TITLE:"):].strip()
        return title or None, rest.strip()
    return None, raw


def generate_doc_with_retries(
    *,
    llm,
    primary_prompt: str,
    diagnostic_prompt_builder: Callable[[str, str], str],
    options: dict,
    is_titled: bool,
    placement_profile: str,
    entity_name: str,
    n_same_prompt_retries: int,
    n_diagnostic_retries: int,
) -> dict:
    """Generate one doc with the verify-and-retry policy.

    Returns a dict:
        accepted: bool
        title: str | None  (only if accepted)
        body: str  (only meaningful if accepted)
        sentences: list[str]  (only meaningful if accepted)
        call_count: int
        used_diagnostic: bool
        last_failure_reason: str  (empty if accepted)
    """
    call_count = 0
    last_draft = ""
    last_reason = ""

    # Same-prompt attempts.
    for _ in range(n_same_prompt_retries):
        raw = llm.generate(prompt=primary_prompt, options=options)
        call_count += 1
        title, body = parse_response(raw)
        if is_titled and title is None:
            last_draft = raw
            last_reason = "Expected a title (TITLE: line); none found."
            continue
        if not is_titled and title is not None:
            last_draft = raw
            last_reason = "Expected no title; one was supplied."
            continue
        ok, reason = verify_placement(title=title, body=body, name=entity_name, expected=placement_profile)
        if ok:
            return {
                "accepted": True,
                "title": title,
                "body": body,
                "sentences": split_sentences(body),
                "call_count": call_count,
                "used_diagnostic": False,
                "last_failure_reason": "",
            }
        last_draft = raw
        last_reason = reason

    # Diagnostic retries.
    for _ in range(n_diagnostic_retries):
        diag_prompt = diagnostic_prompt_builder(last_draft, last_reason)
        raw = llm.generate(prompt=diag_prompt, options=options)
        call_count += 1
        title, body = parse_response(raw)
        if is_titled and title is None:
            last_draft = raw
            last_reason = "Expected a title (TITLE: line); none found."
            continue
        if not is_titled and title is not None:
            last_draft = raw
            last_reason = "Expected no title; one was supplied."
            continue
        ok, reason = verify_placement(title=title, body=body, name=entity_name, expected=placement_profile)
        if ok:
            return {
                "accepted": True,
                "title": title,
                "body": body,
                "sentences": split_sentences(body),
                "call_count": call_count,
                "used_diagnostic": True,
                "last_failure_reason": "",
            }
        last_draft = raw
        last_reason = reason

    return {
        "accepted": False,
        "title": None,
        "body": "",
        "sentences": [],
        "call_count": call_count,
        "used_diagnostic": True,
        "last_failure_reason": last_reason,
    }


async def generate_doc_with_retries_async(
    *,
    llm,
    primary_prompt: str,
    diagnostic_prompt_builder: Callable[[str, str], str],
    options: dict,
    is_titled: bool,
    placement_profile: str,
    entity_name: str,
    n_same_prompt_retries: int,
    n_diagnostic_retries: int,
) -> dict:
    """Async mirror of generate_doc_with_retries. Same return contract."""
    call_count = 0
    last_draft = ""
    last_reason = ""

    for _ in range(n_same_prompt_retries):
        raw = await llm.generate(prompt=primary_prompt, options=options)
        call_count += 1
        title, body = parse_response(raw)
        if is_titled and title is None:
            last_draft = raw
            last_reason = "Expected a title (TITLE: line); none found."
            continue
        if not is_titled and title is not None:
            last_draft = raw
            last_reason = "Expected no title; one was supplied."
            continue
        ok, reason = verify_placement(title=title, body=body, name=entity_name, expected=placement_profile)
        if ok:
            return {
                "accepted": True,
                "title": title,
                "body": body,
                "sentences": split_sentences(body),
                "call_count": call_count,
                "used_diagnostic": False,
                "last_failure_reason": "",
            }
        last_draft = raw
        last_reason = reason

    for _ in range(n_diagnostic_retries):
        diag_prompt = diagnostic_prompt_builder(last_draft, last_reason)
        raw = await llm.generate(prompt=diag_prompt, options=options)
        call_count += 1
        title, body = parse_response(raw)
        if is_titled and title is None:
            last_draft = raw
            last_reason = "Expected a title (TITLE: line); none found."
            continue
        if not is_titled and title is not None:
            last_draft = raw
            last_reason = "Expected no title; one was supplied."
            continue
        ok, reason = verify_placement(title=title, body=body, name=entity_name, expected=placement_profile)
        if ok:
            return {
                "accepted": True,
                "title": title,
                "body": body,
                "sentences": split_sentences(body),
                "call_count": call_count,
                "used_diagnostic": True,
                "last_failure_reason": "",
            }
        last_draft = raw
        last_reason = reason

    return {
        "accepted": False,
        "title": None,
        "body": "",
        "sentences": [],
        "call_count": call_count,
        "used_diagnostic": True,
        "last_failure_reason": last_reason,
    }
