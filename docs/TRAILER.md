# Trailer „Formula Racing“ – Storyboard und Musikwahl

Stand 24.11.2026 · **wartet auf Abnahme** (Storyboard und Musik zuerst, gebaut wird der Trailer erst nach dem Go).
Werkzeuge: `tools/trailer/` · Bilder: `docs/bilder/trailer_storyboard_1…3.jpg`, Einzelbilder in `docs/bilder/trailer/`.

## Auftrag (24.11.2026)

Ein filmischer Spiel-Trailer nach dem Vorbild guter Spieletrailer, mit passender Musik aus dem Spiel („eine lizenzierte“ –
verstanden als: eines der bekannten Lieder aus der Renn-Playlist, nicht die lizenzfreien Titel). Der Trailer bleibt privat beim Nutzer.
Das Spiel soll so schön wie möglich aussehen. Zuerst Storyboard und Musikwahl zur Abnahme.

**Wichtig, weil privat:** Der fertige Trailer und die Vorschau mit Musik enthalten geschützte Musik. Sie kommen **nicht ins Repository**
(nur als Datei an den Nutzer; Ausgabeordner `trailer-ausgabe/` steht in `.gitignore`). Im Repository liegen nur Skripte, Notizen und Bilder aus dem Spiel.

## Was von guten Spieletrailern übernommen wird

(Aus meiner Kenntnis der Trailer von Gran Turismo 7, Forza Horizon 5 und der F1-Reihe sowie des Trailers zum F1-Film – nicht neu recherchiert.)

- **Ruhiger Auftakt mit Nahaufnahmen** statt sofort Action: Lack, Karbon, Helm – mit geringer Schärfentiefe.
- **Ein klarer Wendepunkt**: Die Startampel geht aus, genau auf dem ersten Schlag der Musik.
- **Schnitt im Takt**: Jede Einstellung dauert ganze Takte (2,18 s) oder halbe; in der Steigerung zwei Schläge je Schnitt.
- **Wenige, kurze Schriften im Bild** mit den Kernaussagen statt Sprecher.
- **Abwechslung der Schauplätze**: Dämmerung, Tag, Nacht, Regen; modern, historisch, Kart, Roadster.
- **Atempause vor dem Titel**: nach dem lautesten Teil ein ruhiges, schönes Bild (Regen in Zeitlupe), dann der Titel auf dem Schlussakkord.
- **Kinoformat 2,39:1**, echte Bewegungsunschärfe, keine Bedienelemente im Bild.

## Musik

### Wahl: Hans Zimmer – „F1“ (`music/Hans Zimmer - F1.mp3`, 3:14)

Gemessen mit `tools/trailer/musik_analyse.py` (librosa): **110 BPM** (ein Schlag 0,5455 s, ein Takt 2,18 s), Tempo über das ganze Stück gleich.

| Zeit im Stück | Lautstärke (rel.) | Was passiert | Nutzung im Trailer |
|---|---|---|---|
| 0:00–0:10,8 | −60 … −28 dB | fast Stille, schwillt an | Garage, Startampel |
| 0:10,85 | Sprung auf −11 dB | Thema setzt ein | **Lichter aus** |
| 0:19,6 / 0:28,3 | −11 … −15 dB | zweite Phrase / Anziehen | Monaco, Steigerung |
| 0:33,0 | −7 dB | voller Einsatz mit Schlagwerk | Las Vegas, Legenden, Vielfalt, Zielsprint |
| 2:09,5–2:21 | fällt auf −20 dB | Musik bricht ab | Regen in Zeitlupe |
| 2:21,0 | Sprung auf −10 dB | Schlussteil setzt ein | **Titel** |

Warum dieses Stück: Es ist die Musik des F1-Films, also genau für solche Bilder geschrieben; es hat den für Trailer idealen Bogen
(Stille → Einsatz → volle Kraft → Abbruch → Schlussakkord), und das feste Tempo macht taktgenaue Schnitte möglich.

### Schnitt auf Trailerlänge (1:38)

`tools/trailer/musik_schnitt.py <Vorlage.wav> <Ausgabe.wav> --teile 0:76.65,126.83:148.3 --aus 4.0`

- Teil 1: 0:00–1:16,65 unverändert (Auftakt, Thema, 20 Takte volle Kraft).
- Schnittstelle bei 1:16,65 auf einem Taktanfang, weiter bei 2:06,83 im Stück (gleiche Taktlage, 40 ms Überblendung): noch gut ein Takt volle Kraft, dann der Abbruch.
- Schlussakkord im Trailer bei 1:30,8, ausgeblendet bis 1:38,1.
- Ob die Schnittstelle sauber klingt, ist **nur gemessen, nicht gehört** – bitte in der Vorschau bei 1:16–1:20 hinhören.

### Geprüfte Alternativen aus der Playlist

| Lied | Tempo | Verlauf | Urteil |
|---|---|---|---|
| Mad Max – Brothers in Arms | 108 BPM | von Anfang an laut, kein ruhiger Auftakt | wuchtig, aber düster; zweite Wahl |
| Daft Punk – Derezzed | 117 BPM | 20 s Aufbau, voller Einsatz erst bei 1:10 | elektronisch, weniger „Kino“ |
| Eric Prydz – Opus | 123 BPM | steigt 3:45 lang an | Aufbau viel zu lang für 1:30 |
| Royal Blood – Figure It Out | 108 BPM | Rock, starker Einsatz bei 1:32 | Gesang lenkt ab |
| Tate McRae – Just Keep Watching | 129 BPM | Pop mit Gesang | passt zum Film, nicht zu Zeitlupen |
| Kx5 – Escape | 123 BPM | Gesang, Drop bei 3:05 | Club statt Kino |

### Nebenbefunde in `music/` (nicht geändert)

- `Gesaffelstein - PURSUIT.mp3` ist nur **4 Byte** groß, also keine abspielbare Datei.
- `Eric Prydz - Opus.mp3` und `Kx5 - Escape (feat. Hayla).mp3` sind in Wahrheit WebM/Opus, `Mad Max … Brothers In Arms.mp3` ist AAC in MP4 –
  nur die Endung heißt `.mp3`. Ob das auf jedem Gerät abspielt, ist nicht geprüft.

## Storyboard (19 Einstellungen, 1:38)

Die Standbilder sind **echte Bilder aus dem Spiel** (Grafik „Ultra“, 1920 × 804, ohne Bedienelemente), aufgenommen mit `tools/trailer/studio.js`.
Blätter: `docs/bilder/trailer_storyboard_1.jpg` (1–7), `_2.jpg` (8–13), `_3.jpg` (14–19). Quelle der Texte und Zeiten: `tools/trailer/storyboard.json`.

| Nr. | Zeit | Einstellung | Schauplatz | Schrift im Bild |
|---|---|---|---|---|
| 1 | 0:00–0:04 | Licht auf Karbon: Makrofahrt am Frontflügel, unscharfe LED-Wand | Garage (Showroom) | – |
| 2 | 0:04–0:07,4 | Der Fahrer wartet: Zufahrt auf Helm und Halo | Garage | – |
| 3 | 0:07,4–0:10,85 | Fünf rote Lichter: Tele über die Startaufstellung | Abu Dhabi, Dämmerung | – |
| 4 | 0:10,85–0:15,2 | Lichter aus: Feld schießt über die bodennahe Kamera | Abu Dhabi | – |
| 5 | 0:15,2–0:19,6 | Goldene Stunde: Mitzieher von der Seite im Gegenlicht | Abu Dhabi | – |
| 6 | 0:19,6–0:24 | Monaco von oben: Kranfahrt über den Hafen | Monaco | 24 GRAND-PRIX-STRECKEN |
| 7 | 0:24–0:28,3 | Zwischen den Leitplanken: tiefe Mitfahrt | Monaco | – |
| 8 | 0:28,3–0:33 | Steigerung: 4 Schnitte im Takt, letzter Schlag schwarz | Monaco (Helmkamera, Nahaufnahmen) | – |
| 9 | 0:33–0:37,4 | Silhouette vor der Sphere | Las Vegas, Nacht | TAG UND NACHT |
| 10 | 0:37,4–0:41,7 | 326 km/h auf dem Strip, T-Kamera | Las Vegas | – |
| 11 | 0:41,7–0:50,5 | Sechs Legenden: gleiche Kamera, 6 Schnitte, je im Bildlook der Zeit | Monza | SECHS LEGENDEN · 1967 – 2012 |
| 12 | 0:50,5–0:54,8 | Im Cockpit von 1988 (MP4/4, Fernsehlook) | Monza | – |
| 13 | 0:54,8–0:59,2 | Wo alles beginnt: bodennah vor dem Kartfeld | Genk | VOM KART BIS IN DIE FORMEL 1 |
| 14 | 0:59,2–1:03,6 | Grüne Hölle: RONE Racing #666 | Nordschleife | – |
| 15 | 1:03,6–1:10,1 | Rad an Rad: 3 Schnitte (Zweikampf, Windschatten, Überholen) | Monaco, Las Vegas | – |
| 16 | 1:10,1–1:19,3 | Zielsprint mit Feuerwerk, Kamera steigt auf | Las Vegas, Nacht | – |
| 17 | 1:19,3–1:25 | Regen in Zeitlupe (50 %): Tele frontal, Autos aus der Gischt | Spa, Starkregen | BEI JEDEM WETTER |
| 18 | 1:25–1:30,8 | Tropfen auf dem Visier, Helmkamera, ins Schwarz | Spa | – |
| 19 | 1:30,8–1:38 | Titel: FORMULA RACING · „Vom Kart bis in die Formel 1“ | Schrifttafel | – |

**Gestaltung der Schrift (Entwurf):** Titillium Web wie im Spiel; Schriften im Bild unten links, kursiv, gesperrt, mit rotem Balken;
Titel weiß auf Schwarz mit roter Linie. Kein F1-Logo im Trailer, nur der Spielname.

**Ton:** Musik im Vordergrund. Dazu aus den vorhandenen Spielklängen: Ampel-Töne und hochdrehende Motoren vor dem Start, Vorbeifahrten,
Regen. Keine neuen ElevenLabs-Erzeugungen eingeplant (kostet nichts). Kein Sprecher.

## Vorschau mit Musik (Animatic)

`python3 tools/trailer/animatic.py <Bilderordner> <Musik.wav> <Ausgabe.mp4>` schneidet die Standbilder im geplanten Rhythmus zur
geschnittenen Musik (1280 × 720, 1:38). Einstellungen mit mehreren Schnitten springen im Takt zwischen Bildausschnitten.
Die Datei geht nur an den Nutzer, nicht ins Repository.

## Technik

### Werkzeuge (`tools/trailer/`)

| Datei | Zweck |
|---|---|
| `musik_analyse.py` | Tempo, Lautheitsverlauf und Einsätze eines Liedes messen |
| `musik_schnitt.py` | Abschnitte taktgenau aneinanderfügen, ausblenden, Verlauf als JSON |
| `studio.js` | Spiel im Testbrowser starten, Strecke bauen, offen halten; Befehle über `localhost:<Port>/eval` und `/bild` |
| `studio_spiel.js` | Helfer im Spiel (`TR.…`): Autos aufstellen, eigene Kamera mit Brennweite, Schärfentiefe und Bewegungsunschärfe durch Mitteln vieler Bilder |
| `studio_showroom.js` | dasselbe für die Garage im Hauptmenü (`TRS.…`) |
| `probe.sh`, `hol.sh`, `blatt.sh` | Probebild aufnehmen, gemitteltes Bild holen, Kontaktblatt bauen |
| `storyboard.json` / `storyboard.js` | Inhalt des Storyboards / Blätter und Animatic-Bilder daraus erzeugen |
| `animatic.py` | Vorschau-Video aus Standbildern und Musik |

Am Spiel (`index.html`) wurde **nichts geändert**. `studio.js` setzt beim Laden im Testbrowser drei Einhängepunkte ein:
Code-Auswertung im Modul, feste Kamera mit Brennweite und Neigung (`window.__camFix` darf eine Funktion sein), Haken vor dem Zeichnen (`window.__trPre`).

Beispiel:

```bash
node tools/trailer/studio.js --port 8801 --strecke Spa --wetter heavy --fahrer VER &
tools/trailer/probe.sh 8801 bild.jpg "TR.start(); TR.feld(1150, 0, [[-11, 2.4], [-23, -2.2]]); TR.sim(45, 33); TR.cam({ von: { s: 1400, lat: -0.6, h: 0.6 }, auf: [0, 0.55, 0], fov: 6.5 })"
curl -s localhost:8801/ende
```

Kamera: `von`/`auf` als `[rechts, hoch, vor]` relativ zum Auto, als `{ s, lat, h }` an der Strecke oder als `[x, y, z, 0]` in Weltkoordinaten; `fov` in Grad.
`TR.halt()` stoppt die Bildschleife des Spiels (sonst läuft das Rennen zwischen zwei Befehlen weiter); `TR.skala(0.5)` halbiert die Auflösung für schnelle Proben.

### Gemessene Rechenzeiten (Testbrowser ohne Grafikkarte, 4 Kerne, Grafik „Ultra“)

| Was | Zeit |
|---|---|
| Strecke bauen bis „Rennen läuft“ | 130–240 s (Nordschleife 240 s, Kartbahn 137 s) |
| ein Bild 1920 × 804, Spa im Starkregen | 5,96 s |
| ein Bild 1920 × 804, Nordschleife trocken | 6,45 s |
| ein Bild 1280 × 536, Nordschleife trocken | 4,21 s |
| ein Bild Garage 1920 × 1080 | 3,84 s |

Der Trailer hat 2.943 Bilder (98,1 s × 30). **Schätzung** (nicht gemessen): mit einem Bild je Trailerbild etwa 5 Stunden Rechenzeit,
mit echter Bewegungsunschärfe (mehrere Zwischenbilder) ein Mehrfaches. Deshalb zwei Wege:

1. **Hier in der Cloud** rechnen, Einstellung für Einstellung im Hintergrund; echte Bewegungsunschärfe und Schärfentiefe nur dort, wo sie am meisten bringen (Garage, Mitzieher, Zeitlupe).
2. **Auf dem PC des Nutzers** (mit Grafikkarte, über Remote Control): das Spiel läuft dort in Echtzeit, dann sind Bewegungsunschärfe überall und höhere Auflösung möglich.

### Erfahrungen aus den Probeaufnahmen (für die Umsetzung)

- Am besten sieht das Spiel **nah am Auto** aus (Mitfahrten, Helm- und T-Kamera), in der **Garage**, bei **Nacht** und im **Regen**.
  Lange Brennweiten von der Tribüne zeigen die einfache Umgebung (Bäume, Häuser) – vermeiden.
- Kamera relativ zum Auto braucht die **Fahrbahnhöhe an der Kamerastelle** (an der Steigung von Eau Rouge lag sie sonst unter der Straße) – in `TR.rel` gelöst.
- Die Tempo-Unschärfe und die starke Vignette des Spiels hängen an der Geschwindigkeit; für Außenkameras stellt `window.__trPre` sie ab (`TR.speed = 0`).
- Namensschilder über den Autos werden ausgeblendet (`TR.labels = false`).
- Startampel: `raceState = 'lights'; SG.on = false; lightsOut = 99; lightsT = 4.85` hält fünf rote Lampen; `lightsOut = 0` startet.
- Feuerwerk: `pl.lapsDone = S.laps - 1` und das Auto auf die letzten 700 m setzen; es braucht einige Sekunden Vorlauf und wirkt nur mit weitem Blick nach oben.
- Legenden: Fahrer `SEN`, `RIN`, `MSC`, `AMO`, `HAK`, `VET` wählen – der Bildfilter der Epoche kommt von selbst. Je Legende ein eigener Start des Studios.
- Die Einstellung „Lichter aus“ (Nr. 4) ist im Standbild noch zu weit weg – in der Umsetzung näher an die erste Reihe.

## Offen bis zur Abnahme

- Musik und Schnittstelle (1:16–1:20) in Ordnung?
- Reihenfolge und Auswahl der Einstellungen, Texte der Schriften, Titel.
- Wo gerechnet wird (Cloud oder PC des Nutzers).
