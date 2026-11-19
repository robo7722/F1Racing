// Entwurf nach Apple HIG / Mobile-Game-Mustern: Umschalter oben (Segment), Auswahl am Auto (Pfeile + Wischen), unten nur ein schlankes Logo-Dock bzw. Punkte
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js');
const CSS = `
.hg-seg{position:fixed;left:50%;transform:translateX(-50%);top:calc(56px + env(safe-area-inset-top));z-index:50;display:flex;padding:3px;border-radius:12px;background:rgba(10,12,18,.72);border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}
.hg-seg b{min-width:112px;height:38px;display:flex;align-items:center;justify-content:center;gap:7px;border-radius:9px;font:800 12px/1 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.6)}
.hg-seg b.on{background:#fff;color:#0b0d12;box-shadow:0 2px 8px rgba(0,0,0,.4)}
.hg-seg b.on.gold{background:linear-gradient(180deg,#f1d68e,#c99a3e);color:#2a1d07}
.hg-seg b i{font-style:normal;font-size:11px;opacity:.75}
.hg-arr{position:fixed;top:47%;transform:translateY(-50%);z-index:50;width:48px;height:48px;border-radius:50%;display:grid;place-items:center;background:rgba(10,12,18,.55);border:1px solid rgba(255,255,255,.22);backdrop-filter:blur(10px);color:#fff;font:300 30px/1 system-ui;padding-bottom:4px;box-sizing:border-box}
.hg-arr.l{left:max(14px,env(safe-area-inset-left))}.hg-arr.r{right:max(14px,env(safe-area-inset-right))}
.hg-name{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(84px + env(safe-area-inset-bottom));z-index:50;text-align:center;color:#fff;white-space:nowrap}
.hg-name b{display:block;font:900 15px/1.1 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase}
.hg-name small{display:block;font:700 10.5px/1.3 system-ui,sans-serif;letter-spacing:.1em;color:rgba(255,255,255,.65);text-transform:uppercase;margin-top:2px}
.hg-name.gold b{color:#ecd394}
.hg-dock{position:fixed;left:max(14px,env(safe-area-inset-left));bottom:calc(14px + env(safe-area-inset-bottom));z-index:50;display:flex;gap:2px;padding:4px;border-radius:14px;background:rgba(10,12,18,.6);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(12px)}
.hg-dock span{width:42px;height:44px;display:grid;place-items:center;border-radius:10px;opacity:.55}
.hg-dock span svg{width:26px!important;height:26px!important;filter:brightness(1.4)}
.hg-dock span.on{opacity:1;background:rgba(255,255,255,.14);box-shadow:inset 0 -3px 0 var(--c)}
.hg-dock.gold span.on{box-shadow:inset 0 -3px 0 #ecd394;background:rgba(236,211,148,.16)}
.hg-dock span em{display:none}
.hg-dock.gold span{width:56px;flex-direction:column}
.hg-dock.gold span em{display:block;font:800 9.5px/1 system-ui;color:#ecd394;font-style:normal;margin-top:3px}
.hg-dock.gold span svg{width:20px!important;height:20px!important}
.hg-dots{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(26px + env(safe-area-inset-bottom));z-index:50;display:flex;gap:8px;align-items:center}
.hg-dots i{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.35)}
.hg-dots i.on{width:22px;border-radius:4px;background:#fff}
.hg-dots.gold i.on{background:#ecd394}
.hg-lbl{position:fixed;left:50%;top:4px;transform:translateX(-50%);z-index:99999;white-space:nowrap;font:900 10px/1 system-ui;background:#e10600;color:#fff;padding:5px 9px;border-radius:5px}
#scrTeam #teams,#scrTeam .teams{display:none!important}
#scrTeam .teaminfo{display:none!important}
#mNext{bottom:calc(14px + env(safe-area-inset-bottom))!important}
`;
async function mock(p, v, leg) {
  await p.evaluate(([v, leg]) => {
    document.querySelectorAll('.hg-seg,.hg-arr,.hg-name,.hg-dock,.hg-dots,.hg-lbl').forEach(e => e.remove());
    const add = h => { const d = document.createElement('div'); d.innerHTML = h; const e = d.firstElementChild; document.body.appendChild(e); return e; };
    add('<div class="hg-lbl">' + (v === 'A' ? 'ENTWURF A · Segment oben + Pfeile + Logo-Dock' : 'ENTWURF B · Segment oben + Pfeile/Wischen + Punkte') + (leg ? ' · Legenden' : ' · Saison') + '</div>');
    add('<div class="hg-seg"><b class="' + (leg ? '' : 'on') + '">Saison <i>2026</i></b><b class="' + (leg ? 'on gold' : '') + '">★ Legenden</b></div>');
    add('<div class="hg-arr l">‹</div>'); add('<div class="hg-arr r">›</div>');
    const teams = leg ? ['H_F67', 'H_LOT', 'H_MCL', 'H_MCL98', 'H_FER', 'H_RBR'] : ['MER', 'FER', 'MCL', 'RBR', 'AST', 'WIL', 'RB', 'ALP', 'HAA', 'AUD', 'CAD'].filter(k => window.__T[k]);
    const cur = leg ? 'H_F67' : 'MER', info = window.__T[cur];
    add('<div class="hg-name' + (leg ? ' gold' : '') + '"><b>' + info.n + '</b><small>' + info.s + '</small></div>');
    [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && /^formula 1$/i.test(e.textContent.trim()) && e.getBoundingClientRect().bottom > innerHeight - 80).forEach(e => (e.parentElement.style.visibility = v === 'A' ? 'hidden' : ''));
    if (v === 'A') add('<div class="hg-dock' + (leg ? ' gold' : '') + '">' + teams.map(k => '<span class="' + (k === cur ? 'on' : '') + '" style="--c:' + window.__T[k].c + '">' + window.__T[k].svg + '<em>' + (window.__T[k].y || '') + '</em></span>').join('') + '</div>');
    else add('<div class="hg-dots' + (leg ? ' gold' : '') + '">' + teams.map(k => '<i class="' + (k === cur ? 'on' : '') + '"></i>').join('') + '</div>');
  }, [v, leg]);
  await p.waitForTimeout(300);
}
(async () => { for (const [w, h, n] of [[667, 375, 'iphone_se'], [852, 393, 'iphone_15']]) { const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await ev(`window.__noPre = true; S.driver = 'RUS'; MENU.team = 'MER'; save(); window.__T = {}; for (const k of Object.keys(TEAMS)) { const H = HIST_CAR[k], d = ALL.filter(c => c.team === k); window.__T[k] = { svg: teamBadge(k), c: hex(uiCol(TEAMS[k])), y: H ? H.year : '', n: H ? TEAMS[k].short + ' ' + H.year : TEAMS[k].name, s: H ? H.title + ' · ' + (d[0] ? d[0].name : '') : d.map(c => c.name).join(' · ') }; } 1`);
  await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); for (let k = 0; k < 4 && q('#menu').dataset.scr !== 'team'; k++) { q('#mNext').click(); await new Promise(r => setTimeout(r, 800)); } });
  await p.addStyleTag({ content: CSS });
  const hide = () => p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
  await p.waitForTimeout(4000); await hide();
  for (const v of ['A', 'B']) { await mock(p, v, 0); await p.screenshot({ path: `phone/hig_${v}0_${n}.png` }); }
  await ev(`MENU.team = 'H_F67'; showroomTeam('H_F67'); renderMenu(); 1`); await p.waitForTimeout(7000); await hide();
  for (const v of ['A', 'B']) { await mock(p, v, 1); await p.screenshot({ path: `phone/hig_${v}1_${n}.png` }); }
  await b.close(); } })();
