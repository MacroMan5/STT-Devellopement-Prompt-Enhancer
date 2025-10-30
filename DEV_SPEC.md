# Development Specification: lazy-ptt-enhancer

> **Open-source voice-to-prompt toolkit for AI-assisted development workflows**

**Version**: 1.0.0
**Status**: Pre-Release (MVP Ready)
**License**: MIT
**Target Release**: Q1 2025
**Maintainer**: [@therouxe](https://github.com/therouxe)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Features](#core-features)
4. [Implementation Status](#implementation-status)
5. [API Specification](#api-specification)
6. [CLI Specification](#cli-specification)
7. [Configuration System](#configuration-system)
8. [Output Branding](#output-branding)
9. [Testing Requirements](#testing-requirements)
10. [Documentation Requirements](#documentation-requirements)
11. [Release Checklist](#release-checklist)
12. [Roadmap](#roadmap)

---

## Project Overview

### Mission Statement

**Enable developers to capture voice input, transcribe locally with Whisper, and enhance into detailed specifications using AI—all without leaving their workspace.**

### Key Differentiators

1. **Workspace-Aware**: Generates prompts directly in project directories (no copy-paste)
2. **Always-On Daemon**: Background process waiting for push-to-talk activation
3. **Local-First**: Whisper runs locally (offline capable), only enhancement hits API
4. **Claude Code Integration**: Designed for seamless plugin integration
5. **Branded Output**: All prompts include attribution to @therouxe

### Target Users

- **Primary**: Developers using Claude Code CLI for AI-assisted development
- **Secondary**: Any developer wanting voice-to-prompt workflow
- **Tertiary**: Product managers, technical writers, QA engineers

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                    │
│  (Push F12 → Record → Release F12 → Process → Save)         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     CLI/Daemon Layer                         │
│  (lazy-ptt listen | daemon | enhance-text | process-audio)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│         ┌──────────────────────────────────┐                │
│         │       PTTService (Orchestrator)   │                │
│         └──────────────────────────────────┘                │
│                     ↓           ↓                            │
│         ┌─────────────────┐  ┌──────────────────┐           │
│         │  AudioRecorder  │  │ PromptEnhancer   │           │
│         │  (sounddevice)  │  │ (OpenAI API)     │           │
│         └─────────────────┘  └──────────────────┘           │
│                     ↓                   ↓                    │
│         ┌─────────────────┐  ┌──────────────────┐           │
│         │  WhisperSTT     │  │ PromptStorage    │           │
│         │  (faster-whisper)│ │ (Filesystem)     │           │
│         └─────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Filesystem Output                          │
│  project-management/prompts/PROMPT-{timestamp}.md            │
│  .lazy-ptt/staging/PROMPT-{timestamp}.md (temp)             │
│  .lazy-ptt/metadata/PROMPT-{timestamp}.json (metadata)      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Dependencies |
|-----------|----------------|--------------|
| **CLI** | Parse commands, invoke service layer | argparse |
| **PTTService** | Orchestrate audio → transcription → enhancement → storage | All components |
| **AudioRecorder** | Capture audio via push-to-talk hotkey | sounddevice, pynput |
| **WhisperSTT** | Transcribe audio to text (local) | faster-whisper |
| **PromptEnhancer** | Enhance brief into detailed spec (API) | openai |
| **PromptStorage** | Save/load prompts with metadata | pathlib, json |
| **PTTDaemon** | Background loop for always-on capture | PTTService |

---

## Core Features

### MVP (v1.0.0) - Must Have

- [x] ✅ Push-to-talk audio capture (F12 default)
- [x] ✅ Local Whisper transcription (GPU-accelerated)
- [x] ✅ OpenAI prompt enhancement with structured output
- [x] ✅ Workspace-aware prompt storage (project-management/)
- [x] ✅ CLI commands: listen, enhance-text, process-audio, daemon
- [x] ✅ Daemon mode (always-on background process)
- [x] ✅ Configurable via environment variables
- [x] ✅ Metadata JSON alongside each prompt
- [x] ✅ Error handling with actionable messages
- [ ] ⏳ Branded output with @therouxe attribution
- [ ] ⏳ `lazy-ptt init` command for first-time setup
- [ ] ⏳ `lazy-ptt status` command for diagnostics
- [ ] ⏳ Cross-platform support (Windows, macOS, Linux)
- [ ] ⏳ Unit tests (80% coverage minimum)
- [ ] ⏳ Integration tests for full workflow
- [ ] ⏳ Documentation (README, CLAUDE_CODE_INTEGRATION.md, DEV_SPEC.md)

### Post-MVP (v1.1.0+) - Nice to Have

- [ ] 📅 Local LLM support (Ollama, llama.cpp)
- [ ] 📅 Multi-language transcription (auto-detect)
- [ ] 📅 Custom enhancement profiles (security, marketing, etc.)
- [ ] 📅 REST API endpoint for non-Python clients
- [ ] 📅 Desktop UI (live audio levels, transcription preview)
- [ ] 📅 Web dashboard (session history, statistics)
- [ ] 📅 GitHub issue integration (auto-create from prompt)
- [ ] 📅 Slack/Discord notifications on prompt creation
- [ ] 📅 Voice profile management (different speakers)
- [ ] 📅 Hot-reload configuration (change settings without restart)

---

## Implementation Status

### Completed (Estimated 70%)

| Module | Status | Lines | Tests | Notes |
|--------|--------|-------|-------|-------|
| `cli.py` | ✅ 100% | 176 | ❌ | All commands implemented |
| `config.py` | ✅ 100% | ~150 | ❌ | Environment + YAML config |
| `audio/recorder.py` | ✅ 90% | ~120 | ❌ | Audio capture working |
| `stt/whisper.py` | ✅ 95% | ~80 | ❌ | Whisper integration done |
| `prompt/enhancer.py` | ✅ 100% | 161 | ✅ | OpenAI integration complete |
| `prompt/manager.py` | ✅ 90% | ~200 | ❌ | Storage/loading working |
| `services/ptt_service.py` | ✅ 85% | ~150 | ❌ | Orchestration complete |
| `services/daemon.py` | ✅ 100% | ~60 | ✅ | Daemon loop complete |
| `input/hotkey.py` | ✅ 100% | ~80 | ❌ | Hotkey detection working |

### Remaining Work (Estimated 30%)

#### High Priority (Must Complete for v1.0.0)

1. **Branding System** (2-4 hours)
   - Add footer to all generated prompts
   - Include @therouxe attribution, GitHub link
   - Configurable via `branding` section in config

2. **Init Command** (2-3 hours)
   - `lazy-ptt init` to scaffold config files
   - Check dependencies (CUDA, audio devices)
   - Generate `.env` template
   - Create directory structure

3. **Status Command** (1-2 hours)
   - `lazy-ptt status` to show diagnostics
   - Last prompt path, stats, daemon status
   - Audio device info, model info

4. **Cross-Platform Testing** (4-8 hours)
   - Test on Windows, macOS, Linux
   - Fix path handling (Windows backslashes)
   - Audio device detection across platforms

5. **Unit Tests** (8-12 hours)
   - Test coverage to 80% minimum
   - Mock external dependencies (OpenAI, Whisper)
   - Test error conditions

6. **Documentation** (4-6 hours)
   - Complete README.md
   - Add examples/ directory with sample prompts
   - Document all CLI commands
   - API documentation (for Python API usage)

#### Medium Priority (Can Defer to v1.1.0)

1. **Local LLM Support** (6-10 hours)
   - Support Ollama, llama.cpp endpoints
   - Fallback logic (OpenAI → local)

2. **REST API** (8-12 hours)
   - FastAPI wrapper around PTTService
   - Endpoints: /listen, /enhance, /process-audio
   - Authentication (API key)

3. **Desktop UI** (20-30 hours)
   - Qt or Electron UI
   - Live audio levels, transcription preview
   - Session history

---

## API Specification

### Python API

```python
from lazy_ptt import PTTService, AppConfig, load_config

# Load config from environment + .lazy-ptt.yaml
config = load_config()

# Or create config manually
config = AppConfig(
    openai=OpenAIConfig(api_key="sk-...", model="gpt-4"),
    whisper=WhisperConfig(model="medium", language="en"),
    audio=AudioConfig(sample_rate=16000, channels=1),
    paths=PathConfig(
        project_management_root="./project-management",
        staging_dir="./.lazy-ptt/staging",
    ),
)

# Create service
service = PTTService.from_config(config)

# Capture voice input
outcome = service.listen_once(
    story_id="US-3.4",
    story_title="Add user authentication",
    auto_move=True,
)

print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
print(f"Work type: {outcome.enhanced.work_type}")
print(f"Summary: {outcome.enhanced.summary}")

# Enhance text directly
outcome = service.enhance_text(
    "Add user authentication with OAuth2",
    story_id="US-3.4",
    auto_move=True,
)

# Process existing audio file
outcome = service.process_audio_file(
    Path("recording.wav"),
    story_id="US-3.4",
    auto_move=True,
)
```

### REST API (Post-MVP)

```bash
# Start API server
lazy-ptt serve --port 8000 --api-key YOUR_API_KEY

# Endpoints
POST /v1/listen        # Capture voice (requires audio stream)
POST /v1/enhance       # Enhance text brief
POST /v1/process-audio # Process uploaded audio file
GET  /v1/status        # Server status, last prompt
GET  /v1/prompts       # List generated prompts
GET  /v1/prompts/{id}  # Get specific prompt
```

---

## CLI Specification

### Commands

#### `lazy-ptt init`

**Purpose**: First-time setup wizard

```bash
lazy-ptt init [--config-path PATH]
```

**Behavior**:
1. Check dependencies (Python, CUDA, audio devices)
2. Create `.env` template if not exists
3. Create `.lazy-ptt.yaml` with defaults
4. Create directory structure (project-management/, .lazy-ptt/)
5. Test audio capture (quick recording)
6. Test Whisper model download
7. Print next steps

**Output Example**:
```
✅ Dependencies check passed
✅ Configuration created: .lazy-ptt.yaml
✅ Directory structure created
✅ Audio device detected: Built-in Microphone
✅ Whisper model downloaded: medium

🎤 Setup complete! Next steps:
1. Set your OpenAI API key: export OPENAI_API_KEY=sk-...
2. Start daemon: lazy-ptt daemon --verbose-cycle
3. Press F12 to capture voice input anytime
```

---

#### `lazy-ptt listen`

**Purpose**: Capture single voice input

```bash
lazy-ptt listen [OPTIONS]
  --story-id ID           # Override story ID (default: auto-generate)
  --story-title "Title"   # Story title metadata
  --auto-move             # Move to project-management immediately
  --json                  # Output JSON instead of human-readable
```

**Behavior**:
1. Print "Press F12 to start recording..."
2. Wait for hotkey press
3. Record audio while hotkey held
4. Transcribe with Whisper (show progress)
5. Enhance with OpenAI (show progress)
6. Save to staging or project-management
7. Print prompt path, work type, summary

**Output Example**:
```
🎤 Press F12 to start recording...
🔴 Recording... (release F12 to stop)
✅ Audio captured (3.2s)
🔄 Transcribing with Whisper...
✅ Transcription: "Add user authentication with OAuth2 and session management"
🔄 Enhancing with OpenAI...
✅ Enhanced prompt generated
📄 Prompt saved to: project-management/prompts/PROMPT-20251029-143022.md

Work Type: FEATURE
Summary: Add user authentication with OAuth2 and session management
```

---

#### `lazy-ptt enhance-text`

**Purpose**: Enhance text brief without voice capture

```bash
lazy-ptt enhance-text [OPTIONS]
  --text "Brief text"     # Text to enhance
  --file path/to/file.txt # Or read from file
  --story-id ID
  --story-title "Title"
  --auto-move
  --json
```

**Behavior**:
1. Read text from `--text` or `--file`
2. Enhance with OpenAI
3. Save to staging or project-management
4. Print prompt path, work type, summary

**Output Example**:
```
🔄 Enhancing brief...
✅ Enhanced prompt generated
📄 Prompt saved to: project-management/prompts/PROMPT-20251029-143022.md

Work Type: FEATURE
Summary: Add payment processing with Stripe integration
```

---

#### `lazy-ptt process-audio`

**Purpose**: Transcribe and enhance existing audio file

```bash
lazy-ptt process-audio path/to/audio.wav [OPTIONS]
  --story-id ID
  --story-title "Title"
  --auto-move
  --json
```

**Behavior**:
1. Load audio file (wav, mp3, flac, ogg)
2. Transcribe with Whisper
3. Enhance with OpenAI
4. Save to staging or project-management
5. Print prompt path, work type, summary

**Output Example**:
```
📂 Loading audio: recording.wav
🔄 Transcribing with Whisper...
✅ Transcription: "Fix the login bug where users get logged out after 5 minutes"
🔄 Enhancing with OpenAI...
✅ Enhanced prompt generated
📄 Prompt saved to: project-management/prompts/PROMPT-20251029-143022.md

Work Type: HOTFIX
Summary: Fix session timeout bug in authentication system
```

---

#### `lazy-ptt create-feature`

**Purpose**: Move staged prompt to project-management

```bash
lazy-ptt create-feature path/to/prompt.md [OPTIONS]
  --story-title "Title"   # Override story title in metadata
```

**Behavior**:
1. Load prompt from staging
2. Copy to project-management/prompts/
3. Update metadata with new location
4. Print new path

**Output Example**:
```
📦 Moving prompt to project-management...
✅ Prompt moved: project-management/prompts/PROMPT-20251029-143022.md
```

---

#### `lazy-ptt daemon`

**Purpose**: Run always-on background listener

```bash
lazy-ptt daemon [OPTIONS]
  --stay-local            # Keep in staging, don't auto-move
  --verbose-cycle         # Log each capture cycle
  --log-file PATH         # Write logs to file
```

**Behavior**:
1. Print "Daemon started. Press F12 to capture voice anytime."
2. Enter infinite loop:
   - Wait for hotkey press
   - Record audio
   - Transcribe + enhance
   - Save to staging or project-management
   - If `--verbose-cycle`, print summary
   - Continue loop
3. On Ctrl+C, graceful shutdown

**Output Example (verbose mode)**:
```
🎤 Daemon started. Press F12 to capture voice anytime.
Hotkey: F12
Staging: .lazy-ptt/staging
Auto-move: enabled

[2025-10-29 14:30:22] Waiting for hotkey...
[2025-10-29 14:30:45] Recording...
[2025-10-29 14:30:48] Transcribing...
[2025-10-29 14:30:52] Enhancing...
[2025-10-29 14:30:55] ✅ Prompt saved: project-management/prompts/PROMPT-20251029-143055.md (FEATURE)
[2025-10-29 14:30:55] Waiting for hotkey...

^C
🛑 Daemon stopped gracefully.
```

---

#### `lazy-ptt status`

**Purpose**: Show diagnostics and last prompt info

```bash
lazy-ptt status [OPTIONS]
  --last-prompt           # Print only last prompt path (for scripting)
  --stats                 # Show usage statistics
  --check-deps            # Check all dependencies
```

**Behavior**:
1. Check daemon status (running/stopped)
2. Show last prompt path and metadata
3. If `--stats`, show total prompts, average duration, etc.
4. If `--check-deps`, verify Python, CUDA, audio, models

**Output Example**:
```
🔍 lazy-ptt Status

Daemon: ✅ Running (PID: 12345)
Hotkey: F12

Last Prompt:
  Path: project-management/prompts/PROMPT-20251029-143055.md
  Work Type: FEATURE
  Summary: Add payment processing with Stripe integration
  Created: 2025-10-29 14:30:55

Statistics (last 7 days):
  Total Prompts: 42
  Avg Duration: 4.2s
  Most Common Work Type: FEATURE (60%)

Dependencies:
  ✅ Python 3.11.5
  ✅ CUDA 12.1 (GPU acceleration enabled)
  ✅ Audio Device: Built-in Microphone
  ✅ Whisper Model: medium (downloaded)
  ✅ OpenAI API: Connected (gpt-4)
```

---

## Configuration System

### Environment Variables (Highest Priority)

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults shown)
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_OUTPUT_TOKENS=2048

WHISPER_MODEL=medium  # tiny, base, small, medium, large
WHISPER_LANGUAGE=en   # auto for auto-detect
WHISPER_DEVICE=auto   # auto, cpu, cuda

PTT_HOTKEY=<f12>
AUDIO_DEVICE_INDEX=null  # null for auto-detect
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1

PROJECT_MANAGEMENT_ROOT=./project-management
PROMPT_STAGING_DIR=./.lazy-ptt/staging
```

### YAML Config (Medium Priority)

`.lazy-ptt.yaml` in project root:

```yaml
openai:
  api_key: ${OPENAI_API_KEY}  # Can reference env vars
  model: gpt-4
  temperature: 0.7
  max_output_tokens: 2048

whisper:
  model: medium
  language: en
  device: auto

audio:
  sample_rate: 16000
  channels: 1
  device_index: null

hotkey:
  trigger: "<f12>"

paths:
  project_management_root: ./project-management
  staging_dir: ./.lazy-ptt/staging

branding:
  enabled: true
  attribution: "Generated with lazy-ptt-enhancer by @therouxe"
  github_url: "https://github.com/therouxe/lazy-ptt-enhancer"
  show_links: true
```

### Programmatic Config (Lowest Priority)

```python
from lazy_ptt import AppConfig, OpenAIConfig, WhisperConfig

config = AppConfig(
    openai=OpenAIConfig(api_key="sk-...", model="gpt-4"),
    whisper=WhisperConfig(model="medium", language="en"),
    # ... other config
)

service = PTTService.from_config(config)
```

### Config Resolution Order

1. **Programmatic config** (if using Python API)
2. **Environment variables** (highest priority for CLI)
3. **`.lazy-ptt.yaml`** in current directory
4. **`.lazy-ptt.yaml`** in user home directory (~/.lazy-ptt.yaml)
5. **Default values** (hardcoded in code)

---

## Output Branding

### Branded Prompt Template

Every generated prompt includes attribution footer:

```markdown
# {WORK_TYPE} Plan

**Summary**: {summary}

## Objectives
- {objective 1}
- {objective 2}

## Risks & Unknowns
- {risk 1}
- {risk 2}

## Recommended Milestones
1. {milestone 1}
2. {milestone 2}

## {Custom Section Title}
{custom section content}

## Acceptance Criteria
- [ ] {criterion 1}
- [ ] {criterion 2}

## Original Brief
> {original transcription or text}

---

_Suggested Story ID_: {suggested_story_id}

---

🎤 **Generated with [lazy-ptt-enhancer](https://github.com/therouxe/lazy-ptt-enhancer)**
Created by [@therouxe](https://github.com/therouxe) | Powered by Whisper + OpenAI
[⭐ Star on GitHub](https://github.com/therouxe/lazy-ptt-enhancer) | [📖 Documentation](https://github.com/therouxe/lazy-ptt-enhancer#readme) | [🐛 Report Issues](https://github.com/therouxe/lazy-ptt-enhancer/issues)
```

### Branding Configuration

Users can customize branding in `.lazy-ptt.yaml`:

```yaml
branding:
  enabled: true  # Set to false to disable footer
  attribution: "Generated with lazy-ptt-enhancer by @therouxe"
  github_url: "https://github.com/therouxe/lazy-ptt-enhancer"
  show_links: true  # Include "Star on GitHub" links
  custom_footer: null  # Optional custom footer text
```

### Implementation in Code

Modify `prompt/enhancer.py` → `EnhancedPrompt.to_markdown()`:

```python
def to_markdown(self, branding_config: Optional[BrandingConfig] = None) -> str:
    lines = [
        f"# {self.work_type} Plan",
        "",
        f"**Summary**: {self.summary}",
        # ... rest of content
    ]

    # Add branding footer
    if branding_config and branding_config.enabled:
        lines.extend([
            "",
            "---",
            "",
            f"🎤 **Generated with [lazy-ptt-enhancer]({branding_config.github_url})**",
            f"Created by [@therouxe](https://github.com/therouxe) | Powered by Whisper + OpenAI",
        ])

        if branding_config.show_links:
            lines.append(
                f"[⭐ Star on GitHub]({branding_config.github_url}) | "
                f"[📖 Documentation]({branding_config.github_url}#readme) | "
                f"[🐛 Report Issues]({branding_config.github_url}/issues)"
            )

    return "\n".join(lines).strip() + "\n"
```

---

## Testing Requirements

### Unit Tests (Minimum 80% Coverage)

**Priority Test Files**:

```
tests/
├── unit/
│   ├── test_config.py           # Config loading, validation
│   ├── test_prompt_enhancer.py  # OpenAI integration (mocked)
│   ├── test_prompt_manager.py   # Storage/loading
│   ├── test_whisper_stt.py      # Whisper integration (mocked)
│   ├── test_audio_recorder.py   # Audio capture (mocked)
│   ├── test_ptt_service.py      # Service orchestration
│   ├── test_daemon.py           # Daemon loop control
│   └── test_cli.py              # CLI command parsing
├── integration/
│   ├── test_end_to_end.py       # Full workflow (real audio file)
│   ├── test_daemon_lifecycle.py # Daemon start/stop/signal handling
│   └── test_cross_platform.py   # Windows/macOS/Linux paths
└── fixtures/
    ├── audio/
    │   ├── sample_01.wav         # Test audio files
    │   └── sample_02.mp3
    └── prompts/
        ├── expected_output.md    # Expected prompt format
        └── branding_test.md      # Branding output test
```

### Key Test Scenarios

1. **Config Loading**:
   - Environment variables override YAML
   - Missing required config raises error
   - Default values applied correctly

2. **Prompt Enhancement**:
   - Valid brief returns structured output
   - Empty brief raises ValueError
   - API errors handled gracefully
   - Branding footer included when enabled

3. **Audio Capture**:
   - Hotkey detection works
   - Audio buffer captured correctly
   - Device errors handled

4. **Whisper Transcription**:
   - Audio file transcribed correctly
   - Multi-language support works
   - Model download on first run

5. **Storage**:
   - Prompts saved to correct directory
   - Metadata JSON created alongside
   - Auto-move to project-management works

6. **Daemon**:
   - Starts and stops gracefully
   - Handles Ctrl+C signal
   - Continues after errors
   - Verbose logging works

7. **Cross-Platform**:
   - Path handling (Windows backslashes)
   - Audio device detection
   - Hotkey detection (platform-specific)

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=lazy_ptt --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_prompt_enhancer.py

# Run integration tests only
pytest tests/integration/
```

---

## Documentation Requirements

### Must-Have Documentation

1. **README.md** (User-facing)
   - What is lazy-ptt-enhancer?
   - Installation instructions
   - Quick start (5-minute setup)
   - CLI command reference
   - Configuration reference
   - Examples
   - Troubleshooting
   - License, contributing

2. **CLAUDE_CODE_INTEGRATION.md** (Plugin Developer Guide)
   - How to integrate with Claude Code plugins
   - Daemon setup
   - Hook examples
   - Plugin manifest templates
   - Distribution strategy

3. **DEV_SPEC.md** (This File - Developer Reference)
   - Architecture
   - API specification
   - Implementation status
   - Testing requirements
   - Release checklist

4. **CONTRIBUTING.md** (Contributor Guide)
   - How to contribute
   - Development setup
   - Code style (Black, Ruff)
   - Testing requirements
   - PR process

5. **API.md** (Python API Reference)
   - Python API usage
   - Class documentation
   - Method signatures
   - Examples

### Optional Documentation (Post-MVP)

- `ARCHITECTURE.md` - Detailed architecture diagrams
- `DEPLOYMENT.md` - Production deployment guide
- `SECURITY.md` - Security considerations
- `PERFORMANCE.md` - Performance optimization guide

---

## Release Checklist

### Pre-Release (v1.0.0)

#### Code Complete

- [ ] Branding footer implementation
- [ ] `lazy-ptt init` command
- [ ] `lazy-ptt status` command
- [ ] Cross-platform testing (Windows, macOS, Linux)
- [ ] Error handling review (actionable messages)
- [ ] Code cleanup (remove debug prints, TODOs)

#### Testing

- [ ] Unit tests at 80% coverage
- [ ] Integration tests pass
- [ ] Manual testing on all platforms
- [ ] Audio device compatibility testing
- [ ] API key validation testing

#### Documentation

- [ ] README.md complete
- [ ] CLAUDE_CODE_INTEGRATION.md complete
- [ ] DEV_SPEC.md complete (this file)
- [ ] CONTRIBUTING.md created
- [ ] API.md created
- [ ] CHANGELOG.md created

#### Repository Setup

- [ ] GitHub repository created (`therouxe/lazy-ptt-enhancer`)
- [ ] LICENSE file (MIT)
- [ ] .gitignore (Python, audio files, .env)
- [ ] Issue templates
- [ ] PR template
- [ ] GitHub Actions CI (test, lint, type-check)

#### PyPI Preparation

- [ ] PyPI account created
- [ ] Package metadata updated (pyproject.toml)
- [ ] Build system tested (`python -m build`)
- [ ] Test PyPI upload successful
- [ ] Version number finalized (1.0.0)

### Release Day

1. **Tag Release**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0: Initial public release"
   git push origin v1.0.0
   ```

2. **Build Package**:
   ```bash
   python -m build
   # Creates dist/lazy_ptt_enhancer-1.0.0-py3-none-any.whl
   # Creates dist/lazy_ptt_enhancer-1.0.0.tar.gz
   ```

3. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

4. **Create GitHub Release**:
   - Title: "v1.0.0 - Initial Public Release"
   - Description: Release notes from CHANGELOG.md
   - Attach wheel and source tarball

5. **Announce**:
   - Twitter/X post with demo video
   - Reddit: r/Python, r/ClaudeAI, r/programming
   - Hacker News (Show HN)
   - Dev.to article
   - Personal blog post

### Post-Release

- [ ] Monitor GitHub issues
- [ ] Respond to feedback within 24 hours
- [ ] Update documentation based on FAQs
- [ ] Plan v1.1.0 features based on feedback

---

## Roadmap

### v1.0.0 (Q1 2025) - MVP Release

**Goal**: Stable, production-ready voice-to-prompt toolkit

- ✅ Core features (audio capture, transcription, enhancement)
- ✅ CLI commands (listen, enhance-text, process-audio, daemon)
- ✅ Workspace-aware storage
- ⏳ Branding system
- ⏳ Init/status commands
- ⏳ Cross-platform support
- ⏳ 80% test coverage
- ⏳ Complete documentation
- ⏳ PyPI release

**Success Metrics**:
- 100 PyPI downloads in first week
- 50 GitHub stars in first month
- Zero critical bugs reported
- 5+ community contributions

---

### v1.1.0 (Q2 2025) - Local Models

**Goal**: Remove OpenAI dependency, support local LLMs

**Features**:
- Local LLM support (Ollama, llama.cpp, vLLM)
- Automatic fallback (OpenAI → local if API key missing)
- Model selection CLI flag (`--model llama-3-70b`)
- Custom enhancement profiles (security, marketing, etc.)
- Profile hot-reload (change profile without restart)

**Success Metrics**:
- 500 PyPI downloads/week
- 200 GitHub stars
- 10+ community contributions
- 3+ forks with custom profiles

---

### v1.2.0 (Q2 2025) - Multi-Language

**Goal**: Support non-English workflows

**Features**:
- Multi-language Whisper transcription (auto-detect)
- Multi-language prompt enhancement (French, Spanish, German, etc.)
- Language selection in config
- Language auto-detection from audio

**Success Metrics**:
- 20% non-English users
- Translations for README (French, Spanish, Chinese)

---

### v1.3.0 (Q3 2025) - REST API

**Goal**: Enable non-Python clients

**Features**:
- FastAPI REST API wrapper
- Endpoints: /listen, /enhance, /process-audio
- API key authentication
- Rate limiting
- Docker deployment guide

**Success Metrics**:
- 10+ API clients (JS, Go, Rust, etc.)
- Hosted API service (managed offering)

---

### v2.0.0 (Q4 2025) - Desktop UI

**Goal**: Visual interface for non-technical users

**Features**:
- Desktop UI (Qt or Electron)
- Live audio levels during recording
- Real-time transcription preview
- Enhanced prompt preview with syntax highlighting
- Session history browser
- Settings panel (no config file editing)

**Success Metrics**:
- 1000 downloads of desktop app
- 50% user preference for UI over CLI

---

## Monetization Strategy (Optional)

### Open Source Core (Free Forever)

- CLI tool (all features)
- Python API
- Self-hosted
- Community support (GitHub issues)

### Premium Offerings

1. **Hosted API Service** ($49/month)
   - No local setup required
   - 10k minutes transcription/month
   - Priority support
   - Guaranteed uptime SLA

2. **Team Edition** ($199/month)
   - Multi-user dashboard
   - Shared prompt library
   - SSO integration
   - Usage analytics
   - Audit logs

3. **Enterprise** (Custom Pricing)
   - On-premise deployment
   - Custom model fine-tuning
   - Dedicated support engineer
   - Training sessions
   - Custom integrations

4. **Premium Domain Packs** ($29/one-time)
   - Legal domain pack (contract review, compliance)
   - Medical domain pack (HIPAA-aware, clinical notes)
   - Finance domain pack (risk assessment, compliance)
   - Each pack = custom enhancement profiles + templates

---

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/therouxe/lazy-ptt-enhancer.git
cd lazy-ptt-enhancer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/ tests/
ruff check src/ tests/

# Type check
mypy src/
```

### Code Style

- **Formatter**: Black (line length 100)
- **Linter**: Ruff (all rules except D)
- **Type Checker**: Mypy (strict mode)
- **Docstrings**: Google style
- **Imports**: isort (Black-compatible)

### PR Process

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Run tests (`pytest tests/`)
5. Format code (`black src/ tests/`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request with description

---

## License

MIT License

Copyright (c) 2025 @therouxe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

**lazy-ptt-enhancer** - Voice-powered development workflows
Created by [@therouxe](https://github.com/therouxe)
[⭐ Star on GitHub](https://github.com/therouxe/lazy-ptt-enhancer) | [📖 Documentation](https://github.com/therouxe/lazy-ptt-enhancer#readme) | [🐛 Report Issues](https://github.com/therouxe/lazy-ptt-enhancer/issues)
