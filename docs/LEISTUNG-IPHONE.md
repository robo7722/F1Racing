# Warum läuft das Spiel auf dem iPhone 16 schlecht? (Analyse, 26.11.2026, Stand v3.03)

Frage: „Das Spiel läuft auf iPhone 16 schlecht, warum? Liegt das an Safari?“
**Nur Code- und Notizanalyse – auf einem echten iPhone wurde nichts gemessen.** Alle bisherigen Leistungsrunden
(`LEISTUNG-ANLEITUNG.md`, `LEISTUNG-VERGLEICH-2026-11-18.md`) liefen im Testbrowser (Software-Grafik) bzw. auf Android (Adreno 840).

## Kurzantwort

Teilweise ja. Am Chip liegt es nicht (A18 ist schneller als die Android-Geräte, auf die abgestimmt wurde). Auf dem iPhone
läuft **jeder** Browser mit Apples WebKit-Engine – Chrome oder Firefox auf dem iPhone ändern also nichts. WebKit hat für
WebGL ein paar Eigenheiten, die genau dieses Spiel treffen:

1. **Zeichenaufrufe sind teurer.** Safari übersetzt WebGL über ANGLE nach Metal; jeder Aufruf kostet mehr CPU als in Chrome auf Android.
   Das Spiel hat 200–420 Aufrufe je Bild (Grenze in der Anleitung: 450, abgestimmt auf Android).
2. **Arbeitsspeicher-Grenze je Tab.** iOS beendet oder lädt Tabs bei Speicherdruck neu bzw. verliert den WebGL-Kontext.
   Gemessen ~270 MB Texturspeicher (v2.82), dazu 4,8 MB `index.html` und Modelle/Texturen (~80 MB Dateien).
3. **Shader-Übersetzung ist langsam** und wird nicht so gut zwischengespeichert wie in Chrome → längeres Laden, Hänger beim ersten Rennen nach einem Update.
4. **Stromsparmodus** (gelbe Batterie) begrenzt Safari auf **30 Bilder/s** – sieht aus wie „läuft schlecht“.
5. **Erwärmung:** Nach einigen Minuten drosselt das iPhone CPU/GPU spürbar.
6. **Bildschirmrate:** iPhone 16 (ohne Pro) hat nur 60 Hz – mehr als 60 Bilder/s gehen nicht.

## Was im Code für iPhones gilt (geprüft)

- Standard-Grafikstufe `gfx: 'high'` („Schön“) auch auf Handys (`index.html` ~Z. 1796).
- Renderauflösung „Schön“: Pixelbudget 1,1 MP, max. 1,75× (`basePR`, ~Z. 2783). iPhone 16 quer (852×393 CSS-px) → ca. 1490×690 ≈ 1,03 MP – angemessen.
- Nachbearbeitung mit HalfFloat-Puffer + 2× MSAA auf Touch-Geräten (~Z. 2759) – jedes Bild ein Vollbild-Durchgang.
- `powerPreference: 'high-performance'` wird von Safari ignoriert.
- Dynamische Auflösung wurde entfernt (~Z. 13966) – es gibt keine automatische Absenkung, wenn das Gerät warm wird.
- `isIOS` wird nur für Neigungssteuerung und den Hinweis „Zum Home-Bildschirm“ benutzt – **keine iPhone-eigenen Leistungseinstellungen**.

## Nächste Schritte (Vorschläge)

1. Auf dem iPhone prüfen: Stromsparmodus aus? Grafik auf „Schnell“ stellen – wird es deutlich besser, ist es die GPU/Pixelarbeit, sonst CPU/Aufrufe/Speicher.
2. Einstellungen → Extras → Debug-Menü: echte Bildzeiten und Ruckler-Protokoll auf dem iPhone ablesen (Strecke, Kamera notieren).
3. Klären, was „schlecht“ heißt: gleichmäßig niedrige Bildrate, regelmäßiges Ruckeln, Hänger beim Start, Neuladen/Absturz oder Erwärmung.
4. Mögliche Änderungen danach (erst nach Messung): iOS-Voreinstellung „Schnell“ oder eigenes Pixelbudget, Texturen für iOS verkleinern,
   Grenze für Aufrufe auf iOS niedriger ansetzen.

Siehe auch [[LEISTUNG-ANLEITUNG]], [[LEISTUNG-VERGLEICH-2026-11-18]].
