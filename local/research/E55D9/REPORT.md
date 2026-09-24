# E55D9 Part 1 — prepared single observed Main Menu navigation boot (NOT run)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D9.md`
plus orchestrator pre-gate fixes (lane setup order; post-1170 frame proof).
Part 1 only: preparation receipts, no boot. **No boot, build, source edit,
device/card action, push, or board/global config edit occurred in this part.**
`~/dev/ssx3-work/E55D9/` is reserved for the later released run and was not
created or touched. All Part 1 writes are under `local/research/E55D9/` only.

Goal: a bounded single Mac boot that observes the settled Main Menu and
navigates one button at a time to identify whether an Options/Save item is
actually displayed (E55D8 found only the title→race I26-FAST route; only
Single Event is evidenced on Main Menu, no save/login screen).

## 1. Evidence table (preparation)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703` (read-only check this part), runner-dir guard `git diff --exit-code 14b1e5cb bab6eb3 -- ps2xRuntime/src/runner` exit 0 |
| ON runner (intended) | `~/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner`, two fresh SHA reads this part, both `e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f` (match E55D3/E55D4 pin) |
| ISO (intended) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, two fresh reads, both `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF (intended) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, two fresh reads, both `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Codegen (intended) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, two fresh reads, both `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Boot script (prepared, NOT executed) | `local/research/E55D9/e55d9_boot.py`, SHA `c72e58937e69ded0f63b2ffc780d98a4f9a94341cdf05d2dd5d34863310c39f4` (rev 2: pre-gate fixes) |
| Checker | `local/research/E55D9/check.py`, SHA `4a7c1f33e154872c89ca69056bf4bf7e68b52807158ef3315be5441110c64f4f` |
| Self-checks | `e55d9_boot.py --self-check` 21/21 (route 8 + caps 4 + lane-setup-order 4 + frame-proof scan 5); `check.py` 33/33 PASS (route/limits/pins/discipline/setup-order/frame-proof-required; menu UNOBSERVED by design, 0 frames pre-run) |
| Pre-gate fixes (orchestrator-found) | (1) `prepare_lane()` refuses reuse BEFORE creating `frames/snap` (the old order created the dir first, so every fresh `--label M1` would refuse itself); covered by 4 lane-setup self-checks + `src_setup_order_check_before_create`. (2) After tick 1170 first lands, the run waits up to 120 s grace for a snap PNG tagged ≥ 1170 to persist (`frame_proof` recorded in result.json); `frame_unproven` (OTHER) if it never does; covered by 5 frame-proof self-checks + `src_target_requires_frame_proof` |
| Intended command (after release only) | `python3 local/research/E55D9/e55d9_boot.py --label M1` (at most one boot) |
| Boots/builds/runs | 0 |
| Base commit | `079d4427` (checked `git log -1` before commit) |
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
| F0 | 760 | 12679 | (frame only) | Settled full Main Menu dump before first nav (~52 ticks after I26 settle 708); Cross at 766 deliberately NOT pressed |
| D1 | 820 | 13680 | down hold 150 | Nav pulse 1 |
| F1 | 870 | 14515 | (frame only) | Settle frame after D1 |
| D2 | 920 | 15349 | down hold 150 | Nav pulse 2 (gap 100 ≥ 45) |
| F2 | 970 | 16183 | (frame only) | Settle frame after D2 |
| D3 | 1020 | 17017 | down hold 150 | Nav pulse 3 (gap 100 ≥ 45) |
| F3 | 1070 | 17851 | (frame only) | Settle frame after D3 |
| D4 | 1120 | 18685 | down hold 150 | Nav pulse 4 (gap 100 ≥ 45) |
| F4 | 1170 | 19520 | (frame only) | Settle frame after D4; stop tick |

Route string: `10611:start:250,13680:down:150,15349:down:150,17017:down:150,18685:down:150`.
At most four Down pulses, each separated by 100 guest ticks (≥ 45 required).
No Cross, no card write, no seeded-card change. Stop early if an
Options/Save/profile item is visibly selected, after the F4 frame, or on any
unexpected screen.

## 3. Stop rules and caps

Stop with `bound=target` only at tick ≥ 1170 AND a persisted snap PNG tagged
≥ 1170 (`frame_proof: {tick, file}` recorded in result.json); the 1 s wall
snapshotter can lag the tick, so up to 120 s grace (`frame_proof_grace_s`)
is allowed for that copy to land. `frame_unproven` if the grace expires
without the proof (OTHER). Other stops: `wall_cap` at 500 s wall;
`progress_cap` at 120 s without tick advance; `log_cap` over 16 MiB closed
log; `frames_cap` over 2 GiB scratch; `hash_error` on det-hash markers;
`exit` if the runner exits first. One mini P-lane slot claimed before launch
and released in `finally`; boot from its own cwd
(`~/dev/ssx3-work/E55D9/run/M1`, reserved, not created); only the recorded
PID is terminated/killed (no pkill/pgrep); reuse refused if
`result.json`/`boot.log`/`frames` exists (checked before any dir creation).

## 4. Predeclared A/B/OTHER (judged only after the Part 2 run)

| Outcome | Criterion |
| --- | --- |
| A | A clearly readable Main Menu entry list AND a button-by-button transition (within the ≤4 Down pulses, no Cross) to a displayed Options/Save item, each step evidenced by a full frame PNG the orchestrator can view |
| B | Readable menu frames and all four bounded Down presses executed with no Options/Save/profile entry observed (not proof none exists) |
| OTHER | Title/Main Menu not reached, any ambiguous/unreadable frame, script/input mismatch, pin/cap/lease failure, unexpected screen, early stop before F4 without a visibly selected Options/Save item, or `frame_unproven` (tick 1170 reached but no snap PNG tagged ≥ 1170 within 120 s grace) |

Frame images are evidence for orchestrator viewing, not worker-only labels:
this part makes no readability claim (`check.py` asserts 0 frames pre-run).

## 5. Commands run (read-only; no boot/lease/build)

- Read: brief, `~/dev/AGENTS.md`, `local/AGENTS.local.md`, E55D8 `REPORT.md`/`ORCH-GATE.md`, I26 `ROUTES.md`/`REPORT.md`/`i26_boot.py`, E55D4 `REPORT.md`/`e55d4_boot.py`, E55D3 `REPORT.md`/`ORCH-GATE.md`, E55D4 entry in `docs/todo.md`, `p_lane_lease.py`, E31 `e31_boot.py`
- `git -C ~/dev/ssx3-work/E55D3/PS2Recomp rev-parse HEAD` → `bab6eb3…`; runner-dir guard exit 0
- Two fresh `sha256sum` reads of runner/ISO/ELF/codegen (all match pins)
- `python3 local/research/E55D9/e55d9_boot.py --self-check` → 11/11
- `python3 local/research/E55D9/check.py` → 31/31 PASS
- `sha256sum` of both scripts (SHAs in §1); `git log -1`; `git status`
- Commit `[E55D9] Part 1` with `Orchestrated-By: opencode`, no push

## 6. Gaps (stated plainly)

- Menu settle timing (~708) and per-press settle lag are I26-measured values reused as plan anchors; the actual settled frames are unobserved until Part 2.
- Whether a Down pulse moves the Main Menu selection vs doing nothing is unobserved; four pulses may stay on Single Event.
- Snapshotter tags frames with the latest det-hash tick at copy time (1 s wall grid), not the exact vsync of the PNG; tick labels are approximate.
- Card manifest records empty roots only; any game card write during menu nav would appear in `card_final_*` post-run.
- No speed claim: any elapsed time from the future run is diagnostic only.

**Part 2 released by orchestrator (ORCH-GATE-P1.md): one M1 boot with script SHA
`c72e58937e69ded0f63b2ffc780d98a4f9a94341cdf05d2dd5d34863310c39f4`. See Part 2 below.**

## Part 2 — one observed Main Menu navigation boot (M1, 2026-09-24)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D9P2.md`.
Exactly one boot: `python3 local/research/E55D9/e55d9_boot.py --label M1`.
Script SHA verified before run: `c72e58937e69ded0f63b2ffc780d98a4f9a94341cdf05d2dd5d34863310c39f4` (match).
Scratch exception verified with a tiny sentinel in `~/dev/ssx3-work/E55D9/`, then removed
(rmdir left the path absent so the fresh run could not refuse itself).
No fork/source edit, build, device, seeded-card change, second boot, or push.

### 1. Run outcome

| Item | Value |
| --- | --- |
| Bound | `target` (tick 1170 reached + snap PNG tagged 1193 persisted; phase2_extra 1.025 s) |
| Wall | 47.729 s (cap 500); last det-hash tick 1200; runner_rc -15 (terminated after target) |
| Lease | mini P-lane slot 1, claimed pre-launch, released in `finally` |
| Precheck | fork `bab6eb3`, runner-dir guard exit 0, two matching SHA reads (runner/ISO/ELF/codegen all match pins), fresh empty cards |
| Cards | initial = final = empty (`f9401596…`); no card write |
| Log/frames | boot.log 567282 B (< 16 MiB); frames dir 12314814 B (< 2 GiB) |
| Route | `10611:start:250,13680:down:150,15349:down:150,17017:down:150,18685:down:150` (1 start + 4 downs, no Cross) |
| Pad markers | boot.log carries no per-press pad markers (no new probe per brief); movement evidenced frame-by-frame |
| Speed | no claim (diagnostic build) |

### 2. Frames handed to the visual gate

Five full-resolution PNGs nearest planned F0/F1/F2/F3/F4 ticks 760/870/970/1070/1170,
copied with adjacent `.txt` metadata into this dir (PNG total 1144319 B ≤ 3 MiB):

| Role | File | Tag d | SHA (see `m1-receipts.txt`) | Worker-viewed visible content |
| --- | --- | --- | --- | --- |
| F0 | `snap-763t-0029.25s.png` | +3 | `2385e516…` | Main Menu; selected **Single Event**; "Play any unlocked Single Event." |
| F1 | `snap-865t-0033.29s.png` | -5 | `71892cc7…` | selected **Conquer The Mountain**; "Earn medals or play BIG Challenges to unlock peaks and build your character." |
| F2 | `snap-981t-0038.33s.png` | +11 | `d610563f…` | selected **Multi Play**; "2 player head to head competition." |
| F3 | `snap-1073t-0042.36s.png` | +3 | `fb4254dd…` | selected **Previews**; "View trailers of other EA games." |
| F4 | `snap-1168t-0046.40s.png` | -2 | `1243bb2a…` | selected **Online**; "Compete against SSX 3 players around the world." |

Every frame shows the same 5-item list (Single Event / Conquer The Mountain / Multi Play /
Previews / Online) with footer `X Select`, triangle `Previous`, square `Options`.
Each Down moved the highlight exactly one row. No Options/Save/profile item appears as a
selectable menu entry; "Options" is only the square-button footer hint. No unexpected screen
(all 47 scratch snaps are Main Menu frames). Snapshot tags are approximate (latest det-hash
tick at 1 s wall copy time). Full receipts: `m1-receipts.txt`; full result: `m1-result.json`;
exact stdout: `m1-stdout.txt`. Bulk frames/log stay in private scratch
(`~/dev/ssx3-work/E55D9/run/M1/`, with `boot.log.gz` + `stdout.txt` retained there).

### 3. Classification and recommendation

| Outcome | Verdict |
| --- | --- |
| A | No — no Options/Save/profile item was displayed as a selectable entry |
| B | **Yes — readable Main Menu frames and all four bounded Down presses executed with no such entry observed (not proof none exists)** |
| OTHER | No — menu reached, frames readable, pins/lease/caps/frame-proof all hold |

Recommended next action: orchestrator visual gate of the five PNGs; worker makes no menu-label
claim beyond the table above and no GetDir/Read reachability claim.

### 4. Orchestrator visual gate (2026-09-24, same day)

The orchestrator viewed all five curated PNGs and confirms the selection path
Single Event → Conquer The Mountain → Multi Play → Previews → Online, one row per
Down pulse. Every frame also visibly shows the bottom-right Square button labeled
Options. That footer prompt is **not** an opened Options screen: no Square was pressed
in this route (down-only plus the title START; no Cross, no Square), so no Options
screen was entered and no GetDir/Read reachability claim follows. Predeclared down-only
result stays **B**. Concrete next detour: one-button Square-at-Main-Menu press to test
whether the footer hint opens an Options screen.
