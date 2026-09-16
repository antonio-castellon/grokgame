from __future__ import annotations

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import card

KEYWORDS = (
    "piedra papel",
    "piedra-papel",
    "rock paper",
    "chifoumi",
    "schnick",
    "tijera",
    "scissors",
)

BEATS = {"piedra": "tijera", "papel": "piedra", "tijera": "papel"}
ALIASES = {
    "rock": "piedra",
    "stone": "piedra",
    "paper": "papel",
    "scissors": "tijera",
    "pierre": "piedra",
    "feuille": "papel",
    "ciseaux": "tijera",
    "stein": "piedra",
    "papier": "papel",
    "schere": "tijera",
}


class Rps:
    id = "rps"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=card(
                "rps",
                [
                    pick(
                        lang,
                        {
                            "es": "/cmd join luego /cmd piedra | papel | tijera",
                            "en": "/cmd join then /cmd piedra | papel | tijera",
                            "fr": "/cmd join puis /cmd pierre | feuille | ciseaux",
                            "de": "/cmd join dann /cmd stein | papier | schere",
                        },
                    )
                ],
            ),
            state={"hands": {}},
            commands=cmds(
                [
                    ("join", "join"),
                    ("piedra", "rock"),
                    ("papel", "paper"),
                    ("tijera", "scissors"),
                ]
            ),
            title="RPS",
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        pid = uid(request)
        name = uname(request)
        hands: dict = state.setdefault("hands", {})
        if verb == "join":
            hands.setdefault(pid, {"name": name, "move": None})
            return Turn(say=card("join", [name]), state=state)
        move = ALIASES.get(verb, verb)
        if move not in BEATS:
            return Turn(say=card("rps", ["piedra / papel / tijera"]), state=state)
        hands.setdefault(pid, {"name": name, "move": None})
        hands[pid]["move"] = move
        ready = [p for p in hands.values() if p.get("move")]
        if len(ready) < 2:
            return Turn(say=card(move, [name, pick(lang, {"es": "Esperando rival.", "en": "Waiting.", "fr": "On attend.", "de": "Warten."})]), state=state)
        a, b = ready[0], ready[1]
        ma, mb = a["move"], b["move"]
        if ma == mb:
            msg = pick(lang, {"es": "Empate.", "en": "Tie.", "fr": "Égalité.", "de": "Unentschieden."})
        elif BEATS[ma] == mb:
            msg = f"GANADOR ES: {a['name']}"
        else:
            msg = f"GANADOR ES: {b['name']}"
        for p in hands.values():
            p["move"] = None
        return Turn(say=card("rps", [f"{a['name']} {ma}", f"{b['name']} {mb}", msg]), state=state)
