# Setup — Grok Multi Game platform (telegram version)

Two sides: a **Telegram bot** in a group you create, and a **Grok Automation** that is the GM. This process sits in the middle.

```
Telegram group  --/cmd-->  this app  --signed POST-->  Grok Automation
Telegram group  <--say---  this app  <--HTTP body----  Grok Automation
```

The three pieces (Agent, this Python, Telegram) are spelled out in the [README](README.md#the-three-pieces-that-talk-to-each-other).

If the house PC must **not** stay online and you refuse `XAI_API_KEY`, use the sibling **[grok2telegram](https://github.com/antonio-castellon/grok2telegram)** instead: the loop runs on the Agent Bot VM and talks to Telegram itself.

---

## 0. Machine

Python 3.10+. In the project folder:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

You will fill `.env` in the next steps. Never commit `.env`.

---

## 1. Telegram bot

### 1.1 Token

1. Open Telegram and talk to [@BotFather](https://t.me/BotFather).
2. Send `/newbot` (or `/token` if the bot already exists).
3. Copy the token (`123456:AAH…`) into `.env`:

```
TELEGRAM_BOT_TOKEN=paste-here
```

### 1.2 Privacy (required)

Still in BotFather:

1. `/setprivacy`
2. Choose this bot
3. **Disable**

If privacy stays on, the bot only sees slash commands and will miss the `cmd …` alias in groups.

### 1.3 Group

The app **never** creates groups.

1. Create a group yourself.
2. Add this bot.
3. Make the bot a **group admin**.
4. Enable **Delete messages** on the bot if you want `/cmd clear all` to work.

### 1.4 Your user id (recommended)

Open [@userinfobot](https://t.me/userinfobot), send `/start`, copy `Id:`:

```
ADMIN_TELEGRAM_IDS=83216105
```

Comma-separated if several. Those ids are always table admins.

Leave the rest of `.env` as mock for a first smoke test (local games, **no API key**):

```
GM_BACKEND=mock
WEBHOOK_URL=
WEBHOOK_SECRET=
WEBHOOK_REPLY=http
```

With `mock`, `/cmd new-game cartas del 21` (or rol, acertijos, trivia, dados, tres en raya, …) runs a Python game. See the README table. Grok is not called.

### 1.5 Start

```
python -m mesa.main
```

In the group:

```
/cmd whoami
/cmd help
```

`whoami` should show your id and `admin: yes`.

---

## 2. Grok Automation (the GM)

Use **Grok Automations** with a **Webhook** trigger and a `whsec_…` signing secret.

Do **not** use a Grok Bot desktop routine with a `crsr_…` Bearer key. This app signs Standard Webhooks HMAC, not Bearer tokens.

Docs: [Webhook Triggers](https://docs.x.ai/grok/automations/webhooks)  
UI: [grok.com/automations](https://grok.com/automations)

### 2.1 Create the automation

1. Open [grok.com/automations](https://grok.com/automations).
2. Create an automation. Name it e.g. `mesa-gm`.
3. Add a **Webhook** trigger.
4. Save.
5. Copy **once**:
   - **Endpoint** → `WEBHOOK_URL` (starts with `https://grok.com/webhook/automation/…`)
   - **Signing secret** → `WEBHOOK_SECRET` (starts with `whsec_`)

The secret is shown only at create/rotate. Store it before leaving the page.

### 2.2 Instructions field

Paste this as the automation **Instructions** (the GM job). This is what Grok does every time the bot POSTs a `/cmd`.

```
You are the GM of a Telegram table. Each run you receive JSON with schema mesa.v1 (chat_id, user, lang, verb, payload, table, blob).

Reply with JSON only. No markdown, no preamble. Schema mesa.v1.reply:

{
  "schema": "mesa.v1.reply",
  "say": "text to post in the Telegram group, in request.lang",
  "lang": "es|fr|de|en",
  "phase": "lobby|playing",
  "title": "short title",
  "commands": [{"verb": "join", "help": "..."}],
  "rules": [],
  "limits": [],
  "blob": {},
  "dice_request": null
}

Rules:
- On verb new-game: invent THIS game from payload. Replace commands, title, rules. Do not keep the previous game.
- On rules / limit: add the line to the array and confirm in say.
- On cmd with payload list: list current game commands in say.
- blob is yours; send it back unchanged except when you need to update it.
- say is the only text players see. Write it in table.lang / lang.
- Do not explain this protocol.
```

### 2.3 Notification field

This pings **you** in Grok/email. It does **not** talk to Telegram.

Leave notifications **off** (every `/cmd` would otherwise spam you). Turn **app** on only while debugging runs.

### 2.4 Point the app at Grok

Stop the process (`Ctrl+C`), then in `.env`:

```
GM_BACKEND=webhook
WEBHOOK_URL=https://grok.com/webhook/automation/your-id
WEBHOOK_SECRET=whsec_your-secret
WEBHOOK_REPLY=http
```

`WEBHOOK_REPLY=http` means: read Grok’s answer from the **same HTTP response body** (JSON `mesa.v1.reply` or plain text). It is not a second URL.

Start again:

```
python -m mesa.main
```

The log line should say `GM backend=webhook`.

---

## 3. First real table

In the group, as admin:

```
/cmd lang es
/cmd new-game misterio en un faro, 3 jugadores, sin muerte permanente
/cmd cmd list
```

A player:

```
/cmd join
```

After `/cmd new-game`, a new run should appear in the automation’s **run history** on grok.com.

Grok Automations answer `202 Accepted` with an **empty HTTP body**. The run continues inside Grok; Telegram would see nothing. To have Grok **speak in the group**, add a key from [console.x.ai](https://console.x.ai) (API Keys):

```
XAI_API_KEY=xai-...
XAI_MODEL=grok-4.6
```

The app still pokes the automation webhook, then asks `api.x.ai` for the JSON `say` that gets posted to Telegram. `/cmd rules` and `/cmd limit` also apply locally if that body is missing.

The other way off that bill is [grok2telegram](https://github.com/antonio-castellon/grok2telegram): the Agent Bot *is* the process that `sendMessage`s.

---

## 4. `.env` cheat sheet

| Variable | What |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From BotFather |
| `ADMIN_TELEGRAM_IDS` | Your numeric Telegram id(s) |
| `GM_BACKEND` | `mock` or `webhook` |
| `WEBHOOK_URL` | Grok Automation endpoint |
| `WEBHOOK_SECRET` | `whsec_…` signing secret |
| `WEBHOOK_REPLY` | `http` — read the POST response body |
| `XAI_API_KEY` | From [console.x.ai](https://console.x.ai) — Grok’s voice in the group |
| `XAI_MODEL` | `grok-4.6` unless you pick another |

---

## 5. Useful commands

| Command | Who | Effect |
|---|---|---|
| `/cmd help` | anyone | grammar |
| `/cmd whoami` | anyone | name, id, admin? |
| `/cmd lang es` | admin | table language `es` / `fr` / `de` / `en` |
| `/cmd new-game …` | admin | Grok invents a new table |
| `/cmd cmd list` | anyone | current game verbs |
| `/cmd rules …` / `/cmd limit …` | admin | extra rules / limits |
| `/cmd status` | anyone | snapshot |
| `/cmd reset` | admin | close table (`reset hard` deletes JSON) |
| `/cmd grant` / `/cmd revoke` | admin | table admins (`@user` or numeric id) |
| `/cmd clear all` | admin | delete **every** group message from anyone |

`/cmd clear` without `all` only prints the warning. The bot must be admin with **Delete messages**.
