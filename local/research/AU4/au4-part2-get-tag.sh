#!/usr/bin/env bash
set -euo pipefail
A=/home/brad/au4
F=$A/pcsx2-tag1.bin
sha256sum "$F" > "$A/part2-tag-sha-read1.txt"
sha256sum "$F" > "$A/part2-tag-sha-read2.txt"
diff -u "$A/part2-tag-sha-read1.txt" "$A/part2-tag-sha-read2.txt"
base64 -w0 "$F"
