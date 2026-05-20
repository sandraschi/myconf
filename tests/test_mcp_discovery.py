"""Monorepo-wide MCP discovery tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "agent"))


async def test_remoting_mcp_discovery():
    from packages.remoting_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    required_tools = ["move_mouse", "click_mouse", "type_text", "join_meeting", "leave_meeting"]

    for tool in required_tools:
        assert tool in tool_names, f"Missing tool: {tool}"


async def test_conferencing_mcp_discovery():
    from packages.conferencing_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    required_tools = ["generate_meeting_summary", "extract_action_items", "conference_schedule"]

    for tool in required_tools:
        assert tool in tool_names, f"Missing tool: {tool}"
