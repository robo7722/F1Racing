// Gemeinsamer Starter für die Textur-Werkzeuge: öffnet das Spiel im Testbrowser (Dateien direkt aus dem Projektordner, ohne Server)
// und stellt window.__stkEval(code) bereit – wertet Code im Modul-Bereich von index.html aus (Zugriff auf MODELS, teamTemplate, renderer, …).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const MIME = { html: 'text/html', js: 'text/javascript', json: 'application/json', png: 'image/png', jpg: 'image/jpeg', bin: 'application/octet-stream', mp3: 'audio/mpeg', webmanifest: 'application/manifest+json', svg: 'image/svg+xml', glb: 'model/gltf-binary', wav: 'audio/wav' };
async function spiel({ w = 1280, h = 640, query = '' } = {}) {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: w, height: h } }); p.setDefaultTimeout(600000);
  p.on('pageerror', e => console.log('SEITENFEHLER', String(e).slice(0, 500)));
  p.on('console', m => { const t = m.text(); if (/THREE\.WebGLProgram|shader error|ERROR:/i.test(t)) console.log('SHADER', t.slice(0, 1500)); });
  await p.route('http://f1.test/**', async r => {
    let f = decodeURIComponent(new URL(r.request().url()).pathname); if (f === '/') f = '/index.html'; const full = path.join(ROOT, f);
    if (!full.startsWith(ROOT) || !fs.existsSync(full) || f === '/sw.js') return r.fulfill({ status: 404, body: '' });
    let body = fs.readFileSync(full);
    if (f === '/index.html') { const s = body.toString('utf8'), c = 'const SHOW = {'; if (!s.includes(c)) console.log('WARNUNG: Einhängepunkt fehlt'); body = s.replace(c, 'window.__stkEval = q => eval(q); ' + c); }
    await r.fulfill({ body, contentType: MIME[f.split('.').pop()] || 'application/octet-stream' });
  });
  await p.goto('http://f1.test/index.html' + query, { waitUntil: 'load', timeout: 300000 });
  await p.waitForFunction(() => typeof window.__stkEval === 'function', null, { timeout: 300000 });
  const ev = (code, arg) => p.evaluate(([c, a]) => { window.__arg = a; return window.__stkEval(c); }, [code, arg]);
  return { b, p, ev };
}
module.exports = { spiel, ROOT };
