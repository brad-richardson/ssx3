# RD1 report: the player's rider is mostly missing in races

Exploratory session (Claude Code, Opus 5.5), 2026-09-25 11:02–12:10 EDT (about 1 h 10 min of
the 3 h box). Notebook: `NOTEBOOK.md`. The orchestrator decides; labels say what was measured.

## Outcome

**Mechanism: every guest thread except main runs with VU0 `vf0 = (0,0,0,0)`.** On hardware VU0
vf0 is hardwired to (0,0,0,1). `R5900Context()` (`ps2_runtime.h`) memsets itself and never sets
vf0. The runtime fixes vf0 only for the main context (`ps2_runtime.cpp:876`) and the VU0 state
restore (`:331`), but `EeScheduler::startThread` gives each thread a fresh `R5900Context{}`.
SSX 3 builds the player rider's high-detail bind matrices on a loader thread (guest thread 3). It
uses VU0 macro code that computes `vaddw.xyz vf1, vf0, vf0w` (meant to be 1,1,1) and then
quaternion→matrix rows of the form `1 − 2yy − 2zz`. With vf0 = 0, vf1 = 0, so every diagonal term
vanishes and the rotation rows come out zero. Those bind matrices feed the skin matrices, then the
scratchpad blend palette, then the VIF list, then VU1. The player's vertices land on their bone
origins (a stick figure) and the normals transform to 0 (one flat ambient colour). The rival's
matrices are built elsewhere and render normally.

**Fix:** set `vu0_vf[0] = (0,0,0,1)` in the constructor. Fork branch `rd1-rider` (local, not
pushed) commit **`51c759b4fcefb94cb2fb1abf000fa150a4f261f5`** (+ unit test). With it, the player
rider renders solid and lit on the deterministic Zoe route and on Brad's save (Mac).

UV1's V2/V3 UNPACK fix is **not** this bug. The player and rival use identical UNPACK formats, and
the player's vertex data arrives non-zero (row E3).

## Evidence (tick 1799 / 2099 of the deterministic I26-FAST race, Zoe, unless noted)

| Row | Measurement | Before (base `0ed07c4`) | PCSX2 / after fix | Receipt |
|---|---|---|---|---|
| E1 | Player batch structure (tfx=3 tri-strips, q≈0.0025–0.0034) | n = 1849/80/118/353/449, 53/411 | PCSX2 T65 dump: 1849/80/118/353/484, 53/411 (same model) | `rd1_draws.py`, UV1 A1 capture, `RR1/ref/pcsx2-race.gs` |
| E2 | Player vertex RGBA / bbox | one colour 0x47b89a95 (149,154,184,71); 80- and 118-prim batches collapsed to **one pixel**, 353 → 1×5 px, 411 → 2×7 px | PCSX2: RGB 54–255, A 0–95, 353 → 9×14, 411 → 18×17. **After fix:** RGB 53–255, A 0–95, 353 → 9×17, 411 → 18×26, 80 → 39×33 | NOTEBOOK 11:02; V1 capture |
| E3 | VIF input for the player (probe P1) | same formats as the rival (V4_32 header, V4_16 3x1, V3_16/V3_32 3x1 mask 0x40404040); V3_32 positions non-zero (-46.3, -15.0, -6.9 …) | — | `rd1_trace.py`, `run/P1/rd1.trace` |
| E4 | VU1 bone matrices (VU mem rows 17–116 at xgk 1240 vs rival xgk 1320) | player: rows 0–2 of every 4×4 **zero**, translation set (world ≈ 2850, -45485, 95610, 1) | rival: full rotations | P1 `PS2X_RD1_XGK_DUMP` |
| E5 | Chain upstream (diag watch + GPR/VU0 snapshots, boots W1–W7) | VIF list ← copy loop 0x37ac40 (sub_0037A430) ← SPR palette 0x70000000 ← blend sub_00386128 (0x386cc0; `Σ w·0.01·Bone[i]`, weights OK) ← bone buffer 0x4fc420 ← `out = B × A` sub_00310640 (0x31076c) with **B = bind matrices at 0x158f240: rows 0/1 = 0** ← builder sub_0030DBD0 (0x30e6c4/0x30e708, **guest thread 3**) | — | NOTEBOOK 11:20 table |
| E6 | VU0 state at the builder's store (0x30e708, W7) | **vf0 = (0,0,0,0)**, vf1 = (0,0,0,0), quaternion vf4 = (0,0,0,1), vf10/vf11 = 0 | hardware vf0 = (0,0,0,1) → vf1 = (1,1,1) | `run/W7/boot.log` `[rd1:vu0]` |
| E7 | Frames, Zoe route, tick 2100 | rider collapsed / grey wisp | full rider (hair, red top, grey pants, board) | see Frames |
| E8 | Frames, Brad's save (Mac), tick 2300 | Mac "mostly missing" (faint wisp) = Brad's report | Mac solid, orange/white outfit | see Frames |
| E9 | Det-hash, fix vs base (UV1 A2), ticks 1–2425 | — | first difference at **tick 231** (rdram only, transient 231–255, converges at 256), then from **tick 1543** (race load) onwards: rdram, later vu1Data/scratch; **eeCycle identical at every tick** | `run/D1/boot.log` vs `UV1/run/A2/boot.log` |
| E10 | Menu frame tick 1090 (Select Peak) | fnv `f86140f2` | fix: `f86140f2` (identical) | V1 frames |

## Fix, tests, checks

- Fork `~/dev/ssx3-work/RD1/PS2Recomp`, branch **`rd1-rider`** from `ssx3` `0ed07c4`, not pushed:
  - `51c759b` `[RD1] VU0 vf0 = (0,0,0,1) in every EE context, not only the main one`:
    `ps2xRuntime/include/ps2_runtime.h` +4, `ps2xTest/src/ps2_runtime_kernel_tests.cpp` +24
    (2 files, +28). **This is the fix to fold.**
  - `1f3180d` `[RD1] Default-off one-tick VIF1/VU1 probe and diag-watch register snapshot`:
    new `ps2_rd1_trace.h` + hooks in `ps2_vif1_interpreter.cpp`, `vu/ps2_vu1_core.cpp`,
    `ps2_memory.cpp`, `ps2_runtime.cpp` (5 files, +280/−2). Dev tooling only; skip it when folding
    if you don't want it.
- Test "RD1: every EE context, incl. StartThread's, has VU0 vf0 = (0,0,0,1)": red on unfixed code
  (**612 pass / 1 fail**, `suite-red.log`), green with the fix (**613/613 rc=0**, `suite-green.log`);
  suite run from the worktree root.
- Runner-dir check: `git diff --stat 14b1e5cb rd1-rider -- ps2xRuntime/src/runner` is **empty**.
- Other contexts: `GuestThread`/`GuestInvocation` (`ee_scheduler.h`) and the IOP host context all
  default-construct, so the constructor fix covers them. Invocation/callback contexts
  (`RPC.cpp`, `Thread.cpp`, `System.cpp`, `MPEG.cpp`, `IPU.cpp`, `GS.cpp`) copy a caller context, so
  they inherit a correct vf0 now.
- Runners (Release, diag taps OFF unless noted, sha256, two matching reads each via `rd1_boot.py`):
  fix `runners/ps2EntryRunner-fix` `8b844cf9…6b928f`; fix + det-hash tap `…-fix-det` `80e94f05…74c96`;
  pre-fix probe `…-probe` `539e944f…f2f7da` (probe2 `7dae2705…`, probe3 `dc2972d6…`, probe4
  `d761d455…`, taps `348c5ac4…`). Codegen `~/dev/ssx3-work/codegen-ssx3` (pin as UV1/CT1).

## Frames to view (all under `~/dev/ssx3-work/RD1/`)

| What | Path |
|---|---|
| Zoe, tick 2100, before/after side by side (crop, 2×) | `out/rider-2100-before-after.png` |
| Zoe, tick 2100 full frame: before / after | `in/upload-latest.png` (UV1 A1, base) / `run/V1/frames/upload-latest.png` |
| Zoe, tick 1800: before / after | `in/upload-1.png` / `run/V1/frames/upload-1.png` |
| Mac (Brad's save), tick 2300, before/after side by side | `out/mac-2300-before-after.png` |
| Mac full frames: before / after | `run/M0/frames/upload-latest.png` / `run/M1/frames/upload-latest.png` |
| Player geometry wireframe tick 2099: before (stick figure) / after | `out/geo-2099.png` / `out/geo-2099-fix.png` |
| PCSX2 race reference (T65, other moment) | `~/dev/ssx3/local/research/E51/frames/pcsx2-t65-race-0018.png` |

## Boots (Mac mini, `PS2X_DETERMINISTIC=1`, paraLLEl + `PGS_HIER_BINNING=force`, `PS2X_SOUND=1`, I26-FAST, one slot each, all `bound=target`, `gs_fatal=null`)

| Boot | Runner | Purpose |
|---|---|---|
| P1 | probe | one-tick VIF1/VU1 trace at 1799 + VU1 dumps (E3, E4) |
| W1 | taps | E44 watch (SPR palette writer + regs) |
| W2 | probe | diag watch on the VIF list words (copier) |
| R1 | probe2 | RDRAM/SPR dump at 1799 |
| W3–W7 | probe3/4 | diag watch + GPR (+VU0) snapshots up the chain (E5, E6) |
| V1 | fix | frames 1090/1800/2100 + GS capture to 2101 (E2, E7, E10) |
| D1 | fix-det | det-hash every tick to 2425 (E9) |
| M0 / M1 | probe (pre-fix) / fix | Brad's save (copy of `E55D16/mc0` in the lane dir, scratch only), route shifted +3337 ms (+200 ticks); frames 1300 (Select Peak), 2000, 2300 (E8) |

Mac-save route: I26-FAST with every press +3337 ms. It reached the race (2ND/2, 00:00:06 at
2300). The rider is Mac because that's the Select Character default on Brad's save (E55D16), but
Select Character itself wasn't captured (tick 1300 was already Select Peak).

## Gaps

- **The guest can still overwrite vf0.** Codegen emits `lqc2 $vf0` as a real write (one site:
  0x3fe9bc in sub_003FE828, a VU0 register-file restore); hardware ignores writes to vf0. It is
  harmless as long as what it restores was saved from a correct context, which holds after this
  fix. Making vf0 read-only is a recompiler change and isn't done here.
- The tick 231–255 det-hash blip (boot, rdram only, converges) isn't attributed. It's probably
  another non-main thread's COP2 code seeing the corrected vf0. No frame change at 1090.
- Other VU0 reset values for non-main threads: main also sets `vu0_r` = 1.0 bits; thread contexts
  keep R = 0. Not observed to matter and not changed (one-mechanism rule).
- The per-thread VU0 register file is itself a model difference (the PS2 has one VU0). It's out of
  scope and noted only.
- Why the rival's matrices are right wasn't traced (they're built on a thread whose vf0 is right,
  or through another path). Brad's "AI riders look normal" is consistent with that.
- No iOS or Odin run. The fix is in shared runtime code, so both backends and platforms get it.
- The UV1 A1 capture hardlink `in/uv1-A1.gs.stream` (2.5 GB, shared bytes) and
  `run/V1/gs.stream` can be deleted after the gate. Scratch is otherwise small (runners,
  32 MB RAM dumps).

## Next (the orchestrator decides)

1. Fold `51c759b` (fix + test only) onto fork `ssx3`. It touches one header, so all codegen
   rebuilds. Then run the suite, one det race boot, and view frames.
2. Build for Brad (iPhone/iPad and the Odin APK): rider on his save.
3. Optional hardening lane: treat vf0 as read-only in codegen (`lqc2`/`qmtc2`/VU0 macro dest vf0).

## Tools (this dir)

`rd1_draws.py` (batch census of our capture or a PCSX2 dump: full RGBA, bbox, q, ALPHA/TEST/FBA),
`rd1_p1map.py` (capture PATH1 ordinal ↔ batches), `rd1_plot.py` (wireframe of batches, needs
Pillow via `uv run --with pillow`), `rd1_trace.py` (probe trace: segments per xgk range, UNPACK
census), `rd1_boot.py` (UV1 boot script + `--env`, `--capture-stop`, `--mc-src`).
