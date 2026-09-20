# P1aa — Apply the P1z amendment: kernel-true sema create/signal + boot proof

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 23 §P23-1a/b first
(P1v's clamp-1 rule + its recorded-as-PROVISIONAL note) and
`local/research/P1z/REPORT.md` §P1z-4/§P1z-5 (verdict AMENDED + the exact
A1–A3 amendment) before acting. This is a FIX brief: implement the
verdict table. The semantics judgment is already settled by kernel
disassembly evidence per the review's §7.5 rule — this brief makes no
semantics call, it applies P1z's table. (The PollSema -1/-419 bonus
divergence in P1z-7 is observed-not-fixed: a separate brief owns it.)

## Facts you start from

Stock EE `CreateSema` (@`0x800049b8`): the only -1 paths are
freelist-empty and `init<0`; max stored as-is; the signal path never
reads max (no OVF check exists). P1v's clamp-1 + retained OVF check
diverges from hardware exactly in the two-waiter-less-signals window
(hardware holds count 2; the fork loses the second signal). Current
ladder state (P24): boot parks on the `0x52BE04` stall with 33 creates,
0 `-1` waits, and a 6-line `[drop]` census. P7 runs concurrently in
another pane (movie stub, new `Stubs/` files only) — you share only the
fork remote. Suite baseline is 427/427/0 (P1y, green).

## Gates and rules

- Lease `P1aa`: boots ONLY while holding `/tmp/ssx3-host-lease` — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1aa-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`.
- Fork: the amendment files ONLY (`Kernel/EeScheduler.cpp` +
  `ps2_runtime_kernel_tests.cpp` — record exact paths). `git add`
  those NAMED files only — never `-A`, never stage or touch anything
  else. Verify the diff before committing. One commit with the
  `Orchestrated-By: Muse Code` trailer. `git pull --rebase` before
  pushing; `git push` ONLY inside the fork clone to the `fork` remote.
  If the rebase shows any conflict outside your files, stop and
  report. Never commit generated runner sources or `._*`.
- ssx3: append `## Part 25` to `local/research/P1/REPORT.md`; commit
  that file ONLY with `git add -f`, prefix `[P1aa]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Apply A1–A3 exactly.** A1: delete the `effectiveMax` clamp;
   reject ONLY `initCount < 0` (+ existing id-exhaustion); store
   `maxCount` as-is (negatives + `init>max` accepted, matching the
   kernel). A2: delete the OVF block; waiter-less signals always
   `++count` and return id. A3: zero-max test asserts `maxCount==0`;
   add the two-waiter-less-signals-then-two-waits test (count reaches
   2, all succeed, no OVF). BEFORE/AFTER receipts (same tests, unfixed
   vs fixed tree). Full suite must stay all-green (name any failure
   face — the baseline is 427/427/0).
2. **Max 2 boots (regression proof).** Receipts: boot still reaches
   the `0x52BE04` stall steady state (33 creates, 0 `-1` waits,
   balanced F6/F7 handshake, 1-line watch, `[drop]` census still
   flowing — P1w's tooling intact). One ladder table vs P24-boot1, not
   a diagnosis.
3. **Report.** `## Part 25` (P25-0 lease record, P25-1 diff +
   BEFORE/AFTER + tests, P25-2 boots + ladder check, P25-3 binaries
   and commits, P25-4 exact commands, P25-5 what I could not do).
   Commit, remove the lease if held, stop.
