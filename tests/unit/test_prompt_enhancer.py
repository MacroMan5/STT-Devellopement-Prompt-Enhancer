import json

from lazy_ptt.config import BrandingConfig, OpenAIConfig
from lazy_ptt.prompt.enhancer import PromptEnhancer


class _FakeResponseContent:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeResponseBlock:
    def __init__(self, text: str) -> None:
        self.content = [_FakeResponseContent(text)]


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.output = [_FakeResponseBlock(text)]


class _FakeResponsesClient:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def create(self, **_: object) -> _FakeResponse:
        return _FakeResponse(json.dumps(self._payload))


class _FakeOpenAIClient:
    def __init__(self, payload: dict) -> None:
        self.responses = _FakeResponsesClient(payload)


def test_prompt_enhancer_parses_response_payload() -> None:
    payload = {
        "work_type": "FEATURE",
        "summary": "Implement push-to-talk workflow",
        "objectives": ["Enable quick capture"],
        "risks": ["Microphone unavailable"],
        "recommended_milestones": ["Alpha", "Beta"],
        "sections": [{"title": "Implementation", "content": "Break down services."}],
        "acceptance_criteria": ["Prompt stored in project management"],
        "suggested_story_id": "US-5.1",
    }
    config = OpenAIConfig(
        api_key="test-key",
        model="test-model",
        temperature=0.0,
        max_output_tokens=500,
        base_url=None,
    )
    client = _FakeOpenAIClient(payload)

    enhancer = PromptEnhancer(config, client=client)  # type: ignore[arg-type]
    result = enhancer.enhance("Implement push-to-talk workflow")

    assert result.work_type == "FEATURE"
    assert result.sections[0].title == "Implementation"
    assert result.acceptance_criteria == ["Prompt stored in project management"]
    assert result.suggested_story_id == "US-5.1"
