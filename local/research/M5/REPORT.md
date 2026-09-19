# M5 — Host replay milestone 2, item 1: REPORT

Replay fidelity + side-effect fences, desktop only. Runbook `local/muse/prompts/M5.md`.
No `adb`, no device. No verdicts.

Header read first: `local/research/S2/REPORT.md` Part 3 (desktop runs, the "Two runs,
Metal" block and the forced-determinism block), Part 4 (§A–§E inventory, "What a
ReplayContext still has to own"), `local/research/S2/s2_replay_capacity.h`, and
`docs/research/120hz-host-replay.md` §"Next runtime boundary".

Time box 6 hours; used about 1.5.

## Baseline note (read before the tables)

The brief pins the S2 header at sha256
`31ffc39d88259a1af895d70ac6187d61128b6ff944270fcda2edb23867e23572`.
The file on disk (`local/research/S2/s2_replay_capacity.h`, clean tree) hashes to
`ffbb81b2516f3e47fbb9cb4af94e85fb560f72b473533cae97b3804904a82396`
(single S2 commit `b542ef8`). Step 1 copied the on-disk file verbatim to
`local/research/M5/m5_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every S2 mechanism is kept in all five steps: PE mask on
the preprocess copy, verbatim execute stream, restore of memory updates + CP + XF
before each replay, PauseAndLock stall, pipe snapshot, watched-window re-hash, `done`.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as S2. `m5-det` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile directories must
be fresh per run, so the configuration ran under profiles `m5-det`, `m5-det2` …
`m5-det6`; `m5-single` is the single-core configuration (no `--cpu-thread`, no
forced determinism); `m5-off` is the final player with `SSX_NATIVE_REPLAY=0`.
Each desktop run held `/tmp/ssx3-host-lease` (`printf 'M5\n'`, removed after each
run); waits and holds are in `local/research/M5/waits.log`. Builds ran any time.

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `ffbb81b2…` (= S2 on disk) | `players/m5-baseline` | `m5-baseline-run` (`m5-det`) | `m5-baseline-probe.jsonl` |
| 2 XFB fidelity | `5616be83…` | `players/m5-xfb` | `m5-xfb-run` (`m5-det2`) | `m5-xfb-probe.jsonl` |
| 3 counters | `4cda538d…` | `players/m5-counters` | `m5-counters-run` (`m5-det3`) | `m5-counters-probe.jsonl` |
| 4 scratch (first, superseded) | `0368532f…` | `players/m5-scratch` | `m5-scratch-run` (`m5-det4`) | `m5-scratch-probe.jsonl` |
| 4 scratch (record) | `9a4a1da1…` | `players/m5-scratch2` | `m5-scratch2-run` (`m5-det6`) | `m5-scratch2-probe.jsonl` |
| 5 sequence | `124df0d9…` | `players/m5-seq` | `m5-seq-run` (`m5-det5`) | `m5-seq-probe.jsonl` |
| 5 disabled | `124df0d9…` | `players/m5-seq` | `m5-off-run` (`m5-off`, replay `0`) | `m5-off-probe.jsonl` |
| ref single | `ffea4825…` (final) | `players/m5-seq2` | `m5-single-run` (`m5-single`) | `m5-single-probe.jsonl` |

The committed header is `ffea4825…` (step 5 + the step-4 recount counter). The
step-5 runs (`m5-seq`, `m5-off`) predate that counter by one field
(`efb_total`/`xfb_patch_n` in `restored`); every other receipt is identical. The
`m5-single` run exercises the committed header on the `det=0` path.

Player dirs live under `local/research/M5/players/` (the build driver requires
outputs under `local/`; they are gitignored build outputs, never committed).
Run dirs, player dirs and every probe jsonl (>5 MB, ~20 MB each) live under
`/Volumes/Extreme SSD/m5/` (symlink-free; `realpath` is the path as written).
Probes, runs and players are not committed.

## Step 1 — baseline (control)

Unmodified copy. `analyze.py` prints 200 rows + `done` + `restored det=1 dual=1`.
Wall med/p95 per replay below is the control for every later step.

## Per-step wall table (baseline vs each step)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m5-baseline | 200 | 10.160 / 16.338 / 3.687 / 20.583 | 2.357 / 3.504 | 312306 / 2736 | YES | seq_wall_ms=1884.575 |
| m5-xfb | 200 | 8.861 / 15.633 / 3.570 / 16.881 | 3.796 / 5.340 | 303674 / 2342 | YES | seq_wall_ms=2097.815 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 |
| m5-counters | 200 | 3.727 / 16.014 / 2.824 / 27.074 | 1.857 / 2.892 | 298371 / 2620 | YES | seq_wall_ms=1171.040 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 |
| m5-scratch2 | 200 | 3.447 / 4.421 / 3.117 / 5.090 | 2.041 / 2.144 | 374653 / 3165 | YES | seq_wall_ms=1035.373 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m5-seq | 200 | 3.710 / 4.143 / 3.415 / 5.754 | 2.170 / 2.271 | 357538 / 3111 | YES | seq_wall_ms=1075.811 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m5-single | 200 | 3.560 / 4.657 / 3.239 / 13.247 | 2.191 / 2.419 | 397443 / 3379 | YES | seq_wall_ms=1105.141 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (312306 … 397443 B), so wall medians are not comparable
across rows as mechanism costs; the p95 band and the per-phase table below carry
the comparison. Every run: 200/200 rows, `done`, `restored det=1 dual=1` except
`m5-single` (`det=0 dual=0`), `mask_bp=2 dls=0 walk=100% unknown=0` in all runs.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m5-baseline | 0.206 | 0.002 | 0.043 | 9.915 | 0.001 | 16.138 |
| m5-xfb | 0.345 | 0.002 | 0.059 | 8.402 | 0.001 | 15.223 |
| m5-counters | 0.131 | 0.001 | 0.032 | 3.557 | 0.000 | 15.811 |
| m5-scratch2 | 0.168 | 0.001 | 0.035 | 3.235 | 0.000 | 4.204 |
| m5-seq | 0.119 | 0.001 | 0.034 | 3.558 | 0.000 | 3.978 |
| m5-single | 0.117 | 0.001 | 0.000 | 3.444 | 0.000 | 4.523 |
```

`m5-single` skips the preprocess pass and aux rewind (`pre_ms`/`sync_ms` 0.000),
as designed. The added hashing/capture work runs outside `wall_ms` accounting
(after `wall_end`) except the before-state capture, which sits before
`wall_start`.

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m5-baseline | 1470 | 70560 | 29.7 |
| m5-xfb | 1062 | 50976 | 41.1 |
| m5-counters | 1263 | 60624 | 34.6 |
| m5-scratch2 | 2423 | 116304 | 18.0 |
| m5-seq | 1721 | 82608 | 25.4 |
| m5-single | 1448 | 69504 | 30.2 (`det=0`, counter only) |

## Step 2 — XFB fidelity

The mask walk also decodes the recorded frame's XFB copy: the EFB-copy BP write
(`BPMEM_TRIGGER_EFB_COPY` 0x52 with the XFB bit, bit 14 of `UPE_Copy`) and the
destination (`BPMEM_EFB_ADDR` 0x4b), stride (0x4d) and copy rectangle
(0x49/0x4a, X10Y10) plus y-scale (0x4e) live at that trigger. Byte range mirrors
`TextureCacheBase::CopyRenderTargetToTexture` for the XFB format (block 16x1, 32
B/block) with `height = 1 + WH.y * yScale` as in `BPStructs.cpp`. After the
original frame (before the first restore) the range is hashed (`RamHash`); after
every replay it is hashed again before the next restore.

```
| Arm | xfb_copies | efb_total (non-XFB) | xfb range (addr, bytes) | ref_ok | scratch_ok (addr, patched) | xfb_equal | xfb_equal_scratch | live_xfb_untouched |
| --- | ---: | --- | --- | :-: | --- | --- | --- | :-: |
| m5-baseline | n/a | n/a (n/a) | n/a, n/a B | n/a | n/a (n/a, n/a) | 0/200 | 0/200 | n/a |
| m5-xfb | 1 | n/a (n/a) | 0x004dc660, 573440 B | 1 | n/a (n/a, n/a) | 200/200 | 0/200 | n/a |
| m5-counters | 1 | n/a (n/a) | 0x004dc660, 573440 B | 1 | n/a (n/a, n/a) | 200/200 | 0/200 | n/a |
| m5-scratch2 | 1 | 7 (6) | 0x004dc660, 573440 B | 1 | 1 (0x01645b00, 1) | 200/200 | 200/200 | 1 |
| m5-seq | 1 | n/a (n/a) | 0x004dc660, 573440 B | 1 | 1 (0x01631000, n/a) | 200/200 | 200/200 | 1 |
| m5-single | 1 | 5 (4) | 0x004dc660, 573440 B | 1 | 1 (0x0165c2c0, 1) | 200/200 | 200/200 | 1 |
```

Every run decoded exactly 1 XFB copy at guest range `0x004dc660`, 573440 B
(448 lines at 1280 B stride). `efb_total` (every 0x52 trigger, XFB or not) was
added with the step-4 recount: 7 total / 6 non-XFB (`m5-scratch2`), 5 total / 4
non-XFB (`m5-single`, a different frame). Non-XFB copies keep their destinations
by construction: only the 0x4b writes governing XFB copies are patched
(`xfb_patch_n=1`, `xfb_patch_bad=0` in both recount runs).

## Step 3 — side-effect counters, fail-closed (measures only)

Per replay, before/after deltas of: texture-cache entry count, deferred
EFB-copy queue length, presenter frame count, header-owned `after_frame_event`
trigger count, PE state bytes (via `PixelEngineManager::DoState` into a scratch
`PointerWrap`), VI state bytes (via `VideoInterfaceManager::DoState`), and the
`g_record_fifo_data` fail-closed check (false before every replay in all runs;
no `record_flag_set` event anywhere).

No public accessor exposes the cache entry count or the pending queue length
(`TextureCacheBase.h`: both private, no size getter; `DoState` flushes, so it
cannot serve as a passive probe). The header promotes `TextureCacheBase.h`
visibility header-locally for the probe TU only (no vendor change) for passive
`.size()` reads; every other counter uses public APIs. The `after_frame`
listener only increments; each of its triggers also runs
`TextureCacheBase::OnFrameEnd`, so its count doubles as the `FlushEFBCopies`
opportunity count.

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m5-counters | dtex | -6 | 0 |
| m5-counters | dpend | 0 | 0 |
| m5-counters | dframe | 1 | 1 |
| m5-counters | dafter | 1 | 1 |
| m5-counters | pediff | 0 | 0 |
| m5-counters | vidiff | 0 | 0 |
| m5-scratch2 | dtex | -1 | 1 |
| m5-scratch2 | dpend | 0 | 0 |
| m5-scratch2 | dframe | 1 | 1 |
| m5-scratch2 | dafter | 1 | 1 |
| m5-scratch2 | pediff | 0 | 0 |
| m5-scratch2 | vidiff | 0 | 0 |
| m5-seq | dtex | -5 | 0 |
| m5-seq | dpend | 0 | 0 |
| m5-seq | dframe | 1 | 1 |
| m5-seq | dafter | 1 | 1 |
| m5-seq | pediff | 0 | 0 |
| m5-seq | vidiff | 0 | 0 |
| m5-single | dtex | -7 | 1 |
| m5-single | dpend | 0 | 0 |
| m5-single | dframe | 1 | 1 |
| m5-single | dafter | 1 | 1 |
| m5-single | pediff | 0 | 2 |
| m5-single | vidiff | 0 | 0 |
```

Sequence-entry absolutes (`counters_summary tex0/pend0/fc0`): tex0 105/98/115/113,
pend0 0 in all runs, fc0 8082/8093/8124/8169. `completed=200` in all summaries.

Two observations are recorded without verdict. First, `dframe` is exactly +1 per
replay in every run, including the scratch runs where the live XFB is never
rewritten — the content-change hypothesis (async `ViSwap` seeing fresh XFB bytes
via `VideoBackendBase::Video_OutputXFB`) does not survive the redirect, and the
exact +1 × 200 admits no wall-clock reading; the driver is unresolved (see What
I could not do). Second, `dtex` is never positive beyond +1 while reaching -7:
entries are removed, not accumulated, across these sequences. `dpend` is 0/0 at
every replay boundary with `pend0=0`. `pediff`/`vidiff` are 0/0 on all `det=1`
runs; `m5-single` (`det=0`, execute-side PE calls live) shows `pediff` 0/2.

## Step 4 — replay-owned XFB destination

 scratch rule (how the address was chosen): 16-byte aligned, 0x100 guard gap
above the highest byte used by any recorded RAM memory update or the live XFB,
in the same address base as the live XFB (offset domain here: live XFB
`0x004dc660` carries base 0), with the scratch XFB (same 573440 B) fitting below
the RAM top; verified with `GetPointerForRange` and checked for overlap with the
live XFB in offset domain. The scratch lies inside the S2 whole-RAM watched
window, but the sequence restores all of RAM/EXRAM afterwards, so the re-hash
still verifies (`done` in all scratch runs). Governing 0x4b offsets come from the
mask walk (last 0x4b before each XFB trigger, deduped); patching fails closed
(`xfb_patch_bad`, verbatim stream on any malformed offset).

Chosen scratch addresses: `0x0162b1c0` (first scratch run), `0x01645b00`
(`m5-scratch2`), `0x01631000` (`m5-seq`), `0x0165c2c0` (`m5-single`) —
all above that run's recorded updates and live XFB, all with `xfb_patch_bad=0`.

Receipts: `xfb_equal_scratch=200/200` in `m5-scratch2`, `m5-seq`, `m5-single`;
`live_xfb_untouched=1` (`live_same=200/200`) in all three. The step-2
`xfb_equal` field is still emitted (200/200: the per-replay restores never
clobber the live XFB range, so it holds the original content throughout).

## Step 5 — continuation check

`record_start` carries the presenter frame count as the seam id. After the
sequence and the S2 restore, a one-shot `after_frame` listener captures the
first live XFB copy after resume (range from the live BP regs, hashed from guest
RAM). The disabled run (`SSX_NATIVE_REPLAY=0`, same player) emits the same two
events with `replay_disabled=1`.

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m5-seq (sequence) | `fc=8121` | `replay_disabled=0 fc=8324 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m5-off (disabled) | `replay_disabled=1 fc=8142` | `replay_disabled=1 fc=8142 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m5-single (sequence, det=0) | `fc=8166` | `replay_disabled=0 fc=8369 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

The two `m5-det` runs did not reach the seam at the same frame (8121 vs 8142),
so per the brief the hash comparison is skipped — no comparison is offered. Two
further observations without verdict: `8324 - 8124 = 200` (the `counters_summary`
`fc0` plus exactly the 200 per-replay `dframe` increments lands on the resume
frame), and all three `resume_xfb` hashes are byte-identical
(`0cbfe49a0d4ee325`) at the same address and size. The hash is not degenerate:
FNV-1a64 of 573440 zero bytes is `af864f95a9f12325`. The watched-window re-hash
+ `done` stands in all sequence runs.

## Exact commands

Builds (any time, `local/tooling/ninja` internally; only the header path differs
from `local/research/S2/build_replay_player.py`):

```
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-baseline
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-xfb
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-counters
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-scratch
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-scratch2
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-seq
python3 local/research/M5/build_replay_player.py local/research/M5/players/m5-seq2
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M5\n'`, remove after
each run; profiles fresh per run):

```
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-baseline-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-baseline-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-xfb-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-xfb --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det2 --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-xfb-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-counters-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-counters --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det3 --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-counters-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-scratch-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-scratch --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det4 --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-scratch-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-seq-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-seq --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det5 --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-seq-run --seconds 240
SSX_NATIVE_REPLAY=0 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-off-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-seq --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-off --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-off-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-scratch2-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-scratch2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-det6 --cpu-thread --output /Volumes/Extreme\ SSD/m5/m5-scratch2-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m5/m5-single-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M5/players/m5-seq2 --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m5-single --output /Volumes/Extreme\ SSD/m5/m5-single-run --seconds 240
```

Analysis:

```
python3 local/research/M5/analyze.py "m5-baseline=/Volumes/Extreme SSD/m5/m5-baseline-probe.jsonl" "m5-xfb=/Volumes/Extreme SSD/m5/m5-xfb-probe.jsonl" "m5-counters=/Volumes/Extreme SSD/m5/m5-counters-probe.jsonl" "m5-scratch2=/Volumes/Extreme SSD/m5/m5-scratch2-probe.jsonl" "m5-seq=/Volumes/Extreme SSD/m5/m5-seq-probe.jsonl" "m5-single=/Volumes/Extreme SSD/m5/m5-single-probe.jsonl"
python3 local/research/M5/analyze.py "m5-off=/Volumes/Extreme SSD/m5/m5-off-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M5/` — `m5_replay_context.h`
(`ffea4825…`), `build_replay_player.py`, `analyze.py`, `REPORT.md`, `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m5/` —
`m5-baseline-probe.jsonl`, `m5-xfb-probe.jsonl`, `m5-counters-probe.jsonl`,
`m5-scratch-probe.jsonl`, `m5-scratch2-probe.jsonl`, `m5-seq-probe.jsonl`,
`m5-off-probe.jsonl`, `m5-single-probe.jsonl` (~20 MB each) and the matching
`-run` dirs; per-step header snapshots `m5_replay_context.step{1..5}.h`.
Players (gitignored): `local/research/M5/players/{m5-baseline,m5-xfb,m5-counters,m5-scratch,m5-scratch2,m5-seq,m5-seq2}/`
(each with `player`, `build.json`, launchers). All paths above are symlink-free
as written (`realpath` identical).

## What I could not do

- The brief's pinned S2 sha (`31ffc39d…`) does not match the file on disk
(`ffbb81b2…`, clean tree, single S2 commit). The baseline is the on-disk file;
the step-1 diff is empty against it. The two hashes are both recorded here.
- Player dirs are under `local/research/M5/players/` rather than the SSD: the
build driver refuses outputs outside `local/`. Run dirs and all >5 MB probes are
on the SSD as ordered.
- The `dframe` +1/replay driver is unresolved. Candidates checked:
`Presenter::ViSwap` (non-duplicate) / `ImmediateSwap` are the only
`m_frame_count` writers; the in-sequence present branch is dead and the scratch
redirect (live XFB byte-identical throughout) does not stop the +1, refuting the
XFB-content-change path through `VideoBackendBase::Video_OutputXFB`. Exact +1 ×
200 in every run rules out wall-clock VI-field accumulation. Needs presenter
event tracing, not done here.
- The continuation comparison was skipped per the brief (seam fc 8121 vs 8142).
The triple-identical `resume_xfb` hash (`0cbfe49a0d4ee325` across `m5-seq`,
`m5-off`, `m5-single`) is tabulated as observed; whether the first post-resume
XFB genuinely repeats byte-identical content across runs needs a same-frame
pixel-level follow-up, not done here.
- No `m5-single` run was ordered by the steps; one is included as a reference
(the named profile, final header, `det=0` path) with no comparison offered.
- Desktop only; no device work. `m5-single` shows `pediff` 0/2 — the execute-side
PE effect the S2 report predicted for `det=0` — tabulated, not pursued.

## Files

Committed under `local/research/M5/`: `m5_replay_context.h` (research header,
`ffea4825…`), `build_replay_player.py` (S2 driver, header path only),
`analyze.py` (S2 tables unchanged + M5 XFB/counter/continuation sections),
`REPORT.md` (this file), `waits.log` (lease polls, claims, releases).

## Header diffs per step (`diff -u` against the S2 header)

Step 1: empty (verbatim copy). Steps 2–5 follow, cumulative per step.

### Step 2

```diff
--- local/research/S2/s2_replay_capacity.h	2026-09-18 11:50:29
+++ /Volumes/Extreme SSD/m5/m5_replay_context.step2.h	2026-09-18 20:31:32
@@ -229,6 +229,24 @@
 // preprocess BP handler acts on into five GX_NOPs. Byte length is unchanged,
 // no aux-buffer command is touched, so the preprocess and execute passes still
 // push and pop the same aux payload in the same order.
+// --- M5 step 2: XFB fidelity -------------------------------------------------
+//
+// The same mask walk also decodes the recorded frame's XFB copy destination:
+// the EFB-copy BP write (BPMEM_TRIGGER_EFB_COPY 0x52 with the XFB bit, bit 14)
+// and the live destination (BPMEM_EFB_ADDR 0x4b), stride (0x4d) and copy
+// rectangle (0x49/0x4a, X10Y10) plus y-scale (0x4e) at that trigger. The byte
+// range mirrors TextureCacheBase::CopyRenderTargetToTexture for the XFB format
+// (block 16x1, 32 bytes/block): bytes_per_row = AlignUp(width,16)/16*32,
+// covered = height * stride with height = 1 + WH.y * yScale as in BPStructs.
+struct XfbRange {
+  bool found = false;
+  u32 copies = 0;   // XFB-copy triggers seen in the recorded stream
+  u32 addr = 0;     // guest byte address (copyTexDest << 5)
+  u32 stride = 0;   // bytes per row (copyDestStride << 5)
+  u32 width = 0;    // copyTexSrcWH.x + 1
+  u32 height = 0;   // 1 + copyTexSrcWH.y * yScale
+  u32 bytes = 0;    // height * stride
+};
 struct MaskStats {
   u32 consumed = 0;
   u32 masked = 0;
@@ -238,6 +256,7 @@
   u32 dl_bytes = 0;
   u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
   u32 unknown = 0;
+  XfbRange xfb;
 };
 class PeMaskWalk final : public OpcodeDecoder::Callback {
 public:
@@ -245,7 +264,49 @@
       : m_base(base), m_cp(cp_mem), m_stats(stats) {}
   void OnXF(u16, u8, const u8*) override {}
   void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
-  void OnBP(u8 command, u32) override { m_bp_reg = int(command); }
+  void OnBP(u8 command, u32 value) override {
+    m_bp_reg = int(command);
+    // M5 step 2: track the XFB-copy destination registers live at each XFB trigger.
+    switch (command) {
+    case BPMEM_EFB_TL:
+      m_tl = value;
+      break;
+    case BPMEM_EFB_WH:
+      m_wh = value;
+      break;
+    case BPMEM_EFB_ADDR:
+      m_dest = value;
+      break;
+    case BPMEM_EFB_STRIDE:
+      m_stride = value;
+      break;
+    case BPMEM_COPYYSCALE:
+      m_yscale = value;
+      break;
+    case BPMEM_TRIGGER_EFB_COPY:
+      if ((value >> 14) & 1u) {  // UPE_Copy::copy_to_xfb
+        XfbRange& r = m_stats.xfb;
+        ++r.copies;
+        const u32 w = (m_wh & 0x3ffu) + 1u;
+        const u32 hsrc = (m_wh >> 10) & 0x3ffu;
+        const bool invert = ((value >> 10) & 1u) != 0;  // UPE_Copy::scale_invert
+        float yscale = 1.0f;
+        if (m_yscale != 0)
+          yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
+        // m_yscale == 0 keeps yscale == 1.0f (fallback; real frames set 0x4e).
+        const u32 h = u32(1.0f + float(hsrc) * yscale);
+        r.addr = m_dest << 5;
+        r.stride = m_stride << 5;
+        r.width = w;
+        r.height = h;
+        r.bytes = h * r.stride;
+        r.found = (r.bytes > 0 && r.addr != 0);
+      }
+      break;
+    default:
+      break;
+    }
+  }
   void OnIndexedLoad(CPArray, u32, u16, u8 size) override {
     ++m_stats.indexed;
     m_stats.indexed_bytes += u32(size) * 4u;
@@ -285,6 +346,12 @@
   CPState m_cp;
   MaskStats& m_stats;
   int m_bp_reg = -1;
+  // M5 step 2: last-seen XFB destination registers (24-bit BP values).
+  u32 m_tl = 0;
+  u32 m_wh = 0;
+  u32 m_dest = 0;
+  u32 m_stride = 0;
+  u32 m_yscale = 0;
 };
 static MaskStats BuildMaskedStream(const std::vector<u8>& src, const u32* cp_mem,
                                    std::vector<u8>& out) {
@@ -491,6 +558,19 @@
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
 
+  // M5 step 2: reference hash of the live XFB after the original frame, taken
+  // before the first restore. After every replay the same range is hashed
+  // again (before the next restore) and compared.
+  u64 xfb_ref = 0;
+  bool xfb_ref_ok = false;
+  if (mask.xfb.found && mask.xfb.bytes > 0) {
+    if (u8* ptr = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+      xfb_ref = RamHash(ptr, mask.xfb.bytes);
+      xfb_ref_ok = true;
+    }
+  }
+  unsigned xfb_equal_count = 0;
+
   const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
   const std::vector<u8> prelude = Prelude(file);
   ApplyMemory(system, file);
@@ -498,14 +578,16 @@
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
   {
-    char detail[256];
+    char detail[384];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
-                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u",
+                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
+                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
-                  mask.unknown, mask.benign_unknown);
+                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
+                  mask.xfb.bytes, int(xfb_ref_ok));
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -542,15 +624,23 @@
     replay_wall_ms[replays] = (wall_end - wall_start) * 1000.0;
     replay_cpu_ms[replays] =
         (cpu_start >= 0 && cpu_end >= 0) ? (cpu_end - cpu_start) : -1.0;
+    // M5 step 2: hash the XFB destination after this replay, before the next
+    // restore. Hashed after wall_end so the hash cost stays out of wall_ms.
+    int xfb_equal = 0;
+    if (xfb_ref_ok) {
+      if (u8* rp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes))
+        xfb_equal = (RamHash(rp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+    }
+    xfb_equal_count += unsigned(xfb_equal);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
-                 "\"sync_ms\":%.3f,\"xform\":%d,\"render_execution\":true}\n",
+                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom));
+                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
@@ -571,9 +661,11 @@
       RamHash(live_memory.GetRAM(), ram_size) == RamHash(saved_ram.data(), ram_size) &&
       (exram_size == 0 ||
        RamHash(live_memory.GetEXRAM(), exram_size) == RamHash(saved_exram.data(), exram_size));
-  char done_detail[64]; // whole-200 wall time on the done event.
-  std::snprintf(done_detail, sizeof(done_detail), "seq_wall_ms=%.3f",
-                (seq_end - seq_start) * 1000.0);
+  char done_detail[160]; // whole-200 wall time + M5 XFB count on the done event.
+  std::snprintf(done_detail, sizeof(done_detail),
+                "seq_wall_ms=%.3f xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u",
+                (seq_end - seq_start) * 1000.0, xfb_equal_count, mask.xfb.addr,
+                mask.xfb.bytes);
   Event(window_ok ? "done" : "watched_window_changed", done_detail);
   phase = Phase::Done;
 }
```

### Step 3

```diff
--- local/research/S2/s2_replay_capacity.h	2026-09-18 11:50:29
+++ /Volumes/Extreme SSD/m5/m5_replay_context.step3.h	2026-09-18 20:31:32
@@ -69,6 +69,24 @@
 #include "VideoCommon/AbstractGfx.h"
 #include "VideoCommon/Fifo.h"
 #include "VideoCommon/VideoConfig.h"
+// M5 step 3: side-effect counters. No public accessor exposes the
+// texture-cache entry count (m_textures_by_address) or the deferred EFB-copy
+// queue length (m_pending_efb_copies), so visibility of TextureCacheBase.h is
+// promoted header-locally for this probe TU only (the vendor tree is
+// untouched) for passive size reads. Every other counter uses public APIs:
+// g_presenter->FrameCount(), our own after_frame_event listener, PE/VI DoState
+// snapshots, OpcodeDecoder::g_record_fifo_data.
+#define M5_VIS public
+#define private M5_VIS
+#define protected M5_VIS
+#include "VideoCommon/TextureCacheBase.h"
+#undef private
+#undef protected
+#include "VideoCommon/Present.h"
+#include "VideoCommon/PixelEngine.h"
+#include "Core/HW/VideoInterface.h"
+#include "VideoCommon/VideoEvents.h"
+#include "Common/HookableEvent.h"
 #include <cstdio>
 #include <cstring>
 #include <ctime>
@@ -120,6 +138,55 @@
   return hash;
 }
 
+// --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
+static unsigned long long s_after_frame_triggers = 0;
+struct SideFx {
+  size_t tex_entries = 0;
+  size_t pending = 0;
+  int frame_count = -1;
+  unsigned long long after_frame = 0;
+  std::vector<u8> pe_state;
+  std::vector<u8> vi_state;
+};
+static std::vector<u8> DoStateBytes_PE(Core::System& system) {
+  std::vector<u8> buf(512, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetPixelEngine().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static std::vector<u8> DoStateBytes_VI(Core::System& system) {
+  std::vector<u8> buf(2048, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetVideoInterface().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static SideFx CaptureSideFx(Core::System& system) {
+  SideFx s;
+  if (g_texture_cache) {
+    s.tex_entries = g_texture_cache->m_textures_by_address.size();
+    s.pending = g_texture_cache->m_pending_efb_copies.size();
+  }
+  if (g_presenter) s.frame_count = g_presenter->FrameCount();
+  s.after_frame = s_after_frame_triggers;
+  s.pe_state = DoStateBytes_PE(system);
+  s.vi_state = DoStateBytes_VI(system);
+  return s;
+}
+static unsigned DiffBytes(const std::vector<u8>& a, const std::vector<u8>& b) {
+  unsigned n = 0;
+  const size_t len = a.size() > b.size() ? a.size() : b.size();
+  for (size_t i = 0; i < len; ++i) {
+    const u8 x = i < a.size() ? a[i] : 0;
+    const u8 y = i < b.size() ? b[i] : 0;
+    if (x != y) ++n;
+  }
+  return n;
+}
+
 // Command bytes that restore the recorded initial BP/CP/XF state, mirroring
 // FifoPlayer::LoadRegisters (same register exclusions), so draw command sizes
 // and matrices decode as they did when the frame was recorded.
@@ -229,6 +296,24 @@
 // preprocess BP handler acts on into five GX_NOPs. Byte length is unchanged,
 // no aux-buffer command is touched, so the preprocess and execute passes still
 // push and pop the same aux payload in the same order.
+// --- M5 step 2: XFB fidelity -------------------------------------------------
+//
+// The same mask walk also decodes the recorded frame's XFB copy destination:
+// the EFB-copy BP write (BPMEM_TRIGGER_EFB_COPY 0x52 with the XFB bit, bit 14)
+// and the live destination (BPMEM_EFB_ADDR 0x4b), stride (0x4d) and copy
+// rectangle (0x49/0x4a, X10Y10) plus y-scale (0x4e) at that trigger. The byte
+// range mirrors TextureCacheBase::CopyRenderTargetToTexture for the XFB format
+// (block 16x1, 32 bytes/block): bytes_per_row = AlignUp(width,16)/16*32,
+// covered = height * stride with height = 1 + WH.y * yScale as in BPStructs.
+struct XfbRange {
+  bool found = false;
+  u32 copies = 0;   // XFB-copy triggers seen in the recorded stream
+  u32 addr = 0;     // guest byte address (copyTexDest << 5)
+  u32 stride = 0;   // bytes per row (copyDestStride << 5)
+  u32 width = 0;    // copyTexSrcWH.x + 1
+  u32 height = 0;   // 1 + copyTexSrcWH.y * yScale
+  u32 bytes = 0;    // height * stride
+};
 struct MaskStats {
   u32 consumed = 0;
   u32 masked = 0;
@@ -238,6 +323,7 @@
   u32 dl_bytes = 0;
   u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
   u32 unknown = 0;
+  XfbRange xfb;
 };
 class PeMaskWalk final : public OpcodeDecoder::Callback {
 public:
@@ -245,7 +331,49 @@
       : m_base(base), m_cp(cp_mem), m_stats(stats) {}
   void OnXF(u16, u8, const u8*) override {}
   void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
-  void OnBP(u8 command, u32) override { m_bp_reg = int(command); }
+  void OnBP(u8 command, u32 value) override {
+    m_bp_reg = int(command);
+    // M5 step 2: track the XFB-copy destination registers live at each XFB trigger.
+    switch (command) {
+    case BPMEM_EFB_TL:
+      m_tl = value;
+      break;
+    case BPMEM_EFB_WH:
+      m_wh = value;
+      break;
+    case BPMEM_EFB_ADDR:
+      m_dest = value;
+      break;
+    case BPMEM_EFB_STRIDE:
+      m_stride = value;
+      break;
+    case BPMEM_COPYYSCALE:
+      m_yscale = value;
+      break;
+    case BPMEM_TRIGGER_EFB_COPY:
+      if ((value >> 14) & 1u) {  // UPE_Copy::copy_to_xfb
+        XfbRange& r = m_stats.xfb;
+        ++r.copies;
+        const u32 w = (m_wh & 0x3ffu) + 1u;
+        const u32 hsrc = (m_wh >> 10) & 0x3ffu;
+        const bool invert = ((value >> 10) & 1u) != 0;  // UPE_Copy::scale_invert
+        float yscale = 1.0f;
+        if (m_yscale != 0)
+          yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
+        // m_yscale == 0 keeps yscale == 1.0f (fallback; real frames set 0x4e).
+        const u32 h = u32(1.0f + float(hsrc) * yscale);
+        r.addr = m_dest << 5;
+        r.stride = m_stride << 5;
+        r.width = w;
+        r.height = h;
+        r.bytes = h * r.stride;
+        r.found = (r.bytes > 0 && r.addr != 0);
+      }
+      break;
+    default:
+      break;
+    }
+  }
   void OnIndexedLoad(CPArray, u32, u16, u8 size) override {
     ++m_stats.indexed;
     m_stats.indexed_bytes += u32(size) * 4u;
@@ -285,6 +413,12 @@
   CPState m_cp;
   MaskStats& m_stats;
   int m_bp_reg = -1;
+  // M5 step 2: last-seen XFB destination registers (24-bit BP values).
+  u32 m_tl = 0;
+  u32 m_wh = 0;
+  u32 m_dest = 0;
+  u32 m_stride = 0;
+  u32 m_yscale = 0;
 };
 static MaskStats BuildMaskedStream(const std::vector<u8>& src, const u32* cp_mem,
                                    std::vector<u8>& out) {
@@ -491,6 +625,19 @@
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
 
+  // M5 step 2: reference hash of the live XFB after the original frame, taken
+  // before the first restore. After every replay the same range is hashed
+  // again (before the next restore) and compared.
+  u64 xfb_ref = 0;
+  bool xfb_ref_ok = false;
+  if (mask.xfb.found && mask.xfb.bytes > 0) {
+    if (u8* ptr = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+      xfb_ref = RamHash(ptr, mask.xfb.bytes);
+      xfb_ref_ok = true;
+    }
+  }
+  unsigned xfb_equal_count = 0;
+
   const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
   const std::vector<u8> prelude = Prelude(file);
   ApplyMemory(system, file);
@@ -498,20 +645,46 @@
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
   {
-    char detail[256];
+    char detail[384];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
-                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u",
+                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
+                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
-                  mask.unknown, mask.benign_unknown);
+                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
+                  mask.xfb.bytes, int(xfb_ref_ok));
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
+  // M5 step 3: count after_frame_event triggers for the duration of the
+  // sequence with the header's own listener. Passive: it only increments.
+  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
+  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
+  s_after_frame_triggers = 0;
+  Common::EventHook m5_after_frame_hook =
+      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
+        ++s_after_frame_triggers;
+      });
+  const SideFx fx_base = CaptureSideFx(system);
+  // Min/max trackers over the per-replay deltas for the summary receipt.
+  long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
+  long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
+  bool fx_first = true;
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
+    // M5 step 3, fail-closed: the recorder must be idle; a replay that
+    // re-arms g_record_fifo_data would corrupt any live capture.
+    if (OpcodeDecoder::g_record_fifo_data) {
+      char rd[64];
+      std::snprintf(rd, sizeof(rd), "replay=%u", replays);
+      Event("record_flag_set", rd);
+      break;
+    }
+    const SideFx fx_before = CaptureSideFx(system);
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -542,18 +715,80 @@
     replay_wall_ms[replays] = (wall_end - wall_start) * 1000.0;
     replay_cpu_ms[replays] =
         (cpu_start >= 0 && cpu_end >= 0) ? (cpu_end - cpu_start) : -1.0;
+    // M5 step 2: hash the XFB destination after this replay, before the next
+    // restore. Hashed after wall_end so the hash cost stays out of wall_ms.
+    int xfb_equal = 0;
+    if (xfb_ref_ok) {
+      if (u8* rp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes))
+        xfb_equal = (RamHash(rp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+    }
+    xfb_equal_count += unsigned(xfb_equal);
+    // M5 step 3: after-state and deltas. Captured after wall_end so the
+    // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
+    const SideFx fx_after = CaptureSideFx(system);
+    const long long dtex =
+        static_cast<long long>(fx_after.tex_entries) - static_cast<long long>(fx_before.tex_entries);
+    const long long dpend =
+        static_cast<long long>(fx_after.pending) - static_cast<long long>(fx_before.pending);
+    const long long dframe =
+        static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
+    const long long dafter =
+        static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
+    const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    if (fx_first) {
+      min_dtex = max_dtex = dtex;
+      min_dpend = max_dpend = dpend;
+      min_dframe = max_dframe = dframe;
+      min_dafter = max_dafter = dafter;
+      min_pe = max_pe = pediff;
+      min_vi = max_vi = vidiff;
+      fx_first = false;
+    } else {
+      if (dtex < min_dtex) min_dtex = dtex;
+      if (dtex > max_dtex) max_dtex = dtex;
+      if (dpend < min_dpend) min_dpend = dpend;
+      if (dpend > max_dpend) max_dpend = dpend;
+      if (dframe < min_dframe) min_dframe = dframe;
+      if (dframe > max_dframe) max_dframe = dframe;
+      if (dafter < min_dafter) min_dafter = dafter;
+      if (dafter > max_dafter) max_dafter = dafter;
+      if (pediff < min_pe) min_pe = pediff;
+      if (pediff > max_pe) max_pe = pediff;
+      if (vidiff < min_vi) min_vi = vidiff;
+      if (vidiff > max_vi) max_vi = vidiff;
+    }
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
-                 "\"sync_ms\":%.3f,\"xform\":%d,\"render_execution\":true}\n",
+                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
+                 "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"pediff\":%lld,\"vidiff\":%lld,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom));
+                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
+                 dtex, dpend, dframe, dafter, pediff, vidiff);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
+  // event. completed = capacity rows actually emitted (record_flag_set stops
+  // the sequence early, fail-closed).
+  {
+    char summary[512];
+    std::snprintf(summary, sizeof(summary),
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
+                  "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld",
+                  replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
+                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
+                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi);
+    Event("counters_summary", summary);
+  }
+  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
@@ -571,9 +806,11 @@
       RamHash(live_memory.GetRAM(), ram_size) == RamHash(saved_ram.data(), ram_size) &&
       (exram_size == 0 ||
        RamHash(live_memory.GetEXRAM(), exram_size) == RamHash(saved_exram.data(), exram_size));
-  char done_detail[64]; // whole-200 wall time on the done event.
-  std::snprintf(done_detail, sizeof(done_detail), "seq_wall_ms=%.3f",
-                (seq_end - seq_start) * 1000.0);
+  char done_detail[192]; // whole-200 wall time + M5 XFB count on the done event.
+  std::snprintf(done_detail, sizeof(done_detail),
+                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u",
+                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, mask.xfb.addr,
+                mask.xfb.bytes);
   Event(window_ok ? "done" : "watched_window_changed", done_detail);
   phase = Phase::Done;
 }
```

### Step 4

```diff
--- local/research/S2/s2_replay_capacity.h	2026-09-18 11:50:29
+++ /Volumes/Extreme SSD/m5/m5_replay_context.step4.h	2026-09-18 21:07:43
@@ -69,6 +69,24 @@
 #include "VideoCommon/AbstractGfx.h"
 #include "VideoCommon/Fifo.h"
 #include "VideoCommon/VideoConfig.h"
+// M5 step 3: side-effect counters. No public accessor exposes the
+// texture-cache entry count (m_textures_by_address) or the deferred EFB-copy
+// queue length (m_pending_efb_copies), so visibility of TextureCacheBase.h is
+// promoted header-locally for this probe TU only (the vendor tree is
+// untouched) for passive size reads. Every other counter uses public APIs:
+// g_presenter->FrameCount(), our own after_frame_event listener, PE/VI DoState
+// snapshots, OpcodeDecoder::g_record_fifo_data.
+#define M5_VIS public
+#define private M5_VIS
+#define protected M5_VIS
+#include "VideoCommon/TextureCacheBase.h"
+#undef private
+#undef protected
+#include "VideoCommon/Present.h"
+#include "VideoCommon/PixelEngine.h"
+#include "Core/HW/VideoInterface.h"
+#include "VideoCommon/VideoEvents.h"
+#include "Common/HookableEvent.h"
 #include <cstdio>
 #include <cstring>
 #include <ctime>
@@ -120,6 +138,55 @@
   return hash;
 }
 
+// --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
+static unsigned long long s_after_frame_triggers = 0;
+struct SideFx {
+  size_t tex_entries = 0;
+  size_t pending = 0;
+  int frame_count = -1;
+  unsigned long long after_frame = 0;
+  std::vector<u8> pe_state;
+  std::vector<u8> vi_state;
+};
+static std::vector<u8> DoStateBytes_PE(Core::System& system) {
+  std::vector<u8> buf(512, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetPixelEngine().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static std::vector<u8> DoStateBytes_VI(Core::System& system) {
+  std::vector<u8> buf(2048, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetVideoInterface().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static SideFx CaptureSideFx(Core::System& system) {
+  SideFx s;
+  if (g_texture_cache) {
+    s.tex_entries = g_texture_cache->m_textures_by_address.size();
+    s.pending = g_texture_cache->m_pending_efb_copies.size();
+  }
+  if (g_presenter) s.frame_count = g_presenter->FrameCount();
+  s.after_frame = s_after_frame_triggers;
+  s.pe_state = DoStateBytes_PE(system);
+  s.vi_state = DoStateBytes_VI(system);
+  return s;
+}
+static unsigned DiffBytes(const std::vector<u8>& a, const std::vector<u8>& b) {
+  unsigned n = 0;
+  const size_t len = a.size() > b.size() ? a.size() : b.size();
+  for (size_t i = 0; i < len; ++i) {
+    const u8 x = i < a.size() ? a[i] : 0;
+    const u8 y = i < b.size() ? b[i] : 0;
+    if (x != y) ++n;
+  }
+  return n;
+}
+
 // Command bytes that restore the recorded initial BP/CP/XF state, mirroring
 // FifoPlayer::LoadRegisters (same register exclusions), so draw command sizes
 // and matrices decode as they did when the frame was recorded.
@@ -229,6 +296,24 @@
 // preprocess BP handler acts on into five GX_NOPs. Byte length is unchanged,
 // no aux-buffer command is touched, so the preprocess and execute passes still
 // push and pop the same aux payload in the same order.
+// --- M5 step 2: XFB fidelity -------------------------------------------------
+//
+// The same mask walk also decodes the recorded frame's XFB copy destination:
+// the EFB-copy BP write (BPMEM_TRIGGER_EFB_COPY 0x52 with the XFB bit, bit 14)
+// and the live destination (BPMEM_EFB_ADDR 0x4b), stride (0x4d) and copy
+// rectangle (0x49/0x4a, X10Y10) plus y-scale (0x4e) at that trigger. The byte
+// range mirrors TextureCacheBase::CopyRenderTargetToTexture for the XFB format
+// (block 16x1, 32 bytes/block): bytes_per_row = AlignUp(width,16)/16*32,
+// covered = height * stride with height = 1 + WH.y * yScale as in BPStructs.
+struct XfbRange {
+  bool found = false;
+  u32 copies = 0;   // XFB-copy triggers seen in the recorded stream
+  u32 addr = 0;     // guest byte address (copyTexDest << 5)
+  u32 stride = 0;   // bytes per row (copyDestStride << 5)
+  u32 width = 0;    // copyTexSrcWH.x + 1
+  u32 height = 0;   // 1 + copyTexSrcWH.y * yScale
+  u32 bytes = 0;    // height * stride
+};
 struct MaskStats {
   u32 consumed = 0;
   u32 masked = 0;
@@ -238,6 +323,13 @@
   u32 dl_bytes = 0;
   u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
   u32 unknown = 0;
+  XfbRange xfb;
+  // M5 step 4: stream offsets of the BPMEM_EFB_ADDR writes governing each XFB
+  // copy (for the replay-owned scratch retarget).
+  std::vector<u32> xfb_addr_offsets;
+  // M5 step 4 recount: every EFB-copy trigger (XFB or not). Non-XFB copies
+  // keep their destinations; non-XFB count = efb_copies_total - xfb.copies.
+  u32 efb_copies_total = 0;
 };
 class PeMaskWalk final : public OpcodeDecoder::Callback {
 public:
@@ -245,7 +337,53 @@
       : m_base(base), m_cp(cp_mem), m_stats(stats) {}
   void OnXF(u16, u8, const u8*) override {}
   void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
-  void OnBP(u8 command, u32) override { m_bp_reg = int(command); }
+  void OnBP(u8 command, u32 value) override {
+    m_bp_reg = int(command);
+    // M5 step 2: track the XFB-copy destination registers live at each XFB trigger.
+    switch (command) {
+    case BPMEM_EFB_TL:
+      m_tl = value;
+      break;
+    case BPMEM_EFB_WH:
+      m_wh = value;
+      break;
+    case BPMEM_EFB_ADDR:
+      m_dest = value;
+      break;
+    case BPMEM_EFB_STRIDE:
+      m_stride = value;
+      break;
+    case BPMEM_COPYYSCALE:
+      m_yscale = value;
+      break;
+    case BPMEM_TRIGGER_EFB_COPY:
+      ++m_stats.efb_copies_total;
+      if ((value >> 14) & 1u) {  // UPE_Copy::copy_to_xfb
+        XfbRange& r = m_stats.xfb;
+        ++r.copies;
+        const u32 w = (m_wh & 0x3ffu) + 1u;
+        const u32 hsrc = (m_wh >> 10) & 0x3ffu;
+        const bool invert = ((value >> 10) & 1u) != 0;  // UPE_Copy::scale_invert
+        float yscale = 1.0f;
+        if (m_yscale != 0)
+          yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
+        // m_yscale == 0 keeps yscale == 1.0f (fallback; real frames set 0x4e).
+        const u32 h = u32(1.0f + float(hsrc) * yscale);
+        r.addr = m_dest << 5;
+        r.stride = m_stride << 5;
+        r.width = w;
+        r.height = h;
+        r.bytes = h * r.stride;
+        r.found = (r.bytes > 0 && r.addr != 0);
+        // M5 step 4: remember the governing 0x4b write for the scratch retarget.
+        if (m_last_addr_off != 0xFFFFFFFFu)
+          m_stats.xfb_addr_offsets.push_back(m_last_addr_off);
+      }
+      break;
+    default:
+      break;
+    }
+  }
   void OnIndexedLoad(CPArray, u32, u16, u8 size) override {
     ++m_stats.indexed;
     m_stats.indexed_bytes += u32(size) * 4u;
@@ -276,6 +414,8 @@
         std::memset(m_base + (data - m_base), 0x00, size);  // size GX_NOPs
         ++m_stats.masked;
       }
+      // M5 step 4: offset of the latest 0x4b write (governs the next XFB copy).
+      if (reg == BPMEM_EFB_ADDR) m_last_addr_off = u32(data - m_base);
     }
   }
   CPState& GetCPState() override { return m_cp; }
@@ -285,6 +425,14 @@
   CPState m_cp;
   MaskStats& m_stats;
   int m_bp_reg = -1;
+  // M5 step 2: last-seen XFB destination registers (24-bit BP values).
+  u32 m_tl = 0;
+  u32 m_wh = 0;
+  u32 m_dest = 0;
+  u32 m_stride = 0;
+  u32 m_yscale = 0;
+  // M5 step 4: offset of the latest 0x4b write in the walked stream.
+  u32 m_last_addr_off = 0xFFFFFFFFu;
 };
 static MaskStats BuildMaskedStream(const std::vector<u8>& src, const u32* cp_mem,
                                    std::vector<u8>& out) {
@@ -490,6 +638,97 @@
   // Always built (the counters are the receipt for the aux-budget arithmetic);
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
+
+  // M5 step 2: reference hash of the live XFB after the original frame, taken
+  // before the first restore. After every replay the same range is hashed
+  // again (before the next restore) and compared.
+  u64 xfb_ref = 0;
+  bool xfb_ref_ok = false;
+  if (mask.xfb.found && mask.xfb.bytes > 0) {
+    if (u8* ptr = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+      xfb_ref = RamHash(ptr, mask.xfb.bytes);
+      xfb_ref_ok = true;
+    }
+  }
+  unsigned xfb_equal_count = 0;
+
+  // M5 step 4: replay-owned XFB destination. Allocated once from the top of
+  // the recorded frame's unused guest RAM: 16-byte aligned, 0x100 guard gap
+  // above the highest byte used by any recorded RAM memory update or the live
+  // XFB, in the same address base as the live XFB, with the scratch XFB (same
+  // byte size) fitting below the RAM top. Verified with GetPointerForRange and
+  // checked for overlap with the live XFB in offset domain. The scratch lies
+  // inside the S2 whole-RAM watched window, but the sequence restores all of
+  // RAM/EXRAM afterwards, so the re-hash still verifies. Non-XFB EFB copies
+  // (copy_to_vram) keep their destinations; only the 0x4b writes governing
+  // XFB copies are retargeted, in the replay copies of both the execute and
+  // the preprocess streams (same layout, same offsets).
+  u32 xfb_scratch_addr = 0;
+  bool xfb_scratch_ok = false;
+  bool xfb_patch_bad = false;
+  unsigned xfb_patch_n = 0;
+  std::vector<u8> frame_exec = frame;
+  std::vector<u8> frame_pre_exec = frame_pre;
+  if (mask.xfb.found && mask.xfb.bytes > 0 && ram_size > 0) {
+    const u32 ram_mask = live_memory.GetRamMask();
+    const u32 xfb_off = mask.xfb.addr & ram_mask;
+    u32 top_used = xfb_off + mask.xfb.bytes;
+    for (const auto& update : file->GetFrame(0).memoryUpdates) {
+      if ((update.address & 0x10000000u) == 0) {  // RAM, not EXRAM
+        const u32 end = (update.address & ram_mask) + u32(update.data.size());
+        if (end > top_used) top_used = end;
+      }
+    }
+    const u32 base = mask.xfb.addr & ~ram_mask;
+    const u32 cand_off = (top_used + 0x100u + 15u) & ~15u;
+    if (cand_off >= top_used && cand_off + mask.xfb.bytes <= u32(ram_size)) {
+      const u32 cand = base | cand_off;
+      const bool no_overlap =
+          (cand_off + mask.xfb.bytes <= xfb_off || cand_off >= xfb_off + mask.xfb.bytes);
+      if (no_overlap && live_memory.GetPointerForRange(cand, mask.xfb.bytes) != nullptr) {
+        // Fail closed: every governing 0x4b must be a well-formed 5-byte
+        // GX_LOAD_BP_REG at the recorded offset in both copies.
+        bool patch_ok = !mask.xfb_addr_offsets.empty();
+        std::vector<u32> offs = mask.xfb_addr_offsets;
+        // Dedupe (several XFB triggers may share one governing write).
+        for (size_t i = 0; i < offs.size(); ++i)
+          for (size_t j = i + 1; j < offs.size();) {
+            if (offs[j] == offs[i])
+              offs.erase(offs.begin() + static_cast<std::vector<u32>::difference_type>(j));
+            else
+              ++j;
+          }
+        for (u32 off : offs) {
+          for (const std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
+            if (off + 5 > s->size() || (*s)[off] != 0x61 || (*s)[off + 1] != BPMEM_EFB_ADDR)
+              patch_ok = false;
+          }
+        }
+        if (patch_ok) {
+          xfb_scratch_addr = cand;
+          xfb_patch_n = unsigned(offs.size());
+          const u32 vv = cand >> 5;  // BP value domain (address >> 5)
+          for (u32 off : offs) {
+            for (std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
+              (*s)[off + 2] = u8(vv >> 16);
+              (*s)[off + 3] = u8(vv >> 8);
+              (*s)[off + 4] = u8(vv);
+            }
+          }
+          xfb_scratch_ok = true;
+        } else {
+          xfb_patch_bad = true;
+        }
+      }
+    }
+  }
+  const std::vector<u8>& exec_stream = xfb_scratch_ok ? frame_exec : frame;
+  const std::vector<u8>& pre_stream = xfb_scratch_ok ? frame_pre_exec : frame_pre;
+  unsigned xfb_scratch_count = 0;
+  unsigned live_same_count = 0;
+  unsigned live_ok_count = 0;
+  u64 live_xfb_first = 0;
+  bool live_xfb_have = false;
 
   const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
   const std::vector<u8> prelude = Prelude(file);
@@ -498,20 +737,50 @@
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
   {
-    char detail[256];
+    char detail[448];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
-                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u",
+                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
+                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
+                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
+                  "efb_total=%u xfb_patch_n=%u",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
-                  mask.unknown, mask.benign_unknown);
+                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
+                  mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
+                  xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
+                  xfb_patch_n);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
+  // M5 step 3: count after_frame_event triggers for the duration of the
+  // sequence with the header's own listener. Passive: it only increments.
+  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
+  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
+  s_after_frame_triggers = 0;
+  Common::EventHook m5_after_frame_hook =
+      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
+        ++s_after_frame_triggers;
+      });
+  const SideFx fx_base = CaptureSideFx(system);
+  // Min/max trackers over the per-replay deltas for the summary receipt.
+  long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
+  long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
+  bool fx_first = true;
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
+    // M5 step 3, fail-closed: the recorder must be idle; a replay that
+    // re-arms g_record_fifo_data would corrupt any live capture.
+    if (OpcodeDecoder::g_record_fifo_data) {
+      char rd[64];
+      std::snprintf(rd, sizeof(rd), "replay=%u", replays);
+      Event("record_flag_set", rd);
+      break;
+    }
+    const SideFx fx_before = CaptureSideFx(system);
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -526,9 +795,9 @@
     CopyPreprocessCPStateFromMain();
     VertexLoaderManager::MarkAllDirty();
     const double t_cp = Now();
-    if (deterministic) RunPre(frame_pre);
+    if (deterministic) RunPre(pre_stream);
     const double t_pre = Now();
-    Run(frame);
+    Run(exec_stream);
     if (g_gfx) {
       g_gfx->Flush();
       g_gfx->WaitForGPUIdle();
@@ -542,18 +811,104 @@
     replay_wall_ms[replays] = (wall_end - wall_start) * 1000.0;
     replay_cpu_ms[replays] =
         (cpu_start >= 0 && cpu_end >= 0) ? (cpu_end - cpu_start) : -1.0;
+    // M5 step 2: hash the XFB destination after this replay, before the next
+    // restore. Hashed after wall_end so the hash cost stays out of wall_ms.
+    int xfb_equal = 0;
+    if (xfb_ref_ok) {
+      if (u8* rp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes))
+        xfb_equal = (RamHash(rp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+    }
+    xfb_equal_count += unsigned(xfb_equal);
+    // M5 step 4: scratch compare (hash of the replay-owned region vs the live
+    // XFB after the original frame) and the live-XFB-untouched watch (the
+    // live range must read the same after every replay of the sequence).
+    int xfb_scratch_equal = 0;
+    if (xfb_scratch_ok) {
+      if (u8* sp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes))
+        xfb_scratch_equal = (RamHash(sp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+      if (u8* lp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+        const u64 live_hash = RamHash(lp, mask.xfb.bytes);
+        ++live_ok_count;
+        if (!live_xfb_have) {
+          live_xfb_have = true;
+          live_xfb_first = live_hash;
+          live_same_count = 1;
+        } else if (live_hash == live_xfb_first) {
+          ++live_same_count;
+        }
+      }
+    }
+    xfb_scratch_count += unsigned(xfb_scratch_equal);
+    // M5 step 3: after-state and deltas. Captured after wall_end so the
+    // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
+    const SideFx fx_after = CaptureSideFx(system);
+    const long long dtex =
+        static_cast<long long>(fx_after.tex_entries) - static_cast<long long>(fx_before.tex_entries);
+    const long long dpend =
+        static_cast<long long>(fx_after.pending) - static_cast<long long>(fx_before.pending);
+    const long long dframe =
+        static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
+    const long long dafter =
+        static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
+    const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    if (fx_first) {
+      min_dtex = max_dtex = dtex;
+      min_dpend = max_dpend = dpend;
+      min_dframe = max_dframe = dframe;
+      min_dafter = max_dafter = dafter;
+      min_pe = max_pe = pediff;
+      min_vi = max_vi = vidiff;
+      fx_first = false;
+    } else {
+      if (dtex < min_dtex) min_dtex = dtex;
+      if (dtex > max_dtex) max_dtex = dtex;
+      if (dpend < min_dpend) min_dpend = dpend;
+      if (dpend > max_dpend) max_dpend = dpend;
+      if (dframe < min_dframe) min_dframe = dframe;
+      if (dframe > max_dframe) max_dframe = dframe;
+      if (dafter < min_dafter) min_dafter = dafter;
+      if (dafter > max_dafter) max_dafter = dafter;
+      if (pediff < min_pe) min_pe = pediff;
+      if (pediff > max_pe) max_pe = pediff;
+      if (vidiff < min_vi) min_vi = vidiff;
+      if (vidiff > max_vi) max_vi = vidiff;
+    }
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
-                 "\"sync_ms\":%.3f,\"xform\":%d,\"render_execution\":true}\n",
+                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
+                 "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom));
+                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
+                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
+  // event. completed = capacity rows actually emitted (record_flag_set stops
+  // the sequence early, fail-closed).
+  {
+    char summary[640];
+    std::snprintf(summary, sizeof(summary),
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
+                  "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
+                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
+                  "live_ok=%u live_same=%u",
+                  replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
+                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
+                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
+                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
+                  live_ok_count, live_same_count);
+    Event("counters_summary", summary);
+  }
+  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
@@ -571,9 +926,20 @@
       RamHash(live_memory.GetRAM(), ram_size) == RamHash(saved_ram.data(), ram_size) &&
       (exram_size == 0 ||
        RamHash(live_memory.GetEXRAM(), exram_size) == RamHash(saved_exram.data(), exram_size));
-  char done_detail[64]; // whole-200 wall time on the done event.
-  std::snprintf(done_detail, sizeof(done_detail), "seq_wall_ms=%.3f",
-                (seq_end - seq_start) * 1000.0);
+  // M5 step 4: live_xfb_untouched = every sampled live XFB matched the first
+  // sample of the sequence (and every replay produced a sample).
+  const int live_xfb_untouched =
+      (xfb_scratch_ok && replays > 0 && live_ok_count == replays &&
+       live_same_count == replays)
+          ? 1
+          : 0;
+  char done_detail[288]; // whole-200 wall time + M5 XFB counts on the done event.
+  std::snprintf(done_detail, sizeof(done_detail),
+                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u "
+                "xfb_equal_scratch=%u/200 live_xfb_untouched=%d live_same=%u/%u",
+                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, mask.xfb.addr,
+                mask.xfb.bytes, xfb_scratch_count, live_xfb_untouched, live_same_count,
+                replays);
   Event(window_ok ? "done" : "watched_window_changed", done_detail);
   phase = Phase::Done;
 }
```

### Step 5

```diff
--- local/research/S2/s2_replay_capacity.h	2026-09-18 11:50:29
+++ /Volumes/Extreme SSD/m5/m5_replay_context.step5.h	2026-09-18 21:07:43
@@ -69,6 +69,24 @@
 #include "VideoCommon/AbstractGfx.h"
 #include "VideoCommon/Fifo.h"
 #include "VideoCommon/VideoConfig.h"
+// M5 step 3: side-effect counters. No public accessor exposes the
+// texture-cache entry count (m_textures_by_address) or the deferred EFB-copy
+// queue length (m_pending_efb_copies), so visibility of TextureCacheBase.h is
+// promoted header-locally for this probe TU only (the vendor tree is
+// untouched) for passive size reads. Every other counter uses public APIs:
+// g_presenter->FrameCount(), our own after_frame_event listener, PE/VI DoState
+// snapshots, OpcodeDecoder::g_record_fifo_data.
+#define M5_VIS public
+#define private M5_VIS
+#define protected M5_VIS
+#include "VideoCommon/TextureCacheBase.h"
+#undef private
+#undef protected
+#include "VideoCommon/Present.h"
+#include "VideoCommon/PixelEngine.h"
+#include "Core/HW/VideoInterface.h"
+#include "VideoCommon/VideoEvents.h"
+#include "Common/HookableEvent.h"
 #include <cstdio>
 #include <cstring>
 #include <ctime>
@@ -118,8 +136,102 @@
     hash *= 1099511628211ull;
   }
   return hash;
+}
+
+// --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
+static unsigned long long s_after_frame_triggers = 0;
+struct SideFx {
+  size_t tex_entries = 0;
+  size_t pending = 0;
+  int frame_count = -1;
+  unsigned long long after_frame = 0;
+  std::vector<u8> pe_state;
+  std::vector<u8> vi_state;
+};
+static std::vector<u8> DoStateBytes_PE(Core::System& system) {
+  std::vector<u8> buf(512, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetPixelEngine().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static std::vector<u8> DoStateBytes_VI(Core::System& system) {
+  std::vector<u8> buf(2048, 0);
+  u8* w = buf.data();
+  PointerWrap pw(&w, buf.size(), PointerWrap::Mode::Write);
+  system.GetVideoInterface().DoState(pw);
+  buf.resize(size_t(w - buf.data()));
+  return buf;
+}
+static SideFx CaptureSideFx(Core::System& system) {
+  SideFx s;
+  if (g_texture_cache) {
+    s.tex_entries = g_texture_cache->m_textures_by_address.size();
+    s.pending = g_texture_cache->m_pending_efb_copies.size();
+  }
+  if (g_presenter) s.frame_count = g_presenter->FrameCount();
+  s.after_frame = s_after_frame_triggers;
+  s.pe_state = DoStateBytes_PE(system);
+  s.vi_state = DoStateBytes_VI(system);
+  return s;
+}
+static unsigned DiffBytes(const std::vector<u8>& a, const std::vector<u8>& b) {
+  unsigned n = 0;
+  const size_t len = a.size() > b.size() ? a.size() : b.size();
+  for (size_t i = 0; i < len; ++i) {
+    const u8 x = i < a.size() ? a[i] : 0;
+    const u8 y = i < b.size() ? b[i] : 0;
+    if (x != y) ++n;
+  }
+  return n;
 }
 
+// --- M5 step 5: continuation check ------------------------------------------
+// After the sequence and the S2 restore, capture the first live XFB copy
+// after resume with a one-shot after_frame listener: range from the live BP
+// registers, hashed from guest RAM. The same capture arms in the
+// sequence-disabled run (SSX_NATIVE_REPLAY=0) at its seam marker, so the
+// report can compare the two runs when they reach the seam at the same frame
+// (record_start fc equal); otherwise it says so and skips.
+static void Event(const char* action, const char* detail);
+static Common::EventHook s_resume_hook;
+static void ArmResumeXfbCapture(Core::System& system, int disabled) {
+  if (s_resume_hook) s_resume_hook.reset();
+  s_resume_hook = system.GetVideoEvents().after_frame_event.Register(
+      [disabled](Core::System& sys) {
+        const u32 hsrc = bpmem.copyTexSrcWH.y;
+        const bool invert = bpmem.triggerEFBCopy.scale_invert;
+        float yscale = 1.0f;
+        if (bpmem.dispcopyyscale != 0) {
+          yscale = invert ? (256.0f / float(bpmem.dispcopyyscale))
+                          : (float(bpmem.dispcopyyscale) / 256.0f);
+        }
+        const u32 h = u32(1.0f + float(hsrc) * yscale);
+        const u32 addr = bpmem.copyTexDest << 5;
+        const u32 stride = bpmem.copyDestStride << 5;
+        const u32 bytes = h * stride;
+        u64 hash = 0;
+        bool ok = false;
+        if (bytes > 0) {
+          if (u8* ptr = sys.GetMemory().GetPointerForRange(addr, bytes)) {
+            hash = RamHash(ptr, bytes);
+            ok = true;
+          }
+        }
+        int fc = -1;
+        if (g_presenter) fc = g_presenter->FrameCount();
+        char d[224];
+        std::snprintf(d, sizeof(d),
+                      "replay_disabled=%d fc=%d ok=%d xfb_addr=0x%08x xfb_bytes=%u "
+                      "xfb_hash=%016llx",
+                      disabled, fc, int(ok), addr, bytes,
+                      static_cast<unsigned long long>(hash));
+        Event("resume_xfb", d);
+        s_resume_hook.reset();
+      });
+}
+
 // Command bytes that restore the recorded initial BP/CP/XF state, mirroring
 // FifoPlayer::LoadRegisters (same register exclusions), so draw command sizes
 // and matrices decode as they did when the frame was recorded.
@@ -229,6 +341,24 @@
 // preprocess BP handler acts on into five GX_NOPs. Byte length is unchanged,
 // no aux-buffer command is touched, so the preprocess and execute passes still
 // push and pop the same aux payload in the same order.
+// --- M5 step 2: XFB fidelity -------------------------------------------------
+//
+// The same mask walk also decodes the recorded frame's XFB copy destination:
+// the EFB-copy BP write (BPMEM_TRIGGER_EFB_COPY 0x52 with the XFB bit, bit 14)
+// and the live destination (BPMEM_EFB_ADDR 0x4b), stride (0x4d) and copy
+// rectangle (0x49/0x4a, X10Y10) plus y-scale (0x4e) at that trigger. The byte
+// range mirrors TextureCacheBase::CopyRenderTargetToTexture for the XFB format
+// (block 16x1, 32 bytes/block): bytes_per_row = AlignUp(width,16)/16*32,
+// covered = height * stride with height = 1 + WH.y * yScale as in BPStructs.
+struct XfbRange {
+  bool found = false;
+  u32 copies = 0;   // XFB-copy triggers seen in the recorded stream
+  u32 addr = 0;     // guest byte address (copyTexDest << 5)
+  u32 stride = 0;   // bytes per row (copyDestStride << 5)
+  u32 width = 0;    // copyTexSrcWH.x + 1
+  u32 height = 0;   // 1 + copyTexSrcWH.y * yScale
+  u32 bytes = 0;    // height * stride
+};
 struct MaskStats {
   u32 consumed = 0;
   u32 masked = 0;
@@ -238,6 +368,13 @@
   u32 dl_bytes = 0;
   u32 benign_unknown = 0;  // 0x44 / 0x48: known, ignored, 1 byte (see OnUnknown)
   u32 unknown = 0;
+  XfbRange xfb;
+  // M5 step 4: stream offsets of the BPMEM_EFB_ADDR writes governing each XFB
+  // copy (for the replay-owned scratch retarget).
+  std::vector<u32> xfb_addr_offsets;
+  // M5 step 4 recount: every EFB-copy trigger (XFB or not). Non-XFB copies
+  // keep their destinations; non-XFB count = efb_copies_total - xfb.copies.
+  u32 efb_copies_total = 0;
 };
 class PeMaskWalk final : public OpcodeDecoder::Callback {
 public:
@@ -245,7 +382,53 @@
       : m_base(base), m_cp(cp_mem), m_stats(stats) {}
   void OnXF(u16, u8, const u8*) override {}
   void OnCP(u8 command, u32 value) override { m_cp.LoadCPReg(command, value); }
-  void OnBP(u8 command, u32) override { m_bp_reg = int(command); }
+  void OnBP(u8 command, u32 value) override {
+    m_bp_reg = int(command);
+    // M5 step 2: track the XFB-copy destination registers live at each XFB trigger.
+    switch (command) {
+    case BPMEM_EFB_TL:
+      m_tl = value;
+      break;
+    case BPMEM_EFB_WH:
+      m_wh = value;
+      break;
+    case BPMEM_EFB_ADDR:
+      m_dest = value;
+      break;
+    case BPMEM_EFB_STRIDE:
+      m_stride = value;
+      break;
+    case BPMEM_COPYYSCALE:
+      m_yscale = value;
+      break;
+    case BPMEM_TRIGGER_EFB_COPY:
+      ++m_stats.efb_copies_total;
+      if ((value >> 14) & 1u) {  // UPE_Copy::copy_to_xfb
+        XfbRange& r = m_stats.xfb;
+        ++r.copies;
+        const u32 w = (m_wh & 0x3ffu) + 1u;
+        const u32 hsrc = (m_wh >> 10) & 0x3ffu;
+        const bool invert = ((value >> 10) & 1u) != 0;  // UPE_Copy::scale_invert
+        float yscale = 1.0f;
+        if (m_yscale != 0)
+          yscale = invert ? (256.0f / float(m_yscale)) : (float(m_yscale) / 256.0f);
+        // m_yscale == 0 keeps yscale == 1.0f (fallback; real frames set 0x4e).
+        const u32 h = u32(1.0f + float(hsrc) * yscale);
+        r.addr = m_dest << 5;
+        r.stride = m_stride << 5;
+        r.width = w;
+        r.height = h;
+        r.bytes = h * r.stride;
+        r.found = (r.bytes > 0 && r.addr != 0);
+        // M5 step 4: remember the governing 0x4b write for the scratch retarget.
+        if (m_last_addr_off != 0xFFFFFFFFu)
+          m_stats.xfb_addr_offsets.push_back(m_last_addr_off);
+      }
+      break;
+    default:
+      break;
+    }
+  }
   void OnIndexedLoad(CPArray, u32, u16, u8 size) override {
     ++m_stats.indexed;
     m_stats.indexed_bytes += u32(size) * 4u;
@@ -276,6 +459,8 @@
         std::memset(m_base + (data - m_base), 0x00, size);  // size GX_NOPs
         ++m_stats.masked;
       }
+      // M5 step 4: offset of the latest 0x4b write (governs the next XFB copy).
+      if (reg == BPMEM_EFB_ADDR) m_last_addr_off = u32(data - m_base);
     }
   }
   CPState& GetCPState() override { return m_cp; }
@@ -285,6 +470,14 @@
   CPState m_cp;
   MaskStats& m_stats;
   int m_bp_reg = -1;
+  // M5 step 2: last-seen XFB destination registers (24-bit BP values).
+  u32 m_tl = 0;
+  u32 m_wh = 0;
+  u32 m_dest = 0;
+  u32 m_stride = 0;
+  u32 m_yscale = 0;
+  // M5 step 4: offset of the latest 0x4b write in the walked stream.
+  u32 m_last_addr_off = 0xFFFFFFFFu;
 };
 static MaskStats BuildMaskedStream(const std::vector<u8>& src, const u32* cp_mem,
                                    std::vector<u8>& out) {
@@ -394,6 +587,23 @@
 static inline void Step(CPUState& c) {
   NativeSchedule::Step(c);
   RefreshNow(c);
+  // M5 step 5: sequence-disabled run (SSX_NATIVE_REPLAY=0). At the same idle
+  // seam, emit a one-shot seam marker and arm the resume-XFB capture so the
+  // report can compare it against the sequence run. No recording, no replay.
+  if (!Enabled() && Output() && phase == Phase::Idle) {
+    if (c.pc == 0x801cad24 && c.lr == 0x801cd724 && !render.pending && !update.pending &&
+        D2Window() && !DoubleEnabled() && !WaitEnabled() && !SweepEnabled()) {
+      auto& dis_system = Core::System::GetInstance();
+      int fc = -1;
+      if (g_presenter) fc = g_presenter->FrameCount();
+      char d[96];
+      std::snprintf(d, sizeof(d), "replay_disabled=1 fc=%d", fc);
+      Event("record_start", d);
+      ArmResumeXfbCapture(dis_system, 1);
+      phase = Phase::Done;
+    }
+    return;
+  }
   if (!Enabled() || !Output() || phase == Phase::Done) return;
   if (c.pc != 0x801cad24 || c.lr != 0x801cd724 || render.pending || update.pending) return;
   if (!D2Window()) return;
@@ -424,7 +634,15 @@
     recorder.StartRecording(1, [] {});
     record_wall = Now();
     phase = Phase::Recording;
-    Event("record_start");
+    {
+      // M5 step 5: seam id (presenter frame count) for the continuation
+      // comparison between the sequence run and the sequence-disabled run.
+      int fc = -1;
+      if (g_presenter) fc = g_presenter->FrameCount();
+      char d[64];
+      std::snprintf(d, sizeof(d), "fc=%d", fc);
+      Event("record_start", d);
+    }
     return;
   }
   if (phase == Phase::Recording) {
@@ -491,6 +709,97 @@
   // frame_pre is only executed when the deterministic path is active.
   const MaskStats mask = BuildMaskedStream(frame, file->GetCPMem(), frame_pre);
 
+  // M5 step 2: reference hash of the live XFB after the original frame, taken
+  // before the first restore. After every replay the same range is hashed
+  // again (before the next restore) and compared.
+  u64 xfb_ref = 0;
+  bool xfb_ref_ok = false;
+  if (mask.xfb.found && mask.xfb.bytes > 0) {
+    if (u8* ptr = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+      xfb_ref = RamHash(ptr, mask.xfb.bytes);
+      xfb_ref_ok = true;
+    }
+  }
+  unsigned xfb_equal_count = 0;
+
+  // M5 step 4: replay-owned XFB destination. Allocated once from the top of
+  // the recorded frame's unused guest RAM: 16-byte aligned, 0x100 guard gap
+  // above the highest byte used by any recorded RAM memory update or the live
+  // XFB, in the same address base as the live XFB, with the scratch XFB (same
+  // byte size) fitting below the RAM top. Verified with GetPointerForRange and
+  // checked for overlap with the live XFB in offset domain. The scratch lies
+  // inside the S2 whole-RAM watched window, but the sequence restores all of
+  // RAM/EXRAM afterwards, so the re-hash still verifies. Non-XFB EFB copies
+  // (copy_to_vram) keep their destinations; only the 0x4b writes governing
+  // XFB copies are retargeted, in the replay copies of both the execute and
+  // the preprocess streams (same layout, same offsets).
+  u32 xfb_scratch_addr = 0;
+  bool xfb_scratch_ok = false;
+  bool xfb_patch_bad = false;
+  unsigned xfb_patch_n = 0;
+  std::vector<u8> frame_exec = frame;
+  std::vector<u8> frame_pre_exec = frame_pre;
+  if (mask.xfb.found && mask.xfb.bytes > 0 && ram_size > 0) {
+    const u32 ram_mask = live_memory.GetRamMask();
+    const u32 xfb_off = mask.xfb.addr & ram_mask;
+    u32 top_used = xfb_off + mask.xfb.bytes;
+    for (const auto& update : file->GetFrame(0).memoryUpdates) {
+      if ((update.address & 0x10000000u) == 0) {  // RAM, not EXRAM
+        const u32 end = (update.address & ram_mask) + u32(update.data.size());
+        if (end > top_used) top_used = end;
+      }
+    }
+    const u32 base = mask.xfb.addr & ~ram_mask;
+    const u32 cand_off = (top_used + 0x100u + 15u) & ~15u;
+    if (cand_off >= top_used && cand_off + mask.xfb.bytes <= u32(ram_size)) {
+      const u32 cand = base | cand_off;
+      const bool no_overlap =
+          (cand_off + mask.xfb.bytes <= xfb_off || cand_off >= xfb_off + mask.xfb.bytes);
+      if (no_overlap && live_memory.GetPointerForRange(cand, mask.xfb.bytes) != nullptr) {
+        // Fail closed: every governing 0x4b must be a well-formed 5-byte
+        // GX_LOAD_BP_REG at the recorded offset in both copies.
+        bool patch_ok = !mask.xfb_addr_offsets.empty();
+        std::vector<u32> offs = mask.xfb_addr_offsets;
+        // Dedupe (several XFB triggers may share one governing write).
+        for (size_t i = 0; i < offs.size(); ++i)
+          for (size_t j = i + 1; j < offs.size();) {
+            if (offs[j] == offs[i])
+              offs.erase(offs.begin() + static_cast<std::vector<u32>::difference_type>(j));
+            else
+              ++j;
+          }
+        for (u32 off : offs) {
+          for (const std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
+            if (off + 5 > s->size() || (*s)[off] != 0x61 || (*s)[off + 1] != BPMEM_EFB_ADDR)
+              patch_ok = false;
+          }
+        }
+        if (patch_ok) {
+          xfb_scratch_addr = cand;
+          xfb_patch_n = unsigned(offs.size());
+          const u32 vv = cand >> 5;  // BP value domain (address >> 5)
+          for (u32 off : offs) {
+            for (std::vector<u8>* s : {&frame_exec, &frame_pre_exec}) {
+              (*s)[off + 2] = u8(vv >> 16);
+              (*s)[off + 3] = u8(vv >> 8);
+              (*s)[off + 4] = u8(vv);
+            }
+          }
+          xfb_scratch_ok = true;
+        } else {
+          xfb_patch_bad = true;
+        }
+      }
+    }
+  }
+  const std::vector<u8>& exec_stream = xfb_scratch_ok ? frame_exec : frame;
+  const std::vector<u8>& pre_stream = xfb_scratch_ok ? frame_pre_exec : frame_pre;
+  unsigned xfb_scratch_count = 0;
+  unsigned live_same_count = 0;
+  unsigned live_ok_count = 0;
+  u64 live_xfb_first = 0;
+  bool live_xfb_have = false;
+
   const std::vector<u8> cp_prelude = CpXfPreludeFrom(file->GetCPMem(), file->GetXFRegs());
   const std::vector<u8> prelude = Prelude(file);
   ApplyMemory(system, file);
@@ -498,20 +807,50 @@
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
   {
-    char detail[256];
+    char detail[448];
     std::snprintf(detail, sizeof(detail),
                   "det=%d dual=%d mask_bp=%u dls=%u dl_bytes=%u indexed=%u "
-                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u",
+                  "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
+                  "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
+                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
+                  "efb_total=%u xfb_patch_n=%u",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
-                  mask.unknown, mask.benign_unknown);
+                  mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
+                  mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
+                  xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
+                  xfb_patch_n);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
+  // M5 step 3: count after_frame_event triggers for the duration of the
+  // sequence with the header's own listener. Passive: it only increments.
+  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
+  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
+  s_after_frame_triggers = 0;
+  Common::EventHook m5_after_frame_hook =
+      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
+        ++s_after_frame_triggers;
+      });
+  const SideFx fx_base = CaptureSideFx(system);
+  // Min/max trackers over the per-replay deltas for the summary receipt.
+  long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
+  long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
+  bool fx_first = true;
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
+    // M5 step 3, fail-closed: the recorder must be idle; a replay that
+    // re-arms g_record_fifo_data would corrupt any live capture.
+    if (OpcodeDecoder::g_record_fifo_data) {
+      char rd[64];
+      std::snprintf(rd, sizeof(rd), "replay=%u", replays);
+      Event("record_flag_set", rd);
+      break;
+    }
+    const SideFx fx_before = CaptureSideFx(system);
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -526,9 +865,9 @@
     CopyPreprocessCPStateFromMain();
     VertexLoaderManager::MarkAllDirty();
     const double t_cp = Now();
-    if (deterministic) RunPre(frame_pre);
+    if (deterministic) RunPre(pre_stream);
     const double t_pre = Now();
-    Run(frame);
+    Run(exec_stream);
     if (g_gfx) {
       g_gfx->Flush();
       g_gfx->WaitForGPUIdle();
@@ -542,18 +881,104 @@
     replay_wall_ms[replays] = (wall_end - wall_start) * 1000.0;
     replay_cpu_ms[replays] =
         (cpu_start >= 0 && cpu_end >= 0) ? (cpu_end - cpu_start) : -1.0;
+    // M5 step 2: hash the XFB destination after this replay, before the next
+    // restore. Hashed after wall_end so the hash cost stays out of wall_ms.
+    int xfb_equal = 0;
+    if (xfb_ref_ok) {
+      if (u8* rp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes))
+        xfb_equal = (RamHash(rp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+    }
+    xfb_equal_count += unsigned(xfb_equal);
+    // M5 step 4: scratch compare (hash of the replay-owned region vs the live
+    // XFB after the original frame) and the live-XFB-untouched watch (the
+    // live range must read the same after every replay of the sequence).
+    int xfb_scratch_equal = 0;
+    if (xfb_scratch_ok) {
+      if (u8* sp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes))
+        xfb_scratch_equal = (RamHash(sp, mask.xfb.bytes) == xfb_ref) ? 1 : 0;
+      if (u8* lp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes)) {
+        const u64 live_hash = RamHash(lp, mask.xfb.bytes);
+        ++live_ok_count;
+        if (!live_xfb_have) {
+          live_xfb_have = true;
+          live_xfb_first = live_hash;
+          live_same_count = 1;
+        } else if (live_hash == live_xfb_first) {
+          ++live_same_count;
+        }
+      }
+    }
+    xfb_scratch_count += unsigned(xfb_scratch_equal);
+    // M5 step 3: after-state and deltas. Captured after wall_end so the
+    // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
+    const SideFx fx_after = CaptureSideFx(system);
+    const long long dtex =
+        static_cast<long long>(fx_after.tex_entries) - static_cast<long long>(fx_before.tex_entries);
+    const long long dpend =
+        static_cast<long long>(fx_after.pending) - static_cast<long long>(fx_before.pending);
+    const long long dframe =
+        static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
+    const long long dafter =
+        static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
+    const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    if (fx_first) {
+      min_dtex = max_dtex = dtex;
+      min_dpend = max_dpend = dpend;
+      min_dframe = max_dframe = dframe;
+      min_dafter = max_dafter = dafter;
+      min_pe = max_pe = pediff;
+      min_vi = max_vi = vidiff;
+      fx_first = false;
+    } else {
+      if (dtex < min_dtex) min_dtex = dtex;
+      if (dtex > max_dtex) max_dtex = dtex;
+      if (dpend < min_dpend) min_dpend = dpend;
+      if (dpend > max_dpend) max_dpend = dpend;
+      if (dframe < min_dframe) min_dframe = dframe;
+      if (dframe > max_dframe) max_dframe = dframe;
+      if (dafter < min_dafter) min_dafter = dafter;
+      if (dafter > max_dafter) max_dafter = dafter;
+      if (pediff < min_pe) min_pe = pediff;
+      if (pediff > max_pe) max_pe = pediff;
+      if (vidiff < min_vi) min_vi = vidiff;
+      if (vidiff > max_vi) max_vi = vidiff;
+    }
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
-                 "\"sync_ms\":%.3f,\"xform\":%d,\"render_execution\":true}\n",
+                 "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
+                 "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom));
+                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
+                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
+  // event. completed = capacity rows actually emitted (record_flag_set stops
+  // the sequence early, fail-closed).
+  {
+    char summary[640];
+    std::snprintf(summary, sizeof(summary),
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
+                  "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
+                  "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
+                  "live_ok=%u live_same=%u",
+                  replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
+                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
+                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
+                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
+                  live_ok_count, live_same_count);
+    Event("counters_summary", summary);
+  }
+  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
@@ -571,10 +996,24 @@
       RamHash(live_memory.GetRAM(), ram_size) == RamHash(saved_ram.data(), ram_size) &&
       (exram_size == 0 ||
        RamHash(live_memory.GetEXRAM(), exram_size) == RamHash(saved_exram.data(), exram_size));
-  char done_detail[64]; // whole-200 wall time on the done event.
-  std::snprintf(done_detail, sizeof(done_detail), "seq_wall_ms=%.3f",
-                (seq_end - seq_start) * 1000.0);
+  // M5 step 4: live_xfb_untouched = every sampled live XFB matched the first
+  // sample of the sequence (and every replay produced a sample).
+  const int live_xfb_untouched =
+      (xfb_scratch_ok && replays > 0 && live_ok_count == replays &&
+       live_same_count == replays)
+          ? 1
+          : 0;
+  char done_detail[288]; // whole-200 wall time + M5 XFB counts on the done event.
+  std::snprintf(done_detail, sizeof(done_detail),
+                "seq_wall_ms=%.3f completed=%u xfb_equal=%u/200 xfb_addr=0x%08x xfb_bytes=%u "
+                "xfb_equal_scratch=%u/200 live_xfb_untouched=%d live_same=%u/%u",
+                (seq_end - seq_start) * 1000.0, replays, xfb_equal_count, mask.xfb.addr,
+                mask.xfb.bytes, xfb_scratch_count, live_xfb_untouched, live_same_count,
+                replays);
   Event(window_ok ? "done" : "watched_window_changed", done_detail);
+  // M5 step 5: arm the first-live-XFB-after-resume capture. The existing
+  // watched-window re-hash + done above remain the receipt.
+  ArmResumeXfbCapture(system, 0);
   phase = Phase::Done;
 }
 } // namespace NativeReplay
```
