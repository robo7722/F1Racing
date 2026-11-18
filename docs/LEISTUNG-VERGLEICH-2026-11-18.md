# Leistungsvergleich v2.72 (18.11. vormittags) gegen v2.82 (18.11. nachmittags)

Frage: „Ist die Performance schlechter als heute Morgen?“ Dazwischen kamen vor allem die echten Lack-Texturen (v2.73–v2.75),
das Halo in Lackfarbe (v2.77), die Klassiker-Aufkleberbögen (v2.78–v2.80) und das Start-Minispiel (v2.80/2.81).

Messung mit `qc/perf-vergleich.js` (Playwright, Handy-Emulation 960×432, Touch, Grafik Standard, Monza, volles Feld, KI fährt;
je Kamera 6 Stellen der Runde). Renderzeit läuft in SwiftShader (Software) und ist nur grob vergleichbar (±5 %).

## F1 (Monza)

| | v2.72 | v2.82 |
|---|---|---|
| Zeichenaufrufe Verfolger / Cockpit / TV | 187 / 216 / 216 | 186 / 218 / 218 |
| Dreiecke (Tsd.) Verfolger / Cockpit / TV | 630 / 621 / 618 | 621 / 625 / 622 |
| Hochgeladener Texturspeicher | 278 MB (197 Texturen) | 269 MB (172 Texturen) |
| Shader-Programme | 147 | 147 |
| Renderzeit SwiftShader (ms) | 1606 / 1850 / 1544 | 1655 / 1973 / 1570 |

## F2 (Monza)

| | v2.72 | v2.82 |
|---|---|---|
| Zeichenaufrufe | 186 / 216 / 216 | 187 / 216 / 216 |
| Dreiecke (Tsd.) | 797 / 776 / 773 | 800 / 779 / 777 |
| Texturspeicher | 271 MB (189) | 271 MB (169) |
| Shader | 148 | 148 |

(F2-Läufe liefen parallel, daher Renderzeiten hier nicht verwertbar.)

## Ergebnis

- Kein messbarer Rückschritt: gleiche Zeichenaufrufe, gleiche Dreiecke, gleicher (eher etwas weniger) Texturspeicher, gleiche Shader-Zahl.
- Die gebackene Lack-Textur ersetzt Aufkleberbogen + Logo: auf Touch-Geräten 10 Gegner-Texturen 1018×1020 (halbe Auflösung) + eigene in voll
  statt vorher 27 Bögen 1024×512 + 512×512 – unterm Strich gleich viel Speicher.
- Start-Minispiel: nur ein paar Vergleiche je Bild, keine Rolle.

## Nicht abgedeckt / mögliche Ursachen für ein gefühlt schlechteres Spiel

- **Erster Start nach einem Update**: Der Service Worker lädt alle Dateien neu, der Browser übersetzt die Shader neu → das erste Rennen nach einer neuen Version ruckelt/lädt länger.
- **Klassiker-Autos** (Lotus, McLaren, Ferrari) und Nicht-Monza-Strecken wurden nicht gemessen.
- **Echtes Handy**: Wärme (gedrosselte CPU/GPU nach längerem Spielen), Akku-Sparmodus. SwiftShader zeigt keine GPU-Bandbreite – die Lack-Texturen werden mit Anisotropie 8 abgetastet; falls ein Handy darauf empfindlich ist, wäre `anisotropy = 4` für Gegner ein Versuch.

Vergleich wiederholen: alten Stand mit `git worktree add <ordner> <commit>` auschecken, je Stand `python3 -m http.server <port>`, dann
`node qc/perf-vergleich.js <port> Monza f1`.

## Nachtrag: Vergleich mit gestern (v2.63, 16.11. 01:40 – am 17.11. gab es keine Änderungen)

F1 Monza, Läufe nacheinander (nicht parallel):

| | v2.63 (gestern) | v2.82 (jetzt) | v2.82 ohne Lack-Texturen (`?nobake`) |
|---|---|---|---|
| Zeichenaufrufe Verfolger / Cockpit / TV | 198 / 237 / 236 | 186 / 218 / 218 | 188 / 216 / 216 |
| Dreiecke (Tsd.) | 639 / 667 / 661 | 624 / 629 / 626 | 629 / 621 / 617 |
| Texturspeicher | 278 MB | 270 MB | 278 MB |
| Shader | 155 | 147 | 147 |
| Renderzeit SwiftShader (ms) | 1538 / 1863 / 1516 | 1632–1661 / 1929–1941 / 1542–1570 | 1647 / 1918 / 1543 |

- Gegenüber gestern **weniger** Arbeit für die Grafikkarte: −6 % (Verfolger) bis −8 % (Cockpit/TV) Zeichenaufrufe, −6 % Dreiecke im Cockpit/TV,
  8 Shader weniger (Leistungsrunde v2.64–v2.67 heute früh).
- Die Software-Renderzeit liegt ~2–6 % höher. Mit und ohne Lack-Texturen gleich → **nicht** die Texturen. Größenordnung im Rauschen von SwiftShader;
  auf einem echten Handy nicht überprüft.
