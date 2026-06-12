"""Tests for intelligence tools — meeting_summary, action_items, translation."""

import pytest


@pytest.mark.asyncio
async def test_generate_meeting_summary_calls_sample(mock_ctx):
    """Summary tool calls ctx.sample and returns summary text."""
    from conferencing_mcp.tools.intelligence import generate_meeting_summary

    result = await generate_meeting_summary(
        mock_ctx,
        room_name="standup",
        transcript="Alice: Good morning. Bob: Let's ship it.",
    )
    assert result["success"] is True
    assert result["room_name"] == "standup"
    assert "persisted" in result
    mock_ctx.sample.assert_called_once()


@pytest.mark.asyncio
async def test_extract_action_items_calls_sample(mock_ctx):
    """Action items tool calls ctx.sample and returns items."""
    from conferencing_mcp.tools.intelligence import extract_action_items

    result = await extract_action_items(
        mock_ctx,
        room_name="sprint-planning",
        transcript="Bob: I'll take the login page. Alice: I'll do the API.",
    )
    assert result["success"] is True
    assert "action_items" in result
    mock_ctx.sample.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("language", ["Japanese", "German", "Spanish"])
async def test_set_translation_language(language, mock_ctx):
    """Translation language returns confirmation string with the language name."""
    from conferencing_mcp.tools.intelligence import set_translation_language

    result = await set_translation_language(mock_ctx, language=language)
    assert language in result
    assert "TRANSLATION_MODE_ACTIVE" in result


@pytest.mark.asyncio
async def test_generate_meeting_summary_sample_error_handled(mock_ctx):
    """When ctx.sample raises, the tool returns success=False."""
    mock_ctx.sample.side_effect = RuntimeError("LLM offline")

    from conferencing_mcp.tools.intelligence import generate_meeting_summary

    result = await generate_meeting_summary(mock_ctx, room_name="test", transcript="text")
    assert result["success"] is False
    assert "error" in result
