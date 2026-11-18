# Klassiker-Autos (spieltauglich verkleinert)

| Datei | Quelle | Original | Jetzt | Dreiecke LOD0 / LOD1 / LOD2 | Zeichenaufrufe LOD0 / 1 / 2 |
|---|---|---|---|---|---|
| `lotus49c.glb` | Lotus 49C (1970) | 60 MB, 300 000 Dreiecke, 533 Teile | 4,1 MB | 80 000 / 26 000 / 9 000 | 15 / 11 / 7 |
| `mclaren_mp44.glb` | McLaren MP4/4 (1988) | 75 MB, 1,7 Mio. Dreiecke, 118 Materialien | 3,8 MB | 80 000 / 26 000 / 9 000 | 14 / 11 / 7 |
| `ferrari_f2004.glb` | Ferrari F2004 (2004) | 16 MB, 236 000 Dreiecke, 323 Teile | 3,2 MB | 80 000 / 26 000 / 9 000 | 16 / 16 / 15 |

Zum Vergleich: das F1-Auto im Spiel (`car.bin`) hat 110 000 / 34 000 / 12 000 Dreiecke.

## Aufbau jeder Datei
- Ausgerichtet wie die Spielautos: Meter, y = oben, +z = vorne, Boden y = 0, Mitte zwischen den Achsen z = 0, Wagenmitte x = 0.
  (Der Lotus war im Original 4-fach zu groß und stand rückwärts.)
- Wurzelknoten mit drei Kindern `LOD0`, `LOD1`, `LOD2`; `extras.lodDistances` = [0, 18, 45] m als Vorschlag für die Umschaltung.
- In jeder Stufe: `body` und die vier Räder `wheel_FL`, `wheel_FR`, `wheel_RL`, `wheel_RR` als eigene Knoten, deren Ursprung
  auf der Radachse liegt – zum Drehen nur `rotation.x` ändern. Radmitte, Radius und Breite stehen in `extras.wheels`.
- Kameras in `extras.cams` im Format von `MODELS.cam`/`.tv` im Spiel: `cockpit` und `tv` = [x, y, z, Absenkung des Blickziels in 30 m]
  (Cockpit blickt wie im Spiel zusätzlich 0,45 m tiefer; TV mit 78° Sichtfeld). z bezieht sich auf die Mitte zwischen den Achsen.
  Lotus: Cockpit [0, 0.90, 0.02, 0.3], TV [0, 1.10, -0.40, 1.8] · McLaren: [0, 0.88, -0.05, 0.15], [0, 1.02, -0.18, 1.8] ·
  Ferrari: [0, 0.80, 0.05, 0.3], [0, 1.16, -0.10, 2.0]. Ein Fahrer ist in den Modellen nicht enthalten (im Spiel kommt die Fahrerfigur dazu).
- Lackierung, Sponsoren und Reifenflanke bleiben als Textur (Lack/Sponsoren 1024 px, sonst 512 px), alles andere ist als
  Vertex-Farbe eingebacken; Normal-Maps entfallen. Positionen/Normalen quantisiert (`KHR_mesh_quantization`, lädt der
  GLTFLoader von three.js ohne Zusatz).

## Ansehen / neu bauen
- Vorschau: `modelle/klassiker/vorschau.html` über den lokalen Server öffnen (Auto, Detailstufe, Räder drehen).
- Neu bauen: `python tools/klassiker/build_klassiker.py <quelle.glb> <lotus49c|ferrari_f2004|mclaren_mp44> modelle/klassiker`
  (braucht numpy, scipy, pillow, pymeshlab; auf diesem Rechner das x64-Python 3.14).
