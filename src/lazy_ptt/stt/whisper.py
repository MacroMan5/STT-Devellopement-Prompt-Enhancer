from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from faster_whisper import WhisperModel  # type: ignore
except ImportError:  # pragma: no cover - handled via runtime check
    WhisperModel = None

from ..audio.recorder import AudioBuffer
from ..config import WhisperConfig


@dataclass
class TranscriptionResult:
    text: str
    language: Optional[str]
    duration: float
    temperature: float


class WhisperTranscriber:
    """GPU-accelerated Whisper transcription using faster-whisper."""

    def __init__(self, config: WhisperConfig) -> None:
        self.config = config
        self._model: Optional[WhisperModel] = None

    def _ensure_model(self) -> WhisperModel:
        if WhisperModel is None:
            raise RuntimeError(
                "faster-whisper is not installed. Install it with `pip install faster-whisper` "
                "or disable speech-to-text features."
            )
        if self._model is None:
            self._model = WhisperModel(
                self.config.model_size,
                device=self.config.device,
                compute_type=self.config.compute_type,
                download_root=str(self.config.download_root),
            )
        return self._model

    def transcribe(self, buffer: AudioBuffer, language: Optional[str] = None) -> TranscriptionResult:
        model = self._ensure_model()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(buffer.wav_bytes)
            tmp.flush()
            tmp_path = Path(tmp.name)

        try:
            segments, info = model.transcribe(
                str(tmp_path),
                language=language,
                beam_size=5,
                vad_filter=True,
            )
            text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
            transcript = " ".join(text_parts).strip()
        finally:
            tmp_path.unlink(missing_ok=True)

        return TranscriptionResult(
            text=transcript,
            language=getattr(info, "language", language),
            duration=getattr(info, "duration", buffer.duration_seconds),
            temperature=getattr(info, "temperature", 0.0),
        )

    def transcribe_file(self, file_path: Path, language: Optional[str] = None) -> TranscriptionResult:
        model = self._ensure_model()
        segments, info = model.transcribe(
            str(file_path),
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
        transcript = " ".join(text_parts).strip()
        duration = getattr(info, "duration", 0.0)
        return TranscriptionResult(
            text=transcript,
            language=getattr(info, "language", language),
            duration=duration,
            temperature=getattr(info, "temperature", 0.0),
        )
