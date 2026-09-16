from __future__ import annotations

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import card

KEYWORDS = ("acertijo", "acertijos", "enigma", "enigmas", "riddle", "riddles", "puzzle")

RIDDLES = [
    {"q": {"es": "Blanco por dentro, verde por fuera. ¿Qué es?", "en": "White inside, green outside?", "fr": "Blanc dedans, vert dehors ?", "de": "Innen weiß, außen grün?"}, "a": ("pera", "pear", "poire")},
    {"q": {"es": "Oro parece, plata no es.", "en": "Looks like gold, is not silver. Banana in Spanish riddle: plata no es.", "fr": "On dirait de l'or, ce n'est pas de l'argent.", "de": "Sieht aus wie Gold, ist kein Silber."}, "a": ("platano", "plátano", "banana", "banane")},
    {"q": {"es": "Va por el agua y no se moja.", "en": "Goes on water and does not get wet.", "fr": "Va sur l'eau sans se mouiller.", "de": "Geht übers Wasser und wird nicht nass."}, "a": ("sombra", "shadow", "ombre", "schatten")},
]


class Riddle:
    id = "riddle"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=card("riddle", [pick(lang, RIDDLES[0]["q"]), "/cmd guess …"]),
            state={"i": 0, "scores": {}},
            commands=cmds(
                [
                    ("join", pick(lang, {"es": "jugar", "en": "play", "fr": "jouer", "de": "spielen"})),
                    ("guess", pick(lang, {"es": "probar respuesta", "en": "try an answer", "fr": "deviner", "de": "raten"})),
                    ("hint", pick(lang, {"es": "pista", "en": "hint", "fr": "indice", "de": "Hinweis"})),
                    ("next", pick(lang, {"es": "siguiente", "en": "next", "fr": "suivant", "de": "weiter"})),
                ]
            ),
            title=pick(lang, {"es": "Acertijos", "en": "Riddles", "fr": "Énigmes", "de": "Rätsel"}),
            rules=[brief] if brief else [],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        i = int(state.get("i") or 0) % len(RIDDLES)
        r = RIDDLES[i]
        name = uname(request)
        if verb == "join":
            state.setdefault("scores", {})[uid(request)] = state.get("scores", {}).get(uid(request), 0)
            return Turn(say=card("join", [name, pick(lang, r["q"])]), state=state)
        if verb == "hint":
            ans = r["a"][0]
            return Turn(say=card("hint", [f"{ans[:1]}…"]), state=state)
        if verb == "next":
            state["i"] = (i + 1) % len(RIDDLES)
            return Turn(say=card("next", [pick(lang, RIDDLES[state["i"]]["q"])]), state=state)
        if verb == "guess":
            g = (payload or "").strip().lower()
            if g in r["a"]:
                scores = state.setdefault("scores", {})
                scores[uid(request)] = int(scores.get(uid(request), 0)) + 1
                state["i"] = (i + 1) % len(RIDDLES)
                return Turn(
                    say=card("guess", [pick(lang, {"es": f"Sí, {name}.", "en": f"Yes, {name}.", "fr": f"Oui, {name}.", "de": f"Ja, {name}."}), pick(lang, RIDDLES[state["i"]]["q"])]),
                    state=state,
                )
            return Turn(say=card("guess", [pick(lang, {"es": "No.", "en": "No.", "fr": "Non.", "de": "Nein."})]), state=state)
        return Turn(say=card("riddle", [pick(lang, r["q"])]), state=state)
