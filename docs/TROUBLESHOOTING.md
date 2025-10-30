# Troubleshooting

Common setup hiccups and how to fix them fast.

## sounddevice / PortAudio errors
Symptoms
- ImportError: No module named 'sounddevice'
- PortAudioError: Error opening InputStream

Fix
- macOS: `brew install portaudio`
- Debian/Ubuntu: `sudo apt-get install -y libportaudio2`
- Windows: ensure default input device exists (Sound control panel) and correct driver is installed.
- List devices (Python REPL):
```
>>> import sounddevice as sd
>>> sd.query_devices()
```

## Headless or no desktop session
Symptoms
- Hotkey listener does nothing or errors when running over SSH/CI.

Fix
- `pynput` needs a desktop session; use `process-audio` or `enhance-text` on servers.
- For automation, add the planned REST API (Sprint 2) and call it remotely.

## CUDA/GPU issues (faster‑whisper)
Symptoms
- Torch/cuda mismatch, model fails to load, poor performance.

Fix
- Use CPU fallback: set `WHISPER_DEVICE=cpu` and `WHISPER_COMPUTE_TYPE=int8` (or `float32`).
- Ensure models cache under a writable path (defaults under `${LAZY_PTT_HOME}/.cache/whisper`).

## OpenAI API errors
Symptoms
- Authentication errors; 401/403; rate limits.

Fix
- Set `OPENAI_API_KEY` in `.env`.
- If using a gateway, set `OPENAI_BASE_URL` appropriately.
- Re-run the smoke tests (`docs/SMOKE.md`).

## File permissions / paths
- On first run, the tool creates `outputs/prompts/<STORY_ID>/`. Ensure the process can write to the working directory or set `PTT_OUTPUT_ROOT`.

---
If you hit something not listed here, open an issue with your OS, Python version, and exact error.
