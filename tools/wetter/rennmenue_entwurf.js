// Entwürfe für „Rennen einstellen“ mit Reitern und Wetterwahl (nur Bilder zur Abnahme – das Spiel selbst bleibt unverändert).
// Das Mockup wird per CSS/DOM in den echten Menü-Bildschirm eingespritzt, damit Schrift, Farben und Bausteine stimmen.
//   node tools/wetter/rennmenue_entwurf.js <Ausgabeordner>
const { spiel } = require('../textur/spiel.js'); const fs = require('fs'); const path = require('path');
const CSS = `
#scrRace .rgrid{display:none!important}
.rx{height:calc(100% - 46px);font-family:inherit;color:#fff}
@media (max-height:480px){.rx{height:100%}#scrRace>.mh{display:none!important}}   /* Handy quer: die Überschrift steht schon im Reiter „05 Rennen“ */
.rx svg{fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
/* ---------- Entwurf A: Reiter links mit aktuellem Wert, rechts die Einstellungen der gewählten Gruppe ---------- */
.rxA{display:grid;grid-template-columns:minmax(200px,29%) 1fr;gap:12px}
.rx-nav{display:flex;flex-direction:column;gap:8px;min-height:0}
.rx-nav button{flex:0 1 78px;min-height:44px;display:flex;align-items:center;gap:12px;padding:0 14px 0 12px;text-align:left;color:#fff;border:1px solid rgba(255,255,255,.16);border-left:4px solid rgba(255,255,255,.16);border-radius:6px;background:rgba(21,21,30,.86)}
.rx-nav button svg{width:24px;height:24px;flex:none;opacity:.6}
.rx-nav button span{min-width:0;flex:1}
.rx-nav button b{display:block;font-weight:900;font-style:italic;font-size:14px;letter-spacing:.12em;text-transform:uppercase;line-height:1.15}
.rx-nav button small{display:block;font-size:12px;font-weight:600;color:rgba(255,255,255,.6);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.3}
.rx-nav button em{font-style:normal;font-size:18px;opacity:.35}
.rx-nav button.on{border-color:rgba(255,255,255,.3);border-left-color:#e10600;background:linear-gradient(90deg,rgba(225,6,0,.3),rgba(40,22,26,.92) 55%,rgba(21,21,30,.92))}
.rx-nav button.on svg{opacity:1}.rx-nav button.on small{color:rgba(255,255,255,.85)}.rx-nav button.on em{opacity:.9;color:#fff}
.rx-pane{min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:flex-start;gap:14px;padding:18px 20px!important}
.rxA{align-items:start}.rxA .rx-pane{align-self:stretch;max-height:340px}
@media (max-height:480px){.rx-pane{gap:8px;padding:10px 14px!important;justify-content:center}.rxA .rx-pane{max-height:none}.rx-nav{height:100%}.rx-nav button{flex:1}}
.rx-pane .field{margin:0}
/* ---------- Entwurf B: Reiter oben, darunter eine Fläche ---------- */
.rxB{display:flex;flex-direction:column;gap:0}
.rx-tabs{display:flex;gap:2px;border-bottom:1px solid rgba(255,255,255,.18);flex:none}
.rx-tabs button{flex:1;height:42px;display:flex;align-items:center;justify-content:center;gap:9px;border:0;background:transparent;color:rgba(255,255,255,.5);font-weight:900;font-style:italic;font-size:13px;letter-spacing:.14em;text-transform:uppercase;border-bottom:3px solid transparent;margin-bottom:-1px}
.rx-tabs button svg{width:19px;height:19px}
.rx-tabs button.on{color:#fff;border-bottom-color:#e10600;background:linear-gradient(180deg,rgba(225,6,0,0),rgba(225,6,0,.16))}
.rxB .rx-pane{flex:0 1 300px;border-top:0!important;border-radius:0 0 6px 6px!important}
@media (max-height:480px){.rxB .rx-pane{flex:1}}
/* ---------- Bausteine ---------- */
.rx-2{display:grid;grid-template-columns:1fr 1fr;gap:14px 26px;align-items:start}
.rx-wx{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.rx-wx button{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:3px;padding:10px 12px 9px;min-height:88px;text-align:left;color:#fff;border:1px solid rgba(255,255,255,.16);border-radius:5px;background:rgba(0,0,0,.32)}
.rx-wx button svg{width:30px;height:30px;margin-bottom:auto;opacity:.75}
.rx-wx button b{font-weight:900;font-size:13px;letter-spacing:.08em;text-transform:uppercase;line-height:1.15}
.rx-wx button small{font-size:11px;font-weight:600;color:rgba(255,255,255,.58);line-height:1.25}
.rx-wx button.on{background:linear-gradient(180deg,#fff,#dcdde3);color:#101114;border-color:#fff;box-shadow:inset 0 -4px 0 #e10600}
.rx-wx button.on svg{opacity:1}.rx-wx button.on small{color:rgba(16,17,20,.7)}
@media (max-height:480px){.rx-wx button{min-height:74px;padding:8px 10px 8px}.rx-wx button svg{width:26px;height:26px}.rx-wx button b{font-size:12px}.rx-wx button small{font-size:10.5px}}
.rx-risk{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:12px;padding:9px 12px;border-radius:5px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1)}
.rx-risk label{font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.6);white-space:nowrap}
.rx-risk .bar{height:6px;border-radius:3px;background:rgba(255,255,255,.12);overflow:hidden}.rx-risk .bar i{display:block;height:100%;background:linear-gradient(90deg,#4aa3ff,#9fd0ff)}
.rx-risk b{font-weight:900;font-size:18px;font-variant-numeric:tabular-nums}
.rx-note{font-size:12px;line-height:1.45;color:rgba(255,255,255,.66);margin:0}
.rx-note b{color:#fff}
.rx-lbl{position:fixed;left:50%;top:3px;transform:translateX(-50%);z-index:99999;white-space:nowrap;font:900 10px/1 system-ui;background:#e10600;color:#fff;padding:5px 9px;border-radius:5px}
/* Karriere: Wetter-Hinweis am nächsten Rennen */
.sn-tags i.wx{display:inline-flex;align-items:center;gap:6px}.sn-tags i.wx svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
`;
const ICO = {
  race: '<svg viewBox="0 0 24 24"><path d="M5 21V4"/><path d="M5 5h13l-2.6 4 2.6 4H5"/></svg>',
  wx: '<svg viewBox="0 0 24 24"><path d="M7.5 15.5a4 4 0 0 1 .5-7.97A5.5 5.5 0 0 1 18.4 9a3.3 3.3 0 0 1-.4 6.5z"/><path d="M9 18.5l-1 2.5M13 18.5l-1 2.5M17 18.5l-1 2.5"/></svg>',
  ai: '<svg viewBox="0 0 24 24"><path d="M4 14a8 8 0 0 1 16 0v2.5a2 2 0 0 1-2 2H10l-6-3z"/><path d="M4.2 13H13a2.5 2.5 0 0 1 2.5 2.5V16"/></svg>',
  help: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="2.2"/><path d="M3.8 10.5h5.9M14.3 10.5h5.9M12 14.2v6.2"/></svg>',
  dry: '<svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="5.5"/><path d="M16 4v3M16 25v3M4 16h3M25 16h3M7.5 7.5l2.1 2.1M22.4 22.4l2.1 2.1M7.5 24.5l2.1-2.1M22.4 9.6l2.1-2.1"/></svg>',
  light: '<svg viewBox="0 0 32 32"><path d="M9.5 19a5.2 5.2 0 0 1 .7-10.36A7.2 7.2 0 0 1 24 10.6a4.3 4.3 0 0 1-.5 8.4z"/><path d="M13 23l-1 2.6M19.5 23l-1 2.6"/></svg>',
  heavy: '<svg viewBox="0 0 32 32"><path d="M9.5 17a5.2 5.2 0 0 1 .7-10.36A7.2 7.2 0 0 1 24 8.6a4.3 4.3 0 0 1-.5 8.4z"/><path d="M9.5 21l-2 5.5M14 21l-2 5.5M18.5 21l-2 5.5M23 21l-2 5.5"/></svg>',
  auto: '<svg viewBox="0 0 32 32"><rect x="6" y="6" width="20" height="20" rx="4"/><circle cx="11.5" cy="11.5" r="1.3" fill="currentColor"/><circle cx="20.5" cy="20.5" r="1.3" fill="currentColor"/><circle cx="16" cy="16" r="1.3" fill="currentColor"/><circle cx="20.5" cy="11.5" r="1.3" fill="currentColor"/><circle cx="11.5" cy="20.5" r="1.3" fill="currentColor"/></svg>',
};
function build([variant, tab, wx, trk, risk, date]) {
  document.querySelectorAll('.rx,.rx-lbl').forEach(e => e.remove());
  const WX = { dry: ['Trocken', 'Slicks · volle Haftung'], light: ['Leichter Regen', 'Intermediates · −14 % Grip'], heavy: ['Starker Regen', 'Regenreifen · −25 % Grip'], auto: ['Zufall', 'wie in echt · ' + risk + ' % Regen'] };
  const SUM = { race: '5 Runden · Start P10', wx: WX[wx][0] + (wx === 'auto' ? ' · ' + risk + ' %' : ''), ai: 'Schwierigkeit Mittel', help: 'Touch · Ideallinie aus' }, NAME = { race: 'Rennen', wx: 'Wetter', ai: 'Gegner', help: 'Fahrhilfen' };
  const seg = (opts, on) => '<div class="seg">' + opts.map((o, i) => '<button class="' + (i === on ? 'on' : '') + '">' + o + '</button>').join('') + '</div>';
  const PANE = {
    race: '<div class="rx-2"><div class="field"><label>Renndauer</label><div class="stepper"><button>−</button><output>5</output><button>+</button><span class="unit">Runden</span></div><div class="chips"><button>3</button><button class="on">5</button><button>10</button><button>20</button><button>44 (voll)</button></div></div>'
      + '<div class="field"><label>Startplatz</label><div class="stepper"><button>−</button><output>P10</output><button>+</button></div><div class="gridinfo">Vor dir: <b>Alexander Albon</b> (Williams)<br>Hinter dir: <b>Fernando Alonso</b> (Aston Martin)</div></div></div>',
    wx: '<div class="rx-wx">' + Object.keys(WX).map(k => '<button class="' + (k === wx ? 'on' : '') + '">' + ICO[k] + '<b>' + WX[k][0] + '</b><small>' + WX[k][1] + '</small></button>').join('') + '</div>'
      + '<div class="rx-risk"><label>Regenrisiko ' + trk + ' · ' + date + '</label><div class="bar"><i style="width:' + risk + '%"></i></div><b>' + risk + ' %</b></div>'
      + '<p class="rx-note">' + ({ dry: '<b>Trocken:</b> Rennen bei gutem Wetter, wie bisher.', light: '<b>Leichter Regen:</b> feuchte Fahrbahn mit einzelnen Pfützen, längere Bremswege. Alle fahren auf Intermediates.', heavy: '<b>Starker Regen:</b> viel stehendes Wasser, Gischt hinter den Autos, schlechte Sicht. Alle fahren auf Regenreifen.', auto: '<b>Zufall:</b> Das Wetter wird vor dem Start ausgelost – so oft Regen, wie es an dieser Strecke am Rennwochenende wirklich regnet.' })[wx] + '</p>',
    ai: '<div class="field"><label>Schwierigkeit</label>' + seg(['Leicht', 'Mittel', 'Schwer', 'Profi', 'Legende'], 1) + '</div><p class="rx-note"><b>Mittel:</b> Die Gegner fahren sauber, bremsen aber früh. Gut zum Einfahren auf einer neuen Strecke.</p>',
    help: '<div class="rx-2"><div class="field"><label>Steuerung</label>' + seg(['Neigen', 'Touch'], 1) + '</div><div class="field"><label>Ideallinie</label>' + seg(['Aus', 'Nur Bremsen', 'Voll'], 0) + '</div></div>'
      + '<div class="togs"><div class="tog"><span>Auto-Gas</span><button class="sw"></button></div><div class="tog"><span>Bremsassistent</span><button class="sw"></button></div></div>',
  };
  const keys = ['race', 'wx', 'ai', 'help'], host = document.querySelector('#scrRace'), d = document.createElement('div');
  if (variant === 'A') { d.className = 'rx rxA'; d.innerHTML = '<nav class="rx-nav">' + keys.map(k => '<button class="' + (k === tab ? 'on' : '') + '">' + ICO[k] + '<span><b>' + NAME[k] + '</b><small>' + SUM[k] + '</small></span><em>›</em></button>').join('') + '</nav><div class="rpanel rx-pane">' + PANE[tab] + '</div>'; }
  else { d.className = 'rx rxB'; d.innerHTML = '<nav class="rx-tabs">' + keys.map(k => '<button class="' + (k === tab ? 'on' : '') + '">' + ICO[k] + NAME[k] + '</button>').join('') + '</nav><div class="rpanel rx-pane">' + PANE[tab] + '</div>'; }
  host.appendChild(d);
  const l = document.createElement('div'); l.className = 'rx-lbl'; l.textContent = 'ENTWURF ' + variant + (variant === 'A' ? ' · Reiter links mit aktuellem Wert' : ' · Reiter oben') + ' · ' + NAME[tab]; document.body.appendChild(l);
  // Fußzeile: Auswahl-Chips um Wetter ergänzen (wie die übrigen)
  const ms = document.querySelector('#mSel'); if (ms) { ms.querySelectorAll('.rxc').forEach(e => e.remove()); if (innerHeight > 480) { const s = document.createElement('span'); s.className = 'rxc'; s.textContent = WX[wx][0]; ms.appendChild(s); } }
}
(async () => {
  const out = process.argv[2] || 'entwurf'; fs.mkdirSync(out, { recursive: true });
  for (const [w, h, n] of [[852, 393, 'handy'], [1280, 720, 'desktop']]) {
    const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
    await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1200);
    await ev(`window.__noPre = true; window.__noWarm = true; S.track = 'spa'; S.driver = 'RUS'; S.laps = 5; S.grid = 10; 1`);
    await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); });
    for (let k = 0; k < 8; k++) { const scr = await p.evaluate(() => document.querySelector('#menu').dataset.scr); if (scr === 'race') break; await p.evaluate(() => document.querySelector('#mNext').click()); await p.waitForTimeout(1500);
      await p.waitForFunction(() => !document.querySelector('#loading') || document.querySelector('#loading').classList.contains('hidden'), null, { timeout: 600000 }).catch(() => {}); }
    await p.addStyleTag({ content: CSS });
    await p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
    for (const [v, tab, wx] of [['A', 'wx', 'light'], ['A', 'race', 'light'], ['A', 'wx', 'auto'], ['A', 'help', 'light'], ['A', 'ai', 'light'], ['B', 'wx', 'light'], ['B', 'race', 'light'], ['B', 'help', 'light']]) {
      await p.evaluate(`const ICO = ${JSON.stringify(ICO)};`).catch(() => {}); await p.evaluate(new Function("a", "const ICO = " + JSON.stringify(ICO) + "; return (" + build.toString() + ")(a);"), [v, tab, wx, 'Spa', 28, '19. Juli']); await p.waitForTimeout(250); await p.screenshot({ path: path.join(out, `menue_${v}_${tab}_${wx}_${n}.png`) }); }
    await b.close(); }
})().catch(e => { console.error(e); process.exit(1); });
