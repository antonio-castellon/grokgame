import asyncio

from mesa.gm.base import build_request
from mesa.gm.mock import MockGM, infer_kind, verbs_for_kind
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


def test_new_game_role_verbs():
    reply = _run(
        _req(
            "new-game",
            "juego de rol de suspense en un tren, 4 jugadores, dados solo en combates, sin magia",
        )
    )
    verbs = [c["verb"] for c in reply["commands"]]
    assert verbs == ["join", "act", "look", "inventory"]
    assert reply["phase"] == "playing"
    assert reply["lang"] == "es"
    assert "tren" in reply["say"].lower() or "Tren" in reply["title"] or "tren" in reply["title"].lower()


def test_new_game_riddle_verbs():
    reply = _run(_req("new-game", "concurso de acertijos sobre el mar, pistas de pago"))
    assert [c["verb"] for c in reply["commands"]] == ["join", "guess", "hint", "next"]


def test_new_game_trivia_verbs():
    reply = _run(_req("new-game", "trivia de cine con 4 opciones"))
    assert [c["verb"] for c in reply["commands"]] == [
        "join",
        "a",
        "b",
        "c",
        "d",
        "next",
        "score",
    ]


def test_second_new_game_replaces_commands():
    first = _run(_req("new-game", "rol en un tren"))
    assert "act" in [c["verb"] for c in first["commands"]]
    second = _run(_req("new-game", "acertijo sobre el mar"))
    verbs = [c["verb"] for c in second["commands"]]
    assert "act" not in verbs
    assert "guess" in verbs


def test_rules_and_limit_accumulate():
    reply = _run(
        _req(
            "rules",
            "el tren no puede detenerse hasta el final",
            rules=["sin magia"],
        )
    )
    assert reply["rules"] == ["sin magia", "el tren no puede detenerse hasta el final"]
    reply2 = _run(
        _req("limit", "cada acción máximo 2 frases", limits=["max 4 jugadores"])
    )
    assert reply2["limits"] == ["max 4 jugadores", "cada acción máximo 2 frases"]


def test_lang_switches_say_template():
    es = _run(_req("lang", "es"))
    assert "Idioma" in es["say"]
    fr = _run(_req("lang", "fr"))
    assert "Langue" in fr["say"]
    de = _run(_req("lang", "de"))
    assert "Sprache" in de["say"]
    en = _run(_req("lang", "en"))
    assert "language" in en["say"].lower()


def test_cmd_list_includes_system_and_game():
    commands = [{"verb": "join", "help": "entrar a la mesa"}]
    reply = _run(_req("cmd", "list", commands=commands))
    say = reply["say"]
    assert "join" in say
    assert "new-game" in say
    assert "help" in say


def test_unknown_game_verb_lists_current():
    commands = [{"verb": "guess", "help": "probar"}]
    reply = _run(_req("cast", "bola de fuego", commands=commands))
    assert "guess" in reply["say"]
    assert "cast" in reply["say"]


def test_reset_clears_commands_and_blob():
    reply = _run(
        _req("reset", "", commands=[{"verb": "act", "help": "x"}], blob={"opaque": 1})
    )
    assert reply["phase"] == "lobby"
    assert reply["commands"] == []
    assert reply["blob"] == {}


def test_kind_heuristics():
    assert infer_kind("un enigma en el faro") == "riddle"
    assert verbs_for_kind("riddle") == ("join", "guess", "hint", "next")
    assert infer_kind("preguntas con opciones") == "trivia"
    assert infer_kind("misterio en un faro") == "free"
