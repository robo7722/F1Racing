# Rennfahrer-Modell

Stand: 13.11.2026 (v1.40) – Kart-Fahrer im Spiel eingebaut, stehende Figur als Vorschau.

## Dateien
- `kartfahrer.bin` – sitzender Kart-Fahrer fürs Spiel: Körper + beide Handschuhe als EIN Netz (~12 200 Dreiecke, 435 KB).
- `textures/kart_fahrer.jpg`, `textures/kart_fahrer_n.jpg` – Atlas 1024×512: links Anzug (helle Stoff-Schattierung), rechts Handschuh; Normalen.
- `fahrer/fahrer.glb`, `fahrer/handschuh.glb` – stehende Figur (24 000 Dreiecke), `fahrer/vorschau.html` zeigt sie mit unserem Helm.
- `fahrer/kart_vorschau.html` – Prüfansicht: Kart + Kart-Fahrer + Lenkradkranz (gleiche Lade-Logik wie im Spiel).
- `tools/fahrer/build_fahrer.py <quellordner>` – baut alles neu. Quellordner: `model.obj`, `base.jpg`, `normal.jpg` (Tripo), `glove.kmz`. Vorlagen nicht im Repo (OBJ 25 MB). Braucht numpy, pillow, scipy, trimesh, pymeshlab (+ Systempaket libopengl0).

## Ablauf im Skript
1. **Körper aufräumen**: Splitter-Dreiecke, Kopf mit Tripo-Helm und Hände weg. Ärmel werden mit einer Ebene quer zum Unterarm geschnitten (gerade Kante statt ausgefranst).
2. **Textur säubern**: Logos, Schriftzüge und dunkle Fehlstellen (Fersen, Achseln, Seitennähte) erkannt (dunkler als Umgebung / farbig) und von außen aufgefüllt. Übrig bleibt eine helle Schattierung → keine Sponsoren-Logos mehr.
3. **Verkleinern** mit Erhalt der Textur (MeshLab-Kantenzusammenlegung): 204 000 → 9 000 Dreiecke (Kart) bzw. 24 000 (stehend). Normalen über UV-Nähte gemittelt.
4. **Sitzhaltung** (wie beim echten Kartfahren): einfaches Skelett (Rumpf, Ober-/Unterarm, Ober-/Unterschenkel, Fuß), Gewichte nach Abstand je Körperbereich. Rumpf nur 12° zurück, Oberarme hängen, Ellbogen ~90° unten-außen, Unterarme nach vorn zum Kranz (Zwei-Knochen-IK, 9/3 Uhr). Sitzpunkt wird so gewählt, dass Schulter–Hand ≈ 72 % der Armlänge ist. Knie hoch. Kart-Maßstab 1,1 (Kart ist größer gebaut; Helm dort 0,33 m).
   - Arme werden über eine höhenabhängige Grenze |x| > t(y) erkannt (gemessene Lücke zwischen hängendem Arm und Hüfte). Vorher wurde die Hüftseite neben der Hand mit zum Lenkrad gezogen („Brust mit den Händen verbunden“).
   - Beine wirken erst unterhalb des Gürtels.
5. **Lückenlos**: Die Stulpe wird je Richtung um den Unterarm auf 97 % des Ärmelquerschnitts geweitet und reicht ~8 cm in den Ärmel (`fit_gauntlet`). Der Helm sitzt mit der Unterkante 4,5 cm unter dem oberen Halsende auf dem Kragen.
6. **Handschuhe**: Faust um den Kranz (Krümmung ab den Fingerwurzeln, Radius passend zum Kranzrohr; Skript prüft den Abstand), linke Hand gespiegelt. Rot der Vorlage → Weiß, damit sie in Teamfarbe eingefärbt werden. Logo-Schriftzug auf der Lasche übermalt.

## Im Spiel (`index.html`)
- `KFAHRER` lädt `kartfahrer.bin`; `kartDriver()` nutzt ihn, der alte aus Grundformen gebaute Fahrer bleibt als Rückfall.
- `kartFahrerMat()` färbt im Shader: Anzug = Teamfarbe, Gürtel und Handschuhe = Akzentfarbe, Schuhe dunkel. Gürtel/Schuhe aus der Höhe in Ruhehaltung je Eckpunkt (`aRy`) → gerade Kanten.
- Helm: derselbe wie F1/F2 (`helmMat(…, true)`), beim Kart ohne das Anbauteil unter dem Visier. F1/F2 haben es noch.
- Cockpitkamera der Karts sitzt jetzt auf Augenhöhe im Helm (`cam` aus `KFAHRER.helm`).
- `sw.js`: neue Dateien im Offline-Cache, Cache `f1-rennen-1.40`.

## Offen / Ideen
- Lenkrad dreht sich beim Lenken, die Hände nicht (war beim alten Fahrer genauso).
- Leichte Knautschfalten an der Hüfte durch das Biegen (im Sitz kaum sichtbar).
- F1/F2: Kinnteil am Helm ggf. auch entfernen.
- Stehende Figur könnte fürs Podium/Showroom eingebaut werden.
