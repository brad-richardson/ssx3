#!/usr/bin/env bash
# T50 diff: single-file patch file for the repo + stage.
cd /home/brad/pcsx2-g7/pcsx2 && git diff -- pcsx2/R5900OpcodeImpl.cpp > /home/brad/pcsx2-g7/t50-patch.diff
wc -l /home/brad/pcsx2-g7/t50-patch.diff
sha256sum /home/brad/pcsx2-g7/t50-patch.diff
cp /home/brad/pcsx2-g7/t50-patch.diff /mnt/c/Users/bradr/pcsx2-t4/t50stage/
echo T50_DIFF_DONE
