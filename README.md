![A knight facing a dragon over a table of chess, Parchís, Othello, cards and dice](docs/images/hero-table.jpg)

[**EN**](README.md) · [ES](README.ES.md) · [FR](README.FR.md) · [DE](README.DE.md)

# Grok Multi Game platform (telegram version)

This is an experiment with a ridiculous premise and a wholesome excuse.

**Can an agent bot be the Dungeon Master?** Not a rules engine with 400 pages of errata. A brain. Tonight it runs a dragon hunt. Tomorrow it deals 21. On Saturday it becomes Parchís with extra spite. Same group, same friends, new table.

The channel is **Telegram**, on purpose. Kids already have it. Parents already have it. Nobody has to install *Yet Another Game Client 3.2 (beta)* and create an account named `xXDarkWizard2009Xx`. If the phone can ping a group chat, it can sit at this table.

That is the old internet sneaking back in through a modern door. Before graphics cards had more fans than a football stadium, people played on **BBS boards**, ASCII dungeons, and MUDs where a dragon was three characters of fire and a lot of imagination:

```
  /\
 /  \    "You hear dice in the dark."
< DM >
 \  /
  \/
```

Same energy. Type a command. Get a story. Argue about whether the orc really had line of sight. The felt is a chat window; the master is Grok.

I built it **for fun, for my son**, so he can drag his friends into a game without a rulebook, a shop, or a “minimum 40 GB download.” One group. One bot. An adult hits `/cmd new-game …` in plain language. Grok invents the rest. When they are done wrecking the lighthouse / the deck / the kingdom, `/cmd clear all` sweeps the crumbs like a very obedient tavern keeper.

If it works, we get a pocket tavern that fits in a schoolbag. If it does not, we still get a funny evening and some ASCII cards. Either way: the knight stays on the box art, the kids stay on Telegram, and the grown-up does not have to explain Steam to a twelve-year-old at 22:17.

**Want to open your own table?** The boring (necessary) bits are in **[SETUP.md](SETUP.md)**.

## Play without Grok (no API key)

Grok as a live DM needs an `XAI_API_KEY` (paid API). You do **not** need that to try the tavern.

Set `GM_BACKEND=mock` in `.env` and run `python -m mesa.main`. The bot is then a little cartridge compilation in Python: same `/cmd` grammar, no agent, no token bill.

```
/cmd list games          list the local cartridges
/cmd load blackjack      start one by id (admin)
/cmd new-game cartas del 21   same, if the brief matches
```

If the brief matches nothing, you get the old echo table (join / act / look).

| Say this | You get |
|---|---|
| `/cmd new-game cartas del 21` | Spanish 48-card 21. `/cmd join`, `/cmd otra`, `/cmd planto`. ASCII cards + points. `GANADOR ES:` |
| `/cmd new-game mini rol, un goblin en la cueva` | Tiny RPG. `/cmd join`, `look`, `go norte`, `attack`, `inventory` |
| `/cmd new-game acertijos sobre el mar` | Riddles. `/cmd guess`, `hint`, `next` |
| `/cmd new-game trivia de cine` | Quiz. `/cmd a` `b` `c` `d` |
| `/cmd new-game duelo de dados` | 2d6. `/cmd roll` |
| `/cmd new-game piedra papel tijera` | RPS. `/cmd piedra` `papel` `tijera` |
| `/cmd new-game adivina el número` | 1–100. `/cmd guess 42` |
| `/cmd new-game tres en raya` | Tic-tac-toe. `/cmd put 5` |

These are mock-ups, not Grok. They exist so a kid can play tonight while the grown-up decides whether to feed the API dragon.

---

A player’s entire spellbook, more or less:

```
/cmd new-game  …describe the game like you would to a patient uncle
/cmd join
/cmd cmd list
/cmd clear all     (adults only: wipe the group)
```

Everything else — `otra`, `planto`, `act`, `guess`, `cast` — is invented by Grok for *that* night’s game. Tomorrow the verbs will be different. That is the feature, not a bug. The 90s compilation cartridge on the shelf never promised you would play the same title twice.
