#!/bin/bash
# V2 tier-1 SSD cleanup (Brad approved 2026-09-22). Deletes the entries in
# delete-tier1.txt, then the ps2x-t4 logs the share holds at the same size
# (never emulog-t46r3.txt, which is SSD-only).
S="/Volumes/Extreme SSD"; SH="/Volumes/share/ssx3/ps2x-t4"
cd "$(dirname "$0")"
echo "start $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
while IFS= read -r e; do
  [ -z "$e" ] && continue
  [ -e "$S/$e" ] || { echo "gone: $e"; continue; }
  rm -rf "$S/$e" && echo "deleted: $e" || echo "FAILED: $e"
  rm -f "$S/$(dirname "$e")/._$(basename "$e")"
done < delete-tier1.txt
for f in "$S"/ps2x-t4/emulog-*.txt; do
  b=$(basename "$f"); [ "$b" = emulog-t46r3.txt ] && continue
  a=$(stat -f %z "$f"); m=$(stat -f %z "$SH/$b" 2>/dev/null || echo none)
  if [ "$a" = "$m" ]; then rm -f "$f" "$S/ps2x-t4/._$b" && echo "deleted (share size match $a): ps2x-t4/$b"; else echo "KEPT (share $m vs ssd $a): ps2x-t4/$b"; fi
done
echo "end $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
