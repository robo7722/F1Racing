// Unruhe einer Einstellung messen, ohne Bilder zu rechnen: Kamerastandort, Blickrichtung und Auto (Fahrtrichtung, Lenkung) je Trailerbild aufzeichnen
// und daraus das Zittern bestimmen: Abweichung jedes Werts von der glatten Bahn durch seine Nachbarn (Ausgleichsparabel über 7 Bilder).
// Gleichmäßige Bewegung, Beschleunigen und Kurvenfahrt ergeben null – übrig bleibt, was von Bild zu Bild hin und her springt.
//   node tools/trailer/ruck.js <Port> <Szene[,Szene…]> [--alt] [--rennen '{"fahrer":"LEC"}'] [--json datei]
//   --alt: Aufnahmetechnik bis Fassung 3 (ein Simulationsschritt je Bild, Kamera starr am Auto, Höhe in Stufen, Lenk-Zielpunkt der KI in Stufen)
// Ausgabe je Einstellung (jeweils mittleres Zittern): Lenkung in % des Vollausschlags, Fahrtrichtung des Autos in Grad, Kamerastandort in mm (waagerecht / Höhe),
// Blickrichtung in Grad (seitlich / Neigung). Zum Vergleich: 0,03° Blickzittern sind bei 30° Bildwinkel rund 2 Bildpunkte.
const http = require('http'); const fs = require('fs'); const a = process.argv.slice(2), flag = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : a[i + 1]; }, has = n => a.includes('--' + n);
const PLAN = require('./drehplan.js'), PORT = +a[0], SZENEN = (a[1] || '').split(',').filter(Boolean), FPS = PLAN.fps, J = JSON.stringify, ALT = has('alt');
const post = (weg, daten) => new Promise((ok, nein) => { const r = http.request({ host: '127.0.0.1', port: PORT, path: weg, method: 'POST', timeout: 3600000 }, res => { const c = []; res.on('data', d => c.push(d)); res.on('end', () => { const s = Buffer.concat(c).toString(); if (res.statusCode !== 200) nein(new Error(s.slice(0, 600))); else ok(s); }); }); r.on('error', nein); r.end(daten); });
const ev = async code => { const s = await post('/eval', code); try { return JSON.parse(s); } catch (e) { return s; } };
const rms = v => Math.sqrt(v.reduce((s, x) => s + x * x, 0) / Math.max(1, v.length)), SG = [-2, 3, 6, 7, 6, 3, -2], zit = v => v.slice(3, -3).map((x, i) => x - SG.reduce((s, k, j) => s + k * v[i + j], 0) / 21);
const entw = v => { const o = [v[0]]; for (let i = 1; i < v.length; i++) { let d = v[i] - v[i - 1]; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; o.push(o[i - 1] + d); } return o; };
(async () => {
  if (flag('rennen', '')) { console.log(await post('/rennen', flag('rennen'))); await ev('TR.start(); 1'); }
  await ev(ALT ? 'TR.fein = 0; TR.glatt = null; TR.stufig = true; window.__trGlatt = false; 1' : 'TR.fein = 10.5; TR.glatt = { von: 0.28, auf: 0.09 }; TR.stufig = false; window.__trGlatt = true; 1');
  const alle = {};
  for (const name of SZENEN) { const z = PLAN.szenen[name]; if (!z || z.typ === 'garage') continue; const n = Math.round(z.dauer * FPS), R = [];
    await ev(`TR.start(); pl.lapsDone = 0; pl.finished = false; TR.seed(${z.seed ?? 7}); TR.je = null; TR.speed = 0; TR.vig = null; TR.glatt = ${ALT || z.glatt === false ? 'null' : '{ von: 0.28, auf: 0.09 }'}; ${z.vor || ''}; 1`);
    let cur = null, segVon = 0;
    for (let i = 0; i < n; i++) { const te = (i + 1) / FPS; let seg = z.kams[z.kams.length - 1], von = 0;
      for (const k of z.kams) { if (te <= (k.bis ?? 1e9) + 1e-6) { seg = k; break; } von = k.bis; }
      if (seg !== cur) { cur = seg; segVon = von; await ev(`TR.kam(${J(seg.a)}, ${J(seg.b || null)}, ${J({ ease: seg.ease, wack: seg.wack, wackF: seg.wackF })}); ${seg.vor || ''}; 1`); R.push(null); }
      const bis = Math.min(cur.bis ?? z.dauer, z.dauer), u = Math.max(0, Math.min(1, (te - segVon) / Math.max(1e-6, bis - segVon)));
      const zl = Array.isArray(z.zeitlupe) ? z.zeitlupe[0] + (z.zeitlupe[1] - z.zeitlupe[0]) * (i / Math.max(1, n - 1)) : (z.zeitlupe || 1), ms = 1000 / FPS * zl;
      R.push(await ev(`TR.tz = ${te}; TR.je && TR.je(${te}, ${ms}); TR.u = ${u}; TR.schritt(${ms}, false); (() => { const f = window.__camFix && window.__camFix(), d = new THREE.Vector3(); let p, t; if (f) { p = f.p; t = f.t; } else { camera.getWorldDirection(d); p = camera.position.toArray(); t = [p[0] + d.x, p[1] + d.y, p[2] + d.z]; }
        return JSON.stringify({ p, t, h: pl.h, st: pl.steer, lat: pl.lat, v: pl.v }); })()`)); }
    // Abschnitte zwischen Kamerawechseln getrennt auswerten
    const teile = []; let akt = []; for (const r of R) { if (r === null) { if (akt.length > 8) teile.push(akt); akt = []; } else akt.push(typeof r === 'string' ? JSON.parse(r) : r); } if (akt.length > 8) teile.push(akt);
    const m = { lenk: [], gier: [], ort: [], hoch: [], blick: [], neig: [] };
    for (const T of teile) { const h = entw(T.map(r => r.h));
      m.lenk.push(...zit(T.map(r => r.st * 100))); m.gier.push(...zit(h.map(x => x * 180 / Math.PI)));
      const zx = zit(T.map(r => r.p[0] * 1000)), zz = zit(T.map(r => r.p[2] * 1000)); m.ort.push(...zx.map((x, i) => Math.hypot(x, zz[i]))); m.hoch.push(...zit(T.map(r => r.p[1] * 1000)));
      const by = entw(T.map(r => Math.atan2(r.t[0] - r.p[0], r.t[2] - r.p[2]))), bn = T.map(r => Math.atan2(r.t[1] - r.p[1], Math.hypot(r.t[0] - r.p[0], r.t[2] - r.p[2])));
      m.blick.push(...zit(by.map(x => x * 180 / Math.PI))); m.neig.push(...zit(bn.map(x => x * 180 / Math.PI))); }
    const e = { lenk: rms(m.lenk), gier: rms(m.gier), ort: rms(m.ort), hoch: rms(m.hoch), blick: rms(m.blick), neig: rms(m.neig) }; alle[name] = e;
    console.log(`${name.padEnd(16)} Lenkung ${e.lenk.toFixed(2)} % · Auto ${e.gier.toFixed(4)}° · Kamera ${e.ort.toFixed(1)} mm, Höhe ${e.hoch.toFixed(1)} mm · Blick ${e.blick.toFixed(4)}° / ${e.neig.toFixed(4)}°`); }
  if (flag('json', '')) fs.writeFileSync(flag('json'), J(alle, null, 1));
})().catch(e => { console.error('FEHLER', e.message || e); process.exit(1); });
