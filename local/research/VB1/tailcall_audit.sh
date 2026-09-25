#!/bin/zsh
# VB1: every generated pair function must hand off by a tail branch: count pair
# functions that contain a stack-protector guard load or an indirect call (blr).
set -euo pipefail
bin=$1
nm -n $bin | grep -E "VU1RecompImage.*5f[0-9a-f]{4}ER14VU1" > /tmp/vb1-audit-syms.$$ || true
total=$(wc -l < /tmp/vb1-audit-syms.$$)
lo=$(head -1 /tmp/vb1-audit-syms.$$ | cut -d' ' -f1); hi=$(tail -1 /tmp/vb1-audit-syms.$$ | cut -d' ' -f1)
/opt/homebrew/opt/llvm/bin/llvm-objdump -d --no-show-raw-insn --start-address=0x$lo --stop-address=$(printf "0x%x" $((0x$hi + 4096))) $bin | awk '
/^[0-9a-f]+ <.*VU1RecompImage.*5f[0-9a-f][0-9a-f][0-9a-f][0-9a-f]ER14VU1/ {cur=$2; n++; next}
/^[0-9a-f]+ </ {cur=""; next}
cur!="" && /blr/ {blr[cur]=1}
cur!="" && /__stack_chk/ {chk[cur]=1}
END {b=0;c=0; for(k in blr)b++; for(k in chk)c++; printf "pair_functions=%d with_blr=%d with_stack_chk_call=%d\n", n, b, c}'
echo "nm_pair_symbols=$total"
rm -f /tmp/vb1-audit-syms.$$
