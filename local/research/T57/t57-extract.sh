#!/usr/bin/env bash
# T57 extract: pull vu0call + vif0op + T57_CAP + window markers from a capture emulog.
# PCSX2 emulog lines carry a "[ timestamp]" prefix: match unanchored, strip
# the prefix, then validate every line against the T57 grammar (rejects=0).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t57/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t57-trace.txt}
grep -E 'vu0call vsync=|vif0op vsync=|T57_CAP|T51C_WINDOW|T51C_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE "^(vu0call vsync=[0-9]+ caller_pc=0x[0-9a-f]+ via=(cop2|vif0|unknown) startPC=0x[0-9a-f]+ cycles=[0-9]+ vi1=0x[0-9a-f]+ vi2=0x[0-9a-f]+( ms=0x[0-9a-f]+)?( mark=sub_0037D968)?( end=abort)?|vif0op vsync=[0-9]+ op=[A-Z]+ n=[0-9]+|T57_CAP vsync=[0-9]+|T51C_WINDOW vsync=[0-9]+|T51C_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )" "$OUT" || true
echo "=== counts ==="
for pat in 'vu0call vsync=' 'vif0op vsync=' 'T57_CAP' 'T51C_WINDOW' 'T48_PATHS'; do
  printf '%-20s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T57_EXTRACT_DONE
