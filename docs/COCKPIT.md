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

