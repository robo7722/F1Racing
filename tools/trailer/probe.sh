#!/bin/bash
# Probebild aus dem Studio:  tools/trailer/probe.sh <Port> <Datei.jpg> '<Code vor dem Bild>'   (zeichnet danach 2 Bilder und speichert die Seite)
curl -s "localhost:$1/eval" --data "$3; TR.sim(2, 16.667, true); TR.info()" | cut -c1-220; echo
curl -s "localhost:$1/bild" --data "{\"datei\":\"$2\",\"jpg\":88}" > /dev/null
