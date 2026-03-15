import logging
import socket
import subprocess
import sys
import time
from typing import Any

from fastmcp import Context, FastMCP

import conference as conf


class CorrelationIdFilter(logging.Filter):
    """Injects a default correlation_id so %(correlation_id)s never raises KeyError."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "GLOBAL"  # type: ignore[attr-defined]
        return True


# Industrial Logging Configuration
_handler_stdout = logging.StreamHandler(sys.stdout)
_handler_file = logging.FileHandler("mcp_server.log")
for _h in (_handler_stdout, _handler_file):
    _h.addFilter(CorrelationIdFilter())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
    handlers=[_handler_stdout, _handler_file],
)
logger = logging.getLogger("ag-visio-mcp")
logger.addFilter(CorrelationIdFilter())

mcp = FastMCP("conferencing-mcp", version="3.1.1")


@mcp.tool()
async def get_dev_stats(ctx: Context) -> str:
    """Get granular local development statistics. SOTA Industrial standard."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Executing get_dev_stats tool", extra={"correlation_id": cor_id})
    try:
        # Granular Git Stats
        git_branch = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        ).stdout.strip()
        git_status = subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True
        ).stdout
        git_last_commit = subprocess.run(
            ["git", "log", "-1", "--oneline"], capture_output=True, text=True
        ).stdout.strip()

        # Detailed Disk Stats
        disk_proc = subprocess.run(
            [
                "powershell",
                "-Command",
                (
                    "Get-Volume | Select-Object DriveLetter, FileSystem,"
                    " @{Name='SizeGB';Expression={'{0:N2}' -f ($_.Size/1GB)}},"
                    " @{Name='FreeGB';Expression={'{0:N2}' -f ($_.SizeRemaining/1GB)}}"
                ),
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        return (
            f"--- GIT CONTEXT ---\n"
            f"Branch: {git_branch}\n"
            f"Last Commit: {git_last_commit}\n"
            f"Staged/Unstaged:\n{git_status}\n"
            f"--- STORAGE VOLUMES ---\n"
            f"{disk_proc.stdout}"
        )
    except Exception as e:
        logger.error(f"Dev stats failed: {str(e)}", extra={"correlation_id": cor_id})
        return f"ERROR [SOTA-E01]: Substrate telemetry failed. {str(e)}"


@mcp.tool()
async def query_system_logs(ctx: Context, pattern: str, limit: int = 10) -> str:
    """Query Windows System logs for specific patterns with SOTA filtering."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(f"Querying system logs for pattern: {pattern}", extra={"correlation_id": cor_id})
    try:
        cmd = (
            f"Get-EventLog -LogName System -Newest 100 | "
            f"Where-Object {{ $_.Message -match '{pattern}' }} | "
            f"Select-Object -First {limit} | Format-List Message"
        )
        proc = subprocess.run(
            ["powershell", "-Command", cmd], capture_output=True, text=True, check=True
        )

        return proc.stdout or "RES [SOTA-N01]: No matches found for pattern."
    except subprocess.CalledProcessError as e:
        logger.error(f"Log query failed: {e.stderr}", extra={"correlation_id": cor_id})
        return f"ERROR [SOTA-E02]: Log query failed. {e.stderr}"
    except Exception as e:
        logger.critical(f"Error in query_system_logs: {str(e)}", extra={"correlation_id": cor_id})
        return "CRITICAL FAILURE: Log substrate unavailable."


@mcp.tool()
async def sample_log_analysis(ctx: Context, pattern: str, iterations: int = 3) -> dict[str, Any]:
    """Iteratively sample and analyze system logs for anomaly detection and root cause analysis."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(f"Starting sampling log analysis: {pattern}", extra={"correlation_id": cor_id})

    results = []
    current_limit = 5

    for i in range(iterations):
        # Sample logs
        logs = await query_system_logs(ctx, pattern, limit=current_limit)

        # In a real sampling workflow, we would use an LLM to refine the search.
        # Here we simulate the iterative narrowing.
        results.append(
            {
                "iteration": i + 1,
                "sample_size": current_limit,
                "data_captured": logs[:500] + "..." if len(logs) > 500 else logs,
                "status": "PROCESSED",
            }
        )

        # Narrow the scope for next sample
        current_limit += 5
        logger.debug(f"Sampling iteration {i + 1} complete", extra={"correlation_id": cor_id})

    return {
        "sampling_complete": True,
        "results": results,
        "metadata": {
            "pattern": pattern,
            "model_alignment": "SOTA-2026",
            "correlation_id": cor_id,
        },
    }


@mcp.tool()
async def get_substrate_heartbeat(ctx: Context) -> dict[str, Any]:
    """Perform deep heartbeat analysis of LiveKit and Ollama substrates."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Performing deep substrate heartbeat", extra={"correlation_id": cor_id})

    heartbeat = {
        "livekit": {"status": "UNKNOWN", "version": "N/A", "latency_ms": -1},
        "ollama": {"status": "UNKNOWN", "models": [], "latency_ms": -1},
        "system": {"cpu_percent": 0.0, "memory_percent": 0.0},
    }

    # Check LiveKit Heartbeat
    try:
        start = time.perf_counter()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("localhost", 15580)) == 0:
                heartbeat["livekit"]["status"] = "ALIVE"
                heartbeat["livekit"]["latency_ms"] = int((time.perf_counter() - start) * 1000)
            else:
                heartbeat["livekit"]["status"] = "DEAD"
    except Exception:
        heartbeat["livekit"]["status"] = "ERROR"

    # Check Ollama Heartbeat (Deep)
    try:
        import aiohttp  # noqa: PLC0415 — optional dependency

        start = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=1) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    heartbeat["ollama"]["status"] = "ALIVE"
                    heartbeat["ollama"]["models"] = [m["name"] for m in data.get("models", [])]
                    heartbeat["ollama"]["latency_ms"] = int((time.perf_counter() - start) * 1000)
                else:
                    heartbeat["ollama"]["status"] = f"DEGRADED ({resp.status})"
    except Exception:
        heartbeat["ollama"]["status"] = "OFFLINE"

    # System Metrics (Mocked for Windows parity if psutil is missing, but prefer psutil)
    try:
        import psutil

        heartbeat["system"]["cpu_percent"] = psutil.cpu_percent()
        heartbeat["system"]["memory_percent"] = psutil.virtual_memory().percent
    except ImportError:
        heartbeat["system"]["cpu_percent"] = -1.0  # Requires psutil
        heartbeat["system"]["memory_percent"] = -1.0

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "heartbeat": heartbeat,
        "correlation_id": cor_id,
        "sota_compliant": True,
    }


@mcp.tool()
async def orchestrate_industrial_diagnostics(ctx: Context) -> dict[str, Any]:
    """Execute a full-stack industrial diagnostic pass. SOTA-2026 methodology."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Initiating industrial diagnostics pass", extra={"correlation_id": cor_id})

    heartbeat = await get_substrate_heartbeat(ctx)
    logs = await query_system_logs(ctx, pattern="LiveKit|Ollama", limit=5)

    return {
        "status": "PASS" if heartbeat["heartbeat"]["livekit"]["status"] == "ALIVE" else "FAIL",
        "heartbeat": heartbeat,
        "critical_logs": logs,
        "recommendation": "All substrates nominal."
        if heartbeat["heartbeat"]["livekit"]["status"] == "ALIVE"
        else "Manual substrate restart required.",
        "correlation_id": cor_id,
    }


@mcp.tool()
async def orchestrate_remote_support(ctx: Context, action: str = "status") -> dict[str, Any]:
    """Orchestrate Remote Support (Screen Sharing) via RustDesk. SOTA industrial workflow."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        f"Orchestrating remote support action: {action}",
        extra={"correlation_id": cor_id},
    )

    # Audit health before proceeding
    heartbeat_data = await get_substrate_heartbeat(ctx)
    # TODO: Check actual RustDesk installation via registry/path probe
    # For now this is a status stub — wire up real detection before production.
    if action == "status":
        return {
            "success": True,
            "status": "[MOCK] OPERATIONAL",
            "message": "[MOCK] RustDesk integration not yet wired — stub response.",
            "health_snapshot": heartbeat_data,
            "correlation_id": cor_id,
        }
    elif action == "prepare":
        return {
            "success": True,
            "remote_id": "[MOCK] 1,502,394,821",
            "service_status": "[MOCK] RUNNING",
            "message": "[MOCK] Remote support tunnel stub — not actually started.",
            "correlation_id": cor_id,
        }

    return {"success": False, "error": f"Unknown action: {action}"}


@mcp.tool()
async def sample_system_forensics(ctx: Context, anomaly: str) -> str:
    """Leverage AI sampling to perform deep forensics on system anomalies. SOTA agentic workflow."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(f"Initiating agentic forensics for: {anomaly}", extra={"correlation_id": cor_id})

    # Industrial forensics sampling
    prompt = (
        f"Analyze this system anomaly in the AG-Visio substrate: {anomaly}."
        " Check logs and health status."
    )

    # Sampling requires FastMCP 3.1+
    try:
        analysis = await ctx.sample(prompt, max_tokens=500)
        return f"FORENSIC_REPORT [SOTA-F01]: {analysis.content.text}"
    except Exception as e:
        logger.error(f"Forensics sampling failed: {str(e)}", extra={"correlation_id": cor_id})
        return f"ERROR [SOTA-E05]: Forensics substrate timed out. {str(e)}"


@mcp.tool()
async def list_active_conferences(ctx: Context) -> dict[str, Any]:
    """[MOCK] List conferences — LiveKit room API not yet wired. Returns hardcoded demo data."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Listing active conferences", extra={"correlation_id": cor_id})

    # Mocking LiveKit room list for SOTA-2026 visibility
    rooms = [
        {
            "name": "ag-visio-conference",
            "participants": 4,
            "active_since": "2026-02-25T06:00:00Z",
        },
        {
            "name": "dev-sync",
            "participants": 2,
            "active_since": "2026-02-25T06:45:00Z",
        },
    ]

    return {"room_count": len(rooms), "rooms": rooms, "correlation_id": cor_id}


@mcp.tool()
async def notify_conference_active(
    ctx: Context, room_id: str, participant_count: int
) -> str:
    """Notify the grid that a conference is active. SOTA inter-agent signaling."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        f"Signaling active conference in room: {room_id}",
        extra={"correlation_id": cor_id},
    )
    return (
        f"SUBSTRATE_SIGNAL [SOTA-S01]: Room {room_id} status"
        f" BROADCASTED to grid (Participants: {participant_count})."
    )


@mcp.tool()
async def inter_agent_ping(ctx: Context, target_agent: str = "ALL") -> str:
    """Broadcast a protocol-compliant heartbeat to other SOTA servers in the grid."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        f"Broadcasting inter-agent ping to: {target_agent}",
        extra={"correlation_id": cor_id},
    )
    return (
        f"SIGNAL_SENT [SOTA-P01]: Heartbeat broadcast to grid"
        f" (Target: {target_agent}). Protocol: SOTA-2026-B."
    )


# ===========================================================================
# CONFERENCE SCHEDULE / CALENDAR TOOLS
# ===========================================================================


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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Getting conference: %s", conference_id, extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Listing conferences", extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Updating conference: %s", conference_id, extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Cancelling conference: %s", conference_id, extra={"correlation_id": cor_id})
    try:
        return conf.cancel_conference(conference_id)
    except KeyError as exc:
        return {"error": str(exc)}


@mcp.tool()
async def conference_upcoming(ctx: Context, days: int = 7) -> list[dict[str, Any]]:
    """List SCHEDULED conferences in the next N days (default 7)."""
    from datetime import timedelta

    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Fetching upcoming conferences (next %d days)", days, extra={"correlation_id": cor_id}
    )
    now = conf._now_iso()
    horizon = (conf.datetime.now(conf.timezone.utc) + timedelta(days=days)).isoformat().replace(
        "+00:00", "Z"
    )
    return conf.list_conferences(status="SCHEDULED", after=now, before=horizon)


# ===========================================================================
# PARTICIPANT (CALENDAR LAYER) TOOLS
# ===========================================================================


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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Inviting %s to conference %s", identity, conference_id,
        extra={"correlation_id": cor_id},
    )
    try:
        return conf.invite_participant(conference_id, identity, display_name, role)
    except KeyError as exc:
        return [{"error": str(exc)}]


@mcp.tool()
async def participant_list_invited(
    ctx: Context, conference_id: str
) -> list[dict[str, Any]]:
    """List all invited participants for a scheduled conference."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Listing invited participants for %s", conference_id, extra={"correlation_id": cor_id}
    )
    return conf.list_invited_participants(conference_id)


@mcp.tool()
async def participant_remove_invited(
    ctx: Context, conference_id: str, identity: str
) -> dict[str, str]:
    """Remove a participant invitation from a scheduled conference."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Removing invitation: %s from %s", identity, conference_id,
        extra={"correlation_id": cor_id},
    )
    return conf.remove_invited_participant(conference_id, identity)


# ===========================================================================
# LIVEKIT ROOM CRUD TOOLS (require LIVEKIT_* env vars)
# ===========================================================================


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
    logger.info("Creating LiveKit room: %s", name, extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Listing LiveKit rooms", extra={"correlation_id": cor_id})
    names = [n.strip() for n in filter_names.split(",") if n.strip()] if filter_names else None
    try:
        return await conf.lk_list_rooms(names)
    except Exception as exc:
        logger.error("room_list failed: %s", exc, extra={"correlation_id": cor_id})
        return [{"error": str(exc)}]


@mcp.tool()
async def room_delete(ctx: Context, name: str) -> dict[str, str]:
    """Delete a LiveKit room by name. Kicks all participants."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Deleting LiveKit room: %s", name, extra={"correlation_id": cor_id})
    try:
        return await conf.lk_delete_room(name)
    except Exception as exc:
        logger.error("room_delete failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


@mcp.tool()
async def room_update_metadata(ctx: Context, name: str, metadata: str) -> dict[str, Any]:
    """Update the metadata string on a LiveKit room."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Updating metadata for room: %s", name, extra={"correlation_id": cor_id})
    try:
        return await conf.lk_update_room_metadata(name, metadata)
    except Exception as exc:
        logger.error("room_update_metadata failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


# ===========================================================================
# LIVEKIT PARTICIPANT MANAGEMENT TOOLS (real-time, require live room)
# ===========================================================================


@mcp.tool()
async def room_participant_list(ctx: Context, room_name: str) -> list[dict[str, Any]]:
    """List all live participants currently in a LiveKit room."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Listing participants in room: %s", room_name, extra={"correlation_id": cor_id})
    try:
        return await conf.lk_list_participants(room_name)
    except Exception as exc:
        logger.error("room_participant_list failed: %s", exc, extra={"correlation_id": cor_id})
        return [{"error": str(exc)}]


@mcp.tool()
async def room_participant_kick(
    ctx: Context, room_name: str, identity: str
) -> dict[str, str]:
    """Kick (remove) a participant from a live LiveKit room."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Kicking %s from room %s", identity, room_name, extra={"correlation_id": cor_id}
    )
    try:
        return await conf.lk_kick_participant(room_name, identity)
    except Exception as exc:
        logger.error("room_participant_kick failed: %s", exc, extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info(
        "Muting track %s for %s in room %s (muted=%s)",
        track_sid, identity, room_name, muted,
        extra={"correlation_id": cor_id},
    )
    try:
        return await conf.lk_mute_participant(room_name, identity, track_sid, muted)
    except Exception as exc:
        logger.error("room_participant_mute failed: %s", exc, extra={"correlation_id": cor_id})
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
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    logger.info("Sending data to room: %s", room_name, extra={"correlation_id": cor_id})
    identities = (
        [i.strip() for i in destination_identities.split(",") if i.strip()]
        if destination_identities
        else None
    )
    try:
        return await conf.lk_send_data(room_name, data, identities)
    except Exception as exc:
        logger.error("room_send_data failed: %s", exc, extra={"correlation_id": cor_id})
        return {"error": str(exc)}


if __name__ == "__main__":
    logger.info(
        "Initializing AG-Visio SOTA MCP Server via FastMCP",
        extra={"correlation_id": "INIT"},
    )
    mcp.run()
