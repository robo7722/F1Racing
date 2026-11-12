# Eigene Logos

Lege hier PNG-Dateien ab. Das Spiel lädt sie beim Start. Fehlt eine Datei, bleibt die eingebaute Grafik.

## Team-Logos
Ersetzen die gezeichneten Wappen.

- Dateiname = Team-Kürzel + `.png`, Groß-/Kleinschreibung genau so wie unten
- quadratisch, am besten 256 × 256 px, transparenter Hintergrund

## Titel-Logo (ersetzt „FORMULA RACING“)

Eine einzige Datei: **`logos/LOGO.png`**. Sie erscheint an drei Stellen:

1. beim Starten auf dem Ladebildschirm (groß, mittig)
2. im Hauptmenü oben links (statt des Schriftzugs)
3. in allen Untermenüs klein oben rechts neben dem Zahnrad

So tauschst du es auf GitHub:

1. Bild vorbereiten: PNG, Querformat, **transparenter Hintergrund**, etwa 1000 × 300 px. Das Logo sollte hell sein – der Hintergrund im Spiel ist dunkel. Kein leerer Rand um das Motiv, sonst wirkt es kleiner.
2. Datei genau `LOGO.png` nennen (Großbuchstaben, Endung klein).
3. Auf GitHub das Repository öffnen → Ordner `logos` → **Add file → Upload files** → Datei hineinziehen → **Commit changes**.
4. Ein bis zwei Minuten warten, dann das Spiel neu laden. Als installierte App: einmal ganz schließen und wieder öffnen; erscheint das alte Logo noch, ein zweites Mal neu laden.

Ändern: einfach eine neue `LOGO.png` hochladen (überschreibt die alte). Zurück zum Schriftzug: `LOGO.png` auf GitHub löschen.

## Formel 1
`MER.png` Mercedes · `FER.png` Ferrari · `MCL.png` McLaren · `RBR.png` Red Bull · `AST.png` Aston Martin · `WIL.png` Williams · `RB.png` Racing Bulls · `ALP.png` Alpine · `HAA.png` Haas · `AUD.png` Audi · `CAD.png` Cadillac · `RON.png` RONE Racing

Die elf echten Teams liegen als 512 × 512 px, transparenter Hintergrund, helle Emblem-Variante ohne Schriftzug vor. Quelle: Teamlogos der offiziellen F1-Seite (formula1.com, Saison 2026, Variante „logowhite“), Leerrand abgeschnitten und quadratisch zentriert.

## Formel 2 und Kart
Kürzel mit Vorsatz `F2_` bzw. `K_`, z. B. `F2_INV.png` (Invicta), `F2_HIT.png` (Hitech). Die vollständige Liste steht in `index.html` bei `F2_TEAMS` und `KART_TEAMS`.

### Formel 2 (vorhanden)
`F2_INV.png` Invicta Racing · `F2_HIT.png` Hitech · `F2_CAM.png` Campos Racing · `F2_DAM.png` DAMS · `F2_MPM.png` MP Motorsport · `F2_PRE.png` Prema Racing · `F2_ROD.png` Rodin Motorsport · `F2_ART.png` ART Grand Prix · `F2_AIX.png` AIX Racing · `F2_VAR.png` Van Amersfoort Racing · `F2_TRI.png` Trident Racing

Alle 512 × 512 px, transparenter Hintergrund, helle Variante für dunklen Untergrund. Invicta ist im Original gelb und wurde auf Weiß umgefärbt. Quelle: Teamlogos der offiziellen F2-Seite (fiaformula2.com, Saison 2026, Variante „logowhite“), Leerrand abgeschnitten und quadratisch zentriert.

Logos, die du in den Einstellungen auf dem Gerät lädst, haben Vorrang vor diesen Dateien.
