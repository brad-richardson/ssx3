# Independent frontier review 2 (2026-09-23, Fable, read-only)

The report is kept as delivered, with minor formatting. The orchestrator
verified two headline items (see the note at the end). Fork
`~/dev/PS2Recomp` `ssx3` @ `eac6cba`; canonical codegen
`~/dev/ssx3-work/codegen-ssx3`.

## 0. Ten things that change the plan (ranked)

1. **The saturated TEX1 K in E51 is an HLE ABI bug, not VCALLMSR.**
   - The `log@0x0040D610` stub reads `f12` and writes `f0`
     (`src/lib/Kernel/Stubs/LibC.cpp:1173-1177`). But SSX 3's `log` is the
     double-precision softfloat routine: a0 = 64-bit argument, v0 = result.
   - The caller at `0x37ca40–0x37cab4` computes `240 / (h·2^-14)`, converts
     float→double (`jal func_413AF8` @0x37ca5c), calls `func_40D610`
     @0x37ca64, runs a double multiply chain, converts to int, and then
     `slti v0,v1,-0x7FF` clamps at −0x7FF (= 0x801 in the 12-bit field).
   - The stub never writes v0, so "log(x)" returns the double bits of x.
     The product overflows, and every K lands on the clamp.
   - Fix: unbind `log`, or implement the double ABI.
2. **The VU1 EFU opcode table is shifted by one slot**
   (`src/lib/vu/ps2_vu1_lower.cpp:427,726-770`). The correct table
   (PCSX2 `LowerOP_T3_*`) is 0x78 ESQRT, 0x79 ERSQRT, 0x7A ERCPR, 0x7C ESIN,
   0x7D EATAN, 0x7E EEXP. Word `0x8000afbd` in SSX 3's hot vertex loop is
   ERSQRT, but it's executed as ESIN.
3. **The sweep CSV merged ~4,000 functions.**
   - There are 4,045 interior `addiu $sp,$sp,-N` prologues inside 1,615
     functions.
   - 0 are `jal` targets, 858 are data-referenced (E46 rescan), and 3,187
     are reached neither way.
   - Only 19 are in `extra_function_starts`.
4. **The missing-target policy can't fail, and hides every miss after the
   first.**
   - `ContinueToTarget` returns true with stale `$v0`
     (`ps2_runtime.cpp:2114-2118`), and there's no env override.
   - It reports once per run unless `PS2X_DIAG_REPORT_ALL` is set
     (`:1724-1725`), and there's no counter.
5. **COP0 Count never advances** (`cop0_translator.cpp:47,97`). 4 MFC0
   Count sites (0x3f4414, 0x3f4e08, 0x3f4fa4, 0x3f4fc4); race reach
   unverified.
6. **PINTEH interleaves the wrong halves** (`ps2_runtime_macros.h:786-787`).
   4 sites at 0x3cb8b0–0x3cb8bc, in 16.16 fixed-point code feeding VU0.
7. **Run-to-run divergence has a named cause:** the game seeds its RNG from
   `sceCdReadClock`, which is HLE'd to host `std::time`
   (`Stubs/CD.cpp:706-712`; guest 0x31ae80 → `func_3177C8`). A second
   source is the idle fast-forward, which picks its target by host deadline
   (`EeScheduler.cpp:2836-2844`).
8. **GS CSR isn't write-1-to-clear, and VSINT is never set**
   (`ps2_memory.cpp:205-217`). The vsync waits at 0x37c0dc/0x39608c return
   at once, and every CSR write clobbers FIELD (read at 0x396058).
9. **A GS→EE readback is fed into the VIF parser** (guest
   0x2ec738–0x2ec7a4; the kick at `ps2_memory.cpp:1450-1455` never tests
   CHCR DIR). Reach unverified.
10. **E53's EE-thread FPCR RTZ+FZ affects host code on that thread:**
    - the HLE libm stubs;
    - the CPU GS backend, which runs on the game thread;
    - MPEG decode.

    Scope the mode to generated code, or A/B the GS output.

## A. Remaining classes of silent semantic defects

### A1. Function-boundary discovery (highest, structural)

- **The sweep CSV:** 9,283 functions, with boundaries from `jal` targets
  and `jr ra` ends. Functions reached only through pointers get merged
  into their predecessor.
- **Resume entries work:** the `switch(ctx->pc)` prologue plus the dense
  table, so a label is all that's needed.
- **The jump-table emitter is unused**, and out-of-range `jr` is reported,
  not silent.
- **One direct `J 0x400908`** at 0x400bf8 has no table entry.
- **Detection:**
  1. A recompiler rule: every interior `addiu $sp,$sp,-N` (and
     data-referenced leaf interiors) becomes a resume entry automatically.
  2. `PS2X_MISSING_FUNCTION_POLICY=stop|continue`, dev default `stop`,
     with a per-target counter at exit.
  3. Gate: a full scripted route with `stop` and zero misses.

### A2. Integer / MMI / control translation

| Defect | Evidence | SSX 3 sites | Sev |
|---|---|---|---|
| PINTEH/PINTH wrong lanes | `ps2_runtime_macros.h:786-787` (verified) | 4 / 0 | A |
| COP0 Count frozen | `cop0_translator.cpp:47,97` (verified) | 4 | A when reached |
| BLTZ/BGEZ/BLEZ/BGTZ (+L/AL) compare only the low 32 bits | `control_flow_emitter.cpp:407-425` (verified) | 4,224; 15 with a 64-bit producer nearby (`dsll32` at 0x41138c/0x42d3c4) | B |
| LWU sign-extends | `instruction_translator.cpp:196-197` (verified) | 92 | B |
| LQ/SQ/LQC2/SQC2 don't mask the low 4 address bits | `instruction_translator.cpp:204-207,219-222` (subagent) | 73k; 0 misaligned immediates | B |
| BLTZALL/BGEZALL link only when taken | `control_flow_emitter.cpp:475-478,492-495` (subagent) | ? | B |
| MOVZ/MOVN copy 128 bits | `special_translator.cpp:123-126` (subagent) | 1,558 | C |
| Latent MMI (0 sites): PMFHI/LO, PMULTW/PMADDW/PDIVW, PEXEH/PEXCH…, PABSW/H, PADDUH/PSUBUH, PSLLVW… | `mmi_translation_helpers.cpp` (subagent, unrechecked) | 0 | A if ever used |

The subagent verified the base ISA, shifts, MULT/DIV edge cases, pipeline
1, the PADD/PSUB/PCGT/PCEQ/PEXT/PPAC/PCPY families, QFSRV, delay slots,
likely branches, links and SYSCALL/ERET as correct.

### A3. VU1 interpreter (not covered by E52)

| Defect | Evidence | Sev |
|---|---|---|
| EFU decode shift | `ps2_vu1_lower.cpp:427,726-770` vs PCSX2 `VUops.cpp:3628-3636` (verified by the orchestrator too) | **A, in the hot loop** |
| Budget exit loses state (no `flushPipelines`; `resetScheduler` zeroes XGKICK/writebacks) | `ps2_vu1_core.cpp:~80,1614,1972` (subagent) | A when it fires |
| MSCNT after a cut resumes at the cut PC | `:1649` (subagent) | B |
| VPU_STAT VBS1/XGKICK busy never set | `ps2_runtime.cpp:784-787` (subagent) | B |
| EATAN coefficient typo | `ps2_vu1_lower.cpp:19` (subagent) | C |
| RSQRT(0,0), branch in a delay slot, MAX/MINI clamps | (subagent) | B/C |

Detection: a VU1 differential test of the 7 SSX 3 microprograms on captured
data images against PCSX2 (T65 dumps).

### A4. HLE stubs: wrong ABI, state never set, fabricated replies

| # | Defect | Evidence | Sev |
|---|---|---|---|
| H1 | The `log` stub has the float ABI for a double routine | `LibC.cpp:1173-1177`; guest 0x37ca40–0x37cab4 (verified by the orchestrator too) | **A, live (K = 0x801)** |
| H2 | Host libm replaces guest libm (tanf/expf/fmodf/logf/log/__kernel_rem_pio2f/__kernel_tanf/floorf) | `ssx3.toml`; `LibC.cpp:1150-1194` | B |
| H3 | SIF cmd handlers are registered but never raised | `Stubs/SIF.cpp:66,477-484,793` | A (sound) |
| H4 | Every SSX 3 SIF RPC is unhandled (echo / zero) | `RPC.cpp:340-356,675-685` | A |
| H5 | Alarm syscall numbering (0xFE is set, not cancel; +0xFD/−0xFE fall to the default) | `Dispatcher.cpp:165-177,412-419` | A when reached |
| H6 | Unknown syscalls return 0 | `System.cpp:369-436` | B |
| H7 | `sceSifSendCmd` drops its packets | `RPC.cpp:1086-1177` | A (audio) |
| H8 | A failed CD read zero-fills, returns 0, no callback | `Stubs/CD.cpp:455-456` | B (a Snow Jam 99% candidate, unverified) |
| H9 | The host heap may overlap the guest's EndOfHeap range | `System.cpp:603-657` (unverified) | B |
| H10 | INTC 5 (VIF1) / 7 (VU1) never dispatched; DI not honoured | `EeScheduler.cpp:1953-2007,2501,2675,2681` (verified) | B |

Detection:
- a static ABI check on the stub list;
- a per-(sid,fn) unhandled-RPC counter that fails the run in dev builds;
- a "registered but never raised" audit;
- abort on unknown syscalls in dev builds.

### A5. DMA / VIF / GIF edge modes (subagent unless noted)

| # | Defect | Sev |
|---|---|---|
| M1 | VIF1 DIR=0 readback parsed as VIFcodes (verified) | A when reached |
| M2 | A CHCR read clears STR and writes it back | B |
| M3 | SPR select bit dropped in tags; MADR bit 31 taken as KSEG0 | A when hit |
| M4 | VIFcodes split across FIFO writes are lost | A when hit |
| M5 | V4-5 UNPACK raw; V2 UNPACK leaves z/w stale | A/B |
| M6 | The I-bit doesn't stall or raise INTC 5; VIF1 register reads return CPU writes | B |
| M7 | A split GIF packet is re-parsed as a GIFtag; DIRECT via FIFO sends nothing; GIF DMA completes while PATH3 is masked | A/B |
| M8 | Chain-walk truncations silently reported as complete | C |
| M9 | Transfers complete at the CHCR store | B |
| M10 | MFIFO/stall/REFS not modelled | C |

### A6. GS priv regs, INTC, timers

- P1: CSR W1C/VSINT/FIELD (verified), sev A.
- P2: INTC_STAT/MASK are plain storage, sev A if reached.
- P3: vsync at 60.00 Hz, not 59.94 (every "÷59.94" is biased +0.1%), sev C.
- P4: timer GATE/HOLD unused, sev C.

### A7. Numeric model

E52 covers it. Also item 10 above.

### A8. Diagnostic blind spots

- The missing-target report fires only once per run.
- Taps use per-tap address folds (UCAB); use one `guestPhys()` helper.
- Trace name tables carry the wrong EFU mapping (`ps2_vu1_core.cpp:2023-2029`).
- Moment-matching by the HUD timer is invalid until determinism lands.

## B. Nondeterminism

Guest time is `m_eeCycle`: 32 cycles per back-edge and 8 per dispatch, 0
for HLE/DMA/VU1, plus the idle fast-forward. Events fire when both the
cycle and host deadlines are due. There's a single EE executor thread and
memory is zeroed.

Sources, ranked:
1. **RTC → RNG seed** (verified).
2. **The idle fast-forward picks its target by host deadline**
   (`EeScheduler.cpp:2836-2844`).
3. Same-cycle events are ordered by host deadline, and alarms use `now()`.
4. Live raylib pad state is merged under the script.
5. The `mc0` folder is shared across boots.

Proposal, `PS2X_DETERMINISTIC=1`:
- a fixed RTC, plus timestamps derived from `eeCycle`;
- cycle-only event selection, with host time used for pacing only;
- a neutral pad state under the script, and a per-run `mc0`;
- a **hash tap** `PS2X_DET_HASH_EVERY=N` at VBlankStart
  (vsync, eeCycle, xxh64 of RAM/SPR/VU1 mem, program count). It's the A/B
  and bisect tool, and it gives Mac/Odin equivalence;
- COP0 Count derived from `m_eeCycle`.

## C. Plan to the milestone

1. **E53** (running), with FPCR scoping or a GS A/B.
2. **E54, semantics batch 2:**
   - the `log` fix (H1), EFU table + trace names, PINTEH/PINTH, LWU, 64-bit
     sign branches;
   - COP0 Count from eeCycle, CSR W1C/VSINT/FIELD, INTC 5/7.

   Gate: E51's counters move toward T65 (per-object K, IMAGE uploads ≫ 1,
   startPCs > 5, on-screen prims → 16.7k).
3. **E55:** determinism mode + the hash tap. Gate: two idle boots and one
   loaded boot are hash-identical through the race.
4. **E56, function-boundary closure:**
   - automatic interior-prologue entries;
   - the missing-function policy (`stop` in dev) plus a counter;
   - unknown-syscall abort and an unhandled-RPC counter.

   Gate: a full route with zero misses.
5. **N5 → N7:** the Odin with E53–E56 + E45. Gate: the hash at vsync N
   equals the Mac's; diagnostics-off speed numbers.
6. **E57, VU1 speed**, after E54/E55, validated by the hash.
7. **GB3 → Turnip on the Odin**, on the E55 hash timeline.
8. **Sound** (H3/H4/H7/H5/H8) after 5.
9. **120 Hz sim** after 5–7, using X3's map, measured with the hash tap and
   the vsync counter.

Stop doing:
- adding `extra_function_starts` from boot censuses;
- HUD-timer moment matching, and "same tick" A/B before E55;
- treating VCALLMSR as the K lead;
- bespoke trace headers with their own folds;
- quoting vsync rates without the 60.00-vs-59.94 caveat.

## Verification status

The reviewer verified items 1–10, the A1 census, the ContinueToTarget
semantics, the libm stub list, the CSR merge, the VIF1 DIR path, the EFU
table, the RTC seed chain, the fast-forward code, and that the jump-table
emitter is unused. Subagent-only: the MMI group, VU1 V3–V10, H3–H10,
M2–M10, P2–P4. Unverified reach: PINTEH, the Count users (the readings of
0x3f4f40 conflict), the VIF1 readback, the heap overlap, the fast-forward
impact, and whether E46/E49's zero-miss gates ran with
`PS2X_DIAG_REPORT_ALL`.

**Orchestrator check (09-23):**
- `log@0x40D610`: the guest passes a double in a0 (`daddu a0,v0` after
  0x413AF8) and reads v0. The stub uses f12/f0. Confirmed.
- EFU: PCSX2 T3_01[30] = ERSQRT → funct2 0x79, T3_00[31] = ESIN → 0x7C,
  T3_01[31] = EATAN → 0x7D. Ours has 0x79 = ESIN, 0x7C = EATAN,
  0x7D = EEXP. Confirmed.
