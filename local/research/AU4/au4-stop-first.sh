#!/usr/bin/env bash
set -e
A=/home/brad/au4
export DISPLAY=:99
xdotool key F12 || true
sleep 3
PID=$(cat "$A/pcsx2-au4.pid")
kill "$PID" 2>/dev/null || true
sleep 3
kill 395 2>/dev/null || true
printf 'first_run_tag_file='; test -f "$A/pcsx2-tag1.bin" && stat -c %s "$A/pcsx2-tag1.bin" || echo not-found
printf 'video_files:\n'; find "$A/dat/PCSX2/videos" -type f -printf '%s %p\n'
