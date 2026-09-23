#!/usr/bin/env bash
# T56 probe5: full memWrite site coverage + CACHE op
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe5-out.txt
{
echo "=== ALL_MEMWRITE_RI ==="
grep -n "memWrite" $P/R5900OpcodeImpl.cpp
echo "=== ALL_MEMWRITE_FPU_VU0 ==="
grep -n "memWrite" $P/FPU.cpp $P/VU0.cpp
echo "=== CACHE_OP ==="
grep -n "CACHE" $P/R5900OpcodeImpl.cpp | head -10
echo "=== MEMWRITE_DEF ==="
grep -rn "void memWrite32\|memWrite32(u32" $P/Memory.cpp $P/Memory.h $P/vtlb.cpp 2>/dev/null | head -10
ls $P | grep -i -e memory -e vtlb -e tlb
echo "=== SCRATCH_IN_MEMWRITE ==="
grep -n -i "scratch\|0x70000000\|0x7000" $P/vtlb.cpp 2>/dev/null | head -20
grep -n -i "scratch" $P/Memory.cpp 2>/dev/null | head -20
} > $OUT 2>&1
echo PROBE5_DONE
wc -c $OUT
