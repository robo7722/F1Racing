// Prüfstand für die Regentropfen auf dem Visier (Helmansicht): legt den Tropfen-Shader aus index.html über ein Standbild und rendert je Tempo eine Bildfolge –
// in Sekunden statt Minuten (das Spiel braucht im Testbrowser ~35 s je Bild). Der Shader-Code wird direkt aus index.html gelesen (dropLayer, Aufruf, Einrechnen),
// es wird also immer der echte Stand geprüft. Nur der Zeitverlauf (sim) ist nachgebaut – bei Änderungen in tick() (uDrop) hier mitziehen.
//   node tools/wetter/tropfen_pruefstand.js <Standbild.png> <Ausgabeordner> [km/h ...] [--regen 0..1] [--licht 0..1]      Standard: 0 120 290, starker Regen, Tageslicht
//   --licht: Umgebungslicht für den Zusatzglanz (uDropA): 1 Tag, 0.3 nachts im Flutlicht, 0 nachts im Dunkeln. Das Standbild wird dafür grob in lineare Helligkeit
//   zurückgerechnet (Gamma 2,2) – im Spiel wird vor der Tonwertkurve gerechnet, ein kleiner Zusatz wirkt dort im Dunkeln viel heller als im fertigen Bild.
//   Ergebnis: t<kmh>_<0..7>.png (8 Bilder im Abstand von 66 ms nach 6 s Vorlauf) und zoom.png (vergrößerter Ausschnitt je Tempo)
// Standbild: am besten eine Helmansicht ohne Tropfen, z. B. node tools/wetter/regen_bilder.js Spa heavy <Ordner> 2150,2 --pre "window.__noDrops = 1"
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const a = process.argv.slice(2), opt = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : +a.splice(i, 2)[1]; }, regen = opt('regen', 1), licht = opt('licht', 1), [bg, out, ...kmh] = a; fs.mkdirSync(out, { recursive: true });
  const src = fs.readFileSync(path.join(__dirname, '../../index.html'), 'utf8'), cut = (from, to) => { const i = src.indexOf(from), j = src.indexOf(to, i); if (i < 0 || j < 0) throw new Error('nicht gefunden: ' + from); return src.slice(i, j + to.length); };
  const glsl = cut('float hash12(vec2 p){', '\n') + cut('vec2 hash22(vec2 p){', '\n') + cut('vec4 dropLayer(', '0.55 * gl)); }'), call = cut('drp = dropLayer(', ';'), mix = cut('col = col * (1.0 + drp.w', ';');
  const html = `<!doctype html><meta charset="utf-8"><body style="margin:0;background:#000"><canvas id="c"></canvas>`;
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p.on('pageerror', e => console.log('FEHLER', String(e))); await p.setContent(html);
  await p.evaluate(async ([img, glsl, call, mix, licht]) => {
    const w = 1280, h = 720, cv = document.getElementById('c'); cv.width = w; cv.height = h; const gl = cv.getContext('webgl', { preserveDrawingBuffer: true });
    const vs = 'attribute vec2 a; varying vec2 vUv; void main(){ vUv = a * 0.5 + 0.5; gl_Position = vec4(a, 0.0, 1.0); }';
    const fs = `precision highp float; uniform sampler2D tDiffuse; uniform vec4 uDrop; uniform float uAspect, uDropA; varying vec2 vUv;
      ${glsl}
      void main(){ vec2 uv = vUv, c0 = vUv - 0.5; vec4 drp = vec4(0.0);
        if (uDrop.x > 0.001) { vec2 dq = c0 * vec2(uAspect, 1.0); ${call} uv += drp.xy * vec2(1.0 / uAspect, 1.0); drp.z = min(drp.z, 1.0); }
        vec3 col = pow(texture2D(tDiffuse, uv).rgb, vec3(2.2)); ${mix} gl_FragColor = vec4(pow(max(col, 0.0), vec3(1.0 / 2.2)), 1.0); }`;
    const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr)); gl.useProgram(pr);
    const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW); const l = gl.getAttribLocation(pr, 'a'); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 2, gl.FLOAT, false, 0, 0);
    const im = new Image(); im.src = img; await im.decode(); gl.bindTexture(gl.TEXTURE_2D, gl.createTexture()); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.viewport(0, 0, w, h); gl.uniform1f(gl.getUniformLocation(pr, 'uAspect'), w / h); gl.uniform1f(gl.getUniformLocation(pr, 'uDropA'), licht); const uD = gl.getUniformLocation(pr, 'uDrop');
    window.draw = st => { gl.uniform4f(uD, st.x, st.y, st.z, st.w); gl.drawArrays(gl.TRIANGLES, 0, 3); };
    // Zeitverlauf wie in tick(): y Fahrtwind (0 unter 22 km/h … 1 ab 281 km/h), z Laufzeit der Lebensläufe, w Weg zur Seite
    window.sim = (st, kmh, dt) => { const y = Math.min(1, Math.max(0, (kmh / 3.6 - 6) / 72)); st.y += (y - st.y) * Math.min(1, dt * 4); st.z = (st.z + dt * (1 + st.y * 2.6)) % 3600; st.w = (st.w + dt * Math.pow(st.y, 1.4) * 1.3) % 512; };
  }, ['data:image/png;base64,' + fs.readFileSync(bg).toString('base64'), glsl, call, mix, licht]);
  const list = (kmh.length ? kmh : ['0', '120', '290']).map(Number);
  for (const k of list) { await p.evaluate(([k, r]) => { window.st = { x: 0.42 + 0.58 * r, y: 0, z: 40, w: 0 }; for (let i = 0; i < 360; i++) sim(st, k, 1 / 60); }, [k, regen]);
    for (let f = 0; f < 8; f++) { await p.evaluate(k => { for (let i = 0; i < 4; i++) sim(st, k, 1 / 60); draw(st); }, k); await p.screenshot({ path: path.join(out, `t${String(k).padStart(3, '0')}_${f}.png`) }); } }
  // Übersicht: je Tempo ein Ausschnitt (rechts oben), 2,5-fach vergrößert
  const tiles = []; for (const k of list) tiles.push((await p.goto('about:blank'), fs.readFileSync(path.join(out, `t${String(k).padStart(3, '0')}_0.png`)).toString('base64')));
  await p.setViewportSize({ width: 1200, height: 500 * list.length }); await p.setContent(`<body style="margin:0;background:#000">` + tiles.map(t => `<div style="width:1200px;height:500px;overflow:hidden;position:relative"><img src="data:image/png;base64,${t}" style="position:absolute;left:-1750px;top:-150px;width:3200px;image-rendering:auto"></div>`).join(''));
  await p.screenshot({ path: path.join(out, 'zoom.png') }); await b.close(); console.log('fertig:', out, list.join(', ') + ' km/h');
})().catch(e => { console.error(e); process.exit(1); });
