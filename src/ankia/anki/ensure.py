"""Ensure Zhongwen note type + ankia deck + review options exist."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ankia.anki.connect import invoke
from ankia.paths import DECK_DIRECTORY


def load_model_definition(deck_dir: Path | None = None) -> dict[str, Any]:
    root = deck_dir or DECK_DIRECTORY
    meta = json.loads((root / "model.json").read_text(encoding="utf-8"))
    css = (root / meta["css"]).read_text(encoding="utf-8")
    templates = []
    for tmpl in meta["cardTemplates"]:
        templates.append(
            {
                "Name": tmpl["Name"],
                "Front": (root / tmpl["Front"]).read_text(encoding="utf-8"),
                "Back": (root / tmpl["Back"]).read_text(encoding="utf-8"),
            }
        )
    return {
        "modelName": meta["modelName"],
        "inOrderFields": list(meta["inOrderFields"]),
        "css": css,
        "cardTemplates": templates,
    }


def ensure_model(
    *,
    model_name: str = "Zhongwen",
    deck_dir: Path | None = None,
    url: str = "http://127.0.0.1:8765",
) -> str:
    names = invoke("modelNames", url=url)
    if model_name in names:
        return f"model exists: {model_name}"

    definition = load_model_definition(deck_dir)
    if definition["modelName"] != model_name:
        definition["modelName"] = model_name
    invoke("createModel", url=url, **definition)
    return f"model created: {model_name}"


def ensure_deck(
    *,
    deck_name: str = "ankia",
    options_name: str | None = None,
    deck_dir: Path | None = None,
    url: str = "http://127.0.0.1:8765",
) -> str:
    """Create deck if missing. Only apply vendored options when the deck is new.

    Existing decks keep their review settings untouched.
    """
    root = deck_dir or DECK_DIRECTORY
    options_name = options_name or deck_name
    decks = invoke("deckNames", url=url)
    created = deck_name not in decks
    if created:
        invoke("createDeck", url=url, deck=deck_name)
        options_path = root / "deck_options.json"
        desired = json.loads(options_path.read_text(encoding="utf-8"))
        desired["name"] = options_name
        config_id = _ensure_options_group(desired, options_name=options_name, url=url)
        invoke("setDeckConfigId", url=url, decks=[deck_name], configId=config_id)
        return f"deck created: {deck_name}; options: {options_name} (id={config_id})"

    return f"deck exists: {deck_name} (options left unchanged)"



def _ensure_options_group(
    desired: dict[str, Any],
    *,
    options_name: str,
    url: str,
) -> int:
    """Clone or reuse a deck options group, then apply desired settings."""
    # If this deck already points at a group with the right name, reuse its id.
    # Otherwise clone from Default (1).
    clone_id = invoke(
        "cloneDeckConfigId",
        url=url,
        name=options_name,
        cloneFrom=1,
    )
    if clone_id:
        config_id = int(clone_id)
    else:
        config_id = _find_config_id_by_name(options_name, url=url)
        if config_id is None:
            raise RuntimeError(
                f"deck options group {options_name!r} exists but its id could not be resolved"
            )

    payload = dict(desired)
    payload["id"] = config_id
    payload["name"] = options_name
    payload.setdefault("mod", 0)
    payload.setdefault("usn", -1)
    invoke("saveDeckConfig", url=url, config=payload)
    return config_id


def _find_config_id_by_name(options_name: str, *, url: str) -> int | None:
    """Best-effort: check configs attached to every deck name."""
    for deck in invoke("deckNames", url=url):
        cfg = invoke("getDeckConfig", url=url, deck=deck)
        if cfg and cfg.get("name") == options_name:
            return int(cfg["id"])
    return None
