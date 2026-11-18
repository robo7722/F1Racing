// Sichtbarkeit des Fahrers in den Klassikern messen -> modelle/klassiker/fahrer_sicht.json
// Rendert Auto (schwarz, verdeckt) und Fahrer (jedes Dreieck eigene Farbe = Nummer) aus vielen Blickwinkeln: rundherum in mehreren Abständen und Höhen
// (Verfolger-, Hoch-, Showroom- und Wiederholungskameras), dazu TV- und Helmkamera mit Kopfbewegung. Ein Dreieck des Rumpfs gilt als sichtbar, wenn es
// in irgendeinem Bild mindestens einen Bildpunkt hat. Arme und Hände bleiben im Spiel ohnehin immer (sie bewegen sich).
// Aufruf (Spiel muss über einen lokalen Server laufen):  python -m http.server 8790   und dann   node tools/klassiker/fahrer_sicht.js [port]
// braucht Playwright (Chromium). Dauert mit Software-Rendering einige Minuten.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const port = process.argv[2] || 8790, OUT = path.join(__dirname, '..', '..', 'modelle', 'klassiker', 'fahrer_sicht.json');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 640, height: 400 } }); p.on('pageerror', e => console.log('Seitenfehler', e.message));
  await p.goto(`http://localhost:${port}/index.html?qc=none`, { timeout: 180000 });
  await p.waitForFunction(() => typeof window.__histDbg === 'function', null, { timeout: 180000 });
  const res = await p.evaluate(async () => {
    const D = window.__histDbg(), { THREE } = D, R = D.renderer, out = {}; window.__histFull = true;
    const RT = new THREE.WebGLRenderTarget(768, 768), px = new Uint8Array(768 * 768 * 4);
    const black = new THREE.MeshBasicMaterial({ color: 0x000000, side: THREE.DoubleSide });
    const idMat = new THREE.ShaderMaterial({ side: THREE.DoubleSide, vertexShader: 'attribute vec3 aId; varying vec3 vId; void main(){ vId = aId; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
      fragmentShader: 'varying vec3 vId; void main(){ gl_FragColor = vec4(vId, 1.0); }' });
    for (const team of Object.keys(D.HIST_CAR)) {
      const H = D.HIST_CAR[team]; await D.histLoad(team);
      const m = D.makeHist({ code: 'TST', name: '', num: 1, team, helmet: 0xffffff }, D.TEAMS[team]); D.scene.remove(m.g);
      const sc = new THREE.Scene(); sc.add(m.g); m.g.updateMatrixWorld(true);
      const K = D.F1FAHRER, G = K.geo, I = G.index.array, P = G.attributes.position.array, n = I.length / 3;
      // Fahrer als Dreiecks-Nummern (Bindhaltung = Sitzhaltung des Rumpfs; die Arme sind egal)
      const pos = new Float32Array(n * 9), id = new Float32Array(n * 9);
      for (let t = 0; t < n; t++) { const v = t + 1, c = [(v & 255) / 255, ((v >> 8) & 255) / 255, ((v >> 16) & 255) / 255];
        for (let j = 0; j < 3; j++) { const q = I[t * 3 + j]; pos.set([P[q * 3], P[q * 3 + 1], P[q * 3 + 2]], t * 9 + j * 3); id.set(c, t * 9 + j * 3); } }
      const ig = new THREE.BufferGeometry(); ig.setAttribute('position', new THREE.BufferAttribute(pos, 3)); ig.setAttribute('aId', new THREE.BufferAttribute(id, 3));
      const dm = m.drv.mesh, idMesh = new THREE.Mesh(ig, idMat); idMesh.position.copy(dm.position); dm.parent.add(idMesh); dm.visible = false;
      m.g.traverse(o => { if (o.isMesh && o !== idMesh) o.material = black; if (o.isSprite) o.visible = false; });
      if (m.shpH) m.shpH.visible = false; m.g.updateMatrixWorld(true);
      const seen = new Uint8Array(n + 1), cam = new THREE.PerspectiveCamera(50, 1, 0.03, 200), views = [];
      for (const r of [3.2, 4.5, 6, 9, 14]) for (const h of [0.35, 0.8, 1.3, 1.9, 2.8, 4.4, 7]) for (let a = 0; a < 32; a++) { const w = a / 32 * Math.PI * 2; views.push([[Math.sin(w) * r, h, Math.cos(w) * r], [0, 0.55, 0], 50]); }
      const ck = m.cam, tv = m.tv;
      for (const dx of [-0.08, 0, 0.08]) for (const dy of [-0.03, 0, 0.04]) for (const yaw of [-0.6, -0.3, 0, 0.3, 0.6]) {   // Helm- und TV-Kamera mit Kopfbewegung und Umschauen
        views.push([[ck[0] + dx, ck[1] + dy, ck[2]], [ck[0] + Math.sin(yaw) * 30, ck[1] - ck[3] - 0.45, Math.cos(yaw) * 30], 80]);
        views.push([[tv[0] + dx, tv[1] + dy, tv[2]], [tv[0] + Math.sin(yaw) * 30, tv[1] - tv[3], Math.cos(yaw) * 30], tv[4] || 52]); }
      for (const [eye, tgt, fov] of views) { cam.fov = fov; cam.updateProjectionMatrix(); cam.position.set(...eye); cam.lookAt(...tgt); cam.updateMatrixWorld();
        R.setRenderTarget(RT); R.setClearColor(0x000000, 1); R.clear(); R.render(sc, cam); R.readRenderTargetPixels(RT, 0, 0, 768, 768, px);
        for (let i = 0; i < px.length; i += 4) { const v = px[i] | (px[i + 1] << 8) | (px[i + 2] << 16); if (v) seen[v] = 1; } }
      R.setRenderTarget(null);
      const bits = new Uint8Array(Math.ceil(n / 8)); let vis = 0; for (let t = 0; t < n; t++) if (seen[t + 1]) { bits[t >> 3] |= 1 << (t & 7); vis++; }
      let s = ''; for (const x of bits) s += String.fromCharCode(x);
      out[H.file] = { n, sichtbar: vis, ansichten: views.length, vis: btoa(s) };
    }
    return out;
  });
  for (const k in res) console.log(k, 'Rumpf sichtbar', res[k].sichtbar, 'von', res[k].n, 'Dreiecken,', res[k].ansichten, 'Ansichten');
  fs.writeFileSync(OUT, JSON.stringify(res)); console.log('geschrieben', OUT);
  await b.close();
})().catch(e => { console.error('FEHLER', e); process.exit(1); });
