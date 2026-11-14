# Motor- und Crash-Sounds (ElevenLabs)

Stand: 14.11.2026 – in Arbeit.
Zugehörig: Sound-Code in `index.html` (Abschnitt „Sound“: `SND_ENG`, `SND_CRASH`, `sndEngine`, `bump`).

## Vorher
Alles synthetisch (Web Audio). Motor: 4 Oszillatoren + Rauschen, Verzerrer und Tiefpass, je Klasse andere Obertöne (F1 V6, F2 rauer V6, Kart Zweitakt-Einzylinder). Crash: Sinus-Schlag + gefiltertes Rauschen, bei Wand metallisches Schaben.

## Erzeugung (ElevenLabs Sound Effects, Modell `eleven_text_to_sound_v2`)
Arbeitsfläche: „F1Racing – Motor- und Crash-Sounds“ (https://elevenlabs.io/app/flows/HT7EhoAnO7SkpsQ7zz3c).
- Kostenloser Tarif: nur **eine Erzeugung gleichzeitig**; öfter „busy“ → nacheinander erzeugen. Kosten ~13 Credits je 4-s-Sound (Schätzung vorher 66).
- Prompt-Treue 0,6. Motoren mit `loop: true` (nahtlos) und 4 s Länge, Crashs 1,5–3 s.

| Datei | Prompt (Kurz) | Länge | Status |
|---|---|---|---|
| `sounds/f1_mittel.mp3` | F1 V6 Turbo-Hybrid, konstant 7000 U/min, Onboard | 4 s Loop | fertig, Grundton gemessen **230 Hz** |
| `sounds/f1_hoch.mp3` | F1 V6, konstant 11500 U/min Vollgas | 4 s Loop | 1. Versuch steigt 770→1100 Hz (kein konstanter Ton) → verworfen, neu erzeugen |
| `sounds/f2_mittel.mp3` | F2 3,4-l-V6-Turbo, rau, 6000 U/min | 4 s Loop | fertig, Grundton ~**248 Hz** (schwankt 230–260) |
| `sounds/f2_hoch.mp3` | F2 V6, 9500 U/min Vollgas | 4 s Loop | offen |
| `sounds/kart_mittel.mp3` | 125-ccm-Zweitakt-Kart, mittlere Drehzahl | 4 s Loop | offen |
| `sounds/kart_hoch.mp3` | Kart, hohe Drehzahl | 4 s Loop | offen |
| `sounds/crash_auto.mp3` | Auto trifft Auto, Carbon kracht, Teile fliegen | 2 s | offen |
| `sounds/crash_wand.mp3` | Aufprall Stahl-Leitplanke + kurzes Schaben | 2,5 s | offen |
| `sounds/crash_schwer.mp3` | schwerer Einschlag Betonmauer, Teile splittern | 3 s | offen |
| `sounds/crash_kart.mp3` | Kart rempelt Kart, Plastik + Rahmen | 1,5 s | offen |

## Einbau (index.html)
- `SND_ENG[klasse] = { cyl, vol, lo: [datei, grundton], hi: [...] }` – Grundton = gemessene Zündfrequenz der Aufnahme (Hz). Grundton 0 = Aufnahme nicht verwenden.
- `sndEngine`: beide Loops laufen gleichzeitig; Tonhöhe `playbackRate = Zündfrequenz / Grundton` (Zündfrequenz = Drehzahl/60 · 3 beim V6, · 1 beim Zweitakter), Überblendung gleich laut (cos/sin) über die Frequenz (logarithmisch). Gas weg → Tiefpass 1,5 kHz, Vollgas offen; Schaltruck kurz leiser.
- Läuft eine Aufnahme, schweigt der synthetische Motor; Turbo-Pfeifen, ERS-Heulen und Fehlzündungen bleiben synthetisch. Fremde Autos (Doppler) bleiben vorerst synthetisch.
- Crash (`bump`): Kart → `crash_kart`, Wand → `crash_wand` (sehr hart: `crash_schwer`), Auto-Auto → `crash_auto` (sehr hart: `crash_schwer`); Tonhöhe zufällig ±8 %, Lautstärke nach Stärke, durch den vorhandenen Begrenzer.
- Fehlt eine Datei oder lädt sie nicht → synthetischer Klang wie bisher.
- Diagnose: `window.__snd(true)` startet Audio und zeigt geladene Dateien und die aktive Motor-Aufnahme.

## Messung der Aufnahmen
Grundton per Autokorrelation (Bandpass 60–2000 Hz, mehrere Fenster) und harmonischer Summe; Pegel je 0,25 s; Sprung an der Loop-Naht.
