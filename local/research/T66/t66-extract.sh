#!/usr/bin/env bash
# T66 extract: t66 line families + markers from the capture emulog.
G=/home/brad/pcsx2-g7; E=$G/dat-t57/PCSX2/logs/emulog.txt; T4=/home/brad/pcsx2-t4; S=/mnt/c/Users/bradr/t66stage
TAG=${1:-t66a}
ls -la $E; sha256sum $E
grep -a "t66w \|t66chg \|t66f \|t66v \|t66cen \|t66obj\|t66scan \|T52_MARK" $E > $S/$TAG-trace.txt
grep -a "T48_PATHS" $E | head -1 > $S/$TAG-paths-first.txt; grep -a "T48_PATHS" $E | tail -1 >> $S/$TAG-paths-first.txt
cp $T4/$TAG-poll.log $T4/$TAG-shot-sc.png $S/ 2>/dev/null
wc -l $S/$TAG-trace.txt; sha256sum $S/$TAG-trace.txt
