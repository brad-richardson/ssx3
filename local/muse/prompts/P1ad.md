# P1ad — Diagnose the new park: main 394ED0 list-walk + thread-3 sema-30

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 27 §P27-2b/c/d
first (the new park catalogue: main RUNNING in `sub_00394ED0`,
thread-3 WAIT sema-30, thread 6 WAIT 36, BIND refuted ×3), plus §P27-5
(the open items this brief owns) and §P27-2e (ladder). This is a
DIAGNOSIS brief: attribute the new park and name the exact fix brief.
No fork behavior changes (a one-line diagnostic addition is allowed
only if the park is otherwise unattributable — record the call).

## Facts you start from

P1ac's fix worked: the `0x52BE04` poll is gone, thread 3 advanced into
game code (4 new semaphores, RPC-client waits, an unhandled-host-RPC
sighting at `sid=0x80000211`), and main now spins calling
`sub_00394ED0` 15,989× (4-word memcmp + list-walk retry, dma/gif
frozen). Open threads from P27-5: (a) bounded-vs-circular for the
list-walk (needs a guest-memory trace over the walked list); (b) the
thread-3 sema-30 chain (w30=4/s30=3, signals from tid=1
`ra=0x31acf4` — who should release it?); (c) the outer loop above
`sub_00362DE8` driving the 16k calls; (d) the `0x3C45C0` SendCmd cid
(if it reappears). M15 currently holds the host lease (replays) — poll
patiently. P11 runs concurrently — you share only the fork remote, and
you should need no fork writes at all.

## Gates and rules

- Lease `P1ad`: boots ONLY while holding `/tmp/ssx3-host-lease` — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1ad-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`.
- Fork: READ-ONLY expected. If a diagnostic line is unavoidable: ONE
  file, named `git add`, one commit with the `Orchestrated-By: Muse
  Code` trailer, `git pull --rebase` first, `git push` ONLY inside the
  fork clone to the `fork` remote. Stop on any foreign rebase
  conflict. Never commit generated sources or `._*`.
- ssx3: append `## Part 28` to `local/research/P1/REPORT.md`; commit
  that file ONLY with `git add -f`, prefix `[P1ad]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Static first (lease-free).** Decode `sub_00394ED0` fully (what
   list, what target, what the memcmp compares — and why it never
   matches: empty list? unwritten nodes? wrong base?); decode the
   outer loop above `sub_00362DE8`; map the sema-30 chain (creator,
   all waiters/signallers, the missing release). Table every
   candidate cause + the evidence for and against each.
2. **Max 2 boots.** Receipts: the guest-memory trace over the walked
   list (bounded-vs-circular, node contents over time); the `[drop]`
   census (new sites firing?); sema-30 chain dynamics (does the
   waiter ever release?); unhandled-RPC sightings (shape table, not
   a fix). One ladder table vs P27-boot1 (regression check, not the
   deliverable).
3. **Attribute.** The park's cause (or the narrowed suspect list with
   the exact next probe for each) + WHY the game can't proceed + the
   exact fix brief (file, hunk shape, proof boots). If the park
   turns out to be guest-correct waiting on something upstream, the
   "fix brief" names that thing instead — evidence decides.
4. **Report.** `## Part 28` (P28-0 lease record, P28-1 static
   evidence, P28-2 boots + trace + census, P28-3 attribution + named
   fix brief, P28-4 exact commands, P28-5 what I could not do).
   Commit, remove the lease if held, stop.
