#!/usr/bin/env bash
# AU8 PCSX2 build: backup, patch, build pcsx2-qt, two SHA reads.
set -euo pipefail
G=/home/brad/pcsx2-g7
A=/home/brad/au8
mkdir -p "$A/pre" "$A/logs"
ps -eo pid,comm,args | awk '$2 ~ /^(ninja|clang|clang\+\+|pcsx2-qt|gradle|cc1plus)$/ {print}' > "$A/prebuild-heavy.txt"
if [ -s "$A/prebuild-heavy.txt" ]; then cat "$A/prebuild-heavy.txt"; exit 20; fi
cp $G/pcsx2/pcsx2/R5900OpcodeImpl.cpp $G/pcsx2/pcsx2/SPU2/Mixer.cpp "$A/pre/"
sha256sum "$A/pre/"* > "$A/pre-source-sha.txt"
python3 "$A/au8_patch.py"
{ diff -u "$A/pre/R5900OpcodeImpl.cpp" $G/pcsx2/pcsx2/R5900OpcodeImpl.cpp; diff -u "$A/pre/Mixer.cpp" $G/pcsx2/pcsx2/SPU2/Mixer.cpp; } > "$A/au8-hunk.diff" || true
nice cmake --build "$G/pcsx2/build" --target pcsx2-qt -j8 > "$A/build.log" 2>&1 || { tail -40 "$A/build.log"; exit 1; }
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" > "$A/bin-sha-read1.txt"
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" > "$A/bin-sha-read2.txt"
diff -u "$A/bin-sha-read1.txt" "$A/bin-sha-read2.txt"
cat "$A/bin-sha-read1.txt"
