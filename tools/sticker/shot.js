#!/usr/bin/env node
/* Auto im Showroom des Spiels aufnehmen:  node tools/sticker/shot.js <Kürzel> <Ausgabe-Vorsilbe> [Ansichten]
   Ansichten (durch Komma getrennt, Standard L,R): L / R = ganze linke / rechte Seite, Lf Lm Lr / Rf Rm Rr = vorderes, mittleres, hinteres Drittel vergrößert,
   top = von oben, f34 / r34 = schräg von vorn / hinten. Ergebnis: <Vorsilbe>_<Ansicht>.png (1280 x 640).
   Liest tools/sticker/<Kürzel>.json (F2: zusätzlich "team": "F2_INV" und "driver": "CAM"). Braucht keinen Server: die Dateien kommen direkt aus dem Projektordner. */
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..'); const [key, out, views = 'L,R'] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(path.join(__dirname, key + '.json'), 'utf8'));
const V = { L: [[30, 0.9, 0.35], [0, 0.55, 0.35], 6], Lf: [[14, 1.0, 1.9], [0, 0.45, 1.9], 5], Lm: [[14, 1.1, 0.2], [0, 0.6, 0.2], 5], Lr: [[14, 1.1, -1.5], [0, 0.65, -1.5], 5],
  top: [[0.01, 24, 0.3], [0, 0.5, 0.3], 8], f34: [[9, 3, 12], [0, 0.5, 0.5], 14], r34: [[9, 3, -12], [0, 0.5, -0.3], 14] };
for (const k of ['L', 'Lf', 'Lm', 'Lr', 'f34', 'r34']) V[k.replace('L', 'R').replace(/^([fr])34$/, '$134R')] = [[-V[k][0][0], V[k][0][1], V[k][0][2]], V[k][1], V[k][2]];
const MIME = { html: 'text/html', js: 'text/javascript', json: 'application/json', png: 'image/png', jpg: 'image/jpeg', bin: 'application/octet-stream', mp3: 'audio/mpeg', webmanifest: 'application/manifest+json', svg: 'image/svg+xml' };
// Höchstens zwei Aufnahmen gleichzeitig (jede braucht viel Rechenzeit): Platz in /tmp/f1shot-slots belegen, sonst warten
const SLOTS = '/tmp/f1shot-slots'; let slot = null;
async function takeSlot() { fs.mkdirSync(SLOTS, { recursive: true });
  for (;;) { for (let i = 0; i < 2; i++) { const f = path.join(SLOTS, 's' + i);
      try { fs.writeFileSync(f, String(process.pid), { flag: 'wx' }); slot = f; return; } catch (e) { try { process.kill(+fs.readFileSync(f, 'utf8'), 0); } catch (e2) { try { fs.unlinkSync(f); } catch (e3) {} } } }
    await new Promise(r => setTimeout(r, 4000)); } }
const freeSlot = () => { if (slot) { try { fs.unlinkSync(slot); } catch (e) {} slot = null; } };
process.on('exit', freeSlot); process.on('SIGTERM', () => process.exit(1)); process.on('SIGINT', () => process.exit(1));
(async () => {
  await takeSlot();
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 640 } });
  p.setDefaultTimeout(240000);   // Aufnahmen brauchen unter Last lange
  p.on('pageerror', e => console.log('SEITENFEHLER', String(e).slice(0, 500)));
  p.on('console', m => { const t = m.text(); if (/THREE\.WebGLProgram|shader error|ERROR:/i.test(t)) console.log('SHADER', t.slice(0, 1500)); });
  await p.route('http://f1.test/**', async r => {
    let f = decodeURIComponent(new URL(r.request().url()).pathname); if (f === '/') f = '/index.html'; const full = path.join(ROOT, f);
    if (!full.startsWith(ROOT) || !fs.existsSync(full) || f === '/sw.js') return r.fulfill({ status: 404, body: '' });
    let body = fs.readFileSync(full);
    if (f === '/index.html') { let s = body.toString('utf8');
      const a = 'cam.setViewOffset(W2, H2, SHOW.ox * W2, SHOW.oy * H2, W2, H2); cam.updateProjectionMatrix();', c = 'const SHOW = {';
      if (!s.includes(a) || !s.includes(c)) console.log('WARNUNG: Einhängepunkte in index.html nicht gefunden');
      s = s.replace(a, a + ' if (window.__shotCam) { const q = window.__shotCam; cam.position.set(...q.p).applyMatrix4(SHOW.stage.matrixWorld); cam.clearViewOffset(); cam.fov = q.fov; cam.updateProjectionMatrix(); cam.lookAt(new THREE.Vector3(...q.t).applyMatrix4(SHOW.stage.matrixWorld)); }')
        .replace(c, 'window.__stkEval = q => eval(q); ' + c); body = s; }
    await r.fulfill({ body, contentType: MIME[f.split('.').pop()] || 'application/octet-stream' });
  });
  await p.goto('http://f1.test/index.html', { waitUntil: 'load', timeout: 180000 });
  const ser = cfg.kind, team = cfg.team || key, drv = cfg.driver || '';
  const cmd = `setSeries(${JSON.stringify(ser)}, true); S.team = ${JSON.stringify(team)}; ${drv ? 'S.driver = ' + JSON.stringify(drv) + ';' : ''} SHOW.team = null; showroomTeam(${JSON.stringify(team)}); SHOW.cars.map(m => m.code + ':' + m.g.visible).join(',')`;
  let ok = null;
  for (let i = 0; i < 90 && ok === null; i++) { await p.waitForTimeout(2000); ok = await p.evaluate(c => { try { return window.__stkEval ? String(window.__stkEval(c)) : null; } catch (e) { return null; } }, cmd); }
  console.log('Showroom:', ok);
  await p.addStyleTag({ content: '#menu{visibility:hidden!important}' });
  await p.waitForTimeout(6000);
  for (const k of views.split(',')) { if (!V[k]) { console.log('unbekannte Ansicht', k); continue; }
    const [mp, mt, fov] = V[k];   // Modell (x quer, y hoch, z vorn) -> Bühne (-z, y, x)
    await p.evaluate(c => { window.__shotCam = c; }, { p: [-mp[2], mp[1], mp[0]], t: [-mt[2], mt[1], mt[0]], fov }); await p.waitForTimeout(1800);
    await p.screenshot({ path: out + '_' + k + '.png' }); console.log('->', out + '_' + k + '.png'); }
  await b.close();
})();
