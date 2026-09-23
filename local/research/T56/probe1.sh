#!/usr/bin/env bash
# T56 probe1: store sites + SPR DMA anchors (output to $HOME/t56probe1-out.txt, no pipes in ssh string)
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe1-out.txt
{
echo "=== T51W_CALLSITES ==="
grep -n "t51w_watch" $P/R5900OpcodeImpl.cpp
echo "=== T54W_CALLSITES ==="
grep -n "t54w_watch" $P/R5900OpcodeImpl.cpp | head -20
echo "=== SW_SITES ==="
grep -n "void SW()" $P/R5900OpcodeImpl.cpp
grep -n "void SQ()" $P/R5900OpcodeImpl.cpp
grep -n "void SD()" $P/R5900OpcodeImpl.cpp
grep -n "void SB()" $P/R5900OpcodeImpl.cpp
grep -n "void SH()" $P/R5900OpcodeImpl.cpp
grep -n "void SDL" $P/R5900OpcodeImpl.cpp
grep -n "void SDR" $P/R5900OpcodeImpl.cpp
grep -n "void SWL" $P/R5900OpcodeImpl.cpp
grep -n "void SWR" $P/R5900OpcodeImpl.cpp
echo "=== MEMWRITE_DECL ==="
grep -n "memWrite8\|memWrite16\|memWrite32\|memWrite64\|memWrite128" $P/R5900OpcodeImpl.cpp | head -30
echo "=== SPR_FILES ==="
ls $P | grep -i -e spr -e dma -e scratch
echo "=== TOSPR ==="
grep -rn "toSPR\|fromSPR\|SPR_" $P --include=*.cpp --include=*.h -l | head -20
echo "=== SCRATCHPAD_REFS ==="
grep -rn "scratchpad\|Scratchpad\|SCRATCHPAD" $P --include=*.cpp --include=*.h | head -30
} > $OUT 2>&1
echo PROBE1_DONE
wc -c $OUT
