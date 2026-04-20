Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# Sandra Schipal | SOTA 2026 | Webapp Startup Protocol
# Port: 10886 (myconf frontend)

$WebPort = 10886
Write-Host "Sandra: Cleansing port $WebPort of zombie processes..." -ForegroundColor Cyan

# Use npx kill-port for maximum reliability across environments
npx --yes kill-port $WebPort 2>$null

Write-Host "Sandra: Port $WebPort secured. Initializing Next.js development grid..." -ForegroundColor Green
npm run dev

