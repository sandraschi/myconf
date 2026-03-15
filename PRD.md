# AG-Visio Product Requirements Document (PRD)

**Version**: 1.1  
**Last Updated**: 2025-01-28  
**Status**: Active Development

---

## Executive Summary

AG-Visio is a professional video conferencing platform combining real-time communication with AI-powered voice assistance. Built on LiveKit and Next.js, it delivers enterprise-grade conferencing features with a modern, intuitive interface and intelligent agent capabilities.

### Key Differentiators
- **AI Voice Agent** with natural language understanding and context awareness
- **Premium Glassmorphism UI** with Tailwind 4 and micro-animations
- **Device Testing** before joining meetings
- **Multi-room Support** with seamless switching
- **Real-time Transcription** with speaker identification
- **Remote Support Substrate**: Orchestrated `rustdesk-mcp` integration for industrial assistance.
- **Inter-Agent Signaling**: Grid-wide state propagation and substrate orchestration.
- **Advanced Logging**: Debugging and monitoring with correlation IDs.

---

## Product Vision

### Mission
Provide a privacy-respecting, self-hostable video conferencing solution with AI assistance that enhances rather than replaces human communication.

### Target Users

1. **Development Teams**
   - Need reliable video conferencing for standups and code reviews
   - Value AI assistance for note-taking and context
   - Require self-hosted solutions for IP protection

2. **Technical Organizations**
   - Enterprise teams requiring on-premises deployment
   - Security-conscious organizations
   - Teams with specific compliance requirements

3. **Power Users**
   - Developers and system administrators
   - Users comfortable with self-hosting
   - Those seeking alternatives to cloud-only solutions

---

## Core Features

### 1. Video Conferencing

#### 1.1 Main Conference Room
- **Multi-participant support** via LiveKit infrastructure
- **Grid layout** for video participants
- **Control bar** with standard video/audio toggles
- **Real-time video/audio streams**
- **Adaptive bitrate** based on network conditions

#### 1.2 Connection Management
- **Token-based authentication** for room access
- **Automatic reconnection** on network interruptions
- **Connection status** indicators
- **Clean disconnect** handling

#### 1.3 Room Management
- **Multiple rooms**: `ag-visio-conference`, `development`, `testing`, `demo`
- **Room switching** without page reload
- **Room status** display in topbar
- **Configurable default room** in settings

### 2. Device Testing & Management

#### 2.1 Video Testing Page (`/test`)
- **Live camera preview** with mirrored self-view
- **Device enumeration** (cameras, microphones, speakers)
- **Device selection** dropdowns
- **Real-time device switching**
- **Status indicators** (video/audio working/failed)

#### 2.2 Audio Testing
- **Audio level meter** with visual feedback
- **Color-coded levels** (green/yellow/red)
- **Speaker test** button with tone playback
- **Microphone monitoring**

#### 2.3 Permissions Handling
- **Permission request** flow
- **Error messages** for denied access
- **Browser compatibility** checks
- **Recovery guidance** for common issues

### 3. User Interface

#### 3.1 Topbar
- **User avatar** with first initial
- **User dropdown menu**:
  - User name and connection status
  - Settings link
  - Leave Room button
  - Version information
- **Room selector** (when connected)
- **Help button** (triggers `?` shortcut)
- **Logger button** (opens log viewer)
- **Connection status** indicator

#### 3.2 Sidebar (Retractable)
- **Navigation links**: Dashboard, Settings
- **Active state** highlighting
- **Collapse/expand** with persistence
- **Help button**
- **Logo and branding**

#### 3.3 Modals
- **Help Modal**:
  - Searchable sections
  - Getting Started guide
  - Keyboard shortcuts
  - Agent behavior explanation
  - Troubleshooting tips
- **Log Viewer**:
  - Real-time log display
  - Filter by level
  - Download logs
  - Clear history
  - Auto-scroll toggle

### 4. Settings System

#### 4.1 Connection Settings
- **LiveKit Server URL** (default: `ws://localhost:15580`)
- **Default Room Name** (default: `ag-visio-conference`)

#### 4.2 Device Settings
- **Preferred Camera** selection
- **Preferred Microphone** selection
- **Preferred Audio Output** selection
- **Device Detection** button

#### 4.3 Appearance
- **Theme selector**: Dark, Light, System (dark active, light coming soon)

#### 4.4 Privacy
- **Telemetry opt-out** toggle

#### 4.5 Environment Info
- **Version display**
- **Node environment**
- **LiveKit URL** confirmation

#### 4.6 Persistence
- **localStorage** for client-side persistence
- **Reset to defaults** button
- **Save confirmation** feedback

### 5. Real-time Transcription

#### 5.1 Transcription Panel
- **Right sidebar** (desktop)
- **Speaker identification**
- **Timestamp** for each entry
- **Scrollable history** (limited to 50 entries)
- **Deduplication** logic

#### 5.2 Data Sources
- LiveKit data channels (`RoomEvent.DataReceived`)
- Participant metadata (`RoomEvent.ParticipantMetadataChanged`)
- Agent transcription events

### 6. AI Voice Agent ("Visio")

#### 6.1 Capabilities
- **Voice Activity Detection** (Silero VAD)
- **Speech-to-Text** (Whisper)
- **Text-to-Speech** (Piper)
- **LLM Integration** (Ollama - gemma2)

#### 6.2 Behavior
- **Automatic room joining**
- **Responds when addressed** by name
- **Jargon detection** for technical terms
- **LDDO pattern recognition** (Low-Density Discourse Operators)
- **Context-aware responses**

#### 6.3 Configuration
- Python-based agent (`apps/agent/agent.py`)
- **AGENT_MODE**: Toggle between `local` and `cloud` in `.env`.
- **Local Substrate**: Ollama (gemma2), Whisper (STT), Piper (TTS).
- **Cloud Substrate**: OpenAI (LLM), Deepgram (STT), ElevenLabs (TTS).
- Requires Ollama with compatible model for local mode.

### 7. Logging & Telemetry

#### 7.1 Telemetry Events
- Dashboard mount/unmount
- Token fetch success/failure
- Room connection events
- Room disconnection events
- Device enumeration
- Media stream start/stop
- User actions (logout, room switch)

#### 7.2 Log Viewer
- **Log levels**: info, warning, error, success
- **Filtering** by level
- **Download** as `.txt`
- **Clear** log history
- **Auto-scroll** option
- **1000 entry limit** with rotation
- **Console interception** (log, warn, error)

#### 7.3 Privacy
- **Opt-out** toggle in settings
- **Local-only** logging (no external transmission)
- **Session-scoped** data

### 8. Keyboard Shortcuts

- **`?`** - Open help modal
- **`Esc`** - Close open modal
- **`Enter`** - Submit join form (when focused)

---

## Technical Architecture

### Frontend Stack
- **Next.js 16** (App Router)
- **React 19**
- **TypeScript** (strict mode)
- **TailwindCSS** for styling
- **LiveKit Components** (`@livekit/components-react`)
- **Lucide React** for icons

### Backend / Agent Stack
- **Python 3.11+**
- **livekit-agents** framework
- **Ollama** for LLM
- **Whisper** for STT
- **Piper** for TTS
- **Silero** for VAD

### Infrastructure
- **LiveKit Server** (Docker)
- **Redis** (Docker)
- **Docker Compose** orchestration

### Monorepo
- **Turborepo** for build orchestration
- **Shared packages** (`@repo/ui`, `@repo/eslint-config`, `@repo/typescript-config`)

### MCP Integration
- **Python MCP Server** (Fast_MCP 2.14.4 SOTA Refactor)
- **Context Injection**: `ctx` provided to all tools
- **Tools**: `get_dev_stats`, `query_system_logs`, `sample_log_analysis` (Iterative Sampling)
- **Correlation**: Industrial-standard logging with unique IDs per request

---

## User Flows

### Flow 1: First-Time User Joining Conference

1. Navigate to http://localhost:15500
2. (Optional) Click "Test Camera & Audio"
   - Grant permissions
   - View camera preview
   - Test microphone levels
   - Test speaker output
   - Click "Back to Dashboard" or "Join Conference"
3. Enter participant name
4. Review room and server info
5. Click "Join Room"
6. Wait for token generation
7. Connect to LiveKit room
8. See video grid and controls
9. (Optional) View transcription in right sidebar
10. (Optional) Click help icon or press `?` for guidance

### Flow 2: Switching Rooms

1. User is connected to a room
2. Click room dropdown in topbar
3. Select different room from list
4. Confirm (automatic)
5. Disconnect from current room
6. Reconnect to new room with same participant name
7. See updated room name in topbar

### Flow 3: Viewing Logs

1. Click Terminal icon in topbar
2. Log viewer modal opens
3. See real-time logs with timestamps
4. (Optional) Filter by level
5. (Optional) Toggle auto-scroll
6. (Optional) Download logs
7. (Optional) Clear logs
8. Close modal when done

### Flow 4: Configuring Settings

1. Click user avatar or navigate to `/settings`
2. Modify desired settings:
   - Change LiveKit URL
   - Change default room
   - Select preferred devices
   - Toggle telemetry
3. Click "Save Changes"
4. See success toast
5. Settings persist in localStorage
6. Return to dashboard

---

## Technical Requirements

### Performance
- **Video latency**: < 500ms under normal network conditions
- **Audio latency**: < 300ms
- **Page load time**: < 2s on broadband
- **Transcription delay**: < 1s from speech end

### Browser Support
- **Chrome/Edge**: 90+
- **Firefox**: 88+
- **Safari**: 14+ (WebRTC support required)

### Network Requirements
- **Minimum bandwidth**: 1 Mbps up/down per participant
- **Recommended bandwidth**: 3 Mbps up/down
- **WebRTC ports**: UDP 15581 (LiveKit default)

### System Requirements

#### Web Client
- Modern browser with WebRTC support
- Camera and microphone access
- JavaScript enabled

#### Server/Agent
- **OS**: Windows 10+ / Linux / macOS
- **Docker**: 24.0+
- **Docker Compose**: v2
- **Python**: 3.11+
- **Node.js**: 18+
- **Ollama**: Latest (for AI agent)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for Docker images

---

## Security & Privacy

### Data Handling
- **No external data transmission** (self-hosted)
- **Telemetry opt-out** available
- **Local storage** for settings only
- **No persistent chat history**

### Authentication
- **Token-based** room access
- **Short-lived tokens** (configurable)
- **API key** for token generation (dev: hardcoded, prod: env vars)

### Network Security
- **WebSocket** connections (ws:// in dev, wss:// in prod)
- **CORS** restrictions on API routes
- **No credentials** stored in localStorage

---

## Future Enhancements

### Phase 2 (Planned)
- **Screen sharing** support
- **Recording** functionality
- **Chat panel** alongside transcription
- **Participant list** with actions
- **Hand raise** feature
- **Background blur** / virtual backgrounds
- **Light theme** completion
- **Mobile responsive** improvements

### Phase 2.5: Full self-host calendaring & invitations
- **Event store** – SQLite or Postgres; or CalDAV server (e.g. Radicale, Baïkal) for standards-based calendars
- **Scheduling UI** – Create meetings: title, datetime, duration, room; generate room link + optional QR
- **Invitations** – Send “Join AG-Visio room at &lt;time&gt;” link via email (self-hosted SMTP or Email MCP); copy-link fallback
- **No external calendar dependency** – No Google/Microsoft OAuth; optional CalDAV sync for clients that support it
- **MCP tools** – e.g. list today’s meetings, create meeting, send invite (for Claude/Cursor)

### Phase 3 (Wishlist)
- **Breakout rooms**
- **Whiteboard collaboration**
- **File sharing**
- **End-to-end encryption**
- **SFU optimization** for large rooms (50+ participants)

---

## Success Metrics

### Technical Metrics
- **Uptime**: > 99.5%
- **Connection success rate**: > 95%
- **Audio/video quality**: > 90% "good" rating
- **Device detection success**: > 98%

### User Experience Metrics
- **Time to join**: < 30 seconds
- **Setup completion rate**: > 85%
- **Settings usage**: > 40% of users
- **Device test usage**: > 60% first-time users

### AI Agent Metrics
- **Response relevance**: > 80% user satisfaction
- **Response time**: < 2 seconds
- **False activation rate**: < 5%
- **Transcription accuracy**: > 90% WER (Word Error Rate)

---

## Dependencies

### Critical Dependencies
- **LiveKit Server**: Real-time infrastructure
- **Ollama**: LLM inference for agent
- **Docker**: Containerization

### Optional Dependencies
- **Redis**: State management (can fallback to in-memory)

---

## Deployment

### Full Dockerization
- **One-command stack:** `docker compose up -d` runs livekit, redis, web (port 15500), and agent.
- **Ollama runs outside Docker on your PC.** Start Ollama on the host (e.g. `ollama serve`, `ollama pull gemma2`). The agent container connects to LiveKit inside the network and to the host's Ollama via `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`. On Linux, `extra_hosts: host.docker.internal:host-gateway` is set.
- **Web** in Docker serv- Test at http://localhost:15500/test; browser connects to LiveKit at ws://localhost:15580.
- **Optional:** Add an `ollama` service to compose and set agent `OLLAMA_BASE_URL=http://ollama:11434/v1` for a fully self-contained stack (Ollama inside Docker).

### Development (local web + agent)
```powershell
.\setup.ps1
docker compose up -d
# Terminal 1:
cd apps/agent; .\venv\Scripts\activate; python agent.py dev
# Terminal 2:
npm run dev --workspace=web
```

### Production Considerations
- Replace dev API keys with production secrets
- Use `wss://` (secure WebSocket)
- Enable HTTPS on web server
- Configure LiveKit for production scaling
- Set up monitoring and alerts
- Implement log aggregation
- Configure backup and recovery

---

## Risks & Mitigations

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| WebRTC compatibility | High | Browser detection, fallback messaging |
| Network instability | Medium | Auto-reconnect, quality adaptation |
| Device access denied | High | Clear permission flow, test page |
| Ollama model unavailable | Medium | Graceful degradation, fallback responses |

### User Experience Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Complex setup | Medium | One-step `setup.ps1`, comprehensive docs |
| Unclear UI | Low | Help modal, tooltips, visual feedback |
| Lost settings | Low | localStorage persistence, export/import (future) |

---

## Compliance & Standards

- **WebRTC**: Standards-compliant implementation
- **Accessibility**: WCAG 2.1 Level A (basic compliance)
- **Data Retention**: No persistent data stored by default
- **GDPR**: Self-hosted, no third-party data sharing

---

## Appendix

### Glossary
- **LiveKit**: Open-source WebRTC SFU (Selective Forwarding Unit)
- **MCP**: Model Context Protocol for AI tool integration
- **VAD**: Voice Activity Detection
- **STT**: Speech-to-Text
- **TTS**: Text-to-Speech
- **LDDO**: Low-Density Discourse Operators (jargon detection)
- **Ollama**: Local LLM inference engine

### References
- [LiveKit Documentation](https://docs.livekit.io/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Turborepo Documentation](https://turborepo.dev/)

---

**Document Maintainer**: Development Team  
**Review Cycle**: Bi-weekly  
**Next Review**: 2025-02-11
