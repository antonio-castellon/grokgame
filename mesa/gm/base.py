from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from mesa.parse import SUPPORTED_LANGS
from mesa.store import TableState

SCHEMA_REQUEST = "mesa.v1"
SCHEMA_REPLY = "mesa.v1.reply"

EXPECT = (
    "Responde JSON mesa.v1.reply. Texto al grupo en table.lang / lang. "
    "No expliques el protocolo."
)


@runtime_checkable
class GameMaster(Protocol):
    async def reply(self, request: dict[str, Any]) -> dict[str, Any] | None:
        """Return a mesa.v1.reply dict, or None if there is no body."""


def build_request(
    state: TableState,
    *,
    user_id: int,
    user_name: str,
    username: str | None,
    is_admin: bool,
    verb: str,
    payload: str,
    dice: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA_REQUEST,
        "chat_id": state.chat_id,
        "user": {
            "id": user_id,
            "name": user_name,
            "username": username,
            "is_admin": is_admin,
        },
        "lang": state.lang if state.lang in SUPPORTED_LANGS else "en",
        "verb": verb,
        "payload": payload,
        "dice": dice,
        "table": {
            "phase": state.phase,
            "title": state.title,
            "brief": state.brief,
            "rules": list(state.rules),
            "limits": list(state.limits),
            "commands": list(state.commands),
            "players": state.players_list(),
            "blob": dict(state.blob),
        },
        "expect": EXPECT,
    }


def apply_reply(state: TableState, reply: dict[str, Any] | None) -> None:
    if not reply:
        return
    lang = reply.get("lang")
    if isinstance(lang, str) and lang in SUPPORTED_LANGS:
        state.lang = lang
    phase = reply.get("phase")
    if isinstance(phase, str) and phase:
        state.phase = phase
    if "title" in reply and reply["title"] is not None:
        state.title = str(reply["title"])
    if "commands" in reply and reply["commands"] is not None:
        state.commands = list(reply["commands"])
    if "rules" in reply and reply["rules"] is not None:
        state.rules = [str(r) for r in reply["rules"]]
    if "limits" in reply and reply["limits"] is not None:
        state.limits = [str(x) for x in reply["limits"]]
    if "blob" in reply and reply["blob"] is not None:
        blob = reply["blob"]
        state.blob = dict(blob) if isinstance(blob, dict) else {"value": blob}


def empty_reply(lang: str, say: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA_REPLY,
        "say": say,
        "lang": lang,
        "phase": None,
        "title": None,
        "commands": None,
        "rules": None,
        "limits": None,
        "blob": None,
        "dice_request": None,
    }
