// Entwürfe nur für den Umschalter Saison/Legenden (Rest = v2.92). Mockup per CSS/DOM-Einspritzung.
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js');
const CSS = `
#scrTeam .tmtabs{display:none!important}
.um-seg{position:fixed;z-index:50;display:flex;padding:3px;border-radius:12px;background:rgba(10,12,18,.72);border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}
.um-seg b{min-width:112px;height:38px;display:flex;align-items:center;justify-content:center;gap:7px;border-radius:9px;font:800 12px/1 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.6)}
.um-seg b.on{background:#fff;color:#0b0d12;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.um-seg b.on.gold{background:linear-gradient(180deg,#f1d68e,#c99a3e);color:#2a1d07}
.um-seg b i{font-style:normal;font-size:11px;opacity:.75}
.um-tabs{position:fixed;z-index:50;display:flex;gap:4px}
.um-tabs b{height:36px;padding:0 18px;display:flex;align-items:center;gap:7px;border-radius:10px 10px 0 0;font:800 12px/1 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.55);background:rgba(10,12,18,.55);border:1px solid rgba(255,255,255,.1);border-bottom:0}
.um-tabs b.on{color:#fff;background:rgba(10,12,18,.85);box-shadow:inset 0 3px 0 #e10600}
.um-tabs b.on.gold{color:#ecd394;box-shadow:inset 0 3px 0 #ecd394}
.um-tabs b i{font-style:normal;font-size:11px;opacity:.8}
.um-lbl{position:fixed;left:50%;top:4px;transform:translateX(-50%);z-index:99999;white-space:nowrap;font:900 10px/1 system-ui;background:#e10600;color:#fff;padding:5px 9px;border-radius:5px}
`;
async function mock(p, v, leg) {
  await p.evaluate(([v, leg]) => {
    document.querySelectorAll('.um-seg,.um-tabs,.um-lbl').forEach(e => e.remove());
    const add = h => { const d = document.createElement('div'); d.innerHTML = h; const e = d.firstElementChild; document.body.appendChild(e); return e; };
    add('<div class="um-lbl">' + (v === 'A' ? 'ENTWURF 1 · Segment oben' : 'ENTWURF 2 · Reiter direkt über der Leiste') + (leg ? ' · Legenden' : ' · Saison') + '</div>');
    const tw = document.querySelector('#teams'), R = [...tw.querySelectorAll('.tm')].reduce((a, e) => { const r = e.getBoundingClientRect(); return { l: Math.min(a.l, r.left), t: Math.min(a.t, r.top) }; }, { l: 1e9, t: 1e9 });
    if (v === 'A') { const s = add('<div class="um-seg"><b class="' + (leg ? '' : 'on') + '">Saison <i>2026</i></b><b class="' + (leg ? 'on gold' : '') + '">★ Legenden</b></div>'); s.style.left = '50%'; s.style.transform = 'translateX(-50%)'; s.style.top = 'calc(56px + env(safe-area-inset-top))'; }
    else { const s = add('<div class="um-tabs"><b class="' + (leg ? '' : 'on') + '">Saison <i>2026</i></b><b class="' + (leg ? 'on gold' : '') + '">★ Legenden</b></div>'); s.style.left = Math.max(10, R.l) + 'px'; s.style.top = (R.t - 36 - 6) + 'px'; }
  }, [v, leg]);
  await p.waitForTimeout(300);
}
(async () => { for (const [w, h, n] of [[667, 375, 'iphone_se'], [852, 393, 'iphone_15']]) { const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await ev(`window.__noPre = true; S.driver = 'RUS'; MENU.team = 'MER'; save(); 1`);
  await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); for (let k = 0; k < 4 && q('#menu').dataset.scr !== 'team'; k++) { q('#mNext').click(); await new Promise(r => setTimeout(r, 800)); } });
  await p.addStyleTag({ content: CSS });
  const hide = () => p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
  await p.waitForTimeout(4000); await hide();
  for (const v of ['A', 'B']) { await mock(p, v, 0); await p.screenshot({ path: `phone/um_${v}0_${n}.png` }); }
  await ev(`MENU.team = 'H_F67'; MENU.leg = true; showroomTeam('H_F67'); renderTeams(); renderMenu(); 1`); await p.waitForTimeout(7000); await hide();
  for (const v of ['A', 'B']) { await mock(p, v, 1); await p.screenshot({ path: `phone/um_${v}1_${n}.png` }); }
  await b.close(); } })();
