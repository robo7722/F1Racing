"""Team-Logos der Klassiker aus der jeweiligen Zeit: logos/H_LOT.png, H_MCL.png, H_FER.png, H_F67.png, H_MCL98.png, H_RBR.png (512 × 512 px, transparent).

- H_LOT (1970): Lotus-Plakette – gelber Kreis, Dreieck in British Racing Green, „LOTUS“ und ACBC-Monogramm (Colin Chapman).
  Vorlage: Vektorgrafik der Lotus-Plakette von Wikipedia (tools/klassiker/quellen/lotus_cars_logo.svg, heutige Fassung in Schwarz);
  das Schwarz wird auf das Grün der klassischen Plakette (1970) umgefärbt – Aufbau und Farben wie auf der Nase des 49C.
- H_MCL (1988): Schriftzug „McLaren INTERNATIONAL“ (Teamlogo 1981–1990er), ausgeschnitten aus der Sponsoren-Textur des Modells
  (modelle/klassiker/mclaren_mp44.glb), Buchstaben weiß auf transparent wie die übrigen Logos im Menü.
- H_FER (2004): Scuderia-Ferrari-Schild (gelb, schwarzes Pferd, S F, Trikolore), ausgeschnitten aus der Sponsoren-Textur des F2004-Modells.
- H_F67 (1967): dasselbe Scuderia-Schild (die Form ist seit den 1930ern praktisch gleich; das 312-Modell trägt kein Schild in der Textur),
  aber im wärmeren, etwas matteren Gelb der damaligen Drucke.
- H_MCL98 (1998): „McLaren-Mercedes“ der Jahre 1997–2001 – Mercedes-Stern (aus der Textur des MP4/13-Modells, Nase) über dem Schriftzug
  „McLaren“ mit dem roten Speedmark-Bogen (ab 1997 im Teamlogo). Schrift und Bogen gezeichnet (Schrift: Inter/FreeSans Bold, falls vorhanden).
- H_RBR (2012): Red-Bull-Logo (zwei Stiere, gelbe Sonne, Schriftzug „Red Bull“) aus der Textur des RB8-Modells (Motorabdeckung/Nase),
  dunkelblauer Lack freigestellt.

Aufruf: python tools/klassiker/logos.py [H_LOT H_MCL ...]   (ohne Angabe alle; braucht numpy, scipy, pillow – H_LOT zusätzlich cairosvg)
"""
import io, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
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


def font(sz):
    for f in ['/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf', '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'arialbd.ttf']:
        try: return ImageFont.truetype(f, sz)
        except OSError: pass
    return ImageFont.load_default()


def lotus():   # Lotus 1970: Plakette mit grünem Dreieck
    import cairosvg
    svg = open(os.path.join(ROOT, 'tools', 'klassiker', 'quellen', 'lotus_cars_logo.svg'), encoding='utf-8').read().replace('fill="black"', 'fill="#0b5a36"')
    save(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=1024, output_height=1024))).convert('RGBA'), 'H_LOT')


def mclaren88():   # McLaren 1988: Schriftzug „McLaren INTERNATIONAL“ (schwarz auf weißem Schild in der Textur) -> weiße Schrift, 8-fach hochgerechnet und weich freigestellt
    src = tex('mclaren_mp44', 'Material__1').crop((104, 425, 215, 450))   # nur die Innenfläche des Schildes (ohne Rahmenlinien)
    up = src.resize((src.width * 8, src.height * 8), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2.2))
    L = np.asarray(up.convert('L')).astype(np.float32)
    a = np.clip((150 - L) / 60, 0, 1)   # dunkle Buchstaben -> deckend, weiche Kante statt Pixeltreppe
    im = np.zeros(L.shape + (4,), np.uint8); im[..., :3] = 246; im[..., 3] = (a * 255).astype(np.uint8)
    save(Image.fromarray(im, 'RGBA'), 'H_MCL', size=490)


def ferrari_shield(gelb=(255, 214, 0), color=1.7, bright=1.18):
    """Schild aus der F2004-Textur (schwarzer Hintergrund -> transparent, das danebenliegende Vodafone-Logo bleibt draußen)"""
    src = tex('ferrari_f2004', 'EXT_Sponsors').crop((800, 0, 1020, 290)); up = src.resize((src.width * 3, src.height * 3), Image.LANCZOS)
    A = np.asarray(up).astype(np.float32); lum = A.max(2)
    lab, n = ndimage.label(lum > 45); h, w = lum.shape
    yel = (A[..., 0] > 140) & (A[..., 1] > 120) & (A[..., 2] < 90)   # gelbe Schildfläche
    keep = (set(np.unique(lab[yel])) | {lab[int(h * 0.12), w // 2]}) - {0}   # Schildfläche und Trikolore oben
    m = ndimage.binary_fill_holes(np.isin(lab, list(keep)))
    m = ndimage.binary_dilation(m, iterations=4)   # schwarzen Rand des Schildes mitnehmen
    alpha = ndimage.gaussian_filter(m.astype(np.float32), 1.2)
    # lebendiger (Wunsch v2.69): die Textur ist matt/olivgelb -> Gelb auf Ferrari-Gelb ziehen, Sättigung und Helligkeit anheben
    rgb = Image.fromarray(A.clip(0, 255).astype(np.uint8)); rgb = ImageEnhance.Color(rgb).enhance(color); rgb = ImageEnhance.Brightness(rgb).enhance(bright); rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
    B = np.asarray(rgb).astype(np.float32); yl = np.clip(((B[..., 0] + B[..., 1]) / 2 - B[..., 2] - 30) / 60, 0, 1)   # Anteil „gelb“
    lumY = B.mean(2); med = np.median(lumY[yl > 0.6]) if (yl > 0.6).any() else 150.0
    shade = (lumY / med).clip(0.55, 1.12)[..., None]   # Schattierung des Schildes behalten, Farbe = sattes Ferrari-Gelb
    B = B * (1 - yl[..., None]) + np.array(gelb, np.float32) * shade * yl[..., None]
    return Image.fromarray(np.dstack([B.clip(0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)]), 'RGBA')


def ferrari04(): save(ferrari_shield(), 'H_FER')


def ferrari67(): save(ferrari_shield(gelb=(244, 196, 40), color=1.4, bright=1.1), 'H_F67')   # 1967: wärmeres, matteres Gelb


def mclaren98():
    """McLaren-Mercedes 1998: Mercedes-Stern (Nase in der MP4/13-Textur, dort auf dem Kopf) über „McLaren“ mit rotem Speedmark"""
    src = tex('mclaren_mp413', 'Material_001').crop((487, 418, 529, 460)).rotate(180)   # Stern im Ring, dunkel auf silbernem Grund
    up = src.resize((src.width * 10, src.height * 10), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
    L = np.asarray(up.convert('L')).astype(np.float32); h, w = L.shape
    yy, xx = np.mgrid[0:h, 0:w]; rr = np.hypot(xx - w / 2, yy - h / 2) / (w / 2)
    a = np.clip((150 - L) / 50, 0, 1) * (rr < 0.97)   # dunkle Linien des Sterns -> deckend, Rand außerhalb des Rings weg
    star = np.zeros((h, w, 4), np.uint8); star[..., :3] = 236; star[..., 3] = (a * 255).astype(np.uint8)
    star = Image.fromarray(star, 'RGBA')
    W, H = 1400, 900; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    st = star.resize((360, 360), Image.LANCZOS); im.alpha_composite(st, ((W - 360) // 2, 20))
    f = font(250); t = 'McLaren'; bb = d.textbbox((0, 0), t, font=f); tw = bb[2] - bb[0]
    x0 = (W - tw) // 2 - 40; d.text((x0, 430), t, font=f, fill=(244, 244, 244, 255))
    # Speedmark: roter, nach rechts auslaufender Bogen über dem Ende des Schriftzugs (wie im Logo ab 1997)
    sm = Image.new('L', (W * 2, H * 2), 0); ds = ImageDraw.Draw(sm); cx, cy = (x0 + tw - 60) * 2, 560 * 2   # Mondsichel: äußerer minus versetzter innerer Kreis
    ds.ellipse([cx - 300, cy - 260, cx + 300, cy + 260], fill=255); ds.ellipse([cx - 330, cy - 200, cx + 250, cy + 320], fill=0)
    ds.rectangle([0, cy - 40, W * 2, H * 2], fill=0)   # nur der obere Bogen
    sm = sm.resize((W, H), Image.LANCZOS); red = Image.new('RGBA', (W, H), (226, 12, 20, 255)); red.putalpha(sm); im.alpha_composite(red)
    save(im, 'H_MCL98', size=480)


def redbull12():
    """Red Bull 2012: Stiere mit Sonne (Nase) bzw. Stiere + Schriftzug (Motorabdeckung) aus der RB8-Textur, Lack (dunkelblau) freigestellt"""
    T = tex('redbull_rb8', 'wccarbody_001')
    bulls = T.crop((278, 676, 462, 714)); text = T.crop((276, 722, 464, 770))
    def cut(im, sc=5):
        up = im.resize((im.width * sc, im.height * sc), Image.LANCZOS); A = np.asarray(up).astype(np.float32)
        a = np.clip((A.max(2) - 95) / 45, 0, 1); a = ndimage.gaussian_filter(a, 0.8)   # Lack (dunkelblau, max. Kanal < ~90) -> durchsichtig; Rot, Gelb, Weiß bleiben
        return Image.fromarray(np.dstack([A.clip(0, 255).astype(np.uint8), (a * 255).astype(np.uint8)]), 'RGBA')
    b, t = cut(bulls), cut(text); W = max(b.width, t.width); im = Image.new('RGBA', (W, b.height + t.height + 20), (0, 0, 0, 0))
    im.alpha_composite(b, ((W - b.width) // 2, 0)); im.alpha_composite(t, ((W - t.width) // 2, b.height + 20))
    save(im, 'H_RBR', size=490)


JOBS = {'H_LOT': lotus, 'H_MCL': mclaren88, 'H_FER': ferrari04, 'H_F67': ferrari67, 'H_MCL98': mclaren98, 'H_RBR': redbull12}
if __name__ == '__main__':
    for k in (sys.argv[1:] or list(JOBS)): JOBS[k]()
