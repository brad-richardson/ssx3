#!/usr/bin/env bash
# T57 probe 13: prove the T57 hooks are linked into the running binary.
set -e
BIN=/home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt
echo "===== sha (must match T57 b1 pin) ====="
sha256sum $BIN
echo "===== format strings linked ====="
strings $BIN | grep -c "vu0call vsync=" || true
strings $BIN | grep -c "vif0op vsync=" || true
strings $BIN | grep -c "mark=sub_0037D968" || true
echo "===== t57 symbols linked ====="
nm -C $BIN 2>/dev/null | grep -c "t57_" || true
nm -C $BIN 2>/dev/null | grep "t57_" | head -20 || true
echo T57_PROBE13_DONE
