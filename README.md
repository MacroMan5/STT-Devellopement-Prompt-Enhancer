# Lazy PTT Enhancer — Push‑to‑Talk STT + Prompt Enhancement

A simple developer tool that lets you capture voice notes with a hotkey, transcribe them locally using Whisper, enhance them with an LLM into a structured plan, and save the result as Markdown + JSON. Designed to be pragmatic, fast, and easy to integrate into your workflow or automations.

- Audio capture: press/hold the hotkey to record; release to process.
- Local STT: faster‑whisper for transcription (GPU or CPU).
- Prompt enhancement: OpenAI Responses API shapes the plan as JSON → Markdown.
- Storage: saves under a staging folder and can copy into a project‑management workspace.


## Quick Start

1) Prerequisites
- Python 3.9+
- PortAudio runtime (for `sounddevice`)
  - macOS: `brew install portaudio`
  - Debian/Ubuntu: `sudo apt-get install -y libportaudio2`
- Optional `ffmpeg` for broader audio input
  - macOS: `brew install ffmpeg`
  - Debian/Ubuntu: `sudo apt-get install -y ffmpeg`
- Optional GPU for faster‑whisper
  - Recent NVIDIA driver + CUDA; otherwise set `WHISPER_DEVICE=cpu`

2) Install (local dev)
- Create a venv and install:
```
python -m venv .venv
source .venv/bin/activate
pip install -e '.[api,ui]'
```

3) Configure
- Copy `.env.example` → `.env` and set:
```
OPENAI_API_KEY=sk-your-key
# For CPU only machines
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8  # or float32
```
- Defaults are read from `config/defaults.yaml`. Environment variables override defaults.
- Note: the `--config` CLI flag is reserved for a future override file (Sprint 1 task).

4) Run
- Enhance text only (tests OpenAI):
```
python -m lazy_ptt.cli --verbose enhance-text --text "Add push-to-talk to our CLI" --auto-move
```
- Process an audio file (tests STT + OpenAI):
```
python -m lazy_ptt.cli --verbose process-audio path/to/brief.wav --auto-move
```
- Live push‑to‑talk (hold/release hotkey):
```
python -m lazy_ptt.cli --verbose listen --auto-move
```
- Always‑on daemon:
```
python -m lazy_ptt.cli --verbose daemon
```

Artifacts are created under `outputs/prompts/<STORY_ID>/` by default and (with `--auto-move`) are copied to `project-management/user-story-prompts/<STORY_ID>/`.


## How It Works (Overview)
- Hotkey: `pynput` listens for `PTT_HOTKEY` (default: `space`).
- Record: `AudioRecorder` captures PCM from the selected mic and returns a WAV buffer.
- Transcribe: `WhisperTranscriber` runs faster‑whisper (with VAD) and returns text + metadata.
- Enhance: `PromptEnhancer` calls OpenAI Responses API, requesting structured JSON (work_type, sections, acceptance criteria, etc.), then renders Markdown.
- Save/Move: `PromptStorage` writes markdown + metadata.json to staging and can relocate into `project-management`.

Key modules
- CLI: `src/lazy_ptt/cli.py`
- Config: `src/lazy_ptt/config.py`
- Audio: `src/lazy_ptt/audio/recorder.py`
- STT: `src/lazy_ptt/stt/whisper.py`
- Enhancement: `src/lazy_ptt/prompt/enhancer.py`
- Storage: `src/lazy_ptt/prompt/manager.py`
- Orchestration + Daemon: `src/lazy_ptt/services/ptt_service.py`, `src/lazy_ptt/services/daemon.py`


## Configuration Reference (env vars)
- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (default `gpt-4o-mini`)
- `OPENAI_TEMPERATURE` (default `0.2`)
- `OPENAI_MAX_OUTPUT_TOKENS` (default `1800`)
- `OPENAI_BASE_URL` (optional; advanced/self‑hosted)
- `PTT_LANGUAGE` (e.g., `en`)
- `PTT_SAMPLE_RATE` (default `16000`)
- `PTT_CHUNK_DURATION_MS` (default `64`)
- `PTT_HOTKEY` (default `space`)
- `PTT_INPUT_DEVICE_INDEX` (int; select a specific mic)
- `PTT_OUTPUT_ROOT` (default `./outputs`)
- `WHISPER_MODEL_SIZE` (default `medium`)
- `WHISPER_DEVICE` (`cuda` or `cpu`)
- `WHISPER_COMPUTE_TYPE` (`float16`, `int8`, or `float32`)
- `LAZY_PTT_HOME` (override base directory for outputs and caches)

Precedence (current): built‑in defaults < `config/defaults.yaml` < environment variables. The `--config` override file will be enabled in Sprint 1.


## CLI Usage Examples
- Enhance a text string:
```
python -m lazy_ptt.cli enhance-text \
  --text "Fix 500 on POST /orders, add logging, write tests" \
  --story-id US-123 \
  --story-title "Fix 500 errors" \
  --auto-move
```
- Enhance from a text file:
```
python -m lazy_ptt.cli enhance-text --file notes/brief.txt --auto-move
```
- Transcribe and enhance audio:
```
python -m lazy_ptt.cli process-audio recordings/brief.wav --auto-move
```
- Live PTT capture with custom hotkey and device:
```
PTT_HOTKEY=shift PTT_INPUT_DEVICE_INDEX=2 \
python -m lazy_ptt.cli listen --auto-move
```

Output layout (example)
```
outputs/prompts/US-PTT-20250101-123000/
  US-PTT-20250101-123000_enhanced-prompt.md
  prompt-metadata.json

project-management/user-story-prompts/US-PTT-20250101-123000/
  US-PTT-20250101-123000_enhanced-prompt.md
  prompt-metadata.json
  README.txt  # contains story title when provided
```


## Integration With Claude (or Other Agents)
Pick what fits your template best:

- CLI as a tool (simplest)
  - Shell out to `python -m lazy_ptt.cli ...` and parse stdout for: saved path, work type, summary.
  - Tip: a `--json` output mode is planned to simplify parsing (Sprint 1/2).

- Library import
```
from pathlib import Path
from lazy_ptt import load_config, PTTService

service = PTTService.from_config(load_config())
outcome = service.enhance_text("Implement PTT capture", auto_move=True)
print(outcome.saved_prompt.prompt_path)
```

- REST API (planned in Sprint 2)
  - `POST /enhance-text`, `POST /process-audio`, `POST /listen-once` via FastAPI wrapper.

- Using Claude as enhancer
  - Add a `ClaudeEnhancer` with the same `enhance(text) -> EnhancedPrompt` contract and select via env (future option). The rest of the pipeline remains unchanged.


## Troubleshooting
- sounddevice / PortAudio errors
  - Install PortAudio (see prerequisites). On Linux, verify the microphone: `arecord -l` or `pactl list sources`.
- Headless or no GUI input
  - `pynput` may require a desktop session. On servers, prefer `process-audio` or text enhancement.
- CUDA issues
  - Set `WHISPER_DEVICE=cpu` and `WHISPER_COMPUTE_TYPE=int8` to avoid GPU requirements.
- OpenAI errors
  - Ensure `OPENAI_API_KEY` is set; for custom gateways, set `OPENAI_BASE_URL`.


## Development
- Install dev deps and run tests:
```
pip install -e '.[api,ui]'
pytest -q
```
- Unit tests live under `tests/unit/`.
- Roadmap & tasks: see `SPRINT-1.md`, `SPRINT-2.md`, `SPRINT-3.md`.


## License
MIT — see `LICENSE`.

