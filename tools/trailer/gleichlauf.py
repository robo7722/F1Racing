#!/usr/bin/env python3
"""Gleichlauf der gerechneten Bilder prüfen: Je Einstellung die Bildänderung von Bild zu Bild messen (mittlere Helligkeitsdifferenz, verkleinert auf 320 px)
und Ausreißer melden – ein doppeltes Bild (Änderung nahe null) oder ein Sprung (Änderung viel größer als bei den Nachbarn) wäre im Film als Ruckler zu sehen.
   Aufruf: python3 tools/trailer/gleichlauf.py [--aus trailer-ausgabe] [Szene …]
   Ausgabe je Einstellung: Bildzahl, mittlere Änderung, größtes Verhältnis zum gleitenden Median der Nachbarn (7 Bilder) und die auffälligen Bildnummern.
   Kamerawechsel innerhalb einer Einstellung (Zweikampf: zwei) erscheinen als Sprünge – das ist dort richtig."""
import sys, os, subprocess, re, statistics
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); a = sys.argv[1:]
aus = os.path.join(ROOT, a[a.index('--aus') + 1] if '--aus' in a else 'trailer-ausgabe'); namen = [x for i, x in enumerate(a) if not x.startswith('--') and (i == 0 or a[i - 1] != '--aus')]
B = os.path.join(aus, 'bilder'); auff = 0
for sz in namen or sorted(os.listdir(B)):
    d = os.path.join(B, sz); n = len([f for f in os.listdir(d) if f.endswith('.jpg')]) if os.path.isdir(d) else 0
    if n < 8: continue
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(d, '%04d.jpg'), '-vf', 'scale=320:-1,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-', '-f', 'null', '-'], capture_output=True, text=True)
    v = [float(x) for x in re.findall(r'YAVG=([0-9.]+)', r.stdout)][1:]   # erster Wert gehört zum ersten Bild allein
    if len(v) < 8: continue
    mel = []
    for i, x in enumerate(v):
        nb = v[max(0, i - 3):i] + v[i + 1:i + 4]; m = statistics.median(nb)
        if m > 0.05 and (x > 2.2 * m or x < 0.4 * m): mel.append((i + 2, x / m))   # Bildnummer des zweiten Bilds des Paars
    auff += len(mel)
    print('%-20s %4d Bilder · Änderung im Mittel %5.2f · %s' % (sz, n, statistics.mean(v), 'gleichmäßig' if not mel else 'auffällig: ' + ', '.join('Bild %d (×%.1f)' % m for m in mel[:8])))
print('Auffällige Stellen insgesamt:', auff)
