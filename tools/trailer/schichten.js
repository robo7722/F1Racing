// Warteschlangen für tools/trailer/schicht.js: drei Schichten laufen gleichzeitig (Ports 8821–8823).
// Reihenfolge: zuerst die Proben noch ungeprüfter Einstellungen (billig), dann die geprüften rechnen – so bleibt Zeit, die Proben anzusehen und den Drehplan zu ändern.
const legenden = [['AMO', 's11_amo'], ['RIN', 's11_rin'], ['SEN', 's11_sen,s12_cockpit88'], ['HAK', 's11_hak'], ['MSC', 's11_msc'], ['VET', 's11_vet']];
module.exports = {
  a: [
    { strecke: 'Singapur', fahrer: 'NOR', schritte: [
      { wetter: 'heavy', szenen: 's17a_sgp_regen,s18b_sgp_helm', probe: true },
      { wetter: 'dry', szenen: 's06_sgp_luft,s07_sgp_nah,s16a_sprint,s16b_ziel' },
      { wetter: 'heavy', szenen: 's17a_sgp_regen,s18b_sgp_helm' } ] },
    { strecke: 'Spa', fahrer: 'VER', schritte: [{ wetter: 'heavy', szenen: 's18a_spa_regen', probe: true }, { wetter: 'heavy', szenen: 's18a_spa_regen' }] },
    { strecke: 'Genk', klasse: 'kart', fahrer: 'X', schritte: [{ szenen: 's13_kart', probe: true }, { szenen: 's13_kart' }] },
  ],
  b: [
    { strecke: 'Monaco', fahrer: 'RUS', schritte: [{ szenen: 's08a_helm,s08b_tunnel,s08c_rad,s08d_tcam', probe: true }] },
    { menue: true, schritte: [{ szenen: 's01_garage_fluegel,s02_garage_helm', probe: true }] },
    { strecke: 'Abu Dhabi', fahrer: 'LEC', schritte: [{ szenen: 's03_ampel,s04_start,s05_profil' }] },
    { strecke: 'Monaco', fahrer: 'RUS', schritte: [{ szenen: 's08a_helm,s08b_tunnel,s08c_rad,s08d_tcam' }] },
    { menue: true, schritte: [{ szenen: 's01_garage_fluegel,s02_garage_helm' }] },
  ],
  c: [
    { strecke: 'Las Vegas', fahrer: 'RUS', schritte: [
      { wetter: 'heavy', szenen: 's17b_vegas_regen', probe: true },
      { wetter: 'dry', szenen: 's09_sphere,s10_strip' },
      { wetter: 'heavy', szenen: 's17b_vegas_regen' } ] },
    { strecke: 'Monza', schritte: [{ fahrer: 'LEC', szenen: 's14_duell' }, ...legenden.map(([fahrer, szenen]) => ({ fahrer, szenen }))] },
  ],
};
