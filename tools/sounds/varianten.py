"""Tonhöhen-Varianten der Motor-Loops und „Gas weg“-Loops (v1.99) – siehe docs/SOUNDS.md und docs/SOUNDS-REALISMUS.md.

Warum: Ab v1.99 spielt das Spiel die Motoren in echter Zündfrequenz (F1/F2: U/min ÷ 20, Kart: U/min ÷ 60). Die ElevenLabs-Aufnahmen
liegen aber tief (230–280 Hz ≈ 4.600–5.600 U/min beim V6). Würde das Spiel sie per playbackRate bis 2,4-fach hochstimmen, wanderten
die Auspuff-Resonanzen mit („Spielzeugmotor“). Deshalb hier offline mit Rubberband (Formanten bleiben erhalten) mehrere Stufen
erzeugen; im Spiel muss jede Stufe dann nur noch ~0,8–1,25-fach nachgestimmt werden.

Ablauf je Variante: fertigen (nahtlosen) Spiel-Loop 3× hintereinander → Rubberband (pitch, formant=preserved) → mittleres Drittel
herausnehmen, Naht 0,12 s gleich laut überblenden → gleiche Lautheit (RMS 0,14) → WAV mono 32 kHz. Danach Grundton messen.

„Gas weg“ (Rohaufnahmen sounds/roh/kart_schub.mp3, v6_schub.mp3): stabilen Abschnitt ausschneiden, als Loop überblenden, beim V6
zusätzlich +8 Halbtöne (Rohaufnahme ≈ 242 Hz).

Aufruf: python tools/sounds/varianten.py   (braucht ffmpeg mit rubberband-Filter und numpy)
"""
import os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SND = os.path.join(ROOT, 'sounds'); SR = 32000; RMS = 0.14

# Ziel-Datei: (Quelle in sounds/, Halbtöne)
VAR = {
    'f1_v2': ('f1_mittel.wav', 7),     # 230 -> ~345 Hz ≈ 6.900 U/min
    'f1_v3': ('f1_hoch.wav', 9),       # 260 -> ~437 Hz ≈ 8.700 U/min
    'f1_v4': ('f1_hoch.wav', 13),      # 260 -> ~551 Hz ≈ 11.000 U/min
    'f2_v2': ('f2_mittel.wav', 5),     # 255 -> ~340 Hz ≈ 6.800 U/min
    'f2_v3': ('f2_hoch.wav', -4),      # 556 -> ~441 Hz ≈ 8.800 U/min
    'kart_v0': ('kart_mittel.wav', -12),  # 156 -> ~78 Hz ≈ 4.700 U/min
    'kart_v1': ('kart_mittel.wav', -7),   # 156 -> ~104 Hz ≈ 6.250 U/min
    'kart_v3': ('kart_hoch.wav', 4),      # 177 -> ~223 Hz ≈ 13.400 U/min
}
# Gas weg: Ziel: (Rohdatei, Anfang s, Ende s, Halbtöne)
SCHUB = {'kart_schub': ('kart_schub.mp3', 0.0, 1.0, 0), 'v6_schub': ('v6_schub.mp3', 0.0, 1.3, 8)}


def load(path, af=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-i', path] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).astype(np.float64)


def save(path, x):
    pcm = np.clip(np.round(x * 32767), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def shift(x, st):
    if st == 0: return x
    tmp = os.path.join(SND, '_tmp.wav'); save(tmp, x / max(1.0, np.abs(x).max()))
    try: return load(tmp, f'rubberband=pitch={2 ** (st / 12):.6f}:formant=preserved:pitchq=quality')
    finally: os.remove(tmp)


def seam(y, n, xf):
    """Ausschnitt y[n:2n] als Loop: Anfang mit dem Stück hinter dem Ende gleich laut überblenden."""
    out = y[n:2 * n].copy(); t = np.linspace(0, 1, xf)
    out[:xf] = y[n:n + xf] * np.sin(t * np.pi / 2) + y[2 * n:2 * n + xf] * np.cos(t * np.pi / 2)
    return out


def pitch(x):
    """stärkste Periode (Autokorrelation, 60–3000 Hz) – entspricht dem Grundton, den das Ohr hört."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < 60) | (f > 3000)] = 0; y = np.fft.irfft(X, len(x))
    res = []
    for s in range(0, len(y) - 8192, 4096):
        seg = y[s:s + 8192]; a = np.correlate(seg, seg, 'full')[8191:]; a /= a[0] + 1e-9
        lo, hi = int(SR / 2500), int(SR / 40); res.append(SR / (lo + np.argmax(a[lo:hi])))
    return float(np.median(res))


def norm(x): return x * RMS / np.sqrt(np.mean(x ** 2))


if __name__ == '__main__':
    for name, (src, st) in VAR.items():
        x = load(os.path.join(SND, src)); n = len(x)
        y = shift(np.concatenate([x, x, x]), st)
        out = norm(seam(y, n, int(0.12 * SR)))
        save(os.path.join(SND, name + '.wav'), out)
        print(f'{name}: {src} {st:+d} HT, {n / SR:.2f} s, Grundton {pitch(out):.0f} Hz')
    for name, (src, a, b, st) in SCHUB.items():
        x = load(os.path.join(SND, 'roh', src))[int(a * SR):int(b * SR)]
        x = shift(x, st); xf = int(0.15 * SR); n = len(x) - xf
        t = np.linspace(0, 1, xf); out = x[:n].copy(); out[:xf] = x[:xf] * np.sin(t * np.pi / 2) + x[n:n + xf] * np.cos(t * np.pi / 2)
        out = norm(out); save(os.path.join(SND, name + '.wav'), out)
        print(f'{name}: {src} {a}-{b} s {st:+d} HT, {n / SR:.2f} s, Grundton {pitch(out):.0f} Hz')
