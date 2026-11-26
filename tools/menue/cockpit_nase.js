// Aufruf: node tools/menue/cockpit_nase.js <Ordner> [Fahrerkürzel] [Klasse f1|f2]
// Nase des eigenen Autos aus fester Kamera: normale Materialien vs. Cockpit-Materialien (Helm/TV)
const { spiel } = require('../textur/spiel.js'); const path = require('path');
const OUT = process.argv[2], DRV = process.argv[3] || 'RUS', SER = process.argv[4];
(async () => {
  const { b, p, ev } = await spiel({ w: 1280, h: 720, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
  await ev(`if (byCode('${DRV}')) { S.driver = '${DRV}'; MENU.team = byCode('${DRV}').team; }   /* F2: Fahrer wählt die Klassenwahl */ window.__wxForce = 'dry'; window.__noWarm = true; S.sound = false; S.music = false; 1`);
  await p.evaluate(([t, s]) => window.__race(t, s), ['Monza', SER]);
  console.log('Fahrer', await ev('S.driver'), 'Klasse', await ev('SER'), 'Schale mit Lack-Textur:', await ev(`(() => { cockBuild(pl.mesh); let r = false; pl.mesh.tub.traverse(o => { if (o.isMesh && o.geometry.attributes.uvB) r = true; }); return r; })()`));
  await ev(`raceState = 'race'; raceTime = 20; SG.go = true; document.querySelector('#lights').classList.add('hidden'); document.querySelector('#hud').style.visibility = 'hidden'; 1`);
  // Kamera: über und hinter dem Cockpit, Blick auf die Nase
  const shot = async (name, cam) => {
    await ev(`S.cam = ${cam}; pl.v = 0; window.__frame(4, 33); const g = pl.mesh.g; g.updateMatrixWorld(); const P = (x, y, z) => new THREE.Vector3(x, y, z).applyMatrix4(g.matrixWorld).toArray();
      window.__camFix = { p: P(0.9, 1.6, -0.4), t: P(0, 0.5, 1.8) }; window.__frame(3, 33); 1`);
    await p.screenshot({ path: path.join(OUT, `${DRV}_${name}.png`) });
    console.log(name, await ev(`pl.mesh.body.material === pl.mesh.tp.glossMat ? 'glossMat' : pl.mesh.body.material === pl.mesh.tp.cutGloss ? 'cutGloss' : 'anderes (numMat?)'`)); };
  await shot('a_verfolger_vorher', 0); await shot('b_tv', 3); await shot('c_verfolger_nachher', 0);
  await b.close(); })().catch(e => { console.error(e); process.exit(1); });
