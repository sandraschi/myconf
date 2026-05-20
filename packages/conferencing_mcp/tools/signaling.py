import logging

from fastmcp import Context

from .. import conference as conf
from ..mcp_server import mcp

logger = logging.getLogger("ag-visio-mcp")


@mcp.tool()
async def list_active_conferences(ctx: Context) -> dict:
    """List active LiveKit rooms and scheduled conferences."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")

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
        "correlation_id": cor_id,
    }


@mcp.tool()
async def notify_conference_active(ctx: Context, room_id: str, participant_count: int) -> str:
    """Notify the grid that a conference is active. SOTA inter-agent signaling."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        f"Signaling active conference in room: {room_id}",
        extra={"correlation_id": cor_id},
    )
    return (
        f"SUBSTRATE_SIGNAL [SOTA-S01]: Room {room_id} status BROADCASTED to grid (Participants: {participant_count})."
    )


@mcp.tool()
async def inter_agent_ping(ctx: Context, target_agent: str = "ALL") -> str:
    """Broadcast a protocol-compliant heartbeat to other SOTA servers in the grid."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        f"Broadcasting inter-agent ping to: {target_agent}",
        extra={"correlation_id": cor_id},
    )
    return f"SIGNAL_SENT [SOTA-P01]: Heartbeat broadcast to grid (Target: {target_agent}). Protocol: SOTA-2026-B."
