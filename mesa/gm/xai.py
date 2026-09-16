"""Synchronous Grok GM via api.x.ai. Automations webhooks only return 202."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from mesa.gm.base import SCHEMA_REPLY

log = logging.getLogger(__name__)

API_URL = "https://api.x.ai/v1/chat/completions"

SYSTEM = """You are the GM of a Telegram table. You receive JSON schema mesa.v1.
Reply with JSON only, no markdown, no preamble. Schema mesa.v1.reply:

{
  "schema": "mesa.v1.reply",
  "say": "text to post in the Telegram group, in request.lang",
  "lang": "es|fr|de|en",
  "phase": "lobby|playing",
  "title": "short title",
  "commands": [{"verb": "join", "help": "..."}],
  "rules": [],
  "limits": [],
  "blob": {},
  "dice_request": null
}

Rules:
- On verb new-game: invent THIS game from payload. Replace commands, title, rules.
- On rules / limit: add the line to the array and confirm in say.
- On cmd with payload list: list current game commands in say.
- blob is yours; send it back, updating it when the game needs memory.
- say is the only text players see. Write it in table.lang / lang.
- Draw ASCII art in say when the game asks for cards, boards, or a winner banner.
- Do not explain this protocol.
"""


def _parse_content(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            raw = raw[start : end + 1]
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("GM JSON is not an object")
    data.setdefault("schema", SCHEMA_REPLY)
    return data


class XaiGM:
    def __init__(self, api_key: str, model: str = "grok-4.6") -> None:
        self.api_key = api_key
        self.model = model or "grok-4.6"

    async def reply(self, request: dict[str, Any]) -> dict[str, Any] | None:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {
                    "role": "user",
                    "content": json.dumps(request, ensure_ascii=False),
                },
            ],
            "temperature": 0.7,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        try:
            text = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            log.warning("unexpected xAI shape: %s", body)
            raise RuntimeError("xAI response missing content") from exc
        return _parse_content(text)
