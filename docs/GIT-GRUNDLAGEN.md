# Git: Push, Pull und Pull Request – einfach erklärt

Stand: 14.11.2026

## Bild dazu
- **GitHub** = gemeinsamer Ordner in der Cloud (das „Original“ des Spiels).
- **Branch** = eine Arbeitskopie mit eigenem Namen, z. B. `ccr-a0a2146a-2b9jkt`. Dort wird gebaut, ohne das Original (`main`) anzufassen.
- **Commit** = ein gespeicherter Zwischenstand mit Beschreibung (wie „Speichern unter“ mit Notiz).

## Push
Eigene Commits **hochladen** auf GitHub („ich schiebe meine Änderungen hoch“).
Danach liegen sie auf GitHub im Branch – aber noch **nicht** im Original `main`.

## Pull
Änderungen von GitHub **herunterladen** in die eigene Kopie („ich hole mir den neuesten Stand“).

## Pull Request (PR)
Eine **Anfrage**: „Bitte übernimm die Änderungen aus meinem Branch ins Original `main`.“
- Man sieht darin alle Unterschiede (vorher/nachher) und kann sie prüfen und kommentieren.
- Erst mit **Merge** (Knopf „Merge pull request“ auf GitHub) landen die Änderungen wirklich in `main`.
- Der Name ist verwirrend: Man „bittet“ den Besitzer von `main`, die Änderungen zu sich zu **ziehen** (pull).

Einen „Push Request“ gibt es nicht – gemeint ist meist einfach der Push.

## Ablauf in diesem Projekt
1. Claude arbeitet im Branch, macht Commits und **pusht** sie.
2. Auf Wunsch legt Claude einen **Pull Request** nach `main` an.
3. Du schaust ihn an und klickst **Merge** → das Spiel in `main` ist aktualisiert (z. B. v1.73 Lenkrad).
