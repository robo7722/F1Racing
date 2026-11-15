"""Sound-Effekte über die ElevenLabs-API erzeugen (v2.00) – siehe docs/SOUNDS.md.

Jeder Eintrag: Name -> (Prompt, Länge s, Prompt-Treue, Loop). Je Eintrag VARIANTEN Aufnahmen (sounds/roh/v2/<name>_<k>.mp3);
die beste wählt tools/sounds/aufbereiten_v2.py nach Messwerten aus. Vorhandene Dateien werden nicht neu erzeugt (kostet Credits).
Aufruf: python tools/sounds/erzeugen.py [name ...]   (API-Schlüssel kommt über den Proxy bzw. ELEVEN_API_KEY)
"""
import json, os, sys, time, urllib.request, urllib.error

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sounds', 'roh', 'v2')
VARIANTEN = int(os.environ.get('VARIANTEN', 2))
NO = ', no engine, no music, no voices'
SFX = {
    # Roadster (MX-5 ND2, 2,0-l-Vierzylinder, Sportauspuff)
    'mx5_leer': ('Mazda MX-5 roadster 2.0 litre four-cylinder engine with sport exhaust idling steadily at 850 rpm, recorded close to the exhaust, smooth lumpy four-cylinder idle, constant, no revving, no music, no voices', 4, 0.7, True),
    'mx5_3000': ('Onboard recording of a Mazda MX-5 roadster 2.0 litre four-cylinder engine with sport exhaust running at a constant 3000 rpm under load, steady unchanging drone, no revving, no acceleration, no gear change, no music', 4, 0.8, True),
    'mx5_5000': ('Onboard recording of a Mazda MX-5 roadster 2.0 litre four-cylinder engine with sport exhaust at a constant 5000 rpm at full throttle, raspy steady drone, sustained, no revving, no acceleration, no gear change, no music', 4, 0.8, True),
    'mx5_7000': ('Onboard recording of a Mazda MX-5 roadster four-cylinder engine with sport exhaust screaming at a constant 7000 rpm near the rev limiter, full throttle, sustained steady unchanging high-pitched drone, no revving, no acceleration, no gear change, no music', 4, 0.85, True),
    'mx5_schub': ('Mazda MX-5 roadster four-cylinder with sport exhaust on overrun, throttle closed at 5000 rpm while braking, exhaust burble, crackles and pops, steady, no acceleration, no gear change, no music', 3, 0.75, True),
    # v2.01: zweiter Versuch (realistischer: Onboard auf der Rennstrecke, Ansaug- und Auspuffklang), je 4 Varianten
    'mx5b_leer': ('Close recording of a Mazda MX-5 Miata ND2 with sports exhaust idling at 850 rpm in the pit lane, naturally aspirated 2.0 litre inline-four, slightly lumpy steady idle, realistic field recording, no revving, no music, no voices', 4, 0.75, True),
    'mx5b_tief': ('In-car onboard audio of a Mazda MX-5 Miata ND2 club race car on a race track, naturally aspirated 2.0 litre inline-four with a free-flowing sports exhaust, light throttle in fifth gear holding a steady 2500 rpm, low deep exhaust drone, realistic field recording, no gear change, no revving up or down, no music, no voices', 4, 0.75, True),
    'mx5b_mittel': ('In-car onboard audio of a Mazda MX-5 Miata ND2 club race car on a race track, naturally aspirated 2.0 litre inline-four with a free-flowing sports exhaust, full throttle in third gear holding a steady 4500 rpm, strong raspy exhaust note and intake roar, realistic field recording, no gear change, no revving up or down, no music, no voices', 4, 0.75, True),
    'mx5b_hoch': ('In-car onboard audio of a Mazda MX-5 Miata ND2 club race car on a race track, naturally aspirated 2.0 litre inline-four with a free-flowing sports exhaust, full throttle holding a steady 6500 rpm near the redline, loud raspy four-cylinder howl and intake roar, realistic field recording, no gear change, no revving up or down, no music, no voices', 4, 0.75, True),
    'mx5b_schub': ('In-car onboard audio of a Mazda MX-5 Miata ND2 club race car on a race track, naturally aspirated 2.0 litre inline-four with a free-flowing sports exhaust, lifting off the throttle at 5000 rpm while braking for a corner, exhaust burble and occasional crackles on overrun, realistic field recording, no acceleration, no gear change, no music, no voices', 3, 0.7, True),
    # Einschläge F1/F2 (Carbon), Roadster (Stahlblech), Kart
    'cf_leicht': ('Single light contact between two carbon fibre racing cars: a short dull tap as a front wing endplate touches a rear tyre, rubber thud and small carbon click, close mic, dry, one hit only' + NO, 0.8, 0.75, False),
    'cf_auto': ('Single hard side impact between two open-wheel formula racing cars: loud wheel-to-wheel rubber bang, carbon fibre bodywork cracking, small debris clatter on asphalt, dry, one impact, no explosion' + NO, 1.2, 0.75, False),
    'cf_armco': ('Formula racing car hitting a steel armco guardrail: single loud metallic clang and hollow boom of the corrugated steel barrier, carbon fibre crunch, short metallic ringing rattle of the rail, one impact, no explosion' + NO, 1.5, 0.75, False),
    'cf_beton': ('Formula racing car slamming into a concrete wall: single deep heavy thud, carbon fibre shattering, pieces clattering on the ground, no metallic ringing, one impact, no explosion' + NO, 1.5, 0.75, False),
    'reifenstapel': ('Car crashing into a tyre barrier: single heavy muffled rubber thump of stacked tyres absorbing the hit, short bounce and wobble of the tyres, one impact' + NO, 1.2, 0.75, False),
    # 'cf_schwer' (v2.01 entfernt, zu übertrieben):
    'cf_schwer': ('Heavy high-speed formula racing car crash into a barrier: violent impact, carbon fibre bodywork breaking into pieces, a wheel bouncing away, debris scattering and sliding on asphalt, no fire, no explosion' + NO, 2.5, 0.75, False),
    'stahl_leicht': ('Two small sports cars lightly touching: single short dull metal bump of bumpers, small plastic knock, one hit only' + NO, 0.8, 0.75, False),
    'stahl_auto': ('Two small sports cars colliding side to side: single steel sheet metal crunch, door panel denting, plastic bumper cracking, tiny glass tinkle, one impact, no horn' + NO, 1.2, 0.75, False),
    'stahl_wand': ('Small sports car hitting a steel guardrail: single heavy steel body crunch, plastic bumper shattering, the guardrail clanging, short metal screech, one impact' + NO, 1.5, 0.75, False),
    'stahl_schwer': ('Heavy high-speed sports car crash into a wall: violent steel body crunch, glass shattering, plastic parts breaking off and scattering on asphalt, no fire, no explosion' + NO, 2.5, 0.75, False),
    'kart_kart': ('Two racing go-karts bumping into each other: single hollow plastic sidepod bang and a steel tube frame knock, small rubber tyre bounce, one impact' + NO, 0.8, 0.75, False),
    'kart_wand': ('Racing go-kart crashing into a barrier of stacked tyres: single soft rubber thump, plastic front bumper knock, frame rattle, one impact' + NO, 1.0, 0.75, False),
    # Schaben (Loops)
    'schaben_metall': ('Continuous scraping of a car body sliding along a steel armco guardrail, steady metal grinding screech and rattle, constant, no impact' + NO, 3, 0.75, True),
    'schaben_beton': ('Continuous rough grinding of carbon fibre bodywork sliding along a concrete wall, steady abrasive scraping, constant, no impact' + NO, 3, 0.75, True),
    'schaben_auto': ('Two racing cars rubbing wheels side by side, continuous tyre rubber squealing and scrubbing against each other with light bodywork rubbing, constant' + NO, 3, 0.75, True),
    # Untergrund
    'kies': ('Car tyres ploughing fast through a gravel trap, continuous crunching of gravel, stones spraying and pelting the underbody and wheel arches, constant' + NO, 4, 0.75, True),
    'rasen': ('Car tyres sliding fast across grass and soft soil, continuous swishing rumble and bumpy thumping of the suspension, constant' + NO, 4, 0.75, True),
    'kerb': ('Race car tyres running over red and white serrated rumble strip kerbs at speed, continuous rapid drumming brrrrr vibration, constant' + NO, 3, 0.75, True),
    'kies_einschlag': ('Car leaving the asphalt and plunging into a gravel trap: sudden loud crunch of gravel spraying up, stones hitting the bodywork, single event' + NO, 1.2, 0.75, False),
    # Reifen, Wind
    'quietschen_slick': ('Racing slick tyres scrubbing and squealing under heavy cornering on dry asphalt, continuous low grainy squeal, constant' + NO, 3, 0.75, True),
    'quietschen_strasse': ('Sports car road tyres squealing loudly while sliding through a corner on asphalt, continuous high tyre screech, constant' + NO, 3, 0.75, True),
    'wind': ('Strong wind noise rushing past an open cockpit helmet at high speed, continuous turbulent air buffeting, constant' + NO, 4, 0.75, True),
}


def gen(prompt, dur, infl, loop):
    body = json.dumps({'text': prompt, 'duration_seconds': dur, 'prompt_influence': infl, 'loop': loop, 'model_id': 'eleven_text_to_sound_v2'}).encode()
    for attempt in range(12):
        req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192', data=body, method='POST',
                                     headers={'Content-Type': 'application/json', 'xi-api-key': os.environ.get('ELEVEN_API_KEY', 'proxy')})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            if e.code in (429, 500, 502, 503): time.sleep(5 + attempt * 5); continue
            raise RuntimeError(f'{e.code} {msg}')
    raise RuntimeError('zu viele Versuche')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or list(SFX)
    for n in names:
        p, d, i, l = SFX[n]
        for k in range(1, VARIANTEN + 1):
            f = os.path.join(OUT, f'{n}_{k}.mp3')
            if os.path.exists(f): continue
            try: data = gen(p, d, i, l); open(f, 'wb').write(data); print(n, k, len(data), 'Bytes', flush=True)
            except Exception as e: print(n, k, 'FEHLER', e, flush=True)
