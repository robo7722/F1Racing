# Version 1.22 – Menüs, Positionsturm, Kameras

## Menüs
- **Hauptmenü**: Ziffern 01–04 entfernt. Karriere-Kachel mit weißem Kopfband (Titel + Stand), kleine Kacheln mit Titel oben, Beschreibung unten links, Symbol im roten Feld unten rechts. Anordnung unverändert.
- **Streckenwahl**: Infotafel links (große Skizze, Kurven, Länge, Runden, Land, Kurs), Streckenname als Konturschrift, Streckenleiste unten.
- **Teamwahl**: Teamname oben links, Konturschrift über dem Showroom, Wappenleiste unten, Autos mittig.
- **Karriere › Tabelle**: eine Spalte.
- **Karriere › Rennen**: Karte „Nächstes Rennen“ einzeilig gesetzt, Streckenskizze kleiner, nichts läuft mehr aus der Karte.

## Im Rennen
- **Positionsturm** oben links (`#tower`): Führender, zwei Fahrer davor, Spieler, zwei dahinter. Abstand jeweils zum Vordermann.
- **TV-Kamera**: festes Sichtfeld (`TVFOV` = 78°); Lage der Halo-Grafik wird einmal je Bildgröße berechnet statt in jedem Bild.
- **Helmansicht**: Schmutzspritzer treffen während der Fahrt auf und verblassen in 8–17 s (`visorDirtTick`). Häufiger im Windschatten und neben der Strecke.
- **Cockpit (Test)**: Halo sichtbar, aber durchscheinend (`HALO_GH`): geradeaus fast klar, nach oben und unten zunehmend deckend, an den Seiten voll deckend.
- **Cockpit F1**: Abdeckung vor dem Lenkrad breiter und mit steiler Flanke – verdeckt die gezackte Carbonkante und das offene Ende der Spiegelstreben.

## Stellschrauben
| Was | Wo | Wert |
|---|---|---|
| Halo-Deckkraft Mitte / Rand | `HALO_GH.aMin` / `aMax` | 0,08 / 0,85 |
| Seitliches Einblenden | `HALO_GH.s0` / `s1` | 0,24 / 0,58 |
| Schmutz-Grundrate | `visorDirtTick`, `0.16` | Spritzer je Sekunde bei 60 m/s |
| TV-Sichtfeld | `TVFOV` | 78° |

## Nachtrag (zweite Runde)
- **Hauptmenü**: keine Kamerafahrt mehr – fester, gezeichneter Hintergrund; die Strecke wird dort nicht gerendert.
- **Team-/Fahrerwahl**: Rückwand im Showroom in Teamfarbe mit Teamname als Konturschrift (`showroomWall`), liegt hinter den Autos.
- **Eigene Team-Logos**: Einstellungen › „Team-Logos“ › „Logos laden“. Dateiname = Kürzel oder Teamname (`MER.png`, `ferrari.svg`, `red-bull.png`). Gespeichert nur auf dem Gerät (`localStorage`, Schlüssel `f1logos`), nicht im Projekt.
- **Cockpit-Halo**: blendet direkt an der Kamera aus (kein Blick ins hohle Rohr).
- **Cockpit F1**: Seitenwangen an der Abdeckung neben dem Lenkrad; Öffnung an den Händen breiter (`COCK.f1.wn` 0,055).
- **Cockpit F2**: Öffnung an Lenkrad und Händen breiter (`COCK.f2.wn` 0,05).
- Bewusst nicht gemacht: 1:1-Kopie der Menüs eines bestehenden Spiels. Aufbau und Stimmung sind angelehnt, die Gestaltung ist eigen.

## Nachtrag (dritte Runde)
- **Ablauf** im schnellen Spiel und Zeitrennen: Klasse → Team → Fahrer → Strecke → Rennen.
- **Auswahl-Studio**: Autos stehen fest in Seitenansicht, keine Drehteller, keine Rotation. Teamwahl zeigt ein Auto; zur Fahrerwahl fährt die Kamera zurück und das zweite Auto erscheint; auf der Streckenwahl steht das Auto des gewählten Fahrers rechts, der Streckenname auf der Rückwand.
- **Hauptmenü**: oben zwei große Kacheln (Karriere, Schnelles Spiel), darunter die kleinen.
- **Logos im Repo**: PNGs in `logos/` ablegen, siehe `logos/LIESMICH.md`.
- **Cockpit**: Abdeckung, Seitenwangen und breitere Öffnungen (F1/F2) wieder entfernt – Karosserie wie in 1.21. Der durchscheinende Halo bleibt.
- Pfeil der Weiter-Taste als gezeichneter Winkel, exakt mittig.

## Nachtrag (vierte Runde)
- **Hauptmenü**: graue Glaskacheln mit runden Ecken; in der Karriere-Kachel steht das eigene Auto (Fenster ins Studio).
- **Kamerafahrten im Studio** (`showroomFrame`): Teamwahl nah und schräg von vorn · Fahrerwahl: Fahrt nach vorn, beide Autos frontal · Streckenwahl: Fahrt zur Seite, Auto genau seitlich rechts. Überall leichtes Schweben.
- **Cockpit F1**: nur die Abdeckung vor dem Lenkrad ist breiter und hat eine steile Flanke; keine Seitenwangen, Öffnung unverändert.

## Nachtrag (fünfte Runde)
- **Dynamische Auflösung entfernt** (`dynRes`): die Auflösung bleibt im Rennen fest.
- **Cockpit-Kamera** 3,5 cm tiefer (F1 0,765 · F2 0,795): der Halo-Bügel liegt über dem Horizont.
- **Studio mit 120 mm Brennweite** (`SHOW_FOV` 11,4°), Kamera entsprechend weiter weg. Fahrerwahl: flacher von vorn, Autos 2,45 m nebeneinander.
- **Hauptmenü**: Bilder für Schnelles Spiel, Zeitrennen, Einstellungen (`textures/menu_*.jpg`, aus dem Spiel aufgenommen); Auto in der Karriere-Kachel rechts neben der Taste.
- **Untermenüs** in Graphitglas und Weiß statt Navy und Hellblau, fester Facetten-Hintergrund; die Strecke wird in Menüs nicht mehr gerendert.
- **Eigenes Spiel-Logo**: `logos/LOGO.png` ersetzt den Schriftzug im Hauptmenü.

## Nachtrag (sechste Runde)
- **Cockpit F1 als einheitliche Schale** (`cockShell`): eine durchgehende Fläche ersetzt das Deck rund um die Öffnung; die Karosserie wird dort in der Cockpitansicht nicht gezeichnet (`SHELL`, `cockCutGLSL`). Randhöhen werden einmal am Modell vermessen. Wanne und Schale entstehen an einer Stelle (`cockBuild`).
- **Cockpit zuletzt gezeichnet** (`cockLast`, Reihenfolge 990): Windschatten und Luftstreifen liegen nicht mehr darüber.
- **Cockpit-Kamera**: Höhe und Blickneigung fest, kein Nicken beim Bremsen/Beschleunigen.
- **Studio**: Schwenk beim Teamwechsel (`showroomSwing`), Spiegelung von Auto und Wand im Boden, wandernde Lichtbänder auf der Wand.
- **Hauptmenü**: zeigt bei laufender Karriere das Karriere-Fahrzeug (`showroomCareer`).
- **Klassenwahl**: Rennbilder je Klasse (`textures/class_*.jpg`, Ultra-Grafik, Tiefenunschärfe nachträglich berechnet).
- **Knöpfe**: Pfeile und Symbole als gezeichnete Formen statt Schriftzeichen.

## Nachtrag (siebte Runde)
- **Cockpit-Schale nach Referenz, für F1 und F2** (`SHELLS`, `cockShell`): Schultern steigen von der Öffnung nach außen an, Carbon-Einfassung der Öffnung, breite Blende vor dem Lenkrad. Randhöhen per Median gegen Ausreißer geglättet.
- **F2-Modell**: Normalen an der Nase korrigiert (`renormCar`, Bezugshöhe an der Nase tiefer).
- **Gelände**: Höhen der Geländebänder an der tatsächlichen Position (`foldLim`) – keine senkrechten Wände im Kurveninneren (Red Bull Ring); Hügelstärke und Höhe zwischen zwei Streckenteilen stetig.
- **Klassenbilder**: Auto scharf, Hintergrund unscharf. Hauptmenü ohne Symbole.

## Cockpit-Neubau (F1 und F2)
- **Neues, eigenständiges Cockpit-Modell** (`cockNew`, Maße in `CK`): Wanne, Innenwände, Carbon-Einfassung, Schultern, Armaturenwulst, Vorderdeck und Flanken als ein geschlossenes Netz aus Querschnitten. Es misst nichts am Fahrzeugmodell.
- Das Fahrzeugmodell wird in der Cockpitansicht im Kasten um das neue Modell nicht gezeichnet (`cockCutGLSL`); kurz vor der Vorderachse taucht das neue Modell 1,5 cm kleiner in die echte Nase ein.
- Die früheren Ansätze (`cockTub`, `cockShell`, `SHELLS`) werden für F1/F2 nicht mehr verwendet und können entfernt werden.

## Version 1.23
- **Helm-Modell F1/F2** aus einer Vorlage auf ~3500 Dreiecke reduziert (`HELM_BIN`, `helmGeoNew`), eine Geometrie für alle Autos; Fahrerdesigns als Farbschema im Shader (`HELM_DESIGN`, `helmMat`, 7 Muster). Fahrer (Schultern, Arme, HANS) im Auto.
- **F2-Halo neu modelliert**: ebener Rohrbügel mit geraden Armen, Enden in den Halterungen.
- **F1-Netz**: Kerben an der Unterkante der Seitenkästen geschlossen (`fillNotches`).
- **Studio**: LED-Wand mit Animation und Glitch-Schrift (`wallDraw`); Teamwechsel = Kamera dreht 180° auf der Stelle, Bühne mit neuem Team auf der Gegenseite (`showroomSwap`).
- **Klassenbilder**: Kartbahn Genk, Spa (Raidillon), Singapur (Riesenrad).
- Logos bei jedem Start frisch, Streckenwahl nur über „Weiter“, Cockpit vorgeladen, Überlagerungen im Menü-Stil.

## Version 1.24
- **F2-Modell neu aus dem Original vereinfacht** (`f2car.bin`): Kanten und Ränder bleiben erhalten, Normalen mit Knickwinkel, Halo vollständig. Frühere Nachbesserungen (Normalen, Abdeckplatte, Ersatz-Halo) entfernt.
- **F1**: Spiegelglas in Himmelsfarbe (Shader, `uMir`); Kerben-Füllung an den Seitenkästen wieder entfernt (flackerte).
- **Cockpit**: Nahgrenze 7 cm. **Teamwechsel**: kurzer Schwenk (~70°, 0,75 s).
- **Menüs**: überall eckig; Titelabstand wie vor der Textentfernung; Helmfarben verteilt und in der Fahrerwahl identisch; Logo-Laden im Spiel entfernt (nur noch `logos/`).

## Version 1.25
- **F1-Modell neu aus dem Original** („F1 2026 concept (polygon model)“, Qvist_designs, CC-BY-4.0; 1,16 Mio. Dreiecke, ein Netz ohne Materialien). Ursache der Zacken: Lack/Carbon war früher je Dreieck zugeordnet. Jetzt: Karosserie je Detailstufe als Ganzes vereinfacht (78k / 24k / 7,5k), danach **exakt entlang fester Linien geschnitten** (Boden-Oberkante je Längsposition, Querlenker, Heck, Flügel, Nase, Halo, Cockpit-Innenwand) und erst dann je Dreieck klassifiziert. Räder unverändert aus dem alten `car.bin` übernommen. Spiegelglas als eigenes Teil (`mirror`), Shader-Regel `mirF` stillgelegt.
- Umwandlungsskripte (nur in der Sitzung, nicht im Repo): `f1dec.py` (Vereinfachen), `f1cls.py` (Schnittfelder + Klassen), `f1conv.py` (Schreiben). Achsen: Spiel-x = Quelle-z, y = y + 31 mm, z = 1770 mm − x.
- **F1-Lackierungen**: dunkle Unterkante (`y < 0,15…0,2`) bei 7 Teams entfernt – der Lack reicht bis zum Carbon-Boden.
- **F2-Lackierungen** nach den offiziellen Testfotos 2026 (Barcelona): Prema oben rot/unten weiß, AIX Kupfer mit Leuchtgrün, VAR Orange mit Schwarz, Trident weiß/blau/rot. Übrige Teams passten bzw. waren auf den Fotos nicht eindeutig zu sehen.
- **Menü**: Titel-Logo mittig zwischen Rand und Kacheln; Klassenwahl ohne Haken und ohne Helligkeitswechsel, Fotos F2/F1 gespiegelt, Klassen-Logos aus `logos/KART.png`, `F2.png`, `F1.png`; Schrittleiste: Zahl und Text auf einer Grundlinie, mehr Luft hinter „Rennen“.
- **Studio**: Boden schwarz mit Spiegelung; Teamwechsel mit weicher Blende (Unschärfe + Abdunkeln zur Mitte des Schwenks).

## Version 1.26
- **Teamwechsel**: Bewegungsunschärfe wie bei offenem Verschluss – nur waagrecht (SVG-Filter `#mbx`, `feGaussianBlur stdDeviation="x 0"` auf der Zeichenfläche), Stärke = Schwenkgeschwindigkeit; kein Abdunkeln mehr.
- **F2-Cockpit**: Carbon-Teile über dem Kopf (y > 0,86 im Halo-Bereich) werden in der Cockpitansicht nicht gezeichnet (`cockCutGLSL`).
- **Helmansicht**: Visieröffnung endet unten früher (mehr Kinnbügel im Bild).
- **Einstellungen aus dem Menü**: es wird nichts neu gezeichnet – vorher lief dahinter die Strecke des letzten Rennens weiter.
- **Klassen-Logos**: `logos/F2.png` ohne Schriftzug, 3× hochskaliert mit geschärften Kanten (zwei Flächenfarben).

## Version 1.27
- **Klassenwahl**: Blinken der abgewählten Karte behoben (beim Wegfall von `.on` startete die Einblend-Animation `f1in` neu) – Karten ohne Animation/Übergang. F2-Logo aus neuer Vorlage (ohne Schriftzug, weißer Grund herausgerechnet).
- **Hauptmenü → Untermenü**: schräger Wischer in Rot/Weiß/Dunkel (`#mwipe`, in `showScreen`).
- **Einstellungen/Pause**: kein Fensterrahmen mehr, Inhalt direkt auf dem abgedunkelten Hintergrund, Überschrift mit rotem Schrägstrich.
- **TV-Kamera**: zeigt jetzt das modellierte Cockpit mit Lenkrad und Armen (gleiche Umschaltung wie Cockpitansicht).
- **Cockpit F1**: Spiegelhalter werden nicht mehr mit ausgeschnitten. **F2**: Carbon über dem Kopf nur ausgeblendet, wenn es näher als 42 cm an der Kamera liegt.
- **Tempo-Streifen** weiter außen und viel schwächer; Einblendung „Runde n: Zeit“/„Letzte Runde“ entfernt.
- Nachtrag: Ausnahme für die F1-Spiegelhalter im Cockpit-Ausschnitt nach innen und unten erweitert (y > 0,625, |x| > 0,215) – der Halter reicht bis in die Karosserie. Versuch mit Handschuh-Modell aus einer Vorlage (um den Griff geformt) auf Wunsch verworfen; es bleiben die bisherigen Hände.

## Version 1.28
- **Studio-Boden**: reines Schwarz (`MeshBasicMaterial`, unabhängig von Licht und Teamfarbe); das Spiegelbild der LED-Wand im Boden auf 10 % abgedunkelt – vorher färbte die Wand den Boden je Team (z. B. rot bei Haas).
- **Übergang aus dem Hauptmenü**: Wischer-Streifen entfernt; stattdessen kommt der Inhalt weich aus der Unschärfe nach vorn (`mzoom`), die obere Leiste gleitet ein (`mdrop`).
- **F1-Spiegel im Cockpit**: Halterblatt und sein Fuß stammen wieder vollständig aus dem Originalmodell (Ausnahme im Ausschnitt: z 0,742–0,868, y 0,646–0,712, |x| > 0,20); ein selbst modellierter Sockel wurde verworfen.
- **Cockpit-Kamera** 8 cm näher am Lenkrad (F1 z 0,30, F2 z 0,28).

