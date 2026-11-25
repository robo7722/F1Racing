// Gemeinsamer Starter für Trailer-Aufnahmen: echtes Spiel im Testbrowser, mit Einhängepunkten nur für die Aufnahme (index.html bleibt unverändert).
//   const { starte } = require('./spielstart.js'); const g = await starte({ size: [1920, 804], fahrer: 'VER', menue: false });
//   await g.rennen('Singapur', { fahrer: 'NOR', wetter: 'heavy', klasse: 'f1' });   // baut die Strecke (nur beim ersten Mal) und startet ein Rennen, Bildschleife danach angehalten
//   await g.ev('TR.info()');  await g.zumMenue();  await g.b.close();
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..');
const MIME = { html: 'text/html', js: 'text/javascript', json: 'application/json', png: 'image/png', jpg: 'image/jpeg', bin: 'application/octet-stream', mp3: 'audio/mpeg', webmanifest: 'application/manifest+json', svg: 'image/svg+xml', glb: 'model/gltf-binary', wav: 'audio/wav' };
// Einhängepunkte, die beim Laden in index.html eingesetzt werden (nur im Testbrowser)
const PATCH = [
  ['const SHOW = {', 'window.__stkEval = q => eval(q); const SHOW = {'],
  // feste Kamera: Funktion erlaubt, zusätzlich Brennweite (fov) und Neigung (roll)
  ['if (window.__camFix) { const f = window.__camFix; camera.position.set(...f.p); camera.lookAt(...f.t); camera.updateMatrixWorld(); }',
    'if (window.__camFix) { const f = typeof window.__camFix === "function" ? window.__camFix(dt, now) : window.__camFix; if (f) { camera.position.set(...f.p); camera.up.set(0, 1, 0); camera.lookAt(...f.t); if (f.roll) camera.rotateZ(f.roll); if (f.fov) { camera.fov = f.fov; camera.updateProjectionMatrix(); } camera.updateMatrixWorld(); } }'],
  // Haken unmittelbar vor dem Zeichnen (Effekte überschreiben)
  ['const tR0 = performance.now(); PERF.rT = 0;', 'if (window.__trPre) window.__trPre(dt, now); const tR0 = performance.now(); PERF.rT = 0;'],
  // Kantenglättung des Zwischenbilds einstellbar (für Messungen und Mehrfachbelichtung)
  ['{ type: THREE.HalfFloatType, samples: ultra || !isTouch ? 4 : 2 }', '{ type: THREE.HalfFloatType, samples: window.__trMSAA ?? (ultra || !isTouch ? 4 : 2) }'],
];
async function starte({ size = [1920, 804], dpr = 1, menue = false, fahrer = 'VER', gfx = 'ultra', log = console.log } = {}) {
  const T0 = Date.now(), T = () => ((Date.now() - T0) / 1000).toFixed(0) + ' s';
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: size[0], height: size[1] }, deviceScaleFactor: dpr });
  await ctx.addInitScript(([drv, gfx]) => { try { const s = JSON.parse(localStorage.getItem('f1rennen') || '{}'); Object.assign(s, { driver: drv, gfx, sound: false, music: false, cam: 0, line: 'off', perfHud: false, rone: true, nos: true }); localStorage.setItem('f1rennen', JSON.stringify(s)); } catch (e) {} }, [fahrer, gfx]);
  const p = await ctx.newPage(); p.setDefaultTimeout(1800000);
  p.on('pageerror', e => log('SEITENFEHLER', String(e).slice(0, 400)));
  p.on('console', m => { const t = m.text(); if (/THREE\.WebGLProgram|shader error|ERROR:/i.test(t)) log('SHADER', t.slice(0, 600)); });
  await p.route('http://f1.test/**', async r => {
    let f = decodeURIComponent(new URL(r.request().url()).pathname); if (f === '/') f = '/index.html'; const full = path.join(ROOT, f);
    if (!full.startsWith(ROOT) || !fs.existsSync(full) || f === '/sw.js') return r.fulfill({ status: 404, body: '' });
    let body = fs.readFileSync(full);
    if (f === '/index.html') { let s = body.toString('utf8'); for (const [von, nach] of PATCH) { if (!s.includes(von)) log('WARNUNG: Einhängepunkt fehlt:', von.slice(0, 60)); s = s.replace(von, nach); } body = s; }
    await r.fulfill({ body, contentType: MIME[f.split('.').pop()] || 'application/octet-stream' });
  });
  await p.goto('http://f1.test/index.html' + (menue ? '?mitpre' : '?qc=none&nopre'), { waitUntil: 'load', timeout: 900000 });
  await p.waitForFunction(() => typeof window.__stkEval === 'function' && typeof window.__race === 'function', null, { timeout: 1800000 });
  const ev = code => p.evaluate(c => window.__stkEval(c), code);
  await p.waitForTimeout(1500);
  await ev(fs.readFileSync(path.join(__dirname, 'studio_spiel.js'), 'utf8') + '; 1');
  if (menue) { await ev(fs.readFileSync(path.join(__dirname, 'studio_showroom.js'), 'utf8') + '; TR.halt(); 1'); log(T(), 'Menü bereit'); }
  let lief = false;
  // Rennen starten (weitere Rennen in derselben Sitzung ohne Neuladen; die Strecke wird nur gebaut, wenn sie wechselt)
  const rennen = async (strecke, { fahrer: drv, wetter = 'dry', klasse = 'f1' } = {}) => {
    if (lief) { await ev(`TR.weiter(); toMenu(); 1`); await p.waitForTimeout(1200); }
    await ev(`if (S.gfx !== ${JSON.stringify(gfx)}) { S.gfx = ${JSON.stringify(gfx)}; applyGfx(); } window.__wxForce = ${JSON.stringify(wetter)}; window.__noWarm = true; S.sound = false; S.music = false; S.cam = 0;
      ${drv ? `if (byCode(${JSON.stringify(drv)})) { S.driver = ${JSON.stringify(drv)}; MENU.team = byCode(${JSON.stringify(drv)}).team; }` : ''} save(); 1`);
    const ok = await p.evaluate(([t, s]) => window.__race(t, s), [strecke, klasse]); lief = true;
    await p.waitForFunction(() => document.querySelector('#loading').classList.contains('hidden'), null, { timeout: 1800000 });
    await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
    const info = await ev(`TR.halt(); TR.hud(false); TRK.name + ' · ' + SER + ' · ' + (pl && pl.code) + ' · Wetter ' + WX.cur + ' · L=' + Math.round(L) + ' m · Autos ' + cars.length`);
    log(T(), 'Rennen läuft:', ok, info); return ok;
  };
  return { b, p, ev, rennen, T };
}
module.exports = { starte, ROOT };
