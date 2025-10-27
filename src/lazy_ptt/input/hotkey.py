from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Optional

try:
    from pynput import keyboard
except Exception:  # pragma: no cover - allow import in headless CI
    keyboard = None  # type: ignore


class HotkeyListenerError(RuntimeError):
    """Raised when the hotkey listener encounters an unrecoverable error."""


@dataclass
class HotkeyCallbacks:
    """Callback container used by `HotkeyListener`."""

    on_press: Callable[[], None]
    on_release: Callable[[], None]


class HotkeyListener:
    """Minimal wrapper around pynput's keyboard listener for push-to-talk."""

    def __init__(self, hotkey: str = "space") -> None:
        self.hotkey = hotkey.lower()
        self._listener: Optional[keyboard.Listener] = None
        self._is_active = threading.Event()

    def _matches_hotkey(self, key: keyboard.Key | keyboard.KeyCode) -> bool:
        if isinstance(key, keyboard.Key):
            return key.name == self.hotkey
        if isinstance(key, keyboard.KeyCode):
            return key.char == self.hotkey
        return False

    def start(self, callbacks: HotkeyCallbacks) -> None:
        """Begin listening for hotkey events."""

        if self._listener is not None:
            raise HotkeyListenerError("Hotkey listener already running")
        if keyboard is None:
            raise HotkeyListenerError(
                "pynput is unavailable or no GUI backend is present; hotkey listening is disabled."
            )

        def on_press(key: keyboard.Key | keyboard.KeyCode) -> None:
            if self._matches_hotkey(key):
                callbacks.on_press()

        def on_release(key: keyboard.Key | keyboard.KeyCode) -> bool:
            if self._matches_hotkey(key):
                callbacks.on_release()
            return False  # allow listener to terminate on release

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        self._is_active.set()

    def join(self) -> None:
        """Block until the listener thread has finished."""

        if self._listener is None:
            return
        self._listener.join()
        self._listener = None
        self._is_active.clear()

    def stop(self) -> None:
        """Stop listening for hotkey events."""

        if self._listener:
            self._listener.stop()
            self._listener = None
        self._is_active.clear()

    def is_running(self) -> bool:
        return self._is_active.is_set()
