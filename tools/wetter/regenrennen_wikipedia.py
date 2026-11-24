"""Wie oft war ein Formel-1-Rennen auf einer Strecke wirklich nass? Liest das Feld „Weather“ aus den Infoboxen der englischen
Wikipedia-Rennseiten (2000–heute) und zählt je Strecke die Rennen mit Regen/nasser Fahrbahn. Erste Quelle ist DBpedia (ein Abzug aller
Infoboxen, eine einzige Abfrage); was dort fehlt (die jüngsten Rennen), kommt direkt von Wikipedia – langsam, weil Wikipedia nur wenige
Seiten je Minute herausgibt. `--nur-dbpedia` überspringt das, `--nur-cache` nimmt zusätzlich nur, was schon geladen ist.

    python tools/wetter/regenrennen_wikipedia.py          schreibt regenrennen_ergebnis.json, druckt je Strecke Rennen/nass und alle Wettertexte

Zusammen mit regenwahrscheinlichkeit.py (Wetterarchiv) ergibt das die Regenwahrscheinlichkeit im Spiel – siehe docs/WETTER.md.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

J = lambda a, b, *aus: [y for y in range(a, b + 1) if y not in aus]
# Strecke -> Liste (Name des Grand Prix, Jahre). Nur Rennen, die wirklich auf dieser Strecke gefahren wurden.
RENNEN = {
    'mel':   [('Australian Grand Prix', J(2000, 2026, 2020, 2021))],
    'chn':   [('Chinese Grand Prix', J(2004, 2019) + [2024, 2025, 2026])],
    'suz':   [('Japanese Grand Prix', J(2000, 2006) + J(2009, 2019) + J(2022, 2026))],
    'bhr':   [('Bahrain Grand Prix', J(2004, 2026, 2011)), ('Sakhir Grand Prix', [2020])],
    'jed':   [('Saudi Arabian Grand Prix', J(2021, 2026))],
    'mia':   [('Miami Grand Prix', J(2022, 2026))],
    'mtl':   [('Canadian Grand Prix', J(2000, 2026, 2009, 2020, 2021))],
    'mc':    [('Monaco Grand Prix', J(2000, 2026, 2020))],
    'bcn':   [('Spanish Grand Prix', J(2000, 2025)), ('Barcelona-Catalunya Grand Prix', [2026])],
    'rbr':   [('Austrian Grand Prix', J(2000, 2003) + J(2014, 2026)), ('Styrian Grand Prix', [2020, 2021])],
    'sil':   [('British Grand Prix', J(2000, 2026)), ('70th Anniversary Grand Prix', [0])],
    'spa':   [('Belgian Grand Prix', J(2000, 2026, 2003, 2006))],
    'hun':   [('Hungarian Grand Prix', J(2000, 2026))],
    'zan':   [('Dutch Grand Prix', J(2021, 2026))],
    'monza': [('Italian Grand Prix', J(2000, 2026))],
    'mad':   [('Spanish Grand Prix', [2026])],
    'baku':  [('European Grand Prix', [2016]), ('Azerbaijan Grand Prix', J(2017, 2026, 2020))],
    'sgp':   [('Singapore Grand Prix', J(2008, 2026, 2020, 2021))],
    'cota':  [('United States Grand Prix', J(2012, 2026, 2020))],
    'mex':   [('Mexican Grand Prix', J(2015, 2019)), ('Mexico City Grand Prix', J(2021, 2026))],
    'bra':   [('Brazilian Grand Prix', J(2000, 2019)), ('São Paulo Grand Prix', J(2021, 2026))],
    'vegas': [('Las Vegas Grand Prix', J(2023, 2026))],
    'qat':   [('Qatar Grand Prix', [2021, 2023, 2024, 2025, 2026])],
    'yas':   [('Abu Dhabi Grand Prix', J(2009, 2026))],
    # Nordschleife: als Näherung die Formel-1-Rennen auf dem Nürburgring (gleiche Lage in der Eifel)
    'nos':   [('European Grand Prix', J(2000, 2007)), ('German Grand Prix', [2009, 2011, 2013]), ('Eifel Grand Prix', [2020])],
}
NASS = re.compile(r'rain|wet|damp|drizzl|shower|storm|thunder|humid track', re.I)
KEIN_REGEN = re.compile(r'no rain|without rain|threat(ening)? (of )?rain|chance of rain|rain (before|earlier|overnight|in the morning)', re.I)   # Regen erwähnt, aber nicht im Rennen


def titel(name, jahr):
    return name if jahr == 0 else f'{jahr} {name}'


def holen(titelliste, cache):
    """Wettertexte holen. Wikipedia lässt von einer Adresse nur wenige Seiteninhalte je Minute zu (sonst HTTP 429): kleine Portionen mit Pause,
    Ergebnisse werden in `cache` gemerkt – ein abgebrochener Lauf macht dort weiter."""
    out = json.load(open(cache)) if os.path.exists(cache) else {}
    offen = [t for t in titelliste if t not in out]; n = 6
    while offen:
        teil = offen[:n]
        url = ('https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&rvsection=0'
               '&format=json&formatversion=2&redirects=1&titles=' + urllib.parse.quote('|'.join(teil)))
        req = urllib.request.Request(url, headers={'User-Agent': 'f1-wetter-analyse/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                j = json.load(r)
        except Exception as e:
            print(f'  Wikipedia: {e} – warte ({len(offen)} offen)', file=sys.stderr, flush=True); n = max(3, n - 1); time.sleep(60); continue
        um = {x['to']: x['from'] for x in j['query'].get('redirects', [])}
        um.update({x['to']: um.get(x['from'], x['from']) for x in j['query'].get('normalized', [])})
        for t in teil:
            out[t] = ''   # gefragt; bleibt leer, wenn die Seite fehlt oder kein Wetter nennt
        for p in j['query']['pages']:
            if p.get('missing') or 'revisions' not in p:
                continue
            t = p['revisions'][0]['slots']['main']['content']
            m = re.search(r'\|\s*[Ww]eather\s*=\s*([^\n]*)', t)
            if m:
                w = re.sub(r'<ref[^>]*/>|<ref.*?</ref>|<ref.*$|\{\{[^}]*\}\}|<[^>]+>|\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', lambda x: x.group(1) or '', m.group(1)).strip()
                out[um.get(p['title'], p['title'])] = w
        json.dump(out, open(cache, 'w'), ensure_ascii=False)
        offen = offen[n:]; print(f'  {len(titelliste) - len(offen)}/{len(titelliste)}', file=sys.stderr, flush=True)
        if offen:
            time.sleep(22)
    return out


def dbpedia():
    """Alle Wetterangaben der Grand-Prix-Seiten in EINER Abfrage aus DBpedia (Abzug der Wikipedia-Infoboxen; neueste Rennen können fehlen)."""
    q = ("SELECT ?gp ?w WHERE { ?gp <http://dbpedia.org/property/weather> ?w . FILTER(regex(str(?gp), '_Grand_Prix$')) } LIMIT 10000")
    url = 'https://dbpedia.org/sparql?' + urllib.parse.urlencode({'query': q, 'format': 'application/sparql-results+json'})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'f1-wetter-analyse/1.0'}), timeout=90) as r:
            j = json.load(r)
    except Exception as e:
        print('  DBpedia nicht erreichbar:', e, file=sys.stderr); return {}
    out = {}
    for b in j['results']['bindings']:
        t = urllib.parse.unquote(b['gp']['value'].rsplit('/', 1)[1]).replace('_', ' '); w = b['w']['value'].strip()
        if re.fullmatch(r'[-0-9.,]+', w):
            continue   # reine Temperaturzahlen
        out[t] = (out[t] + '; ' if t in out else '') + w
    return out


def main():
    alle = sorted({titel(n, y) for L in RENNEN.values() for n, ys in L for y in ys})
    cache = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--cache=')), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regenrennen_cache.json'))
    D = dbpedia(); print(f'  DBpedia: {sum(1 for t in alle if t in D)} von {len(alle)} Rennen', file=sys.stderr)
    if '--nur-dbpedia' in sys.argv:
        W = dict(D)
    elif '--nur-cache' in sys.argv:   # nichts nachladen: DBpedia + was schon im Zwischenspeicher liegt
        W = {**(json.load(open(cache)) if os.path.exists(cache) else {}), **D}
    else:
        W = {**holen([t for t in alle if t not in D], cache), **D}
    erg = {}
    for key, L in RENNEN.items():
        n = nass = 0; texte = []
        for name, ys in L:
            for y in ys:
                w = W.get(titel(name, y))
                if not w:
                    continue   # Seite fehlt oder Rennen noch nicht gefahren
                ist = bool(NASS.search(w)) and not KEIN_REGEN.search(w)
                n += 1; nass += ist; texte.append(f"{titel(name, y)}: {w} {'[NASS]' if ist else ''}")
        erg[key] = {'rennen': n, 'nass': nass, 'texte': texte}
        print(f'{key:6s} {n:3d} Rennen, {nass:2d} nass ({100 * nass / max(n, 1):3.0f} %)')
    json.dump(erg, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'regenrennen_ergebnis.json'), 'w'), indent=1, ensure_ascii=False)
    if '--texte' in sys.argv:
        for key, e in erg.items():
            print('\n== ' + key); print('\n'.join(e['texte']))


if __name__ == '__main__':
    main()
