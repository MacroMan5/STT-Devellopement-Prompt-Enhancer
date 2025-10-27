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
        "--auto-move",
        action="store_true",
        help="Immediately move prompt into project-management.",
    )

    enhance_text = subparsers.add_parser("enhance-text", help="Enhance a text brief directly.")
    enhance_text.add_argument("--text", help="Text brief to enhance.")
    enhance_text.add_argument("--file", type=Path, help="Path to a text file containing the brief.")
    enhance_text.add_argument("--story-id", help="Optional story ID override.")
    enhance_text.add_argument("--story-title", help="Optional story title.")
    enhance_text.add_argument(
        "--auto-move",
        action="store_true",
        help="Immediately move prompt into project-management.",
    )

    audio = subparsers.add_parser(
        "process-audio", help="Transcribe and enhance an existing audio file."
    )
    audio.add_argument("path", type=Path, help="Path to audio file (wav/mp3/flac).")
    audio.add_argument("--story-id", help="Optional story ID override.")
    audio.add_argument("--story-title", help="Optional story title.")
    audio.add_argument(
        "--auto-move",
        action="store_true",
        help="Immediately move prompt into project-management.",
    )

    create = subparsers.add_parser(
        "create-feature",
        help="Move a generated prompt into project-management.",
    )
    create.add_argument("prompt_path", type=Path, help="Path to enhanced prompt markdown file.")
    create.add_argument("--story-title", help="Optional story title for README.txt.")

    daemon = subparsers.add_parser("daemon", help="Run always-on PTT listener.")
    daemon.add_argument(
        "--stay-local",
        action="store_true",
        help="Keep prompts in staging directory instead of copying into project-management.",
    )
    daemon.add_argument(
        "--verbose-cycle",
        action="store_true",
        help="Print a summary to stdout after each capture.",
    )

    subparsers.add_parser("devices", help="List input audio devices and indices.")

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
    outcome = service.listen_once(
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=args.auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if args.auto_move:
        print("Prompt also copied into project-management workspace.")
    print(f"Detected work type: {outcome.enhanced.work_type}")
    print(f"Summary: {outcome.enhanced.summary}")
    return 0


def cmd_enhance_text(service: PTTService, args: argparse.Namespace) -> int:
    text = _load_text(args)
    outcome = service.enhance_text(
        text,
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=args.auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if args.auto_move:
        print("Prompt also copied into project-management workspace.")
    print(f"Detected work type: {outcome.enhanced.work_type}")
    return 0


def cmd_process_audio(service: PTTService, args: argparse.Namespace) -> int:
    outcome = service.process_audio_file(
        args.path,
        story_id=args.story_id,
        story_title=args.story_title,
        auto_move=args.auto_move,
    )
    print(f"Prompt saved to: {outcome.saved_prompt.prompt_path}")
    if args.auto_move:
        print("Prompt also copied into project-management workspace.")
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
    auto_move = not args.stay_local

    def _log_cycle(outcome):
        if args.verbose_cycle:
            print(
                f"Prompt stored at {outcome.saved_prompt.prompt_path} "
                f"({outcome.enhanced.work_type})"
            )

    daemon = PTTDaemon(
        service,
        auto_move=auto_move,
        on_cycle=_log_cycle if args.verbose_cycle else None,
    )
    daemon.run()
    return 0


def cmd_devices(_service: PTTService, _args: argparse.Namespace) -> int:
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


COMMAND_HANDLERS = {
    "listen": cmd_listen,
    "enhance-text": cmd_enhance_text,
    "process-audio": cmd_process_audio,
    "create-feature": cmd_create_feature,
    "daemon": cmd_daemon,
    "devices": cmd_devices,
    # registered at bottom
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    # Commands that do not require full service wiring
    if args.command == "devices":
        return cmd_devices(None, args)  # type: ignore[arg-type]
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
