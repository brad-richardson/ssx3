# E52 report: R5900 FPU and COP2 (VU0 macro) translation semantics vs PCSX2

Brief `local/muse/prompts/E52.md`. Worker: Claude Code (Opus pane). Tables,
receipts and a recommendation; the orchestrator decides. **No fixes
applied. No boots.** 1 build (test only).

## Outcome

- **30 audit tests, 27 fail on `eac6cba`** (597 existing tests still pass;
  627 total, 600 pass). The 3 that pass are sanity checks (CVT.W.S/ABS/NEG
  after E50, VOPMULA/VOPMSUB lanes, CFC2 VI). Each numeric test runs the
  generator's own translation of the encoding (written into a header at
  build time), not a hand copy.
- **Three structural defects in VU0 macro translation**, all silent (no
  crash, wrong data), all of the E50 kind (wrong field/register/target):
  1. **VSQI (14 sites) swaps its register fields and writes EE RAM instead
     of VU0 data memory.** `vsqi $vf2, ($vi1++)` is emitted as "store vf1
     at EE address vi2·16, increment vi2". SSX 3 uses it to upload 4–5
     qwords at a time to VU0 data (0x229f30, 0x229f88 at
     `vi1 = a0·5 + 0x50`, 0x3feb38). The VU0 data stays stale, and EE RAM
     0x0000–0x3FF0 gets overwritten. VLQI (1 site) also reads EE RAM.
  2. **VCALLMSR (8 sites) reads `ctx->vi[27]`, past the 16-entry VI
     array**, instead of CMSAR0. Every site sets CMSAR0 three
     instructions earlier (`ctc2 rX, $vi27`, which the recomp stores in
     `vu0_cmsar0`), then starts VU0 at whatever sits in the upper half of
     `vu0_r` lane y.
     0x22A830 (the VCALLMSR at 0x22aa4c) sits in the same code area as the
     VSQI uploaders' caller 0x22ADD8 (it calls 0x229f30 and, through
     0x2425c0, 0x229f88). The call chain between them was not traced.
  3. **CTC2 CMSAR1 (1 site, 0x3fed54) doesn't start VU1** (PCSX2 runs
     `vu1ExecMicro`); VRNEXT (2 sites) never writes its ft; VRINIT/R and
     CTC2/CFC2 R use invented formats.
- **VU0 Q-unit ops (479 sites) give 0 where PCSX2 gives ±FMAX or
  sqrt(|x|):** VDIV x/0 → 0 (85 sites), VSQRT of a negative → 0 (285),
  VRSQRT of 0 or a negative → 0 (104). VRSQRT also drops fs. That is masked
  in SSX 3, because every site divides vf0.w = 1.
- **FPU DIV.S (802 sites):** divide-by-zero gives ±Inf where PCSX2 gives
  ±FMAX, the sign comes from fs only, and a denormal divisor isn't treated
  as zero. Inf then turns into NaN downstream, which the EE never produces.
- **VFTOI0 (46 sites):** positive overflow and the Inf pattern give
  0x80000000 where PCSX2 gives 0x7FFFFFFF (sse2neon copies x86's
  "indefinite" value).
- **Global numeric model (≈31k arithmetic sites):** PCSX2 runs EE FPU and
  VU0 math round-toward-zero with DAZ/FTZ, and clamps Inf/NaN to ±FMAX and
  denormals to ±0. The recomp runs IEEE round-to-nearest on the EE thread
  with none of that. FPU MADD/MADDA.S are also **fused into ARM `fmadd`**
  by clang's default `-ffp-contract=on` (seen in the E50 runner object).
  Each op is off by at most 1 ulp, except near overflow, near underflow,
  and where an FMA changes a cancellation.

## Pins

| Pin | Value |
| --- | --- |
| Recomp | fork `~/dev/PS2Recomp` `ssx3` @ `eac6cba`; audit worktree `~/dev/ssx3-work/E52/PS2Recomp`, branch **`e52-audit` @ `96fc89b`** (test-only, parent `eac6cba`, not pushed) |
| PCSX2 reference | bytesize `/home/brad/pcsx2-g7/pcsx2` @ `9056c0834`; copies in `~/dev/ssx3-work/E52/pcsx2-ref/` (`SHA256SUMS`): `FPU.cpp`, `VUops.cpp`, `VUflags.cpp`, `VU0.cpp`, `VU0micro.cpp`, `iFPU.cpp`, `iFPUd.cpp`, `microVU_Macro.inl`, `Pcsx2Config.cpp`, headers; `COP2.cpp` read in place. Reference = the interpreters; the EE recompiler differs only in DIV.S rounding (nearest via `FPUDivFPCR`) |
| Census input | canonical `~/dev/ssx3-work/codegen-ssx3` (E50 codegen, 9,457 files) |
| Census tool | `census.py` (this dir), which decodes the raw word in every `// 0xADDR: 0xWORD` comment; output `census.md` |
| Test binary | `~/dev/ssx3-work/E52/build/ps2xTest/ps2x_tests` sha256 `8d9fc895b05c58398899e3f27b323c1a8834a4ef4966b81aceed20cc8f51f614` (Release, logs OFF, Homebrew LLVM clang -O3, arm64) |

## Op table

Sites = emitted sites / unique guest addresses in `codegen-ssx3`
(`census.md`). "fields" = what the generator reads vs what the encoding
defines (fs = bits 15:11, ft = 20:16, fd = 10:6; VU dest = 24:21 with x = bit 24;
fsf = 22:21, ftf = 24:23). Verdicts are from the code read. The global table's
test column and the failing-tests table below name the test in
`ps2_fpu_cop2_audit_tests.cpp` (suite `E52FpuCop2Audit`) that covers each
"differs".

### Global rules (apply to every arithmetic row below)

| # | Rule | PCSX2 (reference) | Recomp `eac6cba` | Verdict | Test |
|---|---|---|---|---|---|
| G1 | Host rounding | EE FPU and VU0: round toward zero, DAZ + FTZ (`Pcsx2Config.cpp:32-41`, `DEFAULT_FPU/VU_FP_CONTROL_REGISTER`); the EE recompiler switches to nearest only around DIV.S (`FPUDivFPCR`, `iFPU.cpp:1097`) | host default: round to nearest even, no flush-to-zero on the EE thread (only the VU1 core sets `FE_TOWARDZERO`, scoped, `ps2_vu1_core.cpp:1679/1971`) | **differs** (1 ulp per op) | FPU rounding, VU0 VADD/VMUL rounding, SQRT.S, CVT.S.W, VITOF0, VDIV, VSQRT |
| G2 | Operand clamp | Inf/NaN bit patterns read as ±FMAX, denormals as ±0 (`fpuDouble`, `vuDouble`) | IEEE: Inf/NaN propagate, denormals kept | **differs** | FPU operands, VU0 clamp |
| G3 | Result clamp | overflow → ±FMAX, denormal → ±0 (`checkOverflow`/`checkUnderflow`, `VU_MAC_UPDATE`) | IEEE: ±Inf, denormals | **differs** | FPU results, VU0 flush |
| G4 | Fused multiply-add | product rounded, then added (x86 SSE, no FMA) | clang's default `-ffp-contract=on` fuses the single expression `FPU_ADD_S(ctx->f_acc, FPU_MUL_S(a,b))` into ARM `fmadd`: E50 runner object `unity_242_cxx.cxx.o`, `sub_003C06B0` has 16 `fmadd` for its 16 MADD/MADDA.S sites. VU macro MADD uses two intrinsics in two statements → not fused | **differs (FPU MADD/MADDA only)**; VU same | FPU MADD, VU0 VMADDw |
| G5 | Flags | FPU FCR31 O/U/D/I/C; VU MAC + status per op | FPU: only C (compares) and a wrong DZ bit (0x100000) on DIV; VU: MAC/status never computed | differs, **no consumer found**: 0 CFC1 sites; CFC2 MAC/status/clip reads only in the context save/restore routines 0x31a308, 0x3c0858, 0x3fe828 | none |

### EE FPU (COP1)

| Op | Sites | Fields | PCSX2 | Recomp | Verdict |
|---|---|---|---|---|---|
| LWC1 / SWC1 | 23,766 / 25,600 | rt, base, imm ✓ | raw 32-bit copy | raw copy via memcpy | same |
| MTC1 / MFC1 | 8,248 / 1,857 | rt, fs ✓ | MFC1 sign-extends to 64 | `SET_GPR_U32` sign-extends | same |
| MOV.S | 3,793 | fd, fs ✓ | bit copy | `(float)` copy (bit-preserving on arm64) | same |
| NEG.S / ABS.S | 526 / 293 | fd, fs ✓ | sign-bit xor / clear | `-x` / `fabsf` (sign-bit only) | same (flags G5) |
| ADD.S / SUB.S / MUL.S | 4,300 / 3,035 / 8,456 | fd, fs, ft ✓ | G1–G3 | IEEE nearest | **differs** (G1–G3) |
| ADDA.S / MULA.S | 41 / 1 | fs, ft ✓ | same as ADD/MUL into ACC | same into `f_acc` | **differs** (G1–G3) |
| MADD.S / MADDA.S | 44 / 184 | fd, fs, ft ✓ | acc + round(fs·ft), G1–G3 | fused `fmadd` (G4), nearest | **differs** (G1–G4) |
| MSUB.S / MSUBA.S | 0 / 0 | ✓ | | | n/a |
| DIV.S | 802 | fd, fs, ft ✓ | divisor exp = 0 (±0 or denormal) → ±FMAX with sign fs⊕ft (0/0 too), flags D/I; else fs/ft rounded (nearest in EE recompiler, chop in interpreter), clamp | only exact ±0 divisor caught; result `copysignf(INF, fs*0)` = ±Inf by sign of fs only; denormal divisor → Inf; flag bit 0x100000 | **differs** |
| SQRT.S | 108 (all fs = 0) | ft ✓ (E50 fix) | sqrt(\|ft\|), ±0 kept, chop | sqrt(\|ft\|), ±0 kept, nearest | **differs** (G1 only) |
| RSQRT.S | 0 | fs, ft ✓ (E50 fix) | | | n/a |
| CVT.W.S | 992 | fd, fs ✓ | truncate, saturate by sign past 2^31 | same (E50 `Ps2FpuCvtWS`) | same |
| CVT.S.W | 1,670 | fd, fs ✓ | (float)int under chop | `(float)int` nearest | **differs** above 2^24 |
| MAX.S / MIN.S | 110 / 268 | fd, fs, ft ✓ | integer sign-magnitude compare (`fp_max`/`fp_min`) | `std::max`/`std::min` on floats | **differs** on ±0 and NaN patterns |
| C.EQ / C.LT / C.LE | 689 / 3,048 / 1,148 | fs, ft ✓ | compare `fpuDouble` operands (denormal = 0, Inf/NaN = ±FMAX) | IEEE compare | **differs** on denormals and Inf/NaN patterns |
| C.F.S | 0 | | clears C | clears C | n/a |
| BC1F/T/FL/TL | 2,607 / 598 / 620 / 1,044 | ✓ | C bit 23 | bit 23 | same |
| CFC1 | 0 | | FCR0 = 0x2E00 | FCR0 = 0 | n/a |
| CTC1 FCR31 | 1 | ✓ | stores all bits | masks `0x0183FFFF` | differs, no reader (0 CFC1) |

### COP2 / VU0 macro

| Op | Sites | Fields | PCSX2 | Recomp | Verdict |
|---|---|---|---|---|---|
| LQC2 / SQC2 | 9,410 / 5,111 | ft, base, imm ✓ | 128-bit copy; LQC2 to vf0 discarded | `READ128`/`WRITE128`; low 4 address bits not masked; LQC2 to vf0 writes vf0 (1 site, 0x3fe9bc, context restore) | same for aligned addresses (unaligned untested) |
| QMTC2 / QMFC2 | 1,121 / 451 | rd, rt ✓ | 128-bit copy | 128-bit copy | same |
| VADD/VSUB/VMUL (+bc, q, i) | 12,858 float-op sites in all | fd, fs, ft, bc, dest ✓ (dest bit 3 = x lane) | G1–G3, MAC/status | `_mm_add/sub/mul_ps` (nearest, IEEE) | **differs** (G1–G3, G5) |
| VMADD/VMSUB (+A, bc, q, i) | VMADDw 1,782, VMADDAz 1,672, VMADDAy 895, VMULAx 889, … | ✓ | acc ± round(fs·ft) | mul then add, separate intrinsics (not fused) | **differs** (G1–G3) |
| VOPMULA / VOPMSUB | 258 / 241 | ✓, lanes (y·z, z·x, x·y) ✓ | | | **differs** (G1–G3 only) |
| VMAX / VMINI (+bc, i) | 6+18 / 6+18 | ✓ | integer sign-magnitude compare | `_mm_max/min_ps` → sse2neon `vmaxq/vminq_f32` (ARM FMAX: ±0 right, NaN propagates) | **differs** on negative-NaN patterns (x86 host: also ±0) |
| VFTOI0 | 46 | ✓ | ≥ 2^31 (and Inf/NaN) saturate by sign: + → 0x7FFFFFFF | `_mm_cvttps_epi32` → sse2neon fix-up returns **0x80000000 for every value ≥ 2^31 and NaN** (x86 semantics) | **differs** on positive overflow |
| VITOF0 | 27 | ✓ | (float)int under chop | `_mm_cvtepi32_ps` nearest | **differs** above 2^24 |
| VDIV | 86 (85 = `0x4a6303bc` Q = vf0.w/vf3.x) | fs, fsf, ft, ftf ✓ | divisor ±0/denormal → ±FMAX by sign xor; else fs/ft chop, clamp | `ft != 0 ? fs/ft : 0` → **Q = 0** on divide-by-zero; denormal divisor → Inf | **differs** |
| VSQRT | 285 (all `0x4a0403bd` Q = sqrt(vf4.x)) | ft, ftf ✓ | sqrt(\|ft\|), chop | `sqrtf(max(0, ft))` → **0 for negatives** | **differs** |
| VRSQRT | 108 (all fs = vf0.w = 1.0) | ft, ftf ✓; **fs/fsf decoded but ignored** | fs/sqrt(\|ft\|); ft = 0 → ±FMAX (0/0 → ±0) | `ft > 0 ? 1/sqrt(ft) : 0` | **differs**: zero/negative ft; the missing fs is masked in SSX 3 (every site divides vf0.w = 1) |
| VCLIPw | 0 | ✓ | +x → bit0, −x → bit1, …, against \|ft.w\|, denormal-aware integer compare | −x → bit0, +x → bit1 (swapped); compares against signed ft.w | differs (0 SSX 3 sites) |
| VMOVE / VMR32 / VABS | 3 / 0 / 2 | ✓ | bit ops; ft = vf0 discarded | bit ops | same |
| VMTIR | 10 | it, fs, fsf ✓ | low 16 bits of fs.fsf | same | same |
| VMFIR / VIADD / VISUB / VIADDI / VIAND / VIOR | 0 | ✓ (read) | | | n/a |
| VWAITQ / VNOP | 480 / 16 | | stall / nop | nop (Q computed immediately) | same |
| **VSQI** | **14** (0x229f30 ×8, 0x229f88 ×5, 0x3feb38 ×1) | **wrong**: address from `vi[fs]` and data from `vf[it]` (fields swapped; `vsqi $vf2,($vi1++)` stores vf1 at vi2·16 and increments vi2) | store vf[fs] to **VU0 data memory** at vi[it]·16 (`GET_VU_MEM`, 4 KiB wrap), post-increment vi[it] | `WRITE128` to **EE address** (vi & 0x3FF)·16, i.e. EE RAM 0x0000–0x3FF0 | **differs (two defects)** |
| VLQI | 1 (0x3feb8c) | ft, is ✓ | load from VU0 data memory | `READ128` from EE address vi·16 | **differs** |
| VILWR / VISWR / VLQD / VSQD | 0 | (VSQD has the same field swap as VSQI) | VU0 data memory | EE memory | differs (0 sites) |
| VRINIT | 2 | fs, fsf ✓ | R = 0x3F800000 \| (fs.fsf & 0x7FFFFF) | invented LCG seed over 4 lanes | **differs** |
| VRNEXT | 2 | **ft ignored** | advance 23-bit LFSR (`AdvanceLFSR`), **write R to ft** | invented 4-lane LFSR; **never writes ft** | **differs** |
| VRGET / VRXOR | 0 | | | | n/a |
| CFC2 VI0–15 / CTC2 VI1–15 | 29+… / 7+… | ✓ | 32-bit VI storage in PCSX2 | 16-bit `vi[]` | same for 16-bit values |
| CFC2 / CTC2 Q, I | 287 (Q) / 0 | ✓ | bits | bits | same |
| CTC2 / CFC2 R | 2 / 1 | ✓ | CTC2 keeps 23 bits \| 0x3F800000; CFC2 returns 23 bits | raw 32 bits into all 4 lanes / raw lane 0 | **differs** (context save/restore only) |
| CFC2 status / MAC / clip | 2 / 3 / 2 | ✓ | live flags | `vu0_status` / `vu0_mac_flags` never updated by macro ops | differs, context save only (G5) |
| CTC2 CMSAR0 | 8 | ✓ | stores start address | stores `vu0_cmsar0` | same |
| **VCALLMSR** | **8** (7 addrs: 0x1223f0, 0x22aa4c, 0x2d20c0, 0x32b6d0, 0x37deb8, 0x391470, 0x3fe824; each preceded 3 instructions earlier by `ctc2 rX, $vi27` = the start address) | **wrong register**: reads `ctx->vi[27]` (encoding's is = 27 = CMSAR0) | `vu0ExecMicro(VI[CMSAR0])` (`COP2.cpp:24-30`) | `ctx->vi[27]` is past the 16-entry `vi[]`: it reads bytes 54–55 from `vi`, i.e. the upper half of `vu0_r` lane y | **differs**: starts VU0 at a garbage address |
| VCALLMS | 7 | imm15 ✓ (masked to 9 bits = 4 KiB) | run from imm·8 until E-bit (async) | synchronous run capped at 4,096 cycles (`executeVU0Microprogram`) | unsure (cap; E44/T57 saw 0 VU0 programs at SC) |
| **CTC2 CMSAR1** | **1** (0x3fed54) | ✓ | **starts VU1** at the written address (`vu1ExecMicro`) | stores `vu0_cmsar1` only | **differs** |
| CTC2 FBRST | 8 | ✓ | masks 0x0C0C and resets VU0/VU1 on bits 1/9 | masks 0x0C0C, no reset | differs (reset side effect) |
| BC2* | 0 | | | | n/a |

## Failing tests (`E52FpuCop2Audit`, on `eac6cba` + tests; full output `tests-e52-on-eac6cba.txt`)

| Test | PCSX2 expects | Recomp gives |
|---|---|---|
| FPU ADD/SUB/MUL.S chop | 0x3f800000 / 0x3f7ffffe / 0x3fc00002 | 0x3f800001 / 0x3f7fffff / 0x3fc00003 |
| FPU overflow clamp | FMAX+FMAX = 0x7f7fffff; −FMAX·2 = 0xff7fffff | 0x7f800000 / 0xff800000 |
| FPU operand clamp | 0x7f800000·0 = +0; denormal + −0 = +0 | 0x7fc00000 (NaN) / 0x00400000 |
| FPU underflow flush | 1e-20² = ±0 | 0x000116c2 / 0x800116c2 |
| FPU DIV.S by zero | 1/+0 = +FMAX, 1/−0 = −FMAX, −1/+0 = −FMAX, 0/0 = +FMAX, 1/denormal = +FMAX | +Inf, +Inf, −Inf, +Inf, +Inf |
| FPU SQRT.S chop | sqrt 5 = 0x400f1bbc | 0x400f1bbd |
| FPU MADD/MADDA.S unfused | +0 | 0x33800000 (fused FMA result) |
| FPU MAX/MIN.S | max(−0,+0) = +0; min(+0,−0) = −0; max(0xffc00000,1) = 1 | −0 / +0 / 0xffc00000 |
| FPU C.EQ/C.LE on fpuDouble | true ×3 | false ×3 |
| FPU CVT.S.W chop | 0x4b800001, 0x4effffff | 0x4b800002, 0x4f000000 |
| VU0 VADD/VMUL chop | 0x3f800000, 0x3fc00002 | 0x3f800001, 0x3fc00003 |
| VU0 overflow/Inf clamp | FMAX, FMAX, +0 | 0x7f800000, 0x7f800000, 0x7fc00000 |
| VU0 denormal flush | ±0 | 0x000116c2 / 0x800116c2 |
| VU0 VMADDAz chop | 0x3f800000 | 0x3f800001 (the unfused half of this test passes) |
| VU0 VMAX negative-NaN pattern | 1.0 | 0xffc00000 (±0 cases pass on arm64) |
| VU0 VFTOI0 saturation | 3e9 → 0x7fffffff; 0x7f800000 → 0x7fffffff | 0x80000000 / 0x80000000 |
| VU0 VITOF0 chop | 0x4b800001, 0x4effffff, 0xcb800001 | 0x4b800002, 0x4f000000, 0xcb800002 |
| VU0 VDIV (`0x4a6303bc`) | 1/+0 = +FMAX, 1/−0 = −FMAX, 1/denormal = +FMAX, 1/3 = 0x3eaaaaaa | 0, 0, +Inf, 0x3eaaaaab |
| VU0 VSQRT (`0x4a0403bd`) | sqrt(−4) = 2, sqrt 5 = 0x400f1bbc | 0, 0x400f1bbd |
| VU0 VRSQRT (`0x4a6403be`) | 1/sqrt(+0) = +FMAX, 1/sqrt(−4) = 0.5 | 0, 0 |
| VU0 VRSQRT reads fs (synthetic) | 6/sqrt(4) = 3 | 0.5 |
| VU0 VCLIPw (synthetic) | 0x09 for w = 1 and w = −1 | 0x06 / 0x36 |
| VU0 VRINIT + VRNEXT | vf3.x = 0x3fe8acf1 | 0 (ft never written) |
| COP2 CTC2/CFC2 R | 0x007fffff | 0xffffffff |
| COP2 VCALLMSR | start from `vu0_cmsar0` | `ctx->vi[27]` (out of bounds) |
| COP2 VSQI | store vf2 at vi1, VU0 memory | stores vf1 at vi2, EE memory via `WRITE128` |
| COP2 CTC2 CMSAR1 | starts VU1 | `ctx->vu0_cmsar1 = …` only |

## Ranking (no fixes; the orchestrator batches them)

Effect classes: **A** = wrong data or wrong control flow wherever it runs
(structural); **B** = wrong value on a reachable edge (zero divisor,
negative sqrt, overflow), which then spreads as Inf/NaN or 0; **C** =
≤ 1 ulp per op everywhere (rounding/fusion) or only on pathological
bit patterns.

| Rank | Defect | Sites (emitted) | Class | Likely effect | Fix size (estimate) |
|---|---|---|---|---|---|
| 1 | VSQI field swap + EE-memory target; VLQI EE-memory source | 14 + 1 | A | VU0 microprogram input tables never reach VU0 data (0x229f30/0x229f88 upload 4–5 qwords per object); EE RAM 0x0–0x3FF0 overwritten | generator: swap fields; route to VU0 data memory (runtime already has `m_memory.getVU0Data()`); VSQD/VLQD/VILWR/VISWR share the code |
| 2 | VCALLMSR reads `vi[27]` (OOB) instead of CMSAR0 | 8 | A | every register-started VU0 program starts at a garbage address (0x22aa4c is next to the VSQI uploaders' caller) | generator one-liner: `ctx->vu0_cmsar0 & 0x1FF` |
| 3 | VDIV/VSQRT/VRSQRT special cases (0 instead of ±FMAX / sqrt\|x\|); VRSQRT drops fs | 85 + 285 + 108 | B | normalisations and reciprocals of zero-length or slightly negative inputs become 0 (PCSX2: FMAX or sqrt\|x\|). Likely in geometry and lighting setup: VSQRT is the 4th most common VU0 op | generator: 3 helpers like E50's `Ps2FpuSqrtS`/`Ps2FpuRsqrtS` |
| 4 | FPU DIV.S by zero/denormal → ±Inf (sign of fs only) | 802 | B | Inf and later NaN in game math where the EE saturates to ±FMAX | generator/runtime: one helper |
| 5 | FPU FMA contraction on MADD/MADDA.S | 228 (3 functions) | C, but systematic | dot products and matrix work in `sub_003C06B0`, `sub_003CCA08`, `sub_003CE410` differ in low bits; cancellations can differ by more | one build flag: `-ffp-contract=off` for the runner (or split the expression in the generator) |
| 6 | Global rounding + DAZ/FTZ + Inf/NaN/denormal clamps (FPU and VU0) | ~18.6k FPU + ~12.9k VU0 float sites | C (1 ulp), B at the edges | slow drift; compare/branch flips near ties; CVT.W.S of values just under an integer; overflow gives Inf/NaN instead of FMAX | rounding + FZ: set FPCR once on the EE thread (DIV.S wants nearest under the EE recompiler); clamps need a per-op helper (costs speed; check the E-lane speed rule) |
| 7 | VFTOI0 positive overflow → 0x80000000 | 46 | B (rare) | coordinates saturate to the wrong sign | runtime helper |
| 8 | CTC2 CMSAR1 doesn't start VU1 | 1 (0x3fed54, via 0x3FEBC0 ← 0x375A08) | A, reach unknown | VU1 program never started from the EE path | runtime call |
| 9 | VRNEXT (doesn't write ft) / VRINIT / R format | 2 + 2 + 3 | A, low reach | random numbers wrong (particles?) | port `AdvanceLFSR` |
| 10 | MAX/MIN.S (±0, NaN patterns), C.EQ/C.LE on denormal/Inf patterns, CVT.S.W/VITOF0 above 2^24 | 378 / 4,885 / 1,697 | C | edge values only | helpers |
| — | Flags (FPU FCR31, VU MAC/status), CTC1 mask, CFC1 FCR0, VCLIPw bit order, LQC2→vf0 | — | no consumer found / 0 sites | none observed | leave |

## Recommended next action (the orchestrator decides)

1. **Batch 1 (structural, generator only, rebuild + regen):** VSQI/VLQI
   (fields + VU0 data memory), VCALLMSR (CMSAR0), VDIV/VSQRT/VRSQRT
   (PCSX2 special cases, read fs), DIV.S (±FMAX), VFTOI0 saturation. The
   E52 tests are the acceptance check. Then one race boot against T65,
   since the VU0 upload/start path is a candidate for E51's remaining
   terrain gap. It is **not proven** to run in the race: T57/E44 saw zero
   VU0 programs at SC. A cheap reach check first: count executions of
   0x229f30/0x229f88/0x22aa4c in a race boot (existing call trace) before
   or alongside the fix.
2. **Batch 2 (numeric model):** `-ffp-contract=off` for the runner, then
   the EE-thread FPCR (round-toward-zero + FZ), measured for speed, with
   clamps as a separate decision.
3. Leave the flags as they are unless a consumer turns up.

## Gaps

- No boot: whether any of the class-A sites run during the race is
  unmeasured. T57 (PCSX2) and E44 (recomp) saw no VU0 programs at SC only.
- PCSX2 reference is the interpreter, and T-lane traces use the EE
  recompiler + microVU. The recompiler's operand/result clamping modes
  (`fpuOverflow`, `vu0Overflow` default on; extra/full modes off) were not
  diffed op by op. Only its DIV.S rounding difference is noted.
- FMA contraction is confirmed in one unity object (`unity_242`, 16/16
  sites). The other two MADD files were not disassembled.
- LQC2/SQC2 don't mask the low 4 address bits (EE LQ ignores them).
  Aligned use is assumed; not tested.
- VCALLMS runs synchronously with a 4,096-cycle cap
  (`executeVU0Microprogram`); PCSX2 runs until E-bit, asynchronously.
  Marked unsure; no test.
- The x86 build of the runtime (not used for SSX 3) differs from arm64 on
  VMAX/VMINI ±0. That wasn't tested.

## Exact commands

```
git -C ~/dev/PS2Recomp worktree add -b e52-audit ~/dev/ssx3-work/E52/PS2Recomp ssx3
scp-equivalent: ssh bytesize "wsl -d Ubuntu -- cat /home/brad/pcsx2-g7/pcsx2/pcsx2/<f>" > ~/dev/ssx3-work/E52/pcsx2-ref/<f>
python3 local/research/E52/census.py > local/research/E52/census.md
~/dev/ssx3-work/E52/build.sh ~/dev/ssx3-work/E52/PS2Recomp ~/dev/ssx3-work/E52/build audit   # waits for a quiet host; nice -n 10 ninja -j8 ps2x_tests; 16 s
cd ~/dev/ssx3-work/E52/PS2Recomp && ~/dev/ssx3-work/E52/build/ps2xTest/ps2x_tests   # 627 tests, 600 pass, 27 fail (all E52)
objdump -d ~/dev/ssx3-work/E50/build/ps2xRuntime/CMakeFiles/ps2_game_objects.dir/Unity/unity_242_cxx.cxx.o   # 16 fmadd in sub_003C06B0
```

## Receipts (this dir)

- `census.py`, `census.md`: per-op site counts (emitted/unique/files), SSX 3 encodings per op.
- `ps2_fpu_cop2_audit_tests.cpp`, `e52_snippet_gen.cpp`: the test file and the generator-snippet tool (copies of fork `96fc89b`).
- `e52_snippets.h`: the generator's translation of every tested encoding, as built.
- `tests-e52-on-eac6cba.txt`: suite output for `E52FpuCop2Audit` + totals.
- `~/dev/ssx3-work/E52/`: `suite-audit.log`, `build-audit.log`, `cmake-audit.log`, `build.sh`, `pcsx2-ref/`.
- Budget: 1 build, 0 boots, ~1 h 15 min; disk E52 ≈ 115 MB (build 92 MB, worktree 22 MB).

