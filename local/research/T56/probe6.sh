#!/usr/bin/env bash
# T56 probe6: cpuRegs declaration + VUmicro.h chain
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe6-out.txt
{
echo "=== CPUREGS_DECL ==="
grep -rn "cpuRegs;" $P/*.h | head -5
echo "=== VUMICROH_INCLUDES ==="
grep -n "include" $P/VUmicro.h | head -20
echo "=== MTVUH_INCLUDES ==="
grep -n "include" $P/MTVU.h | head -20
} > $OUT 2>&1
echo PROBE6_DONE
wc -c $OUT
