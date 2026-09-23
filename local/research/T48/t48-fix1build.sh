#!/usr/bin/env bash
# T48 fix1 apply + GSgifTransfer def check + rebuild (the 1 retry).
set -e
P=/home/brad/pcsx2-g7/pcsx2/pcsx2
cp /mnt/c/Users/bradr/pcsx2-t4/t48-fix1.py /home/brad/pcsx2-g7/t48-fix1.py
python3 /home/brad/pcsx2-g7/t48-fix1.py
echo "=== GSgifTransfer def ==="
grep -n -A3 "void GSgifTransfer(" $P/GS/GS.cpp
echo "=== REBUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
ls -la /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
