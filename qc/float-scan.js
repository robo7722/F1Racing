// Schwebende Objekte und Spalten unter Objekten am Hang – im ganzen Streckenumfeld, auch weit abseits der Strecke (alles, was man sehen kann).
// Ablauf: 1. sichtbare Bodenhöhe als Raster aus allen Bodenflächen (Streifen, Kacheln, Gelände, große nach oben zeigende Flächen wie Dünen),
// 2. alle Einzelobjekte (Instanzen; zusammengeführte Netze in Bauteile zerlegt), 3. sich berührende Teile über alle Netze hinweg zu einem Objekt
// zusammenfassen (Dach auf Wänden, Krone auf Stamm), 4. Unterkante gegen den Boden; Gegenprobe per Strahl nach unten (Hügel, Sockel, Dächer).
// Detailstufen und Kachel-Ausblendung hängen von der Kamera ab – sie werden für die Prüfung eingeblendet und danach wiederhergestellt.
// Auch als Konsolenwerkzeug: index.html?qc=none, dann await __qcBot.floatScan().
export async function floatScan(A, opt = {}) {
  const T = A.THREE, tg = A.trackGroup;
  // Detailstufen/Kachel-Ausblendung hängt von der Kamera ab: alles so zeigen, als stünde man daneben
  const saved = []; tg.traverse(o => { if (o.userData.lodHi || o.userData.chunk) saved.push([o, o.geometry, o.visible]); if (o.userData.lodHi) { o.geometry = o.userData.lodHi; o.visible = true; } else if (o.userData.chunk) o.visible = true; });
  const isVis = o => { let p = o; while (p && p !== tg) { if (!p.visible && !(p.userData.chunk || p.userData.lodHi || p.userData.evRef)) return false; p = p.parent; } return true; };
  tg.updateMatrixWorld(true);
  const m = new T.Matrix4(), v = new T.Vector3(), out = [];
  const THR = opt.thr || 0.45, SLOPE = 1.6;
  const tagOf = o => (o.name ? o.name + '|' : '') + (o.material && (o.material.customProgramCacheKey && /facade/.test(o.material.customProgramCacheKey()) ? 'fac' : o.material.type)) + ':' + o.geometry.attributes.position.count + (o.material && o.material.color ? '#' + o.material.color.getHexString() : '');
  let t0 = performance.now(); const yieldMaybe = async () => { if (performance.now() - t0 > 60) { await new Promise(r => setTimeout(r, 0)); t0 = performance.now(); } };
  
  // sichtbare Bodenhöhe: alle Bodenflächen (Streifen, Kacheln, Gelände) auf ein Raster legen, höchste Fläche gewinnt
  const GM = []; tg.traverse(o => { if (!o.isMesh || o.isInstancedMesh || !o.geometry || !o.geometry.attributes.position) return; if (!isVis(o)) return; const ud = o.userData; if (o.material && (o.material.transparent || o.material.visible === false)) return; if (ud.strip || ud.tile || ud.ground || ud.flat) { GM.push(o); return; } const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox(); const bb0 = g.boundingBox; if (Math.max(bb0.max.x - bb0.min.x, bb0.max.z - bb0.min.z) > 30 && g.attributes.position.count > 60) { o.__up = true; GM.push(o); } });
  let gx0 = 1e9, gx1 = -1e9, gz0 = 1e9, gz1 = -1e9; const bb = new T.Box3(); for (const o of GM) { bb.setFromObject(o); gx0 = Math.min(gx0, bb.min.x); gx1 = Math.max(gx1, bb.max.x); gz0 = Math.min(gz0, bb.min.z); gz1 = Math.max(gz1, bb.max.z); }
  let CS = 1; while ((gx1 - gx0) / CS * (gz1 - gz0) / CS > 2.4e7) CS *= 1.5; const NX = Math.ceil((gx1 - gx0) / CS) + 1, NZ = Math.ceil((gz1 - gz0) / CS) + 1, HG = new Float32Array(NX * NZ).fill(-1e9);
  const put = (x, z, y) => { const i = Math.round((x - gx0) / CS), k = Math.round((z - gz0) / CS); if (i < 0 || k < 0 || i >= NX || k >= NZ) return; const q = k * NX + i; if (y > HG[q]) HG[q] = y; };
  for (const o of GM) { const g = o.geometry, P = g.attributes.position, I = g.index, n = I ? I.count : P.count, e = o.matrixWorld.elements, Aa = [0, 0, 0], Bb = [0, 0, 0], Cc = [0, 0, 0];
    const get = (k, w) => { const x = P.getX(k), y = P.getY(k), z = P.getZ(k); w[0] = e[0] * x + e[4] * y + e[8] * z + e[12]; w[1] = e[1] * x + e[5] * y + e[9] * z + e[13]; w[2] = e[2] * x + e[6] * y + e[10] * z + e[14]; };
    for (let t = 0; t + 2 < n; t += 3) { get(I ? I.getX(t) : t, Aa); get(I ? I.getX(t + 1) : t + 1, Bb); get(I ? I.getX(t + 2) : t + 2, Cc);
      if (o.__up) { const ux = Bb[0] - Aa[0], uy = Bb[1] - Aa[1], uz = Bb[2] - Aa[2], vx = Cc[0] - Aa[0], vy = Cc[1] - Aa[1], vz = Cc[2] - Aa[2], ny = uz * vx - ux * vz, nl = Math.hypot(uy * vz - uz * vy, ny, ux * vy - uy * vx) || 1; if (Math.abs(ny / nl) < 0.6) continue; }
      const d = (Bb[2] - Cc[2]) * (Aa[0] - Cc[0]) + (Cc[0] - Bb[0]) * (Aa[2] - Cc[2]); put(Aa[0], Aa[2], Aa[1]); put(Bb[0], Bb[2], Bb[1]); put(Cc[0], Cc[2], Cc[1]); if (Math.abs(d) < 1e-9) continue;
      const i0 = Math.ceil((Math.min(Aa[0], Bb[0], Cc[0]) - gx0) / CS), i1 = Math.floor((Math.max(Aa[0], Bb[0], Cc[0]) - gx0) / CS), k0 = Math.ceil((Math.min(Aa[2], Bb[2], Cc[2]) - gz0) / CS), k1 = Math.floor((Math.max(Aa[2], Bb[2], Cc[2]) - gz0) / CS);
      for (let i = i0; i <= i1; i++) for (let k = k0; k <= k1; k++) { const x = gx0 + i * CS, z = gz0 + k * CS, a = ((Bb[2] - Cc[2]) * (x - Cc[0]) + (Cc[0] - Bb[0]) * (z - Cc[2])) / d, b2 = ((Cc[2] - Aa[2]) * (x - Cc[0]) + (Aa[0] - Cc[0]) * (z - Cc[2])) / d, c = 1 - a - b2; if (a < -1e-4 || b2 < -1e-4 || c < -1e-4) continue; const q = k * NX + i; const y = a * Aa[1] + b2 * Bb[1] + c * Cc[1]; if (y > HG[q]) HG[q] = y; } }
    await yieldMaybe(); }
  const GY = (x, z) => { const fi = (x - gx0) / CS, fk = (z - gz0) / CS, i = Math.round(fi), k = Math.round(fk); let best = -1e9; for (let u = -1; u <= 1; u++) for (let w = -1; w <= 1; w++) { const ii = i + u, kk = k + w; if (ii < 0 || kk < 0 || ii >= NX || kk >= NZ) continue; const h = HG[kk * NX + ii]; if (h > best && Math.hypot(ii - fi, kk - fk) <= 1.0) best = h; } return best > -1e8 ? best : A.groundY(x, z); };
  const rc = new T.Raycaster(), DOWN = new T.Vector3(0, -1, 0); const MB = []; tg.traverse(o => { if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return; if (!isVis(o)) return; if (o.material && (o.material.visible === false || o.material.blending === T.AdditiveBlending)) return; const b = new T.Box3().setFromObject(o); if (b.isEmpty()) return; MB.push({ o, b }); });
  await yieldMaybe();
  const judge = async (pts, top, tag, extra) => {   // pts = Unterkante in Welt [[x,y,z]...]
    let mn = 1e9, mx = -1e9, cx = 0, cz = 0;
    for (const [x, y, z] of pts) { const gy = GY(x, z), d = y - gy; if (d < mn) mn = d; if (d > mx) mx = d; cx += x; cz += z; }
    cx /= pts.length; cz /= pts.length;
    let kind = null; if (mn > THR) kind = 'schwebt'; else if (mx > SLOPE) kind = 'Spalt';
    if (!kind) return;
    if (kind === 'schwebt') {   // Gegenprobe: Strahl nach unten gegen alles (Hügel, Sockel, Dächer …) – trägt irgendetwas das Objekt?
      const sel = pts.length > 5 ? [pts[0], pts[Math.floor(pts.length / 4)], pts[Math.floor(pts.length / 2)], pts[Math.floor(pts.length * 3 / 4)], pts[pts.length - 1]] : pts; let gmin = 1e9;
      for (const [x, y, z] of sel) { const cand = MB.filter(e => x >= e.b.min.x && x <= e.b.max.x && z >= e.b.min.z && z <= e.b.max.z && e.b.min.y < y); rc.set(new T.Vector3(x, y - 0.03, z), DOWN); rc.far = mn + 0.5; const h = rc.intersectObjects(cand.map(e => e.o), false)[0]; const gg = h ? h.distance + 0.03 : mn; if (gg < gmin) gmin = gg; }
      if (gmin < THR) return; mn = gmin; }
    const [d, j] = A.nearestDist(cx, cz); out.push({ kind, tag, x: Math.round(cx), z: Math.round(cz), s: Math.round(j * A.DS), d: Math.round(d), gapMin: +mn.toFixed(2), gapMax: +mx.toFixed(2), y: +(pts[0][1]).toFixed(1), ...extra });
  };
  const meshes = []; tg.traverse(o => { if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return; if (!isVis(o)) return; const ud = o.userData; if (ud.strip || ud.tile || ud.ground || ud.flat || ud.treeSpr) return; if (o.material && o.material.visible === false) return; if (o.material && o.material.blending === T.AdditiveBlending) return; meshes.push(o); });
  const IT = [];   // alle Einzelobjekte: Instanzen und Bauteile zusammengeführter Meshes
  const corners = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]];
  for (const o of meshes) {
    const g = o.geometry, P = g.attributes.position; if (!g.boundingBox) g.computeBoundingBox(); const b = g.boundingBox, H = b.max.y - b.min.y; const tag = tagOf(o);
    if (o.isInstancedMesh) {
      const low = []; const st = Math.max(1, Math.floor(P.count / 2000)); for (let i = 0; i < P.count; i += st) if (P.getY(i) <= b.min.y + Math.max(0.05, H * 0.03)) low.push(i);
      const sel = low.length > 12 ? low.filter((_, k) => k % Math.ceil(low.length / 12) === 0) : low;
      for (let k = 0; k < o.count; k++) { o.getMatrixAt(k, m); if (Math.abs(m.determinant()) < 1e-9) continue; m.premultiply(o.matrixWorld);
        const it = { x0: 1e9, x1: -1e9, y0: 1e9, y1: -1e9, z0: 1e9, z1: -1e9, tag, inst: k };
        for (const [u, w, q] of corners) { v.set(u ? b.max.x : b.min.x, w ? b.max.y : b.min.y, q ? b.max.z : b.min.z).applyMatrix4(m); if (v.x < it.x0) it.x0 = v.x; if (v.x > it.x1) it.x1 = v.x; if (v.y < it.y0) it.y0 = v.y; if (v.y > it.y1) it.y1 = v.y; if (v.z < it.z0) it.z0 = v.z; if (v.z > it.z1) it.z1 = v.z; }
        it.low = sel.map(i => { v.fromBufferAttribute(P, i).applyMatrix4(m); return [v.x, v.y, v.z]; }); it.y0 = Math.min(...it.low.map(p => p[1]));
        IT.push(it); if ((k & 255) === 0) await yieldMaybe(); }
      continue;
    }
    const n = P.count, par = new Int32Array(n); for (let i = 0; i < n; i++) par[i] = i; const f = i => { while (par[i] !== i) { par[i] = par[par[i]]; i = par[i]; } return i; }, un = (a, c) => { a = f(a); c = f(c); if (a !== c) par[a] = c; };
    const W = new Map(); for (let i = 0; i < n; i++) { const k = Math.round(P.getX(i) * 50) + ',' + Math.round(P.getY(i) * 50) + ',' + Math.round(P.getZ(i) * 50); const q = W.get(k); if (q === undefined) W.set(k, i); else un(i, q); }
    const I = g.index; if (I) for (let t = 0; t < I.count; t += 3) { un(I.getX(t), I.getX(t + 1)); un(I.getX(t), I.getX(t + 2)); } else for (let t = 0; t + 2 < n; t += 3) { un(t, t + 1); un(t, t + 2); }
    await yieldMaybe();
    const C = new Map(), mw = o.matrixWorld, WP = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const r = f(i); v.fromBufferAttribute(P, i).applyMatrix4(mw); WP[i * 3] = v.x; WP[i * 3 + 1] = v.y; WP[i * 3 + 2] = v.z; let c = C.get(r); if (!c) C.set(r, c = { x0: 1e9, x1: -1e9, y0: 1e9, y1: -1e9, z0: 1e9, z1: -1e9, id: [], tag }); if (v.x < c.x0) c.x0 = v.x; if (v.x > c.x1) c.x1 = v.x; if (v.y < c.y0) c.y0 = v.y; if (v.y > c.y1) c.y1 = v.y; if (v.z < c.z0) c.z0 = v.z; if (v.z > c.z1) c.z1 = v.z; c.id.push(i); }
    for (const c of C.values()) { const lo = []; for (const i of c.id) if (WP[i * 3 + 1] <= c.y0 + 0.08) lo.push([WP[i * 3], WP[i * 3 + 1], WP[i * 3 + 2]]); c.low = lo.length > 12 ? lo.filter((_, k) => k % Math.ceil(lo.length / 12) === 0) : lo; delete c.id; IT.push(c); }
    await yieldMaybe();
  }
  // sich berührende Teile (±0,3 m) über alle Meshes hinweg zu einem Objekt zusammenfassen (Dach auf Wänden, Krone auf Stamm)
  const p2 = new Int32Array(IT.length); for (let i = 0; i < IT.length; i++) p2[i] = i; const f2 = i => { while (p2[i] !== i) { p2[i] = p2[p2[i]]; i = p2[i]; } return i; }, E = 0.3, G = new Map(), cs = 10;
  for (let i = 0; i < IT.length; i++) { const c = IT[i]; if (c.x1 - c.x0 > 400 || c.z1 - c.z0 > 400) continue; for (let gx = Math.floor((c.x0 - E) / cs); gx <= Math.floor((c.x1 + E) / cs); gx++) for (let gz = Math.floor((c.z0 - E) / cs); gz <= Math.floor((c.z1 + E) / cs); gz++) { const k = gx * 100003 + gz; const a = G.get(k) || G.set(k, []).get(k); for (const jx of a) { const d = IT[jx]; if (c.x0 - E <= d.x1 && d.x0 - E <= c.x1 && c.z0 - E <= d.z1 && d.z0 - E <= c.z1 && c.y0 - E <= d.y1 && d.y0 - E <= c.y1) { const ra = f2(i), rb = f2(jx); if (ra !== rb) p2[ra] = rb; } } a.push(i); } if ((i & 1023) === 0) await yieldMaybe(); }
  const O = new Map(); IT.forEach((c, i) => { const r = f2(i); let q = O.get(r); if (!q) O.set(r, q = { y0: 1e9, y1: -1e9, cs: [] }); q.cs.push(c); q.y0 = Math.min(q.y0, c.y0); q.y1 = Math.max(q.y1, c.y1); });
  const supported = (q, rid) => { const x0 = Math.min(...q.cs.map(c => c.x0)) - 1.2, x1 = Math.max(...q.cs.map(c => c.x1)) + 1.2, z0 = Math.min(...q.cs.map(c => c.z0)) - 1.2, z1 = Math.max(...q.cs.map(c => c.z1)) + 1.2, seen = new Set();
    for (let gx = Math.floor(x0 / cs); gx <= Math.floor(x1 / cs); gx++) for (let gz = Math.floor(z0 / cs); gz <= Math.floor(z1 / cs); gz++) for (const jx of G.get(gx * 100003 + gz) || []) { if (seen.has(jx)) continue; seen.add(jx); const d = IT[jx]; if (f2(jx) === rid) continue; if (d.x0 <= x1 && d.x1 >= x0 && d.z0 <= z1 && d.z1 >= z0 && d.y1 >= q.y0 - 1.5 && d.y0 < q.y0 - 0.2) return true; } return false; };
  let nj = 0; for (const [rid, q] of O) { const pts = []; for (const c of q.cs) if (c.y0 <= q.y0 + 0.1) for (const p of c.low) if (p[1] <= q.y0 + 0.1) pts.push(p); if (!pts.length) continue;
    const lowC = q.cs.reduce((a, c) => c.y0 < a.y0 ? c : a); const ext = Math.max(...q.cs.map(c => Math.max(c.x1 - c.x0, c.z1 - c.z0)));
    if (q.y0 - GY(pts[0][0], pts[0][2]) > THR && supported(q, rid)) continue;
    await judge(pts.length > 24 ? pts.filter((_, k) => k % Math.ceil(pts.length / 24) === 0) : pts, q.y1, lowC.tag, { H: +(q.y1 - q.y0).toFixed(1), ext: +ext.toFixed(1), parts: q.cs.length, inst: lowC.inst, bb: [Math.min(...q.cs.map(c => c.x0)), q.y0, Math.min(...q.cs.map(c => c.z0)), Math.max(...q.cs.map(c => c.x1)), q.y1, Math.max(...q.cs.map(c => c.z1))].map(x => +x.toFixed(1)) }); if ((++nj & 511) === 0) await yieldMaybe(); }
  // gruppieren: gleicher Typ + Art
  for (const [o, g, vis] of saved) { o.geometry = g; o.visible = vis; }
  return out;
}
