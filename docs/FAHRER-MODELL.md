# Rennfahrer-Modell

Stand: 13.11.2026 (v1.36) – Kart-Fahrer im Spiel eingebaut, stehende Figur als Vorschau.

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
4. **Sitzhaltung**: einfaches Skelett (Rumpf, Ober-/Unterarm, Ober-/Unterschenkel, Fuß), Gewichte nach Abstand je Körperbereich. Rumpf 24° zurückgelehnt, Beine nach vorn zu den Pedalen, Arme per Zwei-Knochen-IK an den Lenkradkranz (9/3 Uhr). Kart-Maßstab 1,1 (Kart ist größer gebaut; Helm dort 0,33 m).
5. **Handschuhe**: Faust um den Kranz (Krümmung ab den Fingerwurzeln, Radius passend zum Kranzrohr; Skript prüft den Abstand), linke Hand gespiegelt. Rot der Vorlage → Weiß, damit sie in Teamfarbe eingefärbt werden. Logo-Schriftzug auf der Lasche übermalt.

## Im Spiel (`index.html`)
- `KFAHRER` lädt `kartfahrer.bin`; `kartDriver()` nutzt ihn, der alte aus Grundformen gebaute Fahrer bleibt als Rückfall.
- `kartFahrerMat()` färbt im Shader: Anzug = Teamfarbe, Gürtel und Handschuhe = Akzentfarbe, Schuhe dunkel. Gürtel/Schuhe aus der Höhe in Ruhehaltung je Eckpunkt (`aRy`) → gerade Kanten.
- Helm: derselbe wie F1/F2 (`helmMat(…, true)`), beim Kart ohne das Anbauteil unter dem Visier. F1/F2 haben es noch.
- Cockpitkamera der Karts sitzt jetzt auf Augenhöhe im Helm (`cam` aus `KFAHRER.helm`).
- `sw.js`: neue Dateien im Offline-Cache, Cache `f1-rennen-1.36`.

## Offen / Ideen
- Lenkrad dreht sich beim Lenken, die Hände nicht (war beim alten Fahrer genauso).
- Leichte Knautschfalten an der Hüfte durch das Biegen (im Sitz kaum sichtbar).
- F1/F2: Kinnteil am Helm ggf. auch entfernen.
- Stehende Figur könnte fürs Podium/Showroom eingebaut werden.
