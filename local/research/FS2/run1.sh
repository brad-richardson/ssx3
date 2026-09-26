#!/bin/bash
# usage: run1.sh LABEL APK SHA [extra launch args...]
# FS2: claim the Odin lease (label FS2) before the cool-down, so no other lane takes the
# device between cool-down and launch (Q1 lost it to VR4 that way). launch.py treats an
# 'FS2 ' lease as its own and releases it at exit; the restore then claims its own label.
set -u
cd /Users/brad/dev/ssx3
L=$1; APK=$2; SHA=$3; shift 3
LEASE=local/tooling/odin_lease.sh
until bash $LEASE claim FS2 >/dev/null; do echo "[$(date +%T)] lease busy: $(bash $LEASE status)"; sleep 30; done
echo "[$(date +%T)] lease claimed: $(bash $LEASE status)"
python3 local/research/FS2/cooldown.py --label $L || { bash $LEASE release FS2; exit 1; }
python3 local/research/FS2/launch.py --label $L --variant A --wall 600 --stop-tick 4500 --cpu-window 1900,2500 \
  --apk "$APK" --apk-sha "$SHA" --env PS2X_MTVU=1 --env PS2X_MTVU_LAG=1 --env PS2X_VU1_BLOCKS=1 --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 "$@"
rc=$?
case "$(bash $LEASE status)" in "FS2 "*) bash $LEASE release FS2;; esac
bash local/tooling/odin_restore_play.sh FS2-$L
echo "LAUNCH_RC=$rc RESTORE_RC=$?"
