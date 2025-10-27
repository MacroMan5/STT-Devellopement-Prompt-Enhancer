from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv
try:  # Python 3.9+ importlib.resources modern API
    from importlib.resources import files as _res_files  # type: ignore
except Exception:  # pragma: no cover - fallback for very old Python
    _res_files = None  # type: ignore


@dataclass(frozen=True)
class ProjectPaths:
    """Resolved filesystem locations used by the workflow."""

    repository_root: Path
    project_management_root: Path
    prompt_output_root: Path


@dataclass(frozen=True)
class PTTConfig:
    """Microphone and hotkey settings for push-to-talk recording."""

    language: str
    sample_rate: int
    chunk_duration_ms: int
    silence_threshold: float
    max_record_seconds: int
    hotkey: str
    input_device_index: Optional[int]


@dataclass(frozen=True)
class WhisperConfig:
    """Local Whisper inference settings."""

    model_size: str
    device: str
    compute_type: str
    download_root: Path


@dataclass(frozen=True)
class OpenAIConfig:
    """Configuration for the OpenAI client that performs prompt enhancement."""

    api_key: str
    model: str
    temperature: float
    max_output_tokens: int
    base_url: Optional[str]


@dataclass(frozen=True)
class PromptConfig:
    """Settings that control how enhanced prompts are written to disk."""

    filename_pattern: str
    metadata_filename: str


@dataclass(frozen=True)
class AppConfig:
    """Aggregate configuration used by the PTT workflow."""

    paths: ProjectPaths
    ptt: PTTConfig
    whisper: WhisperConfig
    openai: OpenAIConfig
    prompt: PromptConfig


DEFAULT_CONFIG_PATH = Path("config") / "defaults.yaml"


class ConfigError(RuntimeError):
    """Raised when mandatory configuration values are missing or invalid."""


def _load_yaml(path: Path, *, strict: bool) -> Dict[str, Any]:
    """Load YAML file; optionally error if missing/invalid."""

    if not path.exists():
        if strict:
            raise ConfigError(f"Configuration file not found: {path}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc


def _load_builtin_defaults() -> Dict[str, Any]:
    """Load defaults shipped inside the package (works for wheels/sdists)."""

    # Expect file at lazy_ptt/data/defaults.yaml
    if _res_files is None:
        return {}
    try:
        res = _res_files("lazy_ptt").joinpath("data").joinpath("defaults.yaml")
        with res.open("r", encoding="utf-8") as handle:  # type: ignore[attr-defined]
            return yaml.safe_load(handle) or {}
    except FileNotFoundError:
        return {}
    except Exception as exc:  # pragma: no cover - defensive
        raise ConfigError(f"Failed to load built-in defaults: {exc}") from exc


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Shallow+recursive merge for small nested config dicts."""

    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)  # type: ignore[arg-type]
        else:
            result[k] = v
    return result


def _coerce_int(value: Optional[str], default: int) -> int:
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"Expected integer value, received {value!r}") from exc


def _coerce_float(value: Optional[str], default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ConfigError(f"Expected float value, received {value!r}") from exc


def _optional_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _resolve_base_dir() -> Path:
    """Determine the root directory for relative outputs and caches."""

    override = os.getenv("LAZY_PTT_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.cwd().resolve()


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """Load configuration with precedence: built-in defaults < file overrides < env vars.

    - Built-in defaults are packaged at lazy_ptt/data/defaults.yaml.
    - If `config_path` is provided, its values overlay built-ins (strict load).
    - Else, if repo-local config/defaults.yaml exists, overlay it (lenient load).
    - Environment variables finally override everything.
    """

    load_dotenv()
    defaults = _load_builtin_defaults()
    if config_path is not None:
        defaults = _deep_merge(defaults, _load_yaml(config_path, strict=True))
    elif DEFAULT_CONFIG_PATH.exists():
        defaults = _deep_merge(defaults, _load_yaml(DEFAULT_CONFIG_PATH, strict=False))

    base_dir = _resolve_base_dir()
    project_management_root_env = os.getenv("PROJECT_MANAGEMENT_ROOT")
    if project_management_root_env:
        project_management_root = Path(project_management_root_env).expanduser().resolve()
    else:
        project_management_root = (base_dir / "project-management").resolve()

    prompt_output_root_env = os.getenv("PTT_OUTPUT_ROOT")
    if prompt_output_root_env:
        prompt_output_root = Path(prompt_output_root_env).expanduser().resolve()
    else:
        prompt_output_root = (
            base_dir
            / defaults.get("ptt", {}).get("output_root", "outputs/prompts")
        ).resolve()

    ptt_defaults = defaults.get("ptt", {})
    whisper_defaults = defaults.get("whisper", {})
    openai_defaults = defaults.get("openai", {})
    prompt_defaults = defaults.get("prompt", {})

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ConfigError(
            "OPENAI_API_KEY is not set. "
            "Provide it via environment variable or .env file."
        )

    paths = ProjectPaths(
        repository_root=base_dir,
        project_management_root=project_management_root,
        prompt_output_root=prompt_output_root,
    )

    ptt_config = PTTConfig(
        language=os.getenv("PTT_LANGUAGE", ptt_defaults.get("language", "en")),
        sample_rate=_coerce_int(os.getenv("PTT_SAMPLE_RATE"), ptt_defaults.get("sample_rate", 16_000)),
        chunk_duration_ms=_coerce_int(
            os.getenv("PTT_CHUNK_DURATION_MS"), ptt_defaults.get("chunk_duration_ms", 64)
        ),
        silence_threshold=_coerce_float(
            os.getenv("PTT_SILENCE_THRESHOLD"), ptt_defaults.get("silence_threshold", 0.015)
        ),
        max_record_seconds=_coerce_int(
            os.getenv("PTT_MAX_RECORD_SECONDS"), ptt_defaults.get("max_record_seconds", 120)
        ),
        hotkey=os.getenv("PTT_HOTKEY", ptt_defaults.get("hotkey", "space")),
        input_device_index=_coerce_int(os.getenv("PTT_INPUT_DEVICE_INDEX"), -1) if os.getenv("PTT_INPUT_DEVICE_INDEX") else None,
    )

    whisper_config = WhisperConfig(
        model_size=os.getenv("WHISPER_MODEL_SIZE", whisper_defaults.get("model_size", "medium")),
        device=os.getenv("WHISPER_DEVICE", whisper_defaults.get("device", "cuda")),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", whisper_defaults.get("compute_type", "float16")),
        download_root=(base_dir / whisper_defaults.get("download_root", ".cache/whisper")).resolve(),
    )

    openai_config = OpenAIConfig(
        api_key=openai_api_key,
        model=os.getenv("OPENAI_MODEL", openai_defaults.get("model", "gpt-4o-mini")),
        temperature=_coerce_float(
            os.getenv("OPENAI_TEMPERATURE"), openai_defaults.get("temperature", 0.2)
        ),
        max_output_tokens=_coerce_int(
            os.getenv("OPENAI_MAX_OUTPUT_TOKENS"), openai_defaults.get("max_output_tokens", 1800)
        ),
        base_url=_optional_str(os.getenv("OPENAI_BASE_URL")),
    )

    prompt_config = PromptConfig(
        filename_pattern=os.getenv(
            "PTT_PROMPT_FILENAME_PATTERN",
            prompt_defaults.get("filename_pattern", "{story_id}_enhanced-prompt.md"),
        ),
        metadata_filename=os.getenv(
            "PTT_PROMPT_METADATA_FILENAME",
            prompt_defaults.get("metadata_filename", "prompt-metadata.json"),
        ),
    )

    return AppConfig(paths=paths, ptt=ptt_config, whisper=whisper_config, openai=openai_config, prompt=prompt_config)


def dump_config(config: AppConfig) -> Dict[str, Any]:
    """Helper for debugging and unit tests."""

    return {
        "paths": {
            "repository_root": str(config.paths.repository_root),
            "project_management_root": str(config.paths.project_management_root),
            "prompt_output_root": str(config.paths.prompt_output_root),
        },
        "ptt": config.ptt.__dict__,
        "whisper": {
            **config.whisper.__dict__,
            "download_root": str(config.whisper.download_root),
        },
        "openai": config.openai.__dict__,
        "prompt": config.prompt.__dict__,
    }


def export_config(config: AppConfig, destination: Path) -> None:
    """Export the resolved configuration to a JSON file for inspection."""

    data = dump_config(config)
    destination.write_text(json.dumps(data, indent=2), encoding="utf-8")
