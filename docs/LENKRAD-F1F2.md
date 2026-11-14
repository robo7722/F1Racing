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
- **Lenkrad `SW`** (Cockpit) und Kopie `f1CarWheel` (Außenansicht): Umriss `OUT` (Fase 6 mm), Griffe als Querschnitt-Schlauch (`loft`, veränderliche Dicke) mit Kugelkappen. `SW.spec` = Prüfmodell aller Teile.
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
ERGEBNIS_PLATZHALTER

## Offen / Ideen
- Daumen liegen entlang des Griffs nach oben (Faust aus der Vorlage); beim Vorbild liegen sie vorn auf dem Lenkrad. Dafür müsste der Handschuh im Bauskript neu gebogen werden (Vorlage `glove.kmz` nicht im Repo).
- Handrolle steht beim Lenken meist an der Grenze ±20° – mehr Rolle ließe die Fingerspitzen an den Schlitz kommen.
- Ellbogen/Oberarme hinter z 0,40 liegen wie bisher gewollt unter dem Rand im Monocoque (nicht geprüft).
- Außen-Lenkrad (`f1CarWheel`) ohne Display (wie bisher, Leistung).
