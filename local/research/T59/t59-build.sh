#!/usr/bin/env bash
# T59 build: verify T59 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
echo "=== contenders (want none pcsx2/cmake/ninja) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
grep -c "t58_phys\|t59_maybe_dump\|ebwend\|vaddr=0x" $P/R5900OpcodeImpl.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T59_BUILD_DONE
