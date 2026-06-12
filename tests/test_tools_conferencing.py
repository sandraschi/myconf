"""Tests for conferencing CRUD tools — schedule, get, list, update, cancel."""

import pytest


@pytest.mark.asyncio
async def test_conference_schedule_and_get(mock_ctx, temp_conference_db):
    """Schedule a conference, then fetch it by ID."""
    _conf, _ = temp_conference_db
    from conferencing_mcp.tools.conferences import conference_get, conference_schedule

    result = await conference_schedule(
        mock_ctx,
        title="Sprint Retro",
        scheduled_at="2026-05-23T16:00:00Z",
        organizer="scrum@example.com",
        duration_min=90,
    )
    assert result["title"] == "Sprint Retro"
    assert result["status"] == "SCHEDULED"
    assert "id" in result

    fetched = await conference_get(mock_ctx, conference_id=result["id"])
    assert fetched["title"] == "Sprint Retro"
    assert fetched["organizer"] == "scrum@example.com"


@pytest.mark.asyncio
async def test_conference_get_missing_returns_error(mock_ctx, temp_conference_db):
    """Fetching a non-existent conference returns error dict."""
    from conferencing_mcp.tools.conferences import conference_get

    result = await conference_get(mock_ctx, conference_id="nonexistent-id")
    assert "error" in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status,days,expected_count_min",
    [
        ("SCHEDULED", 7, 0),
        ("", 30, 0),
    ],
)
async def test_conference_list_empty(status, days, expected_count_min, mock_ctx, temp_conference_db):
    """List (possibly filtered) returns a list, may be empty."""
    from conferencing_mcp.tools.conferences import conference_list

    result = await conference_list(mock_ctx, status=status, limit=50)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_conference_update_title(mock_ctx, temp_conference_db):
    """Update a conference's title and verify persistence."""
    from conferencing_mcp.tools.conferences import (
        conference_schedule,
        conference_update,
    )

    cfg = await conference_schedule(
        mock_ctx, title="Old Title", scheduled_at="2026-05-23T10:00:00Z", organizer="me@x.com"
    )
    cid = cfg["id"]

    updated = await conference_update(mock_ctx, conference_id=cid, title="New Title")
    assert updated["title"] == "New Title"


@pytest.mark.asyncio
async def test_conference_update_empty_fields_error(mock_ctx, temp_conference_db):
    """Passing zero valid fields returns an error."""
    from conferencing_mcp.tools.conferences import conference_update

    result = await conference_update(mock_ctx, conference_id="any")
    assert "error" in result


@pytest.mark.asyncio
async def test_conference_cancel(mock_ctx, temp_conference_db):
    """Cancelling a scheduled conference sets status to CANCELLED."""
    from conferencing_mcp.tools.conferences import (
        conference_cancel,
        conference_schedule,
    )

    cfg = await conference_schedule(
        mock_ctx, title="To Cancel", scheduled_at="2026-05-23T11:00:00Z", organizer="me@x.com"
    )
    result = await conference_cancel(mock_ctx, conference_id=cfg["id"])
    assert result["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_conference_upcoming_returns_list(mock_ctx, temp_conference_db):
    """conference_upcoming returns a list within the N-day window."""
    from conferencing_mcp.tools.conferences import conference_upcoming

    result = await conference_upcoming(mock_ctx, days=14)
    assert isinstance(result, list)
