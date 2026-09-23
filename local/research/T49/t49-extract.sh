#!/usr/bin/env bash
# T49 extract: pull T49 + marker lines from the capture emulog.
# NOTE: PCSX2 emulog lines carry a "[ timestamp]" prefix, so all T49 patterns
# are matched unanchored; every extracted line is then validated against the
# T49 grammars and rejects are reported (must be zero).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t48/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-g7/t49-trace.txt}
VU1OUT=${OUT%.txt}-vu1.txt
grep -E 'T49_BEGIN|T49_END|T49_VIF_TRUNCATED|vi-entry|vi-exit|vumem [0-9]+ [0-9a-f]|vif (NOP|STCYCL|OFFSET|BASE|ITOP|STMOD|MSKPATH3|MARK|FLUSHE|FLUSH|FLUSHA|MSCAL|MSCALF|MSCNT|STMASK|STROW|STCOL|MPG|DIRECT|DIRECTHL|UNPACK|NULL) |pair pc=|T48_DUMP_QUEUED|T48_MODE' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
grep -E 'T48_VU1' "$E" | sed 's/^[^]]*] //' > "$VU1OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE '^(T49_BEGIN|T49_END|T49_VIF_TRUNCATED|vi-entry|vi-exit|vumem |vif |pair |T48_DUMP_QUEUED|T48_MODE)' "$OUT" || true
echo "=== counts ==="
for pat in 'T49_BEGIN' 'T49_END' 'vi-entry' 'vi-exit' 'vumem ' 'UNPACK|STCYCL|MSCAL|MARK |BASE |OFFSET|ITOP |STMOD|MSKPATH3|FLUSH|STMASK|STROW|STCOL|MPG|DIRECT|NOP |NULL ' 'pair pc=' 'T48_DUMP_QUEUED'; do
  printf '%-16s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
printf '%-16s %s\n' 'T48_VU1' "$(grep -cE 'T48_VU1' "$VU1OUT" || true)"
echo "=== sha ==="
sha256sum "$OUT" "$VU1OUT"
ls -la "$OUT" "$VU1OUT" "$E"
echo T49_EXTRACT_DONE
