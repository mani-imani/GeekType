"""GeekType core: convert text typed in the wrong keyboard layout.

The two layouts are the US QWERTY layout and the standard Persian layout
(ISIRI 9147, the "Persian" layout of Ubuntu/GNOME, xkb ``ir(pes)``).

The idea is the same one LangOver uses. Every physical key produces one
character per layout and per shift level. Text typed in the wrong layout used
the right keys, so each character is mapped back to its key and replaced with
what the same key (at the same shift level) gives in the other layout.

This module has no dependency outside the standard library and does not touch
the system. The table below was checked against ``/usr/share/X11/xkb/symbols/ir``
by ``tests/test_core.py``.
"""

from __future__ import annotations

from typing import Dict, Tuple

# One row per physical key:
#   (US base, US shift, Persian base, Persian shift)
# Invisible and combining characters are written as escapes on purpose.
_KEYS: Tuple[Tuple[str, str, str, str], ...] = (
    # number row
    ("`", "~", "‍", "÷"),      # ZWJ, division sign
    ("1", "!", "۱", "!"),
    ("2", "@", "۲", "٬"),      # Arabic thousands separator
    ("3", "#", "۳", "٫"),      # Arabic decimal separator
    ("4", "$", "۴", "﷼"),      # rial sign
    ("5", "%", "۵", "٪"),      # Arabic percent sign
    ("6", "^", "۶", "×"),      # multiplication sign
    ("7", "&", "۷", "،"),      # Arabic comma
    ("8", "*", "۸", "*"),
    ("9", "(", "۹", ")"),
    ("0", ")", "۰", "("),
    ("-", "_", "-", "ـ"),           # tatweel
    ("=", "+", "=", "+"),
    # top letter row
    ("q", "Q", "ض", "ْ"),      # dad, sukun
    ("w", "W", "ص", "ٌ"),      # sad, dammatan
    ("e", "E", "ث", "ٍ"),      # theh, kasratan
    ("r", "R", "ق", "ً"),      # qaf, fathatan
    ("t", "T", "ف", "ُ"),      # feh, damma
    ("y", "Y", "غ", "ِ"),      # ghain, kasra
    ("u", "U", "ع", "َ"),      # ain, fatha
    ("i", "I", "ه", "ّ"),      # heh, shadda
    ("o", "O", "خ", "]"),           # khah
    ("p", "P", "ح", "["),           # hah
    ("[", "{", "ج", "}"),           # jeem
    ("]", "}", "چ", "{"),           # tcheh
    ("\\", "|", "\\", "|"),
    # home row
    ("a", "A", "ش", "ؤ"),      # sheen, waw with hamza
    ("s", "S", "س", "ئ"),      # seen, yeh with hamza
    ("d", "D", "ی", "ي"),      # Farsi yeh, Arabic yeh
    ("f", "F", "ب", "إ"),      # beh, alef with hamza below
    ("g", "G", "ل", "أ"),      # lam, alef with hamza above
    ("h", "H", "ا", "آ"),      # alef, alef with madda
    ("j", "J", "ت", "ة"),      # teh, teh marbuta
    ("k", "K", "ن", "»"),      # noon, right guillemet
    ("l", "L", "م", "«"),      # meem, left guillemet
    (";", ":", "ک", ":"),           # keheh
    ("'", '"', "گ", "؛"),      # gaf, Arabic semicolon
    # bottom row
    ("z", "Z", "ظ", "ك"),      # zah, Arabic kaf
    ("x", "X", "ط", "ٓ"),      # tah, maddah above
    ("c", "C", "ز", "ژ"),      # zain, jeh
    ("v", "V", "ر", "ٰ"),      # reh, superscript alef
    ("b", "B", "ذ", "‌"),      # thal, ZWNJ
    ("n", "N", "د", "ٔ"),      # dal, hamza above
    ("m", "M", "پ", "ء"),      # peh, hamza
    (",", "<", "و", ">"),           # waw
    (".", ">", ".", "<"),
    ("/", "?", "/", "؟"),           # Arabic question mark
)

ZWJ = "‍"
ZWNJ = "‌"

LATIN_TO_PERSIAN: Dict[str, str] = {}
PERSIAN_TO_LATIN: Dict[str, str] = {}
for _us0, _us1, _fa0, _fa1 in _KEYS:
    LATIN_TO_PERSIAN[_us0] = _fa0
    LATIN_TO_PERSIAN[_us1] = _fa1
    PERSIAN_TO_LATIN[_fa0] = _us0
    PERSIAN_TO_LATIN[_fa1] = _us1

# A backtick is left alone when going to Persian: that key gives an invisible
# joiner in Persian, and silently deleting a backtick would never be wanted.
del LATIN_TO_PERSIAN["`"]

# Arabic-Indic digits are accepted next to the Persian ones.
for _i in range(10):
    PERSIAN_TO_LATIN[chr(0x0660 + _i)] = str(_i)

TO_LATIN = "to_latin"
TO_PERSIAN = "to_persian"

# Characters that only the Persian layout produces and that are visible.
_PERSIAN_SIGNAL = frozenset(
    ch for ch in PERSIAN_TO_LATIN
    if ord(ch) > 0x7F and ch not in (ZWJ, ZWNJ, "÷", "×", "«", "»")
)


def _is_ascii_letter(ch: str) -> bool:
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z")


def detect(text: str) -> str | None:
    """Return the direction to convert ``text``, or ``None`` if nothing maps.

    Mixed text is converted in the direction of whichever script has more
    characters, so one stray word does not flip the whole selection.
    """
    persian = sum(1 for ch in text if ch in _PERSIAN_SIGNAL)
    latin = sum(1 for ch in text if _is_ascii_letter(ch))
    if persian > latin:
        return TO_LATIN
    if latin > 0:
        return TO_PERSIAN
    # No letters at all (digits, punctuation): only ASCII is left to convert.
    if any(ch in LATIN_TO_PERSIAN and ch != " " for ch in text):
        return TO_PERSIAN
    return None


def _caps_lock_fix(text: str) -> str:
    """Undo an accidental Caps Lock: ALL-CAPS Latin text is lowered first.

    Caps Lock does nothing in the Persian layout, so a selection such as
    ``SGHL`` came from the same keys as ``sghl``. A single capital letter is
    left alone because it may be a real Shift.
    """
    letters = [ch for ch in text if _is_ascii_letter(ch)]
    if len(letters) >= 2 and all(ch.isupper() for ch in letters):
        return "".join(ch.lower() if _is_ascii_letter(ch) else ch for ch in text)
    return text


def _to_latin(text: str) -> str:
    out = []
    previous = ""
    for ch in text:
        if ch == ZWNJ:
            # Shift+Space and Shift+B both give a ZWNJ in the Persian layout.
            # At the start of a word it is almost surely Shift+B. After a
            # character it is almost surely Shift still held on the space bar.
            out.append("B" if previous == "" or previous.isspace() else " ")
        else:
            out.append(PERSIAN_TO_LATIN.get(ch, ch))
        previous = ch
    return "".join(out)


def _to_persian(text: str) -> str:
    text = _caps_lock_fix(text)
    return "".join(LATIN_TO_PERSIAN.get(ch, ch) for ch in text)


def convert(text: str) -> Tuple[str, str | None]:
    """Convert ``text`` and also return the direction that was used."""
    direction = detect(text)
    if direction == TO_LATIN:
        return _to_latin(text), direction
    if direction == TO_PERSIAN:
        return _to_persian(text), direction
    return text, None


def fix_layout(text: str) -> str:
    """Return ``text`` converted to the layout it was meant to be typed in."""
    return convert(text)[0]


if __name__ == "__main__":
    import sys

    for sample in sys.argv[1:] or ["sghl", "سلام"]:
        print("{!r} -> {!r}".format(sample, fix_layout(sample)))
