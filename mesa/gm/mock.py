from __future__ import annotations

import re
from typing import Any

from mesa.gm.base import SCHEMA_REPLY
from mesa.parse import SYSTEM_VERBS
from mesa.skin import DIV, bullets, card

_RIDDLE_RE = re.compile(
    r"acertijo|acertijos|enigma|enigmas|\briddle|\briddles|\bpuzzle|\bpuzzles",
    re.IGNORECASE,
)
_TRIVIA_RE = re.compile(
    r"trivia|\bquiz\b|preguntas|opciones|multiple\s*choice|\bquestions\b",
    re.IGNORECASE,
)

_KIND_RIDDLE = "riddle"
_KIND_TRIVIA = "trivia"
_KIND_FREE = "free"

_HELP = {
    "es": {
        "join": "entrar a la mesa",
        "act": "declarar una acción",
        "look": "describir el lugar",
        "inventory": "ver lo que llevas",
        "guess": "probar una respuesta",
        "hint": "pedir una pista",
        "next": "pasar al siguiente",
        "a": "elegir opción A",
        "b": "elegir opción B",
        "c": "elegir opción C",
        "d": "elegir opción D",
        "score": "ver puntuación",
    },
    "fr": {
        "join": "rejoindre la table",
        "act": "déclarer une action",
        "look": "décrire le lieu",
        "inventory": "voir l'inventaire",
        "guess": "proposer une réponse",
        "hint": "demander un indice",
        "next": "passer au suivant",
        "a": "choisir l'option A",
        "b": "choisir l'option B",
        "c": "choisir l'option C",
        "d": "choisir l'option D",
        "score": "voir le score",
    },
    "de": {
        "join": "dem Tisch beitreten",
        "act": "eine Aktion erklären",
        "look": "den Ort beschreiben",
        "inventory": "Inventar anzeigen",
        "guess": "eine Antwort versuchen",
        "hint": "einen Hinweis bitten",
        "next": "weiter",
        "a": "Option A wählen",
        "b": "Option B wählen",
        "c": "Option C wählen",
        "d": "Option D wählen",
        "score": "Punktestand",
    },
    "en": {
        "join": "join the table",
        "act": "declare an action",
        "look": "describe the place",
        "inventory": "show what you carry",
        "guess": "try an answer",
        "hint": "ask for a hint",
        "next": "go to the next one",
        "a": "choose option A",
        "b": "choose option B",
        "c": "choose option C",
        "d": "choose option D",
        "score": "show the score",
    },
}

_SYSTEM_HELP = {
    "es": "sys  help lang new-game rules limit cmd status reset whoami grant revoke purge",
    "fr": "sys  help lang new-game rules limit cmd status reset whoami grant revoke purge",
    "de": "sys  help lang new-game rules limit cmd status reset whoami grant revoke purge",
    "en": "sys  help lang new-game rules limit cmd status reset whoami grant revoke purge",
}


def infer_kind(brief: str) -> str:
    if _RIDDLE_RE.search(brief or ""):
        return _KIND_RIDDLE
    if _TRIVIA_RE.search(brief or ""):
        return _KIND_TRIVIA
    return _KIND_FREE


def verbs_for_kind(kind: str) -> tuple[str, ...]:
    if kind == _KIND_RIDDLE:
        return ("join", "guess", "hint", "next")
    if kind == _KIND_TRIVIA:
        return ("join", "a", "b", "c", "d", "next", "score")
    return ("join", "act", "look", "inventory")


def infer_title(brief: str) -> str:
    text = (brief or "").strip()
    if not text:
        return "Mesa"
    first = re.split(r"[,.\n]", text, maxsplit=1)[0].strip()
    if not first:
        first = text[:60].strip()
    if len(first) > 60:
        first = first[:60].rstrip()
    return first[:1].upper() + first[1:]


def infer_rules(brief: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"[,;\n]", brief or "") if p.strip()]
    if len(parts) <= 1:
        return [brief.strip()] if brief.strip() else []
    return parts[1:]


def _lang(request: dict[str, Any]) -> str:
    lang = request.get("lang") or "en"
    return lang if lang in _HELP else "en"


def _user_name(request: dict[str, Any]) -> str:
    user = request.get("user") or {}
    return str(user.get("name") or user.get("username") or "player")


def _commands(kind: str, lang: str) -> list[dict[str, str]]:
    help_map = _HELP[lang]
    return [{"verb": verb, "help": help_map[verb]} for verb in verbs_for_kind(kind)]


def _reply(
    request: dict[str, Any],
    say: str,
    **overrides: Any,
) -> dict[str, Any]:
    table = request.get("table") or {}
    out: dict[str, Any] = {
        "schema": SCHEMA_REPLY,
        "say": say,
        "lang": _lang(request),
        "phase": table.get("phase") or "lobby",
        "title": table.get("title") or "",
        "commands": list(table.get("commands") or []),
        "rules": list(table.get("rules") or []),
        "limits": list(table.get("limits") or []),
        "blob": dict(table.get("blob") or {}),
        "dice_request": None,
    }
    out.update(overrides)
    return out


def _t(locale: str, key: str, **kwargs: Any) -> str:
    table = _SAY[locale if locale in _SAY else "en"]
    return table[key].format(**kwargs)


_SAY = {
    "es": {
        "tag_new": "nueva",
        "tag_cmds": "cmds",
        "tag_ok": "ok",
        "tag_lang": "lang",
        "tag_stop": "stop",
        "tag_reset": "reset",
        "tag_join": "join",
        "tag_dice": "dado",
        "lbl_rules": "reglas",
        "lbl_limits": "límites",
        "rules": "Regla añadida: {line}",
        "limit": "Límite añadido: {line}",
        "lang": "Idioma de la mesa: {lang}",
        "no_game_cmds": "ninguno — admin: /cmd new-game",
        "none": "(ninguno)",
        "reset": "Mesa cerrada. Lobby vacío.",
        "unknown": "desconocido: /cmd {verb}",
        "unknown_list": "ahora: {list}",
        "join": "{name} se sienta a la mesa.",
        "dice": "Tirada {detail}.",
        "empty": "(sin payload)",
        "hint_list": "/cmd cmd list",
    },
    "fr": {
        "tag_new": "nouvelle",
        "tag_cmds": "cmds",
        "tag_ok": "ok",
        "tag_lang": "lang",
        "tag_stop": "stop",
        "tag_reset": "reset",
        "tag_join": "join",
        "tag_dice": "dé",
        "lbl_rules": "règles",
        "lbl_limits": "limites",
        "rules": "Règle ajoutée : {line}",
        "limit": "Limite ajoutée : {line}",
        "lang": "Langue de la table : {lang}",
        "no_game_cmds": "aucune — admin : /cmd new-game",
        "none": "(aucun)",
        "reset": "Table fermée. Lobby vide.",
        "unknown": "inconnue : /cmd {verb}",
        "unknown_list": "maintenant : {list}",
        "join": "{name} s'assoit à la table.",
        "dice": "Jet {detail}.",
        "empty": "(sans payload)",
        "hint_list": "/cmd cmd list",
    },
    "de": {
        "tag_new": "neu",
        "tag_cmds": "cmds",
        "tag_ok": "ok",
        "tag_lang": "lang",
        "tag_stop": "stop",
        "tag_reset": "reset",
        "tag_join": "join",
        "tag_dice": "wurf",
        "lbl_rules": "regeln",
        "lbl_limits": "limits",
        "rules": "Regel hinzugefügt: {line}",
        "limit": "Limit hinzugefügt: {line}",
        "lang": "Sprache des Tisches: {lang}",
        "no_game_cmds": "keine — Admin: /cmd new-game",
        "none": "(keine)",
        "reset": "Tisch geschlossen. Leere Lobby.",
        "unknown": "unbekannt: /cmd {verb}",
        "unknown_list": "jetzt: {list}",
        "join": "{name} setzt sich an den Tisch.",
        "dice": "Wurf {detail}.",
        "empty": "(kein Payload)",
        "hint_list": "/cmd cmd list",
    },
    "en": {
        "tag_new": "new",
        "tag_cmds": "cmds",
        "tag_ok": "ok",
        "tag_lang": "lang",
        "tag_stop": "stop",
        "tag_reset": "reset",
        "tag_join": "join",
        "tag_dice": "dice",
        "lbl_rules": "rules",
        "lbl_limits": "limits",
        "rules": "Rule added: {line}",
        "limit": "Limit added: {line}",
        "lang": "Table language: {lang}",
        "no_game_cmds": "none yet — admin: /cmd new-game",
        "none": "(none)",
        "reset": "Table closed. Empty lobby.",
        "unknown": "unknown: /cmd {verb}",
        "unknown_list": "now: {list}",
        "join": "{name} sits at the table.",
        "dice": "Roll {detail}.",
        "empty": "(no payload)",
        "hint_list": "/cmd cmd list",
    },
}


def format_command_list(commands: list[dict[str, str]], lang: str) -> str:
    lines: list[str] = []
    if not commands:
        lines.append(_t(lang, "no_game_cmds"))
    else:
        for item in commands:
            verb = item.get("verb", "")
            help_text = item.get("help", "")
            lines.append(f"{verb}  {help_text}".strip() if help_text else verb)
    lines.append(DIV)
    lines.append(_SYSTEM_HELP[lang if lang in _SYSTEM_HELP else "en"])
    return card(_t(lang, "tag_cmds"), lines)


def current_verb_list(commands: list[dict[str, str]]) -> str:
    game = [str(c.get("verb") or "") for c in commands if c.get("verb")]
    system = sorted(SYSTEM_VERBS)
    parts = game + system
    return ", ".join(parts) if parts else "-"


class MockGM:
    """Intelligent echo. Infers a command list from the new-game brief; no combat engine."""

    async def reply(self, request: dict[str, Any]) -> dict[str, Any] | None:
        verb = str(request.get("verb") or "")
        payload = str(request.get("payload") or "")
        lang = _lang(request)
        table = request.get("table") or {}

        if verb == "new-game":
            kind = infer_kind(payload)
            title = infer_title(payload)
            rules = infer_rules(payload)
            commands = _commands(kind, lang)
            rules_txt = "; ".join(rules) if rules else _t(lang, "none")
            return _reply(
                request,
                card(
                    _t(lang, "tag_new"),
                    [
                        title,
                        payload or _t(lang, "empty"),
                        DIV,
                        f"{_t(lang, 'lbl_rules')}  {rules_txt}",
                        _t(lang, "hint_list"),
                    ],
                ),
                phase="playing",
                title=title,
                commands=commands,
                rules=rules,
                limits=[],
                blob={},
            )

        if verb == "rules":
            rules = list(table.get("rules") or [])
            line = payload.strip()
            if line:
                rules.append(line)
            return _reply(
                request,
                card(
                    _t(lang, "tag_ok"),
                    [_t(lang, "rules", line=line or _t(lang, "empty"))],
                ),
                rules=rules,
            )

        if verb == "limit":
            limits = list(table.get("limits") or [])
            line = payload.strip()
            if line:
                limits.append(line)
            return _reply(
                request,
                card(
                    _t(lang, "tag_ok"),
                    [_t(lang, "limit", line=line or _t(lang, "empty"))],
                ),
                limits=limits,
            )

        if verb == "lang":
            new_lang = payload.strip().lower() or lang
            say_lang = new_lang if new_lang in _SAY else lang
            return _reply(
                request,
                card(
                    _t(say_lang, "tag_lang"),
                    [_t(say_lang, "lang", lang=new_lang)],
                ),
                lang=new_lang,
            )

        if verb == "cmd":
            return _reply(
                request,
                format_command_list(list(table.get("commands") or []), lang),
            )

        if verb == "status":
            return _reply(request, _status_say(table, lang))

        if verb == "reset":
            return _reply(
                request,
                card(_t(lang, "tag_reset"), [_t(lang, "reset")]),
                phase="lobby",
                title="",
                commands=[],
                rules=[],
                limits=[],
                blob={},
            )

        if verb == "dice-result":
            dice = request.get("dice") or {}
            detail = dice.get("detail") or dice.get("expr") or ""
            return _reply(
                request,
                card(_t(lang, "tag_dice"), [_t(lang, "dice", detail=detail)]),
            )

        known = {
            str(c.get("verb") or "").lower()
            for c in (table.get("commands") or [])
        }
        if verb not in known:
            return _reply(
                request,
                card(
                    _t(lang, "tag_stop"),
                    [
                        _t(lang, "unknown", verb=verb),
                        _t(
                            lang,
                            "unknown_list",
                            list=current_verb_list(list(table.get("commands") or [])),
                        ),
                    ],
                ),
            )

        name = _user_name(request)
        if verb == "join":
            say = card(_t(lang, "tag_join"), [_t(lang, "join", name=name)])
        else:
            extra = payload if payload else "·"
            say = card(verb, [name, extra])
        return _reply(request, say)


def _status_say(table: dict[str, Any], lang: str) -> str:
    rules = [str(r) for r in (table.get("rules") or [])]
    limits = [str(x) for x in (table.get("limits") or [])]
    commands = table.get("commands") or []
    none = _t(lang, "none")
    cmd_txt = ", ".join(c.get("verb", "") for c in commands) or none
    title = str(table.get("title") or none)
    return card(
        title,
        [
            f"{table.get('phase') or 'lobby'} · {lang}",
            str(table.get("brief") or none),
            DIV,
            _t(lang, "lbl_rules"),
            *bullets(rules, none),
            _t(lang, "lbl_limits"),
            *bullets(limits, none),
            DIV,
            f"cmds  {cmd_txt}",
        ],
    )
