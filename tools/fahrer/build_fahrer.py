"""Baut den Rennfahrer fürs Spiel aus den Vorlagen (Tripo-Körper + Handschuh-KMZ).

Aufruf:  python3 tools/fahrer/build_fahrer.py <quellordner>
Der Quellordner enthält: model.obj, base.jpg, normal.jpg (Körper, Tripo) und glove.kmz (Handschuh).
Ergebnis: fahrer/fahrer.glb (Körper ohne Kopf/Hände) und fahrer/handschuh.glb (rechter Handschuh, schon an die rechte Hand gesetzt).
Der Helm kommt im Spiel aus HELM_BIN (index.html), der linke Handschuh ist der gespiegelte rechte.
Maße in Metern, Blick nach +z, y nach oben, Füße auf y = 0.
"""
import sys, os, io, zipfile, numpy as np, trimesh
from PIL import Image

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'fahrer')
H = 1.78                    # Körpergröße (Tripo-Modell ist auf Höhe 1 normiert)
os.makedirs(OUT, exist_ok=True)

# ---------- Körper ----------
m = trimesh.load(os.path.join(SRC, 'model.obj'), process=False, force='mesh')
V, F, UV = m.vertices.copy(), m.faces.copy(), m.visual.uv.copy()
w = trimesh.Trimesh(V, F, process=False); w.merge_vertices()          # Nachbarschaft über die UV-Nähte hinweg
comp = trimesh.graph.connected_component_labels(w.face_adjacency, node_count=len(F))
cnt = np.bincount(comp)
keep = cnt[comp] > 100                                                  # Splitter (doppelte Einzeldreiecke) weg
cen = V[F].mean(1)
for c in np.unique(comp):                                               # Kopf mit Tripo-Helm weg (unser Helm kommt drauf)
    if cnt[c] > 100 and cen[comp == c][:, 1].min() > 0.8: keep &= comp != c
hand = (cen[:, 1] < 0.466) & (np.abs(cen[:, 0]) > 0.104) & (cen[:, 1] > 0.3)   # Hände: werden durch die Handschuhe ersetzt
keep &= ~hand
F = F[keep]
used = np.unique(F); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
body = trimesh.Trimesh(V[used] * H, remap[F], process=False)
base = Image.open(os.path.join(SRC, 'base.jpg')).convert('RGB')
nor = Image.open(os.path.join(SRC, 'normal.jpg')).convert('RGB')
mat = trimesh.visual.material.PBRMaterial(name='anzug', baseColorTexture=base, normalTexture=nor, metallicFactor=0.0, roughnessFactor=0.78)
body.visual = trimesh.visual.TextureVisuals(uv=UV[used], material=mat)
body.export(os.path.join(OUT, 'fahrer.glb'))
print('Körper:', len(body.vertices), 'Eckpunkte,', len(body.faces), 'Dreiecke')

# ---------- Handschuh (rechts) ----------
z = zipfile.ZipFile(os.path.join(SRC, 'glove.kmz'))
dae = z.read('models/kmz.dae')
tex = Image.open(io.BytesIO(z.read('images/None - Default Texture.JPG'))).convert('RGB')
# Logo-Schriftzug auf der Klett-Lasche (Textur x 420…580, y 285…425) wird durch das Aufweiten der Stulpe zu einem weißen Fleck verzogen:
# helle Pixel dort mit dem Rot der Lasche übermalen
ta = np.asarray(tex).copy(); reg = ta[285:425, 420:580]
red = np.median(ta[330:380, 600:650].reshape(-1, 3), axis=0).astype(np.uint8)
reg[reg.astype(int).min(2) > 120] = red
tex = Image.fromarray(ta)
sc = trimesh.load(io.BytesIO(dae), file_type='dae', force='scene', resolver=None)
g = trimesh.util.concatenate(list(sc.dump()))
gV, gF, gUV = g.vertices.copy(), g.faces.copy(), g.visual.uv.copy()
# Vorlage: Finger +y, Handfläche +z, Daumen +x, Stulpe unten (y ≈ -23,6), Einheit beliebig.
# Ziel (rechte Hand, Körperseite -x): Finger nach unten, Handfläche zum Oberschenkel (+x), Daumen nach vorn (+z).
wrist_src = np.array([-0.4, -15.5, 9.3])                              # Handgelenk in der Vorlage (schmalste Stelle über der Stulpe)
# Stulpe steckt im Ärmel (Bündchen liegt darüber): nur so weit aufweiten, dass sie die Ärmelöffnung von innen ausfüllt
t = np.clip((-14.5 - gV[:, 1]) / 2.5, 0, 1); t = t * t * (3 - 2 * t)
gV[:, 0] = wrist_src[0] + (gV[:, 0] - wrist_src[0]) * (1 + 0.05 * t)
gV[:, 2] = wrist_src[2] + (gV[:, 2] - wrist_src[2]) * (1 + 0.15 * t)
lo = gV[:, 1] < -15.5; gV[lo, 1] = -15.5 + (gV[lo, 1] + 15.5) * 0.25   # Stulpe kürzen: steckt nur ~2,5 cm im Ärmel
# Finger locker zur Handfläche (+z) gekrümmt: ab den Knöcheln kreisförmig biegen, Winkel wächst mit dem Abstand
y0, Rb = -1.0, 9.0                                                     # Knöchellinie (Vorlage), Biegeradius -> Fingerspitzen ~40° gekrümmt
yy = np.maximum(gV[:, 1] - y0, 0); zax = 9.3 + Rb                      # Biegeachse parallel zu x, vor der Handfläche
d = zax - gV[:, 2]; m_ = yy > 0
gV[m_, 1] = y0 + d[m_] * np.sin(yy[m_] / Rb)
gV[m_, 2] = zax - d[m_] * np.cos(yy[m_] / Rb)
s = 0.0092                                                              # Vorlagen-Einheit -> Meter
R = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)                 # Spalten: Bild von x, y, z
tilt = trimesh.transformations.rotation_matrix(-0.38, [1, 0, 0])[:3, :3]   # Hand nach vorn wie der Unterarm
wrist_dst = np.array([-0.137, 0.475, -0.002]) * H                     # Mitte des abgeschnittenen Ärmelendes
gV = ((gV - wrist_src) * s) @ (tilt @ R).T + wrist_dst
gF = gF[(gV[gF][:, :, 1] < wrist_dst[1] + 0.012).all(1)]                 # was oben im Ärmel verschwindet, ganz weg (sonst stößt die Stulpe am Rand durch)
glove = trimesh.Trimesh(gV, gF, process=False)
gm = trimesh.visual.material.PBRMaterial(name='handschuh', baseColorTexture=tex, metallicFactor=0.0, roughnessFactor=0.7, doubleSided=True)
glove.visual = trimesh.visual.TextureVisuals(uv=gUV, material=gm)
glove.export(os.path.join(OUT, 'handschuh.glb'))
print('Handschuh:', len(glove.vertices), 'Eckpunkte,', len(glove.faces), 'Dreiecke')
