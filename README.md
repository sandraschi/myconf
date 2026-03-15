# myconf (AG-Visio)

**Professional video conferencing platform** with AI voice agent integration, built on Turborepo and LiveKit. Features real-time transcription, multi-room support, and comprehensive device testing.

## Stability & SOTA Alignment

As of February 2026, AG-Visio adheres to strict **SOTA (State-Of-The-Art) standards** for production-grade web applications:
- **Zero-Warning Policy:** The entire `apps/web` workspace is linted with `eslint --max-warnings 0`.
- **Type Hardening:** Replaced global `any` types with `unknown` and strict interfaces in telemetry and real-time data handlers.
- **Hook Optimization:** All React hooks are audited for dependency correctness and memoized via `useCallback` for performance stability.
- **Environmental Integrity:** Explicit environment variable declaration in `turbo.json` ensure predictable builds across dev/CI/prod.
- **Industrial Reliability:** Enhanced agent error prefixing (`SOTA-E03`, `SOTA-C01`) for clear substrate failure diagnostics.
- **Automated Health Monitoring:** Integrated substrate health check tool in the MCP server.

## Project Overview

AG-Visio is a modern, production-ready video conferencing solution combining:
- **LiveKit** real-time communication infrastructure
- **AI Voice Agent** ("Visio") with natural language understanding
- **Model Context Protocol** (MCP) server for system monitoring
- **Professional Web UI** with advanced controls and settings

### Architecture

- **apps/agent**: Python LiveKit voice agent ("Visio")
  - **VAD**: Silero Voice Activity Detection
  - **STT**: Whisper Speech-to-Text
  - **TTS**: Piper Text-to-Speech
  - **LLM**: Ollama integration (e.g., `gemma2`)
  - **Behavior**: Joins rooms, responds when addressed, detects jargon/LDDO patterns

- **apps/web**: Next.js 16 + React 19 application (port 15500)
  - LiveKit client integration
  - Professional topbar with auth, help, logger
  - Room selection and switching
  - Real-time transcription panel
  - Video/audio test page
  - Settings management with localStorage
  - Help modal with extensive documentation
  - Log viewer with filtering and export

- **apps/docs**: Next.js documentation site (port 15501)

- **packages/mcp-server**: Dual-language MCP server
  - **Python** (`mcp_server.py`): FastMCP, `get_dev_stats`, `query_system_logs`
  - **TypeScript** (`src/index.ts`): Windows-compatible disk monitoring
  - Run: `python packages/mcp-server/mcp_server.py` or `node packages/mcp-server/dist/index.js`

- **Infrastructure** (`docker-compose.yaml`):
  - LiveKit server (ports 15580–15582, 15581 for WebRTC)
  - Redis (port 16379)
  - Configuration: `livekit.yaml`

### Features

#### Web Application
- **Multi-room conferencing** with dropdown switcher
- **Remote Support Substrate**: Integrated orchestration of remote assistance tools.
- **Device testing** page (`/test`) with live preview and audio levels
- **Real-time transcription** sidebar with speaker identification
- **Settings page** with device selection, theme, telemetry controls
- **Help system** with keyboard shortcuts (`?` to open)
- **Log viewer** with filtering, export, and auto-scroll
- **User menu** with avatar, status, and logout
- **Premium UI**: 2026 SOTA design with Glassmorphism, dark theme, and micro-animations.

#### AI Agent
- Automatic room joining
- Context-aware responses
- Jargon and LDDO detection
- Natural conversation flow

#### MCP Tools (FastMCP 2.14.4 SOTA)
- **Substrate Health**: `get_system_health` for real-time LiveKit/Ollama monitoring.
- **Remote Orchestration**: `orchestrate_remote_support` for managing `rustdesk-mcp` substrates.
- **Git & Disk Stats**: `get_dev_stats` for industrial dev environment metrics.
- **System Log Query**: Windows Event Log introspection with SOTA filtering.
- **Iterative Sampling**: `sample_log_analysis` for AI-guided root cause analysis.
- **Context Awareness**: Full correlation tracing via injected `ctx`.
- **Inter-Agent Signaling**: `notify_conference_active` for grid-wide state propagation.

## Quick Start

### One-Time Setup

From repo root (PowerShell):

```powershell
.\setup.ps1
```

This script:
1. Installs root and app dependencies
2. Creates `apps/agent/venv` Python virtual environment
3. Installs agent dependencies from `requirements.txt`
4. Installs MCP package dependencies
5. **Ollama check:** if Ollama is not running and GPU has 6GB+ VRAM (nvidia-smi), offers to install Ollama (winget or open download page)

### Running the Stack

**Option A: Full Dockerization (recommended for one-command run)**

1. **Ollama runs outside Docker on your PC.** Start Ollama on the host (e.g. `ollama serve`), then pull the model: `ollama pull gemma2`. The agent container reaches it via `host.docker.internal:11434`.
2. From repo root:
   ```powershell
   docker compose up -d
   ```
3. Access:
   - Web UI: http://localhost:15500
   - Health: http://localhost:15500/health
   - Test page: http://localhost:15500/test
   - Settings: http://localhost:15500/settings

   The agent runs in a container and connects to LiveKit; it uses `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1` to reach Ollama running on your PC (outside Docker). On Linux, `extra_hosts` in compose provides `host.docker.internal`.

**Option B: Dev (web + agent locally)**

1. **Start Infrastructure**:
   ```powershell
   docker compose up -d
   ```

2. **Run LiveKit Agent** (requires Ollama with `gemma2`):
   ```powershell
   cd apps/agent
   .\venv\Scripts\activate
   python agent.py dev
   ```

3. **Run Web Client**:
   ```powershell
   npm run dev --workspace=web
   # Or: cd apps/web; npm run dev
   ```

4. **Access Application**:
   - Web UI: http://localhost:15500
   - Schedule: http://localhost:15500/schedule (create meetings, copy room link)
   - Video Test: http://localhost:15500/test
   - Settings: http://localhost:15500/settings

### Environment Configuration

Create `apps/web/.env.local`:

```env
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:15580
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```


## 🚀 Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

### 📦 Quick Start
Run immediately via `uvx`:
```bash
uvx myconf
```

### 🎯 Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "myconf": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/myconf", "run", "myconf"]
  }
}
```

## Usage

### Joining a Conference

1. Navigate to http://localhost:15500 (or http://YOUR_IP:15500 from another device)
2. (Optional) Test your camera/audio at http://localhost:15500/test
3. Select a room from the dropdown (discovered from LiveKit + defaults)
4. Enter your name
5. Click "Join Room"

**Discovery**: The server URL is auto-detected from your connection. When joining from another PC on the same network (e.g. http://192.168.1.100:15500), the LiveKit URL is inferred as ws://192.168.1.100:15580. No manual configuration needed.

### Switching Rooms

- When connected, use the room dropdown in the topbar
- Available rooms: `ag-visio-conference`, `development`, `testing`, `demo`
- Automatically disconnects from current room and reconnects

### Keyboard Shortcuts

- `?` - Open help modal
- `Esc` - Close modals

### Settings

Configure via Settings page (`/settings`):
- LiveKit server URL
- Default room name
- **Ollama (AI agent):** model discovery, list installed models, load (pull) a model; status and install link if Ollama is not running
- Audio/video device selection
- Theme preference (dark/light/system)
- Telemetry opt-out

### Viewing Logs

Click the Terminal icon in topbar to:
- View real-time logs with color-coded levels
- Filter by: all, info, warning, error, success
- Download logs as `.txt`
- Clear log history
- Toggle auto-scroll

### Roadmap

- **Phase 2.5 (ACTIVE): Full self-host calendaring & AI Operations**
  - **Refined MCP Server**: Fast_MCP 2.14.4 compliant with `ctx` injection
  - **Log Sampling**: Iterative log analysis for automated debugging
  - **Event store** (SQLite/Postgres or CalDAV e.g. Radicale/Baïkal)
  - **Scheduling UI**: create meetings, room link, optional QR
  - **Invitations**: email via self-hosted SMTP or Email MCP; copy-link fallback
  - **No external calendar dependency**; optional CalDAV sync for clients
  - **MCP tools**: list meetings, create meeting, send invite
- See [PRD.md](PRD.md) for full roadmap (Phase 2, 2.5, 3).

## Development

### Turborepo Commands

Build all apps and packages:
```powershell
turbo build
# Or: npx turbo build
```

Build specific package:
```powershell
turbo build --filter=web
```

Develop all apps:
```powershell
turbo dev
```

Develop specific app:
```powershell
turbo dev --filter=web
```

### Project Structure

```
myconf/
├── apps/
│   ├── agent/              # Python LiveKit voice agent
│   │   ├── agent.py        # Main agent entry point
│   │   ├── requirements.txt
│   │   └── venv/           # Python virtual environment
│   ├── web/                # Next.js web application
│   │   ├── app/            # App Router pages
│   │   │   ├── page.tsx    # Dashboard (conference room)
│   │   │   ├── test/       # Video/audio test page
│   │   │   └── settings/   # Settings page
│   │   ├── components/     # React components
│   │   │   ├── Topbar.tsx
│   │   │   ├── LogViewer.tsx
│   │   │   ├── HelpModal.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ui/         # Reusable UI components
│   │   ├── lib/            # Utilities and hooks
│   │   │   ├── settings.ts
│   │   │   ├── telemetry.ts
│   │   │   └── utils.ts
│   │   └── package.json
│   └── docs/               # Documentation site
├── packages/
│   ├── mcp-server/         # MCP server (Python + TypeScript)
│   ├── @repo/ui/           # Shared React components
│   ├── @repo/eslint-config/
│   └── @repo/typescript-config/
├── docker-compose.yaml     # LiveKit + Redis infrastructure
├── livekit.yaml           # LiveKit server configuration
├── setup.ps1              # One-time setup script
└── turbo.json             # Turborepo configuration
```

### Adding Dependencies

**Web app**:
```powershell
cd apps/web
npm install <package-name>
```

**Agent**:
```powershell
cd apps/agent
.\venv\Scripts\activate
pip install <package-name>
# Update requirements.txt
pip freeze > requirements.txt
```

### Testing

#### Web App (Vitest + Playwright)

**Unit and component tests** (Vitest + React Testing Library):
```powershell
cd apps/web
npm run test           # Run once
npm run test:watch     # Watch mode
npm run test:coverage  # With coverage report
```

**End-to-end tests** (Playwright):
```powershell
cd apps/web
npx playwright install  # One-time: install browsers
npm run test:e2e        # Run E2E (starts dev server if needed)
npm run test:e2e:ui     # Run with Playwright UI
```

From repo root:
```powershell
npm run test            # Runs web unit tests via Turbo
npm run test:e2e        # Runs web E2E tests
```

**Test layout**:
- `apps/web/__tests__/lib/` - Unit tests for `lib/utils`, `lib/settings`, `lib/telemetry`
- `apps/web/__tests__/components/` - Component tests (Modal, Toggle)
- `apps/web/e2e/` - Playwright E2E specs (smoke, join flow)

#### Python Agent (pytest)

Agent unit tests target `logic.py` (ReductionistLogic) only, so they run without LiveKit or Ollama:

```powershell
cd apps/agent
pip install -r requirements-dev.txt   # pytest only; optional if venv has deps
pytest
# Or: pytest -v
# Or: pytest tests/test_agent.py
```

From repo root:
```powershell
pytest apps/agent/tests -v
```

**Test layout**:
- `apps/agent/tests/` - Pytest tests
- `apps/agent/tests/test_agent.py` - ReductionistLogic saliency and jargon detection
- `apps/agent/tests/conftest.py` - Path setup and fixtures
- `apps/agent/logic.py` - ReductionistLogic (no LiveKit dependency; used by agent and tests)

#### Python Linting (Ruff)

```powershell
cd apps/agent
.\venv\Scripts\activate
pip install -r requirements-dev.txt
ruff check .
ruff format .
```

From repo root (with ruff in path):
```powershell
ruff check apps/agent packages/mcp-server
ruff format apps/agent packages/mcp-server
```

Config: `pyproject.toml` (line-length 100, target Python 3.10)

## Technology Stack

### Frontend
- **Next.js 16** (React 19, App Router)
- **TailwindCSS** for styling
- **LiveKit Components** (`@livekit/components-react`)
- **TypeScript** for type safety
- **Lucide React** for icons

### Backend / Agent
- **Python 3.11+**
- **livekit-agents** framework
- **Ollama** for LLM inference
- **Whisper** for speech-to-text
- **Piper** for text-to-speech
- **Silero** for voice activity detection

### Infrastructure
- **LiveKit** real-time communication server
- **Redis** for state management
- **Docker** & **Docker Compose**

### Development
- **Turborepo** for monorepo management
- **FastMCP** for MCP server (Python)
- **@modelcontextprotocol/sdk** (TypeScript)

## Troubleshooting

### Port Already in Use

If port 15500 is occupied:
```powershell
# Change port in apps/web/package.json
"dev": "next dev --port <NEW_PORT>"
```

### LiveKit Connection Issues

1. Ensure Docker containers are running:
   ```powershell
   docker compose ps
   ```

2. Check LiveKit server logs:
   ```powershell
   docker compose logs livekit
   ```

3. Verify `.env.local` configuration in `apps/web/`

### Agent Not Responding

1. Verify Ollama is running:
   ```powershell
   ollama list  # Check installed models
   ollama run gemma2  # Test model
   ```

2. Check agent logs in terminal

3. Ensure agent has joined room (check LiveKit server logs)

### Camera/Microphone Access Denied

- Grant browser permissions for camera/microphone
- Test at http://localhost:15500/test
- Check browser console for permission errors


## 🚀 Installation

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

### 📦 Quick Start
Run immediately via `uvx`:
```bash
uvx myconf
```

### 🎯 Claude Desktop Integration
Add to your `claude_desktop_config.json`:
```json
"mcpServers": {
  "myconf": {
    "command": "uv",
    "args": ["--directory", "D:/Dev/repos/myconf", "run", "myconf"]
  }
}
```

## Usage

### Running MCP Tools

**Python**:
```powershell
cd packages/mcp-server
python mcp_server.py
```

**TypeScript**:
```powershell
cd packages/mcp-server
npm run build
node dist/index.js
```

### Available Tools

- `get_dev_stats`: Git status, branch, commits, disk usage
- `query_system_logs`: Windows Event Log queries (limit parameter)

## Contributing

1. Follow existing code structure and naming conventions
2. Update documentation for new features
3. Test changes across all apps
4. Use TypeScript strict mode
5. Follow TailwindCSS utility-first patterns

## License

MIT

## Useful Links

### Turborepo
- [Tasks](https://turborepo.dev/docs/crafting-your-repository/running-tasks)
- [Caching](https://turborepo.dev/docs/crafting-your-repository/caching)
- [Filtering](https://turborepo.dev/docs/crafting-your-repository/running-tasks#using-filters)

### LiveKit
- [Documentation](https://docs.livekit.io/)
- [React Components](https://docs.livekit.io/reference/components/react/)
- [Server SDK](https://docs.livekit.io/server-sdk/)

### Model Context Protocol
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)

