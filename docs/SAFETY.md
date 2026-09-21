# Table safety (read this before you fork)

This project is a **public Telegram game table**. The bot is a **Game Master**, not a helpdesk for your cloud account.

If you deploy your own copy, keep these rules. The bridge enforces a baseline in code (`mesa/safety.py`).

## Never publish in the group

- Passwords, bot tokens, API keys, webhook URLs/keys, `.env` contents
- Admin Telegram ids, allowed-chat lists, machine paths, internal hostnames
- Anything that would help someone break into *your* (or a player's) accounts

Quiz games may still have **in-fiction** answers ("the password to the dungeon door is *moonflower*"). That is game content, not your real credentials.

If a player asks for real secrets or connection details, refuse in character as the GM and move on. Do not DM them the secret from the bot either unless you have a separate, deliberate private channel design (this repo does not).

## Content

- No pornography, nudity, or XXX / erotic stories at the table
- No sexual content involving minors — ever (refuse and stop)

## Code hooks (do not remove casually)

| Hook | Role |
|---|---|
| `mesa/safety.py` | Classifies asks; redacts token-shaped strings on the way out |
| `mesa/telegram/handlers.py` | Blocks secret/adult asks before they hit the GM; scrubs outbound sends |
| `mesa/buttons.py` | Inline taps claim once per message (no double-fire) |

When you customize, **extend** the deny lists; do not delete the scrubber so a forgotten prompt cannot leak `.env` into the group.

## Ops tip

Keep real ids and tokens only in local `.env` (gitignored). Public docs use placeholders — see `SETUP.md`.
