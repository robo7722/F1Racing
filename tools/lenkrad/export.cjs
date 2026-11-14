// Exportiert aus dem laufenden Spiel alles für die Clipping-Prüfung von F1/F2-Lenkrad und Händen (check_lenkrad.py):
// Prüfmodell des Lenkrads (SW.spec), Knochen der Arm-IK über den ganzen Lenkbereich (F1, F1-TV, F2, F2-TV) und die Karosserie/Wanne rund ums Lenkrad.
// Aufruf (Spiel muss über http laufen, z. B. python -m http.server 8765 im Repo):
//   node tools/lenkrad/export.cjs [http://localhost:8765/index.html] [ausgabe.json]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const url = process.argv[2] || 'http://localhost:8765/index.html', out = process.argv[3] || 'lenkrad_export.json';
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const R = { cases: {}, car: {} };
  for (const ser of ['f1', 'f2']) {   // je Klasse eine frische Seite
    const p = await b.newPage({ viewport: { width: 640, height: 360 } });
    p.on('pageerror', e => console.log('Seitenfehler', e.message));
    await p.goto(url, { timeout: 120000 });
    await p.waitForFunction(() => window.__race && window.__qcApi && window.__f1dbg, null, { timeout: 180000 });
    const ok = await p.evaluate(async ser => { const A = window.__qcApi; A.S.gfx = 'low'; const k = Object.keys(A.TRACKS).find(k => /monza/i.test(k)) || Object.keys(A.TRACKS)[0];
      return window.__race(A.TRACKS[k].name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), ser); }, ser);
    if (!ok) throw new Error('Rennen ' + ser + ' startet nicht');
    await p.evaluate(() => { window.__qcApi.S.cam = 2; }); await p.waitForTimeout(2500);   // Cockpitansicht: Wanne wird gebaut
    const r = await p.evaluate(ser => {
      const D = window.__f1dbg(), A = window.__qcApi, T = A.THREE, K = D.K, MD = D.MODELS[ser], m = A.pl.mesh;
      K.fist ||= D.f1Fist(K);
      const res = { spec: D.SW.spec, swPos: MD.swPos, swS: MD.swS, cases: {}, car: [], carTag: [] };
      // Lenkbereich wie im Spiel: Einschlag −1…+1 in Schritten von 0,01 (Lenkraddrehung = −steer · SW_ROT), stetig gefahren wie beim Lenken
      const steer = []; for (let s = 0; s <= 100; s++) steer.push(s / 100); for (let s = 99; s >= -100; s--) steer.push(s / 100); for (let s = -99; s <= 0; s++) steer.push(s / 100);
      for (const tv of [false, true]) {
        const W = D.f1Wheel(MD), pos = new T.Vector3(0, MD.helm[0] + 0.005, MD.helm[1]).sub(new T.Vector3(...K.helm)).add(new T.Vector3(0, tv ? -0.03 : 0, tv ? 0.06 : 0));
        const Cl = W.C.clone().sub(pos), bones = Array.from({ length: 7 }, () => new T.Matrix4()), S = [];
        for (const st of steer) { const sp = -st * D.SW_ROT; D.kartArmsIK(bones, sp, K, Cl, W.AX, W.R); S.push({ st, sp, roll: bones.roll ? bones.roll.slice() : null, M: bones.map(b => Array.from(b.elements)) }); }
        res.cases[ser + (tv ? '-tv' : '')] = { pos: pos.toArray(), S };
      }
      // Karosserie und Cockpitwanne (Fahrzeug-Rahmen) im Bereich ums Lenkrad
      const box = new T.Box3(new T.Vector3(-0.45, 0.25, 0.25), new T.Vector3(0.45, 1.0, 1.1)), g = m.g; g.updateMatrixWorld(true); const inv = new T.Matrix4().copy(g.matrixWorld).invert();
      const meshes = []; [['body', m.body], ['matte', m.matte], ['tub', m.tub], ['halo', m.halo]].forEach(([nm, o]) => { if (o) o.traverse(x => { if (x.isMesh && x.geometry) { x.userData.chk = nm; meshes.push(x); } }); });
      for (const x of meshes) { const geo = x.geometry, P = geo.attributes.position, I = geo.index, M = new T.Matrix4().multiplyMatrices(inv, x.matrixWorld), v = [new T.Vector3(), new T.Vector3(), new T.Vector3()], n = I ? I.count / 3 : P.count / 3;
        for (let f = 0; f < n; f++) { for (let k = 0; k < 3; k++) v[k].fromBufferAttribute(P, I ? I.getX(f * 3 + k) : f * 3 + k).applyMatrix4(M);
          if (v.some(q => box.containsPoint(q))) { res.car.push(v.flatMap(q => [+q.x.toFixed(5), +q.y.toFixed(5), +q.z.toFixed(5)])); res.carTag.push(x.userData.chk); } } }
      return res;
    }, ser);
    R.spec = r.spec; R.wheel = R.wheel || {}; R.wheel[ser] = { swPos: r.swPos, swS: r.swS }; Object.assign(R.cases, r.cases); R.car[ser] = r.car; (R.carTag ||= {})[ser] = r.carTag;
    console.log(ser, 'Fälle', Object.keys(r.cases).join(', '), 'Karosserie-Dreiecke', r.car.length);
    await p.close();
  }
  fs.writeFileSync(out, JSON.stringify(R)); console.log('geschrieben', out);
  await b.close();
})();
