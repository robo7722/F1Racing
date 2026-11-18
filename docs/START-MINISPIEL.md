# Start-Minispiel (Kupplungsstart) – ab v2.80

Wunsch vom 18.11.2026: Beim Rennstart muss man die Kupplung halten, bis die Ampel ausgeht. Die Reaktionszeit wird gemessen.

## Ablauf

1. **Warten:** Ampel steht still, Hinweis „KUPPLUNG + GAS HALTEN“. Erst wenn Kupplung **und** Gas gleichzeitig gehalten werden, läuft der Countdown (rote Lichter) an.
   Mit Auto-Gas reicht die Kupplung.
2. **Countdown:** Hinweis „KUPPLUNG LOSLASSEN, WENN DIE AMPEL AUSGEHT“. Gas dreht den Motor hoch wie bisher.
3. **Ampel aus:** Uhr läuft, bis die Kupplung losgelassen wird → **Reaktionszeit** klein oben in der Mitte („REAKTION 0,231 s“), bleibt das ganze Rennen stehen.
   Bis dahin bleibt das Auto stehen (Motor weiter im „vor dem Start“-Zustand).
4. **Fehlstart:** Kupplung vor dem Erlöschen losgelassen → großes „FEHLSTART“, oben „FEHLSTART · +1,0 s“. Ampel läuft normal weiter, das Auto rollt erst **1 s nach dem Erlöschen** los.
5. Danach erscheinen wieder die Richtungstasten und die ERS-Taste. Kein „LOS!“-Text mehr.

## Belegung

| Gerät | Kupplung | Gas |
|---|---|---|
| Touch | große gelbe Taste **links** (statt der Pfeile, solange der Start läuft) | Gas-Taste |
| Controller | **Bremse** (L2/LT oder X/□) | R2/RT oder A/✕ |
| Tastatur | S / ↓ / Leertaste | W / ↑ |

## Technik (index.html)

- Zustand `SG` (`on`, `armed`, `jump`, `go`, `react`, `outT`), Funktionen `sgReset`, `sgLights`, `sgRace`, `sgGo`, `sgShow`, `sgHint` beim Eingabe-Block.
- `preGo()` ersetzt überall `raceState === 'lights'` für Motorsound, Drehzahl, Lenkrad-LEDs und Anzeigen: gilt auch nach dem Erlöschen, solange die Kupplung noch gehalten wird.
- `updatePlayer`: `canDrive = raceState === 'race' && SG.go`.
- Reaktionszeit in **echter Zeit** (`performance.now()`), nicht Spielzeit – ruckelnde Bilder würden sie sonst schönen. Touch/Tastatur: Zeitpunkt des Loslass-Ereignisses selbst; Controller: pro Bild abgefragt. Pause während des Wartens wird abgezogen.
- Fehlstart-Wartezeit (1 s) in Spielzeit (`raceTime`), wie der Rest des Rennens.
- KI-/Testfahrten überspringen das Spiel: `window.__auto`, `window.__plAI` (QC-Bot) oder `window.__noStartGame = true`.
- KI-Gegner starten unverändert nach ihrer eigenen Reaktionszeit (`c.react`).

## Test

Playwright mit Touch-Emulation (640×300, Grafik „low“, sonst ist SwiftShader zu langsam): Countdown startet erst mit beiden Tasten, Pfeile/ERS ausgeblendet,
nach Loslassen Reaktionszeit sichtbar und Pfeile/ERS wieder da; Fehlstart: Auto steht bis `raceTime` = 1,0 s, dann fährt es.

## Ideen für später

- Beste Reaktionszeit speichern / im Ergebnis anzeigen.
- Fehlstart optional mit Durchfahrtsstrafe statt 1 s Wartezeit.
