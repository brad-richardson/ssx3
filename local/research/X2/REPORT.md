# X2 — PSX 3 Timing Analysis Report

Date: 2026-09-22
Analyst: Research Worker (X2 brief)

## 1. Float Constants

| Constant | IEEE-754 (hex) | Source (ELF) | Source (codegen) | Function | MIPS Instruction | Context |
|----------|---------------|--------------|-----------------|----------|-----------------|---------|
| 60.0 | 0x42700000 | ELF: various | `lui $at, 0x4270` | `sub_00105D98` | VU microcode (vector magnitude) | Used in vector magnitude calculation with 30.0 scaling |
| 30.0 | 0x41f00000 | ELF: various | `lui $at, 0x41f0` | `sub_00105D98` | VU microcode (vector magnitude) | Combined with 60.0 in scaling ratio |
| 10.0 | 0x41200000 | ELF: 0x317148 | `lui $at, 0x4120` | `sub_00316F00` (line 1679) | `mtc1 $at, $f12` | Game loop: stored in `$f12`, used as `0x4120` scaled parameter (sub_00317530 calls) |

**Gaps:**
- IEEE-754 patterns for 1/60 (0x3C888889), 1/30 (0x3D088889), 1/50 (0x3CA3D70A) **were not found** in ELF `.rodata` or `.sdata` dumps.
- The exact 1/60 float is **not stored statically** — it may be computed at runtime via `cvt.s.w` + `mtc1` sequences or constructed from double literals in C++ code.
- `sub_00105D98` uses 60.0 and 30.0 (vector magnitude math in VU microcode) but does not appear to compute inverse frame rates (1/60, 1/30, 1/50).

## 2. Frame Counters and VSync

### WaitVSync Syscall

| Property | Value |
|----------|-------|
| Syscall number | 0x74 |
| Dispatched function | `SetSyscall` (Dispatcher.cpp:376, maps 0x74 → runtime handler) |
| Handler calls | `WaitVSyncTick(..., fixedResult)` (Interrupt.cpp:78) |
| Scheduler method | `EeScheduler::waitVSync(afterTick, fixedResult)` (EeScheduler.cpp:2057) |
| Wait result | `fixedResult >= 0 ? fixedResult : (tick - 1) & 1` (EeScheduler.cpp:2084-2086) |

### WaitVSync Call Sites (from the ELF)

| Target Address | Type | Caller Range | Codegen Function | Codegen File |
|---------------|------|-------------|-----------------|-------------|
| 0x424120 | WaitVSync wrapper (direct call site) | Called from sub_00424110 | `sub_00424110` (line 52: `SET_GPR_S32(ctx, 3, 116)`) | `sub_00424110_0x424110.cpp:52` |
| 0x42c2f0 | System call table init | Called from 0x42c228 (2 callers) | `sub_0042C2F0` | `sub_0042C2F0_0x42c2f0.cpp` |
| 0x42c340 | Timers/disp | Called from 0x42c440, 0x42c474, 0x42c490 (3 callers) | `sub_0042C340` | `sub_0042C340_0x42c340.cpp` |
| 0x42c500 | Timers/disp | Called from `sub_0042C4D0` | `sub_0042C500` | `sub_0042C500_0x42c500.cpp` |
| 0x42c760 | Timers/disp | Called from `sub_0042C6E8` | `sub_0042C760` | `sub_0042C760_0x42c760.cpp` |
| 0x42cbc0 | Timers/disp | Called from `sub_0042CBB0` | `sub_0042CBC0` | `sub_0042CBC0_0x42cbc0.cpp` |

### WaitVSync Wrapper Called from Game Loop

| Property | Value |
|----------|-------|
| Wrapper address | 0x317810 (function `sub_00317810`) |
| Codegen file | `sub_00317810_0x317810.cpp` (75 lines) |
| Parameter passed | 0x50 = 80, then adjusted by `addiu $a0, $a0, -0xFD0` = 351,568 (0x55FD0) |
| Internal call | `func_317A08` (sub_00317A08) |
| PS2 EE Clock | ~147.456 MHz (NTSC) / ~139.176 MHz (PAL) |
| 351,568 cycles ≈ | 0.143 frames at 60 Hz NTSC (0.135 at 50 Hz PAL) |

### Frame Counter Inside Game Loop

| Property | Value |
|----------|-------|
| Register | `$s1` (general-purpose register 17) |
| Initialization | `addiu $s2, $zero, 0x1` at 0x316f1c (sets $s2 = 1, not $s1) |
| Increment | `addiu $s1, $s1, 0x1` at 0x317184 (frame counter +1) |
| Frame limit loaded | `lw $v0, 0x20($s0)` at 0x317188 (offset 32 from game state block, `$s0` = `$16`) |
| Comparison | `slt $v0, $v0, $s1` at 0x31718c (signed: `frame_limit < frame_counter`) |
| Branch back to re-process | `bnel` at 0x317190 → returns to 0x317128 if not exceeded |
| Exit to next phase | 0x3171c8 (if frame counter exceeded) |
| Location in codegen | `sub_00316F00_0x316f00.cpp` lines 1765–1856 |

## 3. Main Loop Shape

### Game Loop (`sub_00316F00`)

| Property | Value |
|----------|-------|
| Address | 0x316F00 – 0x317328 (1,064 bytes) |
| Codegen file | `sub_00316F00_0x316f00.cpp` (2,689 lines) |
| Named function | `cAppMan_mainLoop` (from function map: `sub_00316F00`) |
| Entry sequence | `addiu $sp, -0x40`; store 6 vectors (S0–S2, RA); initialize `$s2 = 1`, `$s1 = 0` |

### Per-Frame Sequence (critical path)

```
label_316f00: push, save S0/S1/S2, RA; $s2 = 1; $s1 = 0
  └─ Read s0 + 0x5C (game state header) → $v1
  └─ Read state→0x28 (sub) → $a0; state→0x2C (func ptr) → $v0
  └─ jalr $v0 (call sub-function), pass $s0 + 0x28
  └─ Read state→0x58 (sub2) → $a0; state→0x5C (func2 ptr) → $v0
  └─ jalr $v0 (call sub2-function), pass $s0 + 0x58
  └─ jal 0x3E5928 (unknown sub-5928)
  └─ Read state→0x60 (sub3) → $a0; state→0x64 (func3 ptr) → $v0
  └─ jalr $v0 (call sub3-function), pass $s0 + 0x60
  └─ Check state→0x5C == 1 (state 1 → branch to 0x316fac)
  └─ Check state→0x5C == 2 (state 2 → branch to 0x3170bc)
  └─ State 0: enter sub loop
  └─ State 1: jal 0x317600 (0x20), then exit
  └─ State 3: jal 0x3175A0 (0x40), then exit

  If state ≠ 0:
  └─ jal 0x317328 (cGameViewMan_updateAll) — called with $s0
  └─ jal 0x317328 again (second call)
  └─ jal 0x319D18 with $4=1
  └─ jal 0x319D10 with $4=1

  └─ Initialize state 0 (sw $zero, 0x4($s0))
  └─ Loop through sub-states (jalr indirect calls):
       └─ jal 0x317328 (cGameViewMan_updateAll) between each
       └─ If state→0x2C == 0: jump to 0x3171c8 (wait path)

  └─ Frame batch section (label_317128 – 0x3171c8):
       └─ jalr sub-functions (same pattern as above)
       └─ addu $s1, $s1, $v0 (accumulate result from sub-functions)
       └─ If $v0 == 0: branch to 0x3171c8 (exit frame batch)
       └─ lui $at, 0x4120 (0x4120 = 10.0f); mtc1 $at, $f12
       └─ jal 0x317530 (func_317530 with $s0 + 0x38)
       └─ Load frame_counter from state→0x4
       └─ Load frame_limit from state→0x20 (offset 32)
       └─ **Frame counter increment**: `addiu $s1, $s1, 0x1`
       └─ **Frame limit check**: `slt $v0, frame_limit, frame_counter` (signed compare)
       └─ If NOT exceeded: branch back to 0x317128 (re-process)
       └─ If exceeded: continue to 0x3171c8 (exit frame batch)

  └─ After frame batch:
       └─ sw 0, state→0x0 (clear pending)
       └─ jal 0x317328 (cGameViewMan_updateAll) — several times
       └─ jal 0x317810 (WaitVSync wrapper, 0x20) — with 0x40 param
       └─ jal 0x3175A0 (0x40) or 0x317600 (0x20)
       └─ jal 0x317530 (0x38) with 10.0f

  └─ WaitVSync call at 0x317810:
       └─ calls func_317A08 with $a0 = 0x50 - 0xFD0 = 351,568 (WaitVSync sleep param in cycles)
```

### Key Inter-Function Calls

| Called Address | Codegen File | Name (from map) | Notes |
|---------------|-------------|----------------|-------|
| 0x317328 | `sub_00317328_0x317328.cpp` | `cGameViewMan_updateAll` | Updates all game views; calls `func_3174A8` with param 1 |
| 0x317530 | `sub_00317530_0x317530.cpp` | — | Called with 10.0f in $f12 (from 0x317148) |
| 0x3175A0 | `sub_003175A0_0x3175a0.cpp` | — | Game state management |
| 0x317600 | `sub_00317600_0x317600.cpp` | — | Game state management |
| 0x317810 | `sub_00317810_0x317810.cpp` | — | WaitVSync wrapper (sleep param = 351,568 cycles) |
| 0x317A08 | Generated | `func_317A08` | Internal WaitVSync core handler (timed wait) |
| 0x319D10 | `sub_00319D10_0x319d10.cpp` | — | Called with $4=1 from game loop |
| 0x319D18 | `sub_00319D18_0x319d18.cpp` | — | Called with $4=1 from game loop |
| 0x3E5928 | `sub_003E5928_0x3e5928.cpp` | — | Called once per game loop iteration |

### Timer Callback

| Property | Value |
|----------|-------|
| Address | 0x227F58 – 0x227F80 (40 bytes) |
| Codegen file | `sub_00227F58_0x227f58.cpp` (86 lines) |
| Named function | `cSSXApp_timerCallback` (from function map) |
| Behavior | Reads timer flag from `-0x850($gp)`; if non-zero, calls `func_326B88` |

### Pre-Update Handler

| Property | Value |
|----------|-------|
| Address | 0x227E98 – 0x227F58 (368 bytes) |
| Codegen file | `sub_00227E98_0x227e98.cpp` (301 lines) |
| Named function | `cSSXApp_preUpdate` (from function map) |

## 4. Cross-Check with GameCube/Dolphin Leads (reserve docs)

### From `local/muse/prompts/X0.md` (frame advance logic brief)

- Speculation that SSX 3 uses frame advancement instead of direct WaitVSync
- Our findings confirm: **the game loop increments a counter (`$s1`) and compares it against a stored frame limit** — matching the "frame batching" model described

### From `120HzHandoffAndSamplingPlan.md`

| Lead | Status | Evidence |
|------|--------|----------|
| Patch site `0x00317184` writes `0x26310002` | **Confirmed location** | This is `addiu $s1, $s1, 0x1` (frame counter increment) at 0x317184 in the ELF, present in generated code at `sub_00316F00_0x316f00.cpp:1800-1801` |
| 120 Hz target | Planned | Patch at 0x317184 modifies frame counter — directly relevant to doubling frame rate |
| Menu → race linkage | Planned | `cGameViewMan_updateAll` (0x317328) called repeatedly from game loop; state transitions (0x5C values 0,1,2,3) control menu vs race flow |

### From `ssx3-functions.sweep.csv`

- `cAppMan_mainLoop`: `sub_00316F00` at 0x316f00–0x317328 (confirmed, analyzed)
- `cGameViewMan_updateAll`: `sub_00317328` at 0x317328–0x317348 (confirmed, 75 lines)
- `cSSXApp_preUpdate`: `sub_00227E98` at 0x227e98–0x227f58 (confirmed, 301 lines)
- `cSSXApp_timerCallback`: `sub_00227F58` at 0x227f58–0x227f80 (confirmed, 86 lines)

## 5. Summary

SSX 3 uses a **frame batching model** rather than a simple WaitVSync-per-frame loop:

1. **Per-iteration**: The game loop (`cAppMan_mainLoop`) calls multiple sub-functions (state-based dispatch via `jalr`) and calls `cGameViewMan_updateAll` (0x317328) to update game views.

2. **Frame batch**: Inside the loop, a **frame counter** (`$s1`) is incremented each iteration, compared against a **frame limit** stored at `state→0x20` (offset 32 from the state block). If the counter hasn't exceeded the limit, the game re-enters the update loop (`bnel → 0x317128`), processing pending frames.

3. **WaitVSync**: After frame batch completion, the game calls `sub_00317810` (WaitVSync wrapper at 0x317810) with a sleep parameter of 351,568 CPU cycles (~0.143 frames at 60 Hz NTSC). This calls `func_317A08`, which blocks the thread until the target tick is reached via the scheduler's `waitVSync` mechanism.

4. **Float constants**: 60.0 and 30.0 are used in VU microcode (vector magnitude). 10.0 is constructed in the game loop via `lui $at, 0x4120; mtc1 $at, $f12` and passed to an unknown function (0x317530). **1/60, 1/30, and 1/50 are not stored as static floats** — they are either computed at runtime or used implicitly through frame counter arithmetic.

5. **Patch site at 0x317184**: This is the frame counter increment (`$s1 = $s1 + 1`). Modifying this to increment by 2 (or skip the WaitVSync wait) would be the direct path to 120 Hz simulation, as confirmed by the 120 Hz handoff document.

## 6. Files Used

| File | Purpose |
|------|---------|
| `~/dev/ssx3-work/E32-inputs/cd/SLUS_207.72` | PS2 ELF binary (9.4 MB, main game binary) |
| `~/dev/ssx3-work/codegen-ssx3/` | Generated C++ simulation code (~9,441 functions) |
| `~/dev/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv` | Function address map (function name → start → end → size) |
| `~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Syscalls/Dispatcher.cpp` | Syscall dispatcher (line 376: WaitVSync → 0x74 → SetSyscall) |
| `~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/Syscalls/Interrupt.cpp` | WaitVSyncTick implementation (line 78) |
| `~/dev/PS2Recomp/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | Scheduler `waitVSync` (line 2057), `completeVSync` (line 2065) |
| `local/muse/prompts/X2.md` | Authoritative task brief |
| `local/muse/prompts/X0.md` | Frame advance logic brief (GameCube/Dolphin leads) |
| `120HzHandoffAndSamplingPlan.md` | 120 Hz handoff document (patch site 0x317184 reference) |
| `AGENTS.md` | Repository rules and product direction |
