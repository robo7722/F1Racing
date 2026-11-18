#!/usr/bin/env python3
"""Original-GLBs der Klassiker vor dem Verkleinern reparieren (Fehler der Vorlagen, 18.11.2026).

Aufruf:  python3 tools/klassiker/vorbereiten.py <schluessel> <original.glb> <texturordner> <ausgabe.glb>
  redbull_rb8:  Karosserie (wccarbody.001) hatte nur eine Glanzkarte als Farbe und 20-fach gestreckte UVs ->
                UVs / 20, Lackierung textures/car_chassis.png (2048², senkrecht gespiegelt) als Farbe.
  ferrari_312:  Karosserie (car_chassis.001) hatte nur einen 16×16-Platzhalter (rot, völlig durchsichtig -> schwarz) ->
                textures/car_chassis.png (1024², senkrecht gespiegelt, „AMON 20“).
  mclaren_mp413: nichts zu tun (Original kann direkt verkleinert werden).
Danach: python3 tools/klassiker/build_klassiker.py <ausgabe.glb> <schluessel> modelle/klassiker
"""
import sys, os, json, struct, shutil, subprocess
key, src, texdir, out = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__)); shutil.copy(src, out)

def scale_uv(path, mat_index, f):
    b = bytearray(open(path, 'rb').read()); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L]); off = 20 + L + 8
    acc = {p['attributes']['TEXCOORD_0'] for me in J['meshes'] for p in me['primitives'] if p.get('material') == mat_index}
    for ai in acc:
        A = J['accessors'][ai]; bv = J['bufferViews'][A['bufferView']]; assert A['componentType'] == 5126
        o = off + bv.get('byteOffset', 0) + A.get('byteOffset', 0); st = bv.get('byteStride', 8)
        for i in range(A['count']):
            u, v = struct.unpack_from('<ff', b, o + i * st); struct.pack_into('<ff', b, o + i * st, u * f, v * f)
        for k in ('min', 'max'):
            if k in A: A[k] = [x * f for x in A[k]]
    js = json.dumps(J, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4); rest = bytes(b[20 + L:])
    open(path, 'wb').write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + len(rest)) + struct.pack('<II', len(js), 0x4E4F534A) + js + rest)

def mat_index(path, name):
    b = open(path, 'rb').read(); L = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + L])
    return next(i for i, m in enumerate(J['materials']) if m.get('name') == name)

def tex(path, name, img, mx):
    subprocess.run([sys.executable, os.path.join(HERE, 'textur_ersetzen.py'), path, name, img, '--flip', '--max', str(mx)], check=True)
    os.remove(path + '.vor_ersetzen')

if key == 'redbull_rb8':
    scale_uv(out, mat_index(out, 'wccarbody.001'), 1 / 20); tex(out, 'wccarbody.001', os.path.join(texdir, 'car_chassis.png'), 2048)
elif key == 'ferrari_312':
    tex(out, 'car_chassis.001', os.path.join(texdir, 'car_chassis.png'), 1024)
print('vorbereitet:', out)
