# PTT Voice Workflow Requirements

## Functional

- Capture push-to-talk audio via configurable hotkey and microphone device.
- Support an always-on daemon that waits for the hotkey and immediately records on press.
- Transcribe captured audio locally using GPU-accelerated Whisper medium model (language configurable).
- Enhance transcribed briefs through OpenAI with contextual work-type detection and structured output.
- Persist enhanced prompts in a staging directory with metadata for later commands and audit.
- Relocate prompts into the project-management repository when running the create-feature helper.
- Support alternate entry points for direct text briefs and pre-recorded audio files.
- Provide notifications/logging summarising each generated prompt (story id, work type, summary).
- Offer optional desktop UI that displays live audio levels, current transcription, enhanced prompt preview, and retains session history.
- Expose library API so other tools can trigger capture/enhancement programmatically.
- Allow selection of domain-specific enhancement profiles (e.g., development, marketing, finance, research) with pluggable prompt templates.
- Provide hosted/local REST API that mirrors CLI functionality for cross-language clients.

## Non-Functional

- Provide configuration through environment variables with YAML defaults and `.env` overrides.
- Ensure end-to-end processing completes within a few seconds for sub-60 second briefs.
- Operate offline for STT once models are downloaded; only enhancement hits external network.
- Maintain audit trail by writing metadata JSON alongside each prompt and copying it with the markdown.
- Ship with unit tests covering storage, enhancement parsing, service orchestration, and daemon loop control.
- Log errors with actionable remediation hints and continue listening without full restart.
- Allow graceful shutdown (Ctrl+C) of the daemon without corrupting in-flight recordings.
- Package the system as a reusable module published to PyPI with semantic versioning and automated updates.
- Provide install-time diagnostics that check for audio devices, CUDA availability, and configuration completeness.
- Persist observability data (logs/metrics) between sessions for retrospective analysis.
- Support configuration/selection of new domain profiles without redeploying the service (hot reload or config files).
- Maintain backward compatibility guarantees for CLI/API consumers via versioned endpoints.
