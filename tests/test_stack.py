"""
Integration tests for the AG-Visio stack.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "agent"))

import pytest


@pytest.mark.asyncio
async def test_conferencing_mcp_tools():
    from packages.conferencing_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    required = [
        "get_dev_stats",
        "get_substrate_heartbeat",
        "generate_meeting_summary",
        "extract_action_items",
        "conference_schedule",
        "conference_list",
        "room_create",
        "room_list",
        "room_delete",
        "participant_invite",
        "participant_list_invited",
        "orchestrate_remote_support",
        "list_active_conferences",
    ]
    for tool in required:
        assert tool in tool_names, f"Missing conferencing tool: {tool}"


@pytest.mark.asyncio
async def test_remoting_mcp_tools():
    from packages.remoting_mcp.mcp_server import mcp

    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]

    required = [
        "move_mouse",
        "click_mouse",
        "type_text",
        "press_key",
        "join_meeting",
        "leave_meeting",
        "get_status",
        "screen_resolution",
    ]
    for tool in required:
        assert tool in tool_names, f"Missing remoting tool: {tool}"


@pytest.mark.asyncio
async def test_conferencing_mcp_health():
    from packages.conferencing_mcp.health_server import MetricsHandler

    assert MetricsHandler is not None


@pytest.mark.asyncio
async def test_myconf_health_module():
    from myconf.health import check_tcp_port, health_response

    result = check_tcp_port("127.0.0.1", 65535, timeout=0.1)
    assert result["status"] in ("DEAD", "ERROR")

    resp = health_response("test", {"dummy": {"status": "ALIVE"}})
    assert resp["status"] == "PASS"
    assert resp["service"] == "test"


@pytest.mark.asyncio
async def test_contact_manager_init():
    from apps.agent.contacts_substrate import ContactManager

    mgr = ContactManager(cache_path="test_contacts_cache.json")
    assert mgr is not None
    assert len(mgr.search("test")) == 0

    import os

    if os.path.exists("test_contacts_cache.json"):
        os.remove("test_contacts_cache.json")


@pytest.mark.asyncio
async def test_memory_substrate_init(tmp_path):
    from apps.agent.memory_substrate import MemorySubstrate

    ms = MemorySubstrate(db_path=str(tmp_path / "lancedb_test"))
    tables = ms.db.list_tables()
    table_names = tables.tables if hasattr(tables, "tables") else tables
    assert "transcripts" in table_names
    assert "codebase" in table_names
    assert "mission_logs" in table_names


@pytest.mark.asyncio
async def test_state_bus_lifecycle():
    from apps.agent.state_bus import StateBus

    bus = StateBus()
    assert not bus.is_connected
    await bus.connect()
    await bus.disconnect()
    assert not bus.is_connected


def test_reductionist_logic():
    from apps.agent.logic import ReductionistLogic

    logic = ReductionistLogic()
    assert logic.analyze_saliency("normal technical discussion") == 0.0
    logic.enable_jargon_detection(True)
    assert logic.analyze_saliency("we need more synergy and holistic alignment") > 0.0
    assert logic.analyze_saliency("") == 0.0


def test_vision_substrate_init():
    from apps.agent.vision_analyze import VisionSubstrate

    vs = VisionSubstrate(mode="local")
    assert vs is not None


def test_reductionist_logic_default_disabled():
    """Jargon detection should be off by default."""
    from apps.agent.logic import ReductionistLogic

    logic = ReductionistLogic()
    assert not logic._jargon_detection_enabled
    assert logic.analyze_saliency("synergy") == 0.0
