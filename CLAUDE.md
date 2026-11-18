# Arbeitsregeln für Claude

- **Sprache:** Immer Deutsch – auch kurze Zwischenmeldungen während der Arbeit, Statusnotizen und Rückfragen. Code-Kommentare und Commit-Nachrichten ebenfalls Deutsch.
- **Git:** Fertige Änderungen immer auch direkt auf `main` pushen (Anweisung vom 15.11.2026), zusätzlich zum Arbeits-Branch der Sitzung. Kein Pull Request nötig. Vorher `origin/main` holen und ggf. mergen; bei gleicher Versionsnummer aus einer parallelen Sitzung die Version erhöhen.
- **Notizen:** Vor jeder Antwort in `docs/` nachsehen, ob es schon Notizen gibt. Erarbeitete Skripte, Analysen und Ideen als Notiz im passenden Ordner unter `docs/` (bzw. `tools/`) speichern.
- **Design-Fragen:** Bei allem, was Aussehen/UI/Gestaltung betrifft, zuerst einen Entwurf (Bild) zur Abnahme schicken und erst nach dem ausdrücklichen Go des Nutzers einbauen (Anweisung vom 18.11.2026). Reine Fehlerbehebungen ohne Gestaltungsfrage sind davon nicht betroffen.
- **ElevenLabs-Credits (kostet echtes Geld):**
  - Vor JEDER Erzeugung den Kontostand prüfen und dem Nutzer die geschätzten Kosten nennen; bei mehr als ~200 Credits vorher fragen.
  - Bevorzugt über die Arbeitsfläche (Flows) erzeugen, vorher `estimate_only`. Die direkte API (`POST /v1/sound-generation`, `tools/sounds/erzeugen.py`) kostet ≈ 100 Credits je Sekunde Ton (≈ 30× teurer) – nur mit `--budget` (Skript bricht sonst ab).
  - Nach jedem Lauf den tatsächlichen Verbrauch nachmessen und nur gemessene Zahlen nennen (Schätzungen als solche kennzeichnen).
  - Vorfall 15.11.2026: ~22.300 Credits in einer Sitzung über die API verbraucht, weil der Preis nicht geprüft wurde (siehe docs/SOUNDS.md, v2.03).
