@echo off
rem QC-Bot per Doppelklick starten: fragt nach Strecken und Umfang, faehrt unsichtbar im Hintergrund, oeffnet am Ende den Bericht.
chcp 65001 >nul
cd /d "%~dp0.."
echo.
echo  ===  Strecken-QC  ===
echo.
python qc/run.py --list
echo.
set "TRACKS="
set /p "TRACKS=Strecken (Schluessel mit Leerzeichen, leer = alle): "
echo.
echo  1 = schnell   (eine Runde je Strecke, Kamera wechselt in der Runde)
echo  2 = gruendlich (eine Runde je Kamera - alle Strecken ca. 2 Stunden)
set "MODE=1"
set /p "MODE=Umfang [1]: "
set "OPT="
if "%MODE%"=="1" set "OPT=--quick"
echo.
python qc/run.py %TRACKS% %OPT%
echo.
pause
