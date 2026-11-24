"""Mehrere Bilder zu einem Übersichtsbogen mit Beschriftung zusammensetzen (für Entwürfe und Vergleiche).

    python tools/wetter/bogen.py aus.jpg --spalten 2 --breite 852 "Titel" bild1.png "Text 1" bild2.png "Text 2" …
"""
import sys
from PIL import Image, ImageDraw, ImageFont


def schrift(px, fett=False):
    for f in (['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if fett else []) + ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        try:
            return ImageFont.truetype(f, px)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    a = sys.argv[1:]
    aus = a.pop(0); spalten = 2; breite = 852
    while a and a[0].startswith('--'):
        k = a.pop(0); v = int(a.pop(0))
        if k == '--spalten': spalten = v
        if k == '--breite': breite = v
    titel = a.pop(0); paare = list(zip(a[0::2], a[1::2]))
    bilder = []
    for f, t in paare:
        im = Image.open(f).convert('RGB'); im = im.resize((breite, round(im.height * breite / im.width)), Image.LANCZOS); bilder.append((im, t))
    rand, kopf, fuss = 18, 54, 34
    h = max(im.height for im, _ in bilder); zeilen = -(-len(bilder) // spalten)
    W = rand + spalten * (breite + rand); H = kopf + zeilen * (h + fuss + rand) + rand
    bogen = Image.new('RGB', (W, H), (14, 15, 20)); d = ImageDraw.Draw(bogen)
    d.rectangle([0, 0, W, kopf - 8], fill=(225, 6, 0)); d.text((rand, 12), titel, font=schrift(22, True), fill=(255, 255, 255))
    for k, (im, t) in enumerate(bilder):
        x = rand + (k % spalten) * (breite + rand); y = kopf + (k // spalten) * (h + fuss + rand) + rand // 2
        bogen.paste(im, (x, y)); d.rectangle([x, y, x + breite - 1, y + im.height - 1], outline=(70, 72, 80))
        d.text((x + 2, y + h + 8), t, font=schrift(16), fill=(225, 228, 235))
    bogen.save(aus, quality=88)
    print(aus, bogen.size)


if __name__ == '__main__':
    main()
