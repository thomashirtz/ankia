# Design decisions

Short rationale for choices that are easy to second-guess later.

## Inbox + timestamped runs

Operators paste into one file and forget paths. Copying the inbox into `data/runs/YYYYMMDD_HHMMSS/` means you can clear the inbox after a good run without losing provenance. Runs are cheap folders; overwriting a shared “last output” path is not.

## One Card per row

Extract yields many seeds from one dump. Downstream steps (especially construct and resume) are simpler when the unit of state is one flashcard, not a batch object that mutates a list in place.

## LLM owns all readings

Headword, sentence, and definition pinyin all come from the LLM. Historical pain came from trusting dump pinyin (wrong tones, NFD) and from automatic readers picking the wrong polyphone reading in context. The model already chooses the sense and the sentence; it should emit the matching reading. Color code only aligns.

## Color is not an LLM step

HTML tone marks must be stable and cheap. Alignment failures become warnings instead of silent wrong colors.

## Dual output: jsonl + tsv

- **jsonl** — native Card names, easy to diff/debug, carries `warnings`.
- **tsv** — Anki import; headers match the note type; column order matches field positions.

One `OrderedDict` holds both order and attr→header mapping so renames stay local.

## Homogeneous Card names, legacy TSV headers

Python/jsonl use `word_*` / `sentence_*` / `definition_*` for clarity. TSV keeps the shorter Anki field names so existing note types and templates keep working without a deck migration.

## Single LLM config slot

Two LLM steps do not need two model wiring graphs. One Hydra `llm:` default is enough; overrides swap the model for the whole run.

## Prompts in Python, not config packs

There are two prompts. Keeping them beside the step preserves the carefully tuned wording (examples, tips, exclusions) without a parallel YAML tree.

## One LLM backend for now

A thin single-provider client beats a multi-provider matrix until a second backend is actually required.

## No Anki package generation in v1

Output stops at TSV/jsonl. Import into an existing deck/note type. Automating `.apkg` / sync can come later without changing the card schema.

## Deliberately skipped (for now)

- Multi-provider LLM wrappers
- Agent/class hierarchies around steps
- Prompt version packs in `configs/`
- Shipping card HTML templates from this repo
- Auto-clearing the inbox
- Heavy batching of construct calls into one request

Add those when a concrete pain shows up—not before.
