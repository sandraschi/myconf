"""Tests for signaling tools — list_conferences, notify, inter_agent_ping."""

import pytest


@pytest.mark.asyncio
async def test_list_active_conferences(mock_ctx, mock_livekit_api):
    """list_active_conferences returns room_count and schedules."""
    from conferencing_mcp.tools.signaling import list_active_conferences

    result = await list_active_conferences(mock_ctx)
    assert "room_count" in result
    assert "livekit_rooms" in result
    assert "scheduled_conferences" in result
    assert result["correlation_id"] == "TEST-CID-001"


@pytest.mark.asyncio
async def test_notify_conference_active(mock_ctx):
    """Notify returns signal confirmation with room_id and participant count."""
    from conferencing_mcp.tools.signaling import notify_conference_active

    result = await notify_conference_active(mock_ctx, room_id="room-42", participant_count=7)
    assert "SUBSTRATE_SIGNAL" in result
    assert "room-42" in result
    assert "7" in result or "Participants" in result


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["ALL", "remoting-substrate", "conferencing-mcp"])
async def test_inter_agent_ping(target, mock_ctx):
    """Ping broadcasts to all or specific target."""
    from conferencing_mcp.tools.signaling import inter_agent_ping

    result = await inter_agent_ping(mock_ctx, target_agent=target)
    assert "SIGNAL_SENT" in result
    assert target in result
