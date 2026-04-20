Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Sandra Schipal | SOTA 2026 | Agent Startup Protocol
# Port: 10887 (myconf backend)

$WebPort = 10887
Write-Host "Sandra: Cleansing port $WebPort of zombie processes..." -ForegroundColor Cyan

# Clear port for potential supervisor/health-check binding
npx --yes kill-port $WebPort 2>$null

Write-Host "Sandra: Port $WebPort secured. Initializing AG-Visio Voice Agent..." -ForegroundColor Green

# Ensure virtual environment is active if present
if (Test-Path "venv\Scripts\Activate.ps1") {
    . venv\Scripts\Activate.ps1
}

# Run the agent with dev mode and explicit port
python agent.py dev --http-port $WebPort

