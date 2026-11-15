"""Aufbereitung der v2.00-Sounds (sounds/roh/v2/<name>_<k>.mp3 aus tools/sounds/erzeugen.py) – siehe docs/SOUNDS.md.

Je Name gibt es 2 Varianten; gewählt wird automatisch nach Messwerten:
- Motor-Loops (mx5_*): möglichst konstante Tonhöhe und Lautheit; der stabilste Abschnitt wird ausgeschnitten.
- übrige Loops (Schaben, Untergrund, Reifen, Wind): möglichst gleichmäßige Lautheit (keine Einzelschläge im Loop).
- Einschläge: genau ein Hauptschlag (keine zweiten Spitzen), steiler Einsatz.
Danach: Loops nahtlos überblenden (0,2 s) und auf RMS 0,14 bringen; Einschläge ab dem Einsatz schneiden, Ende ausblenden,
Spitze auf −1 dBFS. Alles als WAV mono 32 kHz nach sounds/ (Motor-Loops: Grundton wird gemessen und ausgegeben).
Aufruf: python tools/sounds/aufbereiten_v2.py
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from varianten import load, save, pitch, SR, SND

ROH = os.path.join(SND, 'roh', 'v2')
ENGINE = []   # Motor-Loops werden fest gewählt (MX5 unten): die KI trifft die verlangte Drehzahl nicht, die echte Tonhöhe wurde gemessen
# MX5-Roadster (Vierzylinder: Zündfrequenz = U/min ÷ 30), v2.01. Die KI trifft verlangte Drehzahlen nicht (fast alles landet bei 160–280 Hz)
# und dreht innerhalb des Clips leicht hoch/runter. Deshalb: wenige Aufnahmen eines Stils, Tonhöhe geglättet (glaetten.py), kaum verschoben.
# Ziel: (Rohdatei, Abschnitt s, Tonhöhe ca. (Hz, zum Messen), Halbtöne danach) – Grundton in index.html: leer 28,3 (fest = 850 U/min), sonst gemessen
MX5 = {
    'mx5n_leer': ('mx5_leer_1.mp3', None, None, 0),           # v2.04: Leerlauf aus dem ersten Lauf (klarstes Pulsieren 27,1 Hz ≈ 810 U/min), ungeglättet
    'mx5n_tief2': ('mx5b_tief_1.mp3', (0.2, 3.8), 170, -7),   # 116 Hz ≈ 3.500 U/min
    'mx5n_tief3': ('mx5b_tief_1.mp3', (0.2, 3.8), 170, -19),  # v2.04: 58 Hz ≈ 1.750 U/min – Zwischenstufe, damit Gasstöße im Stand nicht 2-fach/0,4-fach gestimmt werden
    'mx5n_hoch': ('mx5b_hoch_1.mp3', (0.2, 3.8), 268, -3),    # 271 -> 228 Hz ≈ 6.850 U/min
    'mx5n_schub': ('mx5b_schub_3.mp3', (0.2, 2.8), 255, 0),   # Gas weg, 253 Hz
}
LOOPS = ['schaben_metall', 'schaben_beton', 'kies', 'rasen', 'kerb']   # wind: seit v2.05 aus tools/sounds/wind.py
HITS = {'cf_leicht': 0.35, 'cf_auto': 0.9, 'cf_armco': 1.2, 'cf_beton': 1.1, 'stahl_leicht': 0.4,
        'stahl_auto': 0.9, 'stahl_wand': 1.2, 'kart_kart': 0.5, 'kart_wand': 0.7, 'kies_einschlag': 1.0}   # Höchstlänge ab Einsatz (s)


def env(x, win=0.02):
    h = int(win * SR); n = len(x) // h
    return np.sqrt(np.mean(x[:n * h].reshape(n, h) ** 2, axis=1))


def pitches(x, w=0.25):
    out = []; h = int(w * SR)
    for s in range(0, len(x) - h, h // 2): out.append(pitch(x[s:s + h]) if h >= 8192 + 4096 else pitch(np.tile(x[s:s + h], 2)))
    return np.array(out)


def best_window(x, length):
    """Abschnitt der Länge `length` (Samples) mit der gleichmäßigsten Lautheit."""
    e = env(x, 0.05); n = int(length / (0.05 * SR)); best, bs = 0, 1e9
    for i in range(0, max(1, len(e) - n)):
        seg = e[i:i + n]; sc = np.std(seg) / (np.mean(seg) + 1e-9)
        if sc < bs: bs, best = sc, i
    return int(best * 0.05 * SR), bs


def loopify(x, xf):
    n = len(x) - xf; t = np.linspace(0, 1, xf); y = x[:n].copy()
    y[:xf] = x[:xf] * np.sin(t * np.pi / 2) + x[n:n + xf] * np.cos(t * np.pi / 2); return y


def norm_rms(x, r=0.14): return x * r / (np.sqrt(np.mean(x ** 2)) + 1e-9)


def onset(x):
    e = env(x, 0.005); thr = 0.15 * e.max(); i = int(np.argmax(e > thr)); return max(0, i * int(0.005 * SR) - int(0.004 * SR))


def peaks_after(x):
    """Anzahl getrennter Spitzen > 50 % der Höchstspitze (Abstand ≥ 150 ms) – 1 = sauberer Einzelschlag."""
    e = env(x, 0.01); m = e.max(); idx = np.where(e > 0.5 * m)[0]
    if not len(idx): return 0
    groups = 1 + int(np.sum(np.diff(idx) > 15)); return groups


def variants(name): return sorted(f for f in os.listdir(ROH) if f.startswith(name + '_') and f[len(name) + 1:-4].isdigit())


if __name__ == '__main__':
    info = {}
    from varianten import shift, seam
    from glaetten import flatten, track
    for name, (src, cut, p0, st) in MX5.items():
        x = load(os.path.join(ROH, src))
        if p0 is None:   # ohne Glätten: ruhigsten 3-s-Abschnitt nehmen
            a, _ = best_window(x[int(0.1 * SR):], int(3.0 * SR)); a += int(0.1 * SR); y = norm_rms(loopify(x[a:a + int(3.0 * SR)], int(0.25 * SR))); ref = 27.1
        else:
            x = x[int(cut[0] * SR):int(cut[1] * SR)]; y, ref, _ = flatten(x, p0); y = norm_rms(loopify(y, int(0.25 * SR)))
        if st: n = len(y); y = norm_rms(seam(shift(np.concatenate([y, y, y]), st), n, int(0.12 * SR)))
        _, p = track(y, ref * 2 ** (st / 12)) if p0 else (None, np.array([ref])); save(os.path.join(SND, name + '.wav'), y)
        info[name] = {'quelle': src, 'halbtoene': st, 'grundton': round(float(np.median(p)), 1), 'laenge': round(len(y) / SR, 2)}; print(name, info[name], flush=True)
    for name in ENGINE + LOOPS:
        best = None
        for f in variants(name):
            x = load(os.path.join(ROH, f)); L = int(min(len(x) - 0.3 * SR, 3.2 * SR))
            a, sc = best_window(x[int(0.1 * SR):], L); a += int(0.1 * SR); seg = x[a:a + L]
            score = sc
            if name in ENGINE:
                p = pitches(seg); p = p[p > 0]; pv = np.std(np.log(p)) if len(p) > 2 else 1; score = sc + 4 * pv
            if best is None or score < best[0]: best = (score, f, seg)
        if not best: print(name, 'fehlt'); continue
        y = norm_rms(loopify(best[2], int(0.2 * SR))); save(os.path.join(SND, name + '.wav'), y)
        p = pitch(y) if name in ENGINE else None
        info[name] = {'quelle': best[1], 'laenge': round(len(y) / SR, 2), 'wert': round(best[0], 3), **({'grundton': round(p, 1)} if p else {})}
        print(name, info[name], flush=True)
    for name, maxlen in HITS.items():
        best = None
        for f in variants(name):
            x = load(os.path.join(ROH, f)); o = onset(x); seg = x[o:o + int(maxlen * SR)]
            pk = peaks_after(seg); e = env(seg, 0.005); attack = int(np.argmax(e)) * 0.005   # Zeit bis zur Spitze
            score = pk + attack * 4
            if best is None or score < best[0]: best = (score, f, seg, pk, attack)
        if not best: print(name, 'fehlt'); continue
        y = best[2].copy(); fo = min(len(y) // 3, int(0.08 * SR)); y[-fo:] *= np.linspace(1, 0, fo) ** 2
        y = y * (10 ** (-1 / 20)) / (np.abs(y).max() + 1e-9); save(os.path.join(SND, name + '.wav'), y)
        info[name] = {'quelle': best[1], 'laenge': round(len(y) / SR, 2), 'spitzen': best[3], 'bis_spitze_s': round(best[4], 3)}
        print(name, info[name], flush=True)
    json.dump(info, open(os.path.join(ROH, 'auswahl.json'), 'w'), indent=1, ensure_ascii=False)
