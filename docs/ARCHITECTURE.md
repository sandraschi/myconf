# Architecture

## Overview

AG-Visio is a **service-oriented monorepo** combining WebRTC (LiveKit), local-first AI (Ollama), MCP-based tool orchestration, Windows-native remoting, and full observability. All services run as Docker containers or local processes.

## Docker Stack (8 containers)

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| livekit | Custom build | 15580–15582 | WebRTC SFU |
| redis | redis:7-alpine | 16379 | State bus + pub/sub |
| web | Custom Next.js build | 15500 | Dashboard |
| agent | Custom Python build | — | Visio AI agent |
| prometheus | prom/prometheus | 19090 | Metrics collection |
| loki | grafana/loki | 13100 | Log aggregation |
| grafana | grafana/grafana | 13000 | Dashboards |
| promtail | grafana/promtail | — | Log shipping |

---

## Service Map

```
┌───────────── Browser (port 10886) ─────────────┐
│  Next.js 16 · React 19 · TailwindCSS 4          │
│  @livekit/components-react · Lucide Icons       │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ LiveKit  │ │ Meeting  │ │ Device Test    │   │
│  │ Room UI  │ │ Intel    │ │ / Settings     │   │
│  └────┬─────┘ └────┬─────┘ └────────────────┘   │
└───────┼─────────────┼────────────────────────────┘
        │ WebSocket   │ HTTP REST / MCP SSE
        ▼             ▼
┌──────────────────────────────────────────────────┐
│          LiveKit Server (port 15580)              │
│  WebRTC SFU · Room Management · Token Auth       │
│  Redis for state + pub/sub                       │
└────┬────────────────────┬────────────────────────┘
     │ WebRTC tracks     │ Data channel
     ▼                    ▼
┌──────────────────────────────────────────────────┐
│          Visio AI Agent (port 10887)              │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Ollama   │  │ Whisper  │  │ Piper TTS      │  │
│  │ LLM      │  │ STT      │  │                │  │
│  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Silero   │  │ LanceDB  │  │ FastEmbed      │  │
│  │ VAD      │  │ RAG      │  │ (384-dim vec)  │  │
│  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Contacts │  │ StateBus │  │ Vision OCR     │  │
│  │ Manager  │  │ (Redis)  │  │ (UIAutomation) │  │
│  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────────────────────────────────────────┐ │
│  │ Dynamic MCP Discovery (scans 10700-10800)    │ │
│  │ Discovers + delegates to remote MCP servers  │ │
│  └──────────────────────────────────────────────┘ │
└──────┬───────────────────────────────────────────┘
       │ SSE
       ▼
┌──────────────────────┐  ┌──────────────────────┐
│ conferencing-mcp     │  │ remoting-mcp          │
│ (port 10720)         │  │ (port 10725)          │
│                      │  │                       │
│ FastMCP 3.2+ server  │  │ FastMCP 3.2+ server   │
│                      │  │                       │
│ Tools:               │  │ Tools:                │
│ • generate_meeting_  │  │ • move_mouse(x, y)    │
│   summary            │  │ • click_mouse(btn)    │
│ • extract_action_    │  │ • type_text(text)     │
│   items              │  │ • press_key(key)      │
│ • conference_schedule│  │ • join_meeting(url,   │
│ • conference_list    │  │   token)              │
│ • room_create        │  │ • leave_meeting()     │
│ • room_list          │  │ • get_status()        │
│ • room_delete        │  │ • screen_resolution() │
│ • participant_invite │  │                       │
│ • participant_list   │  │ LiveKit integration:  │
│ • get_dev_stats      │  │ Captures screen via   │
│ • get_substrate_     │  │ mss, converts BGRA→   │
│   heartbeat          │  │ I420, publishes as    │
│ • list_active_       │  │ LiveKit video track   │
│   conferences        │  │ at 15 FPS             │
│ • orchestrate_remote_│  │                       │
│   support            │  │                       │
│                      │  │                       │
│ Data: SQLite         │  │ State: In-memory      │
│ (conference.db)      │  │                       │
└──────────────────────┘  └──────────────────────┘
```

---

## Communication Protocols

| Between | Protocol | Format |
|---------|----------|--------|
| Browser ↔ LiveKit | WebSocket | WebRTC (SDP/ICE) |
| Browser ↔ MCP servers | SSE + HTTP | JSON-RPC via MCP |
| Browser ↔ Agent | LiveKit data channel | JSON messages |
| Agent ↔ MCP servers | SSE + HTTP | MCP client SDK |
| Agent ↔ Ollama | HTTP | Ollama REST API |
| Agent ↔ Redis | TCP | Redis protocol |
| Agent ↔ LiveKit | WebSocket | livekit-agents SDK |

---

## MCP Tool Discovery

The agent scans ports 10700–10800 at startup for SSE MCP endpoints:

```
agent.py → HTTP GET http://localhost:{port}/mcp → if 200 → sse_client() → ClientSession → list_tools()
```

Discovered tools are registered dynamically in `CombinedMCPFunctionContext` and exposed to the LLM via `@llm.ai_callable`. The agent can delegate to any discovered server using `delegate_to_mcp(server_hint, tool_name, arguments)`.

---

## Data Flow: Meeting Intelligence

```
1. User: "Visio, summarize this meeting"
2. Visio agent → delegates to conferencing-mcp / generate_meeting_summary
3. conferencing-mcp → ctx.sample() → LLM generates summary
4. conferencing-mcp → LanceDB → persists vector embedding
5. conferencing-mcp → returns summary to agent
6. Agent → LiveKit data channel → MeetingIntelligencePanel in browser
```

---

## Data Flow: Remote Screen Publishing

```
1. remoting-mcp / join_meeting() → connects to LiveKit room
2. Launches publish_screen_loop() at 15 FPS:
   a. mss.grab() → numpy array (BGRA)
   b. _bgra_to_i420() → YUV420P bytes
   c. rtc.VideoFrame → video_source.capture_frame()
3. Browser receives remote screen as a LiveKit video track
```

---

## Directory Layout

```
myconf/
├── myconf/                         # Python package (entry point)
│   ├── __init__.py
│   ├── __main__.py                 # uv run -m myconf [service]
│   └── health.py                   # Shared health check utilities
├── apps/
│   ├── agent/                      # Visio AI voice agent
│   │   ├── agent.py                # LiveKit VoicePipelineAgent
│   │   ├── logic.py                # Reductionist logic / jargon analysis
│   │   ├── memory_substrate.py     # LanceDB RAG engine
│   │   ├── contacts_substrate.py   # Multi-provider contact manager
│   │   ├── vision_analyze.py       # OCR / screen perception
│   │   ├── state_bus.py            # Redis inter-agent coordination
│   │   └── tests/
│   └── web/                        # Next.js dashboard (port 10886)
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── __tests__/
├── packages/
│   ├── conferencing_mcp/           # MCP server (port 10720)
│   │   ├── mcp_server.py           # FastMCP 3.2+ server
│   │   ├── conference.py           # SQLite + LiveKit API
│   │   └── health_server.py        # HTTP health endpoint
│   ├── remoting_mcp/               # MCP server (port 10725)
│   │   └── mcp_server.py           # Screen capture + input injection
│   └── ui/                         # Shared React components
├── tests/                          # Monorepo-wide Python tests
├── docker-compose.yaml             # Full stack: livekit + redis + web + agent
├── justfile                        # Command runner
└── pyproject.toml                  # Python project config
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Local-first AI** | All AI runs locally via Ollama — zero cloud dependency, full privacy |
| **MCP as glue** | All services communicate via Model Context Protocol (SSE endpoints) |
| **LanceDB for RAG** | Embedded vector DB — no external service needed, persists to disk |
| **Windows-native remoting** | Uses `SendInput` API (pynput) and `mss` for screen capture |
| **Turborepo monorepo** | Shared configs (TypeScript, ESLint), coordinated builds, test caching |
| **SOTA compliance** | Ruff linting, MyPy, Bandit, Safety checks in CI |
