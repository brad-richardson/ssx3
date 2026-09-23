#!/usr/bin/env bash
# T48 pre-patch stash: record + copy both binaries, stage hook, apply, show diff stat.
set -e
B=/home/brad/pcsx2-g7/pcsx2/build/bin
P=/home/brad/pcsx2-g7/pre-t48
cp /mnt/c/Users/bradr/pcsx2-t4/t48-hook.py /home/brad/pcsx2-g7/t48-hook.py
sha256sum $B/pcsx2-qt $B/pcsx2-gsrunner
ls -la $B/pcsx2-qt $B/pcsx2-gsrunner
cp $B/pcsx2-qt $B/pcsx2-gsrunner $P/
sha256sum $P/pcsx2-qt $P/pcsx2-gsrunner
python3 /home/brad/pcsx2-g7/t48-hook.py
git -C /home/brad/pcsx2-g7/pcsx2 diff --stat
