"""Tests for diagnostics tools — heartbeat, dev_stats, remote_support, forensics."""

import pytest


@pytest.mark.asyncio
async def test_get_substrate_heartbeat_returns_structure(mock_ctx):
    """Heartbeat returns structured dict even when LiveKit is unreachable."""
    from conferencing_mcp.tools.diagnostics import get_substrate_heartbeat

    result = await get_substrate_heartbeat(mock_ctx)
    assert "heartbeat" in result
    assert "livekit" in result["heartbeat"]
    assert "ollama" in result["heartbeat"]
    assert "system" in result["heartbeat"]
    assert result["correlation_id"] == "TEST-CID-001"


@pytest.mark.asyncio
async def test_get_dev_stats_with_mocked_subprocess(mock_ctx, mock_subprocess):
    """get_dev_stats returns formatted report when subprocess mocked."""
    from conferencing_mcp.tools.diagnostics import get_dev_stats

    result = await get_dev_stats(mock_ctx)
    assert "GIT CONTEXT" in result
    assert "STORAGE VOLUMES" in result


@pytest.mark.asyncio
async def test_query_system_logs_with_mocked_subprocess(mock_ctx, mock_subprocess):
    """query_system_logs returns mock stdout with mocked PowerShell."""
    from conferencing_mcp.tools.diagnostics import query_system_logs

    result = await query_system_logs(mock_ctx, pattern="Error")
    assert "mock stdout" in result


@pytest.mark.asyncio
async def test_orchestrate_remote_support_status(mock_ctx, mock_subprocess):
    """Remote support status returns structured dict."""
    from conferencing_mcp.tools.diagnostics import orchestrate_remote_support

    result = await orchestrate_remote_support(mock_ctx, action="status")
    assert "success" in result
    assert "status" in result
    assert "health_snapshot" in result
    assert "correlation_id" in result


@pytest.mark.asyncio
async def test_orchestrate_industrial_diagnostics(mock_ctx, mock_subprocess):
    """Industrial diagnostics returns PASS/FAIL and critical logs."""
    from conferencing_mcp.tools.diagnostics import orchestrate_industrial_diagnostics

    result = await orchestrate_industrial_diagnostics(mock_ctx)
    assert result["status"] in ("PASS", "FAIL")
    assert "critical_logs" in result
    assert "correlation_id" in result


@pytest.mark.asyncio
async def test_sample_system_forensics_uses_ctx_sample(mock_ctx):
    """Forensics tool calls ctx.sample() and returns report."""
    from conferencing_mcp.tools.diagnostics import sample_system_forensics

    result = await sample_system_forensics(mock_ctx, anomaly="LiveKit down on port 15580")
    assert "FORENSIC_REPORT" in result
    mock_ctx.sample.assert_called_once()


@pytest.mark.asyncio
async def test_sample_log_analysis_iterates(mock_ctx, mock_subprocess):
    """sample_log_analysis collects N iterations with increasing sample sizes."""
    from conferencing_mcp.tools.diagnostics import sample_log_analysis

    result = await sample_log_analysis(mock_ctx, pattern="LiveKit", iterations=3)
    assert result["sampling_complete"] is True
    assert len(result["results"]) == 3
    assert result["results"][0]["sample_size"] == 5
    assert result["results"][1]["sample_size"] == 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action,expected_contains",
    [
        ("status", "NOT_INSTALLED"),
        ("unknown_action", "Unknown action"),
    ],
)
async def test_orchestrate_remote_support_parametrized(action, expected_contains, mock_ctx, mock_subprocess):
    """Remote support handles status/unknown actions correctly."""
    from conferencing_mcp.tools.diagnostics import orchestrate_remote_support

    result = await orchestrate_remote_support(mock_ctx, action=action)
    assert expected_contains in str(result)
