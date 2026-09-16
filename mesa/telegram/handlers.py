from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from mesa import admin as admin_mod
from mesa.config import Config
from mesa.dice import roll as roll_dice
from mesa.gm.base import GameMaster, apply_reply, build_request
from mesa.parse import ADMIN_VERBS, SUPPORTED_LANGS, SYSTEM_VERBS, parse_cmd
from mesa.store import Store, TableState

log = logging.getLogger(__name__)

TG_LIMIT = 4000

_MSG = {
    "es": {
        "help": (
            "Mesa de gramática abierta. Un admin describe el juego; Grok inventa "
            "reglas y comandos.\n"
            "Gramática: /cmd <verbo> [texto…]\n"
            "Sistema: help, lang, new-game, rules, limit, cmd list, status, "
            "reset, whoami, grant, revoke.\n"
            "Tras /cmd new-game, /cmd cmd list muestra las acciones de ESA mesa."
        ),
        "whoami": "{name}\nid: {id}\nadmin: {admin}",
        "yes": "sí",
        "no": "no",
        "not_admin": "Solo un admin de la mesa puede usar /cmd {verb}.",
        "unknown": "Comando desconocido: /cmd {verb}\nComandos actuales: {list}",
        "bad_lang": "Idioma no válido. Usa: es, fr, de, en.",
        "grant_ok": "Admin de mesa añadido: {who}",
        "grant_already": "Ya era admin de mesa: {who}",
        "grant_bad": "Indica @usuario o un id numérico: /cmd grant @ana",
        "revoke_ok": "Admin de mesa revocado: {who}",
        "revoke_missing": "No era admin de mesa: {who}",
        "revoke_creator": "No se puede revocar al creador del grupo.",
        "revoke_env": "{who} sigue siendo admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "Indica @usuario o un id numérico: /cmd revoke 123",
        "webhook_empty": "El GM no devolvió cuerpo. Mesa actualizada en local si aplica.",
        "gm_error": "El GM no respondió ({err}).",
        "dice_bad": "El GM pidió un dado inválido: {expr}",
        "lang_local": "Idioma de la mesa: {lang}",
        "yes_admin": "sí",
        "no_admin": "no",
        "status": (
            "Mesa: {title}\n"
            "Fase: {phase} · lang: {lang}\n"
            "Brief: {brief}\n"
            "Reglas:\n{rules}\n"
            "Límites:\n{limits}\n"
            "Comandos: {commands}\n"
            "Jugadores: {players}"
        ),
        "none": "(ninguno)",
        "cmd_need_list": "Usa /cmd cmd list",
    },
    "fr": {
        "help": (
            "Table à grammaire ouverte. Un admin décrit le jeu ; Grok invente "
            "règles et commandes.\n"
            "Grammaire : /cmd <verbe> [texte…]\n"
            "Système : help, lang, new-game, rules, limit, cmd list, status, "
            "reset, whoami, grant, revoke.\n"
            "Après /cmd new-game, /cmd cmd list montre les actions de CETTE table."
        ),
        "whoami": "{name}\nid : {id}\nadmin : {admin}",
        "yes": "oui",
        "no": "non",
        "not_admin": "Seul un admin de la table peut utiliser /cmd {verb}.",
        "unknown": "Commande inconnue : /cmd {verb}\nCommandes actuelles : {list}",
        "bad_lang": "Langue invalide. Utilise : es, fr, de, en.",
        "grant_ok": "Admin de table ajouté : {who}",
        "grant_already": "Était déjà admin de table : {who}",
        "grant_bad": "Indique @user ou un id numérique : /cmd grant @ana",
        "revoke_ok": "Admin de table révoqué : {who}",
        "revoke_missing": "N'était pas admin de table : {who}",
        "revoke_creator": "On ne peut pas révoquer le créateur du groupe.",
        "revoke_env": "{who} reste admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "Indique @user ou un id numérique : /cmd revoke 123",
        "webhook_empty": "Le GM n'a renvoyé aucun corps.",
        "gm_error": "Le GM n'a pas répondu ({err}).",
        "dice_bad": "Le GM a demandé un dé invalide : {expr}",
        "lang_local": "Langue de la table : {lang}",
        "status": (
            "Table : {title}\n"
            "Phase : {phase} · lang : {lang}\n"
            "Brief : {brief}\n"
            "Règles :\n{rules}\n"
            "Limites :\n{limits}\n"
            "Commandes : {commands}\n"
            "Joueurs : {players}"
        ),
        "none": "(aucun)",
        "cmd_need_list": "Utilise /cmd cmd list",
    },
    "de": {
        "help": (
            "Offene Grammatik-Tisch. Ein Admin beschreibt das Spiel; Grok erfindet "
            "Regeln und Befehle.\n"
            "Grammatik: /cmd <verb> [text…]\n"
            "System: help, lang, new-game, rules, limit, cmd list, status, "
            "reset, whoami, grant, revoke.\n"
            "Nach /cmd new-game zeigt /cmd cmd list die Aktionen DIESES Tisches."
        ),
        "whoami": "{name}\nid: {id}\nadmin: {admin}",
        "yes": "ja",
        "no": "nein",
        "not_admin": "Nur ein Tisch-Admin darf /cmd {verb} nutzen.",
        "unknown": "Unbekannter Befehl: /cmd {verb}\nAktuelle Befehle: {list}",
        "bad_lang": "Ungültige Sprache. Nutze: es, fr, de, en.",
        "grant_ok": "Tisch-Admin hinzugefügt: {who}",
        "grant_already": "War bereits Tisch-Admin: {who}",
        "grant_bad": "Gib @user oder eine numerische id an: /cmd grant @ana",
        "revoke_ok": "Tisch-Admin entzogen: {who}",
        "revoke_missing": "War kein Tisch-Admin: {who}",
        "revoke_creator": "Der Gruppenersteller kann nicht entzogen werden.",
        "revoke_env": "{who} bleibt Admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "Gib @user oder eine numerische id an: /cmd revoke 123",
        "webhook_empty": "Der GM hat keinen Body zurückgegeben.",
        "gm_error": "Der GM hat nicht geantwortet ({err}).",
        "dice_bad": "Der GM bat um einen ungültigen Würfel: {expr}",
        "lang_local": "Sprache des Tisches: {lang}",
        "status": (
            "Tisch: {title}\n"
            "Phase: {phase} · lang: {lang}\n"
            "Brief: {brief}\n"
            "Regeln:\n{rules}\n"
            "Limits:\n{limits}\n"
            "Befehle: {commands}\n"
            "Spieler: {players}"
        ),
        "none": "(keine)",
        "cmd_need_list": "Nutze /cmd cmd list",
    },
    "en": {
        "help": (
            "Open-grammar table. An admin describes the game; Grok invents "
            "rules and commands.\n"
            "Grammar: /cmd <verb> [text…]\n"
            "System: help, lang, new-game, rules, limit, cmd list, status, "
            "reset, whoami, grant, revoke.\n"
            "After /cmd new-game, /cmd cmd list shows THIS table's actions."
        ),
        "whoami": "{name}\nid: {id}\nadmin: {admin}",
        "yes": "yes",
        "no": "no",
        "not_admin": "Only a table admin can use /cmd {verb}.",
        "unknown": "Unknown command: /cmd {verb}\nCurrent commands: {list}",
        "bad_lang": "Invalid language. Use: es, fr, de, en.",
        "grant_ok": "Table admin added: {who}",
        "grant_already": "Already a table admin: {who}",
        "grant_bad": "Give @user or a numeric id: /cmd grant @ana",
        "revoke_ok": "Table admin revoked: {who}",
        "revoke_missing": "Was not a table admin: {who}",
        "revoke_creator": "The group creator cannot be revoked.",
        "revoke_env": "{who} remains admin (ADMIN_TELEGRAM_IDS).",
        "revoke_bad": "Give @user or a numeric id: /cmd revoke 123",
        "webhook_empty": "The GM returned no body. Local table updated if applicable.",
        "gm_error": "The GM did not respond ({err}).",
        "dice_bad": "The GM asked for an invalid dice expr: {expr}",
        "lang_local": "Table language: {lang}",
        "status": (
            "Table: {title}\n"
            "Phase: {phase} · lang: {lang}\n"
            "Brief: {brief}\n"
            "Rules:\n{rules}\n"
            "Limits:\n{limits}\n"
            "Commands: {commands}\n"
            "Players: {players}"
        ),
        "none": "(none)",
        "cmd_need_list": "Use /cmd cmd list",
    },
}


def _m(lang: str, key: str, **kwargs: Any) -> str:
    pack = _MSG[lang] if lang in _MSG else _MSG["en"]
    return pack[key].format(**kwargs)


def _verb_list(state: TableState) -> str:
    game = [str(c.get("verb") or "") for c in state.commands if c.get("verb")]
    system = sorted(SYSTEM_VERBS)
    return ", ".join(game + system)


def local_status(state: TableState) -> str:
    lang = state.lang if state.lang in _MSG else "en"
    none = _m(lang, "none")
    rules = "\n".join(f"- {r}" for r in state.rules) if state.rules else none
    limits = "\n".join(f"- {x}" for x in state.limits) if state.limits else none
    commands = ", ".join(c.get("verb", "") for c in state.commands) or none
    players = ", ".join(
        str(p.get("name") or p.get("id")) for p in state.players.values()
    ) or none
    return _m(
        lang,
        "status",
        title=state.title or none,
        phase=state.phase,
        lang=state.lang,
        brief=state.brief or none,
        rules=rules,
        limits=limits,
        commands=commands,
        players=players,
    )


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


async def process_command(ctx: BridgeContext, text: str) -> str | None:
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
            return _m(lang, "unknown", verb=verb, list=_verb_list(state))
        state.upsert_player(ctx.user.id, ctx.user.name)

    if verb in ADMIN_VERBS and not is_adm:
        ctx.store.save(state)
        return _m(lang, "not_admin", verb=verb)

    if verb == "help":
        ctx.store.save(state)
        return _m(lang, "help")

    if verb == "whoami":
        ctx.store.save(state)
        return _m(
            lang,
            "whoami",
            name=ctx.user.name,
            id=ctx.user.id,
            admin=_m(lang, "yes") if is_adm else _m(lang, "no"),
        )

    if verb == "grant":
        target = admin_mod.resolve_user_id(payload, ctx.mentions)
        if target is None:
            ctx.store.save(state)
            return _m(lang, "grant_bad")
        result = admin_mod.grant(state, target)
        ctx.store.save(state)
        who = payload.strip() or str(target)
        key = "grant_already" if result == admin_mod.ALREADY else "grant_ok"
        return _m(lang, key, who=who)

    if verb == "revoke":
        target = admin_mod.resolve_user_id(payload, ctx.mentions)
        if target is None:
            ctx.store.save(state)
            return _m(lang, "revoke_bad")
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
        return _m(lang, keys[result], who=who)

    if verb == "lang":
        new_lang = payload.strip().lower()
        if new_lang not in SUPPORTED_LANGS:
            ctx.store.save(state)
            return _m(lang, "bad_lang")
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

    gm_reply = await _call_gm(ctx, state, verb, payload, is_adm, dice=None)
    if gm_reply is None:
        ctx.store.save(state)
        if verb == "status":
            return local_status(state)
        if verb == "lang":
            return _m(lang, "lang_local", lang=state.lang)
        return _m(lang, "webhook_empty")

    apply_reply(state, gm_reply)
    ctx.store.save(state)

    dice_req = gm_reply.get("dice_request") if isinstance(gm_reply, dict) else None
    first_say = str(gm_reply.get("say") or "").strip() if isinstance(gm_reply, dict) else ""

    if isinstance(dice_req, dict) and dice_req.get("expr"):
        expr = str(dice_req.get("expr"))
        try:
            dice = roll_dice(expr)
        except ValueError:
            return _join_say(first_say, _m(lang, "dice_bad", expr=expr))
        second = await _call_gm(
            ctx, state, "dice-result", dice_req.get("reason") or "", is_adm, dice=dice
        )
        if second:
            apply_reply(state, second)
            ctx.store.save(state)
            second_say = str(second.get("say") or "").strip()
            return _join_say(first_say, second_say)
        return _join_say(first_say, _m(state.lang if state.lang in _MSG else "en", "webhook_empty"))

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
        raise GmError(_m(lang, "gm_error", err=type(exc).__name__)) from exc


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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if message is None or user is None or chat is None:
        return
    text = message.text
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
        say = await process_command(ctx, text)
    except GmError as exc:
        say = str(exc)
    if not say:
        return
    await _publish(message, say)


async def _publish(message: Any, say: str) -> None:
    chunks = _chunk(say, TG_LIMIT)
    for chunk in chunks:
        await message.reply_text(chunk)


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
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    return application
