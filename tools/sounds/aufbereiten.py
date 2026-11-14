"""Aufbereitung der ElevenLabs-Sounds (sounds/roh/*.mp3) für das Spiel – siehe docs/SOUNDS.md.

Motor-Loops: stabilen Abschnitt ausschneiden (Tonhöhe konstant, ohne Ein-/Ausblenden der Aufnahme), Übergang Ende→Anfang
gleich laut überblenden (0,25 s), auf gleiche Lautheit (RMS) bringen, als WAV (16 bit, mono, 32 kHz) speichern.
WAV statt MP3: MP3 fügt am Anfang Stille ein (Encoder-Verzögerung) – beim Loopen knackt es dann alle 3 s.
Grundton (Hz) des fertigen Loops wird gemessen und ausgegeben (Autokorrelation) – Wert gehört in SND_ENG in index.html.

Crash: leiser Vorlauf bis zum Einsatz abgeschnitten, Spitzenpegel auf -1 dBFS, mono, MP3 128 kbit/s (Einzelschuss, die Encoder-Verzögerung stört dort nicht).

Aufruf: python tools/sounds/aufbereiten.py
"""
import os, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROH, OUT = os.path.join(ROOT, 'sounds', 'roh'), os.path.join(ROOT, 'sounds')
SR = 32000
# Datei: (Anfang s, Ende s) des stabilen Abschnitts in der Rohaufnahme
LOOPS = {
    'f1_mittel': (0.40, 3.60),
    'f1_hoch': (0.40, 3.60),
    'f2_mittel': (1.00, 2.75),   # Rohaufnahme schwankt 230–264 Hz, 1,0–2,75 s stabil um 255 Hz
    'f2_hoch': (1.25, 3.30),     # Rohaufnahme steigt 513→573 Hz und blendet am Ende aus; 1,25–3,3 s: 551–573 Hz
    'kart_mittel': (0.40, 2.90),
    'kart_hoch': (0.75, 3.60),
}
CRASH = ['crash_auto', 'crash_wand', 'crash_schwer', 'crash_kart']
XF = 0.25            # Überblendung am Loop-Übergang (s)
RMS = 0.14           # Ziel-Lautheit der Loops


def load(path, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'quiet', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def save_wav(path, x, sr=SR):
    pcm = np.clip(np.round(x * 32767), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def loop(x, xf):
    """Nahtloser Loop der Länge len(x)-xf: Anfang mit dem Stück hinter dem Ende gleich laut überblenden."""
    n = len(x) - xf; y = x[:n].copy(); t = np.linspace(0, 1, xf)
    y[:xf] = x[:xf] * np.sin(t * np.pi / 2) + x[n:n + xf] * np.cos(t * np.pi / 2)
    return y


def pitch(x, sr=SR):
    y = sosfilt(butter(4, [60, 3000], 'band', fs=sr, output='sos'), x); out = []
    for s in np.arange(0.1, len(x) / sr - 0.2, 0.25):
        seg = y[int(s * sr):int(s * sr) + 4096]; seg = seg - seg.mean()
        if len(seg) < 4096: break
        ac = np.correlate(seg, seg, 'full')[4095:]; ac /= ac[0] + 1e-9
        lo, hi = int(sr / 2500), int(sr / 60); out.append(sr / (lo + np.argmax(ac[lo:hi])))
    return np.array(out)


def main():
    for name, (a, b) in LOOPS.items():
        x = load(os.path.join(ROH, name + '.mp3'))[int(a * SR):int(b * SR)]
        y = loop(x, int(XF * SR)); y *= RMS / np.sqrt(np.mean(y ** 2)); pk = np.abs(y).max()
        if pk > 0.98: y *= 0.98 / pk
        save_wav(os.path.join(OUT, name + '.wav'), y)
        p = pitch(y); naht = abs(y[-1] - y[0])
        print(f'{name}.wav  {len(y) / SR:.2f} s  Tonhöhe Median {np.median(p):.0f} Hz (Werte {np.round(p).astype(int).tolist()})  Naht-Sprung {naht:.3f}')
    for name in CRASH:
        src = os.path.join(ROH, name + '.mp3'); x = load(src, 44100); g = 0.89 / np.abs(x).max()
        # Einsatz: erster Zeitpunkt, an dem die Hüllkurve (5 ms) 25 % ihres Maximums erreicht – davor (leiser Vorlauf) abschneiden, sonst kommt der Schlag im Spiel verspätet
        w = 220; env = np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')); on = max(0, int(np.argmax(env > 0.25 * env.max())) - 220)
        subprocess.run(['ffmpeg', '-v', 'quiet', '-y', '-ss', f'{on / 44100:.4f}', '-i', src, '-ac', '1', '-af', f'volume={g:.4f},afade=t=in:d=0.004', '-b:a', '128k', os.path.join(OUT, name + '.mp3')], check=True)
        print(f'{name}.mp3  {len(x) / 44100:.2f} s  Einsatz nach {on / 44.1:.0f} ms abgeschnitten  Verstärkung {g:.2f}')


if __name__ == '__main__':
    main()
