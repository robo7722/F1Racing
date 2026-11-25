// Trailer-Studio: startet das echte Spiel im Testbrowser, baut eine Strecke und bleibt offen. Über einen kleinen lokalen Dienst
// lassen sich dann beliebig viele Einstellungen ausprobieren und Bilder aufnehmen, ohne die Strecke jedes Mal neu zu bauen (~2 min).
//   node tools/trailer/studio.js --port 8801 --strecke Spa [--klasse f1|f2|kart] [--fahrer VER] [--wetter dry|light|heavy] [--gfx ultra] [--size 1920,804] [--dpr 1] [--menue]
//   --menue: keine Strecke bauen, im Hauptmenü bleiben (Garage/Showroom)
// Bedienen:
//   curl -s localhost:8801/eval --data 'pl.v'                      → wertet Code im Spiel aus (Modul-Bereich von index.html)
//   curl -s localhost:8801/bild --data '{"datei":"/pfad/a.png"}'   → Bild der Seite speichern (optional "clip":[x,y,w,h], "jpg":90)
//   curl -s localhost:8801/rennen --data '{"strecke":"Spa","fahrer":"SEN","wetter":"heavy"}'   → weiteres Rennen ohne Neuladen (anderer Fahrer/anderes Wetter)
//   curl -s localhost:8801/ende
const http = require('http'); const { starte } = require('./spielstart.js');
const a = process.argv.slice(2), flag = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : a[i + 1]; }, has = n => a.includes('--' + n);
const PORT = +flag('port', 8801), TRK = flag('strecke', 'Spa'), SER = flag('klasse', 'f1'), DRV = flag('fahrer', 'VER'), WXK = flag('wetter', 'dry'), GFX = flag('gfx', 'ultra');
const SIZE = flag('size', '1920,804').split(',').map(Number), DPR = +flag('dpr', 1), MENUE = has('menue');
(async () => {
  const g = await starte({ size: SIZE, dpr: DPR, menue: MENUE, fahrer: DRV, gfx: GFX });
  if (!MENUE) await g.rennen(TRK, { fahrer: DRV, wetter: WXK, klasse: SER });
  const srv = http.createServer((req, res) => { let d = ''; req.on('data', c => d += c); req.on('end', async () => {
    try {
      if (req.url === '/eval') { const r = await g.ev(d); res.end(typeof r === 'string' ? r : JSON.stringify(r)); }
      else if (req.url === '/bild') { const q = JSON.parse(d), o = { path: q.datei }; if (q.clip) o.clip = { x: q.clip[0], y: q.clip[1], width: q.clip[2], height: q.clip[3] }; if (q.jpg) { o.type = 'jpeg'; o.quality = q.jpg; } await g.p.screenshot(o); res.end('ok ' + q.datei); }
      else if (req.url === '/rennen') { const q = JSON.parse(d); const ok = await g.rennen(q.strecke || TRK, q); res.end('Rennen: ' + ok); }
      else if (req.url === '/ende') { res.end('ende'); await g.b.close(); process.exit(0); }
      else { res.statusCode = 404; res.end('?'); }
    } catch (e) { res.statusCode = 500; res.end('FEHLER ' + String(e).slice(0, 1500)); } }); });
  srv.listen(PORT, '127.0.0.1', () => console.log(g.T(), 'BEREIT auf Port', PORT));
})().catch(e => { console.error(e); process.exit(1); });
