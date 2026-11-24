# Cockpit-Ansicht (Helm- und TV-Kamera)

Stand 24.11.2026 (v2.99). Ältere Einzelheiten zum Cockpit-Modell: `docs/AENDERUNGEN-1.22.md` (Abschnitt „Cockpit-Neubau“), zur Leistung: `docs/LEISTUNG-ANLEITUNG.md`.

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
  (am Tag 0, nachts `CKFILL_NIGHT` = 0,24, gesetzt in `drawWheel`). Formel: `Bild = max(Bild, Eigenfarbe^0,35 × Wert × (0,55 + 0,45 × Normale nach oben))` – dunkle
  Flächen werden verhältnismäßig stärker angehoben als helle (Carbon wird erkennbar), Flächen nach oben mehr (Flutlicht von oben, gibt Form); was schon beleuchtet
  ist (Handschuhe im Flutlicht), bleibt unverändert.
- Falle: Die Bildabstimmung zieht alles unter ~0,02–0,03 (linear) zu Schwarz (Kontrast um Mittelgrau, `uCon`). Der erste Versuch (Zuschlag 0,07) blieb deshalb
  unsichtbar – gemessen im Bild, nicht geschätzt.
- Die Materialien hängen nur am eigenen Auto in Helm-/TV-Kamera – andere Autos und die Verfolgerkameras bleiben unverändert. Kein Neuübersetzen beim Wechsel Tag/Nacht.
- Stellschraube: `CKFILL_NIGHT` (heller/dunkler). Bild: `docs/bilder/cockpit_nacht_v299.jpg` (vorher/nachher).
