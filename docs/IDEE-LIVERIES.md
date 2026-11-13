# Idee: Echte Lackierungen (Liveries) als Bild auf die Automodelle laden

Stand: 12.11.2026 – nur Machbarkeit geprüft, noch nichts gebaut.

## Ausgangslage
- Die Modelle (`car.bin`, `f2car.bin`) enthalten keine echten UV-Koordinaten. `parseCarBin` in `index.html` errechnet sie aus der Position (Würfelprojektion je nach Flächenrichtung).
- Die Farbe kommt heute pro Eckpunkt aus einer Klasse (`paintGeo`: 0 Lack, 1 Akzent, 2 Nasenspitze, 3 Carbon, …) und den Werten in `LIV`.

## Vorschlag: Projektions-Layout
Ein Bild je Auto mit drei Ansichten, die senkrecht aufs Modell projiziert werden:
- Seitenansicht (für beide Seiten, rechts gespiegelt oder als eigene Fläche, damit Schrift lesbar bleibt)
- Draufsicht
- Frontansicht (Nase, Flügel)

Die Vorlage (Umrisse des Modells in diesen Ansichten) lässt sich automatisch aus der Modell-Datei erzeugen. Nur Flächen der Klasse „Lack/Akzent/Nase“ bekommen das Bild; Carbon, Reifen und Halo bleiben wie sie sind. Fehlt das Bild, bleibt die heutige Farblackierung.

Dateien wie bei den Logos: z. B. `liveries/MER.png`, `liveries/F2_INV.png`.

## Grenzen
- Schräge Flächen (Seitenkasten-Unterschnitt, Übergang Seite/Oben) verzerren, an den Übergängen entstehen Nähte.
- Kein Ersatz für ein richtig abgewickeltes Modell; feine Sponsorendetails werden nicht fotogenau.
- Die echten Lackierungen gibt es nicht als fertige Vorlage für dieses Modell – sie müssen nachgezeichnet werden.
- Speicher: 22 Autos × Bild. Auf Handys eher 1024 px je Auto.
- Lackierungen und Sponsorenlogos sind geschützt; privat unkritisch, bei öffentlicher Seite bedenken.

## Nächster Schritt
Prototyp mit einem Auto: Vorlage erzeugen, Testbild auflegen, im Showroom ansehen. Danach entscheiden, ob die Qualität reicht.

## Test 12.11.2026: Aufkleber auf dem Mercedes (umgesetzt)
- `index.html`: `DECALS` (Teamlogo an festen Stellen, hier der Stern auf der Nase) und `SHEETS` (Aufkleberbogen von der Seite), beides im Lack-Programm `liveryMat`. Bisher nur für `MER` eingetragen; gilt nur für F1-Autos mit Eintrag in `LIVERY`.
- `liveries/MER.png`: Aufkleberbogen 4096 × 1024 px, obere Hälfte linke Fahrzeugseite (Nase links), untere Hälfte rechte Seite (Nase rechts). Enthält Snapdragon, CrowdStrike, Microsoft (2×), Solera, TeamViewer, Petronas, Signify, AMG, IWC.
- `tools/aufkleberbogen_mer.py`: schneidet die Schriftzüge aus dem offiziellen Seitenbild (formula1.com, 2026) und setzt sie an Modellkoordinaten. Positionen und Größen stehen in der Tabelle `ST`.
- Bekannte Lücken: Startnummer und Halo-Aufkleber fehlen, IWC ist am Frontflügel kaum zu sehen, TeamViewer wird vom Cockpitrand teils verdeckt. Aufkleber von oben (Flügel, Motorabdeckung) gibt es nur als einzelnes Teamlogo.
- Speicher: der Bogen belegt rund 22 MB Grafikspeicher. Für alle Teams wäre 2048 × 512 px je Bogen sinnvoller.

## Offene Frage: Lackierung ganz über den Bogen
Technisch möglich – der Bogen kann auch deckende Farbflächen und Streifen enthalten. Die Seitenprojektion erreicht aber nur seitliche Flächen; Oberseite und Front brauchen eigene Ansichten, für die es keine offiziellen Bilder gibt. Sinnvoll: Grundfarbe weiter berechnen, Streifen und Sponsoren über den Bogen.

## Stand 13.11.2026: Aufkleber für alle F1- und F2-Autos (umgesetzt)
- Alle Angaben je Auto stehen in `tools/sticker/<Kürzel>.json`; daraus baut `tools/sticker/build.py` den Bogen `liveries/<Kürzel>.png` und die Datei `liveries/liveries.json`, die das Spiel liest. Anleitung: `tools/sticker/ANLEITUNG.md`.
- 11 F1-Teams und 18 F2-Lackierungen: Grundfarbe, große Farbflächen und Sponsoren aus den offiziellen Seitenfotos, Startnummer im Design des Fahrers (`liveries/num/`), kein Aufkleber auf dem Halo. Der MX-5 bleibt unverändert.
- F2: jedes Auto mit eigenem Design hat ein eigenes Kürzel; die früher geteilte Pink-Lackierung ist aufgeteilt in `F2_PINK_MPM`, `F2_PINK_ROD`, `F2_PINK_ART`.
- Nur geschätzt oder unvollständig (kein Seitenfoto): Invicta #1, Campos #6, DAMS #8, MP #9, Prema #12 (Grün laut Miami-Fotos), Rodin #15, ART #16. Der BWT-Schriftzug der pinken Rodin- und ART-Autos ist als Schrift erzeugt, nicht aus einem Foto.
- Bögen sind 2048 × 1024 px; Geräte mit Touch-Bedienung laden sie in halber Auflösung.

## Stand 13.11.2026 (2): Racing Bulls und Karts
- Racing Bulls: die blaue Fläche kommt jetzt als glatte Kurven aus der Grundfarbe (`glsl` in `tools/sticker/RB.json`) statt als Ausschnitt aus dem Foto; VISA und „Red Bull“ sind eigene, nicht gespiegelte Schriftzüge. `build.py` kennt dafür `mask` (Teilkästen für schräge Schrift).
- Karts: erfundener Aufklebersatz je Team, im Spiel gezeichnet (`kartStickerDraw` in `index.html`, keine Bilddateien): Zierform in fünf Arten, Team-Schriftzug auf Seitenkästen, Frontschürze und Nummerntafel, erfundene Ausrüster (`KART_SPONSORS`), gelbe Nummernfelder mit der Startnummer des Fahrers. Die Lage der Flächen in der Textur steht in `KART_UV` und `KART_PLATES` (am Modell ausgemessen).

## Roadster (RONE Racing) – echte Aufkleber, November 2026

Der Roadster trägt jetzt die Aufkleber des echten Autos, aus den Fotos geschnitten. Technik anders als bei F1/F2: eigenes dünnes Netz über dem Lack statt Projektion im Shader (`liveries/MX5.png` + `liveries/MX5.json`). Einzelheiten, Positionen und offene Punkte: `tools/sticker/mx5/ANLEITUNG.md`.
