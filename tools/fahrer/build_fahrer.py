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
sc = trimesh.load(io.BytesIO(dae), file_type='dae', force='scene', resolver=None)
g = trimesh.util.concatenate(list(sc.dump()))
gV, gF, gUV = g.vertices.copy(), g.faces.copy(), g.visual.uv.copy()
# Vorlage: Finger +y, Handfläche +z, Daumen +x, Stulpe unten (y ≈ -23,6), Einheit beliebig.
# Ziel (rechte Hand, Körperseite -x): Finger nach unten, Handfläche zum Oberschenkel (+x), Daumen nach vorn (+z).
wrist_src = np.array([0.0, -13.5, 9.2])                               # Handgelenk in der Vorlage (Beginn der Stulpe)
s = 0.0092                                                              # Vorlagen-Einheit -> Meter
R = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float)                 # Spalten: Bild von x, y, z
tilt = trimesh.transformations.rotation_matrix(-0.12, [1, 0, 0])[:3, :3]   # Hand leicht nach vorn wie der Unterarm
wrist_dst = np.array([-0.128, 0.466, -0.002]) * H
gV = ((gV - wrist_src) * s) @ (tilt @ R).T + wrist_dst
glove = trimesh.Trimesh(gV, gF, process=False)
gm = trimesh.visual.material.PBRMaterial(name='handschuh', baseColorTexture=tex, metallicFactor=0.0, roughnessFactor=0.7, doubleSided=True)
glove.visual = trimesh.visual.TextureVisuals(uv=gUV, material=gm)
glove.export(os.path.join(OUT, 'handschuh.glb'))
print('Handschuh:', len(glove.vertices), 'Eckpunkte,', len(glove.faces), 'Dreiecke')
