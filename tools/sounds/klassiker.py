"""Motor-Loops der Klassiker (v2.69) aufbereiten – Rohdateien sounds/roh/klassiker/<auto>_<stufe>_<k>.mp3 (ElevenLabs-Arbeitsfläche,
Flow „F1Racing – Motor- und Crash-Sounds“, je 2 Varianten à 4 s, siehe docs/SOUNDS.md und docs/KLASSIKER.md).

Je Stufe wird die Variante mit der gleichmäßigsten Lautheit und Tonhöhe gewählt, der ruhigste 3,2-s-Abschnitt nahtlos geloopt und auf RMS 0,14 gebracht.
Grundton: gemessen; die KI trifft die verlangte Drehzahl nicht genau, deshalb wird er auf die Oktave gelegt, die der verlangten Zündfrequenz am nächsten ist
(Zündfrequenz = U/min ÷ 60 × Zylinder/2) – so läuft die Aufnahme bei der verlangten Drehzahl etwa mit Tempo 1. Ausgabe: sounds/hist_<auto>_<stufe>.wav
und die Werte für SND_ENG in index.html.
Aufruf: python tools/sounds/klassiker.py
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from varianten import load, save, pitch, SR, SND
from aufbereiten_v2 import best_window, loopify, norm_rms, pitches

ROH = os.path.join(SND, 'roh', 'klassiker')
AUTO = {'lot': (8, {'mittel': 7000, 'hoch': 9800, 'schub': 7000}), 'mcl': (6, {'mittel': 8500, 'hoch': 12000, 'schub': 8000}), 'fer': (10, {'mittel': 13000, 'hoch': 18000, 'schub': 13000})}
out = {}
for a, (zyl, stufen) in AUTO.items():
    for st, rpm in stufen.items():
        best = None
        for k in (1, 2):
            f = os.path.join(ROH, f'{a}_{st}_{k}.mp3')
            if not os.path.exists(f): continue
            x = load(f); L = int(min(len(x) - 0.3 * SR, 3.2 * SR)); s0, sc = best_window(x[int(0.1 * SR):], L); s0 += int(0.1 * SR); seg = x[s0:s0 + L]
            p = pitches(seg); p = p[p > 0]; pv = float(np.std(np.log(p))) if len(p) > 2 else 1.0
            score = sc + 4 * pv
            if best is None or score < best[0]: best = (score, k, seg, sc, pv)
        y = norm_rms(loopify(best[2], int(0.2 * SR))); name = f'hist_{a}_{st}'; save(os.path.join(SND, name + '.wav'), y)
        m = float(pitch(y)); fire = rpm / 60 * zyl / 2; g = m * 2 ** round(np.log2(fire / m))
        out[name] = {'variante': best[1], 'lautheit_schwankung': round(best[3], 3), 'tonhoehe_schwankung': round(best[4], 3), 'gemessen_hz': round(m, 1), 'grundton': round(g, 1), 'verlangt_upm': rpm, 'tempo_bei_verlangt': round(fire / g, 2)}
        print(name, out[name], flush=True)
json.dump(out, open(os.path.join(ROH, 'auswahl.json'), 'w'), indent=1)
