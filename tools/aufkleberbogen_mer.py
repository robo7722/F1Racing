"""Baut liveries/MER.png: Aufkleberbogen (Sponsoren) für den Mercedes aus dem offiziellen Seitenbild.

Aufruf:  python3 tools/aufkleberbogen_mer.py <Seitenbild.png> liveries/MER.png [Kontrollbild.png]
Seitenbild: https://media.formula1.com/image/upload/v1740000001/common/f1/2026/mercedes/2026mercedescarright.png (3840 px breit, Nase rechts)

Der Bogen zeigt das Auto von der Seite in Modellkoordinaten (z = Länge, y = Höhe):
  obere Hälfte  = linke Fahrzeugseite (+x), Nase links
  untere Hälfte = rechte Fahrzeugseite (-x), Nase rechts
Der Bereich (Z0..Z1, Y0..Y1) muss zu SHEETS.MER in index.html passen.
"""
import sys
import numpy as np
from PIL import Image

Z0, Z1, Y0, Y1 = -2.45, 3.15, 0.0, 1.12
W, HH = 4096, 512                      # je Seite
K = 3787 / 2368                        # die Kästen unten sind am 2400-px-Bild vermessen
OX = 27

# Name: (Kasten im Bild x0,y0,x1,y1 | Art | Schwellen t0,t1 | Mitte z,y am Modell | Breite in m)
#   Art 'w' = helle Schrift, wird rein weiß | 'c' = Farben behalten | 'd' = dunkle Schrift auf hell, wird weiß
ST = {
    'snapdragon':   ((8, 98, 256, 158),     'w', (70, 150), (-2.06, 0.86), 0.42),
    'crowdstrike':  ((38, 181, 220, 210),   'w', (70, 150), (-2.06, 0.71), 0.32),
    'microsoft':    ((888, 62, 1078, 110),  'c', (60, 130), (-0.36, 0.90), 0.36),
    'solera':       ((822, 120, 964, 148),  'w', (80, 160), (-0.62, 0.80), 0.27),
    'teamviewer':   ((894, 177, 1150, 225), 'w', (80, 160), (-0.34, 0.72), 0.44),
    'petronas':     ((792, 302, 1228, 362), 'w', (120, 190), (-0.12, 0.37), 0.86),
    'signify':      ((1362, 358, 1540, 414), 'w', (130, 200), (0.83, 0.28), 0.36),
    'amg':          ((1532, 285, 1688, 305), 'd', (60, 120), (1.17, 0.47), 0.33),
    'iwc':          ((2108, 352, 2200, 396), 'w', (130, 200), (2.27, 0.27), 0.14),
    'microsoft2':   ((2178, 396, 2336, 440), 'c', (70, 140), (2.50, 0.25), 0.24),
}

def cut(img, box, kind):
    x0, y0, x1, y1 = [int(round(v * K)) for v in box]
    a = np.asarray(img.crop((x0 + OX, y0, x1 + OX, y1)).convert('RGB')).astype(np.float32)
    def auto(v):                                     # Schwellen aus dem Ausschnitt selbst: Untergrund -> 0, Schrift -> 1
        lo, hi = np.percentile(v, 30), np.percentile(v, 99.5)
        return np.clip((v - (lo + 0.45 * (hi - lo))) / (0.4 * (hi - lo) + 1e-3), 0, 1)
    if kind == 'd':
        al = auto(255 - a.max(2)); rgb = np.full_like(a, 255)
    else:
        al = auto(a.min(2)); rgb = np.full_like(a, 255)   # kleinster Farbkanal: nur Weiß zählt, farbige Lackstreifen und graue Spiegelungen fallen weg
        if kind == 'c':
            sat = a.max(2) - a.min(2); ac = np.clip((sat - 90) / 60, 0, 1)
            m = ac > al; rgb[m] = np.clip(a[m] * 1.08, 0, 255); al = np.maximum(al, ac)
    return Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA')

def main():
    src, out = sys.argv[1], sys.argv[2]
    img = Image.open(src).convert('RGBA')
    sheet = Image.new('RGBA', (W, HH * 2), (255, 255, 255, 0))
    pxm_x, pxm_y = W / (Z1 - Z0), HH / (Y1 - Y0)
    for name, (box, kind, th, (cz, cy), wm) in ST.items():
        p = cut(img, box, kind)
        w = max(1, round(wm * pxm_x)); h = max(1, round(wm * p.height / p.width * pxm_y))
        p = p.resize((w, h), Image.LANCZOS)
        yy = round((Y1 - cy) * pxm_y - h / 2)
        xl = round((Z1 - cz) * pxm_x - w / 2)        # linke Seite: Nase links
        xr = round((cz - Z0) * pxm_x - w / 2)        # rechte Seite: Nase rechts
        sheet.alpha_composite(p, (xl, yy)); sheet.alpha_composite(p, (xr, HH + yy))
    sheet.save(out, optimize=True)
    if len(sys.argv) > 3:
        bg = Image.new('RGB', sheet.size, (20, 22, 26)); bg.paste(sheet, (0, 0), sheet); bg.save(sys.argv[3])
    print('ok', out, sheet.size)

main()
