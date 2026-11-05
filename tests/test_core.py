"""Tests for geektype.core.

Run from the repository root:

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import re
import string
import sys
import unicodedata
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from geektype import core  # noqa: E402

XKB_IR = "/usr/share/X11/xkb/symbols/ir"

# xkb key name -> (US base, US shift). Independent of the table in core.py.
XKB_US = {
    "TLDE": ("`", "~"), "AE01": ("1", "!"), "AE02": ("2", "@"), "AE03": ("3", "#"),
    "AE04": ("4", "$"), "AE05": ("5", "%"), "AE06": ("6", "^"), "AE07": ("7", "&"),
    "AE08": ("8", "*"), "AE09": ("9", "("), "AE10": ("0", ")"), "AE11": ("-", "_"),
    "AE12": ("=", "+"),
    "AD01": ("q", "Q"), "AD02": ("w", "W"), "AD03": ("e", "E"), "AD04": ("r", "R"),
    "AD05": ("t", "T"), "AD06": ("y", "Y"), "AD07": ("u", "U"), "AD08": ("i", "I"),
    "AD09": ("o", "O"), "AD10": ("p", "P"), "AD11": ("[", "{"), "AD12": ("]", "}"),
    "BKSL": ("\\", "|"),
    "AC01": ("a", "A"), "AC02": ("s", "S"), "AC03": ("d", "D"), "AC04": ("f", "F"),
    "AC05": ("g", "G"), "AC06": ("h", "H"), "AC07": ("j", "J"), "AC08": ("k", "K"),
    "AC09": ("l", "L"), "AC10": (";", ":"), "AC11": ("'", '"'),
    "AB01": ("z", "Z"), "AB02": ("x", "X"), "AB03": ("c", "C"), "AB04": ("v", "V"),
    "AB05": ("b", "B"), "AB06": ("n", "N"), "AB07": ("m", "M"), "AB08": (",", "<"),
    "AB09": (".", ">"), "AB10": ("/", "?"),
}

LATIN_KEYSYMS = {
    "exclam": "!", "asterisk": "*", "parenright": ")", "parenleft": "(",
    "bracketright": "]", "bracketleft": "[", "braceright": "}", "braceleft": "{",
    "colon": ":", "greater": ">", "less": "<", "period": ".", "slash": "/",
    "minus": "-", "equal": "=", "plus": "+", "backslash": "\\", "bar": "|",
    "multiply": "×", "division": "÷",
    "guillemotright": "»", "guillemotleft": "«",
}

ARABIC_NAMES = {
    "Arabic_ra": "ARABIC LETTER REH",
    "Farsi_yeh": "ARABIC LETTER FARSI YEH",
    "Arabic_yeh": "ARABIC LETTER YEH",
    "Arabic_hamzaonwaw": "ARABIC LETTER WAW WITH HAMZA ABOVE",
    "Arabic_hamzaonyeh": "ARABIC LETTER YEH WITH HAMZA ABOVE",
    "Arabic_hamzaunderalef": "ARABIC LETTER ALEF WITH HAMZA BELOW",
    "Arabic_hamzaonalef": "ARABIC LETTER ALEF WITH HAMZA ABOVE",
    "Arabic_maddaonalef": "ARABIC LETTER ALEF WITH MADDA ABOVE",
    "Arabic_tehmarbuta": "ARABIC LETTER TEH MARBUTA",
    "Arabic_superscript_alef": "ARABIC LETTER SUPERSCRIPT ALEF",
    "Arabic_hamza_above": "ARABIC HAMZA ABOVE",
    "Arabic_sukun": "ARABIC SUKUN", "Arabic_dammatan": "ARABIC DAMMATAN",
    "Arabic_kasratan": "ARABIC KASRATAN", "Arabic_fathatan": "ARABIC FATHATAN",
    "Arabic_damma": "ARABIC DAMMA", "Arabic_kasra": "ARABIC KASRA",
    "Arabic_fatha": "ARABIC FATHA", "Arabic_shadda": "ARABIC SHADDA",
    "Arabic_comma": "ARABIC COMMA", "Arabic_semicolon": "ARABIC SEMICOLON",
    "Arabic_question_mark": "ARABIC QUESTION MARK",
    "Arabic_tatweel": "ARABIC TATWEEL",
}

FARSI_DIGITS = {"Farsi_%d" % n: chr(0x06F0 + n) for n in range(10)}


def keysym_to_char(name: str) -> str:
    match = re.fullmatch(r"U([0-9A-Fa-f]{4,6})", name)
    if match:
        return chr(int(match.group(1), 16))
    if name in FARSI_DIGITS:
        return FARSI_DIGITS[name]
    if name in LATIN_KEYSYMS:
        return LATIN_KEYSYMS[name]
    if name in ARABIC_NAMES:
        return unicodedata.lookup(ARABIC_NAMES[name])
    if name.startswith("Arabic_"):
        return unicodedata.lookup("ARABIC LETTER " + name[len("Arabic_"):].upper())
    raise KeyError(name)


def read_xkb_persian():
    """Levels 1 and 2 of xkb ``ir(pes)``: {key name: (base, shift)}."""
    with open(XKB_IR, encoding="utf-8") as handle:
        source = handle.read()
    start = source.index('xkb_symbols "pes" {')
    block = source[start:source.index("\n};", start)]
    keys = {}
    for name, levels in re.findall(r"key\s+<(\w+)>\s*\{\s*\[([^\]]*)\]", block):
        symbols = [part.strip() for part in levels.split(",")]
        keys[name] = (keysym_to_char(symbols[0]), keysym_to_char(symbols[1]))
    return keys


class TableTests(unittest.TestCase):
    def test_every_printable_ascii_character_has_a_key(self):
        printable = {ch for ch in string.printable if not ch.isspace()}
        self.assertEqual(printable, {ch for row in core._KEYS for ch in row[:2]})

    def test_persian_side_has_no_duplicates(self):
        persian = [ch for row in core._KEYS for ch in row[2:]]
        self.assertEqual(len(persian), len(set(persian)))

    def test_round_trip_for_every_character(self):
        for ch, fa in core.LATIN_TO_PERSIAN.items():
            self.assertEqual(core.PERSIAN_TO_LATIN[fa], ch, repr(ch))

    @unittest.skipUnless(os.path.exists(XKB_IR), "xkb data not installed")
    def test_matches_ubuntu_xkb_persian_layout(self):
        xkb = read_xkb_persian()
        by_us = {(row[0], row[1]): (row[2], row[3]) for row in core._KEYS}
        self.assertEqual(set(xkb), set(XKB_US))
        for key, (us, fa) in ((k, (XKB_US[k], xkb[k])) for k in xkb):
            self.assertEqual(by_us[us], fa, key)


class ConversionTests(unittest.TestCase):
    def test_example_from_the_product_description(self):
        self.assertEqual(core.fix_layout("sghl"), "سلام")
        self.assertEqual(core.fix_layout("سلام"), "sghl")

    def test_empty_and_unmappable_text(self):
        self.assertEqual(core.fix_layout(""), "")
        self.assertEqual(core.fix_layout("   \n"), "   \n")
        self.assertIsNone(core.detect("   "))

    def test_shifted_letters_use_the_persian_shift_layer(self):
        self.assertEqual(core.fix_layout("Hf"), "آب")   # alef madda, beh

    def test_caps_lock_is_undone(self):
        self.assertEqual(core.fix_layout("SGHL"), "سلام")
        self.assertEqual(core.fix_layout("SGHL SGHL"), "سلام سلام")

    def test_single_capital_is_a_real_shift(self):
        self.assertEqual(core.fix_layout("S"), "ئ")

    def test_symbols_follow_the_shift_layer(self):
        self.assertEqual(core.fix_layout("{"), "}")
        self.assertEqual(core.fix_layout("<"), ">")
        self.assertEqual(core.fix_layout("("), ")")
        self.assertEqual(core.fix_layout("&"), "،")
        self.assertEqual(core.fix_layout("?"), "؟")
        self.assertEqual(core.fix_layout("~"), "÷")
        self.assertEqual(core.fix_layout("$"), "﷼")

    def test_digits_become_persian_and_back(self):
        self.assertEqual(core.fix_layout("123"), "۱۲۳")
        self.assertEqual(core.fix_layout("۱۲۳"), "123")
        self.assertEqual(core.fix_layout("١٢٣"), "123")

    def test_backtick_is_kept_going_to_persian_and_restored_coming_back(self):
        self.assertEqual(core.fix_layout("sghl`"), "سلام`")
        self.assertEqual(core.fix_layout("سلام‍"), "sghl`")

    def test_newlines_and_spaces_are_untouched(self):
        self.assertEqual(core.fix_layout("sghl\nsghl hg"),
                         "سلام\nسلام ال")

    def test_english_typed_in_the_persian_layout(self):
        typed = "آثممخ ٌخقمی"
        self.assertEqual(core.fix_layout(typed), "Hello World")

    def test_zwnj_is_a_space_after_a_character_and_B_at_a_word_start(self):
        self.assertEqual(core.fix_layout("ّ‌شپ"), "I am")
        self.assertEqual(core.fix_layout("‌خخ"), "Boo")
        self.assertEqual(core.fix_layout("خ ‌خ"), "o Bo")

    def test_mixed_text_follows_the_majority_script(self):
        self.assertEqual(core.detect("سلام سلام hi"), core.TO_LATIN)
        self.assertEqual(core.detect("sghl hello س"), core.TO_PERSIAN)

    def test_converting_twice_returns_the_original_letters(self):
        for word in ("sghl", "hello", "geektype", "qwertyuiop"):
            self.assertEqual(core.fix_layout(core.fix_layout(word)), word)

    def test_unknown_characters_pass_through(self):
        self.assertEqual(core.fix_layout("sghl é中"), "سلام é中")


if __name__ == "__main__":
    unittest.main()
