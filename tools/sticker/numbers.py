#!/usr/bin/env python3
"""Startnummern im Design der Fahrer holen:  python3 tools/sticker/numbers.py
Lädt die offiziellen Nummern-Grafiken (weiß, ohne Rahmen) von formula1.com und fiaformula2.com und schreibt
liveries/num/<f1|f2>_<Nummer>.png (256 x 128, weiß auf durchsichtig). Die Farbe kommt erst im Spiel dazu ("number.color").
Fehlt eine Grafik, zeichnet das Spiel die Nummer selbst."""
import os, io, subprocess
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); OUT = os.path.join(ROOT, 'liveries', 'num')
F1 = 'https://media.formula1.com/image/upload/c_fit,w_800/v1740000001/common/f1/2026/%s/%s/2026%s%snumberwhitefrless.png'
F2 = 'https://res.cloudinary.com/prod-f2f3/c_fit,w_800/v1770000000/common/f2/2026/%s/%s/2026%s%snumberwhitefrless.png'
T1 = {63: ('mercedes', 'georus01'), 12: ('mercedes', 'andant01'), 16: ('ferrari', 'chalec01'), 44: ('ferrari', 'lewham01'), 1: ('mclaren', 'lannor01'), 81: ('mclaren', 'oscpia01'),
      3: ('redbullracing', 'maxver01'), 6: ('redbullracing', 'isahad01'), 14: ('astonmartin', 'feralo01'), 18: ('astonmartin', 'lanstr01'), 23: ('williams', 'alealb01'), 55: ('williams', 'carsai01'),
      30: ('racingbulls', 'lialaw01'), 41: ('racingbulls', 'arvlin01'), 10: ('alpine', 'piegas01'), 43: ('alpine', 'fracol01'), 31: ('haasf1team', 'estoco01'), 87: ('haasf1team', 'olibea01'),
      27: ('audi', 'nichul01'), 5: ('audi', 'gabbor01'), 11: ('cadillac', 'serper01'), 77: ('cadillac', 'valbot01')}
T2 = {1: ('invictaracing', 'rafcam01'), 2: ('invictaracing', 'josdur01'), 3: ('hitech', 'ritmiy01'), 4: ('hitech', 'colher01'), 5: ('camposracing', 'noeleo01'), 6: ('camposracing', 'niktso01'),
      7: ('damslucasoil', 'dinbeg01'), 8: ('damslucasoil', 'rombil01'), 9: ('mpmotorsport', 'gabmin01'), 10: ('mpmotorsport', 'oligoe01'), 11: ('premaracing', 'sebmon01'), 12: ('premaracing', 'marboy01'),
      14: ('rodinmotorsport', 'marste01'), 15: ('rodinmotorsport', 'aledun01'), 16: ('artgrandprix', 'kusmai01'), 17: ('artgrandprix', 'tasint01'), 20: ('aixracing', 'emefit02'), 21: ('aixracing', 'ciashi01'),
      22: ('vanamersfoortracing', 'nicvar01'), 23: ('vanamersfoortracing', 'rafvil01'), 24: ('trident', 'lauvan01'), 25: ('trident', 'johben01')}
os.makedirs(OUT, exist_ok=True)
for ser, tab, url in (('f1', T1, F1), ('f2', T2, F2)):
    for num, (team, drv) in sorted(tab.items()):
        r = subprocess.run(['curl', '-sS', '-f', '-m', '60', '-A', 'Mozilla/5.0', url % (team, drv, team, drv)], capture_output=True)
        if r.returncode != 0 or not r.stdout: print('fehlt', ser, num, drv); continue
        im = Image.open(io.BytesIO(r.stdout)).convert('RGBA'); bb = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
        if not bb: print('leer', ser, num); continue
        im = im.crop(bb); k = min(244 / im.width, 116 / im.height); im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        o = Image.new('RGBA', (256, 128), (255, 255, 255, 0)); a = im.getchannel('A'); w = Image.new('RGBA', im.size, (255, 255, 255, 255)); w.putalpha(a)
        o.paste(w, ((256 - im.width) // 2, (128 - im.height) // 2)); o.save(os.path.join(OUT, '%s_%d.png' % (ser, num)), optimize=True); print('ok', ser, num, drv, im.size)
