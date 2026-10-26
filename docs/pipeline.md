# Pipeline

```text
data/inbox.txt
      │
      ▼
  empty? ──yes──► exit 0 (message only)
      │ no
      ▼
  data/runs/YYYYMMDD_HHMMSS/
      ├── inbox.txt          # snapshot of what ran
      ├── config.yaml
      ├── extract.jsonl      # seeds
      ├── construct.jsonl    # full linguistic fields (append / resume)
      ├── cards.jsonl        # final Card records (+ warnings)
      └── cards.tsv          # Anki import
```

The inbox is **never** cleared automatically. When you like a run, wipe `data/inbox.txt` yourself; the timestamped folder keeps the snapshot.

## Steps

### 1. Extract (LLM, usually one call)

Input: raw inbox text (optionally chunked by character budget).

Output: seed cards with only:

- `word_simplified`, `word_traditional`, `word_pinyin`, `word_meaning`

The model is asked to verify characters and pinyin, keep meanings short, and **drop** unclear / rare / overly technical items. Source pinyin is never trusted (dumps often have wrong tones or combining-mark Unicode).

Written to `extract.jsonl`.

### 2. Construct (LLM, one call per seed)

Input: one seed.

Output: full content fields — example sentence + its pinyin and English, synonyms blob, Chinese definition + pinyin + English, and refreshed headword fields.

Written incrementally to `construct.jsonl` so a mid-batch failure can resume within the same run directory (`runtime.construct_resume`).

### 3. Color (no LLM)

Aligns trusted pinyin syllables to Hanzi and fills `*_colored` fields plus `hint` (first character of the simplified headword). Collects mismatch warnings on the card.

### 4. Export

- `cards.jsonl` — Card attribute names (plus `warnings`).
- `cards.tsv` — same data, columns ordered for Anki; headers use the note-type field names (see [Card model](card-model.md)).

## Run artifacts and resume

Each invocation creates a **new** `YYYYMMDD_HHMMSS` folder. Resume applies to appending within that run’s `construct.jsonl` while the process is still building that folder (e.g. after a partial write in the same design). Re-running the CLI always starts a fresh run id from the current inbox.
