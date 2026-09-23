#!/usr/bin/env bash
# T57 build: verify T57 anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
echo "=== contenders (want none pcsx2/cmake/ninja) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
grep -c "t57_cop2_ctx\|t57_vif0_ctx\|t57_msop\|t57_vif0_count\|t57_arm\|t57_entry\|t57_vu0_ebit\|t57_opname" $P/VU0micro.cpp $P/COP2.cpp $P/Vif_Codes.cpp $P/Vif_Transfer.cpp $P/VU0microInterp.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T57_BUILD_DONE
