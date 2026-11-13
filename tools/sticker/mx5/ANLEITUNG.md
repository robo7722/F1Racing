# Aufkleber des Roadsters (RONE Racing)

Ziel: Der Roadster im Spiel trägt die Aufkleber des echten Autos, 1:1 nach den Fotos (Stand November 2026).

## Wie es funktioniert

Anders als bei den F1- und F2-Autos (Bogen wird im Shader von der Seite aufprojiziert) sind die Roadster-Aufkleber ein **eigenes dünnes Netz**, das 3 mm über Lack bzw. Scheibe liegt:

- `liveries/MX5.png` – Bogen 2048 × 2048 mit allen Aufklebern (weiß bzw. schwarz auf durchsichtig).
- `liveries/MX5.json` – fertiges Netz: Punkte (`p`, in 1/10 mm), Bogen-Koordinaten (`uv`, in 1/8192), Dreiecke (`i`).
- `index.html`: `ROADSTK` lädt beide Dateien, `roadStickers()` baut daraus ein Netz mit einem Material, `makeRoadster()` hängt es ans Auto. Kostet einen Zeichenaufruf, keine Rechenzeit im Shader.
- Fehlt eine der Dateien, zeichnet `roadPaint()` wie früher die grobe Fassung in die Lack-Textur.

Vorteil: Die Schärfe hängt nicht von der Lack-Textur ab (die hat nur rund 210 Pixel je Meter), und Aufkleber auf Front, Heck und Scheiben sind möglich.

## Neu bauen

```bash
python3 tools/sticker/mx5/bauen.py
```

liest `bilder/*.png` und `roadcar.bin`, schreibt Bogen und Netz. Dauert zwei Sekunden. Prüfen:

```bash
node tools/sticker/shot.js RON tools/sticker/.cache/RON L,R,F,B,top,f34n,r34n,Lr,Rf
```

Die Liste `A` in `bauen.py` legt je Aufkleber fest: Bild, Blickrichtung (`L R T F B`), Mitte, Breite in Metern, Drehung, `flip` (spiegeln), `teil` (`lack` oder `glas`), `auto` (Blickrichtung = Flächennormale, für schräge Flächen wie Stoßstangenecke und Tankdeckel).

## Was wo sitzt

| Aufkleber | Ort | Quelle |
|---|---|---|
| Sponsoren-Säule (O·Z, Kenwood, Alpine, NOS, momo, sparco, Yokohama, GReddy) | beide Türen vorn | Seitenfoto links, entzerrt |
| Pirelli | beide Kotflügel vor der Tür | Seitenfoto links |
| schwarze Grafik mit rotem Pfeil-Umriss | beide Seiten, Tür bis hinterer Kotflügel (rechts gespiegelt) | Seitenfoto links; hinteres Ende von Hand ergänzt |
| R.Nemec mit Flagge | beide Türscheiben | nachgesetzt (Inter Bold) |
| Pentagramm | Tankdeckel links | Nahaufnahme, Ellipse zum Kreis entzerrt |
| MAZDASPEED | Stoßstangenecke vorn links, Heck links | Nachtfoto |
| 666 (Fraktur) | Stoßstangenecke vorn rechts | Parkhaus-Foto |
| Oni-Maske 死神谷 | Haube | Nachtfoto frontal, senkrecht um 1,146 gestreckt |
| @Natsukithemiata | Frontlippe | Nachtfoto frontal |
| Limitless Society | Heck links unter der Rückleuchte | Hallenfoto |
| Fisch 666 | Heck rechts unter der Rückleuchte | Nachtfoto |
| スピードハンターズ | Windschutzscheibe oben | Hallenfoto |

Das Modell ist rund 1,157-mal so groß wie das echte Auto; alle Maße sind Modellmaße.

## Fotos zuschneiden (`foto/`)

Die Skripte in `foto/` sind die Arbeitsfassung, mit der die Einzelbilder aus den Fotos entstanden sind. Die Fotos selbst liegen **nicht** im Projekt (Kennzeichen, Personen). Wer neu schneiden will, legt sie als `src/p1.png … p13.png` daneben.

- `side.py`: Seitenfoto über die beiden Radmitten projektiv auf Modellkoordinaten entzerren (danach stimmen Lage und Größe ohne Nacharbeit).
- `cut.py`, `sprites.py`, `adapt.py`: Ausschnitt entzerren, Weiß vom Lack trennen (Helligkeit minus Sättigung bzw. örtliche Schwelle bei dunklen Fotos), kleine Reste entfernen.
- `graf.py`: schwarze Grafik als Maske („nicht rot und dunkel").
- `pent.py`: Ellipse des Rings finden, zum Kreis entzerren.

## Offen

- Nicht übernommen: BLACKLIST-Aufkleber am Heckspoiler (das Modell hat keinen Spoiler), „southsiderz" über der rechten Rückleuchte (im Foto zu klein), die kleinen Plaketten in der Windschutzscheibe, die weißen Dreiecke neben dem vorderen Kennzeichen (nur auf einem älteren Foto).
- Hinteres Kennzeichen bleibt „RONE 666".
- Nur im Showroom geprüft, nicht im Rennen und nicht auf einem echten Handy.
