# E31 CHECKPOINT (pause 2026-09-22 ~19:27Z, Brad needs laptop)

## Done (all 12 boots used; nothing in flight)

- **Mission 1**: e31a — guest polls pad (2 opens, ~46 reads/s); latched START
  delivered (`[padread]`×48) but title never advances. Verdict: need
  press-and-release (Mission 2 premise).
- **Mission 2**: `PS2X_PAD_SCRIPT` implemented on fork branch
  `e29-movie-bypass`, commit `96893da` (489+/0-, Pad.cpp/Pad.h/pad_input_tests.cpp),
  local only, never pushed/merged. Suite **461/461** (fork root, flags off).
  Binary `cec1c024…fb9` (163530496 B, 2 matching SHA reads).
  Scripted path proven: title → main menu → character (Zoe) → setup →
  peak 1 → mode Race → event → rules → loading.
- **Mission 3**: all four bars MET on **Happiness (Rival Challenge)** in e31l:
  (1) menus responding, (2) loading 0→100%, (3) race HUD
  (`1ST/2`, timer, SUPER UBER, 1%, EA RADIO popup), (4) timer advances
  00:00:03 (570.55/572.59/574.64s) → 00:00:04 (578.82/580.91/583.00s+final)
  with visible scene motion, down-tuck held.
- **Snow Jam (Race) stalls at 99%** (e31g: 52 s stuck; e31h: 127 s+ stuck):
  live loop, zero CD reads after ~478 s, zero errors, pump = 0x27CEA8 fan-out
  via 0x27D330/0x284B58 @43.5k/s, park t1 Ready pc=0x423dc8. Tabled in REPORT.
- **No-aggr experiment**: `e31-noaggr-build` (AGRESSIVE_LOGS=OFF), 461/461,
  binary `ee11b25d…5c05bb`. e31i NOT faster (9.1 vs 11.6 frame-ticks/s) →
  function trace is NOT the bottleneck (software GS is). Parked.
- e31l (last boot): rc 0, **cap:function_log** @583.5 s (5 GiB trace cap;
  this run was the fastest: 7637 frame ticks). All 13 script inputs delivered.
  Lease released, runner dead (verified). Race frames pinned:
  - final `upload-latest.png` 38697 B `14146c15…d9ecd` (00:00:04)
  - snap-0572.59s 45568 B `993cfe87…92b52` (00:00:03)
  - snap-0578.82s 41269 B `5f91afee…7125b` (00:00:04)
  - snap-0580.91s 41049 B `de266e7b…3533c` (00:00:04)
  - snap-0583.00s 43750 B `7ae9cabe…d2ba3` (00:00:04)
  - snap-0570.55s 49071 B (SHA in frame-pins.json on resume) (00:00:03)

## State

- Fork worktree on `e29-movie-bypass` (`96893da`), status: `M` nothing
  (committed); `??` ps2_log.txt + `._MPEG.cpp.appledouble-retained-e31`
  (gitignored). **ssx3 mainline untouched at `3adc0478`** (must re-verify).
- ssx3 repo: REPORT.md drafted (needs e31k/l sections), e31_boot.py final,
  frame-pins.json NOT yet written. Nothing committed yet except fork commit.
- Leases: none held. No device processes. No background jobs.

## Exact next step on resume

1. `git log -1` in ssx3 (several lanes commit to main).
2. Finish `local/research/E31/REPORT.md` (e31k/l sections, bar verdicts,
   e31l timeline, commands), write `frame-pins.json` + `boot-results.json`
   (all SHAs above + e31k/l pins), verify fork `ssx3` still `3adc0478`
   and worktree state, checkout `ssx3`?? — NO: brief says work on
   `e29-movie-bypass`; leave branch, just don't touch mainline.
3. Evidence commit `[E31]` with `git add -f`, trailer
   `Orchestrated-By: Muse Code`, no push. Final handback to orchestrator.
