"""Klassiker-Autos (Lotus 49C, Ferrari F2004, McLaren MP4/4) spieltauglich machen.

Aufruf (x64-Python mit pymeshlab, scipy, pillow):
    python tools/klassiker/build_klassiker.py <quelle.glb> <schluessel> <zielordner>
Schlüssel: lotus49c | ferrari_f2004 | mclaren_mp44

Was passiert:
  1. Alle Teile in Weltkoordinaten zusammenführen, ausrichten wie die Spielautos (Meter, y = oben, +z = vorne,
     Boden y = 0, Mitte zwischen den Achsen z = 0, Wagenmitte x = 0). Der Lotus kam 4-fach zu groß und rückwärts.
  2. Räder finden (äußerste Scheiben je Viertel) und als eigene Knoten abtrennen (drehbar um die x-Achse).
  3. Materialien bündeln: kleine/einfarbige/fein gekachelte Texturen werden zu Vertex-Farben,
     alle so gefärbten Teile teilen sich wenige Materialien (je Glanzstufe). Normal-Maps entfallen.
  4. Vereinfachen (Quadric Edge Collapse mit Texturkoordinaten) in drei Detailstufen.
  5. Texturen verkleinern (Lack/Sponsoren 1024, sonst 512, JPEG wo keine Transparenz).
  6. Als GLB schreiben (KHR_mesh_quantization: Positionen int16, Normalen int8, Farben uint8).
Ergebnis: <zielordner>/<schluessel>.glb mit den Knoten LOD0, LOD1, LOD2 (je Rumpf + wheel_FL/FR/RL/RR).
"""
import sys, os, io, json, re
import numpy as np
from PIL import Image
from scipy import sparse
from scipy.sparse.csgraph import connected_components
import pymeshlab as ml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbio import read_glb, flatten, image_bytes, GLBWriter

CARS = {
    'lotus49c':      dict(title='Lotus 49C (1970)',     front=-1, wheelbase=2.413, big=['main_body']),
    'ferrari_f2004': dict(title='Ferrari F2004 (2004)', front=1,  wheelbase=None,  big=['Carpaint', 'EXT_Sponsors']),
    'mclaren_mp44':  dict(title='McLaren MP4/4 (1988)', front=1,  wheelbase=None,  big=['BODY']),
}
LOD_TRIS = [80000, 26000, 9000]
# Kameras wie MODELS.cam/.tv im Spiel (Auto-Koordinaten, +z vorne, z = 0 Mitte zwischen den Achsen): [x, y, z, Absenkung des Blickziels in 30 m]
CAMS = {"lotus49c": {"cockpit": [0, 0.9, 0.02, 0.3], "tv": [0, 1.1, -0.4, 1.8]}, "mclaren_mp44": {"cockpit": [0, 0.88, -0.05, 0.15], "tv": [0, 1.02, -0.18, 1.8]}, "ferrari_f2004": {"cockpit": [0, 0.8, 0.05, 0.3], "tv": [0, 1.16, -0.1, 2.0]}}
CREASE = np.cos(np.radians(40))


def srgb2lin(c): c = np.asarray(c, np.float64); return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


# ---------------------------------------------------------------------------------------------
# Materialien analysieren
# ---------------------------------------------------------------------------------------------
class MatInfo:
    pass


def analyse_materials(js, bn, uv_range):
    out = {}
    imgcache = {}

    def img(ti):
        si = js['textures'][ti]['source']
        if si not in imgcache: imgcache[si] = Image.open(io.BytesIO(image_bytes(js, bn, si))).convert('RGBA')
        return si, imgcache[si]

    for mi, m in enumerate(js.get('materials', [])):
        pb = m.get('pbrMetallicRoughness', {}); I = MatInfo(); I.name = m.get('name') or 'mat%d' % mi
        I.factor = np.array(pb.get('baseColorFactor', [1, 1, 1, 1]), np.float64)
        I.metal = float(pb.get('metallicFactor', 1.0)); I.rough = float(pb.get('roughnessFactor', 1.0))
        I.alpha = m.get('alphaMode', 'OPAQUE'); I.cutoff = m.get('alphaCutoff', 0.5); I.double = bool(m.get('doubleSided', False))
        I.mr_img = None; I.std = 0; I.keep = (False, False)
        bt = pb.get('baseColorTexture'); I.img_id = None; I.mode = 'const'; I.const = I.factor.copy(); I.arr = None
        rng = uv_range.get(mi, np.array([0.0, 0.0]))
        if bt is not None:
            si, im = img(bt['index'])
            small = np.asarray(im.resize((64, 64), Image.BILINEAR), np.float64) / 255
            lin = srgb2lin(small[..., :3]); mean = np.concatenate([lin.reshape(-1, 3).mean(0), [small[..., 3].mean()]])
            std = small[..., :3].std() * 255; I.std = std
            I.const = mean * I.factor
            w, h = im.size
            if std < 5 or rng.max() > 8: I.mode = 'const'                       # einfarbig oder fein gekachelt (Carbon, Riffel) -> Mittelwert
            elif max(w, h) <= 128: I.mode = 'sample'                            # kleine Paletten-/Verlaufstextur -> an den Ecken abtasten
            else: I.mode = 'tex'
            ims = im if max(w, h) <= 256 else im.resize((max(1, w * 256 // max(w, h)), max(1, h * 256 // max(w, h))), Image.BOX)
            a = np.asarray(ims, np.float64) / 255; I.arr = np.concatenate([srgb2lin(a[..., :3]), a[..., 3:]], -1)
            I.img_id = si; I.img = im
            mrt = pb.get('metallicRoughnessTexture')
            if mrt is not None and mrt.get('texCoord', 0) == bt.get('texCoord', 0): I.mr_img = img(mrt['index'])
        # Transparenz nur behalten, wenn wirklich durchsichtig
        if I.alpha == 'BLEND' and I.mode != 'tex' and I.const[3] > 0.97: I.alpha = 'OPAQUE'
        out[mi] = I
    return out


def sample_bilinear(arr, uv):
    h, w = arr.shape[:2]
    x = (uv[:, 0] % 1.0) * w - 0.5; y = (uv[:, 1] % 1.0) * h - 0.5
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
    x0 %= w; y0 %= h; x1 = (x0 + 1) % w; y1 = (y0 + 1) % h
    return (arr[y0, x0] * (1 - fx) * (1 - fy) + arr[y0, x1] * fx * (1 - fy) + arr[y1, x0] * (1 - fx) * fy + arr[y1, x1] * fx * fy)


# ---------------------------------------------------------------------------------------------
# Räder finden
# ---------------------------------------------------------------------------------------------
def find_wheels(P):
    lo, hi = np.percentile(P, 0.05, 0), np.percentile(P, 99.95, 0)
    xc = (lo[0] + hi[0]) / 2; zc = (lo[2] + hi[2]) / 2; W = hi[0] - lo[0]
    wheels = {}
    for sz, fr in [(1, 'F'), (-1, 'R')]:
        for sx, lr in [(-1, 'L'), (1, 'R')]:
            q = (sz * (P[:, 2] - zc) > 0) & (sx * (P[:, 0] - xc) > 0)
            Q = P[q]; ox = sx * (Q[:, 0] - xc); qmax = ox.max()
            band = Q[ox > qmax - 0.05 * W]
            ylo, yhi = np.percentile(band[:, 1], [0.5, 99.5]); zlo, zhi = np.percentile(band[:, 2], [0.5, 99.5])
            cy, cz = (ylo + yhi) / 2, (zlo + zhi) / 2; R0 = max(yhi - ylo, zhi - zlo) / 2
            r = np.hypot(Q[:, 1] - cy, Q[:, 2] - cz)
            # die Außenflanke ist gewölbt -> Radius über die Lauffläche bestimmen (äußere 30 % der Reifenbreite, nicht weiter als 1,4 R0)
            near = (ox > qmax - 0.6 * R0) & (r < 1.4 * R0)
            R = np.percentile(r[near], 99.7)
            tread = (r > 0.93 * R) & (r < 1.03 * R) & (ox > qmax - 1.6 * R)
            inner = np.percentile(ox[tread], 1)
            # Rad sitzt im Lotus/Ferrari/McLaren als Scheibe zwischen inner und qmax
            wheels[fr + lr] = dict(sx=sx, cy=cy, cz=cz, R=R, outer=qmax, inner=inner, xc=xc)
    return wheels


# ---------------------------------------------------------------------------------------------
# Normalen mit Knickwinkel (auf verschweißten Positionen)
# ---------------------------------------------------------------------------------------------
def crease_normals(V, F):
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    fn = np.cross(b - a, c - a); fu = fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-20)
    nf = len(F); cv = F.reshape(-1); cf = np.repeat(np.arange(nf), 3)
    order = np.argsort(cv, kind='stable'); cvs = cv[order]
    cnt = np.bincount(cvs, minlength=len(V)); start = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    n_of = cnt[cvs]; tot = int(n_of.sum())
    ii = np.repeat(np.arange(len(cvs)), n_of)
    offs = np.arange(tot) - np.repeat(np.cumsum(n_of) - n_of, n_of)
    jj = start[cvs][ii] + offs
    fi, fj = cf[order][ii], cf[order][jj]
    ok = (fu[fi] * fu[fj]).sum(1) >= CREASE
    acc = np.zeros((len(cvs), 3)); np.add.at(acc, ii[ok], fn[fj[ok]])
    N = np.zeros((nf * 3, 3)); N[order] = acc
    N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-20
    bad = np.linalg.norm(N, axis=1) < 0.5; N[bad] = np.repeat(fu, 3, 0)[bad]
    return N.reshape(nf, 3, 3)


def transfer_uv(V0, F0, W0, FM0, V1, F1, FM1):
    """Texturkoordinaten für das vereinfachte Netz: jede Ecke ist ein Originalpunkt. Unter den Original-Ecken mit gleichem Punkt und gleichem
    Material nimmt sie die UV der Fläche, die der neuen Fläche am nächsten liegt (richtige Seite einer Naht). Ohne Treffer: nächste Ecke gleichen Materials."""
    from scipy.spatial import cKDTree
    d, vmap = cKDTree(V0).query(V1)
    c0 = np.repeat(V0[F0].mean(1), 3, 0); cv0 = F0.reshape(-1); cm0 = np.repeat(FM0, 3); uv0 = W0.reshape(-1, 2)
    key0 = cv0 * 10000 + cm0; order = np.argsort(key0, kind='stable'); ks = key0[order]
    c1 = np.repeat(V1[F1].mean(1), 3, 0); key1 = vmap[F1].reshape(-1) * 10000 + np.repeat(FM1, 3)
    lo = np.searchsorted(ks, key1, 'left'); hi = np.searchsorted(ks, key1, 'right'); n = hi - lo
    out = np.zeros((len(key1), 2))
    has = n > 0; idx = np.nonzero(has)[0]; nn = n[idx]; tot = int(nn.sum())
    ii = np.repeat(np.arange(len(idx)), nn); jj = lo[idx][ii] + (np.arange(tot) - np.repeat(np.cumsum(nn) - nn, nn))
    dist = np.linalg.norm(c0[order[jj]] - c1[idx][ii], axis=1)
    srt = np.lexsort((dist, ii)); firsts = srt[np.concatenate([[0], np.cumsum(nn)[:-1]])]
    out[idx] = uv0[order[jj[firsts]]]
    miss = np.nonzero(~has)[0]
    if len(miss):
        mm = np.repeat(FM1, 3)[miss]; P1 = V1[F1.reshape(-1)[miss]]
        for m in np.unique(mm):
            sel = cm0 == m; t = cKDTree(V0[cv0[sel]]); _, j = t.query(P1[mm == m]); out[miss[mm == m]] = uv0[np.nonzero(sel)[0][j]]
    return out.reshape(-1, 3, 2)


def write_ply(path, V, F, Wuv, FI):
    """Binäres PLY mit Ecken-UVs (texcoord), Texturnummer 0 und Flächenwert (quality = Teil*10000 + Material).
    Nur so setzt MeshLab gültige Texturindizes, die das texturtreue Vereinfachen verlangt."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    hdr = ('ply\nformat binary_little_endian 1.0\ncomment TextureFile dummy.png\nelement vertex %d\nproperty double x\nproperty double y\nproperty double z\n'
           'element face %d\nproperty list uchar int vertex_indices\nproperty list uchar float texcoord\nproperty int texnumber\nproperty float quality\nend_header\n') % (len(V), len(F))
    fd = np.dtype([('n', 'u1'), ('v', '<i4', 3), ('m', 'u1'), ('t', '<f4', 6), ('tn', '<i4'), ('q', '<f4')])
    fa = np.zeros(len(F), fd); fa['n'] = 3; fa['v'] = F; fa['m'] = 6; fa['t'] = Wuv.reshape(-1, 6); fa['tn'] = 0; fa['q'] = FI
    with open(path, 'wb') as f:
        f.write(hdr.encode()); f.write(np.ascontiguousarray(V, '<f8').tobytes()); f.write(fa.tobytes())
    return path


# ---------------------------------------------------------------------------------------------
def main(src, key, outdir):
    cfg = CARS[key]
    js, bn = read_glb(src)
    prims = flatten(js, bn)
    # ---- zusammenführen ----
    Ps, Fs, UVs, Ms = [], [], [], []; off = 0
    for p in prims:
        Ps.append(p['pos']); Fs.append(p['idx'] + off); off += len(p['pos'])
        UVs.append(p['uv'][p['idx']]); Ms.append(np.full(len(p['idx']), p['mat']))
    P = np.concatenate(Ps); F = np.concatenate(Fs); WUV = np.concatenate(UVs); FM = np.concatenate(Ms); FM[FM < 0] = 9999
    print(key, 'Quelle:', len(F), 'Dreiecke', len(js.get('materials', [])), 'Materialien')
    # ---- ausrichten ----
    if cfg['front'] < 0: P = P * np.array([-1, 1, -1])            # 180° um y
    wh = find_wheels(P)
    zF = (wh['FL']['cz'] + wh['FR']['cz']) / 2; zR = (wh['RL']['cz'] + wh['RR']['cz']) / 2
    s = cfg['wheelbase'] / (zF - zR) if cfg['wheelbase'] else 1.0
    xc = np.mean([w['xc'] for w in wh.values()])
    ground = min(w['cy'] - w['R'] for w in wh.values())
    shift = np.array([xc, ground, (zF + zR) / 2])
    P = (P - shift) * s
    for k, w in wh.items():
        w.update(cy=(w['cy'] - ground) * s, cz=(w['cz'] - shift[2]) * s, R=w['R'] * s, outer=w['outer'] * s, inner=w['inner'] * s,
                 cx=w['sx'] * (w['outer'] + w['inner']) / 2 * s)
        w['outer_s'], w['inner_s'] = w['outer'], w['inner']
    print('  Maßstab %.4f  Radstand %.3f m  Länge %.3f m  Breite %.3f m  Höhe %.3f m' % (s, (zF - zR) * s, np.ptp(P[:, 2]), np.ptp(P[:, 0]), P[:, 1].max()))
    for k, w in wh.items(): print('  Rad %s: Mitte x %.3f y %.3f z %.3f  Radius %.3f  Breite %.3f' % (k, w['cx'], w['cy'], w['cz'], w['R'], w['outer'] - w['inner']))
    # ---- zusammenhängende Teile im Originalnetz (vor dem Verschweißen: sonst kleben Reifen an Querlenkern) ----
    nP = len(P)
    A = sparse.coo_matrix((np.ones(len(F) * 2), (np.concatenate([F[:, 0], F[:, 1]]), np.concatenate([F[:, 1], F[:, 2]]))), shape=(nP, nP))
    ncomp, lab = connected_components(A, directed=False)
    P_orig = P; F_orig = F
    # ---- verschweißen ----
    q = np.round(P / 2e-5).astype(np.int64)
    _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    V = P[first]; F = inv.reshape(-1)[F]
    good = (F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 0] != F[:, 2])
    F, WUV, FM = F[good], WUV[good], FM[good]; F_orig = F_orig[good]
    # ---- Materialien ----
    uv_range = {}
    for mi in np.unique(FM):
        u = WUV[FM == mi].reshape(-1, 2); uv_range[mi] = np.ptp(u, 0) if len(u) else np.zeros(2)
    mats = analyse_materials(js, bn, uv_range)
    # ---- Räder abtrennen (zusammenhängende Teile innerhalb der Radscheibe) ----
    #  a) Teile, die ganz in der Radscheibe liegen   b) Flächen von „Radmaterialien“ (Reifen, Felge: >85 % ihrer Flächen in den Radscheiben), die in der Scheibe liegen
    flab = lab[F_orig[:, 0]]
    part = np.zeros(len(F), np.int64)   # 0 Rumpf, 1..4 Räder
    WN = ['FL', 'FR', 'RL', 'RR']
    caliper = np.array([('calip' in mats[m].name.lower()) if m in mats else False for m in range(10000)])
    fin = np.zeros((4, len(F)), bool)
    for wi, k in enumerate(WN):
        w = wh[k]; ox = w['sx'] * P_orig[:, 0]; r = np.hypot(P_orig[:, 1] - w['cy'], P_orig[:, 2] - w['cz'])
        inside = (r <= w['R'] * 1.04) & (ox >= w['inner'] - 0.08 * w['R']) & (ox <= w['outer'] + 0.02)
        cin = np.ones(ncomp, bool); np.logical_and.at(cin, lab, inside)
        fin[wi] = inside[F_orig].all(1)
        fsel = cin[flab] & ~caliper[FM] & (part == 0)
        part[fsel] = wi + 1
    anyin = fin.any(0); wheelmat = np.zeros(10000, bool)
    for mi in np.unique(FM):
        s2 = FM == mi
        if anyin[s2].mean() > 0.85 and not caliper[mi]: wheelmat[mi] = True
    print('  Radmaterialien:', [mats[m].name for m in np.nonzero(wheelmat)[0] if m in mats])
    for wi, k in enumerate(WN):
        fsel = fin[wi] & wheelmat[FM] & (part == 0); part[fsel] = wi + 1
        print('  Rad %s: %d Dreiecke' % (k, (part == wi + 1).sum()))
    # ---- welche Texturen bleiben? Lack/Sponsoren immer, dazu die 3 auffälligsten Flächen am Rumpf und die Reifenflanke am Rad ----
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]; area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    for wheel in (False, True):
        sel = (part > 0) if wheel else (part == 0)
        cand = []
        for mi in np.unique(FM[sel]):
            I = mats.get(mi)
            if I is None or I.mode != 'tex': continue
            A_ = area[sel & (FM == mi)].sum()
            if not wheel and any(x.lower() in I.name.lower() for x in cfg['big']): I.keep = (True, I.keep[1]); continue
            cand.append((A_ * (I.std if not wheel else 1), A_, mi))
        cand.sort(reverse=True)
        for sc_, A_, mi in cand[:1 if wheel else 3]:
            if A_ > 0.01: mats[mi].keep = (mats[mi].keep[0] or not wheel, mats[mi].keep[1] or wheel)
    print('  Texturen Rumpf:', [I.name for I in mats.values() if I.keep[0]], ' Rad:', [I.name for I in mats.values() if I.keep[1]])
    fid = (part * 10000 + FM).astype(np.float64)
    # ---- Detailstufen: rein geometrisch vereinfachen (texturtreues Vereinfachen blockiert an Nähten und gab den Rädern fast alles),
    #      Ecken bleiben Originalpunkte (keine optimale Platzierung) -> Texturkoordinaten danach aus dem Original übernehmen ----
    lods = []
    tmp = os.path.join(outdir, '_tmp_%s.ply' % key)
    write_ply(tmp, V, F, np.zeros((len(F), 3, 2)), fid)
    for li, target in enumerate(LOD_TRIS):
        ms = ml.MeshSet(); ms.load_new_mesh(tmp)
        if len(F) > target:
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(target), qualitythr=0.3, preserveboundary=False, boundaryweight=1.5,
                                                        optimalplacement=False, preservenormal=True, planarquadric=True, autoclean=True)
        m = ms.current_mesh(); V1 = m.vertex_matrix(); F1 = m.face_matrix().astype(np.int64); I1 = m.face_scalar_array()
        W1 = transfer_uv(V, F, WUV, FM, V1, F1, (I1 % 10000).astype(np.int64))
        print('  LOD%d: %d Dreiecke (Rumpf %d, Räder %s)' % (li, len(F1), (I1 < 10000).sum(), [int(((I1 // 10000) == k).sum()) for k in (1, 2, 3, 4)]))
        lods.append((V1, F1, W1, I1))
    try: os.remove(tmp)
    except OSError: pass
    uvoff, uvsc = {}, {}
    write(cfg, key, outdir, lods, mats, wh, uvoff, uvsc, js, bn)


# ---------------------------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------------------------
def rbucket(r): return 0 if r < 0.5 else 1


def write(cfg, key, outdir, lods, mats, wh, uvoff, uvsc, js, bn):
    W = GLBWriter(); W.js['extensionsUsed'] = ['KHR_mesh_quantization']; W.js['extensionsRequired'] = ['KHR_mesh_quantization']
    tex_of_img = {}; mat_of_group = {}

    def texture_for(I, mr=False):
        im = I.mr_img[1] if mr else I.img; ident = (I.mr_img[0] if mr else I.img_id, mr)
        if ident in tex_of_img: return tex_of_img[ident]
        big = any(b.lower() in I.name.lower() for b in cfg['big'])
        lim = 1024 if (big and not mr) else 512
        w, h = im.size; f = min(1.0, lim / max(w, h)); im2 = im.resize((max(4, round(w * f)), max(4, round(h * f))), Image.LANCZOS) if f < 1 else im
        bio = io.BytesIO()
        alpha_used = (not mr) and I.alpha != 'OPAQUE' and np.asarray(im2)[..., 3].min() < 250
        if alpha_used: im2.save(bio, 'PNG', optimize=True); mime = 'image/png'
        else: im2.convert('RGB').save(bio, 'JPEG', quality=84, optimize=True, progressive=False); mime = 'image/jpeg'
        ti = W.texture(W.image(bio.getvalue(), mime, ('%s_mr' if mr else '%s') % re.sub(r'[^A-Za-z0-9_]', '_', I.name)))
        tex_of_img[ident] = ti; return ti

    def group_of(mi, wheel, lod):
        I = mats.get(mi)
        if I is None: return ('vc', 'OPAQUE', 0, 1, False)
        big = any(x.lower() in I.name.lower() for x in cfg['big'])
        # ferne Stufen: nur Lack/Sponsoren (und in LOD1 die Reifenflanke) als Textur, der Rest als Vertex-Farbe
        if I.mode == 'tex' and I.keep[1 if wheel else 0] and (lod == 0 or (not wheel and big) or (wheel and lod == 1)):
            return ('tex', I.img_id, tuple(np.round(I.factor, 3)), I.alpha, round(I.metal, 2), round(I.rough, 2), I.double, I.mr_img is not None)
        return ('vc', I.alpha, int(I.metal > 0.5), rbucket(I.rough), I.double)

    def material_for(g, mi):
        if g in mat_of_group: return mat_of_group[g]
        I = mats.get(mi)
        if g[0] == 'tex':
            pb = {'baseColorTexture': {'index': texture_for(I)}, 'baseColorFactor': [float(x) for x in I.factor], 'metallicFactor': I.metal, 'roughnessFactor': I.rough}
            if I.mr_img is not None: pb['metallicRoughnessTexture'] = {'index': texture_for(I, mr=True)}
            m = {'name': I.name, 'pbrMetallicRoughness': pb}
            if I.alpha != 'OPAQUE': m['alphaMode'] = I.alpha
            if I.alpha == 'MASK': m['alphaCutoff'] = I.cutoff
        else:
            _, alpha, metal, rb, dbl = g
            m = {'name': 'farbe_%s_%s%s' % ('metall' if metal else 'lack', 'glanz' if rb == 0 else 'matt', '_glas' if alpha != 'OPAQUE' else ''),
                 'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'metallicFactor': float(metal), 'roughnessFactor': [0.35, 0.75][rb]}}
            if alpha != 'OPAQUE': m['alphaMode'] = 'BLEND'
        if g[-1 if g[0] == 'vc' else 6]: m['doubleSided'] = True
        mat_of_group[g] = W.material(m); return mat_of_group[g]

    def emit_mesh(name, V, F, Wuv, FMi, Ncorner, center, wheel, lod):
        """Ein Mesh mit je einem Primitive pro Materialgruppe. Positionen relativ zu center, int16-quantisiert."""
        prims = []
        Vl = V - center
        lo, hi = Vl[F].reshape(-1, 3).min(0), Vl[F].reshape(-1, 3).max(0); mid = (lo + hi) / 2; sc = max(1e-6, (hi - lo).max() / 2 / 32000)
        groups = {}
        for mi in np.unique(FMi): groups.setdefault(group_of(mi, wheel, lod), []).append(mi)
        for g, mlist in groups.items():
            sel = np.isin(FMi, mlist); f = F[sel]; uv = Wuv[sel].copy(); fm = FMi[sel]; nrm = Ncorner[sel]
            col = np.ones((len(f), 3, 4))
            for mi in mlist:
                I = mats.get(mi); s2 = fm == mi
                if I is None: continue
                if mi in uvoff: uv[s2] = uv[s2] * uvsc[mi] + uvoff[mi]
                if g[0] == 'vc':
                    if I.mode in ('sample', 'tex'): c = sample_bilinear(I.arr, uv[s2].reshape(-1, 2)) * I.factor; col[s2] = c.reshape(-1, 3, 4)
                    else: col[s2] = I.const
            # Ecken -> Vertices (gleiche Position, UV, Normale, Farbe zusammenlegen)
            pos_i = f.reshape(-1)
            keyarr = np.concatenate([pos_i[:, None].astype(np.float64), np.round(nrm.reshape(-1, 3) * 127),
                                     np.round(uv.reshape(-1, 2) * 4096) if g[0] == 'tex' else np.zeros((len(pos_i), 2)),
                                     np.round(col.reshape(-1, 4) * 255) if g[0] == 'vc' else np.zeros((len(pos_i), 4))], 1)
            _, first, inv = np.unique(keyarr, axis=0, return_index=True, return_inverse=True)
            inv = inv.reshape(-1)
            qp = np.round((Vl[pos_i[first]] - mid) / sc).astype(np.int16)
            nq = np.round(nrm.reshape(-1, 3)[first] * 127).astype(np.int8)
            at = {}
            pa = W.acc(qp, 'VEC3', 34962, minmax=True)
            at['POSITION'] = pa
            at['NORMAL'] = W.acc(nq, 'VEC3', 34962, normalized=True)
            if g[0] == 'tex': at['TEXCOORD_0'] = W.acc(uv.reshape(-1, 2)[first].astype(np.float32), 'VEC2', 34962)
            else:
                c = np.clip(col.reshape(-1, 4)[first], 0, 1)
                if g[1] == 'OPAQUE': c[:, 3] = 1
                at['COLOR_0'] = W.acc(np.round(c * 255).astype(np.uint8), 'VEC4', 34962, normalized=True)
            idx = inv.astype(np.uint16 if len(first) < 65535 else np.uint32)
            prims.append({'attributes': at, 'indices': W.acc(idx, 'SCALAR', 34963), 'material': material_for(g, mlist[0])})
        return W.mesh(name, prims), mid, sc

    # int16-VEC3-Positionen: Accessor-Stride muss Vielfaches von 4 sein -> eigener Stride
    _acc = W.acc

    def acc_aligned(arr, kind, target=None, minmax=False, normalized=False):
        arr = np.ascontiguousarray(arr)
        if kind == 'VEC3' and arr.dtype.itemsize < 4:
            n = arr.shape[0]; per = arr.dtype.itemsize * 3; stride = (per + 3) // 4 * 4
            buf = np.zeros((n, stride), np.uint8); buf[:, :per] = arr.view(np.uint8).reshape(n, per)
            ai = _acc(buf, 'SCALAR', target)   # Rohdaten mit Stride, Typ unten setzen
            a = W.js['accessors'][ai]
            a.update(componentType={1: 5120, 2: 5122}[arr.dtype.itemsize] if arr.dtype.kind == 'i' else {1: 5121, 2: 5123}[arr.dtype.itemsize], type='VEC3', count=n)
            W.js['bufferViews'][a['bufferView']]['byteStride'] = stride
            if normalized: a['normalized'] = True
            if minmax: a['min'] = arr.min(0).astype(float).tolist(); a['max'] = arr.max(0).astype(float).tolist()
            return ai
        return _acc(arr, kind, target, minmax, normalized)
    W.acc = acc_aligned

    root_children = []
    stats = []
    for li, (V, F, Wuv, FI) in enumerate(lods):
        part = (FI // 10000).astype(int); FMi = (FI % 10000).astype(int)
        N = crease_normals(V, F)
        kids = []; tri = 0; draws = 0
        for pi, nm in enumerate(['body', 'wheel_FL', 'wheel_FR', 'wheel_RL', 'wheel_RR']):
            sel = part == pi
            if not sel.any(): continue
            if pi == 0: c = np.zeros(3)
            else: w = wh[nm[-2:]]; c = np.array([w['cx'], w['cy'], w['cz']])
            mi, mid, sc = emit_mesh('%s_LOD%d' % (nm, li), V, F[sel], Wuv[sel], FMi[sel], N[sel], c, pi > 0, li)
            draws += len(W.js['meshes'][mi]['primitives']); tri += int(sel.sum())
            mnode = W.node({'name': '%s_mesh' % nm, 'mesh': mi, 'translation': [float(x) for x in mid], 'scale': [float(sc)] * 3}, root=False)
            if pi == 0: kids.append(mnode)
            else: kids.append(W.node({'name': nm, 'translation': [float(x) for x in c], 'children': [mnode]}, root=False))
        n = W.node({'name': 'LOD%d' % li, 'children': kids}, root=False); root_children.append(n)
        stats.append(dict(lod=li, tris=tri, draws=draws))
    wheels = {k: dict(x=round(w['cx'], 4), y=round(w['cy'], 4), z=round(w['cz'], 4), r=round(w['R'], 4), width=round(w['outer'] - w['inner'], 4)) for k, w in wh.items()}
    W.node({'name': key, 'children': root_children, 'extras': {'title': cfg['title'], 'wheels': wheels, 'lods': stats,
                                                              'lodDistances': [0, 18, 45], 'cams': CAMS[key]}})
    os.makedirs(outdir, exist_ok=True); path = os.path.join(outdir, key + '.glb'); W.save(path)
    print('  ->', path, '%.2f MB' % (os.path.getsize(path) / 1e6), 'Materialien', len(W.js.get('materials', [])), 'Texturen', len(W.js.get('images', [])), stats)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
