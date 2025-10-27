from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .enhancer import EnhancedPrompt


SAFE_STORY_PATTERN = re.compile(r"[^a-zA-Z0-9_.-]+")


def _slugify(value: str) -> str:
    value = value.strip().lower().replace(" ", "-")
    return SAFE_STORY_PATTERN.sub("-", value).strip("-")


@dataclass
class SavedPrompt:
    story_id: str
    prompt_path: Path
    metadata_path: Path


class PromptStorage:
    """Persists enhanced prompt artifacts and manages relocation to project-management."""

    def __init__(self, output_root: Path, filename_pattern: str, metadata_filename: str) -> None:
        self.output_root = output_root
        self.filename_pattern = filename_pattern
        self.metadata_filename = metadata_filename
        self.output_root.mkdir(parents=True, exist_ok=True)

    def save(self, prompt: EnhancedPrompt, story_id: Optional[str] = None) -> SavedPrompt:
        story_id = (
            story_id
            or prompt.suggested_story_id
            or self._generate_story_id(prompt.work_type)
        ).upper()
        safe_story_id = SAFE_STORY_PATTERN.sub("-", story_id).strip("-")
        if not safe_story_id:
            raise ValueError("Story ID resolved to an empty string")

        story_dir = self.output_root / safe_story_id
        story_dir.mkdir(parents=True, exist_ok=True)

        filename = self.filename_pattern.format(
            story_id=safe_story_id,
            work_type=_slugify(prompt.work_type),
        )
        prompt_path = story_dir / filename
        prompt_path.write_text(prompt.to_markdown(), encoding="utf-8")

        metadata = {
            "story_id": safe_story_id,
            "work_type": prompt.work_type,
            "summary": prompt.summary,
            "objectives": prompt.objectives,
            "risks": prompt.risks,
            "milestones": prompt.milestones,
            "acceptance_criteria": prompt.acceptance_criteria,
            "suggested_story_id": prompt.suggested_story_id,
        }
        metadata_path = story_dir / self.metadata_filename
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return SavedPrompt(
            story_id=safe_story_id,
            prompt_path=prompt_path,
            metadata_path=metadata_path,
        )

    def relocate_to_project_management(
        self,
        saved_prompt: SavedPrompt,
        project_management_root: Path,
        story_title: Optional[str] = None,
    ) -> Path:
        dest_dir = project_management_root / "user-story-prompts" / saved_prompt.story_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        if story_title:
            (dest_dir / "README.txt").write_text(story_title.strip() + "\n", encoding="utf-8")
        dest_prompt = dest_dir / saved_prompt.prompt_path.name
        dest_metadata = dest_dir / saved_prompt.metadata_path.name
        shutil.copy2(saved_prompt.prompt_path, dest_prompt)
        shutil.copy2(saved_prompt.metadata_path, dest_metadata)
        return dest_prompt

    def load_saved_prompt(self, prompt_path: Path) -> SavedPrompt:
        prompt_path = prompt_path.resolve()
        metadata_path = prompt_path.parent / self.metadata_filename
        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found alongside prompt: {metadata_path}"
            )
        story_id = prompt_path.parent.name
        return SavedPrompt(story_id=story_id, prompt_path=prompt_path, metadata_path=metadata_path)

    def _generate_story_id(self, work_type: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        base = _slugify(work_type or "FEATURE").upper()
        return f"US-{base}-{timestamp}"
