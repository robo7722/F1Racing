# Strecken-Anleitung: Neue Rennstrecke einbauen

Diese Anleitung beschreibt, wie eine neue Strecke in `index.html` eingebaut wird. Sie ist aus dem Code abgeleitet (Stand Version 1.01). Zeilennummern sind ungefähr; im Zweifel nach dem Namen suchen (`grep -n "function buildTrack" index.html`).

Wichtig vorab: Die Datei enthält riesige Datenzeilen (Streckenpunkte, OSM-Grundrisse). Nie die ganze Datei öffnen, sondern bereichsweise lesen, z. B. `sed -n '3222,3300p' index.html | cut -c1-900`.

Stellen, an denen der Code nicht eindeutig ist, sind mit **(unklar)** markiert.

---

## 1. Kurzüberblick: Ablauf in 10 Schritten

1. **Streckenverlauf besorgen**: Mittellinie als Punktliste in Metern (x = Osten, z = Süden), in Fahrtrichtung, geschlossen; dazu halbe Fahrbahnbreite je Punkt, optional Höhe je Punkt.
2. **Daten eintragen**: `Object.assign(TRACK_HD, { 'xx-jahr': { pts: [...], hw: [...], el: [...] } })` (bei ca. Zeile 935–955).
3. **Streckeneintrag anlegen**: neuer Schlüssel in `TRACKS` (Zeile ~956) bzw. bei Kartbahnen im `Object.assign(TRACKS, {...})` (~970).
4. **Theme anlegen**: neuer Eintrag in `THEMES` (~974). Am einfachsten ein ähnliches Theme kopieren (`{ ...THEMES.sil, ... }` wie bei `genk`/`wack`) und anpassen.
5. **Asphalt wählen**: `asph` im Theme, optional Foto-Textur in `ROADTEX` (~1612) und Mischung in `asphaltFor` (~1617).
6. **Kalender/Menü**: `TRACK_INFO` (~6807, Kurvenzahl und Farbe der Menükarte), `CAL_F1` (~6592), `F2_DATES` (~6593), `SERIES.*.cal` (~918).
7. **Erster Bau**: Spiel laden, in der Konsole `__build('schlüssel')`. Die Strecke bekommt Fahrbahn, Kerbs, Auslauf, Mauern, Zäune, Bäume, Boxengasse, Tribünen, Schatten und KI automatisch.
8. **Streckenrand nachbessern**: Tribünenplan (`stands`), Auslaufart (`runoffKind`), Wandabstände (`wall`, `runoff`), ggf. Wahrzeichen (`osm`) und Stadt (`city`, `cityBelt`).
9. **Look einstellen**: Himmel, Dunst, Sonne, `look`-Block (Abschnitt 3).
10. **Testen**: Checkliste in Abschnitt 7 (`__clipAll`, `__onRoad`, `__bldOverlap`, `__bench`, `__pace`, `__sim`). Danach Versionsnummer und `CACHE`-Name in `sw.js` erhöhen.

---

## 2. Streckendaten

### 2.1 Koordinaten und Vorzeichen

- Einheit Meter, `x` nach Osten, `z` nach **Süden** (so steht es in den Datenkommentaren: „Meter, z = Süden“). Höhe ist `y`.
- Position entlang der Strecke: `s` in Metern ab Start/Ziel (Punkt 0 der Daten = Startlinie). Negative `s` sind erlaubt (werden mit der Rundenlänge umgebrochen), z. B. `-250` = 250 m vor der Linie.
- Seitlicher Versatz `lat`: **positiv = rechts vom Fahrer**, negativ = links. Entsprechend `WR`/`KERBR`/`GRR` = rechts, `WL`/`KERBL`/`GRL` = links.
- `trackAt(s, lat)` liefert `{x, z, h, i}` (Weltposition, Fahrtrichtung als Winkel, Abschnittsindex).

### 2.2 Datenquellen

| Konstante | Inhalt | Format |
|---|---|---|
| `TRACK_PTS` | grobe Mittellinie (ältere Strecken) | `{ 'it-1922': [[x,z], ...] }` |
| `TRACK_HD` | hochaufgelöste Mittellinie (ca. alle 5 m), das ist die Quelle für den Bau | `{ key: { pts: [[x,z],...], hw: [..], el: [..], s: [..] } }` |
| `OSM_LM` | Wahrzeichen aus OpenStreetMap je Strecke | `{ yas: { b: [ { n: 'Name', r: [[x,z],...], h: Höhe, s: 'Stil' } ], ... } }` |
| `NS_DATA` | Sonderdaten Nordschleife | `wl`/`wr` (Leitplankenabstand je HD-Punkt), `kl`/`kr`/`fl`/`fr` (Zeichenketten aus `0`/`1` je HD-Punkt: Kerb links/rechts, Fangzaun links/rechts), `open`, `karussell`, `hotel`, … |
| `MEL_REF`, `MONZA_REF` | vermessene Referenzdaten (Tribünen, Boxen, Bäume, See …) | siehe `TRK.ref` unten |

Details zu `TRACK_HD`:
- `pts`: Pflicht. Geschlossene Linie; der letzte Punkt muss nicht dem ersten gleichen (die Kurve wird als geschlossener Catmull-Rom-Spline gelesen).
- `hw`: Pflicht. **Halbe** Fahrbahnbreite in Metern, ein Wert je Punkt in `pts` (gleiche Länge). Der Bau klemmt auf mindestens 3,8 m und glättet.
- `el`: optional. Höhe in Metern je Punkt. Fehlt `el`, ist die Strecke flach (`FLAT = true`): Boden ist dann eine einfache Ebene, viele Geländeschritte entfallen.
- `s`: bei drei Strecken vorhanden (Streckenmeter je Punkt). Wird vom Bau nicht gelesen **(unklar, vermutlich nur Herkunftsdaten)**.
- Bisherige Quellen: TUM racetrack-database (LGPL-3.0), bacinger/f1-circuits (MIT), OpenStreetMap (ODbL). Lizenzhinweis als Kommentar über den Daten beibehalten.

### 2.3 Felder eines `TRACKS`-Eintrags

Pflichtfelder:

| Feld | Bedeutung |
|---|---|
| `name` | Kurzname im Menü; `__go('name')` sucht danach |
| `full` | voller Streckenname |
| `land` | Land |
| `km` | Länge als Text, z. B. `'5,793 km'` (nur Anzeige; die echte Länge `L` wird aus den Punkten berechnet) |
| `laps` | volle Renndistanz in Runden (Menü-Chip „(voll)“) |
| `pts` | ausgedünnte Punktliste. Üblich: `TRACK_HD[key].pts.filter((_, k) => k % 3 === 0)`. Im Bau selbst wird `pts` nur für `marina` gelesen; ob Minikarte/Menü es nutzen, habe ich nicht gefunden **(unklar)**. Trotzdem immer setzen. |
| `hd` | der `TRACK_HD`-Eintrag; daraus wird gebaut |
| `theme` | Schlüssel in `THEMES` |

Allgemeine Optionen:

| Feld | Wirkung |
|---|---|
| `kartOnly: true` | Strecke erscheint nur in der Kart-Klasse; Zäune werden in U-Kurven auf die Mitte zwischen zwei Streckenteilen begrenzt |
| `kartLaps` | bei den Kartbahnen gesetzt (8); eine Lesestelle habe ich nicht gefunden **(unklar)** |
| `extra: true` | Bonusstrecke: nur sichtbar, wenn die Einstellung `S.nos` aktiv ist (Nordschleife); andere Runden-Chips (1/2/3/5) |
| `noPit: true` | keine Boxengasse und kein Boxengebäude |
| `noStands: true` | keine automatischen Tribünen |
| `stands` | Tribünenplan: `[[sVon, sBis, Seite, Länge], ...]`. Seite: `'opp'` (gegenüber der Boxengasse), `'out'` (Außenseite der Runde), `'in'` (Innenseite), `'L'`, `'R'`. Länge Standard 44 m. Zwischen `sVon` und `sBis` wird alle `Länge + 2` m eine Tribüne versucht. |
| `standSkip` | `[[sVon, sBis], ...]`: Bereiche, in denen trotz Plan keine Tribüne gebaut wird |
| `standDep` | Tiefe der Tribünen (Standard 21 m; Monaco 12 = schmal und steil) |
| `pitOut: true` | Boxengasse auf der Außenseite statt innen (Abu Dhabi) |
| `osm` | `OSM_LM`-Eintrag: Gebäude aus `osm.b` werden an echter Lage und Höhe extrudiert (Abschnitt 4.6) |
| `city` | `[x, z]`: Zentrum einer Hochhaus-Innenstadt im Hintergrund |
| `citySp` | `[sx, sz]`: Streuung der Innenstadt (Standard 750/800 m) |
| `cityBelt` | `[x0, x1, z0, z1]`: Rechteck mit mittelhohen Häusern (30–115 m) |
| `cityMul` | Faktor für die Anzahl der Stadtgebäude |
| `cityMinD` | Mindestabstand der Häuser zur Strecke; ist es gesetzt, reihen sich Häuser direkt hinter der Leitplanke (Stadtkurs) |
| `cityH` | `[min, max]`: Höhenbereich der Innenstadt |
| `noTall`, `resiTall` | keine Hochhäuser / hohe Wohnhäuser (Monaco); `resiTall` nicht im Detail geprüft **(unklar)** |
| `lake` | `[Umriss, Loch1, ...]`: Wasserfläche als Polygonliste; mit `bay: true` als Bucht mit Kaimauer |
| `parks` | Singapur: `[[Länge, Breite, w, h, Drehung], ...]` in Geokoordinaten; wird nur zusammen mit `sgp` ausgewertet |
| `ref`, `refTrees` | vermessene Referenzdaten (`ref.stands`, `ref.box`, `ref.bld`, `ref.tents`, `ref.trees`, `ref.lake` …). Mit `ref` werden Tribünen aus `ref.stands` gebaut und Mauern vor Gebäuden freigehalten; `refTrees: true` setzt Bäume genau an `ref.trees` statt zufällig. |
| `bakeRes`, `bakeCell` | Auflösung und Kachelgröße der gebackenen Schatten (Standard 1024 Texel auf 192 m). Für sehr lange Strecken kleiner/gröber (Nordschleife 512/256). |

Streckenspezifische Schalter (nur zur Einordnung, für neue Strecken nicht wiederverwenden, sondern bei Bedarf ein eigenes Feld anlegen): `monza`, `mc`, `mtl`, `sgp`, `nos`, `wing`, `tower`, `hotel`/`hotelAx`/`hotelLen`/`hotelHead`/`hotelBody`, `marina`, `dome`, `sphere`, `vegasOsm`, `stripX`, `flyer`/`flyerRot`, `bull`/`bullU`. Jeder schaltet einen handgebauten Block in `buildTrack` ein.

`TRK.refFull` wird an vielen Stellen abgefragt (Kerbs, Mauern, Kiesflächen aus Messdaten, dreifarbige Betonmauer), aber **keine Strecke setzt es derzeit**. Der Pfad ist also ungetestet; nicht ohne Prüfung verwenden.

Minimalbeispiel:

```js
Object.assign(TRACK_HD, { 'nl-1948': { pts: [[0,0],[4.9,-0.8], /* ... */], hw: [6.0, 6.0, /* ... */], el: [3.1, 3.2, /* ... */] } });
// in TRACKS:
zan: { name: 'Zandvoort', full: 'Circuit Zandvoort', land: 'Niederlande', km: '4,259 km', laps: 72,
  pts: TRACK_HD['nl-1948'].pts.filter((_, k) => k % 3 === 0), hd: TRACK_HD['nl-1948'], theme: 'zan',
  stands: [[-250, 100, 'opp', 44], [300, 420, 'out', 40]] },
```

---

## 3. Theme & Look

`TH = THEMES[TRK.theme]` wird beim Bau gesetzt. Fehlende Pflichtfelder führen zu Fehlern (z. B. `TH.kerb.map`, `TH.sky[0]`, `TH.hemi[0]`, `TH.sunDir`), deshalb am besten ein vorhandenes Theme kopieren.

### 3.1 Himmel, Licht, Dunst

| Feld | Bedeutung | übliche Werte |
|---|---|---|
| `sky` | `[oben, mitte, horizont]` Farben des Himmels | Tag `[0x2a68c0, 0x86b8e8, 0xdbe9f3]`, Nacht `[0x02030a, 0x0a0f2a, 0x2a1840]` |
| `phys` | physikalischer Himmel: `turb` (Trübung), `ray` (Rayleigh), `mie`, `g`, `gain` (Helligkeit) | Tag `turb 2.2–4.5, ray 0.9–1.2, mie .0035–.005, g .8, gain .5–.55`; Dämmerung `turb 12, ray 3.4, g .962, gain .4`; Nacht `gain .025–.03` |
| `fog` | Dunstfarbe | Tag `0xbfd2e2`–`0xcad8e6`, Nacht `0x161c2a`/`0x1a1230` |
| `fogNear`, `fogFar` | Beginn und Ende des Dunsts in m | Tag 300–700 / 2600–7500; Nacht 350–380 / 3000–3200 |
| `camFar` | maximale Sichtweite. Tatsächlich gilt `min(camFar oder 4000, fogFar × 1,08 + 250)` | 6000–9500 |
| `sunDir` | Richtung **zur** Sonne `[x, y, z]` (y = Höhe; wird normiert). x = Osten, z = Süden | Mittag `y ≈ 0.5–0.6`, tiefe Sonne `y 0.32` (Monza), Sonnenuntergang `y 0.05` (Yas) |
| `sunCol`, `sunI` | Sonnenfarbe und Stärke | Tag `0xfff0d8…0xfff4e2`, `3.0–3.6`; Dämmerung `0xff7a30`, `1.1`; Nacht `0x9fb4ff`, `0.3` |
| `lightCol` | abweichende Farbe des Sonnenlichts (sonst `sunCol`) | Yas `0xffbe86` |
| `sunCos`, `sunExp` | Größe/Schärfe der Sonnenscheibe | nur Yas gesetzt; sonst Standard |
| `hemi` | `[Himmelsfarbe, Bodenfarbe, Stärke]` Umgebungslicht | Tag Stärke `.35–.46`, Dämmerung `.62`, Nacht `.7` |
| `flood` | Flutlichtstärke. `0` = Sonne wirft die Schatten; `> 0` = Flutlicht wirft die Schatten (auch die gebackenen) | Tag 0, Dämmerung 1.8, Nacht 4.4–4.6 |
| `floodCol` | steht in zwei Themes, wird aber nirgends gelesen (wirkungslos) | – |
| `exposure` | Belichtung | Tag `.95–.97`, Dämmerung `1.0`, Nacht `1.1` |
| `clouds` | `[Menge, …, …, …]` vier Wolkenwerte; erster Wert ist erkennbar die Bedeckung (0 = keine, 1.05 = stark bewölkt). Die anderen drei habe ich nicht entschlüsselt **(unklar)**: vorhandene Werte übernehmen | `[0.4–1.05, 0.46–0.58, 0.6–0.9, 0]` |
| `cloudCol` | Wolkenfarbe | Tag `0xf4f6fa`, Dämmerung `0xb06a8a`, Nacht `0x222244` |
| `haze`, `hazeCol` | zusätzlicher Dunstschleier am Himmel | nur Yas: `.62`, `0xd8865e` |
| `flare` | Stärke des Sonnen-Blendeffekts (Standard 0.8) | Tag `.7–.9`, Nacht `0` |
| `rays` | Lichtstrahlen der Sonne (Standard 0.6; nachts immer 0) | Yas `.7` |
| `night: true` | Nachtmodus: dunklere Linien und Kerbs, schwächerer Asphaltglanz, dunkle Spiegelumgebung, Lichtkegel unter Masten u. v. m. (23 Lesestellen) | Vegas, Singapur |
| `fireworks: true` | Feuerwerk während des Rennens | Yas, Vegas, Singapur |

**Dunstfarbe = Horizontfarbe.** `THREE.ShaderChunk.fog_fragment` ist gepatcht: Zur Sonne hin wird der Dunst heller und nimmt die Farbe des ersten Richtungslichts an. Außerdem nutzt der Asphaltglanz (`sheenMat`) die Dunstfarbe als Spiegelbild des Horizonts. Deshalb `fog` nahe an `sky[2]` wählen (etwas dunkler/grauer), sonst entsteht eine sichtbare Kante am Horizont und die Fahrbahn schimmert in der falschen Farbe.

### 3.2 `look`: Farbkorrektur und Bloom

Alle Felder sind optional (Standard in Klammern, aus `applyLook`).

| Feld | Bedeutung | Bereich in vorhandenen Themes |
|---|---|---|
| `sat` (1.1) | Sättigung | `.8` (Nordschleife, kühl-matt) bis `1.22` (Vegas) |
| `con` (1.08) | Kontrast | `1.0` bis `1.2` |
| `vig` (.38) | Vignette | `.24` bis `.42` |
| `tint` ([1,1,1]) | Farbstich RGB | je Kanal `.92–1.08` |
| `lift` ([0,0,0]) | Anheben der Schatten RGB | `0–.012` |
| `bloom` (.5) | Bloom-Stärke | Tag `.3–.35`, Nacht `.4–.42` |
| `thr` (.9) | Bloom-Schwelle | Tag `.95`, Nacht `1.05`, Dämmerung `.92` |
| `rad` (.45) | Bloom-Radius | `.4–.45` |
| `warm` (0) | Farbtemperatur (+ warm, − kühl) | `-.22` (Silverstone) bis `.38` (Monza) |
| `fade` ([0,0,0]) | Ausbleichen der Tiefen RGB | `0–.022` |
| `grain` (.012) | Filmkorn | `.011–.018` |
| `sh` ([.97,.99,1.04]) | Farbe der Schatten RGB | kühle Schatten: Blau > 1 |
| `hi` ([1.03,1,.96]) | Farbe der Lichter RGB | warme Lichter: Rot > 1, Blau < 1 |

### 3.3 Look-Rezept (echte Werte aus dem Code)

| | Tag (Monza) | Dämmerung (Yas Marina) | Nacht (Singapur) |
|---|---|---|---|
| `sky` | `[0x2a68c0, 0x86b8e8, 0xdbe9f3]` | `[0x0d1236, 0x46367a, 0xef8a4e]` | `[0x03060f, 0x0b1428, 0x22263a]` |
| `phys` | `turb 3.2, ray 1.1, mie .004, g .82, gain .55` | `turb 12, ray 3.4, mie .0045, g .962, gain .4` | `turb 2, ray .5, mie .003, g .7, gain .03` |
| `fog` / `fogNear` / `fogFar` | `0xbfd2e2` / 300 / 2600 | `0xb07e6a` / 260 / 2300 | `0x161c2a` / 380 / 3200 |
| `sunDir` | `[0.55, 0.32, 0.45]` | `[-0.75, 0.05, 0.45]` | `[-0.3, 0.6, 0.4]` |
| `sunCol` / `sunI` | `0xfff1dc` / 3.6 | `0xff7a30` / 1.1 | `0xa8b8ff` / 0.3 |
| `hemi` | `[0xcfe0f5, 0x4a5a30, 0.35]` | `[0xb4bcd8, 0x5a4a3c, 0.62]` | `[0x8a94b8, 0x3a3226, 0.7]` |
| `flood` / `exposure` | 0 / 0.95 | 1.8 / 1.0 | 4.6 / 1.1 |
| `clouds` / `cloudCol` | `[0.85, 0.52, 0.9, 0]` / `0xf4f6fa` | `[0.55, 0.58, 0.6, 0]` / `0xb06a8a` | `[0.25, .6, 1, 0]` / `0x2a2e40` |
| `flare` / `rays` | .8 / Standard | .9 / .7 | 0 / – |
| `look.sat` / `con` / `vig` | 1.13 / 1.09 / .3 | 1.14 / 1.1 / .42 | 1.12 / 1.16 / .36 |
| `look.bloom` / `thr` / `rad` | .35 / .95 / .4 | .4 / .92 / .42 | .4 / 1.05 / .45 |
| `look.warm` | .38 | .26 | .12 |
| `look.sh` / `hi` | `[.98,.96,1.02]` / `[1.11,1.03,.87]` | `[.88,.86,1.14]` / `[1.12,.97,.88]` | `[.85,1.03,1.1]` / `[1.11,1.01,.85]` |
| Zusätze | – | `haze .62`, `poles`, `noBlue`, `fireworks` | `night`, `poles`, `noBlue`, `fireworks`, `cityLit .38` |

Kühler, bedeckter Tag (Silverstone): `phys.turb 4.5`, `clouds [1.05, …]`, `look.sat .9`, `warm -.22`, `tint [.97, 1.01, 1.04]`.

### 3.4 Boden, Streckenrand, Bewuchs

| Feld | Bedeutung | Werte |
|---|---|---|
| `asph` | Asphaltmischung (Schlüssel in `asphaltFor` und `ROADTEX`) | siehe 3.5 |
| `ground` | Bodentextur: `'grass'`, `'sand'`, `'city'` (Asphaltfläche) | |
| `groundTint`, `mainTint` | Einfärbung des Bodens. Achtung: im Code steht `color` zweimal im selben Objekt; es gewinnt `groundTint` (bzw. Weiß), `mainTint` wirkt beim Hauptboden faktisch nicht | z. B. `0xe8efd8` |
| `dryGrass: true` | trockenes Gras (Melbourne) | |
| `bandStone` | Farbe: Böschungen und Stützmauern aus hellem Stein statt Gras (Stadtkurs am Hang) | Monaco `0xd8cdb8` |
| `wall` | Grundabstand der Absperrung. Formel: `W = HW + wall − 7 + Auslauf` | 8–14 (ergibt 1–7 m neben der Fahrbahn auf Geraden) |
| `runoff` | zusätzliche Auslaufbreite an der Kurvenaußenseite (innen immer 3 m) | 0 (Nordschleife), 6–9 (Stadt/Kart), 16–24 (Rennstrecke) |
| `wallH` | Höhe der Leitplanke/Mauer | `.8` (Kart), `1.0–1.2` |
| `wallKind` | `'armco'` (Leitplanke, davor Reifenstapel) oder `'concrete'` (Betonmauer, davor Tecpro-Blöcke) | |
| `runoffKind` | `'gravel'`, `'paved'`, `'asphalt'`, `'grass'` (siehe 4.3) | |
| `runoffCol` | Farbe für bemalten Asphaltauslauf | Yas `0x2ec9cc` |
| `noBlue: true` | keine blaue Linie im Asphaltauslauf | |
| `plainWalls: true` | keine Werbebanden auf den Mauern | Monaco |
| `kerb` | `[Farbe1, Farbe2]` der Randsteine | `[0xd42a1e, 0xf4f4f4]`, Spa `[0xd8231b, 0xf5c518]` |
| `belt` | Farben der Bänder um die Reifenstapel | `['#c8102e', '#f2f2f2']` |
| `ads`, `adCols` | Texte und Farben der Werbebanden | Liste mit 6–8 Wörtern, 5–6 Farben |
| `paint` | `[[sVon, sBis], ...]` bemalte Asphaltstreifen neben der Strecke | nur Spa |
| `poles: true` | Flutlichtmasten alle 46 m (bei `night` mit Lichtkegel auf dem Asphalt) | |
| `tents: true` | weiße Zeltdächer (Yas) | |
| `trees` | `'forest'` (Laub-/Nadelbäume) oder `'palms'`. Bei `'palms'` wird zusätzlich immer eine Stadt erzeugt | |
| `conifer` | Anteil Nadelbäume 0–1 (Standard .33) | .12 (Melbourne) bis .8 (Spielberg) |
| `treeMul` | Faktor auf die Baumzahl (Basis 9000 bei „Schön“, 3500 bei „Schnell“, ×1,4 bei „Ultra“) | .55–2.3 |
| `treeMinD` | Mindestabstand der Bäume hinter der Absperrung (Standard 6; wirksam mind. 7,5 m) | 4–45 |
| `treeBand` | Breite des dichten Waldstreifens entlang der Strecke (Standard 220) | 120–420 |
| `treeExt` | wie weit um die Strecke herum Bäume gestreut werden (Standard 650 Wald, 300 Palmen) | 500–1500 |
| `openInfield: true` | keine Bäume im Innenfeld und in 60 m Streifen an der Strecke | Spielberg |
| `lakePalms: true` | Palmenreihe am Seeufer (braucht `TRK.lake`) | Melbourne |
| `city: true` | Stadtbebauung im Hintergrund; unterdrückt die Waldkante am Horizont | |
| `cityLit` | Anteil erleuchteter Fenster bei Nacht | Singapur `.38` |
| `hills` | `{ h, v, col: [c1, c2] }` Hügelring am Horizont (Grundhöhe, Schwankung, Farben) | `{ h: 80–160, v: 70–140 }` |
| `mountains: true` | Bergketten (Alpen) | Spielberg |
| `vegas: true` | Neonbanden, bunte Spiegelungen, mehr Hochhäuser | |

Gelände (nur bei Strecken mit `el`):

| Feld | Bedeutung |
|---|---|
| `elevScale` | multipliziert alle Höhen (Spielberg `0.5`) |
| `harmonic: true` | Gelände schließt enger an die Strecke an (Übergang 3–25 m hinter der Mauer statt 12–62 m) |
| `bigGround` | vergrößert die Geländeplatte um diesen Wert in m (Nordschleife 1600, Spielberg 5000) |
| `rise` | `{ d0, base, k, max, soft }`: Gelände steigt außerhalb der Strecke in Hangrichtung an (Spielberg). Einzelparameter nicht im Detail geprüft **(unklar)** |
| `hill` | `{ a, b, h }`: Grashügel statt Mauer links zwischen Rundenanteil `a` und `b` |

### 3.5 Asphalt je Strecke

- `asphaltFor(th)` erzeugt je `th.asph` eine Mischung: `b` Grundhelligkeit, `c` Kontrast, `t` Farbstich RGB, `sp` Splittkörner, `pa` dunkle Flecken, `cr` Risse. Unbekannter Schlüssel = Standardmischung. Für eine neue Strecke eine Zeile in der Tabelle `O` ergänzen (z. B. heller, neuer Belag: `b: 54–60`; alter, dunkler: `b: 33–40`, `cr: 8–18`).
- `ROADTEX` ordnet der Strecke ein Foto-Asphaltpaar zu: `textures/<id>_diff_1k.jpg` und `textures/<id>_nor_gl_1k.jpg` (Poly Haven, CC0). Gesucht wird `ROADTEX[TRK.theme] || ROADTEX[TH.asph]`. Vorhanden: `asphalt_track`, `asphalt_pit_lane`, `worn_asphalt`, `asphalt_01/03/05/06/07`, `clean_asphalt`, `road_damaged_clean`, `asphalt_floor`.
- Das Foto wird erst beim Streckenbau nachgeladen; bis dahin liegt der Standardbelag. Die Helligkeit/Tönung kommt weiter aus `b`, `c`, `t` der Mischung (über die Materialfarbe).
- **Service Worker (`sw.js`)**: Die Vorab-Liste `APP` enthält nur `asphalt_track`, `asphalt_pit_lane`, `sand_01`, `gravel_floor` und die Laub-/Gras-Texturen. Andere Asphalt-Fotos werden beim ersten Laden automatisch in den Cache gelegt (gleiche Herkunft). Soll eine neue Textur schon beim Installieren offline verfügbar sein, in `APP` ergänzen. In jedem Fall bei Änderungen `CACHE = 'f1-rennen-x.yy'` hochzählen.
- Kopiert ein Theme ein anderes (`...THEMES.sil`), erbt es dessen `asph` und damit Mischung und Foto.

### 3.6 Laub, Asphaltglanz, Spiegelumgebung (automatisch)

- **`foliageMat`**: durchscheinendes Laub (weicher Lichtübergang, Aufleuchten im Gegenlicht). Jedes Material, das mit `lam({ map: … })` erzeugt wird und dessen Textur `userData.fol` trägt, bekommt es automatisch. Markiert sind `TEX.leaf`, `FOL.needle`, `FOL.card`, `FOL.cardC`, `FOL.frond`. Für neue Pflanzen also diese Texturen mit `lam()` verwenden, kein eigenes `MeshStandardMaterial`.
- **`sheenMat`**: Bei flachem Blickwinkel spiegelt der Asphalt den hellen Horizont (Dunstfarbe). Liegt auf dem Fahrbahnmaterial (Stärke 0,34; nachts 0,12) und automatisch auf jedem `lam({ map: TEX.runoff })` (0,28; nachts 0,1).
- **`buildEnv(groundCol)`**: Spiegelumgebung aus Himmel, Bodenfläche, grauer Asphaltscheibe unter dem Auto und dunklem Horizontband. Bei `TH.trees === 'forest'` ist das Band dunkelgrün, bei `night` fast schwarz, bei `vegas` kommen bunte Leuchtflächen dazu. Die Bodenfarbe wählt der Bau selbst: Nacht `0x141218`, `ground: 'grass'` grün, sonst sandfarben.
- **Auto-Detailstufen**: Ab 120 m ist jedes Auto ein einziges zusammengefasstes Netz; im Schattendurchgang tragen nahe Autos die mittlere Stufe. Je Strecke ist nichts zu tun.

---

## 4. Streckenrand & Objekte

### 4.1 Was `buildTrack(key)` der Reihe nach tut

1. **Linie**: `hd.pts` → geschlossener Catmull-Rom-Spline → leicht geglättet → gleichmäßig auf ca. 2 m neu abgetastet. Ergebnis: `N` Abschnitte, `DS` Abstand, `L` Länge, `PX/PZ` Position, `TX/TZ` Richtung, `RX/RZ` Rechtsvektor.
2. **Breite und Höhe**: `HW` (halbe Breite, geglättet), `ELEV`, `SLOPE`, `FLAT`.
3. **Krümmung**: `KS` (mit Vorzeichen; `KS > 0` = Außenseite links), `KP` (Betrag, verbreitert), später `KR` (Krümmung der Ideallinie).
4. **Kerbs**: `KERB[i] = 1`, wo im Umkreis von ±3 Abschnitten der Radius unter 350 m liegt. `KERBL`/`KERBR` sind normalerweise identisch.
5. **Ideallinie**: `ropeLine` spannt ein „Seil“ durch die Fahrbahn (mit Kerb bis `HW + 0,2`, sonst `HW − 1,15`) → `RL` (seitlicher Versatz je Abschnitt).
6. **Absperrung**: `WL`/`WR` = Abstand der Mauer von der Mittellinie (Formel siehe `wall`/`runoff`). Danach automatische Korrekturen: enge Haarnadeln (innere Planke dicht an der Fahrbahn), nahe Nachbarabschnitte (Lücke zwischen den Absperrungen), nie näher als `HW + 1,2`. `NOWALL` markiert Stellen ohne Mauer (Bit 1 links, Bit 2 rechts), z. B. wo sich die innere Planke über die Fahrbahn falten würde.
7. **Auslaufzonen**: `GRL`/`GRR` (Kiesbett), `PAVEZ` (Schikane mit ebener Asphalt-/Kiesfläche, nur über die Hilfsfunktion `noWall(a, b, ext, pave)`), `GOL`/`GOR` (äußere Kiesgrenze, nur im `refFull`-Pfad).
8. **Tempoprofile und Ideallinie**: `buildProfile`, `buildRacingLine`.
9. **Boden**: Geländeplatte, Geländebänder von der Mauer ins Umland, Gras-Füllstreifen zwischen Fahrbahn und Mauer.
10. **Fahrbahn**: `hStrip` für Asphalt, weiße Linien, Kerbs (drei Streifen, 1,5 m breit, Farbe wechselt alle 2 Abschnitte), Auslauf je `runoffKind`, Gummispur auf der Ideallinie in Brems- und Kurvenbereichen.
11. **Absperrung zeichnen**: `vStrip` für Leitplanke/Mauer, Werbebande (nur auf Geraden mit Radius > 700 m), Sockelschürze, Fangzaun (3,2 m, nicht bei Qualität „Schnell“).
12. **Randdetails**: Reifenstapel/Tecpro in großen Auslaufzonen, Zaunpfosten, Werbetafeln, Kameratürme, Büsche.
13. **Start/Ziel**: Zielstrich, Startplätze, Ampel.
14. **Boxengasse** auf der Innenseite (bzw. `pitOut`), nur wenn der Platz von `s = −300` bis `+160` frei ist (`trackFree`).
15. **Tribünen** (Abschnitt 4.5), Brücken, Bremsschilder 150/100/50 (automatisch aus dem Tempoprofil), Streckenposten alle 270 m, Lichtmasten.
16. **Handgebaute Wahrzeichen** je Strecke, dann **OSM-Gebäude**, dann **Stadt**, **Berge/Hügel**, **Bäume**.
17. **Licht & Himmel** aus dem Theme.
18. **Nachbearbeitung**: `applyElevation` (hebt alles auf Geländehöhe), `tileGround`, `mergeGroups`, `chunkStrips`, `chunkInstances`, Sichtweite, `applySky`, `buildEnv`, `applyLook`, Minikarte, `bakeShadows`, `buildEvict`.

### 4.2 Was eine neue Strecke automatisch bekommt

Fahrbahn mit Linien, Kerbs in Kurven, Auslaufzonen außen, durchgehende Absperrung mit Zaun, Werbebanden, Reifenstapel, Bremsschilder, Posten, Zielstrich und Startaufstellung, Boxengasse, Tribünen an Start/Ziel und an den sechs langsamsten Kurven, Bäume oder Palmen, Waldkante am Horizont, gebackene Schatten, Ideallinie, KI-Tempo, Minikarte.

Von Hand nötig: Tribünenplan (wenn die Automatik unpassend ist), Wahrzeichen und markante Gebäude, Wasserflächen, besondere Auslaufzonen (bemalt, Schikanen ohne Mauer), Hügel/Berge, Stadt.

### 4.3 Auslaufart (`runoffKind`)

| Wert | Ergebnis | Fahrphysik neben der Strecke |
|---|---|---|
| `'gravel'` | Kiesbett in großen Auslaufzonen (ab ca. 6 m Zusatzbreite), sonst 2,2 m Asphaltsaum und Gras | Kies / Gras |
| `'paved'` | hellgrauer Asphaltauslauf in Kurven, 2,2 m Saum auf Geraden; bemalte Zone in der ersten und letzten Kurve | Asphaltauslauf |
| `'asphalt'` | Asphalt durchgehend bis zur Mauer, blaue Linie (außer `noBlue`), optional `runoffCol` | Asphaltauslauf |
| `'grass'` | Gras bis zur Leitplanke, nur 0,7 m Asphaltsaum | 2,2 m Auslauf, dann Gras |

Die Art gilt für die ganze Strecke. Eine Einstellung „je Kurve“ gibt es im Theme nicht. Abweichungen einzelner Kurven müssen im Code ergänzt werden, nach dem Vorbild von Spa: `noWall(a, b, ext, true)` für eine Schikane ohne Mauer mit ebener Fläche, oder `TH.paint` für bemalte Streifen. Dabei immer auch `GRL`/`GRR`/`PAVEZ` passend setzen, damit Optik und Physik übereinstimmen.

### 4.4 Physik-Haken

- `surface(i, lat)` liefert `'road'`, `'kerb'`, `'runoff'`, `'gravel'` oder `'grass'` aus `HW`, `KERBL/R`, `PAVEZ`, `GRL/GRR`, `GOL/GOR` und `TH.runoffKind`.
- `SURF` = `[Gas-Faktor, Zusatzbremsung, ab Tempo, Grip-Faktor]`: Straße/Kerb `[1, 0, 999, 1]`, Auslauf `[0.55, 9, 22, 0.8]`, Gras `[0.35, 20, 18, 0.55]`, Kies `[0.22, 32, 12, 0.45]`.
- `wallAt(i, side)`: Abstand der Absperrung (`side > 0` rechts). Das ist zugleich die Kollisionsgrenze der Autos. Eine Mauer, die nur gezeichnet, aber nicht in `WL`/`WR` eingetragen ist, hält kein Auto auf, und umgekehrt.
- `trackFree(x, z, extra = 1)`: wahr, wenn der Punkt hinter der Absperrung liegt (plus `extra` Meter) und mindestens `HW + 3 + extra` von der Mittellinie entfernt ist. **Vor jedem handgesetzten Objekt aufrufen.**
- `footprintFree(px, pz, rot, x0, x1, len, extra)`: dasselbe für ein gedrehtes Rechteck (lokal x von `x0` bis `x1`, z von `−len/2` bis `len/2`).
- `groundY(x, z)`: Höhe des Geländenetzes (unter Geländebändern abgesenkt). `placeY(x, z)`: Höhe, auf die Objekte gestellt werden. Bei flachen Strecken beide 0.
- `applyElevation` hebt alles in `trackGroup` automatisch an. Objekte deshalb mit `y = 0` als Bodenhöhe bauen. Ausnahmen über `userData`: `strip` (bereits auf Streckenhöhe), `fixed` (nicht anheben, z. B. Horizont), `ground`/`perVertex` (jeder Eckpunkt einzeln), `span` (Brücke: nicht auf den tiefsten Eckpunkt absenken). Große Gruppen und Instanzen (> 6 m) werden am Hang auf den tiefsten Eckpunkt gesetzt, damit nichts schwebt.
- `excl` (Sperrkreise `[x, z, r]`): Wer ein Gebäude setzt, trägt es dort ein, damit Bäume, Stadt und Tribünen ausweichen.

### 4.5 Regeln für den Streckenrand

- **Leitplanken und Zäune durchgehend.** Lücken entstehen nur über `NOWALL`. Jede Lücke muss begründet sein (Kiesbett ohne Mauer, Hügel) und braucht trotzdem ein großes `WL`/`WR`, sonst fahren Autos ins Leere.
- **Nichts innerhalb der Wandlinie.** Kein Objekt mit Bodenkontakt näher an der Mittellinie als `wallAt`. Prüfen mit `trackFree`/`footprintFree`, testen mit `__clipAll()`.
- **Kerbs nur in Kurven.** Die Automatik setzt sie bei Radius < 350 m. Nicht auf Geraden erzwingen; die Ideallinie nutzt Kerbs als befahrbare Fläche.
- **Tribünen außerhalb der Mauern.** `stand()` stellt sie 4 m hinter die Absperrung und baut nur, wenn die ganze Grundfläche frei ist, kein Sperrkreis getroffen wird und keine andere Tribüne überlappt (sonst wird sie bis auf die Hälfte gekürzt oder weggelassen). Gründe für Ablehnungen stehen in `window.__whyS` (`'track'`, `'excl'`, `'stand'`), das Ergebnis des Plans in `window.__stands` (`[s, Seite, gebaut?]`).
- **Bäume nicht näher als der Zaun.** Die Automatik hält `max(WL, WR) + max(treeMinD, 7,5)` ein (Kronenradius). Handgesetzte Bäume genauso behandeln.
- **Gebäude nie verschieben, sondern weglassen**, wenn sie in die Strecke ragen. So macht es der OSM-Pfad.
- **Sich nahe kommende Streckenteile** (Haarnadeln, Über-/Unterführungen): Die Automatik kürzt Absperrungen; trotzdem dort besonders prüfen.

### 4.6 Gebäude und Wahrzeichen

- **OSM-Grundrisse** (`TRK.osm.b`): je Gebäude `{ n: Name, r: [[x,z],...] Umriss, h: Höhe, s: Stil }`. Stile aus `OSM_STYLE`: `gulf`, `tower`, `glass`, `arena`, `brick`, `white` (unbekannt = `tower`). `osmExtrude` zieht den Umriss hoch. Ragt ein Eckpunkt in Strecke oder Wasser (`trackFree(x, z, 2)`), wird das Gebäude ausgelassen; die Namen stehen dann in `window.__osmSkip`.
- **`facadeMat(o)`**: Fassadenmaterial für die instanzierte Stadt (Fensterraster aus Position × Skalierung, nachts beleuchtete Fenster). Für Stadtblöcke verwenden; `__clipCheck()` und `__bldOverlap()` erkennen Gebäude an diesem Material.
- **Stadt**: entsteht bei `TH.city` oder `TH.trees === 'palms'`. Anzahl 600 / 1400 / 2000 Versuche je Qualität, mal `cityMul`. Jedes Haus prüft acht Randpunkte gegen `trackFree(…, 3)` und Überschneidung mit schon gesetzten Häusern.
- **Handgebaute Wahrzeichen**: eigener Block `if (TRK.meinFeld) { … }` vor dem OSM-/Stadt-Block. Teile eines Wahrzeichens in eine `THREE.Group` legen (wird als Ganzes aufs Gelände gesetzt) und einen Sperrkreis in `excl` eintragen.

---

## 5. Realismus-Checkliste (vor dem Bauen recherchieren)

- **Verlauf und Fahrtrichtung**: Punkt 0 = Start/Ziel, Reihenfolge in Rennrichtung. Länge mit `__dbg().L` gegen die offizielle Länge prüfen (Abweichung unter 1 %).
- **Fahrbahnbreite** je Abschnitt (typisch 12–15 m, also `hw` 6–7,5; Stadtkurse 9–12 m; Kartbahnen 7–9 m).
- **Höhenprofil**: höchster/tiefster Punkt, markante Steigungen. Ohne `el` wird die Strecke flach.
- **Kerbfarben** (`kerb`): meist rot/weiß, Spa rot/gelb.
- **Auslaufart**: Kies, Asphalt oder Gras, und wo es Ausnahmen gibt.
- **Absperrung**: Leitplanke (`armco`) oder Betonmauer (`concrete`), Abstand auf Geraden (`wall`) und in Kurven (`runoff`).
- **Boxengasse**: innen oder außen (`pitOut`), Lage von Start/Ziel.
- **Tribünen**: an welchen Streckenmetern, auf welcher Seite (`stands`).
- **Markante Bauten**: Boxengebäude, Türme, Brücken, Hotels; Grundriss und Höhe aus OpenStreetMap (in Spielmeter umrechnen, gleiche Transformation wie die Streckenpunkte).
- **Sonnenstand zur typischen Rennzeit**: Himmelsrichtung und Höhe → `sunDir` (x Osten, z Süden, y Höhe). Tagrennen `y ≈ 0.5–0.6`, später Nachmittag `≈ 0.3`.
- **Wetter und Stimmung**: klar, bewölkt, Dämmerung, Nacht → `phys`, `clouds`, `look`.
- **Umland**: Wald (Laub-/Nadelanteil `conifer`), Wiesen (`openInfield`), Wüste (`ground: 'sand'`, `trees: 'palms'`), Stadt (`city`), Wasser (`lake`), Hügel/Berge (`hills`, `mountains`).
- **Asphalt**: Farbe und Alter (hell/dunkel, rissig, geflickt) → `asph`, `ROADTEX`.
- **Werbung**: Ortsnamen und Kurvennamen für `ads`; keine echten Markennamen nötig.

---

## 6. Performance-Regeln

Ziel auf der Startaufstellung bei Qualität „Schön“ (`S.gfx === 'high'`): **unter ca. 600 Zeichenaufrufe und ca. 1,5 Mio. Dreiecke**.

- **Viele gleiche Objekte immer als `THREE.InstancedMesh`** in `trackGroup`. `chunkInstances` teilt Instanzen mit mindestens 120 Stück räumlich in Kacheln (360 m, Nordschleife 480 m), damit nur Sichtbares gezeichnet wird. `userData.noChunk` schaltet das ab.
- **Detailstufen** über `geometry.userData.lod = [[einfachereGeometrie, abDistanz], [null, abDistanz]]`. `null` = nicht mehr zeichnen. Beispiel Bäume: nah → 170 m → 340 m; Stämme verschwinden ab 600 m. Kleine Instanzen (Radius < 2,5 m) bekommen automatisch eine Ausblendgrenze.
- **Nahe Bäume sind begrenzt**: Nur 1800 Bäume (Ultra 3200, Schnell 800) im 95-m-Streifen bekommen das detaillierte Modell mit Laubkarten (`FOL.card`/`FOL.cardC`, bis 150 m sichtbar); alle anderen das einfache.
- **Einzelbauten zusammenfassen**: `userData.merge = true` an einer Gruppe lässt `mergeGroups` sie mit Nachbarn (350-m-Raster) zu einem Netz verschmelzen. Streifen werden von `chunkStrips` in 900-m-Stücke geteilt.
- **Materialien teilen**: ein `lam()` je Aussehen, nicht je Objekt. Eigene Canvas-Texturen mit `userData.own = true` markieren, damit sie beim Streckenwechsel freigegeben werden.
- **Transparenz vermeiden**: `alphaTest` (und `alphaToCoverage` wie beim Zaun) statt `transparent: true`. Transparente und `MeshBasicMaterial`-Objekte werfen und empfangen keine gebackenen Schatten.
- **Sichtweite**: Hinter `fogFar × 1,08 + 250` wird nichts gezeichnet. Kleinere `fogFar` sparen spürbar (Monza 2600, Nacht ca. 3000). Horizontobjekte ohne Nebel brauchen `userData.fixed` und `material.fog = false`; die Sichtweite wird dann bis höchstens 14 km erweitert.
- **Gebackene Schatten** (`bakeShadows`/`bakeMat`): einmal beim Laden, Kacheln 192 m mit 1024² Texeln (ca. 19 cm), höchstens 250 Kacheln im 100-m-Streifen um die Strecke. Bei sehr langen Strecken `bakeRes`/`bakeCell` senken. Echtzeitschatten werfen nur die Autos.
- **`buildEvict`**: blendet Streckenteile und Bodenkacheln jenseits der Sichtweite (+250 m) aus. Nichts zu tun, aber Objekte sollten in `trackGroup` direkt liegen und eine `boundingSphere` haben.
- **Bauzeit**: `window.__btms` = `[Bau in ms, Schattenbacken in ms]`. Schleifen über alle `N` Abschnitte mal alle `N` Abschnitte vermeiden (bei 5 km sind das 2500 × 2500); `spiNear`/`nearestDist` nutzen.
- **Qualitätsstufen beachten**: `S.gfx` ist `'low'` („Schnell“), `'high'` („Schön“) oder `'ultra'`. Teure Details hinter `hi` (`S.gfx !== 'low'`) legen.

---

## 7. Test-Checkliste

Alle Befehle in der Browser-Konsole. Die Helfer stehen am Ende von `index.html` (~7232).

### 7.1 Bauen und ansehen

| Befehl | Zweck |
|---|---|
| `__build('schlüssel')` | Strecke direkt bauen (ohne Menü). Gibt den Namen zurück. Schlüssel = Schlüssel in `TRACKS` |
| `await __go('Name', 'f1')` | Menü durchklicken: Schnelles Spiel → Klasse (`'kart'`, `'f2'`, `'f1'`) → Strecke; wartet bis gebaut. Läuft gerade ein Rennen, lädt es stattdessen die Seite neu |
| `await __race('Name', 'f1')` | wie `__go`, startet anschließend das Rennen; gibt `true` zurück, wenn es läuft |
| `__view(s, lat, h, s2, lat2, h2)` | feste Kamera: steht bei Streckenmeter `s`, seitlich `lat`, Höhe `h` über der Strecke und blickt auf `s2`/`lat2`/`h2`. Zurücksetzen mit `__camFix = null` |
| `__frame(3)` | zeichnet Bilder auch bei verstecktem Fenster; nach `__view` aufrufen |
| `await __shot()` | zeichnet, wartet 1,2 s (Texturen), zeichnet erneut; für Bildschirmfotos |
| `__tAt(s, lat)` / `__wAt(s)` | Weltposition `[x, y, z, Richtung]` bzw. `{hw, wl, wr, k}` an einem Streckenmeter |
| `__gY(x, z)` | `[groundY, im Meer?, placeY]` an einem Punkt |
| `__dbg()` | Zustand: `L`, `N`, Rennstatus, Reihenfolge, beste Zeiten |

Beispiel Rundgang: `for (let s = 0; s < __dbg().L; s += 200) { __view(s - 25, 0, 4, s + 40, 0, 1); await __shot(); }` und dabei jeweils ein Bildschirmfoto prüfen.

### 7.2 Geometrie prüfen

| Befehl | Soll-Ergebnis | Bedeutung |
|---|---|---|
| `__clipAll()` | leere Liste `[]` | Objekte mit Bodenkontakt innerhalb der Absperrung (Standard: 0,8 m Sicherheitsabstand). Jeder Eintrag: `x`, `z`, Streckenmeter `s`, `lat`, erlaubte Grenze `lim`, Anzahl Punkte `n`, Objekthöhe `h`, Material-`tag` |
| `__clipAll('road')` | `[]` | strenger Blick nur auf Fahrbahn + Kerb |
| `__onRoad()` | `[]` | alles, was auf der Fahrbahnfläche liegt (auch Flaches, 0–4 m über der Strecke), außer den Fahrbahnstreifen. Zeigt Farbe, Geometrietyp und `userData` zum Auffinden |
| `__bldOverlap()` | `overlaps: 0` | Einzelbauten und Stadtgebäude, die sich überschneiden (bis 80 m hinter der Absperrung; anderer Bereich als Parameter). `ex` zeigt die ersten 10 Paare |
| `__clipCheck()` | `clipping: 0` | Stadtgebäude (Fassadenmaterial), deren Ecken in Strecke/Absperrung ragen |
| `__stands`, `__whyS` | – | welche geplanten Tribünen gebaut wurden und warum andere nicht |
| `__osmSkip` | möglichst leer | OSM-Gebäude, die wegen Überschneidung ausgelassen wurden |

Für einen vollständigen Überschneidungstest vor dem Bau `window.__noMerge = true` setzen und neu bauen: dann bleiben Gruppen einzeln, und `__bldOverlap()` sieht jeden Bau. Danach wieder löschen (ohne Zusammenfassen steigen die Zeichenaufrufe).

### 7.3 Leistung prüfen

1. Qualität „Schön“ einstellen, `await __race('Name', 'f1')`, Kamera auf der Startaufstellung lassen.
2. `__bench()` → `{ ms, calls, tris }` (bester von 4 Durchläufen mit GPU-Abgleich). Ziel: `calls < 600`, `tris < 1 500 000`.
3. `__perf()` → Mittel über 20 volle Spielbilder (`calls`, `tris`, `ms`, Pixelverhältnis). `__ri()` zeigt zusätzlich Geometrie-, Textur- und Shaderzahl; `__cpu()` die reine Skriptzeit.
4. An zwei bis drei weiteren Stellen wiederholen (`__view` auf die dichteste Stelle: Stadt, Tribünen, Wald), denn die Startaufstellung ist nicht immer der schlimmste Punkt.
5. `__btms` ansehen: Bau- und Backzeit sollten im Rahmen der vorhandenen Strecken bleiben.

### 7.4 Tempo und KI prüfen

Die KI braucht keine Abstimmung je Strecke: `trackPace()` berechnet aus dem Tempoprofil der Ideallinie (`buildProfile` mit `KR`, Rundenzeit über `lapEst` mit Beschleunigungsgrenze) den Faktor `PACE`. Er skaliert das KI-Tempo mit `PACE` und Grip/Bremse mit `PACE²`, begrenzt auf 0,97–1,09. Ziel: Die geschätzte Profi-Runde liegt je nach Streckencharakter bei 83,5–90,5 % der Idealrunde. `PACE` wird in `seriesProfiles()` beim Rennstart gesetzt (mit `window.__paceX` zum Testen überschreibbar).

- `__pace()` → je Klasse `ideal` (Spieler am Limit) und geschätzte KI-Rundenzeit je Schwierigkeit (`easy`, `mid`, `hard`, `pro`, `leg`), dazu `pace`. Prüfen: Zeiten fallen von `easy` nach `leg`; `ideal` der F1 liegt in der Nähe echter Rundenzeiten; `pace` klebt nicht an 0,97 oder 1,09 (sonst ist die Ideallinie auffällig, meist wegen falscher Breite oder zackiger Punkte). Achtung: `pace` zeigt den Wert des letzten Rennstarts, nicht zwingend den der gerade gebauten Strecke.
- `await __race('Name', 'f1'); __sim(300)` spult 300 s Rennen ohne Bild vor. Danach `__laps()` (Rundenzeiten aller KI-Fahrer) und `__dbg().aiBest`. Prüfen: Alle Fahrer schaffen Runden, Zeiten sind stabil, niemand hängt (fehlende Zeiten = Fahrer steckt fest, meist an einer Engstelle oder Mauer).
- Laut Codekommentar fährt die KI etwa 1,5 % schneller als die Schätzung aus `__pace()`.
- Selbst eine Runde fahren: Bremsschilder, Kerbs, Auslauf und Mauern müssen zum Gefühl passen.

### 7.5 Abschluss

- Alle Klassen prüfen, in denen die Strecke vorkommt (Kart hat schmalere Fahrzeuge und eigene Zaunregeln).
- Qualität „Schnell“ und „Ultra“ je einmal bauen.
- Minikarte, Menükarte (`TRACK_INFO`), Kalender.
- Version und `CACHE` in `sw.js` erhöhen.

---

## 8. Häufige Fehler

| Symptom | Ursache | Abhilfe |
|---|---|---|
| Strecke läuft rückwärts, Boxen auf der falschen Seite | Punktreihenfolge falsch | `pts`, `hw`, `el` gemeinsam umkehren |
| Start/Ziel an falscher Stelle | Punkt 0 ist nicht die Startlinie | Listen rotieren |
| Strecke gespiegelt | z nicht nach Süden | z-Vorzeichen drehen |
| Fehler beim Bau (`undefined`) | `hw` fehlt oder hat andere Länge als `pts`; Theme-Pflichtfeld fehlt (`kerb`, `sky`, `hemi`, `sunDir`, `belt` bei Leitplanken …) | Daten prüfen, Theme von einem vorhandenen kopieren |
| Strecke komplett flach | `el` fehlt | Höhen ergänzen oder bewusst so lassen |
| Zackige Fahrbahn, KI pendelt | Punkte zu grob oder verrauscht | dichter abtasten (ca. 5 m), vorher glätten |
| Mauer schneidet die Fahrbahn in Haarnadeln | zwei Streckenteile sehr nah | `wall`/`runoff` senken; bei Kartbahnen `kartOnly` nutzen; sonst gezielt `WL`/`WR` begrenzen |
| Auto fährt durch eine sichtbare Mauer | Mauer nur gezeichnet, nicht in `WL`/`WR` | Abstand in `WL`/`WR` setzen, daraus zeichnen |
| Unsichtbare Wand | `WL`/`WR` klein, aber `NOWALL` gesetzt | beides zusammen ändern (`noWall()` verwenden) |
| Objekt schwebt oder versinkt am Hang | mit fester Höhe gebaut, oder `userData.fixed`/`strip` falsch gesetzt | mit `y = 0` bauen und `applyElevation` arbeiten lassen |
| Gebäude steht auf der Strecke | `trackFree`/`footprintFree` nicht geprüft | prüfen und im Zweifel weglassen |
| Bäume wachsen durch ein Gebäude | kein Sperrkreis | `excl.push([x, z, radius])` |
| Tribünen fehlen | Grundfläche nicht frei | `__whyS` lesen; `standDep` verkleinern oder Position ändern |
| Keine Boxengasse | Platzprüfung von −300 bis +160 m schlägt fehl | Platz schaffen oder `pitOut`/`noPit` |
| Heller Rand am Horizont, Asphalt schimmert farbig | `fog` passt nicht zu `sky[2]` | Dunstfarbe an die Horizontfarbe angleichen |
| Laub wirkt schwarz und flach | eigenes Material statt `lam({ map: TEX.leaf … })` | Laub-Texturen mit `lam()` verwenden |
| Kein eigener Asphalt sichtbar | `asph`/`ROADTEX` fehlt, Datei falsch benannt (`<id>_diff_1k.jpg`, `<id>_nor_gl_1k.jpg`) oder offline | Namen prüfen; Ladefehler werden still übergangen und beim nächsten Bau erneut versucht |
| Zu viele Zeichenaufrufe | Einzel-Meshes statt Instanzen, viele Materialien | `InstancedMesh`, `userData.merge`, Materialien teilen |
| Zu viele Dreiecke | fehlende Detailstufen, `treeMul`/`cityMul` zu hoch | `userData.lod` setzen, Faktoren senken |
| Speicher wächst beim Streckenwechsel | eigene Texturen ohne `userData.own` | markieren |
| Strecke erscheint nicht im Menü | `kartOnly`/`extra` gesetzt oder nicht im Kalender | Felder und `SERIES.cal`/`CAL_F1` prüfen |
| Strecke fehlt in der Karriere | nicht in `CAL_F1`, `SERIES.f2.cal` (+ `F2_DATES`) oder `SERIES.kart.cal` | eintragen |
| Alte Version nach Update | Service Worker liefert Cache | `CACHE` in `sw.js` erhöhen |

### Kalender im Überblick

- `SERIES` (~918): `kart.cal = ['genk', 'wack', 'sil']`, `f2.cal = [...]`, `f1.cal = null`.
- `calFor(ser)`: F1 nimmt `CAL_F1` (`[['mel', '08.03.'], ...]`), die anderen Klassen ihr `cal`; F2 holt das Datum aus `F2_DATES[key]`, Kart zeigt „Lauf n“.
- Eine normale Strecke (ohne `kartOnly`) ist im Schnellen Spiel in allen Klassen wählbar, auch im Kart (Silverstone steht im Kart-Kalender). `kartOnly`-Strecken gibt es nur im Kart.
- Der Menütext der Kart-Karriere („3 Rennen · Genk, Wackersdorf, Silverstone“, ~6914) ist fest eingetragen und muss bei Änderungen am Kart-Kalender von Hand angepasst werden.

---

## Nachtrag: Stand Version 1.01 (Look, Schwierigkeit, Modelle)

Diese Punkte kamen nach dem Schreiben der Anleitung dazu. Sie gelten automatisch für jede neue Strecke – man muss sie nur kennen.

### Look
- **Asphalt-Körnung (`roadGrain`)**: Fahrbahn-Texturen werden 2,6-fach dichter gekachelt (eine Kachel ≈ 5,4 m statt 14 m). Die Foto-Texturen zeigen etwa 2 m Asphalt; gestreckt wirkten die Steinchen wie loser Schotter. Für eine neue Asphalt-Textur: 1k-Foto mit feiner, gleichmäßiger Körnung wählen, keine großen Flecken (die würden sich alle 5 m wiederholen).
- **Asphalt-Schimmer (`sheenMat`)**: Stärke 0,34 am Tag, 0,12 bei `night`. Der Schimmer nimmt die Dunstfarbe (`fog`) an – deshalb `fog` immer auf die Horizontfarbe des Himmels abstimmen, sonst schimmert die Fahrbahn in einer fremden Farbe.
- **Laub (`foliageMat`)**: nur Materialien mit den Laub-Texturen (`TEX.leaf`, `FOL.*`) bekommen durchscheinendes Laub. Eigene Vegetations-Texturen mit `tex.userData.fol = 1` markieren.
- **Spiegelungen (`buildEnv`)**: unter dem Auto immer Asphaltgrau, am Horizont ein dunkles Band. Bei `trees: 'forest'` ist das Band dunkelgrün, sonst eine gedeckte Mischung aus Bodenfarbe und Grau.
- **Ideallinie**: schlanke Pfeile alle 5 m, Farbe fließend Grün → Gelb (ab 88 % des Limits) → Rot, Größe nimmt mit der Entfernung ab, nach rund 520 m endet sie. Sie folgt `RL` (Ideallinie der KI) – ist die Linie auf einer neuen Strecke unplausibel, liegt es an `RL`/`KR`, nicht an der Darstellung.

### Schwierigkeit (keine Handarbeit je Strecke)
- `trackPace()` berechnet beim Rennstart den Faktor `PACE` (0,97 … 1,09). Er hängt vom Streckencharakter ab: Durchschnittstempo der Ideal-Runde geteilt durch die Höchstgeschwindigkeit der Klasse (Monaco ≈ 0,48, Silverstone ≈ 0,65). Enge Kurse bekommen eine schnellere KI, schnelle Kurse bleiben etwa wie bisher.
- Geeicht an zwei Profi-Referenzen in der F2: Monaco Rennschnitt 1:04, Silverstone Qualifying 1:29. Wer die Eichung ändern will, passt die zwei Zahlen in `trackPace()` an (`0.846` = Zielverhältnis bei Monaco-Charakter, `0.042` = Zuwachs bis Silverstone-Charakter) und `QF` (Qualifying-Mitte relativ zur geschätzten Rennrunde, derzeit 0,970).
- `PACE` skaliert das Tempo der KI mit `PACE` und alle Beschleunigungen (Grip, Bremse, Antrieb) mit `PACE²`. Dadurch bleibt die Fahrlinie gleich und die Rundenzeit sinkt um genau diesen Faktor.
- **Qualifying**: das KI-Feld wird gleichmäßig über bis zu 10 s gestreut (auf kurzen Runden 11 % der Rundenzeit), sortiert nach Fahrerstärke mit etwas Zufall.
- Prüfen einer neuen Strecke: Rennen auf „Profi“ starten, `__sim(200)` und dann `__laps()` – die fliegenden Runden der Spitze sollten etwa 1–2 % unter `__pace().<klasse>.pro / __pace().pace` liegen. Bleiben Autos hängen (eine Runde dauert doppelt so lang), stimmt etwas mit `RL` oder den Wänden nicht.

### Modelle
- **Fernmodell**: ab 120 m ist jedes F1/F2-Auto ein einziges Netz (`farCarGeo`). Neue Automodelle brauchen dafür drei Detailstufen in der `.bin`-Datei.
- **Modellkorrekturen beim Laden**: `flatFins` (ebnet Finnen am F1-Cockpitrand ein) und `addPlate` (deckt den ausgefransten Halo-Ausschnitt der F2 ab). Kleine Fehler in einem importierten Modell lassen sich so beheben, ohne die `.bin`-Datei neu zu erzeugen.
- **Kart**: Fahrer, Helm und Lenkrad sind je ein Netz mit Farben je Eckpunkt (`kartDriver`, `kartSteeringWheel`, Materialien in `KDRV`). Neue Teile dort immer in die `parts`-Liste hängen, nicht als eigenes Mesh – sonst steigen die Zeichenaufrufe wieder (20 Karts × jedes Teil × 2 wegen Schatten).

### Testen
- Screenshots im Vorschaufenster zeigen das Bild erst einen Moment nach dem Zeichnen: nach `__view(...)`/`__frame(...)` eine Sekunde warten.
- `__view` wirkt nur, solange das Spiel nicht pausiert ist (das Fenster pausiert automatisch, wenn es in den Hintergrund gerät).

---

## Nachtrag 2: Streckenrand nach Luftbild (Schikanen, Zäune, Notausgänge)

### Vorgehen: mit der echten Strecke abgleichen
1. Kurve in OpenStreetMap suchen (`openstreetmap.org/search?query=<Kurvenname>`), Koordinaten aus der Adresse ablesen.
2. Luftbild-Kachel ansehen: `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/<z>/<y>/<x>` (z = 17 oder 18, x/y aus Länge/Breite berechnen).
3. Im Spiel dieselbe Stelle von oben ansehen: `__tAt(s)` liefert die Position, dann `__camFix = { p: [x, 130, z], t: [x, 0, z] }` und `__frame(12)`.
4. Vergleichen: Wo steht die Absperrung, was ist Asphalt, was Kies, was Gras? Wo ist bewusst **keine** Absperrung (Notausgang)?

### Bausteine in `buildTrack` (nach dem Block „Rettifilo“ suchen)
- **`turnsIn(s0, s1)`** – findet die engen Kurven (Radius < 70 m) eines Abschnitts und liefert je Kurve `[Anfangsindex, Endindex, rechts?]`.
- **`chordWall(a, b, W, sg, pocket, lim)`** – die Absperrung einer Seite läuft zwischen den Indizes a und b als gerade Sehne statt der Kurve zu folgen. Sie wird nur nach außen verschoben (höchstens `lim` Meter) und nie in einen anderen Streckenast hinein. Für die **Innenseite** enger Kurven: innen bleibt offene Fläche, kein Zaun am Scheitel. Mit `pocket = true` wird die Fläche asphaltiert.
- **`straightOn(a, b, W, sg)`** – die **Geradeaus-Seite** einer Schikane: die Absperrung läuft in Verlängerung der Anfahrtsgeraden weiter, dazwischen liegt ein asphaltierter Notausgang; nach der Schikane kehrt sie über 90 m zur normalen Linie zurück. So sind Rettifilo und Roggia in Monza gebaut.
- **`POCK` / `POCKETS` / `pocketFill`** – die asphaltierten Notausgänge: `POCK[i]` (Bit 1 = links, 2 = rechts) lässt die Fläche wie Auslauf-Asphalt fahren und unterdrückt dort Kies; `pocketFill` zeichnet die Fläche.
- **`CHORD_OK`** – Liste der Strecken, auf denen `chordWall` automatisch auf **alle** engen Kurven angewendet wird (derzeit Monza, Silverstone, Spielberg, Spa), mit ausgenommenen Abschnitten in Metern. Eine neue permanente Strecke hier eintragen und danach `__clipAll()` prüfen: Meldet es Objekte, stehen von Hand gesetzte Bauten hinter der alten Linie – den Abschnitt dann ausnehmen. **Stadtkurse nicht eintragen** (dort steht die Mauer bewusst am Scheitel).
- **`foldLim`** (in `hStrip`) – Bodenstreifen reichen auf der Kurveninnenseite nie über 75 % des Kurvenradius hinaus; dahinter liegt der Geländeboden. Verhindert gezackte, gefaltete Flächen, wenn die Absperrung weit weg steht.

### Fangzaun
- Zwei Schichten: feines Drahtgeflecht (`TEX.fence`, 1 m je Kachel, weich überblendet) und Pfosten mit Spannseilen (`TEX.fencePost`, alle 4 m, deckend).
- Wo ein Zaun steht, entscheidet `fenceAt(i, s)`; wo gar keine Absperrung steht, `NOWALL[i]` (Bit 1 = links, 2 = rechts).
- Regel aus der Praxis: Zaun gehört an Tribünen, Boxenmauer, enge Auslaufzonen und überall dort, wo Zuschauer oder Streckenposten nah stehen – **nicht** quer durch Notausgänge und nicht in das Innere einer Schikane.

### Licht und Spiegelung
- Das Himmelslicht (`ENVP.probe.intensity`) steht auf 1,5: Schatten auf Asphalt und Laub sind aufgehellt, nicht schwarz.
- Nachtstrecken (`night: true`) bekommen in `buildEnv` acht Flutlichtbänke in die Spiegelungsumgebung, damit der Lack nicht schwarz wirkt.
- Der Showroom spiegelt beim Zeichnen sein eigenes Studio (`SHOW.env`), nicht die Strecke.
- Vorsicht bei Kommentaren: In dieser Datei stehen oft mehrere Anweisungen in einer Zeile. Ein `//`-Kommentar mitten in der Zeile schaltet den Rest ab – dort immer `/* … */` verwenden.

---

## Nachtrag 3: Boden-Shader und plastischer Rasen

- **Gummispur (`rubberLine` + `rubberMat`)**: Entlang der Ideallinie (`RL`) ist der Asphalt rund 1,5 m breit dunkler und etwas glatter, der Fahrbahnrand abseits der Linie leicht heller. Kommt automatisch für jede Strecke, weil `RL` ohnehin berechnet wird. Stärke: 0,30 am Tag, 0,22 nachts (Aufruf direkt bei der Fahrbahn in `buildTrack`).
- **Farbvariation (`groundVar`)**: Materialien, deren Textur `userData.gv` trägt (Rasen `TEX.grassP` = 1, Kies `TEX.gravel` = 0,55), bekommen 7–28 m große hellere/dunklere Flecken aus Rauschen über die Weltkoordinaten. Eigene Bodentexturen einfach mit `tex.userData.gv = <Stärke>` markieren.
- **Grasbüschel (`grassTufts`)**: Auf Strecken mit `ground: 'grass'` stehen auf den Grasstreifen (2,5 bis 8,5 m neben der Fahrbahn) kleine gekreuzte Flächen mit Halmen. Sie stehen nur dort, wo `surface()` „grass“ meldet (also nicht auf Kies, Asphalt oder in Notausgängen), und werden nur bis 70 m Entfernung gezeichnet. Farbe: aus dem Mittelwert der Rasentextur – bei einer neuen Rasentextur passt sie sich selbst an. Bei „Schnell“ sind sie aus, bei „Ultra“ dichter.
- **Was Normal-Maps können und was nicht**: Eine Normal-Map lässt eine flache Fläche im Licht uneben wirken, verändert aber nicht die Silhouette. Für sichtbare Halme, Maschendraht oder Laub braucht es echte (durchbrochene) Flächen – deshalb Büschel, Zaun-Geflecht und Laubhülle.
- **Kart-Fahrer (`kartDriver`)**: Rumpf als Rotationskörper mit Taille/Brust/Schultern, verjüngte Gliedmaßen (`tap`), Weste, Nackenstütze, Stiefel. Maße in Zentimetern mal 1,3 (Faktor `SC`); neue Teile immer in die `parts`-Liste.

---

## Nachtrag 4: Bäume je Strecke (`TREE_STYLE`)

Die Bäume der `trees: 'forest'`-Strecken bestehen nicht mehr aus Kugeln und Kegeln, sondern aus Laub- bzw. Zweigflächen um einen kleinen dunklen Kern. Das ergibt eine echte, durchbrochene Silhouette und braucht weniger Dreiecke als vorher (naher Laubbaum rund 440 statt 830, nahe Fichte rund 110 statt 340).

- **Tabelle `TREE_STYLE`** (über `chunkInstances`): je Thema ein Eintrag, sonst gilt `def`.
  - `leaf` – Laubbaum: `lobes` = Kronen-„Wolken“ `[x, y, z, Radius]` (ihre Lage bestimmt die Form: breit und niedrig = Eiche, übereinander = Buche, weit oben = Eukalyptus), `cards`/`sz` = Zahl und Größe der Laubflächen, `lo` = einfache Stufe `[Radius, Höhenfaktor, Mitte]` für entfernte Bäume, `hsl` = Grundfarbe.
  - `con` – Nadelbaum: `kind: 'spruce'` (Fichte: viele hängende Astetagen, spitz) oder `'pine'` (Schirmkiefer: wenige flache Etagen hoch am Stamm), dazu `y0`/`y1` (Kronenhöhe), `r`, `tiers`, `per` (Äste je Etage), `droop` (Hängen), `hsl`.
  - `trunkH` – Stammhöhe; bei hohen Kronen (Kiefer, Eukalyptus) entsprechend größer wählen, sonst schwebt die Krone.
- **Vorhandene Arten**: Monza (Eichen/Hainbuchen + Schirmkiefern), Spa und Nordschleife (hohe Fichten, schlanke Buchen), Spielberg (Bergfichten), Silverstone (breite Eichen), Melbourne (Eukalyptus), Montréal (Ahorn).
- **Neue Strecke**: einen Eintrag unter dem Themennamen anlegen. Der Anteil Nadelbäume kommt weiter aus `TH.conifer`.
- **Detailstufen**: Flächen und Kern bis 170 m, danach eine Wolke bzw. vier Kegel, ab 340 m die gröbste Stufe. Die detaillierte Stufe bekommen die streckennächsten Bäume (bis 2800, bei „Ultra“ 4200).
- **Rinde**: `TEX.bark` + `TEX.barkN` (Furchen und Grate mit Relief, keine durchgehenden schwarzen Streifen).

---

## Nachtrag 5: Tonwertkurve, Farbstimmung und Baum-Kacheln

- **Tonwertkurve**: Der Renderer nutzt die filmische AgX-Kurve (Lichter laufen weich aus und behalten Farbe). Weil AgX von sich aus flauer ist, multipliziert `TONE = { sat: 1.1, con: 1.12 }` Sättigung und Kontrast aller Strecken. Wer das Gesamtbild kräftiger oder ruhiger will, ändert nur diese zwei Zahlen.
- **Farbstimmung je Strecke**: bleibt das `look`-Objekt im Thema (Schatten-/Lichterfarbe `sh`/`hi`, `sat`, `con`, `warm`, `tint`, `lift`, `fade`, `vig`, `bloom`, `grain`). Jedes Thema sollte ein eigenes haben – erbt ein Thema per `...THEMES.x`, übernimmt es sonst auch dessen Stimmung (die Kartbahnen Genk und Wackersdorf haben deshalb jetzt eigene Einträge direkt hinter dem Themen-Block).
  - Richtwerte: warme Abendsonne `warm: .3 … .4`, `hi` rötlich-gelb; kühl-bedeckt `warm: -.2`, `sat: .8 … .9`; Nacht `con: 1.16 … 1.2`, `bloom: .4`, `vig: .36 … .4`.
- **Baum-Kacheln**: Bäume werden in Kacheln von 150 bis 300 m gruppiert (Streckenlänge ÷ 19). Kleine Strecken bekommen kleine Kacheln, damit die Fernstufen überhaupt greifen. Wechsel der Stufen: 130 m (Flächen weg, einfache Krone), 260 m (gröbste Stufe); Stämme ab 450 m aus.

---

## Nachtrag 6: Zurückgenommen
- **Monza**: Die Schikanen-Umbauten (Rettifilo, Roggia) sind wieder wie vor Version 1.01. Die Bausteine `straightOn`, `chordWall` und `pocketFill` bleiben im Code für andere Strecken; Monza steht nicht mehr in `CHORD_OK`.
- **Tonwertkurve**: wieder ACES, `TONE` steht auf 1 (keine globale Anhebung). Die Farbstimmung je Strecke ist unverändert, die neuen Stimmungen für Genk und Wackersdorf bleiben.

---

## Nachtrag 7: Version 1.02 – Überblendung, Gras, Asphalt, Karriere

- **`distFade(material, d0, d1)`**: löst ein Material zwischen d0 und d1 Metern Entfernung punktweise auf (Dither, kein Sortieren, kaum Kosten). Eingesetzt bei den Laubflächen der Bäume (92–128 m, genau vor dem Stufenwechsel), bei Grasbüscheln (40–68 m). Für neue Vegetation mit Alpha-Test dasselbe verwenden, damit nichts plötzlich auftaucht.
- **Grasbüschel (`grassTufts`)** gibt es auf allen Strecken mit `ground: 'grass'`, im ganzen Streifen zwischen Fahrbahn und Absperrung (dicht bis 8 m Abstand, danach lockerer, bis 24 m). Auf Strecken über 9 km (Nordschleife) nur 40 % Dichte.
- **Auslaufzonen („paved“) und Z-Fighting**: Flächen, die übereinander liegen, brauchen deutlich verschiedene `polygonOffset`-Werte (Fahrbahn −2, Auslauf −3, bemalte Streifen −4, Grasfüllung +1). Bei nur ±1 flackert ab ca. 300 m das Gras durch den Asphalt („Loch“).
- **Asphalt** wird zweimal gelesen (`asphaltNoRepeat`, zweiter Maßstab 0,4-fach versetzt) – dadurch keine sichtbare Wiederholung mehr. Die Gummispur (`rubberMat`) ist dezent (0,18).
- **Baum-Flächen**: Laubflächen zeigen nie nach oben (Erhebung begrenzt, Normale in [−0,3 … 0,45]); Schirmkiefern hängen stärker (`droop` 0,34), damit keine flachen Scheiben entstehen.
- **Monaco**: Häuser sind einfache Quader (kein Detailwechsel); die Fassadentextur zeichnet Klappläden (`shutter`-Farben), Fensterbänke und Stürze. Der Hang bis zur Stadtgrenze ist in warmen Dachfarben eingefärbt und mit 17-m-Raster bebaut, damit zwischen den Häusern kein Boden sichtbar ist.
- **Esplanade (Singapur)**: zwei Glaskuppeln mit je 3400 dreieckigen Alu-Spitzen als ein Netz.
- **Vorwärmen (`warmUpTrack`)**: beim Rennstart werden alle Geometrien und Texturen (auch Detailstufen) einmal in ein 8×8-Bild gezeichnet – gegen Ruckler beim ersten Sichtbarwerden (Spa).
- **Grafikwechsel im Rennen**: Strecke wird neu aufgebaut, Rennstand und Autos bleiben (`REBUILD` hält nur die Bildschleife kurz an).
- **Karriere-Bildschirm**: neue Anordnung (links: nächstes Rennen mit Streckenumriss, Rennwochenende, Aktionen; rechts: Tabelle, Kalender). Die Auswahl von Schwierigkeit und Länge bleibt erhalten (`renderMenu` setzt nur noch Reihen mit Einstellungsschlüssel zurück).
- **Kollisionsklang** (`bump(stärke, 'car' | 'wall')`): Schlag, Knirschen, Splitter, bei Wandkontakt zusätzlich metallisches Schaben.
- **Kart-Anzeige**: Halterung am Lenkrohr, Bildschirm zeigt Tempo und Drehzahl (`kartDispTick`).

---

## Nachtrag 8: HUD 2026 und Prüfhilfen

- **HUD**: neuer Tacho (`drawGauge`): Drehzahl-LEDs als flacher Bogen, Tempo groß in der Mitte, Gang links, ERS und Gas/Bremse rechts, rote Kante unten wächst mit dem Tempo. Position, Runde, Tower (mit Akzentkante) und Rundenzeit (hängendes Glasfeld mit Beschriftung) liegen in einer eigenen letzten CSS-Schicht („HUD 2026“ am Ende des Stylesheets) – dort ändern, nicht in den älteren Schichten.
- **Kollisionsklang prüfen ohne Lautsprecher**: `await __bumpTest('wall' | 'car', stärke)` rendert den Klang offline und liefert Spitzenpegel, Dauer, Pegelverlauf und Energie je Frequenzband. Sollwert: Spitze unter 1, unter 150 Hz höchstens ~25 %, Hauptenergie zwischen 1 und 4 kHz (sonst ist er auf Handylautsprechern nicht hörbar).
- **Ruckler messen**: `window.__noWarm = true` vor `__race(...)` schaltet das Vorwärmen (`warmUpTrack`) ab. Dann die Strecke in 15-m-Schritten mit `__view(s, …)` + `__frame(1)` abfahren und die Einzelzeiten auswerten (Median, 99-%-Wert, Höchstwert). Spitzen am Startgitter sind normal (22 Autos dicht beieinander).

- **Esplanade neu (1.07)**: zwei ovale Eierkuppeln (Superellipsoid, Exponent 3), Hülle mit dichtem Raster flacher dreieckiger Alu-Blenden (ein zusammengefasstes Netz je Strecke, Vertexfarben), warm leuchtendes Foyer-Glas, weißer Randträger mit V-Stützen. Kein InstancedMesh verwenden (wird dort ignoriert).

- **Windschatten-Kegel (1.10)**: wechselt nie sprunghaft das Auto – bei neuem Vordermann erst am alten ausblenden, dann am neuen einblenden; Abklingen mit dem geglätteten Wert (slipS) statt mit der Ein/Aus-Bedingung. Prüfhelfer: `__wake()`, `__plRef()`.
- **Spa/bemalte Ausläufe**: `PAINTZ` markiert sie als Auslaufzone (kein Gras, Fahrphysik Auslauf). **F2-Lack**: Klarlack .45 / Rauheit .35.
