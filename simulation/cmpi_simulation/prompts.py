"""LLM prompt templates for primary generation and diagnostic-retry generation."""

from typing import Optional


def _length_clause() -> str:
    return "Write exactly 3 to 4 sentences in the body. Do not write more."


def _title_clause(is_titled: bool) -> str:
    if is_titled:
        return (
            "Begin your response with a single news-style title on its own line, "
            "starting with 'TITLE:' (e.g., 'TITLE: Veridia approves new defence budget'). "
            "Then a blank line, then the body."
        )
    return "Do not include a title or any 'TITLE:' line. Output only the body sentences."


def _placement_clause(placement_profile: str, entity_name: str, is_titled: bool) -> str:
    if placement_profile == "none":
        return (
            f"This document must not mention {entity_name} at all. "
            f"The name {entity_name} must not appear in the title or in any sentence of the body."
        )
    if placement_profile == "slot1":
        if is_titled:
            return (
                f"{entity_name} must appear in the title and also in the first body sentence. "
                f"Do not introduce them only later."
            )
        return f"{entity_name} must be introduced in the first sentence of the body."
    if placement_profile == "slot2":
        if is_titled:
            return (
                f"The title and first body sentence must describe the event itself, without {entity_name}. "
                f"{entity_name} is then introduced in the second body sentence."
            )
        return (
            f"The first sentence describes the event itself, without {entity_name}. "
            f"{entity_name} is then introduced in the second sentence."
        )
    if placement_profile == "slot3":
        if is_titled:
            return (
                f"The title and the first two body sentences set the context, without {entity_name}. "
                f"{entity_name} is introduced in the third body sentence."
            )
        return (
            f"The first two sentences set the context, without {entity_name}. "
            f"{entity_name} is introduced in the third sentence."
        )
    raise ValueError(f"Unknown placement_profile: {placement_profile!r}")


def primary_prompt(
    *,
    is_titled: bool,
    placement_profile: str,
    story_angle: str,
    sub_story_focus: Optional[str],
    parent_event_context: Optional[str],
    entity_name: str,
    journalist_persona: Optional[str] = None,
    secondary_actor: Optional[str] = None,
    supplementary_fact: Optional[str] = None,
) -> str:
    """Build the primary generation prompt for one document."""
    parts = [
        "You are generating a short, realistic-looking news document for a research simulation.",
        f"Story angle: {story_angle}",
    ]
    if sub_story_focus:
        parts.append(f"Specific sub-story focus: {sub_story_focus}.")
    if parent_event_context:
        parts.append(
            f"This document is one of several covering the same overarching event: {parent_event_context}. "
            f"Stay focused on the specific sub-story angle above; do not summarise the entire event."
        )
    if journalist_persona:
        parts.append(
            f"Voice: write as a {journalist_persona}. Choose vocabulary and emphasis appropriate to that beat."
        )
    if secondary_actor:
        parts.append(
            f"Name {secondary_actor} as a secondary actor or quoted figure somewhere in the body. "
            f"This person is distinct from the main protagonist."
        )
    if supplementary_fact:
        parts.append(
            f"Include this specific supplementary detail prominently in the body: {supplementary_fact}"
        )
    parts.append(_length_clause())
    parts.append(_title_clause(is_titled))
    parts.append(_placement_clause(placement_profile, entity_name, is_titled))
    parts.append("Write in clear English in a neutral wire-service register. Output only the document text.")
    return "\n\n".join(parts)


def variant_prompt(
    *,
    canonical_text: str,
    platform_instruction: str,
    is_titled: bool,
    placement_profile: str,
    entity_name: str,
) -> str:
    """Prompt asking the LLM to rewrite a canonical article in a given platform style.

    The variant must preserve the canonical's title-or-no-title structure and the entity's
    first-occurrence position (slot1/slot2/slot3, or absence for "none"), since both
    properties are drawn once per cluster.
    """
    parts = [
        "You are creating a platform-style rewrite of an existing news article for a research simulation.",
        platform_instruction,
        "Keep the same factual content as the original; do not invent new events, places, or people.",
        _title_clause(is_titled),
        _placement_clause(placement_profile, entity_name, is_titled=is_titled),
        f"Original article:\n{canonical_text}",
        "Output only the rewritten document text.",
    ]
    return "\n\n".join(parts)


def variant_diagnostic_prompt(
    *,
    canonical_text: str,
    platform_instruction: str,
    is_titled: bool,
    placement_profile: str,
    entity_name: str,
    previous_draft: str,
    failure_reason: str,
) -> str:
    """Variant rewrite retry prompt: cites the previous failure and re-emphasises placement."""
    base = variant_prompt(
        canonical_text=canonical_text,
        platform_instruction=platform_instruction,
        is_titled=is_titled,
        placement_profile=placement_profile,
        entity_name=entity_name,
    )
    diag = (
        "Your previous rewrite did not satisfy the constraints. "
        f"Reason: {failure_reason}\n\n"
        f"Previous rewrite:\n{previous_draft}\n\n"
        "Please rewrite again. Same platform style, same factual content, but follow the "
        "title and placement rules exactly."
    )
    placement_reminder = ""
    if placement_profile == "slot2":
        placement_reminder = f" {entity_name} must first appear in the second sentence (not earlier, not later)."
    elif placement_profile == "slot3":
        placement_reminder = f" {entity_name} must first appear in the third sentence (not earlier, not later)."
    return base + "\n\n" + diag + placement_reminder


def diagnostic_prompt(
    *,
    is_titled: bool,
    placement_profile: str,
    story_angle: str,
    sub_story_focus: Optional[str],
    parent_event_context: Optional[str],
    entity_name: str,
    previous_draft: str,
    failure_reason: str,
    journalist_persona: Optional[str] = None,
    secondary_actor: Optional[str] = None,
    supplementary_fact: Optional[str] = None,
) -> str:
    """Build a diagnostic-retry prompt that cites the previous failure."""
    base = primary_prompt(
        is_titled=is_titled,
        placement_profile=placement_profile,
        story_angle=story_angle,
        sub_story_focus=sub_story_focus,
        parent_event_context=parent_event_context,
        entity_name=entity_name,
        journalist_persona=journalist_persona,
        secondary_actor=secondary_actor,
        supplementary_fact=supplementary_fact,
    )
    diag = (
        "Your previous draft did not satisfy the placement constraint. "
        f"Reason: {failure_reason}\n\n"
        f"Previous draft:\n{previous_draft}\n\n"
        "Please rewrite. Same story angle, same length, same title rule, but this time follow the "
        "placement rule exactly."
    )
    placement_reminder = ""
    if placement_profile == "slot2":
        placement_reminder = (
            f" {entity_name} must first appear in the second sentence (not earlier, not later)."
        )
    elif placement_profile == "slot3":
        placement_reminder = (
            f" {entity_name} must first appear in the third sentence (not earlier, not later)."
        )
    return base + "\n\n" + diag + placement_reminder
