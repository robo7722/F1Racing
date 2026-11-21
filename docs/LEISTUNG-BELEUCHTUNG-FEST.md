# Würde feste statt dynamischer Beleuchtung die Leistung verbessern?

Frage vom 21.11.2026 (Stand v2.94). Kurzantwort: **kaum** – die Beleuchtung ist bereits fast vollständig fest.

## Was heute schon fest ist

- **Lichtquellen:** Im Rennen gibt es nur drei Lichter (`hemi`, `sun`, `flood`, `index.html` ~Zeile 2362). Farbe und Stärke werden
  einmal je Strecke gesetzt (~Zeile 10581), nicht je Bild. Das Flutlicht ist bei Tagstrecken abgeschaltet (`flood.visible = false`),
  es rechnet also immer nur **ein** gerichtetes Licht + Himmelslicht je Pixel.
- **Schatten der Welt** (Tribünen, Bäume, Gebäude): gebacken (`bakeShadows`), kein `castShadow`.
- **Umgebungsspiegelung:** einmal je Strecke erzeugt (PMREM), nicht laufend.
- Keine Punkt- oder Strahlerlichter im Rennen (Strahler gibt es nur im Schauraum/Menü). Lichtkegel und Lichthöfe der Nachtstrecken
  sind bemalte Flächen, keine echten Lichter.

## Was noch dynamisch ist

Nur die **Echtzeitschatten der Autos**: eine Schattenkarte 1024×1024 (Ultra 2048), jedes Bild neu gezeichnet.

- Kosten des Schattendurchgangs laut `LEISTUNG-ANLEITUNG.md` (seit v2.67, Schattenfiguren): an der Startaufstellung Miami
  21 Zeichenaufrufe / 88 Tsd. Dreiecke; ein Klassiker 8–10 Aufrufe / 9–13 Tsd. Dreiecke. Zum Vergleich das ganze Bild: 200–300 Aufrufe,
  0,6–1,2 Mio. Dreiecke.
- Dazu kommt das Abtasten der Schattenkarte (PCF) für jeden Pixel der schattenempfangenden Flächen (Fahrbahn, eigenes Auto).
- In der Grafikstufe „Niedrig“ sind diese Schatten schon ganz abgeschaltet (`renderer.shadowMap.enabled = hi`).

## Einschätzung (Schätzung, nicht gemessen)

Autoschatten durch einen festen dunklen Fleck unter dem Auto zu ersetzen spart den Schattendurchgang und das Abtasten –
grob im Bereich weniger Prozent der Bildzeit, in der Startaufstellung etwas mehr. Dafür verlieren die Autos sichtbar an Bodenhaftung
im Bild (Design-Frage → erst Entwurf zur Abnahme).

Ein eigener Messlauf am 21.11. (`qc/probe.py monza --race --script qc/perf-cam.js`) lieferte in der Cloud-Umgebung kein Ergebnis
(Software-Renderer, Streckenbau allein ~180 s, danach Zeitlimit). Die Zahlen oben stammen aus den vorhandenen Notizen.

## Wo die Leistung tatsächlich hingeht

Laut den Leistungsrunden (v1.83–1.90, v2.64–2.67): Pixelzahl × Vollbild-Durchgänge (Auflösung, Bloom, Bild-Shader), Zeichenaufrufe
und Dreiecke der Welt, und einzelne wiederkehrende Hänger (Textur-Hochladen, Shader-Nachladen). Dort lohnt sich Suchen eher als beim Licht.

## Möglicher nächster Schritt

Testschalter „Autoschatten aus“ im Debug-Menü, um den Unterschied auf dem echten Handy bei sonst gleicher Grafikstufe zu messen
(Bildzeiten vorher/nachher). Erst wenn das dort spürbar ist, lohnt ein Entwurf für feste Schattenflecken.
