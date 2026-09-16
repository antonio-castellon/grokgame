from __future__ import annotations

import re
from dataclasses import dataclass

# /cmd, /cmd@BotName, or bare "cmd" (group alias when privacy is off).
_CMD_RE = re.compile(
    r"""
    ^\s*
    (?:
        /cmd(?:@[A-Za-z0-9_]+)?
        |
        cmd
    )
    \s+
    ([a-z0-9-]{1,32})
    (?:\s+(.*))?
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE | re.DOTALL,
)

SYSTEM_VERBS = frozenset(
    {
        "help",
        "lang",
        "new-game",
        "rules",
        "limit",
        "cmd",
        "status",
        "reset",
        "whoami",
        "grant",
        "revoke",
        "purge",
        "clear",
    }
)

ADMIN_VERBS = frozenset(
    {
        "lang",
        "new-game",
        "rules",
        "limit",
        "reset",
        "grant",
        "revoke",
        "purge",
        "clear",
    }
)

PURGE_VERBS = frozenset({"purge", "clear"})
PURGE_CONFIRM = frozenset({"all", "todo", "todos", "tous", "alle", "everything"})

SUPPORTED_LANGS = ("es", "fr", "de", "en")


@dataclass(frozen=True)
class ParsedCmd:
    verb: str
    payload: str


def parse_cmd(text: str | None) -> ParsedCmd | None:
    """Return verb+payload if `text` is a /cmd (or cmd) line, else None.

    Plain chat ("buenos días") is not a command and must not reach the GM.
    """
    if not text:
        return None
    match = _CMD_RE.match(text)
    if not match:
        return None
    verb = match.group(1).lower()
    payload = (match.group(2) or "").strip()
    return ParsedCmd(verb=verb, payload=payload)
