# mesa — open-grammar Telegram table

The game is **not** in this Python. A group admin describes the table in natural language; Grok (Agent Bot webhook) invents rules, commands and limits. This process only parses `/cmd`, stores opaque JSON per chat, checks admins, optionally rolls dice the GM requested, and publishes `say`.

One process:

```
python -m mesa.main
```

## Setup

Python 3.10+.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Fill `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather). Leave `GM_BACKEND=mock` until the Agent webhook exists.

### BotFather

1. `/newbot` — copy the token into `.env`.
2. `/setprivacy` — **Disable**. Otherwise the bot only sees slash commands and the `cmd …` alias in groups will not work.
3. Add the bot to a group **you** create. The app never creates Telegram groups.
4. Make the bot a group admin so it can read `getChatAdministrators` (the group creator is then an admin of the table).

Optional: `ADMIN_TELEGRAM_IDS=123,456` — those user ids are always table admins.

## Grammar

```
/cmd <verb> [payload...]
```

In a group with privacy off, the same line without the slash also works: `cmd <verb> [payload]`.

`verb` is `[a-z0-9-]{1,32}`. Everything after it is free text.

System verbs (always exist): `help`, `lang`, `new-game`, `rules`, `limit`, `cmd`, `status`, `reset`, `whoami`, `grant`, `revoke`.

Any other verb (`act`, `join`, `guess`, …) is a **game** verb. The bridge forwards it only if the last GM `new-game` published it in `commands`. A second `new-game` replaces that list; the previous game is gone.

## Try it (mock GM)

In the group, as admin:

```
/cmd lang es
/cmd new-game juego de rol de suspense en un tren, 4 jugadores, dados solo en combates, sin magia
/cmd cmd list
/cmd rules el tren no puede detenerse hasta el final
/cmd limit cada acción máximo 2 frases
/cmd new-game ahora es un concurso de acertijos sobre el mar, pistas de pago
```

After the second `new-game` the command list is riddle verbs (`join`, `guess`, `hint`, `next`), not role-play verbs.

A non-admin:

```
/cmd join
/cmd act miro por la ventanilla
```

`join` is rejected while the table is still lobby (no `new-game` yet). Plain chat (`buenos días`) is ignored and never reaches the GM.

## Webhook GM (later)

`GM_BACKEND=webhook` plus `WEBHOOK_URL` and `WEBHOOK_SECRET`. Requests are `schema: mesa.v1`, signed with [Standard Webhooks](https://www.standardwebhooks.com/) HMAC (`webhook-id`, `webhook-timestamp`, `webhook-signature: v1,…`).

`WEBHOOK_REPLY=http`: if the POST returns JSON `mesa.v1.reply` or plain text, the bridge publishes it. An empty body gets a short notice in the group.

v0 always publishes `say`. If the reply includes `dice_request`, the bridge rolls and calls back with `verb=dice-result`.

## Tests

```
pytest
```

No calls to `api.x.ai`. No hardcoded characters, genres, trivia engine or `/elegir`.
