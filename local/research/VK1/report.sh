#!/bin/bash
# VK1 stage 1: symbolize one Odin perf.data on the mini with NDK r30's host
# simpleperf + F5's unstripped libps2EntryRunner.so (Build ID e39b09b3…, same
# as the F5 APK's). Reports go to local/research/VK1/reports/<label>-*.txt.
# Usage: report.sh <label>   (perf data at ~/dev/ssx3-work/VK1/odin/<label>/perf-<label>.data)
set -euo pipefail
L=$1
SP=/opt/homebrew/share/android-ndk/simpleperf/bin/darwin/x86_64/simpleperf
SYM=$HOME/dev/ssx3-work/VK1/symdir
IN=$HOME/dev/ssx3-work/VK1/odin/$L/perf-$L.data
OUT=$HOME/dev/ssx3/local/research/VK1/reports
mkdir -p "$OUT"
R() { "$SP" report -i "$IN" --symdir "$SYM" "$@"; }
R --sort comm > "$OUT/$L-threads.txt"
R --sort comm,dso > "$OUT/$L-comm-dso.txt"
R --sort comm,dso,symbol --percent-limit 0.2 > "$OUT/$L-comm-dso-sym.txt"
# Where the GsWorker's and main thread's time goes, callers included.
R --children --sort comm,symbol --comms GsWorker --percent-limit 1 > "$OUT/$L-gsworker-children.txt"
# Call graph (1+ MB) stays in scratch, not git.
mkdir -p "$HOME/dev/ssx3-work/VK1/reports-big"
R --children --sort comm,symbol --percent-limit 1 -g caller --comms GsWorker > "$HOME/dev/ssx3-work/VK1/reports-big/$L-gsworker-callgraph.txt" 2>/dev/null || true
wc -l "$OUT/$L"-*.txt
# Finer rows for the present path: GsWorker + main (comm com.ps2x.runner), >= 0.02 %.
R --sort comm,dso,symbol --comms GsWorker,com.ps2x.runner --percent-limit 0.02 > "$OUT/$L-present-threads-sym.txt"
