# Architecture

## Goals

- Paste ugly text (chat exports, popup-dictionary dumps, mixed notes).
- Get a stable set of Anki fields: headword, sentence, synonyms, short definition, tone-colored Hanzi, pinyin.
- Keep the stack small: one LLM provider, one config slot, plain step functions.

## Repository layout

```
ankia/
  data/
    inbox.txt              # you paste here
    runs/YYYYMMDD_HHMMSS/  # one folder per successful start
  configs/
    main.yaml              # inbox path, runtime knobs
    llm/*.yaml             # which LLM model
    hydra/disabled.yaml    # no Hydra output sprawl
  pipelines/main.py        # CLI entry (`python -m pipelines.main`)
  src/ankia/
    schemas/card.py        # Card + TSV column map
    llm/client.py          # LLM structured JSON
    color/align.py         # pinyin ↔ Hanzi → tone marks
    steps/                 # extract, construct, color, export
```

## Config

Hydra loads `configs/main.yaml`. There is **one** LLM default (`llm: gemini_flash`). Extract and construct share that client. Swap models with an override:

```bash
python -m pipelines.main llm=gemini_flash_lite
```

Prompts are **not** in YAML. They live as strings next to the steps that use them (`steps/extract.py`, `steps/construct.py`) so the wording stays easy to edit without a prompt-pack hierarchy.

## Secrets

`GEMINI_API_KEY` (or `GOOGLE_API_KEY`) comes from `.env` at the repo root (gitignored) or from the process environment. Keys never go in Hydra configs.

## Entry point

`pipelines/main.py` is the only operator surface for v1: resolve inbox → snapshot → run steps → write artifacts under `data/runs/…`. The `ankia` package is library-shaped for imports and tests; a public Python API is not the product yet.
