#!/bin/bash
# Internal-disk usage of every ssx3 workstream on the mini, against the
# 200 GB cap (Brad, 2026-09-22; raised from 100). Run before and after any step that writes
# more than ~1 GB. Exit 1 when over the cap.
CAP_GB=200
paths=(~/dev/ssx3 ~/dev/mesa ~/dev/ssx3-work ~/dev/ssx3-inputs ~/dev/PS2Recomp ~/dev/parallel-gs ~/dev/ps2xGS ~/Library/Caches/ccache)
for p in /tmp/e18-mpeg-link /tmp/pf1* /tmp/t4* /tmp/g42* /tmp/ssx3-* /tmp/e3* /tmp/n4*; do [ -e "$p" ] && paths+=("$p"); done
kb=$(du -sk "${paths[@]}" 2>/dev/null | awk '{s+=$1} END {print s+0}')
gb=$(awk -v k="$kb" 'BEGIN {printf "%.1f", k/1048576}')
du -sh "${paths[@]}" 2>/dev/null | sort -h | tail -8
echo "ssx3 internal usage: ${gb} GB of ${CAP_GB} GB cap; disk free: $(df -h /System/Volumes/Data | awk 'NR==2{print $4}')"
awk -v g="$gb" -v c="$CAP_GB" 'BEGIN {exit (g > c)}' || { echo "OVER CAP: stop and tell the orchestrator"; exit 1; }
