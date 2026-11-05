"""Messages shown to the user, in Persian and English.

Desktop notifications default to Persian: the desktop renders right-to-left
text correctly. Terminal output follows the system language, because many
terminals do not. ``GEEKTYPE_LANG=fa`` or ``GEEKTYPE_LANG=en`` overrides both.
"""

from __future__ import annotations

import os

MESSAGES = {
    "fa": {
        # notifications
        "fixed": "متن اصلاح شد",
        "no_selection": "متنی انتخاب نشده است",
        "nothing_to_fix": "چیزی برای اصلاح پیدا نشد",
        "tool_missing": "ابزار لازم پیدا نشد. برای بررسی، geektype --doctor را اجرا کنید",
        "failed": "اصلاح انجام نشد. برای بررسی، geektype --doctor را اجرا کنید",
        # install
        "install_title": "نصب GeekType",
        "step_packages": "نصب بسته‌های لازم",
        "step_service": "راه‌اندازی سرویس ydotoold",
        "step_icon": "نصب آیکون",
        "step_shortcut": "ثبت میان‌بر F9 در GNOME",
        "step_legacy": "حذف سرویس GeekType v1",
        "packages_ok": "بسته‌های لازم از قبل نصب است",
        "no_apt": "این سیستم apt ندارد. بسته‌های زیر را خودتان نصب کنید",
        "no_gsettings": "gsettings پیدا نشد. میان‌بر را در تنظیمات دسکتاپ خودتان بسازید و فرمان زیر را به F9 بدهید",
        "not_gnome": "این دسکتاپ GNOME نیست. نصب خودکار میان‌بر انجام نشد",
        "install_done": "نصب تمام شد. متن اشتباه‌تایپ‌شده را انتخاب کنید و F9 را بزنید",
        "install_check": "برای بررسی همه‌چیز بعد از نصب",
        "uninstall_title": "حذف GeekType",
        "uninstall_done": "حذف شد. بسته‌های نصب‌شده (wl-clipboard، ydotool و libnotify-bin) دست‌نخورده ماندند",
        "need_appimage_or_source": "فرمان نصب باید از AppImage یا از پوشه‌ی سورس اجرا شود",
        # doctor
        "doctor_title": "بررسی GeekType",
        "ok": "درست",
        "warn": "هشدار",
        "fail": "خطا",
        "doctor_all_ok": "همه‌چیز درست است",
        "doctor_problems": "مورد برای رفع وجود دارد",
        "c_python": "نسخه‌ی Python",
        "c_session": "نوع نشست",
        "c_desktop": "دسکتاپ",
        "c_tool": "ابزار",
        "c_service": "سرویس ydotoold",
        "c_socket": "سوکت ydotool",
        "c_keys": "فرستادن کلید",
        "c_clipboard": "خواندن و نوشتن کلیپ‌بورد",
        "c_shortcut": "میان‌بر F9",
        "c_conflict": "تداخل میان‌بر",
        "c_log": "فایل گزارش",
        "h_wayland": "GeekType برای Wayland ساخته شده است. روی X11 آزموده نشده",
        "h_gnome": "فقط GNOME آزموده شده است",
        "h_install": "فرمان نصب را دوباره اجرا کنید: geektype --install",
        "h_missing": "نصب نیست",
        "h_inactive": "فعال نیست",
        "h_no_socket": "سوکت پیدا نشد",
        "h_no_perm": "دسترسی به سوکت ندارید",
        "h_clip_fail": "کلیپ‌بورد پاسخ نداد",
        "h_not_set": "ثبت نشده",
        "h_other_use": "این کلید جای دیگری هم ثبت شده",
        "h_command_gone": "فایل فرمان پیدا نشد",
        "h_py_old": "Python 3.8 یا بالاتر لازم است",
    },
    "en": {
        "fixed": "Text fixed",
        "no_selection": "No text is selected",
        "nothing_to_fix": "Nothing to fix",
        "tool_missing": "A required tool is missing. Run geektype --doctor to check",
        "failed": "Could not fix the text. Run geektype --doctor to check",
        "install_title": "Installing GeekType",
        "step_packages": "Installing required packages",
        "step_service": "Setting up the ydotoold service",
        "step_icon": "Installing the icon",
        "step_shortcut": "Registering the F9 shortcut in GNOME",
        "step_legacy": "Removing the version 1 service",
        "packages_ok": "Required packages are already installed",
        "no_apt": "This system has no apt. Install these packages yourself",
        "no_gsettings": "gsettings was not found. Create a shortcut in your desktop settings and give F9 this command",
        "not_gnome": "This is not a GNOME desktop. The shortcut was not registered",
        "install_done": "Done. Select text typed in the wrong layout and press F9",
        "install_check": "To check everything after installing",
        "uninstall_title": "Removing GeekType",
        "uninstall_done": "Removed. The installed packages (wl-clipboard, ydotool, libnotify-bin) were left alone",
        "need_appimage_or_source": "The install command must run from the AppImage or from the source folder",
        "doctor_title": "GeekType check",
        "ok": "ok",
        "warn": "warn",
        "fail": "fail",
        "doctor_all_ok": "Everything is fine",
        "doctor_problems": "item(s) to fix",
        "c_python": "Python version",
        "c_session": "Session type",
        "c_desktop": "Desktop",
        "c_tool": "Tool",
        "c_service": "ydotoold service",
        "c_socket": "ydotool socket",
        "c_keys": "Sending keys",
        "c_clipboard": "Clipboard read and write",
        "c_shortcut": "F9 shortcut",
        "c_conflict": "Shortcut conflict",
        "c_log": "Log file",
        "h_wayland": "GeekType is built for Wayland. It has not been tried on X11",
        "h_gnome": "Only GNOME has been tried",
        "h_install": "Run the install command again: geektype --install",
        "h_missing": "not installed",
        "h_inactive": "not active",
        "h_no_socket": "socket not found",
        "h_no_perm": "no permission on the socket",
        "h_clip_fail": "the clipboard did not answer",
        "h_not_set": "not registered",
        "h_other_use": "this key is also registered elsewhere",
        "h_command_gone": "the command file was not found",
        "h_py_old": "Python 3.8 or newer is required",
    },
}


def lang(kind: str = "notify") -> str:
    """Return ``"fa"`` or ``"en"`` for notifications (``notify``) or the terminal (``cli``)."""
    forced = os.environ.get("GEEKTYPE_LANG", "").strip().lower()
    if forced in MESSAGES:
        return forced
    if kind == "notify":
        return "fa"
    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(name, "")
        if value:
            return "fa" if value.lower().startswith("fa") else "en"
    return "en"


def t(key: str, kind: str = "cli") -> str:
    table = MESSAGES[lang(kind)]
    return table.get(key) or MESSAGES["en"][key]
