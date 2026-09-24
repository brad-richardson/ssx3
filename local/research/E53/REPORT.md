# E53 report: fix batch 1 from the E52 audit (+ log-stub ABI and VU1 EFU table)

Brief `local/muse/prompts/E53.md` plus the orchestrator's scope addition
(frontier review 2 §0 items 1, 2, 10). Worker: Claude Code (Opus pane).
Tables and receipts; the orchestrator decides. **Stopped at a stop rule:
the race window can't be reached within the 600 s boot cap (details
below).** 2 of 3 boots used.

## Outcome

- **The batch is in:** fork `e52-audit` @ `d3f7508`, not pushed.
  - Suite **630/630** on `e52-audit` and **637/637** on the validation
    branch `e53-val`.
  - All 30 E52 audit tests pass, except 3 assertions deferred as G2
    (Inf/NaN operand clamping). They only run with `PS2X_TEST_DEFERRED=1`,
    and they fail as expected.
  - The regen changes exactly the audited sites. Every change class in the
    codegen diff matches the E52 census count.
  - Fused multiply-adds in the runner's game objects: **228 → 0**.
- **Boot (a), SC: PASS.** The rider renders, and the camera block of all 9
  SC 3D programs matches T65's invariants exactly. SC counts are identical
  to E50's.
- **Boot (b), race: the picture changed, but the race wasn't reached.**
  - VU0 microprograms now really run: **1,665,536 VU0 starts** in one
    boot. Before the fix, the VCALLMSR sites started VU0 at a garbage
    address, and the uploads went to EE RAM.
  - The VU0 data hash changes between starts, so the VSQI uploads land.
  - Guest speed drops from about 17 to about 6 vsyncs/s from the race load
    onwards (tick ~4100). At 480 s the run reached tick 6131, the
    pre-race "Rival Challenge" dialog.
  - At that same tick, **the background shows lit, snow-covered terrain.
    E50 at the same tick shows a dark background with shard fragments**
    (`frames/e53b-prerace-tick6131.png` vs
    `frames/e50f-prerace-tick6131.png`).
  - The T65-format counts, the race camera check and **TEX1 K** need
    ticks 7590–8280. That means a boot of roughly 750–850 s, which is over
    the cap.
- **Decision needed (orchestrator):** OK a ~900 s race boot, or first fix
  the VU0 per-call cost (see "VU0 cost"), then run (b) and (c).

## Pins

| Item | Value |
| --- | --- |
| Fix | fork `~/dev/PS2Recomp` branch `e52-audit` @ **`d3f7508`** (parent `96fc89b` [E52] tests ← `eac6cba`), worktree `~/dev/ssx3-work/E52/PS2Recomp`; not pushed; runner dir unchanged vs `14b1e5cb` |
| Validation branch | `e53-val` @ `98d1534` = `d3f7508` + E50 taps (`749afb7`→`41471aa`, `3685507`→`809551f`) + E51 GIF dump (`0af7eed`→`98d1534`); worktree `~/dev/ssx3-work/E53/PS2Recomp`; local only |
| Codegen | `~/dev/ssx3-work/codegen-ssx3-e53` (regen of `ssx3-e53.toml` = fork toml minus `log@0x0040D610`, internal-disk paths), 9,457 files, 273 MB |
| Runner | `~/dev/ssx3-work/E53/build/ps2xRuntime/ps2EntryRunner` sha256 `be71642055ddadfce2543c3595ce36ccca853ed35c959bfd689bb28c46ce9a70` ×2. Release, runtime/aggressive logs OFF, **but E50/E51 dev taps compiled in: diagnostic build, no speed numbers** |
| Fork `ssx3` | unchanged at `eac6cba` (no rebase needed; E51 had pushed nothing) |

## What changed (fork `d3f7508`)

| # | Item | Change | Where |
|---|---|---|---|
| 1 | VSQI/VSQD/VLQI/VLQD/VILWR/VISWR | fields per the encoding (VSQI/VSQD: fs = 15:11, it = 20:16); address **VU0 data memory** (`Ps2Vu0DataAt`, 4 KiB wrap); vi0 is never incremented; no load into vf0; VILWR/VISWR use 16-bit field words as in PCSX2 | `vu_translation_helpers.cpp`, `ps2_runtime_macros.h` |
| 2 | VCALLMSR | start = `(vu0_cmsar0 & 0x1FF) << 3` | `vu_translation_helpers.cpp` |
| 3 | CTC2 CMSAR1 | stores the value, then `runtime->vu1StartMicroProgramFromEe` (VU1 from `(v & 0x7FF) << 3` with VIF1 TOP/ITOP, like the MSCAL callback; logs the first 8 starts) | `vu_translator.cpp`, `ps2_runtime.cpp/.h` |
| 4 | R register | PCSX2 format (`0x3F800000 \| 23 bits`, every lane of `vu0_r`), `AdvanceLFSR`; VRNEXT writes ft; VRGET/VRINIT/VRXOR; CTC2/CFC2 R | `vu_translation_helpers.cpp`, `vu_translator.cpp`, macros |
| 5 | DIV.S | `Ps2FpuDivS`: exponent-0 divisor → ±FMAX with sign fs⊕ft; else fpuDouble(fs)/fpuDouble(ft) | `fpu_translator.cpp`, macros |
| 6 | MAX.S/MIN.S, VMAX/VMINI | sign-magnitude integer compare (`fp_max`/`fp_min`) | `fpu_translator.cpp`, `vu_translation_helpers.cpp`, macros |
| 7 | C.EQ / C.LT / C.LE | fpuDouble operands. The EE's C.LT/C.LE (functs 0x34/0x36) are emitted as `FPU_C_OLT_S`/`FPU_C_OLE_S`: 3,048 + 1,148 sites | macros |
| 8 | VDIV/VSQRT/VRSQRT | `_vuDIV`/`_vuSQRT`/`_vuRSQRT` (±FMAX, sqrt(\|x\|), VRSQRT reads fs, vuDouble on the result) | `vu_translation_helpers.cpp`, macros |
| 9 | VFTOIn | `floatToInt<n>`: saturate by sign at exponent ≥ 2^31 | same |
| 10 | VCLIPw | PCSX2 bit order, against \|ft.w\| with the integer compare | `vu_translator.cpp`, macros |
| 11 | FMA | `-ffp-contract=off` for C/C++ (non-MSVC), top-level CMake | `CMakeLists.txt` |
| 12 | EE FP mode | `EeScheduler::run()` sets round toward zero + FZ (x86: RTZ + FTZ + DAZ) and restores it on return. `PS2X_EE_FPMODE=ieee\|ps2`, default `ps2`, logged once. `GS::processGIFPacket`, `processNativePackedGIFPacket`, `writeRegister` and FFmpeg `feed`/`flush` switch to host IEEE for their scope | `ps2_fpmode.h` (new), `EeScheduler.cpp`, `gs_frontend.cpp`, `MPEG.cpp` |
| 13 | log ABI (review item 1) | **unbound `log@0x0040D610`** in `games/ssx3/ssx3.toml`, so the guest fdlibm wrapper (a0 → `__ieee754_log`@0x40DB58 → v0) runs. `__ieee754_log` was already recompiled: it is only in `untracked_stubs`, an informational list the recompiler ignores. No other double-precision routine is in the bound `stubs` list | toml; codegen `sub_0040D610` goes from 14 lines to a full body, plus 9 resume entries |
| 14 | VU1 EFU (review item 2) | three tables were shifted, not two: decode (`ps2_vu1_lower.cpp`), **pipeline/latency** (`ps2_vu1_core.cpp:1453-1500`, found while testing) and trace names. All now follow PCSX2 `LowerOP_T3`: 0x78 ESQRT (12), 0x79 ERSQRT (18), 0x7A ERCPR (12), 0x7B WAITP, 0x7C ESIN (29), 0x7D EATAN (54), 0x7E EEXP (44); 0x77 is undefined | vu1 lower/core |
| 15 | dev tap | `PS2X_E53_VU0_LOG=1` (default off): VU0 starts with caller pc, start, cycles, budget hit and an FNV-1a of VU0 data (first 64, then every 256th) | `ps2_runtime.cpp` |

Tests changed: the E52 audit tests now run under `ScopedPs2Mode`, and that
file is compiled with `-frounding-math` so clang can't fold constant inputs
in nearest mode. New tests cover the FP-mode scopes, VSQI/VLQI/VILWR/VISWR
against a real `PS2Runtime` (EE RAM 0–0x3FFF stays clean), and VU1
`0x8000afbd` with vf21.x = 4 → **P = 0.5** (plus ESQRT/ERCPR/EEXP values).
Two upstream tests encoded the old behaviour and were updated: the VU
random-helper string test, and the "all EFU opcodes" latency list.

## Codegen diff (`codegen-ssx3` → `codegen-ssx3-e53`, `~/dev/ssx3-work/E53/codegen-vs-e53.diff`, 544 hunks)

| Class | Old lines | New lines | E52 census |
|---|---|---|---|
| DIV.S | 802 | 802 | 802 |
| MIN.S / MAX.S | 268 / 110 | 268 / 110 | 268 / 110 |
| VSQRT / VRSQRT / VDIV | 285 / 108 / 86 | 285 / 108 / 86 | 285 / 108 / 86 |
| VFTOI0 | 46 | 46 | 46 |
| VMAX / VMINI (all forms) | 24 / 24 | 24 / 24 | 6+18 / 6+18 |
| VSQI + VLQI | 15 | 15 | 14 + 1 |
| VCALLMSR | 8 | 8 | 8 |
| CTC2 CMSAR1 | 1 | 1 | 1 |
| VRINIT/VRNEXT/CTC2 R/CFC2 R | multi-line | 5 | 2 + 2 + 1 + 1 |
| log@0x40D610 | stub call | full guest body + 9 resume entries in `register_functions.cpp` | — |
| anything else | 0 | 0 | — |

C.LT/C.LE/C.EQ, CVT.S.W, VITOF and the rounding mode change only in
runtime macros or runtime state, so their codegen text is unchanged.

## FMA contraction (item 3)

| Runner | fmadd/fmsub/fnmadd/fnmsub/fmla/fmls in `ps2_game_objects` (all unity objects) |
|---|---|
| E50 build (`codegen-ssx3`) | **228** = 44 MADD.S + 184 MADDA.S |
| E53 build | **0** |

## FP mode scope (item 3 + review item 10)

| Code on the EE thread | Mode in `ps2` | Why |
|---|---|---|
| generated guest code (FPU, VU0 macro) | RTZ + FZ | PCSX2's FPU/VU control registers |
| VU0/VU1 microprogram core | RTZ (its own `fesetround` scope) + FZ | PCSX2's VU control register; the scoped rounding still restores the outer mode (test "E53 FP mode") |
| software GS (packets, register writes) | **host IEEE** (scoped) | PCSX2's GS runs on its own thread in default mode |
| FFmpeg decode (MPEG HLE) | **host IEEE** (scoped) | host library |
| HLE libm stubs (sinf, expf, …) | RTZ + FZ | they stand in for guest code, which runs in RTZ on the PS2 |
| GS/present and other host threads | unchanged | FPCR is per thread; only `EeScheduler::run` sets it |

Because the GS is always IEEE, an ieee-vs-ps2 A/B boot (c) now isolates
the guest's FP mode and the libm stubs, not the GS.

## Boots (Mac mini, own run dir `~/dev/ssx3-work/E53/run`, slot 2, PID-tracked by `e46_boot.py`)

| Boot | Command | Wall | Result |
|---|---|---|---|
| e53a SC | `local/research/E53/e53_boot.sh e53a 1300 1310 1305 1305 120 5` | 121 s, rc 0 | PASS (below). Log `2a9dc783b26ce23d` 7,128,299 B |
| e53b race | `local/research/E53/e53_race.sh e53b 480` | 481 s, rc 0 | reached tick 6131 only (race starts ~7600). Log `a65e0945c92612ff` 9,900,116 B |

### (a) SC, vsync 1305 (`an-e53a-t65.md`)

| Block | abs col x | abs col y | abs col z | abs col w | x.y | x.w | y.w | y/x | NaN/Inf/den |
|---|---|---|---|---|---|---|---|---|---|
| e53a, all 9 3D programs | 0.536127 | 0.625481 | 1.002002 | 1.000000 | 0 | 1.65e-15 | 0 | 1.1667 | none |
| PCSX2 T65 | 0.536127 | 0.625481 | 1.002002 | 1.000000 | 0 | 1.65e-15 | 0 | 1.1667 | none |

Camera qw 0x000–0x003 against T65, in ulp: x lane 1 (same as E50),
qw2.y **3 ulp** below T65 (`3f201f85` vs `3f201f88`; E50 was 1 ulp above),
and qw3.z now equal (`433e63ef`). The ulp moves are what a rounding-mode
change is expected to produce; the invariants are unchanged.

SC counts (T65 format, 1305): 611 MSCAL, 5,844 verts, on 4,112, off 38,
straddle 16, zero-area 6, ADC 1,294, the same as e50e.

`frames/e53a-sc-tick1329.png`: Zoe on the Select Character screen,
viewed by eye.

`[E53] PS2X_EE_FPMODE=ps2` is logged. VU0 starts at SC: 0 (matches E44/T57).

### (b) race: VU0 now runs; the pace drops; the pre-race frame changes

VU0 starts over the whole boot: **n = 1,665,536** (sampled lines in
`vu0start-e53b.txt.gz`: 64, then every 256th). No budget hits.

| Caller (guest pc) | Via | startPC | sampled | mean / max VU cycles | distinct VU0-data hashes in samples |
|---|---|---|---|---|---|
| 0x22a934 | VCALLMS | 0x570 | 1,845 | 46 / 46 | 7 |
| 0x22a1e0 | VCALLMS | 0xdb8 | 1,703 | 95 / 160 | 8 |
| **0x22aa4c** | **VCALLMSR** | 0x948 | 1,228 | 40 / 44 | 4 |
| 0x22a09c | VCALLMS | 0xdb8 | 825 | 89 / 160 | 3 |
| **0x37deb8** | **VCALLMSR** | 0x570 | 430 | 46 / 46 | 4 |
| 0x22a64c / 0x22a724 | VCALLMS | 0xef0 | 246 / 160 | 45 / 54 | 3 / 3 |
| **0x32b6d0** | **VCALLMSR** | 0x6e0 | 84 | 44 / 47 | 7 |
| 0x22a2d8 | VCALLMS | 0xdb8 | 26 | 128 / 152 | 2 |
| **0x1223f0 / 0x2d20c0** | **VCALLMSR** | 0x828 | 12 / 6 | 19 | 2 / 1 |
| **0x391470** | **VCALLMSR** | 0x0 | 5 | 718 | 5 |

- 13 distinct VU0-data hashes in all: the uploads land and change between
  programs. The 0x391470 program sees a new hash on each of its first
  starts.
- CTC2 CMSAR1 was never executed in this boot (0 `[E53] CTC2 CMSAR1`
  lines).

Pace (snapshot ticks at the same wall time):

| Wall | 60 s | 120 s | 150 s | 180 s | 240 s | 300 s | 420 s | 480 s |
|---|---|---|---|---|---|---|---|---|
| e50f tick | 1,930 | 3,788 | 4,419 | 4,935 | 5,961 | 6,984 | 8,132 | — (ended at 450 s: 8,415) |
| e53b tick | 1,728 | 3,426 | 4,126 | 4,307 | 4,677 | 5,036 | 5,784 | 6,131 |

From about tick 4100 (race load) e53b advances about 6 ticks/s, against
about 17 in e50f. That is about 830 VU0 starts per vsync averaged over
that stretch, at 19–160 VU cycles each. The VU work itself is small
(~70k VU cycles per vsync), so the cost is per call in
`executeVU0Microprogram`. This is diagnosis by numbers; no profile was
taken.

Frames at tick 6131 (same guest moment on the vsync-clocked route, the
pre-race Rival Challenge dialog), viewed by eye:
- `frames/e53b-prerace-tick6131.png`: lit terrain and snow slopes behind
  the dialog (right edge, and through the panel).
- `frames/e50f-prerace-tick6131.png` (E50, before this batch): dark
  background with light shard fragments inside the panel.

**Not measured (window unreached):** T65-format race counts, the race
camera invariants, per-startPC census, VU1 budget exits, **TEX1 K**, and
the race frame vs `E50/frames` and T65. No gfx or GIF files were written
for e53b.

## Deferred (G2/G3) and the cost estimate

- In `ps2` mode, RTZ already saturates an overflowing result to ±FMAX, and
  FZ flushes denormal inputs and results. So G3 and the denormal half of
  G2 now hold for every host float op.
- What's left is **Inf/NaN bit patterns as operands** (G2): 3 assertions,
  deferred.
- Cost estimate (micro-benchmark `g2_bench.cpp` in this dir, not the runner): a
  per-operand exponent test + select adds about 3 integer ops per operand.
  It measured ×2.7 on a NEON mul+add loop and ×4.3 on scalar (the plain
  scalar loop auto-vectorised, so that ratio overstates it).
- Generated code is dominated by `ctx` loads and stores, so I'd expect
  single-digit to low-double-digit percent on FP-heavy functions. That's
  an estimate only; measure it on a no-diagnostics build.

## Gaps

- **The race is unvalidated.** (b) stopped at tick 6131; (c) not run.
- **Constant folding in the runner:** generated code is not compiled with
  `-frounding-math`. Where clang can see two constant FP operands in one
  function, it folds in nearest mode. The audit tests are protected; the
  runner isn't. Reach unknown, and cost unmeasured if the flag is enabled.
- **DIV.S rounding** follows the thread mode (chop), as PCSX2's interpreter
  and the T-lane interpreter traces do. PCSX2's EE recompiler rounds DIV.S
  to nearest (`FPUDivFPCR`).
- `Ps2Vu0DataAt` wraps at 4 KiB. PCSX2 maps VU0 addresses with bit 0x4000
  onto VU1's VF/VI registers; that window isn't modelled (SSX 3's uploads
  use qword 0x50+).
- CMSAR1 VU1 start is unit-level only (string + build), not reached in a
  boot.
- VU0 per-call cost isn't profiled. `sample <pid>` during the next race
  boot would name it.

## Recommended next action (the orchestrator decides)

1. **Either** OK one ~900 s race boot on this runner (the same `e53_race.sh`
   with a larger wall), **or** first fix the VU0 per-call cost and then run
   (b) within the cap. The second option also serves the eventual 120 Hz
   and Odin speed budget, since about 800 VU0 calls per vsync is the new
   normal. A `sample` of the runner during the race load would decide
   where the cost is.
2. Then (c): the same race boot with `PS2X_EE_FPMODE=ieee`, to separate the
   FP mode from the structural and ABI fixes.
3. The fix commit stands on its own (all audit tests green, codegen diff
   exactly the audited sites, SC unchanged). It can be folded onto `ssx3`
   independently of the race question if the orchestrator wants.

## Receipts

- This dir: `REPORT.md`, `e53_boot.sh`, `e53_race.sh`,
  `e53_analyze.py` (copy of E50's with the E53 run dir), `an-e53a-t65.md`,
  `vu0start-e53b.txt.gz`, `frames/` (e53a SC, e53b and e50f pre-race).
- `~/dev/ssx3-work/E53/`: `ssx3-e53.toml`, `regen.log`,
  `codegen-vs-e53.diff`, `build-val.log`, `suite-val.log` (637/637),
  `build.sh`, `run/` (boot logs, frames).
- `~/dev/ssx3-work/E52/`: `suite-e53t4.log` (630/630),
  `suite-e53-deferred.log` (G2 assertions: 2 tests fail as expected).
- Budget: builds (tests ×4, runner ×1) + 2/3 boots; ~2 h 20 min; disk E53
  1.7 GB + codegen-e53 0.27 GB; internal total 82.0 of 200 GB.
