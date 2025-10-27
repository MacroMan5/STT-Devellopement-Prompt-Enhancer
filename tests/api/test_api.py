from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi.testclient import TestClient

from lazy_ptt.api.server import build_app


class _FakeSaved:
    def __init__(self, story_id: str, path: Path) -> None:
        self.story_id = story_id
        self.prompt_path = path


class _FakeOutcome:
    def __init__(self, text: str = "hello") -> None:
        self.saved_prompt = _FakeSaved("US-1", Path("/tmp/US-1.md"))
        self.enhanced = type(
            "Enhanced",
            (),
            {"summary": f"Summary for {text}", "work_type": "FEATURE"},
        )()
        self.transcription = type("T", (), {"text": text})()


class _FakeService:
    def enhance_text(
        self,
        text: str,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ):
        return _FakeOutcome(text)

    def process_audio_file(
        self,
        _path: Path,
        story_id: Optional[str] = None,
        story_title: Optional[str] = None,
        auto_move: bool = False,
    ):
        return _FakeOutcome("from-audio")


def _fake_factory():
    return _FakeService()


def test_enhance_text_endpoint():
    app = build_app(service_factory=_fake_factory)
    client = TestClient(app)
    resp = client.post("/enhance-text", json={"text": "hello world"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["story_id"] == "US-1"
    assert body["work_type"] == "FEATURE"


def test_process_audio_endpoint(tmp_path):
    app = build_app(service_factory=_fake_factory)
    client = TestClient(app)
    wav_path = tmp_path / "sample.wav"
    wav_path.write_bytes(b"RIFF....WAVE")
    with wav_path.open("rb") as f:
        resp = client.post(
            "/process-audio",
            files={"audio": ("sample.wav", f, "audio/wav")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"].startswith("Summary")
