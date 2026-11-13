#!/usr/bin/env python3
"""Aufkleber des Roadsters (RONE Racing) bauen:  python3 tools/sticker/mx5/bauen.py
Liest die Einzelbilder aus bilder/ und roadcar.bin, schreibt liveries/MX5.png (Bogen) und liveries/MX5.json (Aufkleber-Netz).
Jeder Aufkleber ist ein feines Gitter, das aus einer Blickrichtung auf die Karosserie gelegt wird und 3 mm über dem Lack liegt.
Koordinaten in Metern: x quer (links positiv), y hoch, z nach vorn. Sicht: L / R = von links / rechts (a = z, b = y), T = von oben (a = x, b = z),
F / B = von vorn / hinten (a = x, b = y). w = Breite des ganzen Bildes in Metern, rot = Drehung in Grad (gegen den Uhrzeigersinn aus der Sicht),
flip = Bild spiegeln, teil = 'lack' oder 'glas'."""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from modell import laden, treffer, SICHT, ROOT
HIER = os.path.dirname(os.path.abspath(__file__))
A = [
  # beide Seiten: Sponsoren-Säule an der Tür, Pirelli am Kotflügel, schwarze Grafik (rechts gespiegelt)
  dict(bild='stack', sicht='L', a=0.43, b=0.605, w=0.28), dict(bild='stack', sicht='R', a=0.43, b=0.605, w=0.28),
  dict(bild='pirelli', sicht='L', a=0.7375, b=0.8075, w=0.275), dict(bild='pirelli', sicht='R', a=0.7375, b=0.8075, w=0.275),
  dict(bild='grafik', sicht='L', a=-0.7257, b=0.7043, w=2.091), dict(bild='grafik', sicht='R', a=-0.7257, b=0.7043, w=2.091, flip=True),
  dict(bild='nemec', sicht='L', a=-0.36, b=1.065, w=0.21, teil='glas'), dict(bild='nemec', sicht='R', a=-0.36, b=1.065, w=0.21, teil='glas'),
  # nur links: Pentagramm auf dem Tankdeckel, MAZDASPEED an der vorderen Stoßstangenecke
  dict(bild='pentagramm', sicht='L', a=-1.69, b=0.913, w=0.205, auto=True), dict(bild='mazdaspeed', sicht='L', a=2.05, b=0.55, w=0.27, rot=9, auto=True),
  # nur rechts: 666 vor dem Vorderrad
  dict(bild='n666', sicht='R', a=1.99, b=0.52, w=0.2, auto=True),
  # Haube, Frontlippe, Heck, Windschutzscheibe
  dict(bild='oni', sicht='T', a=0, b=1.53, w=0.435), dict(bild='insta', sicht='F', a=0, b=0.228, w=0.32),
  dict(bild='limitless', sicht='B', a=0.5, b=0.665, w=0.31), dict(bild='mazdaspeed', sicht='B', a=0.5, b=0.585, w=0.34), dict(bild='fisch', sicht='B', a=-0.5, b=0.63, w=0.27),
  dict(bild='banner', sicht='F', a=0, b=1.262, w=1.06, teil='glas'),
  # Anime-Motiv in der Heckscheibe links, Anfängerzeichen rechts, schwarze Streifen auf der Haube (breit an der Scheibe, spitz nach vorn, entlang der Haubenkante, rechts gespiegelt)
  dict(bild='anime', sicht='B', a=0.31, b=1.18, w=0.25, rot=6, teil='glas', auto=True), dict(bild='anfaenger', sicht='B', a=-0.37, b=1.155, w=0.06, teil='glas', auto=True),
  dict(bild='streifen', sicht='T', a=-0.66, b=1.05, w=0.1875, rot=2.5), dict(bild='streifen', sicht='T', a=0.66, b=1.05, w=0.1875, rot=-2.5, flip=True),
  dict(bild='southsiderz', sicht='B', a=-0.3, b=0.905, w=0.25),
  # BLACKLIST-Krone: hängt frei am Innenspiegel (frei = Mitte x, y, z; Vorderseite zeigt nach vorn, Rückseite seitenrichtig zum Fahrer)
  dict(bild='krone', frei=(0.03, 1.18, -0.05), w=0.1, rot=-4),
]
PAD, BW, ZELLE, HOCH = 8, 2048, 0.025, {'lack': 0.003, 'glas': 0.002, 'spoiler': 0.002}
def bogen():
    namen = sorted({s['bild'] for s in A} | {'blacklist'}); ims = {n: Image.open(os.path.join(HIER, 'bilder', n + '.png')).convert('RGBA') for n in namen}; pos = {}; x = y = PAD; zh = 0
    for n in sorted(namen, key=lambda n: -ims[n].height):
        im = ims[n]
        if x + im.width + PAD > BW: x = PAD; y += zh + PAD; zh = 0
        pos[n] = (x, y, im.width, im.height); x += im.width + PAD; zh = max(zh, im.height)
    H = 1 << int(np.ceil(np.log2(y + zh + PAD))); sh = Image.new('RGBA', (BW, H), (255, 255, 255, 0))
    for n, (x, y, w, h) in pos.items(): sh.paste(ims[n], (x, y))
    sh.save(os.path.join(ROOT, 'liveries', 'MX5.png'), optimize=True); return ims, pos, (BW, H)
def netz(s, im, T):
    a, sg, (ua, us), (va, vs) = SICHT[s['sicht']]; w = s['w']; h = w * im.height / im.width; nu = max(2, int(np.ceil(w / ZELLE))); nv = max(2, int(np.ceil(h / ZELLE)))
    gu, gv = np.meshgrid(np.linspace(0, 1, nu + 1), np.linspace(0, 1, nv + 1)); gu = gu.ravel(); gv = gv.ravel()      # Bild: u nach rechts, v nach unten
    lx = (gu - 0.5) * w; ly = (0.5 - gv) * h; r = np.radians(s.get('rot', 0)); rx = lx * np.cos(r) - ly * np.sin(r); ry = lx * np.sin(r) + ly * np.cos(r)
    # Mitte in Bildkoordinaten der Sicht (a/b sind Modellkoordinaten)
    ca = {'L': -s['a'], 'R': s['a'], 'T': s['a'], 'F': s['a'], 'B': -s['a']}[s['sicht']]; cb = -s['b'] if s['sicht'] == 'T' else s['b']
    d = np.zeros(3); d[a] = sg; u = np.zeros(3); u[ua] = us; v = np.zeros(3); v[va] = vs
    if s.get('auto'):     # Blickrichtung = Flächennormale in der Mitte: der Aufkleber liegt unverzerrt auf schrägen Flächen (Stoßstangenecke, Tankdeckel)
        X0, n0, h0 = treffer(T, s['sicht'], np.array([ca]), np.array([cb])); assert h0[0], s
        d = n0[0]; v = v - (v @ d) * d; v /= np.linalg.norm(v); u = np.cross(v, d); ca, cb = u @ X0[0], v @ X0[0]
    M = np.stack([u, v, d]); X, n, hit = treffer(T @ M.T, 'Z', ca + rx, cb + ry); X = (X + n * HOCH[s.get('teil', 'lack')]) @ M; X[~hit] = 0
    s['_d'] = d; dd = X @ d
    al = np.asarray(im.getchannel('A')); tri = []; d = dd
    for j in range(nv):
        for i in range(nu):
            q = [j * (nu + 1) + i, j * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i + 1, (j + 1) * (nu + 1) + i]
            if not hit[q].all() or np.ptp(d[q]) > 0.06: continue
            x0, x1 = int(i / nu * im.width), int(np.ceil((i + 1) / nu * im.width)); y0, y1 = int(j / nv * im.height), int(np.ceil((j + 1) / nv * im.height))
            if s.get('flip'): x0, x1 = im.width - x1, im.width - x0
            if al[y0:y1, x0:x1].max() < 8: continue
            tri += [[q[0], q[3], q[1]], [q[1], q[3], q[2]]]
    return X, (1 - gu if s.get('flip') else gu), gv, np.array(tri, int).reshape(-1, 3), sg * us * vs
def spoiler(T):
    """Schwarze Abrisskante auf dem Kofferraumdeckel (das Modell hat keine): flach in der Mitte, an beiden Enden ein erhöhtes Feld für den BLACKLIST-Aufkleber.
    Liefert die Dreiecke (n, 3, 3) und die Lage der Hinterkante z(x)."""
    xs = np.linspace(-0.6, 0.6, 61); zs = np.arange(-1.9, -2.3, -0.004); ze = []
    for x in xs:
        X, n, hit = treffer(T, 'T', np.full(len(zs), x), -zs); k = 0
        while k + 1 < len(zs) and hit[k + 1] and n[k + 1, 1] > 0.5 and X[k, 1] - X[k + 1, 1] < 0.012: k += 1
        ze.append(zs[k])
    kante = np.poly1d(np.polyfit(xs, ze, 6)); sm = lambda t: np.clip(t, 0, 1) ** 2 * (3 - 2 * np.clip(t, 0, 1)); Q = []
    for x in xs:
        f = sm((abs(x) - 0.355) / 0.03); e = sm((0.6 - abs(x)) / 0.045); d = (0.05 + 0.05 * f) * (0.35 + 0.65 * e); h = (0.009 + 0.013 * f) * (0.2 + 0.8 * e); z = kante(x) + 0.004   # flach; Enden leicht erhöht, laufen spitz aus
        X, n, hit = treffer(T, 'T', np.array([x, x]), -np.array([z + d, z])); ya, ye = X[0, 1] - 0.002, X[1, 1]
        Q.append([[x, ya, z + d], [x, ye + h, z - 0.014], [x, ye + h - 0.006, z - 0.016], [x, ye - 0.006, z - 0.002]])
    Q = np.array(Q); tri = []
    for k in range(len(xs) - 1):
        for i, j, (ax, sg) in ((0, 1, (1, 1)), (1, 2, (2, -1)), (2, 3, (1, -1))):
            for t in ([Q[k, i], Q[k + 1, i], Q[k + 1, j]], [Q[k, i], Q[k + 1, j], Q[k, j]]):
                t = np.array(t); nn = np.cross(t[1] - t[0], t[2] - t[0]); tri.append(t if nn[ax] * sg > 0 else t[::-1])
    for k, sg in ((0, -1), (len(xs) - 1, 1)):
        for t in ([Q[k, 0], Q[k, 1], Q[k, 2]], [Q[k, 0], Q[k, 2], Q[k, 3]]):
            t = np.array(t); nn = np.cross(t[1] - t[0], t[2] - t[0]); tri.append(t if nn[0] * sg > 0 else t[::-1])
    return np.array(tri), kante
def main():
    ims, pos, (W, H) = bogen(); teile = {'lack': laden(('carpaint',)), 'glas': laden(('windowglass',))}; P = []; UV = []; I = []; n0 = 0
    SP, kante = spoiler(teile['lack']); teile['spoiler'] = SP
    for sg in (1, -1):     # BLACKLIST auf den erhöhten Enden, an der Kante ausgerichtet (Schrift von vorn lesbar wie am echten Auto)
        x = 0.47 * sg; A.append(dict(bild='blacklist', sicht='T', a=x, b=kante(x) + 0.047, w=0.15, rot=-np.degrees(np.arctan(kante.deriv()(x))), teil='spoiler'))
    for s in A:
        if 'frei' in s:
            im = ims[s['bild']]; x, y, w, h = pos[s['bild']]; bw = s['w'] / 2; bh = bw * im.height / im.width; r = np.radians(s.get('rot', 0)); c = np.array(s['frei'])
            eck = [(1, 1), (-1, 1), (-1, -1), (1, -1)]; Q = np.array([c + [(ex * bw) * np.cos(r) - (ey * bh) * np.sin(r), (ex * bw) * np.sin(r) + (ey * bh) * np.cos(r), 0] for ex, ey in eck])
            uv = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]) / [W, H]; uvr = uv[[1, 0, 3, 2]]
            P += [Q, Q - [0, 0, 0.001]]; UV += [uvr, uv]; I += [np.array([[0, 1, 3], [1, 2, 3]]) + n0, np.array([[0, 3, 1], [1, 3, 2]]) + n0 + 4]; n0 += 8; print(f"{s['bild']:11s} frei"); continue
        im = ims[s['bild']]; X, u, v, tri, hand = netz(s, im, teile[s.get('teil', 'lack')]); x, y, w, h = pos[s['bild']]
        if not len(tri): print('WARNUNG: trifft nichts', s); continue
        use = np.unique(tri); neu = np.full(len(X), -1); neu[use] = np.arange(len(use)) + n0; tri = neu[tri]
        # Drehsinn so, dass die Vorderseite zum Betrachter zeigt
        Xa = np.zeros((n0 + len(use), 3)); Xa[n0:] = X[use]
        e = np.cross(Xa[tri[:, 1]] - Xa[tri[:, 0]], Xa[tri[:, 2]] - Xa[tri[:, 0]]) @ s['_d']; tri[e < 0] = tri[e < 0][:, ::-1]
        P.append(X[use]); UV.append(np.stack([(x + u[use] * w) / W, (y + v[use] * h) / H], 1)); I.append(tri); n0 += len(use)
        print(f"{s['bild']:11s} {s['sicht']} {len(use):5d} Punkte {len(tri):5d} Dreiecke")
    P = np.concatenate(P); UV = np.concatenate(UV); I = np.concatenate(I)
    out = {'q': 10000, 'p': np.round(P * 10000).astype(int).ravel().tolist(), 'uv': np.round(UV * 8192).astype(int).ravel().tolist(), 'i': I.ravel().tolist(), 'sp': np.round(SP * 10000).astype(int).ravel().tolist()}
    json.dump(out, open(os.path.join(ROOT, 'liveries', 'MX5.json'), 'w'), separators=(',', ':')); print(len(P), 'Punkte,', len(I), 'Dreiecke, Bogen', W, 'x', H)
if __name__ == '__main__': main()
