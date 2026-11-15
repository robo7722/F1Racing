"""Strecke im unsichtbaren Edge bauen, Konsolenbefehle ausführen und Bilder aufnehmen (für das Bauen neuer Strecken).

    python qc/probe.py zan --view 0,0,4,60,0,1 --view 1200,-30,60,1300,0,0 --out shots
    python qc/probe.py zan --eval "__clipAll().length" --eval "__dbg().L"
    python qc/probe.py zan --top 1500,250            Draufsicht über Streckenmeter 1500 aus 250 m Höhe
    python qc/probe.py zan --race --eval "__bench()"   Rennen mit vollem Feld starten (Zeichenaufrufe messen)
    python qc/probe.py zan --script probe.js           eigenes Skript (async, darf await nutzen; `shot(name)` nimmt ein Bild auf)

Jeder Bot nimmt einen eigenen --port (Standard 8850; der Port +1 ist der DevTools-Port).
Bilder landen in --out (Standard qc-reports/probe/<strecke>/), Ergebnisse von --eval als JSON auf stdout.
"""
import argparse, base64, json, os, socket, struct, subprocess, sys, tempfile, threading, time, urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import find_browser, kill_tree, kill_leftovers   # noqa: E402


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass


class WS:
    """Minimaler DevTools-WebSocket mit Antworten."""
    def __init__(self, url):
        u = urlparse(url)
        self.s = socket.create_connection((u.hostname, u.port), timeout=600)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f'GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
                        f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        r = b''
        while b'\r\n\r\n' not in r:
            r += self.s.recv(4096)
        self.buf = r.split(b'\r\n\r\n', 1)[1]
        self.id = 0
        self.exc = []

    def _recv(self, n):
        while len(self.buf) < n:
            d = self.s.recv(1 << 20)
            if not d:
                raise ConnectionError('DevTools-Verbindung beendet')
            self.buf += d
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _frame(self):
        b0, b1 = self._recv(2)
        n = b1 & 0x7f
        if n == 126:
            n = struct.unpack('>H', self._recv(2))[0]
        elif n == 127:
            n = struct.unpack('>Q', self._recv(8))[0]
        return b0 & 0x0f, self._recv(n)

    def call(self, method, params=None):
        self.id += 1
        data = json.dumps({'id': self.id, 'method': method, 'params': params or {}}).encode()
        mask = os.urandom(4)
        n = len(data)
        head = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536 else bytes([0x80 | 127]) + struct.pack('>Q', n))
        self.s.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
        msg = b''
        while True:
            op, pl = self._frame()
            msg += pl
            if op == 0:   # Fortsetzung
                continue
            try:
                j = json.loads(msg)
            except Exception:
                continue
            msg = b''
            if j.get('method') == 'Runtime.exceptionThrown':
                d = j['params']['exceptionDetails']
                self.exc.append(((d.get('exception') or {}).get('description') or d.get('text') or '')[:400] + f" @{d.get('lineNumber')}:{d.get('columnNumber')}")
            if j.get('id') == self.id:
                if 'error' in j:
                    raise RuntimeError(j['error'])
                return j.get('result', {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('track')
    ap.add_argument('--port', type=int, default=8850)
    ap.add_argument('--gfx', default='high')
    ap.add_argument('--size', default='1280,720')
    ap.add_argument('--view', action='append', default=[], help='s,lat,h,s2,lat2,h2 (wie __view)')
    ap.add_argument('--top', action='append', default=[], help='s,höhe[,lat] Draufsicht')
    ap.add_argument('--cam', action='append', default=[], help='x,y,z,tx,ty,tz feste Kamera in Weltkoordinaten')
    ap.add_argument('--eval', action='append', default=[], help='JS-Ausdruck (darf Promise liefern)')
    ap.add_argument('--script', default='', help='JS-Datei, läuft als async-Funktion; shot(name) nimmt ein Bild auf')
    ap.add_argument('--race', action='store_true', help='nach dem Bau ein F1-Rennen mit vollem Feld starten')
    ap.add_argument('--ser', default='f1')
    ap.add_argument('--out', default='')
    ap.add_argument('--browser', default='')
    ap.add_argument('--timeout', type=int, default=240)
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, 'qc-reports', 'probe', a.track)
    os.makedirs(out, exist_ok=True)
    try:
        srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    except OSError:
        sys.exit(f'Port {a.port} belegt – anderen --port wählen.')
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    browser = find_browser(a.browser)
    pre = f'f1qc-{a.port}-'
    kill_leftovers(pre)
    prof = tempfile.mkdtemp(prefix=pre)
    w, h = a.size.split(',')
    url = f'http://127.0.0.1:{a.port}/index.html?qc=none&probe={int(time.time())}'
    proc = subprocess.Popen([browser, f'--user-data-dir={prof}', f'--remote-debugging-port={a.port + 1}', '--no-first-run', '--no-default-browser-check',
                             '--disable-extensions', '--disable-sync', '--disable-default-apps', '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
                             '--disable-backgrounding-occluded-windows', '--mute-audio', f'--window-size={w},{h}', '--ignore-gpu-blocklist',
                             '--headless=new', '--use-angle=d3d11', '--enable-unsafe-swiftshader', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ws = None
    try:
        for _ in range(60):
            try:
                for t in json.load(urllib.request.urlopen(f'http://127.0.0.1:{a.port + 1}/json', timeout=3)):
                    if t.get('type') == 'page' and 'index.html' in t.get('url', ''):
                        ws = WS(t['webSocketDebuggerUrl'])
                break
            except Exception:
                time.sleep(0.5)
        if not ws:
            sys.exit('Edge nicht erreichbar')
        ws.call('Runtime.enable')
        ws.call('Page.enable')
        ws.call('Page.reload', {'ignoreCache': True})   # Seite neu laden, damit Ladefehler (Syntaxfehler) als Ereignis ankommen
        time.sleep(1.5)
        ws.call('Page.setWebLifecycleState', {'state': 'active'})
        ws.call('Emulation.setFocusEmulationEnabled', {'enabled': True})

        def ev(expr, wait=True):
            r = ws.call('Runtime.evaluate', {'expression': expr, 'awaitPromise': wait, 'returnByValue': True, 'timeout': a.timeout * 1000})
            if 'exceptionDetails' in r:
                d = r['exceptionDetails']
                raise RuntimeError((d.get('exception') or {}).get('description') or d.get('text'))
            return (r.get('result') or {}).get('value')

        t0 = time.time()
        while not ev("typeof window.__build === 'function' && typeof window.__race === 'function' && !!window.__dbg"):
            if time.time() - t0 > 90:
                sys.exit('Spiel lädt nicht (index.html-Fehler?): ' + json.dumps(ws.exc, ensure_ascii=False))
            time.sleep(0.5)
        # Fehler der Seite mitschreiben
        ev("window.__perr = []; addEventListener('error', e => window.__perr.push(String(e.message) + ' @' + (e.lineno || '')));"
           "const _ce = console.error; console.error = (...x) => { window.__perr.push(x.map(String).join(' ').slice(0, 300)); _ce(...x); }; 1")
        if a.gfx != 'high':   # Grafikstufe über die Einstellungen setzen (ein URL-Parameter lud die Seite neu)
            ev(f"(window.__S().gfx = {json.dumps(a.gfx)}, 1)")
        t1 = time.time()
        if a.race:
            name = ev(f"__build({json.dumps(a.track)})")   # Name der Strecke (TRACKS ist nicht global)
            ok = ev(f"__race({json.dumps(name)}, {json.dumps(a.ser)})")
            print(json.dumps({'race': ok}))
        else:
            ev(f"__build({json.dumps(a.track)})")
            ev("document.getElementById('menu').classList.add('hidden'); document.querySelectorAll('.overlay').forEach(o => o.classList.add('hidden')); 1")
        ev("new Promise(r => setTimeout(r, 2500))")   # Texturen / Fotoasphalt nachladen
        print(json.dumps({'build_s': round(time.time() - t1, 1), 'btms': ev("window.__btms || null"), 'L': ev("__dbg().L")}), flush=True)

        def shot(name):
            ev("__frame(3)")
            time.sleep(1.0)
            ev("__frame(2)")
            time.sleep(0.4)
            d = ws.call('Page.captureScreenshot', {'format': 'jpeg', 'quality': 82})
            p = os.path.join(out, name + '.jpg')
            with open(p, 'wb') as f:
                f.write(base64.b64decode(d['data']))
            print(json.dumps({'shot': p, 'ri': ev("__ri ? __ri() : null")}), flush=True)

        for k, v in enumerate(a.view):
            ev(f"__view({v})")
            shot(f'view{k}_' + v.replace(',', '_').replace('-', 'm').replace('.', 'p'))
        for k, v in enumerate(a.top):
            q = [float(x) for x in v.split(',')]
            s, hh, lat = q[0], q[1], (q[2] if len(q) > 2 else 0)
            ev(f"(() => {{ const p = __tAt({s}, {lat}); window.__camFix = {{ p: [p[0], p[1] + {hh}, p[2] + 0.01], t: [p[0], p[1], p[2]] }}; }})()")
            shot(f'top{k}_{int(s)}_{int(hh)}')
        for k, v in enumerate(a.cam):
            q = [float(x) for x in v.split(',')]
            ev(f"window.__camFix = {{ p: [{q[0]}, {q[1]}, {q[2]}], t: [{q[3]}, {q[4]}, {q[5]}] }}")
            shot(f'cam{k}')
        for e in a.eval:
            try:
                print(json.dumps({'eval': e, 'value': ev(e)}, ensure_ascii=False, default=str)[:20000], flush=True)
            except Exception as ex:
                print(json.dumps({'eval': e, 'error': str(ex)[:2000]}, ensure_ascii=False), flush=True)
        if a.script:
            src = open(a.script, encoding='utf-8').read()
            # shot() aus dem Skript: Promise, das Python per Polling bedient
            ev("window.__shotQ = []; window.shot = n => new Promise(r => window.__shotQ.push([n, r])); 1")
            ev(f"window.__scrDone = false; window.__scrRes = null; (async () => {{ {src}\n }})().then(v => {{ window.__scrRes = v; }}, e => {{ window.__scrRes = 'FEHLER: ' + (e && e.stack || e); }}).finally(() => {{ window.__scrDone = true; }}); 1", wait=False)
            t2 = time.time()
            while True:
                q = ev("window.__shotQ.length ? window.__shotQ[0][0] : null")
                if q is not None:
                    shot(str(q))
                    ev("window.__shotQ.shift()[1](); 1")
                    continue
                if ev("window.__scrDone"):
                    break
                if time.time() - t2 > a.timeout:
                    print('Skript-Zeitlimit'); break
                time.sleep(0.2)
            print(json.dumps({'script': ev("window.__scrRes")}, ensure_ascii=False, default=str)[:20000])
        print(json.dumps({'page_errors': ev("window.__perr")}, ensure_ascii=False)[:6000])
    finally:
        try:
            kill_tree(proc)
        except Exception:
            pass
        kill_leftovers(pre)
        srv.shutdown()


if __name__ == '__main__':
    main()
