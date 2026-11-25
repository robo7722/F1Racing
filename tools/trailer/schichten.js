// Warteschlangen für tools/trailer/schicht.js (Fassung 3 vom 25.11.2026: Nachbesserungen nach Rückmeldung zum ersten Trailer).
// Fertige Einstellungen werden übersprungen – wer alles neu rechnen will, löscht trailer-ausgabe/bilder/<Szene>.
const legenden = [['AMO', 's11_amo'], ['RIN', 's11_rin'], ['SEN', 's11_sen,s12_cockpit88'], ['HAK', 's11_hak'], ['MSC', 's11_msc'], ['VET', 's11_vet']];
module.exports = {
  a: [
    { strecke: 'Singapur', fahrer: 'NOR', schritte: [
      { wetter: 'dry', szenen: 's06_sgp_kran,s07_sgp_nah,s08b_vorbei,s16a_sprint,s16b_ziel' },
      { wetter: 'heavy', szenen: 's17a_sgp_regen,s18b_sgp_helm' } ] },
    { strecke: 'Spa', fahrer: 'VER', schritte: [{ wetter: 'heavy', szenen: 's18a_spa_regen' }] },
    { strecke: 'Genk', klasse: 'kart', fahrer: 'X', schritte: [{ szenen: 's13_kart' }] },
  ],
  b: [
    { strecke: 'Abu Dhabi', fahrer: 'LEC', schritte: [{ szenen: 's08a_sonne', probe: true }, { szenen: 's03_ampel,s04_start,s05_profil,s08a_sonne' }] },
    { strecke: 'Las Vegas', fahrer: 'RUS', schritte: [
      { wetter: 'heavy', szenen: 's17b_vegas_regen', probe: true },
      { wetter: 'dry', szenen: 's09_sphere,s10_strip' },
      { wetter: 'heavy', szenen: 's17b_vegas_regen' } ] },
    { menue: true, schritte: [{ szenen: 's01_garage_fluegel,s02_garage_helm' }] },
    { strecke: 'Monaco', fahrer: 'RUS', schritte: [{ szenen: 's08c_rad,s08d_tcam' }] },
  ],
  c: [
    { strecke: 'Monza', schritte: [{ fahrer: 'LEC', szenen: 's14_duell,s11_2026' }, ...legenden.map(([fahrer, szenen]) => ({ fahrer, szenen }))] },
  ],
};
