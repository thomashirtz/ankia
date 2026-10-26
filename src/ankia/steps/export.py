"""Write cards.jsonl + cards.tsv."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from ankia.schemas.card import TSV_COLUMNS, Card


def write_jsonl(path: Path, cards: list[Card]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for card in cards:
            f.write(json.dumps(card.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[Card]:
    if not path.exists():
        return []
    cards: list[Card] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cards.append(Card.from_dict(json.loads(line)))
    return cards


def write_tsv(path: Path, cards: list[Card]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(TSV_COLUMNS.values())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for card in cards:
            row = {
                header: getattr(card, attr) or ""
                for attr, header in TSV_COLUMNS.items()
            }
            writer.writerow(row)


def append_jsonl(path: Path, card: Card) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(card.to_dict(), ensure_ascii=False) + "\n")
