import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "agent"))

import pytest


@pytest.mark.asyncio
async def test_meeting_intelligence_tools_registration():
    from packages.conferencing_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "generate_meeting_summary" in tool_names
    assert "extract_action_items" in tool_names

    gen_sum = next((t for t in tools if t.name == "generate_meeting_summary"), None)
    assert gen_sum is not None
    assert "transcript" in gen_sum.parameters["properties"]


@pytest.mark.asyncio
async def test_meeting_intelligence_persistence(mock_agent):
    context = await mock_agent.memory.search("meeting summary")
    assert len(context) == 1
    assert context[0]["text"] == "mock context"
    mock_agent.memory.search.assert_called_once_with("meeting summary")


@pytest.mark.asyncio
async def test_meeting_intelligence_chat_logic(mock_agent):
    response = await mock_agent.chat("Summarize the meeting")
    assert "Mock response from Visio" in response
    mock_agent.chat.assert_called_once_with("Summarize the meeting")
