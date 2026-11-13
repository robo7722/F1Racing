"""QC-Bot starten: Strecken automatisch abfahren und prüfen lassen.

    python qc/run.py                      alle Strecken, eine Runde je Kamera
    python qc/run.py monza spa            nur diese Strecken (Schlüssel aus TRACKS in index.html)
    python qc/run.py --quick              eine Runde je Strecke, Kamera wechselt während der Runde
    python qc/run.py --laps 2 --gfx ultra
    python qc/run.py --list               bekannte Strecken anzeigen
    python qc/run.py --changed            nur Strecken, die sich seit ihrer letzten Prüfung geändert haben (zeigt den Grund)
    python qc/run.py --changed --dry      nur anzeigen, welche das wären
    python qc/run.py mc --at 2900-3100    nur diesen Abschnitt (Streckenmeter) prüfen, dort alle 25 m mit Rundumblick

Braucht nur Python und Edge (oder Chrome). Ergebnis: qc-reports/<Datum>/report.html
Standard: Edge läuft unsichtbar im Hintergrund. Mit --show öffnet sich ein Fenster (echte Bildausgabe).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, threading, time, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import changed as CHG   # noqa: E402  (qc/changed.py: welche Strecken eine Änderung betrifft)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'qc-reports')
STATE = {'done': False, 'last': time.time(), 'tracks_done': set()}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass

    def do_POST(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n) if n else b''
        STATE['last'] = time.time()
        if u.path == '/__qc/log':
            line = body.decode('utf-8', 'replace'); STATE['lastline'] = line; STATE['crashed'] = False
            print('  ' + line, flush=True)
        elif u.path == '/__qc/save':
            run = re.sub(r'[^\w.-]', '_', q.get('run', ['run'])[0])
            rel = q.get('path', ['x'])[0].replace('\\', '/')
            if '..' in rel or rel.startswith('/') or not re.fullmatch(r'[\w./-]+', rel):
                self.send_response(400); self.end_headers(); return
            dst = os.path.join(OUT, run, *rel.split('/'))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(body)
            if rel.endswith('.json') and '/' not in rel and rel != 'summary.json':
                STATE['tracks_done'].add(rel[:-5])
        elif u.path == '/__qc/done':
            STATE['done'] = True
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(204); self.end_headers()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False   # unter Windows dürften sonst zwei Läufe denselben Port belegen und sich gegenseitig den Browser beenden

    def handle_error(self, request, client_address):
        if not isinstance(sys.exc_info()[1], (ConnectionError, BrokenPipeError)):
            super().handle_error(request, client_address)


class CDP:
    """Winziger DevTools-Client (WebSocket nur mit der Standardbibliothek): weckt eine vom Browser eingefrorene Seite wieder auf."""
    def __init__(self, port):
        self.port = port

    def _ws_url(self):
        import urllib.request
        for t in json.load(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json', timeout=3)):
            if t.get('type') == 'page' and 'index.html' in t.get('url', ''):
                return t['webSocketDebuggerUrl']
        return None

    def send(self, *calls):
        import base64, socket, struct
        u = urlparse(self._ws_url() or '')
        if not u.hostname:
            return False
        sock = socket.create_connection((u.hostname, u.port), timeout=5)
        key = base64.b64encode(os.urandom(16)).decode()
        crlf = chr(13) + chr(10)
        hs = (f'GET {u.path} HTTP/1.1{crlf}Host: {u.hostname}:{u.port}{crlf}Upgrade: websocket{crlf}Connection: Upgrade{crlf}'
              f'Sec-WebSocket-Key: {key}{crlf}Sec-WebSocket-Version: 13{crlf}{crlf}')
        sock.sendall(hs.encode())
        resp = b''
        while (crlf * 2).encode() not in resp:
            resp += sock.recv(4096)
        if b' 101 ' not in resp.split(crlf.encode())[0]:
            sock.close(); return False
        for k, (method, params) in enumerate(calls, 1):
            data = json.dumps({'id': k, 'method': method, 'params': params}).encode()
            mask = os.urandom(4)
            head = bytes([0x81]) + (bytes([0x80 | len(data)]) if len(data) < 126 else bytes([0x80 | 126]) + struct.pack('>H', len(data)))
            sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
        time.sleep(0.5)
        sock.close()
        return True


def keep_awake(on):
    """Bildschirm und Rechner wach halten, solange der Bot fährt (wie ein Videoplayer). Schaltet Windows den Bildschirm ab,
    gilt die Seite als verdeckt, alles wird gedrosselt und die Grafikkarte kann kurz einschlafen."""
    if os.name != 'nt':
        return
    import ctypes
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED = 0x80000000, 0x00000001, 0x00000002
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | (ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED if on else 0))


def kill_tree(proc):
    """Edge startet viele Unterprozesse (Grafik, Seiten) – alle beenden, sonst bleiben sie hängen und blockieren den nächsten Start."""
    if proc.poll() is None or os.name == 'nt':
        if os.name == 'nt':
            subprocess.run(['taskkill', '/T', '/F', '/PID', str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.kill()


def kill_leftovers(prof_prefix):
    """Reste früherer, abgebrochener Läufe (Edge mit f1qc-Profil) beenden."""
    if os.name != 'nt':
        return
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='msedge.exe' or Name='chrome.exe'\" | "
          f"Where-Object {{ $_.CommandLine -like '*{prof_prefix}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}")
    subprocess.run(['powershell', '-NoProfile', '-Command', ps], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def find_browser(explicit):
    if explicit:
        return explicit
    pf = [os.environ.get(k, '') for k in ('PROGRAMFILES(X86)', 'PROGRAMFILES', 'LOCALAPPDATA')]
    cands = [os.path.join(p, *s) for p in pf if p for s in (
        ('Microsoft', 'Edge', 'Application', 'msedge.exe'), ('Google', 'Chrome', 'Application', 'chrome.exe'))]
    cands += [shutil.which(n) for n in ('msedge', 'chrome', 'google-chrome', 'chromium')]
    for c in cands:
        if c and os.path.exists(c):
            return c
    sys.exit('Kein Edge/Chrome gefunden – Pfad mit --browser angeben.')


def track_keys():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    i = src.index('const TRACKS = {')
    keys = re.findall(r"^  (\w+): \{ [^\n]*?name: '([^']+)'", src[i:], re.M)
    return [(k, n) for k, n in keys]


def main():
    ap = argparse.ArgumentParser(description='QC-Bot für F1 Racing')
    ap.add_argument('tracks', nargs='*', help='Strecken-Schlüssel (leer = alle)')
    ap.add_argument('--quick', action='store_true', help='eine Runde je Strecke')
    ap.add_argument('--laps', type=int, default=0, help='Runden je Strecke (Standard: eine je Kamera)')
    ap.add_argument('--ser', default='', help='Klasse f1/f2/kart (Kartbahnen immer kart)')
    ap.add_argument('--gfx', default='', help='Grafikstufe low/high/ultra')
    ap.add_argument('--shot', type=int, default=0, help='Abstand der Prüfbilder in Metern')
    ap.add_argument('--no-static', action='store_true', help='statische Geometrie-Prüfungen weglassen')
    ap.add_argument('--port', type=int, default=8793)
    ap.add_argument('--size', default='1280,720', help='Fenstergröße, z. B. 892,412 fürs Handy-Querformat')
    ap.add_argument('--browser', default='', help='Pfad zu Edge/Chrome')
    ap.add_argument('--timeout', type=int, default=300, help='Sekunden ohne Lebenszeichen, bis eine Strecke neu gestartet wird')
    ap.add_argument('--no-open', action='store_true', help='Bericht am Ende nicht öffnen')
    ap.add_argument('--show', action='store_true', help='sichtbares Browserfenster statt unsichtbarem Betrieb (echte Bildausgabe, misst Ruckler am genauesten)')
    ap.add_argument('--selftest', action='store_true', help='absichtlich ein Loch und eine Doppelfläche einbauen und prüfen, ob der Bot sie findet')
    ap.add_argument('--report', default='', metavar='LAUF', help='nur den Bericht eines früheren Laufs neu erstellen (Ordnername in qc-reports)')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--changed', action='store_true', help='nur Strecken prüfen, die sich seit ihrer letzten Prüfung geändert haben')
    ap.add_argument('--dry', action='store_true', help='mit --changed: nur anzeigen, nichts starten')
    ap.add_argument('--accept', action='store_true', help='aktuellen Stand für diese Strecken als geprüft merken, ohne zu fahren (z. B. nach einem Lauf von Hand)')
    ap.add_argument('--at', default='', metavar='VON-BIS', help='nur diesen Abschnitt prüfen (Streckenmeter, z. B. 2900-3100), dicht mit Rundumblick')
    a = ap.parse_args()

    known = track_keys()
    if a.list:
        for k, n in known:
            print(f'{k:8} {n}')
        return
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()   # dieser Stand wird geprüft (und danach je Strecke gemerkt)
    keys = [k.lower() for k in a.tracks] or [k for k, _ in known]
    bad = [k for k in keys if k not in dict(known)]
    if bad:
        sys.exit('Unbekannt: ' + ', '.join(bad) + ' – bekannt: ' + ', '.join(k for k, _ in known))
    if a.accept:
        CHG.remember(OUT, src, keys); print('Als geprüft gemerkt: ' + ', '.join(keys)); return
    if a.changed:
        ch = CHG.changed_tracks(OUT, src, keys, tempfile.gettempdir())
        if not ch:
            print('Keine Strecke betroffen – alle sind mit dem aktuellen Stand schon geprüft.'); return
        print('Betroffene Strecken:')
        for k, why in ch:
            print(f'  {k:6} ' + why[0] + (f' (+{len(why) - 1} weitere Stellen)' if len(why) > 1 else ''))
        if a.dry: return
        keys = [k for k, _ in ch]
    if a.at:
        if not re.fullmatch(r'\d+-\d+', a.at): sys.exit('--at erwartet VON-BIS in Metern, z. B. 2900-3100')
        if len(keys) != 1: sys.exit('--at gilt für genau eine Strecke, z. B.: python qc/run.py mc --at 2900-3100')

    run = a.report or time.strftime('%Y-%m-%d_%H-%M-%S')
    if a.report:   # Strecken des alten Laufs übernehmen
        keys = [k for k, _ in known if os.path.exists(os.path.join(OUT, run, k + '.json'))]
        if not keys:
            sys.exit('Kein Lauf mit Streckendaten gefunden: qc-reports/' + run)
    os.makedirs(os.path.join(OUT, run), exist_ok=True)
    try:
        srv = Server(('127.0.0.1', a.port), Handler)
    except OSError:
        sys.exit(f'Port {a.port} ist belegt – läuft schon ein QC-Lauf? Erst den beenden (oder --port wählen).')
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    params = {'qc': ','.join(keys), 'srv': '1', 'run': run, 'mode': 'quick' if a.quick else 'full'}
    if a.laps: params['laps'] = a.laps
    if a.ser: params['ser'] = a.ser
    if a.gfx: params['gfx'] = a.gfx
    if a.shot: params['shot'] = a.shot
    if a.no_static: params['static'] = '0'
    if a.selftest: params['selftest'] = '1'
    if a.report: params['report'] = '1'
    if a.at: params['at'] = a.at

    def url(i):
        return f'http://127.0.0.1:{a.port}/index.html?' + '&'.join(f'{k}={v}' for k, v in {**params, 'i': i}.items())

    browser = find_browser(a.browser)
    kill_leftovers('f1qc-')
    profs = []
    w, h = a.size.split(',')

    def launch(i):
        prof = tempfile.mkdtemp(prefix='f1qc-'); profs.append(prof)   # jeder Start mit frischem Profil – sonst übernimmt ein hängender Edge den Neustart
        return subprocess.Popen([browser, f'--user-data-dir={prof}', f'--remote-debugging-port={a.port + 1}', '--no-first-run', '--no-default-browser-check',
                                 # frisches Profil darf sich nicht mit dem Windows-Konto anmelden: sonst kommen Sync und Erweiterungen mit, öffnen eigene Tabs und der Spiel-Tab wird im Hintergrund angehalten
                                 '--disable-extensions', '--disable-component-extensions-with-background-pages', '--disable-sync', '--disable-default-apps',
                                 '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                                 '--disable-backgrounding-occluded-windows', '--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,HighEfficiencyModeAvailable,BatterySaverModeAvailable,msSleepingTabs,msEfficiencyMode,msEdgeSleepingTabs', '--disable-renderer-priority-management',
                                 '--mute-audio', '--enable-precise-memory-info', f'--window-size={w},{h}', '--window-position=40,40',
                                 '--ignore-gpu-blocklist', '--enable-gpu-rasterization'] +
                                (['--headless=new', '--use-angle=d3d11', '--enable-unsafe-swiftshader', url(i)] if not a.show else [f'--app={url(i)}']),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f'QC-Lauf {run}: {len(keys)} Strecke(n) – {", ".join(keys)}')
    print(f'Browser: {browser} ({"sichtbares Fenster" if a.show else "unsichtbar im Hintergrund"})\n', flush=True)
    keep_awake(True)
    cdp = CDP(a.port + 1)
    proc = launch(0)
    t0 = time.time()
    tries = {}
    try:
        while not STATE['done']:
            time.sleep(2)
            quiet = time.time() - STATE['last']
            if quiet > 12 and time.time() - STATE.get('nudged', 0) > 10:
                # Seite still: vom Browser eingefroren? Wieder aufwecken und als sichtbar/fokussiert behandeln lassen
                STATE['nudged'] = time.time()
                try:
                    if cdp.send(('Page.setWebLifecycleState', {'state': 'active'}), ('Emulation.setFocusEmulationEnabled', {'enabled': True})):
                        print(f'  .. {int(quiet)} s still – Seite aufgeweckt', flush=True)
                    elif not STATE.get('crashed'):
                        STATE['crashed'] = True
                        print(f'  .. {int(quiet)} s still – Seite nicht mehr erreichbar (abgestürzt?)', flush=True)
                except Exception as e:
                    print(f'  .. Aufwecken fehlgeschlagen: {e}', flush=True)
            if quiet > a.timeout:
                nxt = len(STATE['tracks_done'])
                name = keys[nxt] if nxt < len(keys) else 'Bericht'
                tries[nxt] = tries.get(nxt, 0) + 1
                kill_tree(proc); kill_leftovers('f1qc-'); time.sleep(3)
                # Neustart für den Bericht festhalten (letzte Meldung zeigt, wo es passierte)
                rs_path = os.path.join(OUT, run, 'restarts.json')
                try: rs = json.load(open(rs_path, encoding='utf-8'))
                except Exception: rs = {}
                rs.setdefault(name, []).append({'crashed': bool(STATE.get('crashed')), 'last': STATE.get('lastline', '')})
                json.dump(rs, open(rs_path, 'w', encoding='utf-8'), ensure_ascii=False)
                if tries[nxt] < 2:
                    print(f'  !! {a.timeout} s ohne Lebenszeichen – {name} wird neu gestartet', flush=True)
                else:
                    print(f'  !! {name} hängt erneut – wird übersprungen', flush=True)
                    if nxt < len(keys):
                        with open(os.path.join(OUT, run, keys[nxt] + '.json'), 'w', encoding='utf-8') as f:
                            json.dump({'key': keys[nxt], 'name': keys[nxt], 'verdict': 'Fehler', 'issues': [{'sev': 'hoch', 'cat': 'Ablauf', 'msg': 'Seite reagierte zweimal nicht mehr (Absturz oder Endlosschleife)', 's': None, 'det': ''}]}, f)
                        STATE['tracks_done'].add(keys[nxt])
                    nxt += 1
                STATE['last'] = time.time()
                proc = launch(nxt)
    except KeyboardInterrupt:
        print('\nAbgebrochen.')
    finally:
        try: kill_tree(proc)
        except Exception: pass
        srv.shutdown()
        keep_awake(False)
        kill_leftovers('f1qc-'); time.sleep(1)
        for p in profs:
            shutil.rmtree(p, ignore_errors=True)

    rep = os.path.join(OUT, run, 'report.html')
    print(f'\nDauer {int(time.time() - t0) // 60} min')
    # geprüften Stand je Strecke merken (für --changed) – nur volle Runden ohne Abbruch, nicht Selbsttest/Abschnitt/Bericht
    if not (a.selftest or a.at or a.report):
        ok = []
        for k in keys:
            try:
                r = json.load(open(os.path.join(OUT, run, k + '.json'), encoding='utf-8'))
                if not any(i.get('cat') == 'Ablauf' for i in r.get('issues', [])): ok.append(k)
            except Exception:
                pass
        if ok: CHG.remember(OUT, src, ok)
    try:
        for r in json.load(open(os.path.join(OUT, run, 'summary.json'), encoding='utf-8')):
            n = {s: sum(1 for i in r['issues'] if i[0] == s) for s in ('hoch', 'mittel', 'info')}
            print(f"  {r['name']:14} {r['verdict']:7} {r.get('fps') or '-':>5} fps  p99 {r.get('p99') or '-':>5} ms   hoch {n['hoch']}  mittel {n['mittel']}  info {n['info']}")
    except Exception:
        pass
    if os.path.exists(rep):
        print('Bericht: ' + rep)
        if not a.no_open:
            webbrowser.open('file:///' + rep.replace('\\', '/'))


if __name__ == '__main__':
    main()
