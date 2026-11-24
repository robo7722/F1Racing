// Mehrere Rennen NACHEINANDER in der Helmkamera (ohne Neuladen): je Rennen ein Bild am Start und eins in der Fahrt, dazu der Zustand der Cockpit-Materialien.
// Findet Fehler, die erst beim zweiten Rennen auftreten, weil etwas aus dem ersten übrig bleibt. Anlass (v3.01): Nach einem trockenen Rennen war das Cockpit im
// folgenden Regenrennen schwarz – die Material-Kopien des Cockpits hielten die gelöschte Umgebung des ersten Rennens fest (siehe docs/COCKPIT.md).
//   node tools/menue/rennfolge_cockpit.js <Ausgabeordner> LEC,dry,Zandvoort LEC,light,Zandvoort LEC,heavy,Suzuka        (Fahrer,Wetter,Strecke je Rennen)
// Einzelne Rennen aus frischem Start (wie tools/wetter/regen_bilder.js) zeigen solche Fehler NICHT.
const { spiel } = require('../textur/spiel.js'); const path = require('path'); const out = process.argv[2]; require('fs').mkdirSync(out, { recursive: true });
(async () => { const { b, p, ev } = await spiel({ w: 1280, h: 590, query: '?qc=none' });
  p.on('console', m => { const t = m.text(); if (/error|warn/i.test(m.type()) && !/GPU stall|GroupMarker|Automatic fallback/.test(t)) console.log('KONSOLE', m.type(), t.slice(0, 300)); });
  await p.waitForFunction(() => { const L = document.querySelector('#loading'), M = document.querySelector('#menu'); return typeof window.__race === 'function' && L && L.classList.contains('hidden') && M && !M.classList.contains('hidden'); }, null, { timeout: 600000 });
  await ev(`S.gfx = 'high'; applyGfx(); S.sound = false; S.music = false; S.cam = 2; window.__noWarm = true; 1`);
  let nr = 0;
  const lauf = async (drv, wx, trk) => { await ev(`S.driver = ${JSON.stringify(drv)}; MENU.team = byCode(${JSON.stringify(drv)}).team; S.wx = ${JSON.stringify(wx)}; S.cam = 2; save(); 1`);
    const ok = await p.evaluate(t => window.__race(t), trk);
    await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
    await p.waitForFunction(() => document.querySelector('#loading').classList.contains('hidden'), null, { timeout: 600000 }); await ev(`window.__frame(8, 33); 1`);
    const f = String(++nr) + '_' + drv + '_' + wx + '_' + trk.toLowerCase(); await p.screenshot({ path: path.join(out, f + '_start.png') });
    const st = await ev(`(() => { const m = pl.mesh, mats = [['Karosserie', m.body.material], ['Schale', m.tub && m.tub.children[0].material]], o = { ok: ${ok}, wetter: WX.cur, cam: S.cam, cockOn: cockOn === m, tub: !!(m.tub && m.tub.visible) };
      for (const [n, mt] of mats) if (mt) { const pr = renderer.properties.get(mt), u = pr.currentProgram && pr.uniforms; o[n] = { schluessel: mt.customProgramCacheKey().slice(-40), bake: u && u.uBake ? !!(u.uBake.value && u.uBake.value.image) + '/' + (u.uBakeOn ? u.uBakeOn.value : '-') : 'kein uBake', sheetOn: u && u.uSheetOn ? u.uSheetOn.value : '-', ckFill: u && u.uCkFill ? u.uCkFill.value : '-', env: mt.envMapIntensity, cc: mt.clearcoat }; }
      return JSON.stringify(o); })()`); console.log(f, st);
    await ev(`raceState = 'race'; SG.go = true; window.__plAI = true; document.querySelector('#lights').classList.add('hidden'); document.querySelector('#sgHint').classList.add('hidden'); window.__frame(40, 33); 1`); await p.screenshot({ path: path.join(out, f + '_fahrt.png') });
    await ev(`toMenu(); 1`); await p.waitForTimeout(900); };
  for (const a of process.argv.slice(3)) { const [d, w, t] = a.split(','); await lauf(d, w, t); }
  await b.close(); })().catch(e => { console.error(e); process.exit(1); });
