#!/usr/bin/env python3
"""Trailer schneiden: Bildfolgen aus trailer-ausgabe/bilder/ nach tools/trailer/schnittplan.json taktgenau aneinanderfügen,
   Schriften und Schlusstafel einblenden, Kinoformat mit schwarzen Balken, Musik darunter.
   Aufruf: python3 tools/trailer/schnitt.py <Musik.wav> <Ausgabe.mp4> [--aus trailer-ausgabe] [--vorschau] [--crf 18] [--maxrate 12M | 0]
   --vorschau: halbe Auflösung und schnelle Kodierung; fehlende Einstellungen werden grau gezeigt (zum Prüfen des Schnitts, bevor alles gerechnet ist).
   Vorher: python3 tools/trailer/logo_gross.py <aus>/schrift/logo_gross.png  und  node tools/trailer/schrift.js <aus>/schrift
   Das Ergebnis enthält geschützte Musik – nicht ins Repository legen."""
import sys, os, json, subprocess
a = sys.argv[1:]
def flag(n, d=None):
    if '--' + n in a: i = a.index('--' + n); v = a[i + 1]; del a[i:i + 2]; return v
    return d
vorschau = '--vorschau' in a; a = [x for x in a if x != '--vorschau']; CRF = flag('crf', '18'); MAXRATE = flag('maxrate', '12M')   # Obergrenze der Datenrate: das Filmkorn treibt sie sonst auf ~49 Mbit/s (600 MB)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); AUS = os.path.join(ROOT, flag('aus', 'trailer-ausgabe')); musik, ziel = a[0], a[1]
P = json.load(open(os.path.join(ROOT, 'tools/trailer/schnittplan.json'), encoding='utf-8')); FPS = P['fps']; S = P['schnitte']; f = lambda t: round(t * FPS)
W, H, BH = 1920, 1080, 804; OBEN = (H - BH) // 2
KORN = "noise=alls=4:allf=t"                      # feines Filmkorn nur im Bild, nicht in den Balken
ein, graph, teile, fehlt = [], [], [], []
def eingang(*args): ein.extend(args); return (len([x for x in ein if x == '-i']) - 1)
for k, c in enumerate(S[:-1]):
    N = f(S[k + 1]['von']) - f(c['von']); D = N / FPS; sz = c['szene']; lab = f'c{k}'
    if N <= 0: continue
    if sz == '@schwarz':
        i = eingang('-f', 'lavfi', '-t', f'{D:.4f}', '-i', f'color=c=black:s={W}x{H}:r={FPS}'); graph.append(f'[{i}:v]format=yuv420p,setsar=1[{lab}]')
    elif sz == '@titel':
        i = eingang('-loop', '1', '-framerate', str(FPS), '-t', f'{D:.4f}', '-i', os.path.join(AUS, 'schrift', 'titel.png'))
        graph.append(f"[{i}:v]scale={W}:{H},format=yuv420p,setsar=1,fade=t=in:st=0:d={c.get('ein', 0.25)},fade=t=out:st={D - c.get('aus', 1.5):.3f}:d={c.get('aus', 1.5)}[{lab}]")
    else:
        d = os.path.join(AUS, 'bilder', sz); da = os.path.isdir(d) and len([x for x in os.listdir(d) if x.endswith('.jpg')]) >= N
        if not da:
            fehlt.append(sz)
            if not vorschau: continue
            i = eingang('-f', 'lavfi', '-t', f'{D:.4f}', '-i', f'color=c=0x30303a:s={W}x{BH}:r={FPS}'); kette = f'[{i}:v]format=yuv420p,setsar=1'
        else:
            i = eingang('-framerate', str(FPS), '-start_number', str(1 + c.get('ab', 0)), '-i', os.path.join(d, '%04d.jpg'))
            kette = f"[{i}:v]trim=end_frame={N},setpts=PTS-STARTPTS,scale={W}:{BH}:flags=lanczos,setsar=1,format=yuv444p" + (',' + c['filter'] if c.get('filter') else '') + ',' + KORN
        if c.get('ein'): kette += f",fade=t=in:st=0:d={c['ein']}"
        if c.get('aus'): kette += f",fade=t=out:st={D - c['aus']:.3f}:d={c['aus']}"
        if c.get('text'):
            kurz = c.get('textKurz'); t0, td = (0.04, 0.12) if kurz else (0.35, 0.4); ta = 0.12 if kurz else 0.4
            j = eingang('-loop', '1', '-framerate', str(FPS), '-t', f'{D:.4f}', '-i', os.path.join(AUS, 'schrift', f"text_{c['text']}.png"))
            graph.append(f"[{j}:v]format=rgba,fade=t=in:st={t0}:d={td}:alpha=1,fade=t=out:st={D - ta - 0.06:.3f}:d={ta}:alpha=1[t{k}]"); graph.append(kette + f"[b{k}]"); kette = f"[b{k}][t{k}]overlay=0:0:shortest=1"
        graph.append(kette + f",pad={W}:{H}:0:{OBEN}:black,format=yuv420p,setsar=1[{lab}]")
    teile.append(f'[{lab}]')
if fehlt: print('Es fehlen noch:', ', '.join(fehlt))
if fehlt and not vorschau: sys.exit('Abbruch: nicht alle Einstellungen sind gerechnet (mit --vorschau wird trotzdem geschnitten).')
graph.append(''.join(teile) + f'concat=n={len(teile)}:v=1:a=0' + (',scale=960:540' if vorschau else '') + '[v]')
im = eingang('-i', musik)
kod = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24'] if vorschau else ['-c:v', 'libx264', '-preset', 'slow', '-crf', CRF, '-profile:v', 'high', '-pix_fmt', 'yuv420p'] + ([] if MAXRATE == '0' else ['-maxrate', MAXRATE, '-bufsize', str(2 * int(MAXRATE[:-1])) + 'M'])
cmd = ['ffmpeg', '-v', 'error', '-y', *ein, '-filter_complex', ';'.join(graph), '-map', '[v]', '-map', f'{im}:a', *kod, '-r', str(FPS), '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', ziel]
subprocess.run(cmd, check=True); print(ziel, round(os.path.getsize(ziel) / 1e6, 1), 'MB')
