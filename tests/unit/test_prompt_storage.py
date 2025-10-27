import json
from pathlib import Path

from lazy_ptt.prompt.enhancer import EnhancedPrompt, PromptSection
from lazy_ptt.prompt.manager import PromptStorage


def _sample_prompt() -> EnhancedPrompt:
    return EnhancedPrompt(
        work_type="FEATURE",
        summary="Add push-to-talk workflow",
        objectives=["Capture voice brief", "Enhance prompt", "Save to project management"],
        risks=["Microphone hardware unavailable"],
        milestones=["Prototype", "User story ready"],
        sections=[
            PromptSection(
                title="Implementation",
                content="Outline the service architecture.",
            )
        ],
        acceptance_criteria=["Prompt saved to staging directory"],
        suggested_story_id="US-99.1",
        original_brief="Add a PTT command",
    )


def test_save_creates_prompt_and_metadata(tmp_path: Path) -> None:
    storage = PromptStorage(tmp_path, "{story_id}_prompt.md", "metadata.json")
    prompt = _sample_prompt()

    saved = storage.save(prompt)

    assert saved.prompt_path.exists()
    assert saved.metadata_path.exists()

    metadata = json.loads(saved.metadata_path.read_text(encoding="utf-8"))
    assert metadata["story_id"] == saved.story_id
    assert metadata["work_type"] == "FEATURE"
    assert metadata["summary"].startswith("Add push-to-talk")


def test_relocate_copies_prompt(tmp_path: Path) -> None:
    staging = tmp_path / "staging"
    pm_root = tmp_path / "project-management"
    storage = PromptStorage(staging, "{story_id}_prompt.md", "metadata.json")
    prompt = _sample_prompt()
    saved = storage.save(prompt, story_id="US-10")

    dest_prompt = storage.relocate_to_project_management(saved, pm_root, story_title="PTT Story")

    expected_dir = pm_root / "user-story-prompts" / "US-10"
    assert dest_prompt.exists()
    assert dest_prompt.parent == expected_dir
    assert (expected_dir / "metadata.json").exists()
    assert (expected_dir / "README.txt").read_text(encoding="utf-8").strip() == "PTT Story"
