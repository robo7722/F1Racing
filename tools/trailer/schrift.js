// Schriften und Schlusstafel für den Trailer als PNG erzeugen (durchsichtiger Hintergrund, Schrift des Spiels: Titillium Web).
//   node tools/trailer/schrift.js <Ausgabeordner>     → text_<name>.png (1920 × 804) je Schrift aus schnittplan.json, titel.png (1920 × 1080, mit logos/LOGO.png)
// Das Logo (494 × 124) wird vorher mit scharfen Kanten vergrößert: python3 tools/trailer/logo_gross.py <Ausgabeordner>/logo_gross.png
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const out = process.argv[2] || 'trailer-ausgabe/schrift', PLAN = JSON.parse(fs.readFileSync(path.join(__dirname, 'schnittplan.json'), 'utf8'));
const b64 = f => fs.readFileSync(f).toString('base64');
const font = (w, st = 'normal') => `@font-face{font-family:"Titillium Web";font-weight:${w};font-style:${st};src:url(data:font/woff2;base64,${b64(path.join(__dirname, 'schrift', `titillium-web-latin-${w}-${st}.woff2`))}) format("woff2")}`;
const ROT = '#e10600', esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const CSS = `${font(400)}${font(600)}${font(700)}${font(900)}${font(700, 'italic')}*{box-sizing:border-box;margin:0;padding:0}html,body{background:transparent;font-family:"Titillium Web",sans-serif;-webkit-font-smoothing:antialiased}
.b{position:relative;width:1920px;height:804px;overflow:hidden}
.ov{position:absolute;left:96px;bottom:74px;display:flex;align-items:center;gap:26px;color:#fff;text-shadow:0 3px 22px rgba(0,0,0,.8),0 0 2px rgba(0,0,0,.6)}
.ov .bar{width:15px;height:74px;background:${ROT};transform:skewX(-14deg);box-shadow:0 3px 18px rgba(0,0,0,.5)}
.ov .t{font-weight:700;font-style:italic;font-size:50px;letter-spacing:.17em;line-height:1}
.ov .jahr{font-weight:700;font-style:italic;font-size:104px;letter-spacing:.04em;line-height:.9}
.ov .name{font-weight:600;font-size:30px;letter-spacing:.3em;line-height:1;margin-top:8px;color:#e6e6ec}
.ti{width:1920px;height:1080px;background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(ellipse at 50% 55%,#131318 0%,#000 68%)}
.ti img{width:800px;display:block;filter:drop-shadow(0 0 60px rgba(255,30,0,.28))}
.ti .u{margin-top:54px;font-weight:600;font-size:30px;letter-spacing:.62em;color:#c9c9d2;padding-left:.62em}`;
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(), p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [name, t] of Object.entries(PLAN.schriften)) {
    const inner = t.jahr ? `<div class="bar" style="height:118px"></div><div><div class="jahr">${esc(t.jahr)}</div><div class="name">${esc(t.name)}</div></div>` : `<div class="bar"></div><div class="t">${esc(t.text)}</div>`;
    await p.setContent(`<style>${CSS}</style><div class="b" id="s"><div class="ov">${inner}</div></div>`); await p.evaluate(() => document.fonts.ready);
    await (await p.$('#s')).screenshot({ path: path.join(out, `text_${name}.png`), omitBackground: true });
  }
  const logo = path.join(out, 'logo_gross.png');
  await p.setContent(`<style>${CSS}</style><div class="ti" id="s"><img src="data:image/png;base64,${b64(fs.existsSync(logo) ? logo : path.join(__dirname, '../../logos/LOGO.png'))}"><div class="u">${esc(PLAN.titelzeile || '')}</div></div>`); await p.evaluate(() => document.fonts.ready);
  await (await p.$('#s')).screenshot({ path: path.join(out, 'titel.png') });
  await b.close(); console.log('Schriften in', out);
})().catch(e => { console.error(e); process.exit(1); });
