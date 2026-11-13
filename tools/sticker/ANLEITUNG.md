# Aufkleber für ein Auto anlegen

Ziel: Das Auto im Spiel soll dem echten Auto der Saison 2026 so nahe wie möglich kommen – Grundfarbe, große farbige Flächen, Sponsoren, Startnummer.
Alles, was ein Auto beschreibt, steht in **einer** Datei: `tools/sticker/<Kürzel>.json`. Daraus entsteht der Aufkleberbogen `liveries/<Kürzel>.png` und der Eintrag in `liveries/liveries.json`, den das Spiel liest. `index.html` wird dafür nicht angefasst.

Kürzel: F1 = Teamkürzel (`MER`, `FER`, …). F2 = `F2_` + Lackierung (`F2_INV`, `F2_INV1`, …), siehe `LIV` und `F2_DRIVERS` in `index.html` (letzter Wert je Fahrer).

## Wie das Spiel die Angaben verwendet

1. **Grundfarbe** (`glsl`): ein kleines Programm, das für jeden Punkt des Autos eine Farbe liefert. Nur schlichte Flächen – Wagenfarbe, andersfarbige Flügel/Nase/Unterseite und Farbflächen auf der **Oberseite**, die ein Seiten-Aufkleber nicht erreicht.
2. **Aufkleberbogen** (`stickers`): Ausschnitte aus dem Seitenfoto des echten Autos, **von der Seite** aufs Modell projiziert, auf beide Fahrzeugseiten (Schrift bleibt überall lesbar). Erreicht nur Flächen, die zur Seite zeigen. Liegt über der Grundfarbe.
3. **Teamlogo** (`logos`): das Logo aus `logos/<logoFile>.png` an festen Stellen, vor allem oben auf der Nase.
4. **Startnummer** (`number`): Grafik im Design des Fahrers (liegt schon in `liveries/num/`), je Fahrer automatisch, in der angegebenen Farbe an den angegebenen Stellen.

Aufkleber landen nur auf lackierten Teilen. Carbon-Teile (Unterboden, viele Kleinteile), Reifen, Felgen und das **Halo** bekommen nichts – Schriftzüge dort einfach weglassen.

## Koordinaten am Modell (Meter)

`x` quer (links positiv), `y` hoch (Boden = 0), `z` nach vorn.

| | F1 | F2 |
|---|---|---|
| Hinterachse z | −1,575 | −1,712 |
| Vorderachse z | 1,825 | 1,4335 |
| Radmitte y | 0,36 | 0,30 |
| Länge z | −2,33 … 3,07 | −2,45 … 2,80 |
| höchster Punkt y | 1,10 | 1,17 |

## Ablauf

```bash
python3 tools/sticker/photo.py <Kürzel> "<Adresse des Seitenfotos>"
```
schreibt nach `tools/sticker/.cache/`: `<Kürzel>_ganz.png` (Übersicht) und `<Kürzel>_teil0.png …` (Originalgröße mit Pixelraster). Die Rasterzahlen sind Pixel des Originalfotos – genau diese Werte gehören in die Datei. Für genaues Ausmessen kleiner Bereiche: `python3 tools/sticker/photo.py <Kürzel> --zoom x0 y0 x1 y1` → `<Kürzel>_zoom.png`.

```bash
python3 tools/sticker/build.py <Kürzel>
```
baut den Bogen (Vorschau: `.cache/<Kürzel>_bogen.png`) und schreibt `liveries/liveries.json` neu.

```bash
node tools/sticker/shot.js <Kürzel> tools/sticker/.cache/<Kürzel> L,R,Lf,Lm,Lr,f34
```
startet das Spiel im Testbrowser und nimmt das Auto im Showroom auf (`<Vorsilbe>_<Ansicht>.png`). Dauert 1–4 Minuten (Zeitlimit großzügig setzen, z. B. 10 Minuten), deshalb mehrere Ansichten in **einem** Aufruf holen und nie zwei Aufrufe gleichzeitig starten.
Ansichten: `L`/`R` ganze Seite, `Lf Lm Lr`/`Rf Rm Rr` vorderes/mittleres/hinteres Drittel vergrößert, `top` von oben, `f34`/`r34` schräg von vorn/hinten (links), `f34R`/`r34R` rechts.
Zeilen mit `SHADER` oder `SEITENFEHLER` in der Ausgabe bedeuten einen Fehler im `glsl` – dann bleibt das Auto falsch gefärbt; beheben.

Offizielle Seitenfotos (durchsichtiger Hintergrund):
- F1: `https://media.formula1.com/image/upload/v1740000001/common/f1/2026/<team>/2026<team>carright.png` mit `<team>` = mercedes, ferrari, mclaren, redbullracing, astonmartin, williams, racingbulls, alpine, haasf1team, audi, cadillac
- F2: `https://res.cloudinary.com/prod-f2f3/v1770000000/common/f2/2026/<team>/2026<team>carleft.png` mit `<team>` = invictaracing, hitech, camposracing, damslucasoil, mpmotorsport, premaracing, rodinmotorsport, artgrandprix, aixracing, vanamersfoortracing, trident

## Die Datei

```json
{
 "kind": "f1",
 "photo": "https://…carright.png",
 "rear": [523, 563], "front": [3104, 563],
 "glsl": ["vec3 col = #0d0f12;", "if (c > 0.5 && c < 1.5) col = #101216;", "return col;"],
 "stickers": [
  { "name": "schwung",  "box": [900, 380, 2300, 560], "kind": "key", "key": "#00a19c" },
  { "name": "petronas", "box": [1294, 483, 1991, 579], "kind": "w" },
  { "name": "microsoft","box": [1447, 99, 1751, 176], "kind": "c", "at": [-0.36, 0.90], "w": 0.36 }
 ],
 "zones": [[0.98, 1.36, 0, 0.4]],
 "logoFile": "MER", "logos": [{ "v": "top", "x": 0, "z": 1.5, "s": 0.2 }],
 "number": { "color": "#00d2be", "spots": [{ "v": "side", "z": -1.2, "y": 0.8, "s": 0.18 }, { "v": "top", "x": 0, "z": 2.0, "s": 0.13 }] }
}
```
F2 zusätzlich: `"kind": "f2"`, `"team": "F2_INV"`, `"driver": "DUR"` (Fahrer fürs Testbild), `"drivers": ["DUR"]` (wer diese Lackierung im Spiel fährt), `"liv": { "body": "#f2d100", "acc": "#16181b", "tip": "#16181b", "metal": 0.25 }` (Hauptfarben für Fernansicht und Menü – immer angeben, passend zum `glsl`).

### `rear` / `front`
Mitte des Hinter- und Vorderrads im Foto (Pixel). Daraus wird jede `box` automatisch an die passende Stelle des Modells gerechnet. Weil das Modell nicht genau die Form des echten Autos hat, sitzt manches danach daneben – dann je Aufkleber mit `at` (Mitte z, y), `w`/`h` (Breite/Höhe in Metern) oder `dz`/`dy` (verschieben) nachhelfen.

### `glsl` – Grundfarbe
Rumpf von `vec3 livery(vec3 p, float c)`; muss mit `return <vec3>;` enden. `p` = Punkt am Modell in Metern, `c` = Teileklasse (F1: 0 Lack, 1 Flügel/Anbauteile, 2 Nasenspitze, 7 Halo; F2: immer 0 – dort Flügel über die Lage bestimmen: Frontflügel `p.z > 2.15 && p.y < 0.36`, Nasenspitze `p.z > 2.55`, Heckflügel `p.z < -1.9 && p.y > 0.6`).
Farben als `#rrggbb`. Hilfen: `aaS(d)` = weiche Kante (0 unter, 1 über d = 0), `band(d, a, b)` = 1 zwischen a und b; `mix`, `clamp`, `abs`, `smoothstep` wie üblich.
Bei F1 steht das bisherige Programm in `index.html` unter `const LIVERY = {` → `<Kürzel>:` – als Ausgangspunkt lesen (dort steht `${lc(0x…)}` statt `#…`). **Alles, was jetzt als Aufkleber von der Seite kommt, aus dem Programm entfernen** (sonst steht es doppelt und leicht versetzt). Flächen auf der Oberseite (Motorabdeckung von oben, Nase von oben) dürfen bleiben, wenn sie zum echten Auto passen. Das Halo (`c > 6.5`) einfarbig lassen.

### `stickers`
Reihenfolge = Schichtung: zuerst große Farbflächen, dann Schriftzüge.
- `"kind": "key"` – **große farbige Flächen und Streifen der Lackierung**: alles im Ausschnitt, was der Farbe `key` ähnelt, wird eine glatte Fläche in dieser Farbe (Schatten und Spiegelungen des Fotos verschwinden). `tol` regelt die Toleranz (bunt: Farbton in Grad, Standard 28; Grau/Weiß/Schwarz: Farbabstand, Standard 60), `color` setzt eine andere Ausgabefarbe. Den Ausschnitt so legen, dass keine Reifen, Felgen oder das Halo drin sind.
- `"kind": "w"` – helle Schrift auf dunklem Grund → rein weiß (`color` für andere Farbe).
- `"kind": "d"` – dunkle Schrift auf hellem Grund → schwarz (`color` für andere Farbe).
- `"kind": "c"` – mehrfarbige Logos: Farben bleiben, der Untergrund (Randfarbe des Ausschnitts) wird durchsichtig. Ausschnitt knapp, aber mit 3–6 Pixel einfarbigem Rand.
- `thr: [lo, hi]` (0…1) verschiebt die Schwelle, wenn Schrift zu dünn (kleiner) oder Untergrund mit drin ist (größer). Standard `[0.45, 0.85]`.
- `side`: `"L"` oder `"R"`, wenn etwas nur auf eine Seite gehört.

Der Bogen hat rund 370 Pixel je Meter: Schriftzüge unter etwa 8 cm Breite lohnen nicht. Reifenbeschriftung, Halo-Aufkleber und die **Startnummer aus dem Foto nicht ausschneiden**.

### `zones`
Liegen zwei lackierte Flächen hintereinander (z. B. Chassis-Seite und Seitenkasten-Einlass), erscheint ein Aufkleber auf beiden. `[z von, z bis, |x| von, |x| bis]` beschränkt in diesem Längenabschnitt auf einen Abstand von der Mitte.

### `logos` und `number`
`v: "top"`: von oben, `x`/`z` = Mitte, `s` = Kantenlänge (Logo) bzw. Ziffernhöhe (Nummer; das Feld ist doppelt so breit). `v: "side"`: von der Seite, `z`/`y` = Mitte; `x0`/`x1` begrenzen den Abstand von der Mitte.
Logo nur dort, wo das echte Auto eins hat und es sich vom Lack abhebt (die Logos in `logos/` sind weiß) – sonst `logos` weglassen.
Nummer: Farbe und Stellen wie am echten Auto (meist Nase oben und seitlich an Motorabdeckung/Heckflosse). Die Stelle muss eine lackierte Fläche treffen – im Bild prüfen.

## Prüfen
- Beide Seiten ansehen (`L` und `R`): Schrift lesbar, nichts doppelt, nichts über Kanten verschmiert, keine Reste vom Foto-Untergrund um die Schrift.
- Farben mit dem Foto vergleichen.
- Höchstens drei bis vier Runden; was dann nicht sauber wird, lieber weglassen als schief lassen.
