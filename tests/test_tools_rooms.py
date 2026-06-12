"""Tests for room tools — LiveKit room CRUD + participant management."""

import pytest


@pytest.mark.asyncio
async def test_room_create(mock_ctx, mock_livekit_api):
    """room_create returns the room dict from mocked LiveKit API."""
    from conferencing_mcp.tools.rooms import room_create

    result = await room_create(mock_ctx, name="test-room", max_participants=10)
    assert result["name"] == "new-room"
    mock_livekit_api["lk_create_room"].assert_called_once()


@pytest.mark.asyncio
async def test_room_list(mock_ctx, mock_livekit_api):
    """room_list returns rooms from mocked API."""
    from conferencing_mcp.tools.rooms import room_list

    result = await room_list(mock_ctx)
    assert len(result) == 2
    assert result[0]["name"] == "room-alpha"


@pytest.mark.asyncio
async def test_room_list_with_filter(mock_ctx, mock_livekit_api):
    """room_list with comma-separated filter correctly splits names."""
    from conferencing_mcp.tools.rooms import room_list

    result = await room_list(mock_ctx, filter_names="room-alpha,room-beta")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_room_delete(mock_ctx, mock_livekit_api):
    """room_delete calls LiveKit delete and returns status."""
    from conferencing_mcp.tools.rooms import room_delete

    result = await room_delete(mock_ctx, name="old-room")
    assert result["status"] == "DELETED"
    mock_livekit_api["lk_delete_room"].assert_called_once()


@pytest.mark.asyncio
async def test_room_participant_list(mock_ctx, mock_livekit_api):
    """room_participant_list returns participant data."""
    from conferencing_mcp.tools.rooms import room_participant_list

    result = await room_participant_list(mock_ctx, room_name="room-1")
    assert len(result) >= 1
    assert result[0]["identity"] == "alice"


@pytest.mark.asyncio
async def test_room_participant_kick(mock_ctx, mock_livekit_api):
    """Kicking a participant returns status dict."""
    from conferencing_mcp.tools.rooms import room_participant_kick

    result = await room_participant_kick(mock_ctx, room_name="room-1", identity="alice")
    assert result["status"] == "KICKED"


@pytest.mark.asyncio
async def test_room_participant_mute(mock_ctx, mock_livekit_api):
    """Muting returns status with track_sid."""
    from conferencing_mcp.tools.rooms import room_participant_mute

    result = await room_participant_mute(mock_ctx, room_name="r1", identity="bob", track_sid="TR_x")
    assert result["status"] == "MUTED"
    assert result["muted"] is True


@pytest.mark.asyncio
async def test_room_participant_mute_unmute(mock_ctx, mock_livekit_api):
    """Passing muted=False calls mute with False."""
    from conferencing_mcp.tools.rooms import room_participant_mute

    await room_participant_mute(mock_ctx, room_name="r1", identity="bob", track_sid="TR_x", muted=False)
    mock_livekit_api["lk_mute_participant"].assert_called_with("r1", "bob", "TR_x", False)


@pytest.mark.asyncio
async def test_room_send_data(mock_ctx, mock_livekit_api):
    """Sending data broadcasts to the room."""
    from conferencing_mcp.tools.rooms import room_send_data

    result = await room_send_data(mock_ctx, room_name="r1", data='{"type":"ping"}')
    assert result["status"] == "SENT"
