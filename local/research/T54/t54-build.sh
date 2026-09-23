#!/usr/bin/env bash
# T54 build: verify T54 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t54_census\|t54w_watch\|T54W_ARMED" $P/Interpreter.cpp $P/R5900OpcodeImpl.cpp $P/FPU.cpp $P/VU0.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T54_BUILD_DONE
