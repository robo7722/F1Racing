// Entwurf: Teamleiste fürs Handy verbessert (CSS-Einspritzung)
const { spiel } = require('/home/user/F1Racing/tools/textur/spiel.js');
const CSS = `
#scrTeam{--tw:clamp(44px,min(13.5vh,calc((100vw - 190px) / 13)),62px)}
#scrTeam .teams{gap:8px!important;padding:8px max(10px,env(safe-area-inset-right)) 6px max(10px,env(safe-area-inset-left))!important;scroll-snap-type:x proximity;align-items:flex-end;justify-content:safe center}
#scrTeam .teams .tm{scroll-snap-align:center}
#scrTeam .tmtabs{position:sticky;left:0;z-index:3;height:auto;align-self:stretch;min-height:var(--tw);background:rgba(14,16,22,.92)}
#scrTeam .teams.leg .tmtabs{min-height:max(58px,calc(var(--tw)*1.3))}
#scrTeam .tmtabs button{min-height:24px;font-size:clamp(10px,2.6vh,12px)!important;padding:0 14px 0 12px}
#scrTeam .tmtabs button::after{content:'';position:absolute;inset:-4px -2px}
#scrTeam .tmtabs button i{opacity:1!important}
#scrTeam .tmtabs button:not(.on) i{color:rgba(255,255,255,.55)}
#scrTeam .tm:not(.lcard) svg{filter:brightness(1.35)}
#scrTeam .tm:not(.on):not(.lcard){opacity:.88}
#scrTeam .tm.on:not(.lcard){transform:translateY(-3px)!important;box-shadow:inset 0 -4px 0 var(--c1),0 6px 16px rgba(0,0,0,.5),0 0 14px color-mix(in srgb,var(--c1) 55%,transparent)!important}
#scrTeam .tm.lcard{height:max(58px,calc(var(--tw)*1.3))!important;width:max(112px,min(calc(var(--tw)*2.55),calc((100vw - 200px) / 6 - 8px)))!important;padding:clamp(6px,1.8vh,10px) 8px 0!important}
#scrTeam .tm.lcard .ly{font-size:clamp(17px,4.6vh,22px)!important}
#scrTeam .tm.lcard .ln{font-size:clamp(9.5px,2.6vh,11.5px)!important;text-overflow:ellipsis;margin-top:4px}
#scrTeam .tm.lcard .ld{font-size:clamp(9px,2.5vh,11px)!important;text-overflow:ellipsis;margin-top:2px}
#scrTeam .tm.lcard.on{transform:translateY(-3px)!important;box-shadow:inset 0 -4px 0 #ecd394,0 0 16px rgba(236,211,148,.35)!important}
#scrTeam .teaminfo p{font-size:11.5px!important}
@media (max-height:380px){#scrTeam .teaminfo p+p{display:none}}
#scrTeam .teams{-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent)}
`;
const LBL = (t) => `(() => { const l = document.createElement('div'); l.id = 'mkl'; l.style.cssText = 'position:fixed;left:50%;top:4px;transform:translateX(-50%);z-index:99999;white-space:nowrap;font:900 10px/1 system-ui;background:#e10600;color:#fff;padding:5px 9px;border-radius:5px'; l.textContent = '${t}'; document.body.appendChild(l); })()`;
(async () => { for (const [w, h, n] of [[667, 375, 'iphone_se'], [852, 393, 'iphone_15']]) { const { b, p, ev } = await spiel({ w, h, query: '?qc=none' });
  await p.waitForFunction(() => typeof window.__race === 'function', null, { timeout: 300000 }); await p.waitForTimeout(1500);
  await ev(`window.__noPre = true; S.driver = 'RUS'; MENU.team = 'MER'; save(); 1`);
  await p.evaluate(async () => { const q = s => document.querySelector(s); q('#qPlay').click(); await new Promise(r => setTimeout(r, 800)); for (let k = 0; k < 4 && q('#menu').dataset.scr !== 'team'; k++) { q('#mNext').click(); await new Promise(r => setTimeout(r, 800)); } });
  await p.addStyleTag({ content: CSS });
  const hide = () => p.evaluate(() => [...document.querySelectorAll('div')].filter(d => d.textContent.trim().startsWith('QC-Bot') && d.children.length < 4).forEach(d => d.style.display = 'none'));
  await p.waitForTimeout(4000); await hide(); await p.evaluate(LBL('NEU · ' + n + ' · Saison')); await p.screenshot({ path: `phone/neu_${n}_saison.png` });
  await p.evaluate(() => document.getElementById('mkl').remove());
  await p.click('#teams .tmtabs button[data-leg="1"]'); await p.waitForTimeout(6000); await hide(); await p.evaluate(LBL('NEU · ' + n + ' · Legenden')); await p.screenshot({ path: `phone/neu_${n}_legenden.png` });
  console.log(n, await p.evaluate(() => JSON.stringify([...document.querySelectorAll('#teams .tmtabs button, #teams .tm')].slice(0, 3).map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; }))));
  await b.close(); } })();
