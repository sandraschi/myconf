# AG-Visio Fleet Orchestrator | Sandra Schipal | SOTA 2026
# Unified Startup Substrate for Web UI and Voice Agent

$WebPort = 10886
$AgentPort = 10887

Write-Host "Sandra: Initializing Fleet Orchestration Protocol..." -ForegroundColor Cyan

# 1. Port Cleansing
Write-Host "Sandra: Cleansing substrate ports..." -ForegroundColor Yellow
npx --yes kill-port $WebPort, $AgentPort 2>$null

# 2. Dependency Health Checks
Write-Host "Sandra: Verifying dependency grid (Ollama/Redis)..." -ForegroundColor Yellow

# Check Ollama
try {
    Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -ErrorAction Stop > $null
    Write-Host "  [OK] Ollama Substrate Active" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Ollama not detected! Please start Ollama before proceeding." -ForegroundColor Red
    exit 1
}

# Check Redis (Standard port 6379)
if (Get-NetTCPConnection -LocalPort 6379 -ErrorAction SilentlyContinue) {
    Write-Host "  [OK] Redis Substrate Active" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Redis not detected on 6379. Multi-agent state sync may be degraded." -ForegroundColor DarkYellow
}

# 3. Launch Agent Substrate (Separate Window)
Write-Host "Sandra: Launching Voice Agent substrate..." -ForegroundColor Green
$agentCmd = "cmd /c 'cd apps\agent && python agent.py dev --http-port $AgentPort'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location apps\agent; .\start.ps1" -WindowStyle Normal

# 4. Launch Web UI (Current Window)
Write-Host "Sandra: Launching Web UI substrate..." -ForegroundColor Green
Set-Location apps\web
.\start.ps1

