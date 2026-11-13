"""Welche Strecken hat eine Änderung an index.html betroffen?

Nach jedem QC-Lauf merkt sich run.py je Strecke, mit welchem Stand von index.html sie geprüft wurde
(Kopie in qc-reports/baseline/, Zuordnung in qc-reports/baseline/state.json). `run.py --changed` vergleicht
den aktuellen Stand damit und prüft nur Strecken, deren Daten oder Code sich seitdem geändert haben.

Zuordnung einer geänderten Stelle (in dieser Reihenfolge):
 1. Eintrag einer Strecke in TRACKS, THEMES oder TREE_STYLE -> diese Strecke (Themen auch für Strecken, die sie mit ...THEMES.x erben)
 2. Merkmale einer Strecke in der Zeile oder im umgebenden Block: TRK.<eigene Eigenschaft> (z. B. TRK.mc), TH.<seltene
    Themen-Eigenschaft> (z. B. TH.vegas), Datenkennung ('mc-1929'), eigene Datenkonstanten (MEL_REF, NS_DATA), 'schlüssel'
 3. sonst: liegt die Stelle in einer Funktion, die Strecken baut oder auswertet (trackGroup, hStrip, PX[, HW[, surface( ...)
    -> alle Strecken; andernfalls (Auto, Menü, Musik ...) -> keine
"""
import hashlib, json, os, re, shutil, subprocess

GEN_DATA = {'TRACK_HD', 'TRACK_PTS', 'OSM_LM', 'THEMES', 'TRACKS'}
# Streckengeometrie: in der Änderung selbst oder in der umgebenden Funktion -> allgemeiner Streckencode (betrifft alle)
# (bewusst ohne bloße Aufrufe wie buildTrack(...) – das Menü baut auch Strecken, ändert sie aber nicht)
TRACKISH = re.compile(r'\b(trackGroup\.add|hStrip|vStrip|foldLim|surface|fillGroundHoles|ELEV|PX|PZ|HW|WL|WR|KERBL|KERBR|NOWALL|GRL|GRR|TH)\b\s*[\[(.]')


def _block(lines, start_pat, end_pat='^};|^\\}\\);'):
    """Einträge `  key: {` eines Objekt-Literals -> {key: (erste, letzte Zeile)} (0-basiert)."""
    out, i0 = {}, None
    for i, l in enumerate(lines):
        if i0 is None:
            if re.match(start_pat, l): i0 = i
            continue
        if re.match(end_pat, l): break
    if i0 is None: return out
    cur, cur_i = None, None
    for i in range(i0 + 1, len(lines)):
        l = lines[i]
        m = re.match(r'^  (\w+):\s*\{', l)
        if m or re.match(end_pat, l):
            if cur: out[cur] = (cur_i, i - 1)
            cur, cur_i = (m.group(1), i) if m else (None, None)
            if not m: break
    return out


def profiles(src):
    """Merkmale je Strecke aus dem aktuellen index.html."""
    lines = src.split('\n')
    tr = _block(lines, r'^const TRACKS = \{')
    tr.update(_block(lines, r'^Object\.assign\(TRACKS, \{'))
    th = _block(lines, r'^const THEMES = \{')
    th.update(_block(lines, r'^Object\.assign\(THEMES, \{'))   # Kartbahnen
    for i, l in enumerate(lines):   # THEMES.genk.look = ... (eine Zeile) zum Thema zählen
        m = re.match(r'^THEMES\.(\w+)\.', l)
        if m and m.group(1) in th: th.setdefault(m.group(1) + '#' + str(i), (i, i))
    ts = _block(lines, r'^const TREE_STYLE = \{')
    txt = lambda r: '\n'.join(lines[r[0]:r[1] + 1])
    ent = {k: txt(r) for k, r in tr.items()}
    then = {k: txt(r) for k, r in th.items()}
    props = lambda t: set(re.findall(r'[{,]\s*(\w+):', t))
    pc = {}
    for t in ent.values():
        for p in props(t): pc[p] = pc.get(p, 0) + 1
    tc = {}
    for t in then.values():
        for p in props(t): tc[p] = tc.get(p, 0) + 1
    P = {}
    for k, t in ent.items():
        theme = (re.search(r"theme: '(\w+)'", t) or [None, k])[1]
        themes = {theme}
        for _ in range(3):   # ...THEMES.sil erben
            for tk in list(themes):
                themes |= set(re.findall(r'\.\.\.THEMES\.(\w+)', then.get(tk, '')))
        toks = {"'%s'" % k, 'TRK.%s' % k}
        toks |= {'TRK.%s' % p for p in props(t) if pc[p] <= 2 and len(p) > 2}
        for tk in themes:
            toks |= {'TH.%s' % p for p in props(then.get(tk, '')) if tc.get(p, 99) <= 3 and len(p) > 3}
        toks |= {'"%s"' % d for d in re.findall(r"TRACK_(?:HD|PTS)\['([\w-]+)'\]", t)}
        toks |= {c for c in re.findall(r'\b([A-Z][A-Z0-9_]{2,})\b', re.sub(r"'[^']*'", "''", t)) if c not in GEN_DATA}   # Datenkonstanten (MEL_REF, NS_DATA), nicht Texte wie 'VAE'
        toks |= {'OSM_LM.%s' % m for m in re.findall(r'OSM_LM\.(\w+)', t)}
        P[k] = {'toks': toks, 'themes': themes}
    ranges = {k: [r] for k, r in tr.items()}
    for k, p in P.items():
        for tk in p['themes']:
            ranges[k] += [r for tkey, r in th.items() if tkey.split('#')[0] == tk]
            if tk in ts: ranges[k].append(ts[tk])
        if k in ts: ranges[k].append(ts[k])
    return P, ranges, lines


def _hunks(old_path, new_path):
    """git diff -U0 -> Liste (neue Zeilennummer 0-basiert, Anzahl, geänderter Text alt+neu)."""
    r = subprocess.run(['git', 'diff', '--no-index', '-U0', '--no-color', old_path, new_path], capture_output=True, text=True, encoding='utf-8', errors='replace')
    out, cur = [], None
    for l in r.stdout.split('\n'):
        m = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', l)
        if m:
            n0, cnt = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            cur = [max(0, n0 - 1), cnt, []]; out.append(cur); continue
        if cur and l[:1] in '+-' and not l.startswith(('+++', '---')):
            cur[2].append(l[1:])
    return out


def _net(l):
    """Klammerbilanz einer Zeile ({ minus }), ohne Zeichenketten und Kommentare (grob)."""
    l = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`(?:\\.|[^`\\])*`", '', l)
    l = re.sub(r'/\*.*?\*/', '', l); l = l.split('//')[0] if '//' in l and 'http' not in l else l
    return l.count('{') - l.count('}')


def _context(lines, i):
    """Umgebende Blöcke (Zeilen darüber, die einen noch offenen Block öffnen) bis zur äußersten Funktion; dazu deren Kopf und Text."""
    if i >= len(lines): i = len(lines) - 1
    ind = lambda l: len(l) - len(l.lstrip(' \t'))
    top = lines[i] and not lines[i].startswith((' ', '\t', '}', ')'))
    if top and _net(lines[i]) <= 0:
        return [], lines[i][:120], lines[i]   # eigenständige Anweisung ganz links (z. B. const VERSION = ...): nur sie selbst zählt
    ctx, fn_start = [], (i if top else None)
    cur = ind(lines[i]) if lines[i].strip() else 99
    for j in range(i - 1, max(-1, i - 6000), -1) if fn_start is None else ():   # weniger eingerückte Zeilen darüber, die einen Block öffnen
        l = lines[j]
        if not l.strip() or ind(l) >= cur or _net(l) <= 0: continue
        ctx.append(l[:3000]); cur = ind(l)
        if cur == 0: fn_start = j; break
    if fn_start is None: return ctx, '', lines[i]
    d, fn_end = 0, len(lines)
    for j in range(fn_start, min(len(lines), fn_start + 6000)):
        d += _net(lines[j])
        if d <= 0 and j > fn_start: fn_end = j + 1; break
    return ctx, lines[fn_start][:120], '\n'.join(lines[fn_start:fn_end])


def affected(old_src, new_src, tmpdir):
    """Strecken, die zwischen old_src und new_src betroffen sind -> ({key: [Gründe]}, alle_gründe)."""
    if old_src == new_src: return {}, []
    P, ranges, lines = profiles(new_src)
    a, b = os.path.join(tmpdir, 'qc_old.html'), os.path.join(tmpdir, 'qc_new.html')
    open(a, 'w', encoding='utf-8', newline='\n').write(old_src); open(b, 'w', encoding='utf-8', newline='\n').write(new_src)
    hit, general = {}, []
    add = (lambda k, why: hit.setdefault(k, []).append(why) if why not in hit.get(k, []) else None)
    for n0, cnt, text in _hunks(a, b):
        line_no = n0 + 1; changed = '\n'.join(text)
        # 1. Eintrag einer Strecke / ihres Themas
        direct = [k for k, rs in ranges.items() if any(r0 <= n0 + d <= r1 for r0, r1 in rs for d in range(max(1, cnt)))]
        if direct:
            for k in direct: add(k, 'Zeile %d: Streckeneintrag/Thema' % line_no)
            continue
        # 2. Merkmale in der Änderung oder im umgebenden Block
        ctx, head, body = _context(lines, n0)
        found = False
        for k, p in P.items():
            t = next((t for t in p['toks'] if t in changed), None) or next((t for t in p['toks'] if any(t in c for c in ctx)), None)
            if t: add(k, 'Zeile %d: %s' % (line_no, t)); found = True
        if found: continue
        # 3. allgemeiner Streckencode?
        if TRACKISH.search(changed) or TRACKISH.search(body):
            fm = re.search(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=|window\.(\w+)\s*=)', head)
            general.append(((fm and next((g for g in fm.groups() if g), None)) or 'oberste Ebene', line_no))
    if general:
        by = {}
        for fn, ln in general: by.setdefault(fn, []).append(ln)
        txt = '; '.join('%s (Zeile %s)' % (fn, ', '.join(map(str, ls[:4])) + (' …' if len(ls) > 4 else '')) for fn, ls in list(by.items())[:4])
        for k in P: hit.setdefault(k, []).append('allgemeiner Streckencode: ' + txt)
    return hit, general


# ---------- Stand je Strecke merken ----------
def _bdir(out): return os.path.join(out, 'baseline')


def remember(out, src, keys):
    """Nach einem Lauf: diese Strecken wurden mit `src` geprüft."""
    d = _bdir(out); os.makedirs(d, exist_ok=True)
    h = hashlib.sha1(src.encode('utf-8')).hexdigest()[:16]
    p = os.path.join(d, h + '.html')
    if not os.path.exists(p): open(p, 'w', encoding='utf-8', newline='\n').write(src)
    sp = os.path.join(d, 'state.json')
    try: st = json.load(open(sp, encoding='utf-8'))
    except Exception: st = {}
    for k in keys: st[k] = h
    json.dump(st, open(sp, 'w', encoding='utf-8'), indent=1)
    used = set(st.values())   # nicht mehr gebrauchte Stände löschen
    for f in os.listdir(d):
        if f.endswith('.html') and f[:-5] not in used: os.remove(os.path.join(d, f))


def changed_tracks(out, src, all_keys, tmpdir):
    """-> [(key, [Gründe])] für alle Strecken, die seit ihrer letzten Prüfung betroffen sind."""
    d = _bdir(out)
    try: st = json.load(open(os.path.join(d, 'state.json'), encoding='utf-8'))
    except Exception: st = {}
    res, cache = [], {}
    for k in all_keys:
        h = st.get(k)
        if not h or not os.path.exists(os.path.join(d, h + '.html')):
            res.append((k, ['noch nie mit dem Bot geprüft'])); continue
        if h not in cache:
            cache[h] = affected(open(os.path.join(d, h + '.html'), encoding='utf-8').read(), src, tmpdir)[0]
        if k in cache[h]: res.append((k, cache[h][k]))
    return res
