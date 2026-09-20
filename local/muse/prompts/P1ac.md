# P1ac — Complete the SIF ready-handshake in the HLE (sregs[1]=1)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 26 §P26-3 first
(the attribution + this brief's exact spec), plus §P26-1f (poller
sequence) and §P26-1h (host audit). This is a FIX brief: implement
§P26-3c exactly. P9/P11 run concurrently in other panes — you share
only the fork remote.

## Facts you start from

`0x52BE04` is SIF `sregs[1]`; the game sends `SET_SREG(1,1)` and spins
while it reads 0. On HW the IOP's reply packet arrives via SIF0 DMA and
EE `set_sreg` writes the word; in the HLE the send is a no-op, no SIF0
exists, and the handler map is write-only. The fix completes the
handshake host-side, gated to SSX3. P1ab's predicted next stall: the
game's BIND (`sub_0040B400` → `SendCmd(0x19)` → `WaitSema($s2)` at
`0x40B55C`) parks on an RPC sema — your boots confirm or refute this
(report row, not a second implementation).

## Gates and rules

- Lease `P1ac`: boots ONLY while holding `/tmp/ssx3-host-lease` — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1ac-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`.
- Fork: the named files ONLY (`Syscalls/RPC.cpp` handshake hunk +
  `System.cpp:441` args ride-along + a test if the harness allows —
  record the list). `git add` those NAMED files only — never `-A`,
  never stage or touch anything else. Verify the diff before
  committing. One commit per change with the `Orchestrated-By: Muse
  Code` trailer. `git pull --rebase` before pushing; `git push` ONLY
  inside the fork clone to the `fork` remote. Stop on any foreign
  rebase conflict. Never commit generated sources or `._*`.
- ssx3: append `## Part 27` to `local/research/P1/REPORT.md`; commit
  that file ONLY with `git add -f`, prefix `[P1ac]`, trailer
  `Orchestrated-By: Muse Code`. NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Implement §P26-3c.** In `sceSifSendCmd`, after the extra-copy
   block: if the game is SSX3 (existing `ps2_game_overrides`
   descriptor registry, SLUS-keyed per `games_database.cpp`) AND
   `cid==0x80000001` AND guest packet word[4]==1: write u32 `1` to
   guest `0x52BE04` via `getMemPtr`+`memcpy` + one capped stderr
   receipt line (`[sif-handshake] sregs[1]=1`); return stays 1.
   Ride-along (same commit or second — your call, recorded): add
   `syscallNumber`+`handler` args to the `:441` override `emitDrop`
   (format-only, zero behavior delta). BEFORE/AFTER receipts (census
   line shape + new receipt line present/absent); suite must stay
   all-green (name any face).
2. **Max 2 boots.** Expect: `0x425cf0` counts collapse (poll exits),
   thread-3 pc leaves `0x40b1d0`/`0x425cf0`, thread 3 advances past
   `0x2290E8`, sregs watch stays silent (bypass write — receipt line
   + poll-exit are the proof rows). Catalogue the new park / RPC
   traffic; confirm-or-refute the BIND prediction with line
   receipts. One ladder table vs P26-boot1.
3. **Report.** `## Part 27` (P27-0 lease record, P27-1 diff +
   BEFORE/AFTER + tests, P27-2 boots + poll-exit proof + new park,
   P27-3 binaries and commits, P27-4 exact commands, P27-5 what I
   could not do). Commit, remove the lease if held, stop.
