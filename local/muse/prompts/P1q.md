# P1q — SSX 3 on PS2Recomp, Part 18: why is entry 0 never selected/completed? (no fix)

You are muse in a herdr panel, working directory
`/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch `ssx3`,
remote `fork`). Runbook: exact steps, receipts named up front, **tables,
no verdicts**. Read `/Users/bradrichardson/dev/ssx3/local/research/P1/REPORT.md`
Part 17 first (P17-1 table base + current-entry transitions, P17-2 sole
init hit + W1/W2/W3 silence), plus Part 16 §P16-2d–2f (writers,
`iFILESYS_ExecCommand`/`iFILESYS_CommandCompleteCallback` callers).
`W=/Volumes/Extreme SSD/ps2recomp-spike`. Rules exactly as
`local/muse/prompts/P1c.md` "Rules" (lease `P1q`, no adb, never commit
generated runner sources or `._*`, purge sidecars, one commit per change
with the two trailers, boots foreground ≤90 s, logs
`$W/P1/run/boot-p1q-N.log`, `PS2X_DIAG_PERIOD_MS=5000`), plus: builds
may run any time (`-j4`); boots only while holding the host lease — if
`/tmp/ssx3-host-lease` names another agent, poll every 5 minutes and log
waits to `$W/P1/run/p1q-waits.log`. Push rule: `git push` ONLY inside
this fork clone to the `fork` remote; NEVER run `git push` in
`/Users/bradrichardson/dev/ssx3`. Standing rule: machine-check EVERY
hand hex computation with python3 and paste the check line. Time box
4 hours, max 2 boots.

## Facts you start from

P1p proved the SYNCTASK wait never exits for lack of completion:
entry-0+8 (`0x5e0088`) sees exactly one hit (init zeroing `sd` @
`0x3e64d0`); W1/W2/W3 never fire; current entry `*(0x519AD4)` visits
entry 1 (`0x5e00b0`) and null, never entry 0. Parked `$a0` =
`0x900001` (top byte `0x00` → entry 0, low-20 id `0x1`). Fork HEAD
`e73e36a`, binary `7a7d4b64` fresh (rebuild only if stale). Out of
scope: sema-26 non-delivery, any behavior fix.

## Step 1 — static: entry-0's request + selection logic (no lease, no boot)

a. **Entry-0 contents.** What request sits at `0x5e0080`? Field layout
   of a `0x30`-byte table entry (id at +0? flag at +8? state/chain at
   +4/+0x28 from the W1/chained-`jalr` reads?) from the creator
   (`sub_003DCBD8`/`sub_003DCC88`), the lookup (`sub_003DE670`), and
   the consumers. ELF-decode every struct offset you cite.
b. **Selection.** How does `iFILESYS_ExecCommand` (`sub_003DDFA8`)
   choose the current entry (queue walk? head pointer? state match?)?
   Why entry 1 and never entry 0 in this boot — entry 0's state,
   position, or a predicate it fails? One row per predicate/site.
c. **Completion trigger.** What invokes W1
   (`iFILESYS_CommandCompleteCallback`) — its 10 jal sites, which are
   reachable in this boot, and what event each waits on (CD? RPC?
   timer?). If none can fire, that IS the mechanism — name it.

## Step 2 — dynamic receipt (≤2 boots, only for what static cannot close)

Candidates (pick the minimal set that closes Step 1's residue):
entry-0 full-word watches (`0x5e0080`+0/`+4`/`+8`…) to observe state
transitions; `0x519AD4` transition log across the full boot (does
entry 0 EVER get selected, even transiently?); targeted stub
observation of `0x3ddfa8`/`0x3de420` (below-cutoff in histograms —
a dedicated receipt). Design from Step 1, then run (≤90 s each).

## Step 3 — report

Append `## Part 18` (P18-0 lease record, P18-1 entry-0 + selection +
completion analysis, P18-2 dynamic receipts, P18-3 binaries and
commits, P18-4 exact commands, P18-5 what I could not do) to
`local/research/P1/REPORT.md` in `/Users/bradrichardson/dev/ssx3`;
commit with `git add -f`, prefix `[P1q]`, trailers; push `fork ssx3`
from the fork clone only (expect nothing to push — verify up-to-date);
remove the lease if held; stop.
