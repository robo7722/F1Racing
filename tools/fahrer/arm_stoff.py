"""Hochauflösende Stofftextur nur für die Ärmel der F1/F2-Fahrer (v1.96) -> textures/f1_arm_stoff.jpg

Warum: Die Ärmel bekommen im Atlas textures/kart_fahrer.jpg (Anzug 512²) nur ~4,8 Bildpunkte je cm (≈2 mm je Bildpunkt).
In der Helmkamera liegen die Unterarme 25–50 cm vor dem Auge – die Foto-Schattierung der Vorlage war dort nur noch weiche Flecken.
Die Vorlage (base.jpg) ist nicht im Repo, eine schärfere Fassung des Atlas lässt sich also nicht neu backen.
Stattdessen: eigene kachelbare Stofftextur (1024², eine Kachel = 4 cm -> 256 Bildpunkte je cm), dreiseitig auf die Ruhe-Position projiziert.
Kanäle (Graustufen 0…255, 128 = neutral):
  R  Köpergewebe 2/2 (Höhe): 64 Fäden je Kachel (Faden 0,63 mm), Faserstreifen entlang des Fadens
  G  Melierung: unregelmäßige Garnfarbe, Flecken 1–4 mm (die sieht man auch aus 50 cm)
  B  Flusen/Fasern: feine helle/dunkle Härchen quer über das Gewebe
Mipmaps der Grafikkarte blenden das Gewebe mit der Entfernung von selbst sauber aus (kein Flimmern).
Aufruf: python tools/fahrer/arm_stoff.py
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
N, THREADS = 1024, 64
rng = np.random.default_rng(7)


def per_noise(n, f_lo, f_hi, aniso=(1.0, 1.0)):
    """Kachelbares Rauschen über FFT: nur Frequenzen f_lo…f_hi (Perioden je Kachel), optional gestreckt."""
    fx = np.fft.fftfreq(n) * n; fy = np.fft.fftfreq(n) * n; FX, FY = np.meshgrid(fx, fy)
    f = np.hypot(FX * aniso[0], FY * aniso[1])
    amp = ((f >= f_lo) & (f <= f_hi)) / np.maximum(f, 1)
    z = np.fft.ifft2(amp * np.exp(2j * np.pi * rng.random((n, n)))).real
    return (z - z.mean()) / (z.std() + 1e-9)


y, x = np.mgrid[0:N, 0:N] / N * THREADS            # Faden-Koordinaten
ix, iy = np.floor(x).astype(int), np.floor(y).astype(int); fx, fy = x - ix, y - iy
warp_up = ((ix + iy) % 4) < 2                        # 2/2-Köper: Kettfaden liegt oben, je Zeile um einen Faden versetzt -> schräger Grat
prof_w = np.sin(np.pi * fx) ** 0.6                   # Querschnitt Kettfaden (senkrecht)
prof_f = np.sin(np.pi * fy) ** 0.6                   # Schussfaden (waagerecht)
h = np.where(warp_up, 0.55 + 0.45 * prof_w, 0.55 + 0.45 * prof_f)
fib_v = per_noise(N, 120, 400, aniso=(0.15, 1.0))    # Fasern entlang Kette (senkrecht gestreckt)
fib_h = per_noise(N, 120, 400, aniso=(1.0, 0.15))
h += 0.10 * np.where(warp_up, fib_v, fib_h)
h += 0.06 * per_noise(N, 20, 60)                     # Garn ungleichmäßig dick
h = (h - h.mean()) / h.std()

mel = 0.75 * per_noise(N, 10, 40) + 0.45 * per_noise(N, 40, 110)   # Melierung: Flecken 1–4 mm
mel = (mel - mel.mean()) / mel.std()

# Flusen: wenige dünne Härchen (kurze, zufällig gerichtete Striche)
fl = np.zeros((N, N))
for _ in range(900):
    cx, cy, a, ln = rng.random() * N, rng.random() * N, rng.random() * np.pi, 6 + rng.random() * 18
    s = rng.choice([-1.0, 1.0]) * (0.5 + rng.random())
    for k in np.linspace(-0.5, 0.5, int(ln * 2)):
        px, py = int(cx + np.cos(a) * ln * k) % N, int(cy + np.sin(a) * ln * k) % N
        fl[py, px] += s
fl = np.clip(fl, -1.5, 1.5); fl = (fl - fl.mean()) / (fl.std() + 1e-9)

to8 = lambda a, k: np.clip(128 + a * k, 0, 255).astype(np.uint8)
img = np.dstack([to8(h, 42), to8(mel, 40), to8(fl, 30)])
out = os.path.join(ROOT, 'textures', 'f1_arm_stoff.jpg')
Image.fromarray(img).save(out, quality=85, subsampling=0)   # ohne Farb-Unterabtastung: die drei Kanäle sind getrennte Daten
print('geschrieben', out, os.path.getsize(out), 'Bytes')
