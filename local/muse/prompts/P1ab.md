# P1ab — Diagnose the thread-3 `0x52BE04` poll (census in hand)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 23 §P23-2e/i first
(the stall: thread 3 spins `while (*(0x52BE04)==0)` ~2M calls/block via
`sub_00425CF0`, and boot 2 proved the word never CPU-written), plus Part
25 §P25-2 (current ladder state: same stall, 6-line `[drop]` census, all
`dispatchSyscallOverride`), plus Part 24 §P24-1f/g (what the census
covers and its exclusion rules). This is a DIAGNOSIS brief: attribute the
silence and name the exact fix brief. No fork behavior changes (a
one-line diagnostic addition is allowed only if the stall is otherwise
unattributable — record the call).

## Facts you start from

Open threads from P23-5/P25: (a) no JAL/word sweep was ever run for the
setter entry `0x425d08` (0 printed stub lines = below cutoff, not
absence); (b) host-side `memcpy`/DMA/SIF blits bypassing the watch's
`macros.h` report path are not excluded; (c) `0x52BE04`'s ELF
section/initial bytes were never dumped; (d) the mailbox struct shape
(sibling entries `0x425d08` setter / `0x425d28` base-getter) is unread;
(e) the 6 `dispatchSyscallOverride` drops are unattributed (args gap).
P9/P10 run concurrently in other panes (shim→split, PollSema) — you
share only the fork remote, and you should need no fork writes at all.

## Gates and rules

- Lease `P1ab`: boots ONLY while holding `/tmp/ssx3-host-lease` — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1ab-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`.
- Fork: READ-ONLY expected. If a diagnostic line is unavoidable: ONE
  file, named `git add`, one commit with the `Orchestrated-By: Muse
  Code` trailer, `git pull --rebase` first, `git push` ONLY inside the
  fork clone to the `fork` remote. Stop on any foreign rebase
  conflict. Never commit generated sources or `._*`.
- ssx3: append `## Part 26` to `local/research/P1/REPORT.md`; commit
  that file ONLY with `git add -f`, prefix `[P1ab]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Static first (lease-free).** Dump `0x52BE04`'s ELF section +
   bytes; read the full mailbox file (`0x425cf0`/`0x425d08`/`0x425d28`
   + callers); run the setter-entry JAL/word sweep P1v skipped; audit
   host-side write paths that bypass the watch (memcpy/DMA/SIF sites
   with file:line). Table every candidate writer + the evidence for
   and against each.
2. **Max 2 boots.** Receipts: the `[drop]` census (any new site firing
   near the stall? the override-6 unchanged?); setter-entry call
   evidence (or its confirmed absence); whatever watch/probe row
   closes a candidate. One ladder table vs P25-boot1 (regression
   check, not the deliverable).
3. **Attribute.** The writer (or the narrowed suspect list with the
   exact next probe for each) + WHY it never fires + the exact fix
   brief (file, hunk shape, proof boots). If the stall turns out to be
   guest-correct behavior waiting on something upstream (e.g. an
   ordering dependency), the "fix brief" names that thing instead —
   evidence decides.
4. **Report.** `## Part 26` (P26-0 lease record, P26-1 static evidence,
   P26-2 boots + census, P26-3 attribution + named fix brief, P26-4
   exact commands, P26-5 what I could not do). Commit, remove the
   lease if held, stop.
