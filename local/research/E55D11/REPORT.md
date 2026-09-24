# E55D11 — Part 1 preparation only (bounded Save/Load selection)

Worker: opencode (Muse Spark Contributor Go). Brief: `local/muse/prompts/E55D11.md`.
Part 1 only: preparation receipts, no boot. **No boot, build, fork/source edit,
device/card action, lease claim, seeded-card change, push, board/global config
edit, or other lane's files occurred in this part.**
`~/dev/ssx3-work/E55D11/` is reserved for the later released run and was not
created or touched (verified absent). E55D3 fork/runner and E55D10 private
scratch were read only (SHA reads + guard). All Part 1 writes are under
`local/research/E55D11/` only.

Goal: a bounded single Mac boot from a fresh `~/dev/ssx3-work/E55D11/run/S1`
that follows the proved title START tick636 → Square at tick820 → Options
screen (E55D10 outcome A: post-Square frames 919/944 show Options with Game
Options highlighted and Save/Load four rows below), then four separate Down
pulses to reach Save/Load, one Cross to select it, with frame + card-API
observation gated by predeclared A/B/OTHER.

## 1. Evidence table (preparation)

| Item | Value |
| --- | --- |
| Private fork | `~/dev/ssx3-work/E55D3/PS2Recomp`, HEAD `bab6eb382673155ffd756fe8db265964eeff9703` (read-only check this part), runner-dir guard `git diff --exit-code 14b1e5cb bab6eb3 -- ps2xRuntime/src/runner` exit 0, worktree clean |
| ON runner (intended) | `~/dev/ssx3-work/E55D3/build-taps/ps2xRuntime/ps2EntryRunner`, two fresh SHA reads this part, both `e282c8a79cb4ce3e616244d1cfb0b5ab6d522e2f262408c6ffa92860f211643f` (match E55D3/E55D9/E55D10 pin) |
| ISO (intended) | `~/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso`, two fresh reads, both `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| ELF (intended) | `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72`, two fresh reads, both `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Codegen (intended) | `~/dev/ssx3-work/codegen-ssx3/register_functions.cpp`, two fresh reads, both `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Boot script (prepared, NOT executed) | `local/research/E55D11/e55d11_boot.py`, SHA `f5434273f8384932502f47fc98f80ce5f5c313e3077c41ee8167c520535c476b` |
| Checker | `local/research/E55D11/check.py`, SHA `6cd564fd08077654c727b61abad69ca1ffa21704ca408b740b0127f376c0cc36` |
| Self-checks | `e55d11_boot.py --self-check` 31/31 (route 17 + caps 5 + lane-setup-order 5 + frame-proof scan 4); `check.py` 42/42 PASS (route/pins/caps/discipline/probe/setup-order/frame-proof-required; screen+API UNOBSERVED by design, 0 frames and 0 probe files pre-run) |
| Pad tokens | `start`, `square`, `down`, `cross` all verified valid in fork source (`Pad.cpp:351` `padScriptButtonMask`, read-only) |
| Probe wiring (read-only source inspection) | enable flag `PS2X_PAD_CARD_PROBE=<file>` (`ps2_e55d3_pad_card_probe.h:108-120`; unset/empty = one relaxed atomic per call, no I/O); GetDir markers `getdir seq=… vsync=… ord=… entries=… max=… len=… ok=1 bytes=<hex>` / `ok=0 reason=<bad-port\|unformatted\|no-dir\|empty\|bad-addr>` (header lines 26-29, call sites `MemoryCard.cpp:729,846,864,871,879,887`); McRead markers `mcread seq=… vsync=… ord=… fd=… req=… len=… ok=1 err=… bytes=<hex>` / `ok=0 reason=…` (header lines 30-35, call sites `MemoryCard.cpp:1118,1124,1130,1152,1155`); tick = GS `vsyncTick`, the vsync pad-script clock (`MemoryCard.cpp:716-717,1108-1109`); 16 MiB hard cap with single `cap` line (header lines 38-42) |
| Intended command (after release only) | `python3 local/research/E55D11/e55d11_boot.py --label S1` (at most one boot) |
| Boots/builds/runs | 0 |
| Base commit | `77a4d22e` (checked `git log -1` before commit; tree clean) |
| Disk/text | committed text ~30 KiB (< 512 KiB); `local/research/E55D11` 68 KiB; no scratch written; no speed claim |

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
| S | 636 | 10611 | start hold 250 | I26 title START (E55D10-proved) |
| Q1 | 820 | 13680 | square hold 150 | E55D10-proved Options opener (gap 184 ≥ 60) |
| D1 | 1000 | 16683 | down hold 150 | Options row 1→2 (gap 180; ~80 after Options settle ~919) |
| D2 | 1070 | 17851 | down hold 150 | row 2→3 (gap 70) |
| D3 | 1140 | 19019 | down hold 150 | row 3→4 (gap 70) |
| D4 | 1210 | 20187 | down hold 150 | row 4→Save/Load (gap 70) |
| Fpre | 1290 | 21522 | (frame only) | Settled Save/Load-highlight capture before Cross (80 after D4) |
| C1 | 1360 | 22689 | cross hold 150 | ONE select of the highlighted row (gap 150 from D4) |
| Fpost | 1460 | 24358 | (frame only) | Settled full frame after Cross; stop tick (100 after Cross) |

Route string:
`10611:start:250,13680:square:150,16683:down:150,17851:down:150,19019:down:150,20187:down:150,22689:cross:150`.
Exactly seven entries in start/square/down×4/cross order; all six
inter-input gaps (184, 180, 70, 70, 70, 150) ≥ 60. No other game input; no
card write, no seeded-card change. Stop early on any unexpected screen.

## 3. Stop rules and caps

Stop with `bound=target` only at tick ≥ 1460 AND a persisted snap PNG tagged
≥ 1460 (`frame_proof: {tick, file}` recorded in result.json); the 1 s wall
snapshotter can lag the tick, so up to 120 s grace (`frame_proof_grace_s`)
is allowed for that copy to land. `frame_unproven` if the grace expires
without the proof (OTHER). Other stops: `wall_cap` at 500 s wall;
`progress_cap` at 120 s without tick advance; `log_cap` over 16 MiB closed
log; `frames_cap` over 2 GiB scratch; `hash_error` on det-hash markers;
`exit` if the runner exits first. One mini P-lane slot claimed before launch
and released in `finally`; boot from its own cwd
(`~/dev/ssx3-work/E55D11/run/S1`, reserved, not created); only the recorded
PID is terminated/killed (no pkill/pgrep); reuse refused if
`result.json`/`boot.log`/`probe.log`/`frames` exists (checked before any dir
creation).

## 4. Predeclared A/B/OTHER (judged only after the Part 2 run)

| Outcome | Criterion |
| --- | --- |
| A | A readable Save/Load result screen (post-Cross full frame, orchestrator-viewed) **plus** a copied GetDir table (`getdir … ok=1 bytes=`) or a successful mcRead record (`mcread … ok=1 …`) from `<lane>/probe.log` |
| B | A readable Save/Load result screen without that API evidence, or a different readable screen (state it precisely: which menu/row, which footer) |
| OTHER | Missing/unreadable frame, route/pin/lease/cap mismatch, or ambiguous transition |

A visual screen alone never proves card API reach; empty card files alone do
not prove no card API call. Frame images and probe lines are evidence for
orchestrator viewing, not worker-only labels: this part makes no readability
or API claim (`check.py` asserts 0 frames and 0 probe files pre-run).

## 5. Commands run (read-only; no boot/lease/build)

- Read: brief, `~/dev/AGENTS.md`, repo `AGENTS.md`, `local/AGENTS.local.md`, E55D10 full `REPORT.md`/`ORCH-GATE-P1.md`/`ORCH-GATE-P2.md`/`e55d10_boot.py`/`check.py`/`check-p2.py`, E55D3 `REPORT.md`, `Pad.cpp` button table + probe call sites, `MemoryCard.cpp` GetDir/Read tap sites + tick source, `ps2_e55d3_pad_card_probe.h` (markers, enable flag, cap), E55D11 row in `docs/todo.md` + board row in `docs/status.md`
- `git -C ~/dev/ssx3-work/E55D3/PS2Recomp rev-parse HEAD` → `bab6eb3…`; worktree clean; runner-dir guard exit 0
- Two fresh `sha256sum` reads of runner/ISO/ELF/codegen (all match pins)
- Verified `~/dev/ssx3-work/E55D11/` absent (reserved, untouched)
- `python3 local/research/E55D11/e55d11_boot.py --self-check` → 31/31
- `python3 local/research/E55D11/check.py` → 42/42 PASS
- `sha256sum` of both scripts (SHAs in §1); `git log -1`; `git status`
- Commit `[E55D11] Part 1` with `Orchestrated-By: opencode`, no push

## 6. Gaps (stated plainly)

- Options settle (~919) and post-press settle lags are E55D10-measured values reused as plan anchors; the actual settled frames are unobserved until Part 2.
- Whether four Downs land exactly on Save/Load (no wrap, no missed pulse, no submenu intercept) is unobserved; the pre-Cross frame at ~1290 is the check.
- Whether Cross opens a Save/Load result screen vs doing nothing (or opening something else) is unobserved; one pulse is the whole test.
- Whether Save/Load selection issues any `sceMcGetDir`/`sceMcRead` call is unobserved; the probe file decides after Part 2. If the game reads cards earlier (title/menu), those lines will also be present and must be separated by vsync tick.
- Snapshotter tags frames with the latest det-hash tick at copy time (1 s wall grid), not the exact vsync of the PNG; tick labels are approximate.
- Stop-tick wall cost is unmeasured (E55D10 reached tick 953 in ~36 s wall; 1460 ticks is the same order, well under the 500 s cap) — no speed claim.
- No `p_lane_lease` import resolution at edit time (same `sys.path` pattern as E55D10; resolves at runtime on the mini).

**Do not boot until the orchestrator reviews the exact script SHA and
explicitly releases Part 2 in the worker pane.**

---

# E55D11 — Part 2 run (one released Mac boot, 2026-09-24)

Worker: opencode (Muse Spark Contributor Go). Brief:
`local/muse/prompts/E55D11P2.md`. Exactly one boot with the approved
script SHA `f5434273…476b` (verified before launch; script unedited).
Per-worker `OPENCODE_CONFIG_CONTENT` exception (confined to
`~/dev/ssx3-work/E55D11/**`) verified with a tiny sentinel file and
removed before the run (lane dir absent again afterwards). N-lane
cmake/ninja build was active at first check, so the boot waited per the
brief; the orchestrator confirmed N held, `ps` showed no clang/ninja,
then the single `python3 local/research/E55D11/e55d11_boot.py --label S1`
run proceeded. No fork/source edit, build, Odin/iOS action,
seeded-card change, push, board/global config edit, or upstream
contact. No speed claim (diagnostic taps build).

## 1. Evidence table (run)

| Item | Value |
| --- | --- |
| Result | `bound=target`, `elapsed_s=54.823`, `last_hash_tick=1490`, `phase2_extra_s=1.026`, `runner_pid=45235` (gone; SIGTERM rc=-15 expected), mini slot 1 claimed + released (slots free) |
| Frame proof | tick 1480 `snap-1480t-0053.41s.png` ≥ stop 1460 |
| Caps | `log_bytes=707899` ≤ 16 MiB; `frames_bytes=11879874` ≤ 2 GiB; wall 500 / progress 120 / grace 120 (run-control metrics, not speed) |
| Cards | `mc0`/`mc1` empty at start AND end; manifest SHA `f9401596…ccb9ce` unchanged |
| Padscript (boot.log, 15 rows) | `armed n=7 clock=vsync`; presses Start `0x0008` ×1, Square `0x8000` ×1, Down `0x0040` ×4 (separate i=2..5), Cross `0x4000` ×1, in plan order; 7 releases; no other input. D4 fired `now=20203ms at=20187ms` (16 ms late; D4→Cross gap still 134 ticks ≥ 60) |
| Probe (2864 lines) | `getdir` n=4, ALL at vsync 118/122/126/223 (all < Cross 1360), ALL `ok=0 reason=empty len=0 bytes=(empty)`, port=0 slot=0; `mcread` n=0; `pad` n=2860 (2604 pre-Cross, 256 at/after 1360, all ok len=32) |
| Private lane | `~/dev/ssx3-work/E55D11/run/S1/` (boot.log + .gz, probe.log + .gz, result.json, frames/, empty mc0/mc1). Raw log/probe kept; `.gz` copies made only after the runner exited |
| Curated (committed) | `snap-1284t-0047.36s.png` + `.txt`, `snap-1454t-0053.41s.png` + `.txt`, `s1-result.json`, `s1-receipts.txt`, `check-p2.py`. PNG total 281925 B ≤ 2 MiB; text 245 B + receipts ≤ 512 KiB |
| Checker | `check-p2.py` 42/42 PASS (pins, route, caps, cards, pad rows, probe counts, frame/probe SHAs; visual/API labels NOT asserted) |

## 2. Frames (worker-viewed; visual verdict rests with the orchestrator gate)

| File (meta tick) | Reading |
| --- | --- |
| `snap-1284t-0047.36s.png` (tick 1283; \|1284−1290\|=6, nearest pre-Cross full frame) | Title **Options**; rows Game Options, Sound Options, Controller Settings, HUD Options, **Save/Load (highlighted orange bar)**, Enter Cheat, Credits, DONE; footer "Save or load your SSX 3 progress." + X Select / Triangle Previous |
| `snap-1454t-0053.41s.png` (tick 1454; \|1454−1460\|=6, nearest post-Cross full frame) | Title **Save/Load**; rows **Save game (highlighted orange bar)**, Load game, Save options, Load options, Load replay, New game; footer "Save your progress." + X Select / Triangle Previous |
| Adjacent (viewed, not curated) | 1312: same Options + Save/Load highlight as 1284. 1368 (8 ticks after Cross): still Options + Save/Load highlight (transition in flight). 1480: same Save/Load submenu as 1454. No unexpected screen |

Snapshot filename ticks are approximate (1 s wall grid tagged with the
latest det-hash tick); actual metadata ticks and SHAs are recorded in
`s1-receipts.txt`.

## 3. Outcome vs predeclared gate

Pre-Cross full frame exists and shows the Save/Load row highlighted;
post-Cross full frame shows a readable Save/Load submenu. Card side:
zero `getdir`/`mcread` at/after Cross and zero copied table/read bytes
anywhere — only four early `ok=0 reason=empty` GetDir probes (title
boot, empty cards), which prove API reach but not guest-written bytes.
That is predeclared **B** (readable Save/Load result screen without
copied-GetDir/mcRead evidence). The orchestrator makes the visual
verdict.

## 4. Commands run (one boot only)

- Pre-run: script SHA check, sentinel write/remove under
  `~/dev/ssx3-work/E55D11/`, `ps` heavy-job checks (N build held per
  orchestrator coordination), E55D10 `ORCH-GATE-P2.md` read
- `python3 local/research/E55D11/e55d11_boot.py --label S1` → `bound=target` (sole boot/build/run this part)
- Post-run: PID-gone + lease-free checks, frame viewing (1284, 1454, 1312, 1368, 1480), padscript/probe parsing, `gzip -k` of closed boot.log/probe.log, `cp` of 2 PNG + 2 txt + result.json into `local/research/E55D11/`, `python3 local/research/E55D11/check-p2.py` → 42/42 PASS
- `git log -1`, `git status`, stage explicit paths only, commit `[E55D11] Part 2` with `Orchestrated-By: opencode`, no push

## 5. Gaps (stated plainly)

- Tick tags remain snapshotter-approximate; the curated pre/post frames
  are ±6 ticks from their targets with metadata ticks recorded.
- Why Save/Load selection issued no `sceMcGetDir`/`sceMcRead` (deferred
  read, different API, or no read on submenu open) is unobserved; only
  the absence in this probe window is evidenced.
- The four Down pulses' row-by-row travel is inferred from endpoints
  (Options settled → Save/Load highlighted), not from per-press frames.
- Part-1 `check.py` is not re-run post-curation (it asserts the
  no-frames pre-run state by design); `check-p2.py` is the post-run
  checker.
- No `s1-stdout.txt` is committed: stdout was observed live
  (`bound=target` line matches `s1-result.json`); only byte-verifiable
  copies are committed.

Recommended next action: orchestrator visual gate on the two curated
frames (confirm Save/Load highlight + submenu readings), then decide
whether a follow-up lane presses into the Save/Load submenu (e.g. one
Cross on Save game) with the same probe taps to test for deferred
card-API calls.
