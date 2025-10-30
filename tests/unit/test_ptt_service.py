from pathlib import Path

from lazy_ptt.audio.recorder import AudioBuffer
from lazy_ptt.config import (
    AppConfig,
    OpenAIConfig,
    PTTConfig,
    PromptConfig,
    ProjectPaths,
    WhisperConfig,
)
from lazy_ptt.prompt.enhancer import EnhancedPrompt, PromptSection
from lazy_ptt.prompt.manager import PromptStorage
from lazy_ptt.services.ptt_service import PTTService


class _FakeRecorder:
    def __init__(self, buffer: AudioBuffer) -> None:
        self.buffer = buffer
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> AudioBuffer:
        return self.buffer


class _FakeTranscriber:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls = 0

    def transcribe(self, _buffer: AudioBuffer, language: str | None = None):
        self.calls += 1
        return type("Result", (), {"text": self.text, "language": language, "duration": 1.5, "temperature": 0.0})()

    def transcribe_file(self, _path: Path, language: str | None = None):
        return self.transcribe(AudioBuffer(b"", 16000, 1, 0.0), language=language)


class _FakeEnhancer:
    def __init__(self) -> None:
        self.requests: list[str] = []

    def enhance(self, text: str) -> EnhancedPrompt:
        self.requests.append(text)
        return EnhancedPrompt(
            work_type="FEATURE",
            summary=f"Summary for {text}",
            objectives=["Objective"],
            risks=[],
            milestones=[],
            sections=[PromptSection(title="Plan", content="Implement the workflow.")],
            acceptance_criteria=["Prompt stored"],
            suggested_story_id="US-PTT",
            original_brief=text,
        )


class _FakeHotkeyListener:
    def start(self, callbacks) -> None:
        callbacks.on_press()
        callbacks.on_release()

    def join(self) -> None:
        return None

    def stop(self) -> None:
        return None


def _build_config(tmp_path: Path) -> AppConfig:
    repo_root = tmp_path
    pm_root = tmp_path / "project-management"
    output_root = tmp_path / "staging"
    return AppConfig(
        paths=ProjectPaths(
            repository_root=repo_root,
            project_management_root=pm_root,
            prompt_output_root=output_root,
        ),
        ptt=PTTConfig(
            language="en",
            sample_rate=16000,
            chunk_duration_ms=64,
            silence_threshold=0.015,
            max_record_seconds=120,
            hotkey="space",
            input_device_index=None,
        ),
        whisper=WhisperConfig(
            model_size="medium",
            device="cpu",
            compute_type="int8",
            download_root=tmp_path / ".cache",
        ),
        openai=OpenAIConfig(
            api_key="test",
            model="stub",
            temperature=0.0,
            max_output_tokens=1000,
            base_url=None,
        ),
        prompt=PromptConfig(
            filename_pattern="{story_id}.md",
            metadata_filename="meta.json",
        ),
    )


def _build_service(tmp_path: Path, text: str) -> PTTService:
    config = _build_config(tmp_path)
    buffer = AudioBuffer(b"data", sample_rate=16000, channels=1, duration_seconds=1.0)
    recorder = _FakeRecorder(buffer)
    transcriber = _FakeTranscriber(text)
    enhancer = _FakeEnhancer()
    storage = PromptStorage(config.paths.prompt_output_root, config.prompt.filename_pattern, config.prompt.metadata_filename)
    hotkey = _FakeHotkeyListener()
    return PTTService(config, recorder, transcriber, enhancer, storage, hotkey)


def test_process_audio_buffer_saves_prompt(tmp_path: Path) -> None:
    service = _build_service(tmp_path, "Implement push-to-talk")

    buffer = AudioBuffer(b"data", sample_rate=16000, channels=1, duration_seconds=1.0)
    outcome = service.process_audio_buffer(buffer, story_id="US-PTT", auto_move=False)

    assert outcome.saved_prompt.prompt_path.exists()
    assert not (service.config.paths.project_management_root / "user-story-prompts").exists()


def test_process_audio_buffer_moves_when_requested(tmp_path: Path) -> None:
    service = _build_service(tmp_path, "Implement push-to-talk")

    buffer = AudioBuffer(b"data", sample_rate=16000, channels=1, duration_seconds=1.0)
    outcome = service.process_audio_buffer(buffer, story_id="US-PTT", story_title="PTT Workflow", auto_move=True)

    dest_dir = service.config.paths.project_management_root / "user-story-prompts" / "US-PTT"
    assert dest_dir.exists()
    assert (dest_dir / outcome.saved_prompt.prompt_path.name).exists()
    assert (dest_dir / "meta.json").exists()
