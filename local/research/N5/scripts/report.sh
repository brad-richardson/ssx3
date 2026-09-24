#!/bin/bash
# N5: host-side simpleperf reports for the race profile (unstripped .so matched by build id via --symdir).
BIN=~/n2/toolchain/android-sdk/ndk/28.2.13676358/simpleperf/bin/linux/x86_64/simpleperf
D=~/n5/prof; DATA=$D/perf-race.data; SYM=~/n5/symdir
$BIN report -i $DATA --symdir $SYM --sort comm,symbol --percent-limit 0.05 > $D/self-comm-sym.txt 2> $D/self.err; echo "SELF_RC=$?"
$BIN report -i $DATA --symdir $SYM --sort symbol,dso --percent-limit 0.05 > $D/self-sym-dso.txt 2>> $D/self.err
$BIN report -i $DATA --sort comm > $D/threads.txt 2>> $D/self.err
$BIN report -i $DATA --symdir $SYM --sort dso > $D/dso.txt 2>> $D/self.err
$BIN report -i $DATA --symdir $SYM --children --sort symbol --percent-limit 1 > $D/children.txt 2>> $D/self.err
head -12 $D/self-sym-dso.txt; echo; sed -n '1,40p' $D/threads.txt | grep -v '^$' | head -20; echo; head -25 $D/dso.txt
grep -c 'libps2EntryRunner.so\[+' $D/self-sym-dso.txt | sed 's/^/UNRESOLVED_ROWS=/'
