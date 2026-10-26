"""Minimal Gemini structured-output client (free-tier friendly)."""
from __future__ import annotations

import os
import time
from typing import Any, TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-flash", abbreviation: str = "gemini_flash"):
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Set GEMINI_API_KEY (or GOOGLE_API_KEY) in .env or the environment")
        self.model = model
        self.abbreviation = abbreviation
        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        *,
        schema: type[T],
        system: str,
        user: str,
        max_retries: int = 5,
    ) -> T:
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self.model,
                    contents=user,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
                text = (response.text or "").strip()
                if not text:
                    raise ValueError("empty Gemini response")
                return schema.model_validate_json(text)
            except Exception as exc:  # noqa: BLE001 — retry free-tier blips
                last_err = exc
                msg = str(exc).lower()
                # backoff harder on rate limits
                delay = 2 ** attempt
                if "429" in msg or "rate" in msg or "resource_exhausted" in msg:
                    delay = max(delay, 15)
                time.sleep(delay)
        raise RuntimeError(f"Gemini failed after {max_retries} attempts: {last_err}")

    def generate_dict(
        self,
        *,
        schema: type[BaseModel],
        system: str,
        user: str,
        max_retries: int = 5,
    ) -> dict[str, Any]:
        return self.generate(schema=schema, system=system, user=user, max_retries=max_retries).model_dump()
