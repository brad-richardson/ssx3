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


---

## Part 2: one race boot to 900 s (profiles + deferred race measurements)

Orchestrator gate: batch 1 accepted; one race boot OK'd with a wall up to
900 s; two `sample <pid> 10` profiles; no boot (c); no code change.

### Boot e53c (slot 1, PID 31264, 900 s, rc 0)

| Item | Value |
|---|---|
| Command | `local/research/E53/e53_race.sh e53c 900` + `local/research/E53/e53_sampler.sh e53c <boot.out> 4300 8230` (samples when the latest 5 s snapshot tick crosses each threshold) |
| Runner | the Part-1 runner, `be716420…ce9a70` (diagnostic build: E50/E51 taps, no speed numbers) |
| Reached | tick 8906 at 896 s (race timer past 00:00:19). Profile 1 at **tick 4327** (race load), profile 2 at **tick 8247** (inside the T65-matched window 8256–8265) |
| VU0 starts | n = 4,108,800 over the boot (`[E53] vu0start`) |
| Files (short SHA-256, bytes) | boot log `66555ec7cb7064e6` 12,685,885; gfx `ba3c88ed7060a1b7` 602,159; GIF dump `d9bf02fc9c02e8de` 33,869,640; entry trace `71f72c54bc19666c` 5,446,754 (all in `~/dev/ssx3-work/E53/run`) |

### Profiles (GameThread; `sample` at 1 ms for 10 s; raw files `sample{1,2}-e53c-*.txt.gz`, tables from `e53_sample_table.py` / `e53_sample_incl.py`)

**Part 1's hypothesis was wrong: VU0 is 2.9–3.4% of the EE thread.**
Where the time goes (self samples attributed by the enclosing subsystem):

| Subsystem | tick 4327 (race load) | tick 8247 (race) |
|---|---|---|
| VU1 interpreter, MSCAL path, excluding GS work under XGKICK | 45.5% | 38.8% |
| Software GS under VU1 XGKICK (`GS::processGIFPacket` → `GSCpuBackend`) | 25.5% | 34.2% |
| Software GS, other paths (PATH2/3) | 12.5% | 10.6% |
| **VU0 (`executeVU0Microprogram`, inclusive)** | **2.9%** | **3.4%** |
| E37 VIF text log (`e37AppendVif` → `__vfprintf`, a dev tap) | 5.3% | 4.6% |
| everything else on the EE thread, including all generated guest code | 8.3% | 8.4% |
| waiting/sleeping | ~0% | ~0% |

The EE thread is saturated. The slowdown against e50f comes from the VU1
interpreter and the software GS, which now process a lot more geometry and
textured fill (see the counts below), not from VU0.

Profile 1 (tick 4327):

GameThread samples: 6361 (1 ms interval, 10 s)

| # | function (GameThread) | self samples | share |
|---|---|---|---|
| 1 | `VU1Interpreter::commitReadyPipelines()` | 1122 | 17.6% |
| 2 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)::$_0::ope` | 844 | 13.3% |
| 3 | `GSCpuBackend::WritePixel(GSDrawState const&, int, int, int, unsigned char, unsigned char, unsigned char, unsig` | 633 | 10.0% |
| 4 | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | 595 | 9.4% |
| 5 | `GSCpuBackend::Submit(GSPrimitiveBatch const&)` | 446 | 7.0% |
| 6 | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 321 | 5.0% |
| 7 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)` | 191 | 3.0% |
| 8 | `VU1Interpreter::execUpper(unsigned int)` | 190 | 3.0% |
| 9 | `VU1Interpreter::calculateFmacExactResult(unsigned int, long double&) const` | 145 | 2.3% |
| 10 | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | 134 | 2.1% |
| 11 | `__vfprintf` | 129 | 2.0% |
| 12 | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 101 | 1.6% |
| 13 | `ps2_mpg_src_trace::lookupPay(unsigned char const*, unsigned int&, int&, unsigned int&, unsigned int&)` | 83 | 1.3% |
| 14 | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | 80 | 1.3% |
| 15 | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | 76 | 1.2% |
| 16 | `VU1Interpreter::progressXgkick()` | 70 | 1.1% |
| 17 | `std::__function::__func<unsigned int (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned in` | 65 | 1.0% |
| 18 | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | 59 | 0.9% |
| 19 | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | 56 | 0.9% |
| 20 | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | 50 | 0.8% |
| 21 | `_platform_memmove` | 49 | 0.8% |
| 22 | `__sfvwrite` | 45 | 0.7% |
| 23 | `__bzero` | 42 | 0.7% |
| 24 | `GSMem::ReadCT32(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 33 | 0.5% |
| 25 | `PS2Memory::processVIF1Data(unsigned char const*, unsigned int)` | 28 | 0.4% |

Inclusive under executeVU0Microprogram: 186 of 6361 = 2.9%

| direct callee of executeVU0Microprogram | inclusive samples | share of thread |
|---|---|---|
| `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned ` | 169 | 2.7% |
| `VU1Interpreter::resetScheduler()` | 12 | 0.2% |
| `fprintf` | 2 | 0.0% |

Profile 2 (tick 8247):

GameThread samples: 6714 (1 ms interval, 10 s)

| # | function (GameThread) | self samples | share |
|---|---|---|---|
| 1 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)::$_0::ope` | 1104 | 16.4% |
| 2 | `VU1Interpreter::commitReadyPipelines()` | 1031 | 15.4% |
| 3 | `GSCpuBackend::WritePixel(GSDrawState const&, int, int, int, unsigned char, unsigned char, unsigned char, unsig` | 789 | 11.8% |
| 4 | `VU1Interpreter::calculatePairReadyCycle(VU1Interpreter::DecodedInstructionPair const&) const` | 538 | 8.0% |
| 5 | `GSCpuBackend::Submit(GSPrimitiveBatch const&)` | 439 | 6.5% |
| 6 | `VU1Interpreter::run(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 311 | 4.6% |
| 7 | `GSCpuBackend::SampleTexture(GSDrawState const&, float, float, float, unsigned short, unsigned short)` | 255 | 3.8% |
| 8 | `VU1Interpreter::execUpper(unsigned int)` | 176 | 2.6% |
| 9 | `VU1Interpreter::markPairWrites(VU1Interpreter::DecodedInstructionPair const&)` | 130 | 1.9% |
| 10 | `__vfprintf` | 127 | 1.9% |
| 11 | `std::__function::__func<unsigned int (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned in` | 115 | 1.7% |
| 12 | `VU1Interpreter::calculateFmacExactResult(unsigned int, long double&) const` | 110 | 1.6% |
| 13 | `VU1Interpreter::getDecodedInstructionPairForPc(unsigned char const*, unsigned int, PS2Memory*, unsigned int)` | 80 | 1.2% |
| 14 | `VU1Interpreter::execLower(unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned int)` | 79 | 1.2% |
| 15 | `VU1Interpreter::calculateFmacProductSticky(unsigned char) const` | 68 | 1.0% |
| 16 | `VU1Interpreter::queueVfWrite(unsigned char, unsigned char, float const*, unsigned int)` | 66 | 1.0% |
| 17 | `VU1Interpreter::updateFmacFlags(unsigned char const*, unsigned char, unsigned int)` | 63 | 0.9% |
| 18 | `VU1Interpreter::progressXgkick()` | 62 | 0.9% |
| 19 | `GSMem::ReadCT32(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 58 | 0.9% |
| 20 | `ps2_mpg_src_trace::lookupPay(unsigned char const*, unsigned int&, int&, unsigned int&, unsigned int&)` | 52 | 0.8% |
| 21 | `_platform_memmove` | 50 | 0.7% |
| 22 | `GSMem::ReadP4(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int)` | 47 | 0.7% |
| 23 | `VU1Interpreter::normalizeFmacResult(float*, unsigned char, unsigned char*)` | 38 | 0.6% |
| 24 | `__ultoa` | 33 | 0.5% |
| 25 | `std::__function::__func<void (*)(unsigned char*, unsigned int, unsigned int, unsigned int, unsigned int, unsig` | 31 | 0.5% |

Inclusive under executeVU0Microprogram: 225 of 6714 = 3.4%

| direct callee of executeVU0Microprogram | inclusive samples | share of thread |
|---|---|---|
| `VU1Interpreter::execute(unsigned char*, unsigned int, unsigned char*, unsigned int, GS&, PS2Memory*, unsigned ` | 216 | 3.2% |
| `VU1Interpreter::resetScheduler()` | 8 | 0.1% |
| `fprintf` | 1 | 0.0% |

### Race counts in T65 definitions (`an-e53c-t65.md`, `an-e53c-t65-8256.md`)

| | mscal | p1 verts | on | off | straddle | zero-area | adc |
|---|---|---|---|---|---|---|---|
| e53c 7600–7610 (8 drawing vsyncs) | 842–866 | 36,447–37,979 | 19,507–20,624 | 4,343–5,334 | 860–1,254 | **2,357–2,409** | 8,119–8,699 |
| e50f 7600–7610 (before) | 765–807 | 29,229–30,817 | 19,001–20,598 | 864–1,441 | 94–149 | 2,229–2,359 | 6,870–7,146 |
| e53c 8256–8265 (T65-matched moment, 9 drawing vsyncs) | **685–693** | 31,689–32,024 | 18,480–18,694 | 2,162–2,278 | 673–702 | **2,232–2,356** | 7,516–7,942 |
| PCSX2 T65 26714–26723 | 684–695 starts | 27.5k–28.2k | 16.7k–16.9k | 2.65k–3.06k | 837–912 | 135–162 | 4.7k–4.9k |
| PCSX2 whole race min / median / max | — | 19,382 / 33,700 / 46,822 | 9,591 / 20,382 / 29,644 | 1,321 / 2,997 / 5,652 | 474 / 719 / 1,453 | 49 / 180 / 461 | 4,298 / 7,822 / 10,497 |

- At the T65-matched moment, MSCAL matches PCSX2 (685–693 vs 684–695).
  Off and straddle are now close to T65, and inside PCSX2's whole-race
  range; before, they were below its minimum.
- Verts are ~13% and ADC ~60% above T65 at that moment.
- **Zero-area stays ~15× T65** (and ~5× PCSX2's whole-race max). It's
  unchanged by this batch.

### Per-startPC census, 7600–7610 (per vsync) vs T65 §6 and e50f

| tpc | e53c MSCAL | e50f MSCAL | PCSX2 starts | e53c PATH1 draws (on/off/str) |
|---|---|---|---|---|
| 0x44e | 145.5 | 198.1 | 120.7 | 3,989 (2890/872/226) |
| 0x459 | 233.4 | 244.9 | 133.0 | 7,724 (5444/2049/232) |
| 0x10 / 0xe / 0x4 | 46 / 46 / 24 | 46 / 46 / 24 | 46 / 46 / 24 | 0 / 0 / 1,499 |
| **0x741** | **38.2** | **0** | 39 | 1,111 (1064/29/18) |
| **0x2 / 0x8** | **12 / 4** | **0 / 0** | 12 / 4 | 0 / 0 |
| **0xe0** | **16.5** | 0 | 3 | 1,650 (1264/290/96) |
| **0x28c** | **5** | 0 | 3 | 145 (94/49/2) |
| 0xd7 / 0xf2 / 0xfb | 60.8 / 30 / 4.5 | 22 / 11.3 / 2 | 49.7 / 23 / 5 | 2,187 / 346 / 367 |
| 0x134 / 0x147 / 0x140 | 9 / 3 / 7.4 | 1.0 / 5.7 / 1.0 | 8 / 3 / 7 | 1,532 / 389 / 75 |
| 0x22a / 0x0 / 0xa / 0x6 / 0x73 | 20 / 81 / 16 / 2 / 11 | 20 / 93 / 16 / 2 / 10 | 20 / 81 / 16 / 2 / 11 | 0 / 3,068 / 531 / 80 / 469 |
| 0x257 | 33.6 | 35.7 | 35 | 70 |
| 0x104 / 0x122 | 2 / 1 | — | not in T65 list | 165 / 40 |
| 0x189 | 3.0 | 13.3 | not in T65 list | 270 |

- **All five programs missing in E50 now start** (0x741, 0x2, 0x8, 0xe0,
  0x28c). 0x741, 0x2, 0x8, 0x0 and the HUD programs match T65's rates.
- 0x44e/0x459 are still above T65 (×1.2 / ×1.75), and 0xe0 is at 5.5× T65.
- The windows are different race moments, as in E50; the 8256–8265
  census wasn't printed.

### Race camera (vsync 7606, all 3D programs; `an-e53c-t65.md`)

| Block | abs col x | abs col y | abs col z | abs col w | x.y | x.w | y.w | y/x | NaN/Inf/den |
|---|---|---|---|---|---|---|---|---|---|
| e53c A (0x44e, 0x459) | 0.266262 | 0.310638 | 1.000067 | 1.000000 | −4.6e-09 | 5.0e-09 | −1.1e-08 | 1.1667 | none |
| e53c B (0x134, 0x147, 0x189, 0xf2, 0xd7, 0x104, 0xe0, 0xfb, 0x122, 0x741, 0x22a, …) | 0.266262 | 0.310638 | 1.002002 | 1.000000 | same | same | same | 1.1667 | none |
| PCSX2 T65 §5d A / B | 0.266262 | 0.310638 | 1.000066 / 1.002002 | 1.000000 | ≤1.6e-09 | ≤3.7e-09 | ≤1.8e-08 | 1.1667 | none |

The invariants are met. Col y is now equal to T65 (e50f was 1 digit off),
and the 2D programs (0x10, 0xe, 0x4) carry the 2D matrix.

### VU1 budget exits (gfx 7590–8280, 691 vsyncs)

| Run | vsyncs with 0 exits | with exits |
|---|---|---|
| e53c | 682 | **9 vsyncs × 33 exits** (7656, 7658, 7726, 7759, 7764–7766, 7785, 7786), each at vu_maxcyc = 65,536 (the cap). vu_maxcyc median 23,838 |
| e50f (1300–7610 file) | 210 | 334 × 1, 67 × 2 (17 of 19 drawing vsyncs in 7590–7610 at 1) |

The steady per-vsync exit is gone. Now there are short bursts of 33
capped programs on 9 vsyncs. Which program exhausts wasn't identified
(`PS2X_VU1_TRACE` off).

### TEX1 K (`tex1k-e53c.md`; GIF dump 8258–8265, every textured prim; K = bits 32–43, signed 7.4)

textured prims: 149779, distinct K: 16
| K (hex) | K (value) | prims |
|---|---|---|
| 0x000 | 0.00 | 70383 |
| 0xf79 | -8.44 | 34939 |
| 0xf4e | -11.12 | 23674 |
| 0xf20 | -14.00 | 8262 |
| 0xf47 | -11.56 | 3317 |
| 0xbec | -65.25 | 2205 |
| 0xcc0 | -52.00 | 2065 |
| 0xf2d | -13.19 | 1653 |
| 0xf39 | -12.44 | 1197 |
| 0xca1 | -53.94 | 931 |
| 0x801 | -127.94 | 490 |
| 0xf1f | -14.06 | 236 |
| 0xf08 | -15.50 | 126 |
| 0xc0c | -63.25 | 126 |
| 0xc72 | -56.88 | 126 |
| 0xcb0 | -53.00 | 49 |

| path | VU1 startPC | prims | distinct K | top K |
|---|---|---|---|---|
| 1 | 0x22c8 | 47793 | 9 | 0xf4e×19166, 0xf79×13242, 0xf20×4968, 0x000×3990 |
| 1 | 0x2270 | 25093 | 11 | 0x000×9544, 0xf79×4842, 0xf4e×4508, 0xf20×3294 |
| 1 | 0x0 | 18053 | 1 | 0x000×18053 |
| 1 | 0x9a0 | 13580 | 2 | 0xf79×6790, 0x000×6790 |
| 1 | 0x6b8 | 7128 | 6 | 0x000×3564, 0xf79×2304, 0xf39×882, 0xf08×126 |
| 1 | 0x700 | 7000 | 2 | 0xf79×3500, 0x000×3500 |
| 1 | 0x3a08 | 4861 | 1 | 0x000×4861 |
| 3 | 0x12b8 | 3493 | 1 | 0x000×3493 |
| 1 | 0x398 | 3283 | 1 | 0x000×3283 |
| 1 | 0x820 | 2680 | 2 | 0xf79×1340, 0x000×1340 |
| 1 | 0x790 | 2522 | 5 | 0x000×1261, 0xf79×773, 0xf39×315, 0xf1f×124 |
| 1 | 0xa38 | 2266 | 2 | 0xf79×1133, 0x000×1133 |

- **K is per object now**, where E51 saw 0x801 on every terrain TEX1.
- The terrain programs 0x22c8/0x2270 use 0xf4e, 0xf79, 0xf20, 0xf47, 0xf2d,
  0xf39, 0xf1f, 0xf08 (−8.4 … −15.5). PCSX2 at 00:00:18 has 0xef2 … 0xf4e
  (−17.1 … −11.1); 0xf4e, 0xf47 and 0xf1f appear on both sides.
- **0x801 remains on 490 prims, all from 0x2270** (0.3% of textured prims).
- A second group, 0xbec … 0xcb0 (−52 … −65), comes from 0x22c8/0x2270/
  0x6b8/0x790 on 5,502 prims. It's not in E51's PCSX2 list: either
  different objects at this moment, or a remaining K defect.
- K = 0 covers the non-terrain programs (0x0, 0x3a08, 0x398, PATH3 HUD).
- Units differ from E51's table (per prim here, per TEX1 write there).

### Race frames, viewed by eye (`frames/`)

| Frame | What I see |
|---|---|
| `e53c-race-tick7633.png` (00:00:09) | A coherent **snow bank and ridge**, lit white-blue with visible surface variation. Bare dark **tree trunks** (no foliage) along the ridge, dark rock masses behind. The start-gate structure (dark outline) in the foreground. A small **rider** figure at the gate. **HUD** complete (2ND/2, 00:00:09, 1%, 2 MPH, meter). Sky and lower foreground are flat dark blue/black: no sky dome, no sun |
| `e53c-race-tick8274.png` (00:00:19) | Continuous **snow slopes** on both sides, blue-shaded with white lit patches. Silhouetted trunks and poles, dark rock shapes, the **snow spray trail** from the rider (rider small, at the trail's head). **HUD** complete (2ND/2, 00:00:19, 3%, 44 MPH). Sky black, lower half dark; the slopes look smoothly shaded rather than clearly snow-textured |
| `E50/frames/e50f-race-tick7622.png` / `…8275.png` (before) | sky with sun, lens flare and fog; terrain = dark ground with scattered light-blue shard polygons; HUD present |
| `T65/t65-shot-t65a-race.png` (PCSX2 00:00:18) | fully textured snow, trees with foliage, rock walls, distant mountains, sky; rider large in frame; HUD |

In short: the terrain is now whole geometry (slopes, ridges, trunks, rocks)
where E50 drew shards. Compared with PCSX2 it's still far off:
- no sky or sun (E50 had them);
- no tree foliage;
- dark/black regions where PCSX2 shows lit snow and distant mountains;
- terrain textures look flat.

Rider and HUD are present in all e53c race frames.

### What Part 2 establishes (tables only; the orchestrator decides)

| Question | Answer |
|---|---|
| Where the time goes | VU1 interpreter (39–46%) + software GS (37–45%). VU0 is 3%, guest code ~8%, E37 text log ~5% (dev tap) |
| Race camera | T65 invariants met |
| TEX1 K | per object (−8.4 … −15.5) on terrain; 0x801 only on 490 prims from 0x2270; a −52 … −65 group unexplained |
| Programs missing in E50 | all five now start; MSCAL matches T65 at the matched moment |
| Still off vs PCSX2 | zero-area ~15× T65; verts +13%, ADC +60%; 0x459/0xe0 over-called; 9 vsyncs with 33 capped VU1 programs; no sky/sun; no foliage; dark regions |

Recommended next (the orchestrator decides):
1. **Speed:** the VU1 interpreter and the software GS are the two budgets
   that matter now; VU0 isn't. Separately, the E37 VIF text log formats on
   every VIF1 packet even in this run (~5%); check whether it's gated in
   no-diagnostic builds.
2. **Correctness:** zero-area prims, the sky/sun loss (E50 drew the sky),
   the 0xbec … 0xcb0 K group and the 0x801 leftovers on 0x2270 are the
   next discriminators. A PCSX2-vs-recomp GIF diff of 0x2270/0x22c8 at
   8258–8265 (E51's tooling works on this dump) would name them.

### Part 2 receipts

- This dir: `e53_sampler.sh`, `e53_sample_table.py`,
  `e53_sample_incl.py`, `e53_tex1k.py`, `prof1-e53c.md`, `prof2-e53c.md`,
  `tex1k-e53c.md`, `an-e53c-t65.md`, `an-e53c-t65-8256.md`,
  `sample1-e53c-tick4327.txt.gz`, `sample2-e53c-tick8247.txt.gz`,
  `frames/e53c-race-tick7633.png`, `frames/e53c-race-tick8274.png`.
- Budget: 1 boot (900 s, OK'd exception), no builds, no code change, no
  boot (c).
