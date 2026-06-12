Param([switch]$Headless, [switch]$Rebuild)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Sandra Schipal | SOTA 2026 | Webapp Startup Protocol (Production)
# Port: 10886 (myconf frontend)

$WebPort = 10886
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath

Write-Host "Clearing port $WebPort..." -ForegroundColor Cyan
npx --yes kill-port $WebPort 2>$null

# Build once, serve pre-compiled
$buildId = ".next\BUILD_ID"
if ($Rebuild -or -not (Test-Path $buildId)) {
    Write-Host "Building frontend for production..." -ForegroundColor Cyan
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed! Falling back to dev mode." -ForegroundColor Red
        npm run dev
        exit
    }
}
Write-Host "Starting frontend on port $WebPort..." -ForegroundColor Green
npm run start
