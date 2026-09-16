from __future__ import annotations

from mesa.games.blackjack import Blackjack
from mesa.games.dice import DiceDuel
from mesa.games.number import NumberGuess
from mesa.games.riddle import Riddle
from mesa.games.rpg import Rpg
from mesa.games.rps import Rps
from mesa.games.tictactoe import TicTacToe
from mesa.games.trivia import Trivia

# First keyword hit wins. RPG before "dados" so "dados solo en combates" stays a role table.
GAMES = (
    Blackjack(),
    TicTacToe(),
    Rps(),
    NumberGuess(),
    Riddle(),
    Trivia(),
    Rpg(),
    DiceDuel(),
)

BY_ID = {g.id: g for g in GAMES}


def pick_game(brief: str):
    text = (brief or "").lower()
    for game in GAMES:
        if any(k in text for k in game.keywords):
            return game
    return None


def get_game(game_id: str):
    return BY_ID.get(game_id)


LABELS = {
    "blackjack": {
        "es": "21, baraja de 48",
        "en": "21, 48-card deck",
        "fr": "21, jeu de 48",
        "de": "21, 48 Karten",
    },
    "rpg": {
        "es": "mini-rol, goblin",
        "en": "mini-RPG, goblin",
        "fr": "mini-jdr, gobelin",
        "de": "Mini-Rollenspiel",
    },
    "riddle": {
        "es": "acertijos",
        "en": "riddles",
        "fr": "énigmes",
        "de": "Rätsel",
    },
    "trivia": {
        "es": "trivia A B C D",
        "en": "trivia A B C D",
        "fr": "quiz A B C D",
        "de": "Quiz A B C D",
    },
    "dice": {
        "es": "duelo 2d6",
        "en": "2d6 duel",
        "fr": "duel 2d6",
        "de": "2d6-Duell",
    },
    "rps": {
        "es": "piedra papel tijera",
        "en": "rock paper scissors",
        "fr": "pierre feuille ciseaux",
        "de": "Schere Stein Papier",
    },
    "number": {
        "es": "adivina 1–100",
        "en": "guess 1–100",
        "fr": "devine 1–100",
        "de": "Zahl 1–100",
    },
    "tictactoe": {
        "es": "tres en raya",
        "en": "tic-tac-toe",
        "fr": "morpion",
        "de": "Drei gewinnt",
    },
}

_ALIASES = {
    "21": "blackjack",
    "cartas": "blackjack",
    "rol": "rpg",
    "ttt": "tictactoe",
    "3enraya": "tictactoe",
    "dados": "dice",
    "ppt": "rps",
}


def resolve_game(name: str):
    key = (name or "").strip().lower().replace(" ", "")
    if not key:
        return None
    if key in BY_ID:
        return BY_ID[key]
    if key in _ALIASES:
        return BY_ID[_ALIASES[key]]
    return pick_game(name)


def catalog_lines(lang: str) -> list[str]:
    lang = lang if lang in ("es", "fr", "de", "en") else "en"
    lines = []
    for game in GAMES:
        label = (LABELS.get(game.id) or {}).get(lang) or game.id
        lines.append(f"{game.id}  {label}")
    return lines
