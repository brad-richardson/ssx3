#!/bin/bash
# VR4 Odin leg: wait until the lease is ours (poll 15 s, max 60 min), then
# cooldown + launch (play settings: MTVU + LAG + blocks, core pins) + restore.
# Usage: leg.sh LABEL APK SHA
set -u
L=$1; APK=$2; SHA=$3
cd ~/dev/ssx3
for i in $(seq 1 240); do
  out=$(bash local/tooling/odin_lease.sh claim VR4 2>&1)
  case "$out" in *CLAIMED*) echo "[$(date +%H:%M:%S)] lease claimed"; break;; esac
  [ "$i" = 240 ] && { echo "lease never free: $out"; exit 1; }
  sleep 15
done
python3 local/research/VR4/cooldown.py --label "$L" 2>&1 | tail -1
python3 local/research/VR4/launch.py --label "$L" --variant A --wall 600 --stop-tick 4500 --cpu-window 1900,2500 \
  --apk "$APK" --apk-sha "$SHA" --env PS2X_MTVU=1 --env PS2X_MTVU_LAG=1 --env PS2X_VU1_BLOCKS=1 \
  --env PS2X_GAME_THREAD_CPUS=6 --env PS2X_MTVU_CPUS=7 > ~/dev/ssx3-work/VR4/odin/$L.txt 2>&1
echo "launch rc=$?"
grep -E 'STOP|FATAL|Traceback|\[mtvu\]' ~/dev/ssx3-work/VR4/odin/$L.txt | tail -4 | cut -c1-180
bash local/tooling/odin_restore_play.sh "VR4-$L" 2>&1 | tail -2
python3 local/research/VR4/phases.py "local/research/VR4/logs/$L" 2>&1 | tail -9
