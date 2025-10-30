# lazy-ptt-enhancer

> **Voice-powered development workflows** - Push-to-talk → Whisper transcription → AI enhancement → Instant feature specifications

[![PyPI version](https://badge.fury.io/py/lazy-ptt-enhancer.svg)](https://badge.fury.io/py/lazy-ptt-enhancer)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Transform voice into detailed development specifications in seconds.**

Press F12 → Speak your feature brief → Release → Get enhanced prompt with objectives, risks, acceptance criteria, and more.

---

## 🎯 What is This?

**lazy-ptt-enhancer** is a globally-installable voice-to-prompt toolkit that:

1. **Captures your voice** via push-to-talk (F12 default)
2. **Transcribes locally** with GPU-accelerated Whisper (offline capable)
3. **Enhances with AI** using OpenAI into structured specifications
4. **Saves to your workspace** - Prompts appear directly in `project-management/prompts/`
5. **Works everywhere** - Install once, use in any project directory

**No copy-paste. No context switching. Just speak and code.**

---

## ⚡ Quick Start (5 Minutes)

### 1. Install Globally

```bash
pip install lazy-ptt-enhancer
```

### 2. Initialize in Your Project

```bash
cd ~/my-awesome-project
lazy-ptt init
```

This will:
- ✅ Check dependencies (Python, audio devices, etc.)
- ✅ Create `project-management/prompts/` directory
- ✅ Generate `.env` configuration template
- ✅ Download Whisper model (optional)

### 3. Configure API Key

```bash
# Edit .env file
OPENAI_API_KEY=sk-your-actual-api-key
```

### 4. Start Daemon (Always-On Mode)

```bash
lazy-ptt daemon --verbose-cycle
```

### 5. Use Voice Input Anytime

- Press **F12**
- Say: *"Add user authentication with OAuth2 and session management"*
- Release **F12**

**Result**: Enhanced prompt saved to `./project-management/prompts/PROMPT-{timestamp}.md`

```markdown
# FEATURE Plan

**Summary**: Add user authentication with OAuth2 and session management

## Objectives
- Implement OAuth2 authentication flow
- Add JWT-based session management
- Create user profile management

## Acceptance Criteria
- [ ] Users can sign in with Google/GitHub
- [ ] Sessions persist across browser restarts
- [ ] Users can view and edit their profile

---

🎤 Generated with lazy-ptt-enhancer by @therouxe
```

---

## 🚀 Features

### Core Features

- ✅ **Global installation** - Install once with pip, use anywhere
- ✅ **Per-project initialization** - `lazy-ptt init` in any directory
- ✅ **Push-to-talk audio capture** - F12 (configurable via CLI)
- ✅ **Local Whisper transcription** - GPU-accelerated, offline capable
- ✅ **AI prompt enhancement** - Structured output with objectives, risks, criteria
- ✅ **Workspace-aware storage** - Saves to current directory's `project-management/prompts/`
- ✅ **Auto-move by default** - No staging folder (configurable via `--no-auto-move`)
- ✅ **Always-on daemon mode** - Background process for any project
- ✅ **Claude Code integration** - Designed for plugin compatibility
- ✅ **Branded output** - Attribution to @therouxe in all generated prompts

### Advanced Features

- ⚡ **GPU acceleration** - CUDA support for faster transcription
- 🌐 **Multi-language** - Transcribe in English, Spanish, French, German, etc.
- 🎛️ **Fully configurable** - Environment variables, CLI flags, or YAML config
- 🔒 **Privacy-first** - Whisper runs locally, only enhancement hits API
- 📊 **Metadata tracking** - JSON metadata alongside each prompt
- 🔌 **REST API** - FastAPI server for non-Python clients
- 🎚️ **Device selection** - Choose your microphone with `lazy-ptt devices`

---

## 📦 Installation

### Prerequisites

- **Python 3.9+** (3.11+ recommended)
- **PortAudio** (for audio capture)
  - macOS: `brew install portaudio`
  - Debian/Ubuntu: `sudo apt-get install libportaudio2`
  - Windows: Included with pip packages
- **CUDA Toolkit** (optional, for GPU acceleration)
- **OpenAI API Key** (for prompt enhancement)

### Install Package

```bash
# Using pip (recommended)
pip install lazy-ptt-enhancer

# Or using uv (faster)
uv pip install lazy-ptt-enhancer

# Verify installation
lazy-ptt --help
```

### First-Time Setup in a Project

```bash
cd ~/my-project
lazy-ptt init

# This creates:
# - project-management/prompts/ directory
# - .lazy-ptt/staging/ directory
# - .env configuration template
# - Downloads Whisper model (optional)
```

### Configure Environment

Edit the generated `.env` file:

```bash
# REQUIRED
OPENAI_API_KEY=sk-your-key

# OPTIONAL (defaults shown)
WHISPER_MODEL_SIZE=medium
WHISPER_DEVICE=auto
PTT_HOTKEY=<f12>
```

---

## 🎤 Usage

### Mode 1: Always-On Daemon (Recommended)

Run once per work session:

```bash
lazy-ptt daemon --verbose-cycle
```

**Then press F12 anytime to capture voice input in ANY directory.**

Output:
```
🎤 Daemon started. Press <f12> to capture voice anytime.
Auto-move: ✅ ENABLED (saves to project-management)
Working directory: /home/user/my-project

[✅ project-management] Prompt: ./project-management/prompts/PROMPT-20251030.md (FEATURE)
```

**Tip**: The daemon works across all projects. Change directories and press F12 - prompts save to the new directory's `project-management/`.

---

### Mode 2: Single Voice Capture

Capture one voice input and exit:

```bash
lazy-ptt listen
```

**Press F12, speak, release F12.**

Output:
```
Push-to-talk active. Hold the configured hotkey, speak, and release to process.
Prompt saved to: ./project-management/prompts/PROMPT-20251030-143022.md
✅ Prompt saved to project-management workspace (auto-move enabled)
Detected work type: FEATURE
Summary: Add payment processing with Stripe integration
```

**Disable auto-move** (keep in staging):
```bash
lazy-ptt listen --no-auto-move
```

---

### Mode 3: Enhance Text Brief (No Voice)

Have a text brief already? Enhance it directly:

```bash
lazy-ptt enhance-text --text "Add payment processing with Stripe"
```

Or from a file:

```bash
lazy-ptt enhance-text --file brief.txt
```

---

### Mode 4: Process Existing Audio File

Already have a recording?

```bash
lazy-ptt process-audio recording.wav
```

Supports: `.wav`, `.mp3`, `.flac`, `.ogg`

---

## 🔧 Configuration

### CLI Flags (Highest Priority)

All settings configurable via CLI:

```bash
# Disable auto-move (keep in staging)
lazy-ptt listen --no-auto-move

# Custom story ID
lazy-ptt listen --story-id US-3.4 --story-title "User Authentication"

# Verbose logging
lazy-ptt daemon --verbose-cycle
```

### Environment Variables (Medium Priority)

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional (defaults shown)
export WHISPER_MODEL_SIZE=medium  # tiny, base, small, medium, large
export WHISPER_DEVICE=auto        # auto, cpu, cuda
export PTT_HOTKEY="<f12>"
export PROJECT_MANAGEMENT_ROOT=./project-management
export PTT_OUTPUT_ROOT=./project-management/prompts

# Branding Configuration
export BRANDING_ENABLED=true      # Enable/disable footer branding
export BRANDING_EMOJI="🎤"        # Emoji in footer
export BRANDING_AUTHOR="@therouxe"  # Author attribution
export BRANDING_REPO_URL="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer"
export BRANDING_AUTHOR_URL="https://github.com/therouxe"
```

### YAML Config (Lowest Priority)

Create `.lazy-ptt.yaml` in project root (optional):

```yaml
openai:
  api_key: ${OPENAI_API_KEY}  # Reference env vars
  model: gpt-4
  temperature: 0.7

whisper:
  model_size: medium
  language: en
  device: auto

ptt:
  hotkey: "<f12>"
  output_root: project-management/prompts

paths:
  project_management_root: ./project-management

branding:
  enabled: true
  emoji: "🎤"
  author: "@therouxe"
  repo_url: "https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer"
  author_url: "https://github.com/therouxe"
```

### Branding Configuration

Control the footer attribution in generated prompts:

**Default Behavior**: All prompts include a branded footer with attribution to @therouxe and links to the repository.

**Disable Branding**: To remove the footer entirely:

```bash
# Via environment variable
export BRANDING_ENABLED=false

# Via YAML config
branding:
  enabled: false
```

**Customize Branding**: Modify the footer for forked/custom versions:

```yaml
branding:
  enabled: true
  emoji: "🚀"                    # Change emoji (or use "" for none)
  author: "@yourname"            # Your GitHub username
  repo_url: "https://github.com/yourname/your-fork"
  author_url: "https://github.com/yourname"
```

**Example Custom Footer Output**:

```markdown
---

🚀 **Generated with [lazy-ptt-enhancer](https://github.com/yourname/your-fork)**
Created by [@yourname](https://github.com/yourname) | Powered by Whisper + OpenAI
[⭐ Star on GitHub](https://github.com/yourname/your-fork) | [📖 Documentation](https://github.com/yourname/your-fork#readme) | [🐛 Report Issues](https://github.com/yourname/your-fork/issues)
```

---

## 🎛️ CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `lazy-ptt init` | Initialize lazy-ptt in current directory |
| `lazy-ptt listen` | Capture single voice input |
| `lazy-ptt enhance-text` | Enhance text brief (no voice) |
| `lazy-ptt process-audio` | Transcribe + enhance audio file |
| `lazy-ptt daemon` | Run always-on background listener |
| `lazy-ptt devices` | List available microphones |
| `lazy-ptt --help` | Show help message |

### Common Flags

```bash
--no-auto-move           # Keep in staging (auto-move is DEFAULT)
--story-id ID            # Override story ID (default: auto-generate)
--story-title "Title"    # Add story title metadata
--verbose                # Enable verbose logging
--verbose-cycle          # Log each daemon capture cycle
--no-download            # Skip Whisper model download (init only)
```

### Examples

```bash
# Initialize in new project
cd ~/new-project
lazy-ptt init

# List available microphones
lazy-ptt devices

# Start daemon with verbose output
lazy-ptt daemon --verbose-cycle

# Capture voice with metadata
lazy-ptt listen --story-id US-3.4 --story-title "User Authentication"

# Enhance text brief
lazy-ptt enhance-text --text "Fix login timeout bug"

# Process pre-recorded audio
lazy-ptt process-audio demo.wav

# Keep prompt in staging (disable auto-move)
lazy-ptt listen --no-auto-move
```

---

## 🔌 Claude Code Integration

### Pattern 1: Standalone Daemon (Simplest)

**Terminal 1** (run once per session):
```bash
lazy-ptt daemon --verbose-cycle
```

**Terminal 2** (use Claude Code):
```bash
cd ~/my-project
claude-code

# Voice workflow:
# 1. Press F12 anywhere, say "Add OAuth2 authentication"
# 2. Release F12
# 3. Prompt auto-saved to ./project-management/prompts/
# 4. In Claude Code: /lazy create-feature project-management/prompts/PROMPT-{timestamp}.md
```

---

### Pattern 2: Plugin Command

Add to your plugin's `.claude/commands/voice.md`:

```markdown
# /voice - Capture voice input

## Implementation

```bash
lazy-ptt listen --verbose

# Get the last prompt path
PROMPT_PATH=$(ls -t project-management/prompts/PROMPT-*.md | head -1)

echo "✅ Prompt saved to: $PROMPT_PATH"
echo "Next: /lazy create-feature $PROMPT_PATH"
```
```

Usage in Claude Code:
```bash
/voice
# → Press F12, speak
# → Prompt auto-saved
# → Follow suggested command to create feature
```

---

### Pattern 3: Background Daemon (Production)

Run daemon as systemd service (Linux):

```bash
# Copy service file
sudo cp ops/systemd/lazy-ptt-daemon.service /etc/systemd/system/

# Edit paths and environment
sudo nano /etc/systemd/system/lazy-ptt-daemon.service

# Enable and start
sudo systemctl enable lazy-ptt-daemon
sudo systemctl start lazy-ptt-daemon
sudo systemctl status lazy-ptt-daemon
```

Or launchd (macOS):

```bash
# Copy plist
cp ops/launchd/io.lazy.ptt.daemon.plist ~/Library/LaunchAgents/

# Edit paths
nano ~/Library/LaunchAgents/io.lazy.ptt.daemon.plist

# Load and start
launchctl load ~/Library/LaunchAgents/io.lazy.ptt.daemon.plist
launchctl start io.lazy.ptt.daemon
```

**See [CLAUDE_CODE_INTEGRATION.md](./CLAUDE_CODE_INTEGRATION.md) for complete integration guide.**

---

## 🌐 REST API (Optional)

Run the API server:

```bash
lazy-ptt-api  # Serves on http://127.0.0.1:8000
```

### Endpoints

```bash
# Enhance text
curl -X POST http://127.0.0.1:8000/enhance-text \
  -H 'Content-Type: application/json' \
  -d '{"text":"Add OAuth2 authentication"}' | jq .

# Process audio file
curl -X POST http://127.0.0.1:8000/process-audio \
  -F 'audio=@recording.wav' | jq .

# Trigger PTT capture (requires active desktop session)
curl -X POST http://127.0.0.1:8000/listen-once | jq .
```

---

## 🛠️ Troubleshooting

### Issue: `lazy-ptt` command not found

**Solution**:
```bash
pip install lazy-ptt-enhancer
which lazy-ptt  # Verify installation
```

### Issue: No audio input detected

**Solution**:
```bash
# List available audio devices
lazy-ptt devices

# Select device by index
PTT_INPUT_DEVICE_INDEX=1 lazy-ptt listen
```

### Issue: OpenAI API key not found

**Solution**:
```bash
# Set in environment
export OPENAI_API_KEY=sk-...

# Or create .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue: Whisper model download fails

**Solution**:
```bash
# Install faster-whisper
pip install faster-whisper

# Or skip download during init
lazy-ptt init --no-download
```

### Issue: CUDA out of memory

**Solution**:
```bash
# Use smaller Whisper model
export WHISPER_MODEL_SIZE=small  # or base, tiny

# Or force CPU mode
export WHISPER_DEVICE=cpu
```

### Issue: Prompts not saving to project-management

**Solution**:
```bash
# Check working directory
pwd

# Auto-move is DEFAULT, but verify:
lazy-ptt daemon --verbose-cycle  # Should show "Auto-move: ✅ ENABLED"

# If needed, re-initialize
lazy-ptt init
```

---

## 📖 Documentation

- **[README.md](./README.md)** (this file) - User guide and quick start
- **[CLAUDE_CODE_INTEGRATION.md](./CLAUDE_CODE_INTEGRATION.md)** - Plugin integration patterns
- **[DEV_SPEC.md](./DEV_SPEC.md)** - Development specification and roadmap
- **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** - Current implementation status
- **[examples/EXAMPLE_OUTPUT.md](./examples/EXAMPLE_OUTPUT.md)** - Sample branded output
- **[docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** - Detailed troubleshooting

---

## 🚦 Roadmap

### v1.0.0 (Q1 2025) - Production Release ✅
- ✅ Global pip install workflow
- ✅ Per-project initialization (`lazy-ptt init`)
- ✅ Auto-move by default (configurable)
- ✅ Push-to-talk audio capture
- ✅ Local Whisper transcription
- ✅ AI prompt enhancement
- ✅ Always-on daemon mode
- ✅ REST API server
- ✅ Branding footer
- ✅ systemd/launchd service configs

### v1.1.0 (Q2 2025) - Local Models
- Local LLM support (Ollama, llama.cpp)
- Custom enhancement profiles (security, marketing, etc.)
- Profile hot-reload

### v1.2.0 (Q2 2025) - Multi-Language
- Multi-language transcription (auto-detect)
- Multi-language enhancement (French, Spanish, German, etc.)

### v2.0.0 (Q3 2025) - Desktop UI
- Qt/Electron desktop app
- Live audio levels + transcription preview
- Session history browser
- Visual configuration editor

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer.git
cd STT-Devellopement-Prompt-Enhancer
python -m venv .venv
source .venv/bin/activate
pip install -e ".[api,ui,stt]"
pytest tests/
```

### Code Style

- **Formatter**: Black (line length 100)
- **Linter**: Ruff
- **Type Checker**: Mypy (planned)
- **Docstrings**: Google style

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details.

Copyright (c) 2025 [@therouxe](https://github.com/therouxe)

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - Fast, accurate speech recognition
- **faster-whisper** - GPU-accelerated Whisper implementation
- **OpenAI API** - Powerful prompt enhancement
- **Claude Code** - AI-assisted development workflows

---

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer/issues)
- **Documentation**: [Complete guides](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer#readme)
- **Twitter/X**: [@therouxe](https://twitter.com/therouxe)

---

**lazy-ptt-enhancer** - Voice-powered development workflows
Created by [@therouxe](https://github.com/therouxe)

[⭐ Star on GitHub](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer) | [📖 Documentation](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer#readme) | [🐛 Report Issues](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer/issues)
