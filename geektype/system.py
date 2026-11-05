"""Everything that talks to the desktop: clipboard, key presses, notifications.

Kept apart from the fix cycle so the cycle can be tested with a fake backend.
Every external command has a timeout, because ``wl-paste`` on GNOME can wait
forever when no window has focus.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import List, Optional, Sequence

from . import i18n

# Linux input event codes (linux/input-event-codes.h)
KEY_LEFTCTRL = 29
KEY_LEFTSHIFT = 42
KEY_INSERT = 110

COPY_CHORD = (KEY_LEFTCTRL, KEY_INSERT)     # Ctrl+Insert
PASTE_CHORD = (KEY_LEFTSHIFT, KEY_INSERT)   # Shift+Insert

TEXT_MIME = "text/plain;charset=utf-8"
SOCKET_NAME = "ydotool.sock"
RUNTIME_SOCKET = "/run/geektype/" + SOCKET_NAME
LEGACY_SOCKET = "/tmp/.ydotool_socket"      # used by GeekType v1
MAX_SNAPSHOT = 16 * 1024 * 1024
TIMEOUT = 1.5


class ToolMissing(Exception):
    """A command the cycle needs is not installed."""


class ToolFailed(Exception):
    """A command ran but did not do what was needed."""


def socket_path() -> str:
    """The ydotoold socket: ``YDOTOOL_SOCKET``, else the v2 path, else the v1 path."""
    configured = os.environ.get("YDOTOOL_SOCKET")
    if configured:
        return configured
    for candidate in (RUNTIME_SOCKET, LEGACY_SOCKET):
        if os.path.exists(candidate):
            return candidate
    return RUNTIME_SOCKET


class Snapshot(object):
    """What the clipboard held before GeekType used it."""

    def __init__(self, kind: str, mime: Optional[str] = None, data: Optional[bytes] = None) -> None:
        self.kind = kind          # "empty", "data" or "unknown"
        self.mime = mime
        self.data = data


class Backend(object):
    """The real desktop, through wl-clipboard, ydotool and notify-send."""

    def __init__(self) -> None:
        self.env = dict(os.environ)
        self.env["YDOTOOL_SOCKET"] = socket_path()

    # -- helpers ---------------------------------------------------------
    def _run(self, command: Sequence[str], data: Optional[bytes] = None, timeout: float = TIMEOUT):
        if shutil.which(command[0]) is None:
            raise ToolMissing(command[0])
        try:
            return subprocess.run(
                list(command), input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=timeout, env=self.env, check=False,
            )
        except subprocess.TimeoutExpired:
            return None

    # -- clipboard -------------------------------------------------------
    def read_text(self) -> Optional[str]:
        """The clipboard as text, or ``None`` if it holds no text."""
        result = self._run(["wl-paste", "--no-newline", "--type", "text"])
        if result is None or result.returncode != 0:
            return None
        return result.stdout.decode("utf-8", "replace")

    def snapshot(self) -> Snapshot:
        listing = self._run(["wl-paste", "--list-types"])
        if listing is None:
            return Snapshot("unknown")
        if listing.returncode != 0:
            if b"nothing is copied" in listing.stderr.lower():
                return Snapshot("empty")
            return Snapshot("unknown")
        types: List[str] = [line.strip() for line in listing.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
        text_types = [m for m in types if m.lower().startswith("text/plain")]
        if TEXT_MIME in types:
            mime = TEXT_MIME
        elif text_types:
            mime = text_types[0]
        else:
            others = [m for m in types if "/" in m and m.lower() != "text/html"]
            mime = others[0] if others else (types[0] if types else None)
        if mime is None:
            return Snapshot("unknown")
        result = self._run(["wl-paste", "--no-newline", "--type", mime], timeout=3.0)
        if result is None or result.returncode != 0 or len(result.stdout) > MAX_SNAPSHOT:
            return Snapshot("unknown")
        return Snapshot("data", mime, result.stdout)

    def write_text(self, text: str, primary: bool = False) -> None:
        self._write(text.encode("utf-8"), TEXT_MIME, primary)

    def _write(self, data: bytes, mime: str, primary: bool = False) -> None:
        command = ["wl-copy", "--type", mime]
        if primary:
            command.insert(1, "--primary")
        result = self._run(command, data)
        if result is None or result.returncode != 0:
            raise ToolFailed("wl-copy")

    def restore(self, snap: Snapshot) -> None:
        if snap.kind == "empty":
            self._run(["wl-copy", "--clear"])
        elif snap.kind == "data" and snap.mime is not None and snap.data is not None:
            self._write(snap.data, snap.mime)

    # -- keys ------------------------------------------------------------
    def press(self, chord: Sequence[int]) -> None:
        modifier, key = chord
        sequence = ["%d:1" % modifier, "%d:1" % key, "%d:0" % key, "%d:0" % modifier]
        result = self._run(["ydotool", "key"] + sequence)
        if result is None or result.returncode != 0:
            raise ToolFailed("ydotool")

    # -- notifications ---------------------------------------------------
    def notify(self, key: str) -> None:
        if shutil.which("notify-send") is None:
            return
        try:
            subprocess.run(
                ["notify-send", "--app-name=GeekType", "--icon=geektype", "--expire-time=2500",
                 "--hint=string:x-canonical-private-synchronous:geektype",
                 "GeekType", i18n.t(key, "notify")],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=TIMEOUT, check=False,
            )
        except subprocess.TimeoutExpired:
            pass
