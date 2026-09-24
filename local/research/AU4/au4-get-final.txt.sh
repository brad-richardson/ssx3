#!/usr/bin/env bash
A=/home/brad/au4
cat "$A/video-sha-read1.txt" "$A/video-sha-read2.txt"
printf 'tag1='; test -f "$A/pcsx2-tag1.bin" && stat -c %s "$A/pcsx2-tag1.bin" || echo not-found
printf 'bytesize-au4='; du -sh "$A" | cut -f1
