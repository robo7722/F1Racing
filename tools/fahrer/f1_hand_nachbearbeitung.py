"""Nachbearbeitung von f1fahrer.bin (F1/F2-Fahrer) nach dem Bauskript build_fahrer.py – v1.73.

1. Daumen: Die Faust der Vorlage hat den Daumen gestreckt entlang des Griffs nach oben. Er wird ab dem Grundgelenk um den Griff gelegt
   (vorn auf der Fahrerseite, Spitze nach innen Richtung Tasten) – wie beim echten Griff ans F1-Lenkrad. Arbeitsrahmen ist der Griff im Spiel:
   Lenkrad-Rahmen des F1 (swPos, Drehung 0,45 · π, swS 0,78), Hand mit der Korrektur aus index.html gedreht (F1_FIST: d → d2, Versatz o).
   Der Daumen wird um die Griffachse „gewickelt“: Abstand entlang des Daumens → Winkel um die Achse, Querschnitt bleibt erhalten.
2. Handschuh-Design: aRest der Handschuh-Punkte (sonst ungenutzt, 0) bekommt
   x = Griffseite (1 = Fläche zeigt zur Griffachse: Handfläche, Fingerinnenseiten, Daumenballen), y = Abstand hinter dem Handgelenk Richtung
   Ellbogen (Stulpe/Klettband), z = 1 (Kennung „Daten vorhanden“). Der Shader (kartFahrerMat, F1/F2) zeichnet daraus ein schlichtes Design
   statt der fleckigen Foto-Textur der Vorlage.
3. Normalen der Handschuhe neu (nach dem Biegen).

Aufruf: python tools/fahrer/f1_hand_nachbearbeitung.py [f1fahrer.bin] [--vorschau bild.png] [--spec export.json]
Schreibt die Datei nur einmal um (Kopf-Eintrag "hand": "v1.73"); erneut nur mit --erzwingen auf einer frisch gebauten Datei.
"""
import json, struct, sys, os, heapq
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SW_POS, SW_S = np.array([0, 0.60, 0.665]), 0.78
FIST_C, FIST_D = np.array([0.1939, -0.0161, 0.0380]), np.array([0.1375, 0.9331, 0.3324])
FIST_D2, FIST_O = np.array([-0.08, 1.0, 0.12]), np.array([0.0, -0.022, 0.0])
GRIP_R = 0.0265
# Daumen: Länge ab Spitze (über die Oberfläche, m), die gebogen wird; Übergang zum Ballen
TH_LEN, TH_BLEND = 0.056, 0.012
TH_CLEAR = 0.0045                     # Luft Daumen-Innenseite ↔ Griff (lokal)
TH_EXTRA = 35.0                       # Daumen zusätzlich als Ganzes um die Griffachse zur Fahrerseite gedreht (Grad)


def nrm(v): return v / np.linalg.norm(v)
def rx(a): c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(a): c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rot_between(a, b):
    a, b = nrm(a), nrm(b); v = np.cross(a, b); c = a @ b; vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)


R_W = rx(0.45) @ ry(np.pi)
D, D2 = nrm(FIST_D), nrm(FIST_D2)
Q = rot_between(D, D2)
CC = FIST_C + FIST_O                  # Faustmitte im Spiel (lokal)


def to_game(P):      # Fahrer-Rahmen (rechte Hand, Welt x < 0) -> Lenkrad lokal, Hand korrigiert wie im Spiel
    L = (P - SW_POS) @ R_W / SW_S
    return (L - FIST_C) @ Q.T + CC
def from_game(L):
    L0 = (L - CC) @ Q + FIST_C
    return L0 @ R_W.T * SW_S + SW_POS


def read(path):
    B = open(path, 'rb').read(); hl = struct.unpack('<I', B[:4])[0]; h = json.loads(B[4:4 + hl]); return B, h, 4 + hl


def arr(B, h, b, key, dt, n):
    return np.frombuffer(B, dt, n, b + h[key]).copy()


def geodesic(P, F, src, mask):
    adj = {}
    for f in F:
        if not mask[f].all(): continue
        for a, c in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            w = np.linalg.norm(P[a] - P[c]); adj.setdefault(a, []).append((c, w)); adj.setdefault(c, []).append((a, w))
    dist = {src: 0.0}; pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e9): continue
        for v, w in adj.get(u, []):
            if d + w < dist.get(v, 1e9): dist[v] = d + w; heapq.heappush(pq, (d + w, v))
    out = np.full(len(P), 1e9)
    for k, v in dist.items(): out[k] = v
    return out


def process_hand(P, F, gmask):
    """P: Fahrer-Rahmen, nur die rechte Hand (x < 0) in gmask. Gibt neue Positionen (Fahrer-Rahmen) zurück.
    Daumen liegt in der Vorlage außen am Griff (Winkel ≈ 175°, 0 = innen, 90 = Fahrerseite) und zeigt nach oben (+t). Gewickelt wird er
    um die Griffachse über die Fahrerseite: Höhe über dem Grundgelenk s -> Winkel θ_B − s/r, Winkelversatz im Querschnitt -> Höhe, Radius bleibt."""
    idx = np.where(gmask)[0]; L = to_game(P[idx])
    e1 = np.array([-1.0, 0, 0]); e1 -= D2 * (e1 @ D2); e1 = nrm(e1); e2 = np.cross(D2, e1)   # e1 innen, e2 zum Fahrer
    q = L - CC; t = q @ D2; pr = q - np.outer(t, D2); r = np.linalg.norm(pr, axis=1); ang = np.arctan2(pr @ e2, pr @ e1)
    outer = np.cos(ang) < -0.8                                                                # Außenseite des Griffs (±180° ± 37°)
    tip = idx[outer][np.argmax(t[outer])]                                                     # Daumenspitze: höchster Punkt außen
    gd = geodesic(P, F, tip, gmask)[idx]
    sel = (gd < TH_LEN + TH_BLEND) & (np.cos(ang - np.pi) > 0.55) & (np.sin(ang) > -0.35)   # nur Daumen (außen / außen-Fahrerseite), nicht die Fingerknöchel vorn
    w = np.clip((TH_LEN + TH_BLEND - gd) / TH_BLEND, 0, 1); w = w * w * (3 - 2 * w) * sel
    core = sel & (gd < TH_LEN); base = sel & (np.abs(gd - TH_LEN) < 0.006)
    tB = t[base].mean(); aB = np.arctan2(np.sin(ang[base]).mean(), np.cos(ang[base]).mean()); rc = r[core].mean()
    # Stummel in die Faust einziehen (zum Grundgelenk hin), der neue Daumen (thumb_mesh) deckt die Stelle ab
    Bp = L[base].mean(0)
    Ln = L + (Bp - L) * w[:, None]
    # Zeigefinger-Kuppe ragte spitz über die Faust (vorn-außen, oberhalb t 0,08): flacher an die Faust drücken
    T0 = 0.074; fm = (t > T0) & (np.cos(ang + np.radians(135)) > 0.45) & (w < 0.01)
    Ln[fm] -= np.outer((t[fm] - T0) * 0.92, D2)
    Pn = P.copy(); Pn[idx] = from_game(Ln)
    # Abstand des Daumens zur übrigen Hand (grobe Kollisionsprüfung)
    info = dict(tip=int(tip), tB=round(float(tB), 3), ang_base=round(float(np.degrees(aB)), 1), rB=round(float(np.linalg.norm((Bp - CC) - ((Bp - CC) @ D2) * D2)), 4), n_stummel=int((w > 0.5).sum()))
    return Pn, idx, w, info, dict(tB=float(tB), aB=float(aB), Bp=Bp, e1=e1, e2=e2)


TH_SWEEP, TH_RISE = 105.0, 0.010      # neuer Daumen: Bogen um den Griff (Grad) und Anstieg entlang der Achse (lokal)
TH_RAD = (0.0135, 0.0118, 0.0108)     # Daumenradius Grund / Mitte / Spitze (lokal)
TH_ROOT = (-0.3, 28.0, 0.012, 0.050, 0.0185)   # Daumenwurzel (v1.93): Länge in u, Bogen weiter nach außen (Grad), Versatz Richtung Handgelenk, Abstand zur Griffachse, Dicke


def thumb_mesh(fr, n=36, k=14):
    """Neuer Daumen im Spielrahmen (rechte Hand): Schlauch vom Grundgelenk über die Fahrerseite des Griffs nach innen, runde Kuppe.
    v1.93: Wurzel (u < 0) läuft als Daumenballen in die Hand hinein – Bogen weiter nach außen, tiefer in den Handballen, dicker und
    entlang der Griffachse breiter, hinten geschlossen. Vorher begann der Schlauch frei am Handrücken und wirkte wie ein eigenes Teil.
    Gibt (Punkte, Dreiecke, Längsanteil u je Punkt) zurück."""
    e1, e2 = fr['e1'], fr['e2']; rc = GRIP_R + 0.0045 + TH_RAD[1]
    S = lambda x: (lambda c: c * c * (3 - 2 * c))(np.clip(x, 0, 1))
    def center(u):
        b = S(-u / -TH_ROOT[0]) if u < 0 else 0.0                                  # 0 am Grundgelenk, 1 am Wurzelende
        a = fr['aB'] - np.radians(TH_SWEEP) * u if u >= 0 else fr['aB'] + np.radians(TH_ROOT[1]) * b
        tt = fr['tB'] - 0.004 + TH_RISE * max(u, 0) - TH_ROOT[2] * b; rr = rc + (TH_ROOT[3] - rc) * b
        return CC + tt * D2 + rr * (np.cos(a) * e1 + np.sin(a) * e2)
    us = np.r_[np.linspace(TH_ROOT[0], 0, 8)[:-1], np.linspace(0, 1, n)]; C = np.array([center(u) for u in us])
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    def rad_of(u):
        if u < 0: return TH_RAD[0] + (TH_ROOT[4] - TH_RAD[0]) * S(-u / -TH_ROOT[0])
        return np.interp(u, [0, 0.5, 1], TH_RAD) + (TH_RAD[0] * 0.25) * (1 - S(u / 0.3))   # Ballen läuft weich in den Daumen
    pts, uu = [], []; nr = len(us)
    for i, u in enumerate(us):
        Nv = nrm(np.cross(T[i], D2)); Bv = np.cross(T[i], Nv); r = rad_of(u) * (1.0 if u < 0.85 else np.sqrt(max(0.0, 1 - ((u - 0.85) / 0.15) ** 2)) * 0.85 + 0.15)
        base_r = np.interp(max(u, 0.0), [0, 0.5, 1], TH_RAD) if u >= 0 else TH_RAD[0]; rd = C[i] - CC; rd -= (rd @ D2) * D2; rd = nrm(rd)
        Ci = C[i] + (rad_of(u) - base_r) * rd                                       # dicker nur nach außen: Innenseite (zum Griff) bleibt wo sie war
        sb = 1.0 + 0.35 * (S(-u / -TH_ROOT[0]) if u < 0 else (1 - S(u / 0.3)))      # Wurzel entlang der Griffachse breiter (Ballen statt Rohr)
        for j in range(k):
            a = j / k * 2 * np.pi; pts.append(Ci + r * (np.cos(a) * Nv * 0.85 + np.sin(a) * Bv * sb)); uu.append(max(u, 0.0))   # leicht flach (Daumenballen-Seite)
    tip = C[-1] + T[-1] * TH_RAD[2] * 0.6; pts.append(tip); uu.append(1.0)
    root = C[0] - T[0] * TH_ROOT[4] * 0.5; pts.append(root); uu.append(0.0)
    F = []
    for i in range(nr - 1):
        for j in range(k):
            a0 = i * k + j; a1 = i * k + (j + 1) % k; b0 = a0 + k; b1 = a1 + k; F += [(a0, b0, a1), (a1, b0, b1)]
    ti, ri = len(pts) - 2, len(pts) - 1
    for j in range(k): F.append(((nr - 1) * k + j, ti, (nr - 1) * k + (j + 1) % k))
    for j in range(k): F.append((j, (j + 1) % k, ri))                              # Wurzel geschlossen
    return np.array(pts), np.array(F), np.array(uu)


def vertex_normals(P, F, mask):
    N = np.zeros_like(P); fm = mask[F].all(1); Fg = F[fm]
    fn = np.cross(P[Fg[:, 1]] - P[Fg[:, 0]], P[Fg[:, 2]] - P[Fg[:, 0]])
    for k in range(3): np.add.at(N, Fg[:, k], fn)
    key = np.round(P / 1e-5).astype(np.int64); _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel()   # Nähte zusammenführen
    S = np.zeros((inv.max() + 1, 3)); np.add.at(S, inv, N); N = S[inv]
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]; path = args[0] if args else os.path.join(ROOT, 'f1fahrer.bin')
    opt = {sys.argv[i]: (sys.argv[i + 1] if i + 1 < len(sys.argv) else None) for i in range(1, len(sys.argv)) if sys.argv[i].startswith('--')}
    B, h, b = read(path); nv = h['nv']
    if h.get('hand') == 'v1.73' and '--erzwingen' not in opt and '--vorschau' not in opt:
        print('schon nachbearbeitet (hand v1.73) – nichts zu tun'); return
    P = arr(B, h, b, 'pos', np.float32, nv * 3).reshape(-1, 3).astype(np.float64); Nn = arr(B, h, b, 'nrm', np.float32, nv * 3).reshape(-1, 3)
    reg = arr(B, h, b, 'reg', np.uint8, nv); rest = arr(B, h, b, 'rest', np.float32, nv * 3).reshape(-1, 3)
    F = np.frombuffer(B, np.uint32 if h.get('i32') else np.uint16, h['ni'], b + h['idx']).reshape(-1, 3).astype(int)
    uv = arr(B, h, b, 'uv', np.float32, nv * 2).reshape(-1, 2); ry = arr(B, h, b, 'ry', np.float32, nv); rn = arr(B, h, b, 'rn', np.int8, nv * 3).reshape(-1, 3)
    bi = arr(B, h, b, 'bi', np.uint8, nv * 4).reshape(-1, 4); bw = arr(B, h, b, 'bw', np.uint8, nv * 4).reshape(-1, 4)
    glove = reg == 3; M = np.diag([-1.0, 1, 1]); out = P.copy(); infos = []; add = []
    for sx in (1, -1):    # rechte Hand (Welt x < 0) direkt, linke gespiegelt
        Pm = P @ M if sx < 0 else P; gm = glove & (Pm[:, 0] < 0)
        Pn, idx, w, info, fr = process_hand(Pm, F, gm); infos.append(info)
        out[idx] = (Pn[idx] @ M) if sx < 0 else Pn[idx]
        tp, tf, tu = thumb_mesh(fr); tpw = from_game(tp); tpw = tpw @ M if sx < 0 else tpw
        if sx > 0: tf = tf[:, ::-1]                                               # Umlaufsinn: Normalen nach außen (gespiegelte Hand dreht ihn ohnehin um)
        k_ = bw[idx].argmax(1); bone = np.bincount(bi[idx, k_][bw[idx, k_] > 200]).argmax()   # Handknochen dieser Hand (stärkstes Gewicht)
        add.append((tpw, tf, tu, int(bone), idx))
    # neue Daumen anhängen (Handschuh, starr am Handknochen)
    P2, F2, nv2 = [out], [F], nv
    for tpw, tf, tu, bone, idx in add:
        P2.append(tpw); F2.append(tf + nv2)
        uvn = np.c_[0.75 + 0.2 * tu, 0.5 + 0.2 * np.linspace(0, 1, len(tu))]
        uv = np.vstack([uv, uvn]); reg = np.concatenate([reg, np.full(len(tpw), 3, np.uint8)]); ry = np.concatenate([ry, np.full(len(tpw), -1.0, np.float32)])
        rest = np.vstack([rest, np.zeros((len(tpw), 3), np.float32)]); rn = np.vstack([rn, np.zeros((len(tpw), 3), np.int8)])
        bi = np.vstack([bi, np.tile(np.array([bone, 0, 0, 0], np.uint8), (len(tpw), 1))]); bw = np.vstack([bw, np.tile(np.array([255, 0, 0, 0], np.uint8), (len(tpw), 1))])
        nv2 += len(tpw)
    out = np.vstack(P2); F = np.vstack(F2); glove = reg == 3; Nn = np.vstack([Nn, np.zeros((nv2 - nv, 3), np.float32)])
    N = vertex_normals(out, F, glove); Nn[glove] = N[glove]
    # Griffseite: Normale zeigt zur Griffachse (im Spielrahmen); Abstand hinter dem Handgelenk Richtung Ellbogen
    sh, el, wr = [np.array(a_) for a_ in h['arm']]
    for sx in (1, -1):
        Pm = out @ M if sx < 0 else out; Nm = Nn @ M if sx < 0 else Nn; gm = glove & (Pm[:, 0] < 0); idx = np.where(gm)[0]
        L = to_game(Pm[idx]); Nl = (Nm[idx] @ R_W) @ Q.T
        q = L - CC; t = q @ D2; pr = q - np.outer(t, D2); rd = pr / (np.linalg.norm(pr, axis=1, keepdims=True) + 1e-9)
        pad = np.clip(-(Nl * rd).sum(1), 0, 1) * (np.linalg.norm(pr, axis=1) < 0.075)
        fa = nrm(el - wr); cw = (Pm[idx] - wr) @ fa
        rest[idx, 0] = pad; rest[idx, 1] = cw; rest[idx, 2] = 1.0
    for i, inf in enumerate(infos): print(('rechte' if i == 0 else 'linke') + ' Hand:', inf)
    if '--spec' in opt and opt['--spec']:
        sys.path.insert(0, os.path.join(ROOT, 'tools', 'lenkrad')); from check_lenkrad import wheel_sdf
        spec = json.load(open(opt['--spec']))['spec']
        K = np.array([[0, -D2[2], D2[1]], [D2[2], 0, -D2[0]], [-D2[1], D2[0], 0]])
        for roll in (-20, 0, 20):
            a_ = np.radians(roll); Rr = np.eye(3) + np.sin(a_) * K + (1 - np.cos(a_)) * K @ K
            for sx in (1, -1):
                Pm = out @ M if sx < 0 else out; gm = glove & (Pm[:, 0] < 0); L = to_game(Pm[gm])
                d = wheel_sdf((L - CC) @ Rr.T + CC, spec)
                print(f'Rolle {roll:+d}° Hand {"R" if sx > 0 else "L"}: kleinster Abstand zum Lenkrad {d.min() * SW_S * 1000:+.1f} mm')
    if '--vorschau' in opt and opt['--vorschau']:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        gm = glove & (out[:, 0] < 0); L1 = to_game(out[gm]); pd = rest[gm, 0]
        fig, ax = plt.subplots(1, 3, figsize=(21, 7))
        for a_, (i, j, tt) in zip(ax, [(0, 1, 'vorn x-y'), (2, 1, 'Seite z-y'), (0, 2, 'oben x-z')]):
            a_.scatter(L1[:, i], L1[:, j], c=pd, s=4, cmap='viridis'); a_.set_aspect('equal'); a_.grid(True); a_.set_title('nachher ' + tt)
            tg = np.linspace(-0.12, 0.1, 30); gp = CC + np.outer(tg, D2); a_.plot(gp[:, i], gp[:, j], 'r-')
        plt.savefig(opt['--vorschau'], dpi=55); print('Vorschau', opt['--vorschau'])
        if '--schreiben' not in opt: return
    # neu schreiben (alle Felder, Versätze neu, 4-Byte-ausgerichtet)
    h2 = dict(h); h2['hand'] = 'v1.73'; h2['nv'] = int(nv2); h2['ni'] = int(F.size); i32 = nv2 > 65535; h2['i32'] = i32
    parts = [('pos', out.astype(np.float32)), ('nrm', Nn.astype(np.float32)), ('uv', uv.astype(np.float32)), ('reg', reg.astype(np.uint8)), ('ry', ry.astype(np.float32)),
             ('rest', rest.astype(np.float32)), ('rn', rn.astype(np.int8)), ('bi', bi.astype(np.uint8)), ('bw', bw.astype(np.uint8)), ('idx', F.astype(np.uint32 if i32 else np.uint16))]
    data = bytearray()
    for key, a_ in parts:
        while len(data) % 4: data.append(0)
        h2[key] = len(data); data += np.ascontiguousarray(a_).tobytes()
    hj = json.dumps(h2, separators=(',', ':')).encode()
    while (4 + len(hj)) % 4: hj += b' '
    open(path, 'wb').write(struct.pack('<I', len(hj)) + hj + bytes(data)); print('geschrieben', path, 'Punkte', nv, '->', nv2)


if __name__ == '__main__':
    main()
