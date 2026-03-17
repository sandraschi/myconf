"""Unit tests for the VisioAgent session logic."""

import sys
from unittest.mock import AsyncMock, MagicMock


# Robust mocking of livekit package structure for environments without dependencies
class MockModule(MagicMock):
    def __getattr__(self, name):
        return MagicMock()

def setup_livekit_mocks():
    if "livekit" not in sys.modules:
        livekit = MockModule()
        sys.modules["livekit"] = livekit
        sys.modules["livekit.rtc"] = MockModule()
        sys.modules["livekit.agents"] = MockModule()
        sys.modules["livekit.agents.llm"] = MockModule()
        sys.modules["livekit.agents.pipeline"] = MockModule()
        sys.modules["livekit.agents.voice"] = MockModule()
        sys.modules["livekit.plugins"] = MockModule()
        sys.modules["livekit.plugins.piper_tts"] = MockModule()
        for plugin in ["deepgram", "openai", "silero", "turn_detector", "whisper"]:
            sys.modules[f"livekit.plugins.{plugin}"] = MockModule()

setup_livekit_mocks()

if "ollama" not in sys.modules:
    sys.modules["ollama"] = MockModule()


import pytest

from agent.agent import VisioTools


class TestVisioTools:
    """Verifies that the agent tools (FunctionContext) are correctly implemented."""

    @pytest.fixture
    def tools(self):
        """Returns a VisioTools instance with mocked dependencies."""
        mock_logic = MagicMock()
        mock_memory = MagicMock()
        mock_room = MagicMock()
        mock_contacts = MagicMock()
        return VisioTools(mock_logic, mock_memory, mock_room, mock_contacts)

    def test_tool_registration(self, tools):
        """Standard check: Search and sync tools must be exposed to LLM."""
        assert hasattr(tools, "search_knowledge_base")
        assert hasattr(tools, "sync_contacts")
        assert hasattr(tools, "search_contacts")

    def test_search_knowledge_base_orchestration(self, tools):
        """Verifies the tools correctly delegate search to memory substrate (Synchronous)."""
        tools._memory.query_history.return_value = [{"speaker": "Sandra", "text": "Found it"}]
        tools._memory.query_codebase.return_value = [{"file_path": "app.py", "text": "code snippet"}]

        # In agent.py, search_knowledge_base is a synchronous method (def)
        result = tools.search_knowledge_base("test query")

        assert "Sandra" in result
        assert "Found it" in result
        assert "app.py" in result
        tools._memory.query_history.assert_called_with("test query", limit=3)
        tools._memory.query_codebase.assert_called_with("test query", limit=2)

    def test_search_knowledge_base_no_hits(self, tools):
        """Ensures a polite fallback when no context is found."""
        tools._memory.query_history.return_value = []
        tools._memory.query_codebase.return_value = []

        result = tools.search_knowledge_base("unfindable")
        assert "No relevant historical or technical context" in result

    @pytest.mark.asyncio
    async def test_sync_contacts_orchestration(self, tools):
        """Verifies delegation to contact manager for full sync (Asynchronous)."""
        tools._contacts.sync_all = AsyncMock(return_value=[MagicMock(), MagicMock()])

        # In agent.py, sync_contacts is an asynchronous method (async def)
        result = await tools.sync_contacts()

        assert "SUCCESS" in result
        assert "2 contacts" in result
        tools._contacts.sync_all.assert_called_once()
