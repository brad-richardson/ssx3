#!/usr/bin/env bash
# T65: stash pre-patch SHAs + file copies, apply t65-hook.py, build qt + gsrunner.
set -e
G=/home/brad/pcsx2-g7
P=$G/pcsx2/pcsx2
echo "=== contenders (want none) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
mkdir -p $G/pre-t65
if [ ! -f $G/pre-t65/done ]; then
  for f in GS/GSState.cpp GS/GS.cpp Counters.cpp VU1micro.cpp; do cp $P/$f $G/pre-t65/$(basename $f); done
  sha256sum $G/pre-t65/*.cpp
  cp $G/pcsx2/build/bin/pcsx2-qt $G/pre-t65/pcsx2-qt.t64
  sha256sum $G/pre-t65/pcsx2-qt.t64
  python3 /mnt/c/Users/bradr/t65stage/t65-hook.py $P
  touch $G/pre-t65/done
fi
grep -c "T65\|t65" $P/GS/GSState.cpp $P/GS/GS.cpp $P/Counters.cpp $P/VU1micro.cpp
cd $G/pcsx2 && git diff --stat -- pcsx2/Counters.cpp
echo "=== BUILD ==="; date -u
cmake --build $G/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2 2>&1 | grep -E "error|warning: .*t65|FAILED|Linking|^\[[0-9]+/[0-9]+\] Building" | tail -40
echo "=== POST ==="; date -u
sha256sum $G/pcsx2/build/bin/pcsx2-qt $G/pcsx2/build/bin/pcsx2-gsrunner
ls -la $G/pcsx2/build/bin/pcsx2-qt $G/pcsx2/build/bin/pcsx2-gsrunner
echo T65_BUILD_DONE
