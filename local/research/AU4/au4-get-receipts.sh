#!/usr/bin/env bash
set -euo pipefail
A=/home/brad/au4
G=/home/brad/pcsx2-g7
diff -u "$G/pre-au4/R5900OpcodeImpl.cpp" "$G/pcsx2/pcsx2/R5900OpcodeImpl.cpp" > "$A/au4-hunk.diff" || true
printf '=== PCSX2 rev ===\n' > "$A/pcsx2-rev.txt"
cd "$G/pcsx2"
git rev-parse HEAD >> "$A/pcsx2-rev.txt"
git status --short >> "$A/pcsx2-rev.txt"
cd "$A"
tar -czf - au4-hunk.diff pre-au4-sha.txt bin-sha-read1.txt bin-sha-read2.txt replay-md5.txt replay-hwstat.txt replay-au4-lines.txt input-sha-read1.txt input-sha-read2.txt dat-ini-sha.txt au4a-poll.log build.log build2.log replay.log pcsx2-rev.txt precapture-jobs.txt prereplay-jobs.txt prebuild-jobs.txt prebuild2-jobs.txt | base64 -w0
