#!/usr/bin/env bash
set -euo pipefail
A=/home/brad/au4
I='/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso'
sha256sum "$I" "$A/dat/PCSX2/bios/"* > "$A/input-sha-read1.txt"
sha256sum "$I" "$A/dat/PCSX2/bios/"* > "$A/input-sha-read2.txt"
diff -u "$A/input-sha-read1.txt" "$A/input-sha-read2.txt"
cat "$A/input-sha-read1.txt"
