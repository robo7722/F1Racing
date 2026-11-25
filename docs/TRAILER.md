# Trailer „Formula Racing“

Stand 25.11.2026 · Fassung 3 (nach Rückmeldung zum ersten fertigen Trailer). Werkzeuge: `tools/trailer/` · Storyboard-Blätter der ersten Fassung: `docs/bilder/trailer_storyboard_1…3.jpg`.

**Privat:** Der fertige Trailer und alle Vorschauen enthalten geschützte Musik. Sie kommen **nicht ins Repository** (Ausgabeordner `trailer-ausgabe/`
steht in `.gitignore`), sondern gehen nur als Datei an den Nutzer. Im Repository liegen nur Skripte, Notizen und Bilder aus dem Spiel.

## Auftrag und Rückmeldungen

- **24.11.2026:** filmischer Spiel-Trailer nach dem Vorbild guter Spieletrailer, Musik aus der Renn-Playlist, das Spiel so schön wie möglich; zuerst Storyboard und Musikwahl.
- **25.11.2026 (Rückmeldung zum Storyboard):** MX-5 und „Grüne Hölle“ raus · bei Nr. 6 Singapur statt Monaco · im Regen auch Singapur und überhaupt Nachtstrecken im Regen ·
  in der Helmkamera ein kurzer, spannender Zweikampf · am Ende das F1-Logo aus dem Repository (`logos/LOGO.png`) · sehr filmisch · ohne weitere Abnahme rendern.
- **Musik:** zwischenzeitlich „Tate McRae – Just Keep Watching“ und „Höhepunkt früher“ gewünscht, dann zurückgenommen:
  **Hans Zimmer – „F1“ im ursprünglich vorgeschlagenen Schnitt und Tempo** (1:38).

- **25.11.2026 (Rückmeldung zum ersten Trailer, Fassung 2):** Bild in der Garage zittert an den Rändern · Ampel viel zu schnell · bei 0:22 ein schönerer, filmischerer
  Singapur-Shot · in allen Nachtszenen schwarze Lichtkegel · Shots bei 0:28 und 0:29 ersetzen · Legenden im Takt schneiden · bei Häkkinen eiern die Reifentexturen
  (auch im Spiel beheben) · bei 1:08 wird die Schikane abgekürzt · bei 1:13 läuft der Windeffekt falsch herum (bei allen rückwärts blickenden Kameras entfernen) ·
  Zieleinlauf näher am Auto beginnen und flüssiger, höher steigen · die beiden Regen-Shots bei 1:23/1:24 passen nicht zusammen. Umsetzung: Abschnitt „Fassung 3“ unten.

## Musik

`music/Hans Zimmer - F1.mp3`, gemessen mit `tools/trailer/musik_analyse.py`: **110 BPM** (ein Schlag 0,5455 s, ein Takt 2,182 s), Tempo durchgehend gleich.

| Zeit im Stück | Was passiert | Nutzung im Trailer |
|---|---|---|
| 0:00–0:10,8 | fast Stille, schwillt an | Garage, Startampel |
| 0:10,85 | Thema setzt ein | **Lichter aus** |
| 0:19,6 / 0:28,3 | zweite Phrase / Anziehen | Singapur, Steigerung (Monaco) |
| 0:33,0 | voller Einsatz mit Schlagwerk | Las Vegas, Legenden, Kart, Zweikampf, Zielsprint |
| 2:09,5–2:21 | Musik bricht ab | Regen in Zeitlupe |
| 2:21,0 | Schlussteil setzt ein | **F1-Logo** |

Schnitt auf 1:38: `python3 tools/trailer/musik_schnitt.py <Vorlage.wav> <Ausgabe.wav> --teile 0:76.65,126.83:148.3 --aus 4.0`
(Teil 1 unverändert bis 1:16,65; dort auf einem Taktanfang weiter bei 2:06,83 im Stück, 40 ms Überblendung; Schlussakkord bei 1:30,8).
Die Schnittstelle ist **gemessen, nicht gehört**.

Geprüft und verworfen: Mad Max – Brothers in Arms (kein ruhiger Auftakt), Daft Punk – Derezzed, Eric Prydz – Opus (Aufbau zu lang), Royal Blood, Kx5.
„Tate McRae – Just Keep Watching“ (130 BPM, ein Takt 1,846 s; Refrain bei 0:39, Bruch bei 1:38, Schlussrefrain ab 2:00) war für einen frühen Höhepunkt
schon vermessen, wurde aber nicht verwendet.

**Geräusche** (`tools/trailer/ton.py`, nur vorhandene Spielklänge und gerechnetes Rauschen, keine Kosten): Ampel-Töne und Motoren in der Startaufstellung,
hochdrehende Motoren beim Start, dumpfe Schläge zum Feuerwerk, Regenrauschen im Regenteil. Gemischt nach Pegelmessung (Startaufstellung gleich laut wie die
dort sehr leise Musik, sonst 11–14 dB unter der Musik), **nicht nach Gehör**. Mit `--ohne` entsteht die reine Musikfassung.

Nebenbefunde in `music/` (nicht geändert): `Gesaffelstein - PURSUIT.mp3` ist nur 4 Byte groß; `Eric Prydz - Opus.mp3` und `Kx5 - Escape….mp3` sind WebM/Opus,
`Mad Max … Brothers In Arms.mp3` ist AAC in MP4 – nur die Endung heißt `.mp3`.

## Ablauf (Fassung 3, 1:38, 24 Bilder/s, Kinoformat 2,39:1 in 1920 × 1080)

Quelle der Zeiten: `tools/trailer/schnittplan.json`, der Kameras: `tools/trailer/drehplan.js`.

| Zeit | Einstellung | Schauplatz | Schrift |
|---|---|---|---|
| 0:00–0:02,9 | Makrofahrt am Frontflügel, echte Schärfentiefe | Garage | – |
| 0:02,9–0:05,3 | Zufahrt auf Helm und Halo, Schärfe wandert | Garage | – |
| 0:05,3–0:10,85 | fünf rote Lichter im Abstand von 0,95 s, 1,2 s halten, auf dem letzten Bild aus | Abu Dhabi, Dämmerung | – |
| 0:10,85–0:15,2 | Start: das Feld schießt an der bodennahen Kamera vorbei | Abu Dhabi | – |
| 0:15,2–0:19,6 | Profilfahrt im Gegenlicht, 60 % Tempo, echte Bewegungsunschärfe | Abu Dhabi | – |
| 0:19,6–0:24 | **Kran-Aufzug**: tief vor dem Auto beginnen, rückwärts auf 6,5 m steigen – Feld, Riesenrad, Skyline | Singapur, Nacht | 24 GRAND-PRIX-STRECKEN |
| 0:24–0:28,3 | tiefe Mitfahrt, Riesenrad und Marina Bay Sands dahinter | Singapur | – |
| 0:28,3–0:33 | vier Schnitte im Takt: Helmkamera der Sonne entgegen (Abu Dhabi), Vorbeiflug am Randstein (Singapur), Rad ganz nah und T-Kamera (Monaco); dann Schwarz | – | – |
| 0:33–0:37,4 | Silhouette vor der Sphere, 35 % Tempo | Las Vegas | TAG UND NACHT |
| 0:37,4–0:41,7 | T-Kamera auf dem Strip | Las Vegas | – |
| 0:41,7–0:48,3 | sechs Legenden, gleiche Kamera, **je zwei Schläge** (1,09 s), im Bildlook ihrer Zeit | Monza | Jahr und Auto (1967 … 2012) |
| 0:48,3–0:50,5 | dieselbe Kamera, das Auto von heute – ein Takt | Monza | 2026 · FERRARI |
| 0:50,5–0:54,8 | Cockpit des MP4/4 auf die erste Schikane zu | Monza | – |
| 0:54,8–0:59,2 | bodennah im Bogen vor dem Kartfeld | Genk | VOM KART BIS IN DIE FORMEL 1 |
| 0:59,2–1:10,1 | **Zweikampf**: Helmkamera im Windschatten, ausscheren – ein Takt von außen Rad an Rad – Helmkamera, spät bremsen; endet beim Einlenken | Monza | – |
| 1:10,1–1:14,5 | Nachtsprint, zwei Autos nebeneinander | Singapur | – |
| 1:14,5–1:19,3 | Zielgerade mit Feuerwerk: dicht hinter dem Heck beginnen, gleichmäßig auf 10 m steigen | Singapur | – |
| 1:19,3–1:23,7 | Regen in Zeitlupe (45 %), Riesenrad, spiegelnde Fahrbahn, Lichtkegel im Dunst | Singapur, Starkregen | BEI JEDEM WETTER |
| 1:23,7–1:26,3 | seitlich vor der Sphere, die sich auf der nassen Bahn spiegelt, 50 % | Las Vegas, Starkregen | – |
| 1:26,3–1:28,5 | Teleobjektiv frontal, Autos aus der Gischt, 50 % | Spa, Starkregen | – |
| 1:28,5–1:30,8 | Helmkamera, Tropfen auf dem Visier, ins Schwarz | Singapur, Starkregen | – |
| 1:30,8–1:38 | **F1-Logo** (`logos/LOGO.png`, scharf vergrößert) mit Zeile FORMULA RACING | Schlusstafel | – |

Gestaltung der Schrift: Titillium Web wie im Spiel, unten links, kursiv, gesperrt, roter Balken.

## So wird gerechnet

Am Spiel (`index.html`) ist **nichts geändert**. Die Werkzeuge laden das echte Spiel im Testbrowser und setzen nur dort vier Einhängepunkte ein
(`tools/trailer/spielstart.js`): Code-Auswertung im Modul, eigene Kamera mit Brennweite und Neigung, Haken vor dem Zeichnen, einstellbare Kantenglättung.

| Datei | Zweck |
|---|---|
| `spielstart.js` | Spiel starten, Rennen wechseln (Fahrer, Wetter, Klasse) ohne Neuladen |
| `studio.js` | Studio offen halten; Befehle über `localhost:<Port>/eval`, `/bild`, `/rennen`, `/ende` |
| `studio_spiel.js` | Helfer im Spiel (`TR.…`): feste Zeitbasis, Autos aufstellen, Kamerafahrten, Bildmittelung, Feuerwerk |
| `studio_showroom.js` | Garage (`TRS.…`): Kamera und echte Schärfentiefe |
| `drehplan.js` | alle Einstellungen: Vorbereitung, Kamerafahrt, Dauer, Zeitlupe |
| `dreh.js` | Einstellungen in einem Studio rechnen (`--probe`: vier Bilder in halber Auflösung als Kontaktblatt) |
| `schichten.js` / `schicht.js` | Warteschlangen: Studio starten, proben, rechnen, schließen – neustart-fest |
| `schnittplan.json` / `schnitt.py` | Schnitt im Takt, Schriften, Schlusstafel, Balken, Korn, Ton (`--vorschau` zeigt Fehlendes grau) |
| `schrift.js`, `logo_gross.py` | Schriften und Schlusstafel als Bild; Logo mit scharfen Kanten vergrößern |
| `ton.py` | Musik und Geräusche mischen |
| `musik_analyse.py`, `musik_schnitt.py`, `storyboard.*`, `animatic.py` | erste Fassung: Musikwahl, Storyboard, Vorschau aus Standbildern |

Ablauf für einen neuen Lauf:

```bash
for k in a b c; do nohup node tools/trailer/schicht.js $k 882$(echo $k | tr abc 123) > trailer-ausgabe/schicht_$k.log 2>&1 & done   # rechnet alles, überspringt Fertiges
python3 tools/trailer/logo_gross.py trailer-ausgabe/schrift/logo_gross.png && node tools/trailer/schrift.js trailer-ausgabe/schrift
python3 tools/trailer/ton.py <Musik.wav> <Ton.wav>
python3 tools/trailer/schnitt.py <Ton.wav> trailer-ausgabe/Formula_Racing_Trailer.mp4
```

### Was die Aufnahme filmisch macht

- **Feste Zeitbasis** (`TR.halt`, `TR.takt`): Die Bildschleife des Spiels steht, `performance.now` läuft auf einer eigenen Uhr. Jedes Bild ist exakt 1/24 s Spielzeit,
  Zeitlupe ist einfach ein kleinerer Schritt, der Zufall ist je Einstellung festgelegt (`TR.seed`) – eine Einstellung läuft jedes Mal gleich ab.
- **Kamerafahrten** (`TR.kam(a, b)`): zwei Kamera-Angaben (am Auto, an der Strecke oder in der Welt), dazwischen wird Bild für Bild überblendet; dazu leichte Handkamera-Unruhe.
- **Echte Bewegungsunschärfe** (Profilfahrt): je Bild vier Zwischenbilder über 60 % der Bildzeit, im linearen Licht gemittelt.
- **Echte Schärfentiefe** (Garage): zwölf feste Blendenpunkte auf zwei Ringen; je Bild sechs davon (ein Dreieck innen, eines außen), im nächsten Bild die um 60° gedrehten;
  gemittelt wird über zwei Bilder. Ein Bild kostet so 6 statt 12 Zeichnungen (siehe „Fassung 3“ zum Zittern der ersten Lösung).
- **Tempo-Unschärfe des Spiels** bei Mitfahrten von vorn und hinten (`speed`), aus bei seitlichen Kameras. Die **Luftstreifen** des Spiels sind bei eigenen Kameras immer aus
  (sie fliegen in Fahrtrichtung an der Kamera vorbei – bei rückwärts blickenden Kameras also falsch herum).
- **Feuerwerk gezielt** (`TR.feuerwerk`, `TR.fwLauf`): dieselben Teilchen wie im Spiel, aber dort gezündet, wo die Kamera hinsieht (120–280 m voraus, 50–100 m hoch).
- Schnitt auf den Takt, Kinoformat mit schwarzen Balken, feines Filmkorn nur im Bild.

### Gemessene Rechenzeiten (Testbrowser ohne Grafikkarte, 4 Kerne, „Ultra“, 1920 × 804)

| Was | Zeit |
|---|---|
| Strecke bauen bis „Rennen läuft“ | 76–275 s |
| ein Bild, Singapur trocken, ein Studio allein | 5,1 s (davon Szene 2,1 s, Umgebungsverdeckung 1,0 s, Schatten 0,7 s, Bloom 0,3 s, Sonnenstrahlen 0,3 s) |
| Kantenglättung an/aus | kein messbarer Unterschied (5,1 s gegen 5,7 s) |
| zwei Studios gleichzeitig | je 8,9–9,1 s (zusammen 1,5-mal so schnell wie eines) |
| drei Studios gleichzeitig | je 11,9–13,4 s (zusammen 1,6-mal so schnell) |
| Garage, ein Bild 1920 × 1080 | 3,8 s |
| Fahrer wechseln in derselben Sitzung (Legende) | etwa 115 s |

Deshalb: 24 Bilder/s, drei Studios gleichzeitig, Umgebungsverdeckung nur in ruhigen Einstellungen, Sonnenstrahlen-Durchgang nachts aus (dort ohne Wirkung).

### Ergebnis des Laufs vom 25.11.2026

- 28 Einstellungen, 2.354 Trailerbilder; gerechnet von 01:13 bis 03:46 Uhr (2 h 33 min) in drei gleichzeitigen Warteschlangen, ohne Fehler.
  Am längsten dauerten die Profilfahrt mit vierfacher Belichtung (rund 35 s je Bild), der Zweikampf (264 Bilder) und die Garage (drei Zeichnungen je Bild).
- Schnitt: `schnitt.py` braucht einige Minuten. Mit Filmkorn und ohne Obergrenze wurde die Datei 600 MB groß (49 Mbit/s) –
  deshalb `--crf 18 --maxrate 12M` für die Fassung zum Verschicken.
- Ton: mittlere Lautstärke −18,2 dB, Spitze −0,4 dB. Zusätzlich gibt es eine Fassung nur mit Musik (ohne Geräusche).

### Was schiefging (nicht wiederholen)

- **Vier Studios gleichzeitig** (Last 16, 10 GB belegt): Um 01:10 Uhr startete der Rechner neu, alle laufenden Einstellungen waren weg. Seitdem höchstens drei,
  und die Warteschlangen (`schicht.js`) überspringen fertige Einstellungen und setzen angefangene fort.
- **Kamera relativ zum Auto an Steigungen**: lag unter der Straße – `TR.rel` nimmt die Fahrbahnhöhe an der Kamerastelle.
- **Kamera seitlich neben dem Auto**: stand zweimal hinter der Bande (Abu Dhabi) bzw. hinter der Betonwand (Las Vegas im Regen). Auto auf die andere Fahrbahnseite legen
  (`pl.ovr`) und höchstens 5 m Abstand nehmen.
- **Zweikampf** (drei Fehlversuche): Die KI hält hinter einem Auto rund 35 m Abstand – das Tempo des eigenen Autos wird deshalb je Bild vorgegeben, samt Ausgleich für das,
  was die KI wegbremst. Unter 7,1 m Abstand hält die KI beide Autos seitlich auseinander, dann kommt man nicht mehr auf die andere Seite – also erst ausscheren, dann aufschließen.
  Unter etwa 2,3 m seitlichem Abstand berühren sich die Autos und beide bremsen stark; der Gegner bekommt deshalb eine feste Spur 3,5 m daneben.
- **Nachtregen ist sehr dunkel**: von hinten in der Gischt war fast nichts zu sehen. Gewählt wurden Einstellungen von vorn mit beleuchteter Kulisse, im Schnitt um 22 % aufgehellt.
- **Feuerwerk des Spiels** liegt 200–400 m voraus und wirkt klein; erst das gezielte Zünden füllt den Himmel. Zu nah (60–170 m) überstrahlt es das Bild.
- `xstack` von ffmpeg stürzte bei acht Bildern ab – Kontaktblätter jetzt mit `concat` + `tile`.

## Fassung 3: was nach der Rückmeldung geändert wurde (25.11.2026)

| Rückmeldung | Ursache | Lösung |
|---|---|---|
| Garage zittert an den Rändern | Die Schärfentiefe lief als fester 12er-Umlauf der Blendenpunkte über vier Bilder; der Schwerpunkt der Blende wanderte im 4-Bilder-Takt (gemessen: Bildänderung am Rand schwankte ±12 % mit Periode 4) | je Bild zwei Dreiecke von Blendenpunkten (Schwerpunkt in der Mitte, Streuung in alle Richtungen gleich), gleiche Kamerastellung für alle sechs Zwischenbilder. Zwischenversuch mit Vierergruppen ließ ±6 % im 3-Bilder-Takt übrig |
| Ampel viel zu schnell | Lichter alle 0,5 s, weil die Einstellung nur 3,45 s lang war | Garage auf 5,25 s gekürzt, Ampel 5,6 s lang, Lichter alle 0,95 s wie im Spiel |
| Singapur-Shot bei 0:22 | Luftaufnahme zeigte die einfache Stadt von oben | Kran-Aufzug auf Streckenhöhe mit Riesenrad und Skyline (aus sieben Proben gewählt) |
| schwarze Lichtkegel in allen Nachtszenen | **Fehler im Spiel auf „Ultra“**: die Umgebungsverdeckung behandelte Lichtkegel und Lichtflecken als feste Körper | im Spiel behoben (v3.02, siehe [[LEISTUNG-ANLEITUNG]]); alle Nachtszenen neu gerechnet – jetzt helle Strahlen und beleuchtete Fahrbahn |
| Shots bei 0:28 und 0:29 ersetzen | Monaco-Helmkamera und Tunnelausfahrt | Helmkamera der Sonne entgegen (Abu Dhabi) und Vorbeiflug am Randstein (Singapur) |
| Legenden im Takt | 4 Takte durch 6 Autos = 2,67 Schläge je Auto | je 2 Schläge, danach ein Takt für das Auto von 2026 |
| Reifen bei Häkkinen eiern | eingebackene helle Flecken auf der Reifenflanke des MP4/13 | im Spiel behoben (v3.02, siehe [[KLASSIKER]]) |
| Schikane bei 1:08 abgekürzt | zu starkes Spätbremsen (3,3 m über dem Rand); auch ohne Eingriff fährt die KI dort 1,5 m über den inneren Randstein | Zweikampf 140 m früher beginnen, Einstellung endet beim Einlenken (s ≈ 593); Windschatten-Abstand 8,8 m, sonst klappte das Ausscheren nicht jedes Mal |
| Windeffekt läuft bei 1:13 falsch herum | Luftstreifen des Spiels bei rückwärts blickender Kamera | Luftstreifen bei allen eigenen Kameras aus; betroffene Einstellungen neu gerechnet |
| Zieleinlauf näher beginnen, flüssiger und höher | Start 6,5 m hinter dem Auto, Anstieg nur bis 1,7 m, mit Beschleunigen und Abbremsen | Start 3,3 m hinter dem Heck, gleichmäßig bis 10,5 m |
| Regen-Shots 1:23/1:24 passen nicht | zweimal dieselbe Kameraidee (nah von vorn) hintereinander | Las Vegas jetzt seitlich vor der Sphere, die sich auf der nassen Bahn spiegelt (Kamera diesmal innerhalb der Mauer) |

Lauf der Fassung 3: 19 Einstellungen neu gerechnet (08:11–10:00 Uhr, drei gleichzeitige Läufe, ohne Fehler), die Garage danach noch zweimal (je rund 20 min),
bis die Nachmessung kein Flimmern mehr zeigte (Abweichung der Bildänderung am Rand 0,5–2,3 % ohne festen Takt). Dateien: `trailer-ausgabe/Formula_Racing_Trailer_v3.mp4`
und `…_v3_nur_Musik.mp4` (je 134 MB) – nur beim Nutzer, nicht im Repository.

## Erste Fassung (Storyboard vom 24.11.2026)

19 Einstellungen mit Monaco aus der Luft, RONE-Roadster auf der Nordschleife und Titel „FORMULA RACING“; Blätter in `docs/bilder/trailer_storyboard_1…3.jpg`,
Inhalt in `tools/trailer/storyboard.json`. Die Standbilder dafür entstanden mit `studio.js` und `probe.sh`.
