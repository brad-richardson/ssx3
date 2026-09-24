# E55D14 Part 2A — one empty-card path-observation boot script (prepared, NOT run)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D14P2A.md`.
Part 2A only: preparation receipts, no boot. **No boot, build, card seed/copy,
device/lease action, fork/source edit, push, board/global edit, or upstream
contact occurred in this part.** `~/dev/ssx3-work/E55D14P2/` is reserved for
the later released run and was not created or touched (verified absent).
Fork/runner/codegen/ISO/ELF were read-only (rev-parse/SHA reads + guard
operands only). All Part 2A writes are under `local/research/E55D14P2A/` only.

Goal: a bounded single Mac boot from a fresh `~/dev/ssx3-work/E55D14P2/run/S1`
that replays the proved E55D12 route (E55D11 spine: title START tick636 →
Square at tick820 → Options → four Downs to Save/Load → Cross at tick1360;
E55D12 extension: Down at tick1540 to Load game, Load-highlight frame ~1620,
Cross at tick1700, post frame 1800) on the E55D14P1B `getdirpath` runner, with
frame + card-API observation gated by the predeclared A/B/OTHER below.

## 1. Evidence table (preparation)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D14P1/PS2Recomp`, HEAD `80777cb36d5f84c1cd89122e8074afd48fe78b8e` (read-only check this part), runner-dir guard `git diff --exit-code 14b1e5cb 80777cb -- ps2xRuntime/src/runner` empty, only `.work/` untracked |
| New runner (intended) | `~/dev/ssx3-work/E55D14P1/PS2Recomp/.work/build/ps2xRuntime/ps2EntryRunner`, two fresh SHA reads this part, both `d8fa114d824a277592558425dd91357bcf2f75d0d09390a5680c41ba6002ef04` (match E55D14P1B gate pin) |
| ISO (intended, E55D12 pin) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, SHA `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF (intended, E55D12 pin) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, SHA `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Codegen (intended, E55D12 pin) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, SHA `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Boot script (prepared, NOT executed) | `local/research/E55D14P2A/e55d14_boot.py`, SHA `fa9444a9f80c89dfa2b1e8911d8870ddca87397db083e318f678ea4dc9285694` |
| Checker | `local/research/E55D14P2A/check.py`, SHA `56c761ed8fdb1944b77dd9909f03a43c3d243bdd70526edffe5d11c37f1f16f3` |
| Self-checks | `e55d14_boot.py --self-check` 38/38 (route 19 + caps 6 + precheck 4 + lane-setup-order 5 + frame-proof scan 4); `check.py` 57/57 PASS (route/pins/caps/precheck/discipline/probe/sibling/setup-order/frame-proof-required; screen+API UNOBSERVED by design, 0 frames and 0 probe files pre-run) |
| Pad tokens | `start`, `square`, `down`, `cross` — E55D12-proved, reused unchanged |
| Probe wiring (E55D14P1B tap, default-off) | enable flag `PS2X_PAD_CARD_PROBE=<file>`; GetDir status `getdir … ok=1 bytes=` / `ok=0 reason=` markers; NEW `getdirpath` sibling `getdirpath … pord=<p> … raw/query/parent/pattern/host` markers; McRead `mcread …` markers; tick = GS `vsyncTick` pad-script clock; 16 MiB hard cap |
| Intended command (after release only) | `python3 local/research/E55D14P2A/e55d14_boot.py --label S1` (at most one boot) |
| Boots/builds/runs | 0 |
| Base commit | `ee1f9ee7` (checked `git log -1` before commit; tree clean apart from new lane dir) |
| Disk/text | committed text ~92 KiB (< 512 KiB); `local/research/E55D14P2A` 92 KiB; no scratch written; no speed claim |

## 2. Route (exact input pins; guest ms = tick × 100000/5994)

Identical to E55D12's proved route (E55D12 REPORT §2, ORCH-GATE-P2 A):

`PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_SKIP_MOVIE=1` (dev-only bypass ON),
`PS2X_DETERMINISTIC=1`, `PS2X_DET_HASH_EVERY=1`,
`PS2X_MISSING_FUNCTION_POLICY=stop`, `PS2X_PAD_CARD_PROBE=<lane>/probe.log`,
existing empty card roots (fresh `mc0`/`mc1` under the run cwd, refused
non-empty; no seeded change), `PS2X_FRAME_DUMP_DIR=<lane>/frames` with 1 s
wall snapshotter tagging each `upload-latest.png/.txt` copy with the latest
det-hash tick (`snap-<tick>t-<elapsed>s.{png,txt}`).

| # | Guest tick | ms | Input | Purpose |
| --- | --- | --- | --- | --- |
| S | 636 | 10611 | start hold 250 | I26 title START (E55D11-proved) |
| Q1 | 820 | 13680 | square hold 150 | E55D10-proved Options opener (gap 184 ≥ 60) |
| D1 | 1000 | 16683 | down hold 150 | Options row 1→2 (gap 180) |
| D2 | 1070 | 17851 | down hold 150 | row 2→3 (gap 70) |
| D3 | 1140 | 19019 | down hold 150 | row 3→4 (gap 70) |
| D4 | 1210 | 20187 | down hold 150 | row 4→Save/Load (gap 70) |
| C1 | 1360 | 22689 | cross hold 150 | E55D11 select of Save/Load row (gap 150 from D4) |
| D5 | 1540 | 25692 | down hold 150 | Save game→Load game (gap 180 from C1; ~86 after observed submenu settle ~1454) |
| Fload | 1620 | 27027 | (frame only) | Settled Load-game-highlight capture before C2 (80 after D5) |
| C2 | 1700 | 28362 | cross hold 150 | ONE select of Load game (gap 160 from D5, 80 after Fload) |
| Fpost | 1800 | 30030 | (frame only) | Settled full frame after C2; stop tick (100 after C2) |

Route string:
`10611:start:250,13680:square:150,16683:down:150,17851:down:150,19019:down:150,20187:down:150,22689:cross:150,25692:down:150,28362:cross:150`.
Exactly nine entries in start/square/down×4/cross/down/cross order; all eight
inter-input gaps (184, 180, 70, 70, 70, 150, 180, 160) ≥ 60. No other game input; no
card write, no seeded-card change. Stop early on any unexpected screen.

## 3. Stop rules and caps

Stop with `bound=target` only at tick ≥ 1800 AND a persisted snap PNG tagged
≥ 1800 (`frame_proof: {tick, file}` recorded in result.json); the 1 s wall
snapshotter can lag the tick, so a bounded grace (`frame_proof_grace_s`) is
allowed for that copy to land. `frame_unproven` if the grace expires without
the proof (OTHER). Other stops: `wall_cap` at 500 s wall; `progress_cap` at
120 s without tick advance; `log_cap` over 16 MiB closed log; `frames_cap`
over 2 GiB scratch; `hash_error` on det-hash markers; `exit` if the runner
exits first. One mini P-lane slot claimed before launch and released in
`finally`; boot from its own cwd (`~/dev/ssx3-work/E55D14P2/run/S1`, reserved,
not created); only the recorded PID is terminated/killed (no pkill/pgrep);
reuse refused if `result.json`/`boot.log`/`probe.log`/`frames` exists (checked
before any dir creation).

600 s rule: wall cap 500 s + frame-proof grace **100 s** = 600 s worst-case
active boot, so no boot can exceed 600 s without explicit orchestrator
release. The grace is the ONE cap changed from E55D12 (120 s → 100 s); the
1 s snapshotter grid needs only seconds, so 100 s remains generous. All other
caps, the nine pulses, frame targets, empty-card input, PID/mini-slot cleanup,
16 MiB probe, bounded log/frames and no-reuse guard are preserved unchanged.

## 4. Predeclared A/B/OTHER (judged only after the Part 2B run)

Same pre/post Load game frames as E55D12 (Load-highlight ~1620 pre-C2,
settled full frame ≥1800 post-C2), the exact pad route above, five `getdir`
status rows at the observed menu ticks (four early boot checks + one
post-choice, E55D12-observed at vsync 118/122/126/223 and 1740) and five
`getdirpath` sibling rows paired by per-family ordinal/tick/port/slot/max
(`pord` 1..5 with matching vsync/port/slot/max per row). The new sibling
shifts shared `seq`, so old global seq numbers are NOT compared — pairing is
by per-family ordinal, tick, port, slot and max only.

| Outcome | Criterion |
| --- | --- |
| A | Post-choice `getdirpath` row reveals the escaped raw query, normalized query, parent, pattern and host while the card stays empty and no copied bytes appear |
| B | Path observed but scene/status differs (void for seed design) |
| OTHER | No path, cap, input or preflight failure |

Do not infer a valid save or determinism. `getdirpath` is dev-only/default-off.
A future seed is a separate release.

## 5. Changes vs E55D12's proved script (review aid)

1. Output lane `~/dev/ssx3-work/E55D12` → `~/dev/ssx3-work/E55D14P2`
   (lease tag `E55D12-` → `E55D14P2-`).
2. Fork/runner pins: fork `~/dev/ssx3-work/E55D14P1/PS2Recomp` @
   `80777cb36d5f84c1cd89122e8074afd48fe78b8e` (was E55D3 worktree @
   `bab6eb3`); runner `.work/build/ps2xRuntime/ps2EntryRunner` SHA
   `d8fa114d…ef04` (was `build-taps/…` SHA `e282c8a7…`). ISO/ELF/codegen
   paths and SHAs unchanged (E55D12 pins).
3. Precheck: still rejects any tracked modification and any unexpected
   untracked path, but allows untracked `.work/` (the E55D14P1B build tree;
   pure helper `status_errors()` unit-tested in `--self-check`). Runner-dir
   guard vs `14b1e5cb` kept.
4. Frame-proof grace 120 s → 100 s (600 s rule; §3). All other caps kept.
5. Receipt/checker sibling awareness: script docstring + `check.py` assert
   the `getdirpath` pairing rule (per-family `pord`/tick/port/slot/max, no
   global-seq comparison) without observing any probe row pre-run.

## 6. Commands run (read-only; no boot/lease/build)

- Read: brief, repo `AGENTS.md`, `local/AGENTS.local.md`, E55D14P1 full
  `REPORT.md` + `ORCH-GATE.md`, E55D14P1B full `REPORT.md` + `ORCH-GATE.md` +
  `check.py`, E55D12 full `REPORT.md` (P1 prep + P2 run) + `ORCH-GATE-P1.md` +
  `ORCH-GATE-P2.md` + `e55d12_boot.py` + `check.py` + `check-p2.py`
- `git log -1` → `ee1f9ee7`; `git status --short` (clean); verified
  `~/dev/ssx3-work/E55D14P2/` absent (reserved, untouched) and
  `local/research/E55D14P2A/` absent before `mkdir -p`
- Read-only fork verify: `git -C ~/dev/ssx3-work/E55D14P1/PS2Recomp rev-parse
  HEAD` → `80777cb36d5f84c1cd89122e8074afd48fe78b8e`; `status --porcelain`
  → only `?? .work/`; runner-dir guard
  `git diff --exit-code 14b1e5cb 80777cb -- ps2xRuntime/src/runner` exit 0 (empty)
- Two fresh `shasum -a 256` reads of the new runner (both `d8fa114d…ef04`);
  ISO/ELF/codegen SHAs carried from the E55D12 gate pins (not re-read; the
  script's runtime precheck performs the two matching reads before any boot)
- `python3 local/research/E55D14P2A/e55d14_boot.py --self-check` → 38/38, 0 MISMATCH
- `python3 local/research/E55D14P2A/check.py` → 57/57 ok, 0 FAIL
- `shasum -a 256` of both scripts (SHAs in §1); `du -sk` (92 KiB)
- Commit `[E55D14] Part 2A` with `Orchestrated-By: opencode`, no push

## 7. Gaps (stated plainly)

- Submenu settle (~1454), post-press settle lags, and the tick1740 guest
  query are E55D12-measured values reused as plan anchors; the actual settled
  frames and the raw/pattern path fields are unobserved until Part 2B.
- Whether D5 lands exactly on Load game and whether C2 opens a Load game
  result screen are unobserved; one pulse each is the whole test.
- Whether the post-choice `getdirpath` sibling carries the raw query,
  normalized query, parent, pattern and host is unobserved; only the post-C2
  probe window decides after Part 2B.
- Snapshotter tags frames with the latest det-hash tick at copy time (1 s
  wall grid), not the exact vsync of the PNG; tick labels are approximate.
- Stop-tick wall cost is unmeasured (E55D12 reached tick 1824 in ~68 s wall
  on a diagnostic taps build; 1800 ticks is the same order, well under the
  500 s cap) — no speed claim.
- No `p_lane_lease` import resolution at edit time (same `sys.path` pattern
  as E55D12; resolves at runtime on the mini).
- ISO/ELF/codegen SHAs are carried E55D12 gate pins, not fresh reads this
  part; only the new fork HEAD, `.work/`-only status, runner-dir guard and
  the new runner double-SHA were re-verified read-only. The script's runtime
  precheck performs two matching reads of all four paths before any boot.

**Do not boot until the orchestrator reviews the exact script SHA and
explicitly releases Part 2B in the worker pane.**
