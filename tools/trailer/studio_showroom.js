// Showroom (Garage im Hauptmenü) für Trailer-Bilder: eigene Kamera, Vollbild, Schärfentiefe. Wird im Studio (--menue) ausgewertet.
window.TRS = {
  // Kamera in Bühnen-Koordinaten: Position p, Blickziel t, Bildwinkel fov (Grad), optional seitliche Neigung
  cam(p, t, fov = 30, roll = 0) { const c = SHOW.cam; SHOW.stage.updateMatrixWorld(); const P = new THREE.Vector3(...p).applyMatrix4(SHOW.stage.matrixWorld), T = new THREE.Vector3(...t).applyMatrix4(SHOW.stage.matrixWorld);
    c.position.copy(P); c.up.set(0, 1, 0); c.lookAt(T); if (roll) c.rotateZ(roll); c.fov = fov; c.aspect = innerWidth / innerHeight; c.clearViewOffset(); c.updateProjectionMatrix(); c.updateMatrixWorld(); TRS.P = P; TRS.T = T; TRS.fov = fov; TRS.roll = roll; },
  draw() { const on = ENVP.on, et = ENVP.tex; ENVP.on = true; if (SHOW.env) ENVP.tex = SHOW.env; renderer.setRenderTarget(null); renderer.render(SHOW.scene, SHOW.cam); ENVP.tex = et; ENVP.on = on; },
  // LED-Wand und Lichtlauf auf einen Zeitpunkt stellen
  wall(t) { SHOW.t = t; wallDraw(t); if (SHOW.sweep) SHOW.sweep.offset.x = (-t * 0.035) % 1; },
  // Schärfentiefe: n Bilder mit versetzter Kamera (Blende ap in m), scharf auf dem Blickziel; liefert Data-URL
  dof(n = 32, ap = 0.05, typ, q) { const c = SHOW.cam, P = TRS.P.clone(), T = TRS.T, fw = T.clone().sub(P).normalize(), rt = new THREE.Vector3().crossVectors(fw, new THREE.Vector3(0, 1, 0)).normalize(), up = new THREE.Vector3().crossVectors(rt, fw);
    TR.akStart(); for (let i = 0; i < n; i++) { const r = ap * Math.sqrt((i + 0.5) / n), w = i * 2.399963; c.position.copy(P).addScaledVector(rt, Math.cos(w) * r).addScaledVector(up, Math.sin(w) * r); c.up.set(0, 1, 0); c.lookAt(T); if (TRS.roll) c.rotateZ(TRS.roll); c.updateMatrixWorld(); TRS.draw(); TR.akAdd(); }
    c.position.copy(P); return TR.akEnde(typ, q); },
};
document.querySelector('#menu').style.opacity = 0; window.__norender = true;
