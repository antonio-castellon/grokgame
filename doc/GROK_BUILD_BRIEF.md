# Brief para Grok Build — mesa abierta Telegram + Grok Agent

Pega en Grok Build desde «PROMPT PARA GROK BUILD» hasta el final.
Sustituye cualquier diseño anterior con arquetipos fijos, `/elegir`, modos trivia/rol/acertijos hardcodeados o `characters.py`. Eso NO es el producto.

---

## PROMPT PARA GROK BUILD

Construye un **puente de Telegram de gramática abierta**. El juego no está programado. Un admin describe la mesa en lenguaje natural; Grok (Agent Bot, suscripción, webhook) inventa reglas, comandos y límites. El Python solo transporta, guarda estado opaco y aplica una gramática `/cmd`.

### Restricciones duras

- Un proceso: `python -m mesa.main`
- Python 3.10+, `python-telegram-bot` v21+, `python-dotenv`, stdlib
- PROHIBIDO: `openai`, `xai`, `api.x.ai`, LLM local, lista fija de personajes, lista fija de géneros de juego, motor de trivia/acertijos/rol en Python
- El grupo lo crea un humano en Telegram. La app NO crea grupos
- Textos al usuario en el idioma de la mesa (`lang`). Código en inglés
- Secretos solo en `.env`

### Gramática única

```
/cmd <verb> [payload...]
```

También aceptar el alias sin barra en grupo si privacy está off: `cmd <verb> [payload]`

`verb` = identificador `[a-z0-9-]{1,32}`.
`payload` = el resto de la línea, texto libre (puede ir vacío).

Ejemplos que DEBE entender el parser (no el motor de juego):

```
/cmd new-game misterio en un faro, 3 jugadores, sin muerte permanente
/cmd lang es
/cmd lang fr
/cmd cmd list
/cmd rules no se puede matar NPCs infantiles
/cmd limit max 4 jugadores
/cmd status
/cmd reset
/cmd act abro el cajón izquierdo
/cmd whoami
```

El puente NO decide si `act` o `draw` o `cast` existen. Eso lo declara Grok después de `new-game`. El puente:

1. Siempre deja pasar los **verbos de sistema** (lista abajo).
2. Para cualquier otro verbo: si Grok lo publicó en `commands`, lo reenvía; si no, responde «comando desconocido» + lista actual. En mock, la lista sale del último `new-game` simulado.

### Verbos de sistema (existen siempre, aunque no haya juego)

| verb | quién | payload | efecto local + envío a Grok |
|---|---|---|---|
| `help` | cualquiera | — | texto de ayuda en `lang`; no obliga webhook |
| `lang` | admin | `es\|fr\|de\|en` | guarda `lang`; avisa al grupo; notifica a Grok |
| `new-game` | admin | texto libre describiendo el juego | nueva mesa; Grok inventa reglas y comandos |
| `rules` | admin | texto libre | redefinir / añadir reglas |
| `limit` | admin | texto libre | redefinir límites |
| `cmd` | cualquiera | `list` | publica la lista de comandos vigente |
| `status` | cualquiera | — | resumen local + opcionalmente Grok |
| `reset` | admin | opcional `hard` | cierra la mesa; `hard` borra JSON |
| `whoami` | cualquiera | — | nombre, id, si es admin |
| `grant` | admin | `@user` o user id | añade admin de mesa |
| `revoke` | admin | `@user` o user id | quita admin de mesa (no al creator) |

`/cmd cmd list` se parsea como verb=`cmd`, payload=`list`.

Cualquier otro verb (`act`, `roll`, `hint`, `answer`, `sheet`, `join`…) es **verbo de juego** inventado por Grok.

### Quién es admin

Orden:

1. `ADMIN_TELEGRAM_IDS` en `.env` (si está, esos ids siempre son admin).
2. Administradores reales del chat (`getChatAdministrators`) — el que creó el canal/grupo entra aquí.
3. Ids guardados por `/cmd grant`.

El creador del grupo no se puede `revoke`.

Sin admin no hay `new-game` / `rules` / `limit` / `reset` / `lang` / `grant`.

### Qué hace el Python vs qué hace Grok

Python:
- parsea `/cmd`
- persiste JSON por `chat_id`
- comprueba admin
- tira dados SOLO si Grok, en la respuesta anterior, pidió un roll con esquema concreto (ver abajo). Si no hay petición de dado, el puente no tira
- firma y envía webhook
- publica en el grupo el `say` que devuelve Grok (v0: el puente publica siempre)

Grok:
- interpreta `new-game` y fabrica el juego (rol, acertijos, trivia 4 opciones, juicios, brisca narrativa, lo que el admin haya escrito)
- devuelve la lista de comandos de ESE juego
- aplica `rules` y `limit` sobre la marcha
- narra / puntúa / cambia fase
- habla en `lang`

### Contrato webhook (Agent Bot)

Request que envía el puente:

```json
{
  "schema": "mesa.v1",
  "chat_id": -100123,
  "user": {"id": 7, "name": "Ana", "username": "ana", "is_admin": false},
  "lang": "es",
  "verb": "act",
  "payload": "abro el cajón izquierdo",
  "dice": null,
  "table": {
    "phase": "playing",
    "title": "El faro",
    "brief": "misterio en un faro, sin muerte permanente",
    "rules": ["no muerte permanente"],
    "limits": ["max 3 jugadores"],
    "commands": [
      {"verb": "join", "help": "entrar a la mesa"},
      {"verb": "act", "help": "declarar una acción"},
      {"verb": "look", "help": "describir el lugar"}
    ],
    "players": [{"id": 7, "name": "Ana", "flags": {}}],
    "blob": {"opaque": "estado que solo Grok entiende"}
  },
  "expect": "Responde JSON mesa.v1.reply. Texto al grupo en table.lang / lang. No expliques el protocolo."
}
```

Reply que Grok (o MockGM) debe devolver:

```json
{
  "schema": "mesa.v1.reply",
  "say": "Texto para publicar en el grupo (el idioma de lang).",
  "lang": "es",
  "phase": "playing",
  "title": "El faro",
  "commands": [
    {"verb": "join", "help": "..."},
    {"verb": "act", "help": "..."}
  ],
  "rules": ["..."],
  "limits": ["..."],
  "blob": {},
  "dice_request": null
}
```

Si Grok quiere un dado ANTES de narrar el desenlace, en una primera reply pone:

```json
"dice_request": {"expr": "1d20+2", "reason": "forzar la cerradura"}
```

El puente tira, vuelve a llamar al GM con `verb=dice-result` y `dice={expr,total,detail}` y Grok narra. En v0 MockGM puede resolver sin esa ida y vuelta.

`blob` es opaco para Python: se guarda y se reenvía tal cual. Python no lo interpreta.

### MockGM (obligatorio en v0)

Sin Agent se tiene que poder probar el grupo.

Comportamiento del mock al recibir `new-game`:

- Lee el payload como brief
- Infiere a groso modo (solo en el mock, heurística de palabras):
  - si menciona acertijo/enigma → comandos `join`, `guess`, `hint`, `next`
  - si menciona trivia/preguntas/opciones → `join`, `a`, `b`, `c`, `d`, `next`, `score`
  - en cualquier otro caso → `join`, `act`, `look`, `inventory`
- `say` en el `lang` vigente: presenta el juego, reglas extraídas del texto, y dice que `/cmd cmd list` muestra acciones
- Rellena `commands`, `title`, `rules` (copia frases del brief)

`rules` / `limit`: el mock **añade** la línea al array y confirma en `say`.
`lang`: cambia idioma de `say` a partir de entonces (cuatro plantillas cortas es/fr/de/en, no un traductor real).
`cmd list`: lista `commands` + verbos de sistema.
Verbo de juego desconocido: `say` = desconocido + lista.
`reset`: phase=lobby, commands=[], blob={}.

No implementes un motor de combate ni fichas D&D. El mock es un eco inteligente.

### Estado local por chat_id

```json
{
  "chat_id": -100123,
  "lang": "es",
  "phase": "lobby",
  "title": "",
  "brief": "",
  "rules": [],
  "limits": [],
  "commands": [],
  "admins": [],
  "players": {},
  "blob": {},
  "log": []
}
```

Log: últimos 16 `/cmd` (verb + payload recortado + user).

### Estructura repo

```
mesa/
  main.py
  config.py
  parse.py          # /cmd y alias cmd
  store.py
  dice.py
  admin.py          # env + chat admins + grant
  gm/base.py
  gm/mock.py
  gm/webhook.py     # Standard Webhooks HMAC
  telegram/handlers.py
.env.example
README.md
tests/              # parse, admin, mock new-game/rules/lang/cmd-list, webhook sign
```

### .env.example

```
TELEGRAM_BOT_TOKEN=
ADMIN_TELEGRAM_IDS=
GM_BACKEND=mock
WEBHOOK_URL=
WEBHOOK_SECRET=
WEBHOOK_REPLY=http
```

`WEBHOOK_REPLY=http`: si el POST devuelve JSON reply o texto, publícalo. Si no hay cuerpo, publica un aviso corto.

### Mensajes que el admin debe poder hacer en conversación (aceptación)

En un grupo, admin:

```
/cmd lang es
/cmd new-game juego de rol de suspense en un tren, 4 jugadores, dados solo en combates, sin magia
/cmd cmd list
/cmd rules el tren no puede detenerse hasta el final
/cmd limit cada acción máximo 2 frases
/cmd new-game ahora es un concurso de acertijos sobre el mar, pistas de pago
/cmd lang en
/cmd reset
```

Tras el segundo `new-game`, la lista de comandos YA NO es la de rol: Grok/mock la sustituye. El puente no conserva verbos del juego anterior.

Jugador no admin:

```
/cmd join
/cmd act miro por la ventanilla
```

Si `join` no está en `commands` todavía (lobby sin new-game), rechazo local.

### Criterios de aceptación v0

1. Parser cubre `/cmd new-game texto largo`, `/cmd cmd list`, `/cmd lang de`
2. `characters.py`, clases fijas Warrior/Mage, `/elegir`, modos enum `rol|trivia|acertijos` NO existen
3. Mock: `new-game` + `cmd list` muestra verbos distintos según el brief
4. `rules` y `limit` acumulan texto y salen en `status`
5. No admin no puede `new-game` / `reset` / `lang`
6. «buenos días» en el grupo no llama al GM
7. pytest verde; README con BotFather (`/setprivacy` Disable) y `GM_BACKEND=mock`
8. Cero llamadas a api.x.ai

### Fuera de alcance v0

- Crear el Agent Bot (otro paso)
- Traducción real de calidad (plantillas 4 idiomas en mock)
- Imágenes, voz, polls nativos de Telegram (si Grok pide un poll en v1, ya se verá)
- SQLite

Empieza por `parse.py` + store + mock `new-game`/`rules`/`cmd list`/`lang` + handler Telegram. README corto.
