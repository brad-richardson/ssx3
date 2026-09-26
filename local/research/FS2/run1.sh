#!/bin/bash
# usage: run1.sh LABEL APK SHA [extra launch args...]
set -u
cd /Users/brad/dev/ssx3
L=$1; APK=$2; SHA=$3; shift 3
python3 local/research/FS2/cooldown.py --label $L || exit 1
python3 local/research/FS2/launch.py --label $L --variant A --wall 600 --stop-tick 4500 --cpu-window 1900,2500 \
  --apk "$APK" --apk-sha "$SHA" --env PS2X_MTVU=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 "$@"
rc=$?
bash local/tooling/odin_restore_play.sh FS2-$L
echo "LAUNCH_RC=$rc RESTORE_RC=$?"
