#!/usr/bin/env bash
# T56 probe3: anchors for hook authoring
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe3-out.txt
{
echo "=== RI_TOP_60 ==="
head -60 $P/R5900OpcodeImpl.cpp
echo "=== SB_BODY ==="
sed -n '1045,1210p' $P/R5900OpcodeImpl.cpp
echo "=== FPU_SWC1_CTX ==="
grep -n "void SWC1" $P/FPU.cpp
sed -n "$(grep -n 'void SWC1' $P/FPU.cpp | cut -d: -f1),+25p" $P/FPU.cpp
echo "=== VU0_SQC2_CTX ==="
grep -n "void SQC2" $P/VU0.cpp
sed -n "$(grep -n 'void SQC2' $P/VU0.cpp | cut -d: -f1),+25p" $P/VU0.cpp
echo "=== SPR_TOP ==="
head -30 $P/SPR.cpp
echo "=== GS_VSYNC ==="
grep -n "g_t48_vsync" $P/GS/GS.cpp | head -5
grep -n "g_t48_vsync" $P/R5900OpcodeImpl.cpp | head -5
grep -n "g_t48_vsync" $P/FPU.cpp $P/VU0.cpp $P/SPR.cpp $P/Interpreter.cpp | head -10
echo "=== MEMREAD_SPR ==="
grep -n "include" $P/SPR.cpp
echo "=== PSU_MACRO ==="
grep -rn "define psSu128\|define psSu32\|psSu128(" $P/Memory.h $P/Common.h 2>/dev/null | head -10
grep -rln "psSu128" $P/*.h | head
} > $OUT 2>&1
echo PROBE3_DONE
wc -c $OUT
