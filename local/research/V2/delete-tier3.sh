#!/bin/bash
# V2 tier-3 SSD cleanup: GameCube reserve material (Brad approved 2026-09-22: upstream-review, ssx3-archive, android-spike; D/M4 report text copied to local/research/reserve-gc first). Deletes the entries in
# delete-tier3.txt. 
S="/Volumes/Extreme SSD"; SH="/Volumes/share/ssx3/ps2x-t4"
cd "$(dirname "$0")"
echo "start $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
while IFS= read -r e; do
  [ -z "$e" ] && continue
  [ -e "$S/$e" ] || { echo "gone: $e"; continue; }
  rm -rf "$S/$e" && echo "deleted: $e" || echo "FAILED: $e"
  rm -f "$S/$(dirname "$e")/._$(basename "$e")"
done < delete-tier3.txt
echo "end $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
