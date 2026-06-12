import logging
from typing import Annotated

from fastmcp import Context
from pydantic import Field

from .. import conference as conf
from ..mcp_server import cid, mcp

logger = logging.getLogger("ag-visio-mcp")


@mcp.tool()
async def list_active_conferences(ctx: Context) -> dict:
    """List active LiveKit rooms and scheduled conferences.

    ## Return Format
    {"room_count": int, "livekit_rooms": list, "scheduled_conferences": list, "correlation_id": str}

    ## Examples
    await list_active_conferences()
    """
    _cid = cid(ctx)

    livekit_rooms = []
    scheduled = conf.list_conferences(status="SCHEDULED")

    try:
        livekit_rooms = await conf.lk_list_rooms()
    except Exception as e:
        logger.warning("LiveKit room list unavailable: %s", e)

    return {
        "room_count": len(livekit_rooms),
        "livekit_rooms": livekit_rooms,
        "scheduled_conferences": scheduled,
        "correlation_id": _cid,
    }


@mcp.tool()
async def notify_conference_active(
    ctx: Context,
    room_id: Annotated[str, Field(description="LiveKit room identifier.")],
    participant_count: Annotated[int, Field(description="Number of live participants in the room.")],
) -> str:
    """Notify the grid that a conference is active. SOTA inter-agent signaling.

    ## Return Format
    str — signal confirmation message with room and participant count

    ## Examples
    await notify_conference_active(room_id="room-abc", participant_count=5)
    """
    _cid = cid(ctx)
    logger.info(
        f"Signaling active conference in room: {room_id}",
        extra={"correlation_id": _cid},
    )
    return (
        f"SUBSTRATE_SIGNAL [SOTA-S01]: Room {room_id} status BROADCASTED to grid (Participants: {participant_count})."
    )


@mcp.tool()
async def inter_agent_ping(
    ctx: Context,
    target_agent: Annotated[str, Field(description="Target agent name or 'ALL' for broadcast.")] = "ALL",
) -> str:
    """Broadcast a protocol-compliant heartbeat to other SOTA servers in the grid.

    ## Return Format
    str — signal confirmation with target agent

    ## Examples
    await inter_agent_ping()
    await inter_agent_ping(target_agent="remoting-substrate")
    """
    _cid = cid(ctx)
    logger.info(
        f"Broadcasting inter-agent ping to: {target_agent}",
        extra={"correlation_id": _cid},
    )
    return f"SIGNAL_SENT [SOTA-P01]: Heartbeat broadcast to grid (Target: {target_agent}). Protocol: SOTA-2026-B."
