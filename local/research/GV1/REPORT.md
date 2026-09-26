# GV1 — VU1 on the GPU: feasibility spike

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/GV1.md`, 2026-09-26 from 11:15 EDT.
Design only, plus one Mac microbenchmark. No product code, no fork changes, no device use.
Code lives in `~/dev/ssx3-work/GV1/`. The receipts here are text only.

## Headline

- **Exact VU1 arithmetic on a GPU is possible, and it is bit-exact.**
  - A GLSL port of VR4's exact FMAC core matched the real CPU core (fork `b97b241` sources) on
    **1,000,000 of 1,000,000 cases**:
    - value bits, MAC and status, with **0 mismatches**;
    - all 72 FMAC encodings, VR4's operand generator;
    - 214,648 cases set O, 33,873 set U and 207,536 set Z.
  - It runs on Apple's GPU through MoltenVK, which has **no fp64**. VR4's "exact result" is a double
    rounded to 53 bits, so the kernel emulates that rounding in int64. Denormal and Inf
    intermediates take a software path.
- **Exactness costs ~128× the plain-float rate on the GPU.** Mac M5 Pro GPU, saturated:

  | Kernel | FMAC ops/s |
  | --- | ---: |
  | Exact | 3.3 G |
  | Lite (normalized, fp32 flags only) | 23 G |
  | Plain fp32 | 420 G |

  For scale, the CPU core through its test hook runs **70 M/s on one M5 core**.
- **Only a vertex-parallel shape is viable.**
  - A frame's VU1 FMAC work (≈ 0.7–1.0 M FMAC, ≈ 1–2 M with the rest of the program) costs
    **≈ 0.3–0.6 ms on the M5 Pro** if every vertex gets its own thread.
  - Running each of the 1,040 programs as one thread is latency-bound:
    - measured: **2.9 µs per dependent exact FMAC**;
    - the average program costs ≈ 2 ms per frame;
    - the longest program (23–27 k cycles) alone would cost ≈ 50 ms.
  - Vertex-parallel means taking apart the software-pipelined VU1 loops. That is compiler work,
    not a translation.
- **The Odin GPU budget decides it, and it is already spent.**
  - paraLLEl-GS alone takes **≈ 15.5 M GPU cycles per guest frame**. That is 23.9 ms at 660 MHz
    (FS2 T2) and 19.7 ms at 781–826 MHz (FS2 P1/P2), where the GPU is 75–78 % busy at 0.64×.
  - Against a 16.7 ms frame, GS alone needs ≥ 930 MHz at 100 % busy. Against 8.3 ms it needs
    ≥ 1.86 GHz; the highest clock these logs show is 967 MHz.
  - Exact VU1 on the Adreno adds an estimated **0.7–4 M cycles (1.1–6.1 ms at 660 MHz)**. The
    Adreno scaling of 4–10× the M5 Pro is an **assumption, not measured**.
  - That puts GS + VU1 at **16.2–19.8 M cycles per frame: over 16.7 ms at any clock logged here,
    and about 2× over 8.3 ms.**
- **What it would save on the CPU:** most of the MTVU unit's generated VU1 time, ≈ 16 ms per frame
  after D1. It would cost one frame of GS latency (a per-frame GPU batch and fence) and a PATH1/2/3
  stitch on the CPU.
- **Verdict: no-go as product work now (agrees with the park).** It is a **go for a two-step
  proof only if Brad wants the option kept alive**:
  1. run this exact kernel on the Odin, to replace the 4–10× assumption;
  2. hand-port one hot program (`a564` 0398, B0628's loop, 13.7 % of unit time) as a per-vertex
     kernel, and check its PATH1 output bit for bit against the CPU on a captured frame.

  The CPU routes (VP1 multi-core VU1, D1b/D2) attack the same 16 ms without spending the GPU,
  which is the scarcer resource on the Odin.

## 1. Program census (7 images)

**Sources:**
- canonical images `~/dev/ssx3-work/vu1gen-ssx3/vu1_<hash>.cpp`, the 16 KiB microcode each embeds
  as `(lower, upper)` pairs;
- disassembled with `vu1dis.py` (VU ISA tables; checked against VR4's own description of B2a10);
- time-weighted with VR4's per-address MTVU samples. These are CP1 R2b, Odin play build, 405
  frames: `~/dev/ssx3-work/VR4/asm/iphist-all.txt`.

Block samples are spread evenly over the block's pairs. That is an approximation inside a block
but exact per block. Receipts: `census.txt`, `loops.txt`, `census.py`, `loops.py`, `vu1dis.py`.
The disassembly listings are derived from game code, so they stay in scratch.

### Where unit time goes, per image (MTVU generated code = 21.62 ms/frame on the Odin)

| Image | Non-NOP pairs | E-bit ends | ms/frame | Share |
| --- | ---: | ---: | ---: | ---: |
| `f587398b…` | 1,882 | 13 | 8.68 | 40.1 % |
| `a56458ed…` | 1,869 | 21 | 6.31 | 29.2 % |
| `ad77d08a…` | 1,801 | 15 | 2.88 | 13.3 % |
| `b3bdaeae…` | 1,877 | 7 | 2.64 | 12.2 % |
| `a214cc50…` | 1,792 | 20 | 1.11 | 5.1 % |
| `00df9699…`, `77b7173b…` | 1,873 / 1,886 | 21 / 13 | 0 | 0 % (not in the race window) |

### Where it goes, per innermost loop (`loops.txt`)

**79 % of generated VU1 time is inside innermost loops**, and those loops are per-vertex.

| Image | Loop | Body pairs | ms/frame | Share | FMAC | LQ/SQ | DIV | CLIP | FTOI | Flag ops | Branches |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| a564 | 0628-0718 (B0628) | 31 | 2.97 | 13.7 % | 24 | 13 | 1 | 1 | 2 | 1 | 1 |
| f587 | 2a10-2a50 (B2a10) | 9 | 2.21 | 10.2 % | 6 | 6 | 1 | 0 | 1 | 0 | 1 |
| a564 | 0448-07b8 (outer; rest of 0628's program) | 111 | 1.58 | 7.3 % | 72 | 39 | 3 | 3 | 6 | 4 | 2 |
| f587 | 0a58-0af0 (B0a58) | 20 | 1.18 | 5.4 % | 16 | 2 | 0 | 0 | 1 | 0 | 1 |
| ad77 | 14b0-1560 | 23 | 1.02 | 4.7 % | 16 | 10 | 2 | 2 | 2 | 2 | 3 |
| f587 | 2950-2b00 | 55 | 0.64 | 3.0 % | 24 | 24 | 4 | 0 | 4 | 0 | 3 |
| a564 | 09b0-0aa0 | 31 | 0.54 | 2.5 % | 24 | 6 | 1 | 1 | 2 | 1 | 1 |
| f587 | 30d8-3130 | 12 | 0.50 | 2.3 % | 8 | 4 | 1 | 1 | 1 | 1 | 2 |
| ad77 | 13f8-1570 | 48 | 0.44 | 2.0 % | 32 | 20 | 4 | 4 | 4 | 2 | 4 |
| (15 rows in `loops.txt`) | | | | | | | | | | | |

### What the programs look like

- **Loop shape.** The hot programs all share one shape:
  1. XTOP picks the double-buffer half.
  2. A prologue loads the matrices and lights from VU memory (LQ ×12 in `a564`'s 0398 program), plus
     LOI constants.
  3. A software-pipelined **per-vertex loop**: ILW of the count, LQI of the vertex inputs, a
     matrix × vector (MULAx/MADDAy/MADDAz/MADDw), and one **DIV Q per vertex** for the perspective
     divide (2–4 per iteration where the loop is unrolled).
  4. FTOI4 for the GS XYZ, ITOF12/ITOF15 for ST and colour.
  5. **CLIP + FCAND** on the last three clip results (strip ADC culling), then SQI into the output
     GIF packet.
  6. **One XGKICK after the loop, then E.**
- **B0a58** is lighting: normal transform plus light accumulation, 16 FMAC per vertex, no DIV.
- **Branches.** Most loops are straight-line bodies with an IBNE/IBGTZ counter. Some (`ad77`
  14b0, `b3bd`) branch **per vertex on FCAND results** to an out-of-loop path, which is a
  data-dependent exit (culling or clipping).
- **Calls.** Many BAL/JR subroutine calls sit outside the hot loops: 136 BAL and 78 JR
  statically.
- **EFU.** ERSQRT, MFP and WAITP appear in 3 regions, all with ~0 sampled time. **The race does not
  use EFU in hot code.**
- **FDIV.** DIV is in every transform loop. RSQRT appears in two cold regions.
- **Integer and flags.** IADDIU, ISUBIU, IADD and IBNE drive the loop control. The clip flag
  (CLIP, FCAND, FCOR, FCSET) carries culling. MAC flags (FMAND etc.) are rare. Every FMAC still
  *produces* MAC and status, because the exact core computes them unconditionally.
- **Memory access.**
  - Contiguous LQI/SQI streams through the double-buffered input/output areas (`vi` pointers from
    XTOP/ILW).
  - Constant LQ from low VU memory.
  - No gathers beyond ILW/ILWR of headers.
  - Output is written in place into the GIF packet that XGKICK sends.
- **Program state across MSCALs.** `execute()` resets only the scheduler, pc and vf0. VF, VI, ACC,
  Q, P and the flags **persist between programs** (hand-back §1, `ps2_vu1_core.cpp:1351-1394`).
  The hottest program (`a564` 0398) reloads its matrices, I and vi pointers at entry and looks
  self-contained given VU memory and TOP (manual read). The other programs were **not checked**
  (gap, and stage-1 work below).

### Per-frame workload (race)

| Counter | Value | Source |
| --- | --- | --- |
| VU1 programs (MSCAL) per vsync | 1,040 (890–1,155) | gfx_stats t1800–2400 (diag build `56a5e8a`) |
| VU1 programs per tick | 910–1,170 | VR2 det log `d-det-on` t1800–2436 (`runs-vs-tick.txt`) |
| VU1 cycles per vsync | 1.41 M (gfx_stats); 1.02–1.25 M (VR2 det log) | as above |
| Cycles per program | ≈ 1,050–1,190 (max 23–27 k) | as above |
| XGKICKs (PATH1 packets) per vsync | 1,683 | gfx_stats |
| PATH1 bytes per vsync | 2.15 MB | gfx_stats |
| PATH1 primitives per vsync | 32,309 (≈ 31 per program; top: TRISTRIP) | gfx_stats |
| PATH2 / PATH3 packets per vsync | 256 / 28 (PATH3 0.51 MB) | gfx_stats |
| MTVU jobs per race frame | 8 (5 DMA + 3 FIFO); one VIF1 list carries most of the frame | MT1 |
| FMAC instructions per vsync (estimate) | ≈ 0.7–1.0 M (FMAC upper in ~65 % of hot-loop pairs × 1.0–1.4 M cycles) | this census |

## 2. Exactness on the GPU

### Float semantics the kernel has to reproduce

The kernel reproduces the VR4 core (`ps2_vu1_fmac_simd.h` at `b97b241`):

1. **Normalize the operands.** Exponent 0 becomes a signed zero, and exponent 255 becomes a
   signed `0x7F7FFFFF`. So no denormal, Inf or NaN enters.
2. **Compute the value** with the fp32 op in the same order: `acc ± vs*b`, two roundings, **no
   FMA**.
3. **Classify the exact result.** For ADD, SUB and MADD, VR4's "exact" result is the **double**
   `acc ± vs*b`, so it is exact only up to one rounding to 53 bits. From it VR4 derives:
   - Z (zero);
   - S (sign, including −0);
   - O (> FLT_MAX), which overrides the value to ±MAX;
   - U|Z (< FLT_MIN), which overrides the value to ±0.
4. **Product sticky** for MADD, MSUB and OPMSUB comes from the double product.
5. **MAC and status** are assembled from the dest lanes.

What that asks of a GPU (Mac values from `mac-vulkan-floatcontrols.txt`):

| Requirement | Vulkan guarantee | M5 Pro / MoltenVK 1.4.2 | Odin (Adreno 830, Turnip) | Kernel's answer |
| --- | --- | --- | --- | --- |
| fp32 add/sub/mul correctly rounded, RTE | required (SPIR-V precision table); RTE is the default | `shaderRoundingModeRTEFloat32 = true` | not read (no device use) | plain fp32 ops, `precise` (NoContraction) so nothing fuses |
| No FMA contraction | `precise`/NoContraction honoured | holds: bit-exact | not verified | as above |
| Double classification | needs fp64 | **`shaderFloat64 = false`** | not read; expected false | **int64 emulation** of RN-53: exact alignment, sticky, round, then threshold compare (`classifySum`) |
| Denormal intermediates (product < FLT_MIN feeding `acc +`; denormal or Inf results that survive classification) | preserve vs FTZ unspecified unless float-controls say so | **neither preserve nor FTZ guaranteed** | not read | software RN-to-float of the 48-bit product, and a software add (`roundToFloat`, `softAdd`), taken only in those cases |
| ±0, Inf, NaN | `SignedZeroInfNanPreserve` | true | not read | inputs are normalized; the Inf result case goes through the software add |
| int64 | `shaderInt64` | true | not read; Adreno has no native 64-bit ALU, so it is emulated either way | used in classification |

### Results (`bench-mac.txt`, 11:54 run; kernel SHAs in `src/SHA256SUMS` and at the top of `bench-mac.txt`)

| Check | Result |
| --- | --- |
| CPU reference | The real VU sources at fork `b97b241`, built standalone (`gen_cases`). `execUpperForTest(instr, simd, direct flags)`. **Scalar vs vector forms: 0 mismatches** over the same 1 M cases. |
| Cases | **1,000,000** from VR4's unit-test generator: the same xorshift seed and operand classes (±0, denormals, Inf/NaN patterns, FLT_MIN/MAX neighbourhoods, U/O-straddling exponents, 1-in-8 cancellations). Only the 72 FMAC encodings, `fd ≠ 0`, direct flag commit. |
| **GPU vs CPU** | **0 mismatches** (value 0, MAC 0, status 0). Every case decoded. 1.45 ms GPU for 1 M cases. |
| Class coverage | 214,648 O, 33,873 U, 207,536 Z cases |

**What this proves:** the arithmetic and flag values of one FMAC can be reproduced bit for bit on a
GPU without fp64, deterministically. The kernel is integer plus correctly rounded fp32, so it
should give the same bits on any conformant device.

**What it does not prove:**
- the VU **timing model** is not ported: flag-pipeline latency, queued flag entries, stalls, the
  FSSET/demote paths;
- the non-FMAC ops are not ported: DIV, SQRT, RSQRT, FTOI/ITOF, CLIP, MAX/MINI, EFU. **VU DIV is
  a real problem**, because Vulkan's fp32 division is **not** correctly rounded (2.5 ULP), so it
  needs its own exact software divide;
- Adreno/Turnip was not tested.

### Throughput (M5 Pro GPU, MoltenVK; one mini lease slot held, a det boot in slot 1, load ≈ 9; best of 5–7 dispatches, means up to 1.6× higher)

Kernel: B2a10's matrix × vector, MULAx, MADDAy, MADDAz and MADDw per vertex, as 4 FMAC ops of 4
lanes, with each vertex depending on the previous one.

| Shape | Exact | Lite (normalize + fp32 + flags from the fp32 result) | Plain fp32 |
| --- | ---: | ---: | ---: |
| **Saturated**: 262,144 threads × 64 vertices (67 M FMAC) | 20.43 ms → **3.28 G FMAC/s** | 2.93 ms → 22.9 G/s | 0.16 ms → 420 G/s |
| **Vertex-parallel frame**: 32,768 threads × 64 (8.4 M FMAC) | 3.11 ms → 2.70 G/s | 0.73 ms → 11.5 G/s | 0.03 ms (at the timer floor) |
| **Program-parallel**: 1,024 threads × 200 vertices (0.82 M FMAC, ≈ one frame of programs) | **2.30 ms** → 0.36 G/s; **2.9 µs per dependent exact FMAC** | 0.39 ms | 0.02 ms |
| Dispatch floor: 64 threads × 1 | 0.026 ms GPU | | |
| **CPU, real VR4 core**, 1 thread, M5 Pro, the `execUpperForTest` path (dependent chain) | vector **69.8 M/s**, scalar 36.4 M/s | | |

**Readings:**
- **Exact is 128× plain and 7× lite when saturated.** The integer RN-53 classification and flag
  assembly are the cost; the float op itself is not.
- **A GPU exact FMAC is ≈ 47× one CPU core's vector core** when the GPU is full. It is **worse than
  a CPU** when there are only ~1,000 threads, each running a long dependent chain.
- The CPU figure comes from the test-hook path, not generated blocks. It is an order-of-magnitude
  anchor, not a speed number.
- These are GPU compute timestamps from a Mac. **They are not guest speed numbers.**

## 3. Data path

A read-only code read (subagent, fork `ssx3` `1c37c41`, paraLLEl-GS `3d72467`; every line cited in
`datapath-readback.md`).

```
TODAY (MTVU, instant-VU1 model: each MSCAL runs to completion inside the VIF1 delivery)
EE: D1 CHCR store ──► job snapshot (GIF+VIF1 chunks) ──► MTVU unit thread
MTVU: processVIF1DataImpl ── UNPACK ─► VU1 data (16 KiB, TOPS double buffer)
                          ── MPG    ─► VU1 code  (7 images, selected by hash)
                          ── MSCAL  ─► VU1 run (generated blocks, exact FMAC, cycle-timed)
                                         └─ XGKICK ─► PATH1 packet (1 QW / 2 cycles, whole at EOP)
                          ── DIRECT ─► PATH2 packet;  MSKPATH3 ─► releases one PATH3 packet
        GifArbiter (PATH1 < PATH2 < PATH3, drain now) ─► GS::processGIFPacket ─► GsWorker queue
GsWorker: gif_transfer (paraLLEl decode: vertex_kick → drawing_kick_append: bbox, degeneracy,
          state/TEX/CLUT/page-hazard checks, memcpy into mapped GPU scratch)
          + the runtime's own GIF decode (CSR/transfer state)
          ─► flush_render_pass ─► triangle_setup → binning → ubershader (Vulkan)

GPU VU1 (the only shape that keeps paraLLEl's CPU draw front end):
EE ─► MTVU/CPU: VIF1 parse, UNPACK into a per-frame arena (per-MSCAL memory deltas), MPG,
                MSKPATH3/DIRECT/PATH3 bookkeeping, and the order of every GIF packet
     ─► ONE compute submit per frame: every MSCAL's program (exact FMAC, per-vertex parallel)
        writes its PATH1 packets into a GPU buffer (UMA: CPU-visible)
     ─► fence wait (sync point A) ─► CPU stitches PATH1 packets into the recorded PATH2/PATH3 order
     ─► GsWorker: gif_transfer as today ─► paraLLEl renders (same queue, later in the frame)
```

**What would move, and what would stay:**

| Moves to the GPU | Stays on the CPU |
| --- | --- |
| The VU1 program bodies: FMAC, FDIV, FTOI/ITOF, CLIP, the integer loop control, and LQ/SQ into VU memory | VIF1 parsing and UNPACK (0.86 ms/frame on the Odin), MPG, MSCAL ordering, TOPS/ITOPS |
| Writing the GIF packet data that XGKICK sends | The GIF arbiter order (PATH1/2/3 interleave, MSKPATH3 windows: 20–31 per frame) |
| | All of paraLLEl's per-primitive front end (`drawing_kick_append`, texture cache, CLUT, page hazards) |
| | EE-visible state (CSR, vblank) |

**What paraLLEl-GS would need to take GPU primitives directly.** Nothing like it exists
(hand-back §3):
- every primitive is CPU-written, and `num_primitives` is a CPU count that sizes the dispatches;
- per-draw state (PRIM, contexts, TEX0/CLUT, and the hazard tracking that picks flush points) is
  resolved on the CPU for every primitive.

A GPU-native path would mean re-writing paraLLEl's front end on the GPU. It is out of scope for any
first proof. The realistic first shape above hands packets back to the CPU.

### Sync points (from the hand-back's table, plus the ones a GPU VU1 adds)

| Point | Direction | Race frequency | Effect on a GPU VU1 |
| --- | --- | --- | --- |
| VBlankStart waits for the unit (LAG: the previous frame's jobs) | EE waits for the unit | 1/frame | The GPU batch must finish within the lag window. LAG already allows one frame. |
| EE reads of VU1 code/data, CTC2 CMSAR1, VPU_STAT/FBRST fallbacks | EE waits for the unit | 0 in the race | none |
| GS CSR reads (masked, free under R1) | EE waits for the unit and GsWorker | 4/frame, 278,530 of 278,532 masked | none |
| **New A: GPU → CPU fence for the PATH1 packets** | GsWorker waits for the GPU | 1/frame (batched) or 1,040/frame (per MSCAL) | Batched means one frame of GS latency. Per MSCAL is impossible: 1,040 round trips. |
| **New B: PATH1 relative to PATH2/PATH3 order** | CPU stitch | 1,683 PATH1 + 256 PATH2 + 28 PATH3 packets/frame | The order is static under the instant model (each MSCAL completes before the next VIF command), so the CPU can record it. RR1 shows that getting it wrong breaks textures. |
| **New C: VU1 state carried across MSCALs** | GPU program to program | per program | Programs that read VF/VI/Q/flags left by an earlier program serialize. The hot one reloads its state. Not audited for the rest. |
| GsWorker queue full | unit waits for GsWorker | Odin 6.7 ms/frame pre-FS2, 1.7 after | unchanged (the same packets arrive) |
| XGKICK while the program keeps storing | inside a program | per kick | Today PATH1 reads 1 QW per 2 cycles while stores continue (LSU commits land first). The hot programs kick after their last SQI (`a564` 07c0). Programs that store into a buffer after kicking it need a per-program check. |

## 4. Cost model

### Assumptions (each is labelled; the ones that decide the verdict are in bold)

1. **Workload per race frame:** 0.7–1.0 M FMAC instructions (census: 1.0–1.4 M VU1 cycles, FMAC
   upper in ~65 % of hot-loop pairs). The rest of each program (LQ/SQ, integer loop control, DIV,
   FTOI/ITOF, CLIP, XGKICK writes) is set at **R = 1.3–2.0×** the FMAC cost. It is cheap on the
   GPU except DIV, which needs an exact software divide (≈ 33–97 k per frame).
2. **Mac GPU cost** = workload ÷ the measured exact rate. Vertex-parallel uses the saturated
   3.28 G/s.
3. **Odin GPU = Mac × 4–10 at 660 MHz. This is not measured.**
   - The plain rate measured here is 3.4 T fp32 op/s on the M5 Pro.
   - The Adreno 830's fp32 peak at 660 MHz is taken as ~1/3.4 of that (public-spec order of
     magnitude, not verified here).
   - The exact kernel is integer-heavy (int64 emulated with 32-bit multiplies). Adreno integer
     multiply throughput is assumed to be ≤ fp32 throughput, so the upper end is 10×.
   - Stage 0 below replaces this with one Odin run.
4. **GS GPU work on the Odin:** 15.5–15.8 M GPU cycles per guest frame.
   - It is kgsl busy × wall ÷ ticks over the FS2 races (`odin-gpubusy-fs2.txt`):
     - T2 unpatched: 58.4 % busy, 23.9 ms/frame at 660 MHz;
     - P2/P1 patched Turnip: 75.4 / 77.6 % busy, 19.7 ms/frame at a time-weighted 781 / 826 MHz.
   - Busy × clock is consistent across the clock change (23.9 × 660 ≈ 19.7 × 800), so the work
     scales as cycles.
   - Crude: busy % counts any time the GPU holds work (VK1's caveat), and there are no per-guest
     GPU timestamps (CP2).
5. **Odin max GPU clock:** unmeasured. The highest in these logs is 967 MHz. The system
   performance mode stays Standard (AGENTS.md).

### GPU time per guest frame

| Item | M5 Pro (measured rate) | Odin at 660 MHz (×4–10, assumed) | Odin cycles |
| --- | ---: | ---: | ---: |
| VU1 exact, vertex-parallel (0.9–2.0 M FMAC-equivalents) | 0.27–0.61 ms | **1.1–6.1 ms** | 0.7–4.0 M |
| VU1 exact, program-parallel (1,040 threads; mean program) | 2.5–5.6 ms, **plus the longest program ≈ 17.5 k dependent FMAC × 2.9 µs ≈ 50 ms** | 10–56 ms + tail | no-go |
| VU1 lite, vertex-parallel (PCSX2-style flags, needs a re-baseline) | 0.04–0.09 ms | 0.16–0.9 ms | 0.1–0.6 M |
| GS (paraLLEl, measured on the Odin) | — | 23.9 ms | 15.5–15.8 M |
| **GS + VU1 exact** | — | **25–30 ms** | **16.2–19.8 M** |

### Against the frame budget (the orchestrator's framing)

| Budget | GS alone needs | GS + VU1 exact (16.2–19.8 M cycles) needs | At 967 MHz (highest logged) |
| --- | --- | --- | --- |
| **16.7 ms (60 Hz)** | ≥ 930–950 MHz at 100 % busy | ≥ 0.97–1.19 GHz at 100 % busy | 16.8–20.5 ms: **over** |
| **8.3 ms (120 Hz sim, rendering every sim frame)** | ≥ 1.86–1.90 GHz | ≥ 1.95–2.38 GHz | 16.8–20.5 ms: **≈ 2× over** |

Even the lite form (0.1–0.6 M cycles) does not fit, because GS alone is already at the limit.
**On the Odin the GPU, not the CPU, is the resource that runs out first under this plan.** The
first lever for either budget is GS GPU work (the G lane), not moving more onto the GPU.

### CPU saved, latency, dispatch

- **CPU saved.**
  - The MTVU unit's generated VU1 time was 21.6 ms/frame before D1 (VR4 Table 1), and D1 cut the
    unit's running time by ~5.8 ms. So ≈ 16 ms/frame of generated code would leave the unit thread.
  - VIF1 parsing and UNPACK (0.9), `progressXgkick` (0.7) and the new stitch would stay.
  - After FS2 the unit is the busy thread (93–94 %), so it gates the frame. This is the right
    target in principle; the budget table is the problem.
- **Latency.**
  - The design is one batched submit per frame plus a fence before GsWorker ingests that frame's
    PATH1 packets. That adds **one frame of GS latency**.
  - LAG already lets the unit run one frame behind the EE, so display latency becomes about two
    frames.
- **Dispatch.**
  - The Mac floor is 0.026 ms GPU per dispatch, but submit + fence round trips are what cost.
  - On the Odin, Turnip's submit/fence path was the 22 ms/present problem until FS2's patch, and
    CP1 saw 4 transient Turnip compile threads (~96 % CPU each).
  - **Per-MSCAL dispatch (1,040/frame) is ruled out.** Batch the whole frame, with one pipeline
    per program (7 images, ~20–30 hot programs) compiled ahead of time to avoid compile stutter.

## 5. Verdict and staged plan

### Go / no-go criteria (all must hold before any product work)

1. **GPU headroom on the Odin.**
   - GS GPU cycles per frame + the VU1 kernel's measured cycles must fit in ≤ ~85 % of the frame
     at a sustained clock that can be reached in Standard mode.
   - Today GS alone is 15.5 M cycles, against ~14 M available at 16.7 ms and 967 MHz.
   - This needs the G lane to cut GS GPU work first, or a measured higher sustained clock.
2. **Odin kernel cost.** Exact vertex-parallel VU1 ≤ ~3 ms/frame on the Adreno, measured (stage 0).
3. **Loop transformation.**
   - A static transform must turn the hot VU1 loops (software-pipelined, with loop-carried
     registers, clip-flag windows over 3 vertices and FCAND early exits) into per-vertex kernels,
     with PATH1 output **bit-identical** on a captured frame (stage 1).
   - Programs that fail the analysis stay on the CPU.
4. **The CPU alternatives have run out.** VP1 (multi-core VU1), D1b and D2 must fail to bring the
   unit under 16.7 ms. Those alternatives spend CPU cores the Odin has, not GPU time it lacks.

**Verdict: no-go now.** Criterion 1 fails on today's measurements, and criteria 2 and 4 are open.
This agrees with Brad's park (09-26). Keep the option only through the cheap proofs below.

### Staged plan (only if Brad wants the option kept alive)

| Stage | What | Budget | Stop / next |
| --- | --- | --- | --- |
| **0** | Run `gen_cases` + `host test` + `host bench` from this spike on the Odin as adb-shell binaries (Turnip from the play APK's adrenotools copy, or a plain `libvulkan_freedreno.so`), under `odin_lease.sh`, with the play state untouched. Also dump Turnip's float controls (fp64, int64, denormals, RTE). | 1 NDK build of the harness (bytesize, lock), 1 Odin session ~5 min, screen cool-down | If exact vertex-parallel > 3 ms/frame at the play clock, or not bit-exact, then **stop for good**. |
| **1** | **Smallest proof.** Capture one race frame's VIF1 lists plus the VU1 state at each MSCAL of `a564` (reuse the E36/E37 VU1 trace path; det build) and the CPU's PATH1 packets. Hand-port `a564`'s 0398 program as a per-vertex GLSL kernel: exact FMAC, an exact DIV, FTOI/ITOF, CLIP + FCAND over the strip window. Compare the PATH1 bytes bit for bit on the Mac, then on the Odin. | Mac only, ~1 day; 1 det boot on bradflix for the capture | Not bit-identical or not ≤ 0.5 ms on the Odin → stop. Otherwise go to stage 2. |
| **2** | Automatic translation: an analysis pass over the 7 images (loop-carried registers, TOP/ITOP, cross-MSCAL live-ins, XGKICK-then-store) that emits per-vertex SPIR-V for the programs that qualify and a CPU fallback for the rest. Measure GS + VU1 GPU cycles per frame on the Odin with trace replay. | ~1 week | Criterion 1 must hold with measured numbers. |
| **3** | Runtime integration behind a knob. The MTVU unit records the frame's jobs, submits one GPU batch, and stitches PATH1/2/3 in the recorded order; det-hash **IDENTICAL**. | weeks | the usual det, suite and Odin A/B gates |

### Risks

1. **The GPU budget** (above): already at the limit on the Odin.
2. **De-pipelining.** Most of the unit's time is in software-pipelined loops. A mechanical per-program
   translation gives only program-level parallelism: ~1,040 threads, and one 23–27 k-cycle program
   serializes the whole batch.
3. **State carried across MSCALs.** VF, VI, ACC and flags persist between programs. Only the
   hottest program was checked for self-containment.
4. **XGKICK timing.** PATH1 reads 1 QW per 2 cycles while the program keeps storing; any program
   that writes a kicked buffer after XGKICK needs cycle-accurate ordering.
5. **Data-dependent exits and divergence.** FCAND branches leave the loop per vertex. That is cheap
   if culling is rare and costly in warps where it is not.
6. **Exact DIV/SQRT.** GPU division is not correctly rounded.
7. **Turnip behaviour.** Denormal and contraction handling, compile threads, submit cost. Stage 0
   covers these.
8. **Latency:** +1 frame of GS latency.
9. **Two implementations to keep det-identical.** The CPU fallback and the GPU path must match bit
   for bit forever, or the det-hash net splits.

### What other PS2 emulators do (per `docs/research/review-2026-09-26-astra-emulators.md`)

- **PCSX2:**
  - VU1 runs on the CPU in a JIT (microVU), optionally on its own thread (MTVU), under the same
    instant-VU1 model we use (MT1);
  - its flags come from SSE results with clamping modes, not from an exact double model: the "lite"
    column above, not the exact one;
  - its GS work goes to the GPU; its VU work does not.
- **NetherSX2/AetherSX2 and ARMSX2:** CPU VU recompilers (ARM64 emitters).
- **paraLLEl-GS** puts GS rasterization on the GPU as compute. That is the part of the pipeline that
  is data-parallel by nature.
- **None of the emulators surveyed runs VU microcode on the GPU.** This spike found the reasons
  above: an exact FMAC is ~128× a plain one on a GPU, the programs are serial and
  software-pipelined, and on a phone the GPU is already busy with the GS.

## Exact commands

```sh
# census (mini, read-only inputs)
python3 ~/dev/ssx3-work/GV1/census/census.py census.txt listings.txt   # listings stay in scratch (game-derived)
python3 ~/dev/ssx3-work/GV1/census/loops.py > loops.txt
awk '…' ~/dev/ssx3-work/VR2/run/d-det-on/boot.log > runs-vs-tick.txt    # [vu1-recomp] runs/cycles vs det-hash ticks
# CPU reference: fork VU sources at b97b241, standalone (no fork checkout touched)
cd ~/dev/ssx3-work/GV1/ref && git -C ~/dev/PS2Recomp archive b97b241 ps2xRuntime/include ps2xRuntime/src/lib/vu | tar x
clang++ (Homebrew llvm 23) -DPS2X_ENABLE_DET_HASH_TAP=0 -DPS2X_ENABLE_DIAG_TAPS=0 -DPS2X_VU1_FMAC_SIMD=1 -DUSE_SSE2NEON \
  -I<sse2neon> -Ips2xRuntime/include -Ips2xRuntime/src/lib/Kernel -O3 -DNDEBUG -std=gnu++20 -arch arm64 -ffp-contract=off \
  -c ps2xRuntime/src/lib/vu/*.cpp; clang++ … gen_cases.cpp obj/*.o -o gen_cases
# GPU kernels (glslang 16 via Homebrew) and harness (Homebrew vulkan-loader + MoltenVK 1.4.2)
glslangValidator -V --target-env vulkan1.2 -DMODE={0,1,2} bench.comp -o bench{0,1,2}.spv
glslangValidator -V --target-env vulkan1.2 test.comp -o test.spv          # spirv-val: all valid
clang++ -O2 -std=c++17 -I/opt/homebrew/include host.cpp -L/opt/homebrew/lib -lvulkan -o host
# the run (one mini lease slot, released after): ~/dev/ssx3-work/GV1/run_bench.sh  -> bench-mac.txt
./ref/gen_cases 1000000 ref/cases.bin
./bench/host test bench/test.spv ref/cases.bin
./bench/host bench bench/bench{0,1,2}.spv {32768 64 7 | 1024 200 7 | 262144 64 5}; ./bench/host bench bench/bench0.spv 64 1 20
# Odin GPU busy per guest frame (read-only over FS2's logs)
awk … local/research/FS2/logs/{T2,P2,P1}/gpubusy.txt > odin-gpubusy-fs2.txt
```

Kernel source SHAs (`src/SHA256SUMS`):
- `fmac_core.glsl` `1fdc6fa3…`
- `test.comp` `07a6ac7f…`
- `bench.comp` `ed9854f6…`
- `host.cpp` `0a16c130…`
- `gen_cases.cpp` `64fe9803…`

SPIR-V and binary SHAs are in `bench-mac.txt`: `test.spv` `0f41947e…`, `bench0.spv` `958a12b1…`,
`gen_cases` `f0180991…`.

## Gaps

- **Odin numbers are an assumption.** The Mac→Adreno factor (4–10×) is not measured, and neither
  are Turnip's float controls. Stage 0 exists for this.
- **GS GPU time** is kgsl busy × wall. It is crude, from a driver poll whose ticks are ±40, and
  there are no per-guest GPU timestamps.
- **What the exactness test covers:** FMAC ops only, with direct flag commit, `fd ≠ 0` and no
  queued setup ops (the three differences from VR4's generator). Not ported: DIV/SQRT/RSQRT,
  FTOI/ITOF, CLIP, MAX/MINI, EFU, the VU timing model and the XGKICK engine.
- **How often the software path runs** on real game data was not measured (divergence cost).
- **The benchmark kernel** is a synthetic 4-op transform chain, not a translated VU1 program. Its
  op mix is B2a10's matrix × vector only.
- **Workload per frame:** the FMAC count is an estimate from static slot shares × cycles, and R
  (1.3–2.0×) is a judgement.
- **Census attribution:** block samples are spread evenly over the block's pairs, and program
  regions are split at E bits (MSCAL entry pcs are not recorded). Cross-MSCAL live-ins were
  checked only for `a564`'s 0398 program, by hand.
- **Load during the run.** The benchmark held one mini lease slot while a det boot ran in slot 1
  (load ≈ 9). Best-of-N is quoted; means were up to 1.6× higher.
- **Compile during a hold.** I compiled the 4 VU sources and the harness (a few seconds each, one
  core) at 11:30–11:37 while VR4's speed holds H7 and H8 held the mini's slots. It was a small CPU
  load during their speed runs, and it predates my lease discipline for compiles.
- **The local PS2Recomp checkout** is on a stale `ssx3` (`f949ff0`). Sources were read from `b97b241`
  and `fork/ssx3` `1c37c41` by `git archive` and `git show`. No checkout was changed.
- **Budget used:**
  - about 1 h of the 4 h;
  - 0 device time, 0 boots, 0 fork builds;
  - 1 benchmark run (8 s under the lease);
  - scratch `~/dev/ssx3-work/GV1` is 126 MB, most of it `ref/cases.bin` (1 M cases, 128 MB).
    It is safe to delete.
