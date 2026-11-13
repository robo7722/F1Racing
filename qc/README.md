# QC-Bot: Strecken automatisch abfahren und prüfen

Der Bot fährt jede Strecke selbst (das Spielerauto wird von der KI gesteuert), schaut aus jeder Kamera,
prüft die Strecke zusätzlich von oben und schreibt einen HTML-Bericht mit Bildern zu jedem Befund.

## Starten

Am einfachsten: **`qc/QC-starten.bat` doppelklicken**. Sie fragt nach den Strecken (leer = alle) und dem Umfang
(schnell oder gründlich) und öffnet am Ende den Bericht.

Im Claude-Chat: `/strecken-qc monza spa` (oder „prüf die neue Strecke“) – Claude startet den Bot im Hintergrund
und fasst die Befunde zusammen.

Von Hand:

```bash
python qc/run.py
```

Das prüft alle Strecken mit einer Runde je Kamera. Edge läuft dabei **unsichtbar im Hintergrund**, es öffnet sich kein Fenster.
Am Ende öffnet sich der Bericht `qc-reports/<Datum_Uhrzeit>/report.html`.

| Aufruf | Wirkung |
|---|---|
| `python qc/run.py monza spa` | nur diese Strecken (Schlüssel wie in `TRACKS`) |
| `python qc/run.py neuestrecke --quick` | eine Runde, Kamera wechselt nach jedem Viertel – gut für schnelle Durchläufe beim Bauen |
| `python qc/run.py --laps 2` | feste Rundenzahl (Standard: eine Runde je Kamera) |
| `python qc/run.py --gfx ultra` | Grafikstufe für den Lauf |
| `python qc/run.py --show` | sichtbares Fenster statt unsichtbar (echte Bildausgabe, misst Ruckler am genauesten) |
| `python qc/run.py --size 892,412` | Fenstergröße (z. B. Handy quer) |
| `python qc/run.py --selftest monza --quick` | baut absichtlich ein Loch und eine flimmernde Doppelfläche ein – der Bericht muss beides melden |
| `python qc/run.py --no-static` | ohne die Geometrie-Prüfungen (schneller) |
| `python qc/run.py --report 2026-11-12_23-14-50` | nur den Bericht eines früheren Laufs neu bauen (nach Änderungen am Bot, ohne neu zu fahren) |
| `python qc/run.py --list` | bekannte Strecken anzeigen |
| `python qc/run.py --changed` | nur Strecken, die sich seit ihrer letzten Prüfung geändert haben (siehe unten) |
| `python qc/run.py --changed --dry` | nur anzeigen, welche Strecken betroffen wären und warum |
| `python qc/run.py mc --at 2900-3100` | nur diesen Abschnitt (Streckenmeter) prüfen – dort alle 25 m mit Rundumblick |
| `python qc/run.py --accept` | aktuellen Stand als geprüft merken, ohne zu fahren (z. B. nach einer Prüfung von Hand) |

Braucht nur Python und Edge (oder Chrome, `--browser <Pfad>`). Neue Strecken werden automatisch erkannt.
Ein voller Lauf über alle Strecken dauert etwa 1,5–2 Stunden (eine Runde je Kamera, die Nordschleife allein rund 25 Minuten).

Robustheit: Während des Laufs hält `run.py` den Bildschirm wach. Friert Edge die unsichtbare Seite trotzdem ein (Energiesparen,
gesperrter Bildschirm), weckt `run.py` sie über das DevTools-Protokoll wieder auf (`.. Seite aufgeweckt` im Terminal).
Hängt eine Strecke länger als `--timeout` Sekunden (Standard 300), startet der Bot sie einmal neu und überspringt sie beim zweiten Mal.
Jeder Neustart steht im Bericht als Befund **hoch** („Seite ist abgestürzt“ bzw. „Seite hing“) mit der letzten bekannten Position.
Abgebrochene Läufe hinterlassen keine Edge-Prozesse: `run.py` beendet beim Start Reste früherer Läufe (Profile `f1qc-*`).

Ohne `run.py` geht es auch direkt im Browser, z. B. am Handy: `index.html?qc=monza&mode=quick`.
Der Bericht wird am Ende als HTML-Datei heruntergeladen.

## Nach Änderungen gezielt prüfen

**Welche Strecken (`--changed`):** Nach jedem vollen Lauf merkt sich `run.py` je Strecke, mit welchem Stand von `index.html`
sie geprüft wurde (`qc-reports/baseline/`). `--changed` vergleicht den aktuellen Stand damit – auch nicht committete Änderungen – und
prüft nur betroffene Strecken. Im Terminal steht je Strecke der Grund. Zugeordnet wird so (Logik in `qc/changed.py`):

1. Änderung im Eintrag der Strecke in `TRACKS`, ihrem Thema in `THEMES` (auch geerbt, z. B. `...THEMES.sil` für die Kartbahnen) oder `TREE_STYLE` → diese Strecke.
2. Merkmal der Strecke in der geänderten Zeile oder im umgebenden Block: `TRK.mc`, seltene Themen-Eigenschaften wie `TH.vegas`/`TH.night`,
   Datenkennung (`'mc-1929'`), eigene Datenkonstanten (`MEL_REF`, `NS_DATA`) → diese Strecken.
3. Sonst: allgemeiner Streckencode (z. B. in `buildTrack`, `hStrip`, `surface`) → **alle** Strecken; Auto, Menü, Musik, Versionsnummer → keine.

Nur `index.html` zählt. Wer Texturen oder andere Dateien einer Strecke ändert, gibt die Strecke von Hand an.
Abschnitts-, Selbsttest- und Berichtsläufe merken sich nichts; Strecken mit Abbruch („Seite hing“) auch nicht.

**Welche Stelle (`--at VON-BIS`):** Gilt für genau eine Strecke. Der Bot fährt die ganze Runde, prüft aber nur im Abschnitt –
dort alle 25 m (`--shot` ändert das) mit Rundumblick links/rechts/hinten/oben. Befunde außerhalb (±30 m) fallen weg, die
Ruckler-Statistik bleibt für die ganze Runde. Der Abschnitt darf über Start/Ziel laufen (`--at 5600-200`).
Die Streckenmeter stehen in jedem Befund des letzten Berichts.

Typischer Ablauf: Strecke ändern → `python qc/run.py --changed --dry` (was ist betroffen?) → `python qc/run.py mc --at 2900-3100`
für die geänderte Stelle → `python qc/run.py --changed` zum Abschluss (volle Runde, merkt sich den Stand).

## Was geprüft wird

**Während der Fahrt** (je Kamera: Verfolger, Hoch hinten, Cockpit, T-Cam):

- **Ruckler**: Zeit jedes einzelnen Bildes über die ganze Runde. Bilder über 50 ms zählen als Ruckler, über 100 ms als starke Ruckler.
  Stellen, die in mehreren Runden an derselben Stelle ruckeln, werden als *Ruckelstelle* mit Streckenmeter und Bild gemeldet.
  Die erste Runde wird getrennt ausgewiesen (dort werden Shader und Texturen beim ersten Anblick geladen).
- **Löcher**: Alle 300 m wird die Ansicht ohne Himmel neu gezeichnet. Bleibt unterhalb des Horizonts etwas leer, sieht man ins Nichts
  (magenta Kästen im Bild).
- **Z-Fighting**: Dieselbe Ansicht wird zusätzlich mit veränderter Kamera-Nahebene gezeichnet. Dadurch verschiebt sich kein Pixel,
  es ändert sich nur die Rundung im Tiefenpuffer. Wechselt ein Pixel dabei die Farbe, kämpfen dort zwei Flächen um den Vorrang
  (gelbe Kästen im Bild).
- **Rendering**: schwarze, einfarbige (Kamera steckt in einem Objekt) oder überbelichtete Bilder, WebGL-Fehler, Konsolenfehler, Shader-Fehler.
- **Rundumblick**: In der Verfolger-Runde wird an jeder zweiten Prüfstelle zusätzlich nach links, rechts, hinten und von oben geschaut.
- **Fahrbarkeit**: Bleibt das Bot-Auto stehen oder kommt es öfter von der Strecke ab, deutet das auf Kanten, Mauern oder eine falsche Ideallinie hin.

**Einmal nach dem Streckenbau**:

- Boden von oben (alle Bodenflächen kachelweise von oben gezeichnet): fehlender Boden innerhalb der Absperrung und bis 25 m daneben.
- Z-Fighting im Boden: zwei deckende Bodenflächen weniger als 2 cm übereinander (Strahlen von oben, alle 10 m quer über die Strecke).
- Geometrie mit ungültigen Werten (NaN), fehlende oder nicht geladene Texturen.
- Die vorhandenen Prüfhelfer `__holes`, `__clipAll`, `__onRoad`, `__bldOverlap`, `__clipCheck`.

## Bericht lesen

- Übersicht: eine Zeile je Strecke, Urteil **OK / Prüfen / Fehler**, Bildrate, p99 und Zahl der Befunde je Bereich.
- Je Strecke: Befunde mit Streckenmeter und Bild, Bildzeit-Kurve über die Runde (Farbe = Kamera), Tabelle je Kamera,
  statische Prüfungen und alle Prüfbilder je Kamera zum Durchblättern.
- Stufen: **hoch** = sichtbarer Fehler (Loch in der Absperrung, starke Ruckler, Shader-Fehler), **mittel** = prüfen,
  **info** = wahrscheinlich harmlos (z. B. leichtes Kantenflimmern am Fuß der Banden).
- Rohdaten pro Strecke liegen als `<strecke>.json` daneben, eine Kurzfassung aller Strecken in `summary.json`.

**Z-Fighting lesen:** Gelbe Kästen am Rand von Bodenstreifen (Rasen gegen Randstreifen oder Kies) bedeuten meist, dass eine Fläche
nur per `polygonOffset` nach hinten geschoben ist und knapp über der anderen liegt. Aus flachem Winkel und auf 10 m und mehr reicht
das nicht mehr, die Reihenfolge kippt und der Rand flimmert beim Fahren. Abhilfe: die untere Fläche einige Zentimeter tiefer legen
oder die obere an der Stelle aussparen.

**Messart der Bildzeiten:** Mit sichtbarem Fenster wird der echte Abstand zwischen zwei angezeigten Bildern gemessen.
Unsichtbar (Standard) oder bei gesperrtem Bildschirm zeichnet der Browser nicht von selbst; dann treibt der Bot das Spiel an
und misst die Rechenzeit je Bild, bis die Grafikkarte fertig ist. Beides zeigt Ruckler zuverlässig; die absolute Bildrate ist
nur mit `--show` mit dem echten Spiel vergleichbar. Der Bericht nennt die Messart je Strecke.

## Für neue Strecken

1. Strecke wie in `docs/STRECKEN-ANLEITUNG.md` einbauen.
2. `python qc/run.py <schlüssel> --quick` während des Bauens, `python qc/run.py <schlüssel>` zum Abschluss.
3. Alle Befunde **hoch** beheben, **mittel** ansehen. Ein Vergleich mit einer fertigen Strecke (z. B. `monza`) zeigt, was normal ist.

## Technik

- `qc/qc-bot.js` läuft im Spiel (geladen über `?qc=`), `qc/run.py` startet einen kleinen Server, Edge und sammelt Bilder und Bericht.
- Das Spiel stellt dafür `window.__qcApi` bereit (Ende von `index.html`) und ruft nach jedem gezeichneten Bild `window.__qcF` auf.
  Ohne `?qc` passiert nichts davon.
- Der Service Worker speichert `qc/` und `qc-reports/` nie zwischen.
- Zum Untersuchen von Hand: `index.html?qc=none` lädt nur die Werkzeuge (`window.__qcBot.topVoids()`, `.groundZFight()`, `.probe(camera)`, …).
