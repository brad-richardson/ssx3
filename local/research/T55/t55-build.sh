#!/usr/bin/env bash
# T55 build: verify T55 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
echo "=== contenders (want none pcsx2/cmake/ninja) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
grep -c "t55_call\|t55_enter\|t55_mark\|t55_ret" $P/Interpreter.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T55_BUILD_DONE
