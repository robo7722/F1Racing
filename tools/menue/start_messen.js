// Misst den ersten Start bis ins Hauptmenü: Wie lange dauert der Ladebildschirm, und was passiert danach noch im Hauptmenü (lange Aufgaben im Hauptprogramm,
// Bildabstände, neu übersetzte Shader, neue Texturen/Geometrien)? Ziel: Nach dem Ladebildschirm darf nichts mehr nachgeladen oder übersetzt werden.
//   node tools/menue/start_messen.js [Sekunden im Menü = 25] [BreitexHöhe = 852x393]
// Hinweis: Der Testbrowser rechnet die Grafik per Software – Zeiten sind nur untereinander vergleichbar; entscheidend sind Anzahl und Zeitpunkt der langen Aufgaben
// und ob Shader/Texturen/Geometrien nach dem Einblenden des Menüs noch zunehmen.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const ROOT = path.resolve(__dirname, '../..');
const MIME = { html: 'text/html', js: 'text/javascript', json: 'application/json', png: 'image/png', jpg: 'image/jpeg', bin: 'application/octet-stream', mp3: 'audio/mpeg', webmanifest: 'application/manifest+json', svg: 'image/svg+xml', glb: 'model/gltf-binary', wav: 'audio/wav' };
(async () => { const secs = +(process.argv[2] || 25), [w, h] = (process.argv[3] || '852x393').split('x').map(Number);
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: w, height: h } }); p.setDefaultTimeout(600000);
  p.on('pageerror', e => console.log('SEITENFEHLER', String(e).slice(0, 300)));
  await p.route('http://f1.test/**', async r => { let f = decodeURIComponent(new URL(r.request().url()).pathname); if (f === '/') f = '/index.html'; const full = path.join(ROOT, f);
    if (!full.startsWith(ROOT) || !fs.existsSync(full) || f === '/sw.js') return r.fulfill({ status: 404, body: '' }); let body = fs.readFileSync(full);
    if (f === '/index.html') body = body.toString('utf8').replace('const SHOW = {', 'window.__stkEval = q => eval(q); const SHOW = {');
    await r.fulfill({ body, contentType: MIME[f.split('.').pop()] || 'application/octet-stream' }); });
  await p.addInitScript(() => { const M = window.__M = { t0: performance.now(), long: [], gaps: [], menu: 0, last: 0 };
    try { new PerformanceObserver(l => { for (const e of l.getEntries()) M.long.push([Math.round(e.startTime), Math.round(e.duration)]); }).observe({ entryTypes: ['longtask'] }); } catch (e) {}
    const loop = t => { if (M.last && t - M.last > 50) M.gaps.push([Math.round(t), Math.round(t - M.last)]); M.last = t; const L = document.querySelector('#loading'); if (!M.menu && L && L.classList.contains('hidden') && document.querySelector('#menu') && !document.querySelector('#menu').classList.contains('hidden')) M.menu = t; requestAnimationFrame(loop); }; requestAnimationFrame(loop); });
  await p.goto('http://f1.test/index.html?qc=none&mitpre', { waitUntil: 'load', timeout: 300000 });   // mitpre: das Vorbereiten im Ladebildschirm läuft wie beim Spieler (Werkzeug-Adressen mit ?qc= überspringen es sonst)
  await p.waitForFunction(() => window.__M && window.__M.menu > 0, null, { timeout: 600000 });
  const snap = () => p.evaluate(() => { const r = window.__stkEval('renderer'); return { prog: r.info.programs.length, tex: r.info.memory.textures, geo: r.info.memory.geometries }; });
  const s0 = await snap(); await p.waitForTimeout(secs * 1000); const s1 = await snap();
  const M = await p.evaluate(() => ({ ...window.__M, pre: window.__preLog || null, lade: window.__ladeLog || null }));
  const after = x => x.filter(e => e[0] > M.menu), sum = x => x.reduce((s, e) => s + e[1], 0), la = after(M.long), ga = after(M.gaps);
  console.log('Ladebildschirm bis Menü sichtbar: ' + (M.menu / 1000).toFixed(1) + ' s');
  console.log('im Menü (' + secs + ' s): ' + la.length + ' lange Aufgaben, zusammen ' + sum(la) + ' ms, längste ' + Math.max(0, ...la.map(e => e[1])) + ' ms · ' + ga.length + ' Bildabstände über 50 ms, längster ' + Math.max(0, ...ga.map(e => e[1])) + ' ms');
  console.log('Shader ' + s0.prog + ' → ' + s1.prog + ' · Texturen ' + s0.tex + ' → ' + s1.tex + ' · Geometrien ' + s0.geo + ' → ' + s1.geo);
  console.log('lange Aufgaben nach Menüstart (Sekunde nach Einblenden: Dauer ms): ' + la.map(e => ((e[0] - M.menu) / 1000).toFixed(1) + ':' + e[1]).join('  '));
  if (M.lade) console.log('Vorladen im Ladebildschirm: ' + M.lade.join(' · ')); if (M.pre) console.log('Vorladen im Menü (alt): ' + M.pre.join(' · '));
  await b.close(); })().catch(e => { console.error(e); process.exit(1); });
