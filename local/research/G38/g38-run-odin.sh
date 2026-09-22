#!/usr/bin/env bash
# G38: the ONE Odin run — G31 observation binary REUSED (no rebuild;
# re-verified c91719a0 at build-time-record + PASS1 + PASS2 + pre-push +
# on-device + post-run + report). SAME shape as the Mac leg.
# Transient dir /data/local/tmp/g38/ ONLY; explicit pull list (G31-E1).
set -u
export COPYFILE_DISABLE=1
SSD="/Volumes/Extreme SSD"
DEV=622c49b1
D=/data/local/tmp/g38
adb -s $DEV shell 'rm -rf /data/local/tmp/g38 && mkdir -p /data/local/tmp/g38'
adb -s $DEV push "$SSD/ps2x-g13/g13-dump.gs" $D/g13-dump.gs
adb -s $DEV push "$SSD/parallel-gs-g31-android-build/tools/parallel-gs-replayer" $D/parallel-gs-replayer
adb -s $DEV shell "sha256sum $D/g13-dump.gs $D/parallel-gs-replayer"  # NO gap
adb -s $DEV logcat -c
adb -s $DEV shell "cd $D && date +%s; PGS_SKIP_COMPILATION_TASKS=1 timeout -s KILL 280 ./parallel-gs-replayer $D/g13-dump.gs --iterations 2 --disable-sampler-feedback > g38-run-stdout.txt 2> g38-run-stderr.txt; echo RUN_EXIT=\$?; date +%s"
adb -s $DEV logcat -d -s Granite:V > "$SSD/ps2x-g38/g38-odin-logcat.txt"
for f in g38-run-stdout.txt g38-run-stderr.txt g13-dump.gs.g10-vsync0.ppm g13-dump.gs.g10-vsync1.ppm g13-dump.gs.g10-vsync2.ppm g13-dump.gs.g10-vsync3.ppm g13-dump.gs.g10-vsync4.ppm g13-dump.gs.g10-vsync5.ppm g13-dump.gs.g10-vsync6.ppm g13-dump.gs.g10-vsync7.ppm g13-dump.gs.g8-first.ppm g13-dump.gs.g8-last.ppm; do
  adb -s $DEV pull $D/$f "$SSD/ps2x-g38/odin-$f"
done
adb -s $DEV shell "ls -la $D/; ls -lt /data/tombstones/ | head -4; sha256sum $D/parallel-gs-replayer"
adb -s $DEV shell 'rm -rf /data/local/tmp/g38 && ls /data/local/tmp/'  # OWN step
