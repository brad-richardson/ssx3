#!/bin/bash
# archive_lanes.sh <dir>... — tar each ~/dev/ssx3-work/<dir> (or an absolute path) to the SSD,
# verify the SSD copy's SHA-256 against the stream written, then delete the source.
# ExFAT SSD: one tar per tree (never mv small-file trees), COPYFILE_DISABLE=1.
set -u
DEST="/Volumes/Extreme SSD/ssx3-archive/$(date +%Y-%m-%d)"
export COPYFILE_DISABLE=1
mkdir -p "$DEST" || { echo "no SSD"; exit 1; }
for d in "$@"; do
  case "$d" in /*) src="$d";; *) src="$HOME/dev/ssx3-work/$d";; esac
  [ -d "$src" ] || { echo "SKIP missing $src"; continue; }
  name=$(echo "$src" | sed "s#$HOME/dev/##; s#/#_#g")
  out="$DEST/$name.tar"
  w=$(tar -C "$(dirname "$src")" -cf - "$(basename "$src")" | tee "$out" | shasum -a 256 | cut -d' ' -f1)
  r=$(shasum -a 256 "$out" | cut -d' ' -f1)
  if [ -n "$w" ] && [ "$w" = "$r" ]; then
    echo "$name $w $(du -sh "$out" | cut -f1)" >> "$DEST/MANIFEST.txt"
    rm -rf -- "$src" && echo "OK $name $w"
  else
    echo "FAIL $name write=$w read=$r (source kept)"
  fi
done
