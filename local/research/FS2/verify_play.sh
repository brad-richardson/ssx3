#!/bin/bash
# Read-only check that Brad's play state is in place (stands in for odin_restore_play.sh's
# exit code while its fan-restore line exits 1 when /data/local/tmp/mg/fan_prev is absent).
S=$(cat /Users/brad/dev/ssx3/local/odin-serial); F=/storage/emulated/0/Android/data/com.ps2x.runner/files
P=~/dev/ssx3-work/odin-play; WA=$(awk '$2=="app-release.apk"{print $1}' $P/SHA256SUMS); WE=$(awk '$2=="ps2x.env"{print $1}' $P/SHA256SUMS)
a=$(adb -s $S shell 'pm path com.ps2x.runner | cut -d: -f2 | xargs sha256sum' | cut -d' ' -f1)
e=$(adb -s $S shell sha256sum $F/ps2x.env | cut -d' ' -f1)
t=$(adb -s $S shell "ls -A $F/mc0-test 2>/dev/null | wc -l" | tr -d ' \r')
p=$(adb -s $S shell pidof com.ps2x.runner | tr -d '\r')
ok=1; [ "$a" = "$WA" ] || ok=0; [ "$e" = "$WE" ] || ok=0; [ "$t" = 0 ] || ok=0; [ -z "$p" ] || ok=0
for f in BASLUS-20772-GAM0001/BASLUS-20772-GAM0001 BASLUS-20772-GAM0001/icon.sys BASLUS-20772-GAM0001/ssx1.ico BASLUS-20772-SET0001/BASLUS-20772-SET0001 BASLUS-20772-SET0001/icon.sys BASLUS-20772-SET0001/ssx1.ico; do
  w=$(shasum -a 256 ~/dev/ssx3-work/E55D16/mc0/$f | cut -d' ' -f1); h=$(adb -s $S shell sha256sum $F/mc0/$f | cut -d' ' -f1); [ "$w" = "$h" ] || { ok=0; echo "save MISMATCH $f"; }
done
echo "VERIFY apk=${a:0:12} env=${e:0:12} mc0-test=$t pid=${p:-none} saves-checked ok=$ok"; [ $ok = 1 ]
