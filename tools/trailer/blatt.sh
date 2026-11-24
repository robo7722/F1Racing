#!/bin/bash
# Kontaktblatt aus Bildern (untereinander, je <Breite> px):  tools/trailer/blatt.sh <Ausgabe.jpg> <Breite> <Bild1> <Bild2> …
out="$1"; w="$2"; shift 2; n=$#; args=(); f=""; i=0
for b in "$@"; do args+=(-i "$b"); f+="[$i]scale=$w:-2[v$i];"; i=$((i+1)); done
s=""; for ((k=0;k<n;k++)); do s+="[v$k]"; done
if [ "$n" -gt 1 ]; then ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${s}vstack=inputs=$n" -q:v 4 "$out"; else ffmpeg -v error -y -i "$1" -vf "scale=$w:-2" -q:v 4 "$out"; fi
