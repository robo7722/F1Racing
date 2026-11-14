# F1/F2-Lenkrad und Griff (v1.73)

Stand: 14.11.2026 – Umbau nach Referenzbildern (Onboard-Ansichten aktueller F1-Spiele: breites Carbon-Mittelteil mit großem Display, Schaltlichter oben, Tasten in Spalten, bunte Drehschalter, dicke gummierte Griffe, Hände fest um die Griffe).
Zugehörig: [[FAHRER-MODELL]] (Fahrer, Hände, Arm-IK).

## Ausgangslage (gemessen)
- Die Faust der Fahrerhand in `f1fahrer.bin` ist **kein** Ring um den alten senkrechten Griff: Die freie Röhre in der Faust ist um **~20° gekippt** (oben zum Fahrer hin, leicht nach außen).
  Vermessen als größter freier Zylinder im Handschuh: Mitte lokal (0,1939 / −0,0161 / 0,0380), Richtung (0,1375 / 0,9331 / 0,3324), Radius 3,1 cm lokal (= 2,4 cm Welt) über ±7 cm Länge.
- Folge beim alten Lenkrad: Zeigefinger lief durch die Griffschlaufe, Fingerspitzen steckten im Mittelteil (Kante x 0,157, Spitzen ab x 0,148).
- Die Faust ist zur Innen-/Fahrerseite offen: Handfläche außen, Finger um die Vorderseite, Spitzen innen-vorn → zwischen Griff und Mittelteil muss ein **Fingerschlitz** bleiben.
- Arm-IK (`kartArmsIK`) hatte zwei Fehler für F1/F2:
  - Hände folgten dem Lenkrad nur zu **80 %** (Kart-Regel) → Faust bis 3 cm neben dem Griff.
  - Drehung um die Lenkradmitte `C` statt um den Ursprung der Lenkrad-Gruppe (1 cm versetzt) → bis 6 mm Wandern beim Einlenken.
- Cockpitrand des Automodells (F1 x ±0,16, F2 ±0,18, mit nach unten gezogener Lippe) lag genau in Griffhöhe: Griffe **und** Fäuste steckten darin (Außenansicht).
- Innenwand der Cockpitwanne (x ±0,20) lag bis ~2 cm in Unterarmen/Handgelenken (Cockpit- und TV-Ansicht).

## Umbau (index.html)
- **Lenkrad `SW`** (Cockpit) und Kopie `f1CarWheel` (Außenansicht):
  - Carbon-Mittelteil als Umriss (`OUT`, Fase 6 mm), oben breit mit runden Schultern, Seitenkante x ≤ 0,123 (Fingerschlitz).
  - **Griffe** (`F1_FIST`, `F1_GRIP_R` = 2,65 cm lokal): gerades Stück genau auf der Faustachse (t −0,09…+0,085), unten und oben als Bogen ins Mittelteil – gummiert.
  - Display 0,154 × 0,077 mit Rahmen (Schaltlichter im Display wie bisher), Tasten in zwei Spalten (4 je Seite), weitere Tasten unten, **drei Drehschalter mit farbigen Rastfeldern** (wie die bunten Schalter der Vorbilder), Mittenmarkierung, Schalt- und Kupplungswippen hinten (enden vor den Fingerspitzen), Nabe mit Schnellverschluss.
  - `SW.spec`: Prüfmodell aller Teile (Umriss, Rohre, Zylinder, Quader) für die Abstandsprüfung.
- **Arm-IK** (`kartArmsIK`, nur wenn `K.fist` gesetzt = F1/F2): Hände folgen dem Lenkrad zu 100 %, Drehpunkt = Gruppen-Ursprung, Hand rollt nur um die Faustachse, Rolle weich begrenzt auf ±20° (`F1_ROLL`). Kart unverändert.
- **Cockpitwanne** (`CK.f1/f2.wx`, `ckWo`): Innenwand ab Ellbogenhöhe weiter außen (+3 cm bei z 0,30, +5 cm bei 0,36, +6,6 cm ab 0,48). Schriftzüge auf den Schultern folgen.
- **Automodell** (`widenRim`): Randpunkte im Band um Hände/Griffe nach außen auf x 0,24 geschoben (F1 y 0,56–0,64, z 0,48–0,71; F2 y 0,56–0,70, z 0,46–0,70; weich auslaufend). Cockpitansicht betrifft das nicht (dort wird die Karosserie im Cockpitbereich ohnehin verworfen).

## Prüfung (tools/lenkrad)
1. Spiel per http starten (`python -m http.server 8765` im Repo).
2. `node tools/lenkrad/export.cjs http://localhost:8765/index.html export.json` – Knochen der Arm-IK für Einschlag −1…+1 (Schritt 0,01, stetig gefahren) in F1, F1-TV, F2, F2-TV, dazu Karosserie/Wanne ums Lenkrad.
3. `python tools/lenkrad/check_lenkrad.py export.json` – Abstände (mm, Welt):
   - Rumpf/Arm/Bein/Handschuh gegen das Lenkrad (Abstandsfunktion aus `SW.spec`),
   - Unterarme/Hände (z > 0,40) gegen die Cockpitwanne (Strahltest ±x und +y),
   - Karosserie/Wanne gegen das drehende Lenkrad.

### Ergebnis v1.73
ERGEBNIS_PLATZHALTER

## Offen / Ideen
- Daumen liegen entlang des Griffs nach oben (Faust aus der Vorlage); bei den Vorbildern liegen sie vorn auf dem Lenkrad. Dafür müsste der Handschuh im Bauskript neu gebogen werden (Vorlage `glove.kmz` nicht im Repo).
- Ellbogen/Oberarme liegen wie bisher gewollt unter dem Rand im Monocoque (hinter z 0,40 nicht geprüft).
- Außen-Lenkrad (`f1CarWheel`) hat kein Display (schwarzer Rahmen) – aus Leistungsgründen wie bisher.
