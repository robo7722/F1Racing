// Leistungsmessung je Kamera (für `python qc/probe.py KEY --race --script qc/perf-cam.js`)
// Fährt N Stellen der Runde an und zerlegt jedes Bild in Welt-Durchgang, Eigenes-Auto-Durchgang (Cockpit/T-Cam), Schattenkarte und Rest (Nachbearbeitung).
// Zählt Zeichenaufrufe/Dreiecke (zuverlässig) und CPU-Zeit je Durchgang (nur grob vergleichbar). Optional: window.__pcN (Stellen), window.__pcCams.
const A = window.__qcApi, R = A.renderer, S = A.S, gl = R.getContext(), px = new Uint8Array(4);
const sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
const I = R.info.render; let log = null, depth = 0;
const oR = R.render, oS = R.shadowMap.render;
R.render = function (sc, cam) { if (!log) return oR.call(this, sc, cam); const c0 = I.calls, t0 = I.triangles, p0 = performance.now(), e = { k: sc === A.scene ? (cam.layers.mask === 64 ? 'car' : 'world') : 'post', calls: 0, tris: 0, ms: 0 }; depth++; oR.call(this, sc, cam); depth--; e.calls = I.calls - c0; e.tris = I.triangles - t0; e.ms = performance.now() - p0; log.push(e); };
R.shadowMap.render = function (...a) { if (!log) return oS.apply(this, a); const c0 = I.calls, t0 = I.triangles, p0 = performance.now(); oS.apply(this, a); log.push({ k: 'shadow', calls: I.calls - c0, tris: I.triangles - t0, ms: performance.now() - p0 }); };
const L = A.L, N = window.__pcN || 16, cams = window.__pcCams || [0, 2, 3], out = { track: A.TRK && A.TRK.name, L: Math.round(L), cams: {} };
let objs = 0, meshes = 0; A.scene.traverse(o => { objs++; if (o.isMesh) meshes++; }); out.sceneObjs = objs; out.sceneMeshes = meshes;
{ let tri = 0, m = 0; const g = A.pl && A.pl.mesh && A.pl.mesh.g; if (g) g.traverse(o => { if (o.isMesh && o.visible && o.geometry) { m++; const ix = o.geometry.index; tri += (ix ? ix.count : o.geometry.attributes.position.count) / 3 * (o.isInstancedMesh ? o.count : 1); } }); out.ownCar = { meshes: m, tris: Math.round(tri) }; }
R.info.autoReset = false;
try {
  for (const c of cams) {
    S.cam = c; const rows = [];
    for (let k = 0; k < N; k++) {
      const s = (k + 0.5) * L / N; window.__tp(s); window.__frame(4); window.__tp(s); window.__frame(12);   // 12 Bilder: Detailstufen-Überblendungen (0,35 s) nach dem Versetzen abwarten
      log = []; I.calls = I.triangles = 0; const t0 = performance.now(); A.renderNow(); const cpu = performance.now() - t0; sync();
      const sum = { s: Math.round(s), calls: I.calls, tris: I.triangles, cpu: +cpu.toFixed(2) }; for (const e of log) { const q = sum[e.k] || (sum[e.k] = { calls: 0, tris: 0, ms: 0 }); q.calls += e.calls; q.tris += e.tris; q.ms += e.ms; }
      if (sum.world && sum.shadow) { sum.world.calls -= sum.shadow.calls; sum.world.tris -= sum.shadow.tris; sum.world.ms -= sum.shadow.ms; }   // Schattenkarte läuft innerhalb des Welt-Durchgangs
      let best = 1e9; for (let r = 0; r < 3; r++) { log = null; const t1 = performance.now(); A.renderNow(); A.renderNow(); sync(); best = Math.min(best, (performance.now() - t1) / 2); } sum.msSync = +best.toFixed(2);
      for (const k2 of ['world', 'car', 'shadow', 'post']) if (sum[k2]) { sum[k2].ms = +sum[k2].ms.toFixed(2); sum[k2].tris = Math.round(sum[k2].tris); }
      rows.push(sum); log = null;
      if (k % 4 === 3) await new Promise(r => setTimeout(r, 30));
    }
    const av = f => +(rows.reduce((a, r) => a + f(r), 0) / rows.length).toFixed(1), mx = f => Math.max(...rows.map(f));
    const g = (r, k, f) => (r[k] ? r[k][f] : 0);
    out.cams[c] = { calls: av(r => r.calls), callsMax: mx(r => r.calls), tris: Math.round(av(r => r.tris)), trisMax: mx(r => r.tris), cpu: av(r => r.cpu), msSync: av(r => r.msSync),
      world: { calls: av(r => g(r, 'world', 'calls')), tris: Math.round(av(r => g(r, 'world', 'tris'))), ms: av(r => g(r, 'world', 'ms')) },
      car: { calls: av(r => g(r, 'car', 'calls')), tris: Math.round(av(r => g(r, 'car', 'tris'))), ms: av(r => g(r, 'car', 'ms')) },
      shadow: { calls: av(r => g(r, 'shadow', 'calls')), tris: Math.round(av(r => g(r, 'shadow', 'tris'))), ms: av(r => g(r, 'shadow', 'ms')) },
      post: { calls: av(r => g(r, 'post', 'calls')), ms: av(r => g(r, 'post', 'ms')) },
      worst: rows.slice().sort((a, b) => b.calls - a.calls).slice(0, 3).map(r => ({ s: r.s, calls: r.calls, tris: r.tris, world: g(r, 'world', 'calls'), shadow: g(r, 'shadow', 'calls'), car: g(r, 'car', 'calls') })) };
  }
} finally { R.render = oR; R.shadowMap.render = oS; R.info.autoReset = true; log = null; S.cam = 0; }
out.prog = R.info.programs.length; out.geo = R.info.memory.geometries; out.tex = R.info.memory.textures;
return out;
