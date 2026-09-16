import asyncio
from pathlib import Path

from mesa.gm.mock import MockGM
from mesa.parse import parse_cmd
from mesa.store import Store
from mesa.telegram.handlers import BridgeContext, BridgeUser, process_command


def _ctx(tmp_path: Path, user_id: int = 1, admin: bool = True) -> BridgeContext:
    store = Store(tmp_path)
    chat_admins = {1} if admin and user_id == 1 else set()
    if admin and user_id != 1:
        chat_admins = {user_id}
    return BridgeContext(
        chat_id=-100123,
        user=BridgeUser(id=user_id, name="Ana", username="ana"),
        store=store,
        gm=MockGM(),
        env_admin_ids=frozenset(),
        chat_admin_ids=chat_admins,
        creator_id=1,
        mentions={"ana": 1, "bob": 2},
    )


def _run(ctx: BridgeContext, text: str) -> str | None:
    return asyncio.run(process_command(ctx, text))


def test_plain_chat_does_not_call_gm(tmp_path: Path):
    ctx = _ctx(tmp_path)
    assert _run(ctx, "buenos días") is None
    assert not list(tmp_path.glob("*.json"))


def test_non_admin_cannot_new_game_reset_lang(tmp_path: Path):
    ctx = _ctx(tmp_path, user_id=99, admin=False)
    for text in ("/cmd new-game faro", "/cmd reset", "/cmd lang es"):
        say = _run(ctx, text)
        assert say is not None
        assert "admin" in say.lower()
    state = ctx.store.load(ctx.chat_id)
    assert state.commands == []
    assert state.phase == "lobby"


def test_join_rejected_in_lobby(tmp_path: Path):
    ctx = _ctx(tmp_path)
    say = _run(ctx, "/cmd join")
    assert say is not None
    assert "join" in say.lower() or "desconocido" in say.lower() or "unknown" in say.lower()
    state = ctx.store.load(ctx.chat_id)
    assert "join" not in state.command_verbs()


def test_acceptance_conversation(tmp_path: Path):
    admin = _ctx(tmp_path, user_id=1, admin=True)
    assert _run(admin, "/cmd lang es")
    say = _run(
        admin,
        "/cmd new-game juego de rol de suspense en un tren, 4 jugadores, dados solo en combates, sin magia",
    )
    assert say
    state = admin.store.load(admin.chat_id)
    assert "act" in state.command_verbs()
    listed = _run(admin, "/cmd cmd list")
    assert listed and "act" in listed
    _run(admin, "/cmd rules el tren no puede detenerse hasta el final")
    _run(admin, "/cmd limit cada acción máximo 2 frases")
    status = _run(admin, "/cmd status")
    assert status
    assert "el tren no puede detenerse hasta el final" in status
    assert "cada acción máximo 2 frases" in status

    player = BridgeContext(
        chat_id=admin.chat_id,
        user=BridgeUser(id=7, name="Pepe", username="pepe"),
        store=admin.store,
        gm=admin.gm,
        env_admin_ids=frozenset(),
        chat_admin_ids=set(),
        creator_id=1,
        mentions={},
    )
    joined = _run(player, "/cmd join")
    assert joined
    acted = _run(player, "/cmd act miro por la ventanilla")
    assert acted

    _run(
        admin,
        "/cmd new-game ahora es un concurso de acertijos sobre el mar, pistas de pago",
    )
    state = admin.store.load(admin.chat_id)
    verbs = state.command_verbs()
    assert "guess" in verbs
    assert "act" not in verbs
    listed = _run(admin, "/cmd cmd list")
    assert "guess" in listed
    assert "/cmd act" not in listed

    _run(admin, "/cmd lang en")
    _run(admin, "/cmd reset")
    state = admin.store.load(admin.chat_id)
    assert state.phase == "lobby"
    assert state.commands == []


def test_whoami_and_help(tmp_path: Path):
    ctx = _ctx(tmp_path)
    who = _run(ctx, "/cmd whoami")
    assert who and "1" in who and "Ana" in who
    help_text = _run(ctx, "/cmd help")
    assert help_text and "new-game" in help_text


def test_grant_revoke(tmp_path: Path):
    ctx = _ctx(tmp_path)
    say = _run(ctx, "/cmd grant 2")
    assert say is not None
    assert "added" in say.lower() or "añadido" in say.lower()
    state = ctx.store.load(ctx.chat_id)
    assert 2 in state.admins
    say = _run(ctx, "/cmd revoke 1")
    assert say is not None
    assert "creador" in say.lower() or "creator" in say.lower()


def test_parse_still_covers_spec_lines():
    assert parse_cmd("/cmd new-game texto largo aquí")
    assert parse_cmd("/cmd cmd list").verb == "cmd"
    assert parse_cmd("/cmd lang de").payload == "de"
