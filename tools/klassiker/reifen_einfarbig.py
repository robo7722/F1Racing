#!/usr/bin/env python3
"""Reifen eines Klassikers (GLB) einfarbig dunkel machen: eingebackene Eckenfarben auf Flanke und Lauffläche durch ein gleichmäßiges Gummi-Schwarz ersetzen.

Anlass (v3.02, 25.11.2026, McLaren MP4/13): „Reifentexturen eiern“. Der Reifen hat im Modell keine Textur, sondern Eckenfarben. Auf der Flanke
(55–80 % des Radius) lagen dort helle Flecken – Reste der weißen Reifenbeschriftung des Originals, auf das grobe Netz gebacken. Beim Drehen liefen
diese unregelmäßigen Flecken sichtbar um die Achse. Felge und Nabe (innerhalb von 55 % des Radius) bleiben unverändert.

Aufruf: python3 tools/klassiker/reifen_einfarbig.py <modell.glb> [--ab 0.55] [--grau 9] [--material farbe_lack_matt] [--pruefen]
  --ab       ab welchem Anteil des Radradius eine Ecke zum Reifen zählt (Felgenrand)
  --grau     neuer Farbwert 0–255 (linear), Standard 9 ≈ sehr dunkles Gummi
  --pruefen  nur messen und ausgeben, nichts schreiben
Die Datei wird an Ort und Stelle geändert (gleiche Größe, nur Farbwerte). Danach die Modell-Version in index.html erhöhen (…glb?v=).
"""
import sys, json, struct
import numpy as np
a = sys.argv[1:]
def opt(k, d): return type(d)(a[a.index(k) + 1]) if k in a else d
ab, grau, mname, pruefen, pfad = opt('--ab', 0.55), opt('--grau', 9), opt('--material', 'farbe_lack_matt'), '--pruefen' in a, a[0]
b = bytearray(open(pfad, 'rb').read()); jl = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + jl]); B0 = 20 + jl + 8
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5122: np.int16, 5121: np.uint8, 5120: np.int8}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
def lage(i):
    ac = J['accessors'][i]; v = J['bufferViews'][ac['bufferView']]; nc = NC[ac['type']]; dt = np.dtype(CT[ac['componentType']])
    return B0 + v.get('byteOffset', 0) + ac.get('byteOffset', 0), v.get('byteStride') or dt.itemsize * nc, ac['count'], nc, dt
def lies(i):
    o, st, n, nc, dt = lage(i); return np.array([np.frombuffer(b, dt, nc, o + k * st) for k in range(n)], dtype=np.float64)
netze = sorted({n['mesh'] for n in J['nodes'] if n.get('name', '').startswith('wheel_') and 'mesh' in n}); geaendert = 0
for mi in netze:
    for p in J['meshes'][mi]['primitives']:
        if J['materials'][p['material']].get('name') != mname or 'COLOR_0' not in p['attributes']: continue
        P = lies(p['attributes']['POSITION']); mitte = (P[:, 1:].max(0) + P[:, 1:].min(0)) / 2; r = np.hypot(P[:, 1] - mitte[0], P[:, 2] - mitte[1]); r /= r.max()
        o, st, n, nc, dt = lage(p['attributes']['COLOR_0']); assert dt == np.uint8, 'nur 8-Bit-Farben'
        C = np.array([np.frombuffer(b, dt, nc, o + k * st) for k in range(n)]); reifen = r >= ab
        print(f'Netz {mi}: {int(reifen.sum())} von {n} Ecken im Reifen, Farbe bisher {C[reifen, :3].min()}–{C[reifen, :3].max()} (Mittel {C[reifen, :3].mean():.1f})')
        if not pruefen:
            for k in np.nonzero(reifen)[0]: b[o + k * st:o + k * st + 3] = bytes([grau, grau, min(255, grau + 1)])
            geaendert += int(reifen.sum())
if not pruefen: open(pfad, 'wb').write(b); print(f'{geaendert} Ecken auf {grau} gesetzt → {pfad}')
