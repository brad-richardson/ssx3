#!/usr/bin/env bash
# T56 extract: pull spw + T56_CAP/T56W_ARMED + window markers from a capture emulog.
# PCSX2 emulog lines carry a "[ timestamp]" prefix: match unanchored, strip
# the prefix, then validate every line against the T56 grammar (rejects=0).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t50/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t56-trace.txt}
grep -E 'spw vsync=|T56_CAP|T56W_ARMED|T51C_WINDOW|T51C_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
REGS='a0=[0-9a-f]+ a1=[0-9a-f]+ a2=[0-9a-f]+ a3=[0-9a-f]+ v0=[0-9a-f]+ v1=[0-9a-f]+ t0=[0-9a-f]+ t1=[0-9a-f]+ t2=[0-9a-f]+ t3=[0-9a-f]+ t4=[0-9a-f]+ t5=[0-9a-f]+ t6=[0-9a-f]+ t7=[0-9a-f]+ t8=[0-9a-f]+ t9=[0-9a-f]+ s0=[0-9a-f]+ s1=[0-9a-f]+ s2=[0-9a-f]+ s3=[0-9a-f]+ s4=[0-9a-f]+ s5=[0-9a-f]+ s6=[0-9a-f]+ s7=[0-9a-f]+'
echo "=== rejects (must be 0) ==="
grep -vcE "^(spw vsync=[0-9]+ addr=0x[0-9a-f]+ value=0x[0-9a-f]+ via=[a-z0-9-]+( src=0x[0-9a-f]+)? pc=0x[0-9a-f]+ ra=0x[0-9a-f]+ $REGS|T56_CAP vsync=[0-9]+ addr=0x[0-9a-f]+|T56W_ARMED naddr=[0-9]+|T51C_WINDOW vsync=[0-9]+|T51C_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )" "$OUT" || true
echo "=== counts ==="
for pat in 'spw vsync=' 'T56_CAP' 'T56W_ARMED' 'T51C_WINDOW' 'T48_PATHS'; do
  printf '%-20s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T56_EXTRACT_DONE
