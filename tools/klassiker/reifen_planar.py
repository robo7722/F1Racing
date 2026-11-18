#!/usr/bin/env python3
"""Reifenflanke eines Klassikers (GLB) neu abbilden: zentrierte, runde Textur + ebene Projektion genau um die Radachse.

Anlass (v2.88, 18.11.2026, McLaren MP4/4): „Radtexturen eiern“. Die Flanken-UVs im Modell waren gekachelt und schief (u 0…2, v −1…0) –
der Goodyear-Schriftzug lief beim Drehen nicht rund. Hier wird
  1. aus dem Originalbild ein neues, exakt zentriertes Flankenbild gerechnet: Ring um die gemessene Bildmitte (Innenkreis angepasst)
     radial so umgelegt, dass Bildmitte = Radachse und Bildrand = Reifenaußenradius; außerhalb dunkles Gummi,
  2. jede Ecke des Reifen-Materials neu abgebildet: u/v = eben quer zur Achse (x), Mitte = Radmitte, Radius R = 0,5 im Bild.
     Für linke Räder wird u gespiegelt, damit die Schrift auf BEIDEN Wagenseiten außen richtig herum steht (Innenseite ist verdeckt).
     Die Lauffläche liegt am Bildrand (ρ ≈ 1) und ist damit einfarbig dunkles Gummi.

Aufruf: python3 tools/klassiker/reifen_planar.py <modell.glb> "<Materialname>" [--rin 0.559] [--alt-innen 134.3] [--alt-aussen 252]
  --rin         Innenradius der Flanke (Felgenrand) als Anteil des Außenradius – wird sonst aus dem Modell gemessen
  --alt-innen   Radius des Innenkreises im Originalbild (Pixel, bei 512er-Bild) · --alt-aussen Außenrand der Zeichnung im Original
Vorher wird <modell>.vor_reifen angelegt (nicht im Repo).
"""
import sys, json, struct, io, shutil
import numpy as np
from PIL import Image
from scipy import ndimage

CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5122: np.int16, 5121: np.uint8, 5120: np.int8}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}


def opt(k, d):
    return float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d


def acc_view(J, BIN, i):
    a = J['accessors'][i]; v = J['bufferViews'][a['bufferView']]; dt = np.dtype(CT[a['componentType']]); n = NC[a['type']]
    o = v.get('byteOffset', 0) + a.get('byteOffset', 0); st = v.get('byteStride', 0) or n * dt.itemsize
    raw = np.frombuffer(bytes(BIN[o:o + st * a['count']]), np.uint8).reshape(a['count'], st)[:, :n * dt.itemsize].copy().view(dt).reshape(a['count'], n)
    return raw, o, st


path, mat = [a for a in sys.argv[1:] if not a.startswith('--')][:2]
b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L]); off = 20 + L
bl = struct.unpack('<I', b[off:off + 4])[0]; BIN = bytearray(b[off + 8:off + 8 + bl])
mi = next(i for i, m in enumerate(J['materials']) if m.get('name') == mat)
img_i = J['textures'][J['materials'][mi]['pbrMetallicRoughness']['baseColorTexture']['index']]['source']

# ---- 1) Ecken neu abbilden ----
mesh_side = {}
for nd in J['nodes']:
    if 'mesh' in nd and nd.get('name', '').startswith('wheel_'):
        par = next(p for p in J['nodes'] if nd is not p and J['nodes'].index(nd) in p.get('children', []))
        mesh_side[nd['mesh']] = 1 if par['translation'][0] > 0 else -1     # +1 rechtes Rad (x > 0), −1 linkes
rins = []
done = set()
for me, side in mesh_side.items():
    for pr in J['meshes'][me]['primitives']:
        if pr['material'] != mi: continue
        ui = pr['attributes']['TEXCOORD_0']
        if ui in done: continue
        done.add(ui)
        P, _, _ = acc_view(J, BIN, pr['attributes']['POSITION']); P = P.astype(np.float64)
        UV, o, st = acc_view(J, BIN, ui)
        assert J['accessors'][ui]['componentType'] == 5126, 'UV nicht float'
        cy = (P[:, 1].min() + P[:, 1].max()) / 2; cz = (P[:, 2].min() + P[:, 2].max()) / 2
        dy, dz = P[:, 1] - cy, P[:, 2] - cz; R = np.hypot(dy, dz).max()
        r = np.hypot(dy, dz) / R; rins.append(np.percentile(r, 3))
        u = 0.5 + (-side) * dz / (2 * R)          # linkes Rad (side −1): Kamera bei −x schaut nach +x, rechts im Bild = +z
        v = 0.5 - dy / (2 * R)                    # glTF: v nach unten
        new = np.c_[u, v].astype(np.float32)
        for k in range(len(new)): BIN[o + k * st:o + k * st + 8] = new[k].tobytes()
        J['accessors'][ui]['min'] = [float(new[:, 0].min()), float(new[:, 1].min())]; J['accessors'][ui]['max'] = [float(new[:, 0].max()), float(new[:, 1].max())]
rin = opt('--rin', float(np.median(rins)))
print('UV neu: %d Zugriffe, Innenradius Flanke %.3f' % (len(done), rin))

# ---- 2) zentriertes Flankenbild ----
iv = J['images'][img_i]['bufferView']; v = J['bufferViews'][iv]
src = Image.open(io.BytesIO(bytes(BIN[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]))).convert('RGB')
S0 = src.size[0]; A = np.asarray(src).astype(np.float32); g = ndimage.gaussian_filter(A.mean(2), 1.5)
# Innenkreis im Original messen (Mitte + Radius)
c0 = np.array([S0 / 2, S0 / 2]); pts = []
for a in np.linspace(0, 2 * np.pi, 180, endpoint=False):
    rs = np.arange(0.39 * S0 / 2, 0.68 * S0 / 2, 0.5); xs = c0[0] + rs * np.cos(a); ys = c0[1] + rs * np.sin(a)
    d = np.diff(ndimage.map_coordinates(g, [ys, xs], order=1)); rr = rs[np.argmax(np.abs(d))]; pts.append((c0[0] + rr * np.cos(a), c0[1] + rr * np.sin(a)))
Pp = np.array(pts); Aa = np.c_[2 * Pp, np.ones(len(Pp))]; cc = np.linalg.lstsq(Aa, (Pp ** 2).sum(1), rcond=None)[0]
cx, cyy = cc[0], cc[1]; r_in_old = opt('--alt-innen', np.sqrt(cc[2] + cx ** 2 + cyy ** 2)); r_out_old = opt('--alt-aussen', S0 / 2 - 4)
print('Original: Mitte (%.1f, %.1f), Innenkreis %.1f px, Außenrand %.1f px' % (cx, cyy, r_in_old, r_out_old))
N = 1024; yy, xx = np.mgrid[0:N, 0:N] + 0.5; dx = (xx - N / 2) / (N / 2); dy = (yy - N / 2) / (N / 2); rho = np.hypot(dx, dy); ang = np.arctan2(dy, dx)
ro = r_in_old + (rho - rin) / (1 - rin) * (r_out_old - r_in_old)
sx = cx + ro * np.cos(ang); sy = cyy + ro * np.sin(ang)
out = np.dstack([ndimage.map_coordinates(A[..., k], [sy - 0.5, sx - 0.5], order=1, mode='nearest') for k in range(3)])
rub = np.median(out[(rho > 0.97) & (rho < 0.99)].reshape(-1, 3), 0)   # Gummifarbe am Außenrand
w = np.clip((rho - 0.975) / 0.02, 0, 1)[..., None]; out = out * (1 - w) + rub * w        # Lauffläche/Außenrand: einfarbig
wi = np.clip((rin - 0.01 - rho) / 0.02, 0, 1)[..., None]; out = out * (1 - wi) + rub * wi  # innerhalb des Felgenrands (nicht benutzt): einfarbig
img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
bio = io.BytesIO(); img.save(bio, 'JPEG', quality=90, optimize=True); data = bio.getvalue()

# ---- 3) GLB neu schreiben ----
views = J['bufferViews']; nb = bytearray()
for i, vv in enumerate(views):
    d = data if i == iv else BIN[vv.get('byteOffset', 0):vv.get('byteOffset', 0) + vv['byteLength']]
    while len(nb) % 4: nb.append(0)
    vv['byteOffset'] = len(nb); vv['byteLength'] = len(d); nb.extend(d)
while len(nb) % 4: nb.append(0)
J['buffers'][0]['byteLength'] = len(nb); J['images'][img_i]['mimeType'] = 'image/jpeg'
for t in J.get("textures", []):                       # Sampler mit Randklemme (Bild liegt genau einmal auf der Flanke)
    if t['source'] == img_i: t['sampler'] = next((k for k, s in enumerate(J.get('samplers', [])) if s.get('wrapS') == 33071), t.get('sampler'))   # Rand nicht wiederholen
js = json.dumps(J, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(nb)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(nb), 0x004E4942) + bytes(nb)
shutil.copy(path, path + '.vor_reifen'); open(path, 'wb').write(glb)
if '--bild' in sys.argv: img.save(sys.argv[sys.argv.index('--bild') + 1])
print('geschrieben:', path, len(glb), 'Bytes')
