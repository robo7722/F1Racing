#!/bin/bash
# Bild als Data-URL aus dem Studio holen und speichern:  tools/trailer/hol.sh <Port> <Datei> '<Code, der eine Data-URL liefert>'
curl -s "localhost:$1/eval" --data "$3" | sed 's/^data:image\/[a-z]*;base64,//' | base64 -d > "$2" && ls -la "$2" | awk '{print $5, $9}'
