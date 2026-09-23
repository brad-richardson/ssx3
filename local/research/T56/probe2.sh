#!/usr/bin/env bash
# T56 probe2: SPR DMA + scratchpad write path details
set -u
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
OUT=$HOME/t56probe2-out.txt
{
echo "=== SPR_CPP ==="
cat $P/SPR.cpp
echo "=== END_SPR_CPP ==="
echo "=== SPR_H ==="
cat $P/SPR.h
echo "=== END_SPR_H ==="
} > $OUT 2>&1
echo PROBE2_DONE
wc -c $OUT
