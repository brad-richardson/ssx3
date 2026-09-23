#!/usr/bin/env bash
# T48 single build: verify anchors, print PATH-mapping context, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t48_seen && g8_vsync_index >= 1200" $P/GS/GS.cpp
grep -c "path=%d" $P/GS/Renderers/HW/GSRendererHW.cpp
grep -c "T48_VU1 vsync" $P/VU1micro.cpp $P/VU1microInterp.cpp
echo "=== MTGS PATH mapping ctx ==="
sed -n '360,440p' $P/MTGS.cpp
echo "=== BUILD ==="
date -u
cat /proc/uptime
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
ls -la /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
du -s /home/brad/pcsx2-g7/pcsx2/build
