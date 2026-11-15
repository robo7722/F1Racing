# Motor-Sounds: Wie realistisch? (Vergleich mit echter F1, F2 und Kart)

Stand: 15.11.2026 · Spielstand v1.96.
Zugehörig: [[SOUNDS]] (Erzeugung und Einbau), Code in `index.html` (`SND_ENG`, `sndEngine`, `updateAudio`, `gearInfo`).
Messung: Spektrum und Autokorrelation der Spiel-Loops in `sounds/*.wav` (Skript unten).

## Kurzfazit

| Klasse | Drehzahl-Bereich | Tonhöhe | Klang | Gesamt |
|---|---|---|---|---|
| **F1** | gut (4.000–11.600, 8 Gänge) | **zu tief** – immer 0,6 × echt (≈ 9 Halbtöne) | ordentlich, oben hell | mittel |
| **F2** | etwas zu hoch (bis ~9.450 statt 8.750), **8 statt 6 Gänge** | **Fehler:** hoher Loop eine **Oktave** zu hoch gestimmt, springt beim Überblenden | rau, passt | schwach |
| **Kart** | Höchstwert passt (14.000), aber Drehzahl hängt falsch an der Geschwindigkeit | **richtig** (1 × Zündfrequenz) | Zweitakt-Charakter gut | am besten |

Die Kart-Sounds sind am nächsten an der Realität. F1 klingt wie ein F1-Motor, der eine Stufe zu tief gestimmt ist. F2 hat einen echten Stimmungsfehler.

## Echte Referenzwerte

- **F1 2026:** 1,6-l-V6-Turbo, 3 Zündungen je Umdrehung, 8 Gänge. Regel-Grenze 15.000 U/min, der Benzinfluss bringt oberhalb von ~10.500 U/min kaum noch etwas. Im Rennen also etwa 10.500–12.000 U/min. **Zündfrequenz = U/min ÷ 20** → bei 11.600 U/min ≈ **580 Hz**. Ohne MGU-H, dafür MGU-K mit 350 kW.
- **F2 (Mecachrome V634T):** 3,4-l-V6-Turbo, ~620 PS bei **8.750 U/min = Begrenzer**, 570 Nm bei 6.000 U/min. Kein Hybrid. 6-Gang-Getriebe (Hewland). Zündfrequenz bei 8.750 U/min ≈ **437 Hz**. Lauter und rauer als F1.
- **Kart 125 ccm Zweitakt (X30/Rotax/OK, Direktantrieb):** 1 Zündung je Umdrehung, kein Getriebe, Fliehkraftkupplung. Begrenzer je nach Motor 14.000–16.000 U/min (Rotax ~13.800–14.400). Zündfrequenz bei 14.000 U/min ≈ **233 Hz**. Höchstgeschwindigkeit etwa 105–130 km/h. Drehzahl ist **proportional zur Geschwindigkeit** (nur eine Übersetzung). Sprint-Rennen meist mit **fliegendem Start**.

## Messung der Spiel-Loops

| Loop | im Code eingetragen | gemessen (stärkste Periode) | Klang-Schwerpunkt |
|---|---|---|---|
| f1_mittel | 230 Hz | 230 Hz ✓ | 950 Hz (eher dunkel) |
| f1_hoch | 260 Hz | 260 Hz ✓ | 1.970 Hz (hell) |
| f2_mittel | 255 Hz | 256 Hz ✓ | 660 Hz (sehr dunkel) |
| **f2_hoch** | **280 Hz** | **561 Hz** ✗ (Teilton 278 Hz fehlt, −43 dB) | 1.320 Hz |
| kart_mittel | 155 Hz | 156 Hz ✓ | 1.360 Hz |
| kart_hoch | 177 Hz | 176 Hz ✓ | 1.380 Hz |

`f2_hoch` hat ihre Energie bei 556 Hz und Vielfachen (1.113, 1.668, 2.223 Hz). Die 139-Hz-Grundperiode ist nur ein schwaches Untermuster. Wird der Loop als 280 Hz behandelt, klingt er doppelt so hoch wie gedacht.

## Tonhöhe im Spiel vs. echt

Formel im Spiel: `Ton = U/min ÷ 60 × Zylinderfaktor × tp` (F1/F2: tp = 0,6; Kart: tp = 1).

**F1** (echt = U/min ÷ 20)

| Drehzahl | Spiel | echt | Abweichung |
|---|---|---|---|
| 4.000 (Stand) | 120 Hz | 200 Hz | −9 Halbtöne |
| 7.000 | 210 Hz | 350 Hz | −9 Halbtöne |
| 11.600 (Schaltpunkt) | 348 Hz | 580 Hz | −9 Halbtöne |

→ Der Ablauf (Hochdrehen, Schalten, Abfall) stimmt, aber der Motor klingt wie ein echter F1 bei ~7.000 U/min, wenn er 11.600 dreht. Grund laut [[SOUNDS]]: Sonst müsste die Aufnahme bis 2,6-fach hochgestimmt werden und klänge dünn.

**F2** (Spiel-Drehzahl `4.500 + (gi.rpm − 4.000) / 9.200 × 6.000`)

| Drehzahl | Spiel | echt |
|---|---|---|
| 4.500 | 135 Hz (nur mittlerer Loop) | 225 Hz |
| 6.000 | 180 Hz | 300 Hz |
| 7.500 | **225 Hz und ~450 Hz gleichzeitig** (je 50 %) | 375 Hz |
| 9.000 | ~535 Hz (nur hoher Loop) | 450 Hz (über Begrenzer) |

→ Zwischen 6.000 und 9.000 U/min steigt der Ton um eine **zusätzliche Oktave**, in der Mitte klingen zwei Motoren im Oktavabstand. Oben ist F2 dann höher als F1 bei gleicher Drehzahl (F1 0,6 ×, F2 ~1,2 × echt).
Außerdem: F2 nutzt das F1-Getriebe mit 8 Gängen (echt 6) und dreht in den unteren Gängen bis ~9.450 U/min (echt Begrenzer 8.750).

**Kart** (Spiel-Drehzahl `6.500 + 7.500 × v / v_max`)

| Geschwindigkeit | Spiel | echt (Direktantrieb, ~14.000 bei Höchstgeschw.) |
|---|---|---|
| Stand | 6.500 U/min | ~2.500–3.000 (Leerlauf, Kupplung offen) |
| halbe v_max | 10.250 | ~7.000 |
| v_max | 14.000 ✓ | 14.000 |

→ Tonhöhe stimmt 1:1, aber die Drehzahl schwankt im Spiel nur zwischen ~10.000 und 14.000. Echt fällt sie in der Haarnadel auf 6.000–7.000 und schreit dann bis zum Begrenzer hoch, das typische „Brap-Brap-Kreischen“ fehlt dadurch teilweise.
Nebenbefund: v_max Kart = 0,5 × 95 m/s = **171 km/h**, echt 105–130 km/h.
Startampel: Im Spiel dreht das Kart im Stand bis 13.000 hoch. Mit Fliehkraftkupplung ginge das nicht (es würde losfahren). Echte Kart-Sprints starten fliegend.

## Weitere Punkte

- **Gegner-Autos:** synthetisch (Sägezahn + Rechteck), aber mit echter Zündfrequenz **ohne tp**. Bei gleicher Drehzahl klingt ein F1-Gegner ~9 Halbtöne höher als das eigene Auto. Doppler (0,65–1,5) ist plausibel.
- **Hochschalten:** Lautstärke fällt ~70 ms auf 35 %. Für F1 (nahtloses Getriebe) zu lang und zu tief, eher 20–30 ms und flacher. Für F2 passt eine deutliche Lücke besser.
- **Gas weg:** nur Tiefpass auf 1,5 kHz. Echt klingt Schub ganz anders: F1 Turbo-Abblasen und Ernten, F2 lautes Knallen/Ploppen (im Spiel synthetisch, ok), Kart Zweitakt-„Brabbeln“ (fehlt).
- **Tonhöhen-Verschiebung über `playbackRate`:** Verschiebt auch die Klangfarbe (Auspuff-Resonanzen wandern mit). Bei F1 0,55–1,57-fach hörbar („kleiner Motor“ oben, „Brummen“ unten). Rennspiele nutzen meist 6–12 Loops über die Drehzahl, getrennt nach Last und Schub.
- **ERS-Heulen / Turbo-Pfeifen:** synthetisch, als Spiel-Rückmeldung in Ordnung. 2026 gibt es keine MGU-H mehr, dafür eine stärkere MGU-K. Ein leiseres, dauerhaftes E-Heulen beim Beschleunigen wäre realistischer als nur beim Boost.

## Empfehlungen (nach Aufwand)

1. **F2-Fehler beheben (1 Zahl):** `SND_ENG.f2.hi[1]` von 280 auf **560** setzen. Dann liegt F2 durchgehend bei 0,6 × echt wie F1. Alternativ `tp` für F2 auf ~0,8 anheben.
2. **F2-Drehzahl** auf Begrenzer 8.750 begrenzen, eigenes 6-Gang-Getriebe.
3. **Gegner-Tonhöhe** an das eigene Auto angleichen (`tp` auch in `fn`).
4. **Kart-Drehzahl proportional** zur Geschwindigkeit (z. B. `max(Leerlauf, 14.000 × v / v_max_kart)`), Kart-Startdrehzahl begrenzen.
5. **F1 näher an echt:** `tp` schrittweise 0,6 → 0,75 testen, oder neue, höhere Loops erzeugen (Prompt mit „11,000 rpm, high-pitched“), damit kaum hochgestimmt werden muss.
6. **Mehr Loops:** je Klasse 3–4 Drehzahlstufen und eigene Schub-Loops (Gas weg).

## Mess-Skript (numpy)

```python
import wave, numpy as np
for n in ['f1_mittel','f1_hoch','f2_mittel','f2_hoch','kart_mittel','kart_hoch']:
    w = wave.open(f'sounds/{n}.wav'); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1/sr); X[(f < 60) | (f > 3000)] = 0
    y = np.fft.irfft(X, len(x))[:8192]; a = np.correlate(y, y, 'full')[8191:]; a /= a[0]
    lag = int(sr/2500) + np.argmax(a[int(sr/2500):int(sr/60)])
    print(n, f'stärkste Periode {sr/lag:.0f} Hz')
```

## Quellen
- [Mecachrome V634 (Wikipedia)](https://en.wikipedia.org/wiki/Mecachrome_V634_engine) – 620 PS bei 8.750 U/min, Begrenzer 8.750
- [Motorsport Magazine: F1 2026 Motoren](https://www.motorsportmagazine.com/articles/single-seaters/f1/all-the-key-aspects-changing-on-f1s-2026-engines) – max. 15.000 U/min
- [Motorsport.com: 2026-Motoren](https://www.motorsport.com/f1/news/opportunities-and-headaches-2026-engine-plans/6681770/) – Benzinfluss-Optimum unter 10.500 U/min
- [IAME X30 Junior](https://iame.ae/en/engines/x30-junior) – Begrenzer 16.000 U/min
- [Rotax 125 Max Handbuch](https://www.manualslib.com/manual/1070178/Rotax-125-Max.html?page=58) – Leistung fällt ab ~13.800 U/min
- [Flowracers: X30 Höchstgeschwindigkeit](https://flowracers.com/blog/iame-x30-speed/) – 105–121 km/h
