// Storyboard-Blätter und Animatic-Einzelbilder aus tools/trailer/storyboard.json erzeugen.
//   node tools/trailer/storyboard.js blatt <Ausgabeordner>            → trailer_storyboard_1.jpg … (Blätter zum Ansehen, 1200 px breit)
//   node tools/trailer/storyboard.js bilder <Ausgabeordner>           → szene_NN.png (1280×536, mit Schrift) + leiste_NN.png (1280×92) + titel.png für das Animatic
// Bilder: docs/bilder/trailer/, Musikverlauf: tools/trailer/musik_verlauf.json (aus musik_schnitt.py --json), Schrift: Titillium Web (wie im Spiel).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const ROOT = path.resolve(__dirname, '../..'), BILD = path.join(ROOT, 'docs/bilder/trailer');
const SB = JSON.parse(fs.readFileSync(path.join(__dirname, 'storyboard.json'), 'utf8')), VL = JSON.parse(fs.readFileSync(path.join(__dirname, 'musik_verlauf.json'), 'utf8'));
const b64 = f => fs.readFileSync(f).toString('base64'), img = n => 'data:image/jpeg;base64,' + b64(path.join(BILD, n));
const font = (w, st = 'normal') => `@font-face{font-family:"Titillium Web";font-weight:${w};font-style:${st};src:url(data:font/woff2;base64,${b64(path.join(__dirname, 'schrift', `titillium-web-latin-${w}-${st}.woff2`))}) format("woff2")}`;
const zeit = s => { const m = Math.floor(s / 60), r = s - m * 60; return m + ':' + (r < 10 ? '0' : '') + (Math.abs(r - Math.round(r)) < 0.04 ? Math.round(r).toFixed(0) : r.toFixed(1)).replace('.', ','); };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const ROT = '#e10600';
const CSS = `${font(400)}${font(600)}${font(700)}${font(900)}${font(700, 'italic')}
*{box-sizing:border-box;margin:0;padding:0}body{background:#0b0b0f;color:#e9e9ee;font-family:"Titillium Web",sans-serif;-webkit-font-smoothing:antialiased}
.seite{width:1200px;padding:44px 40px 48px;background:#0b0b0f}
h1{font-weight:900;font-size:46px;letter-spacing:.02em;line-height:1}h1 i{color:${ROT};font-style:normal}
.sub{margin-top:10px;font-size:21px;color:#9a9aa6;font-weight:600;letter-spacing:.04em}
.fakt{margin-top:18px;font-size:22px;line-height:1.45;color:#cfcfd8}.fakt b{color:#fff}
.tl{margin:26px 0 8px}.tl svg{display:block;width:100%}
.sz{margin-top:34px}.kopf{display:flex;align-items:baseline;gap:16px;margin-bottom:10px}
.nr{font-weight:900;font-size:40px;color:${ROT};line-height:1;min-width:54px}.tt{font-weight:900;font-size:34px;letter-spacing:.01em;text-transform:uppercase;line-height:1}
.tc{margin-left:auto;font-weight:700;font-size:24px;color:#9a9aa6;white-space:nowrap}.tc b{color:#fff}
.rahmen{position:relative;width:1120px;height:469px;background:#000;overflow:hidden;border:1px solid #26262e}
.rahmen img{width:100%;height:100%;display:block;object-fit:cover}
.ov{position:absolute;left:5.2%;bottom:9%;display:flex;align-items:center;gap:1.1em;font-weight:700;font-style:italic;letter-spacing:.16em;color:#fff;text-shadow:0 2px 14px rgba(0,0,0,.75)}
.ov:before{content:"";width:.34em;height:1.5em;background:${ROT};transform:skewX(-14deg)}
.was{margin-top:12px;font-size:25px;line-height:1.38;color:#f0f0f4}
.zeile{margin-top:7px;font-size:21px;color:#9a9aa6;line-height:1.35}.zeile b{color:#c9c9d4;font-weight:700}
.akt{margin-top:46px;padding:10px 0 8px;border-top:3px solid ${ROT};font-weight:900;font-size:26px;letter-spacing:.2em;color:#fff;display:flex}.akt span{margin-left:auto;color:#9a9aa6;letter-spacing:.06em;font-weight:700}
.titel{width:100%;height:100%;background:radial-gradient(ellipse at 50% 60%,#16161d 0%,#000 70%);display:flex;flex-direction:column;align-items:center;justify-content:center}
.titel .w{font-weight:900;font-style:normal;letter-spacing:.09em;color:#fff;line-height:1}.titel .l{height:.07em;width:7.2em;background:${ROT};margin:.32em 0 .3em;transform:skewX(-20deg)}
.titel .u{font-weight:600;letter-spacing:.42em;color:#b9b9c4}
.cuts{position:absolute;right:14px;top:12px;background:rgba(0,0,0,.72);border:1px solid #3a3a44;padding:4px 12px;font-weight:700;font-size:19px;letter-spacing:.06em;color:#fff}`;
const titelKarte = fs => `<div class="titel" style="font-size:${fs}px"><div class="w">FORMULA RACING</div><div class="l"></div><div class="u" style="font-size:.2em">VOM KART BIS IN DIE FORMEL 1</div></div>`;
const rahmen = (s, w, ovSize, mitCuts = true) => `<div class="rahmen" style="width:${w}px;height:${Math.round(w * 536 / 1280)}px">${s.bild === '@titel' ? titelKarte(w * 0.075) : `<img src="${img(s.bild)}">`}${s.text ? `<div class="ov" style="font-size:${ovSize}px">${esc(s.text)}</div>` : ''}${mitCuts && s.schnitte ? `<div class="cuts">${s.schnitte} SCHNITTE IM TAKT</div>` : ''}</div>`;

function zeitleiste() {   // Lautheitsverlauf der geschnittenen Musik mit Akten und Szenenmarken
  const W = 1120, H = 190, top = 34, bot = 150, D = SB.laenge, x = t => t / D * W, db = VL.db, y = v => bot - Math.max(0, Math.min(1, (v + 42) / 40)) * (bot - top);
  let p = `M0,${bot}`; for (let i = 0; i < db.length; i += 2) p += `L${x(i / 10).toFixed(1)},${y(db[i]).toFixed(1)}`; p += `L${W},${bot}Z`;
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" font-family="Titillium Web">`;
  SB.akte.forEach((a, k) => { s += `<rect x="${x(a.von)}" y="${top - 30}" width="${x(a.bis) - x(a.von) - 2}" height="24" fill="${k % 2 ? '#1c1c24' : '#24242e'}"/><text x="${(x(a.von) + x(a.bis)) / 2}" y="${top - 12}" fill="#fff" font-size="15" font-weight="900" letter-spacing="2" text-anchor="middle">${a.name}</text>`; });
  s += `<path d="${p}" fill="${ROT}" opacity=".85"/>`;
  SB.szenen.forEach(z => { s += `<line x1="${x(z.von)}" y1="${top}" x2="${x(z.von)}" y2="${bot + 6}" stroke="#fff" stroke-width="1" opacity=".55"/><text x="${(x(z.von) + x(z.bis)) / 2}" y="${bot + 20}" fill="#cfcfd8" font-size="14" font-weight="700" text-anchor="middle">${z.nr}</text>`; });
  for (let t = 0; t <= D; t += 10) s += `<text x="${x(t)}" y="${H - 2}" fill="#77778a" font-size="13" font-weight="600" text-anchor="${t ? 'middle' : 'start'}">${zeit(t)}</text>`;
  return s + '</svg>';
}
const szene = s => `<div class="sz"><div class="kopf"><div class="nr">${String(s.nr).padStart(2, '0')}</div><div class="tt">${esc(s.titel)}</div><div class="tc"><b>${zeit(s.von)} – ${zeit(s.bis)}</b> · ${(s.bis - s.von).toFixed(1).replace('.', ',')} s</div></div>${rahmen(s, 1120, 30)}
<div class="was">${esc(s.was)}</div><div class="zeile"><b>Kamera:</b> ${esc(s.kamera)} &nbsp;·&nbsp; <b>Musik:</b> ${esc(s.musik)}${s.ton ? ` &nbsp;·&nbsp; <b>Ton:</b> ${esc(s.ton)}` : ''}</div></div>`;

(async () => {
  const [modus = 'blatt', out = '.'] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1 });
  if (modus === 'blatt') {
    const teile = [[1, 7], [8, 13], [14, 19]];
    for (let k = 0; k < teile.length; k++) { const [a, e] = teile[k]; let h = `<style>${CSS}</style><div class="seite" id="s">`;
      if (k === 0) h += `<h1>FORMULA RACING <i>–</i> TRAILER</h1><div class="sub">${esc(SB.stand)}</div><div class="fakt"><b>Länge</b> ${zeit(Math.round(SB.laenge))} &nbsp;·&nbsp; <b>Format</b> ${esc(SB.format)}<br><b>Musik</b> ${esc(SB.musik)}</div><div class="tl">${zeitleiste()}</div><div class="zeile">Rote Fläche: Lautstärke der Musik über die Trailerzeit. Weiße Striche: Schnitte, Zahlen: Szenen.</div>`;
      else h += `<div class="sub">FORMULA RACING – TRAILER · Storyboard · Blatt ${k + 1} von ${teile.length}</div>`;
      for (const s of SB.szenen.filter(s => s.nr >= a && s.nr <= e)) { const akt = SB.akte.find(q => Math.abs(q.von - s.von) < 0.01); if (akt) h += `<div class="akt">${akt.name}<span>${zeit(akt.von)} – ${zeit(akt.bis)}</span></div>`; h += szene(s); }
      await p.setContent(h + '</div>'); await p.evaluate(() => document.fonts.ready); const f = path.join(out, `trailer_storyboard_${k + 1}.jpg`); await (await p.$('#s')).screenshot({ path: f, type: 'jpeg', quality: 88 }); console.log(f); }
  } else {
    for (const s of SB.szenen) { const n = String(s.nr).padStart(2, '0');
      await p.setContent(`<style>${CSS}.rahmen{border:0}</style><div id="s" style="width:1280px">${rahmen(s, 1280, 34, false)}</div>`); await p.evaluate(() => document.fonts.ready); await (await p.$('#s')).screenshot({ path: path.join(out, `szene_${n}.png`) });
      if (s.text && s.schnitte) { await p.setContent(`<style>${CSS}.rahmen{border:0}</style><div id="s" style="width:1280px">${rahmen({ ...s, text: '' }, 1280, 34, false)}</div>`); await (await p.$('#s')).screenshot({ path: path.join(out, `szene_${n}_o.png`) }); }   // ohne Schrift für die Sprungschnitte
      await p.setContent(`<style>${CSS}</style><div id="s" style="width:1280px;height:92px;background:#000;display:flex;align-items:center;gap:18px;padding:0 28px"><div class="nr" style="font-size:34px;min-width:0">${n}</div><div class="tt" style="font-size:27px">${esc(s.titel)}</div>${s.schnitte ? `<div style="font-weight:700;font-size:19px;color:#9a9aa6;letter-spacing:.06em">${s.schnitte} SCHNITTE IM TAKT</div>` : ''}<div class="tc" style="font-size:22px"><b>${zeit(s.von)} – ${zeit(s.bis)}</b> · STORYBOARD-VORSCHAU</div></div>`); await p.evaluate(() => document.fonts.ready); await (await p.$('#s')).screenshot({ path: path.join(out, `leiste_${n}.png`) }); }
    console.log('Animatic-Bilder in', out);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
