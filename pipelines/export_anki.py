"""Push a generate-run's cards.tsv into Anki via AnkiConnect."""
from __future__ import annotations

import argparse
import sys

from omegaconf import OmegaConf

from ankia.anki.connect import AnkiConnectError, invoke
from ankia.anki.push import push_run
from ankia.paths import CONFIG_PATH


def main(argv: list[str] | None = None) -> None:
    cfg = OmegaConf.load(CONFIG_PATH / "export_anki.yaml")
    parser = argparse.ArgumentParser(
        prog="pipelines.export_anki",
        description="Push data/runs/<run_id>/cards.tsv into Anki (AnkiConnect).",
    )
    parser.add_argument("run_id", help="Run folder name under data/runs/, e.g. 20261026_181244")
    parser.add_argument("--deck", default=str(cfg.deck_name), help="Anki deck name")
    parser.add_argument("--model", default=str(cfg.model_name), help="Note type")
    parser.add_argument("--url", default=str(cfg.anki_url), help="AnkiConnect URL")
    parser.add_argument("--chunk-size", type=int, default=int(cfg.chunk_size))
    parser.add_argument(
        "--sync",
        action="store_true",
        help="AnkiConnect sync to AnkiWeb after a successful push",
    )
    args = parser.parse_args(argv)

    try:
        result = push_run(
            args.run_id,
            deck_name=args.deck,
            model_name=args.model,
            url=args.url,
            chunk_size=args.chunk_size,
        )
        if args.sync:
            invoke("sync", url=args.url)
    except (AnkiConnectError, FileNotFoundError) as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    for msg in result.messages:
        print(msg)
    print(
        f"run {result.run_id}: added {result.added}, "
        f"skipped {result.skipped}, total {result.total}"
    )
    if args.sync:
        print("synced")


if __name__ == "__main__":
    main()
