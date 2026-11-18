// Aufruf: node tools/klassiker/fahrer_clip_export.js <zielordner>   (danach python tools/klassiker/fahrer_clip.py <zielordner>)
// Exportiert je Klassiker: Autodreiecke (Stufe 0 + Räder, im Auto-Raum) und Fahrer-Dreiecke (Bindhaltung, im Auto-Raum)
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js'); const fs = require('fs');
(async () => { const { b, p } = await spiel({ w: 400, h: 300, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__histDbg === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  const teams = await p.evaluate(() => Object.keys(window.__histDbg().HIST_CAR));
  for (const team of teams) {
    const r = await p.evaluate(async team => { const D = window.__histDbg(), { THREE } = D; await D.histLoad(team); window.__histFull = true;
      const m = D.makeHist({ code: 'TST', name: '', num: 1, team, helmet: 0xffffff }, D.TEAMS[team]); window.__histFull = false; D.scene.remove(m.g);
      m.g.position.set(0, 0, 0); m.g.rotation.set(0, 0, 0); m.g.updateMatrixWorld(true);
      const car = [], v = new THREE.Vector3(), dm = m.drv.mesh;
      m.g.traverse(o => { if (!o.isMesh || o === dm || o.isSkinnedMesh) return; let q = o, vis = true; while (q && q !== m.g) { if (q === m.lodG[1] || q === m.lodG[2]) vis = false; q = q.parent; } if (!vis) return;
        if (m.shpH && (o === m.shpH)) return; const G = o.geometry, P = G.attributes.position; if (!P) return; const I = G.index ? G.index.array : null, n = I ? I.length : P.count;
        for (let k = 0; k < n; k++) { v.fromBufferAttribute(P, I ? I[k] : k).applyMatrix4(o.matrixWorld); car.push(+v.x.toFixed(4), +v.y.toFixed(4), +v.z.toFixed(4)); } });
      const K = D.F1FAHRER, G = K.geo, P = G.attributes.position.array, I = G.index.array, off = dm.position, drv = [];
      for (let k = 0; k < I.length; k++) { const q = I[k]; drv.push(+(P[q * 3] + off.x).toFixed(4), +(P[q * 3 + 1] + off.y).toFixed(4), +(P[q * 3 + 2] + off.z).toFixed(4)); }
      const B = G.attributes.aBi.array, W = G.attributes.aBw.array, arm = []; for (let t = 0; t < I.length / 3; t++) { let a = 0; for (let j = 0; j < 3; j++) { const q = I[t * 3 + j]; for (let k = 0; k < 4; k++) if (B[q * 4 + k] > 0 && W[q * 4 + k] > 0) a = 1; } arm.push(a); }
      return JSON.stringify({ file: m.H.file, car, drv, arm }); }, team);
    fs.writeFileSync(require('path').join(process.argv[2] || '.', 'clip_' + team + '.json'), r); console.log(team, r.length);
  }
  await b.close(); })();
