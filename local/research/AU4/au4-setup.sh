#!/usr/bin/env bash
set -euo pipefail
S=/home/brad/pcsx2-g7/dat-t48/PCSX2
A=/home/brad/au4
D=$A/dat/PCSX2
mkdir -p "$D" "$A/logs"
for dir in bios inis memcards; do cp -a "$S/$dir" "$D/"; done
for dir in cache cheats covers gamesettings inputprofiles logs patches resources snaps sstates textures videos; do mkdir -p "$D/$dir"; done
python3 - <<'PY'
from pathlib import Path
p=Path('/home/brad/au4/dat/PCSX2/inis/PCSX2.ini')
s=p.read_text()
a='[Hotkeys]\n'
assert s.count(a)==1
s=s.replace(a,a+'ToggleVideoCapture = Keyboard/F12\n')
p.write_text(s)
PY
sha256sum "$S/inis/PCSX2.ini" "$D/inis/PCSX2.ini" > "$A/dat-ini-sha.txt"
du -sh "$A"
