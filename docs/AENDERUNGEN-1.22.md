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
