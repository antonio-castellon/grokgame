from mesa.admin import (
    CREATOR,
    ENV,
    MISSING,
    OK,
    grant,
    is_admin,
    parse_user_ref,
    resolve_user_id,
    revoke,
)
from mesa.store import TableState


def test_env_ids_always_admin():
    assert is_admin(
        7,
        env_ids={7},
        chat_admin_ids=set(),
        granted=[],
    )


def test_chat_admin():
    assert is_admin(3, env_ids=set(), chat_admin_ids={3}, granted=[])
    assert not is_admin(4, env_ids=set(), chat_admin_ids={3}, granted=[])


def test_granted_admin():
    assert is_admin(9, env_ids=set(), chat_admin_ids=set(), granted=[9])


def test_grant_and_revoke():
    state = TableState(chat_id=1)
    assert grant(state, 9) == OK
    assert state.admins == [9]
    assert grant(state, 9) != MISSING
    assert revoke(state, 9, creator_id=1, env_ids=set()) == OK
    assert state.admins == []
    assert revoke(state, 9, creator_id=1, env_ids=set()) == MISSING


def test_cannot_revoke_creator():
    state = TableState(chat_id=1, admins=[1, 2], creator_id=1)
    assert revoke(state, 1, creator_id=1, env_ids=set()) == CREATOR
    assert 1 in state.admins


def test_env_admin_stays_admin_after_revoke():
    state = TableState(chat_id=1, admins=[5])
    assert revoke(state, 5, creator_id=1, env_ids={5}) == ENV
    assert 5 not in state.admins
    assert is_admin(5, env_ids={5}, chat_admin_ids=set(), granted=state.admins)


def test_parse_user_ref():
    assert parse_user_ref("@Ana") == (None, "ana")
    assert parse_user_ref("42") == (42, None)
    assert parse_user_ref("") == (None, None)


def test_resolve_from_mentions():
    assert resolve_user_id("@ana", {"ana": 99}) == 99
    assert resolve_user_id("99", {}) == 99
    assert resolve_user_id("@unknown", {}) is None
