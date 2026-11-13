# Rennfahrer-Modell (stehende Figur)

Stand: 13.11.2026 – Vorschau fertig, noch nicht im Spiel eingebaut.

## Dateien
- `fahrer/fahrer.glb` – Körper im Rennanzug (Tripo-Vorlage), 1,78 m, Füße auf y = 0, Blick nach +z. Ohne Kopf und Hände.
- `fahrer/handschuh.glb` – rechter Handschuh, schon an die rechte Hand gesetzt. Links = gespiegelt (`scale.x = -1`).
- `fahrer/vorschau.html` – Vorschau mit unserem Spiel-Helm (`HELM_BIN`, Design wie NEM). Braucht `helm_bin.js` (Kopie aus `index.html`).
- `tools/fahrer/build_fahrer.py <quellordner>` – baut beide GLB neu. Quellordner: `model.obj`, `base.jpg`, `normal.jpg` (Tripo), `glove.kmz` (Handschuh). Die Vorlagen liegen nicht im Repo (OBJ 25 MB).

## Was das Skript macht
- Tripo-Körper: auf 1,78 m skaliert, lose Splitter-Dreiecke entfernt, Kopf mit Tripo-Helm entfernt (unser Helm kommt drauf), Hände ab dem Ärmelbündchen entfernt.
- Handschuh: gedreht (Finger nach unten, Handfläche zum Oberschenkel, Daumen nach vorn), Hand leicht nach vorn geneigt, Finger locker gekrümmt (Biegung ab der Knöchellinie, ~40° an den Spitzen). Stulpe gekürzt: steckt unter dem Ärmel, das Bündchen liegt darüber; was ganz im Ärmel verschwindet, ist abgeschnitten.
- Logo-Schriftzug auf der Klett-Lasche des Handschuhs rot übermalt (war durch die Verformung ein weißer Fleck).
- Helm (nur Vorschau): Anbauteil unter dem Visier (Zone 3 am Kinn) wird im Shader verworfen. Im Spiel selbst ist es noch drin.

## Offen
- Textur des Anzugs: dunkle Fehlstellen an den Stiefelfersen, unter den Achseln, an den Seitennähten – noch nicht ausgebessert.
- Ärmelende leicht ausgefranst (Schnittkante der Tripo-Hand), von Nahem sichtbar.
- 16 nicht-mannigfaltige Kanten im Netz (unsichtbar, nicht repariert).
- Textur trägt echte Sponsoren-Logos (privat ok, öffentlich bedenken).
- Größe: Körper ~210 000 Dreiecke – für Handys später verkleinern.
- Einbau ins Spiel (z. B. Podium/Showroom) und Teamfarben steht noch aus.
