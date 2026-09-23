#!/usr/bin/env bash
# T53 extract: pull tagaddrwrite + T53W markers from a capture emulog.
# PCSX2 emulog lines carry a "[ timestamp]" prefix: match unanchored, strip
# the prefix, then validate every line against the T53 grammars (rejects=0).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t50/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-t4/t53-trace.txt}
grep -E 'tagaddrwrite vsync=|T53W_ARMED|T53W_CAP|T51C_WINDOW|T51C_CAP|T48_PATHS' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE '^(tagaddrwrite vsync=[0-9]+ addr=0x[0-9a-f]+ value=0x[0-9a-f]+ pc=0x[0-9a-f]+ ra=0x[0-9a-f]+( a0=[0-9a-f]{8} a1=[0-9a-f]{8} a2=[0-9a-f]{8} a3=[0-9a-f]{8} v0=[0-9a-f]{8} v1=[0-9a-f]{8} t0=[0-9a-f]{8} t1=[0-9a-f]{8} t2=[0-9a-f]{8} t3=[0-9a-f]{8} t4=[0-9a-f]{8} t5=[0-9a-f]{8} t6=[0-9a-f]{8} t7=[0-9a-f]{8} t8=[0-9a-f]{8} t9=[0-9a-f]{8} s0=[0-9a-f]{8} s1=[0-9a-f]{8} s2=[0-9a-f]{8} s3=[0-9a-f]{8} s4=[0-9a-f]{8} s5=[0-9a-f]{8} s6=[0-9a-f]{8} s7=[0-9a-f]{8}( tu=(ri|swc1|sqc2))?)?|T53W_ARMED naddr=[0-9]+|T53W_CAP vsync=[0-9]+ addr=0x[0-9a-f]+|T51C_WINDOW vsync=[0-9]+|T51C_CAP vsync=[0-9]+|T48_PATHS vsync=[0-9]+ )' "$OUT" || true
echo "=== counts ==="
for pat in 'tagaddrwrite vsync=' 'T53W_ARMED' 'T53W_CAP' 'T51C_WINDOW' 'T48_PATHS'; do
  printf '%-20s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
echo "=== sha ==="
sha256sum "$OUT"
ls -la "$OUT" "$E"
echo T53_EXTRACT_DONE
