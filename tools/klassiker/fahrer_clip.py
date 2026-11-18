# Fahrer-Durchdringung bei den Klassikern entfernen (v2.88, Rückmeldung 18.11.2026: „die Figur clippt unter dem Auto“)
#
# Idee: Ein Rumpf-Dreieck des Fahrers, das aus der Karosserie herausragt, hat freie Sicht nach unten bzw. schräg nach außen-unten –
# im echten Auto liegt unter jedem Körperteil der Sitz bzw. Boden. Für jeden Dreiecks-Mittelpunkt werden Strahlen in die untere
# Halbkugel geschossen (Voxel-Gitter der Karosserie, 1 cm). Kommt ein Teil der Strahlen ungehindert aus dem Auto heraus, liegt das
# Dreieck außerhalb der Hülle und wird in modelle/klassiker/fahrer_sicht.json als unsichtbar markiert (fällt im Spiel weg).
# Arme/Hände bleiben (bewegen sich, werden vom Spiel immer gezeichnet).
#
# Ablauf:  1) node tools/klassiker/fahrer_clip_export.js <ordner> schreibt je Team clip_<TEAM>.json (Auto- und Fahrer-Dreiecke im Auto-Raum, siehe Notiz in docs/KLASSIKER.md)
#          2) python tools/klassiker/fahrer_clip.py <ordner mit clip_*.json> [--dry]
import json, sys, glob, os, base64
import numpy as np

VOX = 0.01
YMAX = 0.3   # nur Teile unten am Fahrer (Gesäß, Beine, Fersen), die durch Boden/Unterseite ragen
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SICHT = os.path.join(ROOT, 'modelle', 'klassiker', 'fahrer_sicht.json')


def voxelize(T):
    lo = T.reshape(-1, 3).min(0) - 0.05; hi = T.reshape(-1, 3).max(0) + 0.05
    dim = np.ceil((hi - lo) / VOX).astype(int) + 1
    G = np.zeros(dim, bool)
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    L = np.maximum(np.linalg.norm(b - a, axis=1), np.maximum(np.linalg.norm(c - a, axis=1), np.linalg.norm(c - b, axis=1)))
    n = np.clip(np.ceil(L / (VOX * 0.5)).astype(int), 1, 400)
    for k in np.unique(n):                         # Dreiecke gleicher Teilung gemeinsam abtasten
        sel = n == k; u, v = np.meshgrid(np.arange(k + 1), np.arange(k + 1)); m = u + v <= k; u = u[m] / k; v = v[m] / k
        P = a[sel, None] + (b[sel] - a[sel])[:, None] * u[None, :, None] + (c[sel] - a[sel])[:, None] * v[None, :, None]
        q = np.floor((P.reshape(-1, 3) - lo) / VOX).astype(int); G[q[:, 0], q[:, 1], q[:, 2]] = True
    return G, lo


def dirs():
    D = [[0, -1, 0]]
    for el in (-0.5, -0.8):                       # sin(Elevation): 30° und 53° unter der Waagerechten
        h = np.sqrt(1 - el * el)
        for k in range(16): w = k / 16 * 2 * np.pi; D.append([np.sin(w) * h, el, np.cos(w) * h])
    return np.array(D)


def escape(G, lo, P, D):
    dim = np.array(G.shape); out = np.zeros((len(P), len(D)), bool)
    steps = int(np.ceil(np.linalg.norm(dim) * 1.0 / 0.5)) + 2
    for j, d in enumerate(D):
        hit = np.zeros(len(P), bool); alive = np.ones(len(P), bool)
        for s in range(2, steps):                 # erste 1 cm überspringen (Startpunkt liegt oft auf dem Sitz)
            X = P + d * (s * VOX * 0.5); q = np.floor((X - lo) / VOX).astype(int)
            ins = np.all((q >= 0) & (q < dim), axis=1); idx = alive & ins
            h = np.zeros(len(P), bool); h[idx] = G[q[idx, 0], q[idx, 1], q[idx, 2]]
            hit |= h; alive &= ~h & ins
            if not alive.any(): break
        out[:, j] = ~hit
    return out


def main():
    src = sys.argv[1]; dry = '--dry' in sys.argv
    S = json.load(open(SICHT)); D = dirs(); rep = {}
    for f in sorted(glob.glob(os.path.join(src, 'clip_*.json'))):
        J = json.load(open(f)); key = J['file']
        T = np.array(J['car'], np.float32).reshape(-1, 3, 3); Dr = np.array(J['drv'], np.float32).reshape(-1, 3, 3); arm = np.array(J['arm'], bool)
        G, lo = voxelize(T)
        V = S[key]; bits = np.unpackbits(np.frombuffer(base64.b64decode(V['vis']), np.uint8), bitorder='little')[:len(Dr)].astype(bool)
        cand = np.where(bits & ~arm)[0]
        P = Dr[cand].mean(1); E = escape(G, lo, P, D)
        frac = E.mean(1); bad = cand[((frac >= 0.12) | E[:, 0]) & (P[:, 1] < YMAX)]   # frei nach unten oder in mindestens 4 von 33 Richtungen – nur unterhalb YMAX (Schultern am Cockpitrand bleiben, sonst Löcher)
        rep[key] = dict(sichtbar=int(len(cand)), entfernt=int(len(bad)), y_max=float(Dr[bad].mean(1)[:, 1].max()) if len(bad) else None)
        print(key, rep[key])
        if not dry:
            bits[bad] = False; pad = np.zeros(int(np.ceil(V['n'] / 8)) * 8, bool); pad[:len(bits)] = bits
            V['vis'] = base64.b64encode(np.packbits(pad, bitorder='little').tobytes()).decode(); V['clip'] = int(len(bad))
    if not dry: json.dump(S, open(SICHT, 'w'), separators=(',', ':')); print('geschrieben:', SICHT)
    return rep


if __name__ == '__main__':
    main()
