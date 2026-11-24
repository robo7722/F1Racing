#!/usr/bin/env python3
"""Musik für den Trailer analysieren: Tempo, Lautheitsverlauf, Abschnitte (Aufbau/Höhepunkte).
   Aufruf: python3 tools/trailer/musik_analyse.py <Datei.mp3> [...]  [--json Ausgabe.json] [--fein]
   Ausgabe je Lied: Länge, Tempo (BPM), Lautheit je 5-s-Fenster als Balken, stärkste Anstiege (mögliche Schnitt-/Drop-Stellen).
   Braucht librosa (pip install librosa). Liest nur, erzeugt keine Tondateien."""
import sys, json, os, warnings
import numpy as np
warnings.filterwarnings('ignore')
import librosa

def analyse(pfad, fein=False):
    y, sr = librosa.load(pfad, sr=22050, mono=True)
    dauer = len(y) / sr
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=hop)
    tempo = float(np.atleast_1d(tempo)[0]); bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
    # Bass-Anteil (unter 150 Hz) und Höhen (über 4 kHz): zeigt, wo Bass/Schlagzeug einsetzen
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    bass = S[f < 150].sum(0); hoch = S[f > 4000].sum(0)
    def fenster(v, sek):
        n = int(np.ceil(dauer / sek)); out = []
        for k in range(n):
            m = (t >= k * sek) & (t < (k + 1) * sek); out.append(float(np.sqrt(np.mean(v[m] ** 2))) if m.any() else 0.0)
        return np.array(out)
    sek = 2.0 if fein else 5.0
    e = fenster(rms, sek); eb = fenster(np.sqrt(bass), sek); eh = fenster(np.sqrt(hoch), sek)
    db = 20 * np.log10(np.maximum(e, 1e-6)); db -= db.max()
    # stärkste Sprünge der Lautheit (geglättet über 1 s): Kandidaten für Einsatz/Drop
    gl = np.convolve(rms, np.ones(43) / 43, mode='same'); d = np.diff(20 * np.log10(np.maximum(gl, 1e-6)), n=1)
    w = int(1.5 * sr / hop); spr = np.array([gl[min(i + w, len(gl) - 1)] / max(gl[max(i - w, 0)], 1e-6) for i in range(len(gl))])
    sprdb = 20 * np.log10(np.maximum(spr, 1e-6)); kand = []
    for i in np.argsort(-sprdb):
        if all(abs(t[i] - k[0]) > 6 for k in kand): kand.append((float(t[i]), float(sprdb[i])))
        if len(kand) >= 8: break
    kand.sort()
    return dict(datei=os.path.basename(pfad), dauer=dauer, bpm=tempo, schlaege=[round(float(x), 3) for x in bt], sek=sek,
                db=[round(float(x), 1) for x in db], bass=[round(float(x), 3) for x in eb / max(eb.max(), 1e-9)], hoch=[round(float(x), 3) for x in eh / max(eh.max(), 1e-9)],
                anstiege=[(round(a, 1), round(b, 1)) for a, b in kand])

def balken(v, breite=24): return '█' * int(round(max(0.0, min(1.0, v)) * breite))

if __name__ == '__main__':
    a = sys.argv[1:]; fein = '--fein' in a; a = [x for x in a if x != '--fein']
    js = None
    if '--json' in a: i = a.index('--json'); js = a[i + 1]; del a[i:i + 2]
    alle = []
    for p in a:
        try: r = analyse(p, fein)
        except Exception as ex: print('FEHLER', p, ex); continue
        alle.append(r)
        print(f"\n=== {r['datei']}  ·  {r['dauer']:.0f} s  ·  {r['bpm']:.0f} BPM")
        for k, x in enumerate(r['db']):
            print(f"{int(k * r['sek']) // 60}:{int(k * r['sek']) % 60:02d}  {x:6.1f} dB  {balken(1 + x / 30):24s}  Bass {balken(r['bass'][k], 10):10s}  Höhen {balken(r['hoch'][k], 10)}")
        print('Stärkste Anstiege (s, dB):', r['anstiege'])
    if js: json.dump(alle, open(js, 'w'), ensure_ascii=False)
