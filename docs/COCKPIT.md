# Cockpit-Ansicht (Helm- und TV-Kamera)

Stand 24.11.2026 (v3.00). Ältere Einzelheiten zum Cockpit-Modell: `docs/AENDERUNGEN-1.22.md` (Abschnitt „Cockpit-Neubau“), zur Leistung: `docs/LEISTUNG-ANLEITUNG.md`.

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
- **Fehler v2.99 → behoben v3.00: Cockpit „manchmal schwarz“** (Rückmeldung mit Bild vom Handy: Ferrari, Suzuka, Regen am Tag – Karosserie und Schale schwarz, Handschuhe
  und Lenkrad richtig). Im Testbrowser nicht nachstellbar. Sehr wahrscheinliche Ursache: Die Formel rechnete `pow( Eigenfarbe, 0.35 )`. Bei Basis 0 liefern manche
  Handy-Grafikchips dafür einen ungültigen Wert (NaN); reine Farben haben Kanäle mit genau 0 (Ferrari-Rot: Grün und Blau). Auch am Tag (Wert 0) blieb `0 × NaN = NaN`,
  ging durch `max()` ins Bild und wurde in der Bildabstimmung (Helligkeit über alle Kanäle) zu Schwarz. Handschuhe und Lenkrad haben keine Kanäle mit 0 – sie blieben richtig.
  Jetzt: keine Potenz mehr (zwei Wurzeln ergeben dieselbe Kurve und sind bei 0 überall definiert), und am Tag wird der Block gar nicht ausgeführt (`if ( uCkFill > 0.0 )`).
  Zusätzlich abgesichert: Ist die Lack-Textur eines Teams noch nicht geladen (langsames Netz, Ladefehler), zeigt der Lack den berechneten Farbverlauf statt einer leeren
  Textur (`uBakeOn`), und der Fahrbahn-Shader im Regen rechnet seine Spiegelstärke ohne `pow()`.
  **Regel für alle Shader:** kein `pow()` mit einer Basis, die 0 werden kann; nichts ins Bild mischen, das NaN sein könnte (auch nicht mit Faktor 0). Der Testbrowser
  (Software-Grafik) rechnet hier „richtig“ und zeigt solche Fehler nicht.
- Stellschraube: `CKFILL_NIGHT` (heller/dunkler). Bild: `docs/bilder/cockpit_nacht_v299.jpg` (vorher/nachher).
