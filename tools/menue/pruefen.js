// Menü-Prüfung: geht alle Menü-Bildschirme durch (Schnelles Spiel, Zeitrennen, Karriere, Einstellungen, Pause, Ergebnis), nimmt je Bildschirm ein Bild auf
// und prüft die Lage aller Bedienelemente und Texte: außerhalb des Fensters, von einem Bereich abgeschnitten, von etwas anderem überdeckt, Text passt nicht ins Feld,
// Kopfzeile überlappt. Für jede Bildschirmgröße ein Ordner mit Bildern und befunde.json.
//   node tools/menue/pruefen.js <Ausgabeordner> [BreitexHöhe ...]        z. B. node tools/menue/pruefen.js pruefung 740x360 852x393 1280x720
//   --ohne-rennen  lässt Pause und Ergebnis weg (spart den Rennstart)
const { spiel } = require('../textur/spiel.js'); const fs = require('fs'); const path = require('path');
function audit() {
  const vw = innerWidth, vh = innerHeight, out = [];
  const layer = ['congrats', 'results', 'hub', 'settings', 'pause'].map(id => document.getElementById(id)).find(e => e && !e.classList.contains('hidden')) || document.getElementById('menu');
  const roots = layer.id === 'menu' ? [layer.querySelector('.scr.on'), layer.querySelector('.mtop'), layer.querySelector('.mfoot')].filter(Boolean) : [layer];
  const shown = e => { if (!e.getClientRects().length) return false; for (let p = e; p && p !== document.body; p = p.parentElement) { const cs = getComputedStyle(p); if (cs.visibility === 'hidden' || +cs.opacity < 0.05) return false; } return true; };
  const name = e => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + ' „' + (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 26) + '“';
  const leafText = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
  for (const root of roots) for (const e of root.querySelectorAll('*')) {
    const tag = e.tagName.toLowerCase(), inter = /^(button|input|select|textarea)$/.test(tag), txt = leafText(e);
    if (!inter && !txt && !/^(canvas|img|output)$/.test(tag)) continue; if (!shown(e)) continue;
    const r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    let clip = null, scroll = false;
    for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) { const cs = getComputedStyle(p), ov = cs.overflowX + ' ' + cs.overflowY; if (!/(hidden|auto|scroll|clip)/.test(ov)) continue;
      const q = p.getBoundingClientRect(); if (r.right > q.right + 1.5 || r.bottom > q.bottom + 1.5 || r.left < q.left - 1.5 || r.top < q.top - 1.5) { clip = p; scroll = /(auto|scroll)/.test(ov) && (p.scrollHeight > p.clientHeight + 1 || p.scrollWidth > p.clientWidth + 1); break; } }
    if (clip) out.push({ k: scroll ? 'scrollen' : 'abgeschnitten', e: name(e), wo: name(clip).split(' „')[0] });
    else if (r.left < -1 || r.top < -1 || r.right > vw + 1 || r.bottom > vh + 1) out.push({ k: 'außerhalb', e: name(e) });
    if (txt && e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible') out.push({ k: 'Text gekürzt', e: name(e) });
    if (!clip) { const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2; if (cx >= 0 && cy >= 0 && cx < vw && cy < vh) { const top = document.elementFromPoint(cx, cy); if (top && top !== e && !e.contains(top) && !top.contains(e) && layer.contains(top)) out.push({ k: 'überdeckt', e: name(e), von: name(top) }); } }
  }
  const head = layer.id === 'menu' && layer.querySelector('.mtop'); if (head) { const ch = [...head.children].filter(shown).map(e => [e, e.getBoundingClientRect()]);
    for (let i = 0; i < ch.length; i++) for (let j = i + 1; j < ch.length; j++) { const a = ch[i][1], b = ch[j][1]; if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1) out.push({ k: 'Kopfzeile überlappt', e: name(ch[i][0]), von: name(ch[j][0]) }); } }
  return out;
}
(async () => {
  const a = process.argv.slice(2), norace = a.includes('--ohne-rennen'); if (norace) a.splice(a.indexOf('--ohne-rennen'), 1);
  const out = a.shift() || 'menue-pruefung', sizes = (a.length ? a : ['740x360', '852x393', '1280x720']).map(x => x.split('x').map(Number));
  for (const [w, h] of sizes) { const dir = path.join(out, w + 'x' + h); fs.mkdirSync(dir, { recursive: true }); const F = {}; let nr = 0;
    const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
    await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
    await ev(`window.__noPre = true; window.__noWarm = true; S.track = 'spa'; S.driver = 'RUS'; S.laps = 5; S.grid = 10; S.wx = 'light'; S.sound = false; S.music = false; 1`);
    const W = ms => p.waitForTimeout(ms), scr = () => p.evaluate(() => document.querySelector('#menu').dataset.scr), click = s => p.evaluate(s => { const e = document.querySelector(s); if (e) e.click(); return !!e; }, s);
    const shot = async name => { await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none')); await W(450);
      const f = String(++nr).padStart(2, '0') + '_' + name; await p.screenshot({ path: path.join(dir, f + '.png') }); F[f] = await p.evaluate(audit); };
    const until = async (want, step) => { for (let k = 0; k < 10; k++) { const s = await scr(); if (s === want) return true; await step(s); await W(1400);
      await p.waitForFunction(() => !document.querySelector('#loading') || document.querySelector('#loading').classList.contains('hidden'), null, { timeout: 600000 }).catch(() => {}); } return false; };
    // Schnelles Spiel
    await shot('titel'); await click('#qPlay'); await W(900); await shot('klasse');
    await click('#mNext'); await W(1500); await shot('team'); if (await click('#teamSeg button:nth-child(2)')) { await W(2500); await shot('team_legenden'); await click('#teamSeg button:nth-child(1)'); await W(1500); }
    await click('#mNext'); await W(1500); await shot('fahrer'); await click('#mNext'); await W(1500); await shot('strecke');
    await until('race', () => click('#mNext'));
    for (const t of ['race', 'wx', 'ai', 'help']) { await click('#rxNav [data-rx="' + t + '"]'); await shot('rennen_' + t); }
    // Einstellungen (aus dem Menü)
    await click('#mGear'); await W(500); for (const t of ['sAudio', 'sGfx', 'sCtl', 'sExtra']) { await click('#settings .ptabs [data-tab="' + t + '"]'); await shot('einstellungen_' + t); } await click('#closeSettings'); await W(400);
    // Zeitrennen
    await ev(`showScreen('title'); 1`); await W(600); await click('#tPlay'); await W(900); await until('race', () => click('#mNext')); await click('#rxNav [data-rx="race"]'); await shot('zeitrennen');
    // Rennen: Pause und Ergebnis
    if (!norace) { await ev(`showScreen('title'); 1`); await W(500); await ev(`window.__wxForce = 'dry'; 1`); const ok = await p.evaluate(() => window.__race('Spa')); await W(500);
      if (ok) { await ev(`raceState = 'race'; SG.go = true; pause(); 1`); await W(500); for (const t of ['pRace', 'pAudio', 'pGfx', 'pCtl']) { await click('#pause .ptabs [data-tab="' + t + '"]'); await shot('pause_' + t); }
        await ev(`resume(); for (const c of cars) { c.lapsDone = S.laps; c.finished = true; c.finishTime = 300 + Math.random() * 20; c.best = 60 + Math.random(); } showResults(); 1`); await W(700); await shot('ergebnis'); await ev(`toMenu(); window.__wxForce = null; 1`); await W(700); } }
    // Karriere
    await ev(`showScreen('title'); 1`); await W(600); await click('#cPlay'); await W(900); await shot('karriere_start_' + await scr());
    await until('season', async s => { if (s === 'name') await p.evaluate(() => { const i = document.querySelector('#cName'); i.value = 'Robert'; i.dispatchEvent(new Event('input', { bubbles: true })); }); if (s === 'career') await click('#carCards .tcard, #carCards button'); else await click('#mNext'); if (s !== 'name') return; });
    for (const t of ['race', 'table', 'cal', 'up']) if (await click('#seTabs [data-t="' + t + '"]')) await shot('saison_' + t);
    await ev(`showScreen('career'); 1`); await W(700); await shot('karriere_klassen');
    fs.writeFileSync(path.join(dir, 'befunde.json'), JSON.stringify(F, null, 1));
    const n = Object.values(F).reduce((s, x) => s + x.length, 0); console.log(w + 'x' + h + ': ' + nr + ' Bildschirme, ' + n + ' Befunde');
    for (const [k, v] of Object.entries(F)) { const g = {}; for (const x of v) { const key = x.k + (x.wo ? ' in ' + x.wo : '') + (x.von ? ' von ' + x.von.split(' „')[0] : ''); (g[key] = g[key] || []).push(x.e.split(' „')[1] ? '„' + x.e.split(' „')[1] : x.e); }
      for (const [key, list] of Object.entries(g)) console.log('  ' + k + ': ' + key + ' ×' + list.length + ' ' + list.slice(0, 4).join(' ')); }
    await b.close(); }
})().catch(e => { console.error(e); process.exit(1); });
