#!/usr/bin/env bash
# T49 single build: verify anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t49_vif_record" $P/Vif_Transfer.cpp $P/VU1micro.cpp
grep -c "T49_BEGIN\|T49_END\|t49_log\|t49_touch\|t49_vif_mark_fn\|vi-entry\|vi-exit" $P/VU1micro.cpp $P/VU1microInterp.cpp $P/VUops.cpp $P/Vif_Codes.cpp
grep -c "g_t49_winstart" $P/GS/GS.cpp $P/VU1micro.cpp
echo "=== BUILD ==="
date -u
cat /proc/uptime
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
ls -la /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
du -s /home/brad/pcsx2-g7/pcsx2/build
