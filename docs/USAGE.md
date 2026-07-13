# Usage Guide

## Dashboard

### Joining a Conference

1. Open `http://localhost:10886` in your browser
2. (Optional) Click **"Test Camera & Audio"** to verify devices
3. Select a room from the dropdown or enter a custom room name
4. Enter your name
5. Click **"Join Room"**

### During a Meeting

- **Video grid**: Click any participant to focus their video
- **Control bar**: Toggle mic, camera, screen share, or leave
- **Right sidebar**: Switch between tabs:
  - **Transcript**: Live captions with speaker identification
  - **Remote**: RustDesk remote control panel
  - **Fleet**: Agent fleet status
  - **Contacts**: Address book
  - **Intelligence**: Meeting summaries and action items
- **Topbar**: Room selector, connection status, help (?) button

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `?` | Open help modal |
| `Esc` | Close modal |
| `Enter` | Submit join form |

---

## Docker Usage

Build all images:

```powershell
docker compose -f docker-compose.yaml -f docker-compose.observability.yaml build
```

Start the full stack (8 containers):

```powershell
docker compose -f docker-compose.yaml -f docker-compose.observability.yaml up -d
```

Stop everything:

```powershell
docker compose -f docker-compose.yaml -f docker-compose.observability.yaml down
```

View logs:

```powershell
docker compose logs -f web agent livekit
```

### Observability

- **Grafana**: http://localhost:13000 (admin/admin) — pre-configured with Prometheus and Loki datasources
- **Prometheus**: http://localhost:19090 — metrics explorer
- **Loki**: http://localhost:13100 — log queries

### Individual Container Builds

```powershell
# Build single images
docker compose build agent       # AI voice agent
docker compose build web         # Next.js dashboard
docker compose -f docker-compose.observability.yaml build  # Observability images pull from Docker Hub

# Rebuild after code changes
docker compose build --no-cache agent
docker compose up -d --force-recreate agent
```

---
### Talking to Visio

1. Join a room with the agent present
2. Say **"Visio"** followed by your request
3. Wait for the agent's voice response

### Example Queries

| You Say | Visio Does |
|---------|------------|
| "Visio, what did we discuss last time?" | Queries LanceDB transcript history |
| "Visio, summarize this meeting" | Generates summary via LLM, persists to memory |
| "Visio, find Steve's email" | Searches contacts |
| "Visio, what's synergy mean?" | Analyzes discourse for jargon dilution |
| "Visio, help me fix this build error" | Requests remote assistance |

### Agent Status

The agent status panel shows:
- Connection state (green = connected)
- Current activity (listening, thinking, speaking)
- Last interaction timestamp

---

## Control Bar

During a meeting, the control bar offers:

| Button | Function |
|--------|----------|
| **Mic** | Toggle microphone on/off |
| **Camera** | Toggle camera on/off |
| **Share Screen** | Start/stop browser screen sharing via `getDisplayMedia` |
| **Leave** | Disconnect from the room |
| **Record** | Start/stop LiveKit Egress recording (red pulsing when active) |
| **Blur** | Toggle background blur on your camera feed (purple when active) |

---

## Device Testing

Navigate to `http://localhost:10886/test`:

1. **Camera**: See live preview, select from dropdown
2. **Microphone**: Speak to see level meter
3. **Speakers**: Click test button to play tone
4. Check status indicators (OK/Fail) before joining

---

## Settings

Navigate to Settings via the user dropdown menu or `http://localhost:10886/settings`.

### Connection
| Setting | Default | Description |
|---------|---------|-------------|
| LiveKit Server URL | `ws://localhost:15580` | WebSocket URL for LiveKit |
| Default Room Name | `ag-visio-conference` | Room auto-selected on join |

### Devices
| Setting | Description |
|---------|-------------|
| Microphone | Preferred audio input |
| Camera | Preferred video input |
| Speaker | Preferred audio output |

Click **"Detect Devices"** to enumerate available hardware.

### Appearance
| Theme | Description |
|-------|-------------|
| Dark | Dark mode (default) |
| Light | Light mode |
| System | Follows OS preference |

### Ollama (AI Agent)
- View installed models
- Check server status
- Pull new models directly from the UI
- Refresh model list

### Privacy
| Setting | Default | Description |
|---------|---------|-------------|
| Telemetry | Enabled | Sends anonymous usage data |

---

## Remote Desktop

### Via MCP Tools

The `remoting-mcp` server exposes direct input control:

```python
# From any MCP client (Claude, Cursor, etc.):
move_mouse(x=500, y=300)
click_mouse(button="left")
type_text(text="npm run build")
press_key(key_name="enter")
```

### Via Dashboard (RustDesk)

1. Open the **Remote** tab in the right sidebar
2. The RustDesk web client loads in an iframe
3. Enter the remote device's ID and password
4. Control the remote machine

### Via Screen Share

Use the `join_meeting` tool on `remoting-mcp` to publish your screen as a LiveKit video track:

```python
join_meeting(url="ws://localhost:15580", token="<token>")
# → "Joined room and publishing screen at 1920x1080."
```

Other participants see your screen as a video tile.

---

## Conference Scheduling

Scheduled conferences are managed via the `conferencing-mcp` server:

```python
# Schedule a meeting
conference_schedule(
    title="Sprint Review",
    scheduled_at="2026-05-10T14:00:00Z",
    organizer="sandra",
    duration_min=60
)

# List today's meetings
conference_upcoming(days=1)

# Invite participants
participant_invite(
    conference_id="<uuid>",
    identity="steve@bank-it.at",
    display_name="Steve"
)
```

---

## Log Viewer

1. Click the terminal icon in the topbar
2. View real-time logs with timestamps
3. Filter by level: INFO, WARNING, ERROR, SUCCESS
4. Toggle auto-scroll
5. Download logs as `.txt`
6. Clear history

Logs are also written to disk:
- `mcp_server.log` — conferencing MCP
- `agent_industrial.log` — AI agent

---

## Health Dashboard

Navigate to `http://localhost:10886/health` for a live system status overview:

- Overall health status (PASS/DEGRADED)
- LiveKit server reachability and active rooms
- Discovery service status
- Auto-refreshes every 10 seconds

---

## Running in Production

### Security Checklist

1. **Replace dev keys**: Generate production LiveKit API keys
2. **Enable WSS**: Configure TLS certificates for `wss://`
3. **HTTPS**: Set up reverse proxy (nginx/Caddy) for the web dashboard
4. **Firewall**: Restrict ports 10720, 10725, 10886 to internal network
5. **TURN**: Configure TURN server for remote participants behind NAT
6. **Monitoring**: Set up alerting on `/health` endpoint failures
7. **Backups**: Configure volume backups for `conference.db` and `lancedb_data`

### Docker Production

```yaml
# Override in docker-compose.override.yaml
environment:
  - LIVEKIT_API_KEY=${LIVEKIT_API_KEY}
  - LIVEKIT_API_SECRET=${LIVEKIT_API_SECRET}
```

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| CPU | 2 cores | 4 cores |
| Disk | 10 GB | 50 GB |
| Bandwidth | 1 Mbps/participant | 3 Mbps/participant |

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Can't join room | LiveKit not running | `docker compose up -d livekit` |
| No audio/video | Permissions denied | Allow camera/mic in browser, test at `/test` |
| Agent not responding | Ollama not running | Check `ollama serve`, verify model installed |
| MCP server unreachable | Port conflict | `just clean` then restart |
| Screen share black | GPU driver issue | Update graphics drivers |
| `uv run -m teleconference_mcp` fails | Dependencies missing | Run `uv sync` |
| Can't find contacts | Outlook not configured | Contacts are read from Windows Address Book |
| Tests failing | LanceDB version mismatch | Run `uv sync --reinstall` |
