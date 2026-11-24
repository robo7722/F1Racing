// Prüft die Renderauflösung der Nachbearbeitung bei Pixelverhältnis 2 (wie auf dem Handy) über Wetterwechsel hinweg. „soll“ und „ist“ müssen in jeder Zeile gleich sein.
// Anlass (v2.97): Nach dem ersten Regenrennen rechnete der neu gebaute Composer nur noch in einfacher Auflösung (852×393 statt 1491×688) – siehe docs/WETTER.md, Abschnitt 5a.
//   node tools/wetter/aufloesung_pruefen.js        (Ende mit Fehlercode 1, wenn eine Zeile abweicht)
const { spiel } = require('../textur/spiel.js');
(async () => { const { b, p, ev } = await spiel({ w: 852, h: 393, query: '?qc=none', dpr: 2 }); let bad = 0;
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
  await ev(`window.__noWarm = true; S.track = 'monza'; S.wx = 'dry'; S.sound = false; S.music = false; S.gfx = 'high'; applyGfx(); 1`);
  const m = async name => { const r = JSON.parse(await ev(`JSON.stringify({ dpr: devicePixelRatio, pr: +renderer.getPixelRatio().toFixed(3), soll: Math.round(innerWidth * renderer.getPixelRatio()) + 'x' + Math.round(innerHeight * renderer.getPixelRatio()), ist: Math.round(composer.renderTarget1.width) + 'x' + Math.round(composer.renderTarget1.height), wx: WX.cur, ssr: WX.ssr })`));
    if (r.soll !== r.ist) bad++; console.log(name.padEnd(24), JSON.stringify(r), r.soll === r.ist ? 'ok' : 'FEHLER'); };
  await m('nach dem Laden');
  await p.evaluate(() => window.__race('Monza')); await m('Rennen trocken');
  await ev(`applyWeather('heavy'); 1`); await m('Wechsel auf Regen');
  await ev(`applyWeather('dry'); 1`); await m('zurück auf trocken');
  await ev(`applyWeather('light'); toMenu(); S.track = 'spa'; S.wx = 'dry'; 1`); await p.evaluate(() => window.__race('Spa')); await m('neue Strecke, trocken');
  await b.close(); process.exit(bad ? 1 : 0); })().catch(e => { console.error(e); process.exit(1); });
