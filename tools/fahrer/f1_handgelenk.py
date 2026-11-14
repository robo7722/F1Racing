"""Handgelenk-Gewichte von f1fahrer.bin (F1/F2-Fahrer) – v1.93.

Problem: Die Handschuh-Stulpe (Zylinder r 3,1 cm bis 4,5 cm hinter dem Handgelenk) hing starr am Handknochen, der Ärmel
(steckt mit r 2,7 cm in der Stulpe) starr am Unterarm. Beim Einlenken knickt die obere Hand bis ~55° gegen den Unterarm ab:
die Stulpe schwenkte als Ganzes aus dem Ärmel, das Ärmelende stach durch die Stulpe und man sah ins offene Ärmelende.

Lösung: Arm- und Handschuh-Punkte im Bereich -1 … +8 cm hinter dem Handgelenk (entlang Handgelenk → Ellbogen der
Bindhaltung) bekommen weiche Gewichte Hand ↔ Unterarm (smoothstep). Stulpe und Ärmel haben an gleicher Stelle das gleiche
Gewicht – sie biegen gemeinsam, der Ärmel bleibt in der Stulpe. Davor (Hand, Daumen, Finger) starr an der Hand, dahinter
starr am Unterarm (wie vorher).

v1.94 – Form am Handgelenk: Der Ärmel war direkt hinter der Stulpe schon 4–5,5 cm dick (Stulpe 3,1 cm) und stand ab 1 cm vor
ihrem Ende außen über – am Handgelenk saß ein schmaler Klotz, dahinter sprang der Unterarm breit heraus. Jetzt läuft der Ärmel
zum Handgelenk schlank zu (bis 3,5 cm, ab 13 cm hinter dem Handgelenk wieder unverändert) und liegt ganz in der Stulpe,
die Stulpe weitet sich zum Ende leicht (3,1 → 3,7 cm, Stulpe über dem Ärmel). Normalen dort neu.

Gewichte: wiederholbar (jedes Mal neu berechnet). Form: nur einmal (Kopf-Eintrag "gelenk": "v1.94").
Aufruf: python tools/fahrer/f1_handgelenk.py [f1fahrer.bin]
"""
import json, struct, sys, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C0, C1 = -0.01, 0.08      # Übergangsbereich hinter dem Handgelenk (m, Bindhaltung)
R_MAX = 0.07              # nur Punkte nahe der Unterarmachse (Arm/Handschuh)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'f1fahrer.bin')
    b = bytearray(open(path, 'rb').read()); n = struct.unpack('<I', b[:4])[0]; h = json.loads(b[4:4 + n]); o = 4 + n; nv = h['nv']
    P = np.frombuffer(bytes(b), np.float32, nv * 3, o + h['pos']).reshape(nv, 3)
    reg = np.frombuffer(bytes(b), np.uint8, nv, o + h['reg'])
    bi = np.frombuffer(bytes(b), np.uint8, nv * 4, o + h['bi']).reshape(nv, 4).copy()
    bw = np.frombuffer(bytes(b), np.uint8, nv * 4, o + h['bw']).reshape(nv, 4).copy()
    sh, el, wr = [np.array(a, float) for a in h['arm']]
    tot = 0
    for sx, (fore, hand) in ((-1, (2, 3)), (1, (5, 6))):   # Arm in h['arm'] liegt bei x < 0 (Knochen 1-3), Spiegelseite 4-6
        m = np.array([sx * (-1), 1, 1])                       # x spiegeln für die rechte Seite
        e, w = el * m, wr * m; fa = (e - w) / np.linalg.norm(e - w)
        q = P - w; cw = q @ fa; rad = np.linalg.norm(q - np.outer(cw, fa), axis=1)
        side = (P[:, 0] * sx > 0)
        sel = side & ((reg == 1) | (reg == 3)) & (rad < R_MAX) & (cw > C0) & (cw < C1)
        # nur Punkte, die bisher an Hand/Unterarm hängen (keine Oberarm-Anteile im Bereich)
        own = np.isin(bi, [fore, hand]) | (bw == 0)
        sel &= own.all(1)
        t = np.clip((cw[sel] - C0) / (C1 - C0), 0, 1); t = t * t * (3 - 2 * t)
        wf = np.round(t * 255).astype(np.int32)
        bi[sel] = 0; bw[sel] = 0
        bi[sel, 0] = hand; bw[sel, 0] = 255 - wf
        bi[sel, 1] = fore; bw[sel, 1] = wf
        print('Seite', 'links' if sx < 0 else 'rechts', 'Punkte', int(sel.sum()), 'Handschuh', int((sel & (reg == 3)).sum()), 'Arm', int((sel & (reg == 1)).sum()))
        tot += int(sel.sum())
    b[o + h['bi']:o + h['bi'] + nv * 4] = bi.tobytes(); b[o + h['bw']:o + h['bw'] + nv * 4] = bw.tobytes()
    if h.get('gelenk') != 'v1.94':
        b = form(b, h, o, P, reg, sh, el, wr)
    open(path, 'wb').write(bytes(b)); print('geschrieben', path, 'geänderte Punkte', tot)


def S(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def form(b, h, o, P, reg, sh, el, wr):
    nv = h['nv']; P = P.astype(np.float64).copy()
    N = np.frombuffer(bytes(b), np.float32, nv * 3, o + h['nrm']).reshape(nv, 3).astype(np.float64).copy()
    I = np.frombuffer(bytes(b), np.uint32 if h.get('i32') else np.uint16, h['ni'], o + h['idx']).reshape(-1, 3).astype(int)
    ch = np.zeros(nv, bool)
    CUFF = lambda c: 0.031 + 0.006 * S((c - 0.012) / 0.029)          # Stulpe: Radius je Abstand hinter dem Handgelenk
    for sx in (-1, 1):
        m = np.array([-sx, 1, 1]); e, w = el * m, wr * m; fa = (e - w) / np.linalg.norm(e - w)
        q = P - w; cw = q @ fa; pr = q - np.outer(cw, fa); rad = np.linalg.norm(pr, axis=1); side = P[:, 0] * sx > 0
        g = side & (reg == 3) & (cw > 0.012) & (cw < 0.06) & (rad > 0.028) & (rad < 0.034)   # Stulpen-Zylinder (r 3,1 cm)
        P[g] = w + np.outer(cw[g], fa) + pr[g] / rad[g, None] * CUFF(cw[g])[:, None]; ch |= g
        a = side & (reg == 1) & (cw > 0.0) & (cw < 0.13) & (rad < 0.09)                       # Ärmel nahe dem Handgelenk
        lim = np.where(cw[a] < 0.041, CUFF(np.minimum(cw[a], 0.041)) - 0.002, CUFF(0.041) - 0.002)
        t = S((cw[a] - 0.03) / 0.10); rn = np.minimum(rad[a], lim) * (1 - t) + rad[a] * t
        P[a] = w + np.outer(cw[a], fa) + pr[a] / (rad[a, None] + 1e-12) * rn[:, None]; ch |= a
        print('Form', 'links' if sx < 0 else 'rechts', 'Stulpe', int(g.sum()), 'Ärmel', int(a.sum()))
    # Normalen der geänderten Punkte aus den angrenzenden Flächen (nur Arm/Handschuh), Nähte zusammengeführt
    fm = np.isin(reg[I], [1, 3]).all(1); F = I[fm]; fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
    Nn = np.zeros_like(P)
    for k in range(3): np.add.at(Nn, F[:, k], fn)
    key = np.c_[np.round(P / 1e-5).astype(np.int64), reg]; _, inv = np.unique(key, axis=0, return_inverse=True); inv = inv.ravel()
    Sm = np.zeros((inv.max() + 1, 3)); np.add.at(Sm, inv, Nn); Nn = Sm[inv]; Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-12
    upd = np.zeros(nv, bool); upd[np.unique(I[fm & ch[I].any(1)].ravel())] = True             # geänderte Punkte und ihre Nachbarn
    N[upd] = Nn[upd]
    b[o + h['pos']:o + h['pos'] + nv * 12] = P.astype(np.float32).tobytes(); b[o + h['nrm']:o + h['nrm'] + nv * 12] = N.astype(np.float32).tobytes()
    h['gelenk'] = 'v1.94'; hj = json.dumps(h).encode(); hj += b' ' * ((-(4 + len(hj)) - (-o % 4)) % 4)   # Daten bleiben gleich ausgerichtet
    return bytearray(struct.pack('<I', len(hj)) + hj + bytes(b[o:]))


if __name__ == '__main__':
    main()
