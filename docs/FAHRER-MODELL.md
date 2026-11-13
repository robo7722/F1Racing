# Rennfahrer-Modell

Stand: 13.11.2026 (v1.44) – Kart-Fahrer im Spiel eingebaut, stehende Figur als Vorschau.

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

## Offen / Ideen
- Lenkrad dreht sich beim Lenken, die Hände nicht (war beim alten Fahrer genauso).
- Leichte Knautschfalten an der Hüfte durch das Biegen (im Sitz kaum sichtbar).
- F1/F2: Kinnteil am Helm ggf. auch entfernen.
- Stehende Figur könnte fürs Podium/Showroom eingebaut werden.
