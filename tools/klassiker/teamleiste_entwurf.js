// Entwürfe Teamleiste/Legenden (nur Mockup, per DOM-Einspritzung im echten Spiel)
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js');
const CSS = `
#teamInfo,.qcbot,#qcBot{}
.mk-seg{position:absolute;left:50%;transform:translateX(-50%);display:flex;gap:2px;padding:3px;border-radius:999px;background:rgba(8,10,16,.62);border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(12px);z-index:5}
.mk-seg b{font:800 10.5px/1 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.55);padding:7px 14px;border-radius:999px;display:flex;gap:7px;align-items:center;white-space:nowrap}
.mk-seg b.on{background:#fff;color:#0b0d12}
.mk-seg b.leg.on{background:linear-gradient(180deg,#f1d68e,#c99a3e);color:#2a1d07}
.mk-seg b em{font-style:normal;font-size:9px;padding:2px 5px;border-radius:6px;background:rgba(217,180,90,.25);color:#ecd394;letter-spacing:.04em}
.mk-seg b.leg.on em{background:rgba(42,29,7,.18);color:#2a1d07}
.mk-row{display:flex;gap:6px;justify-content:center;align-items:flex-end}
.mk-card{position:relative;flex:none;width:min(calc(var(--tw)*2.55),calc((100vw - 180px) / 6 - 6px));height:var(--tw);border-radius:10px;overflow:hidden;background:linear-gradient(180deg,rgba(92,74,44,.80),rgba(30,24,15,.9));border:1px solid rgba(217,180,90,.45);display:grid;display:block;padding:clamp(5px,1.4vh,9px) 8px 0 9px;align-items:center;color:#fff;box-sizing:border-box}
.mk-card svg{position:absolute;right:5px;top:5px;width:calc(var(--tw)*.36)!important;height:calc(var(--tw)*.36)!important;opacity:.95}
.mk-card .y{font:900 clamp(13px,3.1vh,20px)/1 system-ui,sans-serif;color:#ecd394;letter-spacing:.02em}
.mk-card .n{font:800 clamp(8px,1.9vh,11px)/1.15 system-ui,sans-serif;color:rgba(255,255,255,.78);text-transform:uppercase;letter-spacing:.06em;margin-top:3px}
.mk-card .d{font:600 clamp(7.5px,1.7vh,10px)/1.15 system-ui,sans-serif;color:#ecd394;margin-top:2px;white-space:nowrap}.mk-card .n{white-space:nowrap}.mk-card>div{min-width:0;overflow:hidden}.mk-card.on{outline:2px solid #ecd394;outline-offset:-2px;box-shadow:inset 0 -3px 0 #ecd394}
.mk-line{position:absolute;left:8%;right:8%;height:1px;background:linear-gradient(90deg,transparent,rgba(217,180,90,.6),transparent)}
.mk-tile{flex:none;width:calc(var(--tw)*1.35);height:var(--tw);border-radius:10px;box-sizing:border-box;display:grid;place-items:center;align-content:center;gap:3px;background:linear-gradient(160deg,#e9c97a,#a87a2c);color:#2a1d07;border:1px solid #f4dea0;font:900 clamp(8px,1.7vh,10.5px)/1 system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;box-shadow:0 0 0 1px rgba(0,0,0,.3),0 6px 18px rgba(217,160,60,.28)}
.mk-tile i{font-style:normal;font-size:clamp(14px,3.2vh,20px);letter-spacing:0}
.mk-tile.back{background:rgba(9,12,18,.62);color:#fff;border:1px solid rgba(255,255,255,.22);box-shadow:none}
.mk-tabs{flex:none;display:flex;flex-direction:column;height:var(--tw);box-sizing:border-box;border-radius:8px;overflow:hidden;background:rgba(14,16,22,.78);border:1px solid rgba(255,255,255,.14);margin-right:8px}
.mk-tabs b{flex:1;display:flex;align-items:center;gap:6px;padding:0 12px 0 10px;font:800 clamp(8px,1.8vh,10.5px)/1 system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.45);position:relative;white-space:nowrap}
.mk-tabs b+b{border-top:1px solid rgba(255,255,255,.1)}
.mk-tabs b i{font-style:normal;color:#e10600;opacity:.6;font-weight:900}
.mk-tabs b.on{color:#fff;background:linear-gradient(90deg,rgba(225,6,0,.22),rgba(225,6,0,0))}
.mk-tabs b.on::before{content:'';position:absolute;left:0;top:18%;bottom:18%;width:3px;background:#e10600;border-radius:2px}
.mk-tabs b.on i{opacity:1}
.mk-lbl{position:fixed;left:50%;top:6px;transform:translateX(-50%);z-index:99999;white-space:nowrap;font:900 11px/1 system-ui,sans-serif;background:#e10600;color:#fff;padding:7px 12px;border-radius:6px;letter-spacing:.06em}
`;
async function prep(p) {
  await p.evaluate(css => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
    document.querySelectorAll('[id*=qc i],[class*=qc i]').forEach(e => { if (e.textContent.includes('QC')) e.style.display = 'none'; });
    [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot')).forEach(d => d.style.display = 'none'); }, CSS);
}
async function variant(p, v, legMode) {
  await p.evaluate(([v, legMode]) => {
    const tw = document.querySelector('#teams'); const now = [...tw.querySelectorAll('.tmnow .tm')], old = [...tw.querySelectorAll('.tm.hist')];
    if (!tw.dataset.orig) tw.dataset.orig = tw.innerHTML; tw.innerHTML = tw.dataset.orig; document.querySelectorAll('.mk-seg,.mk-lbl,.mk-line').forEach(e => e.remove());
    const N = [...tw.querySelectorAll('.tmnow .tm')].map(e => e.outerHTML), O = [...tw.querySelectorAll('.tm.hist')];
    const DR = { H_F67: 'C. Amon', H_LOT: 'J. Rindt', H_MCL: 'A. Senna', H_MCL98: 'M. Häkkinen', H_FER: 'M. Schumacher', H_RBR: 'S. Vettel' };
    const card = (e, i) => { const k = e.dataset.team, y = e.querySelector('.hy').textContent, nm = e.title.split(' · ')[1].replace(' (Legende)', ''); return '<div class="mk-card' + (i === 2 ? ' on' : '') + '">' + e.querySelector('svg').outerHTML + '<div><div class="y">' + y + '</div><div class="n">' + nm + '<br>' + (DR[k] || '') + '</div></div></div>'; };
    tw.classList.remove('hasLeg'); tw.style.justifyContent = 'center'; tw.style.overflow = 'visible';
    let html;
    if (v === 'A') html = '<span class="mk-row">' + (legMode ? O.map(card).join('') : N.join('')) + '</span>';
    else if (v === 'C') html = '<span class="mk-row"><div class="mk-tabs"><b class="' + (legMode ? '' : 'on') + '"><i>2026</i>Saison</b><b class="' + (legMode ? 'on' : '') + '"><i>★</i>Legenden</b></div>' + (legMode ? O.map(card).join('') : N.join('')) + '</span>';
    else html = '<span class="mk-row">' + (legMode ? '<div class="mk-tile back"><i>‹</i>2026</div>' + O.map(card).join('') : N.join('') + '<div class="mk-tile"><i>★</i>Legenden</div>') + '</span>';
    tw.innerHTML = html;
    if (legMode) tw.querySelectorAll('.tm.on').forEach(e => e.classList.remove('on'));
    const r = tw.getBoundingClientRect();
    if (v === 'A') { const s = document.createElement('div'); s.className = 'mk-seg'; s.innerHTML = '<b class="' + (legMode ? '' : 'on') + '">Saison 2026</b><b class="leg' + (legMode ? ' on' : '') + '">★ Legenden <em>6</em></b>'; document.body.appendChild(s); s.style.top = (r.top - s.offsetHeight - 7) + 'px'; }
    const l = document.createElement('div'); l.className = 'mk-lbl'; l.textContent = ({A:'ENTWURF A · Umschalter oben',B:'ENTWURF B · Legenden-Kachel',C:'ENTWURF C · Umschalter in der Leiste'})[v] + (legMode ? ' – Legenden geöffnet' : ' – Start'); document.body.appendChild(l);
  }, [v, legMode]);
  await p.waitForTimeout(400);
}
(async () => { for (const [w, h] of [[1280, 640], [844, 390]]) { const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await ev(`window.__noPre = true; S.driver = 'RUS'; MENU.team = 'MER'; save(); 1`);
  await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); for (let k = 0; k < 4 && q('#menu').dataset.scr !== 'team'; k++) { q('#mNext').click(); await new Promise(r => setTimeout(r, 800)); } });
  await p.waitForTimeout(5000); await prep(p);
  for (const lm of [0, 1]) { if (lm) { await ev(`delete document.querySelector('#teams').dataset.orig; MENU.team = 'H_MCL'; showroomTeam('H_MCL'); renderMenu(); renderTeams(); 1`); await p.waitForTimeout(6000); await prep(p); } for (const v of ['C', 'B']) { await variant(p, v, lm); await p.screenshot({ path: `mk_${v}${lm}_${w}.png` }); } }
  await b.close(); } })();
