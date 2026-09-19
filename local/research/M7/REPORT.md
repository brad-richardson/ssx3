# M7 — Host replay milestone 2, item 3: REPORT

Pose interpolation + camera delta on the `g_transform` seam, desktop only.
Runbook `local/muse/prompts/M7.md`. No `adb`, no device. No verdicts.

Header read first: `local/research/M6/REPORT.md` (all of it: the scoped bus,
the +1 driver, the guard, "What I could not do"), `local/research/S2/REPORT.md`
Part 4 §"What a `ReplayContext` still has to own" item 5 (this brief is that
item) and §"Arm 2 (s2-egl-b)" (the no-op `g_transform` probe = the zero-cost
baseline), and the base header `local/research/M6/m6_replay_context.h`.

Time box 6 hours; used about 0.7. No holds, no lease contention.

## Baseline note (read before the tables)

The M6 header on disk (`local/research/M6/m6_replay_context.h`, clean tree)
hashes to `e89ca9b8a487fb673a6986897849deab40382f533205e7d18835fb2f2df45eb8`
via `shasum -a 256` (trust `shasum`, not memory; matches the M6 brief's pinned
prefix). Step 1 copied the on-disk file verbatim to
`local/research/M7/m7_replay_context.h`; `diff -u` between them is empty
(§Header diffs, step 1). Every M5/M6 mechanism is kept in all steps: PE mask,
verbatim execute stream, restore, stall, pipe snapshot, watched-window
re-hash, `done`, XFB hash + scratch redirect, side-effect counters,
continuation capture, scoped bus, `m6frame`, presenter tracing, record guard.
All M7 additions are env-gated with defaults that preserve M6 behavior
(`SSX_M7_NO_SUPPRESS` unset, `SSX_M7_XFORM` unset); the committed header is
the step-3 header, from which every step's run is reproducible via env.

One recorded deviation from the runbook's step-1 sentence: the unsuppressed
gap run could not run "on this same player" as the baseline, because the
step-1 header suppresses unconditionally (the scoped-bus install has no
configuration). It ran on a step-1b player whose only change is the env-gated
bypass plus the in-Trigger flag probe (diff in §Header diffs, step 1b).

## Runs

All runs: `tools/gamecube_schedule_check.py --immediate-xfb --resolution 640x528
--game local/game/gxbe69-stock --seconds 240`, as M6. `m7-det` configuration means
dual core + `SSX_S2_FORCE_DETERMINISM=1` + `--cpu-thread`. Profile directories are
fresh per run. `m7-single` is the single-core configuration (no `--cpu-thread`,
no forced determinism, M5 precedent); `m7-off` is the baseline player with
`SSX_NATIVE_REPLAY=0` (M5 `m5-off` shape: force-det + `--cpu-thread` kept).
Each desktop run held `/tmp/ssx3-host-lease` (`printf 'M7\n'`, removed after each
run); the log is `local/research/M7/waits.log` (six claim/release pairs, no
waits, no polls). Builds ran any time.

| Step | Header sha256 | Player | Run (profile) | Probe |
| --- | --- | --- | --- | --- |
| 1 baseline | `e89ca9b8…` (= M6 on disk) | `players/m7-baseline` | `m7-baseline-run` (`m7-det`) | `m7-baseline-probe.jsonl` |
| 1 gap single | `e89ca9b8…` | `players/m7-baseline` | `m7-single-run` (`m7-single`) | `m7-single-probe.jsonl` |
| 1 gap off | `e89ca9b8…` | `players/m7-baseline` | `m7-off-run` (`m7-off`) | `m7-off-probe.jsonl` |
| 1b gap trace | `206f7aae…` | `players/m7-nosuppress` | `m7-trace-run` (`m7-det2`, `SSX_M7_NO_SUPPRESS=1`) | `m7-trace-probe.jsonl` |
| 2 noop | `4171b752…` | `players/m7-xform` | `m7-noop-run` (`m7-det3`, `SSX_M7_XFORM=full`) | `m7-noop-probe.jsonl` |
| 3 delta | `0bfc4860…` | `players/m7-delta` | `m7-delta-run` (`m7-det4`, `SSX_M7_XFORM=delta`) | `m7-delta-probe.jsonl` |

The committed header is `0bfc4860…` (step 3, identical to the step-3 snapshot).

Player dirs live under `local/research/M7/players/` (the build driver requires
outputs under `local/`; they are gitignored build outputs, never committed).
Run dirs and every probe jsonl (>5 MB, ~21 MB each) live under
`/Volumes/Extreme SSD/m7/` (symlink-free; `realpath` is the path as written).
Probes, runs and players are not committed.

## Step 1 — baseline + M6 gaps

Unmodified copy. `analyze.py` prints 200 rows + `done` +
`xfb_equal_scratch=200/200` + `live_xfb_untouched=1` +
`dafter_live`/`dframe`/`dpres`/`dimx` all 0/0 (M6's end state reproduced).
Control for steps 2–3.

Gap 1 — `m7-single` (`det=0` path). Same player, single core, no forced
determinism. `restored` reads `det=0 dual=0`.

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m7-single | 200 | 5.097 / 9.795 / 3.712 / 10.398 | 2.298 / 2.634 | 394932 / 3325 | YES | seq_wall_ms=1409.275 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m7-single | dtex | 0 | 1 |
| m7-single | dpend | 0 | 0 |
| m7-single | dframe | 0 | 0 |
| m7-single | dafter | 1 | 1 |
| m7-single | dafter_live | 0 | 0 |
| m7-single | dpres | 0 | 0 |
| m7-single | dimx | 0 | 0 |
| m7-single | pediff | 0 | 2 |
| m7-single | vidiff | 0 | 0 |
```

Sequence-entry/end absolutes: tex 119→120, pend 0→0, fc 8173→8173, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=16341 first_imm_fc=8170` (M6 step-3 tracing replicates on the
`det=0` path). `pre_ms` med 0.000 (preprocess pass skipped, `det=0`).
Recorded without verdict: every counter matches the suppressed baseline shape
except `pediff` 0/+2 (baseline 0/0).

Gap 2 — `m7-off` (`replay_disabled` continuation). Same player,
`SSX_NATIVE_REPLAY=0`. 0 capacity rows by design; events are `record_start`
+ `resume_xfb` only:

| Field | Value |
| --- | --- |
| `record_start` detail | `replay_disabled=1 fc=6813` |
| `resume_xfb` detail | `replay_disabled=1 fc=6813 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison against sequence runs is skipped
(seams differ); the hash is tabulated as observed in §Continuation check.

Gap 3 — `m7-trace` (unsuppressed-with-tracing). Step-1b player,
`SSX_M7_NO_SUPPRESS=1`, det configuration. `restored` reads `det=1 dual=1`
plus `m7nosup=1`. The mid-Trigger flag flip is observed (not inferred).

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m7-trace | 200 | 6.289 / 14.759 / 4.324 / 19.200 | 3.181 / 3.699 | 373824 / 3181 | YES | seq_wall_ms=2182.289 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m7-trace | dtex | -1 | 1 |
| m7-trace | dpend | 0 | 0 |
| m7-trace | dframe | 1 | 1 |
| m7-trace | dafter | 1 | 1 |
| m7-trace | dafter_live | 1 | 1 |
| m7-trace | dpres | 1 | 1 |
| m7-trace | dimx | 0 | 1 |
| m7-trace | trig_imx | 1 | 1 |
| m7-trace | pediff | 0 | 0 |
| m7-trace | vidiff | 0 | 0 |
```

Sequence absolutes: tex 99→99, pend 0→0, fc 6598→6798, imx 0→1,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=200 seq_after=200 seq_imm=200 seq_vi=0 seq_dup=0
first_imm_pc=13191 first_imm_fc=6595`.

The flip observation (probe registers last on the live bus, so it fires after
the config-refresh listener inside the same Trigger; `HookableEvent::Trigger`
fires in registration order):

| replay | dimx | trig_imx | dpres | dframe | dafter | dafter_live |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 1 | 1 | 1 | 1 | 1 |
| 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| 2 | 0 | 1 | 1 | 1 | 1 | 1 |
| 199 | 0 | 1 | 1 | 1 | 1 | 1 |

Recorded without verdict: replay 0 entered with `imxfb=0` (`imx0=0`, sequence
set false pre-loop) and the in-Trigger probe sampled 1; `dimx==1` exactly once
in the run, at replay 0. `dafter_live=1/1` on all 200 replays (live delivery);
`dpres=+1` and `seq_imm=200` with `seq_vi=0 seq_dup=0` (the post-Trigger
present branch fired Immediate each replay); `dframe=+1` × 200 (M5's +1
reproduced unsuppressed); `resume fc − fc0 = 200`. `dtex` −1/+1 with net 0
over 200 replays (eviction resumed, vs frozen 0/+1 suppressed).
`xfb_equal_scratch=200/200` and `live_xfb_untouched=1` hold unsuppressed.

## Per-step wall table (baseline vs no-op vs delta)

```
| Arm | Replays | Wall med / p95 / min / max (ms) | Thread-CPU med / p95 (ms) | Frame B / updates | done | seq wall |
| --- | ---: | --- | --- | --- | :-: | --- |
| m7-baseline | 200 | 4.332 / 7.479 / 4.233 / 7.817 | 2.156 / 2.203 | 406924 / 3428 | YES | seq_wall_ms=1332.415 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m7-noop | 200 | 3.429 / 4.437 / 3.154 / 7.740 | 2.090 / 2.239 | 401494 / 3485 | YES | seq_wall_ms=1039.629 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
| m7-delta | 200 | 3.607 / 4.439 / 3.144 / 6.690 | 2.032 / 2.186 | 360159 / 3177 | YES | seq_wall_ms=1147.528 completed=200 xfb_equal=200/200 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_equal_scratch=200/200 live_xfb_untouched=1 live_same=200/200 |
```

Frames differ per run (360159 … 406924 B), so wall medians are not comparable
across rows as mechanism costs (M5 §Per-step wall table). All three rows:
200/200 rows, `done`, `restored det=1 dual=1`, `mask_bp=2 dls=0 walk=100%
unknown=0 benign=1` in all runs.

## Per-phase medians

```
| Arm | mem_ms med | cp_ms med | pre_ms med | run_ms med (execute+GPU idle) | sync_ms med | run_ms p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m7-baseline | 0.111 | 0.001 | 0.037 | 4.181 | 0.000 | 7.323 |
| m7-single | 0.130 | 0.001 | 0.000 | 4.960 | 0.000 | 9.664 |
| m7-trace | 0.257 | 0.001 | 0.058 | 5.790 | 0.000 | 14.410 |
| m7-noop | 0.088 | 0.001 | 0.033 | 3.304 | 0.001 | 4.285 |
| m7-delta | 0.098 | 0.001 | 0.035 | 3.473 | 0.001 | 4.291 |
| m7-off | n/a | n/a | n/a | n/a | n/a | n/a |
```

## Aux budget per run (from `restored`)

| Run | `indexed` | `aux_bytes` | 2 MiB / `aux_bytes` |
| --- | ---: | ---: | ---: |
| m7-baseline | 1446 | 69408 | 30.2 |
| m7-single | 1946 | 93408 | 22.5 |
| m7-trace | 2477 | 118896 | 17.6 |
| m7-noop | 1487 | 71376 | 29.4 |
| m7-delta | 1741 | 83568 | 25.1 |

## Step 2 — no-op transform parity

Mechanism: `SSX_M7_XFORM=full` installs the bare `NoopTransform` (S2 arm-2
shape) before replay 0 instead of at replay 100; `restored` reads `m7xform=1`.
All 200 rows tag `xform=1` (`xform=0` count n/a).

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m7-noop | dtex | 0 | 1 |
| m7-noop | dpend | 0 | 0 |
| m7-noop | dframe | 0 | 0 |
| m7-noop | dafter | 1 | 1 |
| m7-noop | dafter_live | 0 | 0 |
| m7-noop | dpres | 0 | 0 |
| m7-noop | dimx | 0 | 0 |
| m7-noop | trig_imx | 0 | 0 |
| m7-noop | pediff | 0 | 0 |
| m7-noop | vidiff | 0 | 0 |
```

Sequence absolutes: tex 103→104, pend 0→0, fc 6949→6949, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=13893 first_imm_fc=6946` (step-3 tracing replicates). The
continuation `resume_xfb` listener fired normally (see §Continuation check).

Recorded without verdict: original-frame equality holds
(`xfb_equal_scratch=200/200`); every M6 counter is identical to baseline
(`dtex` 0/+1 included); `trig_imx=0` on all 200 rows (no in-Trigger flip while
suppressed — the negative control for gap 3's `trig_imx=1`).

Wall delta vs baseline (S2: unmeasurable). Cross-run medians: 3.429 ms
(full no-op, 401494 B frame) vs 4.332 ms (baseline half no-op, 406924 B
frame) — tabulated as observed, with the frame-size caveat above. The
same-frame, same-run half splits (`xform=1` ⟺ replay ≥ 100, so halves are
also first/second 100):

| Arm | xform=0 wall med / p95 (ms) | xform=1 wall med / p95 (ms) | xform=0 run_ms med | xform=1 run_ms med |
| --- | --- | --- | ---: | ---: |
| m7-baseline | 4.345 / 7.473 (n=100) | 4.324 / 7.498 (n=100) | 4.194 | 4.172 |
| m7-single | 5.120 / 9.798 (n=100) | 4.210 / 9.099 (n=100) | 4.988 | 4.101 |
| m7-trace | 6.351 / 14.759 (n=100) | 6.266 / 14.687 (n=100) | 5.797 | 5.790 |
| m7-noop | n/a | 3.429 / 4.437 (n=200) | n/a | 3.304 |
| m7-delta | n/a | 3.607 / 4.439 (n=200) | n/a | 3.473 |

## Step 3 — camera-delta transform

Recorded choice: +0.1f translation on XF mem word 0x003 (position-matrix slot
0, row 0, 4th column = tx; row-major 3x4 — `VertexShaderManager` reads slots
as `posMatrices[idx*4]`), applied whenever a seam-covered write includes that
word. The projection matrix lives in XF regs (0x1020+), where `LoadXFReg`
never fires the seam (`XFStructs.cpp:246-247` is inside the XF-mem branch
only), so slot 0's tx is the camera-most word the seam can reach. Installed
via `SSX_M7_XFORM=delta`; `restored` reads `m7xform=2`; all 200 rows tag
`xform=1`.

Seam-application receipt (`xform_stats`, delta mode only):

| Field | Value |
| --- | --- |
| `mode` | 2 |
| `calls` | 348200 (1741/replay = the run's `indexed` count: every indexed load fired the seam) |
| `hits` | 30400 (152/replay covering word 0x003) |

Pixel quantification (per-replay scratch-vs-live-original diff over 573440
bytes; `xdiff` = differing bytes, `xdmax` = max abs byte diff, `xdmean` =
mean abs byte diff over differing bytes):

| Arm | differing frames (`200 − xfb_scratch_equal`) | xdiff min / max / mean | xdmax min / max | xdmean min / max |
| --- | ---: | --- | ---: | --- |
| m7-delta | 0 | 0 / 0 / 0 | 0 / 0 | 0.000 / 0.000 |

Sample rows (replay: xdiff/xdmax/xdmean): 0: 0/0/0.000, 1: 0/0/0.000,
100: 0/0/0.000, 199: 0/0/0.000.

```
| Arm | counter | min | max |
| --- | --- | ---: | ---: |
| m7-delta | dtex | 0 | 1 |
| m7-delta | dpend | 0 | 0 |
| m7-delta | dframe | 0 | 0 |
| m7-delta | dafter | 1 | 1 |
| m7-delta | dafter_live | 0 | 0 |
| m7-delta | dpres | 0 | 0 |
| m7-delta | dimx | 0 | 0 |
| m7-delta | trig_imx | 0 | 0 |
| m7-delta | pediff | 0 | 0 |
| m7-delta | vidiff | 0 | 0 |
```

Sequence absolutes: tex 104→105, pend 0→0, fc 6845→6845, imx 0→0,
`completed=200`. `present_trace`: `pre_before=3 pre_after=3 pre_imm=3 pre_vi=0
pre_dup=0 seq_before=0 seq_after=0 seq_imm=0 seq_vi=0 seq_dup=0
first_imm_pc=13685 first_imm_fc=6842`. The continuation `resume_xfb` listener
fired normally (see §Continuation check).

Recorded without verdict: `done` stands (watched-window re-hash clean);
`xfb_equal=200/200` (live range untouched) and `live_xfb_untouched=1`; guest
state unchanged (`pediff`/`vidiff` 0/0); event state unchanged
(`dafter_live`/`dframe`/`dpres`/`dimx` 0/0, `trig_imx` 0/0); the delta perturbed
xfmem 152 times per replay yet 0 of 200 replayed frames differ from the
original by any byte, with no drift across replays (xdiff flat 0 on rows
0…199). No leak into guest or event state is observed.

## Continuation check

| Run | `record_start` seam fc | `resume_xfb` |
| --- | --- | --- |
| m7-baseline | `fc=6742` | `replay_disabled=0 fc=6745 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m7-single | `fc=8170` | `replay_disabled=0 fc=8173 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m7-off | `replay_disabled=1 fc=6813` | `replay_disabled=1 fc=6813 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m7-trace | `fc=6595` | `replay_disabled=0 fc=6798 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m7-noop | `fc=6946` | `replay_disabled=0 fc=6949 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |
| m7-delta | `fc=6842` | `replay_disabled=0 fc=6845 ok=1 xfb_addr=0x004dc660 xfb_bytes=573440 xfb_hash=0cbfe49a0d4ee325` |

Per the M5 brief's rule the hash comparison is skipped (seams differ); the
sextuple-identical `resume_xfb` hash (`0cbfe49a0d4ee325`, same address and
size, also identical to all M6 sequence hashes and all three M5
sequence/disabled hashes) is tabulated as observed. `resume fc − fc0` equals
the per-replay `dframe` sum in each run (0 / 0 / n/a-disabled / 200 / 0 / 0).

## Exact commands

Builds (any time; only the header path differs from
`local/research/M6/build_replay_player.py`):

```
python3 local/research/M7/build_replay_player.py local/research/M7/players/m7-baseline
python3 local/research/M7/build_replay_player.py local/research/M7/players/m7-nosuppress
python3 local/research/M7/build_replay_player.py local/research/M7/players/m7-xform
python3 local/research/M7/build_replay_player.py local/research/M7/players/m7-delta
```

Runs (only while `/tmp/ssx3-host-lease` absent; claim `printf 'M7\n'`, remove after
each run; profiles fresh per run):

```
SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-baseline-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-det --cpu-thread --output "/Volumes/Extreme SSD/m7/m7-baseline-run" --seconds 240
SSX_NATIVE_REPLAY=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-single-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-single --output "/Volumes/Extreme SSD/m7/m7-single-run" --seconds 240
SSX_NATIVE_REPLAY=0 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-off-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-baseline --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-off --cpu-thread --output "/Volumes/Extreme SSD/m7/m7-off-run" --seconds 240
SSX_M7_NO_SUPPRESS=1 SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-trace-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-nosuppress --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-det2 --cpu-thread --output "/Volumes/Extreme SSD/m7/m7-trace-run" --seconds 240
SSX_M7_XFORM=full SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-noop-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-xform --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-det3 --cpu-thread --output "/Volumes/Extreme SSD/m7/m7-noop-run" --seconds 240
SSX_M7_XFORM=delta SSX_NATIVE_REPLAY=1 SSX_S2_FORCE_DETERMINISM=1 SSX_NATIVE_PROBE="/Volumes/Extreme SSD/m7/m7-delta-probe.jsonl" python3 tools/gamecube_schedule_check.py --player-dir local/research/M7/players/m7-delta --immediate-xfb --resolution 640x528 --game local/game/gxbe69-stock --profile m7-det4 --cpu-thread --output "/Volumes/Extreme SSD/m7/m7-delta-run" --seconds 240
```

Analysis:

```
python3 local/research/M7/analyze.py "m7-baseline=/Volumes/Extreme SSD/m7/m7-baseline-probe.jsonl" "m7-single=/Volumes/Extreme SSD/m7/m7-single-probe.jsonl" "m7-off=/Volumes/Extreme SSD/m7/m7-off-probe.jsonl" "m7-trace=/Volumes/Extreme SSD/m7/m7-trace-probe.jsonl" "m7-noop=/Volumes/Extreme SSD/m7/m7-noop-probe.jsonl" "m7-delta=/Volumes/Extreme SSD/m7/m7-delta-probe.jsonl"
```

## Player and run dir paths

Evidence dir (committed): `local/research/M7/` — `m7_replay_context.h`
(`0bfc4860…`), `build_replay_player.py`, `analyze.py`, `REPORT.md`, `waits.log`.

Large outputs (not committed): `/Volumes/Extreme SSD/m7/` —
`m7-baseline-probe.jsonl`, `m7-single-probe.jsonl`, `m7-off-probe.jsonl`,
`m7-trace-probe.jsonl`, `m7-noop-probe.jsonl`, `m7-delta-probe.jsonl` (~21 MB
each) and the matching `-run` dirs; per-step header snapshots
`m7_replay_context.step1.h`, `m7_replay_context.step1b.h`,
`m7_replay_context.step2.h`, `m7_replay_context.step3.h` (= committed header).
Players (gitignored): `local/research/M7/players/{m7-baseline,m7-nosuppress,
m7-xform,m7-delta}/` (each with `player`, `build.json`, launchers). All paths
above are symlink-free as written (`realpath` identical).

Build receipts (`build.json` per player: `s2_header_sha256` / `player_sha256`,
12-char prefixes): `m7-baseline` `e89ca9b8a487` / `7794ff889ef8`,
`m7-nosuppress` `206f7aae3d87` / `866b979eb4f2`, `m7-xform` `4171b752eb3b` /
`8859b8d3aa47`, `m7-delta` `0bfc48602573` / `e41afcc3b33a`.

## What I could not do

- The unsuppressed gap run could not run on the unmodified step-1 player (the
  M6 header's scoped-bus install is unconditional, so no unsuppressed
  configuration exists on that binary). The gap is closed with the step-1b
  env-gated player instead (`SSX_M7_NO_SUPPRESS=1`; default = M6 behavior);
  see §Baseline note and §Header diffs, step 1b.
- Player dirs are under `local/research/M7/players/` rather than the SSD: the
  build driver refuses outputs outside `local/`, and the brief orders changing
  only the header path it compiles in. Run dirs and all >5 MB probes are on
  the SSD as ordered.
- Desktop only; no device work.

## Files

Committed under `local/research/M7/`: `m7_replay_context.h` (research header,
`0bfc4860…`), `build_replay_player.py` (M6 driver, header path only),
`analyze.py` (M6 tables unchanged + M7 `trig_imx`/`xdiff`/`xdmax`/`xdmean`
deltas, xform-half wall split, trig_imx distribution, `xform_stats` lines;
missing keys print as n/a), `REPORT.md` (this file), `waits.log` (lease
claims and releases; no waits, no polls).

## Header diffs per step (`diff -u` against the M6 header)

Step 1: empty (verbatim copy). Steps 1b–3 follow, cumulative per step,
generated from `/Volumes/Extreme SSD/m7/m7_replay_context.step{1b,2}.h` and
the committed `local/research/M7/m7_replay_context.h` (= step 3).

### Step 1b

```diff
--- local/research/M6/m6_replay_context.h	2026-09-18 22:02:31
+++ /Volumes/Extreme SSD/m7/m7_replay_context.step1b.h	2026-09-19 00:34:53
@@ -162,6 +162,16 @@
 // GetVideoEvents() expression), so nothing bypasses the swap. No vendor
 // change, no visibility trick: only public members and public operators.
 static unsigned long long s_after_frame_live = 0;
+// --- M7 step 1b: unsuppressed-with-tracing gap mode ------------------------------
+// Closes M6's unordered unsuppressed run. SSX_M7_NO_SUPPRESS=1 skips the scoped
+// bus install (M5 shape: the header probe registers directly on the live bus,
+// last, so it fires after the 12 live listeners incl. the config refresh; the
+// sentinel also goes on the live bus, so dafter_live=1/1 proves live delivery).
+// Unset (default) = exact M6 behavior. In both modes the probe samples
+// g_ActiveConfig.bImmediateXFB inside the Trigger (HookableEvent fires in
+// registration order); replay 0's fx_before.imxfb=0 vs trig_imx=1 directly
+// observes M6's mid-Trigger flag flip.
+static int s_m7_trig_imx = -1;
 // --- M6 step 3: replay-local frame counter + presenter tracing ----------------
 // FrameCount() can no longer age the replay (step 2 suppresses the only
 // in-sequence writer path), so the header owns its own frame counter,
@@ -894,6 +904,11 @@
   Run(prelude);
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
+  // M7 step 1b: unsuppressed gap mode (default off = M6 behavior).
+  const bool m7_no_suppress = [] {
+    const char* v = std::getenv("SSX_M7_NO_SUPPRESS");
+    return v && std::strcmp(v, "1") == 0;
+  }();
   {
     char detail[448];
     std::snprintf(detail, sizeof(detail),
@@ -901,14 +916,14 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n);
+                  xfb_patch_n, int(m7_no_suppress));
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -920,13 +935,27 @@
   // S2 section-A tension (deferred queue growth, frozen eviction).
   s_after_frame_triggers = 0;
   s_after_frame_live = 0;
+  s_m7_trig_imx = -1;
   auto& m6_bus = system.GetVideoEvents().after_frame_event;
   auto m6_saved_bus = m6_bus;
-  m6_bus = Common::HookableEvent<Core::System&>();
-  Common::EventHook m6_after_frame_hook =
-      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
-  Common::EventHook m6_live_sentinel_hook =
-      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  Common::EventHook m6_after_frame_hook, m6_live_sentinel_hook;
+  if (m7_no_suppress) {
+    // M7 step 1b: M5 shape on the live bus (probe last, sentinel live).
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  } else {
+    m6_bus = Common::HookableEvent<Core::System&>();
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  }
   const SideFx fx_base = CaptureSideFx(system);
   // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
   // stalled from here on, so these reads race nothing) + replay-local frame
@@ -957,6 +986,7 @@
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
   long long min_dafter_live = 0, max_dafter_live = 0;
   long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
+  long long min_trigimx = 0, max_trigimx = 0;  // M7 step 1b: in-Trigger flag sample
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
   const double seq_start = Now();
@@ -970,6 +1000,7 @@
       break;
     }
     const SideFx fx_before = CaptureSideFx(system);
+    s_m7_trig_imx = -1;  // M7 step 1b: this replay's in-Trigger sample (or -1)
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -1047,6 +1078,7 @@
         static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    const long long trigimx = s_m7_trig_imx;  // M7 step 1b
     if (fx_first) {
       min_dtex = max_dtex = dtex;
       min_dpend = max_dpend = dpend;
@@ -1055,6 +1087,7 @@
       min_dafter_live = max_dafter_live = dafter_live;
       min_dpres = max_dpres = dpres;
       min_dimx = max_dimx = dimx;
+      min_trigimx = max_trigimx = trigimx;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -1073,6 +1106,8 @@
       if (dpres > max_dpres) max_dpres = dpres;
       if (dimx < min_dimx) min_dimx = dimx;
       if (dimx > max_dimx) max_dimx = dimx;
+      if (trigimx < min_trigimx) min_trigimx = trigimx;
+      if (trigimx > max_trigimx) max_trigimx = trigimx;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
@@ -1086,13 +1121,14 @@
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
                  "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
+                 "\"trig_imx\":%d,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
                  (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
                  dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
-                 pediff, vidiff, xfb_scratch_equal);
+                 s_m7_trig_imx, pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
@@ -1101,7 +1137,7 @@
   const SideFx fx_end = CaptureSideFx(system);
   m6_after_frame_hook.reset();
   m6_live_sentinel_hook.reset();
-  m6_bus = m6_saved_bus;
+  if (!m7_no_suppress) m6_bus = m6_saved_bus;  // M7 step 1b: bypass never swapped
   if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = false;  // M6 step 4
   // M6 step 3: presenter-tracing receipt (pre = live window from record_start
   // to sequence start; seq = during the sequence), then disarm. Reached on
@@ -1142,6 +1178,7 @@
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
                   "dafter_live_min=%lld dafter_live_max=%lld "
                   "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
+                  "trigimx_min=%lld trigimx_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
@@ -1149,9 +1186,9 @@
                   fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
                   fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
                   max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
-                  min_dpres, max_dpres, min_dimx, max_dimx, min_pe, max_pe, min_vi,
-                  max_vi, int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
-                  live_ok_count, live_same_count);
+                  min_dpres, max_dpres, min_dimx, max_dimx, min_trigimx, max_trigimx,
+                  min_pe, max_pe, min_vi, max_vi, int(xfb_scratch_ok), xfb_scratch_addr,
+                  xfb_scratch_count, live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
   XFReplay::g_transform = saved_transform;
```

### Step 2

```diff
--- local/research/M6/m6_replay_context.h	2026-09-18 22:02:31
+++ /Volumes/Extreme SSD/m7/m7_replay_context.step2.h	2026-09-19 00:40:07
@@ -162,6 +162,16 @@
 // GetVideoEvents() expression), so nothing bypasses the swap. No vendor
 // change, no visibility trick: only public members and public operators.
 static unsigned long long s_after_frame_live = 0;
+// --- M7 step 1b: unsuppressed-with-tracing gap mode ------------------------------
+// Closes M6's unordered unsuppressed run. SSX_M7_NO_SUPPRESS=1 skips the scoped
+// bus install (M5 shape: the header probe registers directly on the live bus,
+// last, so it fires after the 12 live listeners incl. the config refresh; the
+// sentinel also goes on the live bus, so dafter_live=1/1 proves live delivery).
+// Unset (default) = exact M6 behavior. In both modes the probe samples
+// g_ActiveConfig.bImmediateXFB inside the Trigger (HookableEvent fires in
+// registration order); replay 0's fx_before.imxfb=0 vs trig_imx=1 directly
+// observes M6's mid-Trigger flag flip.
+static int s_m7_trig_imx = -1;
 // --- M6 step 3: replay-local frame counter + presenter tracing ----------------
 // FrameCount() can no longer age the replay (step 2 suppresses the only
 // in-sequence writer path), so the header owns its own frame counter,
@@ -894,6 +904,19 @@
   Run(prelude);
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
+  // M7 step 1b: unsuppressed gap mode (default off = M6 behavior).
+  const bool m7_no_suppress = [] {
+    const char* v = std::getenv("SSX_M7_NO_SUPPRESS");
+    return v && std::strcmp(v, "1") == 0;
+  }();
+  // M7 step 2: transform select. Unset = M6 behavior (no-op from replay 100);
+  // SSX_M7_XFORM=full installs the no-op for the full sequence (S2 arm-2
+  // shape). (Step 3 adds the delta mode.)
+  const int m7_xform = [] {
+    const char* v = std::getenv("SSX_M7_XFORM");
+    if (v && std::strcmp(v, "full") == 0) return 1;
+    return 0;
+  }();
   {
     char detail[448];
     std::snprintf(detail, sizeof(detail),
@@ -901,14 +924,14 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -920,13 +943,27 @@
   // S2 section-A tension (deferred queue growth, frozen eviction).
   s_after_frame_triggers = 0;
   s_after_frame_live = 0;
+  s_m7_trig_imx = -1;
   auto& m6_bus = system.GetVideoEvents().after_frame_event;
   auto m6_saved_bus = m6_bus;
-  m6_bus = Common::HookableEvent<Core::System&>();
-  Common::EventHook m6_after_frame_hook =
-      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
-  Common::EventHook m6_live_sentinel_hook =
-      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  Common::EventHook m6_after_frame_hook, m6_live_sentinel_hook;
+  if (m7_no_suppress) {
+    // M7 step 1b: M5 shape on the live bus (probe last, sentinel live).
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  } else {
+    m6_bus = Common::HookableEvent<Core::System&>();
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  }
   const SideFx fx_base = CaptureSideFx(system);
   // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
   // stalled from here on, so these reads race nothing) + replay-local frame
@@ -957,8 +994,12 @@
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
   long long min_dafter_live = 0, max_dafter_live = 0;
   long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
+  long long min_trigimx = 0, max_trigimx = 0;  // M7 step 1b: in-Trigger flag sample
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
+  // M7 step 2: full-sequence no-op (the M6 mid-loop install below is kept;
+  // in full mode its replay-100 reinstall is the same pointer, a no-op).
+  if (m7_xform == 1) XFReplay::g_transform = &NoopTransform;
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -970,6 +1011,7 @@
       break;
     }
     const SideFx fx_before = CaptureSideFx(system);
+    s_m7_trig_imx = -1;  // M7 step 1b: this replay's in-Trigger sample (or -1)
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -1047,6 +1089,7 @@
         static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    const long long trigimx = s_m7_trig_imx;  // M7 step 1b
     if (fx_first) {
       min_dtex = max_dtex = dtex;
       min_dpend = max_dpend = dpend;
@@ -1055,6 +1098,7 @@
       min_dafter_live = max_dafter_live = dafter_live;
       min_dpres = max_dpres = dpres;
       min_dimx = max_dimx = dimx;
+      min_trigimx = max_trigimx = trigimx;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -1073,12 +1117,16 @@
       if (dpres > max_dpres) max_dpres = dpres;
       if (dimx < min_dimx) min_dimx = dimx;
       if (dimx > max_dimx) max_dimx = dimx;
+      if (trigimx < min_trigimx) min_trigimx = trigimx;
+      if (trigimx > max_trigimx) max_trigimx = trigimx;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
       if (vidiff > max_vi) max_vi = vidiff;
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
+    // M7 step 2: tag actual install state (default mode identical to M6).
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1086,13 +1134,14 @@
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
                  "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
+                 "\"trig_imx\":%d,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
+                 (wall_end - t_run) * 1000.0, xform_flag, xfb_equal,
                  dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
-                 pediff, vidiff, xfb_scratch_equal);
+                 s_m7_trig_imx, pediff, vidiff, xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
@@ -1101,7 +1150,7 @@
   const SideFx fx_end = CaptureSideFx(system);
   m6_after_frame_hook.reset();
   m6_live_sentinel_hook.reset();
-  m6_bus = m6_saved_bus;
+  if (!m7_no_suppress) m6_bus = m6_saved_bus;  // M7 step 1b: bypass never swapped
   if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = false;  // M6 step 4
   // M6 step 3: presenter-tracing receipt (pre = live window from record_start
   // to sequence start; seq = during the sequence), then disarm. Reached on
@@ -1142,6 +1191,7 @@
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
                   "dafter_live_min=%lld dafter_live_max=%lld "
                   "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
+                  "trigimx_min=%lld trigimx_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
@@ -1149,9 +1199,9 @@
                   fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
                   fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
                   max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
-                  min_dpres, max_dpres, min_dimx, max_dimx, min_pe, max_pe, min_vi,
-                  max_vi, int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
-                  live_ok_count, live_same_count);
+                  min_dpres, max_dpres, min_dimx, max_dimx, min_trigimx, max_trigimx,
+                  min_pe, max_pe, min_vi, max_vi, int(xfb_scratch_ok), xfb_scratch_addr,
+                  xfb_scratch_count, live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
   XFReplay::g_transform = saved_transform;
```

### Step 3

```diff
--- local/research/M6/m6_replay_context.h	2026-09-18 22:02:31
+++ local/research/M7/m7_replay_context.h	2026-09-19 00:45:24
@@ -162,6 +162,16 @@
 // GetVideoEvents() expression), so nothing bypasses the swap. No vendor
 // change, no visibility trick: only public members and public operators.
 static unsigned long long s_after_frame_live = 0;
+// --- M7 step 1b: unsuppressed-with-tracing gap mode ------------------------------
+// Closes M6's unordered unsuppressed run. SSX_M7_NO_SUPPRESS=1 skips the scoped
+// bus install (M5 shape: the header probe registers directly on the live bus,
+// last, so it fires after the 12 live listeners incl. the config refresh; the
+// sentinel also goes on the live bus, so dafter_live=1/1 proves live delivery).
+// Unset (default) = exact M6 behavior. In both modes the probe samples
+// g_ActiveConfig.bImmediateXFB inside the Trigger (HookableEvent fires in
+// registration order); replay 0's fx_before.imxfb=0 vs trig_imx=1 directly
+// observes M6's mid-Trigger flag flip.
+static int s_m7_trig_imx = -1;
 // --- M6 step 3: replay-local frame counter + presenter tracing ----------------
 // FrameCount() can no longer age the replay (step 2 suppresses the only
 // in-sequence writer path), so the header owns its own frame counter,
@@ -632,6 +642,24 @@
 // non-early-out cost a transformed replay would pay. Rows carry `xform`.
 static void NoopTransform(u16, u32) {}
 static constexpr unsigned kTransformFrom = kReplays / 2;
+// --- M7 step 3: camera-delta transform ----------------------------------------
+// Recorded choice: +0.1f translation on XF mem word 0x003 (position-matrix
+// slot 0, row 0, 4th column = tx; row-major 3x4, VertexShaderManager reads
+// slots as posMatrices[idx*4]), applied whenever a seam-covered write includes
+// that word. Pure function of (address, current value): each replay reloads
+// from identical sources first, so no accumulation across passes or replays.
+// The projection matrix lives in XF regs (0x1020+), where LoadXFReg never
+// fires the seam, so slot 0's tx is the camera-most word the seam can reach.
+static unsigned long long s_m7_xform_calls = 0;
+static unsigned long long s_m7_xform_hits = 0;
+static void M7DeltaTransform(u16 address, u32 count) {
+  ++s_m7_xform_calls;
+  if (address <= 0x003 && 0x003 < address + count) {
+    float* w = &xfmem.posMatrices[3];
+    *w += 0.1f;
+    ++s_m7_xform_hits;
+  }
+}
 
 static inline void Step(CPUState& c) {
   NativeSchedule::Step(c);
@@ -894,6 +922,20 @@
   Run(prelude);
   CopyPreprocessCPStateFromMain();
   VertexLoaderManager::MarkAllDirty();
+  // M7 step 1b: unsuppressed gap mode (default off = M6 behavior).
+  const bool m7_no_suppress = [] {
+    const char* v = std::getenv("SSX_M7_NO_SUPPRESS");
+    return v && std::strcmp(v, "1") == 0;
+  }();
+  // M7 step 2: transform select. Unset = M6 behavior (no-op from replay 100);
+  // SSX_M7_XFORM=full installs the no-op for the full sequence (S2 arm-2
+  // shape); SSX_M7_XFORM=delta installs the step-3 camera delta.
+  const int m7_xform = [] {
+    const char* v = std::getenv("SSX_M7_XFORM");
+    if (v && std::strcmp(v, "full") == 0) return 1;
+    if (v && std::strcmp(v, "delta") == 0) return 2;
+    return 0;
+  }();
   {
     char detail[448];
     std::snprintf(detail, sizeof(detail),
@@ -901,14 +943,14 @@
                   "aux_bytes=%u walk=%u/%zu unknown=%u benign=%u "
                   "xfb_copies=%u xfb_addr=0x%08x xfb_bytes=%u xfb_ref_ok=%d "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_patch_bad=%d "
-                  "efb_total=%u xfb_patch_n=%u",
+                  "efb_total=%u xfb_patch_n=%u m7nosup=%d m7xform=%d",
                   int(deterministic), int(system.IsDualCoreMode()), mask.masked,
                   mask.display_lists, mask.dl_bytes, mask.indexed,
                   mask.indexed_bytes + mask.dl_bytes, mask.consumed, frame.size(),
                   mask.unknown, mask.benign_unknown, mask.xfb.copies, mask.xfb.addr,
                   mask.xfb.bytes, int(xfb_ref_ok), int(xfb_scratch_ok),
                   xfb_scratch_addr, int(xfb_patch_bad), mask.efb_copies_total,
-                  xfb_patch_n);
+                  xfb_patch_n, int(m7_no_suppress), m7_xform);
     Event("restored", detail);
   }
   auto* const saved_transform = XFReplay::g_transform;
@@ -920,13 +962,27 @@
   // S2 section-A tension (deferred queue growth, frozen eviction).
   s_after_frame_triggers = 0;
   s_after_frame_live = 0;
+  s_m7_trig_imx = -1;
   auto& m6_bus = system.GetVideoEvents().after_frame_event;
   auto m6_saved_bus = m6_bus;
-  m6_bus = Common::HookableEvent<Core::System&>();
-  Common::EventHook m6_after_frame_hook =
-      m6_bus.Register([](Core::System&) { ++s_after_frame_triggers; });
-  Common::EventHook m6_live_sentinel_hook =
-      m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  Common::EventHook m6_after_frame_hook, m6_live_sentinel_hook;
+  if (m7_no_suppress) {
+    // M7 step 1b: M5 shape on the live bus (probe last, sentinel live).
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  } else {
+    m6_bus = Common::HookableEvent<Core::System&>();
+    m6_after_frame_hook = m6_bus.Register([](Core::System&) {
+      ++s_after_frame_triggers;
+      s_m7_trig_imx = g_ActiveConfig.bImmediateXFB ? 1 : 0;
+    });
+    m6_live_sentinel_hook =
+        m6_saved_bus.Register([](Core::System&) { ++s_after_frame_live; });
+  }
   const SideFx fx_base = CaptureSideFx(system);
   // M6 step 3: presenter-tracing snapshot at sequence start (video thread is
   // stalled from here on, so these reads race nothing) + replay-local frame
@@ -957,8 +1013,17 @@
   long long min_dframe = 0, max_dframe = 0, min_dafter = 0, max_dafter = 0;
   long long min_dafter_live = 0, max_dafter_live = 0;
   long long min_dpres = 0, max_dpres = 0, min_dimx = 0, max_dimx = 0;
+  long long min_trigimx = 0, max_trigimx = 0;  // M7 step 1b: in-Trigger flag sample
   long long min_pe = 0, max_pe = 0, min_vi = 0, max_vi = 0;
   bool fx_first = true;
+  // M7 steps 2-3: pre-loop install for full/delta modes (the M6 mid-loop
+  // install below now runs in default mode only; same behavior there).
+  if (m7_xform == 1) XFReplay::g_transform = &NoopTransform;
+  if (m7_xform == 2) {
+    s_m7_xform_calls = 0;
+    s_m7_xform_hits = 0;
+    XFReplay::g_transform = &M7DeltaTransform;
+  }
   const double seq_start = Now();
   for (replays = 0; replays < kReplays; ++replays) {
     // M5 step 3, fail-closed: the recorder must be idle; a replay that
@@ -970,6 +1035,7 @@
       break;
     }
     const SideFx fx_before = CaptureSideFx(system);
+    s_m7_trig_imx = -1;  // M7 step 1b: this replay's in-Trigger sample (or -1)
     const double wall_start = Now();
     const double cpu_start = ThreadCpuMs();
     // Restore before EVERY replay: recorded memory updates and TMEM (the
@@ -977,7 +1043,8 @@
     // vertex/palette regions), then the recorded CP registers into both CP
     // states so the execute and preprocess passes start from identical array
     // bases, strides and VATs.
-    if (replays == kTransformFrom) XFReplay::g_transform = &NoopTransform;
+    if (replays == kTransformFrom && m7_xform == 0)
+      XFReplay::g_transform = &NoopTransform;  // M7 step 3: default mode only
     ApplyMemory(system, file);
     const double t_mem = Now();
     Run(cp_prelude);
@@ -1028,6 +1095,27 @@
       }
     }
     xfb_scratch_count += unsigned(xfb_scratch_equal);
+    // M7 step 3: per-replay pixel-diff stats (scratch = this replay's frame,
+    // live range = the untouched original). After wall_end, out of wall_ms.
+    unsigned xdiff = 0;
+    int xdmax = 0;
+    double xdmean = 0.0;
+    if (xfb_scratch_ok) {
+      u8* xdp = live_memory.GetPointerForRange(xfb_scratch_addr, mask.xfb.bytes);
+      u8* xlp = live_memory.GetPointerForRange(mask.xfb.addr, mask.xfb.bytes);
+      if (xdp && xlp) {
+        unsigned long long xdacc = 0;
+        for (u32 i = 0; i < mask.xfb.bytes; ++i) {
+          const int dd = xdp[i] > xlp[i] ? xdp[i] - xlp[i] : xlp[i] - xdp[i];
+          if (dd > 0) {
+            ++xdiff;
+            xdacc += (unsigned)dd;
+            if (dd > xdmax) xdmax = dd;
+          }
+        }
+        if (xdiff > 0) xdmean = double(xdacc) / double(xdiff);
+      }
+    }
     // M5 step 3: after-state and deltas. Captured after wall_end so the
     // capture cost stays out of wall_ms. Nothing is suppressed: it measures.
     const SideFx fx_after = CaptureSideFx(system);
@@ -1047,6 +1135,7 @@
         static_cast<long long>(fx_after.imxfb) - static_cast<long long>(fx_before.imxfb);
     const long long pediff = static_cast<long long>(DiffBytes(fx_before.pe_state, fx_after.pe_state));
     const long long vidiff = static_cast<long long>(DiffBytes(fx_before.vi_state, fx_after.vi_state));
+    const long long trigimx = s_m7_trig_imx;  // M7 step 1b
     if (fx_first) {
       min_dtex = max_dtex = dtex;
       min_dpend = max_dpend = dpend;
@@ -1055,6 +1144,7 @@
       min_dafter_live = max_dafter_live = dafter_live;
       min_dpres = max_dpres = dpres;
       min_dimx = max_dimx = dimx;
+      min_trigimx = max_trigimx = trigimx;
       min_pe = max_pe = pediff;
       min_vi = max_vi = vidiff;
       fx_first = false;
@@ -1073,12 +1163,16 @@
       if (dpres > max_dpres) max_dpres = dpres;
       if (dimx < min_dimx) min_dimx = dimx;
       if (dimx > max_dimx) max_dimx = dimx;
+      if (trigimx < min_trigimx) min_trigimx = trigimx;
+      if (trigimx > max_trigimx) max_trigimx = trigimx;
       if (pediff < min_pe) min_pe = pediff;
       if (pediff > max_pe) max_pe = pediff;
       if (vidiff < min_vi) min_vi = vidiff;
       if (vidiff > max_vi) max_vi = vidiff;
     }
     ++s_m6_frame;  // one emitted capacity row = one replayed frame
+    // M7 step 2: tag actual install state (default mode identical to M6).
+    const int xform_flag = int(replays >= kTransformFrom || m7_xform != 0);
     std::fprintf(Output(),
                  "{\"event\":\"replay\",\"schema\":2,\"action\":\"capacity\","
                  "\"wall\":%.6f,\"replay\":%u,\"wall_ms\":%.3f,\"cpu_ms\":%.3f,"
@@ -1086,13 +1180,15 @@
                  "\"sync_ms\":%.3f,\"xform\":%d,\"xfb_equal\":%d,"
                  "\"dtex\":%lld,\"dpend\":%lld,\"dframe\":%lld,\"dafter\":%lld,"
                  "\"dafter_live\":%lld,\"m6frame\":%llu,\"dpres\":%lld,\"dimx\":%lld,"
+                 "\"trig_imx\":%d,\"xdiff\":%u,\"xdmax\":%d,\"xdmean\":%.3f,"
                  "\"pediff\":%lld,\"vidiff\":%lld,\"xfb_scratch\":%d,\"render_execution\":true}\n",
                  wall_end, replays, replay_wall_ms[replays], replay_cpu_ms[replays],
                  (t_mem - wall_start) * 1000.0, (t_cp - t_mem) * 1000.0,
                  (t_pre - t_cp) * 1000.0, (t_run - t_pre) * 1000.0,
-                 (wall_end - t_run) * 1000.0, int(replays >= kTransformFrom), xfb_equal,
+                 (wall_end - t_run) * 1000.0, xform_flag, xfb_equal,
                  dtex, dpend, dframe, dafter, dafter_live, s_m6_frame, dpres, dimx,
-                 pediff, vidiff, xfb_scratch_equal);
+                 s_m7_trig_imx, xdiff, xdmax, xdmean, pediff, vidiff,
+                 xfb_scratch_equal);
     std::fflush(Output()); // every row survives a post-loop death.
   }
   const double seq_end = Now();
@@ -1101,7 +1197,7 @@
   const SideFx fx_end = CaptureSideFx(system);
   m6_after_frame_hook.reset();
   m6_live_sentinel_hook.reset();
-  m6_bus = m6_saved_bus;
+  if (!m7_no_suppress) m6_bus = m6_saved_bus;  // M7 step 1b: bypass never swapped
   if (m6_arm_record) OpcodeDecoder::g_record_fifo_data = false;  // M6 step 4
   // M6 step 3: presenter-tracing receipt (pre = live window from record_start
   // to sequence start; seq = during the sequence), then disarm. Reached on
@@ -1142,6 +1238,7 @@
                   "dframe_min=%lld dframe_max=%lld dafter_min=%lld dafter_max=%lld "
                   "dafter_live_min=%lld dafter_live_max=%lld "
                   "dpres_min=%lld dpres_max=%lld dimx_min=%lld dimx_max=%lld "
+                  "trigimx_min=%lld trigimx_max=%lld "
                   "pediff_min=%lld pediff_max=%lld vidiff_min=%lld vidiff_max=%lld "
                   "xfb_scratch_ok=%d xfb_scratch_addr=0x%08x xfb_scratch_equal=%u "
                   "live_ok=%u live_same=%u",
@@ -1149,11 +1246,20 @@
                   fx_end.tex_entries, fx_end.pending, fx_end.frame_count, fx_base.imxfb,
                   fx_end.imxfb, min_dtex, max_dtex, min_dpend, max_dpend, min_dframe,
                   max_dframe, min_dafter, max_dafter, min_dafter_live, max_dafter_live,
-                  min_dpres, max_dpres, min_dimx, max_dimx, min_pe, max_pe, min_vi,
-                  max_vi, int(xfb_scratch_ok), xfb_scratch_addr, xfb_scratch_count,
-                  live_ok_count, live_same_count);
+                  min_dpres, max_dpres, min_dimx, max_dimx, min_trigimx, max_trigimx,
+                  min_pe, max_pe, min_vi, max_vi, int(xfb_scratch_ok), xfb_scratch_addr,
+                  xfb_scratch_count, live_ok_count, live_same_count);
     Event("counters_summary", summary);
   }
+  // M7 step 3: seam-application receipt (delta mode only; the bare no-op is
+  // uncounted by design). calls = seam invocations during the sequence,
+  // hits = writes covering the delta word.
+  if (m7_xform == 2) {
+    char xs[128];
+    std::snprintf(xs, sizeof(xs), "mode=%d calls=%llu hits=%llu", m7_xform,
+                  s_m7_xform_calls, s_m7_xform_hits);
+    Event("xform_stats", xs);
+  }
   XFReplay::g_transform = saved_transform;
   g_ActiveConfig.bImmediateXFB = true;
   RestoreLive(live);
```
