set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the Teams++ Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [Teams++] MyConf Operations Dashboard v2.0.0' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [Substrate State: Teams++ / UPGRADED]" -ForegroundColor DarkGray; \
    Write-Host ''

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

# Launch the Next.js dashboard
web:
    Set-Location '{{justfile_directory()}}'
    npm run dev --workspace=web

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
