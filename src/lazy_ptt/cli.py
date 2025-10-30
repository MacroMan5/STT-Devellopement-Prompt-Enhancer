from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import AppConfig, ConfigError, load_config
from .services.daemon import PTTDaemon
from .services.ptt_service import PTTService
from .audio.devices import list_input_devices


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="lazy_dev push-to-talk workflow")
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional path to overrides YAML (unused placeholder).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    listen = subparsers.add_parser("listen", help="Capture audio via push-to-talk hotkey.")
    listen.add_argument("--story-id", help="Override story ID for the saved prompt.")
    listen.add_argument(
        "--story-title",
        help="Optional story title to record in metadata.",
    )
    listen.add_argument(
        "--no-auto-move",
        action="store_true",
        help="Keep prompt in staging instead of moving to project-management (auto-move is DEFAULT).",
    )

    enhance_text = subparsers.add_parser("enhance-text", help="Enhance a text brief directly.")
    enhance_text.add_argument("--text", help="Text brief to enhance.")
    enhance_text.add_argument("--file", type=Path, help="Path to a text file containing the brief.")
    enhance_text.add_argument("--story-id", help="Optional story ID override.")
    enhance_text.add_argument("--story-title", help="Optional story title.")
    enhance_text.add_argument(
        "--no-auto-move",
        action="store_true",
        help="Keep prompt in staging instead of moving to project-management (auto-move is DEFAULT).",
    )

    audio = subparsers.add_parser(
        "process-audio", help="Transcribe and enhance an existing audio file."
    )
    audio.add_argument("path", type=Path, help="Path to audio file (wav/mp3/flac).")
    audio.add_argument("--story-id", help="Optional story ID override.")
    audio.add_argument("--story-title", help="Optional story title.")
    audio.add_argument(
        "--no-auto-move",
        action="store_true",
        help="Keep prompt in staging instead of moving to project-management (auto-move is DEFAULT).",
    )

    create = subparsers.add_parser(
        "create-feature",
        help="Move a generated prompt into project-management.",
    )
    create.add_argument("prompt_path", type=Path, help="Path to enhanced prompt markdown file.")
    create.add_argument("--story-title", help="Optional story title for README.txt.")

    daemon = subparsers.add_parser("daemon", help="Run always-on PTT listener.")
    daemon.add_argument(
        "--no-auto-move",
        action="store_true",
        help="Keep prompts in staging instead of moving to project-management (auto-move is DEFAULT).",
    )
    daemon.add_argument(
        "--verbose-cycle",
        action="store_true",
        help="Print a summary to stdout after each capture.",
    )

    subparsers.add_parser("devices", help="List input audio devices and indices.")

    init = subparsers.add_parser(
        "init",
        help="Initialize lazy-ptt in current working directory (creates config, checks dependencies).",
    )
    init.add_argument(
        "--no-download",
        action="store_true",
        help="Skip Whisper model download during initialization.",
    )

    return parser


def _load_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return args.file.read_text(encoding="utf-8")
    raise ConfigError("Provide --text or --file with content to enhance.")


def _resolve_config(args: argparse.Namespace) -> AppConfig:
    # Precedence: built-in defaults < --config YAML < environment variables.
    return load_config(args.config) if getattr(args, "config", None) else load_config()


def cmd_listen(service: PTTService, args: argparse.Namespace) -> int:
    print("Push-to-talk active. Hold the configured hotkey, speak, and release to process.")
    auto_move = not args.no_auto_move  # DEFAULT is True (auto-move enabled)
    outcome = service.listen_once(
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if auto_move:
        print("✅ Prompt saved to project-management workspace (auto-move enabled)")
    else:
        print("📦 Prompt kept in staging (use --no-auto-move to disable auto-move)")
    print(f"Detected work type: {outcome.enhanced.work_type}")
    print(f"Summary: {outcome.enhanced.summary}")
    return 0


def cmd_enhance_text(service: PTTService, args: argparse.Namespace) -> int:
    text = _load_text(args)
    auto_move = not args.no_auto_move  # DEFAULT is True (auto-move enabled)
    outcome = service.enhance_text(
        text,
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if auto_move:
        print("✅ Prompt saved to project-management workspace (auto-move enabled)")
    else:
        print("📦 Prompt kept in staging (use --no-auto-move to disable auto-move)")
    print(f"Detected work type: {outcome.enhanced.work_type}")
    return 0


def cmd_process_audio(service: PTTService, args: argparse.Namespace) -> int:
    auto_move = not args.no_auto_move  # DEFAULT is True (auto-move enabled)
    outcome = service.process_audio_file(
        args.path,
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if auto_move:
        print("✅ Prompt saved to project-management workspace (auto-move enabled)")
    else:
        print("📦 Prompt kept in staging (use --no-auto-move to disable auto-move)")
    print(f"Detected work type: {outcome.enhanced.work_type}")
    return 0


def cmd_create_feature(service: PTTService, args: argparse.Namespace) -> int:
    storage = service.storage
    saved = storage.load_saved_prompt(args.prompt_path)
    dest = storage.relocate_to_project_management(
        saved,
        service.config.paths.project_management_root,
        story_title=args.story_title,
    )
    print(f"Prompt moved to project-management: {dest}")
    return 0


def cmd_daemon(service: PTTService, args: argparse.Namespace) -> int:
    auto_move = not args.no_auto_move  # DEFAULT is True (auto-move enabled)

    def _log_cycle(outcome):
        if args.verbose_cycle:
            status = "✅ project-management" if auto_move else "📦 staging"
            print(
                f"[{status}] Prompt: {outcome.saved_prompt.prompt_path} "
                f"({outcome.enhanced.work_type})"
            )

    print(f"🎤 Daemon started. Press {service.config.ptt.hotkey} to capture voice anytime.")
    print(f"Auto-move: {'✅ ENABLED (saves to project-management)' if auto_move else '❌ DISABLED (saves to staging)'}")
    print(f"Working directory: {Path.cwd()}")
    print("")

    daemon = PTTDaemon(
        service,
        auto_move=auto_move,
        on_cycle=_log_cycle if args.verbose_cycle else None,
    )
    daemon.run()
    return 0


def cmd_devices(_service: PTTService | None, _args: argparse.Namespace) -> int:
    devices = list_input_devices()
    if not devices:
        print(
            "No input devices found or 'sounddevice' not installed. "
            "Install it and try again."
        )
        print(
            "To select a device, set env var PTT_INPUT_DEVICE_INDEX to the device index."
        )
        return 0
    print("Input devices:")
    for idx, name in devices:
        print(f"[{idx}] {name}")
    print(
        "\nSelect by setting env var, e.g.: "
        "PTT_INPUT_DEVICE_INDEX=0 lazy-ptt listen"
    )
    return 0


def cmd_init(_service: PTTService | None, args: argparse.Namespace) -> int:
    """Initialize lazy-ptt in current working directory."""
    import os
    import shutil

    cwd = Path.cwd()
    print(f"🎤 Initializing lazy-ptt in: {cwd}")
    print("")

    # 1. Check Python version
    print("1️⃣  Checking Python version...")
    import sys
    if sys.version_info < (3, 9):
        print(f"   ❌ Python 3.9+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
        return 1
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

    # 2. Check dependencies
    print("\n2️⃣  Checking dependencies...")
    deps_ok = True
    try:
        import sounddevice
        print("   ✅ sounddevice (audio capture)")
    except ImportError:
        print("   ❌ sounddevice not installed (install: pip install sounddevice)")
        deps_ok = False

    try:
        import pynput
        print("   ✅ pynput (hotkey detection)")
    except ImportError:
        print("   ❌ pynput not installed (install: pip install pynput)")
        deps_ok = False

    try:
        import openai
        print("   ✅ openai (prompt enhancement)")
    except ImportError:
        print("   ❌ openai not installed (install: pip install openai)")
        deps_ok = False

    if not deps_ok:
        print("\n⚠️  Missing dependencies. Install with: pip install lazy-ptt-enhancer[stt]")
        return 1

    # 3. Check audio devices
    print("\n3️⃣  Checking audio devices...")
    devices = list_input_devices()
    if not devices:
        print("   ⚠️  No audio devices found. Please check PortAudio installation.")
    else:
        print(f"   ✅ Found {len(devices)} audio input device(s)")
        for idx, name in devices[:3]:  # Show first 3
            print(f"      [{idx}] {name}")

    # 4. Create directory structure
    print("\n4️⃣  Creating directory structure...")
    pm_dir = cwd / "project-management" / "prompts"
    pm_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {pm_dir}")

    staging_dir = cwd / ".lazy-ptt" / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ {staging_dir}")

    # 5. Create .env file if not exists
    print("\n5️⃣  Creating configuration...")
    env_file = cwd / ".env"
    if not env_file.exists():
        env_content = """# lazy-ptt-enhancer configuration
# REQUIRED: OpenAI API key for prompt enhancement
OPENAI_API_KEY=sk-your-key-here

# OPTIONAL: Whisper configuration
WHISPER_MODEL_SIZE=medium
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=float16

# OPTIONAL: Audio configuration
PTT_HOTKEY=<f12>
# PTT_INPUT_DEVICE_INDEX=0

# OPTIONAL: Paths (defaults shown)
# PROJECT_MANAGEMENT_ROOT=./project-management
# PTT_OUTPUT_ROOT=./project-management/prompts
"""
        env_file.write_text(env_content)
        print(f"   ✅ {env_file} (template created)")
        print("      ⚠️  Set your OPENAI_API_KEY in .env file!")
    else:
        print(f"   ⏭️  {env_file} (already exists, skipping)")

    # 6. Download Whisper model (optional)
    if not args.no_download:
        print("\n6️⃣  Downloading Whisper model (this may take a few minutes)...")
        try:
            from faster_whisper import WhisperModel
            print("   📥 Downloading 'medium' model...")
            WhisperModel("medium", device="cpu", compute_type="int8")
            print("   ✅ Whisper model downloaded")
        except ImportError:
            print("   ⚠️  faster-whisper not installed. Install with: pip install faster-whisper")
        except Exception as e:
            print(f"   ⚠️  Model download failed: {e}")
            print("      Model will download on first use")
    else:
        print("\n6️⃣  Skipping Whisper model download (--no-download)")

    # 7. Check environment variables
    print("\n7️⃣  Checking environment...")
    if os.getenv("OPENAI_API_KEY"):
        print("   ✅ OPENAI_API_KEY is set")
    else:
        print("   ⚠️  OPENAI_API_KEY not set (add to .env or export)")

    # Done!
    print("\n" + "="*60)
    print("✅ Initialization complete!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Set your OPENAI_API_KEY in .env file")
    print("2. Start daemon: lazy-ptt daemon --verbose-cycle")
    print(f"3. Press F12 to capture voice input anytime")
    print(f"4. Prompts will be saved to: {pm_dir}")
    print("\n💡 Tip: Run 'lazy-ptt devices' to see available microphones")
    print("")

    return 0


COMMAND_HANDLERS = {
    "listen": cmd_listen,
    "enhance-text": cmd_enhance_text,
    "process-audio": cmd_process_audio,
    "create-feature": cmd_create_feature,
    "daemon": cmd_daemon,
    "devices": cmd_devices,
    "init": cmd_init,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    # Commands that do not require full service wiring
    if args.command in ("devices", "init"):
        return COMMAND_HANDLERS[args.command](None, args)
    try:
        config = _resolve_config(args)
        service = PTTService.from_config(config)
    except ConfigError as exc:
        parser.error(str(exc))
        return 2
    handler = COMMAND_HANDLERS[args.command]
    return handler(service, args)


if __name__ == "__main__":
    sys.exit(main())
