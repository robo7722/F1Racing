#!/usr/bin/env python3
"""Musik auf Trailerlänge schneiden: Abschnitte der Vorlage taktgenau aneinanderfügen (kurze Überblendung), am Ende ausblenden.
   Aufruf: python3 tools/trailer/musik_schnitt.py <Vorlage.wav> <Ausgabe.wav> --teile 0:76.65,126.83:148.0 [--blende 0.04] [--aus 3.5] [--json verlauf.json]
   --teile: Abschnitte der Vorlage in Sekunden (von:bis), in der Reihenfolge, in der sie im Trailer laufen.
   --json: Lautheitsverlauf des Ergebnisses (10 Werte je Sekunde, dB relativ zum Maximum) für die Storyboard-Grafik.
   Die Vorlage vorher mit ffmpeg nach WAV wandeln (44,1 kHz, Stereo). Das Ergebnis enthält geschützte Musik – nicht ins Repository legen."""
import sys, json, numpy as np, soundfile as sf
a = sys.argv[1:]
def flag(n, d=None):
    if '--' + n in a: i = a.index('--' + n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
teile = [tuple(float(x) for x in t.split(':')) for t in flag('teile').split(',')]; bl = float(flag('blende', 0.04)); aus = float(flag('aus', 3.5)); js = flag('json')
y, sr = sf.read(a[0], always_2d=True); n = int(bl * sr); out = None; marken = []
for von, bis in teile:
    seg = y[int(von * sr) - (n if out is not None else 0):int(bis * sr)].copy()
    if out is None: out = seg
    else:   # gleich laute Überblendung über n Abtastwerte, mittig auf der Schnittstelle
        w = np.sin(np.linspace(0, np.pi / 2, n))[:, None]; marken.append(round(len(out) / sr, 3))
        out[-n:] = out[-n:] * np.cos(np.linspace(0, np.pi / 2, n))[:, None] + seg[:n] * w; out = np.concatenate([out, seg[n:]])
k = int(aus * sr); out[-k:] *= (np.linspace(1, 0, k) ** 1.6)[:, None]
sf.write(a[1], out, sr, subtype='PCM_16'); print('Länge', round(len(out) / sr, 2), 's · Schnittstellen bei', marken)
if js:
    m = out.mean(1); h = sr // 10; e = np.array([np.sqrt(np.mean(m[i:i + h] ** 2)) for i in range(0, len(m) - h, h)]); db = 20 * np.log10(np.maximum(e, 1e-5)); db -= db.max()
    json.dump(dict(dauer=len(out) / sr, schnitt=marken, db=[round(float(x), 1) for x in db]), open(js, 'w'))
