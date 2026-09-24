# E55D10 — Part 1 preparation only (one Square-at-Main-Menu detour)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D10.md`.
Part 1 only: preparation receipts, no boot. **No boot, build, source edit,
device/card action, push, or board/global config edit occurred in this part.**
`~/dev/ssx3-work/E55D10/` is reserved for the later released run and was not
created or touched (verified absent). E55D3 fork/runner and E55D9
inputs/scratch were read only (SHA reads + guard). All Part 1 writes are
under `local/research/E55D10/` only.

Goal: a bounded single Mac boot that tests the visible Main Menu footer
prompt (E55D9 showed readable five-item menu + bottom-right **Square:
Options** in all five orchestrator-viewed frames; Square never pressed, no
Options screen or card API call proved).

## 1. Evidence table (preparation)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703` (read-only check this part), runner-dir guard `git diff --exit-code 14b1e5cb bab6eb3 -- ps2xRuntime/src/runner` exit 0 |
| ON runner (intended) | `~/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner`, two fresh SHA reads this part, both `e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f` (match E55D3/E55D9 pin) |
| ISO (intended) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, two fresh reads, both `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF (intended) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, two fresh reads, both `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Codegen (intended) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, two fresh reads, both `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Boot script (prepared, NOT executed) | `local/research/E55D10/e55d10_boot.py`, SHA `03536b0c5b84a95d676ca2e972446827b7be11cfc3153a1a67f8eac9c4447e3f` |
| Checker | `local/research/E55D10/check.py`, SHA `0ac8477cd186e8f8ccd5765d9f381c49fe9c81457cfb685682c3c1247035cae1` |
| Self-checks | `e55d10_boot.py --self-check` 25/25 (route 13 + caps 4 + lane-setup-order 4 + frame-proof scan 4); `check.py` 35/35 PASS (route/pins/caps/discipline/setup-order/frame-proof-required; screen UNOBSERVED by design, 0 frames pre-run) |
| Pad token | `square` verified valid in fork source (`Pad.cpp:383` `padScriptButtonMask`, read-only) |
| Intended command (after release only) | `python3 local/research/E55D10/e55d10_boot.py --label S1` (at most one boot) |
| Boots/builds/runs | 0 |
| Base commit | `6ed56aed3368d9752c24a8bb1b56badb318e6be` (checked `git log -1` before commit) |
| Disk/text | committed text ~30 KiB (< 512 KiB); no scratch written (< 2 GiB); no speed claim |

## 2. Route (exact input pins; guest ms = tick × 100000/5994)

`PS2X_PAD_SCRIPT_CLOCK=vsync`, `PS2X_SKIP_MOVIE=1` (dev-only bypass ON),
`PS2X_DETERMINISTIC=1`, `PS2X_DET_HASH_EVERY=1`,
`PS2X_MISSING_FUNCTION_POLICY=stop`, existing empty card roots
(fresh `mc0`/`mc1` under the run cwd, refused non-empty; no seeded change),
`PS2X_FRAME_DUMP_DIR=<lane>/frames` with 1 s wall snapshotter tagging each
`upload-latest.png/.txt` copy with the latest det-hash tick
(`snap-<tick>t-<elapsed>s.{png,txt}`).

| # | Guest tick | ms | Input | Purpose |
| --- | --- | --- | --- | --- |
| S | 636 | 10611 | start hold 250 | I26 title START (66 ticks after prompt shows ~570) |
| F0 | 760 | 12679 | (frame only) | Settled full Main Menu dump before input (~52 ticks after I26 settle 708) |
| Q1 | 820 | 13680 | square hold 150 | ONE Square press testing the footer prompt (gap 60 ≥ 45) |
| F1 | 920 | 15349 | (frame only) | Settled full frame after Square; stop tick |

Route string: `10611:start:250,13680:square:150`.
Exactly one Square pulse. No Down, no Cross, no other game input; no card
write, no seeded-card change. Stop early on any unexpected screen.

## 3. Stop rules and caps

Stop with `bound=target` only at tick ≥ 920 AND a persisted snap PNG tagged
≥ 920 (`frame_proof: {tick, file}` recorded in result.json); the 1 s wall
snapshotter can lag the tick, so up to 120 s grace (`frame_proof_grace_s`)
is allowed for that copy to land. `frame_unproven` if the grace expires
without the proof (OTHER). Other stops: `wall_cap` at 500 s wall;
`progress_cap` at 120 s without tick advance; `log_cap` over 16 MiB closed
log; `frames_cap` over 2 GiB scratch; `hash_error` on det-hash markers;
`exit` if the runner exits first. One mini P-lane slot claimed before launch
and released in `finally`; boot from its own cwd
(`~/dev/ssx3-work/E55D10/run/S1`, reserved, not created); only the recorded
PID is terminated/killed (no pkill/pgrep); reuse refused if
`result.json`/`boot.log`/`frames` exists (checked before any dir creation).

## 4. Predeclared A/B/OTHER (judged only after the Part 2 run)

| Outcome | Criterion |
| --- | --- |
| A | The post-Square full frame visibly opens an Options screen with a back path |
| B | Readable menu persists or a different readable screen opens, with its exact text recorded |
| OTHER | Missing/unreadable frame, pin/route/lease/cap issue, or ambiguous transition |

A screen alone does not prove Save or GetDir/Read reachability. Frame images
are evidence for orchestrator viewing, not worker-only labels: this part
makes no readability claim (`check.py` asserts 0 frames pre-run).

## 5. Commands run (read-only; no boot/lease/build)

- Read: brief, `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, E55D9 corrected `REPORT.md`/`ORCH-GATE-P1.md`/`ORCH-GATE-P2.md`/`e55d9_boot.py`/`check.py`, `Pad.cpp` button table, E55D10 entry in `docs/todo.md`
- `git -C ~/dev/ssx3-work/E55D3/PS2Recomp rev-parse HEAD` → `bab6eb3…`; runner-dir guard exit 0
- Two fresh `sha256sum` reads of runner/ISO/ELF/codegen (all match pins)
- Verified `~/dev/ssx3-work/E55D10/` absent (reserved, untouched)
- `python3 local/research/E55D10/e55d10_boot.py --self-check` → 25/25
- `python3 local/research/E55D10/check.py` → 35/35 PASS
- `sha256sum` of both scripts (SHAs in §1); `git log -1`; `git status`
- Commit `[E55D10] Part 1` with `Orchestrated-By: opencode`, no push

## 6. Gaps (stated plainly)

- Menu settle timing (~708) and post-press settle lag are I26/E55D9-measured values reused as plan anchors; the actual settled frames are unobserved until Part 2.
- Whether the Square press opens Options vs doing nothing is unobserved; one pulse is the whole test.
- Snapshotter tags frames with the latest det-hash tick at copy time (1 s wall grid), not the exact vsync of the PNG; tick labels are approximate.
- Card manifest records empty roots only; any game card write during the detour would appear in `card_final_*` post-run.
- No speed claim: any elapsed time from the future run is diagnostic only.

**Do not boot until the orchestrator reviews the exact script SHA and
explicitly releases Part 2 in the worker pane.**
