# setup.ps1 - Project AG-Visio Monorepo Setup

Write-Host ">>> Initializing Project AG-Visio Setup..." -ForegroundColor Cyan

# 1. Global / Root Dependencies
Write-Host "`n>>> Installing Root Dependencies..." -ForegroundColor Green
npm install

# 2. Web Client Dependencies
Write-Host "`n>>> Setting up Web Client (/apps/web)..." -ForegroundColor Green
Set-Location apps/web
npm install livekit-client @livekit/components-react @livekit/components-styles
Set-Location ../..

# 3. AI Agent Dependencies (Python)
Write-Host "`n>>> Setting up AI Agent (/apps/agent)..." -ForegroundColor Green
if (!(Test-Path "apps/agent/venv")) {
    python -m venv apps/agent/venv
}
& apps/agent/venv/Scripts/pip install -r apps/agent/requirements.txt

# 4. MCP Server Dependencies
Write-Host "`n>>> Setting up MCP Server (/packages/mcp-server)..." -ForegroundColor Green
Set-Location packages/mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
Set-Location ../..

# 5. Ollama check: if not running and GPU strong enough, offer install
Write-Host "`n>>> Checking Ollama (AI agent LLM)..." -ForegroundColor Green
$ollamaOk = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    if ($r.StatusCode -eq 200) { $ollamaOk = $true }
} catch {
    # Ollama not reachable
}

if ($ollamaOk) {
    Write-Host "Ollama is running." -ForegroundColor Green
} else {
    $gpuStrongEnough = $false
    try {
        $nvidiaOut = & nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null
        if ($nvidiaOut) {
            $memMb = [int](($nvidiaOut -replace ' MiB','').Trim())
            if ($memMb -ge 6144) { $gpuStrongEnough = $true }
        }
    } catch {
        # nvidia-smi not found or failed
    }
    if ($gpuStrongEnough) {
        Write-Host "Ollama not detected. Your GPU has 6GB+ VRAM and may run Ollama well." -ForegroundColor Yellow
        $install = Read-Host "Install Ollama? (y/n)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            $winget = Get-Command winget -ErrorAction SilentlyContinue
            if ($winget) {
                Write-Host "Installing Ollama via winget..." -ForegroundColor Cyan
                winget install Ollama.Ollama --accept-package-agreements
            } else {
                Write-Host "Opening Ollama download page (install manually)." -ForegroundColor Cyan
                Start-Process "https://ollama.com/download"
            }
        }
    } else {
        Write-Host "Ollama not detected. Start it on your PC (ollama serve) or install from https://ollama.com/download" -ForegroundColor Gray
    }
}

Write-Host "`n>>> Setup Complete. 'Mode Cons' ready for deployment." -ForegroundColor Cyan
