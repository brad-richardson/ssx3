#!/usr/bin/env bash
# T66: stash pre-patch SHA + copy, apply t66-hook.py, build qt + gsrunner.
set -e
G=/home/brad/pcsx2-g7
P=$G/pcsx2/pcsx2
echo "=== contenders (want none) ==="
pgrep -af "pcsx2-qt|pcsx2-gsrunner|cmake --build|ninja" || true
mkdir -p $G/pre-t66
if [ ! -f $G/pre-t66/done ]; then
  cp $P/R5900OpcodeImpl.cpp $G/pre-t66/
  sha256sum $G/pre-t66/R5900OpcodeImpl.cpp $G/pcsx2/build/bin/pcsx2-qt
  python3 /mnt/c/Users/bradr/t66stage/t66-hook.py $P/R5900OpcodeImpl.cpp
  touch $G/pre-t66/done
fi
grep -c "t66_" $P/R5900OpcodeImpl.cpp
echo "=== BUILD ==="; date -u
cmake --build $G/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2 2>&1 | grep -E "error|FAILED|Linking|Building" | tail -30
echo "=== POST ==="; date -u
sha256sum $G/pcsx2/build/bin/pcsx2-qt $G/pcsx2/build/bin/pcsx2-gsrunner
ls -la $G/pcsx2/build/bin/pcsx2-qt $G/pcsx2/build/bin/pcsx2-gsrunner
echo T66_BUILD_DONE
