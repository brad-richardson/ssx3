#!/usr/bin/env bash
set -euo pipefail
S=/home/brad/pcsx2-g7/dat-t48/PCSX2
E=/home/brad/e60
D=$E/dat/PCSX2
mkdir -p "$D" "$E/logs"
for dir in bios inis memcards; do cp -a "$S/$dir" "$D/"; done
for dir in cache cheats covers gamesettings inputprofiles logs patches resources snaps sstates textures videos; do mkdir -p "$D/$dir"; done
sha256sum "$S/inis/PCSX2.ini" "$D/inis/PCSX2.ini" > "$E/dat-ini-sha.txt"
du -sh "$E"
