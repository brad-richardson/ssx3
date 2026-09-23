# M4: Odin3 profile + config audit (2026-09-16/17)

## Result

In-race speed on the Odin3 is **purely CPU-bound in the recompiled game
module, which M2 built at `-O0` with IPO off**. The EGL/Adreno backend costs
**<0.5%** of cycles. Ranked from a clean 90 s / 418,619-sample on-device
`simpleperf` flat profile (0 lost) plus a 3 s dwarf call-graph profile, both
screenshot-verified in-race (timer 00:00:06, 5th/6, 3%, 48 MPH).

## Hotspot ranking (share of ALL cycles, 90 s race window)

| Rank | Scope | % total | Notes |
| --- | --- | --- | --- |
| 1 | Recompiled game `func_*` bodies | 28.3% | Top: 802197A0 2.7%, 8022D7A0 2.1%, 802317A0 1.7% (self only; callees below) |
| 2 | FP-emulation helper CALLS | 25.8% | f32/f64 bit-cast, classify, force_single/25bit, fmuls/fma/fadds, psq, fp_available, ni_* |
| 3 | Guest OS idle spin `loop_80288ED4` | 11.8% | Self; +~3.9% read_be32 children = ~15.6% subtree. Idle skip was OFF |
| 4 | Endian load/store helpers | 12.1% | read_be32 7.35% (does memcpy+bswap per call), write_be32, bswap, be64 |
| 5 | libc (memcpy et al) | 5.3% | Mostly serves read_be32 + the idle/copy loops |
| 6 | Video-thread idle SPIN | ~7.0% | __aarch64_cas1_acq_rel: GPU thread starved, waiting on CPU |
| 7 | Dolphin CPU-side core | 2.4% | Run 0.42%, RunGpuOnCpu 0.43%, Sync ~0.06%; JitArm64 ~0% in-race; DSP ~0.01% |
| 8 | Video-thread REAL work | ~2.1% | VideoCommon + Adreno driver (~0.3%); EFB copy, fifo, vertex loader |
| 9 | FrameDumping (screenshots) | 1.5% | Measurement artifact (SSX3_SCREENSHOTS=1), not gameplay cost |

Thread split: CPU thread 89.15%, Video thread 9.12%, FrameDumping 1.48%,
AsyncShaderComp 0.25%. DSO split: recomp.so 80.93%, run-egl 11.98%, libc
5.54%, kernel 0.72%, Adreno EGL driver 0.50%, libllvm-qgl 0.18%.

Dwarf call chains (worked despite -fomit-frame-pointer):
- `func_802857A0` (16.3% children) → `loop_80288ED4` (97%) → 76% self,
  24% `read_be32` → memcpy 15%, bswap32 10%, memcpy_chk 6%.
- `func_802197A0` (9.6% children) → `ppc_fadds` → `ni_add` + `force_single`
  → `f64_bits`, `fp_write_single` → `classify_f32` (+memcpy), `set_fprf`,
  `fp_invalid_gated`. One guest fadds = ~5 nested -O0 helper calls.

Disassembly (NDK llvm-objdump on pulled device .so): `read_be32` = -O0
frame + stack protector + `__memcpy_chk` call + `bswap32` call (~30+ insns
for a 4-byte load); `ppc_fadds` = 4+ nested calls. An `-O0` artifact
throughout: nothing inlines, everything spills.

## Config sins table

| # | Sin | Before (M3/M4) | Lever | Expected |
| --- | --- | --- | --- | --- |
| 1 | Module built `-O0`, IPO off | RECOMPCORE_MODULE_OPT_LEVEL=0, ENABLE_IPO=OFF (M2 bring-up flags) | OPT_LEVEL=2/3 + IPO=ON, keep -ffp-contract=off -fno-fast-math (iOS runs O2+ThinLTO in prod) | ~2.5-3.5x CPU thread (the 81%) |
| 2 | Idle skip off | StaticRecompIdlePC unset (0) | `[Core] StaticRecompIdlePC = 0x80288ED4` in user Config/Dolphin.ini (pure config) | ~1.13x (11.75% of CPU thread); m4b validates |
| 3 | 3x internal resolution | user config.ini resolution=1920x1080 → EFB scale 3 (screenshots 1920x1474 prove it) | resolution=640x528 (scale 1) | ~1.02x (GPU is <1%; tiny — but free) |
| 4 | Movie-forced GPU determinism | SSX3_MOVIE_PLAY/RECORD → IsMovieActive → deterministic GPU thread (extra FIFO aux copies + sync) | Real gameplay has no movie (auto-off); or GPUDeterminismMode=Disabled | small (~1.0-1.05x); profiled speed understates real play |
| 5 | Clocks below max under load | prime 3.07/4.32 GHz, little 1.79/3.53 (walt, thermal status 0) | Pin CPU+GPU threads to prime cores; walt boost experiment | up to ~1.2-1.4x IF raisable; unmeasured |
| 6 | RECOMPCORE_FAST_FP off | default OFF (M2 left a fastfp-probe.o on SSD) | FAST_FP=ON: inline JIT-fidelity FP in chunks, skip FPRF/FI/FR bookkeeping | ~1.1-1.25x on the 25.8% FP share; needs differential validation |
| - | NOT sins (verified clean) | CPU thread ON (dual-core active: Video thread + FIFO panic prove it); fallback=interpreter, DSP JIT on, HLE return-hooks on; vsync off; emu speed cap 1.0 (not binding at 0.125); audio NullSound + DSP HLE on own thread; build Release -O3 for the core; ELF 16K-aligned, device 4K pages; SyncGPU off; MSAA 1x; vertex loader Native (HW); EFB-to-texture fast paths on | — | — |

Prior-art warnings: idle skip "previously regressed or failed progress"
(normal-frame-cpu-spike.md) — m4b re-validates; host_call-style HLE regressed
to 0.30 before, return_hooks are the safe shape (research.md); FP helper
inlining helps only where calls are actually outlined (float-conversion-spike:
already-inlined sites can hurt) — at -O0 everything is outlined so O3+LTO is
strictly the first step.

## GPU-vs-CPU verdict

Purely CPU. Adreno driver 0.5% + qgl 0.18%; whole video thread 9.1% of which
~7% is idle spin and ~2% real work. The EGL backend is not a factor in the 8x
gap at all. Sizing math from a saturated CPU thread: 0.125 × 3.0 (O3+IPO) ×
1.18 (idle, MEASURED) × 1.15 (fastfp) × 1.1-1.2 (clocks?) ≈ 0.56-0.61; 80%
needs 6.4x, so the top 3 close roughly two-thirds of the gap and the rest
needs recompiler codegen work (inline load fast path, FP op fusion) guided
by this profile.

## Top 3 fixes toward 80% (sized, not implemented)

1. **Module -O0 → -O2/-O3 + IPO=ON** (build flags only; strict FP kept).
   Attacks the 81% (helper-call tax ~40% + -O0 bodies). ~2.5-3.5x → 0.3-0.45
   absolute. Lowest risk (iOS precedent), one rebuild + validation run.
2. **Idle skip on** (`StaticRecompIdlePC = 0x80288ED4`, pure config).
   MEASURED by m4b: race 0.125 → 0.147 (1.18x), menus 2.5x, boot 1.6x;
   gameplay intact (screenshot-verified race). Prior-art regression warning
   does not reproduce on this path.
3. **RECOMPCORE_FAST_FP=ON** (inline FP, skip FPRF bookkeeping on
   non-exceptional results). Attacks the 25.8% FP share → ~1.1-1.25x.
   Needs the differential FP validation M2 started (fastfp-probe.o).

## Runs this session

- m4 (PID 10957): DTM replay, 700 s bound, user-m4 fresh. Flat profile
  samples ~475-565 (90 s, 418,619 samples, 0 lost), dwarf ~565-568 (3 s,
  2,571 samples, ended early — see panic note). Died at sample ~590 to the
  FIFO overflow panic (same as m3r), no shutdown counters.
- m4b (PID 14773): same + StaticRecompIdlePC=0x80288ED4 in user-m4b
  (A/B for sin #2). MEASURED: boot/logos 0.599 (1.6x vs m4), menus 0.670
  (2.5x), race 0.147 mean / 0.120 min (1.18x vs m4's 0.125). Race verified
  by screenshot (timer 0:06, 6th/6, 2%, 42 MPH — same race as m4 with tiny
  trajectory divergence: m4 showed 5th/3%/48MPH at 0:06). No gameplay
  regression from idle skip on this path. Died to the same FIFO panic at
  sample 360 (= same EMULATED point as m4's 590: idle skip compresses wall
  time; the panic is deterministic on emulated state).
- m4c (PID 17026): m4b repeat + 60 s in-race flat profile (samples
  ~255-315, 288,716 samples, 0 lost). Race mean 0.147/min 0.120/max 0.205 —
  IDENTICAL to m4b (DTM playback is bit-deterministic). Profile confirms
  loop_80288ED4 13.18% → 0.25% of CPU thread; no new hotspot (FP helpers now
  35.75% of CPU thread = 31% of total, func 38.2%, mem 12.1%). Thread split
  86.6/11.2/1.7. Same panic death at sample 360.

## Incidental findings (for parent)

- **FIFO overflow panic is fatal in headless playback**: m3r AND m4 both died
  at sample ~585-590 (`GatherPipeBursted` CommandProcessor.cpp:394, "CPU
  thread is too fast"). M3 (record) did not panic. Profile before ~sample 580
  in future playback runs. Real (non-movie) gameplay may differ.
- **SSD module .so is 100% zeros** (487 MB sparse): md5 d887d73a… vs device
  ab1df3d0… (valid ELF, 222 MB text). The .a is intact. Refresh the SSD copy
  from /tmp/m4/gGXBE69_recomp.so (pulled 2026-09-16) before any SSD-side
  module work. Core-egl binary matches device (bbd4bdf7…).
- CPU thread is misnamed "GC Adapter Scan" (TID 10999); Video thread TID
  11005. Harmless quirk (stub GCAdapter naming the calling thread?).
- Screenshots prove 3x EFB (1920x1474) and show the known OGL near-ground
  snow fidelity issue (black snow) — unchanged from M3.

## Files

- SSD: /Volumes/Extreme SSD/android-spike/m4/ (this note; was empty dir).
  No other SSD writes. No repo writes. third_party untouched (reads only).
- /tmp/m4/: m4-flat.perf (23 MB), m4-dwarf.perf, m4-rep-*.txt (full reports),
  m4.err/out, m4b.err, m4c-flat.perf (16 MB), m4c-rep-cpu.txt, m4c.err,
  gGXBE69_recomp.so (465 MB device pull), race screenshots (m4-race-*.png,
  m4b-race.png).
- Device /data/local/tmp/mg/: m4.* (run logs), m4-flat.perf, m4-dwarf.perf,
  m4-rep-*.txt, m4-test.perf, m4b.*, m4c.*, m4c-flat.perf, m4c-rep-cpu.txt,
  user-m4/, user-m4b/, user-m4c/.
