from __future__ import annotations

import io
import threading
import time
import wave
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

try:
    import sounddevice as sd  # type: ignore
except ImportError:  # pragma: no cover - handled via runtime check
    sd = None


@dataclass
class AudioBuffer:
    """Container for captured audio data."""

    wav_bytes: bytes
    sample_rate: int
    channels: int
    duration_seconds: float


class AudioCaptureError(RuntimeError):
    """Raised when recording fails unexpectedly."""


class AudioRecorder:
    """High-level microphone recorder tailored for push-to-talk usage."""

    def __init__(
        self,
        sample_rate: int,
        chunk_duration_ms: int,
        channels: int = 1,
        input_device_index: Optional[int] = None,
        silence_threshold: float = 0.015,
        max_record_seconds: int = 120,
    ) -> None:
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * (chunk_duration_ms / 1000.0))
        self.channels = channels
        self.device_index = input_device_index
        self.silence_threshold = silence_threshold
        self.max_record_seconds = max_record_seconds

        self._stream: Optional[sd.InputStream] = None
        self._buffers: list[np.ndarray] = []
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None

    def _audio_callback(
        self, indata: np.ndarray, frames: int, _time_info: dict, status: sd.CallbackFlags
    ) -> None:
        if status:
            raise AudioCaptureError(f"Audio callback reported status: {status}")
        with self._lock:
            self._buffers.append(indata.copy())

    def start(self) -> None:
        """Begin recording audio from the configured input device."""

        if self._stream is not None:
            raise AudioCaptureError("Recorder already active")

        self._buffers.clear()

        if sd is None:
            raise AudioCaptureError(
                "sounddevice dependency missing. Install it with `pip install sounddevice` to record audio."
            )

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=self.channels,
            dtype="float32",
            device=self.device_index,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._start_time = time.monotonic()

    def stop(self) -> AudioBuffer:
        """Stop recording and return the captured audio as a WAV buffer."""

        if self._stream is None:
            raise AudioCaptureError("Recorder is not active")

        try:
            self._stream.stop()
            self._stream.close()
        finally:
            self._stream = None

        with self._lock:
            if not self._buffers:
                raise AudioCaptureError("No audio frames captured")
            audio = np.concatenate(self._buffers, axis=0)
            self._buffers.clear()

        duration_seconds = len(audio) / self.sample_rate
        if duration_seconds > self.max_record_seconds:
            raise AudioCaptureError(
                f"Recording exceeded max duration ({duration_seconds:.2f}s > {self.max_record_seconds}s)"
            )

        wav_bytes = self._to_wav(audio)
        return AudioBuffer(
            wav_bytes=wav_bytes,
            sample_rate=self.sample_rate,
            channels=self.channels,
            duration_seconds=duration_seconds,
        )

    def _to_wav(self, audio: np.ndarray) -> bytes:
        """Convert float32 PCM samples to 16-bit WAV byte stream."""

        scaled = np.clip(audio, -1.0, 1.0)
        pcm16 = (scaled * 32767).astype(np.int16)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit samples
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm16.tobytes())
        return buffer.getvalue()

    def record_blocking(self, on_begin: Optional[Callable[[], None]] = None) -> AudioBuffer:
        """Record until `stop()` is called externally; helper for synchronous workflows."""

        if on_begin:
            on_begin()
        return self.stop()
