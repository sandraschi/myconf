"""Tests for participant management tools — invite, list_invited, remove_invited."""

import pytest


@pytest.mark.asyncio
async def test_participant_invite(mock_ctx, temp_conference_db):
    """Invite a participant to a scheduled conference."""
    from conferencing_mcp.tools.conferences import (
        conference_schedule,
        participant_invite,
    )

    cfg = await conference_schedule(
        mock_ctx, title="Meeting", scheduled_at="2026-06-01T10:00:00Z", organizer="me@x.com"
    )
    cid = cfg["id"]

    result = await participant_invite(mock_ctx, conference_id=cid, identity="alice@x.com", role="PARTICIPANT")
    assert len(result) >= 1
    assert result[0]["identity"] == "alice@x.com"
    assert result[0]["role"] == "PARTICIPANT"


@pytest.mark.asyncio
async def test_participant_invite_default_role(mock_ctx, temp_conference_db):
    """Omitting role defaults to PARTICIPANT."""
    from conferencing_mcp.tools.conferences import (
        conference_schedule,
        participant_invite,
    )

    cfg = await conference_schedule(mock_ctx, title="M2", scheduled_at="2026-06-01T11:00:00Z", organizer="me@x.com")
    result = await participant_invite(mock_ctx, conference_id=cfg["id"], identity="bob@x.com")
    assert result[0]["role"] == "PARTICIPANT"


@pytest.mark.asyncio
async def test_participant_list_invited(mock_ctx, temp_conference_db):
    """List invited participants returns them."""
    from conferencing_mcp.tools.conferences import (
        conference_schedule,
        participant_invite,
        participant_list_invited,
    )

    cfg = await conference_schedule(mock_ctx, title="M3", scheduled_at="2026-06-01T12:00:00Z", organizer="me@x.com")
    await participant_invite(mock_ctx, conference_id=cfg["id"], identity="alice@x.com")
    await participant_invite(mock_ctx, conference_id=cfg["id"], identity="bob@x.com")
    await participant_invite(mock_ctx, conference_id=cfg["id"], identity="carol@x.com")

    result = await participant_list_invited(mock_ctx, conference_id=cfg["id"])
    assert len(result) == 3


@pytest.mark.asyncio
async def test_participant_remove_invited(mock_ctx, temp_conference_db):
    """Remove an invited participant."""
    from conferencing_mcp.tools.conferences import (
        conference_schedule,
        participant_invite,
        participant_remove_invited,
    )

    cfg = await conference_schedule(mock_ctx, title="M4", scheduled_at="2026-06-01T13:00:00Z", organizer="me@x.com")
    await participant_invite(mock_ctx, conference_id=cfg["id"], identity="alice@x.com")

    result = await participant_remove_invited(mock_ctx, conference_id=cfg["id"], identity="alice@x.com")
    assert result.get("identity") == "alice@x.com" or "alice@x.com" in str(result)
