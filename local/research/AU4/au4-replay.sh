#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
A=/home/brad/au4
pgrep -af 'gradle|ninja|clang|pcsx2' > "$A/prereplay-jobs.txt" || true
if [ -s "$A/prereplay-jobs.txt" ]; then cat "$A/prereplay-jobs.txt"; exit 20; fi
for f in /tmp/t48-arm /tmp/t65-arm /tmp/t65-vu-now /tmp/t48-dump-now; do
  if [ -e "$f" ]; then echo "armed file present: $f"; exit 21; fi
done
mkdir -p "$A/replayframes"
timeout 300 "$G/pcsx2/build/bin/pcsx2-gsrunner" -renderer vulkan -dumpdir "$A/replayframes" -logfile "$A/replay.log" -loop 1 -noshadercache -surfaceless -ini "$G/g10-uncorrected.ini" -- "$G/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs" > "$A/replay.stdout" 2>&1
md5sum "$A"/replayframes/*.png > "$A/replay-md5.txt"
grep -A8 STATISTICS "$A/replay.log" > "$A/replay-hwstat.txt"
printf 'au4-lines=' > "$A/replay-au4-lines.txt"
grep -c AU4 "$A/replay.log" >> "$A/replay-au4-lines.txt" || true
cat "$A/replay-md5.txt" "$A/replay-hwstat.txt" "$A/replay-au4-lines.txt"
