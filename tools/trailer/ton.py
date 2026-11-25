#!/usr/bin/env python3
"""Tonspur des Trailers: geschnittene Musik + dezente Geräusche aus den Klängen des Spiels (keine neuen Aufnahmen, keine Kosten).
   Aufruf: python3 tools/trailer/ton.py <Musik.wav> <Ausgabe.wav> [--ohne]        (--ohne: nur Musik, zum Vergleich)
   Geräusche: Ampel-Töne und Motoren in der Startaufstellung (7,4–10,85 s), Start (ab 10,85 s), Feuerwerk (74,5–79,3 s), Regen (79,3–90,8 s).
   Alles bewusst leise unter der Musik – gemischt nach Pegelmessung, nicht nach Gehör."""
import sys, os, numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); SR = 44100
mus, _sr = sf.read(sys.argv[1], always_2d=True); assert _sr == SR; n = len(mus); fx = np.zeros((n, 2), np.float32); rng = np.random.default_rng(7)
def schleife(datei, dauer, rate):
    """Schleife mit veränderlicher Abspielrate (Funktion der Zeit in s) – so entstehen Drehzahlverläufe aus den Motor-Schleifen des Spiels."""
    y, sr = sf.read(os.path.join(ROOT, 'sounds', datei)); y = y if y.ndim == 1 else y.mean(1); m = int(dauer * SR); t = np.arange(m) / SR
    ph = np.cumsum(rate(t) * sr / SR) % (len(y) - 1); i = ph.astype(int); f = ph - i; return (y[i] * (1 - f) + y[i + 1] * f).astype(np.float32)
def tief(x, fc):                      # einfacher Tiefpass (einpolig, zweimal)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x)
    for _ in range(2):
        acc = 0.0
        for k in range(len(x)): acc = a * acc + (1 - a) * x[k]; y[k] = acc
        x = y.copy()
    return y
def lege(x, t0, links=1.0, rechts=1.0):
    i = int(t0 * SR); m = min(len(x), n - i)
    if m > 0: fx[i:i + m, 0] += x[:m] * links; fx[i:i + m, 1] += x[:m] * rechts
def huelle(m, ein, aus): e = np.ones(m, np.float32); a = int(ein * SR); b = int(aus * SR); e[:a] = np.linspace(0, 1, a); e[m - b:] = np.linspace(1, 0, b); return e
if '--ohne' not in sys.argv:
    # Startaufstellung: drei Motoren im Leerlauf mit Gasstößen, lauter werdend
    D = 3.6
    for k, (basis, pan) in enumerate([(0.40, 0.3), (0.46, 0.7), (0.52, 0.5)]):
        stoss = lambda t, k=k: basis + 0.34 * (np.exp(-((t - 1.0 - 0.21 * k) / 0.16) ** 2) + np.exp(-((t - 2.0 - 0.17 * k) / 0.16) ** 2) + 1.25 * np.exp(-((t - 2.95 - 0.1 * k) / 0.3) ** 2))
        x = schleife('f1_mittel.wav', D, stoss); lege(x * huelle(len(x), 0.5, 0.05) * np.linspace(0.035, 0.085, len(x)), 7.3, 1 - pan * 0.6, 0.4 + pan * 0.6)
    # Ampel: fünf dumpfe Töne (wie im Spiel: Rechteck 330 Hz, gefiltert)
    for k in range(5):
        m = int(0.13 * SR); t = np.arange(m) / SR; b = tief(np.sign(np.sin(2 * np.pi * 330 * t)).astype(np.float32), 900) * huelle(m, 0.005, 0.05) * 0.045; lege(b, 7.4 + 0.3 + 0.5 * k)
    # Start: Drehzahl steigt durch drei Gänge, klingt in die Musik aus
    gang = lambda t: 0.78 + 0.42 * ((t % 1.15) / 1.15) + 0.05 * np.minimum(t, 3)
    for datei, gew, pan in (('f1_v2.wav', 0.6, 0.35), ('f1_v3.wav', 0.5, 0.65), ('f1_v4.wav', 0.35, 0.5)):
        x = schleife(datei, 5.0, gang); e = huelle(len(x), 0.03, 2.6) * np.linspace(1, 0.35, len(x)); lege(x * e * 0.45 * gew, 10.83, 1 - pan * 0.5, 0.5 + pan * 0.5)
    # Feuerwerk: tiefe, verhallende Schläge
    for t0 in (74.9, 75.6, 76.1, 76.9, 77.4, 78.2, 78.8):
        m = int(0.9 * SR); b = tief(rng.standard_normal(m).astype(np.float32), 140) * np.exp(-np.arange(m) / (0.22 * SR)) * 2.5; p = rng.random(); lege(b, t0 + rng.random() * 0.1, 0.5 + 0.5 * p, 1 - 0.5 * p)
    # Regen: gleichmäßiges Rauschen, links und rechts verschieden
    m = int(12.2 * SR)
    for c in (0, 1):
        r = rng.standard_normal(m).astype(np.float32); r = r - tief(r, 1800); r = tief(r, 7000) * huelle(m, 1.2, 2.5) * 0.04; i = int(79.1 * SR); k = min(m, n - i); fx[i:i + k, c] += r[:k]
out = mus.astype(np.float32) + fx; sp = float(np.abs(out).max())
if sp > 0.97: out *= 0.97 / sp
db = lambda x: 20 * np.log10(max(float(np.sqrt(np.mean(x ** 2))), 1e-9))
print('Spitze vor Begrenzung %.2f · Pegel Musik %.1f dB · Geräusche gesamt %.1f dB' % (sp, db(mus), db(fx)))
for name, a, b in (('Startaufstellung 7,4–10,8', 7.4, 10.8), ('Start 10,85–13', 10.85, 13), ('Feuerwerk 74,5–79,3', 74.5, 79.3), ('Regen 80–90', 80, 90)):
    i, j = int(a * SR), int(b * SR); print('  %-26s Musik %6.1f dB · Geräusche %6.1f dB' % (name, db(mus[i:j]), db(fx[i:j])))
sf.write(sys.argv[2], out, SR, subtype='PCM_16'); print(sys.argv[2])
