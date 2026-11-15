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
- Realismus-Vergleich mit echter F1/F2/Kart (u. a. F2-Stimmungsfehler im hohen Loop): siehe [[SOUNDS-REALISMUS]].

## v1.99 – Motoren in echter Tonhöhe (Umsetzung von [[SOUNDS-REALISMUS]])
Stand: 15.11.2026.

**Ausgangslage:** F1/F2 klangen 0,6 × echt (≈ 9 Halbtöne zu tief), der hohe F2-Loop war eine Oktave falsch eingetragen (280 statt ~560 Hz), Gegner klangen höher als das eigene Auto, F2 nutzte das F1-Getriebe, die Kart-Drehzahl hing nicht proportional an der Geschwindigkeit.

**Credits:** ElevenLabs (kostenloser Tarif) hatte nur noch 39 Credits. Zwei neue Aufnahmen à 17 Credits (Schätzung sagte 100), Rest ~5. Neue Drehzahlstufen deshalb **offline** erzeugt.

**Neue Dateien:**
- `tools/sounds/varianten.py`: Tonhöhen-Varianten mit Rubberband (`ffmpeg -af rubberband=…:formant=preserved`), Formanten bleiben → kein „Spielzeugmotor“. Naht: Loop 3× hintereinander, mittleres Drittel, 0,12 s überblendet.
- Rohaufnahmen „Gas weg“: `sounds/roh/kart_schub.mp3` (1 s, Zweitakt-Brabbeln), `sounds/roh/v6_schub.mp3` (3 s, V6 Knallen/Blubbern, Drehzahl fällt; verwendet 0–1,3 s, +8 Halbtöne).

| Klasse | Loops (Grundton ≈ U/min) | Schub |
|---|---|---|
| F1 | f1_mittel 230 (4.600) · f1_v2 344 (6.900) · f1_v3 438 (8.750) · f1_v4 552 (11.000) | v6_schub 390, leise (2026: Ernten beim Lupfen) |
| F2 | f2_mittel 255 (5.100) · f2_v2 342 (6.850) · f2_v3 444 (8.900) | v6_schub 390, laut |
| Kart | kart_v0 78 (4.700) · kart_v1 104 (6.250) · kart_mittel 156 (9.350) · kart_v3 224 (13.400) | kart_schub 152 |

`f1_hoch`, `f2_hoch`, `kart_hoch` sind nur noch Quellen für die Varianten (nicht mehr im Spiel/Service-Worker).

**Einbau (`index.html`):**
- `SND_ENG[klasse] = { cyl, vol, cut: [Dauer, Pegel], loops: [[Datei, Grundton], …], schub: [Datei, Grundton, Lautstärke] }`. `tp` entfällt: Zielton = **echte Zündfrequenz** (V6 U/min ÷ 20, Kart U/min ÷ 60).
- Überblendung zwischen den zwei Stufen, die den Zielton einschließen (logarithmisch, Kosinus/Sinus). Tempo je Stufe ~0,8–1,25.
- Motor-Aufnahmen starten erst, wenn **alle** Stufen einer Klasse geladen sind (sonst bleibt der Synthesizer).
- **Gas weg:** Anteil = `(0,45 − Gas)/0,35` × Drehzahl über Schwelle (F1 6.500, F2 5.500, Kart 7.000). Beim Lupfen an zufälliger Stelle neu gestartet. Läuft am Tiefpass vorbei, Hauptmotor dabei −35 %.
- **Schalten:** F1 25 ms auf 65 % (nahtlos), F2 60 ms auf 35 % (Zündunterbrechung), Runterschalten 60 % davon.
- **F2-Getriebe:** `RATIO_F2 = [245, 195, 160, 134, 113, 96]`, Hochschalten bei 8.600, Begrenzer 8.750. `gearInfo(kmh, f2)` liefert jetzt auch `n` (Ganganzahl); die Halo-Anzeige zeigt N–6 bei F2.
- **Kart:** Drehzahl = 14.000 × v/v_max (max. 15.500), darunter Fliehkraftkupplung (Leerlauf 2.800, mit Gas ~5.000). Am Start nur Gasstöße bis ~4.500.
- **Gegner:** Aufnahme statt Sägezahn (F1 f1_v3, F2 f2_v2, Kart kart_mittel), Doppler über `playbackRate`, gleiche Drehzahl-Logik wie das eigene Auto, weiter weg dumpfer. Synthetisch nur noch als Rückfall.
- **F1 MGU-K:** leises Heulen auch beim normalen Beschleunigen (Gas > 50 %), beim Boost wie bisher kräftig.
- **Diagnose:** `__snd()` zeigt zusätzlich km/h, Gang, Phase, Schub-Anteil und das Tempo der Gegner-Aufnahmen.

## v2.00 – Roadster, neue Einschläge, Fahr-Geräusche (alles ElevenLabs)
Stand: 15.11.2026. Konto jetzt im Starter-Tarif (~30.000 Credits/Monat).

**Erzeugung:** neu direkt über die API (`tools/sounds/erzeugen.py`, `POST /v1/sound-generation`, Schlüssel kommt über den Proxy) statt über die Arbeitsfläche – dort bremste das Gleichzeitigkeits-Limit, und das Herunterladen ließ sich nicht skripten. 27 Sounds × 2 Varianten, ~330 Credits (Schätzung der Arbeitsfläche: 984). Rohdateien in `sounds/roh/v2/`. Ein Lauf über die Arbeitsfläche (gleiche Prompts, ~330 Credits) ist ungenutzt.
**Auswahl/Aufbereitung:** `tools/sounds/aufbereiten_v2.py` wählt je Paar automatisch: Loops nach gleichmäßigster Lautheit, Einschläge nach „genau ein Hauptschlag, steiler Einsatz“. Gewählte Varianten stehen in `sounds/roh/v2/auswahl.json`.

### Roadster (MX-5 ND2, 2,0-l-Vierzylinder, Sportauspuff)
- Vorher synthetisch und fälschlich als Reihensechszylinder (3 Zündungen je Umdrehung). Jetzt **2 Zündungen je Umdrehung** (U/min ÷ 30), Begrenzer ~7.500.
- Die KI trifft die verlangte Drehzahl nicht – deshalb Tonhöhe gemessen und Lücken mit Rubberband-Varianten gefüllt:

| Datei | Quelle | Grundton | ≈ U/min |
|---|---|---|---|
| mx5_leer | „850 rpm“ (Variante 1, Pulsieren 27,3 Hz) | 27,3 | 820 |
| mx5_v1 | Leerlauf +8 HT | 43,3 | 1.300 |
| mx5_v2 | „3000 rpm“ −12 HT | 66,5 | 2.000 |
| mx5_v3 | „3000 rpm“ −6 HT | 94 | 2.800 |
| mx5_3000 | „3000 rpm“ (klingt wie 4.000) | 133 | 4.000 |
| mx5_5000 | „5000 rpm“ Variante 2 | 203 | 6.100 |
| mx5_7000 | „7000 rpm“ Variante 1, 0,1–1,8 s | 273 | 8.200 |
| mx5_schub | Gas weg, Blubbern/Knallen | 137 | 4.100 |

- Schalten: Handschaltung mit Kupplung → Lücke 0,16 s auf 30 %.
- Gegner-Roadster nutzen `mx5_5000` (Doppler).

### Einschläge (`SND_CRASH[art][ziel]`)
- Art: `cf` (F1/F2, Carbon), `stahl` (Roadster), `kart`. Ziel: `leicht` (< 0,45), `auto`, `armco` (Leitplanke), `beton` (Mauer, nach `TH.wallKind`), `schwer` (> 0,9 bzw. Wand > 0,85).
- Kart: Rempler `kart_kart`, Bande `kart_wand`, schwer `reifenstapel`.
- **Unfälle anderer** in bis zu 80 m Entfernung sind jetzt hörbar (leiser nach Abstand, höchstens alle 0,6 s).

### Fahr-Geräusche (`SND_FX`, `fxTick`)
| Geräusch | wann | Lautstärke / Tempo |
|---|---|---|
| kies | Untergrund Kies | mit Tempo (bis 25 m/s), Tempo 0,85–1,15 |
| rasen | Untergrund Rasen | mit Tempo |
| kerb | auf Randsteinen | Rattern wird mit dem Tempo schneller (0,55–1,9) |
| kies_einschlag | Wechsel von Asphalt auf Kies/Rasen > 12 m/s | einmalig |
| quietschen_slick / _strasse | Quer-Haftung > 88 % ausgenutzt oder Rutschen nach Kontakt, nur auf Asphalt | F1/F2 0,35, Kart 0,3, Roadster (Straßenreifen) 0,45 |
| schaben_metall / _beton | Kontakt mit Leitplanke bzw. Mauer | mit Tempo |
| schaben_auto | Autos berühren sich | mit Tempo |
| wind | immer | ∝ Tempo², offenes Cockpit |

- Neue Signale aus der Fahrphysik: `c.latUse` (Ausnutzung der Quer-Haftung), `pl.wallT` (Bandenkontakt), `pl.rubT` (Autokontakt).
- Alte Crash-Dateien (`crash_*.wav`) entfernt.
- **Diagnose:** `__snd()` zeigt zusätzlich `surf` und aktive Fahr-Geräusche (`fx`). Testschalter `window.__surfTest = 'gravel'` erzwingt einen Untergrund.

## v2.01 – Rückmeldung: MX-5 unrealistisch, Crashs übertrieben, Quietschen im Pulk, „Wellen“ bei hohem Tempo
Stand: 15.11.2026.

- **Schwere Crashs entfernt** (`cf_schwer`, `stahl_schwer`, `reifenstapel`): starke Treffer nutzen dieselbe Aufnahme wie normale (Auto/Leitplanke/Mauer), nur länger. Höchstlautstärke starker Treffer gesenkt (0,35 + 0,45 · Stärke statt 0,65).
- **MX-5 neu:** 20 neue Aufnahmen (je 4 Varianten, Prompt „In-car onboard audio … club race car on a race track …“, ~250 Credits). Befund: Die KI trifft die verlangte Drehzahl nicht (fast alles 160–280 Hz) und dreht im Clip leicht hoch/runter (bis ±7 %). Das alte Set (7 Stufen aus verschiedenen Clips, bis ±12 HT verschoben) klang deshalb wie mehrere Autos.
  - Jetzt nur 4 Loops eines Stils: `mx5n_leer` (Leerlauf), `mx5n_tief2` (116 Hz ≈ 3.500 U/min, −7 HT), `mx5n_tief` (174 Hz ≈ 5.200), `mx5n_hoch` (228 Hz ≈ 6.850, −3 HT), dazu `mx5n_schub`.
  - **Tonhöhe geglättet** (`tools/sounds/glaetten.py`): Tonhöhe alle 32 ms messen und die Aufnahme mit veränderlichem Tempo so abspielen, dass sie konstant ist (Schwankung vorher 4–7 %, nachher < 1 %). Sonst springt die Tonhöhe an der Loop-Naht zurück (künstliches Auf und Ab alle 2–3 s).
  - Hörprobe alt/neu (Leerlauf → Start → Hochschalten → Gas weg) wird mit einem Skript gerechnet, das die Überblendung des Spiels nachbildet.
- **Quietschen neben anderen Autos:** Der Loop „Reiben Auto an Auto“ (`schaben_auto`) bestand fast nur aus Reifenquietschen und lief bei jeder leichten Berührung im Pulk → entfernt. Reifenquietschen nur noch an der Haftgrenze (> 90 %), nicht mehr nach Kontakten.
- **„Wellen“ bei hohem Tempo** – drei Ursachen behoben:
  1. Motor-Überblendung: zwei Aufnahmen gleicher Tonhöhe dauerhaft gemischt (z. B. F1 bei 10.000–11.000 U/min) schweben gegeneinander. Jetzt wird nur im mittleren Viertel des Abstands zweier Stufen überblendet, sonst läuft genau eine.
  2. Gegner: die 4 nächsten Autos spielten dieselbe Aufnahme fast gleich hoch (Flanger-Effekt). Jetzt abwechselnd zwei verschiedene Aufnahmen, Lautstärke 0,2 statt 0,3.
  3. Fahr-Geräusch-Loops schwollen an und ab (Rasen bis 12-fach, Quietschen/Kies 2,5-fach). `tools/sounds/pegel.py` gleicht den Pegel aus (zyklischer gleitender RMS 300 ms, Teilen durch Hüllkurve^0,9) → langsame Schwankung ≤ 2,2-fach. Wind zusätzlich leiser (0,12 statt 0,3).
- Reihenfolge der Skripte: `erzeugen.py` → `aufbereiten_v2.py` → `pegel.py`.
