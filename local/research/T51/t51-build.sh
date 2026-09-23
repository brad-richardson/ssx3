#!/usr/bin/env bash
# T51 build: verify anchors are clean, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t51e_store_watch\|t51e_syscall_watch\|t51h_irq_watch\|t51g_ad" $P/R5900OpcodeImpl.cpp $P/Hw.cpp $P/GS/GSState.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T51_BUILD_DONE
