# Wetter: Regen (v2.95)

Stand 24.11.2026 (v2.97). Regen und das neue Menü „Rennen einstellen“ (Entwurf A, vom Nutzer gewählt) sind eingebaut und auf `main`. Das Wetter wird im Menü
unter **Rennen einstellen → Wetter** gewählt; in der Karriere wird es je Rennwochenende ausgelost.

Bilder (echte Spielbilder): `docs/bilder/regen_entwurf_tag.jpg`, `regen_entwurf_nacht.jpg`, `regen_helm_reifen.jpg` (Visier-Tropfen, blaue Regenreifen),
`regen_helm_tropfen_v297.jpg` (Tropfen fliegen mit dem Tempo zur Seite: Stand / 150 / 300 km/h) ·
Menü: `rennmenue_v295.jpg` (eingebaut), `menue_kopfzeile_v296.jpg` (Schrittleiste über die volle Breite), Entwürfe `rennmenue_entwurf_A.jpg`, `_B.jpg`, `_desktop.jpg`.

---

## 1. Was gebaut ist

| Baustein | Kurz |
|---|---|
| Wetterstufen | `dry`, `light` (leichter Regen, Intermediates), `heavy` (starker Regen, Regenreifen); `auto` lost nach echter Wahrscheinlichkeit aus |
| Stimmung | geschlossene, helle Wolkendecke mit Struktur, kein Sonnenlicht/keine Schlagschatten (weiche Umgebungsverdeckung bleibt), Dunst (Sicht ~2,3 km leicht, ~1,15 km stark), entsättigtes, kühleres Bild; Nachtrennen: Dunst im Flutlicht, mehr Leuchten |
| Nasse Fahrbahn | dunklerer, glatter Asphalt, Pfützen (auf der Ideallinie weniger, am Rand mehr), Tropfenringe in den Pfützen, Spiegelung der Umgebung (Autos, Banden, Bäume, Tribünen, Flutlichter, Himmel) |
| Regen | ~5.600 feine Striche in einem Kasten um die Kamera, komplett im Vertex-Shader; bei Tempo laufen sie auf den Fluchtpunkt zu (Länge begrenzt) |
| Nachtrennen | Regen ist nur im Flutlicht sichtbar: Lichtkarte der Strecke für die Tropfen um die Kamera, dazu je Mast ein Lichtkegel mit fallendem Regen (nah einzelne Striche, fern ein heller Schleier) |
| Gischt | Wasserschleier hinter den Hinterrädern, Menge nach Tempo und Nässe; wer dicht folgt, sieht schlecht |
| Reifen | alle Autos auf Intermediates (grüne Flanke) bzw. Regenreifen (blaue Flanke) |
| Regenlicht | blinkt bei Nässe durchgehend (4 Hz) |
| Fahrphysik | Haftung −14 % / −25 %, Bremse −12 % / −21 %, Traktion −8 % / −16 % (leicht / stark); nasse Randsteine, Farbe und Gras deutlich glatter; Aquaplaning in Pfützen bei hohem Tempo; die KI bremst früher und fährt Kurven langsamer (gleiche Faktoren) |
| Ton | berechnetes Regenprasseln und Reifenzischen (kein Download, keine ElevenLabs-Credits) |
| Karriere | je Rennwochenende einmal ausgelost (Quali und Rennen gleich), im Spielstand gespeichert (`CHP.wx`) |
| Monaco | im Tunnel fällt kein Regen (Lichtkarte, Kanal „überdacht“) |
| Helmansicht | Regentropfen auf dem Visier: im Stand runde Perlen, die still sitzen; mit dem Tempo treibt sie der Fahrtwind von der Visiermitte zur Seite – erst langsam, bei 300 km/h in unter einer Sekunde über den Rand, mit spitz zulaufendem Schweif (v2.97). Jeder Tropfen wirkt als kleine Linse mit Glanzpunkt (nur „Schön“/„Ultra“) |

## 2. Bedienen und testen

- **Im Spiel**: Rennen einstellen → Reiter „Wetter“: Trocken, Leichter Regen, Starker Regen oder Zufall (nach dem Regenrisiko der Strecke, wird bei jedem Start neu gelost).
- **Testschalter**: `index.html?wetter=stark`, `?wetter=leicht`, `?wetter=trocken` – erzwingt das Wetter für jedes Rennen (auch in der Karriere).
- Konsole: `__wx('heavy')` / `__wx('light')` / `__wx('dry')` schaltet auf der gebauten Strecke um (ohne Neubau), `__WX` zeigt den Zustand.
- Gespeichert wird die Wahl in `S.wx` (`dry`/`light`/`heavy`/`auto`).
- **Lasttest am Handy** (Einstellungen → Extras → Debug-Menü): Bei Regen misst er zusätzlich „ohne Tropfen und Lichtkegel-Regen“, „ohne Gischt“,
  „ohne Pfützen-Spiegelung“ und „trocken zum Vergleich“ – so lässt sich am echten Gerät ablesen, was jeder Baustein kostet.
- Testschalter für Messungen: `window.__noRain`, `__noSpray`, `__noSSR` (danach `applyWeather(WX.cur, true)`).
- Bilder aus dem echten Spiel: `node tools/wetter/regen_bilder.js Spa heavy <Ordner> 1700,0 1700,2 fix:2200:0:1.3:2300:0:0.5`
  (Strecke, Wetter, Ansichten: `Streckenmeter,Kamera` oder Standbild `fix:…`). `--folge 18,1` nimmt nach jedem Bild 18 weitere auf (je 1 Spielbild später) –
  für alles, was sich bewegt. Im Testbrowser kostet jedes Spielbild ~18 s.
- **Visier-Tropfen schnell abstimmen**: `node tools/wetter/tropfen_pruefstand.js <Standbild.png> <Ordner> 0 120 290` legt den Tropfen-Shader (direkt aus
  `index.html` gelesen) über ein Standbild und rendert je Tempo eine Bildfolge plus `zoom.png` – Sekunden statt Minuten. Standbild ohne Tropfen:
  `regen_bilder.js … 2150,2 --pre "window.__noDrops = 1"`.
- **Auflösung prüfen**: Der Testbrowser läuft mit Pixelverhältnis 1 – Fehler in der Renderauflösung fallen so nicht auf. Für solche Prüfungen
  `spiel({ …, dpr: 2 })` (`tools/textur/spiel.js`). Fertige Prüfung über Wetterwechsel hinweg: `node tools/wetter/aufloesung_pruefen.js` (Soll und Ist je Zeile).

## 3. Regenwahrscheinlichkeit je Strecke („wie in echt“)

Zwei Quellen, verrechnet in `tools/wetter/regen_tabelle.py`:

1. **Tatsächlich nasse Formel-1-Rennen seit 2000** je Strecke: Feld „Weather“ der Wikipedia-Rennseiten (über DBpedia in einer Abfrage, die jüngsten Rennen
   direkt von Wikipedia). Stand: 405 Rennen von 2000 bis 2025, davon 55 nass. Die Rennen 2026 fehlen noch bis auf Melbourne – Wikipedia gibt von hier nur wenige
   Seiten je Minute heraus; ein späterer Lauf des Skripts holt sie nach (Zwischenspeicher). Skript: `tools/wetter/regenrennen_wikipedia.py`, Ergebnis mit allen Wettertexten: `regenrennen_ergebnis.json`.
2. **Wetterarchiv** (Open-Meteo, ERA5-Reanalyse, stündlicher Niederschlag am Ort der Strecke, 2000–2024): Anteil der Tage im Fenster ±7 Tage um den
   Renntermin 2026, an denen von einer Stunde vor dem Start bis zwei Stunden danach mindestens 1,0 mm fallen. Skript: `tools/wetter/regenwahrscheinlichkeit.py`,
   Ergebnis: `regen_ergebnis.json`. Die Schwelle 1,0 mm ist geeicht: Damit passt die Summe über alle Strecken zu den tatsächlich nassen Rennen
   (0,5 mm zählt bloßes Nieseln mit und liegt rund 40 % zu hoch).

Verrechnung: `p = (nasse Rennen + 8 · Archivwert) / (Rennen + 8)` – das Archiv zählt wie acht zusätzliche Rennen. Strecken mit vielen Rennen folgen fast
ganz ihrer echten Statistik; neue Strecken (Las Vegas, Madrid) und die Kartbahnen stützen sich auf das Archiv. Das gleicht die Schwächen aus: Das Archiv
(25-km-Raster) überschätzt Regen im Gebirge deutlich (Spielberg 36 %, in echt 1 nasses von 18 Rennen), und eine Handvoll Rennen sagt allein wenig.
„Davon starker Regen“: Anteil der Regentage im Archiv mit mindestens 2 mm in einer Stunde des Rennfensters (begrenzt auf 15–45 %).

<!--RAIN_TABELLE-->
| Strecke | Termin 2026, Start (Ortszeit) | Wetterarchiv 2000–2024 | nasse F1-Rennen seit 2000 | im Spiel | davon starker Regen |
|---|---|---|---|---|---|
| Melbourne | 08.03. 15 Uhr | 6 % | 3 von 25 | **10 %** | 24 % |
| Shanghai | 15.03. 15 Uhr | 10 % | 5 von 18 | **22 %** | 22 % |
| Suzuka | 29.03. 14 Uhr | 18 % | 3 von 22 | **15 %** | 29 % |
| Bahrain | 12.04. 18 Uhr | 1 % | 0 von 22 | **0 %** | 25 % |
| Jeddah | 19.04. 20 Uhr | 0 % | 0 von 5 | **0 %** | 25 % |
| Miami | 03.05. 16 Uhr | 17 % | 1 von 4 | **20 %** | 45 % |
| Montréal | 24.05. 16 Uhr | 15 % | 3 von 23 | **14 %** | 35 % |
| Monaco | 07.06. 15 Uhr | 18 % | 5 von 25 | **20 %** | 24 % |
| Barcelona | 14.06. 15 Uhr | 11 % | 0 von 26 | **3 %** | 33 % |
| Red Bull Ring | 28.06. 15 Uhr | 36 % | 1 von 18 | **15 %** | 45 % |
| Silverstone | 05.07. 15 Uhr | 18 % | 7 von 27 | **24 %** | 31 % |
| Spa | 19.07. 15 Uhr | 26 % | 7 von 24 | **28 %** | 32 % |
| Hungaroring | 26.07. 15 Uhr | 16 % | 6 von 26 | **21 %** | 34 % |
| Zandvoort | 23.08. 15 Uhr | 16 % | 1 von 5 | **18 %** | 34 % |
| Monza | 06.09. 15 Uhr | 12 % | 2 von 26 | **9 %** | 44 % |
| Madrid | 13.09. 15 Uhr | 6 % | 0 von 0 | **6 %** | 29 % |
| Baku | 26.09. 15 Uhr | 3 % | 0 von 9 | **1 %** | 25 % |
| Singapur | 11.10. 20 Uhr | 18 % | 2 von 16 | **14 %** | 33 % |
| Austin | 25.10. 15 Uhr | 8 % | 0 von 13 | **3 %** | 45 % |
| Mexiko-Stadt | 01.11. 14 Uhr | 8 % | 0 von 10 | **3 %** | 45 % |
| São Paulo | 08.11. 14 Uhr | 40 % | 7 von 25 | **31 %** | 45 % |
| Las Vegas | 21.11. 20 Uhr | 2 % | 0 von 3 | **2 %** | 25 % |
| Lusail | 29.11. 19 Uhr | 2 % | 0 von 4 | **1 %** | 25 % |
| Abu Dhabi | 06.12. 17 Uhr | 0 % | 0 von 17 | **0 %** | 25 % |
| Nordschleife | 15.07. 14 Uhr | 17 % | 2 von 12 | **17 %** | 29 % |
| Genk | 15.07. 14 Uhr | 16 % | 0 von 0 | **16 %** | 38 % |
| Wackersdorf | 15.07. 14 Uhr | 16 % | 0 von 0 | **16 %** | 30 % |
<!--/RAIN_TABELLE-->

Grenzen der Daten: Wikipedia nennt bei manchen Rennen kein oder ein ungenaues Wetter (Austin 2015 steht als „Very cloudy“, war aber nass). Die Nordschleife
nutzt als Näherung die F1-Rennen auf dem Nürburgring und das Archiv über die ganze Saison (Mai–September). Neu erzeugen:

```bash
python tools/wetter/regenwahrscheinlichkeit.py
python tools/wetter/regenrennen_wikipedia.py --texte
python tools/wetter/regen_tabelle.py --schreiben      # trägt RAIN_P in index.html ein
```

## 4. Technik (für spätere Änderungen)

Alles steht in `index.html` im Block „Wetter: Regen (v2.95)“ vor dem Himmel. Zustand: `WX`, Stufen: `WXLV`, gemeinsame Shader-Werte: `WXU`.

- **Kein Streckenneubau**: `applyWeather(k)` stellt um – Thema (`wxTheme` leitet per Prototyp-Kette aus dem trockenen Thema ab), Himmel/Nebel/Licht (`applyAtmo`),
  gebackener Himmel und Umgebung (`applySky`, `buildEnv` mit grauer Wolkendecke `envSky`), Schattenstärke (`bakeSun`), Sichtweite (`camera.far`), Kulisse ohne
  Nebel bekommt Nebel, Bodenmaterialien bekommen die Defines. Das Wetter wird beim Rennstart festgelegt (`wxPick` im Start-Knopf) und läuft hinter dem
  Ladebildschirm („Regen zieht auf“); `wxPreset` merkt es schon vor dem Streckenbau vor.
- **Nasse Böden** (`wetMat`, `wxCollect`): nach dem Schatten-Backen werden alle flachen Bodenmaterialien eingeteilt – Asphalt/Beton (Pfützen + Spiegelung),
  Farbe/Curbs (glänzender Film, kaum Pfützen), Gras/Kies/Sand (nur dunkler, ohne Shader-Änderung). Der Regen-Code steht hinter `#ifdef WX_WET`:
  **im trockenen Programm ist er nicht enthalten**. Pfützenkarte `WXPUD` (128², kachelbar); Shader und Fahrphysik (`wxPudAt`) lesen dieselben Werte.
- **Pfützen-Spiegelung (SSR)** ohne eigenen Durchgang: Der Composer rendert die Szene abwechselnd in zwei Puffer – der jeweils andere enthält Farbe **und Tiefe**
  des letzten Bildes (die Tiefe löst Three.js ohnehin mit auf; bei Regen landet sie in einer Tiefentextur statt in einem Puffer). Der Fahrbahn-Shader tastet den
  gespiegelten Strahl in wenigen **Höhenstufen** über der Fahrbahn ab (fein am Boden für Autos und Banden, grob nach oben für Tribünen, Masten, Himmel), misst den
  Treffer zwischen zwei Stufen ein und liest dort die Farbe. Stufen: Handy 4, Laptop 6, Ultra 8; Schnell: keine Spiegelung, nur Himmelsglanz.
  Nur Pixel mit mindestens 3 % Spiegelanteil suchen überhaupt. Das eigene Auto in Helm-/TV-Kamera wird nicht gespiegelt (eigener Tiefenbereich).
  Bei Ultra sorgt ein leerer Tausch-Schritt dafür, dass die Szene trotz AO-Durchgang je Bild den Puffer wechselt.
- **Regen** (`RAINFX`): Linien, Position = Zufallswert im Kasten + Fallweg, relativ zur Kamera umlaufend; Schweif = Bewegung relativ zur Kamera × Belichtungszeit
  (höchstens 85 cm). Additiv in Dunstfarbe. Lichtkarte `WXM` (von oben gezeichnet: R = Flutlicht am Boden, G = überdacht).
- **Lichtkegel-Regen** (`RAINC`, nur Nacht): ein Zeichenaufruf für alle Masten; Lampenpositionen sammelt `WX.lamps` an den drei Stellen, an denen Masten gebaut werden.
- **Visier-Tropfen** (`dropLayer` im Bild-Shader `FinishShader`, Uniform `uDrop`: x Menge, y Fahrtwind, z Laufzeit, w Weg zur Seite): zwei Schichten (wenige
  mittlere, viele kleine), je Rasterzelle höchstens ein Tropfen. Das Raster jeder Bildhälfte wandert nach außen; der Weg wird in `tick` aufsummiert
  (`uDrop.w`, Umlauf bei 512 wegen der Rechengenauigkeit), jede Zeile hat ihr eigenes Tempo. Die Zellen sind 2,5-mal so breit wie hoch – so passt der Schweif
  ohne Nachbarzellen-Abfrage hinein. Die Tropfen werden **nach** Radialunschärfe und Farbsaum eingerechnet (sie sitzen scharf vor dem Bild; vorher
  verschwand ihre Schattierung bei Höchsttempo in der Unschärfe und der Farbsaum färbte sie braun). Uniform-Verzweigung: ohne Regen/Helmansicht kostet es nichts.
- **Visierschmutz** (`visorDirtTick`, dunkle Flecken aus Staub/Gummiabrieb/Insekten, gab es schon vorher): bei Regen kommen keine neuen dazu (v2.97) –
  zwischen den Tropfen sahen sie wie Fehler aus.
- **Composer neu bauen** (`buildComposer()`): danach immer `resize()` aufrufen – der neue Composer startet sonst in einfacher Auflösung (siehe Abschnitt 5a).
- **Gischt** (`SPRAY`, `wxSpray`): bis 1.400 weiche Punkte, nur Autos im Umkreis von 150 m, in Kameranähe ausgeblendet.
- **Vorwärmen**: `precompile()` zeichnet Regen, Gischt und Lichtkegel einmal mit; `warmKey` enthält das Wetter. Gemessen (Spa, starker Regen, alle vier Kameras):
  nach dem Laden 171 Shader, im Rennen kommt keiner dazu.

### Neue Strecken regentauglich bauen

- **Böden** werden automatisch nass, wenn sie wie üblich als flache Streifen/Bodenflächen gebaut sind (`userData.flat`, `ground`, `tile`). Flächen mit Gras-, Kies-,
  Sand- oder Laubtextur werden nur dunkler; eine neue Erd-/Rasentextur bitte mit `textur.userData.soil = 1` kennzeichnen, sonst gilt sie als Asphalt und bekommt Pfützen.
- **Flutlichtmasten** (Nachtstrecken): beim Bau je Mast `WX.lamps.push([Kopf x, Kopf y, Kopf z, Lichtfleck x, Lichtfleck z, Boden y])` – daraus entstehen die Lichtkarte für
  die Tropfen und der Regen im Lichtkegel. Ohne Einträge leuchtet der Regen nur als Band entlang der Strecke.
- **Lichtflecken** auf dem Asphalt über `poolMesh` bauen – sie werden bei Nässe automatisch gedimmt (nasser Asphalt spiegelt statt zu streuen).
- **Überdachte Abschnitte** (Tunnel): in `wxRainSetup` in die Liste `cov` eintragen (Streckenmeter von–bis), dann fällt dort kein Regen.
- **Fernbäume** werden mit dem Licht beim Streckenbau gebacken; bei späterem Wetterwechsel gleicht `applyWeather` nur die Helligkeit an (`WX.imps`).

## 5. Leistung

- Trocken: unverändert (kein Regen-Shader im Programm, keine Tiefentextur, Regen-Objekte unsichtbar und ohne Rechenarbeit; geprüft: Zustand und Bild).
- Wetterwechsel auf gebauter Strecke: Himmel und Umgebung neu backen, Bodenmaterialien neu übersetzen – läuft hinter dem Ladebildschirm (im Testbrowser mit Software-Grafik ~2,2 s).
- Regen kostet **höchstens drei Zeichenaufrufe** (Tropfen, Gischt, nachts Lichtkegel) und kein zusätzliches Vollbild; die Sichtweite sinkt (Tag), dadurch werden
  ferne Objekte gar nicht mehr gezeichnet.
- Der eigentliche Preis ist die Spiegelung im Fahrbahn-Shader: je spiegelndem Pixel 4/6/8 Tiefenabfragen + 1–2 weitere + 1 Farbabfrage. Das lässt sich im
  Testbrowser (Software-Grafik) nicht belastbar messen – **bitte am Handy mit dem Lasttest prüfen** (Schritt „Regen: ohne Pfützen-Spiegelung“). Ist es zu teuer:
  in `applyWeather` die Stufenzahl für `isTouch` senken oder die Spiegelung auf dem Handy nur bei „Ultra“ einschalten (`wxSSRWanted`).
- Regeln aus `docs/LEISTUNG-ANLEITUNG.md` eingehalten: im Ruhezustand nichts tun, vorgewärmt, kein neuer Vollbild-Durchgang, Durchsicht testet die Tiefe.

## 5a. Fehler und Lehren

- **Auflösung brach nach dem ersten Regenrennen ein (v2.95–v2.96, behoben in v2.97).** `applyWeather` baut den Composer neu, wenn die Pfützen-Spiegelung
  an- oder ausgeht (Tiefentextur). Dabei fehlte `resize()`: Der neue Composer rechnete mit einfacher statt Geräteauflösung – auf dem Handy rund ein Drittel
  der Bildpunkte von „Schön“ (im Test 852×393 statt 1491×688) – und das blieb bis zum Neuladen so, auch in trockenen Rennen danach. Jetzt folgt auf jedes
  `buildComposer()` ein `resize()` (in `applyWeather` und im Trockenpfad von `buildTrack`). Aufgefallen ist es im Test nicht, weil der Testbrowser mit
  Pixelverhältnis 1 lief – deshalb der Schalter `dpr` in `tools/textur/spiel.js`.
- **Rosa/grüne Flecken bei Höchsttempo (alt, seit vor v2.95, behoben in v2.97).** Der Farbsaum am Bildrand holte Rot und Blau scharf aus dem Bild, während Grün
  schon radial verwischt war – an hellen Schriftzügen und Baumkanten entstanden rosa/grüne Flecken (im Regen durch den hellen Himmel besonders deutlich).
  Der Farbsaum wird jetzt im verwischten Bereich ausgeblendet (`cm = 0.85 * (1 - bw)`).
- **Visier-Tropfen erst nur dunkle Punkte**: siehe „Visier-Tropfen“ in Abschnitt 4 (Reihenfolge im Bild-Shader).

## 6. Stellschrauben

| Was | Wo |
|---|---|
| Haftung/Bremse/Traktion, Regenmenge, Pfützenmenge je Stufe | `WXLV` |
| Himmel, Dunst, Licht, Bildstimmung bei Regen | `wxTheme` (Tag und Nacht getrennt) |
| Abdunkelung/Glanz je Belag | `WXK` (`asph`, `paint`) |
| Tropfen: Anzahl, Kasten, Belichtung, Farbe | `RAINFX` (`N`, `uBox`, `uExp`), `wxRainSetup` (`uCol`, `uAmt`) |
| Gischt: Menge, Größe, Deckkraft | `wxSpray` |
| Untergründe bei Nässe, Aquaplaning | `SURFW`, `wxAqua` |
| Spiegel-Stufen je Gerät | `applyWeather` (`steps`) |
| Visier-Tropfen: Menge und Größe je Schicht | Aufruf `drp = dropLayer(…)` (Rasterzeilen 10/26, Füllgrad 0,65/0,8), Größe `r` in `dropLayer` |
| Visier-Tropfen: Tempo zur Seite, ab wann | `tick` (`d.w += … Math.pow(d.y, 1.4) * 1.3`; Fahrtwind `d.y`: 0 unter 22 km/h, 1 ab 281 km/h) |
| Visier-Tropfen: Schweiflänge, Zuspitzung, Schräge | `dropLayer` (`st = 1 + wind * 2.4`, `ry`, `d.y -= 0.12 * …`) |

## 7. Menü „Rennen einstellen“ (Entwurf A, eingebaut)

Vorher stand alles auf einer Seite; auf dem Handy war die Ideallinie unten abgeschnitten. Jetzt vier Gruppen: **Rennen** (Renndauer, Startplatz), **Wetter**
(Trocken, Leichter Regen, Starker Regen, Zufall + Regenrisiko der Strecke), **Gegner** (Schwierigkeit mit kurzer Erklärung), **Fahrhilfen** (Steuerung, Ideallinie,
Auto-Gas, Bremsassistent). Links die Reiter – jeder zeigt seinen aktuellen Wert, man sieht alle Einstellungen auf einen Blick –, rechts die gewählte Gruppe.

- HTML: `#scrRace` → `.rx` (`#rxNav`, `.rx-pane` mit vier `.rx-p`), Anzeige: `renderRx()` (wird aus `renderMenu` aufgerufen), gemerkter Reiter: `MENU.rx`.
- Zeitrennen: Reiter „Gegner“ und der Startplatz entfallen. Karriere: am nächsten Rennen steht das Regenrisiko, ab dem Qualifying das ausgeloste Wetter (`renderSeason`).
- Das Logo oben rechts bleibt in der Auswahl (Klasse, Team, Fahrer, Strecke, Rennen) weg – die Schrittleiste braucht den Platz.
- Kopf- und Fußzeile der Auswahl folgen einem Raster (CSS-Block „Kopf- und Fußzeile der Auswahl (v2.95)“): Die Schrittleiste läuft über die volle Breite zwischen
  „Zurück“ und „Einstellungen“ (fünf gleich breite Felder), Kopfzeile, Inhalt und Fußzeile haben denselben Seitenrand (22 px; vorher 16 / 22 / 18), Leiste und
  Knöpfe sind gleich hoch (42 px, auf kleinen Handys 38 px), der Abstand Kopfzeile → Inhalt → Fußzeile ist gleich (10 px, kleines Handy 8 px).
- Am Laptop/Monitor (ab 560 px Höhe) nutzt „Rennen einstellen“ die Höhe: höhere Reiter, die Fläche rechts so hoch wie die Reiter, Inhalt darin mittig.
- Entwürfe (Bilder): `docs/bilder/rennmenue_entwurf_A.jpg`, `_B.jpg`, `_desktop.jpg`; Mockup-Skript `tools/wetter/rennmenue_entwurf.js`.

### Menü-Prüfung (`tools/menue/pruefen.js`)

Geht alle Menü-Bildschirme durch (Schnelles Spiel, Zeitrennen, Karriere, Einstellungen, Pause, Ergebnis), nimmt je Bildschirm ein Bild auf und meldet Elemente, die
außerhalb liegen, abgeschnitten oder überdeckt sind oder deren Text nicht passt:

```bash
node tools/menue/pruefen.js <Ordner> 667x375 740x360 852x393 915x412 1280x720     # --ohne-rennen lässt Pause/Ergebnis weg
```

Gewollte Meldungen (kein Fehler): Scroll-Listen (Streckenkarten, Tabellen, lange Einstellungsseiten), die große Zierzahl auf den Fahrerkarten, „Text gekürzt“ am
Weiter-Knopf (Glanz-Effekt), Überschrift „Team wählen“ (ihr Kasten reicht unter den Umschalter, der Text nicht). Am 24.11.2026 behoben: Saison-Seite auf kleinen
Handys (Rennlänge lag unter dem Start-Knopf), abgeschnittene Helmfarben, mitten im Wort endende Auswahl-Chips in der Fußzeile, angeschnittener Knopf und kaum
lesbare Prozentwerte in den Audio-Einstellungen.

## 8. Ideen für später

- Tropfen auch auf der Linse der TV-Kamera (auf dem Visier der Helmansicht gibt es sie schon: `dropLayer` im Bild-Shader, `uDrop`).
- Wechselndes Wetter im Rennen (abtrocknende Ideallinie, einsetzender Regen) – `WX.wet`/`WX.rain` sind schon getrennte Werte.
- Spritzer beim Durchfahren von Pfützen, Regenrinnen am Fahrbahnrand.
- Boxenstopps mit Reifenwahl gibt es im Spiel nicht – deshalb fahren bei Regen alle auf dem passenden Reifen.
- Bekannte Kleinigkeit: Im Monaco-Tunnel fällt kein Regen, die Fahrbahn bleibt dort aber nass und die Pfützen zeigen weiter Tropfenringe.
