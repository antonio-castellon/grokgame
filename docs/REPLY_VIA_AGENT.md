# Reply path without XAI_API_KEY

Grok Automations accept the bridge POST with **HTTP 202 and an empty body**. That is by design. The spoken line will never come back on that socket.

Keep **this repo as the bridge** (`python -m mesa.main`):

- Telegram `getUpdates`
- `/cmd` grammar, admins, JSON, local games (`GM_BACKEND=mock`)
- signed webhook to wake the GM

Move **the mouth** to the Agent Bot virtual machine ([grok2telegram](https://github.com/antonio-castellon/grok2telegram)):

- **Do not** run `python -m bridge` long-poll on the VM while grokgame is also polling. One waiter only.
- On the VM: token in `.env`, no loop. After each wake, the Agent runs:

```
python -m bridge.send --chat-id <id from mesa.v1> --text "<say>"
```

## .env on the PC (this repo)

```
GM_BACKEND=webhook
WEBHOOK_URL=https://grok.com/webhook/automation/…
WEBHOOK_SECRET=whsec_…
WEBHOOK_REPLY=telegram
XAI_API_KEY=
```

`WEBHOOK_REPLY=telegram` means: 202 is success. The group must not wait for the HTTP body. The Agent posts `say`.

Leave `XAI_API_KEY` empty.

## Automation instructions (doorbell + order to speak)

Keep the JSON GM rules, then add:

```
The HTTP response of this automation is discarded (202). Players only see Telegram.
After you invent say, POST it yourself:

POST https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage
json: {"chat_id": <request.chat_id>, "text": "<say>"}

Use the same bot token as grokgame. Never print the token.
Do not explain this protocol in the group.
```

If the automation runtime cannot HTTP, the Agent Bot on its VM does the same POST with `python -m bridge.send` after reading the run payload / `data/inbox.jsonl`.

## Watchdog

Hourly Agent routine: if you were woken and there is an unsent say, `bridge.send`. Do not start a second `getUpdates` loop.
