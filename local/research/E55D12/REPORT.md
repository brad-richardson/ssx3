# E55D12 — Part 1 preparation only (bounded Load game selection)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D12.md`.
Part 1 only: preparation receipts, no boot. **No boot, build, fork/source edit,
device/card action, lease claim, seeded-card change, push, board/global config
edit, or other lane's files occurred in this part.**
`~/dev/ssx3-work/E55D12/` is reserved for the later released run and was not
created or touched (verified absent). E55D3 fork/runner and E55D11 private
scratch were read only (SHA reads + guard). All Part 1 writes are under
`local/research/E55D12/` only.

Goal: a bounded single Mac boot from a fresh `~/dev/ssx3-work/E55D12/run/S1`
that replays the proved E55D11 spine (title START tick636 → Square at tick820
→ Options → four Downs to Save/Load → Cross at tick1360 opening the six-item
Save/Load submenu, E55D11 outcome B: submenu viewed by tick1454 with Save game
highlighted and Load game one row below), then one separate Down to reach
Load game, one Cross to select it, with frame + card-API observation gated by
predeclared A/B/OTHER.

## 1. Evidence table (preparation)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703` (read-only check this part), runner-dir guard `git diff --exit-code 14b1e5cb bab6eb3 -- ps2xRuntime/src/runner` exit 0, worktree clean |
| ON runner (intended) | `~/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner`, two fresh SHA reads this part, both `e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f` (match E55D3/E55D9/E55D10/E55D11 pin) |
| ISO (intended) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, two fresh reads, both `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF (intended) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, two fresh reads, both `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Codegen (intended) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, two fresh reads, both `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Boot script (prepared, NOT executed) | `local/research/E55D12/e55d12_boot.py`, SHA `9efe732d358a20605fcf9fd88725095dcefd1e15e9e69f5b4a95bc359d6ee8cd` |
| Checker | `local/research/E55D12/check.py`, SHA `fe6c3c4910c721ae4f24557063054a45c76163650254dba1cd9dd55155094056` |
| Self-checks | `e55d12_boot.py --self-check` 33/33 (route 19 + caps 5 + lane-setup-order 5 + frame-proof scan 4); `check.py` 46/46 PASS (route/pins/caps/discipline/probe/setup-order/frame-proof-required; screen+API UNOBSERVED by design, 0 frames and 0 probe files pre-run) |
| Pad tokens | `start`, `square`, `down`, `cross` all verified valid in fork source (E55D11 read-only finding, `Pad.cpp:351` `padScriptButtonMask`, reused unchanged) |
| Probe wiring (E55D11 read-only finding, reused) | enable flag `PS2X_PAD_CARD_PROBE=<file>`; GetDir `getdir … ok=1 bytes=` / `ok=0 reason=` markers; McRead `mcread … ok=1 …` / `ok=0 reason=…` markers; tick = GS `vsyncTick` pad-script clock; 16 MiB hard cap |
| Intended command (after release only) | `python3 local/research/E55D12/e55d12_boot.py --label S1` (at most one boot) |
| Boots/builds/runs | 0 |
| Base commit | `71dd089d` (checked `git log -1` before commit; tree clean apart from new lane dir) |
| Disk/text | committed text ~70 KiB (< 512 KiB); `local/research/E55D12` 72 KiB; no scratch written; no speed claim |

## 2. Route (exact input pins; guest ms = tick × 100000/5994)

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
| D1 | 1000 | 16683 | down hold 150 | Options row 1→2 (gap 180; ~80 after Options settle ~919) |
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

Timing support: E55D11's transition ran C1 at tick1360, still on Options at
tick1368 (in flight), submenu settled by tick1454 (viewed). D5 at 1540 sits
86 ticks after that observed settle and 180 after C1, so the choice is bounded
even if the settle lags E55D11 by tens of ticks. Wall cost scales from E55D11
(1490 ticks in ~55 s wall): 1800 ticks is the same order, well under the
500 s cap — no speed claim.

## 3. Stop rules and caps

Stop with `bound=target` only at tick ≥ 1800 AND a persisted snap PNG tagged
≥ 1800 (`frame_proof: {tick, file}` recorded in result.json); the 1 s wall
snapshotter can lag the tick, so up to 120 s grace (`frame_proof_grace_s`)
is allowed for that copy to land. `frame_unproven` if the grace expires
without the proof (OTHER). Other stops: `wall_cap` at 500 s wall;
`progress_cap` at 120 s without tick advance; `log_cap` over 16 MiB closed
log; `frames_cap` over 2 GiB scratch; `hash_error` on det-hash markers;
`exit` if the runner exits first. One mini P-lane slot claimed before launch
and released in `finally`; boot from its own cwd
(`~/dev/ssx3-work/E55D12/run/S1`, reserved, not created); only the recorded
PID is terminated/killed (no pkill/pgrep); reuse refused if
`result.json`/`boot.log`/`probe.log`/`frames` exists (checked before any dir
creation).

## 4. Predeclared A/B/OTHER (judged only after the Part 2 run)

| Outcome | Criterion |
| --- | --- |
| A | A readable Load game result screen (post-C2 full frame, orchestrator-viewed) **plus** any **post-choice** (vsync ≥ 1700) GetDir or mcRead call — even `ok=0 reason=empty` counts as API reach; success and copied-byte payloads (`ok=1 bytes=`, bytes-bearing mcRead) are stated separately as the stronger observation. Early title/menu GetDir calls (E55D11 saw 4 at vsync 118/122/126/223) are counted separately and do not satisfy A |
| B | A readable Load game result screen without that post-choice API evidence, or a different readable screen (state it precisely: which menu/row, which footer) |
| OTHER | Missing/unreadable pre/post frame, route/pin/lease/cap mismatch, or ambiguous transition |

A visual screen alone never proves card API reach; empty card files alone do
not prove no card API call. A copied GetDir table (`ok=1 bytes=`) or bytes-bearing
mcRead is a separate, stronger observation than `ok=0 reason=empty`. Frame images
and probe lines are evidence for orchestrator viewing, not worker-only labels:
this part makes no readability or API claim (`check.py` asserts 0 frames and
0 probe files pre-run). No changed-card baseline is claimed from a screen alone.

## 5. Commands run (read-only; no boot/lease/build)

- Read: brief, repo `AGENTS.md`, `local/AGENTS.local.md`, E55D11 full `REPORT.md`/`ORCH-GATE-P1.md`/`ORCH-GATE-P2.md`/`e55d11_boot.py`/`check.py`/`check-p2.py`, E55D12 row in `docs/todo.md` + board row in `docs/status.md`
- `git -C ~/dev/ssx3-work/E55D3/PS2Recomp rev-parse HEAD` → `bab6eb3…`; worktree clean; runner-dir guard exit 0
- Two fresh `sha256sum` reads of runner/ISO/ELF/codegen (all match pins)
- Verified `~/dev/ssx3-work/E55D12/` absent (reserved, untouched)
- `python3 local/research/E55D12/e55d12_boot.py --self-check` → 33/33
- `python3 local/research/E55D12/check.py` → 46/46 PASS
- `sha256sum` of both scripts (SHAs in §1); `git log -1`; `git status`
- Commit `[E55D12] Part 1` with `Orchestrated-By: opencode`, no push

## 6. Gaps (stated plainly)

- Submenu settle (~1454) and post-press settle lags are E55D11-measured values reused as plan anchors; the actual settled frames are unobserved until Part 2.
- Whether D5 lands exactly on Load game (no wrap, no missed pulse, no submenu intercept) is unobserved; the Load-highlight frame at ~1620 is the check.
- Whether C2 opens a Load game result screen vs doing nothing (or opening something else) is unobserved; one pulse is the whole test.
- Whether Load game selection issues any `sceMcGetDir`/`sceMcRead` call is unobserved; only the post-C2 probe window decides after Part 2. If the game reads cards earlier (title/menu), those lines will also be present and must be separated by vsync tick (pre-C2 vs ≥1700).
- Snapshotter tags frames with the latest det-hash tick at copy time (1 s wall grid), not the exact vsync of the PNG; tick labels are approximate.
- Stop-tick wall cost is unmeasured (E55D11 reached tick 1490 in ~55 s wall; 1800 ticks is the same order, well under the 500 s cap) — no speed claim.
- No `p_lane_lease` import resolution at edit time (same `sys.path` pattern as E55D11; resolves at runtime on the mini).

**Do not boot until the orchestrator reviews the exact script SHA and
explicitly releases Part 2 in the worker pane.**

---

# E55D12 — Part 2 run (one released Mac boot, 2026-09-24)

Worker: opencode (Muse Spark Contributor Go). Brief:
`local/muse/prompts/E55D12P2.md`. Exactly one boot with the approved
script SHA `9efe732d358a20605fcf9fd88725095dcefd1e15e9e69f5b4a95bc359d6ee8cd`
(verified before launch; script unedited). Per-worker write exception
(confined to `~/dev/ssx3-work/E55D12/**`) verified with a tiny sentinel
file and removed before the run (lane dir absent again afterwards). `ps`
showed no clang/ninja and both mini lease slots free, so the single
`python3 local/research/E55D12/e55d12_boot.py --label S1` run proceeded.
No fork/source edit, build, Odin/iOS action, seeded-card change, push,
board/global config edit, or upstream contact. No speed claim (diagnostic
taps build).

## 1. Evidence table (run)

| Item | Value |
| --- | --- |
| Result | `bound=target`, `elapsed_s=68.084`, `last_hash_tick=1824`, `phase2_extra_s=0.516`, `runner_pid=53708` (gone; SIGTERM rc=-15 expected), mini slot 1 claimed + released (both slots free) |
| Frame proof | tick 1808 `snap-1808t-0067.52s.png` ≥ stop 1800 |
| Caps | `log_bytes=867385` ≤ 16 MiB; `frames_bytes=13644633` ≤ 2 GiB; wall 500 / progress 120 / grace 120 (run-control metrics, not speed) |
| Cards | `mc0`/`mc1` empty at start AND end; manifest SHA `f9401596…ccb9ce` unchanged |
| Padscript (boot.log, 19 rows) | `armed n=9 clock=vsync`; presses Start `0x0008` ×1, Square `0x8000` ×1, Down `0x0040` ×5 (separate i=2..5 plus i=7), Cross `0x4000` ×2 (i=6 C1, i=8 C2), in plan order; 9 releases; no other input. D4 fired `now=20203ms at=20187ms` (16 ms late, same as E55D11); C2 fired `now=28378ms at=28362ms` (16 ms late; gaps still ≥ 60) |
| Probe (3536 lines) | `getdir` n=5: 4 pre-C2 at vsync 118/122/126/223 (addr `0x00b85660`, all `ok=0 reason=empty len=0 bytes=(empty)`, port=0 slot=0) + 1 post-C2 at vsync 1740 (addr `0x00ba5b20`, `ok=0 reason=empty len=0 bytes=(empty)`); `mcread` n=0; `pad` n=3531 (3284 pre-C2, 247 at/after 1700, all ok=1 len=32) |
| Private lane | `~/dev/ssx3-work/E55D12/run/S1/` (boot.log + .gz, probe.log + .gz, result.json, frames/, empty mc0/mc1). Raw log/probe kept; `.gz` copies made only after the runner exited |
| Curated (committed) | `snap-1616t-0060.49s.png` + `.txt`, `snap-1808t-0067.52s.png` + `.txt`, `s1-result.json`, `s1-receipts.txt`, `check-p2.py`. PNG total 319215 B ≤ 2 MiB; text 246 B + receipts ≤ 512 KiB |
| Checker | `check-p2.py` 44/44 PASS (pins, route, caps, cards, pad rows/order, probe counts/ticks, frame/probe SHAs; visual/API labels NOT asserted) |

## 2. Frames (worker-viewed; visual verdict rests with the orchestrator gate)

| File (meta tick) | Reading |
| --- | --- |
| `snap-1616t-0060.49s.png` (tick 1616; \|1616−1620\|=4, nearest pre-C2 full frame) | Title **Save/Load**; rows Save game, **Load game (highlighted orange bar)**, Save options, Load options, Load replay, New game; footer "Load previous game." + X Select / Triangle Previous |
| `snap-1808t-0067.52s.png` (tick 1807; \|1808−1800\|=8, nearest post-C2 full frame; frame proof) | Title **Load game**; header "MEMORY CARD slot1"; rows 1–6 all **\<EMPTY\>** with row 1 highlighted (orange bar); footer "Load game to continue a previously saved game." + Triangle Previous |
| Adjacent (viewed, not curated) | 1590 + 1642: same Save/Load submenu with Load game highlighted as 1616. 1780: same Load game MEMORY CARD slot1 with 6 EMPTY rows as 1808. No unexpected screen |

Snapshot filename ticks are approximate (1 s wall grid tagged with the
latest det-hash tick); actual metadata ticks and SHAs are recorded in
`s1-receipts.txt`.

## 3. Outcome vs predeclared gate

Pre-C2 full frame exists and shows the Load game row highlighted;
post-C2 full frame shows a readable Load game MEMORY CARD screen with six
\<EMPTY\> slots. Card side: one `getdir` call at vsync 1740 (40 ticks
after C2 tick 1700, distinct addr `0x00ba5b20`), `ok=0 reason=empty` with
zero copied table bytes, plus the four early `ok=0 reason=empty` GetDir
probes (title boot, empty cards, same ticks/addrs as E55D11) counted
separately; zero `mcread` anywhere. That is predeclared **A** (readable
Load game result screen plus a post-choice GetDir call; `ok=0` counts as
API reach, with success/copied-byte payloads stated separately as the
stronger — absent — observation). The orchestrator makes the visual
verdict.

## 4. Commands run (one boot only)

- Pre-run: script SHA check (`9efe732d…6ee8cd` match), sentinel
  write/remove under `~/dev/ssx3-work/E55D12/`, `ps` heavy-job check (no
  clang/ninja), lease status (both slots free), E55D11 `ORCH-GATE-P2.md`
  + full `REPORT.md` read
- `python3 local/research/E55D12/e55d12_boot.py --label S1` → `bound=target` (sole boot/build/run this part)
- Post-run: PID-gone + lease-free checks, frame viewing (1616, 1808, 1590, 1642, 1780), padscript/probe parsing, `gzip -k` of closed boot.log/probe.log, `cp` of 2 PNG + 2 txt + result.json into `local/research/E55D12/`, wrote `s1-receipts.txt` + `check-p2.py`, `python3 local/research/E55D12/check-p2.py` → 44/44 PASS
- `git log -1`, `git status`, stage explicit paths only, commit `[E55D12] Part 2` with `Orchestrated-By: opencode`, no push

## 5. Gaps (stated plainly)

- Tick tags remain snapshotter-approximate; the curated pre frame is −4
  ticks from target 1620 and the post frame is +8 (meta tick 1807 vs
  filename 1808), with metadata ticks recorded.
- Why the post-choice GetDir returned `ok=0 reason=empty` on empty cards
  (no dir vs unformatted vs port quirk) is unobserved; only the call's
  presence, tick, addr and empty result are evidenced. No copied table
  bytes and no mcRead were observed.
- The five Down pulses' row-by-row travel is inferred from endpoints
  (E55D11 submenu → Load game highlighted), not from per-press frames.
- Part-1 `check.py` is not re-run post-curation (it asserts the
  no-frames pre-run state by design); `check-p2.py` is the post-run
  checker.
- No `s1-stdout.txt` is committed: stdout was observed live
  (`bound=target` line matches `s1-result.json`); only byte-verifiable
  copies are committed.

Recommended next action: orchestrator visual gate on the two curated
frames (confirm Load game highlight + MEMORY CARD readings), then decide
whether the single post-choice empty GetDir warrants a follow-up lane
(e.g. seeded-card Load attempt, or pressing into a submenu slot) with the
same probe taps to test for table-carrying reads.
