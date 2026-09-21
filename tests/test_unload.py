"""Unload verb: parse + admin-only process stop signal."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mesa.gm.mock import MockGM
from mesa.parse import ADMIN_VERBS, SYSTEM_VERBS, parse_cmd
from mesa.store import Store
from mesa.telegram.handlers import (
    BridgeContext,
    BridgeUser,
    Unload,
    process_command,
)


def test_unload_in_verb_sets():
    assert "unload" in SYSTEM_VERBS
    assert "unload" in ADMIN_VERBS


def test_parse_unload():
    p = parse_cmd("/cmd unload")
    assert p is not None
    assert p.verb == "unload"
    assert p.payload == ""


def _ctx(tmp_path: Path, user_id: int = 1, admin: bool = True) -> BridgeContext:
    store = Store(tmp_path)
    chat_admins = {user_id} if admin else set()
    return BridgeContext(
        chat_id=-100999,
        user=BridgeUser(id=user_id, name="Ana", username="ana"),
        store=store,
        gm=MockGM(),
        env_admin_ids=frozenset(),
        chat_admin_ids=chat_admins,
        creator_id=1,
        mentions={},
    )


def test_unload_admin_returns_sentinel(tmp_path: Path):
    ctx = _ctx(tmp_path, admin=True)
    result = asyncio.run(process_command(ctx, "/cmd unload"))
    assert isinstance(result, Unload)


def test_unload_non_admin_rejected(tmp_path: Path):
    ctx = _ctx(tmp_path, user_id=99, admin=False)
    result = asyncio.run(process_command(ctx, "/cmd unload"))
    assert result is not None
    assert not isinstance(result, Unload)
    assert "admin" in str(result).lower()
