# P1w — Land "no silent drops" in the fork + track the function-map CSV

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 23 first (P1v's fix
+ the new `0x52BE04` stall — context ONLY, you are not diagnosing it),
plus `docs/research/review-2026-09-19-progress.md` §4.2/§7.2 (the
silent-drop pattern) and §7.4 (CSV home). This is a TOOLING brief: make
the next park diagnosable in a single boot.

## Facts you start from

Three of eight ladder rungs were the runtime discarding something without
a trace (`SetAlarm` reject P1c, analyzer MMIO fold P1g, scheduler pc-zero
P1s). The function-map CSV (1000+ splits, currently untracked on the SSD
under `P1/`) now lives in the fork branch alongside the TOML per user
decision — verify the exact SSD path, do NOT assume. P1x runs concurrently
in another pane (PCSX2 reference trace; read-only, own report dir) — you
share only the fork remote, and it never pushes.

## Gates and rules

- Lease `P1w`: boots ONLY while holding `/tmp/ssx3-host-lease` — if it
  names another agent, poll every 5 min and log waits to
  `$W/P1/run/p1w-waits.log`. Builds any time (`-j4`). Max 2 boots,
  ≤90 s foreground each. No `adb`.
- Fork: one commit per change with the two-trailer convention (copy from
  the previous fork commit); `git pull --rebase` before pushing; `git
  push` ONLY inside the fork clone to the `fork` remote. Never commit
  generated runner sources or `._*` (purge sidecars).
- ssx3: append `## Part 24` to `local/research/P1/REPORT.md`; commit that
  file ONLY with `git add -f`, prefix `[P1w]`, two-trailer convention
  (copy from the previous ssx3 commit). NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Track the CSV.** Move the P1 function-map CSV into the fork branch
   next to the TOML (record both exact paths). One `Config:` commit,
   push fork. Verify the build still resolves it end-to-end; if the
   wiring needs a loader change beyond a path, record it as a gap row
   and do NOT redesign the loader.
2. **Drop census.** Every rejected or unhandled path in
   `Kernel/EeScheduler.cpp`, the `Kernel/Syscalls` dispatcher,
   `Stubs/*`, and `elf_analyzer` emits one line (`[drop] <site>
   <reason> <args>`) — on by default in the runner, with a kill-switch
   env (your call, recorded). One commit (+ unit test where the harness
   allows), rebuild, run the suite (name the failure face — AFAIL and
   GsSyncV alternate pre-existing).
3. **Max 2 boots.** Receipts: the `[drop]` census table (site × count,
   top 20 + total) + a ladder check that the boot still reaches the
   `0x52BE04` stall steady state (one table — regression check, not a
   diagnosis).
4. **Report.** `## Part 24` (P24-0 lease record, P24-1 CSV + diff +
   tests, P24-2 boots + census + ladder check, P24-3 binaries and
   commits, P24-4 exact commands, P24-5 what I could not do). Commit,
   remove the lease if held, stop.
