#!/usr/bin/env python3
"""Aufkleberbögen erzeugen:  python3 tools/sticker/build.py <Kürzel> [<Kürzel> ...] | all

Liest tools/sticker/<Kürzel>.json, schneidet die Schriftzüge aus dem Seitenfoto des echten Autos und schreibt
liveries/<Kürzel>.png (2048 x 1024: oben linke Fahrzeugseite mit Nase links, unten rechte Seite mit Nase rechts).
Danach wird liveries/liveries.json aus ALLEN vorhandenen Beschreibungen neu geschrieben (das liest das Spiel).
Eine Vorschau auf dunklem bzw. hellem Grund landet in tools/sticker/.cache/<Kürzel>_bogen.png.

Beschreibung (JSON):
  kind      "f1" | "f2"
  photo     Adresse oder Pfad des Seitenfotos (wird in tools/sticker/.cache/<Kürzel>.png abgelegt)
  rear, front   [x, y] der Radmitten im Foto (Pixel des Originalbilds) - daraus entsteht die Umrechnung Foto -> Modell
  stickers  Liste: { name, box [x0,y0,x1,y1] im Foto, kind "w" helle Schrift -> weiß | "d" dunkle Schrift -> schwarz | "c" Farben behalten,
                          "key" Farbfläche: alles im Ausschnitt, was der Farbe "key" ähnelt, wird eine glatte Fläche in dieser Farbe
                          (für die großen farbigen Streifen und Flächen der Lackierung; "tol" = Toleranz, Standard 28 Grad Farbton bzw. 60 bei Grau/Weiß/Schwarz),
                     color "#rrggbb" (w/d/key: andere Farbe), at [z, y] Mitte am Modell in Metern (sonst aus dem Foto umgerechnet),
                     w Breite und h Höhe in Metern (sonst aus dem Foto; nur w -> Seitenverhältnis bleibt), dz/dy Verschiebung in Metern,
                     side "both" | "L" | "R", thr [lo, hi] Schwellen 0..1,
                     mask [[x0,y0,x1,y1], ...]: nur diese Teilkästen innerhalb von box verwenden (schräge Schrift),
                     smooth r: Farbfläche glätten (Rundung r in Foto-Pixeln, etwa 6 … 14) – Lücken, Fransen und Inseln weg, Rand als glatte Kurve;
                     holes false: Löcher (Schrift in der Fläche) offen lassen; grow n: Fläche um n Foto-Pixel vergrößern (unter die Nachbarfläche, gegen dunkle Fugen),
                     poly [[x,y], ...]: Vieleck in Foto-Pixeln begrenzt die Fläche; mit fill true ist das Vieleck selbst die Fläche in "color"
                       (für Farbflächen mit geraden oder schrägen Kanten – sauberer als jeder Fotoausschnitt; box darf dann fehlen),
                     mirror true/false: auf der anderen Fahrzeugseite spiegelverkehrt auftragen (Standard: true bei "key", sonst false) }
            Reihenfolge = Schichtung: zuerst die großen Farbflächen, danach die Schriftzüge.
  number    Startnummer (Grafik im Design des Fahrers, kommt je Fahrer aus liveries/num/): { "color": "#rrggbb",
              "spots": [ { "v": "side", "z": -1.5, "y": 0.8, "s": 0.16 }, { "v": "top", "x": 0, "z": 1.9, "s": 0.12 } ] }   s = Ziffernhöhe in Metern; x0/x1 = Tiefenbereich
            Die Nummer aus dem Foto NICHT als Aufkleber ausschneiden (beide Autos eines Teams teilen sich den Bogen).
  zones     [[z von, z bis, |x| von, |x| bis], ...]   nur diese Tiefe bekleben (gegen doppelte Schriftzüge)
  logoFile, logos   Teamlogo aus logos/<logoFile>.png, z. B. [{ "v": "top", "x": 0, "z": 1.5, "s": 0.2 }]
  team, driver   nur F2: Team (z. B. "F2_INV") und Fahrerkürzel fürs Testbild; drivers = Fahrerkürzel, die diese Lackierung im Spiel bekommen
  liv       F2-Farben: { "body": "#rrggbb", "acc": ..., "tip": ..., "low": ..., "split": 0.3, "metal": 0.3 }
  glsl      eigenes Lack-Programm (Rumpf von vec3 livery(vec3 p, float c)), Farben als #rrggbb
"""
import sys, os, json, glob, subprocess
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); CACHE = os.path.join(HERE, '.cache')
BOX = {'f1': (-2.45, 3.15, 0.0, 1.12), 'f2': (-2.6, 3.0, 0.0, 1.2)}          # muss zu SHEET_BOX in index.html passen
WHEEL = {'f1': (-1.575, 1.825, 0.3595), 'f2': (-1.712, 1.4335, 0.297)}       # z Hinterachse, z Vorderachse, Höhe der Radmitte im Modell
W, HH = 2048, 512

def photo(key, cfg):
    os.makedirs(CACHE, exist_ok=True); dst = os.path.join(CACHE, key + '.png'); src = cfg['photo']
    if not os.path.exists(dst):
        if src.startswith('http'):
            subprocess.run(['curl', '-sS', '-f', '-L', '-m', '90', '-A', 'Mozilla/5.0', '-o', dst + '.tmp', src], check=True)
            Image.open(dst + '.tmp').convert('RGBA').save(dst); os.remove(dst + '.tmp')
        else:
            Image.open(os.path.join(ROOT, src)).convert('RGBA').save(dst)
    return Image.open(dst).convert('RGBA')

def hexrgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

def cut(img, st):
    x0, y0, x1, y1 = [int(round(v)) for v in st['box']]
    a = np.asarray(img.crop((x0, y0, x1, y1)).convert('RGB')).astype(np.float32); kind = st.get('kind', 'w'); lo_f, hi_f = st.get('thr', [0.45, 0.85])
    def auto(v):                                   # Schwellen aus dem Ausschnitt selbst: Untergrund -> 0, Schrift -> 1
        lo, hi = np.percentile(v, 30), np.percentile(v, 99.5)
        return np.clip((v - (lo + lo_f * (hi - lo))) / ((hi_f - lo_f) * (hi - lo) + 1e-3), 0, 1)
    if kind == 'd':
        al = auto(255 - a.max(2)); rgb = np.empty_like(a); rgb[:] = hexrgb(st.get('color', '#101010'))
    elif kind == 'w':
        al = auto(a.min(2)); rgb = np.empty_like(a); rgb[:] = hexrgb(st.get('color', '#ffffff'))
    elif kind == 'key':                            # Farbfläche: Ähnlichkeit zur Schlüsselfarbe (bunt: Farbton, sonst Abstand im Farbraum)
        key = np.array(hexrgb(st['key']), np.float32); mx, mn = a.max(2), a.min(2); kmx, kmn = key.max(), key.min()
        def hue(r, g, b, mx, mn):
            dlt = np.maximum(mx - mn, 1e-3)
            return np.where(mx == r, ((g - b) / dlt) % 6, np.where(mx == g, (b - r) / dlt + 2, (r - g) / dlt + 4)) * 60
        if (kmx - kmn) / max(kmx, 1) > 0.25:
            tol = st.get('tol', 28); hk = float(hue(key[0], key[1], key[2], kmx, kmn)); dh = np.abs((hue(a[..., 0], a[..., 1], a[..., 2], mx, mn) - hk + 180) % 360 - 180)
            sat = (mx - mn) / np.maximum(mx, 1); al = np.clip((tol - dh) / (tol * 0.3), 0, 1) * np.clip((sat - 0.22) / 0.15, 0, 1) * np.clip((mx - 35) / 30, 0, 1)
        else:
            tol = st.get('tol', 60); dd = np.sqrt(((a - key) ** 2).sum(2)); al = np.clip((tol - dd) / (tol * 0.3), 0, 1)
        rgb = np.empty_like(a); rgb[:] = hexrgb(st.get('color', st['key']))
        if st.get('smooth'): al = smooth(al, st['smooth'], st.get('holes', True), st.get('grow', 0))
    else:                                          # Farben behalten: Abstand zur Randfarbe des Ausschnitts
        edge = np.concatenate([a[:2].reshape(-1, 3), a[-2:].reshape(-1, 3), a[:, :2].reshape(-1, 3), a[:, -2:].reshape(-1, 3)])
        bg = np.median(edge, axis=0); al = auto(np.abs(a - bg).max(2))
        rgb = np.clip((a - bg * (1 - al[..., None])) / np.maximum(al[..., None], 0.08), 0, 255)
    if st.get('poly'):                              # Vieleck (Foto-Pixel): Fläche sauber begrenzen; mit "fill": true ist es die Fläche selbst (wie gezeichnet)
        from PIL import ImageDraw
        k = 4; pm = Image.new('L', ((x1 - x0) * k, (y1 - y0) * k), 0)
        ImageDraw.Draw(pm).polygon([((px - x0) * k, (py - y0) * k) for px, py in st['poly']], fill=255)
        pm = np.asarray(pm.resize((x1 - x0, y1 - y0), Image.LANCZOS)).astype(np.float32) / 255
        al = pm if st.get('fill') else al * pm
        if kind != 'key' and st.get('fill'): rgb = np.empty_like(a); rgb[:] = hexrgb(st.get('color', '#ffffff'))
    if st.get('mask'):                              # nur diese Teilkästen des Ausschnitts gelten (für schräg laufende Schrift, die kein gerader Kasten knapp umschließt)
        keep = np.zeros(al.shape, bool)
        for mx0, my0, mx1, my1 in st['mask']: keep[max(0, int(my0) - y0):max(0, int(my1) - y0), max(0, int(mx0) - x0):max(0, int(mx1) - x0)] = True
        al = al * keep
    return Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA')

def smooth(al, r, holes=True, grow=0):
    """Farbfläche glätten (wie gezeichnete Kurven statt Fotoausschnitt): Lücken durch Schatten, Spiegelungen und Schrift schließen,
    Fransen und Inseln entfernen, Rand rund ziehen. r = Rundung in Foto-Pixeln (etwa 4 … 15)."""
    from scipy import ndimage as nd
    r = max(1, int(r)); p = 3 * r
    m = np.pad(al > 0.5, p, mode='edge')
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; disk = xx * xx + yy * yy <= r * r
    m = nd.binary_closing(m, disk)
    if holes: m = nd.binary_fill_holes(m)
    q = max(1, r // 2); yq, xq = np.mgrid[-q:q + 1, -q:q + 1]; m = nd.binary_opening(m, xq * xq + yq * yq <= q * q)   # schmale Linien bleiben
    lab, n = nd.label(m)
    if n > 1:                                      # kleine Inseln (Spiegelungen, Reste) weg
        size = nd.sum(m, lab, range(1, n + 1)); m = np.isin(lab, 1 + np.flatnonzero(size >= max(size.max() * 0.04, 4 * r * r)))
    if grow: m = nd.binary_dilation(m, iterations=int(grow))   # unter die Nachbarfläche schieben: keine dunkle Fuge zwischen zwei Farben
    s = nd.gaussian_filter(m.astype(np.float32), r * 0.5)
    return np.clip((s - 0.5) * 6.0 + 0.5, 0, 1)[p:-p, p:-p]

def bleed(sheet, rounds=12):
    """Farbe der Aufkleber in die durchsichtige Umgebung ziehen (Deckkraft bleibt 0): sonst mischt die Grafikkarte am Rand Weiß hinein -> heller Saum."""
    a = np.asarray(sheet).astype(np.float32); rgb, al = a[..., :3].copy(), a[..., 3]; have = al > 0
    for _ in range(rounds):
        acc = np.zeros_like(rgb); cnt = np.zeros(al.shape, np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            h = np.roll(have, (dy, dx), (0, 1)); acc += np.roll(rgb, (dy, dx), (0, 1)) * h[..., None]; cnt += h
        new = (~have) & (cnt > 0); rgb[new] = acc[new] / cnt[new][:, None]; have = have | new
    return Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), 'RGBA')

def boxof(st):
    if 'box' not in st and st.get('poly'):
        xs, ys = [p[0] for p in st['poly']], [p[1] for p in st['poly']]; st['box'] = [min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2]
    return st

def build(key):
    cfg = json.load(open(os.path.join(HERE, key + '.json'), encoding='utf-8')); kind = cfg['kind']
    Z0, Z1, Y0, Y1 = BOX[kind]; zr, zf, wy = WHEEL[kind]
    sheet = Image.new('RGBA', (W, HH * 2), (255, 255, 255, 0))
    if cfg.get('stickers'):
        img = photo(key, cfg); (rx, ry), (fx, fy) = cfg['rear'], cfg['front']
        sc = abs(fx - rx) / (zf - zr); d = 1 if fx > rx else -1; cyp = (ry + fy) / 2          # Pixel je Meter, Fahrtrichtung im Foto
        pxm_x, pxm_y = W / (Z1 - Z0), HH / (Y1 - Y0)
        for st in cfg['stickers']:
            st = boxof(st); x0, y0, x1, y1 = st['box']; p = cut(img, st)
            cz = zr + ((x0 + x1) / 2 - rx) * d / sc; cy = wy + (cyp - (y0 + y1) / 2) / sc
            if 'at' in st: cz, cy = st['at']
            cz += st.get('dz', 0); cy += st.get('dy', 0); wm = st.get('w', (x1 - x0) / sc)
            hm = st.get('h', wm * p.height / p.width); w = max(1, round(wm * pxm_x)); h = max(1, round(hm * pxm_y)); p = p.resize((w, h), Image.LANCZOS)
            yy = round((Y1 - cy) * pxm_y - h / 2); side = st.get('side', 'both')
            # Formen (Farbflächen) laufen auf der anderen Fahrzeugseite spiegelverkehrt, Schrift nicht: "mirror" (Standard: nur bei kind "key")
            mir = st.get('mirror', st.get('kind') == 'key'); pm = p.transpose(Image.FLIP_LEFT_RIGHT) if mir else p
            pl, pr = (pm, p) if d > 0 else (p, pm)                                         # Foto mit Nase rechts zeigt die rechte Seite, mit Nase links die linke
            if side in ('both', 'L'): sheet.alpha_composite(pl, (max(0, round((Z1 - cz) * pxm_x - w / 2)), max(0, yy)))
            if side in ('both', 'R'): sheet.alpha_composite(pr, (max(0, round((cz - Z0) * pxm_x - w / 2)), max(0, HH + yy)))
            print('  %-14s z %.2f  y %.2f  Breite %.2f m' % (st.get('name', '?'), cz, cy, wm))
        sheet = bleed(sheet)
        os.makedirs(os.path.join(ROOT, 'liveries'), exist_ok=True); sheet.save(os.path.join(ROOT, 'liveries', key + '.png'), optimize=True)
        bg = Image.new('RGB', sheet.size, tuple(hexrgb(cfg.get('previewBg', '#24262c')))); bg.paste(sheet, (0, 0), sheet); bg.save(os.path.join(CACHE, key + '_bogen.png'))
    print('ok', key)

def manifest():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, '*.json'))):
        key = os.path.basename(f)[:-5]
        try: cfg = json.load(open(f, encoding='utf-8'))
        except Exception as e: print('!! übersprungen', key, e); continue
        m = {'kind': cfg['kind']}
        if cfg.get('stickers') and os.path.exists(os.path.join(ROOT, 'liveries', key + '.png')): m['sheet'] = True
        if cfg.get('zones'): m['zones'] = cfg['zones']
        if cfg.get('logos') and cfg.get('logoFile'): m['logoFile'] = cfg['logoFile']; m['logos'] = cfg['logos']
        if cfg.get('number') and cfg['number'].get('spots'): m['num'] = {'color': cfg['number'].get('color', '#ffffff'), 'list': cfg['number']['spots']}
        if cfg.get('drivers'): m['drivers'] = cfg['drivers']
        if cfg.get('liv'): m['liv'] = {k: (int(v.lstrip('#'), 16) if isinstance(v, str) else v) for k, v in cfg['liv'].items()}
        if cfg.get('glsl'): m['glsl'] = cfg['glsl'] if isinstance(cfg['glsl'], str) else '\n'.join(cfg['glsl'])
        out[key] = m
    out['_num'] = sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(ROOT, 'liveries', 'num', '*.png')))
    dst = os.path.join(ROOT, 'liveries', 'liveries.json'); tmp = dst + '.%d.tmp' % os.getpid()
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); os.replace(tmp, dst)

if __name__ == '__main__':
    keys = sys.argv[1:]
    if keys == ['all']: keys = sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(HERE, '*.json')))
    for k in keys: build(k)
    manifest()
