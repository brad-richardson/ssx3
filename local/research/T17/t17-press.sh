#!/usr/bin/env bash
# T17: single key press ($2, default K=Cross) to window $1, with timing receipts.
set -x
export DISPLAY=:99
WID=${1:?usage: t17-press.sh WINDOW_ID [KEY]}
KEY=${2:-K}
date -u
date -u +%s.%N
xdotool key --window "$WID" "$KEY"
echo "XDOTOOL_EXIT:$?"
date -u
date -u +%s.%N
