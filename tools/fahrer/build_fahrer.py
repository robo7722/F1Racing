"""Baut den Rennfahrer aus den Vorlagen (Tripo-Körper + Handschuh-KMZ).

Aufruf:  python3 tools/fahrer/build_fahrer.py <quellordner>
Quellordner: model.obj, base.jpg, normal.jpg (Körper, Tripo) und glove.kmz (Handschuh).
Braucht: numpy, pillow, scipy, trimesh, pymeshlab, libigl, scikit-image (+ Systempaket libopengl0).

Ergebnis:
  fahrer/fahrer.glb, fahrer/handschuh.glb   stehende Figur (Vorschau: fahrer/vorschau.html; Kart-Prüfansicht: fahrer/kart_vorschau.html)
  kartfahrer.bin                           sitzender Kart-Fahrer fürs Spiel (Körper + beide Handschuhe, ein Netz)
  textures/kart_fahrer.jpg                 Atlas (links Anzug-Schattierung, rechts Handschuh)
  textures/kart_stoff.jpg                  kachelbares Nomex-Gewebe (Höhenkarte) für das Anzugmaterial

Ablauf:
  1. Körper aufräumen: Splitter, Kopf (Tripo-Helm) und Hände weg; Ärmel sauber quer zum Unterarm abschneiden.
  2. Textur säubern: Logos, Schriftzüge und dunkle Fehlstellen (Fersen, Achseln, Seitennähte) entfernen.
     Übrig bleibt eine helle Stoff-Schattierung, die im Spiel mit den Teamfarben eingefärbt wird.
  3. Verkleinern (Kantenzusammenlegung mit Erhalt der Textur).
  4. Kart: Ruhehaltung als geschlossene Außenhülle neu aufbauen (Windungszahl, libigl) – die Vorlage hat Doppelwände, Futter
     und abstehende Schulterklappen, die beim Biegen als Löcher/Schlitze erschienen. Dann über ein einfaches Skelett in die
     Sitzhaltung biegen (Arme gedreht statt linear gemischt, Hände per Zwei-Knochen-IK am Lenkradkranz, Handgelenk gerade),
     Bündchen eng ziehen, Handschuhe zur Faust um den Kranz gekrümmt und mit der Stulpe über das Bündchen gelegt.
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
     'sh': (-0.100, 0.768, -0.040), 'el': (-0.125, 0.605, -0.056), 'wr': (-0.137, 0.475, -0.002)}
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
    """Nur die Form verkleinern (UV-Nähte zählen nicht als feste Kanten – das faltete sonst an Schultern/Oberkörper Dreiecke um),
    danach die Texturkoordinaten vom Originalnetz holen (nächster Punkt, baryzentrisch). Die Anzug-Textur ist fast einfarbig,
    Nähte fallen dabei nicht auf."""
    w = trimesh.Trimesh(V, F, process=False); w.merge_vertices(merge_tex=True, merge_norm=True)
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(vertex_matrix=w.vertices, face_matrix=w.faces))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(target), qualitythr=0.6, preserveboundary=True, boundaryweight=2.0, preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True, autoclean=True)
    m = ms.current_mesh(); v, f = m.vertex_matrix(), m.face_matrix()
    orig = trimesh.Trimesh(V, F, process=False)
    _, _, tri = trimesh.proximity.closest_point(orig, v)
    bc = trimesh.triangles.points_to_barycentric(V[F[tri]], v)
    uv = np.einsum('ij,ijk->ik', bc, UV[F[tri]])
    used = np.unique(f); remap = -np.ones(len(v), int); remap[used] = np.arange(len(used))
    return v[used], remap[f], uv[used]


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


def glove_shape(gV, Rb, y0=-1.0, kurz=True):
    """Stulpe kürzen/leicht weiten (steckt im Ärmel) und Finger um eine Achse vor der Handfläche krümmen.
    kurz=False (Kart): Stulpe bleibt lang – sie wird danach an den Ärmel angepasst (fit_gauntlet)."""
    gV = gV.copy()
    if not kurz:
        yy = np.maximum(gV[:, 1] - y0, 0); zax = 9.3 + Rb; d = zax - gV[:, 2]; m = yy > 0
        gV[m, 1] = y0 + d[m] * np.sin(yy[m] / Rb); gV[m, 2] = zax - d[m] * np.cos(yy[m] / Rb)
        return gV, np.array([-0.4, y0, zax])
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


def arm_masks(V, F, S):
    """Arme in Ruhehaltung: seitlich einer höhenabhängigen Grenze |x| > t(y). Die Grenze liegt in der gemessenen Lücke zwischen
    hängendem Arm und Rumpf/Hüfte (Tripo-Vorlage). Ein fester Wert erwischte die Hüftseite neben der Hand – die wurde mit zum Lenkrad gezogen."""
    x, y = V[:, 0] / S, V[:, 1] / S
    t = np.interp(y, [0.40, 0.54, 0.57, 0.60, 0.635, 0.66, 0.80], [0.106, 0.106, 0.095, 0.089, 0.089, 0.100, 0.100])
    band = (y > 0.40) & (y < 0.80)
    mR, mL = band & (x < -t), band & (x > t)
    if getattr(remesh_winding, 'arm', None) is not None and len(remesh_winding.arm[0]) == len(V):
        # Hülle: Arm und Hüfte sind dort getrennt (freigeschnitten) -> unterhalb y = 0,60 ist der Arm ein eigenes zusammenhängendes Stück
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components
        low = y < 0.60; e = np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]); e = e[low[e[:, 0]] & low[e[:, 1]]]
        n = len(V); _, lab = connected_components(coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)), directed=False)
        for k, sx in enumerate((-1, 1)):
            wr = mir(J['wr']) if sx > 0 else J['wr']
            seed = np.argmin(np.linalg.norm(V / S - wr, axis=1) + (~low) * 9)
            comp = (lab == lab[seed]) & low
            if comp.sum() > 0.3 * low.sum(): continue                                     # doch verbunden: feste Grenze behalten
            if k == 0: mR = np.where(low, comp & band, mR)
            else: mL = np.where(low, comp & band, mL)
    return mR, mL


def remesh_winding(P, F, UV, target, h=0.0015, close_above=(0.66, 0.016), extra=None):
    """Ruhehaltung als saubere, geschlossene Außenhülle neu aufbauen. „Innen“ = verallgemeinerte Windungszahl (libigl) – robust gegen
    die Macken der Vorlage: offene Stellen, doppelwandige Ärmel, im Rumpf steckende Ärmelflächen. Beim Biegen klappten genau diese
    Innenflächen als Schlitze/Trichter an Schulter und Kragen heraus. Danach glatt vernetzen, verkleinern, UV vom Original holen."""
    import igl
    from skimage.measure import marching_cubes
    lo = P.min(0) - 4 * h; dims = np.ceil((P.max(0) - P.min(0)) / h).astype(int) + 9
    gx, gy, gz = [lo[a] + np.arange(dims[a]) * h for a in range(3)]
    Q = np.stack(np.meshgrid(gx, gy, gz, indexing='ij'), -1).reshape(-1, 3)
    w = igl.fast_winding_number(np.ascontiguousarray(P, dtype=np.float64), np.ascontiguousarray(F, dtype=np.int64), Q).reshape(dims)
    inside = np.abs(w) > 0.5
    # Die Vorlage hat im Oberkörper eine innere Futterschicht (vom Kragen abwärts): dort hebt sich die Windungszahl auf, der Rumpf
    # wäre hohl. Jede waagerechte Scheibe einzeln füllen – ein Ring im Querschnitt wird so zur vollen Fläche, Arme bleiben eigene Flecken.
    for jj in range(dims[1]): inside[:, jj, :] = ndimage.binary_fill_holes(inside[:, jj, :])
    f = inside
    if close_above:
        # Spalt zwischen Rücken/Brust und Oberarm schließen (reicht in der Vorlage hinten bis zur Schulter hoch) – nur oberhalb close_above[0],
        # darunter bleibt die echte Lücke zwischen hängendem Arm und Hüfte offen
        y0, rr = close_above; r = int(round(rr / h)); ball = np.linalg.norm(np.indices((2 * r + 1,) * 3) - r, axis=0) <= r + 0.01
        closed = ndimage.binary_closing(np.pad(inside, r), structure=ball)[r:-r, r:-r, r:-r]
        f = inside | (closed & (gy > y0)[None, :, None])                                   # nur ja/nein (Zwischenwerte gaben dünne Häutchen mit Löchern)
    f = ndimage.binary_fill_holes(f)
    if close_above:
        # Lücke zwischen hängendem Arm und Hüfte (in der Vorlage nur ~3 mm) freischneiden, sonst verschmilzt die Hülle dort und der
        # Arm zieht beim Biegen eine Hautfalte von der Hüfte mit. Je Höhenscheibe ist der Arm in der Vorlage ein eigener Fleck:
        # den Fleck um die Armachse nehmen, 2 Voxel Abstand zum Rest freiräumen, und ihn als Arm-Maske fürs Biegen merken.
        armvox = np.zeros_like(f)
        for sx in (-1, 1):
            for jj in np.where((gy > J['wr'][1] - 0.004) & (gy < 0.62))[0]:                # nur wo es Ärmel gibt (Hand ist abgeschnitten)
                t_ = np.clip((gy[jj] - J['wr'][1]) / (J['el'][1] - J['wr'][1]), 0, 1); c = J['wr'] + (J['el'] - J['wr']) * t_
                ci, ck = int(round((sx * -c[0] - lo[0]) / h)), int(round((c[2] - lo[2]) / h))
                lab, n = ndimage.label(inside[:, jj, :])
                if n == 0: continue
                l0 = lab[ci, ck]
                if l0 == 0:                                                               # Achse knapp daneben: nächsten Fleck nehmen
                    ii, kk = np.nonzero(lab); d = (ii - ci) ** 2 + (kk - ck) ** 2
                    if d.min() > 9: continue
                    l0 = lab[ii[d.argmin()], kk[d.argmin()]]
                arm = lab == l0
                if arm.sum() > 0.4 * (lab > 0).sum(): continue                            # mit dem Rumpf verbunden (Achsel): nicht trennen
                armvox[:, jj, :] |= arm
                f[:, jj, :] &= arm | ~ndimage.binary_dilation(arm, iterations=2)
        # dünne Finnen entfernen (morphologisches Öffnen): offene Einzelflächen der Vorlage – v. a. die Schulterklappen – ergeben in der
        # Windungszahl hauchdünne, abstehende Platten, die beim Biegen knautschen
        ro = 3; ball2 = np.linalg.norm(np.indices((2 * ro + 1,) * 3) - ro, axis=0) <= ro + 0.01
        op = ndimage.binary_opening(np.pad(f, ro), structure=ball2)[ro:-ro, ro:-ro, ro:-ro]
        reg = (np.abs(gx) > 0.08)[:, None, None] & ((gy > 0.74) & (gy < 0.84))[None, :, None]   # nur die Schulterkappen
        f = np.where(reg, op, f)
    f = ndimage.gaussian_filter(f.astype(np.float32), 0.8)
    v, fc, _, _ = marching_cubes(f, 0.5)
    v = v * h + lo; fc = fc[:, ::-1]
    m0 = trimesh.Trimesh(v, fc, process=False); parts = m0.split(only_watertight=False)
    m0 = max(parts, key=lambda q: q.area)                                                  # nur die Hülle selbst (keine Krümel)
    ms = pymeshlab.MeshSet(); ms.add_mesh(pymeshlab.Mesh(vertex_matrix=m0.vertices, face_matrix=m0.faces))
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(target), qualitythr=0.7, preservenormal=True, preservetopology=True, optimalplacement=True, planarquadric=True, autoclean=True)
    ms.apply_coord_taubin_smoothing(stepsmoothnum=4)
    m = ms.current_mesh(); v, fc = m.vertex_matrix(), m.face_matrix()
    src = trimesh.Trimesh(P, F, process=False)
    _, dist, tri = trimesh.proximity.closest_point(src, v)
    bc = np.clip(trimesh.triangles.points_to_barycentric(P[F[tri]], v), 0, 1); bc /= bc.sum(1, keepdims=True)
    uv = np.einsum('ij,ijk->ik', bc, UV[F[tri]])
    # Dreiecke, deren Ecken auf verschiedenen UV-Inseln landen, würden quer über die Textur interpolieren (Streifen, Logo-Reste);
    # ebenso neu geschlossene Flächen (weit von der Vorlage): beide bekommen die UV einer sauberen Stoffstelle
    far = dist > 2.5 * h
    span = np.zeros(len(v), bool)
    tuv = uv[fc]; big = (np.ptp(tuv[:, :, 0], 1) > 0.06) | (np.ptp(tuv[:, :, 1], 1) > 0.06)
    span[np.unique(fc[big])] = True
    clean = np.median(uv[~far & ~span], axis=0)
    uv[far | span] = clean
    print(f'UV ersetzt: {int(far.sum())} neue Flächenpunkte, {int(span.sum())} an Inselgrenzen')
    if close_above:                                                                        # Arm-Maske für die neuen Eckpunkte (Ruhehaltung)
        av = ndimage.binary_dilation(armvox, iterations=2); q = np.clip(np.round((v - lo) / h).astype(int), 0, np.array(av.shape) - 1)
        isarm = av[q[:, 0], q[:, 1], q[:, 2]]; remesh_winding.arm = (isarm & (v[:, 0] < 0), isarm & (v[:, 0] > 0))
    mm = trimesh.Trimesh(v, fc, process=False)
    print(f'Hülle: {len(fc)} Dreiecke, geschlossen: {mm.is_watertight}, Teile verworfen: {len(parts) - 1}, Euler {mm.euler_number}')
    if extra is not None: return v, fc, uv, np.einsum('ij,ijk->ik', bc, extra[F[tri]])
    return v, fc, uv


def unfold(V, F, rounds=40, tag=''):
    """Eingeklappte Flächen reparieren: Dreiecke, deren Normale gegen die geglättete Umgebung zeigt (Falte), samt 2 Ringen Nachbarn
    lokal glätten, bis keine mehr übrig sind. Die Tripo-Vorlage hat solche Falten in Achsel, Gürtel und Brust; beim Biegen der Arme
    kamen sie als Risse/Mulden zum Vorschein. Es wird nichts gelöscht – keine neuen Löcher."""
    key = np.unique(np.round(V, 6), axis=0, return_inverse=True)[1].reshape(-1); nk = key.max() + 1
    Fk = key[F]
    from scipy.sparse import coo_matrix, diags
    e = np.vstack([Fk[:, [0, 1]], Fk[:, [1, 2]], Fk[:, [2, 0]]]); e = e[e[:, 0] != e[:, 1]]
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(nk, nk)).tocsr(); A.data[:] = 1
    Avg = diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    Vk = np.zeros((nk, 3)); np.add.at(Vk, key, V); Vk /= np.bincount(key, minlength=nk)[:, None]
    def bad_faces():
        fn = np.cross(Vk[Fk[:, 1]] - Vk[Fk[:, 0]], Vk[Fk[:, 2]] - Vk[Fk[:, 0]]); fa = np.linalg.norm(fn, axis=1); fn = fn / np.maximum(fa, 1e-12)[:, None]
        acc = np.zeros((nk, 3)); np.add.at(acc, Fk.reshape(-1), np.repeat(fn * fa[:, None], 3, 0)); N = acc / np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-12)
        nb = Avg @ N; nb = nb / np.maximum(np.linalg.norm(nb, axis=1, keepdims=True), 1e-12)
        return np.einsum('ij,ij->i', fn, nb[Fk].mean(1)) < 0.05
    b0 = int(bad_faces().sum())
    for _ in range(rounds):
        bad = bad_faces()
        if not bad.any(): break
        m = np.zeros(nk); m[np.unique(Fk[bad])] = 1
        for _ in range(2): m = np.maximum(m, (A @ m > 0).astype(float))
        m = m[:, None]
        for _ in range(3): Vk = Vk + 0.5 * m * (Avg @ Vk - Vk)
    b1 = int(bad_faces().sum())
    if tag: print(f'Falten {tag}: {b0} -> {b1}')
    return Vk[key]


def taubin_zone(V, F, zone, iters=40):
    """Taubin-Glättung (schrumpft nicht) nur dort, wo zone > 0 (weich gewichtet)."""
    key = np.unique(np.round(V, 6), axis=0, return_inverse=True)[1].reshape(-1); nk = key.max() + 1
    from scipy.sparse import coo_matrix, diags
    e = key[np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])]; e = e[e[:, 0] != e[:, 1]]
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(nk, nk)).tocsr(); A.data[:] = 1
    Avg = diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    Vk = np.zeros((nk, 3)); np.add.at(Vk, key, V); Vk /= np.bincount(key, minlength=nk)[:, None]
    zk = np.zeros(nk); np.maximum.at(zk, key, zone); zk = zk[:, None]
    for _ in range(iters):
        Vk = Vk + 0.6 * zk * (Avg @ Vk - Vk); Vk = Vk - 0.63 * zk * (Avg @ Vk - Vk)
    return Vk[key]


def kart_seat():
    """Innenfläche der Sitzschale aus kart.bin: Punkte + Normalen (zum Fahrer hin), nur Sitzbereich (Mitte, hinter dem Lenkrad)."""
    b = open(os.path.join(ROOT, 'kart.bin'), 'rb').read(); hl = struct.unpack('<I', b[:4])[0]; h = json.loads(b[4:4 + hl]); base = 4 + hl
    c = [c for c in h['chunks'] if c['name'] == 'body'][0]
    P = np.frombuffer(b, np.float32, c['nv'] * 3, base + c['pos']).reshape(-1, 3).astype(float)
    I = np.frombuffer(b, np.uint32 if c.get('i32') else np.uint16, c['ni'], base + c['idx']).reshape(-1, 3).astype(int)
    T = P[I]; cen = T.mean(1); sel = (np.abs(cen[:, 0]) < 0.17) & (cen[:, 2] < 0.05) & (cen[:, 2] > -0.75) & (cen[:, 1] > 0.1) & (cen[:, 1] < 0.75)
    m = trimesh.Trimesh(P, I[sel], process=False); pts, fi = trimesh.sample.sample_surface_even(m, 6000, seed=2); n = m.face_normals[fi]
    inner = np.array([0, 0.45, -0.25])                                                    # Punkt im Sitzraum: Normalen zu ihm hin drehen
    n = n * np.sign(np.einsum('ij,ij->i', inner - pts, n))[:, None]
    # nur die dem Fahrer zugewandte Schalenseite: Pfanne (Normale nach oben) und Lehne (Normale nach vorn)
    keep = ((n[:, 1] > 0.5) | ((n[:, 2] > 0.5) & (n[:, 1] > -0.2))) & (np.abs(pts[:, 0]) < 0.11)   # ohne Oberkante der Lehne (Normale schräg nach unten)              # Mitte der Schale (ohne Oberkanten der Seitenwangen)
    return pts[keep], n[keep]


def wheel_frame(mode):
    """Lenkrad im Fahrzeug: Mitte C, Achsen axx (zur rechten Hand, Welt -x), ay (oben am Lenkrad), az (Drehachse), Griffradius R, Griffwinkel th
    (0 = 9/3 Uhr, 30° = 10/2 Uhr). Kart: aus makeKart. F1: SW-Gruppe in index.html (Position swPos, Drehung (0,45 · π · 0), Maßstab swS),
    Griffschlaufen bei lokal x ±0,2, y −0,01, z 0,02."""
    if mode == 'kart':
        az = nrm(np.array([0, 29, -36.0])); axx = np.array([-1.0, 0, 0]); ay = np.cross(az, axx)
        return dict(C=np.array([0, 0.5005, 0.1235]), axx=axx, ay=ay, az=az, R=0.188, th=np.radians(30))
    s = 0.78; Rw = rot_x(0.45) @ np.diag([-1.0, 1, -1])                                 # Euler XYZ: Rx(0,45) · Ry(π)
    C = np.array([0, 0.60, 0.665]) + Rw @ (np.array([0, -0.01, 0.02]) * s)
    return dict(C=C, axx=Rw @ [1.0, 0, 0], ay=Rw @ [0, 1.0, 0], az=Rw @ [0, 0, 1.0], R=0.2 * s, th=0.0)


SC = 1.0
F1_SHEAR = 0.07                                                                        # F1: Kopf/Hals 7 cm vor den Schultern (wie mit HANS) – Schultern weiter vom nahen Lenkrad weg, Arme weniger gebeugt
F1_NECK = 0.08                                                                         # F1: Helm reicht so weit über den Hals (Kart 4,5 cm) – Schultern sitzen höher im Cockpit, der Anzug ist von außen zu sehen
F1_CUT = -1.0                                                                          # F1: Körper unter dieser Ruhe-Höhe weg (-1: nichts – seit das F1-Cockpit von außen offen ist, sieht man Hüfte und Beine)
F1_LEAN = 18
F1_HELM = np.array([0.0, 0.795, 0.18])                                                 # Helmmitte im F1 (MODELS.f1.helm + 5 mm wie im Spiel)


def pose_kart(V, F, S, mode='kart'):
    """V: Körper in Metern (Ruhehaltung, Maßstab S). Gibt gebogene Eckpunkte und Anker (Helm, Griff) zurück.
    mode 'kart': Sitz aus der Kart-Sitzschale, Lenksäule verlängert. mode 'f1': halb liegend im Monocoque (Rumpf 26° zurück),
    Hals oben so, dass der Helm an der Spielposition sitzt; Lenkrad fest (Griffe der SW-Gruppe)."""
    j = {k: v * S for k, v in J.items()}
    bones = {}                                                                         # name: (Kopf, Ende)
    for s, sfx in ((-1, 'R'), (1, 'L')):
        f = (lambda p: p) if s < 0 else mir
        bones['thigh' + sfx] = (f(j['hip']), f(j['knee'])); bones['shin' + sfx] = (f(j['knee']), f(j['ankle'])); bones['foot' + sfx] = (f(j['ankle']), f(j['toe']))
        bones['uarm' + sfx] = (f(j['sh']), f(j['el'])); bones['farm' + sfx] = (f(j['el']), f(j['wr']))
    bones['spine'] = (j['pelvis'], j['neck'])
    M = np.diag([-1.0, 1, 1])

    WF = wheel_frame(mode); az, axx, ay, C, RR, th = WF['az'], WF['axx'], WF['ay'], WF['C'], WF['R'], WF['th']
    gdir = axx * np.cos(th) + ay * np.sin(th)                                          # rechte Hand: 3 Uhr (th 0) bzw. 2 Uhr (th 30°)
    grip = C + gdir * RR; Xg = nrm(-axx * np.sin(th) + ay * np.cos(th))                 # Daumen entlang des Kranzes (Tangente)
    L1, L2 = np.linalg.norm(j['el'] - j['sh']), np.linalg.norm(j['wr'] - j['el'])
    # Ellbogen-Zone: Kart – Oberarme hängen (Ellbogen ≥ 22 cm unter der Schulter); F1 – Arme nach vorn, Ellbogen tief und innerhalb der Cockpitbreite
    EZ = dict(drop=0.22, out_min=0.03, out_max=0.14) if mode == 'kart' else dict(drop=0.0, out_min=0.0, out_max=0.07)

    # ---- Haltung wie beim echten Kartfahren: Rumpf leicht zurück, Oberarme hängen, Ellbogen ~90° unten-außen, Unterarme nach vorn ----
    lean = np.radians(19); Rsp = rot_x(-lean)                                          # Rumpf liegt an der Lehne (die ist ~18° geneigt)

    def solve_arm(hipT):
        sh = hipT + Rsp @ (j['sh'] - j['pelvis'])
        Yg = -az; Xh = Xg
        for _ in range(8):                                                               # ganze Hand in Verlängerung des Unterarms (gerades Handgelenk)
            Zg = np.cross(Xh, Yg); wristT = glove_wrist_world(grip, Xh, Yg, Zg, S)
            dvec = wristT - sh; dist = min(np.linalg.norm(dvec), (L1 + L2) * 0.999); u = nrm(dvec)
            a = (L1 ** 2 - L2 ** 2 + dist ** 2) / (2 * dist); r = np.sqrt(max(L1 ** 2 - a ** 2, 0)); c0 = sh + u * a
            e1 = nrm(np.cross(u, [0, 1, 0])); e2 = np.cross(u, e1); best = None
            for ang in np.linspace(0, 2 * np.pi, 144, endpoint=False):
                el = c0 + r * (np.cos(ang) * e1 + np.sin(ang) * e2)
                fa_ = nrm(wristT - el)
                # natürliche Zone: Ellbogen klar unter der Schulter, leicht außen (nicht abgespreizt, nicht im Rumpf)
                pen = max(0.0, el[1] - (sh[1] - EZ['drop'])) + max(0.0, el[0] - (sh[0] - EZ['out_min'])) + max(0.0, (sh[0] - EZ['out_max']) - el[0])
                sc = -abs(np.dot(fa_, Xg)) - 8.0 * pen                                     # darin: Unterarm möglichst quer zum Kranz
                if mode == 'f1':                                                           # F1: Unterarm fast waagerecht nach vorn, Ellbogen leicht außen und tiefer als die Hand
                    sc = -np.linalg.norm(el - np.array([sh[0] - 0.02, wristT[1] - 0.14, (sh[2] + wristT[2]) / 2]))   # Ellbogen unter dem Arm, innerhalb der Cockpitbreite
                if best is None or sc > best[0]: best = (sc, el)
            el = best[1]; fa = nrm(wristT - el)
            # Hand: zwischen „gerade zum Unterarm“ und „Daumen entlang des Kranzes“ – Handgelenk höchstens ~15° abgewinkelt
            yp = nrm(fa - np.dot(fa, Xg) * Xg); ang = np.arccos(np.clip(np.dot(fa, yp), -1, 1))
            t = 1.0 if ang < 1e-6 else min(1.0, np.radians(15 if mode == 'kart' else 28) / ang)   # Anteil Richtung „Kranz“: höchstens 15° (F1 28°) Knick
            Yg = nrm(fa * (1 - t) + yp * t); Xh = nrm(Xg - np.dot(Xg, Yg) * Yg)           # Rest: Kranz läuft schräg durch die Hand (wie in echt)
        return sh, el, wristT, (Xh, Yg), np.linalg.norm(wristT - sh)

    sw_ext = 0.0
    if mode == 'kart':
        # Sitzposition aus der Sitzschale: Gesäß auf der Pfanne, Rücken an der Lehne – ohne einzudringen (Rumpf-Punkte gegen die Schalen-Innenfläche)
        from scipy.spatial import cKDTree
        sp, sn = kart_seat(); kd = cKDTree(sp)
        xr, yr = V[:, 0] / S, V[:, 1] / S
        torso = (np.abs(V[:, 0]) < 0.10) & (yr > 0.465) & (yr < 0.80); Pt = V[torso] - j['pelvis']   # Gesäß + Rücken (darunter: Oberschenkel, die gehen im Sitzen nach vorn)
        butt, back = Pt[:, 1] < (0.56 - 0.5) * S, Pt[:, 1] > (0.62 - 0.5) * S
        best = None
        for lean_d in range(12, 23, 1):
            Rl = rot_x(-np.radians(lean_d)); Q0 = Pt @ Rl.T
            for hz in np.linspace(-0.52, -0.25, 28):
                for hy in np.linspace(0.18, 0.34, 33):
                    Q = Q0 + [0, hy, hz]; _, k = kd.query(Q); d = np.einsum('ij,ij->i', Q - sp[k], sn[k])
                    pen = np.clip(-d, 0, None)
                    # Gesäß liegt auf der Pfanne UND Rücken liegt an der Lehne (je die 25 nächsten Punkte ≈ 3 mm Abstand), nichts dringt ein
                    cb = ((np.sort(d[butt])[:25] - 0.003) ** 2).mean(); cr = ((np.sort(d[back])[:25] - 0.003) ** 2).mean()
                    sc = (pen ** 2).sum() * 4e4 + (cb + cr) * 1e4
                    if best is None or sc < best[0]: best = (sc, lean_d, np.array([0, hy, hz]), pen.max(), np.sort(d[back])[0], np.sort(d[butt])[0])
        lean = np.radians(best[1]); Rsp = rot_x(-lean); hipT = best[2]
        print(f'Sitz: Neigung {best[1]}°, Becken bei y {hipT[1]:.3f} z {hipT[2]:.3f}, größtes Eindringen {best[3] * 1000:.1f} mm, Abstand Rücken {best[4] * 1000:.0f} mm, Gesäß {best[5] * 1000:.0f} mm')
        # Lenkrad entlang der Lenksäule (Achse az) zum Fahrer schieben, bis die Arme leicht gebeugt sind (Schulter–Hand ≈ 88 % der Armlänge),
        # wie bei einer verstellbaren Kart-Lenksäule. Im Spiel: swExt im Kopf von kartfahrer.bin, dazu ein Verlängerungsrohr.
        sh_w = hipT + Rsp @ (j['sh'] - j['pelvis']); C0 = C.copy()
        for ext in np.arange(0.0, 0.2, 0.005):
            g_ = C0 + az * ext + gdir * RR; wr_ = glove_wrist_world(g_, Xg, -az, np.cross(Xg, -az), S)
            sw_ext = ext
            if np.linalg.norm(wr_ - sh_w) / (L1 + L2) <= 0.88: break
        C = C0 + az * sw_ext; grip = C + gdir * RR
        print(f'Lenkrad {sw_ext * 100:.1f} cm entlang der Lenksäule zum Fahrer')
    else:
        # F1: halb liegend. Hals oben (Ruhe-Eckpunkte y > 0,845, folgen dem Rumpf) so verschieben, dass der Helm (Unterkante 4,5 cm unter
        # dem Halsende, wie beim Kart) genau an der Helmposition des Spiels sitzt.
        lean = np.radians(F1_LEAN); Rsp = rot_x(-lean)
        nk = (V[:, 1] / S > 0.845); Q = (V[nk] - j['pelvis']) @ Rsp.T
        hb = 0.154; hipT = F1_HELM - np.array([0.0, Q[:, 1].max() - F1_NECK + hb, (Q[:, 2].min() + Q[:, 2].max()) / 2 + 0.02 + F1_SHEAR])   # Kopf wird danach um F1_SHEAR nach vorn geschoben (main)
        print(f'F1-Sitz: Neigung {F1_LEAN}°, Becken bei y {hipT[1]:.3f} z {hipT[2]:.3f}')
    sh, el, wristT, (Xh, Yg), dist = solve_arm(hipT)
    print(f'Hand: Daumenachse weicht {np.degrees(np.arccos(np.clip(np.dot(Xh, Xg), -1, 1))):.0f}° vom Kranz ab, Handgelenk-Knick {np.degrees(np.arccos(np.clip(np.dot(Yg, nrm(wristT - el)), -1, 1))):.0f}°')
    out = {'reach': {'R': (dist, L1 + L2), 'L': (dist, L1 + L2)}, 'hip': hipT}
    Rua = rot_between(bones['uarmR'][1] - bones['uarmR'][0], el - sh)
    wr_reached = el + nrm(wristT - el) * L2
    Rfa = rot_between(bones['farmR'][1] - bones['farmR'][0], wr_reached - el)
    T = {'spine': (Rsp, hipT), 'uarmR': (Rua, sh), 'farmR': (Rfa, el), 'uarmL': (M @ Rua @ M, M @ sh), 'farmL': (M @ Rfa @ M, M @ el)}
    out['grip'] = (grip, Xh, Yg, np.cross(Xh, Yg)); out['swExt'] = float(sw_ext); out['C'] = C; out['WF'] = WF
    out['wrist'] = {'R': (wr_reached, wristT), 'L': (M @ wr_reached, M @ wristT)}
    out['elbow'] = el; out['shoulder'] = sh
    for s, sfx in ((-1, 'R'), (1, 'L')):
        f = (lambda p: p) if s < 0 else mir
        # Beine: Knie hoch, Unterschenkel nach vorn-unten zu den Pedalen, Füße aufgestellt (F1: Beine werden später weggeschnitten)
        hip = hipT + f(j['hip'] - j['pelvis'])
        F1L = mode == 'f1'                                                              # F1: Beine fast waagerecht nach vorn unter die Nase, Knie leicht angehoben
        dth = nrm(f(np.array([-0.03, 0.2, 1.0] if F1L else [-0.10, 0.05, 1.0]))); Rth = rot_between(bones['thigh' + sfx][1] - bones['thigh' + sfx][0], dth)
        knee = hip + dth * np.linalg.norm(j['knee'] - j['hip'])
        dsh = nrm(f(np.array([0.02, -0.12, 1.0] if F1L else [0.03, -0.20, 1.0]))); Rsh = rot_between(bones['shin' + sfx][1] - bones['shin' + sfx][0], dsh)
        ankle = knee + dsh * np.linalg.norm(j['ankle'] - j['knee'])
        dft = nrm(f(np.array([-0.05, 0.9, 0.35] if F1L else [-0.05, 0.75, 0.55])))
        Rft = rot_between(Rsh @ (bones['foot' + sfx][1] - bones['foot' + sfx][0]), dft) @ Rsh
        T['thigh' + sfx] = (Rth, hip); T['shin' + sfx] = (Rsh, knee); T['foot' + sfx] = (Rft, ankle)

    # ---- Verformung ----
    # Rumpf + Beine: lineares Mischen der Knochen (dort wird wenig gebogen).
    # Arme: gewichtetes DREHEN um Schulter und Ellbogen (Rotation wird mit dem Gewicht skaliert). Lineares Mischen ließ an der
    # Schulter die Fläche einknicken (Kerbe/Schlitz hinten an der Schulter) und am Ellbogen einfallen.
    P = V; x, y = P[:, 0] / S, P[:, 1] / S
    names = list(bones.keys()); D = np.stack([seg_dist(P, *bones[n]) for n in names], 1); ix = {n: i for i, n in enumerate(names)}
    sstep = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
    armR, armL = arm_masks(V, F, S)
    key = np.unique(np.round(V, 5), axis=0, return_inverse=True)[1].reshape(-1); nk = key.max() + 1
    from scipy.sparse import coo_matrix, diags
    e = key[np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])]; e = e[e[:, 0] != e[:, 1]]
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(nk, nk)).tocsr(); A.data[:] = 1
    Avg = diags(1 / np.maximum(np.asarray(A.sum(1)).ravel(), 1)) @ A
    el_len = np.mean(np.linalg.norm(V[F[:, 0]] - V[F[:, 1]], axis=1)) / S
    def smooth(vals, radius, fixed=None):
        vk = np.zeros(nk); np.add.at(vk, key, vals); vk /= np.bincount(key, minlength=nk)
        fk = None
        if fixed is not None: fk = np.zeros(nk, bool); np.logical_or.at(fk, key, fixed); f0 = vk.copy()
        for _ in range(int(np.clip((radius / el_len) ** 2, 4, 600))):
            vk = 0.5 * vk + 0.5 * (Avg @ vk)
            if fk is not None: vk[fk] = f0[fk]
        return vk[key]
    # Körper (Rumpf/Beine) linear
    def inv(cols):
        Wc = np.zeros_like(D)
        for n in cols: Wc[:, ix[n]] = 1 / (D[:, ix[n]] + 0.012) ** 6
        return Wc
    Wb = inv(['spine'])
    for s, sfx in ((-1, 'R'), (1, 'L')):
        legm = (y < 0.535) & ((x < 0.004) if s < 0 else (x > -0.004))
        for n in ('thigh', 'shin', 'foot'): Wb[:, ix[n + sfx]] = np.where(legm, 1 / (D[:, ix[n + sfx]] + 0.012) ** 6, 0)
    Wb /= Wb.sum(1, keepdims=True)
    for k in range(Wb.shape[1]): Wb[:, k] = smooth(Wb[:, k], 0.03)
    Wb /= Wb.sum(1, keepdims=True)
    Vb = np.zeros_like(P)
    for n in names:
        if n.startswith(('uarm', 'farm')): continue
        R_, head = T[n]; Vb += Wb[:, ix[n]:ix[n] + 1] * ((P - bones[n][0]) @ R_.T + head)
    Vsp = (P - bones['spine'][0]) @ Rsp.T + hipT                                        # reiner Rumpf
    def rpow(R_, t):                                                                   # Drehung R_ zum Anteil t (je Punkt)
        rv = Rot.from_matrix(R_).as_rotvec(); return Rot.from_rotvec(np.outer(t, rv)).as_matrix()
    from scipy.spatial.transform import Rotation as Rot
    Vn = Vb.copy(); W = Wb; out['aw'] = {}
    for s, sfx, am in ((-1, 'R', armR), (1, 'L', armL)):
        shR, elR = bones['uarm' + sfx]; wrR = bones['farm' + sfx][1]
        Rua, sh_t = T['uarm' + sfx]; Rfa, _ = T['farm' + sfx]
        ax_ = elR - shR; tp = ((P - shR) @ ax_) / (ax_ @ ax_)
        # Arm-Anteil: unten (echter Spalt zur Hüfte) hart über die Maske, an der Schulter weich entlang der Oberarmachse
        rad = sstep(0.086, 0.112, s * x) * (1 - sstep(0.76, 0.80, y)) + sstep(0.76, 0.80, y) * sstep(0.03, 0.09, s * x)
        aw = np.where(y < 0.60, am.astype(float), sstep(-0.35, 0.40, tp) * rad)
        aw = smooth(aw, 0.035, fixed=(y < 0.57))
        fw = sstep(0.82, 1.12, tp) * (aw > 0.5)                                          # Unterarm-Anteil um den Ellbogen
        fw = smooth(fw, 0.02)
        out['aw'][sfx] = aw
        E = Rua.T @ Rfa                                                                  # Ellbogen-Drehung im Ruhe-Rahmen
        Pe = elR + np.einsum('nij,nj->ni', rpow(E, fw), P - elR)
        Rr = Rua @ Rsp.T                                                                 # Arm relativ zum Rumpf
        qa = np.einsum('nij,nj->ni', rpow(Rr, aw), (Pe - shR) @ Rsp.T) + sh_t
        side = aw > 1e-4
        Vn[side] = qa[side] + (Vb[side] - Vsp[side]) * (1 - aw[side])[:, None]          # Bein-Anteil des Körpers wirkt nicht auf den Arm
    out['head'] = hipT + Rsp @ (j['neck'] - j['pelvis']) + (j['head'] - j['neck'])   # Kopf aufrecht auf dem Hals (Blick nach vorn)
    out['lean'] = lean; out['arms'] = (armR, armL); out['names'] = names
    return Vn, out


Y0_KART = -4.5                                                                         # Faust: Krümmung ab den Fingerwurzeln


def bend_hand(gV, yp, R1, yf, R2, amax, zs=9.0):
    """Hand um den Kranz legen: Mittellinie (z = zs) läuft bis yp gerade (Handballen), dann Handfläche mit Radius R1 leicht gewölbt
    bis zur Fingerwurzel yf, dann Finger mit Radius R2 um den Kranz (Gesamtwinkel höchstens amax, danach gerade weiter).
    Krümmung zur Handflächenseite (+z). Gibt (verformte Punkte, Mittelpunkt des Fingerbogens = Kranzmitte) zurück."""
    ys = np.linspace(-30.0, 15.0, 4000); ds = ys[1] - ys[0]                               # fester Bereich (auch für einzelne Punkte)
    Sp = np.zeros((len(ys), 2)); T = np.zeros((len(ys), 2)); Nn = np.zeros((len(ys), 2)); ang = 0.0
    Sp[0] = [ys[0], zs]; T[0] = [1, 0]; Nn[0] = [0, 1]
    for i in range(1, len(ys)):
        y = ys[i - 1]; k = 0.0 if y < yp else (1 / R1 if y < yf else 1 / R2)
        if ang >= amax: k = 0.0
        ang += k * ds; T[i] = [np.cos(ang), np.sin(ang)]; Nn[i] = [-np.sin(ang), np.cos(ang)]; Sp[i] = Sp[i - 1] + T[i - 1] * ds
    i_f = np.searchsorted(ys, yf); C = Sp[i_f] + Nn[i_f] * R2                          # Mitte des Fingerbogens
    idx = np.clip(np.searchsorted(ys, gV[:, 1]), 0, len(ys) - 1); h = gV[:, 2] - zs
    out = gV.copy(); P2 = Sp[idx] + Nn[idx] * h[:, None]; out[:, 1] = P2[:, 0]; out[:, 2] = P2[:, 1]
    return out, np.array([-0.4, C[0], C[1]])


# Griff: Kranz liegt am Daumenballen in der Handfläche (y ≈ -8), Handfläche leicht gewölbt, Finger greifen ganz herum
FIST = dict(yp=-6.0, R1=3.6, yf=-1.5, R2=3.5, amax=4.6)


def glove_wrist_world(grip, Xg, Yg, Zg, S):
    gV, ax = bend_hand(G_WRIST[None], **FIST)
    p = (G_WRIST - ax) * G_S * S / H
    R = np.stack([Xg, Yg, Zg], 1)
    return grip + R @ p


def fit_gauntlet(gw, gy, arm_pts, c, ax, S):
    """Lückenlos: Stulpe des Handschuhs über das Ärmelbündchen legen. gw = Handschuh (Welt), gy = Höhe in der Vorlage (Stulpe < -13),
    c = Handgelenk, ax = Unterarmrichtung (Ellbogen -> Hand). Das Bündchen ist vorher auf r = 3 cm eingezogen (main); die Stulpe wird
    rund mit r = 3,45 cm darübergelegt und endet ~4,5 cm vor dem Handgelenk. arm_pts bleibt für spätere Anpassungen in der Signatur."""
    e1 = nrm(np.cross(ax, [0, 1, 0])); e2 = np.cross(ax, e1)
    def polar(P):
        d = P - c; a = d @ ax; rv = d - np.outer(a, ax); return a, np.arctan2(rv @ e2, rv @ e1), np.linalg.norm(rv, axis=1)
    out = gw.copy(); g = gy < -12.5
    ga, gth, gr = polar(gw[g])
    w = np.clip((-12.5 - gy[g]) / 3.0, 0, 1); w = w * w * (3 - 2 * w)                # weich vom Handrücken in die Stulpe
    tgt = np.full(len(gth), (0.030 + 0.0045) * SC)                                          # Stulpe rund, knapp ÜBER dem eng gezogenen Bündchen (r 3 cm)
    nr = gr + (tgt - gr) * w
    na = np.where(gy[g] < -15.5, -0.012 * SC + (gy[g] + 15.5) * G_S * S / H * 0.4, ga * (1 - w) + np.minimum(ga, -0.004) * w)   # endet ~4,5 cm vor dem Handgelenk
    dirs = np.outer(np.cos(gth), e1) + np.outer(np.sin(gth), e2)
    out[g] = c + np.outer(na, ax) + dirs * nr[:, None]
    return out


RB_KART = 2.9                                                                          # Krümmungsradius der Faust (Vorlagen-Einheiten)


def place_glove(gV0, gF, grip, Xg, Yg, Zg, S):
    gV, ax = glove_shape(gV0, RB_KART, Y0_KART, kurz=False)                              # Stulpe (kurz=False: nur Krümmung, wird gleich ersetzt)
    gV, ax = bend_hand(gV0, **FIST)
    p = (gV - ax) * G_S * S / H
    R = np.stack([Xg, Yg, Zg], 1)
    return grip + p @ R.T, gF


def weave_texture(n=256, threads=16):
    """Kachelbare Höhenkarte für Nomex-Gewebe (Köper 2/2): Kett- und Schussfäden als gewölbte Bahnen, diagonaler Grat, leichtes Rauschen."""
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); t = n / threads
    i, j = np.floor(x / t), np.floor(y / t); u, v = (x % t) / t, (y % t) / t
    warp_up = ((i + j) % 4) < 2                                                         # Köper: Kettfaden liegt 2 oben, 2 unten, je Reihe versetzt
    prof = lambda q: np.sin(np.pi * np.clip(q, 0, 1)) ** 0.7
    hw = prof(u) * (0.75 + 0.25 * np.cos(np.pi * (v - 0.5)))                             # Kettfaden (senkrecht)
    hf = prof(v) * (0.75 + 0.25 * np.cos(np.pi * (u - 0.5)))                             # Schussfaden (waagerecht)
    h = np.where(warp_up, 0.55 + 0.45 * hw, 0.55 + 0.45 * hf) * np.where(warp_up, 1, 0.97)
    rng = np.random.default_rng(3); nz = ndimage.gaussian_filter(rng.random((n, n)).astype(np.float32), 1.2, mode='wrap')
    h = h + (nz - nz.mean()) * 0.6
    h = (h - h.min()) / (h.max() - h.min())
    return Image.fromarray((h * 255).astype(np.uint8)).convert('L')


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

    for mode in ('kart', 'f1'):
        if len(sys.argv) < 3 or sys.argv[2] == mode: build_seated(mode, V, F, UV, tex, gV0, gF0, gUV0, gtex)   # optional: nur 'kart' oder 'f1' bauen


def build_seated(mode, V, F, UV, tex, gV0, gF0, gUV0, gtex):
    """Sitzender Fahrer: mode 'kart' -> kartfahrer.bin, mode 'f1' -> f1fahrer.bin (F1/F2: nur Oberkörper mit Armen und Händen,
    die Beine liegen unsichtbar im Monocoque und werden weggeschnitten)."""
    global SC
    S = H * 1.10 if mode == 'kart' else H                                               # Kart ist größer gebaut (Helm dort ~0,33 m hoch), F1 in Originalgröße
    SC = S / (H * 1.10)                                                                 # feste Maße (Bündchen, Stulpe) wurden am Kart abgestimmt
    # Ruhehaltung als geschlossene Hülle neu aufbauen: Die Vorlage hat an der Ärmelnaht innen liegende, überlappende Flächen
    # (Ärmel steckt im Rumpf). Beim Biegen klappten die als Schlitze/Trichter heraus. Die Hülle kennt nur noch die Außenfläche.
    V0 = unfold(V, F, tag='Original')
    kV, kF, kUV = remesh_winding(V0, F, UV, 11000)
    # Schulterklappen (Epauletten) der Vorlage oben außen auf den Schultern: abstehende Kanten, die beim Biegen knautschen -> glatt bügeln
    sst = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
    zone = np.zeros(len(kV))
    for sx in (-1, 1): zone = np.maximum(zone, 1 - sst(0.03, 0.06, np.linalg.norm(kV - np.array([sx * 0.11, 0.79, -0.035]), axis=1)))
    kV = taubin_zone(kV, kF, zone, 60)
    Pk, info = pose_kart(kV * S, kF, S, mode)
    if mode == 'f1':                                                                   # Hals nach vorn (Rumpf liegt zurück, der Kopf schaut nach vorn): oberer Hals ganz, Nacken/Schulteransatz weich
        wn = sst(0.79, 0.85, kV[:, 1]) * (1 - sst(0.05, 0.09, np.abs(kV[:, 0]))) * ~(info['arms'][0] | info['arms'][1])
        Pk = Pk + np.outer(wn, [0, 0.0, F1_SHEAR])
    # Nichts im Kart: Punkte, die (z. B. unter dem Gesäß) in Sitzschale/Karosserie stecken, auf deren Oberfläche + 2 mm schieben, Umgebung weich mitnehmen
    import igl
    bk = open(os.path.join(ROOT, 'kart.bin'), 'rb').read(); hl = struct.unpack('<I', bk[:4])[0]; hk = json.loads(bk[4:4 + hl]); cb = [c for c in hk['chunks'] if c['name'] == 'body'][0]
    KP = np.frombuffer(bk, np.float32, cb['nv'] * 3, 4 + hl + cb['pos']).reshape(-1, 3).astype(float); KI = np.frombuffer(bk, np.uint32 if cb.get('i32') else np.uint16, cb['ni'], 4 + hl + cb['idx']).reshape(-1, 3).astype(np.int64)
    km = trimesh.Trimesh(KP, KI, process=False)
    for _ in range(3 if mode == 'kart' else 0):
        inside = np.abs(igl.fast_winding_number(KP, KI, Pk)) > 0.5
        if not inside.any(): break
        cp, dist, tri = trimesh.proximity.closest_point(km, Pk[inside])
        nn = (cp - Pk[inside]) / np.maximum(dist, 1e-9)[:, None]                          # vom Punkt (innen) zur Oberfläche = nach außen
        delta = np.zeros_like(Pk); delta[inside] = cp + nn * 0.002 - Pk[inside]
        Pk = Pk + delta
        print(f'Sitz: {int(inside.sum())} Punkte aus dem Kart geschoben (max {dist.max() * 1000:.1f} mm)')
    # Übergang Rumpf/Arm (Schulter, Achsel) glätten: dort wird am stärksten gebogen, kleine Knautschfalten verschwinden
    aw = info['aw']['R'] + info['aw']['L']; Pk = taubin_zone(Pk, kF, np.clip(aw * (1 - aw) * 4, 0, 1) * (kV[:, 1] > 0.55), 30)
    Pk = unfold(Pk, kF, tag='gebogen')                                                 # letzte kleine Falten lokal glätten
    # Gestauchte Stellen (vorn an der Schulter, wenn der Arm nach vorn schwingt): Dreiecke schrumpfen stark oder klappen um.
    # Dort kräftig glätten (Taubin, schrumpft nicht) – die Knitter verschwinden, die Form bleibt.
    for _ in range(3):
        def comp():
            a0 = np.linalg.norm(np.cross((kV * S)[kF[:, 1]] - (kV * S)[kF[:, 0]], (kV * S)[kF[:, 2]] - (kV * S)[kF[:, 0]]), axis=1)
            n1 = np.cross(Pk[kF[:, 1]] - Pk[kF[:, 0]], Pk[kF[:, 2]] - Pk[kF[:, 0]]); a1 = np.linalg.norm(n1, axis=1)
            N = smooth_normals(Pk, kF); flip = np.einsum('ij,ij->i', n1 / np.maximum(a1, 1e-12)[:, None], N[kF].mean(1)) < 0.3
            return (a1 / np.maximum(a0, 1e-12) < 0.55) | flip
        bad = comp(); z = np.zeros(len(Pk)); z[np.unique(kF[bad])] = 1
        zk = z.copy()
        for _ in range(3):                                                             # Zone um 3 Ringe erweitern, weich
            e = np.vstack([kF[:, [0, 1]], kF[:, [1, 2]], kF[:, [2, 0]]]); nz = zk.copy(); np.maximum.at(nz, e[:, 0], zk[e[:, 1]] * 0.8); np.maximum.at(nz, e[:, 1], zk[e[:, 0]] * 0.8); zk = nz
        print(f'gestaucht: {int(bad.sum())} Dreiecke')
        if not bad.any(): break
        Pk = taubin_zone(Pk, kF, zk * (kV[:, 1] > 0.5), 40)
    # Ärmelende eng ans Handgelenk (wie ein Strickbündchen): die Vorlage hat dort einen weiten, doppelwandigen Ärmel, der wie eine
    # Glocke abstand. Der Handschuh geht danach ÜBER das Bündchen (wie bei echten Rennhandschuhen).
    Mx = np.array([-1.0, 1, 1]); sst = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
    for k, sfx in enumerate(('R', 'L')):
        wr = info['wrist'][sfx][0]; el = info['elbow'] if sfx == 'R' else info['elbow'] * Mx; ax = nrm(wr - el)
        m = info['arms'][k]; P = Pk[m]; d = P - wr; a = d @ ax; rv = d - np.outer(a, ax); r = np.linalg.norm(rv, axis=1)
        # Bündchen: ab 7,5 cm vor dem Handgelenk auf einen runden Querschnitt (r ≈ 3 cm) einziehen; das Ende (geschlossene Kappe der
        # Hülle) als flache, runde Kappe kurz hinter dem Handgelenk – vorher wurden einzelne Punkte der Kappe zu Zacken ausgezogen
        t = sst(-0.075 * SC, -0.035 * SC, a); rs = 0.030 * SC
        nr = r * (1 - t) + np.minimum(r, rs) * t
        ce = -0.012 * SC; cap = a > ce; na = np.where(cap, ce + (a - ce) * 0.2, a)
        nr = np.where(cap, np.minimum(nr, rs * np.sqrt(np.clip(1 - ((a - ce) / (0.03 * SC)) ** 2, 0.05, 1))), nr)
        Pk[m] = wr + np.outer(na, ax) + rv * (nr / np.maximum(r, 1e-9))[:, None]
    for k, (d, L) in info['reach'].items(): print(f'Reichweite {k}: Abstand {d:.3f} m, Armlänge {L:.3f} m')
    print('Sitzpunkt', np.round(info['hip'], 3), 'Schulter', np.round(info['shoulder'], 3), 'Ellbogen', np.round(info['elbow'], 3), 'Arm-Eckpunkte', int(info['arms'][0].sum()), int(info['arms'][1].sum()))
    # Bereiche: 0 Körper, 3 Handschuh. Dazu je Eckpunkt die Höhe in Ruhehaltung (normiert): daraus zieht der Shader
    # Gürtel (0,548…0,592) und Schuhe (< 0,072) pixelgenau – Farbwechsel je Eckpunkt gäbe bei ~9000 Dreiecken Treppenkanten.
    # Bereiche je Eckpunkt: 0 Rumpf, 1 Arm, 2 Bein, 3 Handschuh. aRy = Höhe in Ruhehaltung (Schuhe, Gürtel), aRest/aRN = Ruhe-Position
    # und -Normale: daraus zeichnet der Shader das Anzug-Design (Streifen, Nähte, Reißverschluss) und legt das Stoffgewebe auf.
    # (Vorher stand für Arme ry = 0,5 als „kein Gürtel“ – an der Grenze Arm/Rumpf lief der Wert über die Gürtelhöhe: gezackte Linie.)
    reg = np.zeros(len(kV), np.uint8); ry = kV[:, 1].astype(np.float32)
    reg[(kV[:, 1] < 0.535) & ~(info['arms'][0] | info['arms'][1])] = 2
    reg[info['arms'][0] | info['arms'][1]] = 1
    rest = kV.astype(np.float32); rn = smooth_normals(kV, kF).astype(np.float32)
    # Arm-Skelett fürs Lenken (Skinning im Shader): Knochen 0 Rumpf, 1/2/3 Oberarm/Unterarm/Hand rechts, 4/5/6 links.
    # Gewichte aus der Ruhe-Position entlang des Arms: u = 0 Schulter … 1 Ellbogen … 2 Handgelenk; weiche Übergänge an Schulter, Ellbogen, Bündchen.
    sst = lambda a, b, v: (lambda t: t * t * (3 - 2 * t))(np.clip((v - a) / (b - a), 0, 1))
    bi = np.zeros((len(kV), 4), np.uint8); bw = np.zeros((len(kV), 4), np.float32); bw[:, 0] = 1
    for k, f, b0 in ((0, lambda q: q, 1), (1, mir, 4)):
        m = info['arms'][k]; sh_, el_, wr_ = f(J['sh']), f(J['el']), f(J['wr'])
        tpu = ((kV - sh_) @ (el_ - sh_)) / np.dot(el_ - sh_, el_ - sh_); tfu = ((kV - el_) @ (wr_ - el_)) / np.dot(wr_ - el_, wr_ - el_)
        u = np.where(tfu > 0, 1 + tfu, tpu)
        wa = sst(-0.15, 0.3, u); wf = sst(0.85, 1.15, u); wh = sst(1.82, 1.97, u)
        W4 = np.stack([1 - wa, wa * (1 - wf), wa * wf * (1 - wh), wa * wf * wh], 1)
        bi[m] = [0, b0, b0 + 1, b0 + 2]; bw[m] = W4[m]
    # Handschuhe (verkleinert) an beide Hände
    hV, hF, hUV = decimate(gV0, gF0, gUV0, 1600)
    parts_V, parts_F, parts_UV, parts_R, parts_Y = [Pk], [kF], [kUV * np.array([0.5, 1.0])], [reg], [ry]
    parts_P, parts_N, parts_BI, parts_BW = [rest], [rn], [bi], [bw]
    off = len(Pk)
    armPts = Pk[info['arms'][0]]                                                       # Ärmel (für die Stulpe), nach dem Engziehen
    gvR, gfR = place_glove(hV, hF, *info['grip'], S)
    armR = info['arms'][0]; el = info['elbow']; wr = info['wrist']['R'][0]
    gvR = fit_gauntlet(gvR, hV[:, 1], armPts, wr, nrm(wr - el), S)
    # Prüfung: Abstand der Handschuh-Eckpunkte zur Kranz-Mittellinie (Kranzrohr 0,021 m) – Faust soll ihn umschließen, nicht durchdringen
    az_ = info['WF']['az']; RR = info['WF']['R']; Cw = info['C']; rel = gvR - Cw; rp = rel - np.outer(rel @ az_, az_)
    ring = Cw + RR * rp / np.linalg.norm(rp, axis=1, keepdims=True); dr = np.linalg.norm(gvR - ring, axis=1)
    near = dr < 0.06
    print(f'Handschuh–Kranz: kleinster Abstand {dr.min():.3f} m, Eckpunkte im Rohr {int((dr < (0.019 if mode == "kart" else 0.0175)).sum())}, Winkelabdeckung um den Kranz', end=' ')
    tang = np.cross(az_, rp / np.linalg.norm(rp, axis=1, keepdims=True)); u1 = rp / np.linalg.norm(rp, axis=1, keepdims=True); d = gvR - ring
    ang = np.degrees(np.arctan2(d @ az_, np.sum(d * u1, 1)))[near]; print(f'{np.ptp(ang):.0f}°')
    for s, sfx in ((-1, 'R'), (1, 'L')):
        pv, pf = (gvR, gfR) if s < 0 else (gvR * np.array([-1.0, 1, 1]), gfR[:, ::-1])   # linke Hand gespiegelt
        parts_V.append(pv); parts_F.append(pf + off); parts_UV.append(hUV * np.array([0.5, 1.0]) + np.array([0.5, 0.0])); parts_R.append(np.full(len(pv), 3, np.uint8)); parts_Y.append(np.full(len(pv), -1, np.float32)); parts_P.append(np.zeros((len(pv), 3), np.float32)); parts_BI.append(np.tile([0, 3 if s < 0 else 6, 0, 0], (len(pv), 1)).astype(np.uint8)); parts_BW.append(np.tile([0, 1, 0, 0], (len(pv), 1)).astype(np.float32)); parts_N.append(np.tile([0, 1, 0], (len(pv), 1)).astype(np.float32)); off += len(pv)
        print(f'Handgelenk {sfx}: Arm endet bei {np.round(info["wrist"][sfx][0], 3)}, Handschuh bei {np.round(info["wrist"][sfx][1], 3)}')
    AV, AF, AUV, AR, AY = np.vstack(parts_V), np.vstack(parts_F), np.vstack(parts_UV), np.concatenate(parts_R), np.concatenate(parts_Y)
    PP, PN, BI, BW = np.vstack(parts_P), np.vstack(parts_N), np.vstack(parts_BI), np.vstack(parts_BW)
    if mode == 'f1':
        # F1/F2: Beine und Becken liegen unsichtbar im Monocoque -> weg (nur Oberkörper mit Armen und Händen). Schnitt unter dem Gürtel.
        low = (AR != 3) & (AR != 1) & (AY < F1_CUT)
        AF = AF[~low[AF].all(1)]; used = np.unique(AF); re = -np.ones(len(AV), np.int64); re[used] = np.arange(len(used)); AF = re[AF]
        AV, AUV, AR, AY, PP, PN, BI, BW = (a[used] for a in (AV, AUV, AR, AY, PP, PN, BI, BW))
        print(f'F1: Beine weggeschnitten (Rest-y < {F1_CUT}), {len(AF)} Dreiecke übrig')
    N = smooth_normals(AV, AF)
    # Atlas: links Anzug-Schattierung, rechts Handschuh
    if mode == 'kart':
      atl = Image.new('RGB', (1024, 512)); atl.paste(tex.resize((512, 512), Image.LANCZOS), (0, 0)); atl.paste(glove_texture(gtex).resize((512, 512), Image.LANCZOS), (512, 0))
      atl.save(os.path.join(ROOT, 'textures', 'kart_fahrer.jpg'), quality=86)
      weave_texture().save(os.path.join(ROOT, 'textures', 'kart_stoff.jpg'), quality=92)
    # Binärformat wie kart.bin: [u32 Länge][JSON-Kopf][Daten]
    # Helm lückenlos auf den Hals: Unterkante 4,5 cm unter dem oberen Ende des Halses (Kragen), mittig über dem Hals, leicht nach vorn
    nk = Pk[kV[:, 1] > 0.845]; HB_BOTTOM = 0.154 * (1.1 if mode == 'kart' else 1.0)                                # Helm-Unterkante unter der Mitte (Spielhelm × 1,1)
    helm = np.array([0.0, nk[:, 1].max() - (0.045 if mode == 'kart' else F1_NECK) + HB_BOTTOM, (nk[:, 2].min() + nk[:, 2].max()) / 2 + 0.02])
    print('Hals oben', np.round(nk[:, 1].max(), 3), '→ Helm', np.round(helm, 3), '(vorher', np.round(info['head'], 3), ')')
    blobs, hdr = [], {'nv': len(AV), 'ni': AF.size, 'helm': np.round(helm, 4).tolist(), 'helmTilt': 0.0, 'swExt': round(info['swExt'], 4)}
    def put(name, arr):
        off = sum(len(b) for b in blobs); b = arr.tobytes(); b += b'\0' * (-len(b) % 4); blobs.append(b); hdr[name] = off
    put('pos', AV.astype(np.float32)); put('nrm', N.astype(np.float32)); put('uv', AUV.astype(np.float32)); put('reg', AR.astype(np.uint8)); put('ry', AY.astype(np.float32))
    put('rest', PP.astype(np.float32)); put('rn', np.round(PN * 127).astype(np.int8))
    BW = BW / BW.sum(1, keepdims=True)
    put('bi', BI.astype(np.uint8)); put('bw', np.round(BW * 255).astype(np.uint8))
    shP, elP, wrP = info['shoulder'], info['elbow'], info['wrist']['R'][0]
    hdr['grip'] = np.round(info['grip'][0], 4).tolist()                                 # Griffmitte rechts (Faust um diesen Punkt) – Laufzeit-IK dreht die Hand um das Rohr durch diesen Punkt
    hdr['arm'] = [np.round(v, 4).tolist() for v in (shP, elP, wrP)]                       # Gelenke rechts (Sitzhaltung); links = gespiegelt
    hdr['swC'] = np.round(info['C'], 4).tolist(); hdr['swAx'] = np.round(info['WF']['az'], 5).tolist(); hdr['rimR'] = round(float(info['WF']['R']), 4)
    put('idx', AF.astype(np.uint16 if len(AV) < 65536 else np.uint32).reshape(-1)); hdr['i32'] = len(AV) >= 65536
    hj = json.dumps(hdr).encode(); hj += b' ' * (-len(hj) % 4)
    with open(os.path.join(ROOT, 'kartfahrer.bin' if mode == 'kart' else 'f1fahrer.bin'), 'wb') as fo: fo.write(struct.pack('<I', len(hj)) + hj + b''.join(blobs))
    print(mode, 'Fahrer:', len(AV), 'Eckpunkte,', len(AF), 'Dreiecke; Helm bei', hdr['helm'])


if __name__ == '__main__':
    main()
