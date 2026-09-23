#!/usr/bin/env bash
# T50 extract: pull srcread + marker lines from a capture emulog.
# NOTE: PCSX2 emulog lines carry a "[ timestamp]" prefix, so all T50 patterns
# are matched unanchored; every extracted line is then validated against the
# T50 grammars and rejects are reported (must be zero).
set -e
E=${1:-/home/brad/pcsx2-g7/dat-t48/PCSX2/logs/emulog.txt}
OUT=${2:-/home/brad/pcsx2-g7/t50-trace.txt}
VU1OUT=${OUT%.txt}-vu1.txt
T49OUT=${OUT%.txt}-t49retrace.txt
grep -E 'srcread |T50_SRCREAD_FULL|mpgpay |T50_MPGPAY_CAP|dmareg |T50_DMAREG_CAP|T48_DUMP_QUEUED|T48_MODE' "$E" | sed 's/^[^]]*] //' > "$OUT" || true
grep -E 'T48_VU1' "$E" | sed 's/^[^]]*] //' > "$VU1OUT" || true
grep -E 'T49_BEGIN|T49_END|vi-entry|vi-exit|vumem [0-9]+ [0-9a-f]|vif (NOP|STCYCL|OFFSET|BASE|ITOP|STMOD|MSKPATH3|MARK|FLUSHE|FLUSH|FLUSHA|MSCAL|MSCALF|MSCNT|STMASK|STROW|STCOL|MPG|DIRECT|DIRECTHL|UNPACK|NULL) |pair pc=' "$E" | sed 's/^[^]]*] //' > "$T49OUT" || true
echo "=== rejects (must be 0) ==="
grep -vcE '^(srcread |T50_SRCREAD_FULL|mpgpay |T50_MPGPAY_CAP|dmareg |T50_DMAREG_CAP|T48_DUMP_QUEUED|T48_MODE)' "$OUT" || true
echo "=== counts ==="
for pat in 'srcread ' 'T50_SRCREAD_FULL' 'mpgpay ' 'T50_MPGPAY_CAP' 'dmareg ' 'T50_DMAREG_CAP' 'T48_DUMP_QUEUED'; do
  printf '%-16s %s\n' "$pat" "$(grep -cE "$pat" "$OUT" || true)"
done
printf '%-16s %s\n' 'T48_VU1' "$(grep -cE 'T48_VU1' "$VU1OUT" || true)"
printf '%-16s %s\n' 'T49_BEGIN' "$(grep -cE 'T49_BEGIN' "$T49OUT" || true)"
echo "=== sha ==="
sha256sum "$OUT" "$VU1OUT" "$T49OUT"
ls -la "$OUT" "$VU1OUT" "$T49OUT" "$E"
echo T50_EXTRACT_DONE
