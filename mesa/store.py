from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


LOG_LIMIT = 16
PAYLOAD_LOG_LIMIT = 80


def _default_state(chat_id: int) -> dict[str, Any]:
    return {
        "chat_id": chat_id,
        "lang": "en",
        "phase": "lobby",
        "title": "",
        "brief": "",
        "rules": [],
        "limits": [],
        "commands": [],
        "admins": [],
        "players": {},
        "blob": {},
        "log": [],
        "creator_id": None,
    }


@dataclass
class TableState:
    chat_id: int
    lang: str = "en"
    phase: str = "lobby"
    title: str = ""
    brief: str = ""
    rules: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    commands: list[dict[str, str]] = field(default_factory=list)
    admins: list[int] = field(default_factory=list)
    players: dict[str, dict[str, Any]] = field(default_factory=dict)
    blob: dict[str, Any] = field(default_factory=dict)
    log: list[dict[str, Any]] = field(default_factory=list)
    creator_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "chat_id": self.chat_id,
            "lang": self.lang,
            "phase": self.phase,
            "title": self.title,
            "brief": self.brief,
            "rules": list(self.rules),
            "limits": list(self.limits),
            "commands": list(self.commands),
            "admins": list(self.admins),
            "players": dict(self.players),
            "blob": dict(self.blob),
            "log": list(self.log),
            "creator_id": self.creator_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TableState:
        chat_id = int(data["chat_id"])
        base = _default_state(chat_id)
        base.update(data)
        players = base.get("players") or {}
        if isinstance(players, list):
            players = {str(p["id"]): p for p in players if "id" in p}
        admins = [int(a) for a in (base.get("admins") or [])]
        creator = base.get("creator_id")
        return cls(
            chat_id=chat_id,
            lang=str(base.get("lang") or "en"),
            phase=str(base.get("phase") or "lobby"),
            title=str(base.get("title") or ""),
            brief=str(base.get("brief") or ""),
            rules=list(base.get("rules") or []),
            limits=list(base.get("limits") or []),
            commands=list(base.get("commands") or []),
            admins=admins,
            players=dict(players),
            blob=dict(base.get("blob") or {}),
            log=list(base.get("log") or []),
            creator_id=int(creator) if creator is not None else None,
        )

    def add_log(self, verb: str, payload: str, user_id: int, user_name: str) -> None:
        self.log.append(
            {
                "verb": verb,
                "payload": (payload or "")[:PAYLOAD_LOG_LIMIT],
                "user": user_name,
                "user_id": user_id,
            }
        )
        self.log = self.log[-LOG_LIMIT:]

    def reset_table(self) -> None:
        """New mesa: drop game verbs, rules, blob. Keep lang/admins/creator."""
        self.phase = "lobby"
        self.title = ""
        self.brief = ""
        self.rules = []
        self.limits = []
        self.commands = []
        self.players = {}
        self.blob = {}

    def command_verbs(self) -> set[str]:
        verbs: set[str] = set()
        for item in self.commands:
            verb = str(item.get("verb") or "").lower()
            if verb:
                verbs.add(verb)
        return verbs

    def upsert_player(self, user_id: int, name: str) -> None:
        key = str(user_id)
        existing = self.players.get(key) or {}
        flags = existing.get("flags") if isinstance(existing.get("flags"), dict) else {}
        self.players[key] = {"id": user_id, "name": name, "flags": flags}

    def players_list(self) -> list[dict[str, Any]]:
        return list(self.players.values())


class Store:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, chat_id: int) -> Path:
        return self.data_dir / f"{chat_id}.json"

    def load(self, chat_id: int) -> TableState:
        path = self._path(chat_id)
        if not path.exists():
            return TableState(chat_id=chat_id)
        raw = json.loads(path.read_text(encoding="utf-8"))
        return TableState.from_dict(raw)

    def save(self, state: TableState) -> None:
        path = self._path(state.chat_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(path)

    def delete(self, chat_id: int) -> None:
        path = self._path(chat_id)
        if path.exists():
            path.unlink()
