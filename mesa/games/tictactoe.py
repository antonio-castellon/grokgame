from __future__ import annotations

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import card

KEYWORDS = ("tres en raya", "3 en raya", "tic-tac", "tictactoe", "tic tac toe", "noughts")

WINS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def _board(cells: list[str]) -> list[str]:
    def c(i: int) -> str:
        return cells[i] if cells[i] else str(i + 1)

    return [
        f" {c(0)} | {c(1)} | {c(2)} ",
        "---+---+---",
        f" {c(3)} | {c(4)} | {c(5)} ",
        "---+---+---",
        f" {c(6)} | {c(7)} | {c(8)} ",
    ]


class TicTacToe:
    id = "tictactoe"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        cells = [""] * 9
        return Turn(
            say=card("ttt", _board(cells) + ["/cmd join  /cmd put 5"]),
            state={"cells": cells, "x": None, "o": None, "turn": "x", "names": {}},
            commands=cmds(
                [
                    ("join", "X then O"),
                    ("put", pick(lang, {"es": "casilla 1–9", "en": "cell 1–9", "fr": "case 1–9", "de": "Feld 1–9"})),
                ]
            ),
            title=pick(lang, {"es": "Tres en raya", "en": "Tic-tac-toe", "fr": "Morpion", "de": "Drei gewinnt"}),
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        pid = uid(request)
        name = uname(request)
        cells: list[str] = list(state.get("cells") or [""] * 9)
        names: dict = state.setdefault("names", {})
        if verb == "join":
            if state.get("x") is None:
                state["x"] = pid
                names[pid] = name
                mark = "X"
            elif state.get("o") is None and pid != state.get("x"):
                state["o"] = pid
                names[pid] = name
                mark = "O"
            else:
                mark = "X" if pid == state.get("x") else "O" if pid == state.get("o") else "?"
            return Turn(say=card("join", [f"{name} {mark}"]), state=state)
        if verb == "put":
            try:
                n = int((payload or "").strip())
            except ValueError:
                return Turn(say=card("put", ["1–9"]), state=state)
            if n < 1 or n > 9 or cells[n - 1]:
                return Turn(say=card("put", [pick(lang, {"es": "Casilla ocupada.", "en": "Taken.", "fr": "Occupée.", "de": "Belegt."})]), state=state)
            turn = state.get("turn") or "x"
            if (turn == "x" and pid != state.get("x")) or (turn == "o" and pid != state.get("o")):
                return Turn(say=card("put", [pick(lang, {"es": "No es tu turno.", "en": "Not your turn.", "fr": "Pas ton tour.", "de": "Nicht dran."})]), state=state)
            mark = "X" if turn == "x" else "O"
            cells[n - 1] = mark
            state["cells"] = cells
            if any(cells[a] == cells[b] == cells[c] == mark for a, b, c in WINS):
                state["turn"] = "done"
                return Turn(say=card("ttt", _board(cells) + [f"GANADOR ES: {name}"]), state=state)
            if all(cells):
                state["turn"] = "done"
                return Turn(say=card("ttt", _board(cells) + [pick(lang, {"es": "Empate.", "en": "Tie.", "fr": "Égalité.", "de": "Unentschieden."})]), state=state)
            state["turn"] = "o" if turn == "x" else "x"
            return Turn(say=card("ttt", _board(cells)), state=state)
        return Turn(say=card("ttt", _board(cells)), state=state)
