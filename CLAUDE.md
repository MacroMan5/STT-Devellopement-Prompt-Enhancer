# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Context

**lazy-ptt-enhancer** is a globally-installable voice-to-prompt toolkit for AI-assisted development workflows. It captures voice input via push-to-talk, transcribes locally with Whisper, and enhances prompts using OpenAI's API.

**Key Workflow**: Press F12 → Speak → Release → Get enhanced prompt saved to `project-management/prompts/`

This is a **production-ready package** distributed via PyPI, not a template or framework.

---

## Architecture Overview

The codebase follows a service-oriented architecture with clear separation of concerns:

```
User (CLI/Daemon)
    ↓
PTTService (orchestrator)
    ↓
┌──────────────┬───────────────┬──────────────────┬─────────────────┐
│ AudioRecorder│ WhisperSTT    │ PromptEnhancer   │ PromptStorage   │
│ (sounddevice)│ (faster-whisper)│ (OpenAI API)   │ (filesystem)    │
└──────────────┴───────────────┴──────────────────┴─────────────────┘
```

### Core Components

1. **PTTService** (`services/ptt_service.py`)
   - Orchestrates the entire workflow
   - Coordinates audio → transcription → enhancement → storage
   - Factory method: `PTTService.from_config(config)`

2. **AudioRecorder** (`audio/recorder.py`)
   - Captures audio via push-to-talk using `sounddevice`
   - Returns `AudioBuffer` with raw audio data

3. **WhisperTranscriber** (`stt/whisper.py`)
   - Local transcription using `faster-whisper`
   - GPU-accelerated (CUDA) when available
   - Returns `TranscriptionResult` with text and metadata

4. **PromptEnhancer** (`prompt/enhancer.py`)
   - Enhances briefs using OpenAI Responses API
   - Structured JSON output → `EnhancedPrompt` dataclass
   - **IMPORTANT**: Uses `responses.create()` not `chat.completions.create()`
   - Includes branding footer in markdown output

5. **PromptStorage** (`prompt/manager.py`)
   - Saves prompts to staging directory with metadata JSON
   - `relocate_to_project_management()` moves to final location
   - Auto-generates story IDs if not provided

6. **PTTDaemon** (`services/daemon.py`)
   - Always-on background listener
   - Handles errors gracefully and continues
   - Supports `--verbose-cycle` for logging

### Configuration System

Configuration precedence (highest to lowest):
1. Environment variables (loaded via `python-dotenv`)
2. Built-in defaults (`lazy_ptt/data/defaults.yaml`)
3. Optional YAML config (`config/defaults.yaml`)

**Key Config Classes**:
- `AppConfig`: Top-level aggregate
- `ProjectPaths`: Filesystem locations
- `PTTConfig`: Audio and hotkey settings
- `WhisperConfig`: Whisper model settings
- `OpenAIConfig`: OpenAI API settings

**Required Environment Variable**:
```bash
OPENAI_API_KEY=sk-...  # MUST be set or ConfigError is raised
```

---

## Common Development Commands

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=lazy_ptt --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_prompt_enhancer.py

# Run with verbose output
pytest -v tests/
```

### Code Quality

```bash
# Format code (Black + Ruff)
black src/ tests/
ruff check src/ tests/ --fix

# Type checking (if mypy is configured)
mypy src/
```

### Local Development

```bash
# Install in editable mode with all extras
pip install -e ".[api,ui,stt]"

# Test the CLI locally
python -m lazy_ptt.cli --help
lazy-ptt --help  # If installed globally

# Run single command
lazy-ptt devices  # List audio devices
lazy-ptt init     # Initialize in current directory
```

### Building and Distribution

```bash
# Build package
python -m build

# Check distribution files
twine check dist/*

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

---

## Key Implementation Details

### OpenAI Responses API Usage

The `PromptEnhancer` uses OpenAI's **Responses API**, not the Chat Completions API:

```python
response = self.client.responses.create(
    model=self.config.model,
    temperature=self.config.temperature,
    max_output_tokens=self.config.max_output_tokens,
    response_format={"type": "json_object"},
    input=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": brief.strip()},
    ],
)
```

**Response extraction** (`_extract_text()` in `prompt/enhancer.py`):
- First tries `response.output[0].content[0].text`
- Falls back to `response.choices[0].message["content"]`
- This dual approach handles API variations

### Auto-Move Pattern

**Default behavior changed**: Auto-move is **enabled by default** (not staging-first):

```python
# CLI flag semantics
auto_move = not args.no_auto_move  # DEFAULT is True

# When auto_move=True:
# - Prompt saves to PTT_OUTPUT_ROOT
# - Immediately relocates to project-management/user-story-prompts/{story_id}/
# - Creates README.txt with story title

# When auto_move=False (--no-auto-move):
# - Prompt stays in PTT_OUTPUT_ROOT (staging)
# - User manually moves with `lazy-ptt create-feature`
```

### Branding Footer

All generated prompts include a footer with attribution:

```markdown
---

🎤 **Generated with [lazy-ptt-enhancer](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer)**
Created by [@therouxe](https://github.com/therouxe) | Powered by Whisper + OpenAI
[⭐ Star on GitHub](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer) | [📖 Documentation](...) | [🐛 Report Issues](...)
```

This is **hardcoded** in `EnhancedPrompt.to_markdown()` (lines 86-96 in `prompt/enhancer.py`).

### Story ID Generation

If no story ID is provided, the system auto-generates:

```python
# Format: US-{WORK_TYPE}-{TIMESTAMP}
# Example: US-FEATURE-20251030-143022
def _generate_story_id(self, work_type: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base = _slugify(work_type or "FEATURE").upper()
    return f"US-{base}-{timestamp}"
```

### Hotkey Listener Pattern

The hotkey listener (`input/hotkey.py`) uses callbacks:

```python
callbacks = HotkeyCallbacks(
    on_press=lambda: recorder.start(),
    on_release=lambda: process(recorder.stop())
)
hotkey_listener.start(callbacks)
hotkey_listener.join()  # Blocks until hotkey pressed
```

**Important**: Each `listen_once()` creates a **one-shot listener** that exits after press/release.

---

## Testing Strategy

### Test Structure

```
tests/
├── unit/              # Isolated component tests
│   ├── test_prompt_enhancer.py  # Mocks OpenAI client
│   ├── test_prompt_storage.py   # Filesystem operations
│   ├── test_ptt_service.py      # Service orchestration
│   └── test_daemon.py           # Daemon lifecycle
└── api/               # API endpoint tests
    └── test_api.py
```

### Key Testing Patterns

1. **Mock OpenAI Client** (in `test_prompt_enhancer.py`):
   ```python
   mock_client = Mock()
   mock_client.responses.create.return_value = mock_response
   enhancer = PromptEnhancer(config, client=mock_client)
   ```

2. **Temporary Directories**:
   ```python
   import tempfile
   with tempfile.TemporaryDirectory() as tmp:
       storage = PromptStorage(Path(tmp), ...)
   ```

3. **Daemon Testing** (in `test_daemon.py`):
   ```python
   daemon.request_stop()  # Graceful shutdown
   ```

### Running Single Tests

```bash
# Run specific test class
pytest tests/unit/test_prompt_enhancer.py::TestPromptEnhancer

# Run specific test method
pytest tests/unit/test_prompt_enhancer.py::TestPromptEnhancer::test_enhance_basic_brief

# Run with print output
pytest -s tests/unit/test_prompt_enhancer.py
```

---

## Common Gotchas

### 1. Windows Path Handling

Always use `pathlib.Path` for cross-platform compatibility:

```python
# Good
path = Path("project-management") / "prompts"

# Bad
path = "project-management/prompts"  # Fails on Windows
```

### 2. OpenAI API Key Required

Many commands will fail with `ConfigError` if `OPENAI_API_KEY` is not set:

```bash
# Set in .env file
OPENAI_API_KEY=sk-...

# Or export
export OPENAI_API_KEY=sk-...
```

### 3. Whisper Model Download

First run downloads the Whisper model (~1.5GB for "medium"):

```bash
# Pre-download during init
lazy-ptt init

# Or skip download and download on first use
lazy-ptt init --no-download
```

### 4. Audio Device Selection

If default microphone isn't detected:

```bash
# List devices
lazy-ptt devices

# Set device index
export PTT_INPUT_DEVICE_INDEX=1
lazy-ptt listen
```

### 5. Daemon vs. Listen Once

```bash
# Daemon: Runs forever, handles multiple captures
lazy-ptt daemon --verbose-cycle

# Listen: Single capture, then exits
lazy-ptt listen
```

---

## File Locations Reference

### Source Code
- **Entry point**: `src/lazy_ptt/cli.py` (CLI parser and command handlers)
- **Service layer**: `src/lazy_ptt/services/ptt_service.py`
- **Configuration**: `src/lazy_ptt/config.py`
- **Prompt enhancement**: `src/lazy_ptt/prompt/enhancer.py`
- **Storage**: `src/lazy_ptt/prompt/manager.py`
- **Daemon**: `src/lazy_ptt/services/daemon.py`

### Configuration
- **Package defaults**: `src/lazy_ptt/data/defaults.yaml` (if exists)
- **User config**: `.env` or `config/defaults.yaml` in project root
- **Environment**: `.env` loaded via `python-dotenv`

### Output Locations
- **Staging**: `{PTT_OUTPUT_ROOT}` (default: `./outputs/prompts/`)
- **Final**: `{PROJECT_MANAGEMENT_ROOT}/user-story-prompts/{story_id}/` (default: `./project-management/user-story-prompts/`)
- **Metadata**: `prompt-metadata.json` alongside each prompt

---

## Documentation Files

- **README.md**: User-facing guide (installation, usage, troubleshooting)
- **DEV_SPEC.md**: Complete technical specification and roadmap
- **CLAUDE_CODE_INTEGRATION.md**: Claude Code plugin integration patterns
- **PROJECT_STATUS.md**: Current implementation status and todos
- **SPRINT-*.md**: Sprint plans and task breakdowns

---

## Development Workflow

### Adding a New CLI Command

1. Add command parser in `cli.py::build_parser()`
2. Implement command handler function (e.g., `cmd_my_command()`)
3. Register in `COMMAND_HANDLERS` dict
4. Add tests in `tests/unit/test_cli.py` (if exists) or create new test file
5. Update `README.md` with command documentation

### Modifying Prompt Enhancement

1. Update `SYSTEM_PROMPT` in `prompt/enhancer.py`
2. Update `EnhancedPrompt` dataclass if adding fields
3. Update `to_markdown()` method to render new fields
4. Add tests to verify JSON parsing and markdown output

### Adding Configuration Options

1. Add to relevant config dataclass in `config.py` (e.g., `PTTConfig`, `OpenAIConfig`)
2. Update `load_config()` to read from environment
3. Update `.env` template in `cmd_init()` (in `cli.py`)
4. Document in `README.md` configuration section

---

## Code Style Guidelines

- **Formatter**: Black (line length 100)
- **Linter**: Ruff (pycodestyle + pyflakes)
- **Type hints**: Use `from __future__ import annotations` for forward references
- **Docstrings**: Google-style (brief, multi-line for complex functions)
- **Imports**: Standard library → Third-party → Local
- **Error handling**: Raise `ConfigError` for configuration issues

---

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if exists)
3. Run full test suite: `pytest tests/`
4. Build package: `python -m build`
5. Test install locally: `pip install dist/*.whl`
6. Upload to PyPI: `twine upload dist/*`
7. Create GitHub release with tag

---

## Related Projects

This project is **separate** from the `LAZY_DEV` framework mentioned in the root CLAUDE.md. This is the **STT_PROMPT_ENHANCER** standalone package, not the larger framework template.

- **Repository**: https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer
- **PyPI**: https://pypi.org/project/lazy-ptt-enhancer/
- **Author**: [@therouxe](https://github.com/therouxe)
