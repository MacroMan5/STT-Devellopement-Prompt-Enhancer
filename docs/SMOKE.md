# Smoke Test — 5 Minutes

Use this to verify your setup without over‑engineering.

Prereqs
- `.env` with a valid `OPENAI_API_KEY`
- PortAudio installed (see README)

## 1) Enhance‑only (OpenAI only)
```
python -m lazy_ptt.cli --verbose enhance-text --text "Add push-to-talk capture to our CLI"
```
Expect
- Prints a saved prompt path and a summary.
- Files placed under `outputs/prompts/<STORY_ID>/`.

## 2) File Transcription (STT + OpenAI)
Have a WAV/MP3/FLAC file ready (10–30s voice note).
```
python -m lazy_ptt.cli --verbose process-audio path/to/brief.wav
```
Expect
- Detected work type and summary.
- Markdown + metadata saved.

## 3) Live Push‑to‑Talk (Optional)
Requires a desktop session; hold the space bar to record, release to process.
```
python -m lazy_ptt.cli --verbose listen
```

## One‑liner Script (optional)
You can run `scripts/smoke.sh` to execute 1) and 2). Set `SMOKE_AUDIO=path/to/file.wav` to enable the second step.

