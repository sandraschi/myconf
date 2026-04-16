# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-04-06
### Added
- **Teams++ AI Upgrade**: Major architectural shift to an autonomous meeting intelligence substrate.
- **Native Remoting Substrate**: Introduced `packages/remoting-mcp` for high-performance screen capture and OS-level input injection (Windows `SendInput`).
- **Dynamic MCP Discovery**: Logic implemented to scan 10700-10800 for SSE endpoints, enabling horizontal tool scaling.
- **Meeting Intelligence Dashboard**: Real-time insights panel with LanceDB-powered persistence for summaries and action items.
- **LiveKit 1.x / Agents 1.x**: Full migration to the latest agentic infrastructure.
- **Port Management**: Standardized port registries for fleet-wide compatibility.

### Changed
- Refactored `apps/agent` into a dynamic MCP client (MCPB 3.1+ compliant).
- Deprecated RustDesk IFrame bridge in favor of native LiveKit remoting.
- Hardened `CombinedMCPFunctionContext` for unified tool orchestration.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-03-17

### Added
- **Long-term Memory Substrate:**
    - Integrated `LanceDB` for high-performance vector storage and semantic recall.
    - Implemented `FastEmbed` for local text embeddings without external API dependency.
    - Automated transcript ingestion pipeline for meeting history persistence.
- **Multimodal Address Book Integration:**
    - **Microsoft Graph:** Sync support for Office 365 contacts.
    - **Windows Local:** Native Windows contact provider orchestration.
    - **Gmail (Google):** Integration for Google People API contacts.
    - **Semantic Search:** RAG-driven contact retrieval via `memory_substrate`.
- **Autonomous Perception & Orchestration:**
    - **Industrial OCR:** Added `IndustrialPerception` tool for workspace awareness.
    - **Multi-Agent Signaling:** Enhanced inter-agent communication via LiveKit data channels.
- **Unified Startup Orchestrator:**
    - Implemented `start.ps1` and `start.bat` for "One-Click" full-stack initialization.
    - Automated dependency detection and environment setup (Node/Python).

### Fixed
- **Quality Engineering:**
    - Standardized Python codebase using **Ruff**, resolving 28+ linting and architectural warnings.
    - Established comprehensive `pytest` scaffold with 100% pass rate on core brain substrates.
    - Improved agent tool delegation logic between `agent.py` and modular substrates.

## [0.2.0] - 2026-03-15

### Added
- **LiveKit 1.x & SDK v2 Upgrade:**
    - Integrated `VoicePipelineAgent` (LiveKit 1.x) with multi-agent session support.
    - Implemented End-of-Utterance (EOU) turn detection for more natural conversations.
    - Upgraded Web UI to LiveKit SDK v2 standards (Identity-based components).
- **Advanced Visualization:**
    - **Focus Mode:** Automatic Promotion of active screen shares to a large viewport (70/30 grid split).
    - **Manual Focus:** Users can manually toggle focus states for any participant/track.
- **RustDesk Integration:**
    - Professional remote control bridge via embedded `RustDeskPanel`.
    - Secure iframe sandboxing for remote interaction.
    - Triple-tab sidebar (Transcript / Chat / Remote).
- **SOTA UX:**
    - Refined dashboard glassmorphism and premium UI animations.
    - Integrated Chat Hub via LiveKit's native chat data channel.

### Fixed
- Resolved all major linting warnings in `apps/web` (SDK v2 migration cleanup).
- Standardized `TrackRef` and `ParticipantTile` usage throughout the dashboard.
- Improved transcription feed responsiveness for long-running sessions.

### [0.1.5] - 2026-02-27
- **Linting & Type Safety:**
  - Resolved 43 original linting warnings in the web application.
  - Fixed `turbo/no-undeclared-env-vars` by registering `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `OLLAMA_HOST`, `NODE_ENV`, `NEXT_PUBLIC_LIVEKIT_URL`, and `CI` in `turbo.json`.
  - Escaped JSX entities (`&quot;`, `&apos;`) in `SettingsPage` and `HelpModal`.
  - Fixed React hook dependencies and memoization (`useCallback`) in `app/test/page.tsx`.
  - Removed unused variables and imports in `page.tsx`, `settings.test.ts`, and `ShareRoomModal.tsx`.
  - Replaced literal constant binary expressions in `utils.test.ts` to satisfy logic verification rules.
- **Implicit Any:** Hardened type definitions in `telemetry.ts` and LiveKit transcription handlers, replacing `any` with `unknown` and specific interfaces.

### Added (Detailed)
- **Full dockerization:** Agent runs in Docker; `docker compose up -d` runs livekit, redis, web (port 3000), and agent. Agent uses `OLLAMA_BASE_URL` (default `http://host.docker.internal:11434/v1`) and `OLLAMA_MODEL` (default `gemma2`). `apps/agent/Dockerfile` and `.dockerignore`; compose `extra_hosts` for Linux. See README and PRD Deployment.
- **Roadmap (Phase 2.5):** Full self-host calendaring & invitations documented in PRD and README (event store, scheduling UI, invite emails via SMTP/Email MCP, MCP tools). See PRD.md.

#### Web Application UI Overhaul
- **Professional Topbar** with auth, help, and logger controls
  - User avatar with dropdown menu (settings, logout, version info)
  - Room selection dropdown with live switching between rooms
  - Connection status indicator with animated pulse
  - Help button (triggers keyboard shortcut `?`)
  - Logger button (opens log viewer modal)
  - Guest mode when not authenticated

- **Video/Audio Test Page** (`/test`)
  - Live camera preview with mirrored self-view
  - Real-time audio level monitoring with color-coded meter
  - Device selection for camera, microphone, and speakers
  - Speaker test functionality
  - Status indicators (green check / red alert)
  - Ready-to-join banner when all devices working
  - Error handling for permissions and device access

- **Log Viewer Modal**
  - Real-time log capture from telemetry and console
  - Filterable by level (all, info, warning, error, success)
  - Color-coded log entries with timestamps
  - Download logs as `.txt` file
  - Clear log history
  - Auto-scroll toggle
  - Supports up to 1000 log entries

- **Enhanced Dashboard**
  - "Test Camera & Audio" button on join screen
  - Improved join flow with clearer instructions
  - Room info display (server URL, room name)
  - Better error messaging

- **Settings System**
  - localStorage persistence for user preferences
  - LiveKit server URL configuration
  - Default room name setting
  - Audio/video/output device selection with detection
  - Theme preference (dark/light/system) - dark mode active
  - Telemetry opt-out toggle
  - Environment info display

- **Help Modal**
  - Searchable sidebar with sections
  - Getting Started guide
  - Joining Room instructions
  - Keyboard Shortcuts reference
  - Agent Behavior explanation
  - Troubleshooting tips
  - Keyboard shortcut: `?` to open

- **Retractable Sidebar**
  - Navigation links (Dashboard, Settings)
  - Collapse/expand with state persistence
  - Help button integration
  - Logo and branding

- **UI Components**
  - `Modal` - Generic reusable modal with sizes
  - `Toggle` - Reusable toggle switch
  - `Topbar` - Professional header component
  - `LogViewer` - Advanced logging interface
  - `HelpModal` - Comprehensive help system
  - CSS animations (fadeIn, slideInFromLeft, zoomIn)
  - Mirror effect for video self-view

#### Features
- **Multi-room support** with dynamic room switching
- **Device management** with detection and selection
- **Real-time transcription** panel (existing, preserved)
- **Telemetry system** with event tracking
- **Keyboard shortcuts** system
- **Responsive design** improvements

#### Technical
- Web app port changed from 3000 to 10800
- Added `cn()` utility for class name merging (clsx + tailwind-merge)
- Settings hook (`useSettings`) with localStorage integration
- Telemetry module with log/error methods
- Environment variable support for LiveKit configuration
- `.env.example` created for easy setup

### Changed
- Updated port from 3000 to 10800 in `apps/web/package.json`
- Enhanced `AppShell` with topbar integration
- Improved `app/layout.tsx` with proper metadata
- Refactored dashboard header to use Topbar component
- Updated CSS with mirror transform and additional animations

### Fixed
- Windows compatibility for MCP server disk usage (TypeScript)
- Parameter naming consistency (`limit` vs `lines`) in MCP tools
- Python agent requirements (`fastmcp` added, `asyncio` removed)
- Setup script to use `requirements.txt` properly
- Focus states and accessibility improvements

## [0.1.0] - 2025-01-28

### Initial Release

#### Core Features
- LiveKit real-time video conferencing
- Python AI voice agent ("Visio") with Ollama integration
- Next.js web frontend with LiveKit client
- Docker Compose infrastructure (LiveKit + Redis)
- Dual-language MCP server (Python + TypeScript)

#### Agent Capabilities
- Silero VAD (Voice Activity Detection)
- Whisper STT (Speech-to-Text)
- Piper TTS (Text-to-Speech)
- Ollama LLM integration (gemma2)
- Jargon and LDDO pattern detection

#### MCP Tools
- `get_dev_stats` - Git and disk statistics
- `query_system_logs` - Windows Event Log queries

#### Infrastructure
- Turborepo monorepo setup
- PowerShell setup script (`setup.ps1`)
- LiveKit server configuration (`livekit.yaml`)
- Docker Compose orchestration

---

## Version History

- **Unreleased**: UI overhaul, video testing, logging, multi-room support
- **0.1.0**: Initial release with core conferencing and AI agent features
