#!/usr/bin/env python3
"""
GeekType - AppImage entrypoint.

Run modes:
    geektype.AppImage --install   -> one-time system setup (deps,
                                      ydotoold service, GNOME F9 shortcut
                                      bound to this very AppImage file)
    geektype.AppImage             -> normal run: do one fix cycle
                                      (this is what the F9 shortcut calls)
"""

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import fix_layout  # noqa: E402

SOCKET_PATH = "/tmp/.ydotool_socket"
_YDOTOOL_ENV = {**os.environ, "YDOTOOL_SOCKET": SOCKET_PATH}


# ---------- fix cycle (normal run) ----------

def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_clipboard() -> str:
    return run(["wl-paste", "--no-newline"])


def set_clipboard(text: str) -> None:
    subprocess.run(["wl-copy"], input=text, text=True)


def send_keys(*keys: str) -> None:
    codes = {"ctrl": 29, "c": 46, "v": 47}
    sequence = [f"{codes[k]}:1" for k in keys] + [f"{codes[k]}:0" for k in reversed(keys)]
    subprocess.run(["ydotool", "key", *sequence], env=_YDOTOOL_ENV)


def wait_for_clipboard_change(previous: str, timeout: float = 1.0) -> str | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        current = get_clipboard()
        if current != previous:
            return current
        time.sleep(0.03)
    return None


def fix_cycle() -> None:
    time.sleep(0.3)  # let a held modifier key be released first
    before = get_clipboard()
    send_keys("ctrl", "c")
    original = wait_for_clipboard_change(before, timeout=1.0)
    if original is None:
        return
    fixed = fix_layout(original)
    if fixed == original:
        return
    set_clipboard(fixed)
    time.sleep(0.05)
    send_keys("ctrl", "v")
    subprocess.run(["notify-send", "-i", "input-keyboard", "-t", "1200", "GeekType", "متن اصلاح شد"])


# ---------- install (one-time setup) ----------

def install() -> None:
    appimage_path = os.environ.get("APPIMAGE")
    if not appimage_path:
        print("!! این باینری باید به‌صورت AppImage اجرا بشه (نه مستقیم اسکریپت پایتون) تا مسیر خودش رو پیدا کنه.")
        sys.exit(1)

    uid, gid = os.getuid(), os.getgid()
    print("==> نصب پیش‌نیازها (wl-clipboard, ydotool, libnotify-bin)...")
    subprocess.run(["sudo", "apt-get", "update", "-qq"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "wl-clipboard", "ydotool", "libnotify-bin"], check=True)

    print("==> تنظیم سرویس ydotoold...")
    service = f"""[Unit]
Description=ydotool daemon

[Service]
ExecStart=/usr/bin/ydotoold --socket-path={SOCKET_PATH} --socket-own={uid}:{gid} --socket-perm=0600
Restart=always

[Install]
WantedBy=default.target
"""
    tmp_service = "/tmp/ydotool.service"
    Path(tmp_service).write_text(service)
    subprocess.run(["sudo", "cp", tmp_service, "/etc/systemd/system/ydotool.service"], check=True)
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", "--now", "ydotool.service"], check=True)

    print("==> ثبت شورتکات F9 تو GNOME...")
    schema = "org.gnome.settings-daemon.plugins.media-keys"
    custom_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/geektype/"

    existing = subprocess.run(["gsettings", "get", schema, "custom-keybindings"],
                               capture_output=True, text=True).stdout.strip()
    if "geektype" not in existing:
        new_list = f"['{custom_path}']" if existing == "@as []" else existing[:-1] + f", '{custom_path}']"
        subprocess.run(["gsettings", "set", schema, "custom-keybindings", new_list], check=True)

    binding_schema = f"{schema}.custom-keybinding:{custom_path}"
    subprocess.run(["gsettings", "set", binding_schema, "name", "GeekType"], check=True)
    subprocess.run(["gsettings", "set", binding_schema, "command", appimage_path], check=True)
    subprocess.run(["gsettings", "set", binding_schema, "binding", "F9"], check=True)

    print("\n==> تمومه! هرجا متن اشتباه‌تایپ‌شده رو سلکت کن و F9 بزن.")


if __name__ == "__main__":
    if "--install" in sys.argv:
        install()
    else:
        fix_cycle()
