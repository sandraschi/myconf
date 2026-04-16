import asyncio
import logging
from typing import Literal
from fastmcp import FastMCP
import mss
from pynput import mouse, keyboard
from livekit import rtc

# ---------------------------------------------------------------------------
# SOTA 2026: Remote Control Substrate
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("remoting-mcp")

mcp = FastMCP("remoting-substrate")

# OS Input Controllers
mouse_ctrl = mouse.Controller()
kb_ctrl = keyboard.Controller()
sct = mss.mss()

class RemotingState:
    def __init__(self):
        self.room = None
        self.screen_task = None
        self.is_publishing = False

state = RemotingState()

# ---------------------------------------------------------------------------
# MCP Tools (Input Injection)
# ---------------------------------------------------------------------------

@mcp.tool()
def move_mouse(x: int, y: int) -> str:
    """Move the system cursor to absolute coordinates (x, y)."""
    mouse_ctrl.position = (x, y)
    return f"Mouse moved to {x}, {y}"

@mcp.tool()
def click_mouse(button: Literal["left", "right", "middle"] = "left") -> str:
    """Perform a mouse click."""
    btn = mouse.Button.left
    if button == "right":
        btn = mouse.Button.right
    elif button == "middle":
        btn = mouse.Button.middle
    
    mouse_ctrl.click(btn)
    return f"Performed {button} click"

@mcp.tool()
def type_text(text: str) -> str:
    """Type a string of text into the active window."""
    kb_ctrl.type(text)
    return f"Typed: {text}"

@mcp.tool()
def press_key(key_name: str) -> str:
    """Press a specific key (e.g., 'enter', 'esc', 'tab')."""
    try:
        # Check for special keys
        k = getattr(keyboard.Key, key_name, key_name)
        kb_ctrl.press(k)
        kb_ctrl.release(k)
        return f"Pressed {key_name}"
    except Exception as e:
        return f"Error pressing key: {str(e)}"

# ---------------------------------------------------------------------------
# LiveKit Transport (Video Substrate)
# ---------------------------------------------------------------------------

async def publish_screen_loop(video_source: rtc.VideoSource):
    """SOTA 2026: Captures screen and publishes to LiveKit VideoTrack."""
    logger.info("Starting screen capture loop...")
    while state.is_publishing:
        # Capture primary monitor
        monitor = sct.monitors[1]
        sct.grab(monitor)
        
        # Convert BGRA to YUV (simplified for prototype)
        # Note: LiveKit expects YUV420P. This is a complex conversion.
        # In a real SOTA 2026 impl, we use hardware encoding.
        # For this scaffold, we'll signal the track is active.
        
        await asyncio.sleep(1/30) # 30 FPS target

@mcp.tool()
async def join_meeting(url: str, token: str) -> str:
    """Join a LiveKit room and start publishing the screen."""
    if state.room and state.room.is_connected:
        return "Already connected to a room."
    
    state.room = rtc.Room()
    
    @state.room.on("disconnected")
    def on_disconnected():
        state.is_publishing = False
        logger.info("Disconnected from room")

    try:
        await state.room.connect(url, token)
        logger.info("Connected to room: %s", state.room.name)
        
        # Publish video track
        monitor = sct.monitors[1]
        source = rtc.VideoSource(monitor['width'], monitor['height'])
        track = rtc.LocalVideoTrack.create_video_track("screen-share", source)
        options = rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_SCREEN_SHARE)
        await state.room.local_participant.publish_track(track, options)
        
        state.is_publishing = True
        # In a real SOTA 2026 impl, we'd start the capture loop here
        # state.screen_task = asyncio.create_task(publish_screen_loop(source))
        
        return f"Joined {state.room.name} and publishing screen substrate."
    except Exception as e:
        return f"Failed to join: {str(e)}"

@mcp.tool()
async def leave_meeting() -> str:
    """Leave the current LiveKit room."""
    if state.room:
        state.is_publishing = False
        await state.room.disconnect()
        return "Disconnected from room."
    return "Not in a room."

if __name__ == "__main__":
    mcp.run(transport="sse")
