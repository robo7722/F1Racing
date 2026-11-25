#!/usr/bin/env python3
"""Echte Radachsen der Klassiker aus den Ringrändern messen (v3.03) – Ergänzung zu radachsen.py, das beim McLaren MP4/13 versagt hat.

Anlass (25.11.2026, McLaren MP4/13): „die Räder eiern“. Im Modell ist das ganze Rad – Reifen, Felge, Nabe, Bremsscheibe – starr mit Sturz eingebaut
(vorn links 3,0°, vorn rechts 3,5°, hinten 1,0°). Das Spiel drehte es um die waagerechte Querachse → Reifenflanken und Felge taumelten (vorn ±17–20 mm
an der Reifenschulter). radachsen.py hatte für dieses Auto unter 0,3° gemeldet: Es sucht die Achse, um die die Laufflächenpunkte den gleichmäßigsten
Abstand haben – bei der stark gewölbten Lauffläche des MP4/13 (Schulter 294 mm, Mitte 326 mm) und der schiefen Punktauswahl hebt sich die Neigung dabei auf.

Verfahren hier (je Rad, Stufe 0):
  1. zusammenhängende Teile des Rad-Netzes suchen; Teile, die rundum laufen (14 von 16 Winkelabschnitten), sind Ringe; der größte ist der Reifen,
  2. durch den äußeren Rand jedes anderen Rings (Felgenhorn, Bremsscheibe, Nabe) eine Ebene legen – ihre Neigung ist die Neigung der Radachse;
     Median über alle Ringe (Rand auf 40 mm begrenzt, mindestens 30 Punkte),
  3. zweite Messung am Reifen allein: Mitte der Reifenbreite über den Umfang (liegt beim geneigten Rad oben und unten seitlich versetzt), viermal nachgeschätzt,
  4. Probe für jede Möglichkeit (keine Neigung / Ringränder / Reifen): Reifen um die Achse zurückdrehen – der seitliche Taumel der Reifenschulter über den
     Umfang muss verschwinden. Taumelt der Reifen ohne Neigung um höchstens ±1 mm, wird nichts eingetragen; sonst gilt die Achse mit dem kleinsten Rest
     (bei fast gleichem Rest Ringränder vor Reifen).
Ausgabe: Werte für HIST_CAR.ax in index.html ([Sturz, Spur] in Grad, Achse = (cos s·cos p, sin s, cos s·sin p)).

Aufruf: python3 tools/klassiker/radachsen_ringe.py [modell.glb …]     (ohne Angabe: alle Modelle in modelle/klassiker)
Fehlversuch (gleiche Sitzung): Felge, Nabe und Scheibe im Modell gerade stellen (GLB ändern). Danach lief die Felge rund, aber der Reifen stand weiter
schief – in der Nahaufnahme wanderte ein Spalt zwischen Felgenhorn und Reifenflanke um das Rad. Das Rad ist ein starrer, geneigter Körper; die Drehachse
muss geneigt werden, nicht das Modell.
"""
import sys, os, glob, json, struct
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5122: np.int16, 5121: np.uint8, 5120: np.int8}; NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
def kreis(Q, m0):
    """Mitte eines Rings: Kreis durch die äußersten Punkte je Winkelabschnitt (48 Abschnitte), Ausreißer (Nasen, Ventil) fallen heraus. Q: [y, z]"""
    rad = 0.0; H = []
    for _ in range(3):
        e = Q - m0; win = np.floor((np.arctan2(e[:, 1], e[:, 0]) + np.pi) / (2 * np.pi) * 48).astype(int) % 48; rr = np.hypot(e[:, 0], e[:, 1]); H = []
        for k in range(48):
            q = np.nonzero(win == k)[0]
            if len(q): H.append(Q[q[np.argmax(rr[q])]])
        H = np.array(H)
        if len(H) < 12: return None, 0
        A = np.c_[2 * H, np.ones(len(H))]; sol = np.linalg.lstsq(A, (H ** 2).sum(1), rcond=None)[0]; c = sol[:2]; rad = np.sqrt(max(sol[2] + c @ c, 0)); res = np.abs(np.hypot(*(H - c).T) - rad)
        gut = res <= max(2.5 * np.median(res), 1e-7)
        if 12 <= gut.sum() < len(H): sol = np.linalg.lstsq(A[gut], (H[gut] ** 2).sum(1), rcond=None)[0]; c = sol[:2]; rad = np.sqrt(max(sol[2] + c @ c, 0))
        m0 = c
    return m0, rad
def drehung(n):
    """Drehmatrix, die die Achsrichtung n auf die Querachse (x) dreht"""
    v = np.cross(n, [1.0, 0, 0]); K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + n[0])
def taumel(Q, c):
    """Seitlicher Taumel des Reifens: Mitte der Reifenbreite in 16 Winkelabschnitten → Ausgleich x = c + A·cos + B·sin. Rückgabe: (Hub in m, A, B, Radius der Schulter)"""
    y = Q[:, 1] - c[0]; z = Q[:, 2] - c[1]; rr = np.hypot(y, z); th = np.arctan2(y, z); win = np.floor((th + np.pi) / (2 * np.pi) * 16).astype(int) % 16; mid, ww, rs = [], [], []
    br = np.array([np.ptp(Q[win == k, 0]) for k in range(16) if (win == k).sum() >= 6])
    if len(br) and np.ptp(br) > 0.05 * np.median(br):                  # Breite schwankt über den Umfang: am Reifen hängen fremde Teile (F2004 hinten rechts) → nur Lauffläche und Schulter werten
        aussen = rr > 0.85 * rr.max(); Q = Q[aussen]; rr = rr[aussen]; win = win[aussen]
    for k in range(16):
        s = win == k
        if s.sum() < 6: continue
        i0, i1 = np.argmin(Q[s, 0]), np.argmax(Q[s, 0]); mid.append((Q[s, 0].min() + Q[s, 0].max()) / 2); ww.append(-np.pi + (k + 0.5) * 2 * np.pi / 16); rs += [rr[s][i0], rr[s][i1]]
    ww = np.array(ww); sol = np.linalg.lstsq(np.c_[np.sin(ww), np.cos(ww), np.ones(len(ww))], np.array(mid), rcond=None)[0]   # sin(th) ~ y (oben), cos(th) ~ z (vorn)
    return float(np.hypot(sol[0], sol[1])), sol[0], sol[1], float(np.mean(rs))

def modell(pfad):
    b = open(pfad, 'rb').read(); jl = struct.unpack('<I', b[12:16])[0]; J = json.loads(b[20:20 + jl]); B0 = 20 + jl + 8; N = J['nodes']; eltern = {c: i for i, n in enumerate(N) for c in n.get('children', [])}
    def lies(i):
        ac = J['accessors'][i]; v = J['bufferViews'][ac['bufferView']]; nc = NC[ac['type']]; dt = np.dtype(CT[ac['componentType']]); o = B0 + v.get('byteOffset', 0) + ac.get('byteOffset', 0); st = v.get('byteStride') or dt.itemsize * nc; n = ac['count']
        raw = np.frombuffer(b[o:o + st * (n - 1) + dt.itemsize * nc], np.uint8); return np.lib.stride_tricks.as_strided(raw, (n, dt.itemsize * nc), (st, 1)).copy().view(dt).reshape(n, nc)
    aus = {}
    for i, n in enumerate(N):
        if not (n.get('name', '').startswith('wheel_') and 'mesh' in n and J['meshes'][n['mesh']].get('name', '').endswith('LOD0')): continue
        s = float(n.get('scale', [1, 1, 1])[0]); O = np.zeros(3); k = i
        while k is not None: O += np.array(N[k].get('translation', [0, 0, 0]), float); k = eltern.get(k)
        prims = J['meshes'][n['mesh']]['primitives']; P = [lies(p['attributes']['POSITION']).astype(np.float64) for p in prims]; start = np.cumsum([0] + [len(x) for x in P]); roh = np.concatenate(P); car = O + s * roh
        tri = np.concatenate([lies(p['indices']).ravel().astype(np.int64).reshape(-1, 3) + start[j] for j, p in enumerate(prims)])
        _, inv = np.unique(np.round(car * 20000), axis=0, return_inverse=True); inv = inv.ravel(); par = np.arange(inv.max() + 1)
        def find(x):
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        for t in inv[tri]:
            r0 = find(t[0]); par[find(t[1])] = r0; par[find(t[2])] = r0
        wurzel = np.array([find(x) for x in inv]); c0 = (car[:, 1:].max(0) + car[:, 1:].min(0)) / 2; T = {}
        for r in np.unique(wurzel):
            Q = car[wurzel == r]; d = Q[:, 1:] - c0; sek = np.unique(np.floor((np.arctan2(d[:, 1], d[:, 0]) + np.pi) / (2 * np.pi) * 16).astype(int) % 16)
            if len(Q) < 24 or len(sek) < 14: continue
            m, R = kreis(Q[:, 1:], (Q[:, 1:].max(0) + Q[:, 1:].min(0)) / 2)
            if m is not None: T[r] = (Q, m, R)
        if not T: continue
        reifen = max(T, key=lambda r: T[r][2]); QR, cR, RR = T[reifen]; neig = []
        for r, (Q, m, R) in T.items():
            if r == reifen or R < 0.2 * RR or np.hypot(*(Q[:, 1:] - cR).T).max() > 0.75 * RR: continue
            e = Q[:, 1:] - m; rand = Q[np.hypot(e[:, 0], e[:, 1]) > 0.97 * R]
            if len(rand) >= 30 and np.ptp(rand[:, 0]) <= 0.04: neig.append(np.linalg.lstsq(np.c_[rand[:, 1:], np.ones(len(rand))], rand[:, 0], rcond=None)[0][:2])
        grad = lambda v: (float(np.degrees(np.arcsin(v[1]))), float(np.degrees(np.arctan2(v[2], v[0]))))
        mitte = np.array([(QR[:, 0].min() + QR[:, 0].max()) / 2, cR[0], cR[1]])
        def rest(nv):
            """Taumel der Reifenschulter (m), wenn das Rad um die Achse nv dreht, und die danach noch verbleibende Neigung (A, B, Schulterradius)"""
            Qn = (QR - mitte) @ drehung(nv).T + mitte; cn, _ = kreis(Qn[:, 1:], cR); return taumel(Qn, cn)
        ex = np.array([1.0, 0, 0]); hub = rest(ex)[0]; nt = ex.copy()
        for _ in range(4):                                             # Achse aus dem Reifen allein: Neigung schätzen, zurückdrehen, Rest nachschätzen
            _, A, B, rs = rest(nt); d = np.array([1.0, -A / rs, -B / rs]); d /= np.linalg.norm(d); nt = drehung(nt).T @ d; nt /= np.linalg.norm(nt)
        kand = {'keine Neigung': ex, 'Reifen': nt}
        if len(neig) >= 2: ab = np.median(np.array(neig), axis=0); nr = np.array([1.0, -ab[0], -ab[1]]); kand['Ringränder'] = nr / np.linalg.norm(nr)
        reste = {k: rest(v)[0] * 1000 for k, v in kand.items()}
        wahl = 'keine Neigung' if reste['keine Neigung'] <= 1.0 else min(reste, key=lambda k: reste[k] + (0.15 if k == 'Reifen' else 0.0))   # unter ±1 mm Taumel: nichts eintragen; sonst im Zweifel Ringränder vor Reifen
        aus[n['name'].split('_')[1]] = dict(ringe=len(neig), kand={k: grad(v) for k, v in kand.items()}, reste=reste, wahl=wahl, ax=grad(kand[wahl]), vor=hub * 1000, nach=reste[wahl])
    return aus

dateien = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, 'modelle', 'klassiker', '*.glb')))
for pf in dateien:
    erg = modell(pf); name = os.path.basename(pf)[:-4]; print(name)
    for k in ['FL', 'FR', 'RL', 'RR']:
        if k not in erg: continue
        e = erg[k]; print(f"  {k}: " + ' · '.join(f"{n_} {g[0]:+.2f}°/{g[1]:+.2f}° → Taumel ±{e['reste'][n_]:.1f} mm" for n_, g in e['kand'].items()) + f"  ⇒ {e['wahl']}")
    noetig = [k for k in ['FL', 'FR', 'RL', 'RR'] if k in erg and erg[k]['wahl'] != 'keine Neigung']
    print('  ' + ('ax: { ' + ', '.join(f"{k}: [{erg[k]['ax'][0]:.2f}, {erg[k]['ax'][1]:.2f}]" for k in noetig) + ' }' if noetig else 'kein ax-Eintrag nötig'))
