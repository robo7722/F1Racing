# Auftrag: Baseball-Stadion in Mexiko-Stadt neu bauen (Estadio Alfredo Harp Helú)

Der Nutzer findet das Gebäude an der Geraden vor Kurve 1 „komisch“. Es war ein einfarbiger, glatter Quader; in v2.32 hat es nur
eine Notfassade (Fensterband-Textur) bekommen. Du sollst es **richtig umbauen**: ein erkennbares Baseball-Stadion mit Tribünenrang,
Fassade, Dach und Details – in der Qualität der übrigen Wahrzeichen (Foro Sol, Palacio de los Deportes in derselben Strecke).

Antworte auf Deutsch, arbeite sauber, **nichts vermuten, alles am echten Spielbild prüfen**, keine Zwischenfragen (siehe unten „Arbeitsweise“).

## 1. Wo ist das Gebäude?

- Strecke: `mex` (Mexiko-Stadt). Datei: `index.html` (eine sehr große Datei, nie ganz lesen: `grep -n` und `sed -n 'a,bp' index.html | cut -c1-400`).
- Code: Bereich `/*@mex:lm{*/ … /*}@mex:lm*/` (in `buildTrack`), Abschnitt
  `// ---------- Estadio Alfredo Harp Helú (Diablos Rojos, 2019): weißes Membrandach „Tridente“ …` (`grep -n "Harp Hel" index.html`).
  Dort: `osmExtrude(M.harpG, 14, conc, redSeat)` = Haupttribüne (Quader), `osmExtrude(M.harpJ, 6, …)` = niedriger Anbau,
  Spielfeld (Rasen, Infield, Bases), Membrandach mit drei Spitzen (`M.harpRoofO`), Masten.
- Daten (OSM, schon in Spielkoordinaten) in `const OSM_MEX = {…}`: `harpG` (22 Punkte, x 397…554, z −155…−25, Mitte ≈ 455/−111),
  `harpJ` (55 Pkt.), `harpRoof`, `harpRoofO` = [cx, cz, Breite, Länge, Winkel], `harpField`, `harp` (Umriss gesamt).
- Es liegt ca. 100–150 m nördlich der Strecke bei Streckenmeter ≈ 700–780 (Gerade vor Turn 1, Turn 1 bei Meter 942–1114).

## 2. So siehst du die Stelle genau wie der Nutzer (Pflicht, bevor du etwas änderst)

Der Nutzer steht mit dem Auto bei **Streckenmeter ≈ 735, quer zur Fahrtrichtung, Blick auf die linke Wand** (Banden „…DE MÉXICO | FORO SOL | PERALTADA |
HERMANOS RODRÍGUEZ“, darüber das große helle Dach, dahinter das Stadion). Nachstellen mit dem Spiel selbst:

```bash
cat > $TEMP/pos.js <<'E'
const w = ms => new Promise(r => setTimeout(r, ms));
await w(1500);
const A = window.__qcApi;
window.__tp(735);                    // Auto auf Streckenmeter 735
const h = A.pl.h - Math.PI / 2;      // quer zur Fahrtrichtung, Blick auf die linke Wand
A.pl.h = h; window.camH = h;
await w(1100); await shot('stelle735');
return 'ok';
E
python qc/probe.py mex --race --port 8858 --script $TEMP/pos.js --out $TEMP/p_stelle
```

Das Bild liegt danach in `$TEMP/p_stelle/stelle735.jpg` (mit dem Read-Werkzeug ansehen). Weitere nützliche Aufrufe:
`python qc/probe.py mex --top 735,220 --out …` (Draufsicht), `--view s,lat,h,s2,lat2,h2` (feste Kamera an der Strecke),
`--eval "__clipAll().length"` usw. Doku: Kopf von `qc/probe.py`, `qc/README.md`, `docs/STRECKEN-ANLEITUNG.md` (Abschnitte 4–6 lesen).
Jeder Lauf nimmt einen eigenen `--port` (Edge-Prozesse nach Abbruch prüfen, Prefix `f1qc-`).

**Eine Stelle im Spiel selbst ablaufen** (Minikarte → Streckenmeter): Startstrich = Streckenanfang; der Marker liegt bei 81 % der
Streckenbreite, der Startstrich bei 30 % → Meter ≈ 700–780. Das Stadion siehst du von jeder Stelle der Geraden ab Meter 600.

## 3. Was soll gebaut werden

Referenzen im Netz suchen (Fotos/Luftbilder, OSM `building` + `leisure=stadium` im Umkreis, Name „Estadio Alfredo Harp Helú“, Diablos Rojos del México,
eröffnet 2019, ca. 20 000 Plätze): Haupttribüne hinter der Home Plate mit mehreren Rängen und Logenband, geschlossene Außenfassade (Beton, Glas,
Rampen/Treppentürme), Flutlichtmasten, Anzeigetafel im Außenfeld, Zuschauerränge entlang der Foul-Linien, Membrandach (Tridente) mit den drei Spitzen.
Mindestens:

1. Haupttribüne nicht mehr als Quader, sondern mit gegliederter Fassade (Geschosse, Pfeiler, Glasflächen, Treppenhäuser, Dachkante) und erkennbarer Form.
2. Sitzränge auf den Seiten und hinter dem Außenfeld (mit der vorhandenen Zuschauertextur `TEX.crowd` / Material `crowdM2`, wie das Foro Sol), nicht nur das Spielfeld.
3. Flutlichtmasten und Anzeigetafel, Zäune; Dach unverändert gut oder verbessert (Unterseite nicht schwarz).
4. Eigene Canvas-Texturen mit `userData.own = true`; Materialien **vor** Schleifen anlegen; gleiche Teile als `InstancedMesh`/`mergeParts`, Einzelbauten mit `userData.merge = true`.
5. Alles an der echten Lage (OSM-Daten oben), in echter Größe.

## 4. Fallen, die schon Zeit gekostet haben (unbedingt beachten)

- **Geometrie in Weltkoordinaten lassen, Gruppen bei 0/0.** `applyElevation()` (`grep -n "function applyElevation"`) hebt jedes Objekt auf die Geländehöhe.
  Für `osmExtrude`-Häuser in den neuen Strecken gibt es dafür `grp.userData.gx/gz` (Schwerpunkt); bei eigenen Gruppen entweder die Gruppe an den Schwerpunkt
  setzen (dann **ohne** `userData.merge`) oder dieselbe Hinweis-Konvention nutzen. **Nie** zusätzlich selbst ein y setzen (Doppelhub: Häuser schweben).
  Gruppen mit `merge = true` und Position ≠ 0 brechen den Verschmelz-Pass und die QC-Funktionen (`__clipAll`, `__bldOverlap` zeigen dann Treffer am Ursprung).
- **Boden:** sichtbarer Boden = Kachel-/Band-Netze (`userData.tile/strip`), `groundY()` ist für die neuen Strecken nur 1,2 m unter `placeY()` (`LOWER`).
  Gebäude brauchen einen Fuß/Skirt (z. B. Wand 6–8 m unter die Unterkante verlängern), sonst schaut bei Hang ein Spalt heraus.
- **Z-Fighting:** keine deckungsgleichen Flächen (Abstand ≥ 0,1 m, besser mehr). `trackPrism(sA,sB,sd,oA0,oA1,oB0,oB1,h,y0)`: 8. Parameter = **Höhe**, 9. = Unterkante.
  Prüfen mit dem QC-Bot: `window.__qcBot.probe(cam).zfBlocks` (siehe `qc/qc-bot.js`, Ablauf wie in den früheren Testskripten: Kamera setzen, `probe`, Netze nacheinander
  ausblenden und schauen, welches die Treffer senkt).
- **Eigene Bereiche nicht verlassen:** Änderungen am Stadion nur im `mex:lm`-Bereich; allgemeine Engine-Änderungen nur gekoppelt an `TRK === TRACKS.mex`
  oder an ein eigenes Streckenfeld, damit keine andere Strecke sich verändert.
- Leistung: an jeder Stelle < 450 Zeichenaufrufe (`--race --eval "__bench()"`), < 1,2 Mio. Dreiecke. Nichts, das erst im Rennen zum ersten Mal gezeichnet wird.
- Kommentare im Code auf Deutsch; viele Anweisungen stehen in einer Zeile – ein `//` mitten in der Zeile schaltet den Rest ab, dort `/* … */` benutzen.
- Python-Skripte schreiben große Bereiche per `replace` mit `assert s.count(alt) == 1`; nach jeder Änderung die Strecke bauen (`probe.py`), nicht nur lesen.

## 5. Abnahme (alles muss stimmen, sonst nicht fertig)

1. Bild von Meter 735 (Skript oben) **vorher und nachher** ansehen; zusätzlich Draufsicht und zwei Ansichten von der Strecke (Meter ≈ 600 und 850) sowie
   ein Bild aus der Kameraposition mitten auf der Geraden. Das Stadion muss erkennbar ein Baseball-Stadion sein, nichts schwebt, nichts flackert.
2. `python qc/probe.py mex --port 8860 --eval "[__clipAll().length,__onRoad().length,__bldOverlap().overlaps,__clipCheck().clipping]"` → `[0, ≤2, 0, 0]`, keine `page_errors`.
3. `--race --eval "__bench()"` unter 450 Zeichenaufrufen.
4. QC-Bot: `python qc/run.py mex --quick --port 8860` (Befunde „Last“ und „Nachladen“ leer, kein neues Z-Fighting/Schweben/Clipping an der Stelle).
5. Andere Strecken nicht verändert: Stichprobe `monza`, `bra`, `chn` bauen (keine Fehler, gleiche `__clipAll`-Werte).
6. Version in `index.html` (`VERSION = '…'`) und `CACHE` in `sw.js` um 1 erhöhen, committen, `git fetch`, auf `origin/main` aufsetzen, pushen.

## 6. Arbeitsweise (Wunsch des Nutzers)

- Keine Rückfragen und keine Zwischenmeldungen; erst am Ende **eine** Meldung: was geändert wurde, was geprüft wurde (mit Bildern), was nicht geprüft werden konnte.
- Nichts als Ergebnis melden, was du nicht am Bild/Messwert gesehen hast. Wenn du etwas vermutest, schreibe „vermutet“ dazu und prüfe es.
- Selbst committen und pushen, wenn alles aus Abschnitt 5 erfüllt ist.
