"""
packages/remoting_mcp/mcp_server.py — Remote Control Substrate
Screen capture, mouse/keyboard injection, and LiveKit screen publishing.
"""

import asyncio
import logging
import os
from typing import Literal

import mss
import numpy as np
from fastmcp import Context, FastMCP
from fastmcp.server import create_proxy
from livekit import rtc
from pynput import keyboard, mouse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remoting-mcp")

mcp = FastMCP("remoting-substrate")

# MCP Bridge: ProxyProvider for multi-server federation
_bridge_urls = os.getenv("MCP_BRIDGE_URLS", "")
if _bridge_urls:
    for _url in _bridge_urls.split(","):
        _url = _url.strip()
        if _url:
            try:
                mcp.add_provider(create_proxy(_url))
                logger.info("MCP bridge registered: %s", _url)
            except Exception as e:
                logger.warning("MCP bridge failed for %s: %s", _url, e)

mouse_ctrl = mouse.Controller()
kb_ctrl = keyboard.Controller()
sct = mss.mss()


class RemotingState:
    def __init__(self):
        self.room = None
        self.screen_task = None
        self.is_publishing = False
        self._source = None
        self._video_track = None


state = RemotingState()


def _bgra_to_i420(bgra_frame: np.ndarray) -> bytes:
    """Convert a BGRA numpy frame to I420 (YUV420P) for LiveKit."""
    height, width = bgra_frame.shape[:2]
    bgra = bgra_frame[:, :, :3]
    b, g, r = bgra[:, :, 0], bgra[:, :, 1], bgra[:, :, 2]
    y = (0.299 * r + 0.587 * g + 0.114 * b).clip(0, 255).astype(np.uint8).tobytes()
    u = np.zeros((height // 2, width // 2), dtype=np.uint8).tobytes()
    v = np.zeros((height // 2, width // 2), dtype=np.uint8).tobytes()
    return y + u + v


# ---------------------------------------------------------------------------
# MCP Tools — Input Injection
# ---------------------------------------------------------------------------


@mcp.tool()
def move_mouse(ctx: Context, x: int, y: int) -> str:
    """Move the system cursor to absolute coordinates (x, y)."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    mouse_ctrl.position = (x, y)
    logger.info("Mouse moved to %d, %d", x, y, extra={"correlation_id": cor_id})
    return f"Mouse moved to {x}, {y}"


@mcp.tool()
def click_mouse(ctx: Context, button: Literal["left", "right", "middle"] = "left") -> str:
    """Perform a mouse click."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    btn = mouse.Button.left
    if button == "right":
        btn = mouse.Button.right
    elif button == "middle":
        btn = mouse.Button.middle
    mouse_ctrl.click(btn)
    logger.info("%s click performed", button, extra={"correlation_id": cor_id})
    return f"Performed {button} click"


@mcp.tool()
def type_text(ctx: Context, text: str) -> str:
    """Type a string of text into the active window."""
    kb_ctrl.type(text)
    return f"Typed: {text}"


@mcp.tool()
def press_key(ctx: Context, key_name: str) -> str:
    """Press a specific key (e.g., 'enter', 'esc', 'tab')."""
    try:
        k = getattr(keyboard.Key, key_name, key_name)
        kb_ctrl.press(k)
        kb_ctrl.release(k)
        return f"Pressed {key_name}"
    except Exception as e:
        return f"Error pressing key: {e!s}"


@mcp.tool()
def screen_resolution(ctx: Context) -> str:
    """Return the current primary monitor resolution."""
    monitor = sct.monitors[1]
    return f"{monitor['width']}x{monitor['height']}"


# ---------------------------------------------------------------------------
# LiveKit Transport — Screen Publishing
# ---------------------------------------------------------------------------


async def publish_screen_loop(video_source: rtc.VideoSource):
    """Captures screen frames and publishes them to the LiveKit VideoTrack."""
    logger.info("Starting screen capture loop at 15 FPS...")
    monitor_idx = 1
    frame_interval = 1.0 / 15.0

    while state.is_publishing:
        loop_start = asyncio.get_event_loop().time()

        try:
            monitor = sct.monitors[monitor_idx]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)

            i420_data = _bgra_to_i420(img)
            frame = rtc.VideoFrame(
                width=monitor["width"],
                height=monitor["height"],
                type=rtc.VideoBufferType.I420,
                data=i420_data,
            )
            video_source.capture_frame(frame)
        except Exception as e:
            logger.error(f"Screen capture frame error: {e}")

        elapsed = asyncio.get_event_loop().time() - loop_start
        sleep_time = max(0, frame_interval - elapsed)
        await asyncio.sleep(sleep_time)


@mcp.tool()
async def join_meeting(ctx: Context, url: str, token: str) -> str:
    """Join a LiveKit room and start publishing the screen as a video track."""
    if state.room and state.room.is_connected:
        return "Already connected to a room."

    state.room = rtc.Room()

    @state.room.on("disconnected")
    def on_disconnected():
        state.is_publishing = False

    try:
        await state.room.connect(url, token)

        monitor = sct.monitors[1]
        video_source = rtc.VideoSource(monitor["width"], monitor["height"])
        video_track = rtc.LocalVideoTrack.create_video_track("screen-share", video_source)
        options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_SCREEN_SHARE)
        await state.room.local_participant.publish_track(video_track, options)

        state._source = video_source
        state._video_track = video_track
        state.is_publishing = True
        state.screen_task = asyncio.create_task(publish_screen_loop(video_source))

        return f"Joined {state.room.name} and publishing screen at {monitor['width']}x{monitor['height']}."
    except Exception as e:
        state.is_publishing = False
        return f"Failed to join: {e!s}"


@mcp.tool()
async def leave_meeting(ctx: Context) -> str:
    """Leave the current LiveKit room and stop screen publishing."""
    if state.screen_task:
        state.is_publishing = False
        state.screen_task.cancel()
        state.screen_task = None
    if state.room:
        await state.room.disconnect()
        state.room = None
        return "Disconnected from room."
    return "Not in a room."


@mcp.tool()
def get_status(ctx: Context) -> dict:
    """Return the current remoting substrate status."""
    cor_id = getattr(ctx, "correlation_id", "GLOBAL")
    return {
        "connected": state.room is not None and state.room.is_connected,
        "publishing": state.is_publishing,
        "room_name": state.room.name if state.room else None,
        "correlation_id": cor_id,
    }


if __name__ == "__main__":
    mcp.run(transport="sse")
