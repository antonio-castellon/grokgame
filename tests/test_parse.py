from mesa.parse import parse_cmd


def test_new_game_long_payload():
    parsed = parse_cmd(
        "/cmd new-game misterio en un faro, 3 jugadores, sin muerte permanente"
    )
    assert parsed is not None
    assert parsed.verb == "new-game"
    assert parsed.payload == "misterio en un faro, 3 jugadores, sin muerte permanente"


def test_cmd_list():
    parsed = parse_cmd("/cmd cmd list")
    assert parsed is not None
    assert parsed.verb == "cmd"
    assert parsed.payload == "list"


def test_lang_de():
    parsed = parse_cmd("/cmd lang de")
    assert parsed is not None
    assert parsed.verb == "lang"
    assert parsed.payload == "de"


def test_examples_from_brief():
    cases = [
        ("/cmd lang es", "lang", "es"),
        ("/cmd lang fr", "lang", "fr"),
        ("/cmd rules no se puede matar NPCs infantiles", "rules", "no se puede matar NPCs infantiles"),
        ("/cmd limit max 4 jugadores", "limit", "max 4 jugadores"),
        ("/cmd status", "status", ""),
        ("/cmd reset", "reset", ""),
        ("/cmd act abro el cajón izquierdo", "act", "abro el cajón izquierdo"),
        ("/cmd whoami", "whoami", ""),
    ]
    for text, verb, payload in cases:
        parsed = parse_cmd(text)
        assert parsed is not None, text
        assert parsed.verb == verb, text
        assert parsed.payload == payload, text


def test_alias_without_slash():
    parsed = parse_cmd("cmd new-game faro")
    assert parsed is not None
    assert parsed.verb == "new-game"
    assert parsed.payload == "faro"


def test_bot_username_suffix():
    parsed = parse_cmd("/cmd@MesaBot lang es")
    assert parsed is not None
    assert parsed.verb == "lang"
    assert parsed.payload == "es"


def test_plain_chat_is_not_a_command():
    assert parse_cmd("buenos días") is None
    assert parse_cmd("hello there") is None
    assert parse_cmd("/start") is None
    assert parse_cmd("") is None
    assert parse_cmd(None) is None


def test_invalid_verb_rejected():
    assert parse_cmd("/cmd") is None
    assert parse_cmd("/cmd foo_bar") is None
    assert parse_cmd("/cmd ThisIsWayTooLongForTheVerbFieldLimitXXX") is None


def test_verb_is_lowercased():
    parsed = parse_cmd("/CMD LANG ES")
    assert parsed is not None
    assert parsed.verb == "lang"
    assert parsed.payload == "ES"
