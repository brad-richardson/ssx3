#!/usr/bin/env bash
# T58 build: verify T58 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
echo "=== contenders (want none pcsx2/cmake/ninja) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
grep -c "t58_store_watch\|t58_dma_watch\|t58_emit\|t58_flush" $P/R5900OpcodeImpl.cpp $P/FPU.cpp $P/VU0.cpp $P/SPR.cpp $P/Sif0.cpp $P/sif2.cpp $P/IPU/IPUdma.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T58_BUILD_DONE
