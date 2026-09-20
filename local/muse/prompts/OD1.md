# OD1 — Odin port readiness of the synth path: named interface + device-run checklist

You are muse in a herdr panel in `/Users/bradrichardson/dev/ssx3`. **Tables,
no verdicts.** Read first: `docs/route-criteria.md` (all of it — the OD1 row
lives in the W-tables; this brief fills the readiness half, not PS2 numbers)
+ the M15 synth report (`local/research/M15/REPORT.md`: synth==blend, residual
2.34%, 87% |d|=1, static 95.67% exact — the path being ported) + the synth
path sources it cites (table the exact files + entry points you read). This is
Part 4 decision 4b: readiness, not the device run itself.

## Facts you start from

- Deliverable 1 — named interface: the synth path's Odin interface as a
  table (entry points, inputs/outputs with shapes + formats, build flags,
  toolchains, device-side deps). Every row points at a file+line or an exact
  gap (OPEN rows named, not hand-waved).
- Deliverable 2 — device-run checklist: what the first Odin run must show,
  as a table (check × pass bar × where the number lands). Bars reference
  `docs/route-criteria.md` B/C rows where they exist; new bars get exact
  thresholds + a one-line why.
- Reachability probe (read-only): `adb devices` + device state + thermal +
  free space, tabled. NO install, NO run, NO settings changes this brief. If
  Odin is unreachable, table that exactly (command + output) and deliver the
  doc-only half — the brief still completes.
- No lease of any kind. No PS2 boots. No fork changes. No game content moves.

## Gates and rules

- `export COPYFILE_DISABLE=1` on every SSD step.
- Evidence dir `local/research/OD1/` (STANDALONE). Commit with `git add -f`,
  prefix `[OD1]`, trailer `Orchestrated-By: Muse Code`. Do not push (the
  orchestrator pushes at poll when the tree is clean).
- Time box: 4 h. Tables, no verdicts — readiness rows only, no route
  recommendation (RC1's no-verdict rule carries over).
- Hygiene: write the report in chunks with a tail receipt (truncated tail
  fails the gate).

## Task 1 — interface table

1. Walk the synth path from the M15 citations to the Odin build: entry
   points, buffer shapes/formats, flags, toolchain, deps. Table each with
   file+line or OPEN.
2. Table the gaps between "builds/runs here" and "builds/runs on Odin"
   (each gap: what + where it bites + what closes it).

## Task 2 — device-run checklist + reachability

1. Checklist table: check × pass bar × W-table/ledger landing slot. Bars
   exact (numbers, not "fast enough").
2. Reachability probe table (`adb devices`, state, thermal, storage).
   Unreachable → exact output tabled, doc-only half delivered.

## Report

`local/research/OD1/REPORT.md`: interface table, gap table, checklist table,
reachability table, exact commands, gaps. Commit evidence (`[OD1]`), stop.
