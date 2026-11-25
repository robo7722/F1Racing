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
const legende = { dauer: TAKT * 4 / 6, ao: false, vor: `TR.feld(5300, 0, []); TR.sim(10, 33.3);`,
  kams: [{ a: { von: [2.4, 0.42, 5.4], auf: [0, 0.5, 0], fov: 30 }, b: { von: [2.1, 0.42, 5.0], auf: [0, 0.5, 0], fov: 29 }, ease: 'lin', speed: 0.4, wack: 0.012 }] };
module.exports = {
  fps: 24, groesse: [1920, 804],
  szenen: {
    /* ---------- Garage ---------- */
    s01_garage_fluegel: { typ: 'garage', dauer: 4.0, sub: 3, fenster: 12, ease: 'lin',
      a: { p: [-5.0, 0.30, 3.0], t: [-3.35, 0.42, 0.45], fov: 26, ap: 0.05 }, b: { p: [-4.15, 0.36, 3.55], t: [-2.7, 0.46, 0.2], fov: 26, ap: 0.05 } },
    s02_garage_helm: { typ: 'garage', dauer: 3.4, sub: 3, fenster: 12, ease: 'lin',
      a: { p: [-2.75, 1.22, 2.0], t: [0.2, 0.82, 0], f: [-0.75, 0.95, 0.1], fov: 21, ap: 0.04 }, b: { p: [-2.15, 1.12, 1.6], t: [0.25, 0.8, 0], f: [0.3, 0.85, 0.05], fov: 20, ap: 0.04 } },
    /* ---------- Abu Dhabi, Dämmerung ---------- */
    s03_ampel: { dauer: 3.45, ao: true,
      vor: `S.grid = 1; placeOnGrid(); raceState = 'lights'; SG.on = false; lightsOut = 99; lightsT = 0; cars.forEach(c => { c.v = 0; });
        TR.je = t => { const lit = Math.max(0, Math.min(5, Math.floor((t - 0.3) / 0.5) + 1)); if (t > 3.36) { lightsOut = 0; } else lightsT = lit * 0.95 + 0.05; }; TR.sim(2, 33.3);`,
      kams: [{ a: { von: { s: -80, lat: 0.5, h: 1.1 }, auf: { s: 0, lat: 0, h: 5.4 }, fov: 15.5 }, b: { von: { s: -72, lat: 0.35, h: 1.05 }, auf: { s: 0, lat: 0, h: 5.6 }, fov: 14 }, ease: 'lin', wack: 0.006 }] },
    s04_start: { dauer: 4.35, ao: true,
      vor: `S.grid = 1; placeOnGrid(); raceState = 'lights'; SG.on = false; lightsOut = 99; lightsT = 4.9; cars.forEach(c => { c.v = 0; }); TR.sim(2, 33.3); lightsOut = 0; window.__plAI = true;`,
      kams: [{ a: { von: { s: -6, lat: 0.25, h: 0.24 }, auf: { s: -28, lat: 0, h: 0.75 }, fov: 27 }, b: { von: { s: -6, lat: 0.25, h: 0.3 }, auf: { s: -28, lat: 0, h: 1.0 }, fov: 38 }, ease: 'lin', wack: 0.012, wackF: 1.6 }] },
    s05_profil: { dauer: 4.4, zeitlupe: 0.6, mb: 4, verschluss: 0.6, ao: true,
      vor: `TR.start(); TR.feld(2868, 3.2, [[-26, 3.0, 1], [-52, 1.5, 1]], 1); TR.je = () => { pl.ovr = 3.2; pl.laneT = raceTime + 9; }; TR.sim(8, 33.3);`,
      kams: [{ a: { von: [-5.0, 0.42, -0.5], auf: [0, 0.5, 0.2], fov: 37 }, b: { von: [-4.6, 0.38, 1.0], auf: [0, 0.5, 0.4], fov: 37 }, ease: 'lin', wack: 0.008 }] },
    /* ---------- Singapur, Nacht ---------- */
    s06_sgp_luft: { dauer: 4.4, ao: false,
      vor: `TR.feld(1380, 0, [[14, 2], [-13, -2], [-27, 2], [30, -1.5], [-41, -1], [45, 1]]); TR.sim(10, 33.3);`,
      kams: [{ a: { von: [-556, 200, -566, 0], auf: [104, 0, 54, 0], fov: 40 }, b: { von: [-426, 115, -436, 0], auf: [144, 10, 74, 0], fov: 38 }, ease: 'lin' }] },
    s07_sgp_nah: { dauer: 4.3, zeitlupe: 0.8, ao: true,
      vor: `TR.feld(1470, 0, [[-12, 2.4], [-25, -2], [-38, 2.2], [-52, -1.2]]); TR.sim(12, 33.3);`,
      kams: [{ a: { von: [3.0, 0.38, 7.5], auf: [0, 0.55, 0], fov: 30 }, b: { von: [1.2, 0.5, 6.5], auf: [0, 0.55, 0], fov: 27 }, ease: 'lin', speed: 0.35, wack: 0.012 }] },
    s16a_sprint: { dauer: TAKT * 2, ao: false,
      vor: `TR.feld(3780, 1.5, [[1.2, -2.6, 0.95], [-15, 0.8, 0.95], [-28, -1.6, 0.95]], 0.93); TR.je = () => { pl.ovr = 1.5; pl.laneT = raceTime + 9; const r = TR.auto(0); r.ovr = -2.6; r.laneT = raceTime + 9; r.v = pl.v - 0.45; }; TR.sim(8, 33.3);`,
      kams: [{ a: { von: [-0.6, 0.35, 10.5], auf: [-0.9, 0.6, 0], fov: 27 }, b: { von: [-1.4, 0.5, 8.5], auf: [-0.9, 0.6, 0], fov: 25 }, ease: 'lin', speed: 0.6, wack: 0.015 }] },
    s16b_ziel: { dauer: 4.85, ao: false,
      vor: `TR.feld(L - 430, 1.2, [[-13, -2.2, 0.97], [-27, 1.5, 0.97], [12, -1.8, 0.97]], 0.97); TR.fwT = 0; TR.fwO = { vor: [120, 280], seit: [30, 95], hoch: [50, 100], takt: 0.26 }; TR.je = (t, ms) => TR.fwLauf(ms, TR.fwO); for (let i = 0; i < 60; i++) { TR.fwLauf(33.3, TR.fwO); TR.takt(33.3, false); }`,
      kams: [{ a: { von: [-1.2, 0.6, -6.5], auf: [0, 2.5, 30], fov: 55 }, b: { von: [-1.6, 1.7, -7.2], auf: [0, 8, 40], fov: 62 }, ease: 'io', speed: 0.3 }] },
    /* ---------- Monza: Legenden und Zweikampf ---------- */
    s11_amo: legende, s11_rin: legende, s11_sen: legende, s11_hak: legende, s11_msc: legende, s11_vet: legende,
    s12_cockpit88: { dauer: TAKT * 2, seite: true, ao: false, vor: `TR.feld(270, 0, []); TR.sim(10, 33.3);`, kams: [{ a: { cam: 2 } }] },
    // Zweikampf in der Helmkamera: im Windschatten heran, ausscheren, nebeneinander auf die erste Schikane zu, innen vorbei. Dazwischen ein Takt von außen.
    s14_duell: { dauer: TAKT * 5, seite: true, ao: false, seed: 11,
      vor: `{ const r = TR.auto(0); TR.feld(5525, -1.6, [[13, -1.6, 1]], 1); r.form = 0.045; TR.brems = 0; TR.vSoll = null;
        TR.innen = Math.hypot(trackAt(600, 3).x - trackAt(640, 0).x, trackAt(600, 3).z - trackAt(640, 0).z) < Math.hypot(trackAt(600, -3).x - trackAt(640, 0).x, trackAt(600, -3).z - trackAt(640, 0).z) ? 1 : -1;
        TR.je = t => { const g = wrapL(r.d - pl.d), sd = TR.innen, rs = modL(r.d); r.ovr = rs > 5000 || rs < 560 ? -1.6 * sd : null; r.laneT = raceTime + 9; pl.laneT = raceTime + 9;   /* Gegner bleibt außen, 3,5 m Abstand zur Seite – bei weniger berühren sich die Autos und beide bremsen */
          const verlust = TR.vSoll != null ? Math.max(0, TR.vSoll - pl.v) : 0;   /* was die KI seit dem letzten Bild weggebremst hat (sie hält sonst 35 m Abstand) */
          let soll = null; { const sp = modL(pl.d); if (!TR.brems && sp > 468 && sp < 800) TR.brems = t; }
          if (TR.brems) { pl.ovr = modL(pl.d) < 575 ? 1.9 * sd : null; if (t - TR.brems < 0.75) soll = Math.max(pl.v, r.v + 8); }   /* später bremsen und innen hinein */
          else if (t < 3.0) { pl.ovr = -1.6 * sd; soll = r.v + Math.max(-0.5, Math.min(3.5, (g - 7.8) * 1.2)); }                                   /* im Windschatten bis dicht ans Heck */
          else { pl.ovr = 1.9 * sd; soll = r.v + Math.max(-1, Math.min(5, (g - (Math.abs(pl.lat - r.lat) > 2.9 ? 2.2 : 7.8)) * 1.2)); }   /* unter 7,1 m Abstand hält die KI beide Autos seitlich auseinander – dann käme man nicht mehr auf die andere Seite */   /* erst zur Seite, dann aufschließen – sonst fährt man dem Gegner ins Heck */                                          /* ausscheren, Rad an Rad – der Gegner bleibt eine halbe Länge vorn */
          if (soll != null) { pl.v = soll + Math.min(verlust, 4); TR.vSoll = pl.v; } else TR.vSoll = null;
          TR.dlog = (TR.dlog || '') + (Math.round(t * 24) % 24 === 0 ? ' t' + t.toFixed(1) + ':g' + g.toFixed(1) + '/v' + Math.round(pl.v * 3.6) + '/s' + Math.round(modL(pl.d)) : ''); }; TR.dlog = ''; TR.sim(6, 33.3); }`,
      kams: [{ bis: TAKT * 2, a: { cam: 2 } },
        { bis: TAKT * 3, a: { von: [-1.4, 0.34, 11.5], auf: [-1.55, 0.6, 0.5], fov: 27 }, b: { von: [-1.2, 0.42, 9.5], auf: [-1.55, 0.6, 0.5], fov: 26 }, ease: 'lin', speed: 0.7, wack: 0.02 },
        { bis: TAKT * 5, a: { cam: 2 } }] },
    /* ---------- Regen ---------- */
    s17a_sgp_regen: { dauer: 4.4, zeitlupe: 0.45, ao: true,
      vor: `TR.feld(1010, 0, [[-11, 2.4], [-23, -2.0], [-36, 1.8], [-50, -1.0]]); TR.sim(40, 33.3);`,
      kams: [{ a: { von: [2.8, 0.36, 8.5], auf: [0, 0.55, 0], fov: 28 }, b: { von: [1.6, 0.42, 7.0], auf: [0, 0.55, 0], fov: 26 }, ease: 'lin', wack: 0.008 }] },
    s18b_sgp_helm: { dauer: 2.3, seite: true, ao: false,
      vor: `TR.feld(2180, 0, [[16, 1.8], [30, -1.6], [47, 0.8]]); S.cam = 2; window.__camFix = null; TR.sim(50, 33.3);`, kams: [{ a: { cam: 2 } }] },
    s17b_vegas_regen: { dauer: 2.6, ao: true,
      vor: `TR.feld(1900, -0.5, [[-15, 1.5, 0.9], [-31, -1.5, 0.9]]); TR.sim(25, 33.3);`,
      kams: [{ a: { von: { s: 1988, lat: 5.6, h: 0.32 }, auf: [0, 0.5, 0], fov: 42 }, wack: 0.006 }] },
    s18a_spa_regen: { dauer: 2.2, zeitlupe: 0.5, ao: false,
      vor: `TR.feld(1150, 0, [[-11, 2.4], [-23, -2.2], [-34, 1.4], [-47, -2.0], [-58, 2.2], [-72, -1.5], [-84, 0.5]]); TR.sim(45, 33.3);`,
      kams: [{ a: { von: { s: 1410, lat: -0.6, h: 0.6 }, auf: [0, 0.55, 0], fov: 6.5 }, b: { von: { s: 1410, lat: -0.6, h: 0.6 }, auf: [0, 0.55, 0], fov: 7.5 }, ease: 'lin' }] },
    /* Varianten zur Auswahl (nur Proben) */
    s17a_v1: { dauer: 4.4, zeitlupe: 0.45, ao: true, vor: `TR.feld(1010, 0, [[-11, 2.4], [-23, -2.0], [-36, 1.8], [-50, -1.0]]); TR.sim(40, 33.3);`,
      kams: [{ a: { von: [2.3, 0.3, 6.2], auf: [0, 0.5, 0], fov: 30 }, b: { von: [1.3, 0.36, 5.4], auf: [0, 0.5, 0], fov: 28 }, ease: 'lin', wack: 0.008 }] },
    s17a_v2: { dauer: 4.4, zeitlupe: 0.45, ao: true, vor: `TR.feld(1430, 0, [[-11, 2.4], [-23, -2.0], [-36, 1.8], [-50, -1.0]]); TR.sim(40, 33.3);`,
      kams: [{ a: { von: [2.3, 0.3, 6.2], auf: [0, 0.5, 0], fov: 30 }, b: { von: [1.3, 0.36, 5.4], auf: [0, 0.5, 0], fov: 28 }, ease: 'lin', wack: 0.008 }] },
    s17a_v3: { dauer: 4.4, zeitlupe: 0.45, ao: true, vor: `TR.feld(1010, 0, [[14, 1.8], [27, -1.5], [-12, 2.0]]); TR.sim(40, 33.3);`,
      kams: [{ a: { von: [-1.6, 0.4, -5.5], auf: [0.3, 0.7, 4], fov: 40 }, b: { von: [-0.8, 0.5, -6.5], auf: [0.3, 0.7, 4], fov: 38 }, ease: 'lin', wack: 0.008 }] },
    s17b_v1: { dauer: 2.6, zeitlupe: 0.5, ao: true, vor: `TR.feld(1915, 1.5, [[-16, -2, 0.9], [-33, 2, 0.9]]); TR.sim(25, 33.3);`,
      kams: [{ a: { von: [6.0, 0.3, 1.2], auf: [342, 22, -496, 0], fov: 48 }, b: { von: [5.6, 0.3, 0.2], auf: [342, 22, -496, 0], fov: 46 }, ease: 'lin' }] },
    s17b_v2: { dauer: 2.6, zeitlupe: 0.5, ao: true, vor: `TR.feld(1915, 1.5, [[-16, -2, 0.9], [-33, 2, 0.9]]); TR.sim(25, 33.3);`,
      kams: [{ a: { von: [7.5, 0.22, 1.0], auf: [342, 18, -496, 0], fov: 52 }, b: { von: [7.2, 0.22, 0.2], auf: [342, 18, -496, 0], fov: 50 }, ease: 'lin' }] },
    s17b_v3: { dauer: 2.6, zeitlupe: 0.5, ao: true, vor: `TR.feld(4250, 0, [[-12, 2.4], [-25, -2], [-38, 2]]); TR.sim(30, 33.3);`,
      kams: [{ a: { von: [1.5, 0.3, 9], auf: [0, 0.6, 0], fov: 26 }, b: { von: [1.0, 0.34, 8], auf: [0, 0.6, 0], fov: 25 }, ease: 'lin' }] },
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
