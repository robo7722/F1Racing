"""Clipping-Prüfung F1/F2-Lenkrad: Hände/Arme/Körper des Fahrers und Karosserie gegen das Lenkrad, über den ganzen Lenkbereich.

Eingabe: Export aus dem Spiel (tools/lenkrad/export.cjs) + f1fahrer.bin. Das Lenkrad wird als Abstandsfunktion aus SW.spec aufgebaut
(Mittelteil mit Fase, Griffrohre, Tasten, Drehschalter, Wippen, Nabe); negativ = Punkt liegt im Lenkrad.
Aufruf: python tools/lenkrad/check_lenkrad.py lenkrad_export.json [f1fahrer.bin]
Ausgabe je Fall (F1, F1-TV, F2, F2-TV): kleinster Abstand je Gruppe in mm (Weltmaß), schlimmster Lenkeinschlag, Handrolle.
"""
import json, struct, sys, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_bin(path):
    B = open(path, 'rb').read(); hl = struct.unpack('<I', B[:4])[0]; h = json.loads(B[4:4 + hl]); b = 4 + hl; nv = h['nv']
    P = np.frombuffer(B, np.float32, nv * 3, b + h['pos']).reshape(-1, 3).astype(np.float64)
    reg = np.frombuffer(B, np.uint8, nv, b + h['reg'])
    bi = np.frombuffer(B, np.uint8, nv * 4, b + h['bi']).reshape(-1, 4).astype(int)
    bw = np.frombuffer(B, np.uint8, nv * 4, b + h['bw']).reshape(-1, 4) / 255.0
    F = np.frombuffer(B, np.uint32 if h.get('i32') else np.uint16, h['ni'], b + h['idx']).reshape(-1, 3).astype(int)
    return P, reg, bi, bw, F


def mids(F):
    """Flächen- und Kantenmitten (zusätzlich zu den Eckpunkten, aus den verformten Eckpunkten gemischt)."""
    a, b, c = F[:, 0], F[:, 1], F[:, 2]
    return [(a, b, c, 1 / 3, 1 / 3, 1 / 3), (a, b, c, .5, .5, 0), (a, b, c, 0, .5, .5), (a, b, c, .5, 0, .5)]


def poly_sdf(px, py, pts):
    """2D-Abstand zu geschlossenem Polygon, negativ innen."""
    V = np.asarray(pts); n = len(V); d = np.full(px.shape, np.inf); s = np.ones(px.shape)
    for i in range(n):
        a, b = V[i], V[(i + 1) % n]; e = b - a; wx, wy = px - a[0], py - a[1]
        t = np.clip((wx * e[0] + wy * e[1]) / (e @ e), 0, 1); dx, dy = wx - e[0] * t, wy - e[1] * t
        d = np.minimum(d, dx * dx + dy * dy)
        c1 = py >= a[1]; c2 = py < b[1]; c3 = e[0] * wy > e[1] * wx
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3); s[flip] *= -1
    return s * np.sqrt(d)


def comb(d2, dz):
    return np.sqrt(np.maximum(d2, 0) ** 2 + np.maximum(dz, 0) ** 2) + np.minimum(np.maximum(d2, dz), 0)


def seg_dist(Q, pts):
    A = np.asarray(pts)[:-1]; Bv = np.asarray(pts)[1:]; best = np.full(len(Q), np.inf)
    for k in range(0, len(Q), 4000):
        q = Q[k:k + 4000, None, :]; e = (Bv - A)[None]; t = np.clip(((q - A[None]) * e).sum(-1) / (e * e).sum(-1), 0, 1)
        best[k:k + 4000] = np.linalg.norm(q - (A[None] + e * t[..., None]), axis=-1).min(1)
    return best


BOX = np.array([[-0.26, -0.17, -0.08], [0.26, 0.17, 0.12]])   # Hüllkasten des Lenkrads (lokal): Punkte außerhalb sind sicher frei


def wheel_sdf(Q, spec, parts=False):
    inb = ((Q > BOX[0]) & (Q < BOX[1])).all(1)
    if not inb.all():
        D = np.full(len(Q), 0.05); Pi = np.zeros(len(Q), int)
        if inb.any():
            r = wheel_sdf(Q[inb], spec, True); D[inb] = r[0]; Pi[inb] = r[1]
        return (D, Pi) if parts else D
    out = []
    for s in spec:
        x, y, z = Q[:, 0], Q[:, 1], Q[:, 2]
        if s['t'] == 'ext':
            pre = (np.abs(x) < 0.25) & (np.abs(y) < 0.2) & (z > -0.1) & (z < 0.15); d = np.full(len(Q), 1.0)
            d[pre] = comb(poly_sdf(x[pre], y[pre], s['pts']), np.maximum(s['z0'] - z[pre], z[pre] - s['z1'])) - s['r']
        elif s['t'] == 'tube':
            pre = np.linalg.norm(Q - np.mean(s['pts'], 0), axis=1) < 0.4; d = np.full(len(Q), 1.0); d[pre] = seg_dist(Q[pre], s['pts']) - s['r']
        elif s['t'] == 'cyl':
            d = comb(np.hypot(x - s['x'], y - s['y']) - s['r'], np.maximum(s['z0'] - z, z - s['z1']))
        elif s['t'] == 'box':
            c, hh, rz = np.array(s['c']), np.array(s['h']), s.get('rz', 0) or 0; q = Q - c; cr, sr = np.cos(-rz), np.sin(-rz)
            q = np.stack([q[:, 0] * cr - q[:, 1] * sr, q[:, 0] * sr + q[:, 1] * cr, q[:, 2]], 1); e = np.abs(q) - hh
            d = np.linalg.norm(np.maximum(e, 0), axis=1) + np.minimum(e.max(1), 0)
        out.append(d)
    D = np.stack(out, 1)
    return (D.min(1), D.argmin(1)) if parts else D.min(1)


def tub_inside(Q, T, cell=0.01):
    """Punkte im Material der Cockpitwanne (geschlossenes Netz): Strahl von der Mitte weg nach außen (±x), ungerade Zahl Treffer = innen."""
    yz = T[:, :, 1:]; lo = yz.min(1); hi = yz.max(1); grid = {}
    for k in range(len(T)):
        for gy in range(int(np.floor(lo[k, 0] / cell)), int(np.floor(hi[k, 0] / cell)) + 1):
            for gz in range(int(np.floor(lo[k, 1] / cell)), int(np.floor(hi[k, 1] / cell)) + 1): grid.setdefault((gy, gz), []).append(k)
    cnt = np.zeros(len(Q), int); keys = np.floor(Q[:, 1:] / cell).astype(int)
    for key in set(map(tuple, keys)):
        tk = grid.get(key)
        if not tk: continue
        m = (keys[:, 0] == key[0]) & (keys[:, 1] == key[1]); q = Q[m]; t = T[tk]
        a, b, c = t[:, 0], t[:, 1], t[:, 2]
        # Schnitt der Geraden (y, z fest) mit der Dreiecksebene über baryzentrische Koordinaten in der y-z-Ebene
        v0 = (b - a)[:, 1:]; v1 = (c - a)[:, 1:]; den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]; ok = np.abs(den) > 1e-12
        w = q[:, None, 1:] - a[None, :, 1:]
        u = (w[..., 0] * v1[:, 1] - v1[:, 0] * w[..., 1]) / np.where(ok, den, 1); v = (v0[:, 0] * w[..., 1] - w[..., 0] * v0[:, 1]) / np.where(ok, den, 1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1); xh = a[:, 0] + (b - a)[:, 0] * u + (c - a)[:, 0] * v
        sg = np.sign(q[:, 0:1]); sg[sg == 0] = 1; out = hit & (xh * sg > q[:, 0:1] * sg)
        cnt[m] = out.sum(1)
    return cnt % 2 == 1


def rx(a): c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(a): c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rz(a): c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def to_local(Pc, W, spin):
    R = rx(0.45) @ ry(np.pi) @ rz(spin)
    return (Pc - np.array(W['swPos'])) @ R / W['swS']


def main():
    ex = json.load(open(sys.argv[1])); binp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'f1fahrer.bin')
    P, reg, bi, bw, F = load_bin(binp); spec = ex['spec']
    # dichte Punkte: Eckpunkte + Flächenmitten + Kantenmitten (Knochen der Eckpunkte gemischt)
    MID = mids(F); step = int(os.environ.get('STEP', '2'))   # jeden 2. Lenkschritt (0,02 Einschlag)
    names = {0: 'Rumpf', 1: 'Arm', 2: 'Bein', 3: 'Handschuh'}
    worst_all = 0.0
    for case, C in ex['cases'].items():
        ser = case.split('-')[0]; W = ex['wheel'][ser]; pos = np.array(C['pos']); S = C['S']
        res = {k: (9.0, None) for k in names}; rolls = []; tubHit = {}
        TT = np.array(ex['car'][ser]).reshape(-1, 3, 3)[np.array(ex['carTag'][ser]) == 'tub'] if 'carTag' in ex else None
        for smp in S[::step]:
            M = [np.array(m).reshape(4, 4).T for m in smp['M']]; Ms = np.stack(M)
            def skin(Pp, bii, bww):
                H = np.c_[Pp, np.ones(len(Pp))]; out = np.zeros((len(Pp), 3))
                for k in range(4): out += bww[:, k:k + 1] * np.einsum('nij,nj->ni', Ms[bii[:, k]], H)[:, :3]
                return out
            Pv = skin(P, bi, bw)
            allP = [Pv]; allR = [reg]
            for a, b, c, wa, wb, wc in MID:
                allP.append(Pv[a] * wa + Pv[b] * wb + Pv[c] * wc); allR.append(reg[a])   # Mitten der verformten Dreiecke
            Q = np.vstack(allP) + pos; RG = np.concatenate(allR)
            near = np.linalg.norm(Q - np.array(W['swPos']), axis=1) < 0.4
            L = to_local(Q[near], W, smp['sp']); d = wheel_sdf(L, spec) * W['swS']; rgn = RG[near]
            for k in names:
                m = rgn == k
                if m.any() and d[m].min() < res[k][0]: res[k] = (d[m].min(), smp['st'])
            if smp.get('roll'): rolls.append(smp['roll'])
            if TT is not None:   # Arme/Hände gegen die Cockpitwanne (Cockpit- und TV-Ansicht zeigen dort nur die Wanne)
                am = np.isin(RG, (1, 3)) & (np.abs(Q[:, 0]) > 0.12); ins = tub_inside(Q[am], TT)
                if ins.any(): tubHit[smp['st']] = (int(ins.sum()), Q[am][ins][np.abs(Q[am][ins][:, 0]).argmax()].round(3).tolist())
        rr = np.degrees(np.abs(np.array(rolls))).max() if rolls else float('nan')
        print(f"{case:6s} " + '  '.join(f"{names[k]} {res[k][0] * 1000:+6.1f} mm (Einschlag {res[k][1]:+.2f})" for k in names) + f"   Handrolle max {rr:.0f}°")
        worst_all = min(worst_all, min(v[0] for v in res.values()))
        if TT is not None:
            print(f"       Arme/Hände in der Cockpitwanne: " + ('frei' if not tubHit else f"{len(tubHit)} Lenkwinkel betroffen, z. B. " + '; '.join(f"Einschlag {k:+.2f}: {v[0]} Punkte, außen {v[1]}" for k, v in list(tubHit.items())[:4])))
            if tubHit: worst_all = min(worst_all, -0.001)
    # Karosserie/Wanne gegen das Lenkrad (Lenkrad dreht, Auto steht)
    for ser, T in ex['car'].items():
        W = ex['wheel'][ser]; T = np.array(T).reshape(-1, 3, 3); pts = []
        for tri in T:
            e = max(np.linalg.norm(tri[1] - tri[0]), np.linalg.norm(tri[2] - tri[1]), np.linalg.norm(tri[0] - tri[2])); n = int(min(40, np.ceil(e / 0.006)))
            for i in range(n + 1):
                for j in range(n + 1 - i): u, v = i / n if n else 0, j / n if n else 0; pts.append(tri[0] + (tri[1] - tri[0]) * u + (tri[2] - tri[0]) * v)
        Pc = np.array(pts); Pc = Pc[np.linalg.norm(Pc - np.array(W['swPos']), axis=1) < 0.35]; best = (9, None, None)
        for st in np.linspace(-1, 1, 21):
            d, part = wheel_sdf(to_local(Pc, W, -st * 0.95), spec, parts=True); d = d * W['swS']; i = d.argmin()
            if d[i] < best[0]: best = (d[i], st, spec[part[i]]['t'])
        print(f"{ser} Karosserie/Wanne: kleinster Abstand {best[0] * 1000:+.1f} mm (Einschlag {best[1]:+.2f}, Teil {best[2]}), {len(Pc)} Prüfpunkte")
        worst_all = min(worst_all, best[0])
    print('ERGEBNIS:', 'kein Clipping' if worst_all >= 0 else f'Durchdringung bis {-worst_all * 1000:.1f} mm')


if __name__ == '__main__':
    main()
