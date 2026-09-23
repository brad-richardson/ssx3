#!/usr/bin/env bash
# T57 probe 14: emit patch diff + stage deliverables for scp.
set -e
P=/home/brad/pcsx2-g7/pcsx2
S=/mnt/c/Users/bradr/t57stage
git -C $P diff --output=$S/t57-patch.diff -- pcsx2/VU0micro.cpp pcsx2/COP2.cpp pcsx2/Vif_Codes.cpp pcsx2/Vif_Transfer.cpp pcsx2/VU0microInterp.cpp
sha256sum $S/t57-patch.diff
wc -c $S/t57-patch.diff
cp /home/brad/pcsx2-t4/t57-trace.txt $S/t57a-trace.txt
cp /home/brad/pcsx2-t4/t57a-poll.log $S/t57a-poll.log
cp /home/brad/pcsx2-t4/t57a-shot-sc.png $S/t57a-shot-sc.png
cp /home/brad/pcsx2-t4/t57probe-poll.log $S/t57probe-poll.log
cp /home/brad/pcsx2-t4/t57-trace.txt $S/t57a-trace.txt
ls -la $S/
du -sh /home/brad/pcsx2-g7/dat-t57
echo T57_PROBE14_DONE
