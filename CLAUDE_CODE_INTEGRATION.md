# Claude Code Integration Guide

> **How to wire lazy-ptt-enhancer CLI + daemon into Claude Code plugins**

Version: 1.0.0
Status: Production Ready
License: MIT

---

## Overview

**lazy-ptt-enhancer** is a voice-to-prompt toolkit that integrates seamlessly with Claude Code workflows. This guide shows how to wire the CLI and daemon into your Claude Code plugins.

### Key Features

- ✅ **Always-on daemon** waiting for push-to-talk activation
- ✅ **Local Whisper transcription** (GPU-accelerated, offline-capable)
- ✅ **AI prompt enhancement** (OpenAI API or local models)
- ✅ **Workspace-aware** - Generates prompts in your working repository
- ✅ **Zero-copy workflow** - Prompts saved directly to project-management/
- ✅ **Branded output** - Generated prompts include attribution

---

## Quick Start

### 1. Install the Package

```bash
# Install from PyPI (once published)
pip install lazy-ptt-enhancer

# Or with uv (recommended for Claude Code projects)
uv pip install lazy-ptt-enhancer

# Verify installation
lazy-ptt --help
```

### 2. Configure Environment

Create `.env` in your project root:

```bash
# Required: OpenAI API for enhancement (or use local model)
OPENAI_API_KEY=sk-...

# Optional: Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=medium

# Optional: Hotkey configuration (default: F12)
PTT_HOTKEY=<f12>

# Optional: Audio device (auto-detect by default)
AUDIO_DEVICE_INDEX=0

# Optional: Working directory for prompts (auto-detect project root)
PROJECT_MANAGEMENT_ROOT=./project-management
```

### 3. Initialize in Your Workspace

```bash
# Initialize configuration
lazy-ptt init

# Start daemon (always-on, waiting for push-to-talk)
lazy-ptt daemon --verbose-cycle
```

**What happens:**
1. Daemon runs in background
2. Press F12 (or configured hotkey) to start recording
3. Speak your feature brief
4. Release F12 to stop recording
5. Auto-transcribes with Whisper (local)
6. Auto-enhances with OpenAI (or local model)
7. Saves enhanced prompt to `project-management/prompts/PROMPT-{timestamp}.md`
8. Ready for `/lazy create-feature` command

---

## Integration Patterns

### Pattern 1: Standalone Daemon (Recommended)

**Use case:** Always-on voice input for any project

```bash
# Terminal 1: Run daemon
lazy-ptt daemon --verbose-cycle

# Terminal 2: Use Claude Code normally
claude-code

# Voice workflow:
# 1. Press F12, say "Add user authentication with OAuth2"
# 2. Release F12
# 3. Daemon saves to project-management/prompts/PROMPT-20251029-143022.md
# 4. In Claude Code: /lazy create-feature project-management/prompts/PROMPT-20251029-143022.md
```

**Pros:**
- ✅ No plugin installation needed
- ✅ Works with any Claude Code project
- ✅ Can run daemon once for entire work session

**Cons:**
- ⚠️ Requires manual terminal management
- ⚠️ Two-step workflow (voice → then create-feature command)

---

### Pattern 2: Plugin Command Integration

**Use case:** Single-command voice-to-feature creation

Create `.claude/commands/voice.md` in your plugin:

```markdown
# /voice - Voice-to-prompt with AI enhancement

## Description
Capture voice input via push-to-talk, transcribe with Whisper, enhance with AI, and create feature.

## Usage
/voice [listen|daemon|status]

## Implementation

When invoked with `listen`:

1. Check if lazy-ptt is installed:
   ```bash
   if ! command -v lazy-ptt &> /dev/null; then
       echo "❌ lazy-ptt-enhancer not installed"
       echo "Install: pip install lazy-ptt-enhancer"
       exit 1
   fi
   ```

2. Capture and enhance voice input:
   ```bash
   # Capture voice, save to project-management
   lazy-ptt listen --auto-move --verbose

   # Extract prompt path from output
   PROMPT_PATH=$(lazy-ptt status --last-prompt)

   echo "✅ Prompt saved to: $PROMPT_PATH"
   echo ""
   echo "Next steps:"
   echo "1. Review the enhanced prompt"
   echo "2. Run: /lazy create-feature $PROMPT_PATH"
   ```

3. When invoked with `daemon`:
   ```bash
   echo "🎤 Starting always-on voice daemon..."
   echo "Press F12 to capture voice input anytime"
   echo "Prompts will be saved to project-management/prompts/"
   echo ""
   lazy-ptt daemon --verbose-cycle
   ```

4. When invoked with `status`:
   ```bash
   lazy-ptt status --last-prompt --stats
   ```

## Examples

**Capture single voice input:**
```bash
/voice listen
# → Press F12, speak, release
# → Prompt saved to project-management/prompts/PROMPT-{timestamp}.md
# → Run: /lazy create-feature {path}
```

**Start always-on daemon:**
```bash
/voice daemon
# → Daemon running, press F12 anytime to capture
```

## Requirements

- `lazy-ptt-enhancer` installed (`pip install lazy-ptt-enhancer`)
- `OPENAI_API_KEY` environment variable set
- Audio input device available
```

---

### Pattern 3: Hook-Based Automation (Advanced)

**Use case:** Automatic voice detection without explicit commands

Create `.claude/hooks/voice-detector.py`:

```python
#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Detect voice command trigger and capture audio.

Triggers when user types: "!voice" or "@voice"
"""
import json
import subprocess
import sys
from pathlib import Path


def main():
    # Read hook input
    hook_input = json.load(sys.stdin)
    user_prompt = hook_input.get("userPrompt", "")

    # Check for voice trigger
    if user_prompt.strip().lower() in ["!voice", "@voice", "/voice"]:
        print("🎤 Voice capture mode activated...", file=sys.stderr)

        # Capture voice input
        result = subprocess.run(
            ["lazy-ptt", "listen", "--auto-move"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Parse prompt path from output
            for line in result.stdout.split("\n"):
                if "Prompt saved to:" in line:
                    prompt_path = line.split(":")[-1].strip()

                    # Read the enhanced prompt
                    enhanced_content = Path(prompt_path).read_text()

                    # Replace user prompt with enhanced version
                    hook_input["userPrompt"] = (
                        f"Create a feature based on this enhanced prompt:\n\n"
                        f"{enhanced_content}\n\n"
                        f"Use /lazy create-feature to implement."
                    )
                    break
        else:
            hook_input["userPrompt"] = (
                f"❌ Voice capture failed: {result.stderr}\n"
                f"Make sure lazy-ptt is installed: pip install lazy-ptt-enhancer"
            )

    # Output modified hook data
    json.dump(hook_input, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
```

**Register hook in `.claude/settings.json`:**

```json
{
  "hooks": {
    "userPromptSubmit": [
      {
        "command": "python .claude/hooks/voice-detector.py"
      }
    ]
  }
}
```

**Usage:**
```
User types: !voice
Hook intercepts → Captures voice → Enhances prompt → Passes to Claude Code
```

---

## Daemon Configuration

### Basic Daemon Setup

```bash
# Run daemon in foreground (development)
lazy-ptt daemon --verbose-cycle

# Run daemon in background (production)
lazy-ptt daemon > /dev/null 2>&1 &
echo $! > ~/.lazy-ptt-daemon.pid

# Stop daemon
kill $(cat ~/.lazy-ptt-daemon.pid)
```

### Daemon with Custom Settings

```bash
# Keep prompts in staging (don't auto-move to project-management)
lazy-ptt daemon --stay-local

# Verbose output (log each capture)
lazy-ptt daemon --verbose-cycle

# Custom hotkey (via environment)
PTT_HOTKEY="<ctrl>+<alt>+v" lazy-ptt daemon
```

### Systemd Service (Linux)

Create `/etc/systemd/system/lazy-ptt.service`:

```ini
[Unit]
Description=lazy-ptt-enhancer daemon
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/your/project
Environment="OPENAI_API_KEY=sk-..."
Environment="PROJECT_MANAGEMENT_ROOT=/path/to/your/project/project-management"
ExecStart=/usr/local/bin/lazy-ptt daemon --verbose-cycle
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable lazy-ptt
sudo systemctl start lazy-ptt
sudo systemctl status lazy-ptt
```

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key for enhancement |
| `OPENAI_MODEL` | `gpt-4` | Model for prompt enhancement |
| `WHISPER_MODEL` | `medium` | Whisper model size (tiny/base/small/medium/large) |
| `PTT_HOTKEY` | `<f12>` | Push-to-talk hotkey |
| `AUDIO_DEVICE_INDEX` | auto | Audio input device index |
| `AUDIO_SAMPLE_RATE` | `16000` | Audio sample rate (Hz) |
| `AUDIO_CHANNELS` | `1` | Audio channels (mono) |
| `PROJECT_MANAGEMENT_ROOT` | `./project-management` | Where to save prompts |
| `PROMPT_STAGING_DIR` | `./.lazy-ptt/staging` | Temporary staging directory |

### Config File (Optional)

Create `.lazy-ptt.yaml` in project root:

```yaml
openai:
  api_key: ${OPENAI_API_KEY}
  model: gpt-4
  temperature: 0.7
  max_output_tokens: 2048

whisper:
  model: medium
  language: en
  device: auto  # auto, cpu, cuda

audio:
  sample_rate: 16000
  channels: 1
  device_index: null  # auto-detect

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

---

## Branded Output

All generated prompts include attribution:

```markdown
# FEATURE Plan

**Summary**: Add user authentication with OAuth2 and session management

## Objectives
- Implement OAuth2 authentication flow
- Add session management with JWT tokens
- Create user profile management

## Risks & Unknowns
- Third-party OAuth provider availability
- Token refresh strategy

## Acceptance Criteria
- [ ] Users can sign in with Google/GitHub
- [ ] Sessions persist across browser restarts
- [ ] Users can view and edit their profile

## Original Brief
> Add user authentication with OAuth2

---

🎤 **Generated with [lazy-ptt-enhancer](https://github.com/therouxe/lazy-ptt-enhancer)**
Created by [@therouxe](https://github.com/therouxe)
Powered by Whisper + OpenAI
```

---

## CLI Reference

### Commands

```bash
# Initialize configuration
lazy-ptt init [--config-path PATH]

# Capture single voice input
lazy-ptt listen [OPTIONS]
  --story-id ID           # Override story ID
  --story-title "Title"   # Story title metadata
  --auto-move             # Move to project-management immediately

# Enhance text brief directly
lazy-ptt enhance-text [OPTIONS]
  --text "Brief text"     # Text to enhance
  --file path/to/file.txt # Or read from file
  --story-id ID
  --auto-move

# Process existing audio file
lazy-ptt process-audio path/to/audio.wav [OPTIONS]
  --story-id ID
  --story-title "Title"
  --auto-move

# Move staged prompt to project-management
lazy-ptt create-feature path/to/prompt.md
  --story-title "Title"

# Run always-on daemon
lazy-ptt daemon [OPTIONS]
  --stay-local            # Keep in staging, don't auto-move
  --verbose-cycle         # Log each capture cycle

# Check status
lazy-ptt status
  --last-prompt           # Show path to last generated prompt
  --stats                 # Show usage statistics
```

---

## Integration Examples

### Example 1: LAZY_DEV Plugin

Add to your LAZY_DEV `.claude/commands/lazy.md`:

```markdown
## /lazy voice

**Description**: Capture voice input and enhance into detailed feature specification.

**Usage**:
```bash
/lazy voice listen
```

**Implementation**:
1. Run `lazy-ptt listen --auto-move`
2. Parse output to get prompt path
3. Suggest next command: `/lazy create-feature {path}`

**Requirements**:
- lazy-ptt-enhancer installed
- OPENAI_API_KEY set in environment
```

### Example 2: Auto-Feature Creation

Create `.claude/commands/voice-feature.md`:

```markdown
# /voice-feature - Voice to feature (one command)

## Description
Capture voice, enhance prompt, and immediately create feature in one command.

## Implementation

```bash
#!/bin/bash
set -e

echo "🎤 Press F12 to record your feature brief..."

# Capture voice and get prompt path
PROMPT_PATH=$(lazy-ptt listen --auto-move --json | jq -r '.prompt_path')

if [ -z "$PROMPT_PATH" ]; then
    echo "❌ Voice capture failed"
    exit 1
fi

echo "✅ Prompt captured and enhanced"
echo "📄 Prompt: $PROMPT_PATH"
echo ""
echo "🚀 Creating feature..."

# Automatically trigger create-feature
/lazy create-feature "$PROMPT_PATH"
```

## Examples

**Single command workflow:**
```bash
/voice-feature
# → Press F12, speak
# → Auto-creates user story + tasks
# → Ready to implement
```
```

### Example 3: Background Daemon + Manual Trigger

**Terminal 1 (run once per work session):**
```bash
lazy-ptt daemon --verbose-cycle
```

**Terminal 2 (use Claude Code normally):**
```bash
# Press F12 anytime to capture voice
# Daemon logs: "Prompt saved to: project-management/prompts/PROMPT-20251029.md"

# In Claude Code:
/lazy create-feature project-management/prompts/PROMPT-20251029.md
```

---

## Troubleshooting

### Issue: lazy-ptt command not found

**Solution:**
```bash
# Install package
pip install lazy-ptt-enhancer

# Or with uv
uv pip install lazy-ptt-enhancer

# Verify installation
which lazy-ptt
lazy-ptt --help
```

### Issue: No audio input detected

**Solution:**
```bash
# List available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Set device index in environment
export AUDIO_DEVICE_INDEX=1
```

### Issue: OpenAI API key not found

**Solution:**
```bash
# Set API key
export OPENAI_API_KEY=sk-...

# Or create .env file
echo "OPENAI_API_KEY=sk-..." > .env
```

### Issue: Daemon stops responding

**Solution:**
```bash
# Check daemon process
ps aux | grep lazy-ptt

# Kill and restart
pkill -f lazy-ptt
lazy-ptt daemon --verbose-cycle
```

### Issue: Prompts not appearing in project-management/

**Solution:**
```bash
# Check if auto-move is enabled
lazy-ptt listen --auto-move

# Or manually move from staging
lazy-ptt create-feature .lazy-ptt/staging/PROMPT-*.md
```

---

## Advanced Usage

### Local Model Support (No API Costs)

Use local LLM instead of OpenAI:

```bash
# Set local model endpoint
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_KEY=local-key
export OPENAI_MODEL=llama-3-70b

# Run daemon with local model
lazy-ptt daemon --verbose-cycle
```

### Multi-Language Support

```bash
# Spanish transcription
export WHISPER_LANGUAGE=es
lazy-ptt listen

# Auto-detect language
export WHISPER_LANGUAGE=auto
lazy-ptt daemon
```

### Custom Enhancement Profiles

Create `.lazy-ptt/profiles/security.yaml`:

```yaml
system_prompt: |
  You are a security architect. Transform briefs into security-focused specifications.
  Include threat modeling, attack vectors, and security requirements.
```

Use profile:

```bash
lazy-ptt listen --profile security
```

---

## Best Practices

### 1. Run Daemon in Background

```bash
# Start daemon when you start work
lazy-ptt daemon --verbose-cycle &

# Use voice input throughout the day without restarting
```

### 2. Use Auto-Move for Seamless Workflow

```bash
# Always use --auto-move to skip manual step
lazy-ptt listen --auto-move
```

### 3. Set Up Shell Alias

Add to `.bashrc` or `.zshrc`:

```bash
alias voice="lazy-ptt listen --auto-move"
alias voice-daemon="lazy-ptt daemon --verbose-cycle"
```

Usage:
```bash
voice
# → Quick voice capture
```

### 4. Integrate with Git Hooks

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Verify all prompts have corresponding features

PROMPTS=$(find project-management/prompts -name "PROMPT-*.md")
for prompt in $PROMPTS; do
    if ! grep -q "$(basename $prompt)" project-management/USER-STORY-*; then
        echo "⚠️  Orphaned prompt: $prompt"
        echo "Run: /lazy create-feature $prompt"
    fi
done
```

---

## Plugin Distribution

When distributing a Claude Code plugin that uses lazy-ptt-enhancer:

### 1. Add Dependency to plugin.json

```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "dependencies": {
    "python": [
      "lazy-ptt-enhancer>=1.0.0"
    ]
  },
  "install": {
    "hooks": ["install.sh"]
  }
}
```

### 2. Create Install Hook

Create `install.sh`:

```bash
#!/bin/bash
set -e

echo "Installing lazy-ptt-enhancer..."
pip install lazy-ptt-enhancer

echo "Verifying installation..."
if ! command -v lazy-ptt &> /dev/null; then
    echo "❌ Installation failed"
    exit 1
fi

echo "✅ lazy-ptt-enhancer installed successfully"
echo ""
echo "Next steps:"
echo "1. Set OPENAI_API_KEY in your environment"
echo "2. Run: lazy-ptt daemon --verbose-cycle"
echo "3. Press F12 to capture voice input anytime"
```

### 3. Document in Plugin README

```markdown
## Requirements

This plugin requires `lazy-ptt-enhancer` for voice input:

```bash
pip install lazy-ptt-enhancer
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=sk-...
```

Start the daemon:

```bash
lazy-ptt daemon --verbose-cycle
```

Press F12 anytime to capture voice input.
```

---

## License

MIT License - See [LICENSE](./LICENSE)

---

## Resources

- **GitHub Repository**: https://github.com/therouxe/lazy-ptt-enhancer
- **PyPI Package**: https://pypi.org/project/lazy-ptt-enhancer
- **Documentation**: https://github.com/therouxe/lazy-ptt-enhancer/docs
- **Issues**: https://github.com/therouxe/lazy-ptt-enhancer/issues

---

**lazy-ptt-enhancer** - Voice-powered development workflows
Created by [@therouxe](https://github.com/therouxe)
