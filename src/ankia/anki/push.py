"""Push a run's cards.tsv into Anki via AnkiConnect."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from ankia.anki.connect import invoke
from ankia.anki.ensure import ensure_deck, ensure_model
from ankia.paths import DECK_DIRECTORY, RUNS_DIRECTORY
from ankia.schemas.card import TSV_COLUMNS


@dataclass
class PushResult:
    run_id: str
    added: int
    skipped: int
    total: int
    messages: list[str]


def push_run(
    run_id: str,
    *,
    deck_name: str = "ankia",
    model_name: str = "Zhongwen",
    deck_dir: Path | None = None,
    runs_dir: Path | None = None,
    url: str = "http://127.0.0.1:8765",
    chunk_size: int = 50,
) -> PushResult:
    runs = runs_dir or RUNS_DIRECTORY
    run_dir = runs / run_id
    tsv_path = run_dir / "cards.tsv"
    if not tsv_path.exists():
        raise FileNotFoundError(f"missing {tsv_path}")

    deck_dir = deck_dir or DECK_DIRECTORY
    messages = [
        ensure_model(model_name=model_name, deck_dir=deck_dir, url=url),
        ensure_deck(deck_name=deck_name, options_name=deck_name, deck_dir=deck_dir, url=url),
    ]

    rows = _read_tsv(tsv_path)
    headers = list(TSV_COLUMNS.values())
    notes = []
    for row in rows:
        fields = {h: row.get(h, "") or "" for h in headers}
        notes.append(
            {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": fields,
                "tags": ["ankia", f"run_{run_id}"],
                "options": {"allowDuplicate": False},
            }
        )

    added = 0
    skipped = 0
    for i in range(0, len(notes), chunk_size):
        batch = notes[i : i + chunk_size]
        can_add = invoke("canAddNotes", url=url, notes=batch) or []
        to_add = [note for note, ok in zip(batch, can_add) if ok]
        skipped += sum(1 for ok in can_add if not ok)
        if not to_add:
            continue
        results = invoke("addNotes", url=url, notes=to_add) or []
        for note_id in results:
            if note_id is None:
                skipped += 1
            else:
                added += 1

    return PushResult(
        run_id=run_id,
        added=added,
        skipped=skipped,
        total=len(notes),
        messages=messages,
    )


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))
