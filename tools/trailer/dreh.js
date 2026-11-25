// Dreh: rechnet Einstellungen aus tools/trailer/drehplan.js als Bildfolgen – in einem laufenden Studio (tools/trailer/studio.js --port N).
//   node tools/trailer/dreh.js <Port> <Szene[,Szene…]> [--probe] [--aus trailer-ausgabe] [--neu] [--rennen '{"fahrer":"SEN","wetter":"heavy"}']
//   --rennen: vorher in derselben Sitzung ein neues Rennen starten (anderer Fahrer/anderes Wetter/andere Klasse; die Strecke bleibt)
//   --probe:  je Einstellung nur 4 Bilder (Anfang, 1/3, 2/3, Ende) in halber Auflösung → <aus>/probe/<erste Szene>.jpg als Kontaktblatt
//   --neu:    schon fertige Einstellungen noch einmal rechnen (sonst werden sie übersprungen)
// Ergebnis: <aus>/bilder/<Szene>/0001.jpg … (1920 × 804). Mehrere Studios können gleichzeitig rechnen (je ein Aufruf).
const fs = require('fs'); const path = require('path'); const http = require('http'); const { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '../..'), a = process.argv.slice(2), flag = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : a[i + 1]; }, has = n => a.includes('--' + n);
const PLAN = require('./drehplan.js'), PORT = +a[0], SZENEN = (a[1] || '').split(',').filter(Boolean), PROBE = has('probe'), AUS = path.resolve(ROOT, flag('aus', 'trailer-ausgabe')), NEU = has('neu'), RENNEN = flag('rennen', '');
const FPS = PLAN.fps, J = JSON.stringify, T0 = Date.now(), T = () => ((Date.now() - T0) / 1000).toFixed(0) + ' s';
const post = (weg, daten) => new Promise((ok, nein) => { const r = http.request({ host: '127.0.0.1', port: PORT, path: weg, method: 'POST', timeout: 3600000 }, res => { const c = []; res.on('data', d => c.push(d)); res.on('end', () => { const s = Buffer.concat(c).toString(); if (res.statusCode !== 200) nein(new Error(s.slice(0, 600))); else ok(s); }); }); r.on('error', nein); r.end(daten); });
const ev = code => post('/eval', code), speichere = (datei, url) => fs.writeFileSync(datei, Buffer.from(url.slice(url.indexOf(',') + 1), 'base64'));

async function szene(name, proben) {
  const z = PLAN.szenen[name]; if (!z) throw new Error('Szene fehlt: ' + name);
  const n = Math.round(z.dauer * FPS) + (z.zugabe ?? 2), dir = path.join(AUS, 'bilder', name), fertig = path.join(dir, 'fertig');
  if (!PROBE && !NEU && fs.existsSync(fertig)) { console.log(T(), name, 'ist fertig – übersprungen'); return; }
  if (!PROBE) fs.mkdirSync(dir, { recursive: true });
  const t0 = Date.now(), seite = !!z.seite, mb = PROBE ? 1 : (z.mb || 1), NP = +flag('proben', 4), zeigen = PROBE ? new Set(Array.from({ length: NP }, (_, k) => Math.min(n - 3, Math.max(1, Math.round(k * (n - 3) / (NP - 1))))) ) : null;
  const ziel = i => PROBE ? path.join(AUS, 'probe', `${name}_${[...zeigen].sort((x, y) => x - y).indexOf(i)}.jpg`) : path.join(dir, String(i + 1).padStart(4, '0') + '.jpg');
  if (z.typ === 'garage') {   // Garage: Schärfentiefe – je Trailerbild 4 Zwischenbilder (ausgewogene Blendenpunkte, gleiche Kamerastellung), gemittelt über die letzten 3 Trailerbilder
    const sub = 4, fen = PROBE ? 8 : 12, U = i => (Math.max(0, i) + 0.5) / n;
    await ev(`TRS.setz(${J(z.a)}, ${J(z.b)}, ${J({ ease: z.ease || 'io', n: fen })}); ${z.vor || ''}; 1`);
    let voll = -9;
    for (let i = 0; i < n; i++) { if (PROBE && !zeigen.has(i)) continue; if (!PROBE && !NEU && fs.existsSync(ziel(i))) continue;
      for (let b = (voll === i - 1 ? i : i - fen / sub + 1); b <= i; b++) for (let k = 0; k < sub; k++) await ev(`TRS.sub(${U(b)}, ${b / FPS}, ${k}, ${b + 1000}); 1`);   /* Puffer füllen: am Anfang und nach einer Wiederaufnahme auch die beiden Bilder davor */
      voll = i; speichere(ziel(i), await ev(`TRS.mittel('image/jpeg', 0.96)`)); if (PROBE) proben.push(ziel(i)); else if (i % 20 === 19) console.log(T(), name, i + 1, '/', n); }
  } else {
    await ev(`TR.start(); pl.lapsDone = 0; pl.finished = false; TR.seed(${z.seed ?? 7}); TR.je = null; TR.speed = 0; TR.vig = null; window.__plLod = ${z.lod ?? 0}; TR.ao(${z.ao !== false}); ${z.vor || ''}; 1`);
    let cur = null, segVon = 0;
    for (let i = 0; i < n; i++) {
      const ta = i / FPS, te = (i + 1) / FPS; let seg = z.kams[z.kams.length - 1], von = 0;
      for (const k of z.kams) { if (te <= (k.bis ?? 1e9) + 1e-6) { seg = k; break; } von = k.bis; }
      if (seg !== cur) { cur = seg; segVon = von; await ev(`TR.kam(${J(seg.a)}, ${J(seg.b || null)}, ${J({ ease: seg.ease, wack: seg.wack, wackF: seg.wackF })}); TR.speed = ${seg.speed ?? 0}; TR.vig = ${seg.vig ?? 'null'}; ${seg.vor || ''}; 1`); }
      const bis = Math.min(cur.bis ?? z.dauer, z.dauer), u = t => Math.max(0, Math.min(1, (t - segVon) / Math.max(1e-6, bis - segVon)));
      const zl = Array.isArray(z.zeitlupe) ? z.zeitlupe[0] + (z.zeitlupe[1] - z.zeitlupe[0]) * (i / Math.max(1, n - 1)) : (z.zeitlupe || 1), ms = 1000 / FPS * zl;
      if ((PROBE && !zeigen.has(i)) || (!PROBE && !NEU && fs.existsSync(ziel(i)))) { await ev(`TR.tz = ${te}; TR.je && TR.je(${te}, ${ms}); TR.u = ${u(te)}; TR.takt(${ms}, false); 1`); continue; }   /* Probe: nur ausgewählte Bilder; Wiederaufnahme nach Abbruch: vorhandene Bilder nur durchsimulieren */
      const url = await ev(`TR.tz = ${te}; TR.bild(${u(ta)}, ${u(te)}, ${ms}, ${mb}, ${seite ? "''" : "'image/jpeg'"}, 0.96, ${z.verschluss ?? 0.5})`);
      if (seite) await post('/bild', J({ datei: ziel(i), jpg: 96 })); else speichere(ziel(i), url);
      if (PROBE) proben.push(ziel(i)); else if (i % 20 === 19) console.log(T(), name, i + 1, '/', n, await ev(`Math.round(pl.v * 3.6) + ' km/h s=' + Math.round(pl.d)`));
    }
  }
  if (!PROBE) fs.writeFileSync(fertig, new Date().toISOString());
  console.log(T(), name, PROBE ? 'Probe' : 'fertig:', n, 'Bilder,', ((Date.now() - t0) / 1000).toFixed(0), 's');
}

(async () => {
  fs.mkdirSync(path.join(AUS, 'probe'), { recursive: true });
  const offen = SZENEN.filter(s => PROBE || NEU || !fs.existsSync(path.join(AUS, 'bilder', s, 'fertig')));
  if (!offen.length) { console.log('alles fertig:', SZENEN.join(',')); return; }
  if (RENNEN) { console.log(T(), await post('/rennen', RENNEN)); await ev(`TR.start(); 1`); }
  const garage = PLAN.szenen[offen[0]].typ === 'garage'; if (!garage) await ev(`TR.skala(${PROBE ? 0.5 : 1}); 1`);
  const proben = []; for (const s of offen) await szene(s, proben);
  if (PROBE && proben.length) {   // Kontaktblatt: je Einstellung eine Zeile mit 4 Bildern
    const ein = proben.flatMap(f => ['-i', f]), out = path.join(AUS, 'probe', 'blatt_' + SZENEN[0] + '.jpg');
    const fl = proben.map((_, k) => `[${k}]scale=480:200,setsar=1[v${k}]`).join(';') + ';' + proben.map((_, k) => `[v${k}]`).join('') + `concat=n=${proben.length}:v=1:a=0,tile=4x${Math.ceil(proben.length / 4)}`;   /* xstack stürzte bei 8 Bildern ab */
    execFileSync('ffmpeg', ['-v', 'error', '-y', ...ein, '-filter_complex', fl, '-frames:v', '1', '-q:v', '4', out]); console.log('Kontaktblatt:', out);
  }
})().catch(e => { console.error('FEHLER', e.message || e); process.exit(1); });
