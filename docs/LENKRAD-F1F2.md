# F1/F2-Lenkrad und Griff (v1.73)

Stand: 14.11.2026 – Umbau nach Referenzbildern. Endgültiges Vorbild: **Ferrari-Lenkrad Prototyp 2026** (Abu Dhabi FP1), Schwerpunkt **Form und Griffe**.
Zwischenschritte (verworfen): eigenes „2024/25“-Design, dann Alpine 2024 (ovale Grifflöcher).
Zugehörig: [[FAHRER-MODELL]] (Fahrer, Hände, Arm-IK).

## Form (Ferrari 2026)
- Breites Carbon-Mittelteil, Oberkante gerade mit LED-Schaltleiste über dem großen Display, runde obere Ecken über den Schlitzen.
- **Griffe**: lang, gummiert, fast senkrecht (oben leicht nach innen), **unten frei** mit rundem, etwas schlankerem Ende (leicht nach innen-vorn gebogen), oben als **Ohr** nach innen gebogen und verjüngt in die Oberkante laufend. Zwischen Griff und Mittelteil ein nach unten offener Schlitz (dort liegen die Fingerspitzen).
- Bedienelemente: Tasten N (grün) und P (rot), je eine blaue darüber, rote Taste und K1 (gelb) neben der LED-Leiste, OK (blau) und eine kleine orange unter dem Display, Beschriftungsfelder (MID/EB), Walzenschalter an den Schlitzkanten (BMIG/BBAL weiß, darunter gelb), **drei große Drehschalter in einer Reihe** mit farbigen Rastfeldern (links/rechts schwarzer Zeigerknebel, Mitte gelbe Scheibe), Schalt- und Kupplungswippen und Nabe hinten.

## Ausgangslage (gemessen)
- Die Faust der Fahrerhand in `f1fahrer.bin` ist eine **um ~20° gekippte** freie Röhre (oben zum Fahrer, leicht nach außen):
  Mitte lokal (0,1939 / −0,0161 / 0,0380), Richtung (0,1375 / 0,9331 / 0,3324), Radius 3,1 cm lokal (= 2,4 cm Welt) über ±7 cm. Offen zur Innen-/Fahrerseite (Handfläche außen, Finger vorn herum, Spitzen innen-vorn).
- Altes Lenkrad: Zeigefinger lief durch die Griffschlaufe, Fingerspitzen im Mittelteil.
- Arm-IK für F1/F2: Hände folgten dem Lenkrad nur zu 80 % (Faust bis 3 cm neben dem Griff) und drehten um einen 1 cm versetzten Punkt (bis 6 mm Wandern).
- Cockpitrand des Automodells (F1 x ±0,16, F2 ±0,18, mit Lippe nach unten) lag in Griffhöhe → Griffe und Fäuste steckten darin (Außenansicht); F1 zusätzlich ein Reststück der alten Abdeckplatte (y 0,576) in der Öffnung; F2-Lenksäule (dünner Kegel) stach vorn durch das Display.
- Innenwand der Cockpitwanne (x ±0,20) lag bis ~2 cm in Unterarmen/Handgelenken; obere Hand stieß bei starkem Einschlag vorn an die Wannenrundung; Ellbogen (TV) am Wannenboden.

## Umbau (index.html)
- **Lenkrad `SW`** (Cockpit) und Kopie `f1CarWheel` (Außenansicht): Umriss `OUT` (Fase 6 mm), Griffe als Querschnitt-Schlauch (`loft`, veränderliche Dicke) mit Kugelkappen. Mittelteil und Griffe sind **ein Netz mit demselben Carbon-Material**; der Griffbogen (Ohr) läuft verjüngt seitlich ins Mittelteil, sein Ende liegt ganz in der Plattendicke (vorher stand die Plattenecke hinter dem Bogen heraus). `SW.spec` = Prüfmodell aller Teile.
- **Griffachse** `F1_FIST.d2` = (−0,08 / 1 / 0,12) statt der gekippten Faustachse; die Hand wird dafür in der Arm-IK fest um die Faustmitte gedreht (`qc`, ~18°). Griff samt Hand 2,2 cm tiefer (`F1_FIST.o`), sonst stieß der Zeigefinger oben an den Bogen. Griffradius `F1_GRIP_R` 2,65 cm lokal (≈ 3–4 mm Luft zu den Fingern).
- **Arm-IK** (`kartArmsIK`, nur mit `K.fist` = F1/F2): Hände folgen zu 100 %, Drehpunkt = Ursprung der Lenkrad-Gruppe, Rolle nur um die Griffachse, weich begrenzt ±20° (`F1_ROLL`). Kart unverändert.
- **Cockpitwanne** (`CK.*.wx`, `ckWo`): Innenwand ab Ellbogenhöhe weiter außen (+3 cm bei z 0,30, +5 cm bei 0,36, +6,6 cm ab 0,48); vordere Rundung enger (`rc` 0,025) und Wanne vorn länger (F1 `z1` 0,765, F2 0,735); F1-Boden 0,265.
- **Automodell**: `widenRim` schiebt Randpunkte an Händen/Griffen auf x 0,24 (nur Außenansicht relevant), F1-Plattenrest entfernt (`dropFaces`), F2-Lenksäulenspitze hinter die Nabe gelegt.

## Prüfung (tools/lenkrad)
1. `node tools/lenkrad/export.cjs . export.json` – lädt das Spiel (Dateien direkt aus dem Repo, kein Webserver nötig), fährt Einschlag −1…+1 in 0,01-Schritten stetig durch (F1, F1-TV, F2, F2-TV), exportiert Knochen, `SW.spec`, Karosserie/Wanne ums Lenkrad.
2. `STEP=2 python tools/lenkrad/check_lenkrad.py export.json` – Abstände in mm (Welt):
   - Rumpf/Arm/Bein/Handschuh gegen das Lenkrad (Abstandsfunktion aus `SW.spec`),
   - Unterarme/Hände (z > 0,40) gegen die Cockpitwanne (Strahltest ±x und +y),
   - Karosserie/Wanne gegen das drehende Lenkrad.

### Ergebnis v1.73
Einschlag −1…+1 in 0,02-Schritten, kleinster Abstand (mm, Welt; negativ wäre Durchdringung):

| Fall | Handschuh ↔ Lenkrad | Arm ↔ Lenkrad | Rumpf/Bein ↔ Lenkrad | Unterarme/Hände ↔ Wanne |
|---|---|---|---|---|
| F1 | +2,4 | +39 | +39 | frei |
| F1-TV | +2,4 | +20,5 | +39 | frei |
| F2 | +1,8 | +27,2 | +40 | frei |
| F2-TV | +1,8 | +0,9 | +40 | frei |

Karosserie/Wanne ↔ drehendes Lenkrad: F1 +29,8 mm, F2 +0,2 mm. **Ergebnis: kein Clipping.**
Handrolle höchstens 20°. Vorher (altes Lenkrad): Zeigefinger durch die Griffschlaufe, Fingerspitzen im Mittelteil, Griffe/Fäuste bis 2 cm im Cockpitrand, Unterarme bis 2 cm in der Wannenwand.

## v1.74 – Daumen, Handschuh, Zittern, Arme, Display
- **Daumen vorn auf dem Griff**: Das Netz hatte nur einen kurzen Daumenstummel außen am Griff (nach oben). `tools/fahrer/f1_hand_nachbearbeitung.py` zieht den Stummel in die Faust ein, drückt die spitz herausstehende Zeigefingerkuppe flacher und setzt einen **neuen Daumen** als Teil des Handschuhs ein (Schlauch, starr am Handknochen): von außen über die Fahrerseite um den Griff, Spitze nach innen Richtung Tasten (Bogen 105°, 4,5 mm Luft zum Griff). Vorher versucht: Stummel umbiegen bzw. um die Achse drehen → Netz zerknitterte (zu grob, ~35 Punkte).
- **Handschuh-Design** (F1/F2): statt der fleckigen Foto-Textur der Vorlage ein schlichtes Design aus der Geometrie (aRest der Handschuh-Punkte vom Skript): Handrücken in Handschuhfarbe, alle Flächen zur Griffachse dunkles Wildleder, Naht an der Grenze, Stulpe mit Klettband in Anzugfarbe, feine Ledernarbung (blendet vor dem Flimmern aus).
- **Zittern der Hand**: Die Handrolle wurde nachgeregelt und sprang bei kleinen Lenkkorrekturen um die Mitte bis 2,3° je 0,01 Einschlag (mit Hysterese bis 15° bei Geradeaus). Jetzt fest aus dem Lenkwinkel: `F1_ROLL · tanh(Einschlag / 0,35)` → höchstens 0,57° je 0,01, geradeaus 0°.
- **Arme/Hände schwarz**: Test mit knallrotem Anzug zeigte – die dunklen Flächen unten im Helmbild sind die Handschuhe im Schatten der Cockpitwand, die Ärmel liegen fast ganz unter dem Bildrand. Streulicht angehoben: Handschuhe 32 %, Arme 40 % der eigenen Farbe (vorher 16 % / 5 %).
- **Display „MODE“**: Text lief rechts aus dem Display („BAL…“), weil die Beschriftung davor die Ausrichtung auf links stellte – jetzt rechtsbündig mit Höchstbreite.
- Prüfung danach: kein Clipping (Handschuh ≥ 1,8 mm, F2-TV Arm +3,1 mm, Karosserie F1 +29,8 / F2 +0,2 mm).

![[bilder/hand_v174_daumen.png]]
![[bilder/hand_v174_seite.png]]

## v1.87 – Zusammenführung mit main (v1.86), F2-Modell
- Du spieltest `main` (v1.86), der Lenkrad-Branch zweigte bei v1.72 ab → „alte Hände“. `main` in den Branch geholt, nur die Versionsnummer kollidierte → v1.87.
- `main` zeigt das eigene Auto in den Verfolgerkameras mit mittlerer Detailstufe. Deren F2-Netz hat 80 große Fächer-Dreiecke vom Cockpitboden (Mitte, y 0,29) zum Rand – quer durch Fahrer, Hände und Lenkrad. In den groben Stufen entfernt (Cockpitansicht verwirft den Bereich ohnehin).
- **„Löcher“ auf der F2-Nase**: keine Löcher in der Lackhaut, sondern 20 winzige dunkle Einzelteile der Vorlage (paarweise, 0,3–4 cm, Schrauben/Öffnungen) auf Nase und Deck. Beim Laden entfernt (zusammenhängende Teile < 6 cm oben auf Nase/Deck, alle Detailstufen).
- Prüfung danach: kein Clipping. Bekannt aus `main` (nicht von diesem Umbau): Seitenfehler „reading 'NaN'“ in `trackAt` beim Start eines F2-Rennens in Monza.

![[bilder/f2_nase_v187.png]]

## v1.93 – Handgelenke, Daumen, Wagenfarbe in der Öffnung, F2-Zacken
Rückmeldung mit drei Bildern (Spa, McLaren F1 und F2).

1. **Handgelenke clippen** (Helmkamera, starker Einschlag): Die Handschuh-Stulpe (Zylinder r 3,1 cm, bis 4,5 cm hinter dem Handgelenk) hing **starr an der Hand**, der Ärmel steckt mit r 2,7 cm darin und hing **starr am Unterarm**. Bei vollem Einschlag knickt die obere Hand gemessen bis **~54°** gegen den Unterarm ab (halber Einschlag ~10°). Die Stulpe schwenkte als Ganzes aus dem Ärmel, das Ärmelende stach als schwarze Spitze heraus und man sah ins offene Stulpenende.
   - Neu: `tools/fahrer/f1_handgelenk.py` gibt Arm- und Handschuhpunkten von 1 cm vor bis 8 cm hinter dem Handgelenk **weiche Gewichte** Hand ↔ Unterarm (smoothstep entlang Handgelenk → Ellbogen). Stulpe und Ärmel haben an gleicher Stelle dasselbe Gewicht, sie biegen also gemeinsam (je Seite 416 Punkte). Das Skript ist wiederholbar und ändert nur `bi`/`bw`.
   - Shader: Die dunkle Grifffläche (Wildleder) endet am Handgelenk. Vorher lag die Unterseite der Stulpe bei Hand oben als großer schwarzer Fleck im Bild.
   - Der große dunkle Unterarm im Bild bei vollem Einschlag ist der McLaren-Anzug (dunkel), kein Fehler.
2. **Wagenfarbe in der Cockpitöffnung** (TV-Kamera neben dem Helm, Helmkamera vorn an den Ecken): Seit v1.73 reicht die Wanne vorn bis z 0,765 (vorher 0,74). Die Ausnahme im Schnitt-Shader, die die Spiegelfüße des Originalmodells stehen lässt, begann aber schon bei z 0,742. Dadurch blieben innen in der Öffnung Streifen und Kanten der Karosserie in Wagenfarbe stehen.
   - Neu: `ckOpen(G)` liefert die Öffnungsbreite je z als Tabelle für den Shader. Die Ausnahme gilt nur noch außerhalb der Öffnung. Vorn an der Rundung (ab z1 − 3 cm bis 2 mm vor die Armaturenwand) wird alles verworfen.
3. **F2: Zacken an den Cockpitschultern** (Helmkamera): Die Innenwand der Wanne wurde in v1.73 nach außen gerückt (+6,6 cm, Platz für Unterarme). Vorn wird die Wanne aber schmaler (`hw` 0,37 → 0,30). Beim F2 blieben deshalb für die Schulter (Einfassung bis Außenflanke) nur **8 mm**, und das Schulterprofil klappte zu spitzen Zacken zusammen.
   - Neu: `ckWo` begrenzt die Innenwand so, dass die Schulter überall mindestens `CK_SCH` = 3,2 cm breit bleibt. Das betrifft beim F2 z > 0,62 (Wand dort bis 2,2 cm weiter innen), beim F1 nur ab z 0,69 um höchstens 2 mm.

4. **Daumen wirkte wie ein eigenes Teil**: Der neue Daumen (v1.74) war ein Schlauch, der am Handrücken frei begann. Zwischen ihm und der Hand blieb ein Spalt, er stand als Bogen ab.
   - Neu in `thumb_mesh` (`TH_ROOT`): Die Wurzel läuft als **Daumenballen** 30 % weiter zurück in die Hand. Der Bogen geht 28° weiter nach außen, 1,2 cm Richtung Handgelenk und tiefer in den Handballen (5 cm von der Griffachse). Er wird dicker (1,85 cm), entlang der Griffachse 35 % breiter und ist hinten geschlossen. Dicker wird er nur nach außen, die Luft zum Griff bleibt 2,4 mm (lokal) wie vorher.
   - `f1fahrer.bin` neu aus der Vorlage vor der Nachbearbeitung (Stand v1.65) erzeugt: `f1_hand_nachbearbeitung.py`, danach `f1_handgelenk.py`.

![[bilder/daumen_v193.png]]
(oben vorher, unten nachher; Hand in Bindhaltung)

Prüfung danach (`export.cjs` + `check_lenkrad.py`, STEP=2): **kein Clipping**. Handschuh ≥ 1,8 mm. Arm F1-TV +25,1, F2 +29,4, F2-TV +7,0 mm (vorher +22,1 / +26,2 / +3,1). Unterarme/Hände in der Wanne frei. Karosserie F1 +10,2 / F2 +4,1 mm.
Hinweis: `f1_handgelenk.py` muss nach jedem Neubau von f1fahrer.bin laufen, nach `f1_hand_nachbearbeitung.py`.

## Offen / Ideen
- An der Faust bleibt oben ein kleiner Grat (Rest der Zeigefingerkuppe), nur in Nahansicht von außen sichtbar.
- Handschuh-Nachbearbeitung (`f1_hand_nachbearbeitung.py`, danach `f1_handgelenk.py`) muss nach jedem Neubau von f1fahrer.bin (build_fahrer.py) erneut laufen.
- Bei vollem Einschlag knickt die obere Hand weiter ~54° ab (jetzt weich gebogen). Weniger ginge mit mehr Handrolle (`F1_ROLL`) oder höherem Ellbogen, beides braucht neue Clipping-Prüfung.
- Ellbogen/Oberarme hinter z 0,40 liegen wie bisher gewollt unter dem Rand im Monocoque (nicht geprüft).
- Außen-Lenkrad (`f1CarWheel`) ohne Display (wie bisher, Leistung).

## Bilder
![[bilder/lenkrad_v173_vorn.png]]
![[bilder/lenkrad_v173_seite.png]]
