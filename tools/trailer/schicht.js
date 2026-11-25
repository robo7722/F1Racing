// Schicht: arbeitet eine Warteschlange ab – Studio starten, Einstellungen proben oder rechnen, Studio schließen, nächste Strecke.
//   node tools/trailer/schicht.js <Schicht> <Port> [--aus trailer-ausgabe]        (Schichten stehen in tools/trailer/schichten.js)
// Neustart-fest: fertige Einstellungen und vorhandene Probeblätter werden übersprungen, ein Block ohne offene Arbeit startet kein Studio.
// Mehrere Schichten laufen gleichzeitig (je ein eigener Port); mehr als drei bringen auf vier Kernen nichts.
const fs = require('fs'); const path = require('path'); const http = require('http'); const { spawn } = require('child_process');
const ROOT = path.resolve(__dirname, '../..'), a = process.argv.slice(2), flag = (n, d) => { const i = a.indexOf('--' + n); return i < 0 ? d : a[i + 1]; };
const NAME = a[0], PORT = a[1], AUS = path.resolve(ROOT, flag('aus', 'trailer-ausgabe')), SCH = require('./schichten.js')[NAME]; if (!SCH || !PORT) { console.error('Aufruf: schicht.js <Schicht> <Port> – bekannt:', Object.keys(require('./schichten.js')).join(', ')); process.exit(1); }
const T0 = Date.now(), T = () => new Date().toISOString().slice(11, 19), log = (...x) => console.log(T(), ...x);
const offen = st => st.probe ? !fs.existsSync(path.join(AUS, 'probe', 'blatt_' + st.szenen.split(',')[0] + '.jpg')) : st.szenen.split(',').some(s => !fs.existsSync(path.join(AUS, 'bilder', s, 'fertig')));
const lauf = (cmd, args, warteAuf) => new Promise(ok => { const p = spawn(cmd, args, { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] }); let fertig = false;
  const zeile = d => { for (const z of String(d).split('\n')) if (z.trim()) { console.log('   ' + z.slice(0, 260)); if (warteAuf && z.includes(warteAuf) && !fertig) { fertig = true; ok(p); } } };
  p.stdout.on('data', zeile); p.stderr.on('data', zeile); p.on('exit', c => { if (!fertig) { fertig = true; ok(warteAuf ? null : c); } }); });
const ende = () => new Promise(ok => { const r = http.request({ host: '127.0.0.1', port: PORT, path: '/ende', method: 'POST', timeout: 8000 }, res => { res.resume(); res.on('end', ok); }); r.on('error', ok); r.on('timeout', () => { r.destroy(); ok(); }); r.end(''); });
const rennen = (b, s) => ({ fahrer: s.fahrer || b.fahrer || 'VER', wetter: s.wetter || 'dry', klasse: b.klasse || 'f1' });
(async () => {
  for (const b of SCH) {
    const erste = b.schritte.find(offen); if (!erste) { log('Block', b.strecke || 'Garage', '– nichts offen'); continue; }
    let aktiv = b.menue ? null : rennen(b, erste);
    const args = b.menue ? ['--menue'] : ['--strecke', b.strecke, '--klasse', aktiv.klasse, '--fahrer', aktiv.fahrer, '--wetter', aktiv.wetter];
    log('Studio startet:', args.join(' ')); const st = await lauf('node', ['tools/trailer/studio.js', '--port', PORT, ...args], 'BEREIT');
    if (!st) { log('FEHLER: Studio kam nicht hoch'); continue; }
    for (const s of b.schritte) { if (!offen(s)) continue;
      const da = ['tools/trailer/dreh.js', PORT, s.szenen, '--aus', AUS]; if (s.probe) da.push('--probe', '--proben', String(s.proben || 4));
      if (!b.menue) { const r = rennen(b, s); if (JSON.stringify(r) !== JSON.stringify(aktiv)) { da.push('--rennen', JSON.stringify(r)); aktiv = r; } }
      log(s.probe ? 'Probe' : 'Dreh', s.szenen, b.menue ? '' : JSON.stringify(aktiv)); const c = await lauf('node', da); if (c) log('FEHLER im Schritt', s.szenen, 'Code', c); }
    await ende(); try { st.kill('SIGKILL'); } catch (e) {} await new Promise(r => setTimeout(r, 2500)); log('Studio beendet');
  }
  log('Schicht', NAME, 'fertig nach', ((Date.now() - T0) / 60000).toFixed(0), 'min');
})();
