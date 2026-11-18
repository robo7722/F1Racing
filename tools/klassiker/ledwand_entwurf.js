// Entwürfe LED-Wand für Legenden (nur Mockup: ersetzt wallDraw im laufenden Spiel)
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js');
const DRAW = String.raw`
window.__wv = window.__wv || 'L1';
const _orig = window.__wallOrig || (window.__wallOrig = wallDraw);
wallDraw = function (now) { const W = SHOW.wall, H = HIST_CAR[SHOW.team]; if (!W || !H) return _orig(now);
  const g = W.cv.getContext('2d'), w = W.cv.width, h = W.cv.height, F = '"Titillium Web",system-ui,sans-serif', T = TEAMS[SHOW.team], d = ALL.find(c => c.team === SHOW.team), nm = d.name.split(' '), dn = (nm[0][0] + '. ' + nm.slice(1).join(' ')).toUpperCase();
  const c1 = hex(uiCol(T)), c2 = hex(T.acc ?? uiCol(T)), yr = String(H.year), car = H.title.toUpperCase();
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.textBaseline = 'alphabetic';
  if (window.__wv === 'L1') {   // Archiv: warmes Sepia, Jahr als riesige Konturzahl, Filmstreifen oben und unten, Korn
    { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#0b0805'); gr.addColorStop(.6, '#1d150c'); gr.addColorStop(1, '#2a1e10'); g.fillStyle = gr; g.fillRect(0, 0, w, h); }
    const sk = h * .42; for (const [a, b, al, col] of [[.30, .50, .55, c1], [.515, .53, .7, '#d9b45a'], [.64, .86, .22, c2]]) { g.globalAlpha = al; g.fillStyle = col; g.beginPath(); g.moveTo(a * w + sk, 0); g.lineTo(b * w + sk, 0); g.lineTo(b * w, h); g.lineTo(a * w, h); g.fill(); }
    g.globalAlpha = 1; g.globalCompositeOperation = 'color'; g.fillStyle = '#b08a4a'; g.globalAlpha = .55; g.fillRect(0, 0, w, h); g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;   // Farben in Richtung Sepia
    { const gr = g.createLinearGradient(0, 0, 0, h * .5); gr.addColorStop(0, 'rgba(8,6,4,.95)'); gr.addColorStop(1, 'rgba(8,6,4,0)'); g.fillStyle = gr; g.fillRect(0, 0, w, h * .5); }
    const cx = 630; let fs = 64; g.font = '900 ' + fs + 'px ' + F; const yw = g.measureText(yr).width; g.lineWidth = 2; g.strokeStyle = 'rgba(236,211,148,.95)'; g.fillStyle = 'rgba(236,211,148,.2)'; g.fillText(yr, cx - yw / 2, 306); g.strokeText(yr, cx - yw / 2, 306);
    fs = 13; g.font = '800 ' + fs + 'px ' + F; g.fillStyle = '#ecd394'; g.textAlign = 'right'; g.fillText(car, cx - yw / 2 - 14, 300); g.textAlign = 'left'; g.fillText(dn, cx + yw / 2 + 14, 300); g.textAlign = 'left';
    g.fillStyle = 'rgba(236,211,148,.6)'; g.fillRect(cx - yw / 2 - 14 - g.measureText(car).width, 304, g.measureText(car).width, 1.5); g.fillRect(cx + yw / 2 + 14, 304, g.measureText(dn).width, 1.5);
    g.fillStyle = '#050403'; g.fillRect(0, 226, w, 12); g.fillStyle = 'rgba(236,211,148,.4)'; for (let x = 4; x < w; x += 10) g.fillRect(x, 229, 5, 6);   // Filmlochung
    const im = g.getImageData(0, 0, w, h), D = im.data; for (let i = 0; i < D.length; i += 4) { const n = (Math.random() - .5) * 26; D[i] += n; D[i + 1] += n; D[i + 2] += n; } g.putImageData(im, 0, 0);
  } else {   // Fallblatt-Tafel: schwarze Klappziffern wie alte Zeitnahme-Tafeln, Teamfarbe als Band links
    g.fillStyle = '#08090b'; g.fillRect(0, 0, w, h);
    const rows = [['LEGENDE', '#ecd394'], [yr, '#ffffff'], [car, '#ffffff'], [dn, '#f5d000']], cw = 12, ch = 16, gap = 2, cols = 15, x0 = 630 - cols * (cw + gap) / 2, y0 = 238;
    g.fillStyle = c1; g.fillRect(x0 - 14, y0, 6, rows.length * (ch + 3) - 3); g.fillStyle = c2; g.fillRect(x0 - 6, y0, 2, rows.length * (ch + 3) - 3);
    rows.forEach(([txt, col], r) => { const y = y0 + r * (ch + 3), start = Math.floor((cols - txt.length) / 2);
      for (let c = 0; c < cols; c++) { const x = x0 + c * (cw + gap); g.fillStyle = '#16181c'; g.fillRect(x, y, cw, ch); g.fillStyle = '#000'; g.fillRect(x, y + ch / 2 - .5, cw, 1);
        const k = c - start, chr = k >= 0 && k < txt.length ? txt[k] : ''; const t = now - (W.t0 || 0) - (r * 0.25 + c * 0.03); const settled = window.__wSettled || t > 0.6;
        const show = settled ? chr : (chr ? 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'[Math.floor(Math.random() * 36)] : '');
        if (show) { g.font = '800 ' + (ch * .78) + 'px ' + F; g.fillStyle = col; const tw = g.measureText(show).width; g.fillText(show, x + cw / 2 - tw / 2, y + ch * .8); } } });
  }
  W.tx.needsUpdate = true; };
1`;
(async () => { for (const [w, h] of [[1280, 640]]) { const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await ev(`window.__noPre = true; S.driver = 'SEN'; MENU.team = 'H_MCL'; save(); 1`);
  await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); for (let k = 0; k < 4 && q('#menu').dataset.scr !== 'team'; k++) { q('#mNext').click(); await new Promise(r => setTimeout(r, 800)); } });
  await p.waitForTimeout(7000); await p.screenshot({ path: 'w_jetzt.png' });
  await ev(DRAW);
  for (const v of ['L1', 'L2']) { await ev(`window.__wv = '${v}'; window.__wSettled = true; 1`); await p.waitForTimeout(1500); await p.screenshot({ path: `w_${v}.png` }); }
  await ev(`MENU.team = 'H_F67'; showroomTeam('H_F67'); renderMenu(); 1`); await p.waitForTimeout(6000);
  for (const v of ['L1', 'L2']) { await ev(`window.__wv = '${v}'; window.__wSettled = true; 1`); await p.waitForTimeout(1500); await p.screenshot({ path: `w_${v}_f67.png` }); }
  await b.close(); } })();
