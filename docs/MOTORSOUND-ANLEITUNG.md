# Anleitung: Motorsound aus einer echten Aufnahme zusammensetzen

Stand: 15.11.2026 · Vorlage: **Roadster (MX-5) im F1Racing-Spiel, Version 2.14** – vom Nutzer als „passt“ abgenommen (Hörprobe `16_MX5_v2.14`).
Gedacht als Vorlage für weitere Spiele (z. B. das Rally-Spiel). Alles hier ist Web Audio (Browser), lässt sich aber auf jede Audio-Engine übertragen.
Ausführliche Entstehungsgeschichte und Messwerte: [[SOUNDS]] (Abschnitte v2.06–v2.14).

---

## 1. Das Prinzip in einem Satz

Ein Motorgeräusch im Spiel muss jederzeit der **aktuellen Drehzahl und dem Gas** folgen – eine Aufnahme läuft aber fest ab. Deshalb wird **eine echte Aufnahme zerlegt** und je nach Fahrzustand aus **fünf Schichten** neu zusammengesetzt:

| Schicht | Drehzahl / Zustand | Woraus | Technik |
|---|---|---|---|
| **1 Leerlauf** | ~850 U/min, Stand | echter Leerlauf-Abschnitt (3 s) | Schleife, Tonhöhe folgt der Drehzahl |
| **2 Gasstöße im Stand** | Gas antippen im Stand | 3 echte Gasstöße (850 → 5.200 → 850) | ganze Aufnahme abspielen, Schleifen schweigen |
| **3 Anfahren / unterer Bereich** | 1.000 – 4.400 U/min | ein echter Durchzug (gleichmäßige Beschleunigung) | **Granular**: kurze Körner von der passenden Stelle |
| **4 Fahren / oberer Bereich** | ab ~4.000 U/min | echte Abschnitte mit **konstanter** Drehzahl (5.200, 6.900) | Drehzahl-Stufen-Schleifen, überblendet |
| **5 Gas weg** | Gas < 45 %, Drehzahl hoch | „Schub“-Loop (Blubbern/Knallen) | Schleife, dazu Tiefpass auf dem Motor |

Wichtig: **Jede Schicht deckt einen Bereich ab, in dem die anderen schweigen.** Gleichzeitig laufen zwei Schichten nur in kurzen, gleich laut überblendeten Übergängen.

---

## 2. Ausgangsmaterial

### Was man braucht (Idealfall: eigenes Auto aufnehmen)
- **Leerlauf**, 20 s, ruhig.
- **Gasstöße im Stand**, 5–10 Stück, einzeln mit Pause dazwischen.
- **Durchzug**: im 3. Gang mit Vollgas gleichmäßig von ~1.200 bis zum Begrenzer, **ohne Schalten**, Mikrofon fest (Innenraum oder Auspuff, nicht vorbeifahrend).
- **Konstante Drehzahlen** unter Last: je 5–10 s bei ~3.000 / 4.500 / 6.000 / Begrenzer.
- **Gas weg**: von hoher Drehzahl Gas weg und ausrollen lassen.
- Möglichst unkomprimiert (WAV), ein Mikrofon pro Durchgang, keine Musik/Sprache.

### Was wir hatten (MX-5)
Keine eigene Aufnahme, sondern **Wikimedia Commons**: „Mazda MX-5 Miata – engine and exhaust sound“, Ride in Japan (YouTube), **Lizenz CC BY 3.0** → Namensnennung im Spiel (Einstellungen → Extras → Credits). 9 min, MX-5 NA 1,6 l.
- Suche: Commons-API `list=search`, `srsearch=<Auto> filetype:audio`, `srnamespace=6`; Lizenz über `prop=imageinfo&iiprop=extmetadata` prüfen (`LicenseShortName`). Freesound braucht einen API-Schlüssel.
- **Nur freie Lizenzen** (CC0, CC BY, CC BY-SA) verwenden und die Quelle angeben.

### KI-Sounds (ElevenLabs) – für Motoren nicht empfehlenswert
- Treffen die verlangte Drehzahl nicht (fast alles landet bei 160–280 Hz), drehen innerhalb des Clips hoch/runter, klingen synthetisch. Für Einschläge, Kies, Wind brauchbar.
- **Kosten**: Arbeitsfläche ≈ 3–4 Credits/s, direkte API ≈ 100 Credits/s (!). Vorher Kontostand prüfen (siehe `CLAUDE.md`).

---

## 3. Analyse der Aufnahme

Alles in `tools/sounds/mx5_echt.py` (Python + numpy + ffmpeg mit Rubberband).

**Drehzahl messen:** Zündfrequenz = U/min ÷ 60 × Zündungen je Umdrehung
(Viertakt-Vierzylinder: **2** → U/min ÷ 30 · V6: 3 · V8: 4 · Sechszylinder: 3 · Zweitakt-Einzylinder: 1).
Gemessen mit Autokorrelation auf dem Bereich 20–600 Hz (Fenster 2.048 Samples, alle 25–100 ms).

Gesucht wird nach drei Arten von Abschnitten:

| Art | Kriterium | MX-5-Ergebnis |
|---|---|---|
| **konstante Drehzahl** | ≥ 1,5 s, Schwankung < 2,5 %, gute Periodizität (r > 0,45) | Leerlauf 132,8 s (28,4 Hz), 5.200 U/min bei 481,5 s |
| **Durchzug** | Drehzahl steigt monoton um mindestens Faktor 2, keine Sprünge (< 8 %), **Pegel konstant** | **469,3–473,0 s: 1.207 → 6.115 U/min** |
| **Gasstoß** | Pegel springt auf > 4 × Leerlauf, davor und danach Leerlauf, < 3 s | 19,95 s · 25,55 s · 28,35 s |

**Fallen bei der Auswahl:**
- **Pegel steigt stark (×16)** → Vorbeifahrt an der Kamera, nicht verwendbar (Doppler, Entfernung).
- **Heller und lauter bei niedriger Drehzahl** → Fahrt unter Last im hohen Gang („gequält“), klingt bei Gasstößen falsch. Beispiel: 1.070-U/min-Abschnitt, Klangschwerpunkt 780 Hz statt ~450 Hz.
- **Durchzug hängt/stockt** (Drehzahl bleibt kurz stehen) oder endet zu früh → oben unbrauchbar.

---

## 4. Aufbereitung (Dateien erzeugen)

| Schritt | Wie | Warum |
|---|---|---|
| **Tonhöhe glätten** (Schleifen) | Tonhöhe alle 32 ms messen, glätten, Aufnahme mit veränderlichem Tempo abspielen, sodass sie konstant ist (`tools/sounds/glaetten.py`) | sonst springt die Tonhöhe an der Loop-Naht zurück → künstliches Auf und Ab alle 2–3 s |
| **Nahtloser Loop** | Ende mit dem Anfang 0,2–0,25 s gleich laut (Sinus/Kosinus) überblenden | kein Knacken |
| **Lautheit** | jede Schleife auf RMS 0,14 | gleich laute Stufen |
| **Stufe verschieben** (nur wenn nötig) | Rubberband `pitch=…:formant=preserved`, **höchstens ±5 Halbtöne** | Formanten bleiben → kein Spielzeug-Klang. Größere Sprünge klingen künstlich |
| **Gasstöße angleichen** | Pegel über dem Leerlauf mit Exponent 0,45 zusammendrücken (echte Dynamik ~26× → ~5×), Leerlauf-Anteil auf RMS der Leerlauf-Schleife, 0,25 s ausblenden | sonst fällt der Pegel beim Wechsel Gasstoß ↔ Schleife auf ein Zehntel („abgehackt“) |
| **Durchzug** | ausschneiden, 10 ms einblenden, Lautheit bei ~2.000 U/min auf RMS 0,14; **Drehzahl-Tabelle** `[Sekunde im Durchzug, U/min]` alle 0,1 s (Median über ±0,1 s, monoton gemacht) | Grundlage der Granular-Wiedergabe |
| **Format** | WAV, mono, 32 kHz, 16 bit | MP3 fügt am Anfang Stille ein → Loop knackt |

MX-5-Dateien (`sounds/`): `mx5e_leer` (28,4 Hz) · `mx5e_durchzug` + Tabelle · `mx5e_5200` (172,8 Hz) · `mx5e_6900` (= 5.200er +5 HT, 230,5 Hz) · `mx5e_blip1..3` · `mx5n_schub`.

---

## 5. Einbau (Web Audio)

### Signalweg
```
Schleifen (Leerlauf, Stufen) ─┐
Granular-Körner ──────────────┼─► Tiefpass (1.500 + Gas·10.500 Hz) ─► Motor-Lautstärke ─► Ausgang
Schub-Loop ──────────────────────────────────────────────────────────► (direkt, ungefiltert)
Gasstöße ────────────────────────────────────────────────────────────► (direkt)
```

### Konfiguration (MX-5, `SND_ENG.road` in `index.html`)
```js
{ cyl: 2, vol: 0.6, cut: [0.16, 0.3],                                   // 2 Zündungen/Umdrehung, Schaltlücke 0,16 s auf 30 %
  loops: [['sounds/mx5e_leer.wav', 28.4, [0.4, 0.4]],                    // [Datei, Grundton Hz, Überblend-Fenster zur nächsten Stufe]
          ['sounds/mx5e_5200.wav', 172.8, [0.3, 0.4]],
          ['sounds/mx5e_6900.wav', 230.5]],
  schub: ['sounds/mx5n_schub.wav', 253.3, 0.3],                          // [Datei, Grundton, Lautstärke]
  blips: ['sounds/mx5e_blip1.wav', 'sounds/mx5e_blip2.wav', 'sounds/mx5e_blip3.wav'],
  gran: { von: 950, bis: 1500, aus: [3900, 4400],                         // Granular ein (950→1.500) und aus (3.900→4.400)
          quellen: [{ file: 'sounds/mx5e_durchzug.wav', tab: [[0.032,1207], …, [3.632,6114]] }] } }
```

### Regeln (mit den Werten, die passen)
1. **Tonhöhe = echte Zündfrequenz.** Tempo jeder Schleife = `U/min / 60 × cyl / Grundton`, begrenzt auf 0,4–2,2. Im Betrieb sollte eine Stufe nur **0,8–1,25-fach** laufen – sonst klingt sie künstlich.
2. **Überblenden immer gleich laut** (Kosinus/Sinus), nie linear (linear sackt in der Mitte ab). Position im **logarithmischen** Abstand zweier Grundtöne; Fenster `[Beginn, Breite]` als Anteil dieses Abstands, darin Smoothstep.
   - Unten (Anfahren) breit, oben schmal: wo die Drehzahl **lange konstant** bleibt, schweben zwei gemischte Aufnahmen („Wellen“).
3. **Granular** (`granTick`): alle **33 ms** ein Korn von **100 ms**, Hann-Fenster ÷ 1,5 (3-fach überlappt = konstante Lautstärke).
   - Startstelle = Stelle im Durchzug, deren Drehzahl (Tabelle) zur aktuellen passt.
   - **Phasenrichtig**: neues Korn beginnt bei „Fortsetzung des vorigen Korns + ganze Zündabstände“, möglichst nah an der Zielstelle (Suche ±60 ms). Sonst löschen sich überlappende Körner aus oder schweben.
   - Über dem Ende des Durchzugs höchstens **1,04-fach** höher spielen (mehr = „viel zu hoch“).
   - Planung im Voraus (`next < t + 0.07`), Körner per `setValueCurveAtTime` gefenstert.
4. **Gasstöße im Stand**: Auslösen, wenn Fahrzeug steht (< 1 m/s), Gas über 45 % steigt und vorher unter 40 % war (an der Ampel steigt der Wert weich an, kein Sprung). Zufällig eine von drei Aufnahmen, Tempo 0,96–1,04. Solange er läuft: Schleifen stumm. 0,3 s vor dem Ende ausblenden (Zeitkonstante 0,08), Schleifen blenden gleichzeitig ein. Gas nach der Spitze gehalten (> 0,6 s) → Gasstoß ausblenden, Schleifen übernehmen.
5. **Lautstärke**: Motor = `vol × (0,5 + 0,5 × Gas)`; **Gasgeben blendet weich ein** (Zeitkonstante 0,14 s ≈ 0,4 s), Gas weg schnell (0,04 s). Schaltlücke: 0,16 s auf 30 % (Handschaltung; F1 nahtlos: 25 ms auf 65 %).
6. **Gas weg**: Schub-Loop-Anteil `(0,45 − Gas)/0,35 × (Drehzahl − 3.200)/2.000`, bei jedem Lupfen an zufälliger Stelle neu starten; Motor dabei −35 %, Tiefpass schließt auf 1,5 kHz.
7. **Drehzahl im Spiel** realistisch halten: Schaltpunkt und Begrenzer passend zum aufgenommenen Motor; Drehzahl wird mit 0,35 je Bild nachgeführt.
8. **Gegner**: eine Stufe aus der Mitte, Doppler über das Tempo; Nachbar-Stimmen abwechselnd aus **verschiedenen** Aufnahmen (gleiche Aufnahme mehrfach = Flanger).

### Bausteine im Code (`index.html`, Abschnitt Sound)
`SND_ENG` (Konfiguration) · `sndEngine()` (Schleifen, Überblendung, Granular-Gewicht, Schub, Gasstöße, Lautstärke) · `granTick()` (Körner) · `updateAudio()` (Drehzahl, Gang, Schaltlücke) · `__snd()` (Diagnose im Browser: Drehzahl, aktive Schleifen mit Tempo/Anteil, Gasstoß, Schub).

---

## 6. Prüfen ohne das Spiel: Hörprobe rechnen

`tools/sounds/hoerprobe_mx5.py` bildet die Spiel-Logik (Schleifen, Granular, Gasstöße, Lautstärken) in Python nach und rechnet einen festen Ablauf als MP3:

| Sekunde | Ablauf |
|---|---|
| 0–2,5 | Leerlauf |
| 2,5–4,8 / 5,4–8,0 | zwei Gasstöße |
| 9,2–11,6 | Anfahren mit Vollgas 850 → 6.000 |
| 11,6–11,8 | Schalten |
| 11,8–13,4 | Vollgas 4.500 → 6.200 |
| 13,4–16,7 | Gas weg, Leerlauf |

`python tools/sounds/hoerprobe_mx5.py ausgabe.mp3` – gibt zusätzlich den Pegel je 0,1 s aus: **Sprünge oder Löcher an Übergängen** sieht man dort, bevor man sie hört.

**Arbeitsweise, die funktioniert hat:** Hörprobe mit **Zeittabelle** an den Hörer geben → Rückmeldung „Sekunde X–Y klingt falsch“ → **nur diese Stelle** ändern, alles andere einfrieren. Hörproben nummerieren und aufheben, damit man zu einem guten Stand zurück kann.

---

## 7. Was nicht funktioniert hat (nicht wiederholen)

| Versuch | Ergebnis |
|---|---|
| KI-Aufnahmen als Motor (ElevenLabs) | falsche Drehzahl, Wandern im Clip, synthetisch |
| 7 Stufen aus verschiedenen Clips, bis ±12 HT verschoben | „klingt wie mehrere Autos“ |
| Gasstöße aus schnell hoch-/runtergezogenen Schleifen | „Sirene“, synthetisch |
| Anfahren aus 4 Stufen konstanter Drehzahl | „abgehackte Übergänge“ |
| Zwei verschiedene Aufnahmen dauerhaft gemischt | Schweben („Wellen“), „zwei Motoren“ |
| Über das Ende der Aufnahme bis 1,3-fach hochstimmen | „viel zu hoch“ |
| Abfall nach Gasstoß zeitlich strecken | „klingt schlimmer“ |
| Granular-Körner im Abstand eines ganzen Arbeitszyklus + zweiter Durchzug | nicht besser, verworfen |
| Pegel-Ausblenden doppelt (Datei + Spiel) | Loch beim Wechsel |
| Wind-/Untergrund-Loops mit Pegelschwankungen | „wellig“ – Pegel glätten oder berechnetes Rauschen |

---

## 8. Übertragen auf das Rally-Spiel – Checkliste

1. **Motor festlegen**: Zylinder/Takt (→ Zündungen je Umdrehung), Leerlauf, Begrenzer, Getriebe (Gänge, Schaltart: sequentiell = kurze Lücke ~50 ms, H-Schaltung = 0,15–0,2 s).
2. **Aufnahme besorgen** (eigene oder freie Lizenz): Leerlauf, Gasstöße, ein **sauberer Durchzug** über den ganzen Bereich, konstante hohe Drehzahl, Gas weg. Bordaufnahme, keine Vorbeifahrt.
3. **Analysieren** (Abschnitt 3) und mit `mx5_echt.py` als Vorlage ausschneiden/aufbereiten (Abschnitt 4).
4. **Schichten einrichten** wie in Abschnitt 1/5. Reicht der Durchzug bis zum Begrenzer, kann Granular den **ganzen** Bereich übernehmen (dann entfallen die oberen Stufen).
5. **Rally-typisch zusätzlich bedenken**: häufige Lastwechsel auf Schotter (Schub-Loop wichtiger), Anti-Lag/Fehlzündungen bei Turbo-Rallyautos (eigene Knall-Aufnahmen als Einzelgeräusche), Untergrund-Geräusche (Schotter, Asphalt, Schnee) als eigene, im Pegel geglättete Loops – nicht lauter als der Motor (Motor ≈ RMS 0,08, Untergrund ≈ 0,04).
6. **Hörprobe rechnen**, Pegel an Übergängen prüfen, mit Zeittabelle abnehmen lassen.
7. **Credits/Lizenzen**: Quelle im Spiel nennen, KI-Kosten vorher prüfen.
