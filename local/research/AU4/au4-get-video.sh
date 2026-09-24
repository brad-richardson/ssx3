#!/usr/bin/env bash
set -euo pipefail
F=$(find /home/brad/au4/dat/PCSX2/videos -maxdepth 1 -type f -name '*.mp4' | head -1)
[ -n "$F" ]
sha256sum "$F" > /home/brad/au4/video-sha-read1.txt
sha256sum "$F" > /home/brad/au4/video-sha-read2.txt
diff -u /home/brad/au4/video-sha-read1.txt /home/brad/au4/video-sha-read2.txt
base64 -w0 "$F"
