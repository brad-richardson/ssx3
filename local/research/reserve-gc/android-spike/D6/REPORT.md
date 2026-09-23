# D6 — Odin race-window profile and per-callback split at stock clocks: REPORT

Question: on the Odin at stock clocks, inside a screenshot-anchored RACE
window, (1) the emulation thread's time split, (2) per-callback CPU/wall
medians and p95. Tables only, no verdicts.

## Gate and method

D5/REPORT.md present; `/data/local/tmp/mg/LEASE` absent and no
moderngekko process at claim. Lease `D6` claimed before the first arm
(removed at the end; device left with 0 procs). Same device rules as
D1b/D5: every `cpu-*` zone < 50 °C before each arm (elapsed below), kill
only on any zone ≥ 110 °C or cpu7 < 2.0 GHz > 5 consecutive ticks (never
triggered; monitored on every arm), per-arm `performance_mode`/`fan_mode`/
caps recorded, settings never changed (mode=1 fan=4 cpu7max=4320000
cpu0max=3532800 throughout).

Launch shape for the perf arms is D1 `d1-base-a` verbatim (pace binary
`D1/moderngekko-run-pace-egl` sha `84de2c226c87d831`, `--template aff-tpl
--movie m3-menu.dtm --module gGXBE69_recomp.so --graphics OGL --idle on
--affinity emu=80,video=40 --sampler --screenshot-seconds 2 --timeout 300
--serial 622c49b1`). Module on device throughout: `gGXBE69_recomp.so`
sha `1c6c89cf79c2cb35` (HEAD module, same as D5).

simpleperf method (M7 recipe adapted): on-device trigger script
(`D6/d6-trigger.sh`, M7 `trigger-place.sh` pattern) waits for
`sample=45` in the live `<tag>.err`, captures placement via
`ps -T -p PID -o tid,psr,pri,comm`, selects the emu thread by affinity
mask == 80 (refuses to profile otherwise), then runs
`simpleperf record -p EMU_PID -t EMU_TID -e cpu-clock -f 4000 -g
--duration 120` (120 s is a backstop only), waits for `sample=60`,
SIGINTs simpleperf. Reports below are host-side
(`android-ndk/simpleperf/bin/darwin/x86_64/simpleperf report`) on the
pulled `perf.data`, emu thread isolated with `--tids`.

## Arms

| arm | binary sha | template/movie | pre-launch | wait | capture (device clock) | shutdown counters |
|---|---|---|---|---|---|---|
| d6-perf-a | 84de2c22 | aff-tpl / m3-menu.dtm | mode=1 fan=4 | CLEAR 48.8C | TID 14226 (mask 80 = run.json emu TID), samples 45→60, 14.1353 s, 70,140 total / 50,610 emu, 0 lost, 11.17 MB | native_exc=433510 hook_fb=438074 |
| d6-perf-b | 84de2c22 | aff-tpl / m3-menu.dtm | mode=1 fan=4 | CLEAR 48.0C | TID 19398 (mask 80 = run.json emu TID), samples 45→60, 15.1511 s, 75,093 total / 54,104 emu, 0 lost, 11.96 MB | native_exc=436440 hook_fb=438580 |
| d6-probe | 220488ca | m6h / m3-menu-imm.dtm | mode=1 fan=4 | CLEAR 49.9C | trial smooth AT=112.0 SECS=12, imm_xfb=1, full lifecycle, 303/303 blended, guest-clean | native_exc=186616 hook_fb=395840 |

Three earlier perf attempts were voided (no data kept): monitor-gap
miss, wrong-thread capture (psr-parse bug, TID 769 AsyncShaderComp),
and a trigger/runner ordering miss. Full notes in `D6/run-notes.log`;
only the three arms above are the deliverable.

## Per-arm race anchors (screenshot-verified, HUD timer visible)

- d6-perf-a: GO! 0:00 4th/6 @02:31:46, 0:10 5th/6 5% 52 MPH @02:31:54,
  pause menu (MCOMM −12 °C) @02:31:58 and :00. Perf bracket 02:31:45–
  02:32:00 starts at the gate shot and ends ≤2 s into the pause menu.
  Pace 13/13 ≈ 1.0 wall-measured over the bracket (race ≈ 13 s wall).
- d6-perf-b: GO! 0:00 4th/6 @02:38:05, 0:07 5th/6 3% 46 MPH @02:38:11,
  pause menu @02:38:17 and :19. Perf bracket 02:38:04–02:38:19, same
  shape (starts at gate, ≤2–4 s pause sliver at tail).
- d6-probe: ZERO emulator screenshots (trial-lse binary has the dead
  shot path, like M4's LSE arms). Anchor by substitution: D1 `capped1x`
  (same m6h template) gate ~+110 s driver with race shots 0:07–0:15,
  the imm movie's documented same-timeline property, and this run's own
  engagement evidence (below): trial window driver 112–124 with all 707
  update rows `position_changed=1`, speeds locked 1.0, full lifecycle.

## Symbol tables (emu thread only, flat, top 25)

d6-perf-a (50,610 samples):

| % | dso | symbol |
|---|---|---|
| 8.14 | gGXBE69_recomp.so | func_802197A0 |
| 6.33 | gGXBE69_recomp.so | func_8022D7A0 |
| 3.56 | moderngekko-run-trial | StaticRecompCore::Run() |
| 3.07 | gGXBE69_recomp.so | func_801097A0 |
| 3.00 | gGXBE69_recomp.so | func_802317A0 |
| 2.73 | gGXBE69_recomp.so | func_8021D7A0 |
| 2.67 | gGXBE69_recomp.so | func_801A57A0 |
| 2.43 | gGXBE69_recomp.so | func_802697A0 |
| 2.40 | moderngekko-run-trial | StaticRecompCore::HookExternalWrite(CPUState*, unsigned int, unsigned long, unsigned char) |
| 2.21 | gGXBE69_recomp.so | func_802157A0 |
| 1.89 | gGXBE69_recomp.so | func_8029D7A0 |
| 1.79 | gGXBE69_recomp.so | func_8020D7A0 |
| 1.72 | [kernel.kallsyms] | [kernel.kallsyms][+ffffffec2688e810] |
| 1.70 | gGXBE69_recomp.so | chassis_dispatch |
| 1.69 | gGXBE69_recomp.so | func_801C17A0 |
| 1.51 | gGXBE69_recomp.so | func_802217A0 |
| 1.41 | moderngekko-run-trial | GPFifo::GPFifoManager::CheckGatherPipe() |
| 1.41 | gGXBE69_recomp.so | func_802357A0 |
| 1.39 | gGXBE69_recomp.so | func_802297A0 |
| 1.38 | gGXBE69_recomp.so | func_802A17A0 |
| 1.28 | gGXBE69_recomp.so | dolrecomp_f32_from_bits_slow |
| 1.22 | gGXBE69_recomp.so | func_802117A0 |
| 1.18 | gGXBE69_recomp.so | func_801E17A0 |
| 1.17 | moderngekko-run-trial | __aarch64_swp4_acq_rel |
| 1.05 | gGXBE69_recomp.so | func_800257A0 |

d6-perf-b (54,104 samples):

| % | dso | symbol |
|---|---|---|
| 8.39 | gGXBE69_recomp.so | func_802197A0 |
| 6.38 | gGXBE69_recomp.so | func_8022D7A0 |
| 3.62 | moderngekko-run-trial | StaticRecompCore::Run() |
| 3.10 | gGXBE69_recomp.so | func_801097A0 |
| 2.99 | gGXBE69_recomp.so | func_802317A0 |
| 2.70 | gGXBE69_recomp.so | func_8021D7A0 |
| 2.62 | gGXBE69_recomp.so | func_801A57A0 |
| 2.46 | gGXBE69_recomp.so | func_802697A0 |
| 2.31 | moderngekko-run-trial | StaticRecompCore::HookExternalWrite(CPUState*, unsigned int, unsigned long, unsigned char) |
| 2.24 | gGXBE69_recomp.so | func_802157A0 |
| 1.91 | gGXBE69_recomp.so | func_8020D7A0 |
| 1.81 | gGXBE69_recomp.so | func_8029D7A0 |
| 1.70 | gGXBE69_recomp.so | func_801C17A0 |
| 1.66 | [kernel.kallsyms] | [kernel.kallsyms][+ffffffec2688e810] |
| 1.57 | gGXBE69_recomp.so | func_802217A0 |
| 1.49 | gGXBE69_recomp.so | chassis_dispatch |
| 1.45 | gGXBE69_recomp.so | func_802A17A0 |
| 1.41 | moderngekko-run-trial | GPFifo::GPFifoManager::CheckGatherPipe() |
| 1.38 | gGXBE69_recomp.so | func_802297A0 |
| 1.33 | gGXBE69_recomp.so | func_802357A0 |
| 1.28 | gGXBE69_recomp.so | dolrecomp_f32_from_bits_slow |
| 1.24 | gGXBE69_recomp.so | func_802117A0 |
| 1.20 | gGXBE69_recomp.so | func_801E17A0 |
| 1.19 | moderngekko-run-trial | __aarch64_swp4_acq_rel |
| 1.11 | gGXBE69_recomp.so | func_800257A0 |

## Grouping (flat %, emu thread)

Bucket rules (`D6/analysis/d6-analyze.py`): guest = module
`func_*`/`loop_*`/`*chunk*`; dispatcher+core = `chassis_dispatch`,
`StaticRecompCore::*`, module FP/convert helpers (`ppc_*`,
`dolrecomp_*`, `convert_*`), CPU/timing loop frames, and
`HookExternalWrite` (called from inside `func_` chunks — see chains);
fifo = `*Fifo*`/`*GatherPipe*`/`*CommandProcessor*`/`Write32`;
exceptions = `*xception*`/`take_exception`/`rfi`; jit =
`PoisonMemory`/`Fallback`/`Jit`; mematomic = `__aarch64_*`/`memcpy`
family; libkernel = libc/libm/linker/`[kernel.kallsyms]`.

| bucket | d6-perf-a % | d6-perf-b % | top members (a) |
|---|---|---|---|
| guest module (func_*/loop_/chunk) | 74.60 | 74.88 | func_802197A0 8.14, func_8022D7A0 6.33, func_801097A0 3.07 |
| dispatcher + StaticRecomp core | 13.23 | 13.04 | Run() 3.56, HookExternalWrite 2.40, chassis_dispatch 1.70 |
| FIFO/GatherPipe/CommandProcessor | 4.52 | 4.36 | CheckGatherPipe 1.41, RunGpuOnCpu 0.53, Write32 0.49 |
| other | 2.55 | 2.65 | AXUCode::ProcessPBList 0.38, GetPPCState 0.32 |
| libc/kernel | 2.43 | 2.45 | kernel [+…810] 1.72, [+…84c] 0.43 |
| memory/atomics | 2.09 | 2.12 | __aarch64_swp4_acq_rel 1.17, __memcpy_nt 0.33, __aarch64_ldadd4 0.31 |
| JIT fallback/PoisonMemory | 0.31 | 0.29 | PoisonMemory 0.30, UpdateMembase 0.01 |
| exceptions | 0.02 | 0.02 | CheckExternalExceptions 0.02 |
| TOTAL | 99.75 | 99.81 | |

## Caller chains

`StaticRecompCore::Run()` children (99.95% both arms; self 3.56/3.62%):

| child | a children-% | b children-% |
|---|---|---|
| chassis_dispatch | 91.12 | 90.84 |
| CoreTiming::Advance() | 3.26 | 3.17 |
| StaticRecompCore::SyncIn() | 0.66 | 0.78 |
| StaticRecompCore::SyncOut() | 0.58 | 0.58 |
| StaticRecompCore::DispatchableAt() | 0.22 | 0.26 |
| Common::FPU::SetSIMDMode() | 0.21 | 0.26 |
| PowerPC::RoundingModeUpdated() | 0.15 | 0.17 |
| StaticRecompCore::LookupChunkSlow() | 0.13 | 0.21 |
| StaticRecompCore::TryHostHle() | 0.05 | 0.04 |
| CoreTiming::Idle() | 0.03 | 0.02 |
| chassis_on_state_loaded | 0.01 | 0.03 |
| JitArm64::Run() | 0.00 | 0.00 |

Chain shape (both arms, full trees in
`analysis/d6-perf-{a,b}-rep-full-cg.txt`): `__start_thread` →
`Core::EmuThread` → `Core::CpuThread` → `CPUManager::Run` →
`PowerPCManager::RunLoop` → `Run()` → `chassis_dispatch` → `func_*`.
There are no separate update/render callback frames in the profile:
FIFO submission flows from inside guest chunks, e.g. arm A
`func_8022D7A0` → `HookExternalWrite` (7.12% of that chunk) →
`CheckGatherPipe` (52%) → `UpdateGatherPipe` (58%) →
`GatherPipeBursted` (54%) → `RunGpu` → `__aarch64_swp4_acq_rel` (29%).
HookExternalWrite overall: 8.68/8.6x% children, ~45–55% into
CheckGatherPipe, ~7–9% into Write32 (both arms).
Top-chunk callees (arm A `func_802197A0`, 9.78% of dispatch):
`ppc_fcmp` 4.90%, `dolrecomp_f32_from_bits_slow` 2.97%,
`convert_to_double` 0.18%, `ppc_fctiw` 0.18% — the M7 FP-helper set,
now inside the dispatch subtree.

## Probe table (d6-probe, trial window driver 112.01–124.01)

Lifecycle (`android_trial` rows): configured imm_xfb=1 →
request@112.000038 → Running (1→2 @112.005870) → cancel@124.006714 →
Finished@124.011060 (frames=1010, extras=303, doubled=0, blended=303,
limited=0). Zero `invalid_immediate_copy_setup` rows in 5,130 probe
rows (2,396 schedule + 1,010 interpolation + 1,010 render + 707 update
+ 7 lifecycle).

| callback | n | CPU-ms med | CPU-ms p95 | wall-ms med | wall-ms p95 | wall-ms max |
|---|---|---|---|---|---|---|
| update | 707 | 3.1880 | 3.6900 | 3.2017 | 3.7273 | 4.4139 |
| render | 1010 | 7.9338 | 10.9993 | 8.6302 | 12.5088 | 20.7272 |

(render n = 707 base + 303 blended extras. All 707 updates
`position_changed=1`, `same_rider=1`, `same_view=1`, state 0→0:
guest-clean, rider moving every frame.)

## Exact commands

Pre-arm each (all `adb -s 622c49b1 shell …`): process check empty,
LEASE=`D6`, `D6/preflight.sh <tag>` thermal gate + settings snapshot,
then (device wall, EDT): perf-a launched 02:31, perf-b 02:37,
probe 02:4x.
- perf arms: `python3 tools/android_trial.py run --binary
  /Volumes/Extreme\ SSD/android-spike/D1/moderngekko-run-pace-egl --tag
  d6-perf-{a,b} --output D6/d6-perf-{a,b}-receipts --template aff-tpl
  --movie m3-menu.dtm --module gGXBE69_recomp.so --graphics OGL --idle
  on --affinity emu=80,video=40 --sampler --screenshot-seconds 2
  --timeout 300 --serial 622c49b1` plus, overlapping,
  `adb shell 'sh /data/local/tmp/mg/d6-trigger.sh d6-perf-{a,b} 45 60'`
  (starts `simpleperf record -p PID -t TID -e cpu-clock -f 4000 -g
  --duration 120`, stops at sample 60; full cmdline in each
  `perf.data` header).
- probe: same runner with `--binary M4/trial-lse/moderngekko-run-trial
  --build-json M4/trial-lse/build.json --tag d6-probe --output
  D6/d6-probe-receipts --template m6h --movie m3-menu-imm.dtm
  --probe-quiet --trial-at 112 --trial-secs 12` (rest identical).
- reports (host NDK simpleperf):
  `report -i d6-perf-{a,b}.perf.data --tids {14226,19398}[ -g |
  -g --full-callgraph --max-stack 8 | --sort dso,symbol]`; grouping via
  `analysis/d6-analyze.py`.

## File list (new under `D6/` only; repo untouched, no commits)

`REPORT.md` (this file), `waits.log`, `thermal-waits.log`,
`run-notes.log`, `preflight.sh`, `mon-perf.sh` (superseded host
monitor, kept for the record), `d6-trigger.sh` (also pushed to device,
removed at end — see below), `d6-perf-a/b-receipts/` (run.json, err,
out, sampler.log, GFX+Dolphin post-inis, 142 shots each),
`d6-probe-receipts/` (same minus shots, plus probe.jsonl),
`d6-perf-a/b.perf.data`, `d6-perf-a/b-{placement.txt,trigger.log}`,
`runner-d6-{perf-a,perf-b,probe}.log`, `analysis/` (flat/emu/cg/
full-cg/dso reports per arm, `grouping.txt`, `d6-analyze.py`),
`symfs/` (module .so pulled sha-verified + pace binary + libc for the
report cross-check).

## What I could not do

- No verdicts, per the plan.
- Capture bracket vs anchored window: START fires at the gate shot
  (sample 45 = gate wall both arms); STOP at sample 60 lands ≤2–4 s
  into the pause menu (pause precedes it by one 2 s shot). A
  `report --filter-file` time-cut was unavailable (format doc not on
  device, no network doc found), so the tables cover gate→pause+sliver;
  the sliver's emu-CPU weight is small (pause menu runs at ~2.2x metric
  speed = less guest work per wall second).
- `record -p PID -t TID` still captured other threads (~28% video);
  emu isolation is done at report time via `--tids` (verified: profiled
  TID == run.json emu TID on both arms).
- Kernel symbols are restricted addresses (`kptr_restrict`; changing it
  is a device-settings change, forbidden) — the 1.7% top kernel row is
  one address, not a name.
- No `take_exception`/vector/`rfi` frames exist in this build (the
  module redirects pc/msr inline per D5 counter semantics), so the
  exceptions bucket shows only the 0.02% `CheckExternalExceptions`
  poll; D5's ~36k/s lazy-FP faults hide inside `func_` bodies and FP
  helpers — the profile cannot split them further.
- Probe screenshots: zero (trial-lse dead shot path); anchored via D1
  `capped1x` (same m6h template) + engagement evidence above.
- `trial-at` deviation from the brief's letter: the perf-arm gate wall
  (+34 s) is aff-tpl-specific; under m6h the gate is at ~+110–117 s
  (D1 capped1x screenshots, t2/t3 AT=124–125 in-race), so AT=112 was
  used; verified in-race post-hoc (all updates moving, full lifecycle).
- Host-generated reports were cross-checked against explicit
  `--symfs` (sha-verified pulled module + local pace binary + pulled
  libc): byte-identical output.
