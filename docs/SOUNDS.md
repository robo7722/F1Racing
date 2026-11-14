# Motor- und Crash-Sounds (ElevenLabs) – v1.95/v1.96

Stand: 14.11.2026.
Zugehörig: Sound-Code in `index.html` (Abschnitt „Sound“: `SND_ENG`, `SND_CRASH`, `sndEngine`, `bump`), Aufbereitung `tools/sounds/aufbereiten.py`.

## Vorher
Alles synthetisch (Web Audio).
- **Motor:** 4 Oszillatoren und Rauschen, Verzerrer und Tiefpass, je Klasse andere Obertöne (F1 V6, F2 rauer V6, Kart Zweitakt-Einzylinder).
- **Crash:** Sinus-Schlag und gefiltertes Rauschen, bei Wandkontakt metallisches Schaben.

Der Synthesizer bleibt als Rückfall, falls eine Datei fehlt oder nicht lädt. Fremde Autos (Doppler-Effekt) bleiben synthetisch.

## Erzeugung (ElevenLabs Sound Effects, `eleven_text_to_sound_v2`)
Arbeitsfläche: „F1Racing – Motor- und Crash-Sounds“ (https://elevenlabs.io/app/flows/HT7EhoAnO7SkpsQ7zz3c).
- **Kostenloser Tarif:** Es läuft nur **eine Erzeugung gleichzeitig**, und oft meldet ElevenLabs „busy“. Deshalb einzeln nacheinander erzeugen. Abgewiesene Versuche werden nicht berechnet.
- **Kosten:** etwa 13 Credits je 4-s-Loop, 5–10 je Crash. Die Vorab-Schätzung war deutlich höher (66). Insgesamt etwa 120 Credits.
- **Einstellungen:** Motoren mit `loop: true` und 4 s Länge, Prompt-Treue 0,6. Für die hohen Drehzahlen im zweiten Versuch 0,85 mit „sustained constant … steady unchanging drone, no revving, no acceleration, no gear change“. Ohne diese Zusätze drehten die Aufnahmen im Clip hoch.
- Originale liegen in `sounds/roh/`, die Spiel-Dateien in `sounds/`.

| Sound | Prompt (Kurz) | Ergebnis | Spiel-Datei |
|---|---|---|---|
| F1 mittel | F1 V6 Turbo-Hybrid, konstant 7000 U/min, Onboard | konstant, Grundton **230 Hz** | `f1_mittel.wav` (2,95 s) |
| F1 hoch | F1 V6, konstante hohe Drehzahl, Dauerton | 1. Versuch drehte hoch (770→1100 Hz), verworfen. 2. Versuch konstant **260 Hz**, heller | `f1_hoch.wav` (2,95 s) |
| F2 mittel | F2 3,4-l-V6-Turbo, rau, 6000 U/min | schwankt 230–264 Hz, Abschnitt 1,0–2,75 s ≈ **255 Hz** | `f2_mittel.wav` (1,5 s) |
| F2 hoch | F2 V6, konstante hohe Drehzahl, Dauerton | 1. Versuch unbrauchbar. 2. Versuch steigt 513→573 Hz, Abschnitt 1,25–3,3 s (Grundperiode 139 Hz, als **280 Hz** gestimmt) | `f2_hoch.wav` (1,8 s) |
| Kart mittel | 125-ccm-Zweitakt-Kart, mittlere Drehzahl | konstant **155 Hz** | `kart_mittel.wav` (2,25 s) |
| Kart hoch | Kart, hohe Drehzahl Vollgas | konstant **177 Hz**, nur wenig höher als mittel | `kart_hoch.wav` (2,6 s) |
| Crash Auto | Auto trifft Auto, Carbon kracht, Teile fliegen | 2 s | `crash_auto.mp3` |
| Crash Wand | Aufprall Stahl-Leitplanke + Schaben | 2,5 s, Hauptschlag nach ~0,3 s | `crash_wand.mp3` |
| Crash schwer | schwerer Einschlag Betonmauer, Teile splittern | 3 s | `crash_schwer.mp3` |
| Crash Kart | Kart rempelt Kart, Plastik + Rahmen | 1,5 s | `crash_kart.mp3` |

## Aufbereitung (`tools/sounds/aufbereiten.py`)
- **Motor-Loops:**
  - stabilen Abschnitt ausschneiden,
  - Übergang Ende→Anfang gleich laut überblenden (0,25 s; Sprung an der Naht danach ≤ 0,04),
  - gleiche Lautheit (RMS 0,14),
  - als **WAV** speichern (mono, 32 kHz, 16 bit). MP3 fügt am Anfang Stille ein, das würde beim Loopen alle 3 s knacken.
  - Das Skript misst den Grundton des fertigen Loops und gibt ihn aus. Der Wert gehört in `SND_ENG`.
- **Crashs:**
  - leiser Vorlauf bis zum Einsatz abgeschnitten (Auto 81 ms, schwer 139 ms, Kart 41 ms), sonst kam der Schlag verspätet,
  - Spitze auf −1 dBFS, MP3 128 kbit/s.

## Einbau (index.html)
- `SND_ENG[klasse] = { cyl, tp, vol, x: [rpmA, rpmB], lo: [datei, grundton], hi: [...] }`.
- **Tonhöhe:** Beide Loops werden auf dieselbe Zieltonhöhe gestimmt: `Zündfrequenz (U/min/60 · cyl) · tp`. `tp` ist bei F1/F2 0,6, sonst müsste die Aufnahme bis auf das 2,6-Fache hochgestimmt werden und klänge dünn. Beim Kart ist `tp` 1.
  - Tempo der Aufnahme (`playbackRate`) etwa: F1 0,55 (Stand) bis 1,57 (12.000 U/min), F2 bis 1,24, Kart bis 1,5.
- **Klangfarbe:** Nach Drehzahl gleich laut überblendet (Kosinus/Sinus, weicher Übergang). F1 7000→10500, F2 6000→9000, Kart 8000→12000 U/min. Da beide Loops gleich gestimmt sind, gibt es beim Überblenden kein Schweben.
- **Gas:** Gas weg schließt den Tiefpass auf 1,5 kHz, Vollgas öffnet bis 12 kHz. Beim Schalten wird es kurz leiser.
- Läuft eine Aufnahme, schweigt der synthetische Motor. Turbo-Pfeifen, ERS-Heulen und Fehlzündungen bleiben synthetisch.
- **Crash (`bump`):**
  - Kart → `crash_kart`,
  - Wand → `crash_wand` (Stärke > 0,85 → `crash_schwer`),
  - Auto-Auto → `crash_auto` (> 0,9 → `crash_schwer`),
  - Tonhöhe zufällig ±8 %, Lautstärke nach Stärke, durch den vorhandenen Begrenzer.
- Die Service-Worker-Liste (`sw.js`) enthält alle Dateien, sie funktionieren also auch offline.
- **Diagnose:** `window.__snd(true)` startet das Audio und zeigt geladene Dateien, aktive Loops (Tempo und Anteil), Drehzahl und Pegel.

## Prüfung
- Browser-Test Kart, F2, F1: Alle 10 Dateien laden. Beide Loops laufen, in der Startaufstellung nur der mittlere. Keine Seitenfehler.
- `__bumpTest` (offline gerendert): Auto 0,5 → Spitze 0,26, 0,6 s. Wand 0,6 → 0,33, 1,5 s. Stärke 1 → 0,74 (Begrenzer), schwerer Einschlag.

## v1.96 – Crash-Sounds neu (Rückmeldung: „klingen grauenvoll und falsch“)
**Ursachen:**
1. **Auslösung:** Schon jedes leichte Antippen (Auto-Auto ab 0,6 m/s Geschwindigkeitsänderung, Wand ab 3 m/s) spielte einen kompletten 2–3-s-Unfall mit splitterndem Carbon. Beim Aneinanderreiben kam er alle 0,35 s neu und lief übereinander.
2. **Aufnahmen (Spektrogramm):**
   - „schwer“ war 1,3 s Breitbandrauschen auf vollem Pegel (wie eine Rausch-Explosion),
   - „Wand“ ein Doppelschlag (Vorschlag und Hauptschlag nach 0,3 s),
   - „Kart“ mehrere Klapper-Schläge.

**Neu erzeugt** (Prompt-Treue 0,75, je „single … impact, short decay, no explosion, no engine“):

| Datei | Prompt (Kurz) | Länge im Spiel |
|---|---|---|
| `crash_leicht.wav` (neu) | leichte Berührung, ein kurzer dumpfer Carbon-Klopfer | 0,17 s (nur der erste von zwei Klopfern) |
| `crash_auto.wav` | einzelner harter Seitentreffer, Carbon-Knacken + dumpfer Schlag | 0,6 s |
| `crash_wand.wav` | einzelner Aufprall an der Streckenbegrenzung, schwerer Schlag + Carbon-Knirschen | 0,9 s |
| `crash_schwer.wav` | heftiger Einschlag in die Reifenmauer, Teile brechen ab und schlittern | 1,3 s |
| `crash_kart.wav` | Kart rempelt Kart, ein hohler Plastik-Klopfer + kleines Metall-Klirren | 0,45 s |

**Aufbereitung:**
- Crashs jetzt auch als **WAV**. Neu kodiertes MP3 hatte ~25 ms Stille vorn.
- Vorlauf abgeschnitten, auf Höchstlänge gekürzt (60 ms ausgeblendet).
- Pegel nach dem 99,9-%-Wert des verwendeten Stücks.

**Auslösung (`bump`):**
- **Art nach Stärke:** < 0,5 leicht, sonst Auto bzw. Wand, > 0,9 (Wand > 0,85) schwer. Kart: immer Kart.
- **Nachklang nach Stärke gekürzt:** 0,12 s + Länge · (0,3 + 0,7 · Stärke).
- **Kein Übereinander:** Ein laufender Crash wird nur von einem mindestens 30 % stärkeren abgelöst (der alte blendet in 20 ms aus).
- Aufnahmen gehen direkt auf den Ausgang. Die Vorausschau des Begrenzers drückte kurze Schläge („leicht“ auf etwa ein Fünftel).

**Messung (`__bumpTest`, offline):**

| Treffer | Spitze | Dauer |
|---|---|---|
| leicht 0,3 | 0,30 | 80 ms |
| Auto 0,6 | 0,54 | 0,2 s |
| Wand 0,6 | 0,62 | 0,45 s |
| schwer (Stärke 1) | 0,8 | 0,75 s |

## Offen / Ideen
- Fremde Autos ebenfalls mit Aufnahmen (mit Doppler über `playbackRate`).
- Eigene Aufnahmen für Gas weg / Schub (Knallen, Blubbern) und Leerlauf in der Box.
- Kart hoch ist kaum höher als Kart mittel. Bei Bedarf neu erzeugen („very high-pitched“).
