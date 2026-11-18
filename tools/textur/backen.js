#!/usr/bin/env node
/* Lack-Textur backen:  node tools/textur/backen.js MER [FER …]   (ohne Kürzel: alle F1- und F2-Lackierungen aus liveries/liveries.json)
   Startet das Spiel mit ?nobake (alte Projektion: Lack-Programm + Aufkleberbogen + Teamlogo) und rendert den Lack-Shader jedes Teams in den UV-Raum der
   abgewickelten Lack-Teile (alle drei Detailstufen, Attribut uvB aus car.bin, siehe uv.py). Doppelte Auflösung, dann verkleinert (glatte Kanten);
   Lücken zwischen den Stücken werden mit den Randfarben aufgefüllt (Mipmaps bluten sonst über die Nähte).
   Ergebnis: liveries/textur/<Kürzel>.webp (verlustfrei; PNG-Fassung in tools/textur/.cache/) und Eintrag in liveries.json (_tex, über build.manifest() aus tools/sticker/build.py). Die Startnummer gehört NICHT in die Textur (bleibt eine Einblendung je Fahrer).
   Ansicht von oben: tools/sticker/.cache/<Kürzel>_oben_bogen.png aus build.py (Eintrag top in tools/sticker/<Kürzel>.json) wird auf alle nach oben
   zeigenden Lackflächen gelegt, die von oben zu sehen sind (Höhenkarte aus Stufe 0, 4 cm Spielraum für Stufe 1/2).
   Danach wieder backen, wenn sich tools/sticker/<Kürzel>.json (build.py) oder die Abwicklung (uv.py) ändert. */
const { spiel, ROOT } = require('./spiel'); const fs = require('fs'); const path = require('path');
const SS = 2;
(async () => {
  const man = JSON.parse(fs.readFileSync(path.join(ROOT, 'liveries', 'liveries.json'), 'utf8'));
  let keys = process.argv.slice(2); if (!keys.length) keys = Object.keys(man).filter(k => man[k] && (man[k].kind === 'f1' || man[k].kind === 'f2'));
  const { b, ev } = await spiel({ w: 640, h: 400, query: '?nobake' });
  fs.mkdirSync(path.join(ROOT, 'liveries', 'textur'), { recursive: true });
  for (const tk of keys) {
    // warten, bis Bogen und Logo geladen sind
    for (let i = 0; i < 90; i++) { const ok = await ev(`(() => { const tk = __arg; if (!hasDecal(tk)) return true; const u = decalUniforms(tk); return (!SHEETS[tk] || u.uSheetOn.value > 0.5) && (!DECALS[tk] || u.uDecalOn.value > 0.5); })()`, tk); if (ok) break; await new Promise(r => setTimeout(r, 1000)); }
    const t0 = Date.now();
    if (!(await ev(`!!LIVERY[__arg]`, tk))) { console.log(tk, 'übersprungen: kein Lack-Programm (Textur würde im Spiel nicht verwendet)'); try { fs.unlinkSync(path.join(ROOT, 'liveries', 'textur', tk + '.webp')); } catch (e) {} continue; }
    const topF = path.join('tools', 'sticker', '.cache', tk + '_oben_bogen.png'), hasTop = fs.existsSync(path.join(ROOT, topF)) && fs.statSync(path.join(ROOT, topF)).mtimeMs >= fs.statSync(path.join(ROOT, 'tools', 'sticker', tk + '.json')).mtimeMs - 1;
    if (!hasTop && JSON.parse(fs.readFileSync(path.join(ROOT, 'tools', 'sticker', tk + '.json'), 'utf8')).top) { console.log(tk, 'FEHLER: Ansicht von oben fehlt oder ist älter als die Beschreibung – erst python3 tools/sticker/build.py', tk); continue; }
    const url = await ev(`(async () => { const tk = __arg[0], SS = __arg[1], topUrl = __arg[2], tp = teamTemplate(tk), MD = tp.M; if (!MD.C.tex) throw new Error('Modell ohne UV – erst tools/textur/uv.py');
      const [W, H] = MD.C.tex, w = W * SS, h = H * SS, base = tp.glossMat, mat = base.clone(), hook = base.livHook || base.onBeforeCompile, R = renderer;
      // Ansicht von oben (build.py: top): Bogen + Höhenkarte (höchster Punkt je Stelle) – nur Flächen bekleben, die von oben zu sehen sind
      const XW = 1.15, kind = LIVMAN[tk].kind, Z0 = kind === 'f2' ? -2.6 : -2.45, Z1 = kind === 'f2' ? 3.0 : 3.15;   // wie TOP_XW / BOX in build.py
      let topTex = null, hRT = null;
      if (topUrl) { topTex = await new THREE.TextureLoader().loadAsync(topUrl); topTex.colorSpace = THREE.SRGBColorSpace; topTex.anisotropy = 8;
        const HW = 690, HH = Math.round((Z1 - Z0) * 300); hRT = new THREE.WebGLRenderTarget(HW, HH, { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter, generateMipmaps: false });
        const hm = new THREE.ShaderMaterial({ side: THREE.DoubleSide, vertexShader: 'varying float vY; void main(){ vY = position.y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }', fragmentShader: 'varying float vY; void main(){ gl_FragColor = vec4(vY, 0.0, 0.0, 1.0); }' });
        const hs = new THREE.Scene(); for (const g of [MD.C.lods[0].gloss, MD.C.lods[0].matte]) { const m = new THREE.Mesh(g, hm); m.frustumCulled = false; hs.add(m); }
        const oc = new THREE.OrthographicCamera(-XW, XW, Z1, Z0, 0.1, 20); oc.position.set(0, 10, 0); oc.up.set(0, 0, 1); oc.lookAt(0, 0, 0); oc.updateMatrixWorld();
        R.setRenderTarget(hRT); R.setClearColor(0x000000, 1); R.clear(); R.render(hs, oc); R.setRenderTarget(null); hm.dispose(); }
      const TOPG = '\\n if (vCls < 2.5 && uTopOn > 0.5) { vec3 bn = normalize(vBN); vec2 tuv = vec2((' + XW.toFixed(3) + ' - vLP.x) / ' + (2 * XW).toFixed(3) + ', (vLP.z - (' + Z0.toFixed(3) + ')) / ' + (Z1 - Z0).toFixed(3) + ');'
        + ' if (bn.y > 0.5 && tuv.x > 0.0 && tuv.x < 1.0 && tuv.y > 0.0 && tuv.y < 1.0 && vLP.y > texture2D(uTopH, tuv).r - 0.04) { vec4 t = texture2D(uTop, tuv); diffuseColor.rgb = mix(diffuseColor.rgb, t.rgb, t.a * smoothstep(0.5, 0.72, bn.y)); } }\\n';
      mat.onBeforeCompile = (sh, r) => { if (hook) hook(sh, r);
        const v = sh.vertexShader.replace('#include <project_vertex>', '#include <project_vertex>\\n gl_Position = vec4(uvB * 2.0 - 1.0, 0.0, 1.0); vBN = normal;'), f = sh.fragmentShader.replace('#include <opaque_fragment>', 'gl_FragColor = sRGBTransferOETF(vec4(diffuseColor.rgb, 1.0)); return;');
        const DK = '\\n { vec3 dN = normalize(vLN);';   // Draufsicht VOR den Seitenaufklebern auftragen: wo beide greifen (geneigte Schultern), gewinnt der Seitenbogen
        const f2 = f.includes(DK) ? f.replace(DK, TOPG + DK) : f.replace('#include <alphamap_fragment>', TOPG + '#include <alphamap_fragment>');
        if (v === sh.vertexShader || !f2.includes('uTopH, tuv') || !f2.includes('sRGBTransferOETF(vec4(diffuseColor')) throw new Error('Einhängepunkt im Shader fehlt');
        sh.vertexShader = 'attribute vec2 uvB; varying vec3 vBN;\\n' + v; sh.fragmentShader = 'uniform sampler2D uTop, uTopH; uniform float uTopOn; varying vec3 vBN;\\n' + f2;
        sh.uniforms.uTop = { value: topTex }; sh.uniforms.uTopH = { value: hRT ? hRT.texture : null }; sh.uniforms.uTopOn = { value: topTex ? 1 : 0 }; };
      mat.customProgramCacheKey = () => 'bake-' + tk; mat.side = THREE.DoubleSide;
      const sc = new THREE.Scene(); for (const L of tp.lods) { const m = new THREE.Mesh(L.gloss, mat); m.frustumCulled = false; sc.add(m); }
      const RT = new THREE.WebGLRenderTarget(w, h, { depthBuffer: false }), cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
      R.setRenderTarget(RT); R.setClearColor(0x000000, 0); R.clear(); R.render(sc, cam); const px = new Uint8Array(w * h * 4); R.readRenderTargetPixels(RT, 0, 0, w, h, px); R.setRenderTarget(null); RT.dispose(); mat.dispose(); if (hRT) hRT.dispose(); if (topTex) topTex.dispose();
      // verkleinern (nur gedeckte Unterpunkte zählen)
      const o = new Float32Array(W * H * 4); for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { let r = 0, g = 0, bl = 0, a = 0;
        for (let j = 0; j < SS; j++) for (let i = 0; i < SS; i++) { const q = ((y * SS + j) * w + x * SS + i) * 4; if (px[q + 3] > 127) { r += px[q]; g += px[q + 1]; bl += px[q + 2]; a++; } }
        const p = (y * W + x) * 4; if (a) { o[p] = r / a; o[p + 1] = g / a; o[p + 2] = bl / a; o[p + 3] = 1; } }
      // Lücken auffüllen: leere Punkte bekommen den Mittelwert ihrer gefüllten Nachbarn, Schritt für Schritt nach außen
      let filled = 0; for (let i = 3; i < o.length; i += 4) filled += o[i];
      for (let pass = 0; pass < 24; pass++) { const add = []; for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const p = (y * W + x) * 4; if (o[p + 3]) continue; let r = 0, g = 0, bl = 0, n = 0;
          for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]) { const X = x + dx, Y = y + dy; if (X < 0 || Y < 0 || X >= W || Y >= H) continue; const q = (Y * W + X) * 4; if (o[q + 3] === 1) { r += o[q]; g += o[q + 1]; bl += o[q + 2]; n++; } }
          if (n) add.push(p, r / n, g / n, bl / n); }
        if (!add.length) break; for (let k = 0; k < add.length; k += 4) { const p = add[k]; o[p] = add[k + 1]; o[p + 1] = add[k + 2]; o[p + 2] = add[k + 3]; o[p + 3] = 1; } }
      let mr = 0, mg = 0, mb = 0, mn = 0; for (let p = 0; p < o.length; p += 4) if (o[p + 3]) { mr += o[p]; mg += o[p + 1]; mb += o[p + 2]; mn++; }
      const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const g2 = cv.getContext('2d'), im = g2.createImageData(W, H);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const p = (y * W + x) * 4, q = ((H - 1 - y) * W + x) * 4, a = o[p + 3];   // Zeile 0 der Textur = oben (flipY)
        im.data[q] = a ? o[p] : mr / mn; im.data[q + 1] = a ? o[p + 1] : mg / mn; im.data[q + 2] = a ? o[p + 2] : mb / mn; im.data[q + 3] = 255; }
      g2.putImageData(im, 0, 0); return [cv.toDataURL('image/png'), W, H, filled / (W * H)]; })()`, [tk, SS, hasTop ? topF.split(path.sep).join('/') + '?t=' + Date.now() : null]);
    const [data, W, H, cov] = url, png = path.join(ROOT, 'tools', 'textur', '.cache', tk + '.png'), out = path.join(ROOT, 'liveries', 'textur', tk + '.webp');
    fs.mkdirSync(path.dirname(png), { recursive: true }); fs.writeFileSync(png, Buffer.from(data.split(',')[1], 'base64'));   // PNG zum Ansehen/Nachbearbeiten (nicht im Repo)
    require('child_process').execFileSync('python3', ['-c', 'import sys; from PIL import Image; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], "WEBP", lossless=True, method=6)', png, out]);   // verlustfreies WebP: halb so groß wie PNG
    console.log(tk, hasTop ? '(mit Ansicht von oben)' : '', W + '×' + H, 'gedeckt', (cov * 100).toFixed(1) + ' %', (fs.statSync(out).size / 1024).toFixed(0) + ' KB', ((Date.now() - t0) / 1000).toFixed(1) + ' s');
  }
  // liveries.json neu schreiben (wie build.py; _tex = alle Dateien in liveries/textur/)
  require('child_process').execFileSync('python3', ['-c', 'import sys; sys.path.insert(0, "tools/sticker"); import build; build.manifest()'], { cwd: ROOT, stdio: 'inherit' });
  await b.close();
})().catch(e => { console.error('FEHLER', e); process.exit(1); });
