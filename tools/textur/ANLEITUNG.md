# Echte Lack-Texturen für F1 und F2

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
- Stufe 0 und 1 mit gleicher Dichte, Stufe 2 mit Maßstab 0,15 (erst ab 35 m); die Dichte wird so gewählt, dass die Textur höchstens 2048 breit/hoch ist
  → 2037 × 2041, 271 Bildpunkte je Meter. **Stufe 1 muss voll sein:** das eigene Auto fährt in den Verfolgerkameras mit Stufe 1, Gegner ab 6 m
  (v2.73 hatte 0,30 → im Rennen deutlich unschärfer als im Showroom, Rückmeldung des Nutzers).
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
  (Touch-Geräte: halbe Auflösung, nur die Lackierung des gewählten Fahrers voll – `ownLiv`); `preloadDecals` wartet auch auf sie.
- Fernmodell (`farCarGeo`): UV aus Stufe 2. Gröbstes Fernmodell (`clusterGeo`, ab `CAR_FAR3`): `bakeColors` liest die Farben aus der Textur
  (auf 256² verkleinert) als Eckpunktfarben – beim Zusammenfassen der Punkte würden die UVs über die Nähte springen.
- Service Worker: `liveries/textur/` wird wie die Bögen immer zuerst am Server nachgefragt.
- **Cockpit-Schale (`cockNew`, Helm- und TV-Kamera) – Fehler bis v2.98, behoben in v2.99:** Die Schale ersetzt in diesen Kameras die Karosserie rund ums Cockpit,
  hat aber keine UV der Lack-Textur (`uvB` fehlt). Ihr Material ist eine Kopie des Lack-Materials – seit v2.73 las es deshalb überall denselben Bildpunkt der
  Textur: die Fläche vor dem Cockpit war einfarbig hellgrau statt lackiert (Rückmeldung 24.11.2026: „Texturen werden in Cockpit- und TV-Ansicht nicht richtig
  geladen“). Jetzt ersetzt der Haken des Schalen-Materials den Texturzugriff wieder durch das Lack-Programm (`livery(vLP, vCls)` an der Lackierposition `aLP`)
  und trägt Bogen und Teamlogo wie vor v2.73 per Projektion auf (`decalGLSL(tk, true)`); `decalProj(tk)` lädt dafür Bogen und Logo des eigenen Teams nach
  (bei gebackenen Teams sind sie sonst nicht geladen). Prüfen: `node tools/wetter/regen_bilder.js Spa dry <Ordner> 2150,2 2150,3 --pre "S.driver = 'VER'; MENU.team = byCode('VER').team"`.
  Merke: Wer am Lack-Shader etwas ändert, das Attribute des Fahrzeugmodells braucht, muss die Schale mit prüfen (eigene Geometrie, nur `position`/`uv`/`aLP`/`aCls`).

## Ansicht von oben (seit v2.75)
In `tools/sticker/<Kürzel>.json` ein Eintrag `top` (Beschreibung im Kopf von `build.py`): Foto von oben, Achsmitten (`rear`/`front`) oder
4+ Passpunkte (`pts`, für schräge Fotos), Aufkleber wie bei der Seite. `build.py` richtet das Foto aus (`.cache/<Kürzel>_oben_ganz.png`,
300 Pixel je Meter, Nase oben, Raster zum Ausmessen in `_oben_raster.png`) und baut `.cache/<Kürzel>_oben_bogen.png`.
`backen.js` legt den Bogen auf alle Lackflächen, deren Normale nach oben zeigt (weich zwischen 0,5 und 0,72 – darunter gilt die Seite, sonst stehen Schriftzüge an Schultern doppelt), und nur dort, wo die Fläche von oben zu sehen ist
(Höhenkarte aus Stufe 0, 4 cm Spielraum). Im Spiel kostet das nichts zusätzlich. Ablauf: `build.py <Kürzel>` → `backen.js <Kürzel>` → `shot.js … top,f34`.

## Vergleich und Prüfen
`shot.js` setzt seit v2.74 auch bei F1 einen Fahrer des Teams (vorher zeigte der Titelbildschirm immer das Auto des gewählten Fahrers, z. B. Russell).
`SHOT_Q='?nobake' node tools/sticker/shot.js MER <Vorsilbe> L,f34,top` nimmt die alte Fassung auf, ohne `SHOT_Q` die gebackene.

## Nächste Schritte (offen)
1. Oberseite/Front nach Referenzfotos bemalen: in `backen.js` zusätzliche Projektionen (von oben, von vorn, schräg) aus Präsentations- und
   Rennfotos – kostet im Spiel nichts mehr, weil alles in der Textur landet. Referenzen dafür fehlen noch (es gibt nur offizielle Seitenfotos).
2. Textur direkt in einem Malprogramm nachbearbeiten (dafür eine Vorlage mit den Umrissen der Stücke erzeugen).
3. ~~F2~~ erledigt in v2.75 (`uv.py f2`: 1809 × 1809, 300 Bildpunkte je Meter). Alle F2-Lackierungen haben ein Lack-Programm und laufen deshalb
   über `liveryMat` wie F1 (der F2-Zweig in `teamTemplate` wird davon überschrieben). Teams ohne Lack-Programm (RONE) überspringt `backen.js`.

## Rezept: ein Team von oben bemalen (am Mercedes erprobt, 18.11.2026)
Fotos von oben: `tools/sticker/.cache/oben/<Kürzel>_<n>.*` (nicht im Repo; Quellen stehen in `tools/sticker/<Kürzel>.json` unter `top.src`).
1. Achsen im Originalfoto bestimmen (Mitte zwischen den beiden Vorderrädern bzw. Hinterrädern, auf der Wagenmitte), als `top.rear`/`top.front`
   eintragen, `top.photo` = Pfad, `top.src` = Quelle, `stickers: []`. `python3 tools/sticker/build.py <K>` → `.cache/<K>_oben_raster.png` ansehen:
   Vorderräder müssen bei z ≈ 1,8, Hinterräder bei z ≈ −1,6 liegen, Nase oben. Schräges Foto: statt rear/front `pts` mit 4+ Punkten [px, py, x, z].
2. Ausmessen im ausgerichteten Bild `.cache/<K>_oben_ganz.png` (300 px/m; Pixel-Raster: x_px = (1,15 − x)·300, y_px = (3,15 − z)·300 für F1,
   (3,0 − z)·300 für F2). Vergrößerte Ausschnitte mit Pixel-Skala anlegen und genau ablesen.
3. Aufkleber in dieser Reihenfolge: große Farbflächen (`key`, `smooth` 3–6, `holes: false` wenn Streifen/Schrift der Grundfarbe durchscheinen sollen,
   bei Grau/Silber `tol` 80–100 und mit `poly` auf die Lackflächen begrenzen, sonst greift der graue Boden mit), danach Schriftzüge (`w` hell auf dunkel,
   `d` dunkel auf hell, `c` mehrfarbig). Halo, Reifen, Spiegel und Carbon-Teile weglassen; die Startnummer auf der Nase NICHT ausschneiden.
4. Lackierte Oberseiten am F1-Modell: Nase z 1,0 … 3,06 (bei z = 2 nur ±0,17 breit), Seitenkästen z −1,32 … 1,16 bis |x| 0,88,
   Heckflügel z −2,32 … −1,76, |x| ≤ 0,57, Höhe 0,76 … 0,91 (Fotos zeigen ihn oft weiter hinten → mit `at` [x, z] und `w` setzen).
   F2: Nase z 1,02 … 2,79, Seitenkästen z −1,41 … 0,66 bis |x| 0,78, Heckflügel z −2,34 … −1,96.
   Der Frontflügel ist am Modell überwiegend Carbon (bekommt keine Aufkleber).
5. `python3 tools/sticker/build.py <K>` → `node tools/textur/backen.js <K>` → `node tools/sticker/shot.js <K> <Vorsilbe> top,f34,f34n,hk` ansehen,
   höchstens 3–4 Runden. Die Ansicht von oben greift nur auf Flächen, deren Normale deutlich nach oben zeigt (ab 0,5); seitliche Flächen bleiben beim Seitenbogen.
6. **Regeln (Nutzer, 18.11.2026):** spiegelgleich (build.py macht Flächen symmetrisch und setzt Logos auf die Gegenseite; mit `top.sym` die besser
   sichtbare Seite wählen); nichts doppelt, was der Seitenbogen schon trägt; Draufsicht wird VOR dem Seitenbogen aufgetragen (Seite gewinnt an Schultern).
