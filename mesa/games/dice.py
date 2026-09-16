from __future__ import annotations

import random

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import card

KEYWORDS = ("duelo de dados", "dice duel", "juego de dados", "dice game")


class DiceDuel:
    id = "dice"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=card(
                "dice",
                [
                    pick(
                        lang,
                        {
                            "es": "Duelo 2d6. /cmd join y /cmd roll.",
                            "en": "2d6 duel. /cmd join and /cmd roll.",
                            "fr": "Duel 2d6. /cmd join et /cmd roll.",
                            "de": "2d6-Duell. /cmd join und /cmd roll.",
                        },
                    )
                ],
            ),
            state={"rolls": {}},
            commands=cmds(
                [
                    ("join", "join"),
                    ("roll", pick(lang, {"es": "tirar 2d6", "en": "roll 2d6", "fr": "lancer 2d6", "de": "2d6 würfeln"})),
                ]
            ),
            title=pick(lang, {"es": "Dados", "en": "Dice", "fr": "Dés", "de": "Würfel"}),
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        pid = uid(request)
        name = uname(request)
        rolls: dict = state.setdefault("rolls", {})
        if verb == "join":
            rolls.setdefault(pid, {"name": name, "total": None})
            return Turn(say=card("join", [name]), state=state)
        if verb == "roll":
            a, b = random.randint(1, 6), random.randint(1, 6)
            rolls[pid] = {"name": name, "total": a + b}
            lines = [f"{name}  {a}+{b}={a+b}"]
            done = [p for p in rolls.values() if p.get("total") is not None]
            if len(done) >= 2 and len(done) == len(rolls):
                best = max(int(p["total"]) for p in done)
                winners = [p["name"] for p in done if int(p["total"]) == best]
                lines.append("GANADOR ES: " + ", ".join(winners))
            return Turn(say=card("roll", lines), state=state)
        return Turn(say=card("dice", [name]), state=state)
