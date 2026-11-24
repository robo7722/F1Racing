// Welche Reifen sind bei welchem Wetter montiert? Startet nacheinander Rennen über den echten Menüweg (Einstellung S.wx, ohne Testschalter) und zählt je Rennen
// Mischung und Farbe der Flankenmarkierung aller Autos. Soll: trocken = rot/gelb/weiß gemischt, leichter Regen = alle Intermediates (grün), starker Regen = alle Regenreifen (blau).
//   node tools/wetter/reifen_pruefen.js light dry heavy light auto-leicht auto-stark
//   auto-leicht / auto-stark: Einstellung „Zufall“, die Auslosung ist für den Test auf leichten bzw. starken Regen festgelegt.
// Stand 24.11.2026 (v3.00): alle Wege richtig – auch nach einem Wetterwechsel zwischen zwei Rennen.
const { spiel } = require('../textur/spiel.js');
(async () => { const { b, p, ev } = await spiel({ w: 1280, h: 720, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
  await ev(`S.gfx = 'high'; applyGfx(); window.__noWarm = true; S.sound = false; S.music = false; 1`);
  const info = () => ev(`(() => { const name = ['weich (rot)', 'mittel (gelb)', 'hart (weiß)', 'Intermediate (grün)', 'Regenreifen (blau)'], far = c => { const col = c.mesh.wfl.geometry.attributes.color; for (let i = 0; i < col.count; i++) { const r = col.getX(i), g = col.getY(i), b = col.getZ(i); if (Math.max(r, g, b) > 0.3 && Math.max(r, g, b) - Math.min(r, g, b) > 0.15) return r > g && r > b ? (g > 0.5 ? 'gelb' : 'rot') : g > b ? 'grün' : 'blau'; } return 'weiß/keine'; };
    const zahl = {}; for (const c of cars) { const k = name[c.mesh.comp] + ' / Markierung ' + far(c); zahl[k] = (zahl[k] || 0) + 1; }
    return JSON.stringify({ gewählt: S.wx, wetter: WX.cur, autos: zahl }); })()`);
  for (const wx0 of process.argv.slice(2)) { const wx = wx0.replace('auto-leicht', 'auto').replace('auto-stark', 'auto'); await ev(`RAIN_P.spa = ${wx0 === 'auto-leicht' ? '[1, 0]' : wx0 === 'auto-stark' ? '[1, 1]' : 'RAIN_P.spa'}; S.wx = ${JSON.stringify(wx)}; save(); 1`); console.log(wx.padEnd(6), 'Rennen', await p.evaluate(() => window.__race('Spa')), await info()); await ev(`toMenu(); 1`); await p.waitForTimeout(900); }
  await b.close(); })().catch(e => { console.error(e); process.exit(1); });
