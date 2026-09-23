#!/usr/bin/env bash
# T50 single build: verify anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t50_read_watch" $P/R5900OpcodeImpl.cpp
grep -c "T50_SRCREAD_FULL\|srcread vsync" $P/R5900OpcodeImpl.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T50_BUILD_DONE
