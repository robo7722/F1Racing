# Klassiker-Autos im Spiel (v2.68)

Stand: 18.11.2026. Drei historische F1-Autos (seit dem Abschnitt „Drei weitere Klassiker“ am Ende: sechs – Ferrari 312, McLaren MP4/13, Red Bull RB8) mit ihrem bekanntesten Fahrer, auswählbar unter **F1** im **Schnellen Spiel** und im **Zeitfahren**.
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

## v2.71 – Sitzposition nach Fotos, Räder um die echte Achse, Live-Instrumente, Schikanen-Strafe
- **Sitzposition** (Referenzfotos vom Nutzer: MP4/5B Senna, Lotus 49B, F2004 Schumacher): `HIST_CAR.seat` = [tiefer, zurück] m – McLaren −7 cm
  (vorher ragten Schultern und Arme über die Seitenkästen, auf dem Foto sieht man nur den Helm), Ferrari −4 cm; Lotus unverändert (aufrecht, Schultern sichtbar).
  Sichtbarkeit danach neu gemessen (`fahrer_sicht.json`).
- **Räder drehen um ihre echte Achse**: `tools/klassiker/radachsen.py` misst Sturz/Spur an den Laufflächenpunkten → `HIST_CAR.ax`. Ferrari vorn 2,2° Sturz,
  0,5° Spur (eierte, weil um die waagerechte Achse gedreht); Lotus hinten 0,7° Spur; Rest < 0,5°. Aufbau: vorn `fl` (lenkt) → Neigung → `wfl` (dreht);
  hinten je Rad Neigung → Drehgruppe (`m.spR`), `m.rr` bleibt leer.
- **Reifenschrift Ferrari**: Die Flankentextur (runder Schriftring) war im Modell zerstückelt und nicht auf die Achse zentriert abgebildet (Ausgleichsrechnung:
  mittlere Abweichung 0,14 Texturbreite) – die Schrift schlingerte. `histTyreUV` bildet die Flanken neu ab (eben um die Radmitte, von außen lesbar).
- **Radteile**: „rund“ nur, wenn der äußere Rand in allen Richtungen gleich weit reicht (±12 % des Radius) – angehängte Halter/Radträger drehen nicht mehr mit
  (Lotus hinten). Vorn zusätzlich 12 cm nach innen erfasst (bis 80 % Radius): Bremsscheibe, Sattel und Radträger lenken mit.
- **Live-Instrumente im Modell** (`HIST_DASH`, `histDashBuild/Draw/Tick`): Flächen über den echten Anzeigen, Lage per Strahl-Treffer aus der Augenposition gemessen.
  Lotus: Drehzahlmesser (Ø 9,4 cm) + Öl/Wasser; McLaren: Anzeigeschlitz 8,5 × 1,6 cm hinter dem Lenkrad (bernsteinfarbene Leuchtbalken, Gang, Tempo);
  Ferrari: Lenkrad-Display 7,9 × 5,5 cm (dreht mit). EINE CPU-Leinwand je Auto, 15× je Sekunde, nur in Helm-/TV-Kamera.
- **Schikanen-Strafe** (alle Autos): zählt nur noch Strecke auf der Kurveninnenseite (`sign(lat) = sign(KS)`, |KS| > 1/400) – wer außen herum fährt, wird nicht
  bestraft. Geprüft an der Monza-Schikane: Innenseite an 15 von 16 Messpunkten richtig (der eine liegt am Übergang zwischen den beiden Kurven).

## v2.72 – Sitzposition wie im Original, Querlenker biegen sich, McLaren-Armaturen, Ferrari-Innenflanke
- **Sitzposition**, gemessen an Überrollbügel/Kopfstütze im Modell (Höchstpunkt der Mittellinie je 5-cm-Scheibe) und den Fotos (maßstabsgleiche
  Seitenansicht ohne Perspektive neben die Fotos gelegt):
  - Lotus: Bügel oben 0,91 m bei z −0,45; auf dem Foto liegt die Helmoberkante knapp unter dem Bügel, der Kopf ~27 cm davor → `seat` [−0,155, −0,08]
    (Helmmitte 0,77 m / z −0,18; vorher ragte der Helm 16 cm über den Bügel).
  - McLaren: Kopfstütze/Bügel 0,90 m bei z −0,05…−0,10 – der Helm (z −0,17) steckte darin. Jetzt davor und tief liegend: `seat` [−0,145, +0,33]
    (Helmmitte 0,76 m / z +0,16). Hinweis: Das Foto zeigt den MP4/5B (1990) mit höherer Airbox; Lage zur Kopfstütze und zum Cockpitausschnitt passt.
  - Ferrari: `seat` [−0,04, +0,12] (Helmmitte 0,79 m / z +0,05).
  - **Kein Eindringen** („Helm darf nicht klippen“): Karosseriepunkte (Stufe 0 samt Lenkrad/Radteilen) im Helm-Ellipsoid (94 % der Helmhülle) gezählt –
    McLaren +0,24: 646, +0,27: 401, +0,30: 147, **+0,33: 0** · Ferrari 0: 582, +0,04: 192, +0,08: 126, **+0,12: 0** · Lotus: 0.
  - Körper hängt jetzt am Auto statt an der vollen Detailstufe (vorher verschwand er ab 18 m, der Helm schwebte allein – „vom Anzug getrennt“).
  - Helmkamera folgt dem Kopf: Lotus [0,033, 0,745, 0,04, 2,6], McLaren [0,007, 0,735, 0,28, 1,2], Ferrari [0, 0,765, 0,17, 0,3]; TV McLaren 1,06 m.
  - Sichtbarkeit neu gemessen: Rumpf sichtbar Lotus 7.977, McLaren 9.050, Ferrari 7.216 von 13.939 Dreiecken.
- **Querlenker/Spurstangen biegen sich** beim Lenken (`histSplitWheels` → `parts.link`, `histLinkMat`): Teile bis 45 cm innen vom Rad, die nicht mit der
  Karosserie verbunden sind (kein gemeinsamer Punkt mit einem Dreieck, das aus der Zone hinausragt), bekommen je Eckpunkt ein Gewicht 0 (inneres Ende) … 1 (am Rad,
  geglättet). Der Vertex-Shader dreht jeden Punkt um die senkrechte Achse durch die Radmitte um Lenkwinkel × Gewicht (Uniform `m.linkU`, ein Programm für alle
  Kopien). Kein Abschneiden, keine Lücke, keine Rechenlast auf der CPU.
- **McLaren-Armaturen** (Foto des echten MP4/4): ganze Tafel 18 × 8,5 cm hinter dem Lenkrad (Ebene durch zwei Messpunkte der gewölbten Tafel, 1,5 cm davor) –
  gebogene Leuchtpunkt-Skala mit 9 0 1 2 3 4 5 6 (40 Punkte, leuchten mit der Drehzahl, oben rot), Lampen rot · FUEL · grün · rot, grüne Gang-Ziffer,
  runde Seitenlampen (Bremse/Schaltblitz), GCU, Tempo.
- **Ferrari**: Innenflanken der Reifen (zum Auto hin) einfarbig dunkel – die gespiegelte Schrift störte im Cockpit.

## v2.78 – McLaren: schwarze Kästen um die Logos (Rückmeldung 18.11.2026)
Die Logos des MP4/4 (Shell, Honda, Goodyear, 12, TAG Heuer, Barcode-Streifen) sind eigene Flächen über der Karosserie (691 Dreiecke, Material `Material_#1.005`).
Ihr Bogen ist im verkleinerten Modell ein JPEG mit schwarzem Hintergrund und das Material undurchsichtig → schwarze Kästen. Das 75-MB-Original liegt nur auf
dem Rechner des Nutzers. Behoben ohne Original: `tools/klassiker/aufkleber_alpha.py` macht das reine Schwarz (Wert 0), das mit dem Hintergrund zusammenhängt,
durchsichtig (die dunklen Logos haben Wert 24 und bleiben), speichert den Bogen als PNG und stellt das Material auf `MASK`. Laden mit `?v=2`.
Beim nächsten Neubau aus dem Original (`build_klassiker.py`) muss das wiederholt werden, falls das Original den Bogen ebenso ohne Deckkraft liefert.

## v2.79 – McLaren: Original-Aufkleberbogen vom Nutzer
Der Nutzer hat die Originaltexturen des MP4/4 geschickt (18.11.2026). Der Aufkleberbogen (`tools/klassiker/quellen/mclaren/aufkleber.png`, 1024², echte
Deckkraft, senkrecht gespiegelt gegenüber glTF) ersetzt mit `tools/klassiker/textur_ersetzen.py … --flip --mask` den Bogen aus v2.78 – doppelte Auflösung,
und das Innere des TAG-Heuer-Schilds ist jetzt durchsichtig (v2.78 hatte es als eingeschlossene Fläche schwarz gelassen). Laden mit `?v=3`.
- **Tacho-Beschriftung** (Original 512×256: BOOST, RADIO, FUEL, BRAKE …): im verkleinerten Modell gibt es dafür keine Texturfläche mehr – `build_klassiker.py`
  hat das Armaturenbrett in Eckpunktfarben umgewandelt (UVs weg). `Material_#59.003` ist NICHT der Tacho, sondern Pedale/Halter/Fußstützen, die ihre Farbe
  aus den Farbfeldern dieses Bilds nehmen (dort liegt auch das BOSS-Schild) – nicht ersetzen. Für die Beschriftung braucht es das Original-GLB (Neubau mit
  erhaltener Armaturen-Textur) oder eine eigene Fläche über dem Armaturenbrett.

## v2.80 – Ferrari F2004: schwarze Kästen hinter Logos
Gleiche Ursache wie beim McLaren: Im Original (`f2004.glb`, vom Nutzer als Archiv geschickt, nicht im Repo) ist `EXT_Sponsors.png` zu 39 % durchsichtig,
das Material aber `OPAQUE` → `build_klassiker.py` speicherte JPEG ohne Deckkraft. Ersetzt durch das Original (`tools/klassiker/quellen/ferrari/sponsoren.png`,
`textur_ersetzen.py … --mask`, gleiche Ausrichtung, nicht spiegeln). Laden mit `?v=2`. Sichtbar vor allem an der Nase (Vodafone, Olympus).
**Bau-Skript-Lehre:** `build_klassiker.py` sollte Deckkraft behalten, wenn das BILD durchsichtige Pixel hat – auch wenn das Material `OPAQUE` ist.
Die Bremssattel-/Detail-Logos (`EXT_Decal.png`) wurden beim Bau zu Eckpunktfarben und fehlen weiter.

## Drei weitere Klassiker: Ferrari 312 (1967), McLaren MP4/13 (1998), Red Bull RB8 (2012)
Wunsch des Nutzers (18.11.2026): „Genau so wie bei den anderen historischen Autos … nach den gleichen Regeln umgebaut.“ Modelle schon verkleinert
(`build_klassiker.py`, Reparaturen `vorbereiten.py`, siehe `modelle/klassiker/LIESMICH.md`), Fahrer und Daten in `modelle/klassiker/FAHRER.md`.

| Team (Schlüssel) | Auto | Fahrer | Bildfilter (`fx`) | Tacho (`gauge`) | Fahrleistung (Topspeed / Grip / Bremse / Beschl.) | Klang |
|---|---|---|---|---|---|---|
| Ferrari 1967 (`H_F67`) | Ferrari 312 | Chris Amon, #20 | 5 – Schwarz-Weiß-Film | 1 Rundinstrumente | 0,79 / 0,55 / 0,52 / 0,64 · 5 Gänge · 550 kg · 10.500/11.000 | `hist_f67` |
| McLaren 1998 (`H_MCL98`) | McLaren MP4/13 | Mika Häkkinen, #8 | 3 – SD-Fernsehbild | 3 Lenkrad-Display | 0,97 / 0,86 / 0,88 / 0,94 · 6 Gänge · 600 kg · 16.800/17.500 | `hist_fer` |
| Red Bull 2012 (`H_RBR`) | Red Bull RB8 | Sebastian Vettel, #1 | 4 – HD-Fernsehen | 3 Lenkrad-Display | 0,99 / 0,95 / 0,95 / 0,96 · 7 Gänge · 640 kg · 17.500/18.000 | `hist_rbr` |

Staffelung: RB8 knapp unter/gleichauf mit dem F2004 (1,00 / 0,94 / 0,95 / 0,97), MP4/13 darunter (Rillenreifen 1998: weniger Grip), 312 deutlich
unter dem Lotus 1970 (0,82 / 0,62 / 0,60 / 0,72: weniger PS je kg, schmale Reifen, keine Flügel). KERS des RB8 ist nicht nachgebildet (alle Klassiker ohne Boost).
Teamleiste: „Historisch“-Bereich jetzt nach Jahr sortiert (1967, 1970, 1988, 1998, 2004, 2012); Knopfbreite aus der Bildbreite gerechnet
(`(100vw − 190px) / 17`, 30–62 px), damit alle 17 Teams in eine Zeile passen.

### Gemessene Werte (`HIST_CAR`)
- **Lenkrad (`sw`)**: wie oben – Kasten um das Lenkrad, Auswahl grün eingefärbt, aus Cockpit, Seite und schräg oben angesehen (eigener kleiner
  Software-Renderer in Python statt Prüfseite), dann `inSw` genau wie `histPrep` angewendet und die Kranzpunkte als Ebene angepasst
  (312: zusätzlich Kreis im Raum, iterativ: R = 0,14 m, Rest 6 mm).

| Auto | Mitte c | Lenkachse a | r / ±t | rh / th | g | herausgelöst |
|---|---|---|---|---|---|---|
| 312 | 0 / 0,544 / 0,427 | 0 / −0,126 / 0,992 | 0,175 / 0,03 | 0,05 / 0,08 | 0,14 | 3.139 Dreiecke (rundes Holzlenkrad, 3 Speichen) |
| MP4/13 | 0 / 0,577 / 0,585 | 0 / −0,012 / 1 | 0,16 / 0,03 | 0,05 / 0,06 | 0,13 | 2.671 Dreiecke (Schmetterling, Kasten in der Mitte) |
| RB8 | 0 / 0,557 / 0,733 | 0 / −0,012 / 1 | 0,15 / 0,03 | 0,05 / 0,06 | 0,12 | 5.146 Dreiecke (Griffe, Tasten, Anzeigefeld oben) |

  Beim RB8 erfasst ein größerer Radius die Seitenwände des Cockpits (bei ±0,17 m) – deshalb r = 0,15. `swRot`: 312 1,2, MP4/13 und RB8 0,95.
- **Radachsen (`ax`)** mit `tools/klassiker/radachsen.py` (jetzt für alle sechs Modelle; die alten drei Werte unverändert): RB8 vorn 0,63° Spur
  (eingetragen), sonst alles unter 0,3° (nicht eingetragen). 312 vorn: Restabweichung 23 mm (gewölbte Lauffläche der Firestone-Reifen, keine Schieflage).
- **Sitz (`seat`)** nach den Fotos und der Eindring-Messung (Karosseriepunkte der Stufe 0 samt Lenkrad und Radteilen im Helm-Ellipsoid, 94 % der Helmhülle):
  - MP4/13: Foto = Helm direkt vor der Kopfstütze, Oberkante etwa auf Höhe der unteren Airbox-Kante, Helm knapp über dem Cockpitrand.
    z +0,28: 26 Punkte (Kopfstütze), +0,29: 0, **+0,30: 0** (1 cm Luft) → `seat` [−0,115, +0,30], Helmmitte 0,76 m / z +0,18.
  - RB8: Foto = Helm tief, nur die obere Hälfte schaut heraus. [−0,165, +0,39]: 3 Punkte (Kopfstützen-Polster bei z +0,10), [−0,185, +0,37]: 26,
    [−0,185, +0,38]: 13, **[−0,185, +0,39]: 0** → Helmmitte 0,69 m / z +0,27 (Cockpitrand dort 0,69–0,75 m).
  - 312: Foto = aufrecht, Helmoberkante etwa auf Höhe des Überrollbügels (0,857 m bei z −0,40), Kopf knapp davor. **`seat` [−0,135, −0,08]**:
    Helmmitte 0,74 m / z −0,20, Oberkante ~3 cm über dem Bügel, 0 Punkte im Helm (auch bei −0,12 und −0,115 frei).
    Schultern sind anders als auf dem Foto kaum zu sehen: der F1-Fahrer (`f1fahrer.bin`) liegt halb, und der Cockpitrand des Modells liegt am Fahrer bei 0,66 m.
  - Helmkamera folgt dem Kopf (Augen = Helmmitte −2,5 cm, +12 cm vor): 312 [0, 0,715, −0,08, 2,6], MP4/13 [0, 0,735, 0,30, 3,0], RB8 [0, 0,665, 0,39, 1,6]
    (4. Wert = Absenkung des Blickziels in 30 m; MP4/13 mit 1,6 lag das Lenkrad-Display am unteren Bildrand).
    TV-Höhe (`tvY`): 312 1,3 m, MP4/13 1,22 m (bei 1,1 m stand die Kamera in der Airbox, Oberkante 1,116 m), RB8 1,2 m (Bügel 1,09 m verdeckte das Bild).
  - Die Kameras in `extras.cams` der neuen Modelle sind Platzhalter [0, 0,85, 0, 0,3] – die Helmmitte rechnet vom Platzhalter-Augenpunkt aus.
- **Live-Instrumente (`HIST_DASH`)**: 312 drei Rundinstrumente im Armaturenbrett (Mitte Drehzahl Ø 8,2 cm, links Öl, rechts Wasser – gleiche Leinwand
  wie beim Lotus), Mitte/Normale aus den Ringpunkten der Instrumente; 1,6–1,8 cm davor, weil die modellierten Skalen-Zacken herausragen.
  MP4/13: Anzeige im Kasten der Lenkradmitte (7 × 4,8 cm, z 0,565). RB8: Anzeigefeld oben am Lenkrad (7,5 × 5,2 cm, z 0,73). Beide drehen mit dem Lenkrad.
- **Tacho entkoppelt**: `histGauge`/`histDashDraw` richten sich nach `HIST_CAR.gauge` (1 Rundinstrumente, 2 McLaren 1988, 3 Lenkrad-Display), nicht mehr nach `fx`.
- **Logos** (`tools/klassiker/logos.py`, jetzt einzeln aufrufbar: `python tools/klassiker/logos.py H_F67 H_MCL98 H_RBR`; nur `H_LOT` braucht cairosvg):
  `H_F67` Scuderia-Schild (aus der F2004-Textur, das 312-Modell hat kein Schild) in wärmerem, matterem Gelb; `H_MCL98` Mercedes-Stern aus der
  MP4/13-Textur über „McLaren“ mit rotem Speedmark-Bogen (gezeichnet, Schrift Inter/FreeSans – nachempfunden, kein Original-Logo);
  `H_RBR` Stiere mit Sonne und Schriftzug „Red Bull“ aus der RB8-Textur (Lack freigestellt).
- `fahrer_sicht.json` neu gemessen (jetzt sechs Autos, `?v=5`), siehe unten. GLB-Dateien laden mit `?v=1` (neu).

### Bildfilter (Finish-Shader, neue `uEra`-Stufen, kein eigener Durchgang)
4. **HD-Fernsehen 2012**: 720p-Eindruck – vier Abtastungen leicht weich, Helligkeit danach kräftig nachgeschärft (feine Säume wie bei Sendern),
   Farbe etwas weicher als Helligkeit; helle Flächen glühen (vier weitere Abtastungen im Abstand 0,6 % der Bildhöhe, nur über 0,75); Sendefarben
   kräftig und leicht übersättigt (1,22), Kontrast 1,07, kühler Weißabgleich (R 0,965, B 1,05). Nur bei Tempo sehr dezente 16×16-Blöcke
   (Stufen und Rauschen je Block, Stärke nach `uSpeed`). Keine Halbbilder (progressiv).
5. **Schwarz-Weiß-Film 1967**: Bildstand wackelt und leicht weich wie der Lotus-Film (gleiche Zweige), dann echtes Schwarzweiß ohne Sepia,
   Kontrast 1,15, flackernde Belichtung (±4 %), grobes Korn, Kratzer hell oder dunkel, Staub hell und dunkel, dunkle Ecken (bis −60 %).
Kosten: HD 8 zusätzliche Texturabfragen, S/W 4 (wie Film 1970) – nur wenn der Klassiker gefahren wird.

### Klang (keine neuen Aufnahmen – ElevenLabs kostet Geld)
- MP4/13 (Mercedes V10) nutzt `hist_fer` (Ferrari-V10-Aufnahmen) mit eigener Drehzahl (Schalten 16.800, höchstens 17.500).
- RB8 (Renault V8): `hist_rbr` = dieselben Aufnahmen mit 4 statt 5 Zündungen je Umdrehung → bei gleicher Drehzahl 20 % tiefer (V8-Lage).
- 312 (V12): `hist_f67` = dieselben Aufnahmen mit 6 Zündungen → bei 11.000/min derselbe Ton wie der V10 bei 13.200/min; Schaltlücke wie Lotus (H-Schaltung).
- Eigene Aufnahmen (Ferrari-V12 der 60er, Renault-V8 2012, Mercedes-V10 1998) wären möglich – vorher Kosten prüfen und fragen (CLAUDE.md).

### Sichtbarkeit des Fahrers (`fahrer_sicht.json`, neu gemessen)
Rumpf sichtbar (von 13.939 Dreiecken): 312 7.563 · MP4/13 6.934 · RB8 5.744 (tief im Cockpit). Lotus/McLaren 1988/F2004 unverändert (7.977 / 9.050 / 7.216).
Der Testbrowser durfte hier keinen lokalen Server starten – gemessen mit derselben Logik über die Datei-Umleitung von `tools/textur/spiel.js`
(`page.route`, Dateien direkt aus dem Projektordner); Ergebnis für die alten drei Autos bitgleich.

### Leistung (gemessen, `qc/perf-cam.js` mit 4 Stellen je Kamera, Monza, volles Feld, Software-Rendering im Testbrowser)
| | Gesamt Mittel / Spitze (Verfolger · Cockpit · TV) | eigenes Auto Cockpit / TV | Schattenkarte |
|---|---|---|---|
| Amon, 312 | 173 / 228 · 159 / 199 · 153 / 196 | 20 Aufrufe 59 Tsd. / 16 Aufrufe 45 Tsd. | 7–8 Aufrufe, 9–13 Tsd. |
| Vettel, RB8 | 183 / 238 · 172 / 218 · 169 / 211 | 28 Aufrufe 68 Tsd. / 29 Aufrufe 71 Tsd. | 8–9 Aufrufe, 9–13 Tsd. |
| Häkkinen, MP4/13 | 195 / 249 · 181 / 226 · 176 / 218 | 34 Aufrufe 77 Tsd. / 34 Aufrufe 81 Tsd. | 12–13 Aufrufe, 9–13 Tsd. |
312 und RB8 wurden vor der neuen Sichtbarkeitsliste gemessen (Fahrer noch vollständig, ~14.000 Dreiecke) – im Spiel jetzt etwas weniger Dreiecke.
Mehr Aufrufe als beim F2004 (22/23) beim RB8: Stufe 0 hat 15 Materialien, dazu Lenkrad, Display, Fahrer, Helm und je Rad die zerlegten Teile.
Shader-Programme nach allen Kamerawechseln: 312 124, RB8 119 (ein Vorher-/Nachher-Vergleich je Kamerawechsel wurde nicht gemessen – QC „Nachladen“ steht noch aus).
Das MP4/13 ist das schwerste Klassiker-Modell (Stufe 0: 21 Zeichenaufrufe, Stufe 2 für den Schatten 12) – alle Werte bleiben weit unter den
Grenzen (450 Aufrufe, 1,2 Mio. Dreiecke). Verbesserung beim nächsten Neubau: Materialien in `build_klassiker.py` zusammenfassen.

### Geprüft (Testbrowser, Monza)
Showroom (schräg vorn, Seite), Verfolger-, Helm- und TV-Kamera, Lenkung voll links/rechts: Lenkrad dreht mit, Hände am Kranz, Display bzw.
Rundinstrumente laufen mit. Sitz verglichen mit den Fotos (`tools/klassiker/quellen/sitz/`): MP4/13 Helm vor der Kopfstütze, knapp über dem Rand;
RB8 tief, obere Helmhälfte sichtbar; 312 Helm ganz über dem Rand, Oberkante ~ Bügelhöhe.
Skripte (Arbeitskopien, nicht im Repo): Python-Renderer für die Lenkrad-/Sitz-/Armaturenbilder, Eindring-Messung und Rennaufnahmen über `tools/textur/spiel.js`.

### Offen
- Amon fuhr 1967 einen **offenen Helm mit Brille** – das Spiel hat nur geschlossene Helme (eigene Helmform wäre nötig). Helmfarbe unsicher (siehe FAHRER.md).
- 312: Auf dem Foto sind Schultern und Oberkörper zu sehen; mit dem halb liegenden F1-Fahrer und dem Cockpitrand des Modells (0,66 m) nur Helm und Arme.
  Höher setzen würde den Helm über den Bügel heben (Foto: Oberkante etwa auf Bügelhöhe) – bewusst so gelassen. Eine aufrechte Sitzhaltung wäre ein eigener Fahrer.
- RB8: KERS (+80 PS) nicht nachgebildet. Vettels Helm 2012 nur als Mittelwert der wechselnden Designs.
- `H_MCL98`-Logo ist nachempfunden (Stern aus der Textur, Schrift/Speedmark gezeichnet) – das Original-Teamlogo 1998 liegt nicht als Datei vor.
- Eigene Motoraufnahmen (V12 1967, V10 1998, V8 2012) wären möglich (Kosten vorher prüfen).

### Bilder (Testbrowser)
![[bilder/klassiker_neu_filter.jpg]]
(oben Verfolgerkamera: 312 mit Schwarz-Weiß-Film, MP4/13 mit SD-Bild, RB8 mit HD-Bild; unten Showroom)

![[bilder/klassiker_neu_cockpit.jpg]]
(Helmkamera geradeaus und mit Einschlag: 312 mit Live-Rundinstrumenten, MP4/13 und RB8 mit Lenkrad-Display)

### v2.87: Helmkamera Ferrari 312 und Red Bull RB8 höher (Wunsch 18.11.2026)
Vorher sah man fast nur Cockpit bzw. Lenkrad, kaum Horizont und Straße. `HIST_CAR.ck` = [x, Augenhöhe, z, Absenkung des Blickziels auf 30 m]:
- Ferrari 312: [0, 0,715, −0,08, 2,6] → **[0, 0,80, −0,08, 1,3]**
- Red Bull RB8: [0, 0,665, 0,39, 1,6] → **[0, 0,74, 0,39, 0,8]**
Geprüft wurde jeweils der alte Wert gegen zwei neue Varianten (Bilder `bilder/helmkamera_312.jpg`, `bilder/helmkamera_rb8.jpg`: alt | a | b). Übernommen ist Variante a: Instrumente bzw. Lenkrad-Display bleiben im Bild.
Werkzeug: Kopie von `rennen.js` mit Feld `ck` je Aufnahme, das `pl.mesh.cam` im laufenden Rennen überschreibt.

### McLaren MP4/13: Maßstab geprüft (Frage 18.11.2026, „Helm zu klein?“)
- Modell: Radstand 3,02 m, Raddurchmesser 0,65 m, Spur vorn 1,56 m und hinten 1,33 m (jeweils Radmitte).
- Echt ([F1Technical](https://f1technical.net/f1db/cars/810/mclaren-mp4-13), [Ultimatecarpage](https://www.ultimatecarpage.com/spec/356/McLaren-MP4-13-Mercedes.html)): Radstand 2.985–3.060 mm, Länge ≈ 4.550 mm, Spur vorn 1.410–1.492 mm und hinten 1.397–1.412 mm. Die Spurwerte sind vermutlich von Radmitte zu Radmitte gemessen.
- Länge und Radstand stimmen. Die Spur ist vorn etwa 6 cm zu breit und hinten etwa 7 cm zu schmal. Die Fahrzeuggröße wirkt sich darauf nicht aus.
- Helm im Verhältnis zum Radstand: im Spiel 0,12, auf dem Referenzfoto (`quellen/sitz/mclaren_mp413_haekkinen.png`) etwa 0,09. Der Helm ist also eher etwas zu groß als zu klein, deshalb wurde nichts geändert.

## v2.88: „Legenden“, synthetische Motoren, Reifen, Fahrer-Durchdringung, Showroom (Rückmeldungen 18.11.2026)

### Legenden in der Teamleiste
- „Historisch“ heißt jetzt **„Legenden“** (Trenner, Schild in der Teaminfo, Tooltip).
- Die aktuellen Teams stehen mittig. Ganz rechts schaut **genau eine Legende** (Trenner + Ferrari 1967) ins Bild, die übrigen erreicht man durch Wischen oder mit dem Mausrad.
  - Umsetzung: `.tmnow` min-width `100 % − Knopfbreite − 40 px`, Knopfbreite als `--tw`.
  - v2.89: Der Knopf „Legenden ›“ aus v2.88 ist entfernt. Er verdeckte das letzte Team (Rückmeldung 18.11.2026: „soll nichts verdecken, rechts nur ein Auto sehen und für die anderen wischen“).
- Ist eine Legende gewählt, scrollt die Leiste beim Aufbau zu ihr.
- Knopfbreite `(100vw − 190px)/13`, weil nur noch die aktuellen Teams in die Breite passen müssen.
- Bild: `bilder/teamleiste_legenden.png` (1280 und 844 px, jeweils Anfang und ganz nach rechts gewischt).

### Motorklang: synthetisch, für alle sechs Legenden
Wunsch: synthetische, passende Klänge. Außerdem hieß es: „RB8 klingt falsch bei hohem Tempo“ und „alle Autos klingen bei max. Drehzahl falsch“.
- **Neu:** `tools/sounds/synth_klassiker.py` berechnet je Motor 5–7 nahtlose Schleifen konstanter Drehzahl (2 s, 32 kHz). Die oberste Stufe liegt genau auf der Höchstdrehzahl. Dazu kommt eine Schleife für „Gas weg“.
- **Modell:**
  - Auspuffstoß je Zündung an seiner Stelle im Arbeitsspiel, mit fester Streuung je Zylinder (ergibt Unterordnungen und das „Raue“).
  - Resonanzen auf der Zündfrequenz und ihren Vielfachen, dazu feste Rohr-Resonanzen in Hz.
  - Rauschen im Zündtakt.
  - Honda-Turbo zusätzlich gedämpft, mit Laderpfeifen und Zischen.
  - Schub: Aussetzer und Knallen.
- **Motoren:** Ferrari V12 (6 Zündungen/U), Cosworth DFV V8 (4), Honda V6 Turbo (3), Ferrari V10 (5), Mercedes V10 (5), Renault V8 (4).
- **Geprüft (gerechnet im Testbrowser, `snd2.js`):** Zwischen 4.000/min und Höchstdrehzahl wird jede Stufe nur 0,86–1,17-fach nachgestimmt. Alle Dateien laden.
  - Vorher wurde der RB8 aus V10-Aufnahmen mit 0,7-fach verlangsamter oberster Stufe gespielt. Der MP4/13 nutzte die Ferrari-Aufnahmen.
- **Begrenzer (alle Autos, auch F1/F2):** Vorher lief die Drehzahl im Windschatten über Vmax bis zu 1.200/min über die Höchstdrehzahl (F1 bis 13.200), die Aufnahmen wurden entsprechend hochgestimmt.
  - Jetzt endet `gearInfo`/`histGear` bei der Höchstdrehzahl (`over: true`), und die Drehzahl sägt knapp darunter (13 Hz, 220–280/min).
  - Das Hochdrehen am Start folgt bei den Legenden ihrer eigenen Höchstdrehzahl.
- **Alte Aufnahmen:** Die ElevenLabs-Aufnahmen `hist_*_mittel/hoch.wav` bleiben im Ordner, werden aber nicht mehr geladen. `hist_lot/mcl/fer_schub.wav` sind durch die synthetischen ersetzt.
- **Nicht geprüft:** Ein echter Mitschnitt im Rennen. Der Testbrowser blieb beim zweiten Rennstart hängen, deshalb wurden nur Stufen, Tempo und Dateien rechnerisch geprüft. Gehört habe ich die Klänge nicht.
- Weitere Klangstufen und Hörproben: `python tools/sounds/synth_klassiker.py [kürzel …] --probe` schreibt `tools/sounds/.probe/<kürzel>_stufen.wav`.

### McLaren MP4/4: Reifen „eiern“
- **Ursache:** Die UVs der Flanke waren gekachelt und schief (u 0…2, v −1…0). Der Schriftzug lief beim Drehen nicht rund um die Achse.
- **Lösung:** `tools/klassiker/reifen_planar.py <glb> "<Material>"`.
  - Ebene Abbildung exakt um die Radachse.
  - Linke Räder sind gespiegelt, damit die Schrift auf **beiden** Wagenseiten außen lesbar ist.
  - Neues zentriertes Flankenbild in 1024 px, radial aus dem Original umgelegt. Der Innenkreis wird gemessen, der Felgenrand (0,554 R) aus dem Modell.
  - Die Lauffläche ist einfarbig, der Sampler klemmt am Rand.
- Gilt für Stufe 0 und 1. Modell-Version `mclaren_mp44: 4`. Bild: `bilder/mp44_reifen.jpg`, Flankenbild `tools/klassiker/quellen/mclaren/flanke_zentriert.png`.

### Fahrerfigur ragt unten aus dem Auto (Ferrari 312, Lotus, McLaren, alle)
- `tools/klassiker/fahrer_clip_export.js` exportiert Auto- und Fahrerdreiecke. Danach prüft `tools/klassiker/fahrer_clip.py` jedes sichtbare Rumpf-Dreieck: Ein Voxelgitter der Karosserie (1 cm) und 33 Strahlen in die untere Halbkugel zeigen, ob das Dreieck nach unten frei liegt. Wenn ja, ragt es aus dem Boden und fällt weg.
- Das gilt nur unterhalb 0,3 m. Darüber ragen beim Lotus die Schultern seitlich aus dem engen Cockpit; würden sie entfernt, entstünden Löcher.
- **Entfernt:**

| Auto | Dreiecke |
|---|---|
| Ferrari 312 | 1.146 |
| Red Bull RB8 | 721 |
| McLaren MP4/13 | 410 |
| Lotus | 387 |
| McLaren MP4/4 | 186 |
| Ferrari F2004 | 98 |

- `fahrer_sicht.json?v=6`. Bild von unten und von der Seite: `bilder/fahrer_unten.jpg`.

### Showroom: Wechsel ohne Hakler
- `showroomPreload()` läuft nach dem Start im Leerlauf. Es lädt alle Legenden-Modelle, baut je Team einmal ein Showroom-Auto und übersetzt die Shader vorab (`renderer.compileAsync`).
- Vorher wurde ein Klassiker erst beim Anklicken geladen: zuerst ein Platzhalter, danach wurde der Showroom neu gebaut.
- Messung im Testbrowser (Software-Rendering, daher nur die Zahl neuer Shader aussagekräftig): Nach dem Vorladen entstehen beim Durchklicken aller 17 Teams 0–1 neue Programme je Team. Vorher waren es bis zu 6, und die Legenden mussten erst laden.
- Abschalten zum Testen: `window.__noPre = true`.

### Weitere Korrekturen
- **Unschärfe blieb stehen:** Wurde während des Kamera-Schwenks beim Teamwechsel schon ein Auto/Fahrer gewählt, blieb die Bewegungsunschärfe auf dem Bild. Jetzt wird der Schwenk beim Verlassen der Teamwahl beendet und der Filter zurückgesetzt, auch beim Rennstart.
- **Musikregler:** Die Lautstärke folgt jetzt sofort (`musSnap`). Vorher blendete die Menümusik ~1 s und die Rennmusik bis zu 3 s nach, deshalb ging die Musik beim Herunterziehen nur verspätet aus.

## Entwurf Teamleiste/Legenden (18.11.2026, zur Abnahme, noch nicht eingebaut)

Rückmeldung zu v2.89: Auch die Lösung mit einer rechts angeschnittenen Legende gefällt nicht. Gewünscht ist ein schöneres UI für die Legenden. Jede Legende soll Jahr, Auto und Fahrer zeigen, beim Lotus nur **Emerson Fittipaldi**.

Das Bild `docs/bilder/teamleiste_entwuerfe.jpg` zeigt oben 1280 px und unten 844 px Breite, jeweils links den Start und rechts die geöffneten Legenden.

- **Entwurf C, Umschalter in der Leiste (Empfehlung):**
  - Links in der Teamleiste sitzt ein kleiner Umschalter mit „2026 Saison“ und „★ Legenden“. Er hat die Höhe einer Kachel und folgt dem Stil der oberen Schrittleiste: dunkles Glas, aktiver Eintrag mit rotem Balken.
  - „Legenden“ tauscht den Inhalt der Leiste aus: Statt der elf Teamkacheln erscheinen sechs breitere Goldkarten mit großem Jahr, Auto und Fahrer sowie dem Logo klein oben rechts.
  - Es gibt kein Scrollen und nichts liegt über dem Auto.
- **Entwurf B, Legenden-Kachel:**
  - Am Ende der Teamreihe steht eine goldene Kachel „★ Legenden“.
  - Nach dem Antippen zeigt die Leiste die Legendenkarten und vorne eine Kachel „‹ 2026“ für den Rückweg.
- **Verworfen, Entwurf A:** Ein schwebender Pillen-Umschalter über der Leiste. Er lag auf dem Auto, und Position und Design gefielen nicht.

Schreibweise auf den Karten (Wunsch): Initiale des Vornamens mit Punkt, dann der ausgeschriebene Nachname, also C. Amon, J. Rindt, A. Senna, M. Häkkinen, M. Schumacher und S. Vettel.

Frage „Oder war Rindt berühmter bei dem Auto?“: Ja.
- Rindt gewann 1970 im 49C den Großen Preis von Monaco, mit dem berühmten Überholen von Brabham in der letzten Runde. 1970 wurde er postum Weltmeister.
- Fittipaldi fuhr den 49C 1970 nur in seinen ersten Rennen. Seinen ersten Sieg holte er im Lotus 72.
- Empfehlung: Rindt bleibt, wie bisher im Spiel. Im Entwurf steht deshalb „J. Rindt“.

Im Spiel fährt der Lotus derzeit Jochen Rindt (`RIN` in index.html, Helmfarben nach FAHRER.md). Für Fittipaldi müssen beim Einbau auch Fahrereintrag und Helm geändert werden.

Das Mockup entsteht nur per DOM-Einspritzung im echten Spiel, mit `node tools/klassiker/teamleiste_entwurf.js` aus dem Scratch-Ordner (schreibt `mk_*.png`).

## v2.90 – MP4/4: „Shell“ und „Honda“ vorn abgeschnitten
Die Aufkleber-Flächen (`Material_#1.005`) liegen an der Seitenkastenwölbung stellenweise minimal unter der Karosserie. Dadurch fehlte vom „S“ in „Shell“ der vordere Teil, ebenso vorn ein Stück von „Honda“.
- **Lösung:** `HIST_CAR.H_MCL.decal = ['Material_#1.005']`. histPrep gibt diesen Materialien einen Tiefenversatz (polygonOffset −4/−8), damit die Aufkleber vor der Karosserie liegen.
- Das Feld gilt allgemein: Andere Legenden mit demselben Fehler bekommen nur einen Eintrag in `decal`.
- Geprüft im Showroom per Ausschnitt-Vergleich.

## v2.90 – Teamleiste Entwurf C eingebaut (Go des Nutzers 18.11.2026)
- **Umschalter:** Links in der Teamleiste sitzt ein Umschalter `.tmtabs` mit „<Jahr> Saison / ★ Legenden“ (`MENU.leg`).
- **Legendenansicht:** „Legenden“ ersetzt die Teamkacheln durch Goldkarten `.tm.hist.lcard`. Jede Karte zeigt das Jahr, das Auto (`HIST_CAR.title`) und den Fahrer als „A. Senna“. Der Inhalt ist mittig (Wunsch), das Logo sitzt klein oben rechts.
- **Umschalten:** Ein Wechsel wählt sofort das zuletzt gewählte Auto der jeweiligen Gruppe (`MENU.lastLeg` bzw. `MENU.lastNow`).
- **Synchron:** Die Ansicht folgt immer dem gewählten Auto. renderMenu baut die Leiste neu, wenn `MENU.leg` nicht mehr dazu passt.
- **Karriere:** Dort gibt es keine Legenden und deshalb auch keinen Umschalter.
- **Entfernt:** Die v2.88/89-Lösung (`.tmnow`, `.tmsep`, `hasLeg`, Legenden rechts außerhalb des Bildes).
- **Arbeitsregel neu (CLAUDE.md):** Bei Design-Fragen erst einen Entwurf zur Abnahme schicken und auf das Go warten.

## Entwurf LED-Wand für Legenden (zur Abnahme, noch nicht eingebaut)
Bild: `docs/bilder/ledwand_legenden_entwuerfe.jpg`. Oben die heutige Wand, links Entwurf 1, rechts Entwurf 2, jeweils mit McLaren 1988 und Ferrari 1967. Mockup-Skript: `tools/klassiker/ledwand_entwurf.js` (ersetzt `wallDraw` im laufenden Spiel).
- **Sichtbarer Wandausschnitt** in der Teamwahl, gemessen per Raycast: Leinwand x ≈ 450…880 und y ≈ 225…320 von 1024×320, Bildmitte bei x ≈ 630. Alles, was gelesen werden soll, muss in diesem Fenster liegen.
- **Entwurf 1 „Archiv“:**
  - Hintergrund in warmem Sepia, mit schrägen Streifen in den Teamfarben, die ins Sepia gezogen sind.
  - In der Mitte das Jahr als große goldene Konturzahl.
  - Links daneben das Auto, rechts der Fahrer, jeweils unterstrichen.
  - Oben ein Filmstreifen mit Lochung, dazu Filmkorn.
- **Entwurf 2 „Fallblatt-Tafel“:**
  - Schwarze Klappziffern wie bei alten Zeitnahme-Tafeln.
  - Vier Zeilen: LEGENDE, Jahr, Auto, Fahrer (Fahrer in Gelb).
  - Ein Band in den Teamfarben am linken Rand.
  - Die Zeichen blättern beim Wechsel durch, bevor sie stehen bleiben.

## Smartphone-Prüfung der Teamleiste (18.11.2026, Entwurf zur Abnahme)
Wunsch: „mit dem UI-Smartphone-Skill prüfen“. Einen solchen Skill gibt es nicht, weder im Projekt noch unter den Skills des Nutzers. Stattdessen hat ein unabhängiger Prüfer die Leiste aus Sicht von Smartphone-UI/UX bewertet. Grundlage waren Screenshots auf iPhone SE (667×375), Galaxy S23 (780×360), iPhone 15 (852×393) und einem großen Android-Gerät (915×412).

**Befunde, nach Schwere:**
1. **Umschalter zu klein:** Die Knöpfe sind nur 17–26 px hoch, empfohlen sind 44 pt (Apple) bzw. 48 dp (Android). Die Schrift ist 8 px groß, und das rote „2026“ ist mit Deckkraft 0,6 kaum lesbar.
2. **Teamkacheln zu klein:** Auf dem SE 37 px, auf dem S23 44 px, mit nur 6 px Abstand. Das führt zu Fehltipps.
3. **Legendenkarten auf dem SE abgeschnitten:** Die Fahrerzeile wird halb abgeschnitten, „MCLAREN MP4/13“ läuft über.
4. **Gequetschte Karten:** Die Karten sind gleich hoch wie die Logo-Kacheln, obwohl sie dreimal so viel Text tragen.
5. **Safe-Areas:** Nicht berücksichtigt (Notch links, Home-Indikator unten).
6. **Schrift zu klein:** Fahrernamen 7,5 px, Kopf-Unterzeile 10,5 px.
7. **Aktive Kachel kaum erkennbar:** Dazu sind die Logos von Aston Martin und Cadillac zu dunkel.

**Entwurf** (Bild `docs/bilder/teamleiste_handy_entwurf.jpg`, links vorher, rechts Entwurf; Skript `tools/klassiker/teamleiste_handy_entwurf.js`):
- **Umschalter:** Je Knopf 28–33 px hoch, Tippfläche nach außen erweitert, Schrift 10–12 px. Das Jahr ist immer voll deckend, beim Wischen bleibt der Umschalter links stehen (sticky).
- **Kacheln:** Mindestens 44 px groß, 8 px Abstand. Lange Reihen werden gewischt statt geschrumpft, mit Einrasten und einem Ausblendverlauf rechts als Hinweis.
- **Legendenkarten:** Mindestens 58 px hoch und 112 px breit, Jahr 17–22 px, Auto und Fahrer 9–11,5 px, Ellipse statt Abschneiden.
- **Aktive Kachel bzw. Karte:** 3 px angehoben, kräftigere Unterkante, Glühen in Team- bzw. Goldfarbe. Inaktive Kacheln leicht gedimmt, Logos heller.
- **Safe-Areas und Kopf:** Seitenabstand mit `env(safe-area-inset-*)`. Kopf-Unterzeile 11,5 px, die Technikzeile fällt bei Höhe unter 380 px weg.

**Kompromiss:** Auf dem SE passen nicht mehr alle 11 Teams bzw. 6 Legenden ins Bild, der Rest wird gewischt.

## v2.91 – LED-Wand „Archiv“ für Legenden eingebaut (Go: „Led Entwurf 1 nehmen“)
- `wallDrawLegend(now, W, H)` zeichnet die Wand, sobald das Team der Wand (`W.team`, gesetzt in showroomWall) eine Legende ist. Die übrigen Teams behalten die bisherige Wand.
- **Inhalt:** Sepia-Hintergrund, Teamfarben-Streifen (pendeln langsam), Jahr als goldene Konturzahl (blendet in 0,7 s ein), links das Auto, rechts der Fahrer.
- **Effekte:** Ein Filmstreifen mit laufender Lochung, Filmkorn aus einer vorberechneten 256×96-Fläche (je Bild verschoben, ohne getImageData) und leichtes Projektorflackern.
- **Lage:** Die Inhalte sitzen im gemessenen sichtbaren Ausschnitt. In der Teamwahl liegt die Mitte bei Leinwand-x 630, in der Fahrerwahl auf der zweiten Wand bei x 465.
- **Getestet:** Teamwahl (McLaren, Lotus), Fahrerwahl (Lotus) und Rückwechsel zu Mercedes (alte Wand). Keine Seitenfehler.
- **Bild:** `docs/bilder/ledwand_legenden.jpg`.
- **Offen:** Der Handy-Entwurf der Teamleiste (siehe oben) wartet noch auf ein eigenes Go.

## v2.92 – Smartphone-Überarbeitung der Teamleiste eingebaut (Go 19.11.2026)
- **Übernahme:** Der Entwurf aus der „Smartphone-Prüfung“ ist 1:1 übernommen, als eigener CSS-Block nach `#scrTeam .tbig`.
- **Auswahl sichtbar:** renderTeams holt die gewählte Kachel bzw. Karte nach jedem Neuaufbau ins Bild (`teamsScrollTo`), weil die Reihe auf kleinen Handys jetzt breiter als der Bildschirm sein kann.
- **Gemessene Größen:**

  | Gerät | Umschalter-Knopf | Legendenkarte |
  |---|---|---|
  | iPhone SE / Galaxy S23 | 103×28 | 112×58 |
  | iPhone 15 | 104×32 | 112×66 |
  | Desktop 1280×640 | 117×39 | 158×81 |

- **Bild:** `docs/bilder/teamleiste_handy_v292.jpg`. Die drei Zeilen sind iPhone SE, Galaxy S23 und iPhone 15, jeweils links Saison und rechts Legenden.

## Teamwahl nach Smartphone-Vorlage (19.11.2026, Entwurf zur Abnahme)
Rückmeldung zu v2.92: Auswahl und Umschalter unten gefallen auf dem Handy nicht. Wunsch: Einen UI-Skill für Smartphones suchen und daraus eine Vorlage ableiten.

**Gefundene Skills** (Katalog, alle noch nicht installiert, dem Nutzer zum Hinzufügen gezeigt):
- „Mobile Design System“ (Material 3 / Apple HIG)
- „frontend-design“ (Anthropic)
- „Design“ (Anthropic: Design-Kritik, Barrierefreiheit)

**Gelesen und als Vorlage genutzt:**
- Die öffentliche Anleitung des „frontend-design“-Skills: erst einen Designplan machen, Generisches vermeiden, sparsam animieren, Texte nur, wo sie helfen.
- Die Apple Human Interface Guidelines zu Segmented Controls: Sie wechseln die Ansicht desselben Inhalts und stehen **oben unter der Navigation**, nicht unten in Konkurrenz zur Leiste. Höchstens etwa fünf Segmente, Tippflächen mindestens 44 pt.
- Dazu das typische Muster aus Handy-Rennspielen: Man blättert am Auto selbst, mit Pfeilen links und rechts und durch Wischen. Unten bleibt nur eine schlanke Positionsanzeige.

**Entwürfe** (Bild `docs/bilder/teamwahl_handy_hig_entwuerfe.jpg`, Skript `tools/klassiker/teamwahl_hig_entwurf.js`):
- **Gemeinsam:**
  - Segment-Umschalter „Saison 2026 | ★ Legenden“ oben neben „Team wählen“, je Segment 112×38 px. Legenden aktiv = Gold.
  - Runde Pfeilknöpfe (48 px) links und rechts neben dem Auto, Wischen über das Auto blättert ebenfalls.
  - Team- bzw. Legendenname mit Fahrern zentriert unter dem Auto. Die Kopfinfo links oben entfällt.
- **A „Logo-Dock“:** Unten links ein schlankes Dock mit allen Logos (44 px hoch) zum direkten Springen. Bei Legenden stehen die Jahreszahlen unter den Logos.
- **B „Punkte“:** Unten nur Seitenpunkte, der aktive Punkt ist breit, bei Legenden in Gold. Gewählt wird ausschließlich über Pfeile und Wischen, das ist die ruhigste Variante.
- **Wahl des Nutzers (21.11.2026): „A central“.** Gemeint ist Entwurf A mit dem Logo-Dock mittig unten.
  - Auf schmalen Handys (≤ 760 px, z. B. iPhone SE) würde das mittige Dock den WEITER-Knopf überdecken. Dort wird WEITER deshalb zu einem kompakten roten Pfeilknopf (52 px).
  - Neuer Entwurf: `docs/bilder/teamwahl_handy_A_mittig.jpg`. Er wartet auf das Go.

## Neustart 21.11.2026: nur der Umschalter Saison/Legenden fürs Handy (Entwurf zur Abnahme)
Der angefangene Umbau v2.93 (Entwurf A mit Pfeilen und Logo-Dock) wurde auf Wunsch verworfen und nie gepusht. Stand im Spiel bleibt v2.92. Neuer Auftrag: Nur der Umschalter zwischen Legenden und 2026 soll fürs Handy angepasst werden, der Rest der Leiste bleibt.

Bild: `docs/bilder/umschalter_handy_entwuerfe.jpg`. Zeilen 1 und 3 zeigen Entwurf 1, Zeilen 2 und 4 Entwurf 2, jeweils iPhone SE bzw. iPhone 15, links Saison und rechts Legenden. Skript: `tools/klassiker/umschalter_entwurf.js`.
- **Entwurf 1 „Segment oben“:**
  - Nach Apple HIG oben neben „Team wählen“, unter der Navigation.
  - Zwei Segmente je 112×38 px. Aktiv ist weiß bzw. bei Legenden gold.
  - Die Leiste unten enthält nur noch die Teams bzw. Karten.
- **Entwurf 2 „Reiter über der Leiste“:**
  - Zwei Reiter (36 px hoch) sitzen direkt auf der Leiste, linksbündig.
  - Aktiv ist dunkel mit rotem Strich oben, bei Legenden gold.
  - Umschalter und Auswahl bleiben zusammen unten, wo der Daumen ist.
- **Umgesetzt als v2.93 (Go „Entwurf 1“, 21.11.2026):** `#teamSeg` (`.tmseg`) im `#scrTeam`, fest oben mittig unter der Schrittleiste.
  - **Größe:** Je Segment 112×38 px, Tippfläche über `::after` auf 46 px Höhe erweitert.
  - **Entfernt:** Der alte Kasten `.tmtabs` in der Leiste samt CSS.
  - **Verhalten:** Wie bisher (`MENU.leg`, zuletzt gewähltes Auto je Gruppe). In der Karriere bleibt das Segment ausgeblendet.
  - **Getestet:** iPhone SE, iPhone 15 und Desktop, Umschalten in beide Richtungen, keine Seitenfehler. Bild: `docs/bilder/umschalter_v293.jpg`.

## v2.94 – Legenden unten mittig (Wunsch 21.11.2026)
- **Kartenbreite:** `min(2,55 × --tw, (100 % − 40 px) / 6)`, gerechnet aus der Leistenbreite (`.teamwrap` hat seitliche Ränder, daher nicht aus `100vw`). Alle sechs Legenden passen auch aufs iPhone SE und stehen mittig, ohne Wischen.
- **Ohne Verlauf:** Der Ausblendverlauf rechts gilt in der Legenden-Ansicht nicht mehr.
- **Bild:** `docs/bilder/legenden_mittig_v294.jpg` (iPhone SE, iPhone 15, Desktop).

## v3.02 – McLaren MP4/13: „Reifentexturen eiern“ (Rückmeldung 25.11.2026)

- **Befund:** Der Reifen des MP4/13 hat keine Textur, sondern Eckenfarben (`farbe_lack_matt`). Auf der Flanke (55–80 % des Radius) lagen dort helle Flecken
  (Werte bis 84 von 255, sonst 0) – Reste der weißen Reifenbeschriftung des Originals, auf das grobe Netz gebacken. Beim Drehen liefen die unregelmäßigen Flecken
  sichtbar um die Achse. Die Felge selbst (Bild `rim.png`) sitzt mittig.
- **Lösung:** `python3 tools/klassiker/reifen_einfarbig.py modelle/klassiker/mclaren_mp413.glb` setzt alle Ecken des Reifens (ab 55 % des Radius, 6.622 Ecken in den
  12 Rad-Netzen aller Detailstufen) auf ein gleichmäßiges, sehr dunkles Grau (9/255). Felge und Nabe bleiben. Die Datei wird an Ort und Stelle geändert (gleiche Größe).
- Modell-Version in `index.html`: `mclaren_mp413: 2` (Abruf mit `?v=2`).
- Geprüft im Testbrowser: Vorderrad aus 1,5 m in mehreren Drehstellungen – Flanke gleichmäßig dunkel, keine wandernden Flecken mehr.
- Wird das Modell neu erzeugt, das Werkzeug danach wieder ausführen (wie `reifen_planar.py` beim MP4/4).
