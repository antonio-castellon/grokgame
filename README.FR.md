![Un chevalier face à un dragon sur une table d’échecs, de Parchís, d’Othello, de cartes et de dés](docs/images/hero-table.jpg)

[EN](README.md) · [ES](README.ES.md) · **FR** · [DE](README.DE.md)

# Grok Multi Game platform (version Telegram)

C’est une expérience avec une idée ridicule et une excuse adorable.

**Un agent peut-il être le maître du donjon ?** Pas un moteur de règles de 400 pages d’errata. Un cerveau. Ce soir, il mène une chasse au dragon. Demain, il sert le 21. Samedi, il devient un Parchís particulièrement rancunier. Le même groupe, les mêmes copains, une autre table.

Le canal, c’est **Telegram**, exprès. Les enfants l’ont déjà. Les parents aussi. Personne n’a à installer *Yet Another Game Client 3.2 (bêta)* ni à créer un compte `xXSorcierSombre2009Xx`. Si le téléphone sait écrire dans un groupe, il a déjà une chaise à cette table.

C’est le vieil internet qui se faufile par une porte moderne. Avant que les cartes graphiques n’aient plus de ventilateurs qu’un stade, on jouait sur des **BBS**, des donjons ASCII et des MUD où un dragon tenait en trois caractères de feu et beaucoup d’imagination :

```
  /\
 /  \    "Tu entends des dés dans le noir."
< DM >
 \  /
  \/
```

La même énergie. Tu tapes une commande. Tu reçois une histoire. Vous vous disputez pour savoir si l’orc avait vraiment une ligne de vue. Le tapis, c’est un chat ; le maître, c’est Grok.

Je l’ai fait **pour le fun, pour mon fils**, pour qu’il embarque ses amis dans une partie sans livre de règles, sans boutique, sans « 40 Go minimum ». Un groupe. Un bot. Un adulte tape `/cmd new-game …` en langage humain. Grok invente le reste. Quand ils ont fini de démolir le phare / le paquet / le royaume, `/cmd clear all` balaie les miettes comme un tavernier trop obéissant.

Si ça marche, on a une taverne de poche qui tient dans un cartable. Sinon, on a quand même une soirée bizarre et des cartes ASCII. Dans les deux cas : le chevalier reste sur la boîte, les enfants restent sur Telegram, et l’adulte n’a pas à expliquer Steam à un gamin de douze ans à 22 h 17.

**Envie d’ouvrir ta propre table ?** Le mode d’emploi (nécessairement ennuyeux) est dans **[SETUP.md](SETUP.md)**.

## Jouer sans Grok (sans clé API)

Un Grok maître en direct demande `XAI_API_KEY` (API payante). **Pas besoin** pour tester la taverne.

Mets `GM_BACKEND=mock` dans `.env` et lance `python -m mesa.main`. Le bot devient une cartouche compilation en Python : même grammaire `/cmd`, pas d’agent, pas de facture.

```
/cmd list games
/cmd load <id>
```

`<id>` est la première colonne (un admin charge le jeu) :

| `/cmd load <id>` | Puis jouer avec |
|---|---|
| `blackjack` | `/cmd join` `/cmd otra` `/cmd planto` — 21 ASCII, `GANADOR ES:` |
| `rpg` | `/cmd join` `look` `go norte` `attack` `inventory` |
| `riddle` | `/cmd guess` `hint` `next` |
| `trivia` | `/cmd a` `b` `c` `d` |
| `dice` | `/cmd join` `/cmd roll` (2d6) |
| `rps` | `/cmd piedra` `papel` `tijera` |
| `number` | `/cmd guess 42` (1–100) |
| `tictactoe` | `/cmd join` `/cmd put 5` |

Ce sont des maquettes, pas Grok. Pour qu’un gamin joue ce soir pendant que l’adulte décide s’il nourrit le dragon de l’API.

---

Le grimoire complet d’un joueur, à peu près :

```
/cmd new-game  …décris le jeu comme à un oncle patient
/cmd join
/cmd cmd list
/cmd clear all     (adultes seulement : vide le groupe)
```

Tout le reste — `otra`, `planto`, `act`, `guess`, `cast` — Grok l’invente pour *cette* soirée. Demain les verbes auront changé. Ce n’est pas un bug : c’est la fonction. La cartouche compilation des années 90 n’a jamais promis que tu rejouerais au même titre deux fois.
