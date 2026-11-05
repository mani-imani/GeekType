"""Reading and writing the GNOME custom shortcut with gsettings."""

from __future__ import annotations

import ast
import shutil
import subprocess
from typing import List, Optional

BASE = "org.gnome.settings-daemon.plugins.media-keys"
PATH = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/geektype/"
SCHEMA = BASE + ".custom-keybinding:" + PATH
KEY = "F9"


def available() -> bool:
    return shutil.which("gsettings") is not None


def _gs(*args: str) -> str:
    result = subprocess.run(["gsettings"] + list(args), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=5, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout.decode("utf-8", "replace").strip()


def _parse_list(raw: str) -> List[str]:
    raw = raw.strip()
    if raw.startswith("@as"):
        raw = raw[3:].strip()
    return list(ast.literal_eval(raw)) if raw else []


def _parse_string(raw: str) -> str:
    return str(ast.literal_eval(raw))


def paths() -> List[str]:
    return _parse_list(_gs("get", BASE, "custom-keybindings"))


def register(command: str) -> None:
    current = paths()
    if PATH not in current:
        _gs("set", BASE, "custom-keybindings", repr(current + [PATH]))
    _gs("set", SCHEMA, "name", "GeekType")
    _gs("set", SCHEMA, "command", command)
    _gs("set", SCHEMA, "binding", KEY)


def unregister() -> None:
    current = paths()
    if PATH in current:
        _gs("set", BASE, "custom-keybindings", repr([p for p in current if p != PATH]))
    for key in ("name", "command", "binding"):
        try:
            _gs("reset", SCHEMA, key)
        except RuntimeError:
            pass


def current() -> Optional[dict]:
    """The registered shortcut as ``{"command", "binding"}``, or ``None``."""
    if PATH not in paths():
        return None
    return {"command": _parse_string(_gs("get", SCHEMA, "command")),
            "binding": _parse_string(_gs("get", SCHEMA, "binding"))}


def others_using(binding: str) -> List[str]:
    """Names of other custom shortcuts that use ``binding``."""
    found = []
    for path in paths():
        if path == PATH:
            continue
        schema = BASE + ".custom-keybinding:" + path
        try:
            if _parse_string(_gs("get", schema, "binding")).lower() == binding.lower():
                found.append(_parse_string(_gs("get", schema, "name")))
        except (RuntimeError, ValueError, SyntaxError):
            continue
    return found
