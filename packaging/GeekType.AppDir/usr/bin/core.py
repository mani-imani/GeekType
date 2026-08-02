"""
GeekType - core layout conversion logic.

This module is OS-independent. It maps characters between the
standard English (US QWERTY) layout and the standard Persian
(ISIRI 2901 / Windows "Persian Standard") layout, based on
*physical key position* - the same idea LangOver uses.

Source of truth for the Persian layout: the official kbdfar.dll
mapping (Microsoft's Persian Standard layout), scancode by scancode.
"""

# Physical key -> (english char typed under US layout, persian char
# typed under Persian Standard layout, unshifted/base state only).
# Order follows the physical keyboard, row by row.
_KEY_PAIRS = [
    # number row
    ("1", "۱"), ("2", "۲"), ("3", "۳"), ("4", "۴"), ("5", "۵"),
    ("6", "۶"), ("7", "۷"), ("8", "۸"), ("9", "۹"), ("0", "۰"),
    ("-", "-"), ("=", "="),
    # QWERTY row
    ("q", "ض"), ("w", "ص"), ("e", "ث"), ("r", "ق"), ("t", "ف"),
    ("y", "غ"), ("u", "ع"), ("i", "ه"), ("o", "خ"), ("p", "ح"),
    ("[", "ج"), ("]", "چ"),
    # ASDF row
    ("a", "ش"), ("s", "س"), ("d", "ی"), ("f", "ب"), ("g", "ل"),
    ("h", "ا"), ("j", "ت"), ("k", "ن"), ("l", "م"),
    (";", "ک"), ("'", "گ"),
    # ZXCV row
    ("z", "ظ"), ("x", "ط"), ("c", "ز"), ("v", "ر"), ("b", "ذ"),
    ("n", "د"), ("m", "پ"), (",", "و"), (".", "."), ("/", "/"),
    ("\\", "\\"),
    # space stays space
    (" ", " "),
]

# Shifted/symbol row pairs (best-effort - covers common punctuation
# typed while holding Shift on an English layout).
_SHIFTED_KEY_PAIRS = [
    ("!", "!"), ("@", "٬"), ("#", "٫"), ("_", "ـ"), ("+", "+"),
    ("{", "چ"), ("}", "ج"), (":", ":"), ('"', "؛"),
    ("<", "و"), (">", "."), ("?", "؟"), ("|", "\\"),
]

LATIN_TO_PERSIAN = {en: fa for en, fa in _KEY_PAIRS}
LATIN_TO_PERSIAN.update({en: fa for en, fa in _SHIFTED_KEY_PAIRS})

PERSIAN_TO_LATIN = {fa: en for en, fa in _KEY_PAIRS}
# don't let the shifted-symbol pairs override the base reverse map
for en, fa in _SHIFTED_KEY_PAIRS:
    PERSIAN_TO_LATIN.setdefault(fa, en)


def _looks_persian(text: str) -> bool:
    """True if text contains at least one Persian/Arabic-range char."""
    return any("\u0600" <= ch <= "\u06FF" for ch in text)


def fix_layout(text: str) -> str:
    """
    Convert text typed in the wrong layout to the intended one.

    If the text looks Persian, treat it as "accidentally typed in
    Persian layout while English was intended" and convert back to
    Latin - and vice versa.
    """
    if _looks_persian(text):
        table = PERSIAN_TO_LATIN
    else:
        table = LATIN_TO_PERSIAN

    return "".join(table.get(ch, ch) for ch in text)


if __name__ == "__main__":
    # quick manual sanity check:
    # "سلام" typed with English layout active looks like "sghl"
    samples = ["sghl", "hgn ی", "kslhder"]
    for s in samples:
        print(f"{s!r} -> {fix_layout(s)!r}")
