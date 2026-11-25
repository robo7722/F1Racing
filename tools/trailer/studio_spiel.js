// Wird im Spiel ausgewertet (Modul-Bereich von index.html): Helfer für Trailer-Aufnahmen unter window.TR.
// Am Spiel selbst ändert das nichts – es läuft nur im Testbrowser (tools/trailer/spielstart.js).
window.TR = (() => {
  const alt = window.TR, TR = { speed: 0, vig: null, labels: false, grain: null, u: 0, vt: alt ? alt.vt : 0, je: null, tz: 0 };
  // beim Nachladen dieser Datei in eine laufende Sitzung die echten Funktionen behalten (die Uhr ist dann schon umgestellt)
  TR.now0 = alt ? alt.now0 : performance.now.bind(performance); TR.raf0 = alt ? alt.raf0 : window.requestAnimationFrame.bind(window); TR.rnd0 = alt ? alt.rnd0 : Math.random; TR.frame0 = alt ? alt.frame0 : window.__frame;

  /* ---------- Zeitbasis ---------- */
  // Bildschleife des Spiels anhalten und auf eine eigene Uhr umstellen: danach vergeht Spielzeit nur noch über TR.takt – jedes Bild exakt gleich lang, wiederholbar.
  TR.halt = () => { window.requestAnimationFrame = () => 0; TR.vt = Math.max(TR.vt, TR.now0()); performance.now = () => TR.vt; last = TR.vt;
    window.__frame = (k = 3, ms = 40) => { const z = !window.__norender; for (let i = 0; i < k; i++) TR.takt(ms, z); window.__norender = !z; }; return 'angehalten'; };
  // zurück zur echten Uhr und Bildschleife (für Menüs und den Rennstart)
  TR.weiter = () => { const off = Math.max(0, TR.vt - TR.now0()); performance.now = () => TR.now0() + off; window.requestAnimationFrame = TR.raf0; window.__frame = TR.frame0; Math.random = TR.rnd0; window.__camFix = null; TR.je = null; last = performance.now(); requestAnimationFrame(frame); return 'läuft'; };
  // ein Schritt Spielzeit (ms), mit oder ohne Zeichnen
  TR.takt = (ms, zeichnen = true) => { window.__norender = !zeichnen; last = TR.vt; TR.vt += ms; tick(TR.vt, true); window.__norender = false; };
  TR.sim = (n, ms = 16.667, zeichnen = false) => { for (let i = 0; i < n; i++) TR.takt(ms, zeichnen); return Math.round(pl.v * 3.6); };
  // Zufall festlegen (gleiche Szene → gleicher Ablauf)
  TR.seed = n => { let a = n >>> 0; Math.random = () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; return 'ok'; };

  /* ---------- Rennen und Autos ---------- */
  // Rennen freigeben: KI fährt das eigene Auto, Ampel/HUD weg
  TR.start = () => { raceState = 'race'; raceTime = 20; SG.go = true; window.__plAI = true; profBot = buildProfile(45.5 * WX.grip, VTOP * SERPH.top, 44 * WX.brk, KR);
    document.querySelector('#lights').classList.add('hidden'); const h = document.querySelector('#sgHint'); if (h) h.classList.add('hidden'); TR.hud(false); return 'ok'; };
  TR.hud = on => { document.body.classList.toggle('ptNoHud', !on); document.querySelector('#hud').style.visibility = on ? '' : 'hidden'; document.querySelector('#controls').style.display = on ? '' : 'none'; };
  // Auto an Streckenmeter s (quer lat) setzen; vf = Anteil des dort möglichen Tempos
  TR.put = (c, s, lat = 0, vf = 0.9, vmax = 95) => { const q = trackAt(s, lat); c.x = q.x; c.z = q.z; c.h = q.h; c.steer = 0; c.sx = c.sz = 0; c.yawKick = 0; c.idx = q.i; c.sPrev = modL(s); projectCar(c); c.d = modL(s); c.sPrev = modL(s); c.stuckT = 0; c.wrongT = 0; c.ovr = null; c.laneT = 0;
    c.v = Math.min((c === pl ? profBot : profAI)[c.idx] * vf, vmax); };
  // Feld aufstellen: eigenes Auto bei s, die anderen nach Liste [[Abstand in m (+ = davor), quer, Tempoanteil], …]; übrige Autos weit weg (halbe Runde)
  TR.feld = (s, lat = 0, liste = [], vf = 0.9) => { TR.put(pl, s, lat, vf); camH = pl.h; const rest = cars.filter(c => c !== pl);
    rest.forEach((c, k) => { const e = liste[k]; if (e) TR.put(c, s + e[0], e[1], e[2] ?? vf); else TR.put(c, s + L / 2 + k * 14, (k % 2 ? 1 : -1) * 2.2, 0.5); }); return rest.slice(0, liste.length).map(c => c.code).join(','); };
  TR.pos = c => { const g = c.mesh.g.position; return [g.x, g.y, g.z, c.h]; };
  // Punkt relativ zum Auto: [rechts, hoch, vor]. Höhe = Fahrbahnhöhe an dieser Stelle + hoch (an Steigungen läge ein Punkt „6 m vor dem Auto auf Autohöhe“ sonst unter der Straße)
  TR.rel = (c, o) => { const [x, y, z, h] = TR.pos(c), fx = Math.sin(h), fz = Math.cos(h), rx = -fz, rz = fx, X = x + rx * o[0] + fx * o[2], Z = z + rz * o[0] + fz * o[2];
    let Y = y; if (!FLAT) { const j = nearestDist(X, Z)[1]; Y = ELEV[j] || 0; } return [X, Y + o[1], Z]; };
  TR.trk = (s, lat = 0, h = 0) => { const a = window.__tAt(s, lat); return [a[0], a[1] + h, a[2]]; };
  const car = k => k == null ? pl : typeof k === 'number' ? cars.filter(c => c !== pl)[k] : cars.find(c => c.code === k) || pl;
  TR.auto = car;

  /* ---------- Kamera ---------- */
  // Angabe: { von: [r,u,v] am Auto | { s, lat, h } an der Strecke | [x,y,z,0] Welt, auf: ebenso (Standard: Auto-Mitte), auto / zielAuto: Kennung oder Index, fov, roll }
  const pt = (q, c, std) => q == null ? TR.rel(c, std) : Array.isArray(q) ? (q.length === 4 ? q.slice(0, 3) : TR.rel(c, q)) : TR.trk(q.s, q.lat || 0, q.h || 0);
  TR.kamWert = sp => { const c = car(sp.auto), ca = car(sp.zielAuto ?? sp.auto); return { p: pt(sp.von, c, [3, 1.2, -6]), t: pt(sp.auf, ca, [0, 0.45, 0]), fov: sp.fov || 40, roll: sp.roll || 0 }; };
  const EASE = { lin: u => u, io: u => u * u * (3 - 2 * u), aus: u => 1 - (1 - u) * (1 - u), ein: u => u * u };
  const rau = (T, k) => Math.sin(T * 3.1 + k * 1.7) * 0.5 + Math.sin(T * 7.3 + k * 2.9) * 0.3 + Math.sin(T * 13.7 + k * 4.1) * 0.2;
  // Kamerafahrt von Angabe a nach b über TR.u = 0…1 (b weglassen = feste Angabe). o: { ease: 'io'|'lin'|'aus'|'ein', wack: Handkamera-Unruhe in m, wackF: Tempo der Unruhe }
  // a = { cam: 2 } schaltet auf eine Spielkamera (0 Verfolger, 2 Helm, 3 T-Kamera) ohne eigene Kamera.
  TR.kam = (a, b, o = {}) => { TR.u = 0; if (!a) { window.__camFix = null; return 'aus'; } if (a.cam != null) { S.cam = a.cam; window.__camFix = null; return 'Spielkamera ' + a.cam; }
    S.cam = 0; const e = EASE[o.ease] || EASE.io, w = o.wack || 0, wf = o.wackF || 1;
    window.__camFix = () => { const A = TR.kamWert(a); let R = A; if (b) { const B = TR.kamWert(b), k = e(Math.min(1, Math.max(0, TR.u))), mix = (x, y) => x + (y - x) * k; R = { p: A.p.map((v, i) => mix(v, B.p[i])), t: A.t.map((v, i) => mix(v, B.t[i])), fov: mix(A.fov, B.fov), roll: mix(A.roll, B.roll) }; }
      if (w) { const T = TR.vt / 1000 * wf; R = { p: [R.p[0] + w * rau(T, 1), R.p[1] + w * 0.6 * rau(T, 2), R.p[2] + w * rau(T, 3)], t: [R.t[0] + w * 0.7 * rau(T, 4), R.t[1] + w * 0.5 * rau(T, 5), R.t[2] + w * 0.7 * rau(T, 6)], fov: R.fov, roll: R.roll + w * 0.02 * rau(T, 7) }; }
      return R; }; return 'ok'; };
  TR.cam = sp => TR.kam(sp);   // alte Schreibweise
  // vor jedem Zeichnen: Tempo-Unschärfe/Vignette des Spiels für Außenkameras steuern, Namensschilder ausblenden
  window.__trPre = () => { if (!finishPass) return; const fu = finishPass.uniforms;
    if (window.__camFix) { fu.uSpeed.value = TR.speed; if (TR.vig != null) fu.uVig.value = TR.vig; }
    if (TR.grain != null) fu.uGrain.value = TR.grain;
    if (!TR.labels) for (const c of cars) if (c.mesh && c.mesh.label) c.mesh.label.visible = false; };
  // ein Bild neu zeichnen, ohne die Simulation weiterzudrehen
  TR.zeichne = () => { if (window.__trPre) window.__trPre(0, TR.vt); syncAoCam(); composer.render(0); };

  /* ---------- Bilder holen ---------- */
  // Sammelpuffer: mehrere Bilder im linearen Licht mitteln (Bewegungsunschärfe, Schärfentiefe)
  const AK = { n: 0, sum: null, w: 0, h: 0, px: null, lut: null };
  TR.akStart = () => { const gl = renderer.getContext(); AK.w = gl.drawingBufferWidth; AK.h = gl.drawingBufferHeight; const n = AK.w * AK.h * 3; if (!AK.sum || AK.sum.length !== n) { AK.sum = new Float32Array(n); AK.px = new Uint8Array(AK.w * AK.h * 4); } else AK.sum.fill(0); AK.n = 0;
    if (!AK.lut) { AK.lut = new Float32Array(256); for (let i = 0; i < 256; i++) AK.lut[i] = Math.pow(i / 255, 2.2); } };
  TR.akAdd = (gew = 1, quelle = null) => { const s = AK.sum, lut = AK.lut; let p = quelle; if (!p) { const gl = renderer.getContext(); renderer.setRenderTarget(null); gl.readPixels(0, 0, AK.w, AK.h, gl.RGBA, gl.UNSIGNED_BYTE, AK.px); p = AK.px; }
    for (let i = 0, j = 0, n = AK.w * AK.h; i < n; i++, j += 4) { const k = i * 3; s[k] += lut[p[j]] * gew; s[k + 1] += lut[p[j + 1]] * gew; s[k + 2] += lut[p[j + 2]] * gew; } AK.n += gew; };
  TR.akEnde = (typ = 'image/jpeg', q = 0.95) => { const cv = TR.akCv || (TR.akCv = document.createElement('canvas')); cv.width = AK.w; cv.height = AK.h; const cx = cv.getContext('2d'), im = cx.createImageData(AK.w, AK.h), d = im.data, s = AK.sum, inv = 1 / AK.n, W = AK.w, H = AK.h, g = 1 / 2.2;
    for (let y = 0; y < H; y++) { const yo = (H - 1 - y) * W; for (let x = 0; x < W; x++) { const k = (yo + x) * 3, j = (y * W + x) * 4; d[j] = Math.pow(s[k] * inv, g) * 255 + 0.5; d[j + 1] = Math.pow(s[k + 1] * inv, g) * 255 + 0.5; d[j + 2] = Math.pow(s[k + 2] * inv, g) * 255 + 0.5; d[j + 3] = 255; } }
    cx.putImageData(im, 0, 0); return cv.toDataURL(typ, q); };
  TR.ak = AK;
  // Ein Trailerbild rechnen: Kamerafahrt von u0 nach u1, ms Spielzeit. mb > 1: Bewegungsunschärfe aus mb Zwischenbildern über den Anteil „verschluss“ der Bildzeit (0,5 = 180°).
  // typ = 'image/jpeg' liefert das Bild als Data-URL; typ leer: nur zeichnen (Seitenbild wird außen aufgenommen).
  TR.bild = (u0, u1, ms, mb = 1, typ = '', q = 0.95, verschluss = 0.5) => { if (TR.je) TR.je(TR.tz, ms);
    if (mb > 1) { TR.u = u0; TR.takt(ms * (1 - verschluss), false); TR.akStart(); for (let k = 0; k < mb; k++) { TR.u = u0 + (u1 - u0) * (1 - verschluss + verschluss * (k + 1) / mb); TR.takt(ms * verschluss / mb); TR.akAdd(); } return typ ? TR.akEnde(typ, q) : 1; }
    TR.u = u1; TR.takt(ms); return typ ? renderer.domElement.toDataURL(typ, q) : 1; };
  // Standbild mit Schärfentiefe (Blende ap in m, scharf auf dem Blickziel) – für Proben
  TR.dof = (n = 24, ap = 0.06) => { const f = window.__camFix && window.__camFix(); if (!f) return null; const P = new THREE.Vector3(...f.p), Tg = new THREE.Vector3(...f.t), fw = Tg.clone().sub(P).normalize(), rt = new THREE.Vector3().crossVectors(fw, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(rt, fw);
    TR.akStart(); for (let i = 0; i < n; i++) { const r = ap * Math.sqrt((i + 0.5) / n), w = i * 2.399963; camera.position.copy(P).addScaledVector(rt, Math.cos(w) * r).addScaledVector(up, Math.sin(w) * r); camera.up.set(0, 1, 0); camera.lookAt(Tg); if (f.roll) camera.rotateZ(f.roll); camera.fov = f.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld(); TR.zeichne(); TR.akAdd(); }
    return TR.akEnde(); };
  // Umgebungsverdeckung (GTAO, nur „Ultra“) und Sonnenstrahlen-Durchgang für eine Einstellung an/aus (spart ~1 s je Bild; nachts tun die Strahlen ohnehin nichts)
  TR.ao = an => { if (!composer) return; for (const p of composer.passes) { if (p.constructor.name === 'GTAOPass') p.enabled = !!an; } if (raysPass) raysPass.enabled = !(TH && TH.night); return an; };
  // Feuerwerk des Spiels gezielt zünden (gleiche Teilchen wie im Spiel, nur der Ort ist frei): pos = [x, Bodenhöhe, z], h = Höhe über Grund
  const FWPAL = [[1, .25, .2], [1, .8, .25], [.3, .6, 1], [.9, .35, 1], [.35, 1, .5], [1, 1, 1], [1, .55, .15]];
  TR.feuerwerk = (pos, h = 45, gr = 1) => { const R = Math.random, c = FWPAL[Math.floor(R() * FWPAL.length)], c2 = R() < .35 ? FWPAL[Math.floor(R() * FWPAL.length)] : c, n = 260 + Math.floor(R() * 120), spd = (20 + R() * 14) * gr, y = pos[1] + h;
    for (let k = 0; k < n; k++) { const u = R() * 2 - 1, a = R() * Math.PI * 2, r = Math.sqrt(1 - u * u), v = spd * (0.85 + R() * 0.15), cc = k % 2 ? c : c2; fwP.emit(pos[0], y, pos[2], Math.cos(a) * r * v, u * v, Math.sin(a) * r * v, 1.8 + R() * 1.0, 6.5, 1.4, cc[0] * 6.5, cc[1] * 6.5, cc[2] * 6.5, 1, -4.5); }
    fwP.emit(pos[0], y, pos[2], 0, 0, 0, 0.3, 18, 4, 3, 2.7, 2.2, 1, 0); };
  // Feuerwerk laufend um das Auto zünden: alle 0,16–0,4 s ein Schuss vor dem Auto (vor = [von, bis] m), seitlich ±(seit[0]…seit[1]) m, Höhe hoch[0]…hoch[1]
  TR.fwLauf = (ms, o = {}) => { TR.fwT = (TR.fwT || 0) - ms / 1000; if (TR.fwT > 0) return; const R = Math.random, vor = o.vor || [60, 170], seit = o.seit || [22, 65], hoch = o.hoch || [35, 70]; TR.fwT = (o.takt || 0.16) + R() * 0.24;
    const sd = R() < 0.5 ? -1 : 1; TR.feuerwerk(TR.rel(pl, [sd * (seit[0] + R() * (seit[1] - seit[0])), 0, vor[0] + R() * (vor[1] - vor[0])]), hoch[0] + R() * (hoch[1] - hoch[0])); };
  // Renderauflösung für schnelle Proben verkleinern (1 = voll)
  TR.skala = f => { DYN.scale = f; resize(); return renderer.getPixelRatio(); };
  // Zeit je Bild messen (k Bilder zeichnen, mit Abgleich)
  TR.mess = (k = 3, ms = 33.333) => { const t0 = TR.now0(); for (let i = 0; i < k; i++) TR.takt(ms); const px = new Uint8Array(4); renderer.setRenderTarget(null); renderer.getContext().readPixels(0, 0, 1, 1, 6408, 5121, px); return Math.round((TR.now0() - t0) / k); };
  TR.info = () => JSON.stringify({ s: Math.round(pl.d), kmh: Math.round(pl.v * 3.6), lat: +(pl.lat || 0).toFixed(1), pos: TR.pos(pl).map(v => +v.toFixed(1)), fov: +camera.fov.toFixed(1), pr: renderer.getPixelRatio(), gr: [renderer.getContext().drawingBufferWidth, renderer.getContext().drawingBufferHeight] });
  return TR; })();
