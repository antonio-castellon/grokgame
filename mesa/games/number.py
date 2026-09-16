from __future__ import annotations

import random

from mesa.games.common import Turn, cmds, pick, uname
from mesa.skin import card

KEYWORDS = (
    "adivina",
    "número secreto",
    "numero secreto",
    "guess the number",
    "number guess",
)


class NumberGuess:
    id = "number"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        secret = random.randint(1, 100)
        return Turn(
            say=card(
                "123",
                [
                    pick(
                        lang,
                        {
                            "es": "Número 1–100. /cmd guess 42",
                            "en": "Number 1–100. /cmd guess 42",
                            "fr": "Nombre 1–100. /cmd guess 42",
                            "de": "Zahl 1–100. /cmd guess 42",
                        },
                    )
                ],
            ),
            state={"secret": secret, "tries": 0},
            commands=cmds(
                [
                    ("join", "join"),
                    ("guess", pick(lang, {"es": "probar un número", "en": "try a number", "fr": "essayer un nombre", "de": "eine Zahl versuchen"})),
                ]
            ),
            title=pick(lang, {"es": "Adivina", "en": "Guess", "fr": "Devine", "de": "Rate"}),
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        if verb == "join":
            return Turn(say=card("join", [uname(request)]), state=state)
        try:
            n = int((payload or "").strip())
        except ValueError:
            return Turn(say=card("guess", ["1–100"]), state=state)
        secret = int(state.get("secret") or 0)
        state["tries"] = int(state.get("tries") or 0) + 1
        if n == secret:
            msg = f"GANADOR ES: {uname(request)}  ({state['tries']})"
            state["secret"] = random.randint(1, 100)
            state["tries"] = 0
            return Turn(say=card("guess", [msg]), state=state)
        hint = pick(lang, {"es": "más alto", "en": "higher", "fr": "plus haut", "de": "höher"}) if n < secret else pick(lang, {"es": "más bajo", "en": "lower", "fr": "plus bas", "de": "niedriger"})
        return Turn(say=card("guess", [str(n), hint]), state=state)
