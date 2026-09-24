#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
E=/home/brad/e60
pgrep -af 'gradle|ninja|clang|pcsx2-qt' > "$E/prereplay-jobs.txt" || true
if [ -s "$E/prereplay-jobs.txt" ]; then cat "$E/prereplay-jobs.txt"; exit 20; fi
for f in /tmp/t48-arm /tmp/t65-arm /tmp/t65-vu-now /tmp/t48-dump-now "$E/arm"; do
  if [ -e "$f" ]; then echo "armed file present: $f"; exit 21; fi
done
mkdir -p "$E/replayframes"
timeout 300 "$G/pcsx2/build/bin/pcsx2-gsrunner" -renderer vulkan -dumpdir "$E/replayframes" -logfile "$E/replay.log" -loop 1 -noshadercache -surfaceless -ini "$G/g10-uncorrected.ini" -- "$G/dat-g13/PCSX2/snaps/SSX 3_SLUS-20772_20260921005452.gs" > "$E/replay.stdout" 2>&1
md5sum "$E"/replayframes/*.png > "$E/replay-md5.txt"
grep -A8 STATISTICS "$E/replay.log" > "$E/replay-hwstat.txt"
printf 'e60-lines=' > "$E/replay-e60-lines.txt"
grep -c E60 "$E/replay.log" >> "$E/replay-e60-lines.txt" || true
cat "$E/replay-md5.txt" "$E/replay-hwstat.txt" "$E/replay-e60-lines.txt"
