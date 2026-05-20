import logging
from datetime import timedelta
from typing import Any

from fastmcp import Context

from .. import conference as conf
from ..mcp_server import mcp

logger = logging.getLogger("ag-visio-mcp")


@mcp.tool()
async def conference_schedule(
    ctx: Context,
    title: str,
    scheduled_at: str,
    organizer: str,
    description: str = "",
    duration_min: int = 60,
    max_participants: int = 50,
) -> dict[str, Any]:
    """Schedule a new conference.

    Args:
        title: Conference title.
        scheduled_at: ISO-8601 UTC datetime, e.g. 2026-03-20T14:00:00Z.
        organizer: Identity of the organizer.
        description: Optional description.
        duration_min: Expected duration in minutes (default 60).
        max_participants: Participant cap (default 50).
    """
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Scheduling conference: %s", title, extra={"correlation_id": cor_id})
    return conf.schedule_conference(
        title=title,
        scheduled_at=scheduled_at,
        organizer=organizer,
        description=description,
        duration_min=duration_min,
        max_participants=max_participants,
    )


@mcp.tool()
async def conference_get(ctx: Context, conference_id: str) -> dict[str, Any]:
    """Fetch a single scheduled conference by ID."""
    try:
        return conf.get_conference(conference_id)
    except KeyError as exc:
        return {"error": str(exc)}


@mcp.tool()
async def conference_list(
    ctx: Context,
    status: str = "",
    after: str = "",
    before: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List conferences with optional filters.

    Args:
        status: Filter by status: SCHEDULED | ACTIVE | ENDED | CANCELLED (empty = all).
        after: ISO-8601 lower bound for scheduled_at (empty = no lower bound).
        before: ISO-8601 upper bound for scheduled_at (empty = no upper bound).
        limit: Max results (default 50).
    """
    return conf.list_conferences(
        status=status or None,
        after=after or None,
        before=before or None,
        limit=limit,
    )


@mcp.tool()
async def conference_update(
    ctx: Context,
    conference_id: str,
    title: str = "",
    description: str = "",
    scheduled_at: str = "",
    duration_min: int = 0,
    max_participants: int = 0,
    status: str = "",
) -> dict[str, Any]:
    """Update mutable fields on a scheduled conference.

    Only non-empty / non-zero args are applied.
    """
    fields: dict[str, Any] = {}
    if title:
        fields["title"] = title
    if description:
        fields["description"] = description
    if scheduled_at:
        fields["scheduled_at"] = scheduled_at
    if duration_min > 0:
        fields["duration_min"] = duration_min
    if max_participants > 0:
        fields["max_participants"] = max_participants
    if status:
        fields["status"] = status
    if not fields:
        return {"error": "No fields provided to update."}
    try:
        return conf.update_conference(conference_id, **fields)
    except KeyError as exc:
        return {"error": str(exc)}


@mcp.tool()
async def conference_cancel(ctx: Context, conference_id: str) -> dict[str, Any]:
    """Cancel a scheduled or active conference."""
    try:
        return conf.cancel_conference(conference_id)
    except KeyError as exc:
        return {"error": str(exc)}


@mcp.tool()
async def conference_upcoming(ctx: Context, days: int = 7) -> list[dict[str, Any]]:
    """List SCHEDULED conferences in the next N days (default 7)."""
    now = conf._now_iso()
    horizon = (conf.datetime.now(conf.timezone.utc) + timedelta(days=days)).isoformat().replace("+00:00", "Z")
    return conf.list_conferences(status="SCHEDULED", after=now, before=horizon)


@mcp.tool()
async def participant_invite(
    ctx: Context,
    conference_id: str,
    identity: str,
    display_name: str = "",
    role: str = "PARTICIPANT",
) -> list[dict[str, Any]]:
    """Invite a participant to a scheduled conference.

    Args:
        conference_id: Conference UUID.
        identity: Unique identity string (e.g. email or username).
        display_name: Human-readable name.
        role: HOST | PARTICIPANT | OBSERVER (default PARTICIPANT).
    """
    try:
        return conf.invite_participant(conference_id, identity, display_name, role)
    except KeyError as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def participant_list_invited(ctx: Context, conference_id: str) -> list[dict[str, Any]]:
    """List all invited participants for a scheduled conference."""
    return conf.list_invited_participants(conference_id)


@mcp.tool()
async def participant_remove_invited(ctx: Context, conference_id: str, identity: str) -> dict[str, str]:
    """Remove a participant invitation from a scheduled conference."""
    return conf.remove_invited_participant(conference_id, identity)
