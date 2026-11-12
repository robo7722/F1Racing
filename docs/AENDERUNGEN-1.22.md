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
