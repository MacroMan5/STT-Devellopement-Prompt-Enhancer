from __future__ import annotations

from typing import List, Tuple

try:
    import sounddevice as sd  # type: ignore
except (ImportError, OSError):  # pragma: no cover - handle missing library or PortAudio
    sd = None


class DeviceError(RuntimeError):
    pass


def list_input_devices() -> List[Tuple[int, str]]:
    """Return list of (index, name) for input-capable devices.

    If sounddevice is unavailable, returns an empty list.
    """

    if sd is None:
        return []
    devices = []
    for idx, info in enumerate(sd.query_devices()):  # type: ignore[attr-defined]
        try:
            if info.get("max_input_channels", 0) > 0:
                devices.append((idx, info.get("name", f"Device {idx}")))
        except (KeyError, AttributeError, TypeError):
            # Skip malformed device entries returned by backend
            continue
    return devices
