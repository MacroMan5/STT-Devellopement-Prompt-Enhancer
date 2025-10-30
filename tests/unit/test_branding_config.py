"""Tests for branding configuration functionality.

This module tests the BrandingConfig dataclass and its integration with
the prompt enhancement system, ensuring backward compatibility and
configurability of footer attribution.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

import pytest

from lazy_ptt.config import (
    AppConfig,
    BrandingConfig,
    ConfigError,
    _coerce_bool,
    _sanitize_markdown_text,
    _validate_url,
    load_config,
)
from lazy_ptt.prompt.enhancer import EnhancedPrompt, PromptSection


class TestBrandingConfig:
    """Test suite for BrandingConfig dataclass and integration."""

    def test_branding_config_default_values(self) -> None:
        """Test that BrandingConfig has sensible defaults matching current output."""
        config = BrandingConfig(
            enabled=True,
            emoji="🎤",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )

        assert config.enabled is True
        assert config.emoji == "🎤"
        assert config.author == "@therouxe"
        assert config.repo_url == "https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer"
        assert config.author_url == "https://github.com/therouxe"

    def test_branding_config_is_frozen(self) -> None:
        """Test that BrandingConfig dataclass is immutable."""
        config = BrandingConfig(
            enabled=True,
            emoji="🎤",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )

        with pytest.raises(AttributeError):
            config.enabled = False  # type: ignore[misc]

    def test_branding_config_custom_values(self) -> None:
        """Test BrandingConfig with custom values."""
        config = BrandingConfig(
            enabled=True,
            emoji="🚀",
            author="@customuser",
            repo_url="https://github.com/customuser/custom-repo",
            author_url="https://github.com/customuser",
        )

        assert config.emoji == "🚀"
        assert config.author == "@customuser"
        assert config.repo_url == "https://github.com/customuser/custom-repo"

    def test_branding_config_disabled(self) -> None:
        """Test BrandingConfig with branding disabled."""
        config = BrandingConfig(
            enabled=False,
            emoji="🎤",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )

        assert config.enabled is False


class TestEnhancedPromptBranding:
    """Test suite for EnhancedPrompt branding footer rendering."""

    def _create_sample_prompt(self, branding: BrandingConfig | None = None) -> EnhancedPrompt:
        """Helper to create a sample EnhancedPrompt for testing."""
        return EnhancedPrompt(
            work_type="FEATURE",
            summary="Test feature",
            objectives=["Objective 1"],
            risks=["Risk 1"],
            milestones=["Milestone 1"],
            sections=[PromptSection(title="Details", content="Test content")],
            acceptance_criteria=["Criterion 1"],
            suggested_story_id="US-1.0",
            original_brief="Test brief",
            branding=branding,
        )

    def test_enhanced_prompt_default_branding_footer(self) -> None:
        """Test that default branding matches current hardcoded footer exactly."""
        branding = BrandingConfig(
            enabled=True,
            emoji="🎤",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )
        prompt = self._create_sample_prompt(branding)
        markdown = prompt.to_markdown()

        # Verify exact footer content
        assert "---" in markdown
        assert "🎤 **Generated with [lazy-ptt-enhancer](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer)**" in markdown
        assert "Created by [@therouxe](https://github.com/therouxe) | Powered by Whisper + OpenAI" in markdown
        assert "[⭐ Star on GitHub](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer)" in markdown
        assert "[📖 Documentation](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer#readme)" in markdown
        assert "[🐛 Report Issues](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer/issues)" in markdown

    def test_enhanced_prompt_custom_branding_footer(self) -> None:
        """Test that custom branding values are reflected in footer."""
        branding = BrandingConfig(
            enabled=True,
            emoji="🚀",
            author="@customuser",
            repo_url="https://github.com/customuser/custom-repo",
            author_url="https://github.com/customuser",
        )
        prompt = self._create_sample_prompt(branding)
        markdown = prompt.to_markdown()

        # Verify custom values in footer
        assert "🚀 **Generated with [lazy-ptt-enhancer](https://github.com/customuser/custom-repo)**" in markdown
        assert "Created by [@customuser](https://github.com/customuser)" in markdown
        assert "[⭐ Star on GitHub](https://github.com/customuser/custom-repo)" in markdown
        assert "[📖 Documentation](https://github.com/customuser/custom-repo#readme)" in markdown
        assert "[🐛 Report Issues](https://github.com/customuser/custom-repo/issues)" in markdown

    def test_enhanced_prompt_disabled_branding(self) -> None:
        """Test that footer is omitted when branding is disabled."""
        branding = BrandingConfig(
            enabled=False,
            emoji="🎤",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )
        prompt = self._create_sample_prompt(branding)
        markdown = prompt.to_markdown()

        # Verify footer is NOT present
        assert "🎤 **Generated with" not in markdown
        assert "Created by [@therouxe]" not in markdown
        assert "[⭐ Star on GitHub]" not in markdown

        # But original content is still there
        assert "# FEATURE Plan" in markdown
        assert "Test brief" in markdown

    def test_enhanced_prompt_no_branding_config(self) -> None:
        """Test backward compatibility when branding config is None (default behavior)."""
        prompt = self._create_sample_prompt(branding=None)
        markdown = prompt.to_markdown()

        # Should still render default footer for backward compatibility
        assert "🎤 **Generated with [lazy-ptt-enhancer](https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer)**" in markdown

    def test_enhanced_prompt_empty_emoji(self) -> None:
        """Test footer with empty emoji string."""
        branding = BrandingConfig(
            enabled=True,
            emoji="",
            author="@therouxe",
            repo_url="https://github.com/MacroMan5/STT-Devellopement-Prompt-Enhancer",
            author_url="https://github.com/therouxe",
        )
        prompt = self._create_sample_prompt(branding)
        markdown = prompt.to_markdown()

        # Footer should work without emoji
        assert "**Generated with [lazy-ptt-enhancer]" in markdown
        assert "🎤" not in markdown


class TestBrandingConfigLoading:
    """Test suite for loading BrandingConfig from YAML and environment variables."""

    def test_load_config_with_default_branding(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that load_config includes default branding configuration."""
        # Create minimal YAML config
        config_file = tmp_path / "defaults.yaml"
        config_file.write_text(
            """
ptt:
  language: en
whisper:
  model_size: tiny
openai:
  model: gpt-4o-mini
""",
            encoding="utf-8",
        )

        # Set required environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

        # Load config
        config = load_config(config_file)

        # Verify branding config exists with defaults
        assert hasattr(config, "branding")
        assert config.branding.enabled is True
        assert config.branding.emoji == "🎤"
        assert config.branding.author == "@therouxe"

    def test_load_config_with_custom_branding_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading custom branding from YAML config."""
        config_file = tmp_path / "defaults.yaml"
        config_file.write_text(
            """
ptt:
  language: en
whisper:
  model_size: tiny
openai:
  model: gpt-4o-mini
branding:
  enabled: true
  emoji: "🚀"
  author: "@customuser"
  repo_url: "https://github.com/customuser/custom-repo"
  author_url: "https://github.com/customuser"
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        config = load_config(config_file)

        assert config.branding.emoji == "🚀"
        assert config.branding.author == "@customuser"
        assert config.branding.repo_url == "https://github.com/customuser/custom-repo"

    def test_load_config_with_disabled_branding_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test disabling branding via YAML config."""
        config_file = tmp_path / "defaults.yaml"
        config_file.write_text(
            """
ptt:
  language: en
whisper:
  model_size: tiny
openai:
  model: gpt-4o-mini
branding:
  enabled: false
""",
            encoding="utf-8",
        )

        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        config = load_config(config_file)

        assert config.branding.enabled is False

    def test_load_config_with_env_var_overrides(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override YAML branding config."""
        config_file = tmp_path / "defaults.yaml"
        config_file.write_text(
            """
ptt:
  language: en
whisper:
  model_size: tiny
openai:
  model: gpt-4o-mini
branding:
  enabled: true
  emoji: "🎤"
  author: "@therouxe"
""",
            encoding="utf-8",
        )

        # Set environment overrides
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setenv("BRANDING_ENABLED", "false")
        monkeypatch.setenv("BRANDING_EMOJI", "🔥")
        monkeypatch.setenv("BRANDING_AUTHOR", "@envuser")
        monkeypatch.setenv("BRANDING_REPO_URL", "https://github.com/envuser/env-repo")
        monkeypatch.setenv("BRANDING_AUTHOR_URL", "https://github.com/envuser")

        config = load_config(config_file)

        # Environment variables should override YAML
        assert config.branding.enabled is False
        assert config.branding.emoji == "🔥"
        assert config.branding.author == "@envuser"
        assert config.branding.repo_url == "https://github.com/envuser/env-repo"
        assert config.branding.author_url == "https://github.com/envuser"

    def test_load_config_partial_env_overrides(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that partial env overrides work (only some values set)."""
        config_file = tmp_path / "defaults.yaml"
        config_file.write_text(
            """
ptt:
  language: en
whisper:
  model_size: tiny
openai:
  model: gpt-4o-mini
branding:
  enabled: true
  emoji: "🎤"
  author: "@yamluser"
""",
            encoding="utf-8",
        )

        # Only override author via env
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setenv("BRANDING_AUTHOR", "@envuser")

        config = load_config(config_file)

        # Author should be from env, others from YAML
        assert config.branding.enabled is True
        assert config.branding.emoji == "🎤"
        assert config.branding.author == "@envuser"


class TestBrandingConfigIntegration:
    """Integration tests for branding config with PromptEnhancer."""

    def test_prompt_enhancer_uses_branding_config(self) -> None:
        """Test that PromptEnhancer passes branding config to EnhancedPrompt."""
        from lazy_ptt.config import OpenAIConfig
        from lazy_ptt.prompt.enhancer import PromptEnhancer

        # Mock OpenAI client
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
            def __init__(self, payload: Dict[str, Any]) -> None:
                self._payload = payload

            def create(self, **_: object) -> _FakeResponse:
                return _FakeResponse(json.dumps(self._payload))

        class _FakeOpenAIClient:
            def __init__(self, payload: Dict[str, Any]) -> None:
                self.responses = _FakeResponsesClient(payload)

        payload = {
            "work_type": "FEATURE",
            "summary": "Test feature",
            "objectives": ["Objective 1"],
            "risks": ["Risk 1"],
            "recommended_milestones": ["Milestone 1"],
            "sections": [{"title": "Details", "content": "Content"}],
            "acceptance_criteria": ["Criterion 1"],
            "suggested_story_id": "US-1.0",
        }

        openai_config = OpenAIConfig(
            api_key="test-key",
            model="test-model",
            temperature=0.0,
            max_output_tokens=500,
            base_url=None,
        )

        branding_config = BrandingConfig(
            enabled=True,
            emoji="🚀",
            author="@testuser",
            repo_url="https://github.com/testuser/test-repo",
            author_url="https://github.com/testuser",
        )

        client = _FakeOpenAIClient(payload)
        enhancer = PromptEnhancer(openai_config, branding=branding_config, client=client)  # type: ignore[arg-type]
        result = enhancer.enhance("Test brief")

        # Verify branding is in the result
        markdown = result.to_markdown()
        assert "🚀 **Generated with [lazy-ptt-enhancer](https://github.com/testuser/test-repo)**" in markdown
        assert "[@testuser](https://github.com/testuser)" in markdown


class TestCoerceBoolEdgeCases:
    """Test suite for _coerce_bool helper function edge cases."""

    def test_coerce_bool_valid_true_values(self) -> None:
        """Test all valid truthy values are accepted."""
        assert _coerce_bool("true", False) is True
        assert _coerce_bool("1", False) is True
        assert _coerce_bool("yes", False) is True
        assert _coerce_bool("on", False) is True

    def test_coerce_bool_valid_false_values(self) -> None:
        """Test all valid falsy values are accepted."""
        assert _coerce_bool("false", True) is False
        assert _coerce_bool("0", True) is False
        assert _coerce_bool("no", True) is False
        assert _coerce_bool("off", True) is False

    def test_coerce_bool_case_insensitive(self) -> None:
        """Test that values are case-insensitive."""
        assert _coerce_bool("TRUE", False) is True
        assert _coerce_bool("FALSE", True) is False
        assert _coerce_bool("Yes", False) is True
        assert _coerce_bool("NO", True) is False
        assert _coerce_bool("True", False) is True
        assert _coerce_bool("FaLsE", True) is False

    def test_coerce_bool_whitespace_handling(self) -> None:
        """Test that leading/trailing whitespace is handled."""
        assert _coerce_bool(" true ", False) is True
        assert _coerce_bool("  1  ", False) is True
        assert _coerce_bool(" false ", True) is False
        assert _coerce_bool("  0  ", True) is False

    def test_coerce_bool_none_returns_default(self) -> None:
        """Test that None returns the default value."""
        assert _coerce_bool(None, True) is True
        assert _coerce_bool(None, False) is False

    def test_coerce_bool_empty_string_returns_default(self) -> None:
        """Test that empty string returns the default value."""
        assert _coerce_bool("", True) is True
        assert _coerce_bool("", False) is False

    def test_coerce_bool_invalid_values_raise_error(self) -> None:
        """Test that invalid boolean values raise ConfigError."""
        with pytest.raises(ConfigError, match="Expected boolean value"):
            _coerce_bool("maybe", False)

        with pytest.raises(ConfigError, match="Expected boolean value"):
            _coerce_bool("2", False)

        with pytest.raises(ConfigError, match="Expected boolean value"):
            _coerce_bool("invalid", True)

        with pytest.raises(ConfigError, match="Expected boolean value"):
            _coerce_bool("truee", False)


class TestValidateUrl:
    """Test suite for _validate_url security validation function."""

    def test_validate_url_valid_https(self) -> None:
        """Test that valid HTTPS URLs are accepted."""
        url = "https://github.com/user/repo"
        assert _validate_url(url, "test_field") == url

    def test_validate_url_valid_http(self) -> None:
        """Test that valid HTTP URLs are accepted."""
        url = "http://example.com/path"
        assert _validate_url(url, "test_field") == url

    def test_validate_url_empty_raises_error(self) -> None:
        """Test that empty URL raises ConfigError."""
        with pytest.raises(ConfigError, match="test_field cannot be empty"):
            _validate_url("", "test_field")

    def test_validate_url_missing_scheme_raises_error(self) -> None:
        """Test that URL without scheme raises ConfigError."""
        with pytest.raises(ConfigError, match="must use http or https scheme"):
            _validate_url("github.com/user/repo", "test_field")

    def test_validate_url_invalid_scheme_raises_error(self) -> None:
        """Test that URL with invalid scheme raises ConfigError."""
        with pytest.raises(ConfigError, match="must use http or https scheme"):
            _validate_url("ftp://example.com", "test_field")

        with pytest.raises(ConfigError, match="must use http or https scheme"):
            _validate_url("javascript:alert(1)", "test_field")

    def test_validate_url_missing_netloc_raises_error(self) -> None:
        """Test that URL without domain raises ConfigError."""
        with pytest.raises(ConfigError, match="must have a valid domain"):
            _validate_url("https://", "test_field")

    def test_validate_url_injection_characters_raise_error(self) -> None:
        """Test that URLs with injection characters raise ConfigError."""
        with pytest.raises(ConfigError, match="contains invalid characters"):
            _validate_url("https://example.com\nmalicious", "test_field")

        with pytest.raises(ConfigError, match="contains invalid characters"):
            _validate_url("https://example.com<script>", "test_field")

        with pytest.raises(ConfigError, match="contains invalid characters"):
            _validate_url("https://example.com\r\n", "test_field")

        with pytest.raises(ConfigError, match="contains invalid characters"):
            _validate_url("https://example.com\tpath", "test_field")


class TestSanitizeMarkdownText:
    """Test suite for _sanitize_markdown_text sanitization function."""

    def test_sanitize_markdown_text_safe_text(self) -> None:
        """Test that safe text passes through unchanged."""
        text = "@therouxe"
        assert _sanitize_markdown_text(text, "test_field") == text

    def test_sanitize_markdown_text_empty_string(self) -> None:
        """Test that empty string is handled safely."""
        assert _sanitize_markdown_text("", "test_field") == ""

    def test_sanitize_markdown_text_escapes_brackets(self) -> None:
        """Test that markdown brackets are escaped."""
        text = "@user[test]"
        result = _sanitize_markdown_text(text, "test_field")
        assert result == "@user\\[test\\]"

    def test_sanitize_markdown_text_escapes_parentheses(self) -> None:
        """Test that markdown parentheses are escaped."""
        text = "@user(test)"
        result = _sanitize_markdown_text(text, "test_field")
        assert result == "@user\\(test\\)"

    def test_sanitize_markdown_text_newlines_raise_error(self) -> None:
        """Test that newlines raise ConfigError."""
        with pytest.raises(ConfigError, match="contains invalid characters"):
            _sanitize_markdown_text("@user\nmalicious", "test_field")

    def test_sanitize_markdown_text_html_chars_raise_error(self) -> None:
        """Test that HTML-like characters raise ConfigError."""
        with pytest.raises(ConfigError, match="contains invalid characters"):
            _sanitize_markdown_text("@user<script>", "test_field")

        with pytest.raises(ConfigError, match="contains invalid characters"):
            _sanitize_markdown_text("@user>test", "test_field")

    def test_sanitize_markdown_text_tabs_raise_error(self) -> None:
        """Test that tabs raise ConfigError."""
        with pytest.raises(ConfigError, match="contains invalid characters"):
            _sanitize_markdown_text("@user\ttest", "test_field")
