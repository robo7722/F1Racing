"""Regenwahrscheinlichkeit je Strecke fürs Spiel: tatsächliche Regenrennen (regenrennen_ergebnis.json) und Wetterarchiv (regen_ergebnis.json) verrechnen.

    p = (nasse Rennen + K · Klimawert) / (Rennen + K)        mit K = 8

Der Klimawert zählt wie K zusätzliche Rennen. Strecken mit vielen Rennen (Spa, Silverstone, Monza …) folgen damit fast ganz ihrer echten
Rennstatistik; neue Strecken mit wenigen oder keinen Rennen (Las Vegas, Madrid, Kartbahnen) stützen sich auf das Wetterarchiv. Das gleicht
auch die Schwächen beider Quellen aus: Das Archiv (25-km-Raster) überschätzt Regen im Gebirge (Spielberg), eine Handvoll Rennen sagt wenig.

    python tools/wetter/regen_tabelle.py            druckt die Zeile für index.html (RAIN_P) und die Tabelle für docs/WETTER.md
    python tools/wetter/regen_tabelle.py --schreiben   trägt RAIN_P in index.html ein (Zeile mit /*@RAIN_P) und die Tabelle in docs/WETTER.md
"""
import json, os, re, sys

HIER = os.path.dirname(os.path.abspath(__file__))
K = 8
NAMEN = {'mel': 'Melbourne', 'chn': 'Shanghai', 'suz': 'Suzuka', 'bhr': 'Bahrain', 'jed': 'Jeddah', 'mia': 'Miami', 'mtl': 'Montréal', 'mc': 'Monaco', 'bcn': 'Barcelona',
         'rbr': 'Red Bull Ring', 'sil': 'Silverstone', 'spa': 'Spa', 'hun': 'Hungaroring', 'zan': 'Zandvoort', 'monza': 'Monza', 'mad': 'Madrid', 'baku': 'Baku', 'sgp': 'Singapur',
         'cota': 'Austin', 'mex': 'Mexiko-Stadt', 'bra': 'São Paulo', 'vegas': 'Las Vegas', 'qat': 'Lusail', 'yas': 'Abu Dhabi', 'nos': 'Nordschleife', 'genk': 'Genk', 'wack': 'Wackersdorf'}


def main():
    klima = json.load(open(os.path.join(HIER, 'regen_ergebnis.json')))['strecken']
    rennen = json.load(open(os.path.join(HIER, 'regenrennen_ergebnis.json')))
    zeilen, js = [], []
    for k, c in klima.items():
        r = rennen.get(k, {'rennen': 0, 'nass': 0}); n, nass = r['rennen'], r['nass']
        p = (nass + K * c['regen']) / (n + K)
        nasse_tage = c['regen'] * c['tage']
        stark = min(0.45, max(0.15, c['stark'])) if nasse_tage >= 12 else 0.25   # zu wenige Regentage im Archiv (Wüste): üblicher Anteil
        js.append(f'{k}: [{p:.3f}, {stark:.2f}]')
        zeilen.append(f"| {NAMEN.get(k, k)} | {c['termin']} {c['start']} Uhr | {100 * c['regen']:.0f} % | {nass} von {n} | **{100 * p:.0f} %** | {100 * stark:.0f} % |")
    zeile = 'const RAIN_P = { ' + ', '.join(js) + ' };'
    print(zeile + '\n')
    print('| Strecke | Termin 2026, Start (Ortszeit) | Wetterarchiv 2000–2024 | nasse F1-Rennen seit 2000 | im Spiel | davon starker Regen |\n|---|---|---|---|---|---|')
    print('\n'.join(zeilen))
    if '--schreiben' in sys.argv:
        f = os.path.join(HIER, '..', '..', 'index.html'); s = open(f, encoding='utf-8').read()
        neu, n = re.subn(r'const RAIN_P = \{[^;]*?\};(\s*/\*@RAIN_P)', lambda m: zeile + m.group(1), s)
        if n != 1:
            sys.exit('Zeile mit /*@RAIN_P in index.html nicht gefunden')
        open(f, 'w', encoding='utf-8').write(neu); print('\nindex.html aktualisiert')
        d = os.path.join(HIER, '..', '..', 'docs', 'WETTER.md'); t = open(d, encoding='utf-8').read()
        tab = '| Strecke | Termin 2026, Start (Ortszeit) | Wetterarchiv 2000–2024 | nasse F1-Rennen seit 2000 | im Spiel | davon starker Regen |\n|---|---|---|---|---|---|\n' + '\n'.join(zeilen)
        t2, n2 = re.subn(r'<!--RAIN_TABELLE-->.*?<!--/RAIN_TABELLE-->', lambda m: '<!--RAIN_TABELLE-->\n' + tab + '\n<!--/RAIN_TABELLE-->', t, flags=re.S)
        if n2 == 1:
            open(d, 'w', encoding='utf-8').write(t2); print('docs/WETTER.md aktualisiert')


if __name__ == '__main__':
    main()
