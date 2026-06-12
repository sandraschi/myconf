import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "apps" / "agent"))
sys.path.insert(0, str(ROOT / "packages"))


# ── Existing fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def mcp_mock():
    from fastmcp import FastMCP

    mcp = FastMCP("test-server")

    @mcp.tool()
    def test_tool(x: int) -> int:
        return x * 2

    return mcp


@pytest.fixture
def livekit_session():
    room = MagicMock()
    room.name = "test-room"
    room.local_participant = MagicMock()
    room.local_participant.publish_data = AsyncMock()
    room.remote_participants = {}
    return room


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.name = "Visio"
    agent.memory = MagicMock()
    agent.memory.search = AsyncMock(return_value=[{"text": "mock context", "score": 0.9}])
    agent.chat = AsyncMock(return_value="Mock response from Visio.")
    return agent


@pytest.fixture
def mock_mcp_client():
    client = AsyncMock()
    client.list_tools = AsyncMock(return_value=[MagicMock(name="test_tool", description="A test tool")])
    client.call_tool = AsyncMock(return_value=MagicMock(content="Tool executed successfully"))
    return client


@pytest.fixture
def temp_lancedb():
    import lancedb

    tmpdir = tempfile.mkdtemp()
    db = lancedb.connect(tmpdir)
    yield db
    import shutil

    shutil.rmtree(tmpdir, ignore_errors=True)


# ── FastMCP Context mock ─────────────────────────────────────────────────────


class _SampleContent:
    def __init__(self, text: str):
        self.content = _SampleText(text)


class _SampleText:
    def __init__(self, text: str):
        self.text = text


@pytest.fixture
def mock_ctx():
    """Mock FastMCP Context with correlation_id and async sample()."""
    ctx = MagicMock()
    ctx.correlation_id = "TEST-CID-001"
    ctx.sample = AsyncMock(return_value=_SampleContent("Mocked LLM response from ctx.sample()"))
    return ctx


# ── Conference DB fixtures ───────────────────────────────────────────────────


@pytest.fixture
def temp_conference_db(monkeypatch, tmp_path):
    """Redirect conference.db to tmp_path and bootstrap tables."""
    from conferencing_mcp import conference as conf

    db_path = tmp_path / "conference.db"
    monkeypatch.setattr(conf, "_DB_PATH", db_path)
    conf._init_db()
    yield conf, db_path


# ── LiveKit API mock ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_livekit_api(monkeypatch):
    """Mock all livekit-api async calls used by room and signaling tools."""
    import conferencing_mcp.conference as conf

    mocks = {
        "lk_list_rooms": AsyncMock(
            return_value=[
                {"name": "room-alpha", "num_participants": 2},
                {"name": "room-beta", "num_participants": 0},
            ]
        ),
        "lk_create_room": AsyncMock(return_value={"name": "new-room", "sid": "RM_test"}),
        "lk_delete_room": AsyncMock(return_value={"status": "DELETED"}),
        "lk_update_room_metadata": AsyncMock(return_value={"name": "room-1", "metadata": '{"k":"v"}'}),
        "lk_list_participants": AsyncMock(
            return_value=[
                {"identity": "alice", "sid": "PA_A", "tracks": [{"sid": "TR_1", "muted": False}]},
            ]
        ),
        "lk_kick_participant": AsyncMock(return_value={"status": "KICKED"}),
        "lk_mute_participant": AsyncMock(return_value={"status": "MUTED", "track_sid": "TR_1", "muted": True}),
        "lk_send_data": AsyncMock(return_value={"status": "SENT"}),
    }
    for name, mock_fn in mocks.items():
        monkeypatch.setattr(conf, name, mock_fn)
    return mocks


# ── Subprocess / socket mock ─────────────────────────────────────────────────


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess.run for diagnostics tools."""
    import subprocess

    def _mock_run(args, capture_output=False, text=False, check=False, **kwargs):
        result = MagicMock()
        result.stdout = "mock stdout"
        result.stderr = ""
        result.returncode = 0
        return result

    monkeypatch.setattr(subprocess, "run", _mock_run)
    monkeypatch.setattr(subprocess, "Popen", MagicMock(return_value=MagicMock(pid=9999)))
