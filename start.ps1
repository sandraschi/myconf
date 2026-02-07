# AG-Visio One-Command Startup
# Starts LiveKit + Redis, then web app. Agent runs separately (requires Ollama).

param(
    [switch]$DockerOnly,
    [switch]$NoDocker
)

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot

Write-Host "AG-Visio Startup" -ForegroundColor Cyan
Write-Host ""

if (-not $NoDocker) {
    Write-Host "Starting Docker (LiveKit + Redis)..." -ForegroundColor Yellow
    Set-Location $repoRoot
    docker compose up -d
    if (-not $?) {
        Write-Host "Docker compose failed. Is Docker running?" -ForegroundColor Red
        exit 1
    }
    Write-Host "LiveKit: ws://localhost:15580" -ForegroundColor Green
    Write-Host "Redis: localhost:16379" -ForegroundColor Green
    Write-Host ""

    if ($DockerOnly) {
        Write-Host "Docker-only mode. Run agent: cd apps/agent; .\venv\Scripts\activate; python agent.py dev" -ForegroundColor Gray
        Write-Host "Run web: npm run dev --workspace=web" -ForegroundColor Gray
        exit 0
    }

    Write-Host "Waiting 3s for LiveKit to be ready..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

Write-Host "Starting web app on port 15500..." -ForegroundColor Yellow
Set-Location $repoRoot
Start-Process -FilePath "npm" -ArgumentList "run", "dev", "--workspace=web" -NoNewWindow -PassThru | Out-Null
Write-Host "Web: http://localhost:15500" -ForegroundColor Green
Write-Host "Health: http://localhost:15500/health" -ForegroundColor Gray
Write-Host ""
Write-Host "To run the AI agent (requires Ollama + gemma2):" -ForegroundColor Gray
Write-Host "  cd apps/agent" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "  python agent.py dev" -ForegroundColor Gray
Write-Host ""
