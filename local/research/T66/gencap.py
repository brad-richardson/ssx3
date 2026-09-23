s = open('/Users/brad/dev/ssx3/local/research/T64/t64-cap.sh').read()
def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a, s.count(a)); s = s.replace(a, b)
rep("# T64 capture: t63-menu-state under EE+VU0 interp, K to SC settled.\n# Window covers the MENU->SC scene build plus a settled tail. Proves SC via\n# F8 + LOADED band; the ebw/ebwlast tail proves the buffers' end state.\n",
    "# T66 capture: T64's recipe (t63-menu-state, dat-t57 EE+VU0 interp) -> K -> SC settled, on the T66 build.\n# t66w/t66chg/t66cen watch the quaternion at 0x00bc5950 from the MENU state; /tmp/t66-dump at settled SC\n# dumps object 0x00bc5920 for 3 vsyncs + one RAM scan. Changes vs t64-cap.sh are marked T66.\n")
rep("TAG=${TAG:-t64a}", "TAG=${TAG:-t66a}")
rep('fail() { echo "T58_FAIL:$1";', 'fail() { echo "T66_FAIL:$1";')
rep("rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump\ntouch /tmp/t48-arm /tmp/t50-arm /tmp/t51-arm",
    "rm -f /tmp/t48-arm /tmp/t48-dump-now /tmp/t49-arm /tmp/t50-arm /tmp/t50-free /tmp/t51-arm /tmp/t51-free /tmp/t51-watch /tmp/t53-watch /tmp/t54-watch /tmp/t56-watch2 /tmp/t59-dump /tmp/t65-arm /tmp/t65-vu-now /tmp/t66-dump /tmp/t52-mark-* # T66\ntouch /tmp/t48-arm # T66: only the G13-autodump suppressor; older lanes' log gates stay off")
rep("touch /tmp/t50-free /tmp/t51-free\nplog \"FREE_GATE_OPEN_WALL:$(date -u +%s.%N)\"\n", "")
rep('press K "MENU_CROSS" 2', 'touch /tmp/t52-mark-scentry # T66\npress K "MENU_CROSS" 2')
rep('touch /tmp/t59-dump\nplog "DUMP_GATE_WALL:$(date -u +%s.%N)"\nsleep 5\n',
    '''touch /tmp/t52-mark-scsettled /tmp/t66-dump # T66
plog "DUMP_GATE_WALL:$(date -u +%s.%N)"
DONE=0
for W in $(seq 1 15); do sleep 2; wallcheck; if grep -q "t66obj_done" $E 2>/dev/null; then DONE=1; break; fi; done
plog "T66_OBJ_DONE=$DONE $(grep -a t66obj_done $E | tail -1)"
[ $DONE -eq 1 ] || fail NO_T66_DUMP
''')
old_counts = [l for l in s.splitlines() if l.startswith('plog "COUNTS')][0]
rep(old_counts, 'plog "COUNTS t66w=$(grep -ac \'t66w vsync=\' $E) t66chg=$(grep -ac \'t66chg vsync=\' $E) t66f=$(grep -ac \'t66f vsync=\' $E) t66v=$(grep -ac \'t66v vsync=\' $E) t66cen=$(grep -ac \'t66cen vsync=\' $E) t66obj=$(grep -ac \'t66obj vsync=\' $E) t66scan=$(grep -ac \'t66scan vsync=\' $E) marks=$(grep -ac T52_MARK $E) emulog=$(stat -c %s $E)"')
rep("echo T64_DONE", "rm -f /tmp/t48-arm /tmp/t66-dump\necho T66_DONE")
open('t66-cap.sh', 'w').write(s)
