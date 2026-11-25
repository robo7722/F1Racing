#!/usr/bin/env python3
"""Einfarbiges Logo (logos/LOGO.png, 494 × 124) mit scharfen Kanten vergrößern: Deckkraft 4-fach hochrechnen und nachschärfen, Farbe flächig setzen.
   Aufruf: python3 tools/trailer/logo_gross.py <Ausgabe.png> [Faktor]"""
import sys, numpy as np
from PIL import Image
aus = sys.argv[1]; f = int(sys.argv[2]) if len(sys.argv) > 2 else 4
im = Image.open(__file__.replace('tools/trailer/logo_gross.py', 'logos/LOGO.png')).convert('RGBA'); a = np.array(im)
farbe = np.median(a[a[..., 3] > 250][:, :3], axis=0).astype(np.uint8)
al = Image.fromarray(a[..., 3]).resize((im.width * f, im.height * f), Image.BICUBIC)
x = np.asarray(al, dtype=np.float32) / 255; x = np.clip((x - 0.5) * 2.6 + 0.5, 0, 1)        # Kante steiler: aus dem weichen Übergang wird wieder eine saubere Kante
out = np.zeros((x.shape[0], x.shape[1], 4), np.uint8); out[..., :3] = farbe; out[..., 3] = (x * 255 + 0.5).astype(np.uint8)
Image.fromarray(out).save(aus); print(aus, out.shape[1], '×', out.shape[0], 'Farbe', tuple(int(v) for v in farbe))
