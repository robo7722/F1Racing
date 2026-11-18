"""Eigene Team-Logos der Klassiker (v2.68): logos/H_LOT.png, H_MCL.png, H_FER.png – 512 × 512 px, transparent.

Stil wie die übrigen Logos (helles Emblem für den dunklen Menü-Hintergrund), aber in Creme/Gold als Zeichen für „historisch“.
Eigene Entwürfe, keine Nachbildung der echten Markenzeichen: Lotus = runde Plakette mit „49C“, McLaren = schräger Schriftzug mit
Tempo-Winkel, Ferrari = schlichtes Wappenschild mit Trikolore-Streifen und „F2004“.
Aufruf: python tools/klassiker/logos.py   (braucht pillow)
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = 2048                      # erst groß zeichnen, dann verkleinern (glatte Kanten)
CREAM, GOLD = (246, 236, 210, 255), (217, 180, 90, 255)
FS = '/usr/share/fonts/truetype/freefont/'
def font(name, size):
    for p in (FS + name, '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()
def text_c(d, xy, t, f, fill, anchor='mm'): d.text(xy, t, font=f, fill=fill, anchor=anchor)
def save(im, key):
    bb = im.getbbox(); im = im.crop(bb); w, h = im.size; n = max(w, h); sq = Image.new('RGBA', (n, n), (0, 0, 0, 0)); sq.paste(im, ((n - w) // 2, (n - h) // 2))
    sq = sq.resize((470, 470), Image.LANCZOS); out = Image.new('RGBA', (512, 512), (0, 0, 0, 0)); out.paste(sq, (21, 21)); out.save(os.path.join(ROOT, 'logos', key + '.png')); print('logos/' + key + '.png')

# Lotus 1970: runde Plakette, Doppelring, „49C“ in Serifenschrift, Band mit „LOTUS“, unten „1970“
im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); c = S // 2
d.ellipse([c - 980, c - 980, c + 980, c + 980], outline=GOLD, width=46)
d.ellipse([c - 900, c - 900, c + 900, c + 900], outline=CREAM, width=70)
d.rectangle([c - 905, c - 150, c + 905, c + 150], fill=CREAM)
text_c(d, (c, c + 8), 'LOTUS', font('FreeSansBold.ttf', 300), (0, 0, 0, 0))
text_c(d, (c, c - 450), '49C', font('FreeSerifBoldItalic.ttf', 420), CREAM)
text_c(d, (c, c + 470), '1970', font('FreeSansBold.ttf', 230), GOLD)
for sx in (-1, 1): d.polygon([(c + sx * 560, c + 470), (c + sx * 700, c + 430), (c + sx * 700, c + 510)], fill=GOLD)
save(im, 'H_LOT')

# McLaren 1988: schräger, kräftiger Schriftzug mit zwei Tempo-Balken (eigener Entwurf), darunter „MP4/4 · 1988“
im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); c = S // 2
txt = Image.new('RGBA', (S, S)); t = ImageDraw.Draw(txt)
text_c(t, (c + 60, c - 120), 'McLAREN', font('FreeSansBoldOblique.ttf', 380), CREAM)
im.alpha_composite(txt)
for k, (y, w) in enumerate([(c + 150, 70), (c + 260, 46)]):
    d.polygon([(c - 900 + k * 120, y + w), (c - 840 + k * 120, y), (c + 980, y), (c + 920, y + w)], fill=GOLD if k else CREAM)
text_c(d, (c + 40, c + 520), 'MP4/4 · 1988', font('FreeSansBoldOblique.ttf', 220), GOLD)
save(im, 'H_MCL')

# Ferrari 2004: Wappenschild (schlicht), oben drei Streifen, „F2004“, unten „2004“
im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im); c = S // 2
shield = [(c - 640, c - 860), (c + 640, c - 860), (c + 640, c + 120), (c + 560, c + 470), (c + 300, c + 760), (c, c + 900), (c - 300, c + 760), (c - 560, c + 470), (c - 640, c + 120)]
d.polygon(shield, outline=CREAM, width=60)
for k, colr in enumerate([(22, 140, 70, 255), CREAM, (206, 30, 40, 255)]): d.rectangle([c - 520 + k * 347, c - 760, c - 520 + (k + 1) * 347 - 20, c - 630], fill=colr)
text_c(d, (c, c - 120), 'F2004', font('FreeSansBoldOblique.ttf', 380), CREAM)
d.line([(c - 420, c + 180), (c + 420, c + 180)], fill=GOLD, width=26)
text_c(d, (c, c + 430), '2004', font('FreeSansBold.ttf', 230), GOLD)
save(im, 'H_FER')
