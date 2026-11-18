"""Team-Logos der Klassiker aus der jeweiligen Zeit: logos/H_LOT.png, H_MCL.png, H_FER.png (512 × 512 px, transparent).

- H_LOT (1970): Lotus-Plakette – gelber Kreis, Dreieck in British Racing Green, „LOTUS“ und ACBC-Monogramm (Colin Chapman).
  Vorlage: Vektorgrafik der Lotus-Plakette von Wikipedia (tools/klassiker/quellen/lotus_cars_logo.svg, heutige Fassung in Schwarz);
  das Schwarz wird auf das Grün der klassischen Plakette (1970) umgefärbt – Aufbau und Farben wie auf der Nase des 49C.
- H_MCL (1988): Schriftzug „McLaren INTERNATIONAL“ (Teamlogo 1981–1990er), ausgeschnitten aus der Sponsoren-Textur des Modells
  (modelle/klassiker/mclaren_mp44.glb), Buchstaben weiß auf transparent wie die übrigen Logos im Menü.
- H_FER (2004): Scuderia-Ferrari-Schild (gelb, schwarzes Pferd, S F, Trikolore), ausgeschnitten aus der Sponsoren-Textur des F2004-Modells.

Aufruf: python tools/klassiker/logos.py   (braucht numpy, scipy, pillow, cairosvg)
"""
import io, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbio import read_glb, image_bytes   # noqa: E402


def tex(key, name):
    js, bn = read_glb(os.path.join(ROOT, 'modelle', 'klassiker', key + '.glb'))
    i = next(k for k, im in enumerate(js['images']) if im.get('name', '').startswith(name))
    return Image.open(io.BytesIO(image_bytes(js, bn, i))).convert('RGB')


def save(im, key, size=470):
    bb = im.getbbox(); im = im.crop(bb); w, h = im.size; s = size / max(w, h)
    im = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    out = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); out.alpha_composite(im, ((512 - im.width) // 2, (512 - im.height) // 2))
    out.save(os.path.join(ROOT, 'logos', key + '.png')); print('logos/' + key + '.png', im.size)


# Lotus 1970: Plakette mit grünem Dreieck
import cairosvg   # noqa: E402
svg = open(os.path.join(ROOT, 'tools', 'klassiker', 'quellen', 'lotus_cars_logo.svg'), encoding='utf-8').read().replace('fill="black"', 'fill="#0b5a36"')
save(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=1024, output_height=1024))).convert('RGBA'), 'H_LOT')

# McLaren 1988: Schriftzug „McLaren INTERNATIONAL“ (schwarz auf weißem Schild in der Textur) -> weiße Schrift, 8-fach hochgerechnet und weich freigestellt
src = tex('mclaren_mp44', 'Material__1').crop((104, 425, 215, 450))   # nur die Innenfläche des Schildes (ohne Rahmenlinien)
up = src.resize((src.width * 8, src.height * 8), Image.BICUBIC).filter(__import__('PIL.ImageFilter', fromlist=['x']).GaussianBlur(2.2))
L = np.asarray(up.convert('L')).astype(np.float32)
a = np.clip((150 - L) / 60, 0, 1)   # dunkle Buchstaben -> deckend, weiche Kante statt Pixeltreppe
im = np.zeros(L.shape + (4,), np.uint8); im[..., :3] = 246; im[..., 3] = (a * 255).astype(np.uint8)
save(Image.fromarray(im, 'RGBA'), 'H_MCL', size=490)

# Ferrari 2004: Schild aus der Textur (schwarzer Hintergrund -> transparent, das danebenliegende Vodafone-Logo bleibt draußen)
src = tex('ferrari_f2004', 'EXT_Sponsors').crop((800, 0, 1020, 290)); up = src.resize((src.width * 3, src.height * 3), Image.LANCZOS)
A = np.asarray(up).astype(np.float32); lum = A.max(2)
lab, n = ndimage.label(lum > 45); h, w = lum.shape
yel = (A[..., 0] > 140) & (A[..., 1] > 120) & (A[..., 2] < 90)   # gelbe Schildfläche
keep = (set(np.unique(lab[yel])) | {lab[int(h * 0.12), w // 2]}) - {0}   # Schildfläche und Trikolore oben
m = ndimage.binary_fill_holes(np.isin(lab, list(keep)))
m = ndimage.binary_dilation(m, iterations=4)   # schwarzen Rand des Schildes mitnehmen
alpha = ndimage.gaussian_filter(m.astype(np.float32), 1.2)
# lebendiger (Wunsch v2.69): die Textur ist matt/olivgelb -> Gelb auf Ferrari-Gelb ziehen, Sättigung und Helligkeit anheben
from PIL import ImageEnhance
rgb = Image.fromarray(A.clip(0, 255).astype(np.uint8)); rgb = ImageEnhance.Color(rgb).enhance(1.7); rgb = ImageEnhance.Brightness(rgb).enhance(1.18); rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
B = np.asarray(rgb).astype(np.float32); yl = np.clip(((B[..., 0] + B[..., 1]) / 2 - B[..., 2] - 30) / 60, 0, 1)   # Anteil „gelb“
lumY = B.mean(2); med = np.median(lumY[yl > 0.6]) if (yl > 0.6).any() else 150.0
shade = (lumY / med).clip(0.55, 1.12)[..., None]   # Schattierung des Schildes behalten, Farbe = sattes Ferrari-Gelb
B = B * (1 - yl[..., None]) + np.array([255, 214, 0], np.float32) * shade * yl[..., None]
im = np.dstack([B.clip(0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
save(Image.fromarray(im, 'RGBA'), 'H_FER')
