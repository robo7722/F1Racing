// Leistungsvergleich zweier Stände (Playwright, Handy-Emulation 960×432, volles Feld, KI fährt):
//   node qc/perf-vergleich.js <port> [Strecke] [f1|f2]   – je Stand einen Server starten (z. B. git worktree + python3 -m http.server <port>)
// Misst: Zeichenaufrufe/Dreiecke/Renderzeit je Kamera (0 Verfolger, 2 Cockpit, 3 TV), hochgeladener Texturspeicher (texImage2D/texStorage2D), Shader.
// Renderzeit in SwiftShader nur grob (±5 %); Aufrufe, Dreiecke und Speicher sind verlässlich.
const { chromium, devices } = require('playwright');
const port = process.argv[2], track = process.argv[3] || 'Monza', ser = process.argv[4] || 'f1';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 960, height: 432 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true, userAgent: devices['Pixel 7'].userAgent });
  await ctx.addInitScript(() => { const T = window.__texUp = { bytes: 0, n: 0, big: {} };
    for (const P of [WebGLRenderingContext.prototype, WebGL2RenderingContext.prototype]) { const o = P.texImage2D; P.texImage2D = function (...a) { try { let w, h; if (a.length >= 9) { w = a[3]; h = a[4]; } else { const src = a[5]; w = src.width || src.videoWidth; h = src.height || src.videoHeight; } if (a[1] === 0 && w * h) { const by = w * h * 4; T.bytes += by; T.n++; const k = w + 'x' + h; T.big[k] = (T.big[k] || 0) + 1; } } catch (e) {} return o.apply(this, a); };
      const s2 = P.texStorage2D; if (s2) P.texStorage2D = function (t, lv, f, w, h) { T.bytes += w * h * 4 * (lv > 1 ? 1.33 : 1); T.n++; const k = 'S' + w + 'x' + h; T.big[k] = (T.big[k] || 0) + 1; return s2.apply(this, arguments); }; } });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto(`http://localhost:${port}/index.html?` + Date.now()); await p.waitForFunction(() => window.__race && window.__qcApi, null, { timeout: 120000 });
  await p.evaluate(() => { window.__noStartGame = true; window.__plAI = true; });
  const t0 = Date.now(); await p.evaluate(([t, s]) => window.__race(t, s), [track, ser]); const tLoad = Date.now() - t0;
  await p.waitForTimeout(8000);
  const r = await p.evaluate(async () => {
    const A = window.__qcApi, R = A.renderer, I = R.info, gl = R.getContext(), px = new Uint8Array(4);
    const sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
    A.pause && A.pause();
    // Texturen der Szene: Anzahl und geschätzter Speicher (RGBA, mit Mipmaps ×1,33)
    const seen = new Set(); let tb = 0, carTb = 0; const big = [];
    const addT = (t, car) => { if (!t || seen.has(t)) return; seen.add(t); const im = t.image; const w = im && (im.width || im.videoWidth), h = im && (im.height || im.videoHeight); if (!w) return; const by = w * h * 4 * (t.generateMipmaps !== false ? 1.33 : 1); tb += by; if (car) carTb += by; big.push([Math.round(by / 1048576 * 10) / 10, w + 'x' + h, (t.name || (im.src || '').split('/').pop() || '').slice(0, 40)]); };
    const carSet = new Set(); for (const c of (A.cars || [])) if (c.mesh && c.mesh.g) c.mesh.g.traverse(o => carSet.add(o));
    A.scene.traverse(o => { if (!o.material) return; for (const m of [].concat(o.material)) for (const k in m) { const v = m[k]; if (v && v.isTexture) addT(v, carSet.has(o)); } });
    big.sort((a, b) => b[0] - a[0]);
    const out = { tex: seen.size, texMB: Math.round(tb / 1048576), carTexMB: Math.round(carTb / 1048576), top: big.slice(0, 8), gpuTex: I.memory.textures, gpuGeo: I.memory.geometries, programs: I.programs.length, cams: {} };
    I.autoReset = false; out.upMB = Math.round(window.__texUp.bytes / 1048576); out.upN = window.__texUp.n; out.upSizes = Object.entries(window.__texUp.big).sort((a, b) => b[1] - a[1]).slice(0, 12);
    for (const cam of [0, 2, 3]) {
      A.S.cam = cam; let calls = 0, tris = 0, ms = []; const L = A.L;
      for (let k = 0; k < 6; k++) { const s = (k + 0.5) * L / 6; window.__tp(s); window.__frame(4); window.__tp(s); window.__frame(12);
        I.render.calls = I.render.triangles = 0; A.renderNow(); sync(); calls += I.render.calls; tris += I.render.triangles;
        let best = 1e9; for (let q = 0; q < 3; q++) { const t1 = performance.now(); A.renderNow(); sync(); best = Math.min(best, performance.now() - t1); } ms.push(best); }
      out.cams[cam] = { calls: Math.round(calls / 6), triK: Math.round(tris / 6000), ms: Math.round(ms.reduce((a, b) => a + b) / ms.length) };
    }
    out.upMB2 = Math.round(window.__texUp.bytes / 1048576); return out;
  });
  r.load = tLoad; r.errs = errs.slice(0, 3); console.log(JSON.stringify(r));
  await b.close();
})();
