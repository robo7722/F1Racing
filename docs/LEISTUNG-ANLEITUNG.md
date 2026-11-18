# Leistungs-Anleitung: Worauf bei neuen Strecken, Autos, Effekten und HUD achten

Stand Version 2.64 (18.11.2026). Ziel: Das Spiel soll auch auf schwächeren Handys gleichmäßig laufen – in **allen** Kameras
(Verfolger, Hoch hinten, Cockpit, TV). Diese Anleitung fasst zusammen, was in den Leistungsrunden (1.83–1.90, 2.64) gemessen wurde
und welche Fehler das Ruckeln verursacht haben. Für den Streckenbau im Detail: `docs/STRECKEN-ANLEITUNG.md`, Abschnitt 6 und 7.3.

---

## 1. Grenzwerte (Qualität „Schön“, volles Starterfeld, an der **schwersten** Stelle der Runde)

| Größe | Grenze | Messen mit |
|---|---|---|
| Zeichenaufrufe je Bild | **< 450** (ab ~500 ruckelt ein aktuelles Handy) | `qc/perf-cam.js`, QC-Kategorie „Last“ |
| Dreiecke je Bild | **< 1,2 Mio.** | `qc/perf-cam.js` |
| Neue Shader/Texturen im Rennen | **0** | QC-Kategorie „Nachladen“ |
| Einzelner Takt (CPU) | kein wiederkehrender Ausreißer; Median und 90-%-Wert dürfen nicht weit auseinander liegen | Skript unten (Abschnitt 7) |
| Eigenes Auto im Cockpit/TV | ~14–16 Aufrufe, ~105–115 Tsd. Dreiecke (2.64) | `perf-cam.js` → `car` |

Entscheidend ist nicht der Durchschnitt, sondern die schwerste Stelle und **regelmäßige Spitzen** (ein Hänger alle paar Bilder fühlt sich
schlimmer an als eine etwas niedrigere, aber gleichmäßige Bildrate).

---

## 2. Die Fehler, die bisher das Ruckeln verursacht haben (bei jeder Änderung zuerst prüfen)

1. **Leinwand (Canvas) als Textur, die im Rennen laufend neu hochgeladen wird – auf einer GPU-Leinwand.**
   Das Lenkrad-Display wurde 10× je Sekunde gezeichnet und mit `needsUpdate` hochgeladen. Eine normale 2D-Leinwand liegt im Browser auf der
   Grafikkarte; beim Hochladen in WebGL muss er sie zurücklesen und warten: **~25 ms Hänger alle 0,1 s** – genau das Ruckeln in Cockpit und TV-Kamera
   (bis 2.63). Regel: Jede Leinwand, die im Rennen aktualisiert und als Textur benutzt wird, **beim Anlegen** so öffnen:
   `cv.getContext('2d', { willReadFrequently: true })` (der erste `getContext`-Aufruf entscheidet). Dann liegt sie im Arbeitsspeicher und das Hochladen
   ist ein einfaches Kopieren. Gilt auch für Leinwände, die per `drawImage` in so eine Leinwand kopiert werden. Außerdem: keine Mipmaps
   (`generateMipmaps = false`, `minFilter = LinearFilter`), so selten wie möglich aktualisieren, so klein wie möglich.
2. **Ein eigenes Material je Bauteil** (in einer Schleife erzeugt) → je Teil ein Zeichenaufruf. Materialien **vor** der Schleife anlegen.
3. **Gruppen aus vielen Einzelteilen ohne `userData.merge = true`** (bzw. `asMerge`). Monaco hatte bis 2.63 das Casino mit 82 Einzelteilen
   = 82 Aufrufe; mit `merge` ~160 Aufrufe weniger an der schwersten Stelle.
4. **Durchsichtig + beidseitig** (`transparent: true` + `side: DoubleSide`): Three.js zeichnet solche Flächen **zweimal** (erst Rück-, dann Vorderseite).
   `precompile()` setzt seit 2.64 automatisch `forceSinglePass` für Ausstanz-Texturen (`alphaTest > 0`), deckende tiefeschreibende Flächen und flache
   Bodenstreifen (`userData.flat`). Für alles andere: Durchsicht vermeiden (`alphaTest`/`alphaToCoverage` statt `transparent`) oder bewusst
   `material.forceSinglePass = true` setzen, wenn die Reihenfolge egal ist. `perf-scan.js` listet solche Flächen unter `drawnTwice`.
5. **Teile, die erst im Rennen zum ersten Mal gezeichnet werden** (Effekt erst ab Tempo X, Teil erst beim Kamerawechsel sichtbar) → Shader wird mitten
   im Rennen übersetzt (gemessen 42–67 ms). Alles muss in `precompile()`/`warmCams()` einmal gezeichnet werden (in der Szene hängen lassen und dort kurz
   sichtbar schalten, Vorbild `WAKE.m`). QC-Kategorie „Nachladen“ muss leer sein.
6. **Zu kleine Instanz-Kacheln** (jede Kachel = ein Aufruf) und **Instanzen ohne Detailstufe** (Bäume mit 17–28 Tsd. Dreiecken je Kachel).

---

## 3. Neue Strecken

- Vollständige Regeln: `docs/STRECKEN-ANLEITUNG.md` Abschnitt 6 (Materialien teilen, `InstancedMesh`, `chunkInstances`, Detailstufen über
  `geometry.userData.lod`, `mergeGroups`/`asMerge`, Sichtweite `fogFar`, gebackene Schatten, Boden zuletzt).
- **Wahrzeichen und Gebäudegruppen** immer mit `userData.merge = true` (oder `mergeLocal` bei bewegten Gruppen). Netze mit Material-Liste werden nicht
  verschmolzen – in Teile mit je einem Material zerlegen.
- **Bäume**: die Dreieckszahl der Baumkacheln ist der häufigste Grund für > 1,2 Mio. Dreiecke (Genk, Suzuka). Lieber weniger, gut verteilte Bäume
  im Nahbereich als dichte Wälder mit voller Detailstufe.
- **Startaufstellung** ist oft die schwerste Stelle (volles Feld + Tribünen + Boxengebäude) – dort zusätzlich sparsam bauen.
- Prüfen: `python qc/probe.py KEY --race --script qc/perf-cam.js` (alle drei Kameras!) und `qc/perf-scan.js` an der schwersten Stelle,
  zum Abschluss `python qc/run.py KEY` (Kategorien „Last“ und „Nachladen“ leer).

## 4. Neue Autos / Fahrzeugmodelle

- **Drei Detailstufen** wie die vorhandenen Modelle: voll (nur eigenes Auto in Cockpit/TV und Gegner < 6 m), mittel (bis 35 m), Fernmodell
  (ein Netz, ab 80 m `CAR_FAR3` ~2.500 Dreiecke, `clusterGeo`), ab 600 m nicht zeichnen. Das Fernmodell muss **ein** Netz mit **einem** Material sein.
- **Wenige Materialien je Auto** (jedes Material eines Gegners ist ein eigener Aufruf; die mittlere Stufe hat ~11 Aufrufe, das ist das Maximum).
  Räder je Seite als ein Netz, Kleinteile in Karosserie oder Carbon-Netz einschmelzen.
- **`MeshPhysicalMaterial` mit Klarlack** ist teuer je Pixel – nur für die Lackfläche, nicht für Kleinteile, Innenraum, Reifen.
- **Cockpit-/TV-Teile des eigenen Autos** (Wanne, Lenkrad, Arme, aufgeschnittene Karosserie) laufen im eigenen Auto-Durchgang (Ebene 6) und
  werden seit 2.64 **vor** der Welt in einen eigenen Tiefenbereich gezeichnet (`carFirst`, `CAR_DR`): Die Welt dahinter wird nicht mehr berechnet
  (Cockpit spart ~2/3 der Weltpixel). Dafür gilt:
  - Neue Cockpitteile müssen **voll deckend** sein und Tiefe schreiben – dann landen sie automatisch im ersten Durchgang.
  - Halbdurchsichtige Teile (`depthWrite: false`, `opacity < 1`, `colorWrite: false`, andere Überblendung) erkennt `seeThru()` und zeichnet sie
    **nach** der Welt (Ebene 7) – so wie den Geister-Halo. Keine eigenen Ebenen-/Reihenfolge-Tricks am Auto ohne diesen Weg zu verstehen.
  - Kein Teil darf `depthTest: false` bekommen (es läge sonst über allem).
  - Das eigene Auto wird im Cockpit/TV nur von der Umgebungsspiegelung beleuchtet (Sonne/Himmelslicht wirken dort nicht – bewusst so, spart Rechenzeit).
- **Anzeigen am Auto** (Lenkrad-Display, Tacho, Navi): siehe Fehler 1 – CPU-Leinwand, selten aktualisieren, keine Mipmaps.
- Prüfen: `perf-cam.js` → `car`-Werte in Cockpit (2) und TV (3) vorher/nachher vergleichen; Bildvergleich mit `window.__oldCar = true/false`.

## 5. Neue Effekte (Partikel, Windschatten, Wetter, Licht)

- **Im Ruhezustand nichts tun**: kein Rechnen, kein Hochladen (`instanceMatrix.needsUpdate`), kein Zeichnen (`visible = false`). Vorbild `Particles.live`, `FOUNT`.
- **Vorwärmen**: Effekt in der Szene lassen und in `precompile()` einmal sichtbar zeichnen (Fehler 5).
- **Vollbild-Durchgänge** (Nachbearbeitung) kosten je Pixel in jedem Bild – lieber in den vorhandenen Finish-Shader einbauen als einen neuen Pass anlegen;
  nur in „Schön“/„Ultra“ (`S.gfx !== 'low'`).
- **Durchsicht** sparsam und **nie über das Cockpit**: Effekte schreiben keine Tiefe, testen sie aber (`depthTest` bleibt an) – dann verdeckt das Cockpit sie richtig.
- **Echtzeitschatten** werfen nur die Autos; neue Objekte bekommen gebackene Schatten (`bakeShadows`), kein `castShadow`.

## 6. HUD und Oberfläche

- HTML-Elemente über dem Spielbild werden vom Browser in jedem Bild über das Bild gelegt – **bildschirmgroße Ebenen** (Leinwände, Verläufe, Filter)
  kosten auf dem Handy viel. Leinwände nur so groß wie ihr Inhalt (Vorbild: TV-Halo-Band seit 2.64, 28 % statt 100 % der Fläche).
- DOM nur ändern, wenn sich der Wert ändert (Vergleich mit letztem Wert, wie bei `SW.vr`); keine `filter: blur()`/`backdrop-filter` auf großen Flächen.
- Nichts im Takt neu messen (`getBoundingClientRect` höchstens ~1× je Sekunde, wie `HH.obst`).

## 7. Prüfwerkzeuge (Kurzreferenz)

| Befehl | Zweck |
|---|---|
| `python qc/probe.py KEY --race --script qc/perf-cam.js` | Aufrufe/Dreiecke je Kamera, aufgeteilt in Welt, eigenes Auto, Schatten, Nachbearbeitung; schwerste Stellen |
| `python qc/probe.py KEY --race --script qc/perf-scan.js` | Verursacher an der schwersten Stelle (Objekte mit Lage `@x,z`, `drawnTwice`, kleine Kacheln, gleiche Optik mit getrennten Materialien) |
| `python qc/run.py KEY --quick` / `python qc/run.py KEY` | QC-Bot: Last, Nachladen, Ruckler, Löcher, Z-Fighting, schwebende Objekte |
| Takt-Messung (Skript unten) | findet **wiederkehrende** Hänger (z. B. Hochladen einer Textur alle n Bilder) |
| `window.__oldCar = true` | alter Zeichenweg für Cockpit/TV (Bildvergleich, Fehlersuche) |
| Handy: Einstellungen → Extras → Debug-Menü | echte Bildzeiten, Ruckler-Protokoll, Lasttest (die Laptop-Zeiten sind nur Hinweise) |

Takt-Messung je Kamera (als `--script`-Datei; Median und 90-%-Wert der kompletten Spieltakte inkl. Zeichnen):

```js
const A = window.__qcApi, out = {};
for (const c of [0, 2, 3]) { A.S.cam = c; window.__tp(A.L * 0.4); window.__frame(10);
  const ts = []; let t = performance.now();
  for (let i = 0; i < 80; i++) { const t0 = performance.now(); A.tick(t += 16.7, true); ts.push(performance.now() - t0); }
  ts.sort((a, b) => a - b); out['cam' + c] = { med: +ts[40].toFixed(2), p90: +ts[72].toFixed(2), max: +ts[79].toFixed(1) }; }
return out;
```

Liegt `p90` weit über `med` (z. B. 27 ms gegen 3 ms), passiert etwas regelmäßig, das teuer ist – dann Verdächtige einzeln abschalten
(Beispiel 2.64: `window.__hands().SW.t = 1e9` schaltete das Lenkrad-Display ab und der Ausreißer verschwand).

**Messhinweise:** Zeichenaufrufe und Dreiecke sind verlässlich. Millisekunden auf dem Laptop schwanken stark (besonders mit mehreren
parallelen Edge-Läufen) – nur für Vorher/Nachher auf derselben Maschine im selben Lauf verwenden. Nach dem Versetzen der Kamera (`__tp`)
mindestens 0,35 s (`__frame(12)`) warten, sonst laufen noch Detailstufen-Überblendungen und Gegner zählen doppelt.

## 8. Messstand 2.64 (Vergleichswerte)

Gemessen mit `perf-cam.js` (10 Stellen je Strecke, Nordschleife 40; Qualität „Schön“, volles Feld, Fenster 1280×720). Aufrufe Mittel/Spitze je
Kamera, Dreiecke = Spitze über alle Kameras. Eigenes Auto in Cockpit/TV: 14 Aufrufe / 105 Tsd. Dreiecke (bis 2.63: 26 / 190 Tsd.; Kart 9 / 33 Tsd.).
Auf allen Strecken ist das Bild in Cockpit und TV pixelgleich zum alten Zeichenweg (Abweichung ≤ 0,02 % der Pixel, nur Kanten).

| Strecke | Verfolger | Cockpit | TV | Dreiecke max |
|---|---|---|---|---|
| Monza | 150/207 | 152/196 | 165/262 | 0,91 Mio. |
| Spa | 189/246 | 193/255 | 201/280 | 0,91 Mio. |
| Silverstone | 160/193 | 166/231 | 186/302 | 1,17 Mio. |
| Red Bull Ring | 139/209 | 177/307 | 193/260 | 1,00 Mio. |
| Montréal | 148/179 | 151/177 | 170/257 | 0,87 Mio. |
| Monaco | 131/219 | 166/270 | 178/294 | 0,69 Mio. (bis 2.63 Spitze 466 Aufrufe) |
| Melbourne | 211/276 | 214/279 | 239/374 | 0,94 Mio. |
| Abu Dhabi | 213/309 | 227/306 | 246/305 | 0,59 Mio. |
| Las Vegas | 241/326 | 241/319 | 315/424 | 1,02 Mio. |
| Singapur | 245/322 | 273/404 | 270/327 | 1,16 Mio. |
| Nordschleife | 197/345 | 247/354 | 264/367 | 1,01 Mio. (bis 2.63 Spitze 514; Streifen 1800 m, Kleinteil-Kacheln 1000 m) |
| Shanghai | 207/262 | 238/302 | 240/327 | 0,75 Mio. |
| Suzuka | 198/313 | 212/285 | 224/270 | 1,09 Mio. |
| Bahrain | 200/266 | 208/269 | 222/250 | 0,71 Mio. |
| Jeddah | 211/288 | 232/285 | 243/343 | 1,05 Mio. |
| Miami | 225/316 | 230/348 | 248/392 | 1,27 Mio. |
| Barcelona | 214/290 | 216/277 | 230/285 | 0,89 Mio. |
| Hungaroring | 191/250 | 201/242 | 201/247 | 0,78 Mio. |
| Zandvoort | 211/323 | 236/334 | 225/294 | 1,11 Mio. |
| Madrid | 170/186 | 186/269 | 201/276 | 0,96 Mio. |
| Baku | 195/306 | 224/281 | 245/293 | 1,02 Mio. |
| Austin | 154/189 | 172/235 | 201/338 | 1,29 Mio. |
| Mexiko-Stadt | 221/276 | 221/279 | 245/304 | 1,06 Mio. |
| São Paulo | 217/266 | 228/264 | 241/264 | 0,99 Mio. |
| Lusail | 204/238 | 202/243 | 217/254 | 0,77 Mio. |
| Genk (Kart) | 166/302 | 170/319 | 185/275 | 1,28 Mio. (2.65: Bäume treeMul .8 → .45; vorher 1,76 Mio.) |
| Wackersdorf (Kart) | 190/313 | 187/311 | 189/268 | 1,36 Mio. (2.65: Bäume treeMul 1,0 → .55; vorher 1,56 Mio.) |

Offen: Genk und Wackersdorf liegen nach der Baum-Reduzierung (2.65) nur noch an der Startaufstellung über 1,2 Mio. Dreiecken – Ursache: **Karts haben
keine Detailstufen** (jedes Kart ~45 Tsd. Dreiecke in jeder Entfernung, 20 Karts = 700–900 Tsd.). Miami und Austin liegen nur in der TV-Kamera direkt an der
Startaufstellung (Meter ~270, volles Feld im Bild) bei ~1,28 Mio. – nicht wegen Bäumen. Lösung für beides: Detailstufen bzw. Fernmodell für Karts.

## 9. Checkliste vor dem Einchecken

- [ ] `perf-cam.js`: alle drei Kameras unter 450 Aufrufen / 1,2 Mio. Dreiecken an der schwersten Stelle (vorher/nachher notieren)
- [ ] `perf-scan.js`: keine neuen Einträge unter `drawnTwice`, `sameLookDiffMat`, `smallInstances` durch die eigene Änderung
- [ ] QC-Bot: „Last“ und „Nachladen“ leer
- [ ] Takt-Messung: kein neuer wiederkehrender Ausreißer in Cockpit/TV
- [ ] Neue Leinwand-Texturen mit `willReadFrequently`, neue Gruppen mit `userData.merge`, Materialien außerhalb von Schleifen
- [ ] Teure Extras hinter `S.gfx !== 'low'`
