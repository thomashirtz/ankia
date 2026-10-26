# Anki export (AnkiConnect)

Push a generate-run’s `cards.tsv` straight into Anki Desktop — no `.apkg` import.

## One-time setup

1. Install **AnkiConnect** (Tools → Add-ons → Get Add-ons → `2055492159`).
2. Restart Anki. Default bind: `127.0.0.1:8765`.
3. Keep Anki open while exporting.

## Blueprint: `data/deck/`

| Path | Role |
|------|------|
| `model.json` | Note type name, field order, template file refs |
| `styling.css` | Card CSS (tone colors, layout) |
| `english_to_chinese/front.html` / `back.html` | Card template |
| `deck_options.json` | Review settings (copied from live `0 - Huawei` via AnkiConnect) |

If note type **Zhongwen** is missing, export creates it from these files. If it already exists, templates are left alone.

## Commands

```bash
# after a generate run (Anki must be open)
python -m pipelines.export_anki 20261026_181244
python -m pipelines.export_anki 20261026_181244 --sync

# or in one shot from the generate pipeline
python -m pipelines.main anki.export=true anki.sync=true
```

Default deck is **`ankia`** (`anki.deck_name` in config, or `--deck`). Notes are tagged `ankia` + `run_<id>`. Duplicates (same first field) are skipped. `anki.export` / `anki.sync` default to `false` in [`configs/main.yaml`](../configs/main.yaml).

## Safety

- If the target deck already exists, its **review options are left unchanged** (vendored `deck_options.json` only applies when creating a new deck).
- Field updates via AnkiConnect do not reset scheduling; this export only **adds** notes (`allowDuplicate: false`).
- Re-running the same export skips cards Anki treats as duplicates.
