#!/usr/bin/env python3
"""UV-Abwicklung des Lack-Teils (Chunk „gloss“) der Automodelle car.bin / f2car.bin für echte Lackierungs-Texturen.

Aufruf:  python3 tools/textur/uv.py f1        (f2 entsprechend)
Liest:   die unveränderte Vorlage tools/textur/quelle/<car|f2car>.bin (wird beim ersten Lauf aus dem Projektordner kopiert)
Schreibt: <car|f2car>.bin mit UV-Koordinaten im Lack-Teil (Feld „uv“, uint16 × 2 je Eckpunkt) und im Kopf „tex“: [Breite, Höhe] der Textur.

- Alle drei Detailstufen liegen in EINER Textur. Stufe 1 (ab 18 m) und 2 (ab 45 m) bekommen nur einen kleinen Teil (Längenmaßstab STUFE).
- Die Eckpunkte des Modells sind an harten Kanten schon getrennt; für die Abwicklung werden sie über die Lage verschweißt (sonst zerfällt das Auto in
  noch mehr Einzelstücke und der Rand um jedes Stück frisst die Textur). Danach wird das Ergebnis Ecke für Ecke auf die Original-Eckpunkte übertragen:
  neuer Eckpunkt = (alter Eckpunkt, UV) – Lage, Normale und Klasse bleiben exakt wie in der Vorlage.
- Rand je Stück PAD Bildpunkte; backen.js füllt die Lücken danach mit den Randfarben auf (sonst bluten Mipmaps über die Nähte).
"""
import json, struct, sys, os, shutil
import numpy as np, xatlas

KIND = sys.argv[1] if len(sys.argv) > 1 else 'f1'
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
NAME = 'car.bin' if KIND == 'f1' else 'f2car.bin'
SRC = os.path.join(HERE, 'quelle', NAME); DST = os.path.join(ROOT, NAME)
TPU = 300                  # Bildpunkte je Meter in Stufe 0 (heutige Aufkleberbögen: ~370, aber nur von der Seite)
STUFE = [1.0, 0.30, 0.15]  # Längenmaßstab je Detailstufe in der Textur
PAD = 2

if not os.path.exists(SRC):
    os.makedirs(os.path.dirname(SRC), exist_ok=True); shutil.copy(DST, SRC); print('Vorlage gesichert:', SRC)
b = open(SRC, 'rb').read(); hl = struct.unpack('<I', b[:4])[0]; H = json.loads(b[4:4 + hl]); base = 4 + hl
if any('uv' in c for c in H['chunks']): sys.exit('Vorlage hat schon UVs – bitte die unveränderte .bin nach ' + SRC + ' legen')

def arr(c, key, dt, n): return np.frombuffer(b, dt, n, base + c[key]).copy()
chunks = []
for c in H['chunks']:
    d = dict(c); d['q'] = arr(c, 'pos', np.int16, c['nv'] * 3).reshape(-1, 3); d['n'] = arr(c, 'nrm', np.int8, c['nv'] * 4).reshape(-1, 4)
    d['c'] = arr(c, 'cls', np.uint8, c['nv']); d['i'] = arr(c, 'idx', np.uint32 if c['i32'] else np.uint16, c['ni']).astype(np.int64)
    chunks.append(d)

atlas = xatlas.Atlas(); parts = []
for d in chunks:
    if d['name'] != 'gloss': continue
    L = d['lod']; P = np.array(d['min']) + (d['q'].astype(np.float64) + 32768) / 65535 * np.array(d['rg'])
    T = d['i'].reshape(-1, 3)
    _, first, inv = np.unique(np.round(P / 2e-4).astype(np.int64), axis=0, return_index=True, return_inverse=True)
    atlas.add_mesh((P[first] * STUFE[L]).astype(np.float32), inv.reshape(-1)[T].astype(np.uint32))
    parts.append((d, T))
co = xatlas.ChartOptions(); po = xatlas.PackOptions(); po.padding = PAD; po.bilinear = True; po.texels_per_unit = TPU; po.resolution = 0; po.rotate_charts = True
atlas.generate(co, po)
W, Hh = atlas.width, atlas.height
print(f'Textur {W} × {Hh} ({W * Hh / 1e6:.2f} Mio. Bildpunkte, {atlas.chart_count} Stücke, Auslastung {atlas.utilization:.2f}), {TPU} Bildpunkte je Meter in Stufe 0')

for k, (d, T) in enumerate(parts):
    vm, ix, uv = atlas[k]; ix = ix.astype(np.int64).reshape(-1, 3)
    if len(ix) != len(T): sys.exit('Dreiecksreihenfolge geändert – Abbruch')
    old = T.reshape(-1); new = ix.reshape(-1)
    key, first, inv = np.unique(old * (1 << 22) + new, return_index=True, return_inverse=True)
    src = old[first]
    nv0 = len(d['q']); d['q'], d['n'], d['c'] = d['q'][src], d['n'][src], d['c'][src]
    d['i'] = inv.reshape(-1).astype(np.int64)
    d['uvq'] = np.clip(np.round(uv[new[first]].astype(np.float64) * 65535), 0, 65535).astype(np.uint16)
    print(f'Stufe {d["lod"]}: Eckpunkte {nv0} -> {len(src)}')

blob = bytearray(); hdr = {k: v for k, v in H.items() if k != 'chunks'}; hdr['tex'] = [W, Hh]; hdr['chunks'] = []
def put(a):
    while len(blob) % 4: blob.append(0)
    o = len(blob); blob.extend(a.tobytes()); return o
for d in chunks:
    nv = len(d['q']); i32 = nv > 65535
    c = {k: d[k] for k in ('name', 'lod', 'min', 'rg')}; c['nv'] = nv; c['ni'] = len(d['i']); c['i32'] = i32
    c['pos'] = put(d['q'].astype(np.int16)); c['nrm'] = put(d['n'].astype(np.int8)); c['cls'] = put(d['c'].astype(np.uint8))
    c['idx'] = put(d['i'].astype(np.uint32 if i32 else np.uint16))
    if 'uvq' in d: c['uv'] = put(d['uvq'])
    hdr['chunks'].append(c)
hj = json.dumps(hdr, separators=(',', ':')).encode()
hj += b' ' * (-len(hj) % 4)   # Daten auf 4 Byte ausrichten (Typed Arrays im Spiel)
open(DST, 'wb').write(struct.pack('<I', len(hj)) + hj + bytes(blob))
print('geschrieben', DST, os.path.getsize(DST), 'Bytes (Vorlage', len(b), ')')
