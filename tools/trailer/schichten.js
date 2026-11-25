// Warteschlangen für tools/trailer/schicht.js (Fassung 4 vom 25.11.2026: alles neu mit 30 Bildern/s und der flüssigeren Aufnahmetechnik).
// Fertige Einstellungen werden übersprungen – wer alles neu rechnen will, löscht trailer-ausgabe/bilder/<Szene>.
// Höchstens drei Schichten gleichzeitig (vier haben die Maschine zum Neustart gebracht).
const legenden = [['AMO', 's11_amo'], ['RIN', 's11_rin'], ['SEN', 's11_sen,s12_cockpit88'], ['HAK', 's11_hak'], ['MSC', 's11_msc'], ['VET', 's11_vet']];
module.exports = {
  // Proben (Kontaktblätter in halber Auflösung) – vor dem Dreh ansehen
  pa: [
    { strecke: 'Singapur', fahrer: 'NOR', schritte: [
      { wetter: 'dry', szenen: 's06_sgp_kran,s08b_vorbei,s07_sgp_nah,s16a_sprint,s16b_ziel', probe: true },
      { wetter: 'heavy', szenen: 's19a_sgp_helm,s17a_sgp_regen,s18b_sgp_helm', probe: true } ] },
    { strecke: 'Spa', fahrer: 'VER', schritte: [{ wetter: 'heavy', szenen: 's19b_spa_helm,s18a_spa_regen', probe: true }] },
  ],
  pb: [
    { strecke: 'Monza', schritte: [{ fahrer: 'LEC', szenen: 's14_duell', probe: true, proben: 12 }, { fahrer: 'LEC', szenen: 's11_2026', probe: true }, { fahrer: 'SEN', szenen: 's12_cockpit88,s11_sen', probe: true }, { fahrer: 'HAK', szenen: 's11_hak', probe: true }] },
    { strecke: 'Abu Dhabi', fahrer: 'LEC', schritte: [{ szenen: 's03_ampel,s04_start,s05_profil,s08a_sonne', probe: true }] },
  ],
  pc: [
    { strecke: 'Las Vegas', fahrer: 'RUS', schritte: [{ szenen: 's09_sphere,s10_strip', probe: true }] },
    { strecke: 'Monaco', fahrer: 'RUS', schritte: [{ szenen: 's08c_rad,s08d_tcam', probe: true }] },
    { strecke: 'Genk', klasse: 'kart', fahrer: 'X', schritte: [{ szenen: 's13_kart', probe: true }] },
  ],
  pd: [   // Nachprobe: neue Stellen der Helm-Regen-Einstellungen, Regen-Nahaufnahme mit starrer Kamera
    { strecke: 'Singapur', fahrer: 'NOR', schritte: [{ wetter: 'heavy', szenen: 's19a_sgp_helm,s17a_sgp_regen', probe: true }] },
    { strecke: 'Spa', fahrer: 'VER', schritte: [{ wetter: 'heavy', szenen: 's19b_spa_helm', probe: true }] },
  ],
  // Dreh (rund 4.100 Renderbilder, gleichmäßig auf drei Schichten verteilt)
  a: [
    { strecke: 'Singapur', fahrer: 'NOR', schritte: [
      { wetter: 'dry', szenen: 's06_sgp_kran,s08b_vorbei,s07_sgp_nah,s16a_sprint,s16b_ziel' },
      { wetter: 'heavy', szenen: 's17a_sgp_regen', probe: true, proben: 8 },   // Blatt ansehen, während die Helm-Einstellungen rechnen
      { wetter: 'heavy', szenen: 's19a_sgp_helm,s18b_sgp_helm,s17a_sgp_regen' } ] },
    { strecke: 'Spa', fahrer: 'VER', schritte: [{ wetter: 'heavy', szenen: 's18a_spa_regen,s19b_spa_helm' }] },
  ],
  b: [
    { strecke: 'Abu Dhabi', fahrer: 'LEC', schritte: [{ szenen: 's03_ampel,s04_start,s05_profil,s08a_sonne' }] },
    { strecke: 'Monza', schritte: [{ fahrer: 'LEC', szenen: 's14_duell,s11_2026' }, ...legenden.map(([fahrer, szenen]) => ({ fahrer, szenen }))] },
  ],
  c: [
    { menue: true, schritte: [{ szenen: 's01_garage_fluegel,s02_garage_helm' }] },
    { strecke: 'Las Vegas', fahrer: 'RUS', schritte: [{ szenen: 's09_sphere,s10_strip' }] },
    { strecke: 'Monaco', fahrer: 'RUS', schritte: [{ szenen: 's08c_rad,s08d_tcam' }] },
    { strecke: 'Genk', klasse: 'kart', fahrer: 'X', schritte: [{ szenen: 's13_kart' }] },
  ],
};
