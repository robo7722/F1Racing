"""Tonhöhe einer Motor-Aufnahme glätten (v2.01): KI-Aufnahmen „wandern“ innerhalb weniger Sekunden um 5–10 % (drehen leicht hoch/runter).
Als Loop springt die Tonhöhe dann an der Naht zurück – man hört alle 2–3 s ein künstliches Auf und Ab.
Hier: Tonhöhe alle 32 ms messen (Autokorrelation, nur ±25 % um den Mittelwert, sonst Oktavfehler), glätten und die Aufnahme mit
zeitlich veränderlichem Tempo abspielen, so dass die Periode überall gleich ist (Tempo-Änderung ≤ 10 % – Klangfarbe bleibt praktisch gleich).
"""
import numpy as np
from varianten import SR


def track(x, p0, hop=1024, win=4096):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[f > 4 * p0] = 0; X[f < 0.5 * p0] = 0; y = np.fft.irfft(X, len(x))
    t, p = [], []
    for s in range(0, len(y) - win, hop):
        seg = y[s:s + win]; a = np.correlate(seg, seg, 'full')[win - 1:]; a /= a[0] + 1e-9
        L0, L1 = int(SR / (p0 * 1.25)), int(SR / (p0 * 0.8)); l = L0 + int(np.argmax(a[L0:L1]))
        if 0 < l - L0 < L1 - L0 - 1:   # Parabel-Interpolation
            y0, y1, y2 = a[l - 1], a[l], a[l + 1]; d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12); l = l + d
        t.append(s + win / 2); p.append(SR / l)
    p = np.array(p); k = np.ones(5) / 5; ps = np.convolve(np.pad(p, 2, mode='edge'), k, 'valid')
    return np.array(t), ps


def flatten(x, p0):
    t, p = track(x, p0); ref = float(np.median(p))
    rate = np.interp(np.arange(len(x)), t, ref / p)            # Eingabe-Schritt je Ausgabe-Sample
    pos = np.cumsum(rate); pos = pos[pos < len(x) - 1]
    i = pos.astype(int); fr = pos - i
    return x[i] * (1 - fr) + x[i + 1] * fr, ref, p
