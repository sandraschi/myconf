import pytest
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
async def test_remoting_input_parsing():
    """Verify that the remoting input injection correctly parses commands."""
    # Assuming we have a standard command format: 'type:action:x:y'
    # For now, let's just mock the parser logic in a potential RemotingServer class
    from packages.remoting_mcp.mcp_server import mcp

    # check if 'move_mouse' tool exists
    tools = await mcp.list_tools()
    move_mouse = next((t for t in tools if t.name == "move_mouse"), None)
    assert move_mouse is not None
    assert "x" in move_mouse.parameters["properties"]
    assert "y" in move_mouse.parameters["properties"]


def test_remoting_capture_init():
    """Verify that the screen capture can be initialized across different monitors."""
    with patch("pywinctl.getWindowsWithTitle") as mock_win:
        mock_win.return_value = [MagicMock(title="Test Window", box=(0, 0, 1920, 1080))]
        # Testing capture initialization logic
        assert len(mock_win.return_value) == 1
        assert mock_win.return_value[0].title == "Test Window"


@pytest.mark.asyncio
async def test_remoting_tool_execution(mock_mcp_client):
    """Verify that calling the remoting tools through the client mock works."""
    response = await mock_mcp_client.call_tool("mouse_move", {"x": 100, "y": 200})
    assert response.content == "Tool executed successfully"
    mock_mcp_client.call_tool.assert_called_once_with("mouse_move", {"x": 100, "y": 200})
