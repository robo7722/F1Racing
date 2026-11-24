// Regen-Bilder aus dem echten Spiel aufnehmen (Abnahme, Vergleich nach Änderungen):
//   node tools/wetter/regen_bilder.js <Strecke> <dry|light|heavy> <Ausgabeordner> [Streckenmeter,Kamera ...] [--gfx high|ultra|low] [--size 1280,720] [--nohud]
//   Beispiel: node tools/wetter/regen_bilder.js Spa heavy bilder 300,0 1200,2 --nohud
//   Bildfolge (Bewegung prüfen, z. B. Tropfen auf dem Visier): --folge 12[,2] nimmt nach jedem Bild 12 weitere auf, jeweils 2 Spielbilder (66 ms) später → …_f01.png …
//   Standbild mit fester Kamera: fix:s:quer:höhe:s2:quer2:höhe2[:basis] (Kamera an Streckenmeter s, Blick auf s2; das eigene Auto steht bei basis+14, sonst s+14)
// Kamera: 0 Verfolger, 1 hoch hinten, 2 Helm, 3 TV. Das eigene Auto fährt selbst (KI), vor jedem Bild laufen ~1,3 s Spielzeit.
const { spiel } = require('../textur/spiel.js'); const fs = require('fs'); const path = require('path');
(async () => {
  const a = process.argv.slice(2), flag = n => { const i = a.indexOf('--' + n); if (i < 0) return null; const v = a[i + 1]; a.splice(i, 2); return v; };
  const nohud = a.includes('--nohud'); if (nohud) a.splice(a.indexOf('--nohud'), 1);
  const warm = a.includes('--warm'); if (warm) a.splice(a.indexOf('--warm'), 1);
  const gfx = flag('gfx') || 'high', size = (flag('size') || '1280,720').split(',').map(Number), pre = flag('pre') || '', frames = +(flag('frames') || 40), folge = (flag('folge') || '0').split(',').map(Number);
  const [trk = 'Spa', wx = 'heavy', out = 'regen-bilder', ...views] = a; fs.mkdirSync(out, { recursive: true });
  const { b, p, ev } = await spiel({ w: size[0], h: size[1], query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
  const T0 = Date.now(), T = () => ((Date.now() - T0) / 1000).toFixed(0) + ' s';
  await ev(`if (S.gfx !== ${JSON.stringify(gfx)}) { S.gfx = ${JSON.stringify(gfx)}; applyGfx(); } window.__wxForce = ${JSON.stringify(wx)}; window.__noWarm = ${warm ? 'false' : 'true'}; S.sound = false; S.music = false; ${pre}; 1`);
  const ok = await p.evaluate(t => window.__race(t), trk); console.log(T(), 'Rennen läuft:', ok, await ev(`WX.cur + ' ssr=' + WX.ssr + ' mats=' + WX.mats.length + ' soil=' + WX.soil.length + ' lamps=' + WX.lamps.length + ' progs=' + renderer.info.programs.length`));
  await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
  await ev(`raceState = 'race'; raceTime = 20; SG.go = true; window.__plAI = true; profBot = buildProfile(45.5 * WX.grip, VTOP, 44 * WX.brk, KR); document.querySelector('#lights').classList.add('hidden'); document.querySelector('#sgHint').classList.add('hidden'); ${nohud ? "document.body.classList.add('ptNoHud'); document.querySelector('#hud').style.visibility = 'hidden'; document.querySelector('#controls').style.display = 'none';" : ''} 1`);
  for (const v of views.length ? views : ['300,0']) {
    if (v.startsWith('fix:')) { const q = v.slice(4).split(':').map(Number), s = q.length > 6 ? q.pop() : q[0];   // Standbild; optionaler 7. Wert: Streckenmeter, ab dem die Autos stehen (sonst wie die Kamera)
      await ev(`S.cam = 0; { const put = (c, s, lat) => { const q = trackAt(s, lat); c.x = q.x; c.z = q.z; c.h = q.h; c.steer = 0; c.sx = c.sz = 0; c.yawKick = 0; c.idx = q.i; c.sPrev = modL(s); projectCar(c); c.d = modL(s); c.sPrev = modL(s); c.v = 0; c.stuckT = 0; };
        put(pl, ${s} + 14, -1.5); cars.filter(c => c !== pl).forEach((c, k) => put(c, ${s} + 26 + k * 11, (k % 2 ? -1 : 1) * 2.6)); }
        window.__view(${q.join(',')}); raceState = 'lights'; window.__frame(8, 33); raceState = 'race'; 1`);
      const f = path.join(out, `${trk.toLowerCase()}_${wx}_fix${Math.round(q[0])}_${q[2]}.png`); await p.screenshot({ path: f }); await ev(`window.__camFix = null; 1`); console.log(T(), f); continue; }
    const [s, cam = 0] = v.split(',').map(Number);
    // Feld hinter und vor dem eigenen Auto aufstellen (alle mit dem Tempo, das ihr Profil dort erlaubt), dann ohne Zeichnen einfahren lassen und die letzten Bilder zeichnen
    const info = await ev(`S.cam = ${cam}; { const put = (c, s, lat) => { const q = trackAt(s, lat); c.x = q.x; c.z = q.z; c.h = q.h; c.steer = 0; c.sx = c.sz = 0; c.yawKick = 0; c.idx = q.i; c.sPrev = modL(s); projectCar(c); c.d = modL(s); c.sPrev = modL(s); c.stuckT = 0; c.wrongT = 0; c.v = Math.min((c === pl ? profBot : profAI)[c.idx] * 0.9, 80); };
      put(pl, ${s}, 0); camH = pl.h; cars.filter(c => c !== pl).forEach((c, k) => put(c, ${s} + (k < 3 ? 16 + k * 13 : -(12 + (k - 3) * 12)), (k % 2 ? 1 : -1) * 2.4)); }
      window.__norender = true; window.__frame(${frames}, 33); window.__norender = false; window.__frame(3, 33);
      JSON.stringify({ kmh: Math.round(pl.v * 3.6), progs: renderer.info.programs.length, spray: SPRAY.live, ton: !!WXS.g, maske: !!WXM.tex })`);
    const f = path.join(out, `${trk.toLowerCase()}_${wx}_${s}_cam${cam}.png`); await p.screenshot({ path: f }); console.log(T(), f, info);
    for (let k = 1; k <= folge[0]; k++) { await ev(`window.__frame(${folge[1] || 2}, 33); 1`); await p.screenshot({ path: f.replace('.png', '_f' + String(k).padStart(2, '0') + '.png') }); } }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
