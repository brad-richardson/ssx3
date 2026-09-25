#!/usr/bin/env bash
# AU9 PCSX2 build: pristine copies, patch, build pcsx2-qt, two SHA reads.
set -euo pipefail
G=/home/brad/pcsx2-g7
A=/home/brad/au9
mkdir -p "$A/pre" "$A/logs"
ps -eo pid,comm,args | awk '$2 ~ /^(ninja|clang|clang\+\+|pcsx2-qt|gradle|cc1plus|java)$/ {print}' > "$A/prebuild-heavy.txt"
if [ -s "$A/prebuild-heavy.txt" ]; then cat "$A/prebuild-heavy.txt"; exit 20; fi
F="pcsx2/R5900OpcodeImpl.cpp pcsx2/SPU2/Mixer.cpp pcsx2/SPU2/spu2.cpp pcsx2/SPU2/Dma.cpp"
if [ -s "$A/pre-source-sha.txt" ]; then for f in $F; do cp "$A/pre/$(basename $f)" $G/pcsx2/$f; done; sha256sum -c "$A/pre-source-sha.txt"; else
for f in $F; do cp $G/pcsx2/$f "$A/pre/$(basename $f)"; done
sha256sum "$A/pre/"* > "$A/pre-source-sha.txt"; fi
python3 "$A/au9_patch.py"
: > "$A/au9-hunk.diff"; for f in $F; do diff -u "$A/pre/$(basename $f)" $G/pcsx2/$f >> "$A/au9-hunk.diff" || true; done
nice cmake --build "$G/pcsx2/build" --target pcsx2-qt -j16 > "$A/build.log" 2>&1 || { grep -B2 -A6 'error' "$A/build.log" | head -60; exit 1; }
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" > "$A/bin-sha-read1.txt"
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" > "$A/bin-sha-read2.txt"
diff -u "$A/bin-sha-read1.txt" "$A/bin-sha-read2.txt"
cat "$A/bin-sha-read1.txt"
