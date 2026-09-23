# [X1] Static Read: Stall Functions 0x27CEA8, 0x27D330, 0x284B58, 0x423DC0, 0x377B6C

**Brief:** `local/muse/prompts/X1.md`
**Date:** 2026-09-22
**Status:** Complete

## Table 1: Callers of Stall-Causing Functions

| Function | Callers (File, Guest Addr) | Notes |
|----------|---------------------------|-------|
| `0x27CEA8` | `sub_0027CE58_0x27ce58.cpp` (entire function) | Dispatch callback runner |
| | `sub_002797A0_0x2797a0.cpp` at `0x279D18` (line 3277) | Called from a path scheduling routine |
| `0x27D330` | `sub_0027D320_0x27d320.cpp` at `0x27D330` (line 48) | Called directly from the caller's entry point |
| | `sub_0027CEA8_0x27cea8.cpp` at `0x27CF50` (line 417) | Called inside the stall loop body |
| `0x284B58` | `sub_00283E60_0x283e60.cpp` | IOP shutdown command dispatch |
| | `sub_00284AE8_0x284ae8.cpp` | IOP status polling helper |
| `0x423DC0` | `sub_00423DB0_0x423db0.cpp` (entire function, line 49) | Syscall wrapper (Open, 0x44) |
| | `sub_00376938_0x376938.cpp` at `0x377B5C`, `0x377B64` | Open call from stall loop (lines 10133, 10159) |
| | 30+ other callers (syscalls: Read, Write, Close, Lread, etc.) | Syscall dispatcher |
| `0x377B6C` (return addr) | `sub_00376938_0x376938.cpp` at `0x377B64`/`0x377B68` (lines 10162) | Returned-to address after Open completes |

## Table 2: Stall Loop Exit Conditions (Static Read)

### Loop A: `0x27CEA8` (dispatch callbacks with stall check)
- **Address range:** 0x27CEA8 - 0x27CF88
- **Structure:** Outer loop iterates 0..19 (20 iterations), polling a dispatch table.
- **Outer exit condition:** If `READ32(s4 + offset(s3)) != 0` (non-zero callback found), the loop exits and that callback is invoked. If all 20 entries are zero, the function returns to caller.
- **Inner stall loop (at 0x27CF50):** Calls `func_27D330` (0x27D330) in a loop. Exit when `$s0 < $s2` (i.e., `$s0 < $s3` from `bnez` count), checked via `bnel` at `0x27CF5C`. This is guarded by `eeCheckpointDue()` — the runtime will yield.
- **Inner stall check:** Reads `$v1 = READ32(s1 + 0xC)` each iteration.
- **Key status read:** `$s4` pointer comes from `READ32(s4)` at `0x27CECC`.
- **Stall write:** `WRITE32(s4, s1)` at `0x27CF00` — writes back s1 pointer.

### Loop B: `0x27D320 -> 0x27D330` (data processing)
- **Address range:** 0x27D320 - 0x27D330
- **Structure:** Shifts `$a1 <<= 2`, computes `a0 += a1 * ...`, then `jr $ra`.
- **Exit condition:** Returns directly via `jr $ra` to caller's return address (0x27CF58). No loop of its own — it's a subroutine called from 0x27CEA8's inner loop.
- **Stall concern:** The caller (0x27CEA8) wraps calls to this in a loop checking `s0 < s2`.

### Loop C: `0x284B58` (IOP shutdown poll)
- **Address range:** 0x284B58 - 0x284B80
- **Structure:** Contains 4 distinct path handlers (jr $ra variants), each reading from `a0`-relative offsets (0, 0x30, 0x70, 0x74, 0x78).
- **Exit condition:** Each path returns immediately via `jr $ra`. The *caller* polls these, not the function itself.
- **Key caller behavior (in 0x283E60 / 0x284AE8):** Polls `READ32(s0 + 0x38A8) == 0` — the IOP shutdown status flag must clear to 0.

### Loop D: `0x377B6C` (IOP handle poll + Open)
- **Context:** Located in `sub_00376938` (lines 10133-10250), called from `0x377B5C`.
- **Exit conditions (both must pass):**
  1. `sltiu $v1, $v1, 0x1` at `0x377B7C`: `handle < 1` (handle is -1 / does not exist yet)
  2. `sltiu $v0, $v0, 0x1` at `0x377B88`: `pending < 1` (no pending IOP command)
- **Stall writes:** The loop writes back handle (0x5A10) and pending (0x5A24) each iteration, plus params (0x5A00-0x5A18). This is an IOP-command dispatcher/poller.
- **Post-Open:** After Open syscall returns, the code at 0x377B70 constructs command `$a1 = 0xCCCC80` (lui $a1, 0xC | ori $a1, 0xCC80), reads pending op from 0x5A24, and writes the handle + params back.

## Table 3: Syscalls Called From/ Near Stall Paths

| Syscall Offset | $v1 (syscall #) | Syscall Name | Notes |
|---------------|-----------------|-------------|-------|
| `0x423DC0` | 68 (0x44) | Open | **STALL-CRITICAL** — called from 0x377B64, blocks until file opens |
| `0x423DA0` | 64 (0x40) | Lread | Called during stall wait; reads from handle |
| `0x423C90` | 47 (0x2F) | Read | Used in stall polling |
| `0x423C40` | -42 (0xFFD6) | Close | Called to close handle after stall |
| `0x423CB0` | -49 (0xFFCF) | Write | Used for IOP command dispatch |
| `0x423B50` | -27 (0xFFE5) | IOP Shutdown (cmd 0xE5) | Negative = unsigned 0xE5 = 229 |
| `0x423B20` | 252 (0xFC) | IOP Shutdown (cmd 0xFC) | Full shutdown |

## Table 4: Memory Addresses Polled in Stall Loops

| Address | Function | Operation | Meaning |
|---------|----------|-----------|---------|
| `s3 + 0x5A10` | 0x377B6C | lw `$v1` | IOP handle number (polling for valid handle) |
| `s3 + 0x5A24` | 0x377B74 | lw `$v0` | Pending IOP command (stall while != 0) |
| `s3 + 0x5A0C` | 0x377B80 | lw `$a3` | IOP command parameters |
| `s0 + 0x38A8` | 0x284AE8 | lw (stall poll) | IOP shutdown status flag (0 = not shutting down) |
| `s0 + 0x234C` | 0x284AE8 | lh (stall poll) | IOP shutdown code (== 0x41 = shutdown complete marker) |
| `s0 + 0x1080` | 0x284AE8 | sw (stall trigger) | Write `0x41` to trigger IOP shutdown |
| `s4 + offset(s3)` | 0x27CEA8 | lw (outer loop) | Dispatch table callback pointer (0x27CECC) |
| `s1 + 0xC` | 0x27CEA8 inner | lw (inner loop) | Per-callback status (inner stall exit) |
| `a0 + 0x38` | 0x284B58 | lw (path 2) | Shutdown progress (non-negative = done) |

## Analysis

### Three Distinct Stall Paths

**Path 1 — IOP Open Stall (0x377B6C):**
The game attempts to `Open` a file handle via syscall 68 (0x44). The stall loop at 0x377B6C polls two conditions: (1) the handle number at 0x5A10 must be >= 1 (i.e., handle -1 means not ready), and (2) the pending command flag at 0x5A24 must be 0 (no pending IOP work). If either fails, the loop re-submits the Open request.

**Root cause hypothesis:** If the runtime's syscall handler for Open (0x423DE0) doesn't properly simulate IOP file opening, or if it returns -1 / blocks indefinitely, the stall loop never exits. The runtime must synthesize a valid handle and return it, or simulate the IOP filesystem behavior.

**Path 2 — IOP Shutdown Stall (0x284AE8 / 0x283E60):**
The game triggers IOP shutdown by writing `0x41` to offset 0x1080 from `s0`, then polls: (1) `s0 + 0x38A8 == 0` (shutdown status flag), and (2) `s0 + 0x234C` reads the shutdown code (expecting 0x41). After shutdown completes, it polls `s0 + 0x234C` to read the shutdown code (must equal 0x41), then writes the shutdown command `0x41` to `s0 + 0x1080`.

**Root cause hypothesis:** The runtime must implement the IOP shutdown command (syscall 229 / 0xE5 at 0x423B50) to respond correctly to the shutdown command, setting the status flag to 0 and the shutdown code to 0x41. If this doesn't happen, the stall poll `READ32(s0 + 0x38A8) == 0` never passes.

**Path 3 — Dispatch Callback Stall (0x27CEA8):**
The game iterates through 20 dispatch callbacks, invoking each one with data from `s1`. Inside each callback, it calls `func_27D330` (which is just data processing — shift/add, then return). The inner loop checks `s0 < s2` and reads `s1 + 0xC` as a status. The outer loop checks `dispatch_table[offset] != 0`.

**Root cause hypothesis:** If the dispatch table at `s4` contains non-zero entries that invoke callbacks where `s1 + 0xC` never reaches a valid exit value, or if `func_27D330` stalls, the loop hangs. The runtime yields via `eeCheckpointDue()` but may never make progress.

## Recommended Next Action

1. **Priority 1 — Open Syscall (0x423DE0):** Implement a synthetic file open that returns a valid handle (>= 1) and ensures the stall loop at 0x377B6C sees handle >= 1 and pending == 0. The stall loop actively writes back the handle and pending flag each iteration, suggesting the game expects a specific IOP filesystem interface.

2. **Priority 2 — IOP Shutdown (0x423B50 / 0x423B20):** Implement the shutdown command handler to set `s0 + 0x38A8 = 0` and `s0 + 0x234C = 0x41` after a simulated delay.

3. **Priority 3 — Dispatch Callbacks (0x27CEA8):** Ensure dispatch callbacks return proper status values at `s1 + 0xC` and that the dispatch table is populated with valid entries, or that the game initializes the table to zeros (no callbacks to invoke).

4. **Validate with runtime boot:** After implementing the above, test with a game boot to verify the stall loops exit and gameplay proceeds.
