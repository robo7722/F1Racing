"""Regenwahrscheinlichkeit je Strecke aus echten Wetterdaten (für das Karriere-Wetter im Spiel).

Quelle: Open-Meteo Archiv (ERA5-Reanalyse, stündlicher Niederschlag am Ort der Strecke), Jahre 2000–2024.
Je Strecke zählen alle Tage im Fenster ±7 Tage um den Renntermin 2026 (Zusatzstrecken: breiteres Fenster über die Saison).
Ein Tag gilt als „Regenrennen“, wenn von einer Stunde vor dem Start bis zwei Stunden nach dem Start mindestens SCHWELLE mm fallen
(nasse Fahrbahn beim Start oder Regen im Rennen). „Stark“ heißt: in einer Stunde des Fensters mindestens STARK mm.

    python tools/wetter/regenwahrscheinlichkeit.py            rechnet alle Strecken, schreibt regen_ergebnis.json und druckt die Tabelle fürs Spiel
    python tools/wetter/regenwahrscheinlichkeit.py --cache DIR  Rohdaten dort zwischenspeichern (Standard: Temp-Ordner)

Es werden nur die Koordinaten der Strecken an api.open-meteo.com geschickt.
"""
import argparse, json, os, sys, tempfile, time, urllib.request
from datetime import date, datetime, timedelta

# Schlüssel wie in TRACKS: (Breite, Länge, Tag.Monat des Rennens 2026, Startstunde Ortszeit, halbe Fensterbreite in Tagen)
STRECKEN = {
    'mel':   (-37.8497, 144.9680, '08.03.', 15, 7),
    'chn':   (31.3389, 121.2197, '15.03.', 15, 7),
    'suz':   (34.8431, 136.5407, '29.03.', 14, 7),
    'bhr':   (26.0325, 50.5106, '12.04.', 18, 7),
    'jed':   (21.6319, 39.1044, '19.04.', 20, 7),
    'mia':   (25.9581, -80.2389, '03.05.', 16, 7),
    'mtl':   (45.5000, -73.5228, '24.05.', 16, 7),
    'mc':    (43.7347, 7.4206, '07.06.', 15, 7),
    'bcn':   (41.5700, 2.2611, '14.06.', 15, 7),
    'rbr':   (47.2197, 14.7647, '28.06.', 15, 7),
    'sil':   (52.0786, -1.0169, '05.07.', 15, 7),
    'spa':   (50.4372, 5.9714, '19.07.', 15, 7),
    'hun':   (47.5789, 19.2486, '26.07.', 15, 7),
    'zan':   (52.3888, 4.5409, '23.08.', 15, 7),
    'monza': (45.6156, 9.2811, '06.09.', 15, 7),
    'mad':   (40.4650, -3.6150, '13.09.', 15, 7),
    'baku':  (40.3725, 49.8533, '26.09.', 15, 7),
    'sgp':   (1.2914, 103.8640, '11.10.', 20, 7),
    'cota':  (30.1328, -97.6411, '25.10.', 15, 7),
    'mex':   (19.4042, -99.0907, '01.11.', 14, 7),
    'bra':   (-23.7036, -46.6997, '08.11.', 14, 7),
    'vegas': (36.1147, -115.1728, '21.11.', 20, 7),
    'qat':   (25.4900, 51.4542, '29.11.', 19, 7),
    'yas':   (24.4672, 54.6031, '06.12.', 17, 7),
    # Zusatzstrecken ohne festen Termin: ganze Saison (Mai–September) am Nachmittag
    'nos':   (50.3356, 6.9475, '15.07.', 14, 75),
    'genk':  (50.9886, 5.5636, '15.07.', 14, 75),
    'wack':  (49.3186, 12.1811, '15.07.', 14, 75),
}
JAHRE = range(2000, 2025)
SCHWELLE = 1.0   # mm im Fenster Start−1 h … Start+2 h (geeicht: mit 1,0 mm passt die Summe über alle Strecken zu den tatsächlich nassen F1-Rennen; 0,5 mm zählt bloßes Nieseln mit)
STARK = 2.0      # mm in einer Stunde des Fensters


def laden(key, lat, lon, cache):
    f = os.path.join(cache, f'om_{key}.json')
    if os.path.exists(f):
        return json.load(open(f))
    url = (f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}'
           f'&start_date={JAHRE[0]}-01-01&end_date={JAHRE[-1]}-12-31&hourly=precipitation&timezone=auto')
    for versuch in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                j = json.load(r)
            json.dump(j, open(f, 'w'))
            return j
        except Exception as e:   # Netzfehler oder Ratenbegrenzung: warten und noch einmal
            print(f'  {key}: {e} – neuer Versuch', file=sys.stderr)
            time.sleep(15 * (versuch + 1))
    raise SystemExit(f'{key}: keine Daten')


def auswerten(j, tagmonat, start, halb):
    zeit, mm = j['hourly']['time'], j['hourly']['precipitation']
    idx = {t: i for i, t in enumerate(zeit)}
    d, m = (int(x) for x in tagmonat.strip('.').split('.'))
    n = nass = stark = 0
    for jahr in JAHRE:
        for off in range(-halb, halb + 1):
            tag = date(jahr, m, d) + timedelta(days=off)
            i = idx.get(datetime(tag.year, tag.month, tag.day, start).strftime('%Y-%m-%dT%H:%M'))
            if i is None or i < 1 or i + 2 >= len(mm):
                continue
            w = [x or 0 for x in mm[i - 1:i + 3]]   # Stunde vor dem Start bis zwei Stunden danach (Werte = Summe der vorangegangenen Stunde)
            n += 1
            if sum(w) >= SCHWELLE:
                nass += 1
                if max(w) >= STARK:
                    stark += 1
    return n, nass, stark


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', default=os.path.join(tempfile.gettempdir(), 'f1-wetter'))
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    out = {}
    for key, (lat, lon, tm, start, halb) in STRECKEN.items():
        neu = not os.path.exists(os.path.join(a.cache, f'om_{key}.json'))
        n, nass, stark = auswerten(laden(key, lat, lon, a.cache), tm, start, halb)
        out[key] = {'termin': tm, 'start': start, 'tage': n, 'regen': round(nass / n, 3), 'stark': round(stark / max(nass, 1), 2)}
        print(f'{key:6s} {tm} {start:2d} Uhr  {n:4d} Tage  Regen {100 * nass / n:5.1f} %  davon stark {100 * stark / max(nass, 1):4.0f} %')
        if neu:
            time.sleep(2)
    json.dump({'quelle': 'Open-Meteo Archiv (ERA5), 2000–2024', 'schwelle_mm': SCHWELLE, 'stark_mm_h': STARK, 'strecken': out},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regen_ergebnis.json'), 'w'), indent=1, ensure_ascii=False)
    print('\nconst RAIN_P = { ' + ', '.join(f"{k}: [{v['regen']:.2f}, {v['stark']:.2f}]" for k, v in out.items()) + ' };')


if __name__ == '__main__':
    main()
