#!/usr/bin/env bash
# T56 probe4: SPR TU include precedents
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe4-out.txt
{
echo "=== DMAC_TOP_40 ==="
head -40 $P/Dmac.cpp
echo "=== DMAC_CPUREGS ==="
grep -n "cpuRegs" $P/Dmac.cpp | head -5
echo "=== HW_CPUREGS_INCLUDE ==="
grep -n "include" $P/Hw.cpp | head -20
grep -n "cpuRegs" $P/Hw.cpp | head -5
echo "=== R5900H_INCLUDES ==="
grep -n "include" $P/R5900.h | head -20
echo "=== MEMORYH_INCLUDES ==="
grep -n "include" $P/Memory.h | head -20
echo "=== SPRH ==="
cat $P/SPR.h
echo "=== COMMONH_ATOMIC ==="
grep -n "atomic" $P/Common.h | head -5
} > $OUT 2>&1
echo PROBE4_DONE
wc -c $OUT
