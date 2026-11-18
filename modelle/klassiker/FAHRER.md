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

Einordnung fürs Spiel: Lotus = viel Leistung pro Gewicht, aber kaum Grip und Abtrieb (rutschig, lange Bremswege);
McLaren = stark beschleunigend, mittlerer Grip; Ferrari = schnellstes Auto, viel Grip und Abtrieb, kürzeste Bremswege.

## Quellen
- Wikipedia: Lotus 49, McLaren MP4/4, Ferrari F2004, Jochen Rindt
- Ferrari: ferrari.com/en-EN/formula1/f2004 (Leistung, Gewicht, Getriebe)
- Honda: global.honda/en/F1/machine/1988_McLarenHondaMP44 (Leistung)
- McLaren: „The story behind Ayrton Senna's helmet“ (Helmdesign)
- FIA Formula 3: „The story behind Schumacher's helmet design“, cmhelmets.com (Schumacher-Helm)
- Autosport Nostalgia Forum (Rindts Helm 1970 – nur Forenberichte)
