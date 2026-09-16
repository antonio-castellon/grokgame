from __future__ import annotations

from mesa.store import TableState

# grant/revoke outcomes
OK = "ok"
ALREADY = "already"
CREATOR = "creator"
MISSING = "missing"
ENV = "env"
BAD_REF = "bad_ref"


def is_admin(
    user_id: int,
    *,
    env_ids: frozenset[int] | set[int],
    chat_admin_ids: set[int],
    granted: list[int],
) -> bool:
    """Env ids always win, then Telegram chat admins, then /cmd grant."""
    return user_id in env_ids or user_id in chat_admin_ids or user_id in granted


def parse_user_ref(payload: str) -> tuple[int | None, str | None]:
    """Return (user_id, username_without_at). Either side may be None."""
    text = (payload or "").strip()
    if not text:
        return None, None
    if text.startswith("@"):
        name = text[1:].strip()
        return None, name.lower() or None
    if text.isdigit() or (text[0] == "-" and text[1:].isdigit()):
        return int(text), None
    return None, text.lower()


def resolve_user_id(
    payload: str,
    mentions: dict[str, int],
) -> int | None:
    user_id, username = parse_user_ref(payload)
    if user_id is not None:
        return user_id
    if not username:
        return None
    return mentions.get(username.lower())


def grant(state: TableState, user_id: int) -> str:
    if user_id in state.admins:
        return ALREADY
    state.admins.append(user_id)
    return OK


def revoke(
    state: TableState,
    user_id: int,
    *,
    creator_id: int | None,
    env_ids: frozenset[int] | set[int],
) -> str:
    if creator_id is not None and user_id == creator_id:
        return CREATOR
    if user_id in env_ids:
        if user_id in state.admins:
            state.admins.remove(user_id)
        return ENV
    if user_id not in state.admins:
        return MISSING
    state.admins.remove(user_id)
    return OK
