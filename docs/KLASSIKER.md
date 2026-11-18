# Klassiker-Autos im Spiel (v2.68)

Stand: 18.11.2026. Drei historische F1-Autos mit ihrem bekanntesten Fahrer, auswählbar unter **F1** im **Schnellen Spiel** und im **Zeitfahren**.
In der **Karriere kommen sie nicht vor** (wie RONE Racing nur vom Spieler gefahren, nie als Gegner).
Modelle und Neubau: `modelle/klassiker/LIESMICH.md` · Fahrer und Technik: `modelle/klassiker/FAHRER.md`.

| Team (Schlüssel) | Auto | Fahrer | Bildfilter | Fahrleistung (Topspeed / Grip / Bremse / Beschl. gegenüber F1 2026) |
|---|---|---|---|---|
| Lotus 1970 (`H_LOT`) | Lotus 49C | Jochen Rindt, #3 | 1 – alter Film, Sepia | 0,82 / 0,62 / 0,60 / 0,72 · 5 Gänge · 500 kg |
| McLaren 1988 (`H_MCL`) | McLaren MP4/4 | Ayrton Senna, #12 | 2 – VHS-Aufnahme | 0,93 / 0,78 / 0,75 / 0,95 · 6 Gänge · 540 kg |
| Ferrari 2004 (`H_FER`) | Ferrari F2004 | Michael Schumacher, #1 | 3 – SD-Fernsehbild | 1,00 / 0,94 / 0,95 / 0,97 · 7 Gänge · 605 kg |

Die Fahrleistungen sind Richtwerte (Lotus: viel Leistung, kaum Abtrieb → rutschig, lange Bremswege; McLaren: starker Antritt, mittlerer Grip;
Ferrari: fast auf heutigem Niveau). Alle drei ohne Boost (ERS). Zum Nachjustieren: `HIST_CAR[...].ph` in `index.html`.

## Aufbau im Code (`index.html`, Abschnitt „Klassiker“ vor dem GoKart-Abschnitt)
- `F1_TEAMS.H_LOT/H_MCL/H_FER` mit `hist: true, playerOnly: true`, Fahrer `RIN`, `SEN`, `MSC` in `F1_DRIVERS`, Helme in `HELM_DESIGN`, Anzüge in `SUIT_F1`.
- `HIST_CAR`: Datei, Jahr, Bildfilter (`fx`), Lenkrad-Daten (`sw`), Lenkraddrehung (`swRot`), Gewicht, Gänge, Drehzahlen, Fahrleistung (`ph`), Infozeile.
- **Laden erst bei Bedarf** (`histLoad`): wenn das Team im Menü gewählt wird (`showroomTeam`) bzw. spätestens beim Start (`#go` wartet, Ladebildschirm
  „Klassiker wird geladen“). Beim Spielstart wird nichts geladen (3,2–4,1 MB je Auto). Der Service Worker legt die GLB-Dateien danach dauerhaft in den
  Cache `fr-models` (auch offline nutzbar). Neue Fassung eines Modells: `?v=` in `histLoad` erhöhen.
- `makeHist` baut eine leere Hülle (alle Fahrer werden beim Start als Auto angelegt); `histFill` füllt sie aus der Vorlage, sobald sie geladen ist.
  `histDone` misst dann die Kollisionsmaße neu, löst das Vorwärmen neu aus (`WARM_KEY = ''`) und baut den Showroom neu.
- **Detailstufen**: `histLod` nach Kameraabstand mit `extras.lodDistances` [0, 18, 45] m (±2 m Puffer); eigenes Auto in Helm- und TV-Kamera immer volle Stufe.
  Testschalter `window.__histLod = 0` (immer volle Stufe).
- **Räder**: die Radknoten jeder Stufe hängen in `wfl`/`wfr` (Lenkeinschlag über `fl`/`fr`) bzw. `rr` (Hinterachse); gedreht wird wie bei allen Autos über `rotation.x`.
- **Kameras**: `extras.cams` aus dem Modell (`m.cam`, `m.tv`); der 5. TV-Wert ist das Sichtfeld (52° statt `TVFOV` = 78°), `updateCamera` liest ihn.
  Angepasst im Spiel (`HIST_CAR.ck`/`tvY`, weil die Werte ohne Fahrer bestimmt wurden): Lotus-Helmkamera [0, 0.87, −0.08, 4.2] (vorher lag das Lenkrad unter
  dem Bildrand), McLaren-Blick etwas tiefer [0, 0.88, −0.05, 1.4]; TV-Höhe Lotus 1,35 m und McLaren 1,12 m (vorher füllte der Helm das halbe Bild).
  Ferrari unverändert. Der Helm sitzt in der TV-Kamera wie beim F1-Auto 3 cm tiefer und 6 cm weiter vorn.

## Lenkrad und Hände
Die Lenkräder sind im Modell in die Karosserie eingebacken. `histPrep` löst sie beim Laden heraus: Alle Dreiecke der vollen Stufe, deren drei Ecken im
Lenkradbereich liegen, bekommen eine eigene Geometrie (gleiche Attribute, nur ein neuer Index – kein Speicher doppelt). Bereich je Auto in `HIST_CAR.sw`:

| Auto | Mitte c (x, y, z) | Lenkachse a (nach vorn) | Kranz r / ±t | Nabe rh / th | Grenze h | Griffradius g |
|---|---|---|---|---|---|---|
| Lotus | 0,033 / 0,52 / 0,463 | −0,008 / −0,38 / 0,925 | 0,165 / 0,03 | 0,05 / 0,09 | – | 0,134 |
| McLaren | 0,007 / 0,48 / 0,722 | −0,005 / −0,20 / 0,98 | 0,17 / 0,025 | 0,05 / 0,08 | – | 0,129 |
| Ferrari | 0 / 0,519 / 0,517 | 0 / −0,118 / 0,993 | 0,175 / 0,04 | 0,04 / 0,06 | 0,125 (sonst kommt der Gurt mit) | 0,118 |

Gefunden mit einer Prüfseite (Modell laden, Auswahl grün einfärben, aus Cockpit, Seite und schräg oben ansehen) und einer Ebenen-Anpassung an die
Kranzpunkte (kleinste Hauptachse). Das Lenkrad dreht um die Lenkachse (`swRot`: Lotus 1,35, McLaren 1,2, Ferrari 0,95 rad bei vollem Einschlag).
Die Hände (`makeArms`) greifen auf 9 und 3 Uhr am Kranz und wandern mit (`histArms`, wie beim Roadster), Ellbogen-Ziel je Auto `sw.e`.
Fahrer: Helm mit Fahrer-Design und Oberkörper aus Grundformen (Helmmitte = Augenpunkt + 2,5 cm hoch, 12 cm zurück, wie beim F1-Modell).

## Bildfilter (Finish-Shader, Uniform `uEra`)
Kein eigener Vollbild-Durchgang: drei Verzweigungen im vorhandenen Finish-Shader (Leistungs-Anleitung Abschnitt 5), nur in „Schön“/„Ultra“.
Schalter in den Einstellungen → Extras: „Zeitfilter bei Klassikern“ (`S.histFx`).
1. **Lotus 1970 – alter Film**: Bildstand wackelt (24 Bilder/s), weicher, Sepia, flackernde Belichtung, grobes Korn, Kratzer, Staub, dunkle Ecken.
2. **McLaren 1988 – VHS**: Farbe läuft horizontal aus, Zeilen zittern, wandernder Störstreifen, Kopfumschaltung am unteren Rand, Zeilen, Rauschen, blasser.
3. **Ferrari 2004 – SD-Fernsehen**: 576 Zeilen, Farbe in halber Auflösung (4:2:0), kräftige Sendefarben, leichte 8×8-Blöcke, Halbbilder.

## Leistung (gemessen, `qc/perf-cam.js`, Monza, volles Feld, 4 Stellen je Kamera, Software-Rendering im Testbrowser)
| | Gesamt Mittel / Spitze (Verfolger · Cockpit · TV) | eigenes Auto Cockpit / TV | Schattenkarte |
|---|---|---|---|
| Russell, F1 2026 (Vergleich) | 157 / 203 · 160 / 207 · 164 / 197 | 14 Aufrufe 105 Tsd. / 16 Aufrufe 112 Tsd. | 7–11 Aufrufe, 45–58 Tsd. |
| Schumacher, F2004 – zuerst | 190 / 236 · 182 / 229 · 174 / 216 | 22 Aufrufe 87 Tsd. / 23 Aufrufe 90 Tsd. | 26–28 Aufrufe, 104–108 Tsd. |
| Schumacher, F2004 – mit Schattenstufe | 172 / 220 · 164 / 213 · 157 / 203 | 22 Aufrufe 87 Tsd. / 23 Aufrufe 90 Tsd. | 8–10 Aufrufe, 9–13 Tsd. |

Schattenstufe: Die sichtbaren Stufen werfen keinen Schatten. Ein Abbild der Stufe 2 (9.000 Dreiecke) liegt nur auf der Schattenebene `SHP_L`
(`userData.shpOnly`, der Auto-Durchgang `carPass`/`drawOwnCar` lässt es aus). Kein Shader wird im Rennen nachgeladen (Kamerawechsel 0 → 1 → 2 → 3:
Programme 123 → 123). Der Ferrari ist das schwerste der drei Modelle (16 Zeichenaufrufe in Stufe 0); Lotus und McLaren haben 15 bzw. 14.

## Menü
Teamleiste: die Klassiker stehen abgetrennt am Ende (Knöpfe dafür etwas kleiner: höchstens 6,1 % der Bildbreite, damit alle 14 Teams auf ein Querformat passen) („Historisch“ senkrecht, goldene Linie), mit Jahr unter dem Logo und gold/sepia Hintergrund.
Teaminfo: Schild „Historisch“, Modell, Fahrer und eine Technikzeile. Zeitfahren-Bestzeiten werden je Klassiker getrennt gespeichert (`|H_LOT` usw.).

## Logos
Seit v2.69 die **Logos aus der jeweiligen Zeit** (Wunsch), erzeugt mit `tools/klassiker/logos.py` (braucht cairosvg):
- `H_LOT.png` – Lotus-Plakette wie auf der Nase des 49C: gelber Kreis, Dreieck in British Racing Green, „LOTUS“, ACBC-Monogramm. Vorlage ist die
  Vektorgrafik von Wikipedia (`tools/klassiker/quellen/lotus_cars_logo.svg`, heutige Fassung in Schwarz), das Schwarz wird auf das klassische Grün umgefärbt.
- `H_MCL.png` – Schriftzug „McLaren INTERNATIONAL“ (Teamlogo der 80er), aus der Sponsoren-Textur des MP4/4-Modells, weiß auf transparent.
- `H_FER.png` – gelbes Scuderia-Ferrari-Schild (Pferd, S F, Trikolore), aus der Sponsoren-Textur des F2004-Modells, Hintergrund freigestellt.
Wikimedia lieferte die Originaldateien wegen Drosselung (Fehler 429) nicht; die Texturen der Modelle zeigen die Logos so, wie sie auf den Autos waren.
v2.68 hatte eigene Entwürfe in Creme/Gold. Die Logo-Knöpfe der Klassiker haben keinen Sepia-Filter mehr (Originalfarben).

## Offen / Ideen
- **Motorklang**: die Klassiker nutzen die vorhandenen F1-Aufnahmen mit eigenem Getriebe (Lotus bis 10.200, McLaren bis 12.100, Ferrari bis 12.900 U/min
  auf der Klangskala). Echte V8/V6-Turbo/V10-Klänge wären eigene Aufnahmen (ElevenLabs kostet Credits – vorher fragen, siehe CLAUDE.md).
- Rindts Helmfarbe ist unsicher (weiß gewählt, siehe FAHRER.md).
- Im Modus „Einfach“ (Grafik niedrig) gibt es keinen Finish-Shader und damit keinen Zeitfilter.
- Gegner bleiben moderne F1-Autos (gegen den Lotus chancenlos) – reine Klassiker-Rennen wären eine eigene Idee (dann Detailstufen für Gegner prüfen).

## Bilder (v2.68, Testbrowser)
![[bilder/klassiker_v268_filter.jpg]]
(Verfolgerkamera Lotus mit Filmfilter, McLaren mit VHS, Ferrari mit SD-Bild; Teamwahl mit „Historisch“-Bereich)

![[bilder/klassiker_v268_cockpit.jpg]]
(Helmkamera geradeaus und bei vollem Einschlag: Lotus, McLaren, Ferrari – Lenkrad dreht, Hände greifen mit)

## v2.70 – Fahrer im Auto, Räder, Tachos, Klänge (Rückmeldungen vom 18.11.2026)
- **Fahrer aus dem Modell** (`histDriver`): derselbe Rennfahrer wie im modernen F1 (`f1fahrer.bin`: Anzug, Handschuhe, Arme per IK), statt der
  Grundform-Arme. Helm an der Helmmitte des Klassikers, Fäuste am Kranz: `kartArmsIK` hat dafür einen neuen Parameter `Q` (Lage des Ziel-Lenkrads
  gegenüber dem Bau-Lenkrad `_swQ`), Griffradius auf `sw.g` skaliert. Helmkamera: nur Unterarme und Hände (`uCut` wie beim F1).
- **Unsichtbare Teile entfernt**: `tools/klassiker/fahrer_sicht.js` rendert Auto (schwarz) und Fahrer (Dreiecks-Nummern als Farbe) aus 1.210 Blickwinkeln
  (rundherum in 5 Abständen × 7 Höhen × 32 Richtungen, dazu Helm- und TV-Kamera mit Kopfbewegung) und schreibt `modelle/klassiker/fahrer_sicht.json`.
  Rumpf-Dreiecke, die nie zu sehen sind, fallen weg; Arme/Hände bleiben immer. Ergebnis (von 13.939): Lotus 10.993 sichtbar (offenes Cockpit, Fahrer
  schaut weit heraus), McLaren 8.555, Ferrari 7.844. Testschalter `window.__histFull = true` (vor dem Laden): ganzer Fahrer.
- **Räder** (`histSplitWheels`): Teile im Radzylinder werden in zusammenhängende Stücke zerlegt; rundum geschlossene (Reifen, Felge, Scheibe) drehen,
  die übrigen lenken vorn nur mit bzw. stehen hinten. Lotus: Innenseite der Vorderräder gehörte zur Karosserie (lenkte nicht mit), am Hinterrad drehten
  Halter mit. Achsmitte aus dem Reifenring gemessen: Ferrari vorn lag 8,5 mm, hinten 3 mm daneben (Räder eierten); Lotus/McLaren < 1 mm.
- **Bremslicht** (Regenlicht) bei McLaren und Ferrari am hintersten Punkt der Wagenmitte (automatisch aus dem Modell), blinkt beim Bremsen.
- **Kein Boost**: Boost-Taste und ERS-Anzeige sind bei den Klassikern ausgeblendet (`noBoost`).
- **Tacho je Epoche** (`histGauge`, statt der Halo-Grafik): Lotus Armaturenbrett mit Drehzahlmesser (rot ab 10.000), Öl und Wasser, Tempo im Zählwerk;
  McLaren Drehzahlmesser bis 14.000 mit orangem Zeiger, Ladedruck, bernsteinfarbene Sieben-Segment-Anzeige; Ferrari Lenkrad-Display mit 15 Schaltlampen,
  graugrünem LCD (großer Gang, Tempo, Platz, Runde, Zeit) und Tasten.
- **Filter**: Sepia nur noch leicht weich (Mischung 0,3 statt 0,7, Bildstand-Wackeln ein Drittel, feineres Korn). SD 2004 ohne Verpixeln: leicht weich,
  Farbe weicher als Helligkeit, feine Kantenanhebung, kräftige Sendefarben.
- **Menü**: Jahreszahl klein in der Ecke, Logo bleibt mittig. Ferrari-Logo in sattem Gelb (`logos.py`). Fahrerwahl: einzelnes Auto mittig.
- **Motorklang**: eigene Aufnahmen, siehe unten und `docs/SOUNDS.md` (v2.70).

### Klänge
| Klasse | Loops (Grundton) | Gas weg | Zündungen/Umdr. | Drehzahl (Schalten/Höchst) |
|---|---|---|---|---|
| `hist_lot` (Cosworth V8) | mittel 512 Hz, hoch 577 Hz | 496 Hz | 4 | 9.600 / 10.200 |
| `hist_mcl` (Honda V6 Turbo) | mittel 564 Hz, hoch 561 Hz | 284 Hz | 3 | 11.800 / 12.500 |
| `hist_fer` (Ferrari V10) | mittel 1.099 Hz, hoch 1.625 Hz | 1.296 Hz | 5 | 17.600 / 18.300 |
Dateien `sounds/hist_*.wav`, werden nur geladen, wenn mit dem Klassiker gefahren wird (`lazy`, `histSnd`).
