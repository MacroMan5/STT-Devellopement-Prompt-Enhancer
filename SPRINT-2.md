# SPRINT 2 — MVP Launch

Goal: ship a minimal but usable product to teammates: local CLI plus optional lightweight API, device enumeration, and simple distribution. Keep changes small and focused.

Success Criteria
- Simple REST API available for non‑Python callers (no auth/roles yet).
- Microphone device enumeration and selection supported from the CLI.
- Basic OS service templates provided (opt‑in) for running a daemon.
- CI builds and runs tests on push/PR; optional release flow prepared.

---

## 1) Minimal REST API (FastAPI)

- Task: Add FastAPI app with three endpoints using `PTTService`:
  - `POST /enhance-text` {text, story_id?, story_title?, auto_move?}
  - `POST /process-audio` multipart file `audio`, fields story_id?, story_title?, auto_move?
  - `POST /listen-once` triggers a PTT cycle on server; returns `saved paths + summary` (for demo only)
  - File(s): `src/lazy_ptt/api/server.py`, tests in `tests/api/test_api.py`
  - Extras: add `project.optional-dependencies.api` already present; add script entry `lazy-ptt-api`.
  - Acceptance:
    - `uvicorn lazy_ptt.api.server:app` runs; cURL examples in README work.
    - Unit test stubs pass using fakes (no real mic in CI).

## 2) Device Enumeration + Selection

- Task: Add `lazy-ptt devices` CLI subcommand to list input devices and indexes using `sounddevice.query_devices()`.
  - File(s): `src/lazy_ptt/cli.py`, `src/lazy_ptt/audio/devices.py` (new), docs update
  - Acceptance:
    - Running the command prints indices and names; setting `PTT_INPUT_DEVICE_INDEX` respects selection on next run.

## 3) OS Service Templates (optional for power users)

- Task: Provide example unit files to run daemon at startup.
  - Files: `ops/systemd/lazy-ptt-daemon.service`, `ops/launchd/io.lazy.ptt.daemon.plist`, docs
  - Acceptance:
    - Files are parameterized with the user’s virtualenv/env; README shows how to enable/disable.

## 4) CI (minimal) and Release Prep

- Task: GitHub Actions workflow for lint + test matrix (3.10/3.11, Linux + macOS).
  - File(s): `.github/workflows/ci.yml`
  - Acceptance:
    - On PRs, lint and tests run; artifacts not required.

- Task: Prepare release workflow (manual publish).
  - File(s): `.github/workflows/release.yml` (optional), `pyproject.toml` metadata pass
  - Acceptance:
    - `python -m build` produces wheel/sdist; `twine check` passes.

## 5) Docs

- Task: Update README for API usage and devices command; add brief “service” instructions.
  - Acceptance:
    - New users can hit the API and select a microphone with clear steps.

---

Deliverables Checklist
- [ ] FastAPI server with 3 endpoints + examples
- [ ] `devices` CLI subcommand
- [ ] systemd/launchd example files
- [ ] CI for lint+tests
- [ ] Buildable packages and optional release workflow
- [ ] Docs updated for API + devices + services

Timebox
- Target: 2–3 days, depending on CI/release polish.

