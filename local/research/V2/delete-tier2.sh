#!/bin/bash
# V2 tier-2 SSD cleanup: parked I-lane dirs (Brad approved 2026-09-22). Deletes the entries in
# delete-tier2.txt, then prunes the dangling fork worktree entries.
S="/Volumes/Extreme SSD"; SH="/Volumes/share/ssx3/ps2x-t4"
cd "$(dirname "$0")"
echo "start $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
while IFS= read -r e; do
  [ -z "$e" ] && continue
  [ -e "$S/$e" ] || { echo "gone: $e"; continue; }
  rm -rf "$S/$e" && echo "deleted: $e" || echo "FAILED: $e"
  rm -f "$S/$(dirname "$e")/._$(basename "$e")"
done < delete-tier2.txt
git -C "$S/ps2recomp-spike/PS2Recomp" worktree prune -v 2>&1 | grep -v non-monotonic
echo "end $(date) free=$(df -h "$S" | awk 'NR==2{print $4}')"
