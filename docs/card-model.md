# Card model

A `Card` is mutable state filled across the pipeline. Internal / jsonl names are long and homogeneous. TSV headers use shorter Anki note-type names via an ordered map.

## Naming pattern

Zones: `word`, `sentence`, `definition`, plus `synonyms` and `hint`.

Roles (where they apply):

| Role | Meaning |
|------|---------|
| `*_simplified` | Simplified-script Chinese text |
| `*_traditional` | Traditional-script Chinese (headword) |
| `*_pinyin` | Spaced syllables with tone marks (NFC) |
| `*_meaning` | English |
| `*_colored` | Hanzi wrapped in `<mark class="tone-N">` |

Examples: `word_pinyin`, `sentence_simplified_colored`, `definition_meaning`.

`definition_*` is a short Chinese gloss of the headword (and its English), not “look this up in an external dictionary app.”

## Fields by stage

| Stage | Fills |
|-------|--------|
| Extract | `word_simplified`, `word_traditional`, `word_pinyin`, `word_meaning` |
| Construct | sentence / synonyms / definition (+ their pinyin); may refresh word_* |
| Color | all `*_colored`, `hint`; may append `warnings` |

## TSV export map

`TSV_COLUMNS` is an `OrderedDict`: **Card attribute → TSV header**. Insertion order is the Anki field order (positional import). Headers match the existing note type:

| Card attribute | TSV header |
|----------------|------------|
| `word_simplified` | `Simplified` |
| `word_simplified_colored` | `SimplifiedColored` |
| `word_traditional` | `Traditional` |
| `word_traditional_colored` | `TraditionalColored` |
| `word_pinyin` | `Pinyin` |
| `word_meaning` | `Meaning` |
| `hint` | `Hint` |
| `sentence_simplified` | `SentenceSimplified` |
| `sentence_simplified_colored` | `SentenceSimplifiedColored` |
| `sentence_meaning` | `SentenceMeaning` |
| `sentence_pinyin` | `SentencePinyin` |
| `synonyms` | `Synonyms` |
| `synonyms_colored` | `SynonymsColored` |
| `definition_simplified` | `DictionarySimplified` |
| `definition_simplified_colored` | `DictionarySimplifiedColored` |
| `definition_pinyin` | `DictionaryPinyin` |
| `definition_meaning` | `DictionaryMeaning` |

`warnings` is jsonl-only.

## Synonym string format

Plain text (not a nested list), for Anki HTML:

```text
字 (pīn yīn) - gloss<br>字2 (pīn yīn) - gloss
```

Coloring parses the parenthetical pinyin to tone-mark the synonym headword.
