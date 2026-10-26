"""Extract seed cards from ugly inbox text (README seed prompt, nearly verbatim)."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ankia.color.align import nfc
from ankia.llm.client import GeminiClient
from ankia.schemas.card import Card

EXTRACT_SYSTEM = """\
Please create a verified list of Chinese words, ensuring accuracy and clarity in each entry. For each word:

    1. **Double-check the Chinese characters** (both simplified and traditional, if applicable).
    2. **Confirm the pinyin transcription**, ensuring proper spacing and tone markings. Never trust the source pinyin blindly — it may use wrong tones, NFD combining marks, or be incomplete. Always emit clean NFC pinyin with proper tone marks and **one space between each syllable**.
    3. **Provide a concise English translation** (e.g., one or two words) that reflects the most common meaning of the word in context.

Exclude any words that are:
    - Unclear, ambiguous, or have meanings that are not straightforward.
    - Rare, overly technical, or context-dependent in ways that might not be intuitive.

Return a JSON object with a `cards` array. Each card has:
    - word_simplified: simplified Chinese characters
    - word_traditional: traditional Chinese characters (same as simplified when identical)
    - word_pinyin: pinyin with one space between each syllable and proper tone markings
    - word_meaning: a simple, clear English translation in one or two words

Use the provided list as input, and output only those entries that are confirmed to be accurate and clear.

---

### Example Input

    - 启用 (invoke)
    - 大型 (large-scale)
    - 深奥 (profound)

---

### Example Output (conceptual)

启用 / 啟用 / qǐ yòng / invoke
大型 / 大型 / dà xíng / large-scale
深奥 / 深奧 / shēn ào / profound
"""


class SeedCard(BaseModel):
    word_simplified: str
    word_traditional: str
    word_pinyin: str
    word_meaning: str


class ExtractResult(BaseModel):
    cards: list[SeedCard] = Field(default_factory=list)


def extract_cards(client: GeminiClient, inbox_text: str, *, chunk_chars: int = 12000) -> list[Card]:
    text = nfc(inbox_text).strip()
    if not text:
        return []

    chunks = _chunk(text, chunk_chars)
    cards: list[Card] = []
    seen: set[str] = set()
    for chunk in chunks:
        result = client.generate(
            schema=ExtractResult,
            system=EXTRACT_SYSTEM,
            user=f"### Word List\n\n{chunk}",
        )
        for seed in result.cards:
            simp = nfc(seed.word_simplified).strip()
            if not simp or simp in seen:
                continue
            seen.add(simp)
            cards.append(
                Card(
                    word_simplified=simp,
                    word_traditional=nfc(seed.word_traditional).strip(),
                    word_pinyin=nfc(seed.word_pinyin).strip(),
                    word_meaning=nfc(seed.word_meaning).strip(),
                )
            )
    return cards


def _chunk(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    lines = text.splitlines(keepends=True)
    chunks: list[str] = []
    buf: list[str] = []
    size = 0
    for line in lines:
        if size + len(line) > max_chars and buf:
            chunks.append("".join(buf))
            buf, size = [], 0
        buf.append(line)
        size += len(line)
    if buf:
        chunks.append("".join(buf))
    return chunks
