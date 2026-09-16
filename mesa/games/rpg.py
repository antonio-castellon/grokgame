from __future__ import annotations

import random
from typing import Any

from mesa.games.common import Turn, cmds, pick, uid, uname
from mesa.skin import DIV, card

KEYWORDS = (
    "rol",
    "rpg",
    "dungeon",
    "mazmorra",
    "dragon",
    "dragón",
    "caballero",
    "knight",
    "aventura",
    "adventure",
)

ROOMS = {
    "tavern": {
        "es": "Taberna. Huele a pretzels. Al norte, un sendero.",
        "en": "Tavern. Pretzels. A path leads north.",
        "fr": "Taverne. Bretzels. Un sentier au nord.",
        "de": "Taverne. Brezeln. Ein Pfad nach Norden.",
        "exits": {"north": "path", "norte": "path"},
    },
    "path": {
        "es": "Bosque. Algo gruñe al norte, en una cueva.",
        "en": "Woods. Something growls north, in a cave.",
        "fr": "Bois. Un grognement au nord, dans une grotte.",
        "de": "Wald. Ein Knurren im Norden, eine Höhle.",
        "exits": {"north": "cave", "norte": "cave", "south": "tavern", "sur": "tavern"},
    },
    "cave": {
        "es": "Cueva húmeda. Un goblin enseña los dientes.",
        "en": "Damp cave. A goblin bares its teeth.",
        "fr": "Grotte. Un gobelin montre les dents.",
        "de": "Höhle. Ein Goblin fletscht die Zähne.",
        "exits": {"south": "path", "sur": "path"},
    },
}

_HELP = {
    "es": [
        ("join", "entrar en la taberna"),
        ("look", "mirar el lugar"),
        ("go", "ir: norte/sur"),
        ("act", "decir qué haces"),
        ("attack", "atacar (1d20)"),
        ("inventory", "ver mochila"),
    ],
    "en": [
        ("join", "enter the tavern"),
        ("look", "look around"),
        ("go", "go north/south"),
        ("act", "say what you do"),
        ("attack", "attack (1d20)"),
        ("inventory", "backpack"),
    ],
    "fr": [
        ("join", "entrer"),
        ("look", "regarder"),
        ("go", "aller nord/sud"),
        ("act", "déclarer une action"),
        ("attack", "attaquer (1d20)"),
        ("inventory", "inventaire"),
    ],
    "de": [
        ("join", "eintreten"),
        ("look", "umsehen"),
        ("go", "gehen nord/süd"),
        ("act", "Aktion sagen"),
        ("attack", "angreifen (1d20)"),
        ("inventory", "Inventar"),
    ],
}


def _hero(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "hp": 12,
        "room": "tavern",
        "inv": ["torch"],
    }


class Rpg:
    id = "rpg"
    keywords = KEYWORDS

    def start(self, lang: str, brief: str) -> Turn:
        return Turn(
            say=card(
                "rol",
                [
                    pick(
                        lang,
                        {
                            "es": "Mini-rol. /cmd join, /cmd look, /cmd go norte.",
                            "en": "Mini-RPG. /cmd join, /cmd look, /cmd go north.",
                            "fr": "Mini-jdr. /cmd join, /cmd look, /cmd go nord.",
                            "de": "Mini-Rollenspiel. /cmd join, /cmd look, /cmd go nord.",
                        },
                    ),
                    pick(
                        lang,
                        {
                            "es": "Hay un goblin en la cueva. 1d20 para atacar.",
                            "en": "A goblin lurks in the cave. Attack with 1d20.",
                            "fr": "Un gobelin dans la grotte. Attaque 1d20.",
                            "de": "Ein Goblin in der Höhle. Angriff 1d20.",
                        },
                    ),
                ],
            ),
            state={"heroes": {}, "goblin": 6, "won": False},
            commands=cmds(_HELP.get(lang) or _HELP["en"]),
            title=pick(lang, {"es": "El goblin", "en": "The goblin", "fr": "Le gobelin", "de": "Der Goblin"}),
            rules=[
                pick(
                    lang,
                    {
                        "es": "Sin muerte permanente: si caes, despiertas en la taberna.",
                        "en": "No permadeath: you wake in the tavern.",
                        "fr": "Pas de mort permanente: tu te réveilles à la taverne.",
                        "de": "Kein Permadeath: du wachst in der Taverne auf.",
                    },
                )
            ],
        )

    def handle(self, verb: str, payload: str, request: dict, state: dict, lang: str) -> Turn:
        if verb == "join":
            return self._join(request, state, lang)
        hero = (state.get("heroes") or {}).get(uid(request))
        if not hero:
            return Turn(
                say=card("rol", [pick(lang, {"es": "Primero /cmd join", "en": "First /cmd join", "fr": "D'abord /cmd join", "de": "Zuerst /cmd join"})]),
                state=state,
            )
        if verb == "look":
            return Turn(say=card("look", self._look(hero, state, lang)), state=state)
        if verb == "go":
            return self._go(hero, payload, state, lang)
        if verb == "inventory":
            stuff = ", ".join(hero.get("inv") or []) or "—"
            return Turn(say=card("inv", [f"{hero['name']}", f"HP {hero['hp']}", stuff]), state=state)
        if verb == "attack":
            return self._attack(hero, state, lang)
        extra = payload or "…"
        return Turn(
            say=card("act", [hero["name"], extra, pick(lang, {"es": "El mundo no se inmuta. Prueba /cmd look.", "en": "Nothing obvious happens. Try /cmd look.", "fr": "Rien. Essaie /cmd look.", "de": "Nichts. /cmd look."})]),
            state=state,
        )

    def _join(self, request: dict, state: dict, lang: str) -> Turn:
        pid = uid(request)
        name = uname(request)
        heroes = state.setdefault("heroes", {})
        if pid not in heroes:
            heroes[pid] = _hero(name)
        hero = heroes[pid]
        return Turn(
            say=card("join", [pick(lang, {"es": f"{name} entra en la taberna.", "en": f"{name} enters the tavern.", "fr": f"{name} entre.", "de": f"{name} tritt ein."}), f"HP {hero['hp']}"]),
            state=state,
        )

    def _look(self, hero: dict, state: dict, lang: str) -> list[str]:
        room_id = hero.get("room") or "tavern"
        room = ROOMS[room_id]
        lines = [pick(lang, room), f"HP {hero['hp']}"]
        if room_id == "cave" and int(state.get("goblin") or 0) > 0:
            lines.append(f"goblin HP {state['goblin']}")
        if state.get("won"):
            lines.append(pick(lang, {"es": "El goblin ya no está.", "en": "The goblin is gone.", "fr": "Plus de gobelin.", "de": "Kein Goblin mehr."}))
        return lines

    def _go(self, hero: dict, payload: str, state: dict, lang: str) -> Turn:
        key = (payload or "").strip().lower()
        room = ROOMS[hero.get("room") or "tavern"]
        dest = (room.get("exits") or {}).get(key)
        if not dest:
            return Turn(
                say=card("go", [pick(lang, {"es": "No hay salida ahí. norte / sur", "en": "No exit that way. north / south", "fr": "Pas de sortie. nord / sud", "de": "Kein Ausgang. nord / süd"})]),
                state=state,
            )
        hero["room"] = dest
        return Turn(say=card("go", self._look(hero, state, lang)), state=state)

    def _attack(self, hero: dict, state: dict, lang: str) -> Turn:
        if hero.get("room") != "cave":
            return Turn(
                say=card("attack", [pick(lang, {"es": "Aquí no hay a quién pegar.", "en": "Nothing to hit here.", "fr": "Rien à frapper.", "de": "Nichts zum Schlagen."})]),
                state=state,
            )
        if int(state.get("goblin") or 0) <= 0:
            return Turn(
                say=card("attack", [pick(lang, {"es": "Ya cayó.", "en": "Already down.", "fr": "Déjà à terre.", "de": "Schon erledigt."})]),
                state=state,
            )
        roll = random.randint(1, 20)
        lines = [f"1d20 = {roll}"]
        if roll >= 12:
            dmg = random.randint(1, 6)
            state["goblin"] = max(0, int(state["goblin"]) - dmg)
            lines.append(f"hit {dmg}  goblin HP {state['goblin']}")
            if state["goblin"] <= 0:
                state["won"] = True
                hero.setdefault("inv", []).append("goblin tooth")
                lines.append(pick(lang, {"es": "El goblin cae. Diente en la mochila.", "en": "Goblin drops. A tooth in your pack.", "fr": "Le gobelin tombe.", "de": "Goblin fällt."}))
        else:
            hero["hp"] = int(hero["hp"]) - 2
            lines.append(pick(lang, {"es": "Fallaste. El goblin araña -2 HP.", "en": "Miss. Goblin claws -2 HP.", "fr": "Raté. -2 HP.", "de": "Daneben. -2 HP."}))
            lines.append(f"HP {hero['hp']}")
            if hero["hp"] <= 0:
                hero["hp"] = 12
                hero["room"] = "tavern"
                lines.append(pick(lang, {"es": "Caes. Despiertas en la taberna.", "en": "You fall. You wake in the tavern.", "fr": "Tu tombes. Taverne.", "de": "Du fällst. Taverne."}))
        return Turn(say=card("attack", lines), state=state)
