from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

from telegram import Update
from telegram.constants import ChatType, ParseMode
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from mesa import admin as admin_mod
from mesa.config import Config
from mesa.dice import roll as roll_dice
from mesa.games import catalog_lines, get_game, resolve_game
from mesa.gm.base import GameMaster, apply_reply, build_request
from mesa.parse import (
    ADMIN_VERBS,
    PURGE_CONFIRM,
    PURGE_VERBS,
    SUPPORTED_LANGS,
    SYSTEM_VERBS,
    parse_cmd,
)
from mesa.skin import DIV, as_html_pre, bullets, card
from mesa.store import Store, TableState
from mesa.telegram.purge import bot_can_delete, purge_upto

log = logging.getLogger(__name__)

TG_LIMIT = 4000

_MSG = {
    "es": {
        "tag_help": "ayuda",
        "tag_you": "tú",
        "tag_stop": "stop",
        "tag_ok": "ok",
        "tag_mesa": "mesa",
        "tag_lang": "lang",
        "tag_err": "err",
        "help_intro": "Un admin describe el juego; Grok inventa reglas y comandos.",
        "help_sys": "sys  help lang new-game rules limit cmd status reset whoami grant revoke clear list load",
        "help_after": "Locales: /cmd list games",
        "help_load": "id para /cmd load <id>:",
        "tag_purge": "clear",
        "purge_need": "Borra TODOS los mensajes de cualquiera. Confirma: /cmd clear all",
        "purge_work": "Borrando todos los mensajes…",
        "purge_ok": "Listo. Borrados ~{n} (omitidos {fail}).",
        "purge_denied": "El bot debe ser admin con permiso Borrar mensajes.",
        "purge_none": "Nada que borrar.",
        "yes": "sí",
        "no": "no",
        "not_admin": "Solo un admin de la mesa puede usar /cmd {verb}.",
        "unknown": "desconocido: /cmd {verb}",
        "unknown_list": "ahora: {list}",
        "bad_lang": "Idioma no válido. Usa: es, fr, de, en.",
        "grant_ok": "admin añadido: {who}",
        "grant_already": "ya era admin: {who}",
        "grant_bad": "usa @usuario o un id: /cmd grant @ana",
        "revoke_ok": "admin revocado: {who}",
        "revoke_missing": "no era admin: {who}",
        "revoke_creator": "No se puede revocar al creador del grupo.",
        "revoke_env": "{who} sigue admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "usa @usuario o un id: /cmd revoke 123",
        "webhook_empty": "El GM no devolvió cuerpo.",
        "rule_ok": "Regla añadida: {line}",
        "limit_ok": "Límite añadido: {line}",
        "new_game_empty": "Grok recibió new-game, pero el webhook no envía el relato al grupo. Pon WEBHOOK_REPLY=telegram (el Agent en la VM escribe en el grupo) o XAI_API_KEY.",
        "agent_woken": "Máster despertado. La respuesta llega desde el Agent (VM), no por el webhook.",
        "gm_error": "El GM no respondió ({err}).",
        "dice_bad": "Dado inválido: {expr}",
        "lang_local": "Idioma de la mesa: {lang}",
        "lbl_rules": "reglas",
        "lbl_limits": "límites",
        "lbl_cmds": "cmds",
        "lbl_pcs": "pcs",
        "none": "(ninguno)",
        "tag_games": "juegos",
        "games_hint": "/cmd load blackjack",
        "load_bad": "Juego desconocido. /cmd list games",
        "load_need": "Indica el juego: /cmd load blackjack",
    },
    "fr": {
        "tag_help": "aide",
        "tag_you": "toi",
        "tag_stop": "stop",
        "tag_ok": "ok",
        "tag_mesa": "table",
        "tag_lang": "lang",
        "tag_err": "err",
        "help_intro": "Un admin décrit le jeu ; Grok invente règles et commandes.",
        "help_sys": "sys  help lang new-game rules limit cmd status reset whoami grant revoke clear list load",
        "help_after": "Locaux : /cmd list games",
        "help_load": "id pour /cmd load <id> :",
        "tag_purge": "clear",
        "purge_need": "Efface TOUS les messages de n'importe qui. Confirme : /cmd clear all",
        "purge_work": "Suppression de tous les messages…",
        "purge_ok": "Fait. Supprimés ~{n} (ignorés {fail}).",
        "purge_denied": "Le bot doit être admin avec le droit Supprimer des messages.",
        "purge_none": "Rien à supprimer.",
        "yes": "oui",
        "no": "non",
        "not_admin": "Seul un admin de la table peut utiliser /cmd {verb}.",
        "unknown": "inconnue : /cmd {verb}",
        "unknown_list": "maintenant : {list}",
        "bad_lang": "Langue invalide. Utilise : es, fr, de, en.",
        "grant_ok": "admin ajouté : {who}",
        "grant_already": "déjà admin : {who}",
        "grant_bad": "indique @user ou un id : /cmd grant @ana",
        "revoke_ok": "admin révoqué : {who}",
        "revoke_missing": "n'était pas admin : {who}",
        "revoke_creator": "On ne peut pas révoquer le créateur du groupe.",
        "revoke_env": "{who} reste admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "indique @user ou un id : /cmd revoke 123",
        "webhook_empty": "Le GM n'a renvoyé aucun corps.",
        "rule_ok": "Règle ajoutée : {line}",
        "limit_ok": "Limite ajoutée : {line}",
        "new_game_empty": "Grok a reçu new-game, mais le webhook n'envoie pas le récit. Ajoute XAI_API_KEY (console.x.ai).",
        "agent_woken": "Maître réveillé. La réponse vient de l'Agent (VM), pas du webhook.",
        "gm_error": "Le GM n'a pas répondu ({err}).",
        "dice_bad": "Dé invalide : {expr}",
        "lang_local": "Langue de la table : {lang}",
        "lbl_rules": "règles",
        "lbl_limits": "limites",
        "lbl_cmds": "cmds",
        "lbl_pcs": "pcs",
        "none": "(aucun)",
        "tag_games": "jeux",
        "games_hint": "/cmd load blackjack",
        "load_bad": "Jeu inconnu. /cmd list games",
        "load_need": "Indique le jeu : /cmd load blackjack",
    },
    "de": {
        "tag_help": "hilfe",
        "tag_you": "du",
        "tag_stop": "stop",
        "tag_ok": "ok",
        "tag_mesa": "tisch",
        "tag_lang": "lang",
        "tag_err": "err",
        "help_intro": "Ein Admin beschreibt das Spiel; Grok erfindet Regeln und Befehle.",
        "help_sys": "sys  help lang new-game rules limit cmd status reset whoami grant revoke clear list load",
        "help_after": "Lokal: /cmd list games",
        "help_load": "id für /cmd load <id>:",
        "tag_purge": "clear",
        "purge_need": "Löscht ALLE Nachrichten von jedem. Bestätigen: /cmd clear all",
        "purge_work": "Lösche alle Nachrichten…",
        "purge_ok": "Fertig. Gelöscht ~{n} (übersprungen {fail}).",
        "purge_denied": "Bot muss Admin mit Recht Nachrichten löschen sein.",
        "purge_none": "Nichts zu löschen.",
        "yes": "ja",
        "no": "nein",
        "not_admin": "Nur ein Tisch-Admin darf /cmd {verb} nutzen.",
        "unknown": "unbekannt: /cmd {verb}",
        "unknown_list": "jetzt: {list}",
        "bad_lang": "Ungültige Sprache. Nutze: es, fr, de, en.",
        "grant_ok": "Admin hinzugefügt: {who}",
        "grant_already": "war bereits Admin: {who}",
        "grant_bad": "gib @user oder eine id: /cmd grant @ana",
        "revoke_ok": "Admin entzogen: {who}",
        "revoke_missing": "war kein Admin: {who}",
        "revoke_creator": "Der Gruppenersteller kann nicht entzogen werden.",
        "revoke_env": "{who} bleibt Admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "gib @user oder eine id: /cmd revoke 123",
        "webhook_empty": "Der GM hat keinen Body zurückgegeben.",
        "rule_ok": "Regel hinzugefügt: {line}",
        "limit_ok": "Limit hinzugefügt: {line}",
        "new_game_empty": "Grok hat new-game empfangen, aber der Webhook liefert keinen Text. WEBHOOK_REPLY=telegram oder XAI_API_KEY.",
        "agent_woken": "Master geweckt. Antwort kommt vom Agent (VM), nicht vom Webhook.",
        "gm_error": "Der GM hat nicht geantwortet ({err}).",
        "dice_bad": "Ungültiger Würfel: {expr}",
        "lang_local": "Sprache des Tisches: {lang}",
        "lbl_rules": "regeln",
        "lbl_limits": "limits",
        "lbl_cmds": "cmds",
        "lbl_pcs": "pcs",
        "none": "(keine)",
        "tag_games": "spiele",
        "games_hint": "/cmd load blackjack",
        "load_bad": "Unbekanntes Spiel. /cmd list games",
        "load_need": "Spiel angeben: /cmd load blackjack",
    },
    "en": {
        "tag_help": "help",
        "tag_you": "you",
        "tag_stop": "stop",
        "tag_ok": "ok",
        "tag_mesa": "table",
        "tag_lang": "lang",
        "tag_err": "err",
        "help_intro": "An admin describes the game; Grok invents rules and commands.",
        "help_sys": "sys  help lang new-game rules limit cmd status reset whoami grant revoke clear list load",
        "help_after": "Local: /cmd list games",
        "help_load": "id for /cmd load <id>:",
        "tag_purge": "clear",
        "purge_need": "Deletes EVERY message from anyone. Confirm: /cmd clear all",
        "purge_work": "Deleting every message…",
        "purge_ok": "Done. Deleted ~{n} (skipped {fail}).",
        "purge_denied": "The bot must be admin with Delete messages permission.",
        "purge_none": "Nothing to delete.",
        "yes": "yes",
        "no": "no",
        "not_admin": "Only a table admin can use /cmd {verb}.",
        "unknown": "unknown: /cmd {verb}",
        "unknown_list": "now: {list}",
        "bad_lang": "Invalid language. Use: es, fr, de, en.",
        "grant_ok": "admin added: {who}",
        "grant_already": "already admin: {who}",
        "grant_bad": "give @user or a numeric id: /cmd grant @ana",
        "revoke_ok": "admin revoked: {who}",
        "revoke_missing": "was not a table admin: {who}",
        "revoke_creator": "The group creator cannot be revoked.",
        "revoke_env": "{who} remains admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "give @user or a numeric id: /cmd revoke 123",
        "webhook_empty": "The GM returned no body.",
        "rule_ok": "Rule added: {line}",
        "limit_ok": "Limit added: {line}",
        "new_game_empty": "Grok got new-game, but the webhook does not send the story. Set WEBHOOK_REPLY=telegram (Agent VM posts) or XAI_API_KEY.",
        "agent_woken": "GM woken. The line arrives from the Agent VM, not from the webhook body.",
        "gm_error": "The GM did not respond ({err}).",
        "dice_bad": "Invalid dice: {expr}",
        "lang_local": "Table language: {lang}",
        "lbl_rules": "rules",
        "lbl_limits": "limits",
        "lbl_cmds": "cmds",
        "lbl_pcs": "pcs",
        "none": "(none)",
        "tag_games": "games",
        "games_hint": "/cmd load blackjack",
        "load_bad": "Unknown game. /cmd list games",
        "load_need": "Name a game: /cmd load blackjack",
    },
}


def _m(locale: str, key: str, **kwargs: Any) -> str:
    pack = _MSG[locale] if locale in _MSG else _MSG["en"]
    return pack[key].format(**kwargs)


def _notice(lang: str, tag: str, *lines: str) -> str:
    return card(_m(lang, tag), [line for line in lines if line])


def _verb_list(state: TableState) -> str:
    game = [str(c.get("verb") or "") for c in state.commands if c.get("verb")]
    system = sorted(SYSTEM_VERBS)
    return ", ".join(game + system)


def local_status(state: TableState) -> str:
    lang = state.lang if state.lang in _MSG else "en"
    none = _m(lang, "none")
    title = state.title or _m(lang, "tag_mesa")
    cmds = ", ".join(c.get("verb", "") for c in state.commands) or none
    players = ", ".join(
        str(p.get("name") or p.get("id")) for p in state.players.values()
    ) or none
    lines = [
        f"{state.phase} · {state.lang}",
        state.brief or none,
        DIV,
        _m(lang, "lbl_rules"),
        *bullets(list(state.rules), none),
        _m(lang, "lbl_limits"),
        *bullets(list(state.limits), none),
        DIV,
        f"{_m(lang, 'lbl_cmds')}  {cmds}",
        f"{_m(lang, 'lbl_pcs')}  {players}",
    ]
    return card(title, lines)


def _empty_gm(
    ctx: BridgeContext,
    state: TableState,
    verb: str,
    payload: str,
    lang: str,
) -> str:
    """Grok Automations often return 202 with no body. Keep the table moving."""
    if verb == "status":
        ctx.store.save(state)
        return local_status(state)
    if verb == "lang":
        ctx.store.save(state)
        return _notice(lang, "tag_lang", _m(lang, "lang_local", lang=state.lang))
    if verb == "rules":
        line = payload.strip()
        if line:
            state.rules.append(line)
        ctx.store.save(state)
        return _notice(lang, "tag_ok", _m(lang, "rule_ok", line=line or _m(lang, "none")))
    if verb == "limit":
        line = payload.strip()
        if line:
            state.limits.append(line)
        ctx.store.save(state)
        return _notice(lang, "tag_ok", _m(lang, "limit_ok", line=line or _m(lang, "none")))
    via_agent = getattr(ctx.gm, "reply_mode", "") in {"telegram", "agent", "none"}
    if via_agent:
        ctx.store.save(state)
        return _notice(lang, "tag_ok", _m(lang, "agent_woken"))
    if verb == "new-game":
        ctx.store.save(state)
        return _notice(lang, "tag_err", _m(lang, "new_game_empty"))
    ctx.store.save(state)
    return _notice(lang, "tag_err", _m(lang, "webhook_empty"))


@dataclass(frozen=True)
class PurgeAll:
    """Admin confirmed a full Telegram history wipe. Handler runs the API."""

    lang: str


@dataclass
class Reply:
    text: str
    photos: list[str] = field(default_factory=list)


@dataclass
class BridgeUser:
    id: int
    name: str
    username: str | None = None


@dataclass
class BridgeContext:
    chat_id: int
    user: BridgeUser
    store: Store
    gm: GameMaster
    env_admin_ids: frozenset[int]
    chat_admin_ids: set[int] = field(default_factory=set)
    creator_id: int | None = None
    mentions: dict[str, int] = field(default_factory=dict)


async def process_command(ctx: BridgeContext, text: str) -> str | Reply | PurgeAll | None:
    """Handle one chat line. None means ignore (do not call the GM, do not reply)."""
    parsed = parse_cmd(text)
    if parsed is None:
        return None

    state = ctx.store.load(ctx.chat_id)
    if ctx.creator_id is not None and state.creator_id is None:
        state.creator_id = ctx.creator_id
    creator_id = state.creator_id if state.creator_id is not None else ctx.creator_id

    state.add_log(parsed.verb, parsed.payload, ctx.user.id, ctx.user.name)

    is_adm = admin_mod.is_admin(
        ctx.user.id,
        env_ids=ctx.env_admin_ids,
        chat_admin_ids=ctx.chat_admin_ids,
        granted=state.admins,
    )
    lang = state.lang if state.lang in _MSG else "en"
    verb = parsed.verb
    payload = parsed.payload

    if verb not in SYSTEM_VERBS:
        if verb not in state.command_verbs():
            ctx.store.save(state)
            return _notice(
                lang,
                "tag_stop",
                _m(lang, "unknown", verb=verb),
                _m(lang, "unknown_list", list=_verb_list(state)),
            )
        state.upsert_player(ctx.user.id, ctx.user.name)

    if verb in ADMIN_VERBS and not is_adm:
        ctx.store.save(state)
        return _notice(lang, "tag_stop", _m(lang, "not_admin", verb=verb))

    if verb == "help":
        ctx.store.save(state)
        return card(
            _m(lang, "tag_help"),
            [
                _m(lang, "help_intro"),
                DIV,
                "/cmd <verb> [text]",
                _m(lang, "help_sys"),
                DIV,
                _m(lang, "help_after"),
                _m(lang, "help_load"),
                *catalog_lines(lang),
            ],
        )

    if verb == "whoami":
        ctx.store.save(state)
        admin_flag = _m(lang, "yes") if is_adm else _m(lang, "no")
        return card(
            _m(lang, "tag_you"),
            [
                ctx.user.name,
                f"id  {ctx.user.id}",
                f"admin  {admin_flag}",
            ],
        )

    if verb == "list":
        ctx.store.save(state)
        hint = payload.strip().lower()
        if hint and hint not in {"games", "game", "juegos", "jeux", "spiele", "local"}:
            return _notice(lang, "tag_games", _m(lang, "games_hint"))
        lines = catalog_lines(lang) + [DIV, _m(lang, "games_hint")]
        return card(_m(lang, "tag_games"), lines)

    if verb == "load":
        name = payload.strip()
        if not name:
            ctx.store.save(state)
            return _notice(lang, "tag_stop", _m(lang, "load_need"))
        game = resolve_game(name)
        if game is None:
            ctx.store.save(state)
            return _notice(lang, "tag_stop", _m(lang, "load_bad"))
        state.reset_table()
        state.brief = f"load {game.id}"
        state.phase = "playing"
        turn = game.start(lang, game.id)
        state.title = turn.title or game.id
        state.commands = turn.commands or []
        state.rules = turn.rules or []
        state.blob = {"_local": game.id, "g": turn.state}
        ctx.store.save(state)
        return turn.say

    if verb == "grant":
        target = admin_mod.resolve_user_id(payload, ctx.mentions)
        if target is None:
            ctx.store.save(state)
            return _notice(lang, "tag_stop", _m(lang, "grant_bad"))
        result = admin_mod.grant(state, target)
        ctx.store.save(state)
        who = payload.strip() or str(target)
        key = "grant_already" if result == admin_mod.ALREADY else "grant_ok"
        return _notice(lang, "tag_ok", _m(lang, key, who=who))

    if verb == "revoke":
        target = admin_mod.resolve_user_id(payload, ctx.mentions)
        if target is None:
            ctx.store.save(state)
            return _notice(lang, "tag_stop", _m(lang, "revoke_bad"))
        result = admin_mod.revoke(
            state,
            target,
            creator_id=creator_id,
            env_ids=ctx.env_admin_ids,
        )
        ctx.store.save(state)
        who = payload.strip() or str(target)
        keys = {
            admin_mod.OK: "revoke_ok",
            admin_mod.MISSING: "revoke_missing",
            admin_mod.CREATOR: "revoke_creator",
            admin_mod.ENV: "revoke_env",
        }
        tag = "tag_ok" if result == admin_mod.OK else "tag_stop"
        return _notice(lang, tag, _m(lang, keys[result], who=who))

    if verb in PURGE_VERBS:
        ctx.store.save(state)
        if payload.lower() not in PURGE_CONFIRM:
            return _notice(lang, "tag_purge", _m(lang, "purge_need"))
        return PurgeAll(lang=lang)

    if verb == "lang":
        new_lang = payload.strip().lower()
        if new_lang not in SUPPORTED_LANGS:
            ctx.store.save(state)
            return _notice(lang, "tag_stop", _m(lang, "bad_lang"))
        state.lang = new_lang
        lang = new_lang

    if verb == "new-game":
        state.reset_table()
        state.brief = payload
        state.phase = "lobby"

    if verb == "reset":
        hard = payload.strip().lower() == "hard"
        if hard:
            ctx.store.delete(ctx.chat_id)
            state = TableState(chat_id=ctx.chat_id)
            if ctx.creator_id is not None:
                state.creator_id = ctx.creator_id
            state.add_log(verb, payload, ctx.user.id, ctx.user.name)
        else:
            state.reset_table()
            state.phase = "lobby"

    ctx.store.save(state)

    local_id = (state.blob or {}).get("_local")
    if local_id and verb not in SYSTEM_VERBS:
        game = get_game(str(local_id))
        if game is not None:
            turn = game.handle(
                verb,
                payload,
                {
                    "user": {
                        "id": ctx.user.id,
                        "name": ctx.user.name,
                        "username": ctx.user.username,
                    }
                },
                dict((state.blob or {}).get("g") or {}),
                lang,
            )
            state.blob = {"_local": local_id, "g": turn.state}
            if turn.commands is not None:
                state.commands = turn.commands
            if turn.title:
                state.title = turn.title
            ctx.store.save(state)
            if turn.photos:
                return Reply(text=turn.say, photos=list(turn.photos))
            return turn.say

    gm_reply = await _call_gm(ctx, state, verb, payload, is_adm, dice=None)
    if gm_reply is None:
        return _empty_gm(ctx, state, verb, payload, lang)

    apply_reply(state, gm_reply)
    ctx.store.save(state)

    dice_req = gm_reply.get("dice_request") if isinstance(gm_reply, dict) else None
    first_say = str(gm_reply.get("say") or "").strip() if isinstance(gm_reply, dict) else ""

    if isinstance(dice_req, dict) and dice_req.get("expr"):
        expr = str(dice_req.get("expr"))
        try:
            dice = roll_dice(expr)
        except ValueError:
            return _join_say(first_say, _notice(lang, "tag_err", _m(lang, "dice_bad", expr=expr)))
        second = await _call_gm(
            ctx, state, "dice-result", dice_req.get("reason") or "", is_adm, dice=dice
        )
        if second:
            apply_reply(state, second)
            ctx.store.save(state)
            second_say = str(second.get("say") or "").strip()
            return _join_say(first_say, second_say)
        loc = state.lang if state.lang in _MSG else "en"
        return _join_say(first_say, _notice(loc, "tag_err", _m(loc, "webhook_empty")))

    if verb == "status" and not first_say:
        return local_status(state)
    return first_say or None


async def _call_gm(
    ctx: BridgeContext,
    state: TableState,
    verb: str,
    payload: str,
    is_adm: bool,
    dice: dict[str, Any] | None,
) -> dict[str, Any] | None:
    request = build_request(
        state,
        user_id=ctx.user.id,
        user_name=ctx.user.name,
        username=ctx.user.username,
        is_admin=is_adm,
        verb=verb,
        payload=payload,
        dice=dice,
    )
    try:
        return await ctx.gm.reply(request)
    except Exception as exc:
        log.exception("GM error for verb=%s chat=%s", verb, state.chat_id)
        lang = state.lang if state.lang in _MSG else "en"
        raise GmError(_notice(lang, "tag_err", _m(lang, "gm_error", err=type(exc).__name__))) from exc


class GmError(RuntimeError):
    pass


def _join_say(*parts: str) -> str | None:
    text = "\n".join(p for p in parts if p)
    return text or None


def extract_mentions(message: Any) -> dict[str, int]:
    """username.lower() -> user id, from text_mention entities only."""
    out: dict[str, int] = {}
    entities = getattr(message, "entities", None) or []
    for ent in entities:
        user = getattr(ent, "user", None)
        if user is None:
            continue
        out[str(user.id)] = user.id
        if user.username:
            out[user.username.lower()] = user.id
    return out


async def _chat_admins(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> tuple[set[int], int | None]:
    chat = update.effective_chat
    user = update.effective_user
    ids: set[int] = set()
    creator_id: int | None = None
    if chat is None:
        return ids, creator_id
    if chat.type == ChatType.PRIVATE and user is not None:
        return {user.id}, user.id
    try:
        admins = await context.bot.get_chat_administrators(chat.id)
    except Exception:
        log.debug("get_chat_administrators failed for %s", chat.id, exc_info=True)
        return ids, creator_id
    for member in admins:
        ids.add(member.user.id)
        if member.status == "creator":
            creator_id = member.user.id
    return ids, creator_id


def _remember(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int) -> None:
    buckets: dict[int, deque[int]] = context.bot_data.setdefault(
        "seen_ids", defaultdict(lambda: deque(maxlen=500))
    )
    if chat_id not in buckets:
        buckets[chat_id] = deque(maxlen=500)
    buckets[chat_id].append(int(message_id))


def _seen_ids(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> list[int]:
    buckets = context.bot_data.get("seen_ids") or {}
    return list(buckets.get(chat_id) or [])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if message is None or user is None or chat is None:
        return
    _remember(context, chat.id, message.message_id)
    text = message.text or message.caption
    if not text:
        return
    if parse_cmd(text) is None:
        return

    store: Store = context.bot_data["store"]
    gm: GameMaster = context.bot_data["gm"]
    config: Config = context.bot_data["config"]
    chat_admin_ids, creator_id = await _chat_admins(update, context)

    ctx = BridgeContext(
        chat_id=chat.id,
        user=BridgeUser(
            id=user.id,
            name=user.full_name or user.first_name or str(user.id),
            username=user.username,
        ),
        store=store,
        gm=gm,
        env_admin_ids=config.admin_telegram_ids,
        chat_admin_ids=chat_admin_ids,
        creator_id=creator_id,
        mentions=extract_mentions(message),
    )
    try:
        result = await process_command(ctx, text)
    except GmError as exc:
        result = str(exc)
    if isinstance(result, PurgeAll):
        await _execute_purge(message, context, result.lang)
        return
    if isinstance(result, Reply):
        await _publish_photos(message, result)
        return
    if not result:
        return
    await _publish(message, result)


async def _execute_purge(message: Any, context: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    chat_id = message.chat_id
    if not await bot_can_delete(context.bot, chat_id):
        await _publish(
            message,
            _notice(lang, "tag_stop", _m(lang, "purge_denied")),
            reply=False,
        )
        return
    work = _notice(lang, "tag_purge", _m(lang, "purge_work"))
    progress = None
    try:
        progress = await context.bot.send_message(
            chat_id=chat_id,
            text=as_html_pre(work),
            parse_mode=ParseMode.HTML,
        )
        _remember(context, chat_id, progress.message_id)
    except Exception:
        log.debug("could not post purge progress", exc_info=True)
    extra = _seen_ids(context, chat_id)
    stats = await purge_upto(
        context.bot,
        chat_id,
        int(message.message_id),
        extra_ids=extra,
    )
    if progress is not None:
        try:
            await progress.delete()
        except Exception:
            pass
    if stats.denied:
        say = _notice(lang, "tag_stop", _m(lang, "purge_denied"))
    elif stats.deleted <= 0:
        say = _notice(lang, "tag_purge", _m(lang, "purge_none"))
    else:
        say = _notice(
            lang,
            "tag_purge",
            _m(lang, "purge_ok", n=stats.deleted, fail=stats.failed),
        )
    await _publish(message, say, reply=False)


async def _publish_photos(message: Any, result: Reply) -> None:
    bot = message.get_bot()
    chat_id = message.chat_id
    caption = (result.text or "")[:1024]
    sent_caption = False
    for path in result.photos:
        try:
            with open(path, "rb") as fh:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=fh,
                    caption=caption if not sent_caption else None,
                )
            sent_caption = True
        except Exception:
            log.exception("send_photo failed %s", path)
    if not sent_caption and result.text:
        await _publish(message, result.text, reply=False)


async def _publish(message: Any, say: str, *, reply: bool = True) -> None:
    bot = message.get_bot()
    chat_id = message.chat_id
    for chunk in _chunk(say, TG_LIMIT - 24):
        html = as_html_pre(chunk)
        sent = None
        if reply:
            try:
                sent = await message.reply_text(html, parse_mode=ParseMode.HTML)
            except Exception as exc:
                if "not found" not in str(exc).lower():
                    raise
                log.debug("reply target gone, sending standalone: %s", exc)
        if sent is None:
            await bot.send_message(
                chat_id=chat_id, text=html, parse_mode=ParseMode.HTML
            )


def _chunk(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    rest = text
    while rest:
        if len(rest) <= limit:
            parts.append(rest)
            break
        cut = rest.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(rest[:cut])
        rest = rest[cut:].lstrip("\n")
    return parts


def build_application(config: Config, store: Store, gm: GameMaster) -> Application:
    application = Application.builder().token(config.telegram_bot_token).build()
    application.bot_data["config"] = config
    application.bot_data["store"] = store
    application.bot_data["gm"] = gm
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    return application
