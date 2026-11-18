"""Synthetische Motorklänge für die Legenden (v2.88, Wunsch 18.11.2026: „Erstelle die Sounds für die historischen Autos synthetisch und passend“).

Warum synthetisch: Die bisherigen Klassiker-Klänge waren ElevenLabs-Aufnahmen bzw. umgestimmte V10-Aufnahmen (RB8, MP4/13, 312).
Sie wurden im Spiel bis zum Begrenzer stark nachgestimmt und klangen oben falsch (RB8 bei hohem Tempo). Hier wird jeder Motor
nach seiner Bauart erzeugt (Zylinderzahl, Zündfolge, Drehzahl), und zwar je Drehzahlstufe neu – die oberste Stufe liegt genau
auf der Höchstdrehzahl. Im Spiel wird jede Stufe nur noch ≤ ~1,2-fach nachgestimmt. Kostet keine Credits.

Modell (je Stufe, nahtlose Schleife durch Rechnen im Frequenzraum – alles periodisch über die Schleifenlänge):
  * Auspuffstöße: je Zündung ein Impuls an seiner Stelle im Arbeitsspiel (720° / Zylinderzahl), mit fester Abweichung je Zylinder
    (Lautstärke, Zeitpunkt) und kleinem Zufall je Arbeitsspiel → Unterordnungen (das „Raue“ eines echten Motors).
  * Klangformung: Resonatoren auf Vielfachen der Zündfrequenz (Abgasschwingung) + feste Rohr-Resonanzen in Hz + Helligkeit je Drehzahl.
  * Verbrennungs-/Ansaugrauschen: Rauschen, im Takt der Zündungen moduliert, bandbegrenzt.
  * Turbo (Honda V6 1988): gedämpft (Tiefpass), Laderpfeifen, Abblaszischen.
  * „Gas weg“ (Schub): schwache, unregelmäßige Zündungen mit Aussetzern und Knallen.

Aufruf: python tools/sounds/synth_klassiker.py [Kürzel …]   → sounds/hist_<kürzel>_s<n>.wav, sounds/hist_<kürzel>_schub.wav
Gibt die Zeilen für SND_ENG in index.html aus (Grundton = Zündfrequenz der Stufe, wie die übrigen Motoren).
Hörproben: --probe schreibt tools/sounds/.probe/<kürzel>_hochlauf.wav (Hochdrehen über alle Stufen, nur zum Anhören).
"""
import os, sys, wave, zlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SND = os.path.join(ROOT, 'sounds'); SR = 32000; RMS = 0.14; LOOP = 2.0

# n: Zylinder · rpm: [unterste Stufe, Höchstdrehzahl] · st: Anzahl Stufen · var: Streuung je Zylinder (Lautstärke) · tj: Zeitversatz je Zylinder
# (Anteil des Zündabstands) · hell: Helligkeit (Abfall der Obertöne, kleiner = heller) · rohr: feste Resonanzen [Hz, Güte, Pegel] · rau: Rauschanteil
# · tief: Tiefpass Hz (Turbo/Schalldämpfer) · sub: Anteil der halben Ordnung (Kurbelwelle) · turbo: Laderpfeifen
CARS = {
    'f67': dict(name='Ferrari 312 (1967) – 3,0-l-V12, 60°, gleichmäßige Zündfolge', n=12, rpm=[4500, 11000], st=5, var=0.07, tj=0.012, hell=1.15,
                rohr=[[620, 2.2, 1.4], [1700, 2.5, 1.0], [3300, 3.0, 0.5]], rau=0.22, tief=7000, sub=0.20),
    'lot': dict(name='Lotus 49C (1970) – Cosworth DFV 3,0-l-V8, flache Kurbelwelle', n=8, rpm=[4500, 10200], st=5, var=0.11, tj=0.02, hell=1.05,
                rohr=[[480, 2.0, 1.5], [1350, 2.2, 1.1], [2900, 2.8, 0.6]], rau=0.30, tief=7500, sub=0.30),
    'mcl': dict(name='McLaren MP4/4 (1988) – Honda RA168E 1,5-l-V6 Turbo', n=6, rpm=[4500, 12500], st=5, var=0.06, tj=0.01, hell=1.45,
                rohr=[[380, 1.8, 1.6], [1100, 2.0, 0.9]], rau=0.26, tief=2600, sub=0.18, turbo=dict(f=7200, pegel=0.06, zisch=0.05)),
    'fer': dict(name='Ferrari F2004 – 3,0-l-V10, 90°, bis 18.300/min', n=10, rpm=[4500, 18300], st=7, var=0.04, tj=0.006, hell=0.85,
                rohr=[[1150, 2.4, 1.2], [2600, 2.6, 1.0], [5200, 3.0, 0.6]], rau=0.14, tief=11000, sub=0.10),
    'mcl98': dict(name='McLaren MP4/13 (1998) – Mercedes FO110G 3,0-l-V10, bis 17.500/min', n=10, rpm=[4500, 17500], st=7, var=0.05, tj=0.008, hell=0.95,
                  rohr=[[980, 2.2, 1.3], [2300, 2.6, 0.9], [4600, 3.0, 0.5]], rau=0.16, tief=10000, sub=0.12),
    'rbr': dict(name='Red Bull RB8 (2012) – Renault RS27 2,4-l-V8, flache Kurbelwelle, bis 18.000/min', n=8, rpm=[4500, 18000], st=7, var=0.065, tj=0.01, hell=0.9,
                rohr=[[900, 2.2, 1.2], [2200, 2.4, 1.1], [4400, 3.0, 0.7]], rau=0.18, tief=10500, sub=0.16),
}


def wav_write(path, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())


def stage(C, rpm, seed, schub=False):
    """Eine nahtlose Schleife bei fester Drehzahl. Gibt (Signal, Zündfrequenz in Hz) zurück."""
    rng = np.random.default_rng(seed); n = C['n']
    f_cyc = rpm / 120.0                                   # Arbeitsspiele je Sekunde (Viertakt: 2 Umdrehungen)
    N = int(round(LOOP * SR)); K = max(1, int(round(LOOP * f_cyc)))
    f_cyc = K * SR / N                                    # exakt periodisch über die Schleife
    f_fire = f_cyc * n
    cyl_a = 1 + C['var'] * rng.standard_normal(n)         # feste Eigenheiten je Zylinder
    cyl_t = C['tj'] * rng.standard_normal(n)
    f = np.fft.rfftfreq(N, 1 / SR); spec = np.zeros(len(f), complex); env_spec = np.zeros(len(f), complex)
    T = []
    for c in range(K):
        for j in range(n):
            a = cyl_a[j] * (1 + 0.025 * rng.standard_normal())
            if schub:
                a *= rng.uniform(0.15, 0.6) if rng.random() > 0.3 else 0.0   # Aussetzer
                if rng.random() < 0.012: a = rng.uniform(2.5, 4.5)          # Knall im Auspuff
            t = (c + (j + cyl_t[j] + 0.004 * rng.standard_normal()) / n) / f_cyc
            T.append((t % LOOP, a))
    ts = np.array([x[0] for x in T]); am = np.array([x[1] for x in T])
    # Impulsfolge im Frequenzraum (Bruchteil-Zeiten, bandbegrenzt, periodisch)
    for s in range(0, len(ts), 400):
        spec += (am[s:s + 400, None] * np.exp(-2j * np.pi * f[None, :] * ts[s:s + 400, None])).sum(0)
    env_spec[:] = spec
    # Klangformung
    H = np.zeros(len(f), complex); fz = np.maximum(f, 1.0)
    for h, g in [(1, 1.0), (2, 0.55), (3, 0.3), (4, 0.18)]:             # Abgasschwingung auf der Zündfrequenz und Vielfachen
        Q = 3.5; H += g / (1 + 1j * Q * (fz / (h * f_fire) - (h * f_fire) / fz))
    for f0, Q, g in C['rohr']:                                           # feste Rohr-/Gehäuse-Resonanzen
        H += 0.35 * g / (1 + 1j * Q * (fz / f0 - f0 / fz))
    sub = C.get('sub', 0)
    if sub:                                                              # halbe und Kurbel-Ordnungen (kommen aus der Zylinder-Streuung, hier betont)
        for h in (0.5, 1.5):
            H += sub / (1 + 1j * 5 * (fz / (h * f_fire) - (h * f_fire) / fz))
    rpm_k = rpm / C['rpm'][1]
    tilt = (fz / f_fire) ** (-C['hell'] * (1.15 - 0.35 * rpm_k))          # oben heller
    tilt[f < 0.3 * f_fire] *= (f[f < 0.3 * f_fire] / (0.3 * f_fire)) ** 2  # kein Brummen unter der halben Ordnung
    lp = 1 / np.sqrt(1 + (f / C['tief']) ** 4)
    hp = 1 / np.sqrt(1 + (60 / fz) ** 4)
    y = np.fft.irfft(spec * H * tilt * lp * hp, N)
    # Verbrennungs-/Ansaugrauschen, im Takt der Zündungen
    env = np.fft.irfft(env_spec * np.exp(-(f / (2.2 * f_fire)) ** 2), N); env = np.maximum(env, 0); env /= env.max() + 1e-9
    nz = np.fft.irfft(np.fft.rfft(rng.standard_normal(N)) * np.exp(-((np.log(fz / (1800 + 2600 * rpm_k))) / 0.9) ** 2), N)
    nz *= 0.35 + env
    y = y / (np.sqrt(np.mean(y ** 2)) + 1e-9) + C['rau'] * (1.6 if schub else 1) * nz / (np.sqrt(np.mean(nz ** 2)) + 1e-9)
    tb = C.get('turbo')
    if tb and not schub:                                                 # Laderpfeifen (steigt mit der Drehzahl) und Zischen
        k = round(tb['f'] * rpm_k * LOOP) / LOOP; tt = np.arange(N) / SR
        y += tb['pegel'] * np.sqrt(2) * np.sin(2 * np.pi * k * tt) * (0.8 + 0.2 * np.sin(2 * np.pi * round(3 * LOOP) / LOOP * tt))
        hs = np.fft.irfft(np.fft.rfft(rng.standard_normal(N)) * np.exp(-((f - 5000) / 1800) ** 2), N)
        y += tb['zisch'] * hs / (np.sqrt(np.mean(hs ** 2)) + 1e-9)
    if schub:
        y = np.fft.irfft(np.fft.rfft(y) * (1 / np.sqrt(1 + (f / (C['tief'] * 0.45)) ** 4)), N)
    y *= RMS / (np.sqrt(np.mean(y ** 2)) + 1e-9)
    pk = np.abs(y).max()
    if pk > 0.95: y = np.tanh(y * 1.2) / 1.2   # seltene Spitzen (Knallen) weich begrenzen
    return y, f_fire


def build(key, probe=False):
    C = CARS[key]; lo, hi = C['rpm']; st = C['st']
    rpms = [lo * (hi / lo) ** (i / (st - 1)) for i in range(st)]
    loops = []
    for i, r in enumerate(rpms):
        y, ff = stage(C, r, seed=zlib.crc32(('%s%d' % (key, i)).encode()))
        fn = 'hist_%s_s%d.wav' % (key, i); wav_write(os.path.join(SND, fn), y); loops.append((fn, ff, r))
    ys, fs = stage(C, rpms[-2], seed=7 + len(key), schub=True)
    wav_write(os.path.join(SND, 'hist_%s_schub.wav' % key), ys)
    js = ', '.join("['sounds/%s', %.1f]" % (fn, ff) for fn, ff, _ in loops)
    print("SND_ENG.hist_%s loops: [%s], schub: ['sounds/hist_%s_schub.wav', %.1f]   // %s · Stufen %s U/min" % (key, js, key, fs, C['name'], '/'.join(str(int(round(r))) for *_, r in loops)))
    if probe:
        os.makedirs(os.path.join(ROOT, 'tools', 'sounds', '.probe'), exist_ok=True)
        # Hochlauf: Stufen nacheinander, je 1 s, mit Überblendung – nur zum Anhören, nicht im Spiel
        parts = [stage(C, r, seed=3)[0][:SR] for r in np.linspace(lo, hi, 8)]
        wav_write(os.path.join(ROOT, 'tools', 'sounds', '.probe', key + '_stufen.wav'), np.concatenate(parts))
    return loops


if __name__ == '__main__':
    ks = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CARS)
    for k in ks: build(k, '--probe' in sys.argv)
