// Garage (Showroom im Hauptmenü) für Trailer-Bilder: eigene Kamera, Vollbild, echte Schärfentiefe. Wird im Studio (--menue) ausgewertet.
// Schärfentiefe: jedes Zwischenbild wird von einem anderen Punkt der Blende aus gezeichnet; gemittelt wird gleitend über die letzten n Zwischenbilder.
// So kostet ein Trailerbild nur 3 statt 12 Zeichnungen – bei den langsamen Kamerafahrten der Garage fällt die längere „Belichtung“ nicht auf.
window.TRS = {
  ring: [], n: 12, k: 0,
  // Kamera in Bühnen-Koordinaten (Auto: Nase bei x ≈ −3,3, Heck bei x ≈ +2,9, Mitte z = 0): Position p, Blickziel t, Bildwinkel fov (Grad)
  cam(p, t, fov = 30, roll = 0) { const c = SHOW.cam; SHOW.stage.updateMatrixWorld(); const P = new THREE.Vector3(...p).applyMatrix4(SHOW.stage.matrixWorld), T = new THREE.Vector3(...t).applyMatrix4(SHOW.stage.matrixWorld);
    c.position.copy(P); c.up.set(0, 1, 0); c.lookAt(T); if (roll) c.rotateZ(roll); c.fov = fov; c.aspect = innerWidth / innerHeight; c.clearViewOffset(); c.updateProjectionMatrix(); c.updateMatrixWorld(); TRS.P = P; TRS.T = T; TRS.fov = fov; TRS.roll = roll; },
  draw() { const on = ENVP.on, et = ENVP.tex; ENVP.on = true; if (SHOW.env) ENVP.tex = SHOW.env; renderer.setRenderTarget(null); renderer.render(SHOW.scene, SHOW.cam); ENVP.tex = et; ENVP.on = on; },
  // LED-Wand und Lichtlauf auf einen Zeitpunkt stellen
  wall(t) { SHOW.t = t; wallDraw(t); if (SHOW.sweep) SHOW.sweep.offset.x = (-t * 0.035) % 1; },
  // Kamerafahrt festlegen: a → b mit { p, t, f (Schärfepunkt, sonst t), fov, ap (Blende in m) }
  setz(a, b, o = {}) { TRS.a = a; TRS.b = b || a; TRS.ease = o.ease || 'io'; TRS.n = o.n || 12; TRS.ring = []; TRS.k = 0; document.querySelector('#menu').style.opacity = 0; window.__norender = true; return 'ok'; },
  wert(u) { const e = TRS.ease === 'lin' ? u : u * u * (3 - 2 * u), A = TRS.a, B = TRS.b, m = (x, y) => x + (y - x) * e, v = (x, y) => x.map((q, i) => m(q, y[i]));
    return { p: v(A.p, B.p), t: v(A.t, B.t), f: v(A.f || A.t, B.f || B.t), fov: m(A.fov, B.fov), ap: m(A.ap ?? 0.04, B.ap ?? 0.04) }; },
  // ein Zwischenbild: Kamera bei u (0…1), Wandzeit wt (s); der Blendenpunkt wandert mit jedem Aufruf weiter
  sub(u, wt = 0) { const W = TRS.wert(Math.max(0, Math.min(1, u))), c = SHOW.cam; SHOW.stage.updateMatrixWorld(); const M = SHOW.stage.matrixWorld;
    const P = new THREE.Vector3(...W.p).applyMatrix4(M), T = new THREE.Vector3(...W.t).applyMatrix4(M), F = new THREE.Vector3(...W.f).applyMatrix4(M);
    const fw = T.clone().sub(P).normalize(), rt = new THREE.Vector3().crossVectors(fw, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(rt, fw);
    const dF = F.clone().sub(P).dot(fw), F0 = P.clone().addScaledVector(fw, dF);   // Mitte der Schärfeebene auf der Blickachse
    const i = TRS.k++ % TRS.n, r = W.ap * Math.sqrt((i + 0.5) / TRS.n), w = i * 2.399963;
    c.position.copy(P).addScaledVector(rt, Math.cos(w) * r).addScaledVector(up, Math.sin(w) * r); c.up.set(0, 1, 0); c.lookAt(F0); c.fov = W.fov; c.aspect = innerWidth / innerHeight; c.clearViewOffset(); c.updateProjectionMatrix(); c.updateMatrixWorld();
    TRS.wall(wt); TRS.draw(); const gl = renderer.getContext(), buf = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4); gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, buf);
    TRS.ring.push(buf); if (TRS.ring.length > TRS.n) TRS.ring.shift(); return TRS.ring.length; },
  mittel(typ = 'image/jpeg', q = 0.96) { TR.akStart(); for (const r of TRS.ring) TR.akAdd(1, r); return TR.akEnde(typ, q); },
  // Standbild mit Schärfentiefe (für Proben): n Bilder mit versetzter Kamera, scharf auf dem Blickziel
  dof(n = 32, ap = 0.05, typ, q) { const c = SHOW.cam, P = TRS.P.clone(), T = TRS.T, fw = T.clone().sub(P).normalize(), rt = new THREE.Vector3().crossVectors(fw, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(rt, fw);
    TR.akStart(); for (let i = 0; i < n; i++) { const r = ap * Math.sqrt((i + 0.5) / n), w = i * 2.399963; c.position.copy(P).addScaledVector(rt, Math.cos(w) * r).addScaledVector(up, Math.sin(w) * r); c.up.set(0, 1, 0); c.lookAt(T); if (TRS.roll) c.rotateZ(TRS.roll); c.updateMatrixWorld(); TRS.draw(); TR.akAdd(); }
    c.position.copy(P); return TR.akEnde(typ, q); },
};
document.querySelector('#menu').style.opacity = 0; window.__norender = true;
