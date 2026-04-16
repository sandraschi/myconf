"""
packages/mcp-server/conference.py
Conference room CRUD, calendaring, and participant management for AG-Visio.

Storage:
  - LiveKit Server API (livekit-api): real-time room and participant operations
  - SQLite (conference.db): persistent calendar / scheduled sessions

Env vars required:
  LIVEKIT_URL     e.g. ws://localhost:7880
  LIVEKIT_API_KEY
  LIVEKIT_API_SECRET
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("ag-visio-mcp.conference")

# ---------------------------------------------------------------------------
# Database bootstrap
# ---------------------------------------------------------------------------

_DB_PATH = Path(__file__).parent / "conference.db"


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS conferences (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                description TEXT,
                room_name   TEXT,              -- LiveKit room name (set when room is created)
                scheduled_at TEXT NOT NULL,    -- ISO-8601 UTC
                duration_min INTEGER NOT NULL DEFAULT 60,
                organizer   TEXT NOT NULL,
                max_participants INTEGER DEFAULT 50,
                metadata    TEXT DEFAULT '{}', -- JSON blob
                status      TEXT DEFAULT 'SCHEDULED',  -- SCHEDULED | ACTIVE | ENDED | CANCELLED
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_conf_scheduled ON conferences(scheduled_at);
            CREATE INDEX IF NOT EXISTS idx_conf_status    ON conferences(status);

            CREATE TABLE IF NOT EXISTS conference_participants (
                id              TEXT PRIMARY KEY,
                conference_id   TEXT NOT NULL REFERENCES conferences(id),
                identity        TEXT NOT NULL,
                display_name    TEXT,
                role            TEXT DEFAULT 'PARTICIPANT',  -- HOST | PARTICIPANT | OBSERVER
                invited_at      TEXT NOT NULL,
                joined_at       TEXT,
                left_at         TEXT,
                UNIQUE(conference_id, identity)
            );
            CREATE INDEX IF NOT EXISTS idx_cp_conf ON conference_participants(conference_id);
            """
        )


_init_db()

# ---------------------------------------------------------------------------
# LiveKit API helpers (lazy-loaded so missing LIVEKIT_* vars only fail at call
# time, not at import time — allows testing without a running LiveKit server)
# ---------------------------------------------------------------------------


def _lk_room_service():
    """Return a livekit.api.RoomServiceClient, or raise with a clear message."""
    try:
        from livekit import api as lk_api  # livekit-api package
    except ImportError as exc:
        raise RuntimeError(
            "livekit-api not installed. Add it to requirements.txt."
        ) from exc

    url = os.environ.get("LIVEKIT_URL", "")
    key = os.environ.get("LIVEKIT_API_KEY", "")
    secret = os.environ.get("LIVEKIT_API_SECRET", "")

    if not all([url, key, secret]):
        raise RuntimeError(
            "LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET must all be set."
        )

    livekit_api = lk_api.LiveKitAPI(url=url, api_key=key, api_secret=secret)
    return livekit_api


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Conference (Calendar) CRUD — pure SQLite, no LiveKit needed
# ---------------------------------------------------------------------------


def schedule_conference(
    title: str,
    scheduled_at: str,
    organizer: str,
    description: str = "",
    duration_min: int = 60,
    max_participants: int = 50,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a new scheduled conference.

    Args:
        title: Human-readable conference title.
        scheduled_at: ISO-8601 UTC datetime, e.g. '2026-03-20T14:00:00Z'.
        organizer: Identity string of the organizer.
        description: Optional conference description.
        duration_min: Expected duration in minutes.
        max_participants: Maximum allowed participants.
        metadata: Arbitrary JSON metadata.

    Returns:
        The created conference record as a dict.
    """
    cid = str(uuid.uuid4())
    now = _now_iso()
    meta_str = json.dumps(metadata or {})
    with _get_db() as conn:
        conn.execute(
            """
            INSERT INTO conferences
              (id, title, description, scheduled_at, duration_min, organizer,
               max_participants, metadata, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?, 'SCHEDULED',?,?)
            """,
            (cid, title, description, scheduled_at, duration_min, organizer,
             max_participants, meta_str, now, now),
        )
    return get_conference(cid)


def get_conference(conference_id: str) -> dict[str, Any]:
    """Fetch a single conference by ID. Raises KeyError if not found."""
    with _get_db() as conn:
        row = conn.execute(
            "SELECT * FROM conferences WHERE id=?", (conference_id,)
        ).fetchone()
    if row is None:
        raise KeyError(f"Conference not found: {conference_id}")
    return dict(row)


def list_conferences(
    status: str | None = None,
    after: str | None = None,
    before: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    List conferences with optional filters.

    Args:
        status: Filter by status (SCHEDULED | ACTIVE | ENDED | CANCELLED).
        after: ISO-8601 lower bound for scheduled_at.
        before: ISO-8601 upper bound for scheduled_at.
        limit: Maximum results.
    """
    clauses: list[str] = []
    params: list[Any] = []
    if status:
        clauses.append("status=?")
        params.append(status)
    if after:
        clauses.append("scheduled_at>=?")
        params.append(after)
    if before:
        clauses.append("scheduled_at<=?")
        params.append(before)
    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    params.append(limit)
    with _get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM conferences {where} ORDER BY scheduled_at ASC LIMIT ?",
            params,
        ).fetchall()
    return [dict(r) for r in rows]


def update_conference(conference_id: str, **fields: Any) -> dict[str, Any]:
    """
    Update mutable fields on a conference.

    Updatable fields: title, description, scheduled_at, duration_min,
    max_participants, metadata, status.
    """
    allowed = {
        "title", "description", "scheduled_at", "duration_min",
        "max_participants", "metadata", "status", "room_name",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        raise ValueError("No valid fields to update.")
    updates["updated_at"] = _now_iso()
    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [conference_id]
    with _get_db() as conn:
        conn.execute(
            f"UPDATE conferences SET {set_clause} WHERE id=?", values
        )
    return get_conference(conference_id)


def cancel_conference(conference_id: str) -> dict[str, Any]:
    """Cancel a scheduled or active conference."""
    return update_conference(conference_id, status="CANCELLED")


# ---------------------------------------------------------------------------
# Participant CRUD (calendar layer — SQLite)
# ---------------------------------------------------------------------------


def invite_participant(
    conference_id: str,
    identity: str,
    display_name: str = "",
    role: str = "PARTICIPANT",
) -> dict[str, Any]:
    """Invite (register) a participant for a scheduled conference."""
    # Check the conference exists
    get_conference(conference_id)
    pid = str(uuid.uuid4())
    now = _now_iso()
    with _get_db() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO conference_participants
              (id, conference_id, identity, display_name, role, invited_at)
            VALUES (?,?,?,?,?,?)
            """,
            (pid, conference_id, identity, display_name, role, now),
        )
    return list_invited_participants(conference_id)


def list_invited_participants(conference_id: str) -> list[dict[str, Any]]:
    """List all invited participants for a conference."""
    with _get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM conference_participants WHERE conference_id=? ORDER BY invited_at",
            (conference_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def remove_invited_participant(conference_id: str, identity: str) -> dict[str, str]:
    """Remove an invitation."""
    with _get_db() as conn:
        conn.execute(
            "DELETE FROM conference_participants WHERE conference_id=? AND identity=?",
            (conference_id, identity),
        )
    return {"status": "removed", "identity": identity, "conference_id": conference_id}


# ---------------------------------------------------------------------------
# LiveKit Room CRUD — real-time operations via LiveKit Server API
# ---------------------------------------------------------------------------


async def lk_create_room(
    name: str,
    max_participants: int = 50,
    empty_timeout: int = 300,
    metadata: str = "",
) -> dict[str, Any]:
    """
    Create a LiveKit room.

    Args:
        name: Room name/identifier.
        max_participants: Participant cap.
        empty_timeout: Seconds until empty room is auto-closed.
        metadata: Arbitrary string metadata attached to the room.
    """
    api = _lk_room_service()
    try:
        from livekit.api import CreateRoomRequest

        room = await api.room.create_room(
            CreateRoomRequest(
                name=name,
                max_participants=max_participants,
                empty_timeout=empty_timeout,
                metadata=metadata,
            )
        )
        return {
            "sid": room.sid,
            "name": room.name,
            "num_participants": room.num_participants,
            "creation_time": room.creation_time,
            "metadata": room.metadata,
        }
    finally:
        await api.aclose()


async def lk_list_rooms(names: list[str] | None = None) -> list[dict[str, Any]]:
    """List all active LiveKit rooms, optionally filtered by name."""
    api = _lk_room_service()
    try:
        from livekit.api import ListRoomsRequest

        resp = await api.room.list_rooms(ListRoomsRequest(names=names or []))
        return [
            {
                "sid": r.sid,
                "name": r.name,
                "num_participants": r.num_participants,
                "creation_time": r.creation_time,
                "metadata": r.metadata,
            }
            for r in resp.rooms
        ]
    finally:
        await api.aclose()


async def lk_delete_room(name: str) -> dict[str, str]:
    """Delete a LiveKit room by name."""
    api = _lk_room_service()
    try:
        from livekit.api import DeleteRoomRequest

        await api.room.delete_room(DeleteRoomRequest(room=name))
        return {"status": "deleted", "room": name}
    finally:
        await api.aclose()


async def lk_update_room_metadata(name: str, metadata: str) -> dict[str, Any]:
    """Update the metadata string on a LiveKit room."""
    api = _lk_room_service()
    try:
        from livekit.api import UpdateRoomMetadataRequest

        room = await api.room.update_room_metadata(
            UpdateRoomMetadataRequest(room=name, metadata=metadata)
        )
        return {"name": room.name, "metadata": room.metadata}
    finally:
        await api.aclose()


# ---------------------------------------------------------------------------
# LiveKit Participant operations
# ---------------------------------------------------------------------------


async def lk_list_participants(room_name: str) -> list[dict[str, Any]]:
    """List all live participants in a LiveKit room."""
    api = _lk_room_service()
    try:
        from livekit.api import ListParticipantsRequest

        resp = await api.room.list_participants(ListParticipantsRequest(room=room_name))
        return [
            {
                "sid": p.sid,
                "identity": p.identity,
                "name": p.name,
                "state": p.state,
                "joined_at": p.joined_at,
                "metadata": p.metadata,
                "is_publisher": p.is_publisher,
            }
            for p in resp.participants
        ]
    finally:
        await api.aclose()


async def lk_kick_participant(room_name: str, identity: str) -> dict[str, str]:
    """Remove a participant from a LiveKit room."""
    api = _lk_room_service()
    try:
        from livekit.api import RemoveParticipantRequest

        await api.room.remove_participant(
            RemoveParticipantRequest(room=room_name, identity=identity)
        )
        return {"status": "kicked", "identity": identity, "room": room_name}
    finally:
        await api.aclose()


async def lk_mute_participant(
    room_name: str,
    identity: str,
    track_sid: str,
    muted: bool = True,
) -> dict[str, Any]:
    """
    Mute or unmute a specific track for a participant.

    Args:
        room_name: LiveKit room name.
        identity: Participant identity.
        track_sid: Track SID to mute/unmute.
        muted: True to mute, False to unmute.
    """
    api = _lk_room_service()
    try:
        from livekit.api import MuteRoomTrackRequest

        resp = await api.room.mute_published_track(
            MuteRoomTrackRequest(
                room=room_name, identity=identity, track_sid=track_sid, muted=muted
            )
        )
        return {
            "track_sid": resp.track.sid,
            "muted": resp.track.muted,
            "identity": identity,
        }
    finally:
        await api.aclose()


async def lk_send_data(
    room_name: str,
    data: str,
    destination_identities: list[str] | None = None,
) -> dict[str, str]:
    """
    Send arbitrary data message to a room or specific participants.

    Args:
        room_name: Target LiveKit room.
        data: UTF-8 string payload (JSON recommended).
        destination_identities: List of identities to target, or None for broadcast.
    """
    api = _lk_room_service()
    try:
        from livekit.api import SendDataRequest

        await api.room.send_data(
            SendDataRequest(
                room=room_name,
                data=data.encode("utf-8"),
                destination_identities=destination_identities or [],
            )
        )
        return {"status": "sent", "room": room_name, "bytes": str(len(data))}
    finally:
        await api.aclose()
