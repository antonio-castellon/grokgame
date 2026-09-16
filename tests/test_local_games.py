import asyncio

from mesa.games import pick_game
from mesa.gm.base import build_request
from mesa.gm.mock import MockGM
from mesa.store import TableState


def _run(request):
    return asyncio.run(MockGM().reply(request))


def _req(verb, payload="", **table_over):
    state = TableState(chat_id=-100123, lang="es")
    for key, value in table_over.items():
        setattr(state, key, value)
    return build_request(
        state,
        user_id=7,
        user_name="Ana",
        username="ana",
        is_admin=True,
        verb=verb,
        payload=payload,
    )


def test_catalog_picks():
    assert pick_game("juego de cartas del 21").id == "blackjack"
    assert pick_game("mini rol con un dragón").id == "rpg"
    assert pick_game("tres en raya").id == "tictactoe"
    assert pick_game("piedra papel tijera").id == "rps"
    assert pick_game("misterio en un faro") is None


def test_blackjack_hit_and_ascii():
    start = _run(_req("new-game", "cartas del 21"))
    assert start["blob"]["_local"] == "blackjack"
    verbs = [c["verb"] for c in start["commands"]]
    assert "otra" in verbs and "planto" in verbs
    blob = start["blob"]
    joined = _run(_req("join", "", commands=start["commands"], blob=blob, phase="playing"))
    blob = joined["blob"]
    hit = _run(_req("otra", "", commands=start["commands"], blob=blob, phase="playing"))
    assert "pts" in hit["say"]
    assert "┌" in hit["say"]


def test_list_and_load_via_bridge(tmp_path):
    from pathlib import Path

    from tests.test_bridge import _ctx, _plain, _run

    ctx = _ctx(tmp_path)
    listed = _run(ctx, "/cmd list games")
    assert listed
    body = _plain(listed)
    assert "blackjack" in body
    assert "rpg" in body
    say = _run(ctx, "/cmd load blackjack")
    assert say
    state = ctx.store.load(ctx.chat_id)
    assert state.blob.get("_local") == "blackjack"
    assert "otra" in state.command_verbs()
    joined = _run(ctx, "/cmd join")
    assert joined
    hit = _run(ctx, "/cmd otra")
    assert hit and "pts" in hit


def test_rpg_join_look():
    start = _run(_req("new-game", "aventura de rol"))
    blob = start["blob"]
    cmds = start["commands"]
    joined = _run(_req("join", "", commands=cmds, blob=blob, phase="playing"))
    blob = joined["blob"]
    looked = _run(_req("look", "", commands=cmds, blob=blob, phase="playing"))
    assert "HP" in looked["say"]
