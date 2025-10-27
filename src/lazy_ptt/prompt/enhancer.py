from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, List, Optional

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - handled via runtime check
    OpenAI = None

from ..config import OpenAIConfig


SYSTEM_PROMPT = """
You are an elite software architect and product lead. Transform terse engineering briefs into full, actionable plans.

Return a JSON object with:
- work_type: one of ["NEW_PROJECT","FEATURE","HOTFIX","REFACTOR","ENHANCEMENT","DOCUMENTATION"]
- summary: concise high-level summary
- objectives: array of key goals
- risks: array of notable risks or unknowns
- recommended_milestones: ordered array of milestone labels
- sections: array of objects { "title": str, "content": str } tailored to the work
- acceptance_criteria: array of verifiable bullets
- suggested_story_id: optional recommended story ID slug (e.g., "US-4.2")

Focus on relevance. Include only sections that serve the work described in the brief.
""".strip()


@dataclass
class PromptSection:
    title: str
    content: str


@dataclass
class EnhancedPrompt:
    work_type: str
    summary: str
    objectives: List[str]
    risks: List[str]
    milestones: List[str]
    sections: List[PromptSection]
    acceptance_criteria: List[str]
    suggested_story_id: Optional[str]
    original_brief: str

    def to_markdown(self) -> str:
        lines: List[str] = [
            f"# {self.work_type} Plan",
            "",
            f"**Summary**: {self.summary}",
            "",
        ]
        if self.objectives:
            lines.append("## Objectives")
            lines.extend(f"- {item}" for item in self.objectives)
            lines.append("")
        if self.risks:
            lines.append("## Risks & Unknowns")
            lines.extend(f"- {item}" for item in self.risks)
            lines.append("")
        if self.milestones:
            lines.append("## Recommended Milestones")
            for index, milestone in enumerate(self.milestones, start=1):
                lines.append(f"{index}. {milestone}")
            lines.append("")
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append(section.content.strip())
            lines.append("")
        if self.acceptance_criteria:
            lines.append("## Acceptance Criteria")
            lines.extend(f"- [ ] {item}" for item in self.acceptance_criteria)
            lines.append("")
        lines.append("## Original Brief")
        lines.append(f"> {self.original_brief}")
        lines.append("")
        if self.suggested_story_id:
            lines.append(f"_Suggested Story ID_: {self.suggested_story_id}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


class PromptEnhancer:
    """Wrapper responsible for calling OpenAI and shaping the result."""

    def __init__(self, config: OpenAIConfig, client: Optional[object] = None) -> None:
        self.config = config
        if client is not None:
            self.client = client
        else:
            if OpenAI is None:
                raise RuntimeError(
                    "openai package not installed. Install it with `pip install openai` "
                    "or inject a compatible client instance."
                )
            self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def enhance(self, brief: str) -> EnhancedPrompt:
        if not brief or not brief.strip():
            raise ValueError("Brief must be non-empty")

        response = self.client.responses.create(
            model=self.config.model,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
            response_format={"type": "json_object"},
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": brief.strip()},
            ],
        )
        payload = _extract_text(response)
        data = json.loads(payload)
        sections = [
            PromptSection(title=item.get("title", "Details"), content=item.get("content", "").strip())
            for item in data.get("sections", [])
        ]

        return EnhancedPrompt(
            work_type=data.get("work_type", "FEATURE"),
            summary=data.get("summary", "").strip(),
            objectives=_string_list(data.get("objectives")),
            risks=_string_list(data.get("risks")),
            milestones=_string_list(data.get("recommended_milestones")),
            sections=sections,
            acceptance_criteria=_string_list(data.get("acceptance_criteria")),
            suggested_story_id=data.get("suggested_story_id"),
            original_brief=brief.strip(),
        )


def _string_list(value: Optional[Iterable[str]]) -> List[str]:
    if not value:
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _extract_text(response: object) -> str:
    """
    Extract text payload from OpenAI responses.create output.

    The Responses API returns a structure with an `output` list. We inspect the
    first content block and fall back to string conversion if needed.
    """

    if hasattr(response, "output"):
        output = getattr(response, "output")
        if output:
            content = output[0].content
            if content:
                return content[0].text
    if hasattr(response, "choices"):
        choices = getattr(response, "choices")
        if choices:
            return choices[0].message["content"]
    return str(response)
