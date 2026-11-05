"""Tests for geektype.cycle with a fake desktop."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from geektype import cycle, system  # noqa: E402


class FakeBackend(object):
    """A clipboard plus an app with a selection; records what happens."""

    def __init__(self, selection="sghl", clipboard="old", copy_works=True, paste_works=True,
                 missing=False, clipboard_stuck=False):
        self.selection = selection
        self.clipboard = clipboard
        self.primary = None
        self.copy_works = copy_works
        self.paste_works = paste_works
        self.missing = missing
        self.clipboard_stuck = clipboard_stuck
        self.pasted = []
        self.notes = []
        self.restored = None

    def snapshot(self):
        if self.missing:
            raise system.ToolMissing("wl-paste")
        return system.Snapshot("data", system.TEXT_MIME, (self.clipboard or "").encode())

    def read_text(self):
        return self.clipboard

    def write_text(self, text, primary=False):
        if primary:
            self.primary = text
        elif not self.clipboard_stuck or text.startswith("geektype-"):
            self.clipboard = text

    def press(self, chord):
        if chord == system.COPY_CHORD and self.copy_works and self.selection is not None:
            self.clipboard = self.selection
        if chord == system.PASTE_CHORD and self.paste_works:
            self.pasted.append(self.clipboard)

    def restore(self, snap):
        self.restored = snap.data.decode()
        self.clipboard = self.restored

    def notify(self, key):
        self.notes.append(key)


def run(backend):
    return cycle.run_cycle(backend, sleep=lambda s: None, clock=_fake_clock())


def _fake_clock():
    state = {"t": 0.0}

    def clock():
        state["t"] += 0.05
        return state["t"]
    return clock


class CycleTests(unittest.TestCase):
    def test_fixes_the_selection_and_restores_the_clipboard(self):
        backend = FakeBackend(selection="sghl", clipboard="my notes")
        self.assertEqual(run(backend), cycle.OK)
        self.assertEqual(backend.pasted, ["سلام"])
        self.assertEqual(backend.primary, "سلام")
        self.assertEqual(backend.clipboard, "my notes")

    def test_persian_selection_becomes_latin(self):
        backend = FakeBackend(selection="سلام")
        self.assertEqual(run(backend), cycle.OK)
        self.assertEqual(backend.pasted, ["sghl"])

    def test_no_selection_never_pastes_old_clipboard_text(self):
        backend = FakeBackend(selection=None, clipboard="sghl")
        self.assertEqual(run(backend), cycle.NO_SELECTION)
        self.assertEqual(backend.pasted, [])
        self.assertEqual(backend.clipboard, "sghl")

    def test_selection_equal_to_old_clipboard_is_still_fixed(self):
        backend = FakeBackend(selection="sghl", clipboard="sghl")
        self.assertEqual(run(backend), cycle.OK)
        self.assertEqual(backend.pasted, ["سلام"])

    def test_nothing_to_fix(self):
        backend = FakeBackend(selection="   ")
        self.assertEqual(run(backend), cycle.NOTHING)
        self.assertEqual(backend.pasted, [])

    def test_clipboard_that_does_not_update_is_reported_not_pasted(self):
        backend = FakeBackend(selection="sghl", clipboard_stuck=True)
        self.assertEqual(run(backend), cycle.FAILED)
        self.assertEqual(backend.pasted, [])

    def test_missing_tool(self):
        self.assertEqual(run(FakeBackend(missing=True)), cycle.MISSING)

    def test_unexpected_error_is_reported_not_raised(self):
        backend = FakeBackend()
        backend.press = lambda chord: 1 / 0
        self.assertEqual(run(backend), cycle.FAILED)


class LockTests(unittest.TestCase):
    def test_second_lock_is_refused_until_the_first_is_released(self):
        path = os.path.join(tempfile.mkdtemp(), "lock")
        first, second = cycle.Lock(path), cycle.Lock(path)
        self.assertTrue(first.acquire())
        self.assertFalse(second.acquire())
        first.release()
        self.assertTrue(second.acquire())
        second.release()

    def test_run_returns_busy_when_locked(self):
        path = os.path.join(tempfile.mkdtemp(), "lock")
        holder = cycle.Lock(path)
        holder.acquire()
        backend = FakeBackend()
        self.assertEqual(cycle.run(backend, cycle.Lock(path)), cycle.BUSY)
        self.assertEqual(backend.pasted, [])
        holder.release()


if __name__ == "__main__":
    unittest.main()
