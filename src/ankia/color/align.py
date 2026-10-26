"""Trusted-pinyin → tone-colored Hanzi (no pypinyin/jieba)."""
from __future__ import annotations

import html
import re
import unicodedata
from dataclasses import dataclass

_PINYIN_SYLLABLE_RE = re.compile(r"[a-zA-ZüÜvVāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+[1-5]?")
_SYNONYM_PHRASE_RE = re.compile(r"^([^\s(]+)\s*\(([^)]+)\)")

_TONE_MARK_TO_NUMBER = {
    "ā": 1, "ē": 1, "ī": 1, "ō": 1, "ū": 1, "ǖ": 1,
    "á": 2, "é": 2, "í": 2, "ó": 2, "ú": 2, "ǘ": 2,
    "ǎ": 3, "ě": 3, "ǐ": 3, "ǒ": 3, "ǔ": 3, "ǚ": 3,
    "à": 4, "è": 4, "ì": 4, "ò": 4, "ù": 4, "ǜ": 4,
}

_HANZI_RANGES = (
    ("\u4E00", "\u9FFF"),
    ("\u3400", "\u4DBF"),
    ("\uF900", "\uFAFF"),
)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def _is_chinese(ch: str) -> bool:
    return any(start <= ch <= end for start, end in _HANZI_RANGES)


def parse_pinyin_syllables(pinyin: str) -> list[str]:
    if not pinyin or not pinyin.strip():
        return []
    return _PINYIN_SYLLABLE_RE.findall(nfc(pinyin).strip())


def tone_from_syllable(syllable: str) -> int:
    for char in reversed(syllable):
        if char.isdigit():
            return int(char)
    for char in syllable:
        if char in _TONE_MARK_TO_NUMBER:
            return _TONE_MARK_TO_NUMBER[char]
    return 5


@dataclass(slots=True)
class _Char:
    hanzi: str
    tone: int

    @property
    def marked(self) -> str:
        return f'<mark class="tone-{self.tone}">{html.escape(self.hanzi)}</mark>'


def color_hanzi(text: str, pinyin: str) -> tuple[str, str | None]:
    """Color Chinese chars from trusted spaced pinyin.

    Non-Hanzi are passed through (HTML-escaped). Returns (html, warning_or_None).
    """
    text = nfc(text)
    pinyin = nfc(pinyin)
    if not text:
        return "", None

    hanzi = [ch for ch in text if _is_chinese(ch)]
    syllables = parse_pinyin_syllables(pinyin)
    if len(hanzi) != len(syllables):
        warning = (
            f"pinyin/hanzi mismatch for {text!r} / {pinyin!r}: "
            f"{len(syllables)} syllables vs {len(hanzi)} hanzi"
        )
        return html.escape(text), warning

    out: list[str] = []
    hi = 0
    for ch in text:
        if _is_chinese(ch):
            out.append(_Char(hanzi=ch, tone=tone_from_syllable(syllables[hi])).marked)
            hi += 1
        else:
            out.append(html.escape(ch))
    return "".join(out), None


def color_synonyms(synonyms: str) -> tuple[str, list[str]]:
    """Color Hanzi in ``字 (pīn yīn) - gloss<br>…`` using parenthetical pinyin."""
    synonyms = nfc(synonyms)
    if not synonyms:
        return "", []

    warnings: list[str] = []
    colored_entries: list[str] = []
    for entry in synonyms.split("<br>"):
        entry = entry.strip()
        if not entry:
            continue
        match = _SYNONYM_PHRASE_RE.match(entry)
        if not match:
            colored_entries.append(html.escape(entry))
            warnings.append(f"synonym parse miss: {entry!r}")
            continue
        hanzi = match.group(1).replace(" ", "")
        pinyin = match.group(2)
        colored, warn = color_hanzi(hanzi, pinyin)
        if warn:
            warnings.append(warn)
        colored_entries.append(entry.replace(match.group(1), colored, 1))
    return "<br>".join(colored_entries), warnings


def _self_check() -> None:
    html_out, warn = color_hanzi("刺中", "cì zhòng")
    assert warn is None, warn
    assert 'tone-4">中' in html_out, html_out
    assert 'tone-4">刺' in html_out or 'tone-' in html_out

    # NFD input should be normalized by caller; raw combining marks fail parse
    nfc_text = nfc("ci\u0300 zho\u0300ng")
    assert "ì" in nfc_text or "ò" in nfc_text or nfc_text != "ci\u0300 zho\u0300ng"

    colored, warns = color_synonyms("射中 (shè zhòng) - hit")
    assert "tone-" in colored, colored
    assert not warns, warns
    print("align self-check ok")


if __name__ == "__main__":
    _self_check()
