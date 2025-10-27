from __future__ import annotations

import logging
import threading
import time
from typing import Callable, Optional

from .ptt_service import PTTOutcome, PTTService

LOGGER = logging.getLogger(__name__)


class PTTDaemon:
    """
    Blocking loop that keeps the PTT workflow ready for incoming hotkey presses.

    Each time the configured hotkey is pressed/released, a full capture → STT →
    enhancement → storage cycle executes. The daemon can run indefinitely or until
    `request_stop` is invoked (e.g., from a signal handler or test hook).
    """

    def __init__(
        self,
        service: PTTService,
        *,
        auto_move: bool = True,
        idle_sleep_seconds: float = 0.1,
        on_cycle: Optional[Callable[[PTTOutcome], None]] = None,
    ) -> None:
        self.service = service
        self.auto_move = auto_move
        self.idle_sleep_seconds = idle_sleep_seconds
        self.on_cycle = on_cycle
        self._stop_event = threading.Event()

    def request_stop(self) -> None:
        """Signal the daemon loop to exit after the current iteration."""

        self._stop_event.set()

    def run(self) -> None:
        """Run the daemon loop until `request_stop` is called or Ctrl+C is received."""

        LOGGER.info(
            "PTT daemon active: press %s to capture briefs. Press Ctrl+C to exit.",
            self.service.config.ptt.hotkey,
        )
        try:
            while not self._stop_event.is_set():
                try:
                    outcome = self.service.listen_once(auto_move=self.auto_move)
                    LOGGER.info(
                        "Prompt stored at %s (work type: %s)",
                        outcome.saved_prompt.prompt_path,
                        outcome.enhanced.work_type,
                    )
                    if self.on_cycle:
                        self.on_cycle(outcome)
                except KeyboardInterrupt:
                    raise
                except Exception as exc:
                    LOGGER.exception("PTT cycle failed: %s", exc)
                    time.sleep(self.idle_sleep_seconds)
        except KeyboardInterrupt:
            LOGGER.info("PTT daemon interrupted by user.")
        finally:
            self._stop_event.clear()
            LOGGER.info("PTT daemon shutting down.")

