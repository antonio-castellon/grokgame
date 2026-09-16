from __future__ import annotations

import random
from typing import Any

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import DIV, card

SUITS = ("oros", "copas", "espadas", "bastos")
RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
RANK_NAME = {1: "AS", 10: "SOTA", 11: "CABAL", 12: "REY"}

KEYWORDS = (
    "21",
    "blackjack",
    "veintiuno",
    "veinte y uno",
    "cartas del 21",
)

_HELP = {
    "es": [
        ("join", "sentarse a la mesa"),
        ("otra", "pedir una carta"),
        ("planto", "plantarse"),
        ("manos", "ver las manos"),
    ],
    "en": [
        ("join", "sit down"),
        ("otra", "hit: take a card"),
        ("planto", "stand"),
        ("manos", "show hands"),
    ],
    "fr": [
        ("join", "s'asseoir"),
        ("otra", "tirer une carte"),
        ("planto", "rester"),
        ("manos", "voir les mains"),
    ],
    "de": [
        ("join", "Platz nehmen"),
        ("otra", "eine Karte ziehen"),
        ("planto", "halten"),
        ("manos", "Hände zeigen"),
    ],
}

_RULES = {
    "es": [
        "Baraja española de 48 (1–7, 10, 11, 12).",
        "AS=1 u 11; 10/SOTA/CABAL/REY=10.",
        "/cmd otra pide carta; /cmd planto se planta.",
        "Gana quien más cerca de 21 sin pasarse.",
    ],
    "en": [
        "Spanish 48-card deck (1–7, 10, 11, 12).",
        "Ace=1 or 11; face cards=10.",
        "/cmd otra hits; /cmd planto stands.",
        "Closest to 21 without busting wins.",
    ],
    "fr": [
        "Jeu espagnol de 48 cartes.",
        "As=1 ou 11; figures=10.",
        "/cmd otra tire; /cmd planto reste.",
        "Le plus proche de 21 sans dépasser gagne.",
    ],
    "de": [
        "Spanisches 48er-Blatt.",
        "Ass=1 oder 11; Bilder=10.",
        "/cmd otra zieht; /cmd planto hält.",
        "Wer 21 nicht überschreitet und am nächsten ist, gewinnt.",
    ],
}


def _deck() -> list[list[Any]]:
    return [[r, s] for s in SUITS for r in RANKS]


def _val(rank: int) -> int:
    if rank >= 10:
        return 10
    return rank


def _total(hand: list[list[Any]]) -> int:
    raw = [_val(int(c[0])) for c in hand]
    total = sum(raw)
    aces = sum(1 for c in hand if int(c[0]) == 1)
    while aces and total + 10 <= 21:
        total += 10
        aces -= 1
    return total


def _label(rank: int) -> str:
    return RANK_NAME.get(rank, str(rank))


def _ascii_card(rank: int, suit: str) -> str:
    lab = _label(rank).ljust(5)
    su = suit[:5].upper().ljust(5)
    return "\n".join(
        [
            "┌───────┐",
            f"│ {lab} │",
            f"│ {su} │",
            "└───────┘",
        ]
    )


def _winner_banner(name: str, lang: str) -> str:
    line = pick(
        lang,
        {
            "es": "GANADOR ES",
            "en": "WINNER IS",
            "fr": "GAGNANT",
            "de": "GEWINNER",
        },
    )
    return "\n".join(
        [
            "*  *  *  *  *",
            f"  {line}",
            f"  {name}",
            "*  *  *  *  *",
        ]
    )


def _fresh() -> dict[str, Any]:
    deck = _deck()
    random.shuffle(deck)
    return {"deck": deck, "players": {}, "order": [], "over": False}


class Blackjack:
    id = "blackjack"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=card(
                "21",
                [
                    pick(
                        lang,
                        {
                            "es": "Cartas del 21. /cmd join y luego /cmd otra.",
                            "en": "Game of 21. /cmd join then /cmd otra.",
                            "fr": "Jeu de 21. /cmd join puis /cmd otra.",
                            "de": "21. /cmd join, dann /cmd otra.",
                        },
                    ),
                    "/cmd cmd list",
                ],
            ),
            state=_fresh(),
            commands=cmds(_HELP.get(lang) or _HELP["en"]),
            title="21",
            rules=list(_RULES.get(lang) or _RULES["en"]),
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        if state.get("over"):
            return Turn(
                say=card(
                    "21",
                    [
                        pick(
                            lang,
                            {
                                "es": "Partida cerrada. /cmd new-game 21",
                                "en": "Hand is over. /cmd new-game 21",
                                "fr": "Finie. /cmd new-game 21",
                                "de": "Vorbei. /cmd new-game 21",
                            },
                        )
                    ],
                ),
                state=state,
            )
        if verb == "join":
            return self._join(request, state, lang)
        if verb == "otra":
            return self._hit(request, state, lang)
        if verb == "planto":
            return self._stand(request, state, lang)
        if verb == "manos":
            return Turn(say=card("21", self._hands_lines(state)), state=state)
        return Turn(say=card("21", [verb]), state=state)

    def _join(self, request: dict, state: dict, lang: str) -> Turn:
        pid = uid(request)
        name = uname(request)
        players: dict = state.setdefault("players", {})
        if pid in players:
            return Turn(
                say=card("21", [pick(lang, {"es": f"{name} ya está.", "en": f"{name} is in.", "fr": f"{name} est là.", "de": f"{name} sitzt."})]),
                state=state,
            )
        players[pid] = {"name": name, "hand": [], "stand": False, "bust": False}
        state.setdefault("order", []).append(pid)
        return Turn(
            say=card("join", [pick(lang, {"es": f"{name} se sienta.", "en": f"{name} sits.", "fr": f"{name} s'assoit.", "de": f"{name} setzt sich."}), "/cmd otra"]),
            state=state,
        )

    def _need_player(self, request: dict, state: dict, lang: str) -> tuple[str, dict] | Turn:
        pid = uid(request)
        players = state.get("players") or {}
        if pid not in players:
            return Turn(
                say=card("21", [pick(lang, {"es": "Primero /cmd join", "en": "First /cmd join", "fr": "D'abord /cmd join", "de": "Zuerst /cmd join"})]),
                state=state,
            )
        return pid, players[pid]

    def _hit(self, request: dict, state: dict, lang: str) -> Turn:
        got = self._need_player(request, state, lang)
        if isinstance(got, Turn):
            return got
        pid, p = got
        if p.get("stand") or p.get("bust"):
            return Turn(
                say=card("21", [pick(lang, {"es": "Ya no puedes pedir.", "en": "You cannot hit.", "fr": "Plus de carte.", "de": "Keine Karte mehr."})]),
                state=state,
            )
        deck: list = state.setdefault("deck", [])
        if not deck:
            extra = _deck()
            random.shuffle(extra)
            deck.extend(extra)
        rank, suit = deck.pop()
        p["hand"].append([rank, suit])
        total = _total(p["hand"])
        art = _ascii_card(int(rank), str(suit))
        lines = art.split("\n") + [f"pts {total}"]
        if total > 21:
            p["bust"] = True
            p["stand"] = True
            lines.append(pick(lang, {"es": "Te pasas.", "en": "Bust.", "fr": "Dépassé.", "de": "Überkauft."}))
        end = self._maybe_end(state, lang)
        if end:
            lines.extend(["", end])
        return Turn(say=card("otra", lines), state=state)

    def _stand(self, request: dict, state: dict, lang: str) -> Turn:
        got = self._need_player(request, state, lang)
        if isinstance(got, Turn):
            return got
        pid, p = got
        p["stand"] = True
        total = _total(p["hand"])
        lines = [f"{p['name']}: {total}"]
        end = self._maybe_end(state, lang)
        if end:
            lines.extend(["", end])
        return Turn(say=card("planto", lines), state=state)

    def _active(self, state: dict) -> bool:
        players = state.get("players") or {}
        if len(players) < 1:
            return True
        return any(not p.get("stand") and not p.get("bust") for p in players.values())

    def _maybe_end(self, state: dict, lang: str) -> str | None:
        players = list((state.get("players") or {}).values())
        if len(players) < 1:
            return None
        if any(not p.get("stand") and not p.get("bust") for p in players):
            return None
        alive = [p for p in players if not p.get("bust") and p.get("hand")]
        if not alive:
            state["over"] = True
            return pick(lang, {"es": "Todos se pasaron.", "en": "Everyone busted.", "fr": "Tout le monde a sauté.", "de": "Alle überkauft."})
        best = max(_total(p["hand"]) for p in alive)
        winners = [p for p in alive if _total(p["hand"]) == best]
        state["over"] = True
        if len(winners) == 1:
            return _winner_banner(winners[0]["name"], lang)
        names = ", ".join(p["name"] for p in winners)
        return pick(lang, {"es": f"Empate: {names}", "en": f"Tie: {names}", "fr": f"Égalité : {names}", "de": f"Unentschieden: {names}"})

    def _hands_lines(self, state: dict) -> list[str]:
        lines: list[str] = []
        for p in (state.get("players") or {}).values():
            total = _total(p.get("hand") or [])
            flag = " *" if p.get("stand") else ""
            if p.get("bust"):
                flag = " X"
            lines.append(f"{p['name']} {total}{flag}")
        return lines or ["—"]
