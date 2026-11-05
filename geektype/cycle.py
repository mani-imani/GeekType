"""The F9 cycle: copy the selection, convert it, paste it back.

Order of events (every step has a reason, see the comments):

1. Take a lock, so two quick F9 presses never overlap.
2. Snapshot the clipboard so it can be restored afterwards.
3. Put a unique marker in the clipboard. If the clipboard still holds the
   marker after Ctrl+Insert, nothing was selected. This replaces guessing from
   old clipboard content, which is how v1 could paste stale text.
4. Convert, write the result to the clipboard and the primary selection, and
   paste with Shift+Insert. Ctrl+Insert / Shift+Insert are used instead of
   Ctrl+C / Ctrl+V because terminals treat Ctrl+C as an interrupt.
5. Read the clipboard back to confirm the result is what is about to be
   pasted, then restore the original clipboard after a delay.
"""

from __future__ import annotations

import fcntl
import logging
import os
import time
import uuid
from typing import Callable, Optional

from . import core, system

log = logging.getLogger("geektype")

# Seconds. Wayland apps need a moment to react to a synthetic key press.
KEY_SETTLE = 0.08
COPY_WAIT = 1.0
POLL = 0.03
PASTE_SETTLE = 0.25
RESTORE_DELAY = 0.15

# Outcomes (also the notification keys, except "ok" which maps to "fixed").
OK = "ok"
NO_SELECTION = "no_selection"
NOTHING = "nothing_to_fix"
MISSING = "tool_missing"
FAILED = "failed"
BUSY = "busy"

NOTIFY_KEY = {OK: "fixed", NO_SELECTION: "no_selection", NOTHING: "nothing_to_fix",
              MISSING: "tool_missing", FAILED: "failed"}


def lock_path() -> str:
    base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    return os.path.join(base, "geektype.lock")


class Lock(object):
    """A non-blocking single-instance lock (released when the process ends)."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or lock_path()
        self.handle = None

    def acquire(self) -> bool:
        self.handle = open(self.path, "w")
        try:
            fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.handle.close()
            self.handle = None
            return False
        return True

    def release(self) -> None:
        if self.handle is not None:
            try:
                fcntl.flock(self.handle, fcntl.LOCK_UN)
            finally:
                self.handle.close()
                self.handle = None


def _wait_for(read: Callable[[], Optional[str]], done: Callable[[Optional[str]], bool],
              timeout: float, sleep: Callable[[float], None], clock: Callable[[], float]) -> Optional[str]:
    deadline = clock() + timeout
    value = read()
    while not done(value) and clock() < deadline:
        sleep(POLL)
        value = read()
    return value


def run_cycle(backend, sleep: Callable[[float], None] = time.sleep,
              clock: Callable[[], float] = time.monotonic) -> str:
    """Run one fix and return an outcome constant. Never raises."""
    marker = "geektype-" + uuid.uuid4().hex
    snapshot = None
    try:
        snapshot = backend.snapshot()
        backend.write_text(marker)
        sleep(KEY_SETTLE)
        backend.press(system.COPY_CHORD)
        copied = _wait_for(backend.read_text, lambda v: v is not None and v != marker,
                           COPY_WAIT, sleep, clock)
        if copied is None or copied == marker or copied == "":
            _restore(backend, snapshot)
            return NO_SELECTION

        fixed, direction = core.convert(copied)
        if direction is None or fixed == copied:
            _restore(backend, snapshot)
            return NOTHING

        backend.write_text(fixed, primary=True)
        backend.write_text(fixed)
        confirmed = _wait_for(backend.read_text, lambda v: v == fixed, COPY_WAIT, sleep, clock)
        if confirmed != fixed:
            log.error("clipboard did not take the fixed text")
            _restore(backend, snapshot)
            return FAILED
        sleep(KEY_SETTLE)
        backend.press(system.PASTE_CHORD)
        sleep(PASTE_SETTLE)
        sleep(RESTORE_DELAY)
        _restore(backend, snapshot)
        log.info("fixed %d characters (%s)", len(copied), direction)
        return OK
    except system.ToolMissing as error:
        log.error("missing tool: %s", error)
        return MISSING
    except Exception:  # the shortcut must never crash silently
        log.exception("unexpected error")
        if snapshot is not None:
            _restore(backend, snapshot)
        return FAILED


def _restore(backend, snapshot) -> None:
    try:
        backend.restore(snapshot)
    except Exception:
        log.exception("could not restore the clipboard")


def run(backend=None, lock: Optional[Lock] = None) -> str:
    """Take the lock, run the cycle and show the notification."""
    backend = backend or system.Backend()
    lock = lock or Lock()
    if not lock.acquire():
        log.info("another fix is running")
        return BUSY
    try:
        outcome = run_cycle(backend)
    finally:
        lock.release()
    key = NOTIFY_KEY.get(outcome)
    if key:
        backend.notify(key)
    return outcome
