#!/usr/bin/env python3
"""Seitenfoto zum Vermessen aufbereiten:  python3 tools/sticker/photo.py <Kürzel> [Adresse oder Pfad]

Legt das Foto in tools/sticker/.cache/<Kürzel>.png ab (Adresse aus tools/sticker/<Kürzel>.json, falls nicht angegeben) und schreibt
  <Kürzel>_ganz.png     Übersicht (auf 1600 px Breite verkleinert) mit Raster
  <Kürzel>_teil<N>.png  Ausschnitte in Originalgröße (je 1100 px breit, überlappend) mit Pixelraster alle 50 px, beschriftet alle 100 px
Die Zahlen am Raster sind Pixel des Originalbilds - genau diese Werte gehören in "box", "rear" und "front".
Mit  --zoom x0 y0 x1 y1  entsteht zusätzlich <Kürzel>_zoom.png: dieser Bereich dreifach vergrößert mit Raster alle 10 px.
"""
import sys, os, json, subprocess
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, '.cache'); ROOT = os.path.dirname(os.path.dirname(HERE))

def grid(im, ox, oy, step, lab, k=1):
    d = ImageDraw.Draw(im, 'RGBA'); W, H = im.size
    x = (ox // step + 1) * step
    while (x - ox) * k < W:
        X = (x - ox) * k; big = x % lab == 0; d.line([(X, 0), (X, H)], fill=(255, 255, 0, 110 if big else 40))
        if big: d.text((X + 2, 2), str(x), fill=(255, 255, 0, 255)); d.text((X + 2, H - 12), str(x), fill=(255, 255, 0, 255))
        x += step
    y = (oy // step + 1) * step
    while (y - oy) * k < H:
        Y = (y - oy) * k; big = y % lab == 0; d.line([(0, Y), (W, Y)], fill=(0, 255, 255, 110 if big else 40))
        if big: d.text((2, Y + 1), str(y), fill=(0, 255, 255, 255)); d.text((W - 30, Y + 1), str(y), fill=(0, 255, 255, 255))
        y += step
    return im

def main():
    a = sys.argv[1:]; zoom = None
    if '--zoom' in a: i = a.index('--zoom'); zoom = [int(v) for v in a[i + 1:i + 5]]; a = a[:i]
    key = a[0]; os.makedirs(CACHE, exist_ok=True); dst = os.path.join(CACHE, key + '.png')
    src = a[1] if len(a) > 1 else None
    if src or not os.path.exists(dst):
        if not src: src = json.load(open(os.path.join(HERE, key + '.json'), encoding='utf-8'))['photo']
        if src.startswith('http'):
            subprocess.run(['curl', '-sS', '-f', '-L', '-m', '90', '-A', 'Mozilla/5.0', '-o', dst + '.tmp', src], check=True); Image.open(dst + '.tmp').convert('RGBA').save(dst); os.remove(dst + '.tmp')
        else: Image.open(src if os.path.isabs(src) else os.path.join(ROOT, src)).convert('RGBA').save(dst)
    im = Image.open(dst).convert('RGBA'); bg = Image.new('RGBA', im.size, (120, 120, 132, 255)); bg.alpha_composite(im); im = bg.convert('RGB'); W, H = im.size
    print('Foto', dst, W, 'x', H)
    if zoom:
        x0, y0, x1, y1 = zoom; z = im.crop((x0, y0, x1, y1)).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.LANCZOS); grid(z, x0, y0, 10, 50, 3).save(os.path.join(CACHE, key + '_zoom.png')); print('->', os.path.join(CACHE, key + '_zoom.png')); return
    k = 1600 / W; ov = im.resize((1600, round(H * k)), Image.LANCZOS); d = ImageDraw.Draw(ov, 'RGBA')
    for x in range(0, W, 200): d.line([(x * k, 0), (x * k, ov.height)], fill=(255, 255, 0, 90)); d.text((x * k + 2, 2), str(x), fill=(255, 255, 0, 255))
    for y in range(0, H, 100): d.line([(0, y * k), (1600, y * k)], fill=(0, 255, 255, 90)); d.text((2, y * k + 1), str(y), fill=(0, 255, 255, 255))
    ov.save(os.path.join(CACHE, key + '_ganz.png')); print('->', os.path.join(CACHE, key + '_ganz.png'))
    n = 0; x = 0
    while x < W:
        t = im.crop((x, 0, min(W, x + 1100), H)); grid(t, x, 0, 50, 100).save(os.path.join(CACHE, '%s_teil%d.png' % (key, n))); print('->', os.path.join(CACHE, '%s_teil%d.png' % (key, n)), 'x', x, '..', min(W, x + 1100)); n += 1; x += 1000

main()
