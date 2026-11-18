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
- Nur geschätzt oder unvollständig (kein Seitenfoto): Invicta #1, Campos #6, DAMS #8, MP #9, Prema #12 (Grün laut Miami-Fotos), Rodin #15, ART #16. (Stand später: siehe Abschnitt „F2: Farbflächen geglättet, zweite Autos“.) Der BWT-Schriftzug der pinken Rodin- und ART-Autos ist als Schrift erzeugt, nicht aus einem Foto.
- Bögen sind 2048 × 1024 px; Geräte mit Touch-Bedienung laden sie in halber Auflösung.

## Stand 13.11.2026 (2): Racing Bulls und Karts
- Racing Bulls: die blaue Fläche kommt jetzt als glatte Kurven aus der Grundfarbe (`glsl` in `tools/sticker/RB.json`) statt als Ausschnitt aus dem Foto; VISA und „Red Bull“ sind eigene, nicht gespiegelte Schriftzüge. `build.py` kennt dafür `mask` (Teilkästen für schräge Schrift).
- Karts: erfundener Aufklebersatz je Team, im Spiel gezeichnet (`kartStickerDraw` in `index.html`, keine Bilddateien): Zierform in fünf Arten, Team-Schriftzug auf Seitenkästen, Frontschürze und Nummerntafel, erfundene Ausrüster (`KART_SPONSORS`), gelbe Nummernfelder mit der Startnummer des Fahrers. Die Lage der Flächen in der Textur steht in `KART_UV` und `KART_PLATES` (am Modell ausgemessen).

## F2: Farbflächen geglättet, zweite Autos – 13.11.2026 (3)
- Problem: große Farbflächen kamen als Fotoausschnitt (`kind: key`) mit Schatten, Spiegelungen und Lücken aufs Auto und wirkten abgehackt (Trident Rot/Blau, VAR-Schwung, Prema-Bänder, DAMS-Hellblau, MP-Schwarz, Rodin-Haube, Campos-Weiß).
- Lösung wie bei Racing Bulls, aber automatisch: `build.py` kennt `smooth` (+ `holes`, `grow`), siehe `tools/sticker/ANLEITUNG.md`. Gesetzt bei AIX, BLK, CAMW, DAM, GREY, HIT, INV, ITA, ORA, PINK_ART, TRI, VAR. Prema #11 hat zusätzlich den SAGA-Schriftzug.
- Zweite Autos ohne eigenes Foto fahren jetzt die Lackierung des Teamkollegen (Wunsch des Nutzers): Câmara #1 = Invicta wie Dürksen, Tsolov #6 = Campos wie León, Biliński #8 = DAMS wie Beganović. `F2_INV1`, `F2_CAMR`, `F2_DAM2` gelöscht, Fahrer in `drivers` der ersten Lackierung.
- Neue Fotoquellen: Rennfotos in den Artikeln von fiaformula2.com (Fahrerseiten `/en/drivers/<name>` verlinken Artikel; Bilder unter `res.cloudinary.com/prod-f2f3/image/upload/c_limit,w_1600/f2/global/articles/…`). Gefunden: MP #9 und ART #16 pink mit rotem Windhager-Heckflügel, Prema #12 grün (Aston-Martin-Farben, gelbgrüner Strich an der Nase). Keine Fotos gefunden für Câmara #1, Tsolov #6, Biliński #8, Dunne #15.
- Rodin #15 (Dunne): kein Foto, aber Berichte (Alpine-Akademie, pinke BWT-Lackierung) und der Rennanzug passen zu Pink – deshalb pink geblieben, roter Heckflügel wie bei den anderen pinken Alpine-Autos (Annahme).

## Roadster (RONE Racing) – echte Aufkleber, November 2026

Der Roadster trägt jetzt die Aufkleber des echten Autos, aus den Fotos geschnitten. Technik anders als bei F1/F2: eigenes dünnes Netz über dem Lack statt Projektion im Shader (`liveries/MX5.png` + `liveries/MX5.json`). Einzelheiten, Positionen und offene Punkte: `tools/sticker/mx5/ANLEITUNG.md`.

## Reifenflanken F1 und F2 – November 2026

Die Reifen tragen die echte Beschriftung (PIRELLI, P ZERO, zwei Bögen mit Karomuster) in der Farbe der Mischung (rot, gelb, weiß). Vorlage: Produktbild eines Pirelli-Reifens von vorn; daraus `textures/reifen_flanke.png` (weiß, Deckkraft = Zeichnung). Im Spiel: `ringParts()` legt auf beide Flanken einen Kreisring mit dieser Textur, `WMAT` blendet per `alphaTest` aus, die Farbe kommt aus der Eckpunktfarbe. Kein zusätzlicher Zeichenaufruf. Der graue Felgenring und das FSC-Zeichen des echten Reifens fehlen. Nur im Showroom geprüft.

## Radabdeckungen F1 – November 2026

Jedes F1-Team hat seine Radabdeckung der Saison 2026 (Vorlage: F1-Grafik „Wheel covers for 2026“). Technik: flache Scheibe auf der Radaußenseite in `wheelGeoM()`, Design je Team in `WHEEL_COVER` gezeichnet, `wheelMat(team)` legt es in die Mitte einer Kopie der Flankentextur. Kein zusätzlicher Zeichenaufruf; je Team eine Textur (1024², auf Touch-Geräten 512²). Die Designs sind nach der Grafik nachgezeichnet, nicht ausgeschnitten. F2 und Kart unverändert. Nur im Showroom geprüft.

## Idee 18.11.2026: echte Texturen wie bei den Klassikern (noch nichts gebaut)

Frage des Nutzers: Lassen sich aus den Aufklebern „richtige“ Texturen machen wie bei den historischen Autos?

**Unterschied heute:**
- Klassiker (`modelle/klassiker/*.glb`): fertige Modelle mit UV-Abwicklung, Lack und Sponsoren als Bild (1024 px) – jede Fläche hat ihren festen Platz in der Textur, auch Oberseite und Front.
- F1/F2 (`car.bin`, `f2car.bin`): **ein** gemeinsames Modell je Klasse ohne UV-Koordinaten (`parseCarBin` errechnet nur eine Würfelprojektion). Die Lackierung entsteht im Shader: Grundfarbe aus `glsl`, Aufkleberbogen nur **von der Seite** projiziert, Teamlogo und Nummer als Einblendung.

**Weg dorthin:**
1. Einmalig `car.bin` und `f2car.bin` abwickeln (z. B. xatlas in Python), UV-Koordinaten in die .bin schreiben (alle drei Detailstufen gleiche Abwicklung bzw. eigene, gebacken aus Stufe 0).
2. Backen: je Lackierung das heutige Ergebnis (glsl + Bogen + Logo) in eine Textur 1024² (Touch 512²) rendern – sieht danach zunächst gleich aus, ist aber die Grundlage.
3. Nachbessern pro Fläche: Oberseite (Motorabdeckung, Nase, Heckflügel, Endplatten), die die Seitenprojektion nicht erreicht; Nähte an schrägen Flächen fallen weg.
4. Startnummer bleibt Einblendung je Fahrer (sonst eine Textur je Fahrer statt je Team).
5. Danach im Spiel ein einfaches Material mit Textur statt Projektions-Shader (eher leichter; Speicher 1024² ≈ 5 MB mit Mipmaps statt 2048×1024 ≈ 8 MB heute).

**Referenzen (Stand 18.11.2026 geprüft):**
- Alle 27 Aufkleber-Dateien `tools/sticker/*.json` mit Foto-Adresse und Ausschnitt-Koordinaten liegen im Repo; die offiziellen Seitenfotos (formula1.com, fiaformula2.com) sind noch abrufbar.
- `tools/sticker/.cache/` (Ausschnitte, Übersichten) ist nicht eingecheckt, `photo.py` erzeugt es neu.
- Es gibt **nur Seitenansichten**. Für Oberseite/Front fehlen Vorlagen – müssten aus Launch- und Rennfotos (schräg/oben) nachgezeichnet werden.

**Vorschlag:** Prototyp mit einem Team (Mercedes), im Showroom vergleichen, dann entscheiden.

## Echte Texturen F1 – umgesetzt in v2.73 (18.11.2026)
Prototyp mit Mercedes, danach alle F1-Lackierungen gebacken. Werkzeuge und Ablauf: `tools/textur/ANLEITUNG.md`.
- `car.bin` hat jetzt eine UV-Abwicklung des Lack-Teils (alle drei Detailstufen in einer Textur 1708 × 1710, 300 Bildpunkte je Meter in Stufe 0;
  die alten Bögen hatten ~370/m, aber nur von der Seite). Unveränderte Vorlage: `tools/textur/quelle/car.bin`.
- Je Team `liveries/textur/<Kürzel>.webp` (verlustfrei, zusammen 4,7 MB für 12 Lackierungen; die alten F1-Bögen waren 2,7 MB und werden für gebackene Teams nicht mehr geladen), gebacken aus dem bisherigen Lack-Programm + Bogen + Logo. Sieht im Showroom gleich aus wie
  vorher (Schrift minimal weicher), keine sichtbaren Nähte. Startnummer bleibt Einblendung.
- Der eigentliche Gewinn kommt erst mit dem nächsten Schritt: Oberseite, Nase und Flügel lassen sich jetzt bemalen (Projektionen von oben/vorn beim Backen
  oder Malprogramm) – dafür fehlen noch Referenzfotos von oben/schräg. Die Seitenfotos in `tools/sticker/*.json` sind noch abrufbar.
- Sichtbarkeits-Messung (nur sichtbare Dreiecke abwickeln) ausprobiert und verworfen: nur 0,2 von 15,6 m² Lackfläche sind unsichtbar.

### v2.74: Texturen im Rennen so scharf wie im Showroom
Rückmeldung: in der Nähe, vor allem am eigenen Auto in der Außenansicht, zu unscharf. Ursache: Verfolgerkameras zeigen das eigene Auto in Detailstufe 1
(Gegner ab 6 m ebenfalls), und Stufe 1 hatte nur 30 % Maßstab in der Textur (~90 statt 300 Bildpunkte je Meter). Jetzt Stufe 0 und 1 gleich (271/m),
Textur 2037 × 2041 (Grafikspeicher je Team ~22 MB mit Mipmaps statt ~15 MB). Touch-Geräte: eigene Lackierung voll, andere halb.

### v2.75: F2 mit Texturen, Ansicht von oben vorbereitet
- F2-Modell abgewickelt (1809 × 1809, 300/m), alle 15 F2-Lackierungen gebacken – sehen aus wie vorher.
- Technik für die Ansicht von oben fertig (build.py `top`, backen.js mit Höhenkarte), mit einem Testgitter geprüft. Die eigentlichen Draufsichten
  folgen, sobald Referenzbilder gefunden sind (Auftrag des Nutzers 18.11.: „Bilder von oben suchen, Texturen von allen Seiten komplett, auch F2 und Karts“).
- Leistungsmessung v2.73 (Monza, volles Feld, Software-Rendering): Zeichenaufrufe, Dreiecke, Shader-Programme gebacken = alt; 162 statt 169 Texturen.
- shot.js zeigte seit v2.72 immer Russells Mercedes (Titelbildschirm zeigt das Auto des gewählten Fahrers) – setzt jetzt einen Fahrer des Teams.

### v2.76/v2.77: Überschneidungen und Halos (Rückmeldungen 18.11.2026)
- Doppelte Sponsoren: was der Seitenbogen schon trägt (Schulter der Motorabdeckung, Seitenkasten-Rand), nicht noch einmal aus der Draufsicht nehmen
  (Mercedes: Microsoft/Solera/TeamViewer standen doppelt). Seitenbogen läuft jetzt weich aus (Normale 0,3 → 0,55 statt harter Kante bei 0,45),
  Draufsicht greift erst ab 0,5 (weich bis 0,72).
- Halo je Lackierung einfarbig in der echten Farbe, ohne Logos: `tools/sticker/halo.json` (am oberen Bügel der Seitenfotos abgelesen) → `halo` in
  liveries.json → `liveryMat` (Klasse 7) und TV-Halo (`haloFlat`). Bunt: Alpine rosa, Aston Martin grün, Audi grau, Haas weiß; F2: AIX grün,
  ITA rot, DAMS/Trident dunkelblau, BLK/Campos/Rodin hell; sonst schwarz.
