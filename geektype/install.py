"""``geektype --install`` and ``--uninstall``: what v1's setup.sh did, in Python."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from typing import List

from . import shortcut, system
from .i18n import t

PACKAGES = ("wl-clipboard", "ydotool", "libnotify-bin")
UNIT_NAME = "geektype-ydotoold.service"
UNIT_PATH = "/etc/systemd/system/" + UNIT_NAME
LEGACY_UNIT = "/etc/systemd/system/ydotool.service"
ICON_NAME = "geektype.svg"


def _sudo(*command: str) -> int:
    prefix: List[str] = [] if os.geteuid() == 0 else ["sudo"]
    return subprocess.call(prefix + list(command))


def _root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def program_path() -> str:
    """The file the shortcut should run: the AppImage, or ``bin/geektype``."""
    appimage = os.environ.get("APPIMAGE")
    if appimage and os.path.exists(appimage):
        return os.path.abspath(appimage)
    return os.path.join(_root(), "bin", "geektype")


def unit_text(uid: int, gid: int) -> str:
    return (
        "[Unit]\n"
        "Description=ydotool daemon for GeekType\n\n"
        "[Service]\n"
        "RuntimeDirectory=geektype\n"
        "RuntimeDirectoryMode=0755\n"
        "ExecStart=/usr/bin/ydotoold --socket-path=%s --socket-own=%d:%d --socket-perm=0600\n"
        "Restart=on-failure\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n" % (system.RUNTIME_SOCKET, uid, gid)
    )


def _step(key: str) -> None:
    print("-> " + t(key))


def _packages() -> None:
    _step("step_packages")
    missing = [p for p in PACKAGES if subprocess.call(
        ["dpkg", "-s", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0] \
        if shutil.which("dpkg") else list(PACKAGES)
    if not missing:
        print("   " + t("packages_ok"))
        return
    if shutil.which("apt-get") is None:
        print("   %s: %s" % (t("no_apt"), " ".join(missing)))
        return
    _sudo("apt-get", "update", "-qq")
    _sudo("apt-get", "install", "-y", *missing)


def _service() -> None:
    _step("step_service")
    handle, tmp = tempfile.mkstemp(suffix=".service")
    try:
        with os.fdopen(handle, "w") as out:
            out.write(unit_text(os.getuid(), os.getgid()))
        _sudo("install", "-m", "0644", tmp, UNIT_PATH)
    finally:
        os.unlink(tmp)
    _sudo("systemctl", "daemon-reload")
    _sudo("systemctl", "enable", "--now", UNIT_NAME)


def _legacy() -> None:
    """Remove the v1 service, but only if it is the one v1 created."""
    try:
        with open(LEGACY_UNIT, encoding="utf-8") as handle:
            body = handle.read()
    except OSError:
        return
    if system.LEGACY_SOCKET not in body:
        return
    _step("step_legacy")
    _sudo("systemctl", "disable", "--now", "ydotool.service")
    _sudo("rm", "-f", LEGACY_UNIT)
    _sudo("systemctl", "daemon-reload")


def _icon() -> None:
    _step("step_icon")
    for candidate in (os.path.join(_root(), "assets", "icons", "geektype-icon.svg"),
                      os.path.join(os.environ.get("APPDIR", ""), "geektype.svg")):
        if os.path.exists(candidate):
            target = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps")
            os.makedirs(target, exist_ok=True)
            shutil.copyfile(candidate, os.path.join(target, ICON_NAME))
            return


def _shortcut(command: str) -> None:
    _step("step_shortcut")
    if "GNOME" not in os.environ.get("XDG_CURRENT_DESKTOP", "").upper():
        print("   " + t("not_gnome"))
        print("   %s: %s" % ("F9", command))
        return
    if not shortcut.available():
        print("   %s: %s" % (t("no_gsettings"), command))
        return
    shortcut.register(command)


def _ensure_executable(path: str) -> None:
    """The F9 shortcut runs ``path`` directly, so it must be executable.

    Files uploaded through the GitHub website or extracted from some ZIP tools
    lose the executable bit; put it back for the owner, group and others.
    """
    try:
        mode = os.stat(path).st_mode
        if not mode & 0o111:
            os.chmod(path, mode | 0o755)
    except OSError:
        pass


def install() -> int:
    program = program_path()
    if not os.path.exists(program):
        print(t("need_appimage_or_source"), file=sys.stderr)
        return 1
    _ensure_executable(program)
    print(t("install_title") + "\n")
    _packages()
    _legacy()
    _service()
    _icon()
    _shortcut(shlex.quote(program))
    print("\n" + t("install_done"))
    print("%s: %s --doctor" % (t("install_check"), shlex.quote(program)))
    return 0


def uninstall() -> int:
    print(t("uninstall_title") + "\n")
    if shortcut.available():
        try:
            shortcut.unregister()
        except Exception:
            pass
    if os.path.exists(UNIT_PATH):
        _sudo("systemctl", "disable", "--now", UNIT_NAME)
        _sudo("rm", "-f", UNIT_PATH)
        _sudo("systemctl", "daemon-reload")
    icon = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps/" + ICON_NAME)
    if os.path.exists(icon):
        os.unlink(icon)
    print(t("uninstall_done"))
    return 0
