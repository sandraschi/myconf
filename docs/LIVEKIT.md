# LiveKit Configuration

## Overview

[LiveKit](https://livekit.io) is the WebRTC infrastructure powering all real-time audio/video communication. It runs as a Docker container and provides:

- **SFU** (Selective Forwarding Unit) for multi-participant video
- **Room management** via REST API
- **Token-based authentication**
- **Data channels** for transcription and agent messages

---

## Server Configuration

### `livekit.yaml`

```yaml
port: 15580
rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: false
keys:
  devkey: secret
logging:
  level: info
```

| Setting | Default | Notes |
|---------|---------|-------|
| `port` | 15580 | WebSocket port for client connections |
| `rtc.port_range_start` | 50000 | First UDP port for WebRTC media |
| `rtc.port_range_end` | 60000 | Last UDP port for WebRTC media |
| `rtc.stun_servers` | Google STUN | Public STUN for NAT traversal |
| `rtc.turn.enabled` | false | Enable for production behind NAT |
| `keys` | devkey/secret | Replace with production secrets |
| `logging.level` | info | Set to `debug` for troubleshooting |

### Starting LiveKit

```powershell
docker compose up -d livekit
```

Or build from source:

```powershell
docker build -t livekit-server -f livekit.Dockerfile .
docker run -p 15580:15580 -p 15581:15581 -p 15582:15582/udp livekit-server
```

---

## Room Management

LiveKit rooms are managed via the **conferencing-mcp** server, which wraps the `livekit-api` Python SDK.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `room_create` | Create a new room with configurable max participants and empty timeout |
| `room_list` | List all active rooms, optionally filtered by name |
| `room_delete` | Delete a room (kicks all participants) |
| `room_update_metadata` | Update metadata string on a room |
| `room_participant_list` | List live participants in a room |
| `room_participant_kick` | Remove a participant from a room |
| `room_participant_mute` | Mute/unmute a participant's track |
| `room_send_data` | Send data message to room participants |

### Environment Variables

```
LIVEKIT_URL=ws://localhost:15580
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
```

These must match the keys in `livekit.yaml`.

---

## Token Authentication

The web dashboard fetches a room token via its `/api/token` route:

```typescript
const resp = await fetch("/api/token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ roomName: room, participantName: name }),
});
```

Tokens are short-lived and generated server-side using `livekit-server-sdk`.

---

## STUN Server

LiveKit includes built-in STUN support for NAT traversal. Google public STUN servers are configured by default.

```yaml
rtc:
  stun_servers:
    - stun:stun.l.google.com:19302
    - stun:stun1.l.google.com:19302
```

For production deployments behind symmetric NATs, deploy a TURN server separately (e.g. [coturn](https://github.com/coturn/coturn)) and point LiveKit at it. This version of LiveKit does not support TURN configuration via config file — use environment variables or a reverse proxy if needed.

---

## Docker Compose Service

```yaml
livekit:
  build:
    context: .
    dockerfile: livekit.Dockerfile
  ports:
    - "15580:15580"     # WebSocket
    - "15581:15581"     # WebRTC
    - "15582:15582/udp" # WebRTC UDP
  restart: always
  volumes:
    - livekit_data:/var/lib/livekit
```

---

## Network Ports

| Port | Protocol | Purpose | Firewall |
|------|----------|---------|----------|
| 15580 | TCP | WebSocket (client → server) | Open |
| 15581 | TCP | WebRTC signaling | Open |
| 15582 | UDP | WebRTC media | Open if remote participants |
| 50000–60000 | UDP | WebRTC media (configurable) | Open if remote participants |

---

## Health Check

The conferencing-mCP server probes LiveKit availability:

```python
# TCP connectivity test
check_tcp_port("localhost", 15580)
# → {"status": "ALIVE", "latency_ms": 2}
```

The web dashboard at `/health` shows LiveKit reachability and active rooms.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ConnectionError` on join | LiveKit not running | `docker compose up -d livekit` |
| `401 Unauthorized` | Key mismatch | Check `livekit.yaml` keys match env vars |
| No video from remote | UDP ports blocked | Open ports 15582 + 50000–60000 |
| Room list empty | Wrong `LIVEKIT_URL` | Check port (15580, not 7880) |
| Agent can't connect | Wrong `LIVEKIT_API_KEY` | Verify agent environment |

---

## Authentication via Authentik

AG-Visio supports OIDC authentication via [Authentik](https://goauthentik.io/), a self-hosted identity provider.

### Prerequisites

- Authentik instance (see docker-compose.yaml for a commented-out service definition)
- Administrator access to create an OAuth2/OIDC provider

### Authentik Setup

1. Log into your Authentik admin interface (default: `http://localhost:9000`)
2. Navigate to **Applications → Providers**
3. Click **Create → OAuth2/OIDC Provider**
   - **Client Type**: Confidential
   - **Redirect URIs**: `http://localhost:10886/api/auth/callback/authentik`
   - **Scopes**: OpenID, Email, Profile
4. Save and note the **Client ID** and **Client Secret**
5. Navigate to **Applications → Applications**
6. Click **Create** and link to the provider above

### Dashboard Configuration

Create `apps/web/.env.local` with the Authentik credentials:

```env
# Required: a random secret for JWT encryption (generate: openssl rand -base64 32)
AUTH_SECRET=your-random-secret-here

# Authentik OIDC
AUTH_AUTHENTIK_ID=your-client-id
AUTH_AUTHENTIK_SECRET=your-client-secret
AUTH_AUTHENTIK_ISSUER=http://localhost:9000/application/o/ag-visio
```

### How It Works

1. User visits any dashboard page → middleware checks for session cookie
2. No session → redirect to `/auth/signin`
3. User clicks "Sign in with Authentik" → OIDC flow to Authentik
4. Authentik validates credentials → redirects back to `/api/auth/callback/authentik`
5. next-auth creates a JWT session → user is redirected to original page
6. When user joins a room → `/api/token` uses the authenticated identity (name, email) for the LiveKit token
7. LiveKit token includes user metadata (auth_provider, email) for agent context

### Disabling Auth for Development

Set `AUTH_DISABLED=true` in your env to bypass the middleware and token check.
