set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File ../mcp-central-docs/scripts/just-dashboard.ps1 -Path .

# ── Teams++ Orchestration ───────────────────────────────────────────────────

# Launch the native remoting substrate
remoting:
    Set-Location '{{justfile_directory()}}/packages/remoting_mcp'
    .\start.ps1

# Launch the meeting intelligence server
conferencing:
    Set-Location '{{justfile_directory()}}/packages/conferencing_mcp'
    .\start.ps1

# Launch the Visio AI agent
agent:
    Set-Location '{{justfile_directory()}}/apps/agent'
    .\venv\Scripts\activate; \
    python agent.py dev

# Launch the Next.js dashboard (production)
web:
    Set-Location '{{justfile_directory()}}'
    npm run start --workspace=web

# Build the Next.js dashboard for production
build-web:
    Set-Location '{{justfile_directory()}}'
    npm run build --workspace=web

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting across monorepo
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check apps/ packages/

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check apps/ packages/ --fix --unsafe-fixes; \
    uv run ruff format apps/ packages/

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r apps/ packages/ -x **/node_modules/**,**/venv/**

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# ── Maintenance ───────────────────────────────────────────────────────────────

# Perform PWSH-native monorepo cleanup
clean:
    @Write-Host 'Cleaning monorepo caches and nodes...' -ForegroundColor Yellow; \
    Get-ChildItem -Path . -Filter '__pycache__' -Recurse | Remove-Item -Recurse -Force; \
    Get-ChildItem -Path . -Filter '.turbo' -Recurse | Remove-Item -Recurse -Force; \
    Write-Host 'Done.' -ForegroundColor Green

# Invoke the project setup substrate
setup:
    Set-Location '{{justfile_directory()}}'
    .\setup.ps1
