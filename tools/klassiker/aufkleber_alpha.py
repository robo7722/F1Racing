#!/usr/bin/env python3
"""Aufkleberbogen eines Klassiker-Modells mit schwarzem Hintergrund durchsichtig machen (Rückmeldung 18.11.2026: McLaren MP4/4 zeigte schwarze
Kästen um Shell, Honda, Nummer usw. – im verkleinerten Modell ist der Bogen ein JPEG ohne Deckkraft, das Material undurchsichtig).

Aufruf:  python3 tools/klassiker/aufkleber_alpha.py modelle/klassiker/mclaren_mp44.glb "Material_#1.005" [Schwelle]
- Durchsichtig wird nur das dunkle Gebiet, das mit dem großen Hintergrund zusammenhängt (Flutfüllung); schwarze Schrift INNERHALB eines Logos
  (z. B. TAG Heuer) bleibt, weil sie von hellen Rändern eingeschlossen ist.
- Der Bogen wird als PNG mit Deckkraft gespeichert, das Material bekommt alphaMode MASK (Ausstanzen, kein Sortierproblem).
- Die Datei wird überschrieben; vorher liegt eine Sicherung unter <Datei>.vor_alpha (nicht im Repo).
"""
import sys, json, struct, io, shutil
import numpy as np
from PIL import Image
from scipy import ndimage as nd

path, mat_name = sys.argv[1], sys.argv[2]; thr = int(sys.argv[3]) if len(sys.argv) > 3 else 40
b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L]); off = 20 + L
bl = struct.unpack('<I', b[off:off + 4])[0]; BIN = b[off + 8:off + 8 + bl]
mi = next(i for i, m in enumerate(J['materials']) if m.get('name') == mat_name); M = J['materials'][mi]
img_i = J['textures'][M['pbrMetallicRoughness']['baseColorTexture']['index']]['source']; bv = J['bufferViews'][J['images'][img_i]['bufferView']]
im = Image.open(io.BytesIO(BIN[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']])).convert('RGB'); a = np.asarray(im).astype(np.int32)
dark = a.max(2) < thr
lab, n = nd.label(dark); sizes = nd.sum(dark, lab, range(1, n + 1))
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
big = {i + 1 for i, s in enumerate(sizes) if s > dark.size * 0.002}             # großer Hintergrund (auch Inseln zwischen Logos)
bg = np.isin(lab, list(edge | big))
bg = nd.binary_dilation(bg, iterations=1) & (a.max(2) < thr * 2)               # dunkle Kantenpixel (JPEG-Saum) mitnehmen
alpha = np.where(bg, 0, 255).astype(np.uint8)
rgba = np.dstack([a.astype(np.uint8), alpha])
# Farbe in die durchsichtigen Ränder ziehen (sonst schwarzer Saum beim Filtern)
rgb = rgba[..., :3].astype(np.float32); have = alpha > 0
for _ in range(8):
    acc = np.zeros_like(rgb); cnt = np.zeros(alpha.shape, np.float32)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        h = np.roll(have, (dy, dx), (0, 1)); acc += np.roll(rgb, (dy, dx), (0, 1)) * h[..., None]; cnt += h
    new = (~have) & (cnt > 0); rgb[new] = acc[new] / cnt[new][:, None]; have |= new
out = Image.fromarray(np.dstack([rgb.astype(np.uint8), alpha]), 'RGBA'); bio = io.BytesIO(); out.save(bio, 'PNG', optimize=True); png = bio.getvalue()
print('durchsichtig: %.1f %%' % (100 * (alpha == 0).mean()), 'PNG', len(png), 'Bytes (vorher', bv['byteLength'], ')')
# BIN neu zusammensetzen: alle bufferViews der Reihe nach, das Bild ersetzt
views = J['bufferViews']; target = J['images'][img_i]['bufferView']; nb = bytearray()
for i, v in enumerate(views):
    data = png if i == target else BIN[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
    while len(nb) % 4: nb.append(0)
    v['byteOffset'] = len(nb); v['byteLength'] = len(data); nb.extend(data)
while len(nb) % 4: nb.append(0)
J['buffers'][0]['byteLength'] = len(nb); J['images'][img_i]['mimeType'] = 'image/png'
M['alphaMode'] = 'MASK'; M['alphaCutoff'] = 0.5
js = json.dumps(J, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(nb)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(nb), 0x004E4942) + bytes(nb)
shutil.copy(path, path + '.vor_alpha'); open(path, 'wb').write(glb); print('geschrieben', path, len(glb), 'Bytes')
Image.fromarray(np.where(alpha[..., None] > 0, rgba[..., :3], np.array([255, 0, 255], np.uint8)).astype(np.uint8)).save('/tmp/claude-0/-home-user-F1Racing/a88aa794-cb6d-58b8-a901-68dcd665125a/scratchpad/mcl/bogen_alpha.png')
