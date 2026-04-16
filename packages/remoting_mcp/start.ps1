# SOTA 2026: remoting-mcp startup
# Standardized port: 10725
# ---------------------------------------------------------------------------

$PORT = 10725
$HOST = "0.0.0.0"

# 1. Kill existing squatters
$zombies = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($z in $zombies) {
    if ($z) {
        Write-Host "Culling zombie process: $z" -ForegroundColor Yellow
        Stop-Process -Id $z -Force
    }
}

# 2. Virtual Environment Check
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    ./.venv/Scripts/python -m pip install -r requirements.txt
}

# 3. Start FastMCP on port 10725 (SSE)
Write-Host "Targeting Port Substrate 10725..." -ForegroundColor Cyan
./.venv/Scripts/python mcp_server.py
