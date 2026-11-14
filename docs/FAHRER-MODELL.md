# Rennfahrer-Modell

Stand: 14.11.2026 (v1.60) – derselbe Fahrer in Kart, F1 und F2; stehende Figur als Vorschau.

## Dateien
- `kartfahrer.bin` – sitzender Kart-Fahrer fürs Spiel: Körper + beide Handschuhe als EIN Netz (~14 200 Dreiecke).
- `f1fahrer.bin` – derselbe Fahrer halb liegend für F1/F2 (gleiches Format, Hände an den Griffen des F1-Lenkrads).
- `textures/kart_fahrer.jpg` – Atlas 1024×512: links Anzug (helle Stoff-Schattierung), rechts Handschuh.
- `textures/kart_stoff.jpg` – kachelbares Nomex-Köpergewebe (Höhenkarte 256², vom Bauskript erzeugt).
- `fahrer/fahrer.glb`, `fahrer/handschuh.glb` – stehende Figur (24 000 Dreiecke), `fahrer/vorschau.html` zeigt sie mit unserem Helm.
- `fahrer/kart_vorschau.html` – Prüfansicht: Kart + Kart-Fahrer + Lenkradkranz (gleiche Lade-Logik wie im Spiel).
- `tools/fahrer/build_fahrer.py <quellordner> [kart|f1]` – baut alles neu (oder nur einen der beiden Sitzfahrer, je ~3 min). Quellordner: `model.obj`, `base.jpg`, `normal.jpg` (Tripo), `glove.kmz`. Vorlagen nicht im Repo (OBJ 25 MB). Braucht numpy, pillow, scipy, trimesh, pymeshlab, libigl, scikit-image (+ Systempaket libopengl0).

## Ablauf im Skript
1. **Körper aufräumen**: Splitter-Dreiecke, Kopf mit Tripo-Helm und Hände weg. Ärmel quer zum Unterarm geschnitten.
2. **Textur säubern**: Logos, Schriftzüge und dunkle Fehlstellen erkannt und von außen aufgefüllt → helle Schattierung, keine Sponsoren-Logos.
3. **Geschlossene Hülle** (`remesh_winding`): Die Tripo-Vorlage ist kein sauberes Netz – doppelwandige Ärmel, ein Futter im Oberkörper, im Rumpf steckende Ärmelflächen, abstehende Schulterklappen. Beim Biegen kamen die als **Löcher/Schlitze an Schulter und Kragen** heraus. Deshalb wird die Ruhehaltung neu aufgebaut:
   - innen/außen über die Windungszahl (libigl), je Höhenscheibe gefüllt (Futter), Spalt Rücken/Oberarm geschlossen, dünne Finnen an den Schulterkappen weggeöffnet,
   - Lücke Arm/Hüfte freigeschnitten (sonst zog der Arm eine Hautfalte von der Hüfte mit),
   - Ergebnis: eine geschlossene Hülle mit Kugel-Topologie (Euler 2), 11 000 Dreiecke; UV vom Original, an UV-Nähten/neuen Flächen eine saubere Stoffstelle.
4. **Sitzhaltung** (wie beim echten Kartfahren): Rumpf 12° zurück, Oberarme hängen, Ellbogen ~90° unten-außen, Unterarme nach vorn zum Kranz (Zwei-Knochen-IK, 9/3 Uhr). Sitzpunkt so, dass Schulter–Hand ≈ 72 % der Armlänge.
   - Rumpf/Beine linear gemischt; **Arme gedreht** (Rotation um Schulter und Ellbogen, mit dem Gewicht skaliert) – lineares Mischen ließ die Schulter einknicken.
   - Bein-Anteil wirkt nicht auf die Arme (vorher entstanden dadurch Zacken am Unterarm).
   - **Hände gerade**: Hand in Verlängerung des Unterarms, Handgelenk höchstens ~15° abgewinkelt; der Kranz läuft schräg durch die Faust (wie in echt). Vorher war die Hand bis 48° abgeknickt.
   - Gestauchte Stellen und Übergang Rumpf/Arm lokal geglättet (Taubin, schrumpft nicht).
5. **Lückenlos Ärmel → Handschuh**: Bündchen auf r = 3 cm eingezogen und rund abgeschlossen; Stulpe rund (r 3,45 cm) darübergelegt, endet ~4,5 cm vor dem Handgelenk.
6. **Helm** sitzt mit der Unterkante 4,5 cm unter dem oberen Halsende auf dem Kragen.
7. **Handschuhe**: Faust um den Kranz, linke Hand gespiegelt, Rot der Vorlage → Weiß (Teamfarbe).

Prüfansicht: `fahrer/kart_vorschau.html?debug` färbt Rückseiten grün – so sieht man Löcher/umgeklappte Flächen sofort.

## Im Spiel (`index.html`)
- `KFAHRER` lädt `kartfahrer.bin`; `kartDriver()` nutzt ihn, der alte aus Grundformen gebaute Fahrer bleibt als Rückfall.
- **Anzugmaterial** `kartFahrerMat()` (Abschnitt `KFMAT-START … KFMAT-END`, die Prüfansicht liest genau diesen Abschnitt):
  - MeshPhysicalMaterial mit **Sheen** (Stoffglanz), Rauheit je Bereich: Stoff 0,86, Strick 0,8, Handschuh (Wildleder) 0,62, Schuhe (Glattleder) 0,38, Reißverschluss Metall.
  - **Gewebe**: Köper-Höhenkarte dreiseitig auf die *Ruhe*-Position projiziert (Gewebe wandert beim Sitzen mit dem Stoff mit), als Relief über Bildschirm-Ableitungen (Bump), ca. 1,6 cm je Kachel.
  - **Design je Bildpunkt aus der Ruhe-Position** (`aRest`, `aRN`): Seitenstreifen an Rumpf, Ärmeln und Hosenbeinen (Akzentfarbe), Schulterpasse, Gürtel, Strickkragen, Reißverschluss vorn, Stretch-Einsätze mit Rippen (unterer Rücken, Achsel innen, Kniekehle), Strickbündchen an Ärmeln und Hosenbeinen, weiße Aufnäher (Brust, Gürtel – ohne Logos).
  - **Nähte** als Rillen im Relief und etwas dunkler.
  - Arm/Rumpf/Bein werden je Bildpunkt aus der Ruhe-Position bestimmt (gleiche Grenze wie `arm_masks`), nicht je Eckpunkt – sonst gezackte Kanten.
- **Behoben (v1.44):** gezackte weiße Linie seitlich am Körper/über die Schultern. Ursache: Arme hatten `aRy = 0,5` als „kein Gürtel“, an der Grenze zum Rumpf lief der Wert über die Gürtelhöhe → dünner Gürtelstreifen. Jetzt eigener Bereich `aReg` (0 Rumpf, 1 Arm, 2 Bein, 3 Handschuh).
- Helm: derselbe wie F1/F2 (`helmMat(…, true)`), beim Kart ohne das Anbauteil unter dem Visier.
- Cockpitkamera der Karts sitzt auf Augenhöhe im Helm (`cam` aus `KFAHRER.helm`).

## v1.49 – Sitz, Cockpit, Lenken, Helme
- **Sitz**: Sitzposition aus der Sitzschale in `kart.bin` berechnet (`kart_seat`): Gesäß liegt auf der Pfanne, Rücken an der Lehne (je ~3 mm Abstand), nichts dringt ein. Neigung 14°.
- **Lenkrad** rückt dafür 12 cm entlang der Lenksäule zum Fahrer (verstellbare Säule, `swExt` in `kartfahrer.bin`), mit Verlängerungsrohr – so sind die Arme leicht gebeugt.
- **Cockpitansicht Kart**: Kamera tiefer (9 cm unter der Helmmitte) und Blick ~24° nach unten: Lenkrad, Display und beide Hände im Bild. Die alten eingeblendeten Arme sind beim neuen Fahrer aus; man sieht die echten Arme des Modells.
- **Lenken**: Arme mit Skelett (7 Knochen, Gewichte im Bauskript, Skinning im Shader). `kartArmsIK` je Bild: Hand bleibt am Kranz und dreht mit dem Lenkrad, Schulter fest, Ober-/Unterarm starr – der Ellbogen ergibt sich aus der Zwei-Knochen-IK und bleibt in seiner Ebene.
- **Helme (alle Karts)**: Das Anbauteil unter dem Visier wurde vorher weggeschnitten → Loch mit Blick ins Helminnere (dunkle, „komische“ Formen, am deutlichsten bei hellen/blauen Helmen). Jetzt `helmGeoKart`: Kinnteil auf die Schalenform gelegt und in Helmfarbe, eingelassene Lüftungsschlitze glatt schattiert, Visier nur von vorn. Rest: zwei winzige Lüftungspunkte, nur aus nächster Nähe sichtbar.

## v1.50 – Korrektur nach Handy-Screenshot
- Lenkrad drehte beim Kart mit vollem Einschlag um 92° (`steer × 1,6`) – die Hand landete über dem Lenkrad, der Arm lag quer vor dem Gesicht. Jetzt `KART_SW_ROT = 0,7` (~40°) für Karts mit neuem Fahrer.
- Ellbogen-Pol nach unten-außen gezogen (Ellbogen bleibt beim Einlenken unten).
- Gewebe-Relief und Strickrippen werden ausgeblendet, sobald sie feiner als ein Bildpunkt sind (Pixelmuster/Flimmern auf dem Handy).
- Getestet mit vollem Einschlag in beide Richtungen (vorher nur halber Einschlag – deshalb übersehen).

## v1.51 – kein Clipping
Geprüft rechnerisch (Punkte aus dem laufenden Spiel ausgelesen, Windungszahl gegen Körper und Kart) bei Einschlag −1, −0,5, 0, 0,5, 1:
- **Kamera**: nichts näher als 40 cm im Bild – kein Abschneiden an der Nahgrenze, auch beim Umschauen.
- **Hand in den Oberschenkel** bei vollem Einschlag (≈3 cm): Oberschenkel flacher gelegt (Knie tiefer, wie beim echten Kart).
- **Ellbogen in die Hüfte** beim unteren Arm: Ellbogen-Pol jetzt außen-unten statt unten.
- **Gesäß/Oberschenkel in der Sitzschale** (bis 7 mm): Punkte im Kart werden im Bauskript auf die Oberfläche + 2 mm geschoben.
- Ergebnis: 0 Punkte Hand↔Bein, 0 Anzug↔Kart, Arm↔Rumpf nur 1 Punkt 1,4 mm am Schultergelenk (fließender Übergang derselben Fläche).
- Beabsichtigte Überlappungen bleiben: Handschuh-Stulpe über dem Bündchen, Faust um den Lenkradkranz.

## v1.53 – Griff, Handgelenke, Kamera
- **Griff** (`bend_hand`, `FIST` im Bauskript): Hand-Mittellinie bis zum Handballen gerade, Handfläche leicht gewölbt (R 3,6), Finger um den Kranz (R 3,5). Der Kranz liegt am Daumenballen in der Handfläche (Abstand 2,3 bei Rohrradius 2,07 Vorlagen-Einheiten), die Finger umschließen ihn ohne einzudringen.
- **Handgelenke** (`kartArmsIK`): Die Hand rollt um das Kranzrohr, bis sie in Linie mit dem Unterarm steht; der Ellbogen wird auf seinem IK-Kreis so gewählt, dass der Unterarm zur Hand zeigt (nicht über Schulter −10 cm, nicht in Hüfte/Rumpf, nicht nach hinten); der Unterarm übernimmt die Verdrehung (Elle/Speiche); die Hände folgen dem Kranz zu 80 % (er gleitet etwas durch die Faust).
  - Gemessener Knick Hand↔Unterarm: geradeaus 1° (vorher 16°), halber Einschlag ≤ 13° (vorher 40°), voller Einschlag ≤ 39° (vorher 62°).
  - Durchdringung bei −1…+1: 0 Hand↔Bein, 0 Arm↔Rumpf, 0 Anzug↔Kart.
- **Cockpitkamera Kart**: wieder höher (3 cm unter Helmmitte), Blick ~15° nach unten – Lenkrad und Hände im Bild.

## v1.58 – F1/F2-Fahrer, Teamanzüge, Kart 10/2 Uhr
**Kart**
- Hände auf **10 und 2 Uhr** (`wheel_frame`: Griffwinkel 30° über der Waagerechten, Daumen entlang der Kranz-Tangente). Die Lenksäule rückt dafür weiter zum Fahrer (19,5 cm, Schulter–Hand 85 % der Armlänge).
- Helmkamera höher (0,5 cm unter Helmmitte) und flacher (Blicksenkung 10 statt 15,5 → Horizont im oberen Bilddrittel, Hände und Kranz bleiben im Bild).

**F1/F2** (`pose_kart(..., mode='f1')`, `build_seated('f1')` → `f1fahrer.bin`)
- Gleicher Körper, halb liegend (Rumpf 18° zurück), Becken vorn, Beine fast waagerecht unter die Nase. Der Hals wird so gesetzt, dass der Helm **genau an der bisherigen Spielposition** (0 / 0,795 / 0,18) sitzt – Helmkamera und TV-Kamera bleiben unverändert. Der Helm reicht 8 cm über den Hals (Kart 4,5 cm): die Schultern sitzen höher im Cockpit.
- Lenkrad aus der SW-Gruppe (`wheel_frame('f1')` = `f1Wheel()` im Spiel): Griffe bei lokal x ±0,2 · swS, Drehachse = lokale z-Achse nach Drehung (0,45 / π / 0). F2 (andere Helm- und Lenkradposition) nutzt dasselbe Modell: Körper um die Helm-Differenz verschoben, die Arm-IK greift das F2-Lenkrad.
- Ellbogen-Wahl F1: Unterarm fast waagerecht, Ellbogen etwas außen und tiefer als die Hand. Das F1-Lenkrad sitzt nah am Fahrer (Schulter–Handgelenk 0,40 m bei 0,55 m Armlänge) – die Arme sind deutlich gebeugt, die Ellbogen gehen nach außen/unten (im Monocoque verdeckt).
- Im Spiel: `f1Driver()` (eigenes Objekt neben der Helmgruppe, folgt deren TV-Versatz), `kartArmsIK(out, spin, K, C, AX, RIM)` verallgemeinert. Lenkwinkel wie das Cockpit-Lenkrad (`steer × SW_ROT`).
- **Helmkamera**: Rumpf und Beine werden per Shader verworfen (`uCut`), Arme und Hände bleiben – die alten eingeblendeten Arme (`ARMS.f1`) sind aus. Nichts näher als 16 cm (Nahgrenze).
- **TV-Kamera**: nur Helm und Fahrer ausgetauscht, Kameraposition und Helmversatz unverändert.
- Helm mit den Kart-Korrekturen (`helmGeoKart`, ohne Anbauteil unter dem Visier).
- **Offenes F1-Cockpit**: Das F1-Modell hatte über dem Fahrer eine Gitterplatte auf Höhe 0,576 (Cockpit von außen zu, man sah nur den Helm). `dropFaces` entfernt sie innerhalb der Cockpitöffnung (|x| < 0,2, z 0,1–0,8) – wie beim F2 sieht man jetzt Anzug, Arme und Hände.
- Mit `lodFadePrep` (v1.56) wird das Material je Auto kopiert; die Knochen werden deshalb in die Uniforms des Originals geschrieben (`U` beim Bau gemerkt) und `uniformsNeedUpdate` an der Kopie gesetzt.

**Teamanzüge** (`SUIT_F1`, `suitDesign`, `kartFahrerMat(..., des)`)
- Je Team Grundfarbe, zweite Farbe, Akzent (Streifen, Schulterpasse) und Handschuhfarbe, ohne Logos. Schnitte: 0 einfarbig, 1 Unterteil (z. B. McLaren schwarz unten), 2 Seitenteile + Ärmel (Mercedes, Williams, Haas), 3 Schärpe (Ferrari, Red Bull), 4 Schulterpartie + Ärmel oben (Aston Martin, Alpine, Cadillac).
- F2: aus der Lackierung (Hauptfarbe, Unterteil oder Flügelfarbe).

## v1.59 – F1-Cockpit von außen wie beim F2
- Wunsch: auch beim F1 von außen ins modellierte Cockpit sehen und den Anzug erkennen.
- **Innenraum dunkel**: Sitzlehne, Kopfstütze, Innenwände neben den Schultern und der Cockpitrand werden in Cockpitfarbe gezeichnet statt in Wagenfarbe (zweiter Bereich `COCK.f1.b2`: |x| < 0,25, z −0,25…0,38, y < 0,76; wirkt in `inCock` und `cockGLSL`). Vorher saß der Fahrer zwischen orangen bzw. teamfarbenen Wänden.
- **Lenkrad im Auto** (F1 und F2, alle Autos): `f1CarWheel` – Kopie des Cockpit-Lenkrads (Carbon-Körper, Griffe, Tasten; ohne Display) an `swPos`, dreht mit dem Einschlag; die Hände greifen es jetzt sichtbar (vorher griffen sie ins Leere). In Helm- und TV-Kamera des Spielers bleibt das Cockpit-Lenkrad SW zuständig, die Kopie ist dann aus. Gehört zu den Detailteilen (Fernmodell blendet es aus).

## v1.60 – F1/F2: Griff, springende Hände, Clipping in der TV-Ansicht
Gemessen mit einem Durchlauf des Lenkeinschlags −1…+1 in Schritten von 0,01 (Bones aus dem laufenden Spiel; Skript im Arbeitsordner `sweep.cjs`).
- **Griff saß neben der Schlaufe**: Die IK nahm als Griffpunkt den Lenkradpunkt, der dem Handgelenk am nächsten liegt (beim runden Kartkranz in Ordnung, beim F1 lag die Hand hinter/neben der Griffschlaufe, die Finger vor der Lenkradfront). Jetzt steht die echte Griffmitte im Kopf von `f1fahrer.bin` (`grip`); die Faust liegt um diesen Punkt.
- **Hände in TV-Ansicht und F2 neben dem Lenkrad (5–12 cm)**: Die IK verwechselte den Griff in Bindhaltung mit dem Griff am verschobenen Lenkrad (TV-Kamera: Fahrer rückt mit dem Helm 6 cm vor; F2: anderes Lenkrad). Jetzt G0 = Bindgriff, G = Griff am Lenkrad dieses Autos. Fehler jetzt 0,1 mm in allen vier Fällen (F1, F1-TV, F2, F2-TV).
- **Arme stark gebeugt, Ellbogen außerhalb des Cockpits** (|x| 0,29): Kopf/Hals 7 cm vor die Schultern geschoben (`F1_SHEAR`, wie mit HANS-System), die Schultern sitzen damit weiter vom nahen Lenkrad weg (Arm zu 79 % gestreckt statt 73 %), Ellbogen unter dem Arm innerhalb der Cockpitbreite (|x| ≤ 0,215), Handgelenk bis 28° geknickt.
- **Springen**: Ellbogen wurde in 7,5°-Stufen gesucht und wechselte zwischen zwei fast gleich guten Lagen; die Hand-Rolle (`phi`) schwang im engen F2-TV-Fall zwischen zwei Werten. Jetzt: Feinsuche, ab dem zweiten Bild nur nahe der letzten Lage, Rolle weich begrenzt (tanh, ±1,3 rad), gedämpft nachgeführt und höchstens 0,04 rad je Bild. Größter Sprung je 0,01 Einschlag: vorher bis 140 mm, jetzt ≤ 4 mm.
- Das Kart nutzt dieselbe IK (ohne `grip` im Kopf wie bisher: nächster Kranzpunkt), Bilder geprüft.

## Offen / Ideen
- Lenkrad dreht sich beim Lenken, die Hände nicht (war beim alten Fahrer genauso).
- Leichte Knautschfalten an der Hüfte durch das Biegen (im Sitz kaum sichtbar).
- Stehende Figur könnte fürs Podium/Showroom eingebaut werden.
