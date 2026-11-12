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
