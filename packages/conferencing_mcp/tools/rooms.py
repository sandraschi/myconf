import logging
from typing import Any

from fastmcp import Context

from .. import conference as conf
from ..mcp_server import mcp

logger = logging.getLogger("ag-visio-mcp")


@mcp.tool()
async def room_create(
    ctx: Context,
    name: str,
    max_participants: int = 50,
    empty_timeout: int = 300,
    metadata: str = "",
) -> dict[str, Any]:
    """Create a LiveKit room.

    Args:
        name: Room name (unique identifier).
        max_participants: Hard participant cap.
        empty_timeout: Seconds until empty room auto-closes.
        metadata: Arbitrary string metadata.
    """
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    try:
        return await conf.lk_create_room(name, max_participants, empty_timeout, metadata)
    except Exception as exc:
        logger.error("room_create failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


@mcp.tool()
async def room_list(ctx: Context, filter_names: str = "") -> list[dict[str, Any]]:
    """List all active LiveKit rooms.

    Args:
        filter_names: Comma-separated room names to filter by (empty = all).
    """
    names = [n.strip() for n in filter_names.split(",") if n.strip()] if filter_names else None
    try:
        return await conf.lk_list_rooms(names)
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def room_delete(ctx: Context, name: str) -> dict[str, str]:
    """Delete a LiveKit room by name. Kicks all participants."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    try:
        return await conf.lk_delete_room(name)
    except Exception as exc:
        logger.error("room_delete failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


@mcp.tool()
async def room_update_metadata(ctx: Context, name: str, metadata: str) -> dict[str, Any]:
    """Update the metadata string on a LiveKit room."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    try:
        return await conf.lk_update_room_metadata(name, metadata)
    except Exception as exc:
        logger.error("room_update_metadata failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


@mcp.tool()
async def room_participant_list(ctx: Context, room_name: str) -> list[dict[str, Any]]:
    """List all live participants currently in a LiveKit room."""
    try:
        return await conf.lk_list_participants(room_name)
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def room_participant_kick(ctx: Context, room_name: str, identity: str) -> dict[str, str]:
    """Kick (remove) a participant from a live LiveKit room."""
    try:
        return await conf.lk_kick_participant(room_name, identity)
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def room_participant_mute(
    ctx: Context,
    room_name: str,
    identity: str,
    track_sid: str,
    muted: bool = True,
) -> dict[str, Any]:
    """Mute or unmute a participant's track in a live LiveKit room.

    Args:
        room_name: Target room.
        identity: Participant identity.
        track_sid: Track SID (get from room_participant_list).
        muted: True to mute, False to unmute.
    """
    try:
        return await conf.lk_mute_participant(room_name, identity, track_sid, muted)
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
async def room_send_data(
    ctx: Context,
    room_name: str,
    data: str,
    destination_identities: str = "",
) -> dict[str, str]:
    """Send a data message to a LiveKit room or specific participants.

    Args:
        room_name: Target room.
        data: UTF-8 string payload (JSON recommended).
        destination_identities: Comma-separated identities (empty = broadcast).
    """
    identities = [i.strip() for i in destination_identities.split(",") if i.strip()] if destination_identities else None
    try:
        return await conf.lk_send_data(room_name, data, identities)
    except Exception as exc:
        return {"error": str(exc)}
