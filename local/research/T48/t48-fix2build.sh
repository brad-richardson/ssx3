#!/usr/bin/env bash
# T48 fix2 apply + final rebuild.
set -e
cp /mnt/c/Users/bradr/pcsx2-t4/t48-fix2.py /home/brad/pcsx2-g7/t48-fix2.py
python3 /home/brad/pcsx2-g7/t48-fix2.py
echo "=== REBUILD ==="
date -u
cmake --build /home/brad/pcsx2-g7/pcsx2/build --target pcsx2-qt pcsx2-gsrunner -j2
echo "=== POST ==="
date -u
sha256sum /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
ls -la /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-qt /home/brad/pcsx2-g7/pcsx2/build/bin/pcsx2-gsrunner
du -s /home/brad/pcsx2-g7/pcsx2/build
