"""Hard table safety: secrets stay off Telegram; no adult content.

Forks: keep this module wired. Do not weaken it for "just this group".
"""

from __future__ import annotations

import os
import re
from typing import Literal

Kind = Literal["secrets", "adult", "ok"]

# Asking the table about *real* infrastructure / credentials / private ids.
# In-fiction quiz passwords ("dungeon password is moonflower") must stay allowed.
_SECRETS_ASK = re.compile(
    r"""(?ix)
    (
      \b(api[_\s-]?key|access[_\s-]?token|bot\s*token|telegram[_\s-]?token|
         webhook\s*key|webhook\s*url|whsec_|crsr_|
         dotenv|admin_telegram|allowed_chat_ids|
         private[_\s-]?key|ssh[_\s-]?key)\b
      |
      (?<!\w)\.env(?!\w)
      |
      \b(password|passwd|passwort|contrase[nñ]a|mot\s*de\s*passe|secret|credential|token|clave)\b
        .{0,48}\b(bot|telegram|admin|account|webhook|server|vm|bridge|token|api|env)\b
      |
      \b(bot|telegram|admin|account|webhook|server|vm|bridge|api|env)\b
        .{0,48}\b(password|passwd|contrase[nñ]a|secret|credential|token|clave)\b
      |
      \b(dame|show|give|leak|exfiltrat|cat|print|dump)\b.{0,40}(\.env\b|dotenv|token|password|secret|clave|webhook)
      |
      \b(admin[_\s-]?id|telegram[_\s-]?id\s+de\s+admin)\b
    )
    """,
)

_ADULT_ASK = re.compile(
    r"""(?ix)
    \b(
      porn|porno|xxx|nsfw|onlyfans|
      nude|nudes|nudity|desnudo|desnuda|nackt|
      erotic|er[oó]tic[oa]|sex\s*story|historia\s*er[oó]tica|
      hardcore|hentai|rule34|
      blowjob|handjob|cumshot|anal\s*sex|orgasm|
      foll[ae]r|coger\b|polvo\b|putas?\b|
      child\s*porn|csam|underage\s*sex|menor(es)?\s*(desnud|sex)
    )\b
    """,
)

_TOKENISH = re.compile(
    r"""(?x)
    \b(gh[pousr]_[A-Za-z0-9_]{20,}|
       xox[baprs]-[A-Za-z0-9-]{10,}|
       whsec_[A-Za-z0-9+/=_-]{16,}|
       crsr_[A-Za-z0-9_]{16,}|
       sk-[A-Za-z0-9]{20,})\b
    """
)

_ENV_NAMES = (
    "TELEGRAM_BOT_TOKEN",
    "WEBHOOK_URL",
    "WEBHOOK_SECRET",
    "ADMIN_TELEGRAM_IDS",
    "XAI_API_KEY",
)


def classify_player_text(text: str) -> Kind:
    """What kind of player ask is this?"""
    raw = text or ""
    if _ADULT_ASK.search(raw):
        return "adult"
    if _SECRETS_ASK.search(raw):
        return "secrets"
    return "ok"


def refusal(kind: Kind, lang: str = "en") -> str:
    lang = (lang or "en").lower()[:2]
    if kind == "adult":
        msg = {
            "es": "En esta mesa no hay contenido sexual ni historias XXX. Solo juego de mesa / rol apto.",
            "en": "No sexual content or XXX stories at this table. Tabletop / RPG only.",
            "fr": "Pas de contenu sexuel ni d'histoires XXX à cette table. Jeu de rôle / plateau seulement.",
            "de": "Kein sexueller Inhalt und keine XXX-Geschichten an diesem Tisch. Nur Brett-/Rollenspiel.",
        }
        return msg.get(lang, msg["en"])
    if kind == "secrets":
        msg = {
            "es": "Soy solo el máster de la mesa. No hablo de contraseñas, tokens, ids internos ni de la conexión del sistema.",
            "en": "I'm only the table GM. I don't discuss passwords, tokens, internal ids, or system connection details.",
            "fr": "Je suis seulement le MJ. Pas de mots de passe, tokens, ids internes ni détails de connexion système.",
            "de": "Ich bin nur der Spielleiter. Keine Passwörter, Tokens, interne IDs oder System-Verbindungsdaten.",
        }
        return msg.get(lang, msg["en"])
    return ""


def _secret_values() -> list[str]:
    out: list[str] = []
    for name in _ENV_NAMES:
        val = (os.getenv(name) or "").strip()
        if len(val) >= 8:
            out.append(val)
    return out


def scrub_outbound(text: str) -> str:
    """Redact env secrets and token-shaped strings before Telegram send."""
    if not text:
        return text
    scrubbed = text
    for val in _secret_values():
        if val and val in scrubbed:
            scrubbed = scrubbed.replace(val, "[REDACTED]")
    scrubbed = _TOKENISH.sub("[REDACTED]", scrubbed)
    scrubbed = re.sub(
        r"https?://(?:grok\.com|api2\.cursor\.sh)/[^\s]+webhook[^\s]*",
        "[REDACTED-URL]",
        scrubbed,
        flags=re.I,
    )
    return scrubbed


def block_reason_for_payload(verb: str, payload: str) -> Kind | None:
    """Return secrets/adult if this command must not reach the GM."""
    blob = f"{verb} {payload or ''}".strip()
    kind = classify_player_text(blob)
    return None if kind == "ok" else kind
