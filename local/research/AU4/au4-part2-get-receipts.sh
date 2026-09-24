#!/usr/bin/env bash
set -euo pipefail
A=/home/brad/au4
E=$A/dat/PCSX2/logs/emulog.txt
{
  grep -m1 'AU4_DESC' "$E" || true
  grep -m1 'AU4_TAG_OPEN' "$E" || true
} > "$A/part2-hook-lines.txt"
{
  stat -c '%s %n' "$A/pcsx2-tag1.bin" "$E"
  find "$A/dat/PCSX2/videos" -maxdepth 1 -type f -printf '%s %p\n'
  du -sh "$A"
  pgrep -af 'gradle|ninja|clang|pcsx2|Xvfb' || true
} > "$A/part2-run-summary.txt"
sha256sum "$A/part2-hunk.diff" > "$A/part2-hunk-sha.txt"
cd "$A"
tar -czf - part2-pre-sha.txt part2-bin-sha-read1.txt part2-bin-sha-read2.txt part2-tag-sha-read1.txt part2-tag-sha-read2.txt part2-video-sha-read1.txt part2-video-sha-read2.txt part2-hunk.diff part2-hunk-sha.txt part2-build.log part2-hook-lines.txt part2-run-summary.txt part2-prebuild-jobs.txt prereplay-jobs.txt replay-md5.txt replay-hwstat.txt replay-au4-lines.txt au4b-poll.log | base64 -w0
