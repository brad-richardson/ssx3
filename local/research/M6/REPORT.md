# M6 — Host replay milestone 2, item 2: REPORT

Event-bus split + frame-aging + record guard, desktop only. Runbook `local/muse/prompts/M6.md`.
No `adb`, no device. No verdicts.

Header read first: `local/research/M5/REPORT.md` (all of it: step tables, the
`dframe` +1 mystery, the skipped continuation, "What I could not do") and
`local/research/S2/REPORT.md` Part 4 (§A–§E inventory and "What a
ReplayContext still has to own" items 2–4).

Time box 6 hours; used about 1.2 before the battery hold plus about 0.5
for the post-release negative-control run and final write.

## Baseline note (read before the tables)

The M5 header on disk (`local/research/M5/m5_replay_context.h`, clean tree)
hashes to `ffea482536be95578ad87611c6ce4ce3fee75a9814a96ee9a722efdf408ee5ed`
via `shasum -a 256` (trust `shasum`, not memory; the M5 brief pinned a stale
S2 sha). Step 1
copied the on-disk file verbatim to `local/research/M6/m6_replay_context.h`;
`diff -u` between them is empty (§Header diffs, step 1). Every M5 mechanism is
kept in all four steps: PE mask, verbatim execute stream, restore, stall, pipe
snapshot, watched-window re-hash, `done`, XFB hash + scratch redirect,
side-effect counters, continuation capture.

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M5. `m6-det` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile directories must
be fresh per run, so the configuration ran under profiles `m6-det`, `m6-det2` …
`m6-det5`. No step orders an `m6-single` run; none was run.
Each desktop run held `/tmp/ssx3-host-lease` (`printf 'M6\n'`, removed after each
run); waits, holds and the battery hold are in `local/research/M6/waits.log`.
Builds ran any time.

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `ffea4825…` (= M5 on disk) | `players/m6-baseline` | `m6-baseline-run` (`m6-det`) | `m6-baseline-probe.jsonl` |
| 2 suppression | `b2e73714…` | `players/m6-suppress` | `m6-suppress-run` (`m6-det2`) | `m6-suppress-probe.jsonl` |
| 3 aging | `f7b8dbb1…` | `players/m6-aging` | `m6-aging-run` (`m6-det3`) | `m6-aging-probe.jsonl` |
| 4 guard | `e89ca9b8…` | `players/m6-guard` | `m6-guard-run` (`m6-det4`) | `m6-guard-probe.jsonl` |
| 4 negctrl | `e89ca9b8…` | `players/m6-guard` | `m6-negctrl-run` (`m6-det5`, `SSX_M6_ARM_RECORD=1`) | `m6-negctrl-probe.jsonl` |

The committed header is `e89ca9b8…` (step 4). Steps 1–3 ran before the battery
hold; the step-4 guard run was in flight when the hold landed (finished
normally); the negative control ran after release on AC power (see waits.log).

Player dirs live under `local/research/M6/players/` (the build driver requires
outputs under `local/`; they are gitignored build outputs, never committed).
Run dirs and every probe jsonl (>5 MB, ~20 MB each) live under
`/Volumes/Extreme SSD/m6/` (symlink-free; `realpath` is the path as written).
Probes, runs and players are not committed.

## Step 1 — baseline (control)

Unmodified copy. `analyze.py` prints 200 rows + `done` +
`xfb_equal_scratch=200/200` + `live_xfb_untouched=1` (M5's end state
reproduced). Control for every later step.

## Per-step wall table (baseline vs each step)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m6-baseline | 200 | 6.884 / 14.343 / 3.887 / 18.470 | 2.987 / 3.499 | 331082 / 2882 | YES | seq_wall_ms=2174.628 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m6-suppress | 200 | 2.427 / 3.678 / 2.134 / 8.637 | 1.320 / 1.529 | 273688 / 2456 | YES | seq_wall_ms=863.782 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m6-aging | 200 | 2.918 / 3.751 / 2.487 / 6.079 | 1.665 / 1.834 | 318412 / 2774 | YES | seq_wall_ms=934.200 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m6-guard | 200 | 2.840 / 4.307 / 2.427 / 5.662 | 1.664 / 1.789 | 341813 / 2827 | YES | seq_wall_ms=932.892 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m6-negctrl | 0 | n/a / n/a / n/a / n/a | n/a / n/a | 321645 / 2818 | YES | seq_wall_ms=0.003 completed=0 xfb_equal=0/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=0 live_same=0/0 |
```

Frames differ per run (273688 … 341813 B), so wall medians are not comparable
across rows as mechanism costs (M5 §Per-step wall table). The four guard-run
rows: 200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2 dls=0
walk=100% unknown=0 benign=1` in all runs. The negctrl row: 0 rows by
design (guard stop), `done` still stands, same `restored` shape
(`det=1 dual=1 mask_bp=2 dls=0 walk=100% unknown=0 benign=1`).

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m6-baseline | 0.239 | 0.001 | 0.050 | 6.530 | 0.000 | 14.053 |
| m6-suppress | 0.096 | 0.001 | 0.023 | 2.298 | 0.001 | 3.555 |
| m6-aging | 0.110 | 0.001 | 0.028 | 2.778 | 0.000 | 3.592 |
| m6-guard | 0.103 | 0.001 | 0.029 | 2.710 | 0.000 | 4.158 |
| m6-negctrl | n/a | n/a | n/a | n/a | n/a | n/a |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m6-baseline | 1678 | 80544 | 26.0 |
| m6-suppress | 1040 | 49920 | 42.0 |
| m6-aging | 1542 | 74016 | 28.3 |
| m6-guard | 1119 | 53712 | 39.0 |
| m6-negctrl | 1600 | 76800 | 27.3 |

## Step 2 — scoped `after_frame_event` suppression

Mechanism: scoped bus. `HookableEvent` exposes only `Register`/`Trigger`
publicly (live handles are subscriber-owned; no unregister-other, no gate flag
at either Trigger site), but `VideoEvents::after_frame_event` is a public
member and `HookableEvent` is copyable/assignable through implicit public
special members with the copy sharing listener storage. The sequence saves the
live bus by copy, move-assigns a fresh bus into the member, registers the
header counter on the scoped bus and a sentinel on the saved bus, and restores
by copy-assignment after the sequence (normal and `record_flag_set`-break
paths). Both Trigger sites resolve the member fresh per call and no subsystem
caches a reference (all 16 vendor-tree uses are `Register`/`Trigger` on a
fresh `GetVideoEvents()` expression). No vendor change, no visibility trick.
The live listener set is 12 `Register` sites (S2 §C's 7 plus FifoRecorder,
VideoConfig, CustomResourceManager, CustomShaderCache, GraphicsModManager).

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m6-suppress | dtex | 0 | 1 |
| m6-suppress | dpend | 0 | 0 |
| m6-suppress | dframe | 0 | 0 |
| m6-suppress | dafter | 1 | 1 |
| m6-suppress | dafter_live | 0 | 0 |
| m6-suppress | pediff | 0 | 0 |
| m6-suppress | vidiff | 0 | 0 |
```

Sequence-entry/end absolutes (`counters_summary tex0/texN/pend0/pendN/fc0/fcN`):
tex 86→87, pend 0→0, fc 6338→6338. `completed=200`. `done` stands,
`xfb_equal_scratch=200/200`, `live_xfb_untouched=1`. The continuation
`resume_xfb` listener (armed on the restored live bus after the sequence)
fired normally.

Recorded without verdict: per-replay `dafter_live=0` (live listeners never
fired) while the header counter still counts every trigger (`dafter=1`);
`dframe` 0/0 during the sequence (was +1/+1 unsuppressed); `dpend` 0/0 with
`pendN=0` (the deferred queue does not grow — the in-stream SETDRAWDONE /
PE_TOKEN flush points in the verbatim execute stream still drain per replay);
`dtex` 0/+1 with net +1 over 200 replays (eviction frozen — never negative —
vs M5's −7…+1 per-replay removals).

## Step 3 — frame-aging semantics + the +1 driver

`FrameCount()` frozen during the suppressed sequence (receipt: `dframe=0` per
replay, `fc0=fcN=6390`); replay-local frame counter `m6frame` in its place
(1…200 monotonic, one count per emitted capacity row). `g_ActiveConfig`
sampled per replay (`dimx=0/0`, `imx0=imxN=0`: the flag stays false
throughout). Presenter tracing (`before_present_event` in all paths,
`after_present_event` in non-skipped presents, reason split):

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m6-aging | dtex | 0 | 1 |
| m6-aging | dpend | 0 | 0 |
| m6-aging | dframe | 0 | 0 |
| m6-aging | dafter | 1 | 1 |
| m6-aging | dafter_live | 0 | 0 |
| m6-aging | dpres | 0 | 0 |
| m6-aging | dimx | 0 | 0 |
| m6-aging | pediff | 0 | 0 |
| m6-aging | vidiff | 0 | 0 |
```

`present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0
seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0 first_imm_pc=12775
first_imm_fc=6387` (pre = live window record_start→sequence; the 3 live
Immediate presents are the tracer's positive control; first matches the
`record_start` seam `fc=6387`). `done` stands,
`xfb_equal_scratch=200/200`, `live_xfb_untouched=1`.
Sequence absolutes: tex 99→100, pend 0→0, fc 6390→6390, `completed=200`.

The +1 driver (M5's unresolved `dframe` +1/replay), named with file:line +
trigger: `Presenter::ImmediateSwap` (`Present.cpp:235`, `m_frame_count++`),
called from the XFB-copy present branch (`BPStructs.cpp:364`), re-armed every
replay by the `VideoConfig::CheckForConfigChanges` after_frame listener
(registered `VideoConfig.cpp:231`; body `:293` calls `UpdateActiveConfig()`
`:313`, which does `g_ActiveConfig = g_Config` `:50–54`, restoring
`bImmediateXFB=true` from the config layer). The listener runs inside the
`after_frame_event` Trigger (`BPStructs.cpp:353`); the present-branch flag
check (`BPStructs.cpp:361`) comes after the Trigger in program order, so the
same replay's XFB copy presents. Exact +1 × 200 from replay 0,
content-independent (survives the scratch redirect) and wall-clock-free —
every M5 observation fits. Enumeration over the 12 suppressed listeners: only
the config-refresh listener can reach `m_frame_count`; the other 11 touch no
presenter state.

Ruled out: the `ViSwap` path (`VideoBackendBase.cpp:110` via `AsyncRequests`,
needs VI-timing `Video_OutputXFB` calls — frozen with the guest parked; stale
queue drains are excluded by `PauseAndLock` stalling the pulling video thread,
and no `VideoInterface`-reason present was traced live either, `pre_vi=0`);
duplicate presents (`pre_dup=0`, `seq_dup=0`); the `DoState` Trigger
(`Present.cpp:1050`, read-mode only, never taken in-sequence); XFB-content
change (M5's scratch redirect already refuted it).

Evidence-status note (one line): the naming rests on the cited code path plus
elimination (suppressed runs: flag false throughout, zero presents,
`dframe=0`; unsuppressed M5 runs: `dframe=+1` × 200). No
unsuppressed-with-tracing run directly observed the mid-Trigger flag flip (one
run per step; none ordered it).

## Step 4 — fail-closed `g_record_fifo_data` guard

The M5 loop-top check is kept (sample before every replay; on true emit
`record_flag_set` and stop the sequence). Negative control:
`SSX_M6_ARM_RECORD=1` arms the sampled flag before replay 0 through the
public global (no vendor change), restored to false after the sequence.
`FifoRecorder::StartRecording` was considered and rejected for the arming: its
listener sets the flag from `IsRecording()` on the next after_frame trigger,
which under suppression never reaches the live bus — the flag itself is the
guard's sampled condition and the exact hazard (gates `WriteGPCommand` /
`UseMemory`). The `record_flag_set` detail carries `armed=%d`.

Main guard run (unarmed): no `record_flag_set` event; 200/200 rows, `done`,
`xfb_equal_scratch=200/200`, `live_xfb_untouched=1`; all step-2/3 receipts
preserved (`dafter_live` 0/0, `dframe` 0/0, `dpres` 0/0, `dimx` 0/0, `dpend`
0/0, `dtex` 0/+1, `pediff`/`vidiff` 0/0). Sequence absolutes: tex 100→101,
pend 0→0, fc 7534→7534, imx 0→0, `completed=200`. `present_trace`:
`pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0 seq_before=0
seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0 first_imm_pc=15063 first_imm_fc=7531`
(step-3 tracing replicates: live Immediate presents pre-sequence, zero
in-sequence).

Negative-control run (`SSX_M6_ARM_RECORD=1`, profile `m6-det5`, post-release
on AC power). The analyzer printed `RECORD_FLAG_SET (sequence stopped
early)`; event list: `record_start recorded gpu_stall pipe_saved restored
record_flag_set present_trace counters_summary done resume_xfb`. `restored`
detail: `det=1 dual=1 mask_bp=2 dls=0 dl_bytes=0 indexed=1600 aux_bytes=76800
walk=321645/321645 unknown=0 benign=1 xfb_copies=1 xfb_addr=0x004dc660
xfb_bytes=573440 xfb_ref_ok=1 xfb_scratch_ok=1 xfb_scratch_addr=0x016300c0
xfb_patch_bad=0 efb_total=7 xfb_patch_n=1`. `present_trace`:
`pre_before=3 pre_after=3 pre_imm=3 pre_vi=0 pre_dup=0 seq_before=0
seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0 first_imm_pc=15459 first_imm_fc=7729`
(step-3 tracing replicates a third time: live Immediate presents
pre-sequence, zero in-sequence).

| Field | Analyzer source | Value |
| --- | --- | --- |
| `record_flag_set` detail | probe action (`wall=140.082910 replay=0`) | `replay=0 armed=1` |
| capacity rows emitted | wall table `Replays` (`grep -c`) | 0 |
| `counters_summary` | `completed=` | `completed=0 tex0=102 pend0=0 fc0=7732 texN=102 pendN=0 fcN=7732 imx0=0 imxN=0` (all delta mins/maxes 0; `xfb_scratch_equal=0 live_ok=0 live_same=0`) |
| `done` detail | seq-wall column | `seq_wall_ms=0.003 completed=0 xfb_equal=0/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=0/200 live_xfb_untouched=0 live_same=0/0` |
| `resume_xfb` detail | continuation row | `replay_disabled=0 fc=7732 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Recorded without verdict: the guard fired on the loop-top sample before
replay 0 (`replay=0 armed=1`) and the sequence stopped with 0 capacity rows;
`done` still stands (`completed=0` in its detail); the scoped bus was
restored and the flag disarmed on the break path (the continuation
`resume_xfb` listener fired normally with the run's fifth identical hash —
see Continuation check). `live_xfb_untouched=0` with `live_same=0/0`: no
live comparison ran (zero rows), tabulated as observed.

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m6-baseline | `fc=6280` | `replay_disabled=0 fc=6483 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m6-suppress | `fc=6335` | `replay_disabled=0 fc=6338 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m6-aging | `fc=6387` | `replay_disabled=0 fc=6390 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m6-guard | `fc=7531` | `replay_disabled=0 fc=7534 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m6-negctrl | `fc=7729` | `replay_disabled=0 fc=7732 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ); the
quintuple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same address and
size, also identical to all three M5 sequence/disabled hashes) is tabulated
as observed. `resume fc − fc0` equals the per-replay `dframe` sum in each run
(200 / 0 / 0 / 0 / 0). No `replay_disabled` run was ordered by the M6 brief; none
was run.

## Exact commands

Builds (any time; only the header path differs from
`local/research/M5/build_replay_player.py`):

```
python3 local/research/M6/build_replay_player.py local/research/M6/players/m6-baseline
python3 local/research/M6/build_replay_player.py local/research/M6/players/m6-suppress
python3 local/research/M6/build_replay_player.py local/research/M6/players/m6-aging
python3 local/research/M6/build_replay_player.py local/research/M6/players/m6-guard
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M6\n'`, remove after
each run; profiles fresh per run):

```
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m6/m6-baseline-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M6/players/m6-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m6-det --cpu-thread --output /Volumes/Extreme\ SSD/m6/m6-baseline-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m6/m6-suppress-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M6/players/m6-suppress --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m6-det2 --cpu-thread --output /Volumes/Extreme\ SSD/m6/m6-suppress-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m6/m6-aging-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M6/players/m6-aging --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m6-det3 --cpu-thread --output /Volumes/Extreme\ SSD/m6/m6-aging-run --seconds 240
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m6/m6-guard-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M6/players/m6-guard --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m6-det4 --cpu-thread --output /Volumes/Extreme\ SSD/m6/m6-guard-run --seconds 240
SSX_M6_ARM_RECORD=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE=/Volumes/Extreme\ SSD/m6/m6-negctrl-probe.jsonl python3 tools/gamecube_schedule_check.py --player-dir local/research/M6/players/m6-guard --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m6-det5 --cpu-thread --output /Volumes/Extreme\ SSD/m6/m6-negctrl-run --seconds 240
```

Analysis:

```
python3 local/research/M6/analyze.py "m6-baseline=/Volumes/Extreme SSD/m6/m6-baseline-probe.jsonl" "m6-suppress=/Volumes/Extreme SSD/m6/m6-suppress-probe.jsonl" "m6-aging=/Volumes/Extreme SSD/m6/m6-aging-probe.jsonl" "m6-guard=/Volumes/Extreme SSD/m6/m6-guard-probe.jsonl"
python3 local/research/M6/analyze.py "m6-negctrl=/Volumes/Extreme SSD/m6/m6-negctrl-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M6/` — `m6_replay_context.h`
(`e89ca9b8…`), `build_replay_player.py`, `analyze.py`, `REPORT.md`, `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m6/` —
`m6-baseline-probe.jsonl`, `m6-suppress-probe.jsonl`, `m6-aging-probe.jsonl`,
`m6-guard-probe.jsonl`, `m6-negctrl-probe.jsonl` (~20 MB each) and the matching
`-run` dirs; per-step header snapshots `m6_replay_context.step{1..4}.h`.
Players (gitignored): `local/research/M6/players/{m6-baseline,m6-suppress,m6-aging,m6-guard}/`
(each with `player`, `build.json`, launchers). All paths above are symlink-free
as written (`realpath` identical).

## What I could not do

- Orchestrator battery hold (see `waits.log`): the MacBook was untethered, so
  after the in-flight step-4 guard run all further emulator runs held until
  release (battery + thermal-throttle timing noise). Release came on AC
  power; the negative-control run ran post-hold (guard receipts only — zero
  capacity rows, so no wall data crosses the hold boundary).
- No step orders an `m6-single` run (`det=0` path); none was run. The profile
  is defined by the brief but unordered.
- No `replay_disabled` continuation run was ordered by the M6 brief; none was
  run. Continuation receipts are the per-run `resume_xfb` events above.
- The +1-driver naming rests on code path + elimination (see Step 3's
  evidence-status note); no unsuppressed-with-tracing run observed the
  mid-Trigger flag flip directly.
- Player dirs are under `local/research/M6/players/` rather than the SSD: the
  build driver refuses outputs outside `local/`. Run dirs and all >5 MB probes are
  on the SSD as ordered.
- Desktop only; no device work.

## Files

Committed under `local/research/M6/`: `m6_replay_context.h` (research header,
`e89ca9b8…`), `build_replay_player.py` (M5 driver, header path only),
`analyze.py` (M5 tables unchanged + M6 `dafter_live`/`dpres`/`dimx`/`m6frame`/
`present_trace` sections; missing keys print as n/a),
`REPORT.md` (this file), `waits.log` (lease polls, claims, releases, holds).

## Header diffs per step (`diff -u` against the M5 header)

Step 1: empty (verbatim copy). Steps 2–4 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m6/m6_replay_context.step{2,3,4}.h`.

### Step 2

```diff
--- local/research/M5/m5_replay_context.h	2026-09-18 21:16:36
+++ /Volumes/Extreme SSD/m6/m6_replay_context.step2.h	2026-09-18 21:51:08
@@ -140,11 +140,33 @@
 
 // --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
 static unsigned long long s_after_frame_triggers = 0;
+// --- M6 step 2: scoped after_frame_event bus ---------------------------------
+//
+// HookableEvent's public API is Register/Trigger only: live listeners cannot
+// be unregistered (handles are owned by the subscribers) and no gate flag
+// exists at either Trigger site (BPStructs.cpp:353 is unconditional;
+// Present.cpp:1050 is Presenter::DoState read-mode only, never taken during
+// the sequence). The scoped bus uses two more public facts: VideoEvents'
+// after_frame_event is a public member (VideoEvents.h), and HookableEvent is
+// copyable/assignable through its implicit public special members, with the
+// copy sharing the listener storage. So the sequence saves the live bus by
+// copy (shares storage, keeps it alive), move-assigns a fresh empty bus into
+// the member (live listeners orphaned but intact via weak_ptr), registers the
+// header's own counter on the scoped bus, and registers a sentinel on the
+// saved bus: any Trigger that somehow reached live storage would move it, so
+// per-replay dafter_live=0 proves none did. Restored by copy-assignment after
+// the sequence (both the normal and the record_flag_set-break paths). Both
+// Trigger sites resolve the member fresh on every call and no subsystem caches
+// a reference to it (all vendor-tree uses are Register/Trigger on a fresh
+// GetVideoEvents() expression), so nothing bypasses the swap. No vendor
+// change, no visibility trick: only public members and public operators.
+static unsigned long long s_after_frame_live = 0;
 struct SideFx {
   size_t tex_entries = 0;
   size_t pending = 0;
   int frame_count = -1;
   unsigned long long after_frame = 0;
+  unsigned long long after_frame_live = 0;  // M6 step 2: sentinel on saved bus
   std::vector<u8> pe_state;
   std::vector<u8> vi_state;
 };
@@ -172,6 +194,7 @@
   }
   if (g_presenter) s.frame_count = g_presenter->FrameCount();
   s.after_frame = s_after_frame_triggers;
+  s.after_frame_live = s_after_frame_live;
   s.pe_state = DoStateBytes_PE(system);
   s.vi_state = DoStateBytes_VI(system);
   return s;
@@ -825,19 +848,25 @@
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
-  // M5 step 3: count after_frame_event triggers for the duration of the
-  // sequence with the header's own listener. Passive: it only increments.
-  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
-  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
+  // M6 step 2: install the scoped bus; the header's own counter moves to it
+  // (still counts every trigger) while the live listeners stay on the saved
+  // bus. Each trigger no longer runs TextureCacheBase::OnFrameEnd
+  // (FlushEFBCopies + Cleanup): the dpend/dtex receipts below measure the
+  // S2 section-A tension (deferred queue growth, frozen eviction).
   s_after_frame_triggers = 0;
-  Common::EventHook m5_after_frame_hook =
-      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
-        ++s_after_frame_triggers;
-      });
+  s_after_frame_live = 0;
+  auto& m6_bus = system.GetVideoEvents().after_frame_event;
+  auto m6_saved_bus = m6_bus;
+  m6_bus = Common::HookableEvent<Core::System&>();
+  Common::EventHook m6_after_frame_hook =
+      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
+  Common::EventHook m6_live_sentinel_hook =
+      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
   const SideFx fx_base = CaptureSideFx(system);
   // Min/max trackers over the per-replay deltas for the summary receipt.
   long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_dafter_live = 0, max_dafter_live = 0;
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
   const double seq_start = Now();
@@ -920,6 +949,8 @@
         static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
     const long long dafter =
         static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long dafter_live = static_cast<long long>(fx_after.after_frame_live) -
+                                  static_cast<long long>(fx_before.after_frame_live);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
     if (fx_first) {
@@ -927,6 +958,7 @@
       min_dpend = max_dpend = dpend;
       min_dframe = max_dframe = dframe;
       min_dafter = max_dafter = dafter;
+      min_dafter_live = max_dafter_live = dafter_live;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -939,6 +971,8 @@
       if (dframe > max_dframe) max_dframe = dframe;
       if (dafter < min_dafter) min_dafter = dafter;
       if (dafter > max_dafter) max_dafter = dafter;
+      if (dafter_live < min_dafter_live) min_dafter_live = dafter_live;
+      if (dafter_live > max_dafter_live) max_dafter_live = dafter_live;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
@@ -950,35 +984,45 @@
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"dafter_live\":%lld,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                  (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
-                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
+                 dtex, dpend, dframe, dafter, dafter_live, pediff, vidiff,
+                 xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M6 step 2: end-state capture, then drop the scoped bus and restore the
+  // live bus. Reached on both the normal and the record_flag_set-break paths.
+  const SideFx fx_end = CaptureSideFx(system);
+  m6_after_frame_hook.reset();
+  m6_live_sentinel_hook.reset();
+  m6_bus = m6_saved_bus;
   // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
   // event. completed = capacity rows actually emitted (record_flag_set stops
-  // the sequence early, fail-closed).
+  // the sequence early, fail-closed). M6 step 2 adds dafter_live min/max and
+  // the end absolutes (texN/pendN/fcN) for the accumulation/growth receipts.
   {
-    char summary[640];
+    char summary[768];
     std::snprintf(summary, sizeof(summary),
-                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d texN=%zu pendN=%zu fcN=%d "
                   "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "dafter_live_min=%lld dafter_live_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
                   replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
-                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
-                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
-                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
-                  live_ok_count, live_same_count);
+                  fx_end.tex_entries, fx_end.pending, fx_end.frame_count, min_dtex,
+                  max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
+                  min_dafter, max_dafter, min_dafter_live, max_dafter_live, min_pe,
+                  max_pe, min_vi, max_vi, int(xfb_scratch_ok), xfb_scratch_addr,
+                  xfb_scratch_count, live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
-  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```

### Step 3

```diff
--- local/research/M5/m5_replay_context.h	2026-09-18 21:16:36
+++ /Volumes/Extreme SSD/m6/m6_replay_context.step3.h	2026-09-18 21:57:36
@@ -87,6 +87,7 @@
 #include "Core/HW/VideoInterface.h"
 #include "VideoCommon/VideoEvents.h"
 #include "Common/HookableEvent.h"
+#include <atomic>
 #include <cstdio>
 #include <cstring>
 #include <ctime>
@@ -140,11 +141,56 @@
 
 // --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
 static unsigned long long s_after_frame_triggers = 0;
+// --- M6 step 2: scoped after_frame_event bus ---------------------------------
+//
+// HookableEvent's public API is Register/Trigger only: live listeners cannot
+// be unregistered (handles are owned by the subscribers) and no gate flag
+// exists at either Trigger site (BPStructs.cpp:353 is unconditional;
+// Present.cpp:1050 is Presenter::DoState read-mode only, never taken during
+// the sequence). The scoped bus uses two more public facts: VideoEvents'
+// after_frame_event is a public member (VideoEvents.h), and HookableEvent is
+// copyable/assignable through its implicit public special members, with the
+// copy sharing the listener storage. So the sequence saves the live bus by
+// copy (shares storage, keeps it alive), move-assigns a fresh empty bus into
+// the member (live listeners orphaned but intact via weak_ptr), registers the
+// header's own counter on the scoped bus, and registers a sentinel on the
+// saved bus: any Trigger that somehow reached live storage would move it, so
+// per-replay dafter_live=0 proves none did. Restored by copy-assignment after
+// the sequence (both the normal and the record_flag_set-break paths). Both
+// Trigger sites resolve the member fresh on every call and no subsystem caches
+// a reference to it (all vendor-tree uses are Register/Trigger on a fresh
+// GetVideoEvents() expression), so nothing bypasses the swap. No vendor
+// change, no visibility trick: only public members and public operators.
+static unsigned long long s_after_frame_live = 0;
+// --- M6 step 3: replay-local frame counter + presenter tracing ----------------
+// FrameCount() can no longer age the replay (step 2 suppresses the only
+// in-sequence writer path), so the header owns its own frame counter,
+// incremented once per emitted capacity row. The presenter tracing names M5's
+// unresolved dframe +1/replay writer: before_present_event fires in every
+// ViSwap/ImmediateSwap path (even duplicates), after_present_event in every
+// non-skipped present, and PresentInfo.reason splits Immediate vs
+// VideoInterface vs duplicate. Armed while still live (the recorded original
+// frame presents, so a non-empty pre-sequence count is the tracer's positive
+// control), snapshotted at sequence start, emitted as present_trace after the
+// sequence. Atomics: during the live window the callbacks run on the video
+// thread while the sequence reads post-stall; during the sequence the video
+// thread is stalled (PauseAndLock) and only this thread's synchronous
+// ImmediateSwap path can fire.
+static unsigned long long s_m6_frame = 0;
+static std::atomic<unsigned long long> s_pres_before{0}, s_pres_after{0};
+static std::atomic<unsigned long long> s_pres_imm{0}, s_pres_vi{0}, s_pres_dup{0};
+static std::atomic<bool> s_pres_got_imm{false}, s_pres_got_vi{false};
+static std::atomic<unsigned long long> s_pres_first_imm_pc{0}, s_pres_first_imm_fc{0};
+static std::atomic<unsigned long long> s_pres_first_vi_pc{0}, s_pres_first_vi_fc{0};
+static Common::EventHook s_pres_before_hook, s_pres_after_hook;
 struct SideFx {
   size_t tex_entries = 0;
   size_t pending = 0;
   int frame_count = -1;
   unsigned long long after_frame = 0;
+  unsigned long long after_frame_live = 0;  // M6 step 2: sentinel on saved bus
+  unsigned long long present_before = 0;    // M6 step 3: presenter tracing
+  int imxfb = -1;                           // M6 step 3: g_ActiveConfig sample
   std::vector<u8> pe_state;
   std::vector<u8> vi_state;
 };
@@ -172,6 +218,9 @@
   }
   if (g_presenter) s.frame_count = g_presenter->FrameCount();
   s.after_frame = s_after_frame_triggers;
+  s.after_frame_live = s_after_frame_live;
+  s.present_before = s_pres_before.load(std::memory_order_relaxed);
+  s.imxfb = g_ActiveConfig.bImmediateXFB ? 1 : 0;
   s.pe_state = DoStateBytes_PE(system);
   s.vi_state = DoStateBytes_VI(system);
   return s;
@@ -643,6 +692,43 @@
       std::snprintf(d, sizeof(d), "fc=%d", fc);
       Event("record_start", d);
     }
+    // M6 step 3: arm presenter tracing while still live. The recorded
+    // original frame presents, so a non-empty pre-sequence count is the
+    // tracer's positive control.
+    s_pres_before.store(0, std::memory_order_relaxed);
+    s_pres_after.store(0, std::memory_order_relaxed);
+    s_pres_imm.store(0, std::memory_order_relaxed);
+    s_pres_vi.store(0, std::memory_order_relaxed);
+    s_pres_dup.store(0, std::memory_order_relaxed);
+    s_pres_got_imm.store(false, std::memory_order_relaxed);
+    s_pres_got_vi.store(false, std::memory_order_relaxed);
+    s_pres_before_hook =
+        system.GetVideoEvents().before_present_event.Register([](PresentInfo& info) {
+          s_pres_before.fetch_add(1, std::memory_order_relaxed);
+          if (info.reason == PresentInfo::PresentReason::Immediate) {
+            s_pres_imm.fetch_add(1, std::memory_order_relaxed);
+            bool want = false;
+            if (s_pres_got_imm.compare_exchange_strong(want, true,
+                                                       std::memory_order_relaxed)) {
+              s_pres_first_imm_pc.store(info.present_count, std::memory_order_relaxed);
+              s_pres_first_imm_fc.store(info.frame_count, std::memory_order_relaxed);
+            }
+          } else if (info.reason == PresentInfo::PresentReason::VideoInterface) {
+            s_pres_vi.fetch_add(1, std::memory_order_relaxed);
+            bool want = false;
+            if (s_pres_got_vi.compare_exchange_strong(want, true,
+                                                      std::memory_order_relaxed)) {
+              s_pres_first_vi_pc.store(info.present_count, std::memory_order_relaxed);
+              s_pres_first_vi_fc.store(info.frame_count, std::memory_order_relaxed);
+            }
+          } else {
+            s_pres_dup.fetch_add(1, std::memory_order_relaxed);
+          }
+        });
+    s_pres_after_hook =
+        system.GetVideoEvents().after_present_event.Register([](PresentInfo&) {
+          s_pres_after.fetch_add(1, std::memory_order_relaxed);
+        });
     return;
   }
   if (phase == Phase::Recording) {
@@ -651,6 +737,8 @@
     if (!ready) {
       if (Now() - record_wall > 2.0) {
         Event("record_failed");
+        s_pres_before_hook.reset();  // M6 step 3: never leave tracing armed
+        s_pres_after_hook.reset();
         phase = Phase::Done;
       }
       return;
@@ -825,19 +913,35 @@
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
-  // M5 step 3: count after_frame_event triggers for the duration of the
-  // sequence with the header's own listener. Passive: it only increments.
-  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
-  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
-  s_after_frame_triggers = 0;
-  Common::EventHook m5_after_frame_hook =
-      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
-        ++s_after_frame_triggers;
-      });
+  // M6 step 2: install the scoped bus; the header's own counter moves to it
+  // (still counts every trigger) while the live listeners stay on the saved
+  // bus. Each trigger no longer runs TextureCacheBase::OnFrameEnd
+  // (FlushEFBCopies + Cleanup): the dpend/dtex receipts below measure the
+  // S2 section-A tension (deferred queue growth, frozen eviction).
+  s_after_frame_triggers = 0;
+  s_after_frame_live = 0;
+  auto& m6_bus = system.GetVideoEvents().after_frame_event;
+  auto m6_saved_bus = m6_bus;
+  m6_bus = Common::HookableEvent<Core::System&>();
+  Common::EventHook m6_after_frame_hook =
+      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
+  Common::EventHook m6_live_sentinel_hook =
+      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
   const SideFx fx_base = CaptureSideFx(system);
+  // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
+  // stalled from here on, so these reads race nothing) + replay-local frame
+  // counter reset.
+  const unsigned long long pres0_before = s_pres_before.load(std::memory_order_relaxed);
+  const unsigned long long pres0_after = s_pres_after.load(std::memory_order_relaxed);
+  const unsigned long long pres0_imm = s_pres_imm.load(std::memory_order_relaxed);
+  const unsigned long long pres0_vi = s_pres_vi.load(std::memory_order_relaxed);
+  const unsigned long long pres0_dup = s_pres_dup.load(std::memory_order_relaxed);
+  s_m6_frame = 0;
   // Min/max trackers over the per-replay deltas for the summary receipt.
   long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_dafter_live = 0, max_dafter_live = 0;
+  long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
   const double seq_start = Now();
@@ -920,6 +1024,12 @@
         static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
     const long long dafter =
         static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long dafter_live = static_cast<long long>(fx_after.after_frame_live) -
+                                  static_cast<long long>(fx_before.after_frame_live);
+    const long long dpres = static_cast<long long>(fx_after.present_before) -
+                            static_cast<long long>(fx_before.present_before);
+    const long long dimx =
+        static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
     if (fx_first) {
@@ -927,6 +1037,9 @@
       min_dpend = max_dpend = dpend;
       min_dframe = max_dframe = dframe;
       min_dafter = max_dafter = dafter;
+      min_dafter_live = max_dafter_live = dafter_live;
+      min_dpres = max_dpres = dpres;
+      min_dimx = max_dimx = dimx;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -939,46 +1052,92 @@
       if (dframe > max_dframe) max_dframe = dframe;
       if (dafter < min_dafter) min_dafter = dafter;
       if (dafter > max_dafter) max_dafter = dafter;
+      if (dafter_live < min_dafter_live) min_dafter_live = dafter_live;
+      if (dafter_live > max_dafter_live) max_dafter_live = dafter_live;
+      if (dpres < min_dpres) min_dpres = dpres;
+      if (dpres > max_dpres) max_dpres = dpres;
+      if (dimx < min_dimx) min_dimx = dimx;
+      if (dimx > max_dimx) max_dimx = dimx;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
       if (vidiff > max_vi) max_vi = vidiff;
     }
+    ++s_m6_frame;  // one emitted capacity row = one replayed frame
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                  (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
-                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
+                 dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
+                 pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M6 step 2: end-state capture, then drop the scoped bus and restore the
+  // live bus. Reached on both the normal and the record_flag_set-break paths.
+  const SideFx fx_end = CaptureSideFx(system);
+  m6_after_frame_hook.reset();
+  m6_live_sentinel_hook.reset();
+  m6_bus = m6_saved_bus;
+  // M6 step 3: presenter-tracing receipt (pre = live window from record_start
+  // to sequence start; seq = during the sequence), then disarm. Reached on
+  // both the normal and the record_flag_set-break paths.
+  {
+    const unsigned long long e_before = s_pres_before.load(std::memory_order_relaxed);
+    const unsigned long long e_after = s_pres_after.load(std::memory_order_relaxed);
+    const unsigned long long e_imm = s_pres_imm.load(std::memory_order_relaxed);
+    const unsigned long long e_vi = s_pres_vi.load(std::memory_order_relaxed);
+    const unsigned long long e_dup = s_pres_dup.load(std::memory_order_relaxed);
+    char trace[384];
+    std::snprintf(trace, sizeof(trace),
+                  "pre_before=%llu pre_after=%llu pre_imm=%llu pre_vi=%llu pre_dup=%llu "
+                  "seq_before=%llu seq_after=%llu seq_imm=%llu seq_vi=%llu seq_dup=%llu "
+                  "first_imm_pc=%llu first_imm_fc=%llu first_vi_pc=%llu first_vi_fc=%llu",
+                  pres0_before, pres0_after, pres0_imm, pres0_vi, pres0_dup,
+                  e_before - pres0_before, e_after - pres0_after, e_imm - pres0_imm,
+                  e_vi - pres0_vi, e_dup - pres0_dup,
+                  s_pres_first_imm_pc.load(std::memory_order_relaxed),
+                  s_pres_first_imm_fc.load(std::memory_order_relaxed),
+                  s_pres_first_vi_pc.load(std::memory_order_relaxed),
+                  s_pres_first_vi_fc.load(std::memory_order_relaxed));
+    Event("present_trace", trace);
+  }
+  s_pres_before_hook.reset();
+  s_pres_after_hook.reset();
   // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
   // event. completed = capacity rows actually emitted (record_flag_set stops
-  // the sequence early, fail-closed).
+  // the sequence early, fail-closed). M6 step 2 adds dafter_live min/max and
+  // the end absolutes (texN/pendN/fcN) for the accumulation/growth receipts;
+  // M6 step 3 adds dpres/dimx min/max and the imxfb end absolutes.
   {
-    char summary[640];
+    char summary[768];
     std::snprintf(summary, sizeof(summary),
-                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d texN=%zu pendN=%zu fcN=%d "
+                  "imx0=%d imxN=%d "
                   "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "dafter_live_min=%lld dafter_live_max=%lld "
+                  "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
                   replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
-                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
-                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
-                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
+                  fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
+                  fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
+                  max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
+                  min_dpres, max_dpres, min_dimx, max_dimx, min_pe, max_pe, min_vi,
+                  max_vi, int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
                   live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
-  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```

### Step 4

```diff
--- local/research/M5/m5_replay_context.h	2026-09-18 21:16:36
+++ /Volumes/Extreme SSD/m6/m6_replay_context.step4.h	2026-09-18 22:02:33
@@ -87,6 +87,7 @@
 #include "Core/HW/VideoInterface.h"
 #include "VideoCommon/VideoEvents.h"
 #include "Common/HookableEvent.h"
+#include <atomic>
 #include <cstdio>
 #include <cstring>
 #include <ctime>
@@ -140,11 +141,56 @@
 
 // --- M5 step 3: side-effect counters, fail-closed (measures only) -----------
 static unsigned long long s_after_frame_triggers = 0;
+// --- M6 step 2: scoped after_frame_event bus ---------------------------------
+//
+// HookableEvent's public API is Register/Trigger only: live listeners cannot
+// be unregistered (handles are owned by the subscribers) and no gate flag
+// exists at either Trigger site (BPStructs.cpp:353 is unconditional;
+// Present.cpp:1050 is Presenter::DoState read-mode only, never taken during
+// the sequence). The scoped bus uses two more public facts: VideoEvents'
+// after_frame_event is a public member (VideoEvents.h), and HookableEvent is
+// copyable/assignable through its implicit public special members, with the
+// copy sharing the listener storage. So the sequence saves the live bus by
+// copy (shares storage, keeps it alive), move-assigns a fresh empty bus into
+// the member (live listeners orphaned but intact via weak_ptr), registers the
+// header's own counter on the scoped bus, and registers a sentinel on the
+// saved bus: any Trigger that somehow reached live storage would move it, so
+// per-replay dafter_live=0 proves none did. Restored by copy-assignment after
+// the sequence (both the normal and the record_flag_set-break paths). Both
+// Trigger sites resolve the member fresh on every call and no subsystem caches
+// a reference to it (all vendor-tree uses are Register/Trigger on a fresh
+// GetVideoEvents() expression), so nothing bypasses the swap. No vendor
+// change, no visibility trick: only public members and public operators.
+static unsigned long long s_after_frame_live = 0;
+// --- M6 step 3: replay-local frame counter + presenter tracing ----------------
+// FrameCount() can no longer age the replay (step 2 suppresses the only
+// in-sequence writer path), so the header owns its own frame counter,
+// incremented once per emitted capacity row. The presenter tracing names M5's
+// unresolved dframe +1/replay writer: before_present_event fires in every
+// ViSwap/ImmediateSwap path (even duplicates), after_present_event in every
+// non-skipped present, and PresentInfo.reason splits Immediate vs
+// VideoInterface vs duplicate. Armed while still live (the recorded original
+// frame presents, so a non-empty pre-sequence count is the tracer's positive
+// control), snapshotted at sequence start, emitted as present_trace after the
+// sequence. Atomics: during the live window the callbacks run on the video
+// thread while the sequence reads post-stall; during the sequence the video
+// thread is stalled (PauseAndLock) and only this thread's synchronous
+// ImmediateSwap path can fire.
+static unsigned long long s_m6_frame = 0;
+static std::atomic<unsigned long long> s_pres_before{0}, s_pres_after{0};
+static std::atomic<unsigned long long> s_pres_imm{0}, s_pres_vi{0}, s_pres_dup{0};
+static std::atomic<bool> s_pres_got_imm{false}, s_pres_got_vi{false};
+static std::atomic<unsigned long long> s_pres_first_imm_pc{0}, s_pres_first_imm_fc{0};
+static std::atomic<unsigned long long> s_pres_first_vi_pc{0}, s_pres_first_vi_fc{0};
+static Common::EventHook s_pres_before_hook, s_pres_after_hook;
 struct SideFx {
   size_t tex_entries = 0;
   size_t pending = 0;
   int frame_count = -1;
   unsigned long long after_frame = 0;
+  unsigned long long after_frame_live = 0;  // M6 step 2: sentinel on saved bus
+  unsigned long long present_before = 0;    // M6 step 3: presenter tracing
+  int imxfb = -1;                           // M6 step 3: g_ActiveConfig sample
   std::vector<u8> pe_state;
   std::vector<u8> vi_state;
 };
@@ -172,6 +218,9 @@
   }
   if (g_presenter) s.frame_count = g_presenter->FrameCount();
   s.after_frame = s_after_frame_triggers;
+  s.after_frame_live = s_after_frame_live;
+  s.present_before = s_pres_before.load(std::memory_order_relaxed);
+  s.imxfb = g_ActiveConfig.bImmediateXFB ? 1 : 0;
   s.pe_state = DoStateBytes_PE(system);
   s.vi_state = DoStateBytes_VI(system);
   return s;
@@ -643,6 +692,43 @@
       std::snprintf(d, sizeof(d), "fc=%d", fc);
       Event("record_start", d);
     }
+    // M6 step 3: arm presenter tracing while still live. The recorded
+    // original frame presents, so a non-empty pre-sequence count is the
+    // tracer's positive control.
+    s_pres_before.store(0, std::memory_order_relaxed);
+    s_pres_after.store(0, std::memory_order_relaxed);
+    s_pres_imm.store(0, std::memory_order_relaxed);
+    s_pres_vi.store(0, std::memory_order_relaxed);
+    s_pres_dup.store(0, std::memory_order_relaxed);
+    s_pres_got_imm.store(false, std::memory_order_relaxed);
+    s_pres_got_vi.store(false, std::memory_order_relaxed);
+    s_pres_before_hook =
+        system.GetVideoEvents().before_present_event.Register([](PresentInfo& info) {
+          s_pres_before.fetch_add(1, std::memory_order_relaxed);
+          if (info.reason == PresentInfo::PresentReason::Immediate) {
+            s_pres_imm.fetch_add(1, std::memory_order_relaxed);
+            bool want = false;
+            if (s_pres_got_imm.compare_exchange_strong(want, true,
+                                                       std::memory_order_relaxed)) {
+              s_pres_first_imm_pc.store(info.present_count, std::memory_order_relaxed);
+              s_pres_first_imm_fc.store(info.frame_count, std::memory_order_relaxed);
+            }
+          } else if (info.reason == PresentInfo::PresentReason::VideoInterface) {
+            s_pres_vi.fetch_add(1, std::memory_order_relaxed);
+            bool want = false;
+            if (s_pres_got_vi.compare_exchange_strong(want, true,
+                                                      std::memory_order_relaxed)) {
+              s_pres_first_vi_pc.store(info.present_count, std::memory_order_relaxed);
+              s_pres_first_vi_fc.store(info.frame_count, std::memory_order_relaxed);
+            }
+          } else {
+            s_pres_dup.fetch_add(1, std::memory_order_relaxed);
+          }
+        });
+    s_pres_after_hook =
+        system.GetVideoEvents().after_present_event.Register([](PresentInfo&) {
+          s_pres_after.fetch_add(1, std::memory_order_relaxed);
+        });
     return;
   }
   if (phase == Phase::Recording) {
@@ -651,6 +737,8 @@
     if (!ready) {
       if (Now() - record_wall > 2.0) {
         Event("record_failed");
+        s_pres_before_hook.reset();  // M6 step 3: never leave tracing armed
+        s_pres_after_hook.reset();
         phase = Phase::Done;
       }
       return;
@@ -825,19 +913,50 @@
   }
   auto* const saved_transform = XFReplay::g_transform;
   g_ActiveConfig.bImmediateXFB = false;
-  // M5 step 3: count after_frame_event triggers for the duration of the
-  // sequence with the header's own listener. Passive: it only increments.
-  // Each trigger also runs TextureCacheBase::OnFrameEnd (FlushEFBCopies +
-  // Cleanup), so the count doubles as the FlushEFBCopies opportunity count.
+  // M6 step 2: install the scoped bus; the header's own counter moves to it
+  // (still counts every trigger) while the live listeners stay on the saved
+  // bus. Each trigger no longer runs TextureCacheBase::OnFrameEnd
+  // (FlushEFBCopies + Cleanup): the dpend/dtex receipts below measure the
+  // S2 section-A tension (deferred queue growth, frozen eviction).
   s_after_frame_triggers = 0;
-  Common::EventHook m5_after_frame_hook =
-      system.GetVideoEvents().after_frame_event.Register([](Core::System&) {
-        ++s_after_frame_triggers;
-      });
+  s_after_frame_live = 0;
+  auto& m6_bus = system.GetVideoEvents().after_frame_event;
+  auto m6_saved_bus = m6_bus;
+  m6_bus = Common::HookableEvent<Core::System&>();
+  Common::EventHook m6_after_frame_hook =
+      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
+  Common::EventHook m6_live_sentinel_hook =
+      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
   const SideFx fx_base = CaptureSideFx(system);
+  // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
+  // stalled from here on, so these reads race nothing) + replay-local frame
+  // counter reset.
+  const unsigned long long pres0_before = s_pres_before.load(std::memory_order_relaxed);
+  const unsigned long long pres0_after = s_pres_after.load(std::memory_order_relaxed);
+  const unsigned long long pres0_imm = s_pres_imm.load(std::memory_order_relaxed);
+  const unsigned long long pres0_vi = s_pres_vi.load(std::memory_order_relaxed);
+  const unsigned long long pres0_dup = s_pres_dup.load(std::memory_order_relaxed);
+  s_m6_frame = 0;
+  // M6 step 4: fail-closed g_record_fifo_data guard (the M5 loop-top check
+  // below is kept: sample before every replay, emit record_flag_set and stop
+  // the sequence on true). Negative control: SSX_M6_ARM_RECORD=1 arms the
+  // sampled flag before replay 0 through the public global (no vendor
+  // change), proving the guard fires; restored to false after the sequence so
+  // the live session resumes unarmed. FifoRecorder::StartRecording was
+  // considered and rejected for the arming: its listener sets the flag from
+  // IsRecording() on the next after_frame trigger, which under suppression
+  // never reaches the live bus — the flag itself is the guard's sampled
+  // condition and the exact hazard (it gates WriteGPCommand/UseMemory).
+  const bool m6_arm_record = [] {
+    const char* v = std::getenv("SSX_M6_ARM_RECORD");
+    return v && std::strcmp(v, "1") == 0;
+  }();
+  if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = true;
   // Min/max trackers over the per-replay deltas for the summary receipt.
   long long min_dtex = 0, max_dtex = 0, min_dpend = 0, max_dpend = 0;
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
+  long long min_dafter_live = 0, max_dafter_live = 0;
+  long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
   const double seq_start = Now();
@@ -846,7 +965,7 @@
     // re-arms g_record_fifo_data would corrupt any live capture.
     if (OpcodeDecoder::g_record_fifo_data) {
       char rd[64];
-      std::snprintf(rd, sizeof(rd), "replay=%u", replays);
+      std::snprintf(rd, sizeof(rd), "replay=%u armed=%d", replays, int(m6_arm_record));
       Event("record_flag_set", rd);
       break;
     }
@@ -920,6 +1039,12 @@
         static_cast<long long>(fx_after.frame_count) - static_cast<long long>(fx_before.frame_count);
     const long long dafter =
         static_cast<long long>(fx_after.after_frame) - static_cast<long long>(fx_before.after_frame);
+    const long long dafter_live = static_cast<long long>(fx_after.after_frame_live) -
+                                  static_cast<long long>(fx_before.after_frame_live);
+    const long long dpres = static_cast<long long>(fx_after.present_before) -
+                            static_cast<long long>(fx_before.present_before);
+    const long long dimx =
+        static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
     if (fx_first) {
@@ -927,6 +1052,9 @@
       min_dpend = max_dpend = dpend;
       min_dframe = max_dframe = dframe;
       min_dafter = max_dafter = dafter;
+      min_dafter_live = max_dafter_live = dafter_live;
+      min_dpres = max_dpres = dpres;
+      min_dimx = max_dimx = dimx;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -939,46 +1067,93 @@
       if (dframe > max_dframe) max_dframe = dframe;
       if (dafter < min_dafter) min_dafter = dafter;
       if (dafter > max_dafter) max_dafter = dafter;
+      if (dafter_live < min_dafter_live) min_dafter_live = dafter_live;
+      if (dafter_live > max_dafter_live) max_dafter_live = dafter_live;
+      if (dpres < min_dpres) min_dpres = dpres;
+      if (dpres > max_dpres) max_dpres = dpres;
+      if (dimx < min_dimx) min_dimx = dimx;
+      if (dimx > max_dimx) max_dimx = dimx;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
       if (vidiff > max_vi) max_vi = vidiff;
     }
+    ++s_m6_frame;  // one emitted capacity row = one replayed frame
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
                  "\"mem_ms\":%.3f,\"cp_ms\":%.3f,\"pre_ms\":%.3f,\"run_ms\":%.3f,"
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
+                 "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                  (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
-                 dtex, dpend, dframe, dafter, pediff, vidiff, xfb_scratch_equal);
+                 dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
+                 pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
+  // M6 step 2: end-state capture, then drop the scoped bus and restore the
+  // live bus. Reached on both the normal and the record_flag_set-break paths.
+  const SideFx fx_end = CaptureSideFx(system);
+  m6_after_frame_hook.reset();
+  m6_live_sentinel_hook.reset();
+  m6_bus = m6_saved_bus;
+  if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = false;  // M6 step 4
+  // M6 step 3: presenter-tracing receipt (pre = live window from record_start
+  // to sequence start; seq = during the sequence), then disarm. Reached on
+  // both the normal and the record_flag_set-break paths.
+  {
+    const unsigned long long e_before = s_pres_before.load(std::memory_order_relaxed);
+    const unsigned long long e_after = s_pres_after.load(std::memory_order_relaxed);
+    const unsigned long long e_imm = s_pres_imm.load(std::memory_order_relaxed);
+    const unsigned long long e_vi = s_pres_vi.load(std::memory_order_relaxed);
+    const unsigned long long e_dup = s_pres_dup.load(std::memory_order_relaxed);
+    char trace[384];
+    std::snprintf(trace, sizeof(trace),
+                  "pre_before=%llu pre_after=%llu pre_imm=%llu pre_vi=%llu pre_dup=%llu "
+                  "seq_before=%llu seq_after=%llu seq_imm=%llu seq_vi=%llu seq_dup=%llu "
+                  "first_imm_pc=%llu first_imm_fc=%llu first_vi_pc=%llu first_vi_fc=%llu",
+                  pres0_before, pres0_after, pres0_imm, pres0_vi, pres0_dup,
+                  e_before - pres0_before, e_after - pres0_after, e_imm - pres0_imm,
+                  e_vi - pres0_vi, e_dup - pres0_dup,
+                  s_pres_first_imm_pc.load(std::memory_order_relaxed),
+                  s_pres_first_imm_fc.load(std::memory_order_relaxed),
+                  s_pres_first_vi_pc.load(std::memory_order_relaxed),
+                  s_pres_first_vi_fc.load(std::memory_order_relaxed));
+    Event("present_trace", trace);
+  }
+  s_pres_before_hook.reset();
+  s_pres_after_hook.reset();
   // M5 step 3: 200-row summary table (min/max of each delta) as one receipt
   // event. completed = capacity rows actually emitted (record_flag_set stops
-  // the sequence early, fail-closed).
+  // the sequence early, fail-closed). M6 step 2 adds dafter_live min/max and
+  // the end absolutes (texN/pendN/fcN) for the accumulation/growth receipts;
+  // M6 step 3 adds dpres/dimx min/max and the imxfb end absolutes.
   {
-    char summary[640];
+    char summary[768];
     std::snprintf(summary, sizeof(summary),
-                  "completed=%u tex0=%zu pend0=%zu fc0=%d "
+                  "completed=%u tex0=%zu pend0=%zu fc0=%d texN=%zu pendN=%zu fcN=%d "
+                  "imx0=%d imxN=%d "
                   "dtex_min=%lld dtex_max=%lld dpend_min=%lld dpend_max=%lld "
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
+                  "dafter_live_min=%lld dafter_live_max=%lld "
+                  "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
                   replays, fx_base.tex_entries, fx_base.pending, fx_base.frame_count,
-                  min_dtex, max_dtex, min_dpend, max_dpend, min_dframe, max_dframe,
-                  min_dafter, max_dafter, min_pe, max_pe, min_vi, max_vi,
-                  int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
+                  fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
+                  fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
+                  max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
+                  min_dpres, max_dpres, min_dimx, max_dimx, min_pe, max_pe, min_vi,
+                  max_vi, int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
                   live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
-  m5_after_frame_hook.reset();
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```
