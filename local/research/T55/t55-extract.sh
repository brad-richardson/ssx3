#!/usr/bin/env bash
# T55 extract: pull h394 + T55_CAP + window markers from a capture emulog.
# PCSX2 emulog lines carry a "[ timestamp]" prefix: match unanchored, strip
# the prefix, then validate every line against the T55 grammar (rejects=0).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t50/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t55-trace.txt}
grep -E 'h394 vsync=|T55_CAP|T51C_WINDOW|T51C_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE '^(h394 vsync=[0-9]+ tgt=0x[0-9a-f]+ a0=0x[0-9a-f]+ s1=0x[0-9a-f]+ w0=0x[0-9a-f]+ w1=0x[0-9a-f]+ w2=0x[0-9a-f]+ w3=0x[0-9a-f]+ hash=0x[0-9a-f]+ ret=0x[0-9a-f]+ stores=[01]|T55_CAP vsync=[0-9]+|T51C_WINDOW vsync=[0-9]+|T51C_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )' "$OUT" || true
echo "=== counts ==="
for pat in 'h394 vsync=' 'T55_CAP' 'T51C_WINDOW' 'T48_PATHS'; do
  printf '%-20s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T55_EXTRACT_DONE
