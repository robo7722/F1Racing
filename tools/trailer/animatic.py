#!/usr/bin/env python3
"""Animatic (Storyboard-Vorschau als Video): die Standbilder im geplanten Schnittrhythmus mit der geschnittenen Musik.
   Aufruf: python3 tools/trailer/animatic.py <Bilderordner aus „storyboard.js bilder“> <Musik.wav> <Ausgabe.mp4>
   Je Szene ein langsamer Zoom; Szenen mit „schnitte“ springen im Takt zwischen Ausschnitten. Das Video enthält die geschützte Musik – nicht ins Repository legen."""
import sys, json, os, subprocess, tempfile
bilder, musik, aus = sys.argv[1:4]; FPS = 30
SB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storyboard.json'), encoding='utf-8'))
tmp = tempfile.mkdtemp(prefix='animatic_'); teile = []
AUSSCHNITT = [(1.0, .5, .5), (1.28, .2, .55), (1.14, .8, .5), (1.4, .5, .62), (1.2, .35, .4), (1.32, .7, .6)]   # Zoom, Lage x/y für Sprungschnitte
f = lambda t: round(t * FPS)
for s in SB['szenen']:
    n = s.get('schnitte', 1); a, e = s['von'], s['bis']; nr = f"{s['nr']:02d}"
    for k in range(n):
        f0, f1 = f(a + (e - a) * k / n), f(a + (e - a) * (k + 1) / n); N = f1 - f0; z0, fx, fy = AUSSCHNITT[k % len(AUSSCHNITT)] if n > 1 else (1.0, .5, .5)
        zoom = f"zoompan=z='{z0}+{0.05 if s['bild'] != '@titel' else 0.02}*on/{N}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}':d={N}:s=1280x536:fps={FPS}"
        fx_ = []
        if s['nr'] == 1: fx_.append('fade=in:0:36')
        if s['nr'] == 8 and k == n - 1: fx_.append(f'fade=out:{N - 9}:1')        # letzter Schlag: Schwarz
        if s['nr'] == 18: fx_.append(f'fade=out:{N - 54}:50')
        if s['nr'] == 19: fx_ += ['fade=in:0:5', f'fade=out:{N - 60}:55']
        kette = f"[0]scale=3840:-1,{zoom}{',' + ','.join(fx_) if fx_ else ''},pad=1280:720:0:92:black[p];[p][1]overlay=0:628,format=yuv420p[o]"
        ziel = os.path.join(tmp, f'{nr}_{k}.mp4'); teile.append(ziel)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(bilder, f'szene_{nr}_o.png' if k and os.path.exists(os.path.join(bilder, f'szene_{nr}_o.png')) else f'szene_{nr}.png'), '-i', os.path.join(bilder, f'leiste_{nr}.png'), '-filter_complex', kette, '-map', '[o]', '-frames:v', str(N), '-r', str(FPS), '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', ziel], check=True)
liste = os.path.join(tmp, 'liste.txt'); open(liste, 'w').write(''.join(f"file '{t}'\n" for t in teile))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', liste, '-i', musik, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', aus], check=True)
print(aus, round(os.path.getsize(aus) / 1e6, 1), 'MB')
