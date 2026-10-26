# LLM and prompts

## Provider

ankia ships with one LLM client by default (configured under `configs/llm/`). There is no multi-provider abstraction yet.

The client requests **JSON matching a Pydantic schema**, retries on empty/invalid responses, and backs off harder on rate limits.

## Why structured output

Field counts and formats (especially synonym `<br>` lines and spaced pinyin) break easily in free-form TSV chat replies. Schema validation keeps construct/export boring and testable.

## Extract prompt (intent)

Near-verbatim operational rules:

- Double-check simplified and traditional.
- Emit clean spaced tone-mark pinyin; **do not trust** dump readings.
- English gloss: short (one or two words), most common sense in context.
- Exclude unclear, ambiguous, rare, or overly technical entries.
- Return only entries that are confirmed clear.

Output shape: JSON list of seed fields (`word_*` only).

## Construct prompt (intent)

Same care, full card:

- Example sentence must disambiguate polyphones / multi-sense words.
- Synonyms: exact `Simplified (pinyin) - Translation` with `<br>`.
- Short but informative Chinese + English definitions.
- Accurate simp/trad pairing.
- Sentence Chinese: Hanzi plus `，` and `。` only (no digits / exotic punctuation).
- No spaces inserted between Chinese characters in sentence/definition Hanzi.
- Also emit `sentence_pinyin` and `definition_pinyin` (syllable-spaced, tone-marked), aligned to those strings.

Output shape: one JSON object per card (construct fields).

## Call shape

| Step | Calls |
|------|--------|
| Extract | One structured call per inbox chunk |
| Construct | One structured call per seed card |
| Color | None |

This favors resume and clearer failures over packing many cards into one giant construct response.
