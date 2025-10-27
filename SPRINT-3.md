# SPRINT 3 — Nice‑To‑Have Enhancements (Keep It Simple)

Goal: small quality-of-life features that improve day-to-day use without bloating scope.

Success Criteria
- Features are opt-in, minimally coupled, and do not complicate core flows.
- No regressions to SPRINT 1–2 behavior; tests remain simple.

---

## 1) Basic Desktop/TUI Feedback (Optional)

- Task: Add a minimal terminal UI (Rich) that shows:
  - Live status: “Recording…/Processing…/Saved at <path>”
  - Last summary and work type
  - File(s): `src/lazy_ptt/ui/tui.py`, CLI flag `--tui` on `listen`/`daemon`
  - Acceptance:
    - When `--tui` is passed, users see status and last outcome; no TUI by default.

## 2) Domain Profiles for Enhancement

- Task: Allow selecting a domain profile that augments the system prompt (dev/marketing/research, etc.).
  - Files: `src/lazy_ptt/prompt/profiles/*.yaml` (tiny templates), `src/lazy_ptt/prompt/enhancer.py` to accept `profile`
  - CLI: `--profile` on `enhance-text`, `process-audio`, `listen`
  - Acceptance:
    - Choosing `--profile dev` tweaks output sections (e.g., architecture, testing) consistently.

## 3) Desktop Notification (Post‑Save)

- Task: On Linux/macOS/Windows, send an optional OS notification when a prompt is generated.
  - Files: `src/lazy_ptt/notify.py` (uses `plyer` or lightweight per‑OS calls), feature-flag via env `PTT_NOTIFY=1`
  - Acceptance:
    - With flag on, a notification with story_id + summary appears after save/move.

## 4) Language Auto‑Detection Fallback

- Task: If `PTT_LANGUAGE` unset, let Whisper auto-detect and surface it in metadata.
  - Files: `src/lazy_ptt/stt/whisper.py` (pass `language=None`), `src/lazy_ptt/prompt/manager.py` metadata includes detected language
  - Acceptance:
    - Recording in a non‑English language yields a detected language code in the JSON.

## 5) Head/Tail Trim (Gating) — Simple Version

- Task: Apply a minimal RMS threshold on head/tail to reduce dead air.
  - Files: `src/lazy_ptt/audio/recorder.py`
  - Acceptance:
    - Short pauses are trimmed; configuration uses existing `silence_threshold` and remains optional.

## 6) Logs to File (Daemon Mode)

- Task: Add `--log-file` option to CLI/daemon to write rotating logs.
  - Files: `src/lazy_ptt/cli.py`, `src/lazy_ptt/services/daemon.py`
  - Acceptance:
    - When set, logs are persisted with rotation; no change when omitted.

---

Deliverables Checklist
- [ ] Optional TUI status
- [ ] Domain profiles and `--profile`
- [ ] Optional desktop notifications
- [ ] Language auto‑detection fallback
- [ ] Simple silence trimming
- [ ] Optional log‑to‑file for daemon

Timebox
- Target: 3–4 days, features are independent and can be cherry‑picked.

