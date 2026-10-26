# Coloring

Tone colors are **deterministic**. The LLM supplies readings; code only aligns and renders.

## Pipeline

1. Normalize strings to Unicode **NFC** (combining tone marks in dumps must not reach the syllable parser as NFD).
2. Collect Hanzi from the text; parse spaced pinyin into syllables.
3. If Hanzi count ≠ syllable count → keep escaped plain text, record a **warning**, do not invent tones.
4. Otherwise wrap each Hanzi in `<mark class="tone-N">…</mark>` where N is 1–5 (5 = neutral).
5. Non-Hanzi (punctuation, etc.) is HTML-escaped and passed through.

Tone comes from tone marks on vowels or a trailing digit on the syllable.

## What is colored

- Headword simplified and traditional (same headword pinyin).
- Example sentence (from `sentence_pinyin`).
- Definition Chinese (from `definition_pinyin`).
- Synonym headwords (pinyin inside the parentheses of each synonym entry).

Plain pinyin columns (`word_pinyin`, `sentence_pinyin`, …) stay uncolored text for Anki.

## What is not used

No third-party Chinese segmenter or automatic reading library for production coloring. Aligning LLM pinyin avoids polyphone guesses that disagree with the card’s intended reading.

## Hint

`hint` is the first character of `word_simplified` — a small reveal aid for the card template, not an LLM field.

## Checks

`ankia.color.align` includes a small self-check / unit tests for a known polyphone alignment (`刺中` + `cì zhòng` → tone-4 on 中).
