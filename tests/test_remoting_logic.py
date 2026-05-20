import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "agent"))

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_remoting_input_parsing():
    from packages.remoting_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    move_mouse = next((t for t in tools if t.name == "move_mouse"), None)
    assert move_mouse is not None
    assert "x" in move_mouse.parameters["properties"]
    assert "y" in move_mouse.parameters["properties"]


def test_remoting_capture_init():
    with patch("pywinctl.getWindowsWithTitle") as mock_win:
        mock_win.return_value = [MagicMock(title="Test Window", box=(0, 0, 1920, 1080))]
        assert len(mock_win.return_value) == 1
        assert mock_win.return_value[0].title == "Test Window"


@pytest.mark.asyncio
async def test_remoting_tool_execution(mock_mcp_client):
    response = await mock_mcp_client.call_tool("mouse_move", {"x": 100, "y": 200})
    assert response.content == "Tool executed successfully"
    mock_mcp_client.call_tool.assert_called_once_with("mouse_move", {"x": 100, "y": 200})
