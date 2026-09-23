#!/usr/bin/env bash
# T61 build: verify T61 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
echo "=== contenders (want none pcsx2/cmake/ninja) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
grep -c "t61_app_account\|t61_vsync_tick\|t61_flush_all\|t61_apc_tick\|t61_apc_flush\|t60_phys\|t58_phys" $P/Interpreter.cpp $P/R5900OpcodeImpl.cpp $P/Vif_Transfer.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T61_BUILD_DONE
