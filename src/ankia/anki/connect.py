"""Minimal AnkiConnect client."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class AnkiConnectError(RuntimeError):
    pass


def invoke(
    action: str,
    *,
    url: str = "http://127.0.0.1:8765",
    **params: Any,
) -> Any:
    payload = {"action": action, "version": 6, "params": params}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise AnkiConnectError(
            f"AnkiConnect unreachable at {url}. Is Anki open with the add-on enabled?"
        ) from exc

    if body.get("error"):
        raise AnkiConnectError(f"{action}: {body['error']}")
    return body.get("result")
