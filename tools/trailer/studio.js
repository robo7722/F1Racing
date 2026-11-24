// Trailer-Studio: startet das echte Spiel im Testbrowser, baut eine Strecke und bleibt offen. Über einen kleinen lokalen Dienst
// lassen sich dann beliebig viele Einstellungen ausprobieren und Bilder aufnehmen, ohne die Strecke jedes Mal neu zu bauen (~2 min).
//   node tools/trailer/studio.js --port 8801 --strecke Spa [--klasse f1|f2|kart] [--fahrer VER] [--wetter dry|light|heavy] [--gfx ultra] [--size 1920,804] [--dpr 1] [--menue]
//   --menue: keine Strecke bauen, im Hauptmenü bleiben (Showroom-Bilder)
// Bedienen (siehe tools/trailer/README.md):
//   curl -s localhost:8801/eval --data 'pl.v'                      → wertet Code im Spiel aus (Modul-Bereich von index.html)
//   curl -s localhost:8801/bild --data '{"datei":"/pfad/a.png"}'   → Bild der Seite speichern (optional "clip":[x,y,w,h], "jpg":90)
//   curl -s localhost:8801/ende
// Am Spiel wird nichts geändert: die Einhängepunkte (Kamera mit Brennweite/Neigung, Haken vor dem Zeichnen) werden nur beim Laden im Testbrowser eingesetzt.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const http = require('http');
const ROOT = path.resolve(__dirname, '../..');
const MIME = { html: 'text/html', js: 'text/javascript', json: 'application/json', png: 'image/png', jpg: 'image/jpeg', bin: 'application/octet-stream', mp3: 'audio/mpeg', webmanifest: 'application/manifest+json', svg: 'image/svg+xml', glb: 'model/gltf-binary', wav: 'audio/wav' };
const a = process.argv.slice(2), flag = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : a[i + 1]; }, has = n => a.includes('--' + n);
const PORT = +flag('port', 8801), TRK = flag('strecke', 'Spa'), SER = flag('klasse', 'f1'), DRV = flag('fahrer', 'VER'), WXK = flag('wetter', 'dry'), GFX = flag('gfx', 'ultra');
const SIZE = flag('size', '1920,804').split(',').map(Number), DPR = +flag('dpr', 1), MENUE = has('menue');
const T0 = Date.now(), T = () => ((Date.now() - T0) / 1000).toFixed(0) + ' s';

// Einhängepunkte, die beim Laden in index.html eingesetzt werden (nur im Testbrowser)
const PATCH = [
  ['const SHOW = {', 'window.__stkEval = q => eval(q); const SHOW = {'],
  // feste Kamera: zusätzlich Brennweite (fov), Neigung (roll)
  ['if (window.__camFix) { const f = window.__camFix; camera.position.set(...f.p); camera.lookAt(...f.t); camera.updateMatrixWorld(); }',
    'if (window.__camFix) { const f = typeof window.__camFix === "function" ? window.__camFix(dt, now) : window.__camFix; if (f) { camera.position.set(...f.p); camera.up.set(0, 1, 0); camera.lookAt(...f.t); if (f.roll) camera.rotateZ(f.roll); if (f.fov) { camera.fov = f.fov; camera.updateProjectionMatrix(); } camera.updateMatrixWorld(); } }'],
  // Haken unmittelbar vor dem Zeichnen (Effekte überschreiben)
  ['const tR0 = performance.now(); PERF.rT = 0;', 'if (window.__trPre) window.__trPre(dt, now); const tR0 = performance.now(); PERF.rT = 0;'],
];

(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: SIZE[0], height: SIZE[1] }, deviceScaleFactor: DPR });
  await ctx.addInitScript(([drv, gfx]) => { try { const s = JSON.parse(localStorage.getItem('f1rennen') || '{}'); Object.assign(s, { driver: drv, gfx, sound: false, music: false, cam: 0, line: 'off', perfHud: false, rone: true, nos: true }); localStorage.setItem('f1rennen', JSON.stringify(s)); } catch (e) {} }, [DRV, GFX]);
  const p = await ctx.newPage(); p.setDefaultTimeout(900000);
  p.on('pageerror', e => console.log('SEITENFEHLER', String(e).slice(0, 500)));
  p.on('console', m => { const t = m.text(); if (/THREE\.WebGLProgram|shader error|ERROR:/i.test(t)) console.log('SHADER', t.slice(0, 800)); });
  await p.route('http://f1.test/**', async r => {
    let f = decodeURIComponent(new URL(r.request().url()).pathname); if (f === '/') f = '/index.html'; const full = path.join(ROOT, f);
    if (!full.startsWith(ROOT) || !fs.existsSync(full) || f === '/sw.js') return r.fulfill({ status: 404, body: '' });
    let body = fs.readFileSync(full);
    if (f === '/index.html') { let s = body.toString('utf8'); for (const [von, nach] of PATCH) { if (!s.includes(von)) console.log('WARNUNG: Einhängepunkt fehlt:', von.slice(0, 60)); s = s.replace(von, nach); } body = s; }
    await r.fulfill({ body, contentType: MIME[f.split('.').pop()] || 'application/octet-stream' });
  });
  await p.goto('http://f1.test/index.html' + (MENUE ? '?mitpre' : '?qc=none&nopre'), { waitUntil: 'load', timeout: 600000 });
  await p.waitForFunction(() => typeof window.__stkEval === 'function' && typeof window.__race === 'function', null, { timeout: 900000 });
  const ev = code => p.evaluate(c => window.__stkEval(c), code);
  await p.waitForTimeout(1500); console.log(T(), 'Spiel geladen');
  if (!MENUE) {
    await ev(`if (S.gfx !== ${JSON.stringify(GFX)}) { S.gfx = ${JSON.stringify(GFX)}; applyGfx(); } window.__wxForce = ${JSON.stringify(WXK)}; window.__noWarm = true; S.sound = false; S.music = false; 1`);
    const ok = await p.evaluate(([t, s]) => window.__race(t, s), [TRK, SER]);
    console.log(T(), 'Rennen läuft:', ok, await ev(`TRK.name + ' · ' + SER + ' · ' + (pl && pl.code) + ' · Wetter ' + WX.cur + ' · L=' + Math.round(L) + ' m · Autos ' + cars.length`));
    await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
  }
  await ev(fs.readFileSync(path.join(__dirname, 'studio_spiel.js'), 'utf8') + '; TR.halt(); 1');
  if (MENUE) await ev(fs.readFileSync(path.join(__dirname, 'studio_showroom.js'), 'utf8') + '; 1');
  const srv = http.createServer((req, res) => { let d = ''; req.on('data', c => d += c); req.on('end', async () => {
    try {
      if (req.url === '/eval') { const r = await ev(d); res.end(typeof r === 'string' ? r : JSON.stringify(r)); }
      else if (req.url === '/bild') { const q = JSON.parse(d), o = { path: q.datei }; if (q.clip) o.clip = { x: q.clip[0], y: q.clip[1], width: q.clip[2], height: q.clip[3] }; if (q.jpg) { o.type = 'jpeg'; o.quality = q.jpg; } await p.screenshot(o); res.end('ok ' + q.datei); }
      else if (req.url === '/ende') { res.end('ende'); await b.close(); process.exit(0); }
      else { res.statusCode = 404; res.end('?'); }
    } catch (e) { res.statusCode = 500; res.end('FEHLER ' + String(e).slice(0, 1500)); } }); });
  srv.listen(PORT, '127.0.0.1', () => console.log(T(), 'BEREIT auf Port', PORT));
})().catch(e => { console.error(e); process.exit(1); });
