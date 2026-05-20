import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "agent"))

import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mcp_mock():
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
