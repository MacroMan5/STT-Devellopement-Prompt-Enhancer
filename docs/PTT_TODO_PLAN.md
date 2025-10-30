# PTT Voice Workflow Build Plan

This checklist tracks the remaining work to deliver the production-ready push-to-talk pipeline.

## Foundation

- [x] Stand up GPU-accelerated Whisper transcription via faster-whisper
- [x] Implement OpenAI-backed prompt enhancement pipeline with JSON contract
- [x] Persist prompts + metadata and integrate with `/lazy create-feature`
- [x] Document configuration, environment setup, and troubleshooting flows
- [x] Add always-on daemon loop so the service continually listens for PTT events

## Audio Capture Improvements

- [ ] Expose microphone enumeration utility and document device selection
- [ ] Add optional automatic silence trimming / head-tail noise gating
- [ ] Provide CLI flag to record multi-channel input when hardware supports it

## Quality & Reliability

- [ ] Add end-to-end smoke test that mocks audio/STT/OpenAI stack
- [ ] Stress-test hotkey listener on Windows/macOS/Linux and capture notes
- [ ] Implement telemetry/log rotation for daemon mode
- [ ] Package a sample systemd/launchd script for background startup
- [ ] Finalize pip-installable distribution (`lazy-ptt-enhancer`) with release pipeline
- [ ] Stand up CI/CD publishing pipeline in `MacroMan5/STT-Devellopement-Prompt-Enhancer`
- [ ] Expose REST/gRPC service wrapper with contract tests

## UX Enhancements

- [ ] Surface desktop notifications when prompts are generated
- [ ] Expose hook to auto-launch `/lazy create-feature` after prompt save
- [ ] Allow language auto-detection fallback when `PTT_LANGUAGE` unset
- [ ] Build lightweight desktop UI showing live waveform, transcription, and enhanced prompt
- [ ] Persist session history so previous briefs can be recalled between runs
- [ ] Add opt-in analytics/log export for long-term tracking
- [ ] Implement domain/profile selector (development, marketing, finance, research, etc.)
- [ ] Ship starter templates for each domain with customizable prompt definitions
