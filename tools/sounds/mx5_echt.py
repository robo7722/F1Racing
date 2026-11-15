"""MX-5 aus einer ECHTEN Aufnahme (v2.06) – ersetzt die KI-Aufnahmen.

Quelle: „Mazda MX-5 Miata – engine and exhaust sound“, Ride in Japan (YouTube: „MAZDA MX5 Miata 1.6L exhaust sound sample“),
Wikimedia Commons, Lizenz CC BY 3.0 (Namensnennung nötig – steht im Spiel unter Einstellungen → Extras → Credits).
https://commons.wikimedia.org/wiki/File:Mazda_MX-5_Miata_-_engine_and_exhaust_sound_(YouTube_wKeTXxwpkS0).opus
NA 1,6 l statt ND2 2,0 l, aber derselbe Vierzylinder-Charakter (Zündfrequenz = U/min ÷ 30).

Die 9-min-Aufnahme wurde nach Abschnitten mit konstanter Drehzahl durchsucht (Autokorrelation alle 0,1 s, ≥ 1,5 s, Schwankung < 2,5 %).
Die gewählten Ausschnitte liegen als sounds/roh/echt/mx5_<name>.wav (unbearbeitet, 32 kHz mono) im Projekt; hier werden sie
geglättet (glaetten.py), nahtlos geloopt und auf gleiche Lautheit gebracht. Die oberste Stufe ist die 5.200er um +5 HT verschoben
(Rubberband, Formanten bleiben) – über 5.600 U/min gibt es in der Aufnahme keinen konstanten Abschnitt.
v2.07: Die 1.070er-Stelle (r1100) war Fahren unter Last (heller, angestrengt) und klang bei Gasstößen im Stand falsch –
ersetzt durch die 2.400er-Stelle −7 HT (≈ 1.600 U/min). r1100 bleibt als Rohausschnitt liegen, wird aber nicht mehr verwendet.
Aufruf: python tools/sounds/mx5_echt.py [Pfad zur .opus]   (mit Pfad: Ausschnitte neu schneiden; ohne: vorhandene Ausschnitte nutzen)
"""
import os, sys, subprocess, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from varianten import load, save, shift, seam, SR, SND
from glaetten import flatten, track

ROH = os.path.join(SND, 'roh', 'echt')
# Name: (Start s, Länge s, ungefährer Grundton Hz)   – Zeiten in der Commons-Aufnahme
CUT = {'leer': (132.8, 2.9, 28.4), 'r1100': (393.8, 3.0, 35.8), 'r2400': (448.1, 4.8, 79.6), 'r3500': (436.7, 4.5, 115.9), 'r5200': (481.5, 2.0, 173.0), 'schub': None}
OUT = {'mx5e_leer': ('leer', 0)}   # v2.08: nur noch der Leerlauf als Schleife – alles darüber kommt granular aus dem Durchzug (vorher 2400/3500/5200/6900-Stufen)


def loopify(x, xf):
    n = len(x) - xf; t = np.linspace(0, 1, xf); y = x[:n].copy()
    y[:xf] = x[:xf] * np.sin(t * np.pi / 2) + x[n:n + xf] * np.cos(t * np.pi / 2); return y


def norm(x): return x * 0.14 / (np.sqrt(np.mean(x ** 2)) + 1e-9)


# Echte Gasstöße im Stand (v2.07): Zeiten in der Commons-Aufnahme (Beginn, Dauer der Drehzahl-Spitze)
BLIPS = {'mx5e_blip1': (19.95, 0.75), 'mx5e_blip2': (25.55, 1.15), 'mx5e_blip3': (28.35, 1.30)}


def abfall_strecken(seg, faktor=1.8, laenge=1.0):
    """(v2.11, seit v2.12 nicht mehr verwendet – das Problem war die Mischung mit der Leerlauf-Schleife danach, nicht der Abfall) v2.10: Der echte Abfall nach dem Gasstoß (5.000 → Leerlauf in ~0,5 s, leichte Schwungmasse) wirkte im Spiel zu hart.
    Ab kurz nach der Spitze wird 1 s Abfall per Rubberband zeitlich gestreckt (Tonhöhe bleibt) – die Drehzahl sinkt echt klingend, nur langsamer."""
    h = int(0.02 * SR); env = np.array([np.sqrt(np.mean(seg[i:i + h] ** 2)) for i in range(0, len(seg) - h, h)])
    a = (int(np.argmax(env)) + 4) * h; b = min(len(seg), a + int(laenge * SR))
    tmp = os.path.join(SND, '_tmp_abfall.wav'); save(tmp, seg[a:b])
    try: st = load(tmp, f'rubberband=tempo={1 / faktor:.4f}:pitchq=quality:transients=smooth')
    finally: os.remove(tmp)
    xf = int(0.02 * SR); t = np.linspace(0, 1, xf)
    head = seg[:a + xf].copy(); head[-xf:] = seg[a:a + xf] * np.cos(t * np.pi / 2) + st[:xf] * np.sin(t * np.pi / 2)
    tail = seg[b:]; mid = st[xf:]; m2 = mid.copy(); m2[-xf:] = mid[-xf:] * np.cos(t * np.pi / 2) + tail[:xf] * np.sin(t * np.pi / 2) if len(tail) >= xf else mid[-xf:]
    return np.concatenate([head, m2, tail[xf:]])


def blip_angleichen(seg, k=0.55):
    """Echte Dynamik: Spitze ~26× lauter als der Leerlauf. Im Spiel liegt die Leerlauf-Schleife auf normaler Lautstärke – ohne Anpassung
    fiel der Pegel beim Wechsel Schleife → Gasstoß auf ein Zehntel und sprang danach wieder hoch („abgehackt“).
    Hier: Pegel über dem Leerlauf mit Exponent 1−k zusammendrücken (26× → ~4×), Leerlauf-Anteil auf RMS 0,14 wie die Schleifen."""
    h = int(0.02 * SR); p = np.concatenate([np.zeros(h), seg ** 2, np.zeros(h)]); c = np.cumsum(np.concatenate([[0], p]))
    env = np.sqrt((c[2 * h:] - c[:-2 * h]) / (2 * h))[:len(seg)] + 1e-6
    idle = np.sqrt(np.mean(seg[:int(0.1 * SR)] ** 2)) + 1e-6
    g = np.where(env > idle, (env / idle) ** -k, 1.0); y = seg * g
    y *= 0.14 / (np.sqrt(np.mean(y[:int(0.1 * SR)] ** 2)) + 1e-9)
    if np.abs(y).max() > 0.95: y *= 0.95 / np.abs(y).max()
    return y


# Durchzug für die Granular-Wiedergabe (v2.08): echte Beschleunigung 1.244 → 6.115 U/min ohne Schaltvorgang (Commons-Aufnahme 469,3–473,0 s)
DURCHZUG = (469.3, 473.0)
# v2.09: zweiter Durchzug für ≥ 4.000 U/min – sehr gleichmäßig 3.710 → 6.115 U/min in 9,2 s, konstanter Pegel (Bordaufnahme). Der erste wird oben unsauber
# (hängt bei ~5.050, endet bei 6.115). Durchzug 118,3–122,3 s (bis 6.960) ist ein Vorbeifahren (Pegel ×16) – ungeeignet.
DURCHZUG2 = (489.5, 498.8)


def drehzahl_tabelle(seg, step=0.025):
    """Drehzahl an jeder Stelle des Durchzugs: Autokorrelation alle 25 ms, Median über ±0,1 s, monoton steigend gemacht."""
    N = 2048; hop = int(step * SR); f = np.fft.rfftfreq(N, 1 / SR); T, P = [], []
    for s in range(0, len(seg) - N, hop):
        w = seg[s:s + N]; X = np.fft.rfft(w * np.hanning(N)); X[(f < 20) | (f > 600)] = 0; y = np.fft.irfft(X, N)
        ac = np.correlate(y, y, 'full')[N - 1:]; ac /= ac[0] + 1e-9; L0, L1 = int(SR / 300), int(SR / 30); l = L0 + int(np.argmax(ac[L0:L1]))
        T.append((s + N / 2) / SR); P.append(SR / l)
    lp = np.log(np.array(P)); med = np.array([np.median(lp[max(0, i - 4):i + 5]) for i in range(len(lp))])
    return np.array(T), np.exp(np.maximum.accumulate(med)) * 30


if __name__ == '__main__':
    os.makedirs(ROH, exist_ok=True)
    if len(sys.argv) > 1:
        x = load(sys.argv[1])
        for k, c in CUT.items():
            if c: a, d, _ = c; save(os.path.join(ROH, f'mx5_{k}.wav'), x[int(a * SR):int((a + d) * SR)] / (np.abs(x).max() + 1e-9))
    if len(sys.argv) > 1:
        for name, (a, d) in BLIPS.items(): save(os.path.join(ROH, name.replace('mx5e_', 'mx5_') + '.wav'), x[int((a - 0.12) * SR):int((a + d + 1.4) * SR)] / (np.abs(x).max() + 1e-9))
    for name in BLIPS:
        seg = load(os.path.join(ROH, name.replace('mx5e_', 'mx5_') + '.wav')); fo = int(0.01 * SR); fi = int(0.01 * SR)   # v2.12: Ende nur 10 ms ausblenden – das Spiel überblendet selbst (vorher 0,25 s → Loch beim Wechsel zur Leerlauf-Schleife)
        # v2.12: abfall_strecken nicht mehr verwendet (klang schlimmer)
        seg[-fo:] *= np.linspace(1, 0, fo) ** 2; seg[:fi] *= np.linspace(0, 1, fi); y = blip_angleichen(seg); save(os.path.join(SND, name + '.wav'), y)
        h = int(0.05 * SR); e = np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) for i in range(0, len(y) - h, h)])
        print(f'{name}: {len(y) / SR:.2f} s, Leerlauf-Pegel {e[:2].mean():.3f}, Spitze {e.max():.3f} (×{e.max() / e[:2].mean():.1f}), Ende {e[-6:-4].mean():.3f}')
    if len(sys.argv) > 1:
        a, b = DURCHZUG; save(os.path.join(ROH, 'mx5_durchzug.wav'), x[int(a * SR):int(b * SR)] / (np.abs(x).max() + 1e-9))
    seg = load(os.path.join(ROH, 'mx5_durchzug.wav')); fi = int(0.01 * SR); seg[:fi] *= np.linspace(0, 1, fi)
    T, R = drehzahl_tabelle(seg)
    # Lautheit: so normiert, dass der Durchzug bei ~2.000 U/min so laut ist wie die Schleifen (RMS 0,14); darüber wird er von selbst lauter
    i2 = np.searchsorted(R, 2000); c = int(T[min(i2, len(T) - 1)] * SR); g = 0.14 / (np.sqrt(np.mean(seg[max(0, c - 4000):c + 4000] ** 2)) + 1e-9)
    y = seg * g; y *= min(1, 0.95 / np.abs(y).max()); save(os.path.join(SND, 'mx5e_durchzug.wav'), y)
    tab = [[round(float(t), 3), int(r)] for t, r in zip(T[::4], R[::4])]
    if len(sys.argv) > 1:
        a, b = DURCHZUG2; save(os.path.join(ROH, 'mx5_durchzug2.wav'), x[int(a * SR):int(b * SR)] / (np.abs(x).max() + 1e-9))
    s2 = load(os.path.join(ROH, 'mx5_durchzug2.wav')); s2[:fi] *= np.linspace(0, 1, fi); T2, R2 = drehzahl_tabelle(s2)
    # gleiche Lautheit wie Durchzug 1 bei 3.900 U/min (Übergabe)
    rms = lambda z, TT, RR: np.sqrt(np.mean(z[max(0, int(TT[min(np.searchsorted(RR, 3900), len(TT) - 1)] * SR) - 4000):int(TT[min(np.searchsorted(RR, 3900), len(TT) - 1)] * SR) + 4000] ** 2))
    y2 = s2 * rms(y, T, R) / (rms(s2, T2, R2) + 1e-9); y2 *= min(1, 0.95 / np.abs(y2).max()); save(os.path.join(SND, 'mx5e_durchzug2.wav'), y2)
    tab2 = [[round(float(t), 3), int(r)] for t, r in zip(T2[::6], R2[::6])]
    print('mx5e_durchzug2:', f'{len(y2) / SR:.2f} s, {R2[0]:.0f} → {R2[-1]:.0f} U/min, Tabelle:', json.dumps(tab2, separators=(',', ':')))
    print('mx5e_durchzug:', f'{len(y) / SR:.2f} s, {R[0]:.0f} → {R[-1]:.0f} U/min, Tabelle ({len(tab)} Punkte):', json.dumps(tab, separators=(',', ':')))
    res = {}
    for name, (k, st) in OUT.items():
        x = load(os.path.join(ROH, f'mx5_{k}.wav')); p0 = CUT[k][2]
        y, ref, _ = flatten(x, p0); y = norm(loopify(y, int(min(0.25, len(y) / SR / 6) * SR)))
        if st: n = len(y); y = norm(seam(shift(np.concatenate([y, y, y]), st), n, int(0.1 * SR)))
        _, p = track(y, ref * 2 ** (st / 12)); save(os.path.join(SND, name + '.wav'), np.clip(y, -0.99, 0.99))
        res[name] = round(float(np.median(p)), 1)
        print(f'{name}: {k} {st:+d} HT, Grundton {res[name]} Hz ≈ {res[name] * 30:.0f} U/min, Schwankung {np.std(np.log(p)) * 100:.1f} %, {len(y) / SR:.2f} s', flush=True)
