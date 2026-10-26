"""Inbox → extract → construct → color → cards.jsonl + cards.tsv."""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

import hydra
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf

from ankia.anki.connect import AnkiConnectError, invoke
from ankia.anki.push import push_run
from ankia.paths import CONFIG_PATH, REPOSITORY_PATH, RUNS_DIRECTORY
from ankia.steps.color import color_card
from ankia.steps.construct import construct_card
from ankia.steps.export import append_jsonl, read_jsonl, write_jsonl, write_tsv
from ankia.steps.extract import extract_cards


def run_pipeline(cfg: DictConfig) -> Path | None:
    inbox = Path(cfg.inbox)
    if not inbox.is_absolute():
        inbox = REPOSITORY_PATH / inbox
    if not inbox.exists():
        print(f"Inbox not found: {inbox}", file=sys.stderr)
        return None

    text = inbox.read_text(encoding="utf-8")
    if not text.strip():
        print(f"Inbox empty ({inbox}) — nothing to do.")
        return None

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIRECTORY / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(inbox, run_dir / "inbox.txt")
    (run_dir / "config.yaml").write_text(OmegaConf.to_yaml(cfg), encoding="utf-8")

    client = instantiate(cfg.llm)
    chunk_chars = int(cfg.runtime.extract_chunk_chars)
    resume = bool(cfg.runtime.construct_resume)

    extract_path = run_dir / "extract.jsonl"
    construct_path = run_dir / "construct.jsonl"
    cards_jsonl = run_dir / "cards.jsonl"
    cards_tsv = run_dir / "cards.tsv"

    print(f"Run {run_id} → {run_dir}")
    print("extract…")
    seeds = extract_cards(client, text, chunk_chars=chunk_chars)
    write_jsonl(extract_path, seeds)
    print(f"  {len(seeds)} seed(s)")

    done = {c.word_simplified: c for c in read_jsonl(construct_path)} if resume else {}
    constructed = []
    print("construct…")
    for i, seed in enumerate(seeds, 1):
        if seed.word_simplified in done:
            card = done[seed.word_simplified]
            print(f"  [{i}/{len(seeds)}] resume {seed.word_simplified}")
        else:
            print(f"  [{i}/{len(seeds)}] {seed.word_simplified}")
            card = construct_card(client, seed)
            append_jsonl(construct_path, card)
        constructed.append(card)

    print("color…")
    colored = [color_card(c) for c in constructed]
    write_jsonl(cards_jsonl, colored)
    write_tsv(cards_tsv, colored)
    n_warn = sum(len(c.warnings) for c in colored)
    print(f"Wrote {len(colored)} cards → {cards_tsv}")
    if n_warn:
        print(f"{n_warn} warning(s) — see cards.jsonl", file=sys.stderr)

    _maybe_anki(cfg, run_id)
    return run_dir


def _maybe_anki(cfg: DictConfig, run_id: str) -> None:
    anki = cfg.get("anki")
    if not anki:
        return
    do_export = bool(anki.get("export", False))
    do_sync = bool(anki.get("sync", False))
    if not do_export and not do_sync:
        return

    url = str(anki.get("url", "http://127.0.0.1:8765"))
    try:
        if do_export:
            print("anki export…")
            result = push_run(
                run_id,
                deck_name=str(anki.get("deck_name", "ankia")),
                model_name=str(anki.get("model_name", "Zhongwen")),
                url=url,
            )
            for msg in result.messages:
                print(f"  {msg}")
            print(
                f"  added {result.added}, skipped {result.skipped}, total {result.total}"
            )
        if do_sync:
            print("anki sync…")
            invoke("sync", url=url)
            print("  synced")
    except (AnkiConnectError, FileNotFoundError) as exc:
        print(f"anki step failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


@hydra.main(version_base=None, config_path=str(CONFIG_PATH), config_name="main")
def main(cfg: DictConfig) -> None:
    run_pipeline(cfg)


if __name__ == "__main__":
    main()
