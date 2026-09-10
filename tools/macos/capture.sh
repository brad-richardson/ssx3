#!/bin/sh
# Capture the PCSX2 window to PATH (needs the screen-recording permission for the terminal).
root=$(cd "$(dirname "$0")/../.." && pwd)
id=$("$root/local/bin/window_id") || { echo "no PCSX2 window" >&2; exit 1; }
screencapture -x -l "$id" "$1" && echo "$1"
