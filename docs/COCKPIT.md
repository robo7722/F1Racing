# Cockpit-Ansicht (Helm- und TV-Kamera)

Stand 24.11.2026 (v3.01). Ältere Einzelheiten zum Cockpit-Modell: `docs/AENDERUNGEN-1.22.md` (Abschnitt „Cockpit-Neubau“), zur Leistung: `docs/LEISTUNG-ANLEITUNG.md`.

## Aufbau (Kurzfassung)
- In Kamera 2 (Helm) und 3 (TV) wird das Fahrzeugmodell des eigenen Autos im Kasten ums Cockpit nicht gezeichnet (`cockCut` → `tp.cutGloss`, `tp.cutMatte`);
  an seine Stelle tritt das eigene Cockpit-Modell `m.tub` (`cockNew`: Wanne, Innenwände, Schultern, Vorderdeck, Flanken), dazu Lenkrad (`SW.g`) und Arme (`ARMS.f1.g`).
  Eine Stelle für Bau und Vorladen: `cockBuild(m)`; Umschalten: `cockpitInterior(on)`.
- Die Schale trägt den Lack des Autos: `tp.shellMat` ist eine Kopie des Lack-Materials, die Farbe wird an der Lackierposition `aLP` berechnet.

## Lackierung der Schale (v2.99)
Seit den gebackenen Lack-Texturen (v2.73) las die Schale immer denselben Bildpunkt – sie hat keine UV dieser Textur. Die Fläche vor dem Cockpit war hellgrau.
Behoben: Die Schale rechnet den Lack wieder selbst und projiziert Bogen und Logo (Einzelheiten: `tools/textur/ANLEITUNG.md`, Abschnitt „Im Spiel“).
Bild: `docs/bilder/cockpit_lack_v299.jpg` (vorher/nachher).

Dazu **seidenmatter Lack in Helm-/TV-Kamera** (`ckSatin`, v2.99): Aus Augenhöhe sieht man die Fläche vor dem Cockpit sehr flach. Klarlack und metallischer Grundlack
spiegeln so fast nur noch den Himmel – die Kuppe vor dem Lenkrad war weiß-silbern statt in Wagenfarbe (beim Red Bull besonders auffällig). Für die beiden
Cockpit-Fassungen des eigenen Autos (`tp.cutGloss`, `tp.shellMat` – beide gleich, sonst sähe man die Naht) gilt: Klarlack ≤ 0,2, Rauheit ≥ 0,5, Metall ≤ 0,2,
Spiegelung ≤ 0,5. Verfolgerkameras, Showroom und andere Autos bleiben glänzend. Ein erster, schwächerer Versuch (Klarlack 0,35, Spiegelung 0,8) ließ die Kuppe noch blass.
Geprüft: F1 (Red Bull, Spa) und F2 (Helm, TV, Verfolger) ohne Shader-Fehler.

## Cockpit bei Nacht (v2.99)
Wunsch: „Bei Nachtrennen soll das Cockpit nicht komplett schwarz sein, man soll noch leicht was erkennen.“
- Die Cockpit-Teile sind dunkel (Carbon, schwarzes Lenkrad); nachts fehlen Sonne und heller Himmel in der Spiegelung – übrig blieb fast reines Schwarz.
- Lösung ohne zusätzliches Licht in der Szene (das würde alle Materialien neu übersetzen und jedes Auto aufhellen): `ckFill(material)` hängt an die Materialien
  der Cockpit-Teile (aufgeschnittene Karosserie, Schale, Lenkrad, Arme) eine **Helligkeits-Untergrenze**, gesteuert über **eine Zahl** `CKFILL.value`
  (am Tag 0, nachts `CKFILL_NIGHT` = 0,24, gesetzt in `drawWheel`). Formel: `Bild = max(Bild, f(Eigenfarbe) × Wert × (0,55 + 0,45 × Normale nach oben))` mit `f = 0,4·√x + 0,6·∜x` (entspricht etwa `x^0,35`) – dunkle
  Flächen werden verhältnismäßig stärker angehoben als helle (Carbon wird erkennbar), Flächen nach oben mehr (Flutlicht von oben, gibt Form); was schon beleuchtet
  ist (Handschuhe im Flutlicht), bleibt unverändert.
- Falle: Die Bildabstimmung zieht alles unter ~0,02–0,03 (linear) zu Schwarz (Kontrast um Mittelgrau, `uCon`). Der erste Versuch (Zuschlag 0,07) blieb deshalb
  unsichtbar – gemessen im Bild, nicht geschätzt.
- Die Materialien hängen nur am eigenen Auto in Helm-/TV-Kamera – andere Autos und die Verfolgerkameras bleiben unverändert. Kein Neuübersetzen beim Wechsel Tag/Nacht.
- Absicherung v3.00 (war **nicht** die Ursache des schwarzen Cockpits, bleibt aber sinnvoll): keine Potenz mehr in der Formel (zwei Wurzeln ergeben dieselbe
  Kurve und sind bei 0 überall definiert), am Tag wird der Block gar nicht ausgeführt (`if ( uCkFill > 0.0 )`).
- Stellschraube: `CKFILL_NIGHT` (heller/dunkler). Bild: `docs/bilder/cockpit_nacht_v299.jpg` (vorher/nachher).

## Schwarzes Cockpit nach Wetter- oder Streckenwechsel (behoben in v3.01)
Rückmeldung 24.11.2026 mit zwei Bildern vom Handy (Ferrari; Suzuka und Zandvoort, beide im Regen): Karosserie und Schale in der Helmkamera schwarz, „lädt nicht
immer richtig“.

- **Ursache:** Die Umgebung (Licht und Spiegelung der Autos) ist eine gemeinsame Textur `ENVP.tex`; Materialien holen sie über den Abruf `material.envMap`
  (Eigenschaft am Prototyp von `MeshStandardMaterial`). `clone()` kopiert aber `this.envMap = source.envMap` – der Abruf liefert dabei die **aktuelle** Umgebung,
  und die Kopie legte sie fest bei sich ab. Jeder Neuaufbau der Umgebung (`buildEnv`: neue Strecke, Wetterwechsel) löscht die alte Textur; die Kopie zeigte danach
  auf nichts mehr und bekam kein Umgebungslicht. Im Trockenen fiel das kaum auf (die Sonne beleuchtet weiter), im Regen gibt es keine Sonne → schwarz.
- **Betroffen:** alle Kopien, die bei gebauter Strecke entstehen – die Cockpit-Fassungen des eigenen Autos (`cockCut` → `tp.cutGloss`/`tp.cutMatte`, Schale
  `tp.shellMat`), außerdem Nummern-Materialien (`numMat`) nach einem Team-/Klassenwechsel während einer Sitzung.
- **Warum „manchmal“:** nur wenn nach dem Bau der Cockpit-Teile die Umgebung neu entsteht – zweites Rennen mit demselben Team auf anderer Strecke oder mit anderem
  Wetter, oder das Wetter wird erst nach dem Streckenbau gewählt/ausgelost („Zufall“). Das erste Rennen nach dem Start mit vorher gewähltem Wetter war immer richtig –
  genau so liefen alle meine Einzelprüfungen, deshalb fiel es nicht auf.
- **Behebung:** Der Setzer von `envMap` legt die gemeinsame Umgebung nie mehr im Material ab (`v === ENVP.tex` → `null`); jedes Material holt sie weiter bei jedem
  Bild frisch. Eine eigene, ausdrücklich gesetzte Umgebung bleibt möglich.
- **Nachgestellt und geprüft** mit `node tools/menue/rennfolge_cockpit.js <Ordner> LEC,dry,Zandvoort LEC,light,Zandvoort LEC,heavy,Suzuka` – vorher im zweiten
  Rennen schwarz, jetzt rot. Bild: `docs/bilder/cockpit_schwarz_v301.jpg` (oben vorher, unten jetzt).
- **Irrweg (v3.00):** Zuerst hatte ich eine ungültige Rechnung auf Handy-Grafikchips vermutet (`pow()` mit Basis 0) – nicht nachgestellt, nur geschlossen. Falsch.
  **Lehre:** Ein Fehler, der „manchmal“ auftritt, wird erst nachgestellt (Reihenfolge der Schritte wie beim Spieler: mehrere Rennen, Wetter wechseln), dann behoben.


## Lack in Helm-/TV-Kamera auf dem Handy unscharf (behoben in v3.04)
Rückmeldung 26.11.2026: „In Cockpit- und TV-Ansicht werden die Texturen nicht richtig von dem F1-Auto außen geladen.“ (gleiche Worte wie am 24.11., damals die
einfarbige Schale, siehe oben und `tools/textur/ANLEITUNG.md`).

- **Am Rechner nicht nachstellbar** – Helm und TV zeigen die Lackierung richtig. Der Unterschied liegt beim Handy/Tablet (`DECAL_SMALL`, Zeiger „coarse“).
- **Ursache:** Das Vorbereiten im Ladebildschirm (`showroomPreload`, seit v2.99) baut jedes Team einmal und lädt dabei die Lack-Texturen **aller** Teams
  (`decalUniforms`). Auf Touch-Geräten wird dabei jede Textur auf halbe Auflösung verkleinert – außer für den Fahrer, der **in diesem Moment** gewählt ist (`ownLiv`).
  Wählt man danach ein anderes Team, bleibt dessen Lackierung halb aufgelöst (`DECAL_TEX` merkt sich die Textur). In der Verfolgerkamera fällt das kaum auf,
  in Helm- und TV-Kamera liegt die Nase direkt vor dem Auge → verwaschen. Die Werkzeuge im Testbrowser liefen mit `?nopre` und ohne Touch – deshalb nie gesehen.
- **Nachgestellt** mit einem Testlauf (Touch nachgebildet, `?mitpre`, gespeicherter Fahrer Russell, dann Verstappen gewählt): Red-Bull-Textur 1018 × 1020 statt 2037 × 2041. Nach der Behebung 2037 × 2041, keine Seitenfehler. Bild: `docs/bilder/cockpit_lack_handy_v304.png` (oben vorher, unten nachher; auf der einfarbigen Nase ist der Unterschied klein, deutlicher bei Schriftzügen und Kanten).
- **Behebung:** `ownLivFull()` (aufgerufen in `placeOnGrid`, also bei Fahrerwahl und Rennstart) lädt die Texturen des eigenen Teams in voller Auflösung nach;
  eine noch ladende Textur wird gleich voll übernommen (`userData.full`). Die halbe Textur bleibt sichtbar, bis die volle fertig ist (kein schwarzes Aufblitzen),
  danach wird sie freigegeben. Bogen und Logo der Cockpit-Schale (`decalProj`, nur eigenes Team) werden jetzt immer voll geladen.
- **Offen:** Ob das genau das Bild beim Nutzer war, ist ohne Bildschirmfoto nicht sicher – falls es anders aussieht (falsche Farben, graue/schwarze Flächen), Foto anfordern.

## Sponsoren, Muster und Startnummer fehlen in Helm-/TV-Kamera (behoben in v3.05)
Rückmeldung 26.11.2026 (nach v3.04): „Man sieht die Sponsoren und Nummern und andere Lackierungen nicht aus der Helm- und TV-Ansicht, nur die Farbe.“
Die Unschärfe aus v3.04 war also nicht das Hauptproblem. Zwei Ursachen:

1. **Schale ohne Lack-Textur.** *(Lösung in v3.06 ersetzt, siehe nächster Abschnitt.)* Die Schale (`cockNew`: Vorderdeck, Schultern, Flanken) ersetzt in Helm/TV die Karosserie ums Cockpit – genau die Fläche, die man
   von dort sieht. Seit v2.99 rechnet sie den Grundlack (`livery()`) und projiziert den alten Seitenbogen; alles, was nur in der gebackenen Textur steckt
   (Sponsoren von oben, Muster), fehlte. Nachweis: Shader der Schale enthielt kein `texture2D(uBake…)`, die Cockpit-Fassung der Karosserie schon.
   **Behebung:** `ckShellUV`/`ckShellUVCalc` geben der Schale Textur-Koordinaten (`uvB`) – je Punkt die des nächsten Lack-Dreiecks der Karosserie (Stufe 0,
   gesucht an `aLP`, nur Dreiecke mit ähnlicher Ausrichtung, |cos| ≥ 0,35). Gegen verschmierte Streifen an den Nähten der Abwicklung: eigene Eckpunkte je
   Dreieck, alle drei Ecken im selben Stück der Abwicklung (Stücke = über gemeinsame Punkte verbundene Dreiecke). Dreiecke ohne Gegenstück bekommen
   `uvB = −1` → dort rechnet der Shader weiter den Lack. Ergebnis je Klasse zwischengespeichert (`CK_UV`, Schlüssel = `uvB`-Attribut des Modells).
   Teams ohne gebackene Textur: unverändert (Lack-Programm + Bogen-Projektion).
2. **Startnummer.** Cockpit-Fassung (`cockCut`) und Schale wurden aus `tp.glossMat` gebaut – dem Team-Material **ohne** Nummer; das eigene Auto trägt
   `numMat` (mit Nummer). Beim Zurückschalten wurde außerdem `tp.glossMat` gesetzt → Nummer fehlte danach auch in der Verfolgerkamera.
   **Behebung:** `cockEnt(tp, base, k)` baut Cockpit-Fassung und Schale je Grundmaterial; `m.bodyMat0` merkt sich das Material des Autos und wird beim
   Zurückschalten wieder gesetzt. (Vorher: `tp.cutGloss`, `tp.shellMat` – gibt es nicht mehr.)

Prüfen: `node tools/menue/cockpit_nase.js <Ordner> RUS` (feste Kamera über dem Cockpit, Verfolger → TV → Verfolger; Material muss durchgehend das mit Nummer sein) und
`node tools/wetter/regen_bilder.js Spa dry <Ordner> 2150,3 2150,2 --nohud --pre "S.driver = 'RUS'; MENU.team = byCode('RUS').team"`.
Bild: `docs/bilder/cockpit_textur_v305.png` (links vorher, rechts nachher: Mercedes, Deck vor dem Cockpit).
**Lehre:** Bei „Texturen nicht richtig“ zuerst fragen bzw. vergleichen, WAS fehlt (Schrift? Farbe? Schärfe?) – v3.04 hat eine echte, aber kleinere Ursache behoben.

## Zacken auf den Schultern nach v3.05 → Projektion von oben (v3.06)
Rückmeldung 26.11.2026 mit Bildschirmfoto (Ferrari, Singapur, Nacht, Regen, Helmkamera): „Die Texturen buggen jetzt, gibt es keine bessere oder saubere Lösung?“
Gezackte rot-weiße Flecken auf beiden Schultern, PERONI verzerrt.

- **Ursache:** v3.05 suchte je Punkt der Schale das nächste Karosserie-Dreieck und übernahm dessen Textur-Koordinate. Die Schale hat aber eine eigene Form
  (höhere Schultern, andere Breite als die Karosserie darunter) – die Zuordnung sprang zwischen Flächen und Stücken der Abwicklung. Nachgestellt:
  `node tools/wetter/regen_bilder.js Singapur heavy <Ordner> 600,2 600,3 --nohud --pre "S.driver = 'LEC'; MENU.team = byCode('LEC').team"`.
- **Lösung:** `ckTop`/`ckTopDraw`: Die Karosserie (Stufe 0, Lack aus der gebackenen Textur, sonst Eckpunktfarbe; Carbon-Teile in Carbonfarbe) wird einmal je Team
  **senkrecht von oben** in ein Bild gezeichnet (512 × 1024, Bereich |x| ≤ 0,44, z von `zB` − 0,05 bis `zF` + 0,05; Teile höher als die Schale + 5 cm – Spiegel –
  bleiben weg). Die Schale liest an ihrer Lackierposition (x, z) dieses Bild: Sie sieht dort genau so aus wie die Karosserie von oben, lückenlos.
  Wo das Bild leer ist, rechnet der Shader den Lack wie bisher. Gezeichnet wird, sobald die Lack-Textur geladen ist (beim Cockpitbau oder im ersten Cockpit-Bild);
  nach dem Nachladen in voller Auflösung (`ownLivFull`) neu. Die Punktsuche (`ckShellUV`) ist entfernt.
- Speicher: ein Bild 512 × 1024 je Team, für das der Cockpitbau lief (praktisch nur das eigene), ~2,8 MB mit Mipmaps. Kein Rechenaufwand mehr beim Bau.
- Flanken der Schale (steil) bekommen die Farbe der Kante von oben – dort gestreckt, aus Helm/TV kaum zu sehen.
- Geprüft: Ferrari Singapur Regen (Helm, TV), Red Bull Spa (TV). Bild: `docs/bilder/cockpit_textur_v306.png` (oben v3.05 mit Zacken, unten v3.06).
- **Lehre:** Eine Zuordnung „nächster Punkt“ zwischen zwei verschieden geformten Flächen springt. Wenn man aus einer Richtung schaut, aus dieser Richtung projizieren.
