# P1y — Fix the flaky ps2xTest pair (AFAIL↔GsSyncV alternation)

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read `local/research/P1/REPORT.md` Part 23 §P23-1c first
(the 426-test table: P1v saw the GsSyncV face, the orchestrator's re-run
on the same tree saw the AFAIL face). This is a FIX brief: make the suite
deterministically green. Queued since P1j; it costs every gate read a
"pre-existing failure" paragraph.

## Facts you start from

One `ps2xTest` case fails build-to-build, alternating between the AFAIL
face (`GS alpha-test AFAIL independently masks framebuffer and depth`)
and the GsSyncV face (`sceGsSyncVCallback … reserved async stack pool`)
on the same tree — order/state dependent, documented pre-existing. P1w
runs concurrently in another pane (fork tooling, builds in
`/tmp/p1-link`) — you share only the fork remote.

## Gates and rules

- Host tests only: NO fork boots, no lease, no `adb`. Builds any time
  (`-j4`) in your OWN build dir on the SSD
  (`/Volumes/Extreme SSD/ps2x-p1y/build` — NEVER `/tmp/p1-link`,
  P1w builds there; internal disk is tight so heavy artifacts stay on
  the SSD).
- Fork: fix + test changes only, one commit per change with the
  two-trailer convention (copy from the previous fork commit);
  `git pull --rebase` before pushing; `git push` ONLY inside the fork
  clone to the `fork` remote. Never commit generated runner sources or
  `._*`. If a rebase shows a conflict outside your files, stop and
  report — do not resolve P1w's side.
- Evidence dir `local/research/P1y/` (STANDALONE — do NOT append to
  `P1/REPORT.md`; a peer brief owns it concurrently). Commit with
  `git add -f`, prefix `[P1y]`, two-trailer convention (copy from the
  previous ssx3 commit). NEVER run `git push` in ssx3.
- Time box 4 hours.

## Steps

1. **Reproduce both faces.** Build the suite in your dir, run it N≥5
   times (record every run: pass/fail + face). Then isolate: single-test
   runs, subset runs, ordering probes — table what the alternation
   depends on.
2. **Fix.** The minimal correct fix (test isolation/harness ordering vs
   a real product bug — evidence decides; record the call). Rebuild,
   run N≥5 times: all green, both faces gone.
3. **Prove no drift.** Full-suite count before/after (expect 426 total,
   0 fail after), and confirm the P1v zero-max test still passes.
4. **Report.** `local/research/P1y/REPORT.md`: reproduction table,
   isolation evidence, diff + why, before/after run tables, exact
   commands, receipt paths, "What I could not do". Commit, stop.
