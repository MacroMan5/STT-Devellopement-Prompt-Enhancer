from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..audio.recorder import AudioBuffer, AudioRecorder
from ..config import AppConfig, ConfigError
from ..input.hotkey import HotkeyCallbacks, HotkeyListener
from ..prompt.enhancer import EnhancedPrompt, PromptEnhancer
from ..prompt.manager import PromptStorage, SavedPrompt
from ..stt.whisper import TranscriptionResult, WhisperTranscriber

LOGGER = logging.getLogger(__name__)


@dataclass
class PTTOutcome:
    saved_prompt: SavedPrompt
    transcription: TranscriptionResult
    enhanced: EnhancedPrompt


class PTTService:
    """Coordinates audio capture, transcription, enhancement, and storage."""

    def __init__(
        self,
        config: AppConfig,
        recorder: AudioRecorder,
        transcriber: WhisperTranscriber,
        enhancer: PromptEnhancer,
        storage: PromptStorage,
        hotkey_listener: HotkeyListener,
    ) -> None:
        self.config = config
        self.recorder = recorder
        self.transcriber = transcriber
        self.enhancer = enhancer
        self.storage = storage
        self.hotkey_listener = hotkey_listener

    @classmethod
    def from_config(cls, config: AppConfig) -> "PTTService":
        recorder = AudioRecorder(
            sample_rate=config.ptt.sample_rate,
            chunk_duration_ms=config.ptt.chunk_duration_ms,
            channels=1,
            input_device_index=config.ptt.input_device_index,
            silence_threshold=config.ptt.silence_threshold,
            max_record_seconds=config.ptt.max_record_seconds,
        )
        transcriber = WhisperTranscriber(config.whisper)
        enhancer = PromptEnhancer(config.openai)
        storage = PromptStorage(
            output_root=config.paths.prompt_output_root,
            filename_pattern=config.prompt.filename_pattern,
            metadata_filename=config.prompt.metadata_filename,
        )
        hotkey_listener = HotkeyListener(config.ptt.hotkey)
        return cls(config, recorder, transcriber, enhancer, storage, hotkey_listener)

    def enhance_text(
        self,
        text: str,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ) -> PTTOutcome:
        if not text.strip():
            raise ConfigError("Cannot enhance empty text")
        LOGGER.debug("Enhancing text brief")
        enhanced = self.enhancer.enhance(text.strip())
        saved = self.storage.save(enhanced, story_id=story_id)
        if auto_move:
            dest = self.storage.relocate_to_project_management(
                saved,
                self.config.paths.project_management_root,
                story_title=story_title or enhanced.summary,
            )
            LOGGER.info("Prompt moved to %s", dest)
        return PTTOutcome(
            saved_prompt=saved,
            transcription=TranscriptionResult(
                text=text.strip(),
                language=self.config.ptt.language,
                duration=0.0,
                temperature=0.0,
            ),
            enhanced=enhanced,
        )

    def process_audio_buffer(
        self,
        buffer: AudioBuffer,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ) -> PTTOutcome:
        LOGGER.debug("Transcribing captured audio")
        transcription = self.transcriber.transcribe(buffer, language=self.config.ptt.language)
        if not transcription.text:
            raise ConfigError("Transcription returned empty text")
        LOGGER.debug("Enhancing transcribed text: %s", transcription.text)
        enhanced = self.enhancer.enhance(transcription.text)
        saved = self.storage.save(enhanced, story_id=story_id)
        if auto_move:
            dest = self.storage.relocate_to_project_management(
                saved,
                self.config.paths.project_management_root,
                story_title=story_title or enhanced.summary,
            )
            LOGGER.info("Prompt moved to %s", dest)
        return PTTOutcome(saved_prompt=saved, transcription=transcription, enhanced=enhanced)

    def process_audio_file(
        self,
        file_path: Path,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ) -> PTTOutcome:
        LOGGER.debug("Transcribing audio file: %s", file_path)
        transcription = self.transcriber.transcribe_file(
            file_path, language=self.config.ptt.language
        )
        if not transcription.text:
            raise ConfigError(f"No transcription produced for {file_path}")
        enhanced = self.enhancer.enhance(transcription.text)
        saved = self.storage.save(enhanced, story_id=story_id)
        if auto_move:
            dest = self.storage.relocate_to_project_management(
                saved,
                self.config.paths.project_management_root,
                story_title=story_title or enhanced.summary,
            )
            LOGGER.info("Prompt moved to %s", dest)
        return PTTOutcome(saved_prompt=saved, transcription=transcription, enhanced=enhanced)

    def listen_once(
        self,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ) -> PTTOutcome:
        """Engage PTT workflow for a single press/release cycle."""

        result: dict[str, PTTOutcome] = {}

        def on_press() -> None:
            LOGGER.info("Recording started")
            self.recorder.start()

        def on_release() -> None:
            LOGGER.info("Recording stopped; processing audio")
            buffer = self.recorder.stop()
            outcome = self.process_audio_buffer(
                buffer, story_id=story_id, story_title=story_title, auto_move=auto_move
            )
            result["outcome"] = outcome

        callbacks = HotkeyCallbacks(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start(callbacks)
        self.hotkey_listener.join()

        if "outcome" not in result:
            raise ConfigError("PTT session ended without capturing audio")
        return result["outcome"]
