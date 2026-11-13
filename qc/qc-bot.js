// QC-Bot für F1 Racing: fährt jede Strecke selbst ab, schaut aus jeder Kamera und sucht nach
// Rucklern, Löchern im Boden, Z-Fighting (Tiefenpuffer-Flimmern) und Darstellungsfehlern.
// Start: index.html?qc=all (oder ?qc=monza,spa). Mit qc/run.py werden Bilder und Bericht in qc-reports/ gespeichert,
// ohne Server (z. B. am Handy) lädt der Browser am Ende einen eigenständigen HTML-Bericht herunter.
// URL-Parameter: qc=all|liste  mode=full|quick  laps=n  ser=f1|f2|kart  gfx=low|high|ultra  static=0  shot=m  srv=1  run=id  i=n
const A = window.__qcApi, T = A.THREE, P = new URLSearchParams(location.search);
const W8 = ms => new Promise(r => setTimeout(r, ms));
const CFG = {
  list: (P.get('qc') || 'all').toLowerCase(), mode: P.get('mode') === 'quick' ? 'quick' : 'full', laps: +P.get('laps') || 0, ser: P.get('ser') || '',
  gfx: P.get('gfx') || '', stat: P.get('static') !== '0', srv: P.get('srv') === '1', run: P.get('run') || new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-'), i: +P.get('i') || 0, selftest: P.get('selftest') === '1', reportOnly: P.get('report') === '1'
};
// at=2900-3100: nur diesen Abschnitt prüfen (Streckenmeter, darf über Start/Ziel laufen, z. B. 5600-200) – dort dicht, Befunde außerhalb fallen weg
CFG.at = (m => m ? [+m[1], +m[2]] : null)(/^(\d+)-(\d+)$/.exec(P.get('at') || ''));
CFG.shot = +P.get('shot') || (CFG.at ? 25 : CFG.mode === 'quick' ? 200 : 300);
const inAt = (s, pad = 0) => { if (!CFG.at) return true; const L = A.L || 1e9, m = v => ((v % L) + L) % L, a = m(CFG.at[0] - pad), b = m(CFG.at[1] + pad), x = m(s); return a <= b ? x >= a && x <= b : x >= a || x <= b; };
const CAMN = ['Verfolger', 'Hoch hinten', 'Cockpit', 'T-Cam'];
const LOG = [];
// Fenster verdeckt (Bildschirm gesperrt, minimiert): der Browser zeichnet dann nicht von selbst – der Bot treibt das Spiel mit 60 Bildern/s an
// und misst die Rechenzeit je Bild bis die Grafikkarte fertig ist (statt des Abstands zwischen angezeigten Bildern)
const PUMP = { on: false, cb: null, n: 0, hid: 0, hold: false };
(function pumpLoop() {
  // statt blockierend auf die Grafikkarte zu warten (readPixels kann im Energiesparzustand ewig hängen), einen Zaun setzen und nachfragen
  const go = () => {
    if (!document.hidden) PUMP.hid = 0; else if (!PUMP.hid) PUMP.hid = performance.now();
    if (!document.hidden || !A.running || performance.now() - PUMP.hid < 1000) { PUMP.on = false; setTimeout(go, 200); return; }
    PUMP.on = true; const t = performance.now();
    if (A.paused && !PUMP.hold) A.resume(); A.tick(t, false); PUMP.n++;
    const gl = A.renderer.getContext(), fence = gl.fenceSync ? gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0) : null; gl.flush();
    let lastP = t, froze = false;   /* kommt ein Nachfragen über 0,5 s zu spät, hat der Browser die Seite eingefroren – dieses Bild zählt nicht */
    const done = () => { const w = performance.now() - t; if (fence) gl.deleteSync(fence); if (PUMP.cb && !froze) PUMP.cb(w); setTimeout(go, Math.max(1, 16.6 - w)); };
    const poll = () => { const n = performance.now(); if (n - lastP > 500) froze = true; lastP = n; if (!fence || gl.getSyncParameter(fence, gl.SYNC_STATUS) === gl.SIGNALED || n - t > 3000) done(); else setTimeout(poll, 1); };
    poll(); };
  setTimeout(go, 200); })();
let rafN = 0, hookN = 0; (function cnt() { rafN++; requestAnimationFrame(cnt); })();

// ---------- Ablage: mit Server (run.py) als Dateien, sonst im Speicher ----------
const MEM = { files: {} };
async function save(path, data, type = 'application/json') {
  if (!CFG.srv) { MEM.files[path] = data; return path; }
  const body = typeof data === 'string' ? data : data instanceof Blob ? data : JSON.stringify(data);
  for (let k = 0; k < 3; k++) { try { const r = await fetch('/__qc/save?run=' + encodeURIComponent(CFG.run) + '&path=' + encodeURIComponent(path), { method: 'POST', headers: { 'Content-Type': type }, body }); if (r.ok) return path; } catch (e) {} await W8(300); }
  return null;
}
function log(msg) { const line = new Date().toTimeString().slice(0, 8) + ' ' + msg; LOG.push(line); console.log('[QC] ' + msg); ui(msg); if (CFG.srv) fetch('/__qc/log', { method: 'POST', body: line }).catch(() => {}); }

// ---------- kleine Statusanzeige (nur DOM – landet nicht in den Bildern) ----------
const box = document.createElement('div'); box.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:99999;font:12px/1.35 ui-monospace,Consolas,monospace;color:#e8ffe8;background:rgba(0,0,0,.72);padding:6px 9px;border-left:3px solid #36d07a;pointer-events:none;max-width:46vw;white-space:pre-wrap';
document.body.appendChild(box); let uiHead = 'QC-Bot';
function ui(msg) { box.textContent = uiHead + '\n' + msg; }

// ---------- Fehler mitschreiben (Konsole, Ausnahmen, WebGL) ----------
const ERR = [];
for (const lv of ['error', 'warn']) { const o = console[lv].bind(console); console[lv] = (...a) => { const m = a.map(x => x && x.stack ? x.stack.split('\n')[0] : typeof x === 'object' ? (() => { try { return JSON.stringify(x).slice(0, 200); } catch (e) { return String(x); } })() : String(x)).join(' ').slice(0, 400); if (!/\[QC\]/.test(m)) ERR.push({ lv, m, t: performance.now() }); o(...a); }; }
addEventListener('error', e => ERR.push({ lv: 'error', m: 'Ausnahme: ' + (e.message || e) + (e.filename ? ' @' + e.filename.split('/').pop() + ':' + e.lineno : ''), t: performance.now() }));
addEventListener('unhandledrejection', e => ERR.push({ lv: 'error', m: 'Promise: ' + String(e.reason && e.reason.message || e.reason).slice(0, 300), t: performance.now() }));
let longTasks = []; try { new PerformanceObserver(l => { for (const e of l.getEntries()) longTasks.push({ t: e.startTime, d: e.duration }); }).observe({ entryTypes: ['longtask'] }); } catch (e) {}

// ---------- Hilfsfunktionen ----------
const sLap = () => { const L = A.L, d = A.pl.d || 0; return ((d % L) + L) % L; };
const at = s => Math.round(s) + ' m';
const pct = (a, q) => { if (!a.length) return 0; const b = Float64Array.from(a).sort(); return b[Math.min(b.length - 1, Math.floor(q * b.length))]; };
const lum = (d, i) => 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
function sOf(x, z) { const [d, j] = A.nearestDist(x, z); return { s: j * A.DS, d }; }
const TW = 480, TH2 = 270;   // Bildgröße für Auswertung und Vorschaubilder
const rtA = new T.WebGLRenderTarget(TW, TH2), rtB = new T.WebGLRenderTarget(TW, TH2), rtC = new T.WebGLRenderTarget(TW, TH2);
for (const r of [rtA, rtB, rtC]) r.texture.colorSpace = T.SRGBColorSpace;
const bufA = new Uint8Array(TW * TH2 * 4), bufB = new Uint8Array(TW * TH2 * 4), bufC = new Uint8Array(TW * TH2 * 4);
const cv = document.createElement('canvas'); cv.width = TW; cv.height = TH2; const cx = cv.getContext('2d', { willReadFrequently: true });
// Pixel aus einem Render-Target (unten beginnend) als JPEG; mark: Liste [x,y,r,farbe] zum Einzeichnen
function rtJpeg(buf, mark) { const im = cx.createImageData(TW, TH2); for (let y = 0; y < TH2; y++) im.data.set(buf.subarray((TH2 - 1 - y) * TW * 4, (TH2 - y) * TW * 4), y * TW * 4); for (let k = 3; k < im.data.length; k += 4) im.data[k] = 255; cx.putImageData(im, 0, 0); drawMarks(mark); return cv.toDataURL('image/jpeg', 0.72); }
function drawMarks(mark) { if (!mark) return; for (const [x, y, r, c] of mark) { cx.strokeStyle = c; cx.lineWidth = 2; cx.strokeRect(x - r, y - r, 2 * r, 2 * r); } }
// aktuelles Bild auf dem Bildschirm (direkt nach dem Zeichnen, sonst ist der Puffer leer)
function screenJpeg(mark) { cx.drawImage(A.renderer.domElement, 0, 0, TW, TH2); drawMarks(mark); return cv.toDataURL('image/jpeg', 0.72); }
function screenStats() { cx.drawImage(A.renderer.domElement, 0, 0, TW, TH2); const d = cx.getImageData(0, 0, TW, TH2).data; let s = 0, s2 = 0, n = 0; for (let i = 0; i < d.length; i += 16) { const l = lum(d, i); s += l; s2 += l * l; n++; } const m = s / n; return { mean: +m.toFixed(1), std: +Math.sqrt(Math.max(0, s2 / n - m * m)).toFixed(1) }; }

let imgN = 0, TRK_KEY = '';
async function img(dataUrl, tag) { if (!dataUrl) return null; const name = 'img/' + TRK_KEY + '_' + (++imgN) + '_' + tag + '.jpg'; if (!CFG.srv) { MEM.files[name] = dataUrl; return name; } const b = await (await fetch(dataUrl)).blob(); return save(name, b, 'image/jpeg'); }
const pendingImgs = []; function imgLater(dataUrl, tag, cb) { pendingImgs.push(img(dataUrl, tag).then(cb)); }

// Szene ohne Himmel zeichnen: wo danach nichts steht (Alpha 0, Magenta), sieht man ins Leere
function withVoidScene(fn) {
  const r = A.renderer, hide = [A.sky, A.skyBox, A.HORIZ].filter(Boolean), vis = hide.map(o => o.visible), bg = A.scene.background, cc = r.getClearColor(new T.Color()), ca = r.getClearAlpha(), prev = r.getRenderTarget();
  hide.forEach(o => o.visible = false); A.scene.background = null; r.setClearColor(0xff00ff, 0);
  try { return fn(); } finally { hide.forEach((o, k) => o.visible = vis[k]); A.scene.background = bg; r.setClearColor(cc, ca); r.setRenderTarget(prev); }
}
function renderTo(rt, cam, buf) { const r = A.renderer, prev = r.getRenderTarget(); r.setRenderTarget(rt); r.clear(); r.render(A.scene, cam); r.readRenderTargetPixels(rt, 0, 0, TW, TH2, buf); r.setRenderTarget(prev); }
const isVoid = (b, i) => b[i + 3] === 0;   /* nichts gezeichnet: der Hintergrund bleibt durchsichtig (Alpha 0) – jede deckende oder halbdurchsichtige Fläche hinterlässt Alpha > 0 */

// Prüfung einer Ansicht: (1) Blick nach unten ins Leere = Loch, (2) Z-Fighting: die Szene zweimal mit winzig verschobener Kamera zeichnen –
// auf glatten Flächen darf sich dabei nichts ändern; wechselt dort die Farbe, kämpfen zwei Flächen um denselben Tiefenwert.
const _v = new T.Vector3(), _o = new T.Vector3();
function probe(cam) {
  const out = { void: 0, zf: 0, marks: [] }, aspect = cam.aspect; cam.aspect = TW / TH2; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  // (1) Löcher
  withVoidScene(() => renderTo(rtA, cam, bufA));
  const vm = new Map(); let firstHit = null;
  for (let y = 0; y < TH2; y += 2) for (let x = 0; x < TW; x += 2) { const i = (y * TW + x) * 4; if (!isVoid(bufA, i)) continue;
    _v.set((x + 0.5) / TW * 2 - 1, (y + 0.5) / TH2 * 2 - 1, 0.5).unproject(cam).sub(cam.position).normalize();
    if (_v.y > -0.08) continue;   /* nahe am Horizont oder nach oben: dort ist Himmel normal */
    out.void++; const k = (x >> 4) + ',' + (y >> 4); if (!vm.has(k)) vm.set(k, [x, TH2 - 1 - y]);
    if (!firstHit) { const e = A.FLAT ? 0 : (A.ELEV[A.pl.idx] || 0), t = (e - cam.position.y) / _v.y; if (t > 0 && t < 2000) firstHit = [cam.position.x + _v.x * t, cam.position.z + _v.z * t]; } }
  if (out.void >= 6) { for (const [x, y] of vm.values()) out.marks.push([x + 8, y - 8, 10, '#ff00ff']); if (firstHit) out.voidAt = sOf(firstHit[0], firstHit[1]).s; }
  // (2) Z-Fighting: dieselbe Ansicht mit anderer Nahebene zeichnen. Das verschiebt kein einziges Pixel (x/y bleiben gleich),
  // ändert aber die Rundung im Tiefenpuffer – wechselt ein Pixel dabei die Farbe, kämpfen dort zwei Flächen um den Vorrang.
  const c2 = cam.clone(), n0 = cam.near; renderTo(rtA, cam, bufA);
  const sm = A.renderer.shadowMap, au = sm.autoUpdate; sm.autoUpdate = false; sm.needsUpdate = false;   /* Schatten aus Bild A behalten – sonst verschieben sich Schattenkanten mit der Nahebene */
  c2.near = n0 * 0.9; c2.updateProjectionMatrix(); c2.updateMatrixWorld(); renderTo(rtB, c2, bufB);   /* Nahebene leicht nach innen: nichts wird abgeschnitten, die Tiefe nur etwas anders gerundet – */
  c2.near = n0 * 0.8; c2.updateProjectionMatrix(); renderTo(rtC, c2, bufC);   /* was dabei kippt, flimmert auch im Spiel, sobald sich die Kamera bewegt */
  sm.autoUpdate = au;
  const LA = new Float32Array(TW * TH2), LB = new Float32Array(TW * TH2), LC = new Float32Array(TW * TH2);
  for (let p = 0; p < TW * TH2; p++) { LA[p] = lum(bufA, p * 4); LB[p] = lum(bufB, p * 4); LC[p] = lum(bufC, p * 4); }
  const cdiff = (b2, p) => Math.abs(bufA[p * 4] - b2[p * 4]) + Math.abs(bufA[p * 4 + 1] - b2[p * 4 + 1]) + Math.abs(bufA[p * 4 + 2] - b2[p * 4 + 2]);
  const zb = new Map();
  for (let y = 0; y < TH2; y++) for (let x = 0; x < TW; x++) { const p = y * TW + x;
    if (cdiff(bufB, p) < 40 && cdiff(bufC, p) < 40) continue;
    const k = (x >> 4) + ',' + (y >> 4); zb.set(k, (zb.get(k) || 0) + 1); out.zf++; }
  const blocks = [...zb.entries()].filter(([, n]) => n >= 4); out.zfBlocks = blocks.length;
  for (const [k] of blocks) { const [bx, by] = k.split(',').map(Number); out.marks.push([bx * 16 + 8, TH2 - 1 - (by * 16 + 8), 9, '#ffd400']); }
  // Bildwerte für "schwarz/einfarbig" (aus der normalen Ansicht ohne Nachbearbeitung)
  let s = 0, s2 = 0, n = 0; for (let p = 0; p < TW * TH2; p += 4) { s += LA[p]; s2 += LA[p] * LA[p]; n++; } out.mean = s / n; out.std = Math.sqrt(Math.max(0, s2 / n - out.mean ** 2));
  cam.aspect = aspect; cam.updateProjectionMatrix();
  return out;
}

// ---------- statische Prüfungen nach dem Streckenbau ----------
// Lange Rechnungen in Häppchen: blockiert die Seite länger als einige Sekunden am Stück, hält Edge sie für hängend
// und behandelt sie danach als verdeckt (bis hin zum Einfrieren) – deshalb alle 80 ms kurz Luft holen.
let _tY = 0; const pause = async () => { if (performance.now() - _tY > 80) { await W8(0); _tY = performance.now(); } };
function groundMeshes() { const out = []; A.trackGroup.traverse(o => { if (!o.isMesh || !o.visible || o === A.HORIZ || !o.geometry || !o.geometry.attributes.position) return; const u = o.userData; if (u.strip || u.tile || u.ground || u.flat || u.fixed) { out.push(o); return; } if (o.isInstancedMesh) return; const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox(); if (g.boundingBox.max.y - g.boundingBox.min.y < 1.5) out.push(o); }); return out; }

// Boden von oben (nur Bodenflächen, orthografisch, kachelweise): Magenta im Streckenbereich = Loch im Boden
async function topVoids() {
  const G = groundMeshes(), LY = 7; G.forEach(o => o.layers.enable(LY));
  const { N, PX, PZ, WL, WR } = A; let x0 = 1e9, x1 = -1e9, z0 = 1e9, z1 = -1e9, yMax = -1e9;
  for (let i = 0; i < N; i++) { const m = Math.max(WL[i], WR[i]) + 30; x0 = Math.min(x0, PX[i] - m); x1 = Math.max(x1, PX[i] + m); z0 = Math.min(z0, PZ[i] - m); z1 = Math.max(z1, PZ[i] + m); yMax = Math.max(yMax, A.FLAT ? 0 : A.ELEV[i]); }
  const TS = 200, RES = 400, mpp = TS / RES, cam = new T.OrthographicCamera(-TS / 2, TS / 2, TS / 2, -TS / 2, 1, 2000); cam.layers.set(LY); cam.up.set(0, 0, -1);
  const rt = new T.WebGLRenderTarget(RES, RES), buf = new Uint8Array(RES * RES * 4), hits = new Map(); let n = 0;
  {
    for (let tx = x0; tx < x1; tx += TS) for (let tz = z0; tz < z1; tz += TS) { await pause();
      // Streckenbereich dieser Kachel grob vormerken (2-m-Raster), damit nur dort genau geprüft wird
      const CM = 100, cm = new Uint8Array(CM * CM); let any = false;
      for (let i = 0; i < N; i += 2) { const R = Math.max(WL[i], WR[i]) + 25, cxp = (PX[i] - tx) / 2, czp = (PZ[i] - tz) / 2, rr = R / 2; if (cxp < -rr || czp < -rr || cxp > CM + rr || czp > CM + rr) continue;
        for (let a = Math.max(0, Math.floor(cxp - rr)); a <= Math.min(CM - 1, Math.ceil(cxp + rr)); a++) for (let b = Math.max(0, Math.floor(czp - rr)); b <= Math.min(CM - 1, Math.ceil(czp + rr)); b++) { cm[b * CM + a] = 1; any = true; } }
      if (!any) continue;
      cam.position.set(tx + TS / 2, yMax + 400, tz + TS / 2); cam.lookAt(tx + TS / 2, 0, tz + TS / 2); cam.updateMatrixWorld();
      withVoidScene(() => { const r = A.renderer; r.setRenderTarget(rt); r.clear(); r.render(A.scene, cam); r.readRenderTargetPixels(rt, 0, 0, RES, RES, buf); });
      for (let py = 0; py < RES; py += 2) for (let px = 0; px < RES; px += 2) { const i = (py * RES + px) * 4; if (!isVoid(buf, i)) continue;
        const wx = tx + (px + 0.5) * mpp, wz = tz + TS - (py + 0.5) * mpp; if (!cm[Math.floor((wz - tz) / 2) * CM + Math.floor((wx - tx) / 2)]) continue;
        const [d, j] = A.nearestDist(wx, wz); if (d > Math.max(A.WL[j], A.WR[j]) + 25) continue;
        n++; const k = Math.round(wx / 10) + ',' + Math.round(wz / 10); const e = hits.get(k) || { x: Math.round(wx), z: Math.round(wz), s: Math.round(j * A.DS), d: +d.toFixed(1), inWall: d < Math.max(A.WL[j], A.WR[j]), n: 0 }; e.n++; hits.set(k, e); } }
  }
  G.forEach(o => o.layers.disable(LY)); rt.dispose();
  // benachbarte 10-m-Zellen (bis 25 m Abstand) zu einem Loch zusammenfassen
  const cl = []; for (const e of [...hits.values()].filter(e => e.n >= 2).sort((a, b) => b.n - a.n)) { const c = cl.find(c => Math.hypot(c.x - e.x, c.z - e.z) < 25 + c.r); if (c) { c.n += e.n; c.cells++; c.r = Math.max(c.r, Math.hypot(c.x - e.x, c.z - e.z)); c.inWall = c.inWall || e.inWall; c.d = Math.min(c.d, e.d); } else cl.push({ ...e, cells: 1, r: 0 }); }
  const list = cl.map(c => ({ ...c, r: Math.round(c.r), m2: Math.round(c.n * 4 * mpp * mpp) })).sort((a, b) => b.inWall - a.inWall || b.n - a.n);
  return { px: n, spots: list.length, list: list.slice(0, 12) };
}

// Z-Fighting im Boden: Strahlen von oben – zwei verschiedene, deckende Flächen in weniger als 2 cm Abstand flimmern gegeneinander.
// Ein Treffer zählt erst, wenn er 30 cm daneben wieder auftritt (Kanten zwischen zwei Streifen sind kein Fehler).
async function groundZFight() {
  const G = groundMeshes().filter(o => { const m = o.material; return m && !Array.isArray(m) && !m.transparent && m.depthWrite !== false && m.depthTest !== false && !m.polygonOffset; });
  const rc = new T.Raycaster(), dn = new T.Vector3(0, -1, 0), o3 = new T.Vector3(), { N, DS, PX, PZ, RX, RZ, WL, WR } = A, st = Math.max(1, Math.round(10 / DS)), out = new Map(); let n = 0;
  const pair = (x, z, e) => { rc.set(o3.set(x, e + 8, z), dn); rc.far = 16; const h = rc.intersectObjects(G, false); for (let k = 0; k + 1 < h.length; k++) { const a = h[k], b = h[k + 1]; if (b.distance - a.distance > 0.02) continue; if (a.object === b.object && a.faceIndex === b.faceIndex) continue; if (a.object === b.object) continue; return [a, b]; } return null; };
  for (let i = 0; i < N; i += st) { await pause(); const e = A.FLAT ? 0 : A.ELEV[i]; for (let o = -(WL[i] + 6) + 0.37; o <= WR[i] + 6; o += 2.1) { const x = PX[i] + RX[i] * o, z = PZ[i] + RZ[i] * o; n++; const p = pair(x, z, e); if (!p) continue;
      if (!pair(x + 0.3 * RZ[i] + 0.21 * RX[i], z - 0.3 * RX[i] + 0.21 * RZ[i], e)) continue;
      const k = Math.round(i * DS / 20); const m = out.get(k) || { s: Math.round(i * DS), lat: +o.toFixed(1), x: Math.round(x), z: Math.round(z), y: +p[0].point.y.toFixed(2), a: tagOf(p[0].object), b: tagOf(p[1].object), n: 0 }; m.n++; out.set(k, m); } }
  const list = [...out.values()].sort((a, b) => b.n - a.n); return { rays: n, spots: list.length, list: list.slice(0, 12) };
}
const tagOf = o => { const m = o.material, c = m && m.color ? '#' + m.color.getHexString() : ''; return (o.name || o.geometry.type.replace('Geometry', '')) + ' ' + (m && m.map ? 'tex ' : '') + c + (Object.keys(o.userData).length ? ' [' + Object.keys(o.userData).join('/') + ']' : ''); };

// Kies/Auslauf-Löcher (wie __holes im Spiel, aber in Häppchen und nach Stellen zusammengefasst): wo die Fahrphysik Kies oder Auslauf meldet,
// muss von oben zuerst ein Streifen getroffen werden – trifft der Strahl den Rasenboden (oder nichts), schaut Rasen durch
async function gravelHoles(step = 2, dl = 1.5) {
  const rc = new T.Raycaster(), dn = new T.Vector3(0, -1, 0), o3 = new T.Vector3(), objs = [], { N, PX, PZ, RX, RZ, HW, WL, WR, DS } = A;
  A.trackGroup.traverse(o => { if (!o.isMesh || o.isInstancedMesh || !o.visible || !o.geometry || !o.geometry.attributes.position) return; const u = o.userData; if (u.strip || u.tile || u.ground || u.flat || u.fixed) { objs.push(o); return; } const g = o.geometry; if (!g.boundingBox) g.computeBoundingBox(); if (g.boundingBox.max.y - g.boundingBox.min.y < 1.5) objs.push(o); });
  let n = 0, bad = 0; const bins = new Map();
  for (const [sd, W] of [[-1, WL], [1, WR]]) for (let i = 0; i < N; i += step) { await pause();
    for (let o = HW[i] + 3; o <= W[i] - 1.6; o += dl) { const sf = A.surface(i, sd * o); if (sf !== 'gravel' && sf !== 'runoff') continue; if (A.surface((i - 2 + N) % N, sd * o) !== sf || A.surface((i + 2) % N, sd * o) !== sf) continue;
      const x = PX[i] + RX[i] * sd * o, z = PZ[i] + RZ[i] * sd * o, [d, j] = A.nearestDist(x, z); if (d < HW[j] + 2.5 || Math.abs(j - i) > 40 && Math.abs(j - i) < N - 40) continue;
      rc.set(o3.set(x, (A.FLAT ? 0 : A.ELEV[i]) + 6, z), dn); rc.far = 14; const h = rc.intersectObjects(objs, false)[0]; n++;
      if (!h || h.object.userData.tile || h.object.userData.ground) { bad++; const k = sd + ':' + Math.round(i * DS / 25); const e = bins.get(k) || [Math.round(i * DS), sd, Math.round(o), sf, 0]; e[4]++; bins.set(k, e); } } }
  // benachbarte 25-m-Abschnitte derselben Seite zusammenfassen
  const at = []; for (const e of [...bins.values()].sort((a, b) => a[1] - b[1] || a[0] - b[0])) { const l = at[at.length - 1]; if (l && l[1] === e[1] && e[0] - l[5] <= 30) { l[4] += e[4]; l[5] = e[0]; } else at.push([...e, e[0]]); }
  return { trk: A.TRK.name, kind: A.TH.runoffKind, flat: !!A.FLAT, n, bad, spots: at.length, at: at.sort((a, b) => b[4] - a[4]).slice(0, 8).map(a => [a[0], a[1], a[2], a[3], a[4], a[5]]) };
}

// kaputte Geometrie (NaN), fehlende Texturen, Materialien ohne Shader
function integrity() {
  const nan = [], tex = new Set(); let meshes = 0;
  A.scene.traverse(o => { if (!o.isMesh || !o.geometry) return; meshes++; const g = o.geometry; try { if (!g.boundingSphere) g.computeBoundingSphere(); if (!g.boundingSphere || !isFinite(g.boundingSphere.radius) || isNaN(g.boundingSphere.center.x)) nan.push(tagOf(o)); } catch (e) { nan.push(tagOf(o) + ' (' + e.message + ')'); }
    for (const m of [].concat(o.material || [])) for (const k of ['map', 'normalMap', 'roughnessMap', 'alphaMap', 'emissiveMap']) { const t = m[k]; if (!t || t.isRenderTargetTexture || t.isDataTexture || t.isCanvasTexture) continue; const im = t.image; if (!im) tex.add(k + ' fehlt: ' + tagOf(o)); else if (im.complete === false || (im.naturalWidth === 0 && im.width === 0)) tex.add(k + ' nicht geladen: ' + (im.src || '').split('/').pop()); } });
  return { meshes, nan: nan.slice(0, 10), nanN: nan.length, tex: [...tex].slice(0, 10), texN: tex.size };
}

// Ansicht einer Stelle für den Bericht (von schräg oben, 14 m hinter der Stelle in Fahrtrichtung)
function viewOf(s, lat, mark = true) {
  const { N, DS, PX, PZ, TX, TZ } = A, i = Math.floor(((s % A.L) + A.L) % A.L / DS) % N, e = A.FLAT ? 0 : A.ELEV[i];
  const x = PX[i] + A.RX[i] * lat, z = PZ[i] + A.RZ[i] * lat, cam = new T.PerspectiveCamera(60, TW / TH2, 0.3, 4000);
  cam.position.set(x - TX[i] * 14, e + 7, z - TZ[i] * 14); cam.lookAt(x, e, z); cam.updateMatrixWorld();
  renderTo(rtA, cam, bufA); return rtJpeg(bufA, mark ? [[TW / 2, TH2 / 2, 22, '#ff3b30']] : null);
}

async function staticChecks(R) {
  const t0 = performance.now(), st = R.static = {};
  const run = async (name, fn) => { log('Statische Prüfung: ' + name); await W8(30); const t = performance.now(); try { st[name] = await fn(); } catch (e) { st[name] = { error: String(e.message || e) }; } st[name + '_ms'] = Math.round(performance.now() - t); };
  await run('integrity', integrity);
  await run('topVoids', topVoids);
  await run('groundZFight', groundZFight);
  await run('gravelHoles', gravelHoles);
  if (window.__clipAll) await run('clipAll', () => { const r = window.__clipAll(); return { n: r.length, list: r.slice(0, 8) }; });
  if (window.__onRoad) await run('onRoad', () => { const r = window.__onRoad(); return { n: r.length, list: r.slice(0, 8) }; });
  if (window.__bldOverlap) await run('bldOverlap', () => window.__bldOverlap());
  if (window.__clipCheck) await run('facadeClip', () => window.__clipCheck());
  st.ms = Math.round(performance.now() - t0);
  // Befunde mit Bild
  const I = st.integrity || {};
  if (I.nanN) issue(R, 'hoch', 'Rendering', I.nanN + ' Objekte mit ungültiger Geometrie (NaN)', null, I.nan.join(' · '));
  if (I.texN) issue(R, 'mittel', 'Rendering', I.texN + ' Texturen fehlen oder laden nicht', null, I.tex.join(' · '));
  const tv = st.topVoids || {};
  for (const e of (tv.list || []).slice(0, 5)) { const lat = 0; issue(R, e.inWall ? 'hoch' : 'mittel', 'Loch im Boden', 'Kein Boden ' + (e.inWall ? 'innerhalb der Absperrung' : 'neben der Strecke') + ' (ca. ' + e.m2 + ' m², ' + e.d + ' m von der Streckenmitte)', e.s, 'x ' + e.x + ' · z ' + e.z, viewAt(e.x, e.z)); void lat; }
  const zf = st.groundZFight || {};
  for (const e of (zf.list || []).slice(0, 5)) issue(R, 'mittel', 'Z-Fighting', 'Zwei Bodenflächen liegen aufeinander (< 2 cm): ' + e.a + ' / ' + e.b, e.s, 'seitlich ' + e.lat + ' m · ' + e.n + ' Treffer', viewAt(e.x, e.z));
  const gh = st.gravelHoles || {};
  if (gh.bad) for (const a of (gh.at || []).slice(0, 5)) issue(R, 'mittel', 'Loch im Boden', 'Rasen schaut durch ' + (a[3] === 'gravel' ? 'das Kiesbett' : 'den Auslauf') + ' (' + a[4] + ' Messpunkte' + (a[5] > a[0] ? ', bis ' + at(a[5]) : '') + ')', a[0], 'Seite ' + (a[1] < 0 ? 'links' : 'rechts') + ', ' + a[2] + ' m neben der Mitte', viewOf(a[0], a[1] * a[2]));
  const ca = st.clipAll || {};
  for (const e of (ca.list || []).slice(0, 4)) issue(R, 'mittel', 'Clipping', 'Objekt ragt in Fahrbahn/Auslauf (' + e.h.toFixed(1) + ' m hoch, ' + e.n + ' Bodenpunkte)', e.s, 'seitlich ' + e.lat + ' m, Grenze ' + e.lim + ' m', viewAt(e.x, e.z));
  const orr = st.onRoad || {};
  for (const e of (orr.list || []).filter(e => !(e.geo === 'PlaneGeometry' && Math.abs(e.dy) < 0.25)).slice(0, 3)) issue(R, 'info', 'Clipping', 'Objekt auf der Fahrbahn (' + e.type + ' ' + e.geo + (e.col ? ' #' + e.col : '') + ', ' + e.dy + ' m über Asphalt)', e.s, e.ud || '', viewAt(e.x, e.z));
  const bo = st.bldOverlap || {};
  for (const e of (bo.ex || []).slice(0, 3)) issue(R, 'info', 'Clipping', 'Gebäude überschneiden sich (' + e[0] + ' / ' + e[1] + ')', e[2], '', viewAt((e[3] + e[5]) / 2, (e[4] + e[6]) / 2, 40));
  const fc = st.facadeClip || {};
  if (fc.clipping) issue(R, 'mittel', 'Clipping', fc.clipping + ' Fassaden stehen auf der Strecke', null, '');
}
function viewAt(x, z, back = 14) { const [, j] = A.nearestDist(x, z), e = A.FLAT ? 0 : A.ELEV[j]; const cam = new T.PerspectiveCamera(60, TW / TH2, 0.3, 4000); cam.position.set(x - A.TX[j] * back, e + back * 0.5, z - A.TZ[j] * back); cam.lookAt(x, e, z); cam.updateMatrixWorld(); renderTo(rtA, cam, bufA); return rtJpeg(bufA, [[TW / 2, TH2 / 2, 22, '#ff3b30']]); }

function issue(R, sev, cat, msg, s, det, jpeg) { const it = { sev, cat, msg, s: s == null ? null : Math.round(s), det: det || '' }; R.issues.push(it); if (jpeg) imgLater(jpeg, cat.replace(/\W+/g, ''), p => it.img = p); return it; }

// ---------- Fahrt: Bildzeiten messen, Ansichten prüfen ----------
function drive(R) {
  return new Promise(done => {
    const pl = A.pl, cams = [0, 1, 2].concat(pl.mesh && pl.mesh.tv ? [3] : []), nc = cams.length;
    const lapsWanted = CFG.laps || (CFG.mode === 'quick' ? 1 : nc);
    R.cams = cams.map(c => CAMN[c]); R.laps = lapsWanted;
    const F = { t: [], s: [], cam: [], lap: [], k: [] }, hitches = [], samples = [];
    let prev = 0, skip = 2, nextShot = 0, lapC = null, lastLap = -1, camNow = -1, hitchShots = 0, t0 = performance.now(), slowT = 0, offT = 0, lastS = 0;
    const tMax = (lapsWanted * (A.L / 40) + 90) * 1000, tRace = lapsWanted * (A.L / 35) + 60;   // Notbremse nach Rennzeit (Schnitt unter 126 km/h); die Uhr darf im Hintergrundbetrieb viel länger laufen
    const camFor = (lap, s) => CFG.mode === 'quick' && !CFG.laps ? cams[Math.min(nc - 1, Math.floor(s / A.L * nc))] : cams[lap % nc];
    const hb = setInterval(() => { const p = A.pl; log('Fahrt: ' + A.raceState + ' t=' + (A.raceTime || 0).toFixed(0) + ' s · ' + Math.round(sLap()) + ' m · Runde ' + (lapC == null ? '-' : lapC < 0 ? 'Anlauf' : lapC + 1) + ' · ' + Math.round((p.v || 0) * 3.6) + ' km/h · Kamera ' + CAMN[A.S.cam] + ' · ' + F.t.length + ' Bilder · ' + samples.length + ' Ansichten' + (A.paused ? ' · PAUSE' : '') + (document.hidden ? ' · VERSTECKT' : '') + ' · rAF ' + rafN + ' · hook ' + hookN + ' · selbst ' + PUMP.n); rafN = hookN = PUMP.n = 0; }, 10000);
    let cur = null;
    // eine Bildzeit verbuchen – k 0: echter Abstand zweier angezeigter Bilder, k 1: Rechenzeit inkl. Grafikkarte (Fenster verdeckt)
    const rec = (dt, k) => { if (!cur) return; const { s, cm, lr, now } = cur; if (skip > 0) { skip--; return; } if (!(dt > 0 && dt < 5000)) return;
      F.t.push(+dt.toFixed(1)); F.s.push(Math.round(s)); F.cam.push(cm); F.lap.push(lr); F.k.push(k);
      if (dt > 30) { const h = { s: Math.round(s), dt: Math.round(dt), cam: cm, lap: lr, k, lt: longTasks.filter(x => x.t > now - dt - 50).reduce((a, x) => Math.max(a, x.d), 0) | 0 };
        hitches.push(h); if (dt > 45 && hitchShots < 8 * (lr + 1)) { hitchShots++; imgLater(screenJpeg(), 'ruckler', p => h.img = p); } } };
    PUMP.cb = w => rec(w, 1);
    const finish = why => { PUMP.cb = null; clearInterval(hb); window.__qcF = null; R.drive = { why, ms: Math.round(performance.now() - t0) }; R.frames = F; R.hitches = hitches; R.samples = samples; done(); };
    window.__qcF = (now, forced) => {
      if (forced) return; hookN++;
      const st = A.raceState; if (st !== 'race' || A.raceTime < 2 || A.paused) { prev = now; return; }
      // Runden selbst zählen: ab der ersten Überquerung der Ziellinie (steht die Startaufstellung kurz dahinter, zählt die Runde sofort)
      const s = sLap(); if (lapC === null) { lapC = s < 300 ? 0 : -1; lastS = s; }
      if (lastS > A.L - 400 && s < 400) lapC++;
      const lr = lapC; if (lr < 0) { lastS = s; prev = now; return; }
      if (lr >= lapsWanted) return finish('fertig');
      if (A.raceTime > tRace || performance.now() - t0 > tMax * 4) return finish('Zeitlimit – Runden nicht geschafft (Bot zu langsam oder hängt fest)');
      const cm = camFor(lr, s); if (cm !== camNow) { A.S.cam = cm; camNow = cm; skip = 3; R.events.push({ t: 'Kamera', s: Math.round(s), lap: lr, v: CAMN[cm] }); }
      if (lr !== lastLap) { lastLap = lr; nextShot = s + CFG.shot * 0.5; uiHead = 'QC-Bot · ' + R.name + ' · Runde ' + (lr + 1) + '/' + lapsWanted; }
      const dt = now - prev; prev = now;
      cur = { s, cm, lr, now }; if (!PUMP.on) rec(dt, 0);
      // Fahrer-Bot: steckt fest oder fährt neben der Strecke?
      const v = A.pl.v || 0; slowT = v < 8 ? slowT + dt / 1000 : 0; if (slowT > 4) { R.events.push({ t: 'Bot steht', s: Math.round(s), lap: lr }); slowT = -30; }
      const sf = A.pl.surf; offT = sf && sf !== 'road' && sf !== 'kerb' ? offT + dt / 1000 : 0; if (offT > 1.5) { R.events.push({ t: 'Bot neben der Strecke (' + sf + ')', s: Math.round(s), lap: lr }); offT = -10; }
      if (Math.abs(s - lastS) > A.L / 2) nextShot = CFG.shot * 0.5; lastS = s;
      // Ansicht prüfen
      if (CFG.at && !inAt(s)) nextShot = s;   /* außerhalb des Abschnitts keine Ansichten – die erste Stelle im Abschnitt wird sofort geprüft */
      else if (s >= nextShot && s < nextShot + 300) {
        nextShot = s + CFG.shot; skip = 2;
        const shot = screenJpeg(), st2 = screenStats(), smp = { s: Math.round(s), lap: lr, cam: CAMN[cm], view: 'Kamera', mean: st2.mean, std: st2.std };
        const pr = probe(A.camera); Object.assign(smp, { void: pr.void, zf: pr.zfBlocks, zfPx: pr.zf });
        smp.calls = A.renderer.info.render.calls; smp.tris = A.renderer.info.render.triangles;
        const gl = A.renderer.getContext(), ge = gl.getError(); if (ge) smp.glErr = ge;
        samples.push(smp); imgLater(pr.marks.length ? (cx.drawImage(A.renderer.domElement, 0, 0, TW, TH2), drawMarks(pr.marks.map(m => [m[0], m[1], m[2], m[3]])), cv.toDataURL('image/jpeg', 0.72)) : shot, 'cam' + cm, p => smp.img = p);
        flagSample(R, smp, pr, cm);
        // Rundumblick (nur in der Verfolger-Runde, jede zweite Stelle): links, rechts, hinten, von oben
        if (cm === 0 && (CFG.at || samples.filter(x => x.cam === CAMN[0] && x.view === 'Kamera').length % 2 === 1)) for (const [nm, yaw, up, dist] of [['links', Math.PI / 2, 2.6, 0], ['rechts', -Math.PI / 2, 2.6, 0], ['hinten', Math.PI, 2.6, 0], ['oben', 0, 26, 18]]) {
          const p = A.pl, h = p.h + yaw, c3 = new T.PerspectiveCamera(62, TW / TH2, 0.8, A.camera.far), ey = p.ey || 0;   /* Nah- und Fernebene wie die Kamera im Spiel (mit 4000 m wurden die Berge abgeschnitten und die Schnittkante als Flimmern gemeldet) */
          c3.position.set(p.x - Math.sin(h) * dist, ey + up, p.z - Math.cos(h) * dist);   /* seitlich/hinten: direkt über dem Auto (nie hinter Zäunen), oben: 18 m zurück */ c3.lookAt(p.x + Math.sin(h) * 30, ey + (up > 10 ? 0 : 0.8), p.z + Math.cos(h) * 30); c3.updateMatrixWorld();
          const q = probe(c3), sm2 = { s: Math.round(s), lap: lr, cam: CAMN[0], view: nm, void: q.void, zf: q.zfBlocks, zfPx: q.zf, mean: +q.mean.toFixed(1), std: +q.std.toFixed(1) };
          renderTo(rtA, c3, bufA); samples.push(sm2); imgLater(rtJpeg(bufA, q.marks), 'rund', pth => sm2.img = pth); flagSample(R, sm2, q, 0);
        }
      }
    };
  });
}
function flagSample(R, smp, pr, cm) {
  const where = smp.cam + (smp.view !== 'Kamera' ? ' (Blick ' + smp.view + ')' : '');
  if (pr.void >= 25) issue(R, pr.void > 200 ? 'hoch' : 'mittel', 'Loch im Boden', 'Blick ins Leere unterhalb des Horizonts (' + pr.void + ' Pixel) – ' + where, pr.voidAt ?? smp.s, 'Magenta-Kästen im Bild', null).ref = smp;
  if (pr.zfBlocks > 150) issue(R, 'info', 'Rendering', 'Ansicht großflächig unruhig (' + pr.zfBlocks + ' Bereiche) – meist ein Zaun oder Objekt direkt vor der Kamera – ' + where, smp.s, 'kein typisches Z-Fighting', null).ref = smp;
  else if (pr.zfBlocks >= 3) { const it = issue(R, pr.zfBlocks >= 8 ? 'mittel' : 'info', 'Z-Fighting', 'Flimmernde Flächen (' + pr.zfBlocks + ' Bereiche) – ' + where, smp.s, 'gelbe Kästen im Bild', null); it.ref = smp; it.zb = pr.zfBlocks; }
  if (smp.mean < 12 && smp.std < 6) issue(R, 'hoch', 'Rendering', 'Bild fast schwarz – ' + where, smp.s, 'Helligkeit ' + smp.mean, null).ref = smp;
  else if (smp.std < 5) issue(R, 'mittel', 'Rendering', 'Bild einfarbig (Kamera in einem Objekt?) – ' + where, smp.s, 'Kontrast ' + smp.std, null).ref = smp;
  else if (smp.mean > 240) issue(R, 'mittel', 'Rendering', 'Bild überbelichtet – ' + where, smp.s, 'Helligkeit ' + smp.mean, null).ref = smp;
  if (smp.glErr) issue(R, 'hoch', 'Rendering', 'WebGL-Fehler ' + smp.glErr + ' – ' + where, smp.s, '', null);
  void cm;
}

// ---------- Auswertung der Bildzeiten ----------
function perfSummary(R) {
  const F = R.frames, out = { all: null, byCam: {}, firstLap: null, hot: [] }; if (!F || !F.t.length) return out;
  const sum = idx => { const a = idx.map(k => F.t[k]); if (!a.length) return null; const med = pct(a, 0.5), n = a.length, tot = a.reduce((x, y) => x + y, 0);
    return { n, fps: +(1000 * n / tot).toFixed(1), med: +med.toFixed(1), p95: +pct(a, 0.95).toFixed(1), p99: +pct(a, 0.99).toFixed(1), max: Math.round(Math.max(...a)), d33: a.filter(x => x > 30).length, d50: a.filter(x => x > 50).length, d100: a.filter(x => x > 100).length, perMin: +(a.filter(x => x > 50).length / (tot / 60000)).toFixed(1) }; };
  const hid = F.k.filter(x => x).length / F.k.length; R.timing = hid > 0.5 ? 'Rechenzeit je Bild bis die Grafikkarte fertig ist (Fenster war verdeckt, ' + Math.round(hid * 100) + ' %)' : 'Abstand der angezeigten Bilder (echte Anzeige)';
  const all = F.t.map((_, k) => k); out.all = sum(all);
  for (const c of new Set(F.cam)) { const mine = all.filter(k => F.cam[k] === c), later = mine.filter(k => F.lap[k] > 0); out.byCam[CAMN[c]] = sum(later.length > 200 ? later : mine); }   /* ohne Aufwärmrunde, falls die Kamera auch später fuhr */
  out.firstLap = sum(all.filter(k => F.lap[k] === 0));
  // wiederkehrende Ruckelstellen: 25-m-Abschnitte mit Rucklern (>50 ms) in mehreren Runden, oder einmal sehr stark (>120 ms) nach der ersten Runde
  const bins = new Map(); for (const h of R.hitches) { if (h.dt <= 50) continue; const b = Math.round(h.s / 25); const e = bins.get(b) || { s: b * 25, laps: new Set(), n: 0, max: 0, cams: new Set(), img: null, bg: undefined }; e.laps.add(h.lap); e.n++; e.max = Math.max(e.max, h.dt); e.cams.add(CAMN[h.cam]); e.bg = e.bg !== false && h.k === 1; if (!e.img && h.img) e.img = h.img; bins.set(b, e); }
  out.hot = [...bins.values()].filter(e => e.laps.size >= 2 || e.max > 120 && [...e.laps].some(l => l > 0)).sort((a, b) => b.max - a.max).slice(0, 8).map(e => ({ s: e.s, laps: [...e.laps].map(l => l + 1), n: e.n, max: e.max, cams: [...e.cams], img: e.img, bg: e.bg }));
  // Befunde
  const a = out.all; if (a) {
    if (a.perMin > 6 || a.p99 > 60) issue(R, 'hoch', 'Ruckler', 'Häufige Ruckler: ' + a.perMin + ' pro Minute über 50 ms, p99 ' + a.p99 + ' ms', null, 'Median ' + a.med + ' ms, ' + a.fps + ' fps');
    else if (a.perMin > 1.5 || a.p99 > 40) issue(R, 'mittel', 'Ruckler', 'Gelegentliche Ruckler: ' + a.perMin + ' pro Minute über 50 ms, p99 ' + a.p99 + ' ms', null, 'Median ' + a.med + ' ms, ' + a.fps + ' fps');
    if (a.med > 20) issue(R, hid > 0.5 ? 'info' : 'mittel', 'Ruckler', 'Grundtempo unter 50 fps (Median ' + a.med + ' ms)', null, 'Bildrate ' + a.fps + ' fps' + (hid > 0.5 ? ' · im Hintergrund gemessen, mit --show prüfen' : ''));
  }
  for (const h of out.hot) { const bg = h.bg && h.laps.length === 1 && h.n === 1;   /* ein einzelner Riesen-Aussetzer im Hintergrundbetrieb kann auch vom System kommen */
    const it = issue(R, bg ? 'mittel' : h.max > 120 ? 'hoch' : 'mittel', 'Ruckler', 'Ruckelstelle: bis ' + h.max + ' ms (Runde ' + h.laps.join(', ') + ' · ' + h.cams.join(', ') + ')', h.s, h.n + ' Ruckler im Abschnitt' + (bg ? ' · einmalig und im Hintergrund gemessen – mit --show bestätigen' : '')); it.img = h.img; }
  const fl = out.firstLap; if (fl && fl.d100 >= 3 && R.laps > 1) issue(R, 'info', 'Ruckler', 'Erste Runde: ' + fl.d100 + ' Bilder über 100 ms (Shader/Texturen werden erst beim ersten Anblick geladen)', null, 'max ' + fl.max + ' ms');
  return out;
}

// Dreiecke im Umkreis r eines Punkts aus einer Geometrie entfernen (Kopie – geteilte Geometrien bleiben heil)
function cutHole(o, p, r) { o.updateMatrixWorld(true); const g = o.geometry.clone(), P = g.attributes.position, inv = new T.Matrix4().copy(o.matrixWorld).invert(), c = p.clone().applyMatrix4(inv), v = new T.Vector3();
  const idx = g.index ? Array.from(g.index.array) : Array.from({ length: P.count }, (_, k) => k), keep = [];
  const q = [new T.Vector3(), new T.Vector3(), new T.Vector3()], side = (a, b) => (b.x - a.x) * (c.z - a.z) - (b.z - a.z) * (c.x - a.x);
  for (let k = 0; k < idx.length; k += 3) { let near = false; for (let j = 0; j < 3; j++) { q[j].fromBufferAttribute(P, idx[k + j]); if (Math.hypot(q[j].x - c.x, q[j].z - c.z) < r) near = true; }
    const d1 = side(q[0], q[1]), d2 = side(q[1], q[2]), d3 = side(q[2], q[0]); if ((d1 >= 0 && d2 >= 0 && d3 >= 0) || (d1 <= 0 && d2 <= 0 && d3 <= 0)) near = true;   /* große Dreiecke: enthält es die Stelle? */
    if (!near) keep.push(idx[k], idx[k + 1], idx[k + 2]); } void v;
  g.setIndex(keep); o.geometry = g; if (o.userData.lodHi) o.userData.lodHi = g; }
// ---------- Selbsttest: absichtlich Fehler einbauen, die der Bot finden muss ----------
// (a) bei 300 m eine rote Fläche exakt auf dem Asphalt (Z-Fighting), (b) bei 700 m die Bodenfläche neben der Strecke ausblenden (Loch)
function selfTest(R) {
  const { DS, PX, PZ, RX, RZ, TX, TZ, HW } = A, rc = new T.Raycaster(), dn = new T.Vector3(0, -1, 0), G = groundMeshes(), out = {};
  const hit = (x, z) => { rc.set(new T.Vector3(x, 500, z), dn); rc.far = 1000; return rc.intersectObjects(G, false)[0]; };
  { const i0 = Math.round(300 / DS), n = Math.round(40 / DS), P = [], I = [];
    for (let k = 0; k <= n; k++) { const i = i0 + k; for (let o = -HW[i] * 0.8; o <= HW[i] * 0.8 + 0.01; o += HW[i] * 0.4) { const x = PX[i] + RX[i] * o, z = PZ[i] + RZ[i] * o, h = hit(x, z); P.push(x, h ? h.point.y : 0, z); } }
    for (let k = 0; k < n; k++) for (let j = 0; j < 4; j++) { const a = k * 5 + j, b = a + 5; I.push(a, b, a + 1, a + 1, b, b + 1); }
    const g = new T.BufferGeometry(); g.setAttribute('position', new T.Float32BufferAttribute(P, 3)); g.setIndex(I); g.computeVertexNormals();
    g.translate(0, 0.25, 0);   /* zwei deckungsgleiche Flächen (rot/blau) 25 cm über dem Asphalt: kämpfen garantiert um den Tiefenwert */
    const g2 = g.clone(); { const ix = g2.index.array; for (let q = 0; q < ix.length; q += 6) { const a = ix[q], b = ix[q + 1], a1 = ix[q + 2], b1 = ix[q + 5]; ix.set([a, b, b1, a, b1, a1], q); } g2.index.needsUpdate = true; }   /* gleiche Fläche, andere Diagonalen – wie zwei unabhängig gebaute Bodenteile */
    [[g, 0xff2020], [g2, 0x2040ff]].forEach(([gg, c]) => { const m = new T.Mesh(gg, new T.MeshStandardMaterial({ color: c, side: T.DoubleSide, roughness: 1 })); m.userData.flat = true; m.name = 'QC-Selbsttest-ZFight'; A.trackGroup.add(m); });
    out.zfight = '300–340 m'; }
  { const i = Math.round(700 / DS), o = HW[i] + 12, h = hit(PX[i] + RX[i] * o, PZ[i] + RZ[i] * o) || hit(PX[i] - RX[i] * o, PZ[i] - RZ[i] * o);
    if (h) { rc.set(new T.Vector3(h.point.x, 500, h.point.z), dn); const all = rc.intersectObjects(G, false).filter(x => x.point.y > h.point.y - 3); for (const x of all) cutHole(x.object, h.point, 7); out.hole = '700 m: ' + all.length + ' Bodenschichten ausgeblendet (' + [...new Set(all.map(x => tagOf(x.object)))].join(' / ') + ')'; } }
  R.selftest = out; log('Selbsttest eingebaut: ' + JSON.stringify(out)); void TX; void TZ;
}

// ---------- Ablauf einer Strecke ----------
async function runTrack(key) {
  const tr = A.TRACKS[key], ser = CFG.ser && !tr.kartOnly ? CFG.ser : tr.kartOnly ? 'kart' : 'f1';
  TRK_KEY = key; imgN = 0; ERR.length = 0; longTasks = [];
  const R = { key, name: tr.name, full: tr.full || '', ser, gfx: A.S.gfx, mode: CFG.mode, issues: [], events: [], ua: navigator.userAgent, screen: innerWidth + '×' + innerHeight + ' @' + devicePixelRatio, started: new Date().toISOString() };
  uiHead = 'QC-Bot · ' + tr.name; log('Strecke bauen und Rennen starten (' + ser + ')');
  window.__plAI = true; if (tr.extra) A.S.nos = true;
  const t0 = performance.now();
  const ok = await window.__race(tr.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), ser);
  R.buildMs = Math.round(performance.now() - t0);
  if (!ok || !A.running || A.TRK !== tr) { issue(R, 'hoch', 'Ablauf', 'Rennen ließ sich nicht starten (Strecke ' + (A.TRK && A.TRK.name) + ')', null, ''); return finishTrack(R); }
  A.botOn(); A.S.laps = 99; R.L = Math.round(A.L);
  if (CFG.selftest) selfTest(R);
  A.resume();
  if (CFG.stat) { PUMP.hold = true; A.pause(); await staticChecks(R); PUMP.hold = false; A.resume(); }   /* Rennen ruht, solange geprüft wird */
  log('Fahrt startet – ' + (CFG.laps || (CFG.mode === 'quick' ? 1 : 'eine Runde je Kamera')));
  const wd = setInterval(() => { if (A.paused) A.resume(); }, 1000);   // Fenster kurz verdeckt -> Spiel pausiert sich, weiterfahren
  await drive(R); clearInterval(wd);
  R.perf = perfSummary(R);
  for (const e of R.events) if (/Bot steht/.test(e.t)) issue(R, 'mittel', 'Fahrbarkeit', 'Bot-Auto bleibt stehen (Runde ' + (e.lap + 1) + ')', e.s, 'mögliche Kante, Mauer oder Fehler in der Ideallinie');
  { const off = R.events.filter(e => /neben/.test(e.t)); if (off.length >= 2) issue(R, 'info', 'Fahrbarkeit', 'Bot-Auto kommt ' + off.length + '× von der Strecke ab', off[0].s, off.map(e => at(e.s)).slice(0, 8).join(', ')); }
  if (R.drive.why !== 'fertig') issue(R, 'hoch', 'Ablauf', R.drive.why, null, '');
  return finishTrack(R);
}
async function finishTrack(R) {
  // Konsolenfehler zusammenfassen
  const errs = new Map(); for (const e of ERR) { const k = e.lv + ':' + e.m.replace(/\d+/g, '#').slice(0, 160); const x = errs.get(k) || { lv: e.lv, m: e.m, n: 0 }; x.n++; errs.set(k, x); }
  R.errors = [...errs.values()].sort((a, b) => (b.lv === 'error') - (a.lv === 'error') || b.n - a.n).slice(0, 25);
  for (const e of R.errors.filter(e => e.lv === 'error' && /qc-bot/.test(e.m)).slice(0, 3)) issue(R, 'mittel', 'Ablauf', 'Fehler im QC-Bot selbst (kein Spielfehler): ' + e.m.slice(0, 160), null, '');
  for (const e of R.errors.filter(e => e.lv === 'error' && !/qc-bot/.test(e.m)).slice(0, 6)) issue(R, /shader|program|WebGL/i.test(e.m) ? 'hoch' : 'mittel', 'Rendering', 'Konsolenfehler' + (e.n > 1 ? ' (' + e.n + '×)' : '') + ': ' + e.m.slice(0, 160), null, '');
  try { const gl = A.renderer.getContext(), ex = gl.getExtension('WEBGL_debug_renderer_info'); R.gpuName = ex ? gl.getParameter(ex.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); } catch (e) {}
  R.mem = performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : null;
  const ri = A.renderer.info; R.gpu = { geo: ri.memory.geometries, tex: ri.memory.textures, prog: ri.programs ? ri.programs.length : 0 };
  await Promise.all(pendingImgs); pendingImgs.length = 0;
  for (const it of R.issues) if (it.ref) { it.img = it.img || it.ref.img; delete it.ref; }
  if (CFG.at) { R.at = CFG.at; R.issues = R.issues.filter(i => i.s == null ? i.cat !== 'Z-Fighting' : inAt(i.s, 30)); }   /* Abschnittsprüfung: nur Befunde im Abschnitt (±30 m); Streckenweites wie Ruckler-Statistik bleibt */
  // Z-Fighting im Bild: nur die 6 stärksten Stellen einzeln, der Rest als eine Zeile (alle Bilder bleiben unter „Ansichten“)
  { const vz = R.issues.filter(i => i.zb).sort((a, b) => b.zb - a.zb), rest = vz.slice(6);
    if (rest.length) { R.issues = R.issues.filter(i => !rest.includes(i)); issue(R, 'info', 'Z-Fighting', 'Weitere ' + rest.length + ' Ansichten mit leichtem Flimmern (je ' + Math.min(...rest.map(i => i.zb)) + '–' + Math.max(...rest.map(i => i.zb)) + ' Bereiche)', null, 'bei ' + [...new Set(rest.map(i => i.s))].sort((a, b) => a - b).map(at).join(', ')); } }
  const rank = { hoch: 0, mittel: 1, info: 2 }; R.issues.sort((a, b) => rank[a.sev] - rank[b.sev]);
  R.verdict = R.issues.some(i => i.sev === 'hoch') ? 'Fehler' : R.issues.some(i => i.sev === 'mittel') ? 'Prüfen' : 'OK';
  R.log = LOG.slice(); R.finished = new Date().toISOString();
  await save(R.key + '.json', R);
  log(R.name + ': ' + R.verdict + ' (' + R.issues.length + ' Befunde)');
  return R;
}

// Bekannte Fehlalarme älterer Läufe entfernen (beim Berichtsbau, damit auch alte Daten sauber erscheinen):
// ausgeblendete Instanzen (Größe 0) liegen alle am Ursprung und zählten früher als Clipping; flache Startplatz-Markierungen
function cleanIssues(R) {
  const st = R.static || {}, origin = new Set([...((st.clipAll || {}).list || []), ...((st.onRoad || {}).list || [])].filter(e => e.x === 0 && e.z === 0).map(e => e.s));
  R.issues = (R.issues || []).filter(i => !(i.cat === 'Clipping' && origin.has(i.s)) && !(i.cat === 'Clipping' && /PlaneGeometry/.test(i.msg) && /, -?0\.[0-2]\d? m über Asphalt/.test(i.msg)));
  R.issues = R.issues.map(i => i.cat === 'Clipping' ? { ...i, msg: i.msg.replace(/\((?:function|onBeforeCompile)[\s\S]*?, ([\d.]+ m hoch)\)/, '($1)') } : i);
  R.verdict = R.issues.some(i => i.sev === 'hoch') ? 'Fehler' : R.issues.some(i => i.sev === 'mittel') ? 'Prüfen' : 'OK';
  return R;
}

// ---------- Bericht ----------
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
function chart(R) {
  const F = R.frames; if (!F || !F.t.length) return ''; const W = 900, H = 150, L = R.L || 1, col = ['#4ea1ff', '#b08cff', '#36d07a', '#ffb020'], ymax = 120, y = v => H - Math.min(v, ymax) / ymax * (H - 14) - 2;
  let dots = ''; for (let k = 0; k < F.t.length; k++) { const v = F.t[k]; if (v < 24 && k % 3) continue; dots += `<circle cx="${(F.s[k] / L * W).toFixed(1)}" cy="${y(v).toFixed(1)}" r="${v > 50 ? 2.6 : 1.1}" fill="${col[F.cam[k]]}" ${v > 50 ? '' : 'opacity=".55"'}/>`; }
  const grid = [16.7, 33.3, 50, 100].map(v => `<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}" class="gl"/><text x="${W - 4}" y="${y(v) - 3}" text-anchor="end" class="gt">${Math.round(v)} ms</text>`).join('');
  const km = []; for (let m = 0; m < L; m += 500) km.push(`<text x="${m / L * W + 2}" y="${H + 12}" class="gt">${m ? (m / 1000).toFixed(1) + ' km' : 'Start'}</text>`);
  const leg = [...new Set(F.cam)].map(c => `<span><i style="background:${col[c]}"></i>${CAMN[c]}</span>`).join('');
  return `<div class="chart"><div class="leg">Bildzeit über die Runde · ${leg}</div><svg viewBox="0 0 ${W} ${H + 16}" preserveAspectRatio="none">${grid}${dots}${km.join('')}</svg></div>`;
}
function reportHtml(all, imgSrc) {
  const im = p => p ? `<a href="${esc(imgSrc(p))}" target="_blank"><img loading="lazy" src="${esc(imgSrc(p))}"></a>` : '';
  const cnt = (R, cat) => R.issues.filter(i => i.cat === cat && i.sev !== 'info').length;
  const cell = (n, warnAt = 1) => `<td class="${n >= warnAt ? (n >= 3 ? 'bad' : 'warn') : 'ok'}">${n || '–'}</td>`;
  const rows = all.map(R => { const a = R.perf && R.perf.all || {}; return `<tr><td><a href="#t-${R.key}">${esc(R.name)}</a><small>${esc(R.ser)} · ${R.L ? (R.L / 1000).toFixed(2) + ' km' : ''}</small></td><td class="v ${R.verdict}">${R.verdict}</td><td>${a.fps ?? '–'}</td><td>${a.p99 ?? '–'}</td><td>${a.perMin ?? '–'}</td>${cell(cnt(R, 'Ruckler'))}${cell(cnt(R, 'Loch im Boden'))}${cell(cnt(R, 'Z-Fighting'))}${cell(cnt(R, 'Rendering'))}${cell(cnt(R, 'Clipping'))}${cell(cnt(R, 'Fahrbarkeit') + cnt(R, 'Ablauf'))}</tr>`; }).join('');
  const sect = all.map(R => {
    const p = R.perf || {}, st = R.static || {};
    const camRows = Object.entries(p.byCam || {}).filter(([, v]) => v).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${v.fps}</td><td>${v.med}</td><td>${v.p95}</td><td>${v.p99}</td><td>${v.max}</td><td>${v.d50}</td><td>${v.d100}</td></tr>`).join('');
    const fl = p.firstLap ? `<tr class="dim"><td>1. Runde (Aufwärmen)</td><td>${p.firstLap.fps}</td><td>${p.firstLap.med}</td><td>${p.firstLap.p95}</td><td>${p.firstLap.p99}</td><td>${p.firstLap.max}</td><td>${p.firstLap.d50}</td><td>${p.firstLap.d100}</td></tr>` : '';
    const iss = R.issues.map(i => `<div class="iss ${i.sev}"><div class="it"><b>${esc(i.sev)}</b><span class="cat">${esc(i.cat)}</span>${i.s != null ? `<span class="pos">bei ${at(i.s)}${R.L ? ' (' + Math.round(i.s / R.L * 100) + ' %)' : ''}</span>` : ''}<div>${esc(i.msg)}</div>${i.det ? `<small>${esc(i.det)}</small>` : ''}</div>${im(i.img)}</div>`).join('') || '<p class="ok">Keine Befunde.</p>';
    const byCam = {}; for (const s of R.samples || []) (byCam[s.cam + (s.view !== 'Kamera' ? ' · Rundumblick' : '')] ||= []).push(s);
    const sheets = Object.entries(byCam).map(([k, list]) => `<details><summary>${esc(k)} – ${list.length} Bilder</summary><div class="sheet">${list.map(s => `<figure class="${s.void >= 25 || s.zf >= 3 ? 'flag' : ''}">${im(s.img)}<figcaption>${at(s.s)}${s.view !== 'Kamera' ? ' · ' + esc(s.view) : ''}${s.calls ? ' · ' + s.calls + ' DC' : ''}${s.void ? ' · Leere ' + s.void : ''}${s.zf ? ' · ZF ' + s.zf : ''}</figcaption></figure>`).join('')}</div></details>`).join('');
    const sRow = (k, label, v) => st[k] ? `<tr><td>${label}</td><td>${v}</td><td>${st[k + '_ms'] ?? ''} ms</td></tr>` : '';
    const stat = !Object.keys(st).length ? '' : `<table class="st"><tr><th>Statische Prüfung</th><th>Ergebnis</th><th>Dauer</th></tr>${sRow('integrity', 'Geometrie / Texturen', (st.integrity.meshes || 0) + ' Objekte · ' + (st.integrity.nanN || 0) + ' NaN · ' + (st.integrity.texN || 0) + ' fehlende Texturen')}${sRow('topVoids', 'Boden von oben (Löcher)', (st.topVoids.spots ?? '?') + ' Stellen')}${sRow('groundZFight', 'Z-Fighting im Boden', (st.groundZFight.spots ?? '?') + ' Stellen · ' + (st.groundZFight.rays || 0) + ' Strahlen')}${sRow('gravelHoles', 'Kies/Auslauf-Löcher', (st.gravelHoles.spots ?? '?') + ' Stellen · ' + (st.gravelHoles.bad ?? '?') + ' von ' + (st.gravelHoles.n ?? '?') + ' Messpunkten')}${sRow('clipAll', 'Clipping in Auslauf (__clipAll)', st.clipAll.n ?? '?')}${sRow('onRoad', 'Objekte auf Fahrbahn (__onRoad)', st.onRoad.n ?? '?')}${sRow('bldOverlap', 'Gebäude-Überschneidung', (st.bldOverlap.overlaps ?? '?') + ' von ' + (st.bldOverlap.n ?? '?'))}${sRow('facadeClip', 'Fassaden auf Strecke', (st.facadeClip.clipping ?? '?') + ' von ' + (st.facadeClip.buildings ?? '?'))}</table>`;
    const errs = (R.errors || []).length ? `<details><summary>Konsole – ${R.errors.length} Meldungen</summary><pre>${R.errors.map(e => esc(e.lv + (e.n > 1 ? ' ×' + e.n : '') + ': ' + e.m)).join('\n')}</pre></details>` : '';
    const ev = (R.events || []).length ? `<details><summary>Ablauf – ${R.events.length} Ereignisse</summary><pre>${R.events.map(e => esc('Runde ' + (e.lap + 1) + ' · ' + at(e.s) + ' · ' + e.t + (e.v ? ': ' + e.v : ''))).join('\n')}</pre></details>` : '';
    return `<section id="t-${R.key}"><h2>${esc(R.name)} <span class="v ${R.verdict}">${R.verdict}</span></h2><p class="meta">${esc(R.full)} · ${esc(R.ser)} · Grafik ${esc(R.gfx)} · ${R.laps || '?'} Runden · Kameras: ${esc((R.cams || []).join(', '))} · Aufbau ${((R.buildMs || 0) / 1000).toFixed(1)} s${R.mem ? ' · JS-Speicher ' + R.mem + ' MB' : ''}${R.gpu ? ' · ' + R.gpu.geo + ' Geometrien, ' + R.gpu.tex + ' Texturen, ' + R.gpu.prog + ' Shader' : ''}${R.gpuName ? ' · GPU ' + esc(R.gpuName) : ''}</p>
      <h3>Befunde (${R.issues.length})</h3>${iss}
      <h3>Bildzeiten</h3><p class="meta">Messart: ${esc(R.timing || '–')}</p>${chart(R)}<table class="pf"><tr><th>Kamera</th><th>fps</th><th>Median</th><th>p95</th><th>p99</th><th>max</th><th>&gt;50 ms</th><th>&gt;100 ms</th></tr>${camRows}${fl}</table>
      ${stat}<h3>Ansichten</h3>${sheets}${errs}${ev}</section>`; }).join('');
  const when = new Date().toLocaleString('de-DE');
  return `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Strecken-QC</title><style>
:root{--bg:#0d1117;--pn:#161b22;--ln:#2a313c;--tx:#e6edf3;--mu:#8b949e;--ok:#36d07a;--wa:#ffb020;--bd:#ff4d4f;--in:#4ea1ff}
@media (prefers-color-scheme:light){:root{--bg:#f6f8fa;--pn:#fff;--ln:#d0d7de;--tx:#1f2328;--mu:#59636e}}
body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.45 system-ui,Segoe UI,sans-serif;padding:16px;max-width:1400px;margin:auto}
h1{font-size:22px;margin:4px 0}h2{font-size:19px;margin:0 0 4px}h3{font-size:14px;margin:18px 0 6px;color:var(--mu);text-transform:uppercase;letter-spacing:.05em}
section{background:var(--pn);border:1px solid var(--ln);padding:14px 16px;margin:18px 0}.meta{color:var(--mu);margin:0}
table{border-collapse:collapse;width:100%;overflow-x:auto}th,td{border-bottom:1px solid var(--ln);padding:5px 8px;text-align:left;font-variant-numeric:tabular-nums}th{color:var(--mu);font-weight:600}
td small{display:block;color:var(--mu)}.ok{color:var(--ok)}.warn{color:var(--wa);font-weight:600}.bad{color:var(--bd);font-weight:700}
.v{font-weight:700;padding:1px 7px;font-size:13px}.v.OK{color:#06240f;background:var(--ok)}.v.Prüfen{color:#2b1d00;background:var(--wa)}.v.Fehler{color:#fff;background:var(--bd)}
.iss{display:flex;gap:12px;align-items:flex-start;border-left:4px solid var(--in);padding:6px 10px;margin:6px 0;background:rgba(127,127,127,.06)}.iss.hoch{border-color:var(--bd)}.iss.mittel{border-color:var(--wa)}
.iss .it{flex:1;min-width:0}.iss b{text-transform:uppercase;font-size:11px;margin-right:8px}.cat{font-weight:600;margin-right:8px}.pos{color:var(--mu)}.iss small{color:var(--mu);display:block;word-break:break-word}
.iss img{width:240px;display:block}.sheet{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin:8px 0}
figure{margin:0}figure img{width:100%;display:block}figure.flag img{outline:3px solid var(--wa)}figcaption{font-size:11px;color:var(--mu)}
details{margin:8px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font-size:12px;color:var(--mu)}
.chart svg{width:100%;height:170px;background:rgba(127,127,127,.06)}.gl{stroke:var(--ln)}.gt{fill:var(--mu);font-size:10px}.leg{font-size:12px;color:var(--mu)}.leg span{margin-left:10px}.leg i{display:inline-block;width:9px;height:9px;margin-right:4px}
.dim td{color:var(--mu)}.wrap{overflow-x:auto}
@media (max-width:700px){.iss{flex-direction:column}.iss img{width:100%}}
</style></head><body><h1>Strecken-QC</h1><p class="meta">${esc(when)} · Modus ${esc(CFG.mode)}${CFG.at ? ' · nur Abschnitt ' + CFG.at[0] + '–' + CFG.at[1] + ' m' : ''} · ${esc(all[0] ? all[0].screen : '')} · ${esc(navigator.userAgent.replace(/.*(Edg\/[\d.]+|Chrome\/[\d.]+|Firefox\/[\d.]+|Safari\/[\d.]+).*/, '$1'))}</p>
<div class="wrap"><table><tr><th>Strecke</th><th>Urteil</th><th>fps</th><th>p99 ms</th><th>Ruckler/min</th><th>Ruckler</th><th>Löcher</th><th>Z-Fight</th><th>Rendering</th><th>Clipping</th><th>Fahrt</th></tr>${rows}</table></div>
<p class="meta">Zahlen in den Spalten = Befunde der Stufe „mittel“ oder „hoch“. Ruckler = Bild über 50 ms. Magenta-Kästen = Blick ins Leere, gelbe Kästen = flimmernde Flächen (Z-Fighting).</p>${sect}</body></html>`;
}

// ---------- Steuerung ----------
function trackKeys() { const all = Object.keys(A.TRACKS); return CFG.list === 'all' ? all : CFG.list.split(',').map(s => s.trim()).filter(k => A.TRACKS[k]); }
async function main() {
  // Grafikstufe einstellen (braucht einen Neustart der Seite)
  if (CFG.gfx && A.S.gfx !== CFG.gfx) { try { const o = JSON.parse(localStorage.getItem('f1rennen') || '{}'); o.gfx = CFG.gfx; localStorage.setItem('f1rennen', JSON.stringify(o)); } catch (e) {} location.reload(); return; }
  await W8(1500);
  const keys = trackKeys(); if (CFG.list === 'none') { log('Nur Werkzeuge geladen (window.__qcBot)'); return; } if (!keys.length) { log('Keine Strecke gefunden: ' + CFG.list + ' – bekannt: ' + Object.keys(A.TRACKS).join(', ')); return; }
  if (CFG.srv) {
    // mit Server: eine Strecke pro Seitenaufruf (frischer Speicher, ein Absturz stoppt nicht den ganzen Lauf)
    if (CFG.i < keys.length && !CFG.reportOnly) { await runTrack(keys[CFG.i]); const u = new URL(location.href); u.searchParams.set('i', CFG.i + 1); u.searchParams.set('run', CFG.run); location.replace(u.href); return; }
    log('Bericht erstellen'); const all = [];
    for (const k of keys) { try { const r = await fetch('qc-reports/' + CFG.run + '/' + k + '.json', { cache: 'no-store' }); if (r.ok) all.push(cleanIssues(await r.json())); } catch (e) {} }
    // Neustarts durch run.py (Seite hing oder stürzte ab) als Befund an die Strecke hängen
    try { const r = await fetch('qc-reports/' + CFG.run + '/restarts.json', { cache: 'no-store' }); if (r.ok) { const rs = await r.json();
      for (const R of all) for (const x of rs[R.key] || []) { const m = /· (\d+) m · Runde (\S+) .*Kamera ([^·]+)/.exec(x.last || '');
        R.issues.unshift({ sev: 'hoch', cat: 'Ablauf', msg: (x.crashed ? 'Seite ist abgestürzt' : 'Seite hing') + ' – Strecke wurde neu gestartet' + (m ? ' (zuletzt Runde ' + m[2] + ', ' + m[3].trim() + ')' : ''), s: m ? +m[1] : null, det: (x.last || '').slice(0, 160) });
        R.verdict = 'Fehler'; } } } catch (e) {}
    await save('report.html', reportHtml(all, p => p), 'text/html');
    const sum = all.map(R => ({ key: R.key, name: R.name, verdict: R.verdict, issues: R.issues.map(i => [i.sev, i.cat, i.s, i.msg]), fps: R.perf && R.perf.all && R.perf.all.fps, p99: R.perf && R.perf.all && R.perf.all.p99, perMin: R.perf && R.perf.all && R.perf.all.perMin }));
    await save('summary.json', sum); await fetch('/__qc/done?run=' + encodeURIComponent(CFG.run), { method: 'POST' }).catch(() => {});
    log('Fertig – Bericht: qc-reports/' + CFG.run + '/report.html'); return;
  }
  // ohne Server: alles in diesem Tab, danach Bericht herunterladen
  const all = [];
  for (const k of keys) { all.push(await runTrack(k)); if (A.running) { try { document.querySelector('#toMenu').click(); } catch (e) {} await W8(1500); } }   /* Rennen beenden, zurück ins Menü – die nächste Strecke startet von dort */
  const html = reportHtml(all, p => MEM.files[p] || p);
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([html], { type: 'text/html' })); a.download = 'strecken-qc-' + CFG.run + '.html'; document.body.appendChild(a); a.click();
  log('Fertig – Bericht wurde heruntergeladen');
}
window.__qcBot = { selfTest, topVoids, gravelHoles, groundZFight, groundMeshes, cutHole, probe, integrity };
main().catch(e => log('Abbruch: ' + (e && e.stack || e)));
