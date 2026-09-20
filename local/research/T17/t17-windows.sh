#!/usr/bin/env bash
# T17: list visible X windows (ids + names) for key-target selection.
set -x
export DISPLAY=:99
date -u
for w in $(xdotool search --onlyvisible --name .); do
  echo "ID:$w NAME:$(xdotool getwindowname $w)"
done
echo "--- active ---"
xdotool getactivewindow
xdotool getwindowname $(xdotool getactivewindow)
