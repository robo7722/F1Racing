# Trailer „Formula Racing“

Stand 25.11.2026 · Fassung 4 (nach der zweiten Rückmeldung zum fertigen Trailer; Fassung 3 siehe unten). Werkzeuge: `tools/trailer/` · Storyboard-Blätter der ersten Fassung: `docs/bilder/trailer_storyboard_1…3.jpg`.

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
- **25.11.2026 (Rückmeldung zu Fassung 3):** die zweite Sphere-Einstellung (im Regen) ist schlecht · mehr Regen zeigen, „der sieht hübsch aus, gerade in der Helmansicht“ ·
  manche Kamerafahrten sind zu hakelig, nicht flüssig genug – auch die Autobewegungen beim Lenken sollen weicher sein · bei Häkkinen eiern die Räder immer noch ·
  der Feuerwerks-Shot gehört ans Ende. Umsetzung: Abschnitt „Fassung 4“ unten; die Räder: `docs/KLASSIKER.md`, v3.03.

## Musik

`music/Hans Zimmer - F1.mp3`, gemessen mit `tools/trailer/musik_analyse.py`: **110 BPM** (ein Schlag 0,5455 s, ein Takt 2,182 s), Tempo durchgehend gleich.

| Zeit im Stück | Was passiert | Nutzung im Trailer |
|---|---|---|
| 0:00–0:10,8 | fast Stille, schwillt an | Garage, Startampel |
| 0:10,85 | Thema setzt ein | **Lichter aus** |
| 0:19,6 / 0:28,3 | zweite Phrase / Anziehen | Singapur, Steigerung (Monaco) |
| 0:33,0 | voller Einsatz mit Schlagwerk | Las Vegas, Legenden, Kart, Zweikampf, Zielsprint |
| 2:09,5–2:21 | Musik bricht ab | Regen in Zeitlupe, Regen aus dem Helm, dann der Zielsprint als Anlauf |
| 2:21,0 | Schlussteil setzt ein | **Zieleinlauf mit Feuerwerk** (bis Fassung 3: F1-Logo) |
| 2:25,4 | zwei Takte später, wieder lauter | **F1-Logo** |

Schnitt auf 1:42 (Fassung 4): `python3 tools/trailer/musik_schnitt.py <Vorlage.wav> <Ausgabe.wav> --teile 0:76.65,126.83:151.95 --aus 4.0`
(Teil 1 unverändert bis 1:16,65; dort auf einem Taktanfang weiter bei 2:06,83 im Stück, 40 ms Überblendung; Schlussakkord bei 1:30,8; Fassung 3 endete bei 148,3 = 1:38).
Nach dem Schlussakkord läuft das Stück weiter (Pegel je halbe Sekunde gemessen: Akkord −19 dB, kurze Senke, ab zwei Takte später −17 dB) – dort sitzt jetzt das Logo.
Die Schnittstelle ist **gemessen, nicht gehört**.

Geprüft und verworfen: Mad Max – Brothers in Arms (kein ruhiger Auftakt), Daft Punk – Derezzed, Eric Prydz – Opus (Aufbau zu lang), Royal Blood, Kx5.
„Tate McRae – Just Keep Watching“ (130 BPM, ein Takt 1,846 s; Refrain bei 0:39, Bruch bei 1:38, Schlussrefrain ab 2:00) war für einen frühen Höhepunkt
schon vermessen, wurde aber nicht verwendet.

**Geräusche** (`tools/trailer/ton.py`, nur vorhandene Spielklänge und gerechnetes Rauschen, keine Kosten): Ampel-Töne und Motoren in der Startaufstellung,
hochdrehende Motoren beim Start, Regenrauschen im Regenteil (1:10–1:26), dumpfe Schläge zum Feuerwerk (1:31–1:35). Gemischt nach Pegelmessung (Startaufstellung gleich laut wie die
dort sehr leise Musik, sonst 11–14 dB unter der Musik), **nicht nach Gehör**. Mit `--ohne` entsteht die reine Musikfassung.

Nebenbefunde in `music/` (nicht geändert): `Gesaffelstein - PURSUIT.mp3` ist nur 4 Byte groß; `Eric Prydz - Opus.mp3` und `Kx5 - Escape….mp3` sind WebM/Opus,
`Mad Max … Brothers In Arms.mp3` ist AAC in MP4 – nur die Endung heißt `.mp3`.

## Ablauf (Fassung 4, 1:42, 30 Bilder/s, Kinoformat 2,39:1 in 1920 × 1080)

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
| 0:59,2–1:10,1 | **Zweikampf**: Helmkamera im Windschatten, weich ausscheren – ein Takt von außen Rad an Rad – Helmkamera, spät bremsen; endet beim Einlenken | Monza | – |
| 1:10,1–1:14,5 | **Helmkamera im Regen**, hinter drei Autos in der Gischt, Tribünen im Flutlicht | Singapur, Starkregen | BEI JEDEM WETTER |
| 1:14,5–1:16,65 | Teleobjektiv frontal, Autos aus der Gischt, 50 % | Spa, Starkregen | – |
| 1:16,65–1:19,3 | **Helmkamera im Regen** durch Eau Rouge: Randsteine, Tropfen auf dem Visier, Gischt | Spa, Starkregen | – |
| 1:19,3–1:23,7 | Regen in Zeitlupe (45 %), Riesenrad, spiegelnde Fahrbahn, Lichtkegel im Dunst (Musik bricht ab) | Singapur, Starkregen | – |
| 1:23,7–1:26,4 | **Helmkamera im Regen**, Tropfen auf dem Visier | Singapur, Starkregen | – |
| 1:26,4–1:30,8 | Nachtsprint, zwei Autos nebeneinander – Anlauf auf den Schlussakkord | Singapur | – |
| 1:30,8–1:35,2 | **Zieleinlauf mit Feuerwerk** auf dem Schlussakkord: dicht hinter dem Heck beginnen, gleichmäßig auf 10 m steigen | Singapur | – |
| 1:35,2–1:41,8 | **F1-Logo** (`logos/LOGO.png`, scharf vergrößert) mit Zeile FORMULA RACING | Schlusstafel | – |

Gestaltung der Schrift: Titillium Web wie im Spiel, unten links, kursiv, gesperrt, roter Balken.

## So wird gerechnet

Am Spiel (`index.html`) ist für den Trailer **nichts geändert**. Die Werkzeuge laden das echte Spiel im Testbrowser und setzen nur dort Einhängepunkte ein
(`tools/trailer/spielstart.js`): Code-Auswertung im Modul, eigene Kamera mit Brennweite und Neigung, Haken vor dem Zeichnen, einstellbare Kantenglättung –
und seit Fassung 4 vier Änderungen an der KI-Lenkung (stufenloser Zielpunkt, weiches Lenkrad, weiches Querziel), siehe „Fassung 4“.

| Datei | Zweck |
|---|---|
| `spielstart.js` | Spiel starten, Rennen wechseln (Fahrer, Wetter, Klasse) ohne Neuladen |
| `studio.js` | Studio offen halten; Befehle über `localhost:<Port>/eval`, `/bild`, `/rennen`, `/ende` |
| `studio_spiel.js` | Helfer im Spiel (`TR.…`): feste Zeitbasis, Autos aufstellen, Kamerafahrten, Bildmittelung, Feuerwerk |
| `studio_showroom.js` | Garage (`TRS.…`): Kamera und echte Schärfentiefe |
| `drehplan.js` | alle Einstellungen: Vorbereitung, Kamerafahrt, Dauer, Zeitlupe |
| `dreh.js` | Einstellungen in einem Studio rechnen (`--probe`: vier Bilder in halber Auflösung als Kontaktblatt) |
| `ruck.js` | Unruhe einer Einstellung messen, ohne Bilder zu rechnen: Zittern (Lenkung, Fahrtrichtung, Kamerastandort, Blickrichtung), Einschwingen nach dem Aufsetzen, Lenkweg je Sekunde, größter Lenkschritt (`--verlauf` = Lenkung der ersten 20 Bilder, `--quer N` = weiches Querziel erzwingen, `--alt` = Technik bis Fassung 3) |
| `gleichlauf.py` | fertige Bilder prüfen: Bildänderung von Bild zu Bild (doppelte Bilder, Sprünge), schwarze oder stehende Einstellungen |
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

**Vor dem Dreh** jede Einstellung messen (`node tools/trailer/ruck.js <Port> <Szenen> --verlauf`, dauert Sekunden): „Einschwingen“ über 12 % oder „Lenkweg“ über 100 %/s
heißt, dass ein Auto im Bild hart umlenkt – dann `quer: 1.6` setzen oder das Auto mit `'ideal'` auf die Ideallinie stellen und neu proben.
**Nach dem Dreh** `python3 tools/trailer/gleichlauf.py` (Ruckler, schwarze oder stehende Einstellungen). Ein Kontaktblatt aus vier Bildern zeigt beides nicht.

### Was die Aufnahme filmisch macht

- **Feste Zeitbasis** (`TR.halt`, `TR.takt`): Die Bildschleife des Spiels steht, `performance.now` läuft auf einer eigenen Uhr. Jedes Bild ist exakt 1/30 s Spielzeit (bis Fassung 3: 1/24 s), seit Fassung 4 in Schritten von höchstens 10,5 ms gerechnet (`TR.schritt`),
  Zeitlupe ist einfach ein kleinerer Schritt, der Zufall ist je Einstellung festgelegt (`TR.seed`) – eine Einstellung läuft jedes Mal gleich ab.
- **Kamerafahrten** (`TR.kam(a, b)`): zwei Kamera-Angaben (am Auto, an der Strecke oder in der Welt), dazwischen wird Bild für Bild überblendet. Der Kamerastandort folgt der Fahrtrichtung des Autos träge (`TR.glatt`), die Handkamera-Unruhe ist seit Fassung 4 entfernt.
- **Echte Bewegungsunschärfe** (Profilfahrt; seit Fassung 4 auch die feste Kamera am Randstein): je Bild vier Zwischenbilder über 50–60 % der Bildzeit, im linearen Licht gemittelt.
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

Deshalb: drei Studios gleichzeitig (bis Fassung 3 mit 24 Bildern/s, seit Fassung 4 mit 30), Umgebungsverdeckung nur in ruhigen Einstellungen, Sonnenstrahlen-Durchgang nachts aus (dort ohne Wirkung).

### Ergebnis der Läufe vom 25.11.2026

**Fassung 4** (abends):
- Hauptdreh: 30 Einstellungen, 2.910 Trailerbilder, gerechnet von 15:17 bis 19:37 Uhr (4 h 20 min) in drei Warteschlangen, zuletzt mit einer Hilfsschicht für die Legenden.
  Mit drei Studios kostet ein Bild rund 13,6 s, die Profilfahrt mit vierfacher Belichtung 44 s, die Garage 36 s (sechs Zeichnungen je Bild), das Kart 22 s.
- Nachdreh (siehe „Fassung 4“): 15 Einstellungen, 1.145 Bilder, von 20:02 bis 21:47 Uhr – einschließlich Messen aller Strecken, Proben und der zweimal gerechneten Spa-Einstellung.
- Prüfung: `gleichlauf.py` meldet vier Stellen, alle erwartet (zwei Kamerawechsel im Zweikampf, zwei Reservebilder hinter dem Ende der Ampel-Einstellung).
- Schnitt: je Fassung rund 4 Minuten; 1920 × 1080, 30 Bilder/s, 3.053 Bilder, 101,77 s, 147,5 MB (11,6 Mbit/s) mit `--crf 18 --maxrate 12M`.
- Ton: mittlere Lautstärke −16,4 dB, Spitze −0,3 dB; nur Musik: −16,2 dB / −0,4 dB.

**Fassung 2** (nachts):

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

## Fassung 4: was nach der zweiten Rückmeldung geändert wurde (25.11.2026)

| Rückmeldung | Ursache | Lösung |
|---|---|---|
| zweite Sphere-Einstellung (im Regen) ist schlecht | – | gestrichen (`s17b_vegas_regen`) |
| mehr Regen, gerade in der Helmansicht | bisher eine Helm-Einstellung von 2,3 s | drei Helm-Einstellungen (Singapur 4,4 s, Spa/Eau Rouge 2,65 s, Singapur 2,75 s) plus Zeitlupe und Teleobjektiv: 16,3 s Regen statt 11,5 s. Stellen aus je drei Proben gewählt (verworfen: Singapur s = 940 – enge Kurve, Arme überkreuzt; Spa s = 6150 – ebenso) |
| Feuerwerk ans Ende | stand vor dem Regenteil | Reihenfolge: Zweikampf → Regen (laut) → Regen (ruhig) → Nachtsprint als Anlauf → **Zieleinlauf mit Feuerwerk auf dem Schlussakkord** → Logo zwei Takte später. Musik dafür 3,7 s länger (bis 151,95 s des Stücks) |
| Kamerafahrten hakelig | (1) Kamerahöhe am Auto = Höhe des *nächsten Streckenpunkts* → an Steigungen Stufen von einigen Zentimetern; (2) Kamera hing starr an der augenblicklichen Fahrtrichtung, jede Lenkkorrektur schwenkte sie mit; (3) Handkamera-Unruhe; (4) 24 Bilder/s laufen auf 60-Hz-Bildschirmen ungleichmäßig (3:2) | (1) `TR.hoehe`: Höhe stufenlos zwischen den Streckenpunkten; (2) `TR.glatt`: Standort folgt der Fahrtrichtung mit 0,28 s, Blickziel mit 0,09 s; (3) `wack` überall entfernt, Fahrten gleichförmig (`lin`); (4) **30 Bilder/s**; feste Kamera am Randstein mit Bewegungsunschärfe |
| Autobewegungen beim Lenken nicht weich | Die KI zielt auf den Streckenpunkt Nr. `idx + Vorausschau` – der Zielpunkt springt alle paar Meter weiter, das Lenkrad zuckt; es darf sich mit 7 Vollausschlägen je Sekunde drehen. Dazu: ein Simulationsschritt je Trailerbild (42 ms), harte Spurvorgaben (`c.ovr`) und Tempo-Sprünge im Zweikampf (+20 km/h in einem Bild) | Nur im Testbrowser: Zielpunkt und Ideallinie stufenlos interpoliert, Lenkrad über 0,07 s geglättet und auf 3,5 Vollausschläge je Sekunde begrenzt (`window.__trGlatt`). Simulation in Schritten von höchstens 10,5 ms (`TR.schritt`). Spurwechsel weich über `TR.spur` (3,5 m in gut 2,5 s), Tempo-Vorgaben nur mit begrenzter Beschleunigung, Vorlauf jeder Einstellung mit derselben Steuerung wie im Bild |
| Häkkinens Räder eiern | das ganze Rad ist im Modell mit Sturz eingebaut, gedreht wurde um die waagerechte Achse | im Spiel behoben (v3.03, `docs/KLASSIKER.md`); Legenden neu gerechnet |

**Gemessen** (`node tools/trailer/ruck.js <Port> <Szenen> [--alt]`, Monza; „Zittern“ = Abweichung von der glatten Bahn durch die Nachbarbilder):

| Einstellung | Kennzahl | bis Fassung 3 | Fassung 4 |
|---|---|---|---|
| Cockpit MP4/4 (Anbremsen erste Schikane) | Lenk-Zittern | 2,01 % des Vollausschlags | 0,08 % |
| | größte Lenkänderung von Bild zu Bild | 17,9 % | 4,0 % |
| | Zittern der Fahrtrichtung / der Blickrichtung | 0,038° / 0,039° | 0,002° / 0,005° |
| Zweikampf | Lenk-Zittern | 1,58 % | 0,25 % |
| | mittlere Lenkänderung je Bild | 1,70 % | 0,34 % |
| | Ausscheren | Lenkrad in einem Bild von 0 auf 59 % | höchstens 6 % Ausschlag, über 3 s |
| | Tempo beim Aufschließen | +21 km/h von einem Bild zum nächsten | +19 km/h über 1 s |

Das Zittern von Bild zu Bild war also schon vorher klein (rund 1 Bildpunkt); der sichtbare Unterschied liegt in den **Rucken** – Lenkrad, Spurwechsel, Tempo.

**Fehlversuche und Stolpersteine:**
- Erste Kennzahl (zweite Differenz von Bild zu Bild) mischte echte Kurvenbeschleunigung mit Zittern und zeigte „schlechter“ an – ersetzt durch die Abweichung von einer Ausgleichsparabel über 7 Bilder.
- Regen-Nahaufnahme in Singapur: Mit der weicheren KI-Lenkung fährt das Auto eine etwas andere Linie – die Kamera stand im ersten Bild hinter einer Werbebande. Starre Kameraführung (`glatt: false`) half nicht; die Einstellung beginnt jetzt 0,4 s später und näher an der Wagenmitte. **Nach jeder Änderung an Lenkung oder Zeitschritt alle Einstellungen neu proben.**
- Der helle Punktestreifen quer durchs Bild bei Senna (MP4/4) ist kein Fehler, sondern das Bandrauschen des 1988er-Bildlooks des Spiels; in der halben Probenauflösung wirkt es doppelt so grob.
- Idee fürs Spiel (nicht umgesetzt): der stufenlose Lenk-Zielpunkt würde auch im Spiel die KI-Autos ruhiger lenken lassen.

### Nachdreh am selben Abend: Pendeln nach dem Aufsetzen, Sägezahn-Lenken der KI

Gefunden erst beim Durchsehen der fertigen Häkkinen-Bilder (Ausschnitt des Vorderrads über zwölf Bilder nebeneinander): Das Rad lenkte in den ersten 0,4 s der
1,1 s kurzen Einstellung von stark eingeschlagen auf gerade und wieder zurück – genau das kann man für „eiernde Räder“ halten. Die Messung zeigte zwei Ursachen,
und sie betrafen 15 der 30 Einstellungen:

1. **Aufsetzen neben der Ideallinie.** `TR.feld` stellt die Autos auf eine feste Querlage (meist Streckenmitte), die KI will aber sofort auf ihre Ideallinie –
   in Monza bei s = 5300 liegt die 4 m daneben. Sie schwenkt hart ein und pendelt nach. Mit dem weicheren Lenkrad der Fassung 4 (3,5 statt 7 Vollausschläge je Sekunde)
   dauert das Einpendeln länger und fällt mitten ins Bild; bis Fassung 3 war es im kurzen Vorlauf zum Teil schon vorbei.
2. **Spurwechsel der KI sind Sprünge.** Zum Überholen setzt die KI ihr Querziel schlagartig auf eine andere Spur (`c.ovr`), und sie weicht hart aus, wenn ein Auto
   neben ihr ist. Im Regen (wenig Grip, der Lenk-Sollwert geht sofort in den Anschlag) wird daraus ein Sägezahn zwischen den Vollausschlägen –
   in der Helmansicht reißt der Fahrer das Lenkrad hin und her und fährt quer über die ganze Bahn (Singapur: von −5,3 m auf +1,2 m und zurück auf −6,7 m).

**Lösung** (nur im Testbrowser, das Spiel bleibt unverändert):
- **Weiches Querziel** (`quer: 1.6` je Einstellung → `window.__trQuer`): Das Querziel der KI wandert mit der Ideallinie mit und nähert sich dem, was die KI will
  (Ideallinie, Überholspur, Ausweichen), mit höchstens 1,6 m/s seitlich und weichem Anfahren. Beim Aufsetzen zeigt das Auto entlang der – um seinen Abstand versetzten – Ideallinie.
  Die Streckenbegrenzung gilt auch für das weiche Ziel.
- **`TR.feld(s, 'ideal', …)`**: das eigene Auto direkt auf die Ideallinie setzen (Legenden – die Bildkomposition blieb fast gleich, weil das Auto dort ohnehin hinfuhr).

**Gemessen** (`ruck.js`; Lenkweg = Summe aller Lenkänderungen je Sekunde, eine saubere Kurve kostet rund 50 %/s):

| Einstellung | vorher | nachher |
|---|---|---|
| Legenden und 2026er Ferrari (7 Einstellungen) | Lenkung in 12 Bildern von +63 % auf −73 %, dann zurück auf +36 % | gleichmäßig von 0 auf 26 % (Einlenken in die Parabolica) |
| Singapur-Kran | +48 % → −97 % → +70 % | 7 % → 5 % → 57 % (eine Kurve) |
| Vorbeifahrt am Randstein | +81 % → −87 % in 15 Bildern | 5–6 % |
| Zieleinlauf mit Feuerwerk | −50 % … −66 % mit Zacken (Lenk-Zittern 0,72 %) | −24 % → +2 % (0,03 %) |
| Helm im Regen, Singapur (lang) | Lenkweg 137 %/s, mehrfach Vollausschlag hin und her | 46 %/s, eine Kurve |
| Helm im Regen, Singapur (kurz) | 244 %/s | 26 %/s |
| Helm im Regen, Spa (Eau Rouge) | 135 %/s; am Ende 3 % → 87 % → −51 % | 45 %/s |
| Las Vegas Strip (Kamera über dem Helm) | 151 %/s, zwei Spurwechsel mit ±80 % | 6 %/s, größter Schritt von Bild zu Bild 0,8 % |
| Kart | 110 %/s, größter Schritt 11,7 % | 55 %/s, größter Schritt 5,5 % |

Unverändert geblieben (gemessen, kein Pendeln und kein Sägezahn): Start und Profilfahrt in Abu Dhabi, Gegenlicht, Singapur-Nahaufnahme (45 %/s), Nachtsprint (12 %/s),
Regen-Nahaufnahme, Sphere (Vollausschlag in der engen Kurve, aber gleichmäßig: 27 %/s), Monaco Rad (eine Kurve) und T-Kamera (Schikane: einmal von links nach rechts),
Cockpit MP4/4 (28 %/s), Zweikampf (10 %/s; das Einlenken in die Schikane in den letzten sechs Bildern ist gewollt), Spa-Teleobjektiv (3 %/s).

**Stolpersteine beim Nachdreh:**
- **Singapur-Nahaufnahme:** Mit weichem Querziel fuhr das Auto 0,9 m über den Randstein hinaus (das Mitwandern mit der Ideallinie galt auch jenseits der Streckenbegrenzung).
  Die Begrenzung ist jetzt eingebaut; die Einstellung blieb, wie sie war. (Eingebaut wurde sie erst, nachdem Kran, Vorbeifahrt, Zieleinlauf und die beiden Singapur-Helm-Einstellungen
  gerechnet waren – ob sie dort eingreifen würde, ist nicht nachgemessen; ein erneuter Dreh dieser fünf kann deshalb geringfügig anders ausfallen.)
- **Kart:** Mit weichem Querziel blieben die drei Karts davor in ihrer Spur und standen vor der Kamera. Weit weggestellt flog das eigene Kart aus der Kurve –
  `TR.start` baut das Tempoprofil des eigenen Fahrzeugs mit Formel-1-Grip, bisher hatten es nur die Vorderleute gebremst. In der Einstellung gilt jetzt `profBot = profAI`.
- **Schwarze Bilder:** Die Spa-Helm-Einstellung wurde beim ersten Nachdreh komplett schwarz gerechnet (alle 82 Bilder, Helligkeit 6 von 255), obwohl die Probe unmittelbar davor
  im selben Studio in Ordnung war und das Protokoll normal aussah. Ursache nicht geklärt; Verdacht: Probe in halber Auflösung im Regen, danach volle Auflösung ohne neues Rennen
  (in Las Vegas – trocken – und in Singapur – mit neuem Rennen dazwischen – trat es nicht auf). Ein frisches Studio rechnete sie richtig.
  **Nach einer Probe im Regen ein neues Rennen starten (`--rennen`) oder ein frisches Studio nehmen**; `gleichlauf.py` meldet schwarze und stehende Einstellungen jetzt von selbst.
- **Studios beenden:** `pkill` auf `studio.js` beendete die Studios nicht; die neu gestarteten stürzten mit „Adresse belegt“ ab, und das Warten auf „BEREIT“ hing zehn Minuten.
  Studios über `curl -X POST localhost:<Port>/ende` schließen.
- **Proben mit vier Bildern zeigen keine Bewegung.** Alle Proben der Fassung 4 waren abgenommen – das Pendeln steckte zwischen den Probenbildern. Deshalb die Messung vor dem Dreh (oben).

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
