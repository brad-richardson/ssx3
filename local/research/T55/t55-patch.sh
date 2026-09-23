#!/usr/bin/env bash
# T55 patch diff: Interpreter.cpp (the only touched file) vs HEAD.
# Carries T48-T55 hunks; T55's own are the T55-marked lines.
set -e
git -C /home/brad/pcsx2-g7/pcsx2 diff -- pcsx2/Interpreter.cpp > /home/brad/pcsx2-t4/t55-patch.diff
sha256sum /home/brad/pcsx2-t4/t55-patch.diff
wc -c /home/brad/pcsx2-t4/t55-patch.diff
grep -c "T55" /home/brad/pcsx2-t4/t55-patch.diff
echo T55_PATCH_DONE
