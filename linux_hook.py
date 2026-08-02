#!/usr/bin/env python3
"""
GeekType - Linux (GNOME/Wayland) hook.

This script is meant to be triggered by a GNOME custom keyboard
shortcut bound to the Pause/Break key. Each run does one full
fix cycle:

    1. Simulate Ctrl+C to copy whatever text is currently selected
    2. Read the clipboard
    3. Run it through core.fix_layout()
    4. Write the result back to the clipboard
    5. Simulate Ctrl+V to paste the fixed text over the selection

Requires (install once):
    sudo apt install wl-clipboard
    sudo apt install ydotool ydotoold   # or build from source, see setup notes
    # ydotoold must be running (as a systemd service or manually)
    # your user must be able to talk to it (usually via the input group)

This file lives next to core.py - keep them in the same folder.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# ydotoold on this machine creates its socket at /tmp/.ydotool_socket
# instead of the client's default (/run/user/<uid>/.ydotool_socket),
# so we point the client at it explicitly.
_YDOTOOL_ENV = {**os.environ, "YDOTOOL_SOCKET": "/tmp/.ydotool_socket"}

# make sure core.py (in the same folder) is importable regardless of
# where this script is invoked from (GNOME runs shortcuts with cwd=~)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import fix_layout  # noqa: E402


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_clipboard() -> str:
    return run(["wl-paste", "--no-newline"])


def set_clipboard(text: str) -> None:
    subprocess.run(["wl-copy"], input=text, text=True)


def send_keys(*keys: str) -> None:
    # ydotool key syntax: e.g. "ctrl+c" needs keycodes; the simplest
    # reliable form is `ydotool key` with modifier down/up pairs.
    # 29 = ctrl, 46 = c, 47 = v  (standard Linux input event codes)
    codes = {
        "ctrl": 29,
        "c": 46,
        "v": 47,
    }
    sequence = []
    for k in keys:
        sequence.append(f"{codes[k]}:1")
    for k in reversed(keys):
        sequence.append(f"{codes[k]}:0")
    subprocess.run(["ydotool", "key", *sequence], env=_YDOTOOL_ENV)


def wait_for_clipboard_change(previous: str, timeout: float = 1.0) -> str | None:
    """Poll the clipboard until it differs from `previous`, or give up."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = get_clipboard()
        if current != previous:
            return current
        time.sleep(0.03)
    return None


def main() -> None:
    # give the user a moment to fully release the trigger hotkey
    # (e.g. Shift+Pause) before we send our own Ctrl+C - otherwise
    # a still-held Shift turns our Ctrl+C into Ctrl+Shift+C, which
    # is "Inspect Element" in Chrome and similar shortcuts elsewhere.
    time.sleep(0.3)

    # 1. copy current selection - but verify it actually landed in the
    # clipboard instead of guessing with a fixed delay. This is what
    # was causing the "pastes my previous clipboard item" bug.
    before = get_clipboard()
    send_keys("ctrl", "c")
    original = wait_for_clipboard_change(before, timeout=1.0)
    if original is None:
        return  # nothing got copied (no selection, or app too slow)

    fixed = fix_layout(original)
    if fixed == original:
        return  # nothing to do

    # 2. write back + paste
    set_clipboard(fixed)
    time.sleep(0.05)
    send_keys("ctrl", "v")

    # 3. let the user know it actually did something
    subprocess.run(
        ["notify-send", "-i", "input-keyboard", "-t", "1200", "GeekType", "متن اصلاح شد"],
    )

    # 3. quick visual confirmation that something happened
    notify(fixed)


def notify(fixed_text: str) -> None:
    preview = fixed_text if len(fixed_text) <= 40 else fixed_text[:40] + "…"
    subprocess.run(
        ["notify-send", "-t", "1200", "-i", "input-keyboard", "GeekType", preview]
    )


if __name__ == "__main__":
    main()
