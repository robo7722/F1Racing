"""Handgelenk-Gewichte von f1fahrer.bin (F1/F2-Fahrer) – v1.93.

Problem: Die Handschuh-Stulpe (Zylinder r 3,1 cm bis 4,5 cm hinter dem Handgelenk) hing starr am Handknochen, der Ärmel
(steckt mit r 2,7 cm in der Stulpe) starr am Unterarm. Beim Einlenken knickt die obere Hand bis ~55° gegen den Unterarm ab:
die Stulpe schwenkte als Ganzes aus dem Ärmel, das Ärmelende stach durch die Stulpe und man sah ins offene Ärmelende.

Lösung: Arm- und Handschuh-Punkte im Bereich -1 … +8 cm hinter dem Handgelenk (entlang Handgelenk → Ellbogen der
Bindhaltung) bekommen weiche Gewichte Hand ↔ Unterarm (smoothstep). Stulpe und Ärmel haben an gleicher Stelle das gleiche
Gewicht – sie biegen gemeinsam, der Ärmel bleibt in der Stulpe. Davor (Hand, Daumen, Finger) starr an der Hand, dahinter
starr am Unterarm (wie vorher).

Ändert nur die Felder bi/bw (Knochen-Nummern und -Gewichte), gleiche Größe. Wiederholbar (berechnet die Gewichte jedes Mal neu).
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
    open(path, 'wb').write(bytes(b)); print('geschrieben', path, 'geänderte Punkte', tot)


if __name__ == '__main__':
    main()
