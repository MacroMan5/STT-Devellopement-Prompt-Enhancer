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

**lazy-ptt-enhancer** is a voice-to-prompt toolkit that:

1. **Captures your voice** via push-to-talk (F12 default)
2. **Transcribes locally** with GPU-accelerated Whisper (offline capable)
3. **Enhances with AI** using OpenAI (or local models) into structured specifications
4. **Saves to your workspace** - Prompts appear directly in `project-management/prompts/`
5. **Integrates with Claude Code** - Works seamlessly with AI-assisted development workflows

**No copy-paste. No context switching. Just speak and code.**

---

## ⚡ Quick Start (5 Minutes)

### 1. Install

```bash
pip install lazy-ptt-enhancer
```

### 2. Configure

```bash
export OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

### 3. Start Daemon (Always-On Mode)

```bash
lazy-ptt daemon --verbose-cycle
```

### 4. Use Voice Input Anytime

- Press **F12**
- Say: *"Add user authentication with OAuth2 and session management"*
- Release **F12**

**Result**: Enhanced prompt saved to `project-management/prompts/PROMPT-{timestamp}.md`

```markdown
# FEATURE Plan

**Summary**: Add user authentication with OAuth2 and session management

## Objectives
- Implement OAuth2 authentication flow
- Add JWT-based session management
- Create user profile management

## Risks & Unknowns
- Third-party OAuth provider availability
- Token refresh strategy complexity

## Acceptance Criteria
- [ ] Users can sign in with Google/GitHub
- [ ] Sessions persist across browser restarts
- [ ] Users can view and edit their profile

## Original Brief
> Add user authentication with OAuth2 and session management

---

🎤 Generated with lazy-ptt-enhancer by @therouxe
```

---

## 🚀 Features

### Core Features

- ✅ **Push-to-talk audio capture** - F12 (or custom hotkey)
- ✅ **Local Whisper transcription** - GPU-accelerated, offline capable
- ✅ **AI prompt enhancement** - Structured output with objectives, risks, criteria
- ✅ **Workspace-aware storage** - Prompts saved directly to project directories
- ✅ **Always-on daemon mode** - Background process waiting for voice input
- ✅ **Claude Code integration** - Designed for plugin compatibility
- ✅ **Branded output** - Attribution to @therouxe in all generated prompts
- ✅ **Multi-format support** - Works with voice, text briefs, or audio files

### Advanced Features

- ⚡ **GPU acceleration** - CUDA support for faster transcription
- 🌐 **Multi-language** - Transcribe in English, Spanish, French, German, etc.
- 🎛️ **Configurable** - Environment variables, YAML config, or Python API
- 🔒 **Privacy-first** - Whisper runs locally, only enhancement hits API
- 📊 **Metadata tracking** - JSON metadata alongside each prompt
- 🎨 **Custom profiles** - Different enhancement styles (security, marketing, etc.)

---

## 📦 Installation

### Prerequisites

- **Python 3.9+** (3.11+ recommended)
- **CUDA Toolkit** (optional, for GPU acceleration)
- **OpenAI API Key** (for prompt enhancement)

### Install Package

```bash
# Using pip
pip install lazy-ptt-enhancer

# Or using uv (recommended for Claude Code projects)
uv pip install lazy-ptt-enhancer

# Verify installation
lazy-ptt --help
```

### First-Time Setup

```bash
# Initialize configuration
lazy-ptt init

# This will:
# 1. Check dependencies (Python, CUDA, audio devices)
# 2. Create .env template
# 3. Create .lazy-ptt.yaml config
# 4. Download Whisper model (first run only)
# 5. Test audio capture
```

---

## 🎤 Usage

### Mode 1: Always-On Daemon (Recommended)

Run once per work session:

```bash
lazy-ptt daemon --verbose-cycle
```

**Then press F12 anytime to capture voice input.**

Output:
```
🎤 Daemon started. Press F12 to capture voice anytime.
Hotkey: F12
Staging: .lazy-ptt/staging
Auto-move: enabled

[2025-10-29 14:30:45] Waiting for hotkey...
[2025-10-29 14:30:48] Recording...
[2025-10-29 14:30:52] Transcribing...
[2025-10-29 14:30:55] Enhancing...
[2025-10-29 14:30:58] ✅ Prompt saved: project-management/prompts/PROMPT-20251029-143058.md (FEATURE)
[2025-10-29 14:30:58] Waiting for hotkey...
```

---

### Mode 2: Single Voice Capture

Capture one voice input and exit:

```bash
lazy-ptt listen --auto-move
```

**Press F12, speak, release F12.**

Output:
```
🎤 Press F12 to start recording...
🔴 Recording... (release F12 to stop)
✅ Audio captured (3.2s)
🔄 Transcribing with Whisper...
✅ Transcription: "Add payment processing with Stripe"
🔄 Enhancing with OpenAI...
✅ Enhanced prompt generated
📄 Prompt saved to: project-management/prompts/PROMPT-20251029-143022.md

Work Type: FEATURE
Summary: Add payment processing with Stripe integration
```

---

### Mode 3: Enhance Text Brief (No Voice)

Have a text brief already? Enhance it directly:

```bash
lazy-ptt enhance-text --text "Add payment processing with Stripe" --auto-move
```

Or from a file:

```bash
lazy-ptt enhance-text --file brief.txt --auto-move
```

---

### Mode 4: Process Existing Audio File

Already have a recording?

```bash
lazy-ptt process-audio recording.wav --auto-move
```

Supports: `.wav`, `.mp3`, `.flac`, `.ogg`

---

## 🔧 Configuration

### Environment Variables (Quickest)

```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional (defaults shown)
export OPENAI_MODEL=gpt-4
export WHISPER_MODEL=medium  # tiny, base, small, medium, large
export PTT_HOTKEY="<f12>"
export PROJECT_MANAGEMENT_ROOT=./project-management
```

### YAML Config (Recommended)

Create `.lazy-ptt.yaml` in your project root:

```yaml
openai:
  api_key: ${OPENAI_API_KEY}  # Reference env vars
  model: gpt-4
  temperature: 0.7

whisper:
  model: medium  # tiny, base, small, medium, large
  language: en   # or "auto" for auto-detect
  device: auto   # auto, cpu, cuda

audio:
  sample_rate: 16000
  channels: 1

hotkey:
  trigger: "<f12>"

paths:
  project_management_root: ./project-management
  staging_dir: ./.lazy-ptt/staging

branding:
  enabled: true
  attribution: "Generated with lazy-ptt-enhancer by @therouxe"
  github_url: "https://github.com/therouxe/lazy-ptt-enhancer"
```

### Python API (Advanced)

```python
from lazy_ptt import PTTService, AppConfig, load_config

# Load from environment + YAML
config = load_config()
service = PTTService.from_config(config)

# Capture voice input
outcome = service.listen_once(auto_move=True)
print(f"Prompt: {outcome.saved_prompt.prompt_path}")

# Enhance text directly
outcome = service.enhance_text("Add user auth", auto_move=True)
```

---

## 🎛️ CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `lazy-ptt init` | First-time setup wizard |
| `lazy-ptt listen` | Capture single voice input |
| `lazy-ptt enhance-text` | Enhance text brief (no voice) |
| `lazy-ptt process-audio` | Transcribe + enhance audio file |
| `lazy-ptt daemon` | Run always-on background listener |
| `lazy-ptt status` | Show diagnostics and last prompt |
| `lazy-ptt --help` | Show help message |

### Common Options

```bash
--auto-move              # Move prompt to project-management immediately
--story-id ID            # Override story ID (default: auto-generate)
--story-title "Title"    # Add story title metadata
--verbose                # Enable verbose logging
--json                   # Output JSON (for scripting)
```

### Examples

```bash
# Capture voice with metadata
lazy-ptt listen --story-id US-3.4 --story-title "User Authentication" --auto-move

# Enhance text brief
lazy-ptt enhance-text --text "Fix login timeout bug" --auto-move

# Process pre-recorded audio
lazy-ptt process-audio demo.wav --auto-move

# Run daemon with verbose output
lazy-ptt daemon --verbose-cycle

# Check status
lazy-ptt status --last-prompt --stats
```

---

## 🔌 Claude Code Integration

### Pattern 1: Standalone Daemon

**Terminal 1** (run once per session):
```bash
lazy-ptt daemon --verbose-cycle
```

**Terminal 2** (use Claude Code):
```bash
claude-code

# Voice workflow:
# 1. Press F12, say "Add OAuth2 authentication"
# 2. Release F12
# 3. In Claude Code: /lazy create-feature project-management/prompts/PROMPT-{timestamp}.md
```

---

### Pattern 2: Plugin Command

Add to your plugin's `.claude/commands/voice.md`:

```markdown
# /voice - Capture voice input

## Implementation

```bash
lazy-ptt listen --auto-move --verbose

PROMPT_PATH=$(lazy-ptt status --last-prompt)
echo "✅ Prompt saved to: $PROMPT_PATH"
echo "Next: /lazy create-feature $PROMPT_PATH"
```
```

Usage in Claude Code:
```bash
/voice
# → Press F12, speak
# → Prompt auto-saved
# → Run suggested command to create feature
```

---

### Pattern 3: Hook-Based Automation

Create `.claude/hooks/voice-detector.py`:

```python
#!/usr/bin/env python3
import json, subprocess, sys

hook_input = json.load(sys.stdin)
user_prompt = hook_input.get("userPrompt", "")

if user_prompt.strip().lower() == "!voice":
    result = subprocess.run(["lazy-ptt", "listen", "--auto-move"], capture_output=True, text=True)
    # Parse prompt path and inject into conversation
    # ... (see CLAUDE_CODE_INTEGRATION.md for full example)

json.dump(hook_input, sys.stdout)
```

Register in `.claude/settings.json`:
```json
{
  "hooks": {
    "userPromptSubmit": [{"command": "python .claude/hooks/voice-detector.py"}]
  }
}
```

**See [CLAUDE_CODE_INTEGRATION.md](./CLAUDE_CODE_INTEGRATION.md) for complete integration guide.**

---

## 📖 Documentation

- **[README.md](./README.md)** (this file) - Overview and quick start
- **[CLAUDE_CODE_INTEGRATION.md](./CLAUDE_CODE_INTEGRATION.md)** - How to wire CLI into Claude Code plugins
- **[DEV_SPEC.md](./DEV_SPEC.md)** - Development specification and architecture
- **[examples/EXAMPLE_OUTPUT.md](./examples/EXAMPLE_OUTPUT.md)** - Sample branded output

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
python -c "import sounddevice; print(sounddevice.query_devices())"

# Set device index in environment
export AUDIO_DEVICE_INDEX=1
```

### Issue: OpenAI API key not found

**Solution**:
```bash
export OPENAI_API_KEY=sk-...

# Or create .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue: Whisper model download fails

**Solution**:
```bash
# Manually download model
python -c "from faster_whisper import WhisperModel; WhisperModel('medium')"
```

### Issue: Daemon stops responding

**Solution**:
```bash
# Check process
ps aux | grep lazy-ptt

# Kill and restart
pkill -f lazy-ptt
lazy-ptt daemon --verbose-cycle
```

### Issue: CUDA out of memory

**Solution**:
```bash
# Use smaller Whisper model
export WHISPER_MODEL=small  # or base, tiny

# Or force CPU mode
export WHISPER_DEVICE=cpu
```

---

## 🚦 Roadmap

### v1.0.0 (Q1 2025) - MVP Release ✅
- ✅ Core features (audio capture, transcription, enhancement)
- ✅ CLI commands (listen, enhance-text, process-audio, daemon)
- ⏳ Branding system (in progress)
- ⏳ Init/status commands
- ⏳ Cross-platform support (Windows, macOS, Linux)
- ⏳ 80% test coverage
- ⏳ Complete documentation

### v1.1.0 (Q2 2025) - Local Models
- Local LLM support (Ollama, llama.cpp)
- Custom enhancement profiles (security, marketing, etc.)
- Profile hot-reload

### v1.2.0 (Q2 2025) - Multi-Language
- Multi-language transcription (auto-detect)
- Multi-language enhancement (French, Spanish, German, etc.)

### v1.3.0 (Q3 2025) - REST API
- FastAPI REST API wrapper
- API key authentication
- Docker deployment

### v2.0.0 (Q4 2025) - Desktop UI
- Qt/Electron desktop app
- Live audio levels + transcription preview
- Session history browser

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/therouxe/lazy-ptt-enhancer.git
cd lazy-ptt-enhancer
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

### Code Style

- **Formatter**: Black (line length 100)
- **Linter**: Ruff
- **Type Checker**: Mypy
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

- **GitHub Issues**: [Report bugs or request features](https://github.com/therouxe/lazy-ptt-enhancer/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/therouxe/lazy-ptt-enhancer/discussions)
- **Twitter/X**: [@therouxe](https://twitter.com/therouxe)

---

**lazy-ptt-enhancer** - Voice-powered development workflows
Created by [@therouxe](https://github.com/therouxe)

[⭐ Star on GitHub](https://github.com/therouxe/lazy-ptt-enhancer) | [📖 Documentation](https://github.com/therouxe/lazy-ptt-enhancer#readme) | [🐛 Report Issues](https://github.com/therouxe/lazy-ptt-enhancer/issues)
