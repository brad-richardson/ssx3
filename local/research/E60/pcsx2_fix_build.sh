#!/usr/bin/env bash
set -euo pipefail
G=/home/brad/pcsx2-g7
E=/home/brad/e60
P=$G/pcsx2/pcsx2/Interpreter.cpp
python3 - <<'PY'
from pathlib import Path
p=Path('/home/brad/pcsx2-g7/pcsx2/pcsx2/Interpreter.cpp')
s=p.read_text()
a='#include "R5900OpcodeTables.h"\n'
assert s.count(a)==1
s=s.replace(a,a+'#include "VU.h" // E60 raw VU0 tap\n')
p.write_text(s)
PY
diff -u "$G/pre-e60/Interpreter.cpp" "$P" > "$E/pcsx2-hunk.diff" || true
cmake --build "$G/pcsx2/build" --target pcsx2-qt pcsx2-gsrunner -j2 > "$E/build2.log" 2>&1 || {
  grep -E 'error:|FAILED:|undefined symbol|ninja: build stopped' "$E/build2.log" | head -30 || true
  exit 21
}
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$E/bin-sha-read1.txt"
sha256sum "$G/pcsx2/build/bin/pcsx2-qt" "$G/pcsx2/build/bin/pcsx2-gsrunner" > "$E/bin-sha-read2.txt"
diff -u "$E/bin-sha-read1.txt" "$E/bin-sha-read2.txt"
