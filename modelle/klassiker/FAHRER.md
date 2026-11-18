# Klassiker – Fahrer und Daten für den Einbau

Je Auto ein Fahrer: der bekannteste. Das Spiel führt Fahrer als `[Kürzel, Name, Nummer, Team, Helmfarbe]`
und Helme in `HELM_DESIGN[Kürzel] = [Farbe 1, Farbe 2, Farbe 3, Muster, Visier]` (Muster 0–6 beim Einbau passend wählen).

## Lotus 49C (1970) – Jochen Rindt
- Österreicher (geboren 18.04.1942 in Mainz, gestorben 05.09.1970 in Monza).
- Startnummer **3** – so ist das Modell lackiert (Gold Leaf Team Lotus, Sieg in Monaco 1970 im 49C).
- 1970: 5 Siege (Monaco im 49C; Niederlande, Frankreich, Großbritannien, Deutschland im Lotus 72), Weltmeister nach seinem Tod.
- Helm: **unsicher**. Nach Forenberichten ab Hockenheim 1970 ein rein weißer Vollvisierhelm (Bell Star), davor meist offener Helm;
  auch von Silber ist die Rede. Vorschlag: weiß mit dunklem Visier, ohne Muster.
- Vorschlag Spiel: `['RIN', 'Jochen Rindt', 3, <Lotus-Team>, 0xf2f2f2]`

## McLaren MP4/4 (1988) – Ayrton Senna
- Brasilianer (geboren 21.03.1960 in São Paulo, gestorben 01.05.1994 in Imola).
- Startnummer **12** – so ist das Modell lackiert (Marlboro McLaren Honda).
- 1988: 8 Siege, 13 Pole-Positions, erster WM-Titel. McLaren gewann 15 von 16 Rennen.
- Helm (gut belegt): gelber Grund, ein grüner Streifen oben und ein blauer darunter, beide gehen auf Augenhöhe vom Visier aus nach hinten
  (Design von Sid Mosca, Farben der brasilianischen Flagge).
- Vorschlag Spiel: `['SEN', 'Ayrton Senna', 12, <McLaren-Team>, 0xf5d000]`, `HELM_DESIGN.SEN = [0xf5d000, 0x149a3c, 0x1a3fa8, <Streifen>, 0x101418]`

## Ferrari F2004 (2004) – Michael Schumacher
- Deutscher (geboren 03.01.1969 in Hürth).
- Startnummer **1** (Weltmeister 2003).
- 2004: 13 Siege (damals Rekord), siebter und letzter WM-Titel.
- Helm (Schuberth RF1): Ferrari-Rot, durch weiße Linien in Felder geteilt, oben die Sterne (im Lauf der Jahre blau, später rot),
  hinten die deutschen Farben Schwarz-Rot-Gold. In Monza 2004 eine Sonderausgabe in Grün-Weiß-Rot.
- Vorschlag Spiel: `['MSC', 'Michael Schumacher', 1, <Ferrari-Team>, 0xd40000]`, `HELM_DESIGN.MSC = [0xd40000, 0xf2f2f2, 0x1a1a1a, <Felder>, 0x101418]`

## Ferrari 312 (1967) – Chris Amon
- Neuseeländer (geboren 20.07.1943 in Bulls, gestorben 03.08.2016 in Rotorua).
- Startnummer **20** – so ist das Modell lackiert („AMON 20“, Monaco 1967). Deshalb Amon und nicht Lorenzo Bandini (in Monaco 1967 tödlich verunglückt).
- 1967: Dritter in Monaco, Belgien, Großbritannien und Deutschland, WM-Fünfter. Gilt als bester Fahrer ohne GP-Sieg.
- Helm: **unsicher**. Auf dem Referenzfoto (`tools/klassiker/quellen/sitz/ferrari_312_1967.jpg`) ein offener, weißer Helm mit Brille, keine Streifen zu
  erkennen. Ein Leserkommentar (primotipo.com) nennt blaue und rote Ränder (blau rechts, rot links), ähnlich dem Helm im Film „Grand Prix“ (1966) –
  nicht belegt. Im Spiel: weiß ohne Muster, dunkles Visier (das Spiel hat nur geschlossene Helme; offener Helm mit Brille wäre eine eigene Form).
- Spiel: `['AMO', 'Chris Amon', 20, 'H_F67', …]`, `HELM_DESIGN.AMO = [0xf2f2f2, 0xf2f2f2, 0xf2f2f2, 0, 0x2a2622]`

## McLaren MP4/13 (1998) – Mika Häkkinen
- Finne (geboren 28.09.1968 in Vantaa).
- Startnummer **8** – so ist das Modell lackiert (West McLaren Mercedes, silbern/schwarz).
- 1998: 8 Siege, 9 Pole-Positions, erster WM-Titel (zweiter 1999). McLaren Konstrukteursweltmeister.
- Helm (gut belegt): weißer Grund mit blauen Streifen (meist als drei Blautöne von hell nach dunkel beschrieben), Farben noch aus seiner Kartzeit;
  dunkles Visier. Bottas trug 2018 in Monaco eine Hommage daran. Im Spiel: weiß mit zwei blauen Streifen (Muster 6, dunkel- und hellblau).
- Spiel: `['HAK', 'Mika Häkkinen', 8, 'H_MCL98', …]`, `HELM_DESIGN.HAK = [0xf2f2f2, 0x13306e, 0x3f8fd8, 6, 0x101418]`

## Red Bull RB8 (2012) – Sebastian Vettel
- Deutscher (geboren 03.07.1987 in Heppenheim).
- Startnummer **1** (Weltmeister 2011) – so ist das Modell lackiert (Startnummer 1, „S. VETTEL“).
- 2012: 5 Siege, dritter WM-Titel in Folge (mit 3 Punkten vor Alonso).
- Helm: **wechselnd** – Vettel trug fast in jedem Rennen ein anderes Design (Singapur 2012 mit Leuchtdioden, Suzuka japanisch, Austin in Holzoptik,
  in Monza 2012 sein 50. Design). Grundlage war meist ein Red-Bull-Design aus blauen und silbernen Feldern nach der Dose. Im Spiel als Mittelwert:
  weiß mit dunkelblauem Hinterteil und rotem Streifen (Muster 2) – kein bestimmtes Rennen.
- Spiel: `['VET', 'Sebastian Vettel', 1, 'H_RBR', …]`, `HELM_DESIGN.VET = [0xf2f2f2, 0x1b2a6b, 0xd8102c, 2, 0x101418]`

## Technische Daten (für die Fahrphysik)
| | Lotus 49C | McLaren MP4/4 | Ferrari F2004 |
|---|---|---|---|
| Motor | Ford Cosworth DFV, 3,0 l V8, Sauger | Honda RA168E, 1,5 l V6 Turbo (2,5 bar) | Ferrari 053, 3,0 l V10, Sauger |
| Leistung | ca. 430 PS bei 9 000–10 000/min | ca. 675–685 PS bei 12 300–12 500/min | 865 PS bei 18 300/min (Ferrari-Angabe) |
| Gewicht | ca. 500 kg | ca. 540 kg | 605 kg mit Fahrer und Flüssigkeiten |
| Getriebe | Hewland, 5 Gänge, H-Schaltung | 6 Gänge, H-Schaltung | 7 Gänge, sequenziell, Schaltwippen |
| Reifen | Firestone | Goodyear | Bridgestone |
| Abtrieb | kleine Flügel, kaum Abtrieb | wenig (Turbo-Ära, flacher Wagen) | sehr viel (V10-Ära, Spitzenwert) |
| Höchstgeschwindigkeit | keine verlässliche Angabe | ca. 333 km/h in Hockenheim (eine Messung) | keine offizielle Angabe (Quellen 338 bis über 370 km/h) |

| | Ferrari 312 (1967) | McLaren MP4/13 (1998) | Red Bull RB8 (2012) |
|---|---|---|---|
| Motor | Ferrari V12, 3,0 l, Sauger | Mercedes-Benz FO110G, 3,0 l V10, Sauger | Renault RS27, 2,4 l V8, Sauger + KERS |
| Leistung | ca. 390 PS bei ca. 10 500–11 000/min | ca. 780 PS bei ca. 17 000–17 500/min | ca. 750 PS bei 18 000/min (Begrenzung), KERS + ca. 80 PS für 6,7 s je Runde |
| Gewicht | ca. 550 kg | 600 kg (Mindestgewicht mit Fahrer) | 640 kg (Mindestgewicht mit Fahrer) |
| Getriebe | 5 Gänge, H-Schaltung | 6 Gänge, sequenziell | 7 Gänge, sequenziell, Schaltwippen |
| Reifen | Firestone | Bridgestone (Rillenreifen, ab 1998 Pflicht) | Pirelli |
| Radstand (Modell) | 2,47 m | 3,02 m | 3,43 m |

Einordnung fürs Spiel: Lotus = viel Leistung pro Gewicht, aber kaum Grip und Abtrieb (rutschig, lange Bremswege);
McLaren = stark beschleunigend, mittlerer Grip; Ferrari = schnellstes Auto, viel Grip und Abtrieb, kürzeste Bremswege.

## Quellen
- Wikipedia: Lotus 49, McLaren MP4/4, Ferrari F2004, Jochen Rindt
- Ferrari: ferrari.com/en-EN/formula1/f2004 (Leistung, Gewicht, Getriebe)
- Honda: global.honda/en/F1/machine/1988_McLarenHondaMP44 (Leistung)
- McLaren: „The story behind Ayrton Senna's helmet“ (Helmdesign)
- FIA Formula 3: „The story behind Schumacher's helmet design“, cmhelmets.com (Schumacher-Helm)
- Autosport Nostalgia Forum (Rindts Helm 1970 – nur Forenberichte)
- Wikipedia: Chris Amon, Ferrari 312, McLaren MP4/13, Red Bull RB8 · primotipo.com (Leserkommentar zu Amons Helm, unbelegt)
- Autosport / Eurosport 2018 („Bottas to use Hakkinen helmet colours in Monaco“), cmhelmets.com (Häkkinen-Helm)
- Motor Sport Magazine („The designer behind Sebastian Vettel's Formula 1 crash helmets“), RaceFans („Sebastian Vettel's F1 career in helmets“)
