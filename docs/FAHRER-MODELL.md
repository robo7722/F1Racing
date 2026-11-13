# Rennfahrer-Modell

Stand: 13.11.2026 (v1.50) – Kart-Fahrer im Spiel eingebaut, stehende Figur als Vorschau.

## Dateien
- `kartfahrer.bin` – sitzender Kart-Fahrer fürs Spiel: Körper + beide Handschuhe als EIN Netz (~14 200 Dreiecke).
- `textures/kart_fahrer.jpg` – Atlas 1024×512: links Anzug (helle Stoff-Schattierung), rechts Handschuh.
- `textures/kart_stoff.jpg` – kachelbares Nomex-Köpergewebe (Höhenkarte 256², vom Bauskript erzeugt).
- `fahrer/fahrer.glb`, `fahrer/handschuh.glb` – stehende Figur (24 000 Dreiecke), `fahrer/vorschau.html` zeigt sie mit unserem Helm.
- `fahrer/kart_vorschau.html` – Prüfansicht: Kart + Kart-Fahrer + Lenkradkranz (gleiche Lade-Logik wie im Spiel).
- `tools/fahrer/build_fahrer.py <quellordner>` – baut alles neu. Quellordner: `model.obj`, `base.jpg`, `normal.jpg` (Tripo), `glove.kmz`. Vorlagen nicht im Repo (OBJ 25 MB). Braucht numpy, pillow, scipy, trimesh, pymeshlab, libigl, scikit-image (+ Systempaket libopengl0).

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

## Offen / Ideen
- Lenkrad dreht sich beim Lenken, die Hände nicht (war beim alten Fahrer genauso).
- Leichte Knautschfalten an der Hüfte durch das Biegen (im Sitz kaum sichtbar).
- F1/F2: Kinnteil am Helm ggf. auch entfernen.
- Stehende Figur könnte fürs Podium/Showroom eingebaut werden.
