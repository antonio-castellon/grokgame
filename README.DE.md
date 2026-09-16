![Ein Ritter vor einem Drachen über einem Tisch mit Schach, Parchís, Othello, Karten und Würfeln](docs/images/hero-table.jpg)

[EN](README.md) · [ES](README.ES.md) · [FR](README.FR.md) · **DE**

# Grok Multi Game platform (Telegram-Version)

Das hier ist ein Experiment mit einer albernen Prämisse und einer herzlichen Ausrede.

**Kann ein Agent der Spielleiter sein?** Keine Regelmaschine mit 400 Seiten Errata. Ein Gehirn. Heute Abend leitet er eine Drachenjagd. Morgen gibt er 21 aus. Am Samstag wird er zum Parchís mit Extra-Bosheit. Dieselbe Gruppe, dieselben Freunde, ein neuer Tisch.

Der Kanal ist **Telegram**, absichtlich. Die Kinder haben es schon. Die Eltern auch. Niemand muss *Yet Another Game Client 3.2 (beta)* installieren oder einen Account namens `xXDunklerMagier2009Xx` anlegen. Wenn das Handy in eine Gruppe tippen kann, hat es schon einen Platz an diesem Tisch.

Das ist das alte Internet, das sich durch eine moderne Tür mogelt. Bevor Grafikkarten mehr Lüfter hatten als ein Fußballstadion, spielte man auf **BBS-Boards**, ASCII-Kerkern und MUDs, wo ein Drache aus drei Zeichen Feuer und sehr viel Vorstellungskraft bestand:

```
  /\
 /  \    "Du hörst Würfel in der Dunkelheit."
< DM >
 \  /
  \/
```

Dieselbe Energie. Befehl tippen. Geschichte kriegen. Streiten, ob der Ork wirklich Sichtlinie hatte. Das Filz ist ein Chatfenster; der Meister ist Grok.

Ich habe es **zum Spaß, für meinen Sohn** gebaut, damit er seine Freunde in ein Spiel ziehen kann — ohne Regelbuch, ohne Shop, ohne „mindestens 40 GB Download“. Eine Gruppe. Ein Bot. Ein Erwachsener schreibt `/cmd new-game …` in normaler Sprache. Grok erfindet den Rest. Wenn sie den Leuchtturm / das Kartenspiel / das Königreich ruiniert haben, fegt `/cmd clear all` die Krümel weg wie ein überaus gehorsamer Wirt.

Wenn es klappt, haben wir eine Taschentaverne für den Ranzen. Wenn nicht, bleibt wenigstens ein schräger Abend und ein paar ASCII-Karten. So oder so: der Ritter bleibt auf der Schachtel, die Kinder bleiben bei Telegram, und der Erwachsene muss einem Zwölfjährigen um 22:17 nicht Steam erklären.

**Eigenen Tisch aufmachen?** Das Langweilige (aber Nötige) steht in **[SETUP.md](SETUP.md)**.

## Spielen ohne Grok (ohne API-Key)

Grok als Live-Spielleiter braucht `XAI_API_KEY` (kostenpflichtige API). Zum Testen der Taverne **nicht**.

Setze `GM_BACKEND=mock` in `.env` und starte `python -m mesa.main`. Der Bot ist dann eine Python-Compilation-Kassette: dieselbe `/cmd`-Grammatik, kein Agent, keine Rechnung.

```
/cmd list games          lokale Spiele auflisten
/cmd load blackjack      eines per id starten (Admin)
/cmd new-game cartas del 21   dasselbe, wenn der Text passt
```

Sonst Echo-Tisch (join / act / look).

| Sag das | Bekommst du |
|---|---|
| `/cmd new-game cartas del 21` | 21, 48 Karten. `join`, `otra`, `planto`. ASCII-Karten. `GANADOR ES:` |
| `/cmd new-game mini rol, un goblin en la cueva` | Mini-Rollenspiel. `look`, `go norte`, `attack` |
| `/cmd new-game acertijos sobre el mar` | Rätsel. `guess`, `hint`, `next` |
| `/cmd new-game trivia de cine` | Quiz. `a` `b` `c` `d` |
| `/cmd new-game duelo de dados` | 2d6. `roll` |
| `/cmd new-game piedra papel tijera` | `piedra` `papel` `tijera` |
| `/cmd new-game adivina el número` | 1–100. `guess 42` |
| `/cmd new-game tres en raya` | `put 5` |

Das sind Attrappen, nicht Grok. Damit ein Kind heute Abend spielen kann, während der Erwachsene überlegt, ob der API-Drache Futter bekommt.

---

Das ganze Zauberbuch eines Spielers, ungefähr:

```
/cmd new-game  …beschreib das Spiel wie einem geduldigen Onkel
/cmd join
/cmd cmd list
/cmd clear all     (nur Erwachsene: Gruppe leeren)
```

Alles andere — `otra`, `planto`, `act`, `guess`, `cast` — erfindet Grok für *diesen* Abend. Morgen sind die Verben andere. Das ist kein Fehler, das ist der Witz. Die 90er-Compilation-Kassette im Regal hat nie versprochen, dass du zweimal denselben Titel spielst.
