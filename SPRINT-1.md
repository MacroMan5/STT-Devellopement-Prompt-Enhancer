# SPRINT 1 — Dev Toolchain Ready + Critical Fixes

Goal: get a developer-usable CLI that works end‑to‑end locally (record → STT → enhance → save/move), remove packaging pitfalls, and smooth local iteration. Keep scope tight and pragmatic.

Out-of-scope: API service, desktop/TUI, domain profiles, telemetry (moved to later sprints).

Success Criteria
- Local installs via `pip install -e .` work reliably on macOS/Linux/Windows.
- CLI commands `enhance-text`, `process-audio`, `listen`, and `daemon` run with a real `OPENAI_API_KEY`.
- Config can be overridden deterministically (env and optional YAML path).
- A minimal README enables a new dev to set up and run in <10 minutes.

---

## 1) Packaging/Docs: README and Defaults Loading

- Task: Add a repo‑root `README.md` referenced by `pyproject.toml` to avoid build failures.
  - File(s): `README.md`, `pyproject.toml`
  - Acceptance:
    - `pip wheel .` or `python -m build` succeeds without “README” missing.
    - README includes Quick Start, prerequisites, and CLI examples.

- Task: Make `config/defaults.yaml` loadable when the package is installed, not only when run from repo root.
  - Change: Move defaults into the package and load via `importlib.resources`.
  - File(s): `src/lazy_ptt/config.py`, new `src/lazy_ptt/data/defaults.yaml`, `pyproject.toml` (include package data)
  - Acceptance:
    - Running `python -m lazy_ptt.cli --verbose enhance-text --text 'hello'` outside repo still finds defaults.
    - If YAML missing, fall back to hardcoded defaults without crashing.

## 2) Config Overrides: Wire `--config`

- Task: Honor `--config` path to a YAML file that overrides defaults, with final precedence:
  - Built‑in defaults < file at `--config` < environment variables < explicit CLI args (where applicable).
  - File(s): `src/lazy_ptt/cli.py` (`_resolve_config`), `src/lazy_ptt/config.py` (accept path arg already)
  - Acceptance:
    - Passing a YAML with `openai.model: gpt-4o-mini` and exporting env `OPENAI_MODEL=gpt-4o` ends up using `gpt-4o`.
    - Supplying a different `prompt.filename_pattern` via YAML is reflected in the saved file.

## 3) Smoke Test + Runbook

- Task: Add a simple end‑to‑end smoke doc and script for local verification (no network for STT; OpenAI call allowed).
  - Add `docs/SMOKE.md` describing three checks: enhance-only, process-audio, live listen.
  - Optional script: `scripts/smoke.sh` to run `enhance-text` and `process-audio` (skips live input).
  - Acceptance:
    - A new dev following `SMOKE.md` can complete checks with copy‑paste commands.

## 4) Minimal Dev Tooling (Keep It Light)

- Task: Add a tiny `Makefile` with just: `setup`, `lint`, `test`, `run-listen`, `run-audio`, `run-enhance`.
  - File(s): `Makefile`
  - Acceptance:
    - `make setup` installs extras `[api,ui]` and pre-commit if present.
    - `make test` runs pytest successfully.

- Task: Add `ruff` + `black` config and optional `pre-commit` hooks (no over‑engineering, default settings).
  - File(s): `pyproject.toml` (tool configs), `.pre-commit-config.yaml`
  - Acceptance:
    - `ruff` and `black` run clean on a fresh clone after `make setup`.

## 5) Small Code Hygiene (Critical Clarity)

- Task: Wire or remove unused pieces to avoid confusion.
  - `record_blocking()` vs. current lifecycle: either document as internal or implement a timed blocking variant.
  - `_start_time` unused: remove or use for safety checks.
  - File(s): `src/lazy_ptt/audio/recorder.py`
  - Acceptance:
    - No dead code or misleading API remains; docstrings reflect actual behavior.

- Task: Clarify `silence_threshold` usage.
  - Option A (quick): mark as “reserved” in README/config comments and keep for later trimming.
  - Option B (small): apply a basic head/tail gate (RMS threshold) when converting buffers.
  - File(s): `src/lazy_ptt/audio/recorder.py`, `README.md`, `config comments`
  - Acceptance:
    - Either the setting is hidden/marked reserved, or basic gating is active and tested on a sample.

## 6) Troubleshooting

- Task: Add concise troubleshooting with common errors:
  - Missing PortAudio/sounddevice, CUDA mismatch, OpenAI key, headless `pynput` limitations.
  - File(s): `docs/TROUBLESHOOTING.md`, link from README
  - Acceptance:
    - Encountering any of the above leads to an actionable fix via the page.

---

Deliverables Checklist
- [ ] README with Quick Start and Troubleshooting links
- [ ] Package‑internal defaults loading (works after install)
- [ ] `--config` overrides respected
- [ ] Smoke doc/script validated on one machine
- [ ] Minimal Makefile + (optional) pre‑commit
- [ ] Audio recorder hygiene and `silence_threshold` status clarified

Timebox
- Target: 1–2 days of focused work.

