from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

from ..config import AppConfig, ConfigError, load_config
from ..services.ptt_service import PTTService


class EnhanceTextRequest(BaseModel):
    text: str = Field(min_length=1)
    story_id: Optional[str] = None
    story_title: Optional[str] = None
    auto_move: bool = False


class ProcessAudioResponse(BaseModel):
    story_id: str
    prompt_path: str
    summary: str
    work_type: str
    transcription_text: str


def _service_from_env() -> PTTService:
    config: AppConfig = load_config()
    return PTTService.from_config(config)


def build_app(service_factory=_service_from_env) -> FastAPI:
    app = FastAPI(title="lazy-ptt API", version="0.1.0")

    def _response_from_outcome(outcome) -> ProcessAudioResponse:
        return ProcessAudioResponse(
            story_id=outcome.saved_prompt.story_id,
            prompt_path=str(outcome.saved_prompt.prompt_path),
            summary=outcome.enhanced.summary,
            work_type=outcome.enhanced.work_type,
            transcription_text=outcome.transcription.text,
        )

    @app.post("/enhance-text", response_model=ProcessAudioResponse)
    def enhance_text(req: EnhanceTextRequest):  # type: ignore[valid-type]
        try:
            service = service_factory()
            outcome = service.enhance_text(
                req.text,
                story_id=req.story_id,
                story_title=req.story_title,
                auto_move=req.auto_move,
            )
            return _response_from_outcome(outcome)
        except ConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/process-audio", response_model=ProcessAudioResponse)
    async def process_audio(audio: UploadFile = File(...), story_id: Optional[str] = None, story_title: Optional[str] = None, auto_move: bool = False):  # type: ignore[valid-type]
        try:
            service = service_factory()
            # Persist upload to a temp file to let existing pipeline handle formats.
            suffix = Path(audio.filename or "upload").suffix or ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                data = await audio.read()
                tmp.write(data)
                tmp_path = Path(tmp.name)
            try:
                outcome = service.process_audio_file(
                    tmp_path,
                    story_id=story_id,
                    story_title=story_title,
                    auto_move=auto_move,
                )
            finally:
                tmp_path.unlink(missing_ok=True)
            return _response_from_outcome(outcome)
        except ConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/listen-once", response_model=ProcessAudioResponse)
    def listen_once(story_id: Optional[str] = None, story_title: Optional[str] = None, auto_move: bool = False):  # type: ignore[valid-type]
        try:
            service = service_factory()
            outcome = service.listen_once(
                story_id=story_id, story_title=story_title, auto_move=auto_move
            )
            return _response_from_outcome(outcome)
        except ConfigError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = build_app()


def main() -> None:
    # Convenience entrypoint to run the API quickly via `lazy-ptt-api`.
    import uvicorn

    uvicorn.run("lazy_ptt.api.server:app", host="127.0.0.1", port=8000, reload=False)

