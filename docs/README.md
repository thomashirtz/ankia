# ankia wiki

ankia turns messy Chinese vocabulary dumps into Anki-ready flashcards: an LLM fills linguistic content; deterministic code applies tone colors and writes files.

| Page | Topic |
|------|--------|
| [Architecture](architecture.md) | Layout, config, how a run starts |
| [Pipeline](pipeline.md) | Inbox → extract → construct → color → export |
| [Card model](card-model.md) | Fields, naming, TSV mapping |
| [LLM & prompts](llm-and-prompts.md) | LLM client, what the models are asked |
| [Coloring](coloring.md) | How pinyin becomes tone HTML |
| [Design decisions](design-decisions.md) | Why these choices (and what was skipped) |
| [Anki export](anki-export.md) | AnkiConnect push into deck `ankia` |

Day-to-day usage lives in the root [README](../README.md).
