"""Baut den Rennfahrer aus den Vorlagen (Tripo-Körper + Handschuh-KMZ).

Aufruf:  python3 tools/fahrer/build_fahrer.py <quellordner>
Quellordner: model.obj, base.jpg, normal.jpg (Körper, Tripo) und glove.kmz (Handschuh).
Braucht: numpy, pillow, scipy, trimesh, pymeshlab.

Ergebnis:
  fahrer/fahrer.glb, fahrer/handschuh.glb   stehende Figur (Vorschau: fahrer/vorschau.html; Kart-Prüfansicht: fahrer/kart_vorschau.html)
  kartfahrer.bin                           sitzender Kart-Fahrer fürs Spiel (Körper + beide Handschuhe, ein Netz)
  textures/kart_fahrer.jpg, _n.jpg         Atlas (links Anzug, rechts Handschuh) + Normalen

Ablauf:
  1. Körper aufräumen: Splitter, Kopf (Tripo-Helm) und Hände weg; Ärmel sauber quer zum Unterarm abschneiden.
  2. Textur säubern: Logos, Schriftzüge und dunkle Fehlstellen (Fersen, Achseln, Seitennähte) entfernen.
     Übrig bleibt eine helle Stoff-Schattierung, die im Spiel mit den Teamfarben eingefärbt wird.
  3. Verkleinern (Kantenzusammenlegung mit Erhalt der Textur).
  4. Kart: Figur über ein einfaches Skelett in die Sitzhaltung biegen (Rumpf zurückgelehnt, Beine nach vorn,
     Hände am Lenkrad per Zwei-Knochen-IK), Handschuhe zur Faust um den Lenkradkranz gekrümmt.
"""
import sys, os, io, json, zipfile, struct
import numpy as np, trimesh, pymeshlab
from PIL import Image, ImageFilter
from scipy import ndimage
from trimesh.intersections import slice_faces_plane

SRC = sys.argv[1]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
H = 1.78                                   # Körpergröße der stehenden Figur (Tripo ist auf Höhe 1 normiert)

# ---------- Gelenke der Tripo-Vorlage (normiert, rechte Körperseite = -x, Blick +z) ----------
J = {'hip': (-0.050, 0.500, -0.003), 'knee': (-0.054, 0.280, -0.015), 'ankle': (-0.054, 0.070, -0.040), 'toe': (-0.060, 0.020, 0.075),
     'pelvis': (0.0, 0.500, -0.005), 'neck': (0.0, 0.830, -0.030), 'head': (0.0, 0.912, 0.008),
     'sh': (-0.105, 0.790, -0.040), 'el': (-0.125, 0.605, -0.056), 'wr': (-0.137, 0.475, -0.002)}
J = {k: np.array(v) for k, v in J.items()}
mir = lambda p: p * np.array([-1, 1, 1])


def nrm(v): return v / np.linalg.norm(v)


# ======================================================================================
# 1. Körper aufräumen
# ======================================================================================
def load_body():
    m = trimesh.load(os.path.join(SRC, 'model.obj'), process=False, force='mesh')
    V, F, UV = m.vertices.copy(), m.faces.copy(), m.visual.uv.copy()
    w = trimesh.Trimesh(V, F, process=False); w.merge_vertices()
    comp = trimesh.graph.connected_component_labels(w.face_adjacency, node_count=len(F)); cnt = np.bincount(comp)
    cen = V[F].mean(1); keep = cnt[comp] > 100                                  # Splitter weg
    for c in np.unique(comp):                                                     # Kopf mit Tripo-Helm weg
        if cnt[c] > 100 and cen[comp == c][:, 1].min() > 0.8: keep &= comp != c
    # Hände: Arm-Bereich unterhalb des Handgelenks grob weg, dann sauber quer zum Unterarm schneiden
    arm = (np.abs(cen[:, 0]) > 0.104) & (cen[:, 1] > 0.3) & (cen[:, 1] < 0.56)
    keep &= ~(arm & (cen[:, 1] < 0.44))
    F_keep, F_arm = F[keep & ~arm], F[keep & arm]
    newV, newUV, faces = [V], [UV], [F_keep]
    nV = len(V)
    for s in (-1, 1):
        fa = F_arm[np.sign(V[F_arm].mean(1)[:, 0]) == s]
        el, wr = (J['el'], J['wr']) if s < 0 else (mir(J['el']), mir(J['wr']))
        n = nrm(el - wr)                                                           # behalten: Seite zum Ellbogen
        o = wr + n * 0.008
        sv, sf, suv = slice_faces_plane(V, fa, n, o, uv=UV)
        newV.append(sv); newUV.append(suv); faces.append(sf + nV); nV += len(sv)
    V2, UV2, F2 = np.vstack(newV), np.vstack(newUV), np.vstack(faces)
    used = np.unique(F2); remap = -np.ones(len(V2), int); remap[used] = np.arange(len(used))
    return V2[used], remap[F2], UV2[used]


# ======================================================================================
# 2. Textur säubern
# ======================================================================================
def clean_texture():
    img = Image.open(os.path.join(SRC, 'base.jpg')).convert('RGB')
    a = np.asarray(img).astype(np.float32) / 255
    L = a @ np.array([0.299, 0.587, 0.114], np.float32)
    sat = a.max(2) - a.min(2)
    # dunkle oder farbige Stellen (Logos, Schrift, Fehlstellen) als Loch markieren und von außen her auffüllen
    ref = ndimage.median_filter(L, size=31)
    bad = (L < ref - 0.06) | (sat > 0.12) | (L < 0.55)
    bad = ndimage.binary_dilation(bad, iterations=3)
    out = L.copy()
    good = ~bad
    # Auffüllen: wiederholt mit dem Mittel der guten Nachbarn (Push-Pull über eine Gauß-Pyramide)
    filled = L * good; wgt = good.astype(np.float32)
    acc_v, acc_w = np.zeros_like(L), np.zeros_like(L)
    for sig in (2, 4, 8, 16, 32, 64):
        acc_v = ndimage.gaussian_filter(filled, sig); acc_w = ndimage.gaussian_filter(wgt, sig)
        est = acc_v / np.maximum(acc_w, 1e-4)
        take = (~good) & (acc_w > 0.15)
        out[take] = est[take]; filled = np.where(take, est, filled); wgt = np.where(take, 1.0, wgt); good = good | take
    # Kontrast der Stoff-Schattierung ruhig halten: hell, leichte Falten bleiben
    out = ndimage.gaussian_filter(out, 1.2)
    out = np.clip(0.84 + (out - np.median(out)) * 0.5, 0.65, 1.0)
    return Image.fromarray((out * 255).astype(np.uint8)).convert('RGB')


# ======================================================================================
# 3. Verkleinern mit Erhalt der Textur
# ======================================================================================
def decimate(V, F, UV, target):
    w = trimesh.Trimesh(V, F, process=False); w.merge_vertices(merge_tex=True, merge_norm=True)
    # verschweißte Positionen, UV je Ecke (Wedge) aus dem Original
    wuv = UV[F].reshape(-1, 2)
    # über eine OBJ-Datei laden: so kennt MeshLab die Textur je Fläche (direkt übergebene UV gelten als "ohne Textur")
    import tempfile
    tmp = tempfile.mkdtemp(); Image.new('RGB', (4, 4)).save(os.path.join(tmp, 't.png'))
    with open(os.path.join(tmp, 'm.mtl'), 'w') as fo: fo.write('newmtl m\nmap_Kd t.png\n')
    with open(os.path.join(tmp, 'm.obj'), 'w') as fo:
        fo.write('mtllib m.mtl\n'); fo.write(''.join(f'v {a:.6f} {b:.6f} {c:.6f}\n' for a, b, c in w.vertices))
        fo.write(''.join(f'vt {a:.6f} {b:.6f}\n' for a, b in wuv)); fo.write('usemtl m\n')
        fo.write(''.join(f'f {a + 1}/{3 * i + 1} {b + 1}/{3 * i + 2} {c + 1}/{3 * i + 3}\n' for i, (a, b, c) in enumerate(w.faces)))
    ms = pymeshlab.MeshSet(); ms.load_new_mesh(os.path.join(tmp, 'm.obj'))
    ms.meshing_decimation_quadric_edge_collapse_with_texture(targetfacenum=int(target), qualitythr=0.5, extratcoordw=1.0, preserveboundary=True, boundaryweight=2.0, optimalplacement=True, preservenormal=True, planarquadric=True)
    m = ms.current_mesh()
    v, f, t = m.vertex_matrix(), m.face_matrix(), m.wedge_tex_coord_matrix().reshape(-1, 3, 2)
    # Ecken mit gleicher Position+UV zusammenfassen -> Eckpunkte je UV
    key = np.round(np.hstack([np.repeat(f.reshape(-1, 1), 1, 1), t.reshape(-1, 2) * 8192]), 0)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    V2 = v[uniq[:, 0].astype(int)]; UV2 = uniq[:, 1:] / 8192; F2 = inv.reshape(-1, 3)
    return V2, F2, UV2


# ======================================================================================
# Handschuh
# ======================================================================================
def load_glove():
    z = zipfile.ZipFile(os.path.join(SRC, 'glove.kmz'))
    tex = Image.open(io.BytesIO(z.read('images/None - Default Texture.JPG'))).convert('RGB')
    ta = np.asarray(tex).copy(); reg = ta[285:425, 420:580]                         # Logo-Schriftzug auf der Klett-Lasche übermalen
    red = np.median(ta[330:380, 600:650].reshape(-1, 3), axis=0).astype(np.uint8)
    reg[reg.astype(int).min(2) > 120] = red
    tex = Image.fromarray(ta)
    sc = trimesh.load(io.BytesIO(z.read('models/kmz.dae')), file_type='dae', force='scene', resolver=None)
    g = trimesh.util.concatenate(list(sc.dump()))
    return g.vertices.copy(), g.faces.copy(), g.visual.uv.copy(), tex

# Vorlage: Finger +y, Handfläche +z, Daumen +x, Stulpe unten; Handgelenk an der schmalsten Stelle
G_WRIST = np.array([-0.4, -15.5, 9.3]); G_S = 0.0092                              # Vorlagen-Einheit -> Meter (bei H = 1,78)


def glove_shape(gV, Rb, y0=-1.0):
    """Stulpe kürzen/leicht weiten (steckt im Ärmel) und Finger um eine Achse vor der Handfläche krümmen."""
    gV = gV.copy()
    t = np.clip((-14.5 - gV[:, 1]) / 2.5, 0, 1); t = t * t * (3 - 2 * t)
    gV[:, 0] = G_WRIST[0] + (gV[:, 0] - G_WRIST[0]) * (1 + 0.05 * t)
    gV[:, 2] = G_WRIST[2] + (gV[:, 2] - G_WRIST[2]) * (1 + 0.15 * t)
    lo = gV[:, 1] < -15.5; gV[lo, 1] = -15.5 + (gV[lo, 1] + 15.5) * 0.25
    yy = np.maximum(gV[:, 1] - y0, 0); zax = 9.3 + Rb; d = zax - gV[:, 2]; m = yy > 0
    gV[m, 1] = y0 + d[m] * np.sin(yy[m] / Rb); gV[m, 2] = zax - d[m] * np.cos(yy[m] / Rb)
    return gV, np.array([-0.4, y0, zax])                                             # zweiter Wert: Punkt auf der Krümmungsachse


def glove_texture(tex):
    """Rot -> Weiß (wird im Spiel mit der Teamfarbe eingefärbt), Schwarz/Grau bleiben."""
    a = np.asarray(tex).astype(np.float32) / 255
    red = np.clip((a[..., 0] - np.maximum(a[..., 1], a[..., 2]) - 0.15) / 0.3, 0, 1)
    lum = a.max(2)
    white = np.stack([lum] * 3, -1) * 1.0
    out = a * (1 - red[..., None]) + white * red[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# ======================================================================================
# 4. Sitzhaltung (Kart)
# ======================================================================================
def rot_between(a, b):
    a, b = nrm(a), nrm(b); v = np.cross(a, b); c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-9: return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def rot_x(a): c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def seg_dist(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(P - (a + t[:, None] * ab), axis=1)


def pose_kart(V, S):
    """V: Körper in Metern (Ruhehaltung, Maßstab S). Gibt gebogene Eckpunkte, Helm-Anker und Handgelenk-Ziele zurück."""
    j = {k: v * S for k, v in J.items()}
    bones = {}                                                                         # name: (Kopf, Ende)
    for s, sfx in ((-1, 'R'), (1, 'L')):
        f = (lambda p: p) if s < 0 else mir
        bones['thigh' + sfx] = (f(j['hip']), f(j['knee'])); bones['shin' + sfx] = (f(j['knee']), f(j['ankle'])); bones['foot' + sfx] = (f(j['ankle']), f(j['toe']))
        bones['uarm' + sfx] = (f(j['sh']), f(j['el'])); bones['farm' + sfx] = (f(j['el']), f(j['wr']))
    bones['spine'] = (j['pelvis'], j['neck'])

    # ---- Zielhaltung (Kart-Koordinaten: vorne +z, rechts -x) ----
    hipT = np.array([0, 0.19, -0.30]); lean = np.radians(24)
    Rsp = rot_x(-lean)                                                                 # Rumpf nach hinten gelehnt
    T = {'spine': (Rsp, hipT)}                                                          # Knochen: (Drehung, Zielposition des Kopfs)
    # Lenkrad (aus makeKart): Mitte (0, 0.5005, 0.1235), Achsen axx=(-1,0,0), az=nrm(0,29,-36), ay=az×axx, Kranzradius 0.188
    az = nrm(np.array([0, 29, -36.0])); axx = np.array([-1.0, 0, 0]); ay = np.cross(az, axx); C = np.array([0, 0.5005, 0.1235])
    out = {'grip': {}}
    for s, sfx in ((-1, 'R'), (1, 'L')):
        f = (lambda p: p) if s < 0 else mir
        # Beine: Oberschenkel leicht nach vorn-oben, Unterschenkel nach vorn zu den Pedalen, Füße aufgestellt
        hip = hipT + f(j['hip'] - j['pelvis'])
        dth = nrm(f(np.array([-0.06, 0.20, 1.0]))) ; Rth = rot_between(bones['thigh' + sfx][1] - bones['thigh' + sfx][0], dth)
        knee = hip + dth * np.linalg.norm(j['knee'] - j['hip'])
        dsh = nrm(f(np.array([0.02, -0.30, 1.0]))); Rsh = rot_between(bones['shin' + sfx][1] - bones['shin' + sfx][0], dsh)
        ankle = knee + dsh * np.linalg.norm(j['ankle'] - j['knee'])
        dft = nrm(f(np.array([-0.05, 0.75, 0.55]))); Rft = rot_between(bones['foot' + sfx][1] - bones['foot' + sfx][0], dft) @ Rsh
        Rft = rot_between(Rsh @ (bones['foot' + sfx][1] - bones['foot' + sfx][0]), dft) @ Rsh
        T['thigh' + sfx] = (Rth, hip); T['shin' + sfx] = (Rsh, knee); T['foot' + sfx] = (Rft, ankle)
        # Arme: Griff bei 9/3 Uhr; Hand außen am Kranz, Finger umfassen ihn nach innen
        # rechte Hand: lokales +x des Lenkrads = Welt -x; Wrap-Achse entlang des Kranzes (ay), Finger nach vorn (-az), Handfläche nach innen.
        # Linke Hand = Spiegelbild der rechten (x -> -x).
        Mx = np.array([-1.0, 1, 1])
        grip = C + axx * 0.188 + ay * (-0.02); Xg = ay; Yg = -az; Zg = np.cross(Xg, Yg)
        if sfx == 'R': out['grip'] = (grip, Xg, Yg, Zg)
        wristT = glove_wrist_world(grip, Xg, Yg, Zg, S)
        if s > 0: wristT = wristT * Mx; Yg = Yg * Mx
        sh = hipT + Rsp @ f(j['sh'] - j['pelvis'])
        L1, L2 = np.linalg.norm(j['el'] - j['sh']), np.linalg.norm(j['wr'] - j['el'])
        dvec = wristT - sh; dist = np.linalg.norm(dvec)
        out.setdefault('reach', {})[sfx] = (dist, L1 + L2)
        dist_c = min(dist, (L1 + L2) * 0.999)
        # Ellbogen auf dem IK-Kreis: so wählen, dass der Unterarm möglichst in Richtung der Hand zeigt (-Yg) und nach außen/unten
        u = nrm(dvec); a = (L1 ** 2 - L2 ** 2 + dist_c ** 2) / (2 * dist_c); r = np.sqrt(max(L1 ** 2 - a ** 2, 0)); c0 = sh + u * a
        e1 = nrm(np.cross(u, [0, 1, 0])); e2 = np.cross(u, e1); best = None
        for ang in np.linspace(0, 2 * np.pi, 72, endpoint=False):
            el = c0 + r * (np.cos(ang) * e1 + np.sin(ang) * e2); fa = nrm(wristT - el)
            sc = np.dot(fa, Yg) * 1.0 + np.dot(nrm(el - sh), np.array([-s * 0.6, -1, 0.2])) * 0.6
            if best is None or sc > best[0]: best = (sc, el)
        el = best[1]
        Rua = rot_between(bones['uarm' + sfx][1] - bones['uarm' + sfx][0], el - sh)
        wr_reached = el + nrm(wristT - el) * L2
        Rfa = rot_between(bones['farm' + sfx][1] - bones['farm' + sfx][0], wr_reached - el)
        T['uarm' + sfx] = (Rua, sh); T['farm' + sfx] = (Rfa, el)
        out.setdefault('wrist', {})[sfx] = (wr_reached, wristT)

    # ---- Gewichte: Abstand zu den erlaubten Knochen je Körperbereich ----
    P = V; x, y = P[:, 0] / S, P[:, 1] / S
    names = list(bones.keys()); D = np.stack([seg_dist(P, *bones[n]) for n in names], 1)
    allow = np.zeros_like(D, bool); ix = {n: i for i, n in enumerate(names)}
    armR = (x < -0.104) & (y < 0.80) & (y > 0.40); armL = (x > 0.104) & (y < 0.80) & (y > 0.40)
    leg = y < 0.55
    for i, n in enumerate(names):
        sfx = n[-1]; sideMask = (x < 0.004) if sfx == 'R' else (x > -0.004)
        if n.startswith(('uarm', 'farm')):
            allow[:, i] = (armR if sfx == 'R' else armL) | (((x < -0.07) if sfx == 'R' else (x > 0.07)) & (y > 0.72) & (y < 0.83))
        elif n.startswith(('thigh', 'shin', 'foot')):
            allow[:, i] = leg & sideMask & ~(armR | armL)
        else:
            allow[:, i] = ~(armR | armL) & (y > 0.40)
    allow[:, ix['spine']] |= ~allow.any(1)
    W = np.where(allow, 1 / (D + 0.012) ** 6, 0); W /= W.sum(1, keepdims=True)
    Vn = np.zeros_like(P)
    for i, n in enumerate(names):
        R, head = T[n]; Vn += W[:, i:i + 1] * ((P - bones[n][0]) @ R.T + head)
    out['head'] = hipT + Rsp @ (j['neck'] - j['pelvis']) + (j['head'] - j['neck'])   # Kopf aufrecht auf dem zurückgelehnten Hals (Blick nach vorn); out['lean'] = lean; out['T'] = T; out['bones'] = bones
    return Vn, out


Y0_KART = -4.5                                                                         # Faust: Krümmung ab den Fingerwurzeln


def glove_wrist_world(grip, Xg, Yg, Zg, S):
    gV, ax = glove_shape(G_WRIST[None], RB_KART, Y0_KART)
    p = (G_WRIST - ax) * G_S * S / H
    R = np.stack([Xg, Yg, Zg], 1)
    return grip + R @ p


RB_KART = 2.9                                                                          # Krümmungsradius der Faust (Vorlagen-Einheiten)


def place_glove(gV0, gF, grip, Xg, Yg, Zg, S):
    gV, ax = glove_shape(gV0, RB_KART, Y0_KART)
    p = (gV - ax) * G_S * S / H
    R = np.stack([Xg, Yg, Zg], 1)
    return grip + p @ R.T, gF


def smooth_normals(V, F):
    """Normalen über gleiche Positionen gemittelt (sonst harte Kanten an den UV-Nähten)."""
    mesh = trimesh.Trimesh(V, F, process=False); fn = mesh.face_normals * mesh.area_faces[:, None]
    key = np.unique(np.round(V, 5), axis=0, return_inverse=True)[1].reshape(-1)
    acc = np.zeros((key.max() + 1, 3)); np.add.at(acc, key[F].reshape(-1), np.repeat(fn, 3, 0))
    N = acc[key]; return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)


# ======================================================================================
# Hauptablauf
# ======================================================================================
def main():
    os.makedirs(os.path.join(ROOT, 'fahrer'), exist_ok=True)
    V, F, UV = load_body()
    print('Körper aufgeräumt:', len(F), 'Dreiecke')
    tex = clean_texture()
    nor = Image.open(os.path.join(SRC, 'normal.jpg')).convert('RGB')
    gV0, gF0, gUV0, gtex = load_glove()

    # ---- stehende Figur (Vorschau) ----
    sV, sF, sUV = decimate(V, F, UV, 24000)
    body = trimesh.Trimesh(sV * H, sF, vertex_normals=smooth_normals(sV * H, sF), process=False)
    body.visual = trimesh.visual.TextureVisuals(uv=sUV, material=trimesh.visual.material.PBRMaterial(name='anzug', baseColorTexture=tex, normalTexture=nor, metallicFactor=0.0, roughnessFactor=0.8))
    body.export(os.path.join(ROOT, 'fahrer', 'fahrer.glb'))
    gV, _ = glove_shape(gV0, 9.0)
    R = np.array([[0, 0, 1], [0, -1, 0], [1, 0, 0]], float) @ np.eye(3)
    tilt = trimesh.transformations.rotation_matrix(-0.38, [1, 0, 0])[:3, :3]
    wd = np.array([-0.137, 0.475, -0.002]) * H
    gW = ((gV - G_WRIST) * G_S) @ (tilt @ R).T + wd
    keepf = (gW[gF0][:, :, 1] < wd[1] + 0.012).all(1)
    glove = trimesh.Trimesh(gW, gF0[keepf], process=False)
    glove.visual = trimesh.visual.TextureVisuals(uv=gUV0, material=trimesh.visual.material.PBRMaterial(name='handschuh', baseColorTexture=gtex, metallicFactor=0.0, roughnessFactor=0.7, doubleSided=True))
    glove.export(os.path.join(ROOT, 'fahrer', 'handschuh.glb'))
    print('stehend:', len(sF), 'Dreiecke Körper')

    # ---- Kart-Fahrer ----
    S = H * 1.10                                                                        # Kart ist größer gebaut (Helm dort ~0,33 m hoch)
    kV, kF, kUV = decimate(V, F, UV, 9000)
    Pk, info = pose_kart(kV * S, S)
    for k, (d, L) in info['reach'].items(): print(f'Reichweite {k}: Abstand {d:.3f} m, Armlänge {L:.3f} m')
    # Bereiche: 0 Körper, 3 Handschuh. Dazu je Eckpunkt die Höhe in Ruhehaltung (normiert): daraus zieht der Shader
    # Gürtel (0,548…0,592) und Schuhe (< 0,072) pixelgenau – Farbwechsel je Eckpunkt gäbe bei ~9000 Dreiecken Treppenkanten.
    reg = np.zeros(len(kV), np.uint8); ry = kV[:, 1].astype(np.float32)
    ry[(np.abs(kV[:, 0]) > 0.104) & (kV[:, 1] > 0.3)] = 0.5                         # Arme: kein Gürtelband auf den Unterarmen
    # Handschuhe (verkleinert) an beide Hände
    hV, hF, hUV = decimate(gV0, gF0, gUV0, 1600)
    parts_V, parts_F, parts_UV, parts_R, parts_Y = [Pk], [kF], [kUV * np.array([0.5, 1.0])], [reg], [ry]
    off = len(Pk)
    gvR, gfR = place_glove(hV, hF, *info['grip'], S)
    # Prüfung: Abstand der Handschuh-Eckpunkte zur Kranz-Mittellinie (Kranzrohr 0,021 m) – Faust soll ihn umschließen, nicht durchdringen
    az_ = nrm(np.array([0, 29, -36.0])); Cw = np.array([0, 0.5005, 0.1235]); rel = gvR - Cw; rp = rel - np.outer(rel @ az_, az_)
    ring = Cw + 0.188 * rp / np.linalg.norm(rp, axis=1, keepdims=True); dr = np.linalg.norm(gvR - ring, axis=1)
    near = dr < 0.06
    print(f'Handschuh–Kranz: kleinster Abstand {dr.min():.3f} m, Eckpunkte im Rohr {int((dr < 0.019).sum())}, Winkelabdeckung um den Kranz', end=' ')
    tang = np.cross(az_, rp / np.linalg.norm(rp, axis=1, keepdims=True)); u1 = rp / np.linalg.norm(rp, axis=1, keepdims=True); d = gvR - ring
    ang = np.degrees(np.arctan2(d @ az_, np.sum(d * u1, 1)))[near]; print(f'{np.ptp(ang):.0f}°')
    for s, sfx in ((-1, 'R'), (1, 'L')):
        pv, pf = (gvR, gfR) if s < 0 else (gvR * np.array([-1.0, 1, 1]), gfR[:, ::-1])   # linke Hand gespiegelt
        parts_V.append(pv); parts_F.append(pf + off); parts_UV.append(hUV * np.array([0.5, 1.0]) + np.array([0.5, 0.0])); parts_R.append(np.full(len(pv), 3, np.uint8)); parts_Y.append(np.full(len(pv), -1, np.float32)); off += len(pv)
        print(f'Handgelenk {sfx}: Arm endet bei {np.round(info["wrist"][sfx][0], 3)}, Handschuh bei {np.round(info["wrist"][sfx][1], 3)}')
    AV, AF, AUV, AR, AY = np.vstack(parts_V), np.vstack(parts_F), np.vstack(parts_UV), np.concatenate(parts_R), np.concatenate(parts_Y)
    N = smooth_normals(AV, AF)
    # Atlas: links Anzug-Schattierung, rechts Handschuh; Normalen links Anzug, rechts flach
    atl = Image.new('RGB', (1024, 512)); atl.paste(tex.resize((512, 512), Image.LANCZOS), (0, 0)); atl.paste(glove_texture(gtex).resize((512, 512), Image.LANCZOS), (512, 0))
    atn = Image.new('RGB', (1024, 512), (128, 128, 255)); atn.paste(nor.resize((512, 512), Image.LANCZOS), (0, 0))
    atl.save(os.path.join(ROOT, 'textures', 'kart_fahrer.jpg'), quality=86); atn.save(os.path.join(ROOT, 'textures', 'kart_fahrer_n.jpg'), quality=90)
    # Binärformat wie kart.bin: [u32 Länge][JSON-Kopf][Daten]
    blobs, hdr = [], {'nv': len(AV), 'ni': AF.size, 'helm': np.round(info['head'], 4).tolist(), 'helmTilt': 0.0}
    def put(name, arr):
        off = sum(len(b) for b in blobs); b = arr.tobytes(); b += b'\0' * (-len(b) % 4); blobs.append(b); hdr[name] = off
    put('pos', AV.astype(np.float32)); put('nrm', N.astype(np.float32)); put('uv', AUV.astype(np.float32)); put('reg', AR.astype(np.uint8)); put('ry', AY.astype(np.float32))
    put('idx', AF.astype(np.uint16 if len(AV) < 65536 else np.uint32).reshape(-1)); hdr['i32'] = len(AV) >= 65536
    hj = json.dumps(hdr).encode(); hj += b' ' * (-len(hj) % 4)
    with open(os.path.join(ROOT, 'kartfahrer.bin'), 'wb') as fo: fo.write(struct.pack('<I', len(hj)) + hj + b''.join(blobs))
    print('Kart-Fahrer:', len(AV), 'Eckpunkte,', len(AF), 'Dreiecke; Helm bei', hdr['helm'])


if __name__ == '__main__':
    main()
