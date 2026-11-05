"""``geektype --doctor``: check each piece the F9 cycle depends on."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from typing import List, Tuple

from . import i18n, shortcut, system
from .i18n import t

OK, WARN, FAIL = "ok", "warn", "fail"
Result = Tuple[str, str, str]   # (level, label, detail)

TOOLS = ("wl-copy", "wl-paste", "ydotool", "ydotoold", "notify-send")


def _service_active() -> bool:
    if shutil.which("systemctl") is None:
        return False
    for unit in ("geektype-ydotoold.service", "ydotool.service"):
        result = subprocess.run(["systemctl", "is-active", "--quiet", unit], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False)
        if result.returncode == 0:
            return True
    return False


def collect(backend=None) -> List[Result]:
    results: List[Result] = []
    add = lambda level, key, detail="": results.append((level, t(key), detail))

    if sys.version_info < (3, 8):
        add(FAIL, "c_python", t("h_py_old"))
    else:
        add(OK, "c_python", "%d.%d.%d" % sys.version_info[:3])

    session = os.environ.get("XDG_SESSION_TYPE", "")
    add(OK if session == "wayland" else WARN, "c_session", session or "?")
    if session != "wayland":
        results[-1] = (WARN, t("c_session"), "%s. %s" % (session or "?", t("h_wayland")))

    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "")
    if "GNOME" in desktop.upper():
        add(OK, "c_desktop", desktop)
    else:
        add(WARN, "c_desktop", "%s. %s" % (desktop or "?", t("h_gnome")))

    for tool in TOOLS:
        if shutil.which(tool):
            results.append((OK, "%s: %s" % (t("c_tool"), tool), ""))
        else:
            results.append((FAIL, "%s: %s" % (t("c_tool"), tool), t("h_missing")))

    if _service_active():
        add(OK, "c_service")
    else:
        add(FAIL, "c_service", "%s. %s" % (t("h_inactive"), t("h_install")))

    sock = system.socket_path()
    if not os.path.exists(sock):
        add(FAIL, "c_socket", "%s: %s" % (t("h_no_socket"), sock))
    elif not os.access(sock, os.R_OK | os.W_OK):
        add(FAIL, "c_socket", "%s: %s" % (t("h_no_perm"), sock))
    else:
        add(OK, "c_socket", sock)

    backend = backend or system.Backend()
    try:
        # Shift alone does nothing visible, so it is a safe key to test with.
        result = backend._run(["ydotool", "key", "%d:1" % system.KEY_LEFTSHIFT, "%d:0" % system.KEY_LEFTSHIFT])
        add(OK if result is not None and result.returncode == 0 else FAIL, "c_keys")
    except system.ToolMissing:
        add(FAIL, "c_keys", t("h_missing"))

    try:
        snap = backend.snapshot()
        marker = "geektype-" + uuid.uuid4().hex
        backend.write_text(marker)
        ok = backend.read_text() == marker
        backend.restore(snap)
        add(OK if ok else FAIL, "c_clipboard", "" if ok else t("h_clip_fail"))
    except (system.ToolMissing, system.ToolFailed):
        add(FAIL, "c_clipboard", t("h_clip_fail"))

    if shortcut.available():
        try:
            info = shortcut.current()
            if info is None:
                add(FAIL, "c_shortcut", "%s. %s" % (t("h_not_set"), t("h_install")))
            else:
                first = info["command"].replace('"', "").replace("'", "").split(" --")[0].strip()
                exists = os.path.exists(first)
                level = OK if info["binding"] == shortcut.KEY and exists else FAIL
                detail = "%s -> %s" % (info["binding"], info["command"])
                if not exists:
                    detail += ". " + t("h_command_gone")
                add(level, "c_shortcut", detail)
                clash = shortcut.others_using(info["binding"])
                if clash:
                    add(WARN, "c_conflict", "%s: %s" % (t("h_other_use"), ", ".join(clash)))
        except Exception as error:  # gsettings schema missing, etc.
            add(WARN, "c_shortcut", str(error))
    else:
        add(WARN, "c_shortcut", "gsettings")

    from . import log as logmod
    add(OK, "c_log", logmod.log_file())
    return results


def run() -> int:
    print(t("doctor_title"))
    print()
    results = collect()
    problems = 0
    for level, label, detail in results:
        mark = {OK: t("ok"), WARN: t("warn"), FAIL: t("fail")}[level]
        print("  [%s] %s%s" % (mark, label, (": " + detail) if detail else ""))
        if level == FAIL:
            problems += 1
    print()
    print(t("doctor_all_ok") if not problems else "%d %s" % (problems, t("doctor_problems")))
    return 1 if problems else 0
