#!/usr/bin/env bash
# T17: fresh boot with T4-identical flags; preserves any prior emulog first.
set -x
date -u
export DISPLAY=:99 QT_QPA_PLATFORM=xcb
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f /home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt ]; then
  sha256sum /home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt
  mv /home/brad/pcsx2-t4/dat/PCSX2/logs/emulog.txt /home/brad/pcsx2-t4/dat/PCSX2/logs/emulog-pre-t17-$TS.txt
  ls -la /home/brad/pcsx2-t4/dat/PCSX2/logs/
fi
rm -f /home/brad/pcsx2-t4/pcsx2.pid
nohup /home/brad/pcsx2-t4/pcsx2/build/bin/pcsx2-qt \
  -nogui -slowboot -turbo \
  -datapath /home/brad/pcsx2-t4/dat \
  -logfile /home/brad/pcsx2-t4/logs/boot-t17.log \
  -- "/home/brad/pcsx2-t4/inputs/SSX 3 (USA).iso" \
  > /home/brad/pcsx2-t4/logs/boot-t17.stdout 2>&1 &
echo "$!" > /home/brad/pcsx2-t4/pcsx2.pid
echo "PID:$!"
date -u +%s > /home/brad/pcsx2-t4/t17-boot-epoch.txt
cat /home/brad/pcsx2-t4/t17-boot-epoch.txt
sleep 20
ps -o pid,etime,time,stat,cmd -p "$(cat /home/brad/pcsx2-t4/pcsx2.pid)"
