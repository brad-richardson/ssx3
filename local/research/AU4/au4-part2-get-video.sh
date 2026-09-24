#!/usr/bin/env bash
set -euo pipefail
A=/home/brad/au4
F=$(ls -t "$A"/dat/PCSX2/videos/*.mp4 | head -1)
sha256sum "$F" > "$A/part2-video-sha-read1.txt"
sha256sum "$F" > "$A/part2-video-sha-read2.txt"
diff -u "$A/part2-video-sha-read1.txt" "$A/part2-video-sha-read2.txt"
base64 -w0 "$F"
