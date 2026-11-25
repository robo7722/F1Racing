// Drehplan für den Trailer (Stand v2, 25.11.2026): jede Einstellung mit Vorbereitung, Kamerafahrt und Dauer.
// Gerechnet wird mit tools/trailer/dreh.js in einem laufenden Studio (eine Strecke je Studio, mehrere Rennen nacheinander).
//   Studio            Rennen (Fahrer, Wetter)           Einstellungen
//   Garage (--menue)  –                                 s01_garage_fluegel, s02_garage_helm
//   Abu Dhabi         LEC trocken                       s03_ampel, s04_start, s05_profil
//   Singapur          NOR trocken · NOR Starkregen      s06_sgp_luft, s07_sgp_nah, s16a_sprint, s16b_ziel · s17a_sgp_regen, s18b_sgp_helm
//   Las Vegas         RUS trocken · RUS Starkregen      s09_sphere, s10_strip · s17b_vegas_regen
//   Monza             AMO RIN SEN HAK MSC VET · LEC     s11_* (sechs Legenden), s12_cockpit88 (SEN) · s14_duell
//   Genk (Kart)       –                                 s13_kart
//   Spa               VER Starkregen                    s18a_spa_regen
//   Monaco            RUS trocken                       s08a_helm, s08b_tunnel, s08c_rad, s08d_tcam
// Kamera-Angaben: von/auf als [rechts, hoch, vor] am Auto, { s, lat, h } an der Strecke oder [x, y, z, 0] in der Welt; fov in Grad.
// kams: Abschnitte einer Einstellung (bis = Ende in s); a → b ist eine Fahrt; speed = Tempo-Unschärfe des Spiels (0…1,2); wack = Handkamera-Unruhe in m.
const TAKT = 2.182;   // ein Takt der Musik (110 BPM)
const legende = { dauer: TAKT / 2, ao: false,   // je zwei Schläge der Musik (vorher 4 Takte durch 6 = nicht im Takt)
  vor: `TR.feld(5300, 0, []); TR.sim(10, 33.3);`,
  kams: [{ a: { von: [2.4, 0.42, 5.4], auf: [0, 0.5, 0], fov: 30 }, b: { von: [2.1, 0.42, 5.0], auf: [0, 0.5, 0], fov: 29 }, ease: 'lin', speed: 0.3, wack: 0.012 }] };
module.exports = {
  fps: 24, groesse: [1920, 804],
  szenen: {
    /* ---------- Garage ---------- */
    s01_garage_fluegel: { typ: 'garage', dauer: 2.85, ease: 'lin',
      a: { p: [-4.9, 0.31, 3.05], t: [-2.8, 0.42, 0.3], f: [-3.25, 0.42, 0.45], fov: 26, ap: 0.05 }, b: { p: [-4.3, 0.35, 3.45], t: [-2.3, 0.46, 0.15], f: [-2.85, 0.46, 0.3], fov: 26, ap: 0.05 } },
    s02_garage_helm: { typ: 'garage', dauer: 2.4, ease: 'lin',
      a: { p: [-2.75, 1.22, 2.0], t: [0.2, 0.82, 0], f: [-0.75, 0.95, 0.1], fov: 21, ap: 0.04 }, b: { p: [-2.15, 1.12, 1.6], t: [0.25, 0.8, 0], f: [0.3, 0.85, 0.05], fov: 20, ap: 0.04 } },
    /* ---------- Abu Dhabi, Dämmerung ---------- */
    s03_ampel: { dauer: 5.6, ao: true,   // fünf Lichter im Abstand von 0,95 s (wie im Spiel), 1,2 s halten, auf dem letzten Bild aus
      vor: `S.grid = 1; placeOnGrid(); raceState = 'lights'; SG.on = false; lightsOut = 99; lightsT = 0; cars.forEach(c => { c.v = 0; });
        TR.je = t => { const lit = Math.max(0, Math.min(5, Math.floor((t - 0.45) / 0.95) + 1)); if (t > 5.52) { lightsOut = 0; } else lightsT = lit * 0.95 + 0.05; }; TR.sim(2, 33.3);`,
      kams: [{ a: { von: { s: -84, lat: 0.55, h: 1.12 }, auf: { s: 0, lat: 0, h: 5.3 }, fov: 16 }, b: { von: { s: -70, lat: 0.3, h: 1.04 }, auf: { s: 0, lat: 0, h: 5.6 }, fov: 13.5 }, ease: 'lin', wack: 0.005 }] },
    s04_start: { dauer: 4.35, ao: true,
      vor: `S.grid = 1; placeOnGrid(); raceState = 'lights'; SG.on = false; lightsOut = 99; lightsT = 4.9; cars.forEach(c => { c.v = 0; }); TR.sim(2, 33.3); lightsOut = 0; window.__plAI = true;`,
      kams: [{ a: { von: { s: -6, lat: 0.25, h: 0.24 }, auf: { s: -28, lat: 0, h: 0.75 }, fov: 27 }, b: { von: { s: -6, lat: 0.25, h: 0.3 }, auf: { s: -28, lat: 0, h: 1.0 }, fov: 38 }, ease: 'lin', wack: 0.012, wackF: 1.6 }] },
    s05_profil: { dauer: 4.4, zeitlupe: 0.6, mb: 4, verschluss: 0.6, ao: true,
      vor: `TR.start(); TR.feld(2868, 3.2, [[-26, 3.0, 1], [-52, 1.5, 1]], 1); TR.je = () => { pl.ovr = 3.2; pl.laneT = raceTime + 9; }; TR.sim(8, 33.3);`,
      kams: [{ a: { von: [-5.0, 0.42, -0.5], auf: [0, 0.5, 0.2], fov: 37 }, b: { von: [-4.6, 0.38, 1.0], auf: [0, 0.5, 0.4], fov: 37 }, ease: 'lin', wack: 0.008 }] },
    s08a_sonne: { dauer: 1.09, seite: true, ao: false, vor: `TR.start(); TR.feld(1560, 0, [[16, 1.6], [31, -1.6], [-14, 2]]); S.cam = 2; window.__camFix = null; TR.sim(30, 33.3);`, kams: [{ a: { cam: 2 } }] },
    /* ---------- Singapur, Nacht ---------- */
    s06_sgp_kran: { dauer: 4.4, ao: true, zeitlupe: 0.7,   // Kran-Aufzug (gewählt aus sieben Proben): tief vor dem Auto beginnen, rückwärts auf 6,5 m steigen – Feld, beleuchtete Strecke, Riesenrad und Skyline kommen ins Bild
      vor: `TR.feld(1000, 0, [[-12, 2.4], [-25, -2], [-38, 2.2], [-52, -1.2], [-66, 1.5], [-80, -2]]); TR.sim(12, 33.3);`,
      kams: [{ a: { von: [1.4, 0.55, 7], auf: [0, 0.7, 0], fov: 30 }, b: { von: [3.5, 6.5, 24], auf: [0, 5, -45], fov: 36 }, ease: 'lin' }] },
    s08b_vorbei: { dauer: 1.09, ao: true,   // feste Kamera am Randstein: das Auto rauscht dicht vorbei
      vor: `TR.feld(1060, 0.5, [[-14, -2.2], [-27, 1.8], [-40, -1]]); TR.sim(8, 33.3);`, kams: [{ a: { von: { s: 1118, lat: -3.6, h: 0.22 }, auf: [0, 0.5, 0], fov: 34 } }] },
    s07_sgp_nah: { dauer: 4.3, zeitlupe: 0.8, ao: true,
      vor: `TR.feld(1470, 0, [[-12, 2.4], [-25, -2], [-38, 2.2], [-52, -1.2]]); TR.sim(12, 33.3);`,
      kams: [{ a: { von: [3.0, 0.38, 7.5], auf: [0, 0.55, 0], fov: 30 }, b: { von: [1.2, 0.5, 6.5], auf: [0, 0.55, 0], fov: 27 }, ease: 'lin', speed: 0.35, wack: 0.012 }] },
    s16a_sprint: { dauer: TAKT * 2, ao: false,
      vor: `TR.feld(3780, 1.5, [[1.2, -2.6, 0.95], [-15, 0.8, 0.95], [-28, -1.6, 0.95]], 0.93); TR.je = () => { pl.ovr = 1.5; pl.laneT = raceTime + 9; const r = TR.auto(0); r.ovr = -2.6; r.laneT = raceTime + 9; r.v = pl.v - 0.45; }; TR.sim(8, 33.3);`,
      kams: [{ a: { von: [-0.6, 0.35, 10.5], auf: [-0.9, 0.6, 0], fov: 27 }, b: { von: [-1.4, 0.5, 8.5], auf: [-0.9, 0.6, 0], fov: 25 }, ease: 'lin', speed: 0.4, wack: 0.015 }] },
    s16b_ziel: { dauer: 4.85, ao: false,
      vor: `TR.feld(L - 430, 1.2, [[-13, -2.2, 0.97], [-27, 1.5, 0.97], [12, -1.8, 0.97]], 0.97); TR.fwT = 0; TR.fwO = { vor: [120, 280], seit: [30, 95], hoch: [50, 100], takt: 0.26 }; TR.je = (t, ms) => TR.fwLauf(ms, TR.fwO); for (let i = 0; i < 60; i++) { TR.fwLauf(33.3, TR.fwO); TR.takt(33.3, false); }`,
      kams: [{ a: { von: [-0.5, 0.42, -3.3], auf: [0, 0.9, 10], fov: 50 }, b: { von: [-3.2, 10.5, -15], auf: [0, 15, 60], fov: 60 }, ease: 'lin', speed: 0.3 }] },   // dicht hinter dem Heck beginnen, gleichmäßig auf 10 m steigen
    /* ---------- Monza: Legenden und Zweikampf ---------- */
    s11_amo: legende, s11_rin: legende, s11_sen: legende, s11_hak: legende, s11_msc: legende, s11_vet: legende, s11_2026: { ...legende, dauer: TAKT },
    s12_cockpit88: { dauer: TAKT * 2, seite: true, ao: false, vor: `TR.feld(270, 0, []); TR.sim(10, 33.3);`, kams: [{ a: { cam: 2 } }] },
    // Zweikampf in der Helmkamera: im Windschatten heran, ausscheren, nebeneinander auf die erste Schikane zu, innen vorbei. Dazwischen ein Takt von außen.
    s14_duell: { dauer: TAKT * 5, seite: true, ao: false, seed: 11,
      vor: `{ const r = TR.auto(0); TR.feld(5400, -1.6, [[14, -1.6, 1]], 1); r.form = 0.045; TR.brems = 0; TR.vSoll = null;   /* Startpunkt so, dass die Einstellung beim Einlenken endet – weiter hinein fährt die KI weit über den inneren Randstein (sah wie Abkürzen aus) */
        TR.innen = Math.hypot(trackAt(600, 3).x - trackAt(640, 0).x, trackAt(600, 3).z - trackAt(640, 0).z) < Math.hypot(trackAt(600, -3).x - trackAt(640, 0).x, trackAt(600, -3).z - trackAt(640, 0).z) ? 1 : -1;
        TR.je = t => { const g = wrapL(r.d - pl.d), sd = TR.innen, rs = modL(r.d); r.ovr = rs > 5000 || rs < 560 ? -1.6 * sd : null; r.laneT = raceTime + 9; pl.laneT = raceTime + 9;   /* Gegner bleibt außen, 3,5 m Abstand zur Seite – bei weniger berühren sich die Autos und beide bremsen */
          const verlust = TR.vSoll != null ? Math.max(0, TR.vSoll - pl.v) : 0;   /* was die KI seit dem letzten Bild weggebremst hat (sie hält sonst 35 m Abstand) */
          let soll = null; { const sp = modL(pl.d); if (!TR.brems && sp > 468 && sp < 800) TR.brems = t; }
          if (TR.brems) { pl.ovr = modL(pl.d) < 575 ? 1.9 * sd : null; if (t - TR.brems < 0.5) soll = Math.max(pl.v, r.v + 6); }   /* später bremsen und innen hinein */
          else if (t < 3.0) { pl.ovr = -1.6 * sd; soll = r.v + Math.max(-0.5, Math.min(3.5, (g - 8.8) * 1.2)); }                                   /* im Windschatten bis dicht ans Heck */
          else { pl.ovr = 1.9 * sd; soll = r.v + Math.max(-1, Math.min(5, (g - (Math.abs(pl.lat - r.lat) > 2.9 ? 2.2 : 8.8)) * 1.2)); }   /* unter 7,1 m Abstand hält die KI beide Autos seitlich auseinander – dann käme man nicht mehr auf die andere Seite */   /* erst zur Seite, dann aufschließen – sonst fährt man dem Gegner ins Heck */                                          /* ausscheren, Rad an Rad – der Gegner bleibt eine halbe Länge vorn */
          if (soll != null) { pl.v = soll + Math.min(verlust, 4); TR.vSoll = pl.v; } else TR.vSoll = null;
          TR.dlog = (TR.dlog || '') + (Math.round(t * 24) % 24 === 0 ? ' t' + t.toFixed(1) + ':g' + g.toFixed(1) + '/v' + Math.round(pl.v * 3.6) + '/s' + Math.round(modL(pl.d)) : ''); }; TR.dlog = ''; TR.sim(6, 33.3); }`,
      kams: [{ bis: TAKT * 2, a: { cam: 2 } },
        { bis: TAKT * 3, a: { von: [-1.4, 0.34, 11.5], auf: [-1.55, 0.6, 0.5], fov: 27 }, b: { von: [-1.2, 0.42, 9.5], auf: [-1.55, 0.6, 0.5], fov: 26 }, ease: 'lin', speed: 0.7, wack: 0.02 },
        { bis: TAKT * 5, a: { cam: 2 } }] },
    /* ---------- Regen ---------- */
    s17a_sgp_regen: { dauer: 4.4, zeitlupe: 0.45, ao: true,   // gewählt aus drei Proben: nah von vorn, Riesenrad dahinter, spiegelnde Fahrbahn (von hinten in der Gischt war es zu dunkel)
      vor: `TR.feld(1010, 0, [[-11, 2.4], [-23, -2.0], [-36, 1.8], [-50, -1.0]]); TR.sim(40, 33.3);`,
      kams: [{ a: { von: [2.3, 0.3, 6.2], auf: [0, 0.5, 0], fov: 30 }, b: { von: [1.3, 0.36, 5.4], auf: [0, 0.5, 0], fov: 28 }, ease: 'lin', wack: 0.008 }] },
    s18b_sgp_helm: { dauer: 2.3, seite: true, ao: false,
      vor: `TR.feld(2180, 0, [[16, 1.8], [30, -1.6], [47, 0.8]]); S.cam = 2; window.__camFix = null; TR.sim(50, 33.3);`, kams: [{ a: { cam: 2 } }] },
    s17b_vegas_regen: { dauer: 2.6, zeitlupe: 0.5, ao: true,   // seitlich vor der Sphere: Auto links auf der Bahn (lat −1,5), Kamera 5,6 m rechts daneben = noch innerhalb der Mauer
      vor: `TR.feld(1915, -1.5, [[-16, 1.6, 0.9], [-33, -1.0, 0.9]]); TR.je = () => { pl.ovr = -1.5; pl.laneT = raceTime + 9; }; TR.sim(25, 33.3);`,
      kams: [{ a: { von: [5.6, 0.3, 1.3], auf: [342, 22, -496, 0], fov: 48 }, b: { von: [5.2, 0.3, 0.3], auf: [342, 22, -496, 0], fov: 46 }, ease: 'lin' }] },
    s18a_spa_regen: { dauer: 2.2, zeitlupe: 0.5, ao: false,
      vor: `TR.feld(1150, 0, [[-11, 2.4], [-23, -2.2], [-34, 1.4], [-47, -2.0], [-58, 2.2], [-72, -1.5], [-84, 0.5]]); TR.sim(45, 33.3);`,
      kams: [{ a: { von: { s: 1410, lat: -0.6, h: 0.6 }, auf: [0, 0.55, 0], fov: 6.5 }, b: { von: { s: 1410, lat: -0.6, h: 0.6 }, auf: [0, 0.55, 0], fov: 7.5 }, ease: 'lin' }] },
    /* ---------- Monaco: vier schnelle Schnitte ---------- */
    s08a_helm: { dauer: 1.09, seite: true, ao: false, vor: `TR.feld(1195, 0, [[12, 0.5], [-12, -0.5]]); S.cam = 2; window.__camFix = null; TR.sim(30, 33.3);`, kams: [{ a: { cam: 2 } }] },
    s08b_tunnel: { dauer: 1.09, ao: false, vor: `TR.feld(1850, 0, [[-12, 1.5], [-25, -1.5], [-38, 1]]); TR.sim(25, 33.3);`,
      kams: [{ a: { von: [2.2, 0.4, 9], auf: [0, 0.6, 0], fov: 24 }, b: { von: [2.0, 0.4, 8], auf: [0, 0.6, 0], fov: 24 }, ease: 'lin', speed: 0.5, wack: 0.015 }] },
    s08c_rad: { dauer: 1.09, ao: true, vor: `TR.feld(2280, 0, [[-14, 1.2]]); TR.sim(20, 33.3);`,
      kams: [{ a: { von: [-2.5, 0.3, 3.1], auf: [-0.85, 0.34, 1.8], fov: 23 }, b: { von: [-2.4, 0.3, 2.7], auf: [-0.85, 0.34, 1.8], fov: 23 }, ease: 'lin', speed: 0.5, wack: 0.006 }] },
    s08d_tcam: { dauer: 1.09, seite: true, ao: false, vor: `TR.feld(2470, 0, [[14, 0.5], [28, -0.5]]); S.cam = 3; window.__camFix = null; TR.sim(30, 33.3);`, kams: [{ a: { cam: 3 } }] },
    /* ---------- Kart ---------- */
    s13_kart: { dauer: TAKT * 2, ao: true,
      vor: `TR.feld(280, 0, [[5, 1.2], [10, -1], [-5, -1.2], [-10, 1], [-15, -0.6], [16, 0.5], [-20, 0.8]]); TR.sim(30, 33.3);`,
      kams: [{ a: { von: [1.7, 0.3, 3.8], auf: [0, 0.4, 0], fov: 36 }, b: { von: [-0.9, 0.34, 3.3], auf: [0, 0.4, 0], fov: 34 }, ease: 'io', speed: 0.2, wack: 0.01 }] },
    /* ---------- Las Vegas ---------- */
    s09_sphere: { dauer: TAKT * 2, zeitlupe: 0.35, ao: true,
      vor: `TR.feld(1946, 1.5, [[-16, -2, 0.9], [-33, 2, 0.9], [20, -2.2, 0.9]]); TR.sim(6, 33.3);`,
      kams: [{ a: { von: [5.4, 0.42, 1.6], auf: [342, 30, -496, 0], fov: 46 }, b: { von: [5.0, 0.42, 0.2], auf: [342, 24, -496, 0], fov: 43 }, ease: 'lin' }] },
    s10_strip: { dauer: TAKT * 2, seite: true, ao: false, vor: `TR.feld(4250, 0, [[18, 2], [34, -2], [-15, -2.2], [52, 1]]); TR.sim(40, 33.3);`, kams: [{ a: { cam: 3 } }] },
  },
};
