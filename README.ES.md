![Un caballero frente a un dragón sobre una mesa de ajedrez, Parchís, Othello, cartas y dados](docs/images/hero-table.jpg)

[EN](README.md) · **ES** · [FR](README.FR.md) · [DE](README.DE.md)

# Grok Multi Game platform (versión Telegram)

Esto es un experimento con una premisa ridícula y una excusa adorable.

**¿Puede un agente ser el máster?** No un motor de reglas con 400 páginas de erratas. Un cerebro. Esta noche dirige una cacería de dragones. Mañana reparte el 21. El sábado se convierte en Parchís con rencor extra. El mismo grupo, los mismos amigos, otra mesa.

El canal es **Telegram**, a propósito. Los críos ya lo tienen. Los padres también. Nadie tiene que instalar *Yet Another Game Client 3.2 (beta)* ni crearse una cuenta llamada `xXMagoOscuro2009Xx`. Si el teléfono sabe escribir en un grupo, ya está sentado a la mesa.

Es internet de los 90 colándose por una puerta de ahora. Antes de que las tarjetas gráficas tuvieran más ventiladores que un estadio, la gente jugaba en **BBS**, mazmorras ASCII y MUDs donde un dragón eran tres caracteres de fuego y mucha imaginación:

```
  /\
 /  \    "Oyes dados en la oscuridad."
< DM >
 \  /
  \/
```

La misma energía. Escribes un comando. Te llega una historia. Discutís si el orco tenía línea de visión. El tapete es un chat; el máster es Grok.

Lo hice **por diversión, para mi hijo**, para que meta a sus amigos en una partida sin reglamento, sin tienda y sin un «mínimo 40 GB». Un grupo. Un bot. Un adulto escribe `/cmd new-game …` en lenguaje de verdad. Grok inventa el resto. Cuando terminen de destrozar el faro / el mazo / el reino, `/cmd clear all` barre las migas como un tabernero demasiado obediente.

Si funciona, tenemos una taberna de bolsillo que cabe en la mochila. Si no, igual nos queda una noche rara y unas cartas ASCII. En cualquier caso: el caballero se queda en la caja, los críos en Telegram, y el adulto no tiene que explicar Steam a un niño de doce años a las 22:17.

**¿Quieres abrir tu propia mesa?** Lo aburrido (e imprescindible) está en **[SETUP.md](SETUP.md)**.

---

## Las tres piezas que se hablan

Este repo es **una** de tres partes. No son tres copias del mismo programa. Cada una tiene un oficio.

```
  jugadores
     |
     v
[3] Grupo de Telegram       la mesa. Los humanos escriben /cmd. Nadie abre Grok.
     |
     |  Bot API (HTTPS de salida)
     v
[2] Python en un PC         ESTE repositorio (grokgame).
     |                       Parsea /cmd, guarda el JSON, tira dados si se los
     |                       piden, habla con Telegram, despierta al máster.
     |
     |  webhook firmado / API
     v
[1] Agent / Automation      el cerebro. Inventa el juego con new-game,
                             habla el idioma de la mesa, devuelve say.
```

| Pieza | Dónde vive | Qué le toca decidir |
|---|---|---|
| **1. Agente** | Nube Grok (suscripción) | Qué *es* el juego. Verbos tras `new-game`. Narración. Reglas que acaba de inventar el admin. |
| **2. Python en el PC** | Tu máquina, este repo, `python -m mesa.main` | Gramática `/cmd`, quién es admin, JSON en disco, dados, I/O de Telegram. No la historia. |
| **3. Telegram** | El grupo que creas a mano | Lo único que ven los jugadores. La app nunca crea el grupo. |

El proceso del PC tiene que seguir en marcha o el grupo se queda mudo. El Agent duerme entre turnos: esta app lo despierta (webhook). Un webhook de Automations responde **`202` y cuerpo vacío** — es un timbre, no la frase dicha. Para que `say` vuelva al grupo hace falta `XAI_API_KEY` (ver SETUP) o el proyecto hermano de abajo.

**Hermano, sin PC en el camino:** [grok2telegram](https://github.com/antonio-castellon/grok2telegram) monta el mismo tubo `/cmd` **en la máquina virtual del Agent Bot**. Long-poll a Telegram desde la nube de Grok (solo HTTPS de salida) y `sendMessage` al grupo. Úsalo cuando el PC de casa no puede ser servidor y no quieres la API de pago.

No arranques *dos* bucles `getUpdates` a la vez (PC + VM) con el mismo token. Telegram entrega cada update a un solo waiter.

---

## Jugar sin Grok (sin clave API)

Para que Grok sea el máster en directo hace falta `XAI_API_KEY` (API de pago). **No** hace falta para probar la taberna.

Pon `GM_BACKEND=mock` en `.env` y arranca `python -m mesa.main`. El bot es entonces un cartucho recopilatorio en Python: la misma gramática `/cmd`, sin agente, sin factura.

```
/cmd list games
/cmd load <id>
```

`<id>` es la primera columna (un admin carga el juego):

| `/cmd load <id>` | Luego juegas con |
|---|---|
| `blackjack` | `/cmd join` `/cmd otra` `/cmd planto` — 21 ASCII, `GANADOR ES:` |
| `rpg` | `/cmd join` `look` `go norte` `attack` `inventory` |
| `riddle` | `/cmd guess` `hint` `next` |
| `trivia` | `/cmd a` `b` `c` `d` |
| `dice` | `/cmd join` `/cmd roll` (2d6) |
| `rps` | `/cmd piedra` `papel` `tijera` |
| `number` | `/cmd guess 42` (1–100) |
| `tictactoe` | `/cmd join` `/cmd put 5` |

Son maquetas, no Grok. Están para que un crío juegue esta noche mientras el adulto decide si da de comer al dragón de la API.

---

El grimorio entero de un jugador, más o menos:

```
/cmd new-game  …describe el juego como se lo contarías a un tío paciente
/cmd join
/cmd cmd list
/cmd clear all     (solo adultos: borra el grupo)
```

Todo lo demás — `otra`, `planto`, `act`, `guess`, `cast` — lo inventa Grok para *esa* noche. Mañana los verbos serán otros. Eso no es un fallo: es el truco. El cartucho recopilatorio de los 90 nunca prometió que ibas a jugar al mismo título dos veces.
