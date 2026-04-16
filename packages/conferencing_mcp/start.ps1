# start.ps1 — SOTA 2026 Startup Script
# Industrial-grade process management for conferencing-mcp

$PORT = 10720
$NAME = "conferencing-mcp"

Write-Host "[INIT] Starting $NAME on port $PORT..." -ForegroundColor Cyan

# 1. Clear port squatters
$process = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
if ($process) {
    Write-Host "[CLEANUP] Killing process $process squatting on port $PORT" -ForegroundColor Yellow
    Stop-Process -Id $process -Force
}

# 2. Start MCP server (SSE transport)
Write-Host "[EXEC] Launching FastMCP server..." -ForegroundColor Green
# We use -u for unbuffered output to ensure logs capture in real-time
python -u mcp_server.py sse --port $PORT
