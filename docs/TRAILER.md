# Trailer „Formula Racing“

Stand 25.11.2026 · Fassung 2 (nach Rückmeldung zum Storyboard). Werkzeuge: `tools/trailer/` · Storyboard-Blätter der ersten Fassung: `docs/bilder/trailer_storyboard_1…3.jpg`.

**Privat:** Der fertige Trailer und alle Vorschauen enthalten geschützte Musik. Sie kommen **nicht ins Repository** (Ausgabeordner `trailer-ausgabe/`
steht in `.gitignore`), sondern gehen nur als Datei an den Nutzer. Im Repository liegen nur Skripte, Notizen und Bilder aus dem Spiel.

## Auftrag und Rückmeldungen

- **24.11.2026:** filmischer Spiel-Trailer nach dem Vorbild guter Spieletrailer, Musik aus der Renn-Playlist, das Spiel so schön wie möglich; zuerst Storyboard und Musikwahl.
- **25.11.2026 (Rückmeldung zum Storyboard):** MX-5 und „Grüne Hölle“ raus · bei Nr. 6 Singapur statt Monaco · im Regen auch Singapur und überhaupt Nachtstrecken im Regen ·
  in der Helmkamera ein kurzer, spannender Zweikampf · am Ende das F1-Logo aus dem Repository (`logos/LOGO.png`) · sehr filmisch · ohne weitere Abnahme rendern.
- **Musik:** zwischenzeitlich „Tate McRae – Just Keep Watching“ und „Höhepunkt früher“ gewünscht, dann zurückgenommen:
  **Hans Zimmer – „F1“ im ursprünglich vorgeschlagenen Schnitt und Tempo** (1:38).

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

## Ablauf (Fassung 2, 1:38, 24 Bilder/s, Kinoformat 2,39:1 in 1920 × 1080)

Quelle der Zeiten: `tools/trailer/schnittplan.json`, der Kameras: `tools/trailer/drehplan.js`.

| Zeit | Einstellung | Schauplatz | Schrift |
|---|---|---|---|
| 0:00–0:04 | Makrofahrt am Frontflügel, echte Schärfentiefe | Garage | – |
| 0:04–0:07,4 | Zufahrt auf Helm und Halo, Schärfe wandert | Garage | – |
| 0:07,4–0:10,85 | fünf rote Lichter gehen einzeln an, auf dem letzten Bild aus | Abu Dhabi, Dämmerung | – |
| 0:10,85–0:15,2 | Start: das Feld schießt an der bodennahen Kamera vorbei | Abu Dhabi | – |
| 0:15,2–0:19,6 | Profilfahrt im Gegenlicht, 60 % Tempo, echte Bewegungsunschärfe | Abu Dhabi | – |
| 0:19,6–0:24 | Kranfahrt über die Marina Bay | Singapur, Nacht | 24 GRAND-PRIX-STRECKEN |
| 0:24–0:28,3 | tiefe Mitfahrt, Riesenrad und Marina Bay Sands dahinter | Singapur | – |
| 0:28,3–0:33 | vier Schnitte im Takt: Helm in der Haarnadel, Tunnelausfahrt, Rad ganz nah, T-Kamera; dann Schwarz | Monaco | – |
| 0:33–0:37,4 | Silhouette vor der Sphere, 35 % Tempo | Las Vegas | TAG UND NACHT |
| 0:37,4–0:41,7 | T-Kamera auf dem Strip, Tempo-Effekt des Spiels | Las Vegas | – |
| 0:41,7–0:50,5 | sechs Legenden, gleiche Kamera, je 1,45 s, im Bildlook ihrer Zeit | Monza | Jahr und Auto (1967 … 2012) |
| 0:50,5–0:54,8 | Cockpit des MP4/4 auf die erste Schikane zu | Monza | – |
| 0:54,8–0:59,2 | bodennah im Bogen vor dem Kartfeld | Genk | VOM KART BIS IN DIE FORMEL 1 |
| 0:59,2–1:10,1 | **Zweikampf**: Helmkamera im Windschatten, ausscheren – ein Takt von außen Rad an Rad – Helmkamera, spät bremsen, innen vorbei | Monza | – |
| 1:10,1–1:14,5 | Nachtsprint, zwei Autos nebeneinander | Singapur | – |
| 1:14,5–1:19,3 | Zielgerade mit Feuerwerk, Kamera steigt | Singapur | – |
| 1:19,3–1:23,7 | Regen in Zeitlupe (45 %), Riesenrad, spiegelnde Fahrbahn | Singapur, Starkregen | BEI JEDEM WETTER |
| 1:23,7–1:26,3 | Strip im Regen, 50 % | Las Vegas, Starkregen | – |
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
- **Echte Schärfentiefe** (Garage): jedes Zwischenbild von einem anderen Punkt der Blende aus; gemittelt wird gleitend über die letzten 12 Zwischenbilder,
  so kostet ein Bild nur 3 statt 12 Zeichnungen.
- **Tempo-Unschärfe des Spiels** bei Mitfahrten von vorn und hinten (`speed`), aus bei seitlichen Kameras.
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

## Erste Fassung (Storyboard vom 24.11.2026)

19 Einstellungen mit Monaco aus der Luft, RONE-Roadster auf der Nordschleife und Titel „FORMULA RACING“; Blätter in `docs/bilder/trailer_storyboard_1…3.jpg`,
Inhalt in `tools/trailer/storyboard.json`. Die Standbilder dafür entstanden mit `studio.js` und `probe.sh`.
