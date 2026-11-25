"""ACHTUNG (v3.03): unzuverlässig – beim McLaren MP4/13 (gewölbte Lauffläche, 3° Sturz) meldete dieses Verfahren unter 0,3°, bei Lotus und RB8 Neigungen,
die es nicht gibt. Die Werte in HIST_CAR.ax stammen seit v3.03 aus tools/klassiker/radachsen_ringe.py (siehe docs/KLASSIKER.md). Nur noch zum Vergleich.

Echte Radachsen der Klassiker messen (v2.71): Die Räder sind im Modell mit Sturz/Spur eingebaut, das Spiel dreht sie aber um die
waagerechte Querachse -> sie „eierten“ (Ferrari). Je Rad (Stufe 0): Laufflächenpunkte (außerhalb 93 % des Radius um die Radmitte) auswählen, dann die
Achsrichtung suchen, bei der deren Abstand zur Achse am gleichmäßigsten ist (Gitter ±12°, fein nachgesucht). Ausgabe für HIST_CAR.ax.
Aufruf: python tools/klassiker/radachsen.py
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbio import read_glb, accessor, node_matrix
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def axis_of(P, c, R):
    """Laufflächenpunkte = alles außerhalb 93 % des Radius um die Radmitte c (aus extras.wheels); Achse = Richtung mit gleichmäßigstem Abstand."""
    d = P - c; T = P[np.hypot(d[:, 1], d[:, 2]) > 0.93 * R]; q0 = T - T.mean(0); best = None
    for st, rng in [(np.radians(0.25), np.radians(8)), (np.radians(0.02), np.radians(0.3))]:
        cy, cz = (best[1], best[2]) if best else (0, 0)
        for ty in np.arange(cy - rng, cy + rng + 1e-9, st):
            for tz in np.arange(cz - rng, cz + rng + 1e-9, st):
                a = np.array([np.cos(ty) * np.cos(tz), np.sin(ty), np.cos(ty) * np.sin(tz)]); r = np.linalg.norm(q0 - np.outer(q0 @ a, a), axis=1); sd = r.std()
                if best is None or sd < best[0]: best = (sd, ty, tz, a)
    return best

out = {}
for k in ['lotus49c', 'mclaren_mp44', 'ferrari_f2004', 'mclaren_mp413', 'redbull_rb8', 'ferrari_312']:
    js, bn = read_glb(os.path.join(ROOT, 'modelle', 'klassiker', k + '.glb')); N = js['nodes']; res = {}; UD = [n for n in N if n.get('extras', {}).get('wheels')][0]['extras']['wheels']
    def walk(i, M, path):
        n = N[i]; W = M @ node_matrix(n); p = path + [n.get('name', '')]
        if 'mesh' in n and n['name'].startswith('wheel') and 'LOD0' in p:
            P = np.vstack([accessor(js, bn, pr['attributes']['POSITION']).astype(float) for pr in js['meshes'][n['mesh']]['primitives']]) @ W[:3, :3].T + W[:3, 3]
            w = n['name'][6:8]; e = UD[w]; s, ty, tz, a = axis_of(P, np.array([e['x'], e['y'], e['z']]), e['r'])
            res[w] = {'a': [round(float(x), 5) for x in a], 'sturz_grad': round(float(np.degrees(ty)), 2), 'spur_grad': round(float(np.degrees(tz)), 2), 'rest_mm': round(float(s) * 1000, 2)}
            print(k, w, res[w])
        for ch in n.get('children', []): walk(ch, W, p)
    for r in js['scenes'][0]['nodes']: walk(r, np.eye(4), [])
    out[k] = res
json.dump(out, open(os.path.join(ROOT, 'modelle', 'klassiker', 'radachsen.json'), 'w'), indent=1)
