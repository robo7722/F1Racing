"""Hörprobe des Roadster-Motors ohne das Spiel (v2.14) – siehe docs/MOTORSOUND-ANLEITUNG.md, Abschnitt 6.

Bildet die Spiel-Logik nach (Leerlauf-Schleife, Granular-Wiedergabe aus dem echten Durchzug 1.000–4.400 U/min, Stufen 5.200/6.900,
echte Gasstöße, Lautstärken und Überblendungen wie in sndEngine/granTick) und rechnet einen festen Ablauf:
0–2,5 Leerlauf · 2,5–4,8 und 5,4–8,0 Gasstöße · 9,2–11,6 Anfahren 850→6.000 · 11,6–11,8 Schalten · 11,8–13,4 Vollgas 4.500→6.200 · 13,4–16,7 Gas weg, Leerlauf.
Gibt den Pegel je 0,1 s um das Anfahren aus (Sprünge/Löcher an Übergängen sichtbar machen).
Aufruf: python tools/sounds/hoerprobe_mx5.py ausgabe.mp3
"""
import sys, os, wave, subprocess, json, re, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR = 32000; SND = os.path.join(ROOT, 'sounds')
def L(n):
    w = wave.open(os.path.join(SND, n + '.wav')); return np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
TAB = json.loads(re.search(r"file: 'sounds/mx5e_durchzug\.wav', tab: (\[\[.*?\]\])", html).group(1)); TT = np.array([a[0] for a in TAB]); RR = np.array([a[1] for a in TAB], float)
LOOPS = [('mx5e_leer', 28.4, (0.4, 0.4)), ('mx5e_5200', 172.8, (0.3, 0.4)), ('mx5e_6900', 230.5, None)]
seq = []; blips = []
def ramp(a, b, sec, thr):
    n = int(sec * 100); seq.extend((a + (b - a) * k / n, thr, 0) for k in range(n))
def blip(name, dur):
    blips.append((len(seq) / 100, name)); seq.extend((850, 0, 1) for _ in range(int((dur - 0.3) * 100))); seq.extend((850, 0, 0) for _ in range(30))
ramp(850, 850, 2.5, 0); blip('mx5e_blip1', 2.27); ramp(850, 850, 0.6, 0); blip('mx5e_blip2', 2.67); ramp(850, 850, 1.2, 0)
ramp(850, 6000, 2.4, 1); ramp(6000, 4500, 0.16, 0.2); ramp(4500, 6200, 1.6, 1); ramp(6200, 850, 1.8, 0); ramp(850, 850, 1.5, 0)
rpm = np.array([s[0] for s in seq]); thr = np.array([s[1] for s in seq]); mute = np.array([s[2] for s in seq], float)
for i in range(1, len(rpm)): rpm[i] = rpm[i - 1] + (rpm[i] - rpm[i - 1]) * 0.35
N = len(seq) * SR // 100; t = np.arange(N) / SR; tt = np.arange(len(seq)) / 100
R = np.interp(t, tt, rpm); T = np.interp(t, tt, thr); M = np.interp(t, tt, np.convolve(mute, np.ones(16) / 16, 'same'))
gw = np.clip((R - 950) / 550, 0, 1) * (1 - np.clip((R - 3900) / 500, 0, 1)); gw = gw * gw * (3 - 2 * gw)
fq = R / 30; bases = np.array([l[1] for l in LOOPS]); loop = np.zeros(N)
i = np.clip(np.searchsorted(bases, fq) - 1, 0, len(LOOPS) - 2); u = np.clip(np.log(fq / bases[i]) / np.log(bases[i + 1] / bases[i]), 0, 1)
xs = np.array([(l[2] or (0.38, 0.24))[0] for l in LOOPS]); xw = np.array([(l[2] or (0.38, 0.24))[1] for l in LOOPS])
x = np.clip((u - xs[i]) / xw[i], 0, 1); x = x * x * (3 - 2 * x)
for k, (f, base, _) in enumerate(LOOPS):
    b = L(f); w = np.where(i == k, np.cos(x * np.pi / 2), 0) + np.where(i + 1 == k, np.sin(x * np.pi / 2), 0)
    pos = np.cumsum(np.clip(fq / base, 0.4, 2.2)) % len(b); j = pos.astype(int); fr = pos - j; loop += w * (b[j] * (1 - fr) + b[(j + 1) % len(b)] * fr)
eng = loop * np.cos(gw * np.pi / 2)
dz = L('mx5e_durchzug'); G = 0.1; H = G / 3; gl = int(G * SR); win = np.sin(np.pi * np.arange(gl) / (gl - 1)) ** 2 / 1.5; gr = np.zeros(N + gl * 2)
Sx, ST, Sr = 0.0, 0.0, 1.0; Tn = 0.0
while Tn < N / SR:
    k0 = int(Tn * SR); rp = R[min(k0, N - 1)]; r = np.clip(rp, RR[0], RR[-1]); k = 0
    while k < len(RR) - 2 and RR[k + 1] < r: k += 1
    p = TT[k] + np.clip((r - RR[k]) / max(1, RR[k + 1] - RR[k]), 0, 1) * (TT[k + 1] - TT[k]); rt = np.clip(rp / r, 0.6, 1.04); per = 30 / r
    cont = Sx + (Tn - ST) * Sr; s0 = cont + round((p - cont) / per) * per
    if not abs(s0 - p) < 0.06 or s0 < 0: s0 = p
    s0 = min(max(s0, 0), len(dz) / SR - G * rt - 0.005); w = np.sin(gw[min(k0, N - 1)] * np.pi / 2)
    if w > 0.002:
        src = s0 * SR + np.arange(gl) * rt; i0 = src.astype(int); fr = src - i0; g = dz[i0] * (1 - fr) + dz[np.minimum(i0 + 1, len(dz) - 1)] * fr
        gr[k0:k0 + gl] += g * win * w
    Sx, ST, Sr = s0, Tn, rt; Tn += H
eng += gr[:N]
V = 0.6 * (0.5 + 0.5 * np.maximum(T, 0.2)) * (1 - M); Vs = np.copy(V); au = 1 - np.exp(-1 / (0.14 * SR)); ad = 1 - np.exp(-1 / (0.04 * SR))
for n in range(1, N): Vs[n] = Vs[n - 1] + (V[n] - Vs[n - 1]) * (au if V[n] > Vs[n - 1] else ad)
out = eng * Vs
for t0, name in blips:
    b = L(name); s0 = int(t0 * SR); e = min(N, s0 + len(b)); out[s0:e] += b[:e - s0]
out *= 0.6 / np.abs(out).max()
subprocess.run(['ffmpeg', '-v', 'quiet', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-b:a', '160k', sys.argv[1]], input=(out * 32767).astype('<i2').tobytes(), check=True)
h = int(0.1 * SR); e = [np.sqrt(np.mean(out[q:q + h] ** 2)) for q in range(0, N - h, h)]
print('Pegel 8,8–12 s:', ' '.join(f'{q / 10:.1f}:{v:.3f}' for q, v in enumerate(e) if 8.8 <= q / 10 <= 12))
