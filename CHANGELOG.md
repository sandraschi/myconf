# Changelog

All notable changes to AG-Visio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
