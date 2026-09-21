#!/bin/sh
# G14: ONE bounded on-device replay (rich dump) + log pull + cleanup.
# Wall cap: device-side `timeout -s KILL 280`. /data/local/tmp/g14/ ONLY
# (never mg/). Log output is logcat tag "Granite" (Granite logging on
# Android targets logcat, not stderr). G14 result: exit 139, 0 PPMs.
set -e
export COPYFILE_DISABLE=1
DEV=622c49b1
G14DIR=/data/local/tmp/g14
SSD14="/Volumes/Extreme SSD/ps2x-g14"
adb -s $DEV shell "rm -rf $G14DIR && mkdir -p $G14DIR && df -h /data"
adb -s $DEV push "/Volumes/Extreme SSD/ps2x-g13/g13-dump.gs" $G14DIR/g13-dump.gs
adb -s $DEV push "/Volumes/Extreme SSD/parallel-gs-g14-android-build/tools/parallel-gs-replayer" $G14DIR/parallel-gs-replayer
adb -s $DEV shell "cd $G14DIR && chmod 755 parallel-gs-replayer && ls -la && sha256sum g13-dump.gs parallel-gs-replayer"
adb -s $DEV logcat -d -s Granite:V | tail -3            # before-snapshot (expect empty)
adb -s $DEV shell "cd $G14DIR && date +%s; timeout -s KILL 280 ./parallel-gs-replayer $G14DIR/g13-dump.gs --iterations 2; echo RUN_EXIT=\$?; date +%s"
adb -s $DEV logcat -d -s Granite:V > "$SSD14/g14-logcat.txt"   # run log
adb -s $DEV shell "ls -la $G14DIR/"                     # outputs (PPMs if any)
# Pull scanouts when present: adb -s $DEV pull $G14DIR/ <staging> (G14: none produced)
adb -s $DEV shell "rm -f $G14DIR/parallel-gs-replayer $G14DIR/g13-dump.gs && rmdir $G14DIR && ls /data/local/tmp/"
