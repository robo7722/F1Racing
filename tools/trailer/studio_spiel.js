// Wird von studio.js im Spiel ausgewertet (Modul-Bereich von index.html): Helfer für Trailer-Aufnahmen unter window.TR.
// Am Spiel selbst ändert das nichts – es läuft nur im Testbrowser.
window.TR = (() => {
  const TR = { speed: 0, vig: null, labels: false, grain: null };
  // Rennen freigeben: KI fährt das eigene Auto, Ampel/HUD weg
  TR.start = () => { raceState = 'race'; raceTime = 20; SG.go = true; window.__plAI = true; profBot = buildProfile(45.5 * WX.grip, VTOP * SERPH.top, 44 * WX.brk, KR);
    document.querySelector('#lights').classList.add('hidden'); const h = document.querySelector('#sgHint'); if (h) h.classList.add('hidden'); TR.hud(false); return 'ok'; };
  TR.hud = on => { document.body.classList.toggle('ptNoHud', !on); document.querySelector('#hud').style.visibility = on ? '' : 'hidden'; document.querySelector('#controls').style.display = on ? '' : 'none'; };
  // Auto an Streckenmeter s (quer lat) setzen; vf = Anteil des dort möglichen Tempos
  TR.put = (c, s, lat = 0, vf = 0.9, vmax = 95) => { const q = trackAt(s, lat); c.x = q.x; c.z = q.z; c.h = q.h; c.steer = 0; c.sx = c.sz = 0; c.yawKick = 0; c.idx = q.i; c.sPrev = modL(s); projectCar(c); c.d = modL(s); c.sPrev = modL(s); c.stuckT = 0; c.wrongT = 0;
    c.v = Math.min((c === pl ? profBot : profAI)[c.idx] * vf, vmax); };
  // Feld aufstellen: eigenes Auto bei s, die anderen nach Liste [[Abstand in m (+ = davor), quer], …]; übrige Autos weit weg (halbe Runde)
  TR.feld = (s, lat = 0, liste = [], vf = 0.9) => { TR.put(pl, s, lat, vf); camH = pl.h; const rest = cars.filter(c => c !== pl);
    rest.forEach((c, k) => { const e = liste[k]; if (e) TR.put(c, s + e[0], e[1], e[2] ?? vf); else TR.put(c, s + L / 2 + k * 14, (k % 2 ? 1 : -1) * 2.2, 0.5); }); return rest.slice(0, liste.length).map(c => c.code).join(','); };
  // Startaufstellung wie im Spiel (zwei Reihen versetzt) ab Streckenmeter s0 rückwärts
  TR.sim = (n, ms = 16.667, zeichnen = false) => { window.__norender = !zeichnen; window.__frame(n, ms); window.__norender = false; return Math.round(pl.v * 3.6); };
  TR.pos = c => { const g = c.mesh.g.position; return [g.x, g.y, g.z, c.h]; };
  // Punkt relativ zum Auto: [rechts, hoch, vor]
  // Höhe = Fahrbahnhöhe an dieser Stelle + hoch (an Steigungen läge ein Punkt „6 m vor dem Auto auf Autohöhe“ sonst unter der Straße)
  TR.rel = (c, o) => { const [x, y, z, h] = TR.pos(c), fx = Math.sin(h), fz = Math.cos(h), rx = -fz, rz = fx, X = x + rx * o[0] + fx * o[2], Z = z + rz * o[0] + fz * o[2];
    let Y = y; if (!FLAT) { const j = nearestDist(X, Z)[1]; Y = ELEV[j] || 0; } return [X, Y + o[1], Z]; };
  TR.trk = (s, lat = 0, h = 0) => { const a = window.__tAt(s, lat); return [a[0], a[1] + h, a[2]]; };
  const car = k => k == null ? pl : typeof k === 'number' ? cars.filter(c => c !== pl)[k] : cars.find(c => c.code === k) || pl;
  // Kamera setzen. spec: { von: [r,u,v] am Auto | { s, lat, h } an der Strecke | [x,y,z] Welt, auf: ebenso (Standard: Auto-Mitte), auto: Kennung/Index, fov, roll }
  TR.cam = spec => { if (!spec) { window.__camFix = null; return 'aus'; } TR.spec = spec;
    const pt = (q, c, std) => q == null ? TR.rel(c, std) : Array.isArray(q) ? (q.length === 4 ? q.slice(0, 3) : TR.rel(c, q)) : TR.trk(q.s, q.lat || 0, q.h || 0);
    window.__camFix = () => { const c = car(spec.auto), ca = car(spec.zielAuto ?? spec.auto); return { p: pt(spec.von, c, [3, 1.2, -6]), t: pt(spec.auf, ca, [0, 0.45, 0]), fov: spec.fov || 40, roll: spec.roll || 0 }; }; return 'ok'; };
  // vor jedem Zeichnen: Tempo-Unschärfe/Vignette des Spiels für Außenkameras steuern, Namensschilder ausblenden
  window.__trPre = () => { if (!finishPass) return; const fu = finishPass.uniforms;
    if (window.__camFix) { fu.uSpeed.value = TR.speed; if (TR.vig != null) fu.uVig.value = TR.vig; }
    if (TR.grain != null) fu.uGrain.value = TR.grain;
    if (!TR.labels) for (const c of cars) if (c.mesh && c.mesh.label) c.mesh.label.visible = false; };
  // ein Bild neu zeichnen, ohne die Simulation weiterzudrehen (für Schärfentiefe: Kamera vorher versetzen)
  TR.zeichne = () => { if (window.__trPre) window.__trPre(0, performance.now()); syncAoCam(); composer.render(0); };
  // Sammelpuffer: mehrere Bilder im linearen Licht mitteln (Bewegungsunschärfe, Schärfentiefe)
  const AK = { n: 0, sum: null, w: 0, h: 0, px: null, lut: null, inv: null };
  TR.akStart = () => { const gl = renderer.getContext(); AK.w = gl.drawingBufferWidth; AK.h = gl.drawingBufferHeight; const n = AK.w * AK.h * 3; if (!AK.sum || AK.sum.length !== n) { AK.sum = new Float32Array(n); AK.px = new Uint8Array(AK.w * AK.h * 4); } else AK.sum.fill(0); AK.n = 0;
    if (!AK.lut) { AK.lut = new Float32Array(256); for (let i = 0; i < 256; i++) AK.lut[i] = Math.pow(i / 255, 2.2); } };
  TR.akAdd = (gew = 1) => { const gl = renderer.getContext(); renderer.setRenderTarget(null); gl.readPixels(0, 0, AK.w, AK.h, gl.RGBA, gl.UNSIGNED_BYTE, AK.px); const s = AK.sum, p = AK.px, lut = AK.lut; for (let i = 0, j = 0, n = AK.w * AK.h; i < n; i++, j += 4) { const k = i * 3; s[k] += lut[p[j]] * gew; s[k + 1] += lut[p[j + 1]] * gew; s[k + 2] += lut[p[j + 2]] * gew; } AK.n += gew; };
  TR.akEnde = (typ = 'image/png', q = 0.95) => { const cv = TR.akCv || (TR.akCv = document.createElement('canvas')); cv.width = AK.w; cv.height = AK.h; const cx = cv.getContext('2d'), im = cx.createImageData(AK.w, AK.h), d = im.data, s = AK.sum, inv = 1 / AK.n, W = AK.w, H = AK.h;
    for (let y = 0; y < H; y++) { const yo = (H - 1 - y) * W; for (let x = 0; x < W; x++) { const k = (yo + x) * 3, j = (y * W + x) * 4; d[j] = Math.pow(s[k] * inv, 1 / 2.2) * 255 + 0.5; d[j + 1] = Math.pow(s[k + 1] * inv, 1 / 2.2) * 255 + 0.5; d[j + 2] = Math.pow(s[k + 2] * inv, 1 / 2.2) * 255 + 0.5; d[j + 3] = 255; } }
    cx.putImageData(im, 0, 0); return cv.toDataURL(typ, q); };
  // Schärfentiefe: n Bilder mit versetzter Kamera (Blende ap in m, Schärfe auf dem Blickziel) mitteln; liefert Bild als Data-URL
  TR.dof = (n = 24, ap = 0.06) => { const f = window.__camFix && window.__camFix(); if (!f) return null; const P = new THREE.Vector3(...f.p), Tg = new THREE.Vector3(...f.t), fw = Tg.clone().sub(P).normalize(), rt = new THREE.Vector3().crossVectors(fw, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(rt, fw);
    TR.akStart(); const alt = window.__camFix;
    for (let i = 0; i < n; i++) { const r = ap * Math.sqrt((i + 0.5) / n), w = i * 2.399963; const o = rt.clone().multiplyScalar(Math.cos(w) * r).add(up.clone().multiplyScalar(Math.sin(w) * r));
      camera.position.copy(P).add(o); camera.up.set(0, 1, 0); camera.lookAt(Tg); if (f.roll) camera.rotateZ(f.roll); camera.fov = f.fov; camera.updateProjectionMatrix(); camera.updateMatrixWorld(); TR.zeichne(); TR.akAdd(); }
    window.__camFix = alt; return TR.akEnde(); };
  // Bewegungsunschärfe für ein Standbild: n Zwischenbilder über die Belichtungszeit (ms) mitteln
  TR.mb = (n = 12, belichtung = 16, typ, q) => { TR.akStart(); for (let i = 0; i < n; i++) { window.__frame(1, belichtung / n); TR.akAdd(); } return TR.akEnde(typ, q); };
  // Bildschleife des Spiels anhalten: danach läuft nur noch, was über __frame/TR.sim angefordert wird (reproduzierbar, keine Rechenzeit im Leerlauf)
  TR.halt = () => { window.requestAnimationFrame = () => 0; return 'angehalten'; };
  // Renderauflösung für schnelle Proben verkleinern (1 = voll)
  TR.skala = f => { DYN.scale = f; resize(); return renderer.getPixelRatio(); };
  TR.info = () => JSON.stringify({ s: Math.round(pl.d), kmh: Math.round(pl.v * 3.6), pos: TR.pos(pl).map(v => +v.toFixed(1)), fov: +camera.fov.toFixed(1), calls: renderer.info.render.calls, pr: renderer.getPixelRatio(), gr: [renderer.getContext().drawingBufferWidth, renderer.getContext().drawingBufferHeight] });
  return TR; })();
