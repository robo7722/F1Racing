# Echte Lack-Texturen für F1 (und später F2)

Stand: 18.11.2026 (v2.73). Hintergrund und Entscheidung: `docs/IDEE-LIVERIES.md`, Abschnitt „Echte Texturen“.

Bis v2.72 entstand die Lackierung im Shader: Grundfarbe aus dem Lack-Programm (`glsl`), Aufkleberbogen **von der Seite** projiziert, Teamlogo eingeblendet.
Jetzt hat der Lack-Teil des F1-Modells (`car.bin`, Chunk `gloss`, alle drei Detailstufen) eine **UV-Abwicklung**, und jedes Team hat eine
**Textur** `liveries/textur/<Kürzel>.webp` (verlustfrei) wie die Klassiker-Modelle. Jede Fläche hat ihren festen Platz im Bild, also auch Oberseite, Front und Flügel.

## Werkzeuge (Reihenfolge)

```bash
python3 tools/textur/uv.py f1
```
Wickelt den Lack-Teil ab (xatlas; `pip install xatlas scipy numpy`). Liest immer die **unveränderte Vorlage** `tools/textur/quelle/car.bin`
und schreibt `car.bin` neu: Feld `uv` (uint16 × 2) je Eckpunkt im Chunk `gloss`, im Kopf `tex` = [Breite, Höhe].
- 300 Bildpunkte je Meter in Stufe 0 (`TPU`), Stufe 1/2 mit Maßstab 0,30/0,15 (ab 18 m bzw. 45 m reicht weniger) → Textur 1708 × 1710.
- Für die Abwicklung werden die Eckpunkte über die Lage verschweißt (das Modell ist an harten Kanten getrennt; sonst 6.000+ Einzelstücke).
  Lage, Normale und Klasse bleiben exakt wie in der Vorlage, nur an den Nähten werden Eckpunkte verdoppelt (Stufe 0: 33.442 → 48.923).
- **Nach jedem neuen Lauf müssen alle Texturen neu gebacken werden** (andere Abwicklung).

```bash
node tools/textur/backen.js            # alle F1-Lackierungen aus liveries/liveries.json
node tools/textur/backen.js MER FER    # nur diese
```
Startet das Spiel im Testbrowser mit `?nobake` (alte Projektion) und rendert den echten Lack-Shader jedes Teams in den UV-Raum: doppelte Auflösung,
verkleinert, Lücken zwischen den Stücken mit den Randfarben aufgefüllt (sonst bluten Mipmaps über die Nähte). Schreibt `liveries/textur/<Kürzel>.webp` (verlustfrei, halb so groß wie PNG; die PNG-Fassung liegt in `tools/textur/.cache/`)
und `liveries.json` (`_tex`, über `build.manifest()`). Dauert ~2 s je Team (plus ~15 s Start).
Die **Startnummer** gehört nicht in die Textur – sie bleibt eine Einblendung je Fahrer (`NUMS`, `numMat`).

**Wichtig:** Wer `tools/sticker/<Kürzel>.json` ändert und `build.py` laufen lässt, muss danach neu backen – das Spiel nimmt die Textur, nicht den Bogen
(`build.py` erinnert daran).

## Im Spiel (`index.html`)
- `parseCarBin`: liest `uv` → Attribut `uvB`, `tex` → `MODELS.f1.C.tex`. `paintGeo` reicht `uvB` durch.
- `LIVTEX` / `baked(tk)`: Team hat eine Textur (`_tex`) und das Modell UVs. Testschalter `?nobake` in der Adresse = alte Projektion.
- `liveryMat`: Lackklassen < 2,5 lesen `texture2D(uBake, vBUV)` statt `livery()`; Halo (Klasse 7) bleibt beim Lack-Programm (einfarbig).
  `decalGLSL` lässt Bogen und Logo weg, nur die Nummer bleibt. `decalUniforms` lädt dann die Textur statt Bogen und Logo
  (Touch-Geräte: halbe Auflösung wie bisher); `preloadDecals` wartet auch auf sie.
- Fernmodell (`farCarGeo`): UV aus Stufe 2. Gröbstes Fernmodell (`clusterGeo`, ab `CAR_FAR3`): `bakeColors` liest die Farben aus der Textur
  (auf 256² verkleinert) als Eckpunktfarben – beim Zusammenfassen der Punkte würden die UVs über die Nähte springen.
- Service Worker: `liveries/textur/` wird wie die Bögen immer zuerst am Server nachgefragt.

## Vergleich und Prüfen
`SHOT_Q='?nobake' node tools/sticker/shot.js MER <Vorsilbe> L,f34,top` nimmt die alte Fassung auf, ohne `SHOT_Q` die gebackene.

## Nächste Schritte (offen)
1. Oberseite/Front nach Referenzfotos bemalen: in `backen.js` zusätzliche Projektionen (von oben, von vorn, schräg) aus Präsentations- und
   Rennfotos – kostet im Spiel nichts mehr, weil alles in der Textur landet. Referenzen dafür fehlen noch (es gibt nur offizielle Seitenfotos).
2. Textur direkt in einem Malprogramm nachbearbeiten (dafür eine Vorlage mit den Umrissen der Stücke erzeugen).
3. F2 (`f2car.bin`) genauso: `uv.py f2`, F2-Zweig in `teamTemplate` (eigener Shader) umstellen.
