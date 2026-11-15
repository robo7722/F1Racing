"""Fahrtwind als gleichmäßiges Rauschen (v2.05) – ersetzt die ElevenLabs-Aufnahme, die 7–8-mal je Sekunde pulsierte (Böen am Helm):
bei hohem Tempo klang das „wellig“. Hier: Rauschen direkt im Frequenzbereich geformt (tiefes Rauschen + etwas Zischen), zufällige Phasen.
Weil das Spektrum auf einem festen Raster liegt, ist das Signal von selbst periodisch – der Loop hat keine Naht und keine Pegelschwankung.
Aufruf: python tools/sounds/wind.py
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from varianten import SND, SR, save

if __name__ == '__main__':
    n = 4 * SR; f = np.fft.rfftfreq(n, 1 / SR); rng = np.random.default_rng(7)
    mag = 1 / (1 + (f / 350) ** 2) ** 0.5            # tiefes Rauschen (Luftstrom), fällt ab 350 Hz mit 6 dB/Oktave
    mag += 0.12 / (1 + ((f - 2200) / 1400) ** 2)      # leichtes Zischen um 2,2 kHz (Kanten, Helm)
    mag *= (f > 40) * np.clip(f / 120, 0, 1)          # kein Brummen unter 40 Hz
    X = mag * np.exp(2j * np.pi * rng.random(len(f))); y = np.fft.irfft(X, n)
    y *= 0.14 / np.sqrt(np.mean(y ** 2)); save(os.path.join(SND, 'wind.wav'), np.clip(y, -0.99, 0.99))
    h = int(0.05 * SR); e = np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) for i in range(0, n - h, h)])
    E = np.abs(np.fft.rfft(e - e.mean())); fe = np.fft.rfftfreq(len(e), 0.05)
    print(f'wind.wav: 4 s, Pegel je 50 ms min/max {e.min():.3f}/{e.max():.3f} (Verhältnis {e.max() / e.min():.2f}), Naht {abs(y[0] - y[-1]):.3f}')
