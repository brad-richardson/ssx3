# P1ag — Long-boot proof: the 4th sema-30 signal + thread-3 release downstream of the hash phase (no fork changes)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 29 (P1af) first —
all of it: the SPR fix unparked the `0x394ED0` walk (104k balanced
calls, 0 cycles), main is RUNNING game code at 90 s, and the 4th
sema-30 signal is predicted downstream of the still-running hash
phase (§P28-3a link 6, P29-2d/f). This brief PROVES that prediction
with a longer boot. Peer lanes run concurrently — you share the fork
remote AND the fork tree with T1 (snapshot emitter work may be in
the tree; see below).

## Facts you start from

- Fork `$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch
  `ssx3`, at `e483d8d` (P1af's SPR fix, pushed). P1af's binaries
  are gone — you rebuild.
- P1af end state (both 90 s boots): thread 1 RUNNING `0x39b72c`,
  threads 2–6 WAIT (26/30/31/32/36), sema-30 3 signals / 4 waits
  ending parked, 5.3k returning `0x362DE8` invocations and going,
  stubs steady at 222 distinct, no park anywhere.
- T1 may have uncommitted emitter changes in `$R` when you build.
  That is EXPECTED (P1af §P29-3 precedent): record `git status` +
  `git log` + mtimes at build time, build anyway, and note that
  the snapshot emitter (if present) is env-off. NEVER stage, touch,
  or commit foreign files. You make ZERO fork commits.

## Gates and rules

- Lease `P1ag`: boots ONLY while holding `/tmp/ssx3-p-lane-lease`
  (the SHARED P-lane lease) — if it names another agent (T1's
  proof boot has priority: yield to it), poll every 5 min and log
  waits to `$W/P1/run/p1ag-waits.log`. Max 2 boots: ONE long boot
  ≤300 s foreground + ONE optional ≤90 s confirm. No `adb`.
- NO fork changes of any kind (diag brief — no source edits, no
  commits, no push). The 20k probe cap stays (P1af §P29-5); trace
  enter/exit gives totals.
- Evidence: append Part 30 to `local/research/P1/REPORT.md` ONLY
  (no other ssx3 files). Commit with `git add -f`, prefix
  `[P1ag]`, trailer `Orchestrated-By: Muse Code`. NEVER run `git
  push` in ssx3.
- Time box: 4 h. Tables, no verdicts.

## Task 1 — rebuild + long boot (the 4th signal)

1. Record tree state (`git log --oneline -3`, `git status
   --short`, `git diff --stat` if dirty), rebuild
   `ps2EntryRunner` (`-j4`), record binary sha.
2. Claim the P-lane lease; run ONE boot up to 300 s foreground
   (same env/scripts as P1af: `PS2X_DIAG_394ED0=1` kept; sed the
   LOG name). Kill at first sight of thread-3 RUNNING post-90 s
   + 30 s grace, or at 300 s. Release the lease immediately.
3. Mine: sema-30 signal #4 (line, pc, signalling thread) or its
   continued absence with the hash-phase progress counters
   (`0x362DE8` invocation total, main pc samples); thread-3's
   first RUNNING sample (block, pc); stub-distinct series (new
   phases show as new distinct counts).

## Task 2 — phase-exit table (what main does next)

Whether or not the signal lands, table from the long boot: main
pc-sample histogram across blocks (does `0x362DE8` stop growing?
what replaces the hash phase?); drop census (new sites?);
RPC/CD/SIF/GS deltas vs the P1af ladder; crash/FATAL count. If a
NEW park appears (all-N stub phase, hung call, frozen counters),
diagnose it to P1ad depth (shape + counts + first receipt) — that
becomes the next fix brief's §P30-3b equivalent. If main is still
in the hash phase at 300 s, table the growth rate (invocations/s
from trace totals) and the projected phase-exit time.

## Report

Part 30: lease record + tree-state-at-build + boot receipt +
sema-30 verdict table (signal #4: present with pc/thread, or
absent with progress counters) + phase-exit/new-park table +
ladder vs P1af-boot1 + gap rows. Commit REPORT.md only, stop.
