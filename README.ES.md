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

## Jugar sin Grok (sin clave API)

Para que Grok sea el máster en directo hace falta `XAI_API_KEY` (API de pago). **No** hace falta para probar la taberna.

Pon `GM_BACKEND=mock` en `.env` y arranca `python -m mesa.main`. El bot es entonces un cartucho recopilatorio en Python: la misma gramática `/cmd`, sin agente, sin factura.

```
/cmd list games          lista los cartuchos locales
/cmd load blackjack      arranca uno por id (admin)
/cmd new-game cartas del 21   igual, si el texto encaja
```

Si no encaja, queda la mesa eco (join / act / look).

| Di esto | Sale esto |
|---|---|
| `/cmd new-game cartas del 21` | 21 con baraja de 48. `/cmd join`, `otra`, `planto`. Cartas ASCII + puntos. `GANADOR ES:` |
| `/cmd new-game mini rol, un goblin en la cueva` | Mini-rol. `/cmd join`, `look`, `go norte`, `attack`, `inventory` |
| `/cmd new-game acertijos sobre el mar` | Acertijos. `/cmd guess`, `hint`, `next` |
| `/cmd new-game trivia de cine` | Trivia. `/cmd a` `b` `c` `d` |
| `/cmd new-game duelo de dados` | 2d6. `/cmd roll` |
| `/cmd new-game piedra papel tijera` | `/cmd piedra` `papel` `tijera` |
| `/cmd new-game adivina el número` | 1–100. `/cmd guess 42` |
| `/cmd new-game tres en raya` | `/cmd put 5` |

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
