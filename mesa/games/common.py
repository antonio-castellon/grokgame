from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Turn:
    say: str
    state: dict[str, Any]
    commands: list[dict[str, str]] | None = None
    title: str | None = None
    rules: list[str] | None = None
    phase: str = "playing"


def uid(request: dict[str, Any]) -> str:
    user = request.get("user") or {}
    return str(user.get("id") or "0")


def uname(request: dict[str, Any]) -> str:
    user = request.get("user") or {}
    return str(user.get("name") or user.get("username") or "player")


def cmds(pairs: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"verb": v, "help": h} for v, h in pairs]


def pick(lang: str, table: dict[str, str]) -> str:
    return table.get(lang) or table["en"]
