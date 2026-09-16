from __future__ import annotations

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import card

KEYWORDS = ("trivia", "quiz", "preguntas", "opciones", "questions")

Q = [
    {
        "q": {"es": "¿Cuántos lados tiene un hexágono?", "en": "How many sides has a hexagon?", "fr": "Côtés d'un hexagone ?", "de": "Seiten eines Sechsecks?"},
        "opts": ("4", "5", "6", "8"),
        "ok": "c",
    },
    {
        "q": {"es": "Capital de Francia", "en": "Capital of France", "fr": "Capitale de la France", "de": "Hauptstadt Frankreichs"},
        "opts": ("Lyon", "Paris", "Marsella", "Niza"),
        "ok": "b",
    },
    {
        "q": {"es": "2+2×2 =", "en": "2+2×2 =", "fr": "2+2×2 =", "de": "2+2×2 ="},
        "opts": ("6", "8", "4", "2"),
        "ok": "a",
    },
]


class Trivia:
    id = "trivia"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=self._qcard(0, lang),
            state={"i": 0, "scores": {}},
            commands=cmds(
                [
                    ("join", "join"),
                    ("a", "A"),
                    ("b", "B"),
                    ("c", "C"),
                    ("d", "D"),
                    ("next", "next"),
                    ("score", "score"),
                ]
            ),
            title="trivia",
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        i = int(state.get("i") or 0) % len(Q)
        if verb == "join":
            state.setdefault("scores", {}).setdefault(uid(request), 0)
            return Turn(say=card("join", [uname(request)]), state=state)
        if verb == "next":
            state["i"] = (i + 1) % len(Q)
            return Turn(say=self._qcard(state["i"], lang), state=state)
        if verb == "score":
            scores = state.get("scores") or {}
            lines = [f"{k} {v}" for k, v in scores.items()] or ["—"]
            return Turn(say=card("score", lines), state=state)
        if verb in {"a", "b", "c", "d"}:
            ok = Q[i]["ok"]
            scores = state.setdefault("scores", {})
            pid = uid(request)
            if verb == ok:
                scores[pid] = int(scores.get(pid, 0)) + 1
                msg = pick(lang, {"es": "Correcto.", "en": "Correct.", "fr": "Correct.", "de": "Richtig."})
            else:
                msg = pick(lang, {"es": f"No. Era {ok.upper()}.", "en": f"No. It was {ok.upper()}.", "fr": f"Non. C'était {ok.upper()}.", "de": f"Nein. {ok.upper()}."})
            state["i"] = (i + 1) % len(Q)
            return Turn(say=card(verb, [uname(request), msg]), state=state)
        return Turn(say=self._qcard(i, lang), state=state)

    def _qcard(self, i: int, lang: str) -> str:
        item = Q[i]
        letters = "ABCD"
        lines = [pick(lang, item["q"])]
        for n, opt in enumerate(item["opts"]):
            lines.append(f"{letters[n]}) {opt}")
        return card("trivia", lines)
