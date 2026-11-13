"""Roadster-Modell (roadcar.bin) lesen und Strahlen entlang einer Achse auf die Karosserie werfen."""
import json, struct, os
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
def laden(mats=('carpaint',)):
    b = open(os.path.join(ROOT, 'roadcar.bin'), 'rb').read(); hl = struct.unpack('<I', b[:4])[0]; h = json.loads(b[4:4 + hl]); base = 4 + hl; out = []
    for c in h['parts']:
        if c['m'] not in mats or c.get('w', -1) >= 0: continue
        q = np.frombuffer(b, np.int16, c['nv'] * 3, base + c['pos']).reshape(-1, 3).astype(float); P = np.array(c['min']) + (q + 32768) / 65535 * np.array(c['rg'])
        I = np.frombuffer(b, np.uint32 if c.get('i32') else np.uint16, c['ni'], base + c['idx']).reshape(-1, 3).astype(int); out.append(P[I])
    return np.concatenate(out)     # (Dreiecke, 3 Ecken, xyz)
# Blickrichtungen: Achse a (0 = x, 1 = y, 2 = z), s = Seite, von der man schaut; u/v = Bildachsen (rechts, oben) als (Achse, Vorzeichen)
SICHT = {'L': (0, 1, (2, -1), (1, 1)), 'R': (0, -1, (2, 1), (1, 1)), 'T': (1, 1, (0, 1), (2, -1)), 'F': (2, 1, (0, 1), (1, 1)), 'B': (2, -1, (0, -1), (1, 1)), 'Z': (2, 1, (0, 1), (1, 1))}
def treffer(T, sicht, pu, pv):
    """Punkte (pu, pv) in Bildkoordinaten der Sicht -> (Punkt xyz, Normale, getroffen) der vordersten Fläche."""
    a, s, (ua, us), (va, vs) = SICHT[sicht]; n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); ln = np.linalg.norm(n, axis=1); ok = ln > 1e-12; T = T[ok]; n = n[ok] / ln[ok, None]
    f = n[:, a] * s > 0.02; T = T[f]; n = n[f]
    A = np.stack([T[:, :, ua] * us, T[:, :, va] * vs], 2); D = T[:, :, a] * s      # 2D-Ecken und Tiefe (groß = nah am Betrachter)
    best = np.full(len(pu), -1e9); bn = np.zeros((len(pu), 3)); mn = A.min(1); mx = A.max(1)
    for i in range(len(pu)):
        p = np.array([pu[i], pv[i]]); c = np.nonzero((mn[:, 0] <= p[0]) & (mx[:, 0] >= p[0]) & (mn[:, 1] <= p[1]) & (mx[:, 1] >= p[1]))[0]
        if not len(c): continue
        a0, a1, a2 = A[c, 0], A[c, 1], A[c, 2]; v0 = a1 - a0; v1 = a2 - a0; v2 = p - a0; den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
        with np.errstate(divide='ignore', invalid='ignore'):
            w1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den; w2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
        ins = (np.abs(den) > 1e-14) & (w1 >= -1e-6) & (w2 >= -1e-6) & (w1 + w2 <= 1 + 1e-6)
        if not ins.any(): continue
        d = D[c, 0] + w1 * (D[c, 1] - D[c, 0]) + w2 * (D[c, 2] - D[c, 0]); d[~ins] = -1e9; k = d.argmax(); best[i] = d[k]; bn[i] = n[c[k]]
    hit = best > -1e8; X = np.zeros((len(pu), 3)); X[:, ua] = np.asarray(pu) * us; X[:, va] = np.asarray(pv) * vs; X[:, a] = best * s
    return X, bn, hit
