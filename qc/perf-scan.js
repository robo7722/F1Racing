// Wer verursacht die Zeichenaufrufe? (für `python qc/probe.py KEY --race --script qc/perf-scan.js`)
// Fährt N Stellen ab (Verfolger und Cockpit), nimmt an der schwersten Stelle jeder Kamera die Liste aller Zeichenaufrufe auf und fasst sie zusammen:
// je Objekt (Pfad, Material, Dreiecke), doppelt gezeichnete Objekte (durchsichtig + beidseitig = zwei Durchgänge), kleine Instanz-Kacheln,
// Netze mit mehreren Materialien und Materialien, die viele einzelne Aufrufe haben (Kandidaten zum Zusammenfassen). Optional: window.__psAt = [Meter, …].
const A = window.__qcApi, R = A.renderer, S = A.S, L = A.L, N = window.__pcN || 24;
const I = R.info.render, oRB = R.renderBufferDirect; let rec = null;
const name = o => { const p = []; let x = o; while (x && x !== A.scene && p.length < 5) { p.push((x.name || x.type) + (x.userData && x.userData.lm ? '[' + x.userData.lm + ']' : '')); x = x.parent; } return p.reverse().join('/'); };
const tri = (geo, grp, obj) => Math.round(((geo.index ? (grp ? grp.count : geo.index.count) : (grp ? grp.count : geo.attributes.position.count)) / 3) * (obj.isInstancedMesh ? obj.count : 1));
R.renderBufferDirect = function (cam, sc, geo, mat, obj, grp) { if (rec && (sc === A.scene || sc === null)) rec.push({ cam: sc === null ? 'shadow' : cam.layers.mask === 64 ? 'car' : 'main', obj, geo, mat, grp: !!grp, tris: tri(geo, grp, obj), side: mat.side }); return oRB.apply(this, arguments); };
const _v = new A.THREE.Vector3();
const where = o => { const g = o.geometry; if (!g) return ''; if (!g.boundingSphere) g.computeBoundingSphere(); const b = o.isInstancedMesh ? (o.boundingSphere || (o.computeBoundingSphere(), o.boundingSphere)) : g.boundingSphere; _v.copy(b.center).applyMatrix4(o.matrixWorld); return '@' + Math.round(_v.x) + ',' + Math.round(_v.z) + ' r' + Math.round(b.radius * o.matrixWorld.getMaxScaleOnAxis()) + ' ' + g.type.replace('Geometry', '') + (Object.keys(o.userData || {}).length ? ' ud:' + Object.keys(o.userData).slice(0, 4).join('+') : '') + (Object.keys(g.userData || {}).length ? ' gud:' + Object.keys(g.userData).slice(0, 4).join('+') : ''); };
const out = { track: A.TRK && A.TRK.name, L: Math.round(L), cams: {} };
const isOwn = o => { const g = A.pl && A.pl.mesh && A.pl.mesh.g; for (let x = o; x; x = x.parent) if (x === g) return true; return false; };
const isCar = o => { for (const c of [A.pl, ...(A.ais || [])]) { const g = c && c.mesh && c.mesh.g; if (!g) continue; for (let x = o; x; x = x.parent) if (x === g) return true; } return false; };
try {
  for (const c of [0, 2]) {
    S.cam = c; let worst = null;
    const spots = window.__psAt || Array.from({ length: N }, (_, k) => (k + 0.5) * L / N);
    for (const s of spots) { window.__tp(s); window.__frame(4); window.__tp(s); window.__frame(2); R.info.autoReset = false; I.calls = 0; A.renderNow(); const n = I.calls; R.info.autoReset = true; if (!worst || n > worst.n) worst = { s, n }; }
    window.__tp(worst.s); window.__frame(4); window.__tp(worst.s); window.__frame(2);
    rec = []; A.renderNow(); const list = rec; rec = null;
    const main = list.filter(e => e.cam === 'main'), sh = list.filter(e => e.cam === 'shadow');
    const by = new Map(); for (const e of main) { const own = isOwn(e.obj), car = !own && isCar(e.obj); const k = own ? 'EIGENES AUTO' : car ? 'GEGNER-AUTOS' : name(e.obj) + ' | ' + e.mat.type + (e.mat.map ? '+map' : '') + (e.obj.isInstancedMesh ? ' inst' : ''); const q = by.get(k) || { k, calls: 0, tris: 0, objs: new Set(), mats: new Set() }; q.calls++; q.tris += e.tris; q.objs.add(e.obj.id); q.mats.add(e.mat.uuid); by.set(k, q); }
    const top = [...by.values()].sort((a, b) => b.calls - a.calls).slice(0, 30).map(q => ({ k: q.k.slice(0, 160), calls: q.calls, tris: q.tris, objs: q.objs.size, mats: q.mats.size }));
    const cnt = new Map(); for (const e of main) cnt.set(e.obj.id, (cnt.get(e.obj.id) || 0) + 1);
    const twice = []; const seen = new Set(); for (const e of main) if (cnt.get(e.obj.id) > 1 && !e.grp && !seen.has(e.obj.id)) { seen.add(e.obj.id); twice.push({ k: (isOwn(e.obj) ? 'EIGEN ' : isCar(e.obj) ? 'GEGNER ' : '') + name(e.obj).slice(0, 80) + ' ' + where(e.obj), mat: e.mat.type, n: cnt.get(e.obj.id), tris: e.tris, transp: e.mat.transparent, side: e.mat.side }); }
    const smallInst = main.filter(e => e.obj.isInstancedMesh && e.obj.count <= 8 && !isCar(e.obj)).map(e => ({ k: name(e.obj).slice(0, 80) + ' ' + where(e.obj), count: e.obj.count, tris: e.tris }));
    const multi = new Map(); for (const e of main) if (e.grp && !isCar(e.obj)) { const k = name(e.obj).slice(0, 120); multi.set(k, (multi.get(k) || 0) + 1); }
    const perMat = new Map(); for (const e of main) if (!isCar(e.obj) && !e.obj.isInstancedMesh) { const q = perMat.get(e.mat.uuid) || { type: e.mat.type, color: e.mat.color ? e.mat.color.getHexString() : '', map: !!e.mat.map, calls: 0, tris: 0, ex: name(e.obj).slice(0, 60) + ' ' + where(e.obj) }; q.calls++; q.tris += e.tris; perMat.set(e.mat.uuid, q); }
    const sigMat = new Map(); for (const e of main) if (!isCar(e.obj)) { const m = e.mat, k = [m.type, m.color && m.color.getHexString(), m.map && m.map.uuid, m.roughness, m.metalness, m.transparent, m.side, m.vertexColors].join(','); const q = sigMat.get(k) || { k: k.slice(0, 90), mats: new Set(), calls: 0, ex: name(e.obj).slice(0, 60) + ' ' + where(e.obj) }; q.mats.add(m.uuid); q.calls++; sigMat.set(k, q); }
    const objs = new Map(); for (const e of main) if (!isCar(e.obj)) { const q = objs.get(e.obj.id) || { k: name(e.obj).slice(0, 60) + ' ' + where(e.obj), mat: e.mat.type + (e.mat.map ? '+map' : '') + (e.mat.color ? ' #' + e.mat.color.getHexString() : '') + (e.mat.transparent ? ' transp' : '') + (e.obj.isInstancedMesh ? ' inst' + e.obj.count : ''), calls: 0, tris: 0 }; q.calls++; q.tris += e.tris; objs.set(e.obj.id, q); }
    const topObjs = [...objs.values()].sort((a, b) => b.tris - a.tris).slice(0, 20);
    out.cams[c] = { topObjs, s: Math.round(worst.s), calls: main.length, shadowCalls: sh.length, tris: main.reduce((a, e) => a + e.tris, 0),
      own: main.filter(e => isOwn(e.obj)).length, opp: main.filter(e => !isOwn(e.obj) && isCar(e.obj)).length,
      top, drawnTwice: twice.slice(0, 25), smallInstances: smallInst.slice(0, 20), smallInstCount: smallInst.length,
      multiMaterial: [...multi].sort((a, b) => b[1] - a[1]).slice(0, 15),
      matManyCalls: [...perMat.values()].filter(q => q.calls >= 4).sort((a, b) => b.calls - a.calls).slice(0, 15),
      sameLookDiffMat: [...sigMat.values()].filter(q => q.mats.size >= 3).sort((a, b) => b.calls - a.calls).slice(0, 12).map(q => ({ k: q.k, mats: q.mats.size, calls: q.calls, ex: q.ex })) };
  }
} finally { R.renderBufferDirect = oRB; rec = null; S.cam = 0; R.info.autoReset = true; }
return out;
