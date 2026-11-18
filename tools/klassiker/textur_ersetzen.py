#!/usr/bin/env python3
"""Textur eines Materials in einem Klassiker-Modell (GLB) durch ein Originalbild ersetzen.

Aufruf:  python3 tools/klassiker/textur_ersetzen.py <modell.glb> "<Materialname>" <bild.png> [--flip] [--mask] [--max 1024]
  --flip   Bild senkrecht spiegeln (Originale aus dem Modellierprogramm liegen oft mit v nach oben, glTF erwartet v nach unten)
  --mask   Deckkraft des Bilds verwenden, Material auf alphaMode MASK (Ausstanzen) stellen
  --max    größte Kantenlänge (Standard 1024)
Gespeichert wird PNG (mit --mask) bzw. JPEG (Qualität 90). Vorher wird <modell>.vor_ersetzen angelegt (nicht im Repo).
Anlass (18.11.2026): McLaren MP4/4 – Aufkleberbogen ohne Deckkraft (schwarze Kästen) und falsche Textur am Armaturenbrett („BOSS“ statt Beschriftung).
Originale vom Nutzer: tools/klassiker/quellen/mclaren/.
"""
import sys, json, struct, io, shutil
from PIL import Image, ImageOps

args = [a for a in sys.argv[1:] if not a.startswith('--')]; opts = [a for a in sys.argv[1:] if a.startswith('--')]
path, mat_name, img_path = args[0], args[1], args[2]
mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 1024
if mx and str(mx) in args: args.remove(str(mx))
b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L]); off = 20 + L
bl = struct.unpack('<I', b[off:off + 4])[0]; BIN = b[off + 8:off + 8 + bl]
mi = next(i for i, m in enumerate(J['materials']) if m.get('name') == mat_name); M = J['materials'][mi]
img_i = J['textures'][M['pbrMetallicRoughness']['baseColorTexture']['index']]['source']
users = [i for i, m in enumerate(J['materials']) if 'baseColorTexture' in m.get('pbrMetallicRoughness', {}) and J['textures'][m['pbrMetallicRoughness']['baseColorTexture']['index']]['source'] == img_i]
if len(users) > 1: sys.exit('Bild wird von mehreren Materialien genutzt: %s' % users)
im = Image.open(img_path); im = im.convert('RGBA')
if '--flip' in opts: im = ImageOps.flip(im)
if max(im.size) > mx: im.thumbnail((mx, mx), Image.LANCZOS)
bio = io.BytesIO()
if '--mask' in opts:
    import numpy as np                                     # Farbe in durchsichtige Ränder ziehen (kein dunkler Saum beim Filtern)
    a = np.asarray(im).astype(np.float32); rgb, al = a[..., :3].copy(), a[..., 3]; have = al > 127
    for _ in range(8):
        acc = np.zeros_like(rgb); cnt = np.zeros(al.shape, np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            h = np.roll(have, (dy, dx), (0, 1)); acc += np.roll(rgb, (dy, dx), (0, 1)) * h[..., None]; cnt += h
        new = (~have) & (cnt > 0); rgb[new] = acc[new] / cnt[new][:, None]; have |= new
    Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), 'RGBA').save(bio, 'PNG', optimize=True); mime = 'image/png'
    M['alphaMode'] = 'MASK'; M['alphaCutoff'] = 0.5
else:
    im.convert('RGB').save(bio, 'JPEG', quality=90, optimize=True); mime = 'image/jpeg'
    M.pop('alphaMode', None); M.pop('alphaCutoff', None)
data = bio.getvalue(); views = J['bufferViews']; target = J['images'][img_i]['bufferView']; nb = bytearray()
for i, v in enumerate(views):
    d = data if i == target else BIN[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
    while len(nb) % 4: nb.append(0)
    v['byteOffset'] = len(nb); v['byteLength'] = len(d); nb.extend(d)
while len(nb) % 4: nb.append(0)
J['buffers'][0]['byteLength'] = len(nb); J['images'][img_i]['mimeType'] = mime
js = json.dumps(J, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(nb)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(nb), 0x004E4942) + bytes(nb)
shutil.copy(path, path + '.vor_ersetzen'); open(path, 'wb').write(glb)
print('ersetzt: Material', mat_name, 'Bild', img_i, im.size, mime, len(data), 'Bytes ->', path, len(glb), 'Bytes')
