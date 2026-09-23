#!/usr/bin/env bash
# T50 build 2: verify anchors, build qt+gsrunner.
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
grep -c "t50_read_watch\|t50b_mpg\|t50b_dmareg\|t50b_tag_tap" $P/R5900OpcodeImpl.cpp $P/Vif1_Dma.cpp $P/Vif_Codes.cpp $P/Vif1_MFIFO.cpp $P/Dmac.cpp
echo "=== BUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
echo T50_BUILD2_DONE
