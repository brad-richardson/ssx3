#!/usr/bin/env bash
# T65 extract: line families from the capture emulog + dumps into a stage dir.
G=/home/brad/pcsx2-g7
E=$G/dat-t48/PCSX2/logs/emulog.txt
S=$G/t65-out
T4=/home/brad/pcsx2-t4
mkdir -p $S
ls -la $E; sha256sum $E
echo "=== top prefixes ==="
sed -n '1~50p' $E | sed -E 's/^\[ *[0-9.]+\] //' | awk '{print $1}' | sort | uniq -c | sort -rn | head -12
grep -a "T65_BOX" $E > $S/t65a-box.txt
grep -a "T65_VU\|T48_DUMP_QUEUED\|T48_MODE\|T52_MARK" $E > $S/t65a-vu.txt
grep -a "T48_PATHS" $E > $S/t65a-paths.txt
grep -a "T48_VU1 " $E > $S/t65a-t48vu1.txt
grep -a "G12_DRAW\|G12_VSYNC\|DUMP_VSYNC" $E > $S/t65a-draw.txt
cp $G/t65-vu1-1.bin $G/t65-vu1-2.bin $S/
cp $T4/t65a-poll.log $T4/t65-shot-t65a-sc.png $T4/t65-shot-t65a-race.png $T4/t65-shot-t65a-rules.png $S/ 2>/dev/null
pnmtopng $T4/t65a-race-live.ppm > $S/t65a-race-live.png 2>/dev/null
pnmtopng $T4/t65a-sc-settled.ppm > $S/t65a-sc-settled.png 2>/dev/null
NEWGS=$(ls -t "$G/dat-t48/PCSX2/snaps/" | grep "\.gs" | head -1); echo "GS dump: $NEWGS"
ls -la "$G/dat-t48/PCSX2/snaps/$NEWGS"; sha256sum "$G/dat-t48/PCSX2/snaps/$NEWGS"
zstd -q -f -19 "$G/dat-t48/PCSX2/snaps/$NEWGS" -o $S/t65a-race.gs.zst 2>/dev/null || cp "$G/dat-t48/PCSX2/snaps/$NEWGS" $S/t65a-race.gs
sha256sum $G/t65-race-state
wc -l $S/*.txt; sha256sum $S/*.bin
cd $S && tar czf /mnt/c/Users/bradr/t65stage/t65a-out.tgz . && ls -la /mnt/c/Users/bradr/t65stage/t65a-out.tgz
