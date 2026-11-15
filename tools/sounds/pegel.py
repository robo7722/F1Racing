"""Pegel von Fahr-Geräusch-Loops beruhigen (v2.01): KI-Aufnahmen schwellen an und ab (Wind 3,5-fach, Kies 7-fach, Quietschen in 2,5-s-Wellen).
Als Loop klingt das wie ein „wellenartiges“ Pumpen. Hier: Hüllkurve (gleitender RMS, 300 ms, zyklisch – der Loop bleibt nahtlos) messen
und das Signal durch Hüllkurve^0,9 teilen – 90 % der Schwankung verschwinden, Struktur (Steine, Rattern) bleibt.
Aufruf: python tools/sounds/pegel.py   (nach aufbereiten_v2.py)
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from varianten import SND, SR, save
import wave

NAMES = ['kies', 'rasen', 'schaben_metall', 'schaben_beton']


def read(path):
    w = wave.open(path); return np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.


def calm(x, win=0.3, k=0.9):
    h = int(win * SR); p = np.concatenate([x[-h:], x, x[:h]]) ** 2
    c = np.cumsum(np.concatenate([[0], p])); e = np.sqrt((c[2 * h:] - c[:-2 * h]) / (2 * h))[:len(x)] + 1e-4
    y = x / e ** k; return y * 0.14 / np.sqrt(np.mean(y ** 2))


if __name__ == '__main__':
    for n in NAMES:
        f = os.path.join(SND, n + '.wav'); x = read(f); y = calm(x)
        h = int(0.4 * SR); env = lambda z: np.array([np.sqrt(np.mean(z[i:i + h] ** 2)) for i in range(0, len(z) - h, h)])
        a, b = env(x), env(y); y = np.clip(y, -0.99, 0.99); save(f, y)
        print(f'{n}: Pegel-Verhältnis max/min vorher {a.max() / a.min():.1f}, nachher {b.max() / b.min():.1f}')
