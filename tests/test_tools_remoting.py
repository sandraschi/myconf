"""Tests for remoting tools — input injection + LiveKit meeting transport."""

import pytest


@pytest.mark.asyncio
async def test_move_mouse(mock_ctx):
    """move_mouse returns confirmation string with coordinates."""
    from packages.remoting_mcp.mcp_server import move_mouse

    result = move_mouse(mock_ctx, x=500, y=300)
    assert "Mouse moved to 500, 300" == result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "button,expected",
    [
        ("left", "left click"),
        ("right", "right click"),
        ("middle", "middle click"),
    ],
)
async def test_click_mouse_parametrized(button, expected, mock_ctx):
    """click_mouse returns confirmation for all button types."""
    from packages.remoting_mcp.mcp_server import click_mouse

    result = click_mouse(mock_ctx, button=button)
    assert expected in result


@pytest.mark.asyncio
async def test_type_text(mock_ctx):
    """type_text returns the typed string."""
    from packages.remoting_mcp.mcp_server import type_text

    result = type_text(mock_ctx, text="Hello")
    assert "Typed: Hello" == result


@pytest.mark.asyncio
async def test_press_key_enter(mock_ctx):
    """press_key with 'enter' returns success."""
    from packages.remoting_mcp.mcp_server import press_key

    result = press_key(mock_ctx, key_name="enter")
    assert "Pressed enter" == result


@pytest.mark.asyncio
async def test_press_key_invalid_returns_error(mock_ctx):
    """press_key with non-existent key returns error string."""
    from packages.remoting_mcp.mcp_server import press_key

    result = press_key(mock_ctx, key_name="nonexistent_key_xyz")
    assert "Error" in result


@pytest.mark.asyncio
async def test_screen_resolution(mock_ctx):
    """screen_resolution returns a resolution string."""
    from packages.remoting_mcp.mcp_server import screen_resolution

    result = screen_resolution(mock_ctx)
    assert "x" in result


@pytest.mark.asyncio
async def test_get_status(mock_ctx):
    """get_status returns structured state dict with correlation_id."""
    from packages.remoting_mcp.mcp_server import get_status

    result = get_status(mock_ctx)
    assert "connected" in result
    assert "publishing" in result
    assert "room_name" in result
    assert result["correlation_id"] == "TEST-CID-001"
