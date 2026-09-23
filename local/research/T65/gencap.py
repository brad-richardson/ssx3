src = open('/Users/brad/dev/ssx3/local/research/T48/t48-capB.sh').read()
s = src
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)
rep("# T48 Capture B (v3): lean closed-loop. Identity-vs-ref legs (no pre-snaps,\n# no depart gates); event verified by orange-bar presence; rules by\n# Cross->animated loop; loading-animated gate before pre-race wait.\n",
    "# T65 capture: T48 Capture B's route (t48-capB.sh v5, dat-t48: EE rec, VU1 interp, MTVU off) on the T65 build.\n# /tmp/t65-arm from boot (T65_BOX every vsync); VU1 dump #1 at settled Select Character, #2 + T48 GS dump in the race;\n# F1 race statefile at the end. Changes vs t48-capB.sh are marked T65.\n")
rep("LOG=$T4/t48b-poll.log", "TAG=${TAG:-t65a}\nLOG=$T4/$TAG-poll.log")
rep('fail() { echo "T48B_FAIL:$1"; stamp; kill $(cat $T4/pcsx2-t48.pid) 2>/dev/null; sleep 5; exit 1; }',
    'fail() { echo "T65_FAIL:$1"; stamp; kill $(cat $T4/pcsx2-t65.pid) 2>/dev/null; sleep 5; exit 1; }')
rep("wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; }",
    "wallcheck() { [ $(( $(date -u +%s) - T_BOOT )) -lt $WALL_CAP ] || fail WALL_CAP; [ $(stat -c %s $E 2>/dev/null || echo 0) -lt 2000000000 ] || fail EMULOG_CAP; } # T65: +2 GB emulog cap")
rep("cp \"$SNAPS/$NEW\" $T4/t48-shot-$LAB.png || fail GSHOT_CP_$LAB\n  ls -la $T4/t48-shot-$LAB.png",
    "cp \"$SNAPS/$NEW\" $T4/t65-shot-$LAB.png || fail GSHOT_CP_$LAB\n  ls -la $T4/t65-shot-$LAB.png")
s = s.replace("t48b-", "$TAG-")
rep("rm -f /tmp/t48-arm /tmp/t48-dump-now\ntouch /tmp/t48-arm; ls -la /tmp/t48-arm",
    "rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump /tmp/t65-arm /tmp/t65-vu-now # T65\nrm -f /tmp/t52-mark-* $G/t65-vu1-*.bin # T65\ntouch /tmp/t48-arm /tmp/t65-arm; ls -la /tmp/t48-arm /tmp/t65-arm # T65: box from boot")
s = s.replace("pcsx2-t48.pid", "pcsx2-t65.pid")
rep("xvfb-t48b.log", "xvfb-$TAG.log")
rep("boot-t48b.log", "boot-$TAG.log")
rep("boot-t48b.stdout", "boot-$TAG.stdout")
rep('''vudump() {''', '''vudump() {''', 0) if False else None
rep("leg() {", '''vudump() { # T65: request one VU1 dump (3 EE vsyncs) and wait for its DONE line.
  local N=$1 LAB=$2
  touch /tmp/t65-vu-now
  plog "VUDUMP_${LAB}_REQ_WALL:$(date -u +%s.%N)"
  for W in $(seq 1 20); do
    sleep 2; wallcheck
    if grep -q "T65_VU_DONE n=$N " $E 2>/dev/null; then plog "VUDUMP_${LAB} done at wait$W: $(grep "T65_VU_DONE n=$N " $E | tail -1)"; return 0; fi
  done
  fail NO_VUDUMP_$LAB
}
leg() {''')
rep("leg K MENU $REFSC\n", '''leg K MENU $REFSC
sleep 15; wallcheck # T65: settle Select Character, then the control dump
snap $TAG-sc-settled || fail SNAP_SC_SETTLED
read SM SP <<< $(score_ref $T4/$TAG-sc-settled.ppm $REFSC)
plog "SC_SETTLED ident mean=$SM p99=$SP"
is_ident $SM || fail NO_SC_SETTLED
vudump 1 SC
gshot $TAG-sc
''')
rep('''touch /tmp/t48-dump-now
ls -la /tmp/t48-dump-now''', '''sleep 3 # T65
vudump 2 RACE
touch /tmp/t48-dump-now
ls -la /tmp/t48-dump-now''')
rep('''gshot $TAG-race
ls -lat $SNAPS | head -n 8
ls -la $T4/t48-shot-$TAG-race.png $E
kill $(cat $T4/pcsx2-t65.pid); sleep 10; pgrep -a pcsx2-qt || true
stamp
echo T48B_DONE''', '''gshot $TAG-race
snap $TAG-race-live || fail SNAP_RACE_LIVE
press F1 "STATE_SAVE" # T65: race statefile for reuse
T_SAVE_START=$(date -u +%s)
sleep 8
SSD=$DAT/PCSX2/sstates
STATE_NEWEST=$(ls -t "$SSD" 2>/dev/null | grep -v -i backup | head -n 1)
plog "STATE newest=$STATE_NEWEST size=$(stat -c %s "$SSD/$STATE_NEWEST") mtime=$(stat -c %Y "$SSD/$STATE_NEWEST") save_start=$T_SAVE_START"
[ $(stat -c %Y "$SSD/$STATE_NEWEST") -ge $((T_SAVE_START - 10)) ] && cp "$SSD/$STATE_NEWEST" $G/t65-race-state && sha256sum $G/t65-race-state | tee -a $LOG
plog "COUNTS box=$(grep -c 'T65_BOX' $E) vurec=$(grep -c 'T65_VUREC' $E) paths=$(grep -c 'T48_PATHS' $E) draw=$(grep -c 'G12_DRAW' $E) emulog=$(stat -c %s $E)"
ls -la $G/t65-vu1-*.bin
kill $(cat $T4/pcsx2-t65.pid); sleep 10; pgrep -a pcsx2-qt || true
rm -f /tmp/t65-arm /tmp/t48-arm
stamp
echo T65_DONE''')
open('t65-cap.sh', 'w').write(s)
