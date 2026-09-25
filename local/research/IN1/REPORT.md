# IN1 Part 1 — do the missing VIF1 interrupts matter?

Worker: Muse Code, brief `local/muse/prompts/IN1.md`. Base fork `ssx3` `56a5e8a`,
worktree `~/dev/ssx3-work/IN1/PS2Recomp`, branch `in1-intc` (one commit
`775600c`, local only, no push). Runner `ba412c9f…554ab468` (two matching SHA
reads), suite 611/611. Route I26-FAST, `PS2X_DETERMINISTIC=1`,
`PS2X_SKIP_MOVIE=1` (dev-only), empty mc0, paraLLEl (`GRANITE_VULKAN_LIBRARY` +
`PS2X_GS_BACKEND=parallel`, GB8 env), `PS2X_MISSING_FUNCTION_POLICY=stop`.

Code change (default-off logging only, no behaviour change; `+40` in
`ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp`, runner dir untouched):
`PS2X_VIF1_IBIT_LOG=1` → one `[vif1:ibit] vsync=<n> count=<m>` line per vsync
(zero-count vsyncs included), printed as the vsync advances, counting VIFcodes
with bit 31 set at the existing `irq` site.

## Q1 — readers of `0x5059d8+0x80` (0x505a58): none

Only 4 static materializations of `0x5059d8` exist in 813,048 indexed
instructions (`ee-xref`, exhaustive over lui+addiu/ori/load/store pairs):

| Site | Function | Use of the base |
| --- | --- | --- |
| `0x362364` | VIF1 INTC handler `0x362340` | `$a1` = base; `lw`+`sw` at `+0x80` = the increment itself |
| `0x375ebc` | `sub_00375A08` | `$a0` = base in jal delay slot → callee `sub_00361EB8` |
| `0x3762e0` | `sub_00375A08` | `$a0` = base in jal delay slot → callee `sub_00361F40` |
| `0x377cc8` | `sub_00376938` | `$a0` = base in jal delay slot → callee `sub_00361F90` |

What the three callees do with the base (register followed through every
nested call; `ee-at` excerpts below):

| Callee | Behaviour on the base | Touches `+0x80`? |
| --- | --- | --- |
| `sub_00361EB8` | init: stores `-1` to `+0x00–0x3C` and `+0x40–0x7C`; zeroes `+0x80–0x94` via `sub_00361F60`; registers INTC 5/7 handlers via `sub_00361E30`→`sub_00361F98` (writes handler ids at base+cause*4 = `+0x14`/`+0x1C`) | write once (zero at init), never read |
| `sub_00361F40`→`sub_00361E80`→`sub_00362008` | unregisters INTC 5/7 (reads id + writes `-1` at `+0x14`/`+0x1C`) | no |
| `sub_00361F90` | single `jr $ra` — empty stub; the `0x377cc8` call is a no-op | no |

Every load/store at offset `0x80` in the reachable set, `sub_00375A08`,
`sub_00376938` (exhaustive sweep; all other `+0x80` ops in `sub_00376938` are
`($sp)` stack slots, 24 total):

| Addr | Insn | Base reg | Verdict |
| --- | --- | --- | --- |
| `0x362378` / `0x362388` | `lw`/`sw $v0, 0x80($a1)` | `$a1` = `0x5059d8` | the handler's own increment, not a reader |
| `0x3621a8` / `0x3622b4` | `sd`/`ld $v0, 0x80($a0)` | `$a0` = caller's stack buffer (`sub_00362120`/`sub_00362230` FP save/restore) | stack slot, not the counter |
| `0x376524` | `lw $a1, 0x80($v0)` | `$v0` = `0xA4*$s1 + [$s0+0x59CC]` (vtable-method array entry at `0x3764c0`, `this`-relative) | cannot alias: the `0x5059d8` pointer is never stored to memory (see below), so no loaded pointer can equal it |
| `0x375f78`, all in `sub_00376938` | `sdr`/`sq`/`lq`/… `0x80($sp)` | `$sp` | stack slots |

Pointer-escape audit: all 50 stores in `[0x361e30,0x362400)` with source
`$a0/$a1/$s0/$s1/$v0/$v1` enumerated. Every `sq $s0/$s1,($sp)` is a prologue
callee-save that precedes the `daddu $s0,$a0` assignment (caller's value, not
the pointer); all other value stores are `-1`/`0`/handler ids/FP regs or the
`8 → VIF1_FBRST` write. The pointer `0x5059d8` is never written to memory, so
no indirect reader can exist either. `ee-xref 0x505a58`: no code refs, no data
words. Neighbour context: `sub_003627A8` writes `0x505a80` (base+`0xA8`) at
`0x3627f4`/`0x362804`; that function has no `+0x80` loads.

`ee-at` excerpts (handler increment; init zeroing; the vtable load):

```
0x362378: lw $v0, 0x80($a1)     # $a1 = 0x5059d8 (set 0x362364, delay slot)
0x362388: sw $v0, 0x80($a1)     # [delay slot] write-back of v0+1
0x361f60: addiu $a0, $a0, 0x84  # sub_00361F60 zeroes base+0x80..0x94, no reads
0x376524: lw $a1, 0x80($v0)     # $v0 = 0xA4*$s1+[0x59CC]($s0), entry field -> func_37BD98
```

Verdict: the counter is **write-only** — zeroed once at init, incremented by
the VIF1 handler. It is not frame pacing, not a wait loop, not a read debug
stat. Nothing observes it.

## Q2 — i-bit VIFcodes per vsync on the F1 det route: zero everywhere

One boot B1 to tick 2400 (`bound=target`, last_tick 2408, 86.3 s wall,
`gs_fatal=null`, `[gs-path]` = F1 line). `[vif1:ibit]` series:

| Measure | Value |
| --- | --- |
| Readable per-vsync lines | 2337, vsync 38–2383 (first VIF1 activity at tick 38) |
| Nonzero vsyncs | **none — all 2337 lines are `count=0`; total 0 i-bit VIFcodes** |
| Race phase (≥ tick 1714) | 668 lines, 1714–2383, all 0 |
| Interior vsyncs lost to torn stdout writes | 11 (9 gaps: 503, 640, 849, 986, 1220, 1352, 1687, 1952, 2252; 4 torn fragments recovered) |
| Tail unflushed (SIGTERM + stdio buffering, pre-declared) | ~2384–2407 |

The zeros are "VIFcodes seen, none with the i-bit", not idle: each vsync's
line prints only when a later vsync's VIFcode arrives, so contiguous lines
38–2383 prove VIF1 processed ≥1 VIFcode at every vsync 39–2384.
Cross-check: `gfx_stats.log` (2409 lines, vsync 0–2408) shows ~1100+
MSCAL/vsync through the race (e.g. tick 1710: `mscal=1109 vu_maxcyc=25784`).
The game does not set the i-bit on this route — consistent with pacing via
MSCAL/FLUSH + VBlank instead of i-bit stalls.

Adjacent observation (no verdict): the game handler tests VIF1_STAT bit 10
(`andi 0x400`, `0x36235c`), while our interpreter sets bit 11 on `irq`
(`ps2_vif1_interpreter.cpp`, `1u << 11 // INT`). Whoever models INTC 5 later
should check the STAT layout; out of scope here (no behaviour change).

## Q3 — PCSX2 reference: not run (brief's opt-out applies)

Q1 shows no reader, so per the brief this run is optional — and Q2 makes it
moot: with zero i-bit VIFcodes on the route, INTC 5 would never fire on real
HW either. Cheap check only: no `hwIntcIrq`/`INTC_VIF1`/i-bit mentions in
`local/research/{T48,T65,AU9}/REPORT.md`. If the orchestrator wants
belt-and-braces, the named follow-up stands: `au9_patch.py` hook pattern on
bytesize counting `hwIntcIrq(INTC_VIF1)` over 30 s of race.

## Recommendation

**INTC 5 + i-bit stall modelling is not needed** for the SSX 3 race route:
the game sets no i-bit VIFcodes (Q2: 0 of ~2400 vsyncs) and reads the VIF1
interrupt counter nowhere (Q1: write-only). The missing VIF1/VU1 dispatch
(CT1 Q4) is therefore benign on this route. Suggested next action: keep the
CT1 finding closed for the race; re-open only if a new route sets the i-bit
(the `PS2X_VIF1_IBIT_LOG` counter on branch `in1-intc` detects exactly that —
fold or drop per orchestrator call; a future version should `fflush` or use
the diag-report path, and note stdout logging races with `[vsync-rate]`).

## Gaps

1. 11 interior vsyncs + ~24 tail vsyncs of the ibit series unobserved (torn
   stdout writes from concurrent log threads; SIGTERM stdio-buffer loss).
   All 2337 readable vsyncs are 0; per-frame i-bit use is ruled out, a
   sub-24-vsync burst hiding in the gaps is not (mechanistically unlikely —
   the game's VIF1 packet builder would emit i-bits every frame if it paced
   on them).
2. Route-scoped (I26-FAST single race), same as CT1. Other paths (menus
   beyond the route, Multi Play/Online) untested.
3. A second boot with the same binary would have the same flush/tear
   behaviour, so it was not spent; a rebuild for `fflush` would exceed the
   1-build budget.

## Receipts

- Build: `56a5e8a` + `in1-intc` `775600c` (40-line logging diff),
  Release/HB-clang, `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`,
  `BUILD_TEST=ON`, runtime/aggressive logs OFF, diag taps OFF, det-hash OFF,
  `GS_SHADOW_PARALLEL=ON`, parallel-gs `963cb57` (fork tip). Configure rc=0,
  build rc=0, suite **611/611 rc=0**. Runner
  `ba412c9f89535296aba554e2a0bfa4c1c3eea82112a4aa0af7a8bfab554ab468`
  (two reads match).
- B1: `bound=target`, last_tick 2408, 86.3 s, `gs_fatal=null`, slot 1.
  Pins (ISO/ELF/codegen SHA) verified twice per boot (match CT1 pins).
- Scratch: `~/dev/ssx3-work/IN1/` (build, `in1_boot.py`, `run/B1`). Disk
  112.5/200 GB before build.
- Runner-dir guard: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`
  empty (change is in `src/lib/` only). Worktree commit local, never pushed.
- Budgets: 1 build / 1, 1 boot / 2, ~1 h of 1.5 h.

Exact commands:

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/IN1/PS2Recomp -b in1-intc fork/ssx3  # 56a5e8a
# edit ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp (+40: PS2X_VIF1_IBIT_LOG)
cd ~/dev/ssx3-work/IN1
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)
cp ~/dev/ssx3-work/CT1/ct1_boot.py in1_boot.py  # then adapt: IN1 paths/labels, swap CT1 knobs for PS2X_VIF1_IBIT_LOG
python3 in1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label B1 --stop-tick 2400
(cd PS2Recomp && git add ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp && git commit -m "[IN1] default-off PS2X_VIF1_IBIT_LOG per-vsync i-bit counter")
```

## Orchestrator gate (2026-09-25)

**Pass.** No reader of the handler's counter was found on the route, and the game sets no VIF1 i-bits
(count 0 in every readable vsync), so INTC 5 could never fire here; CT1's missing dispatch is benign
for this route. The `PS2X_VIF1_IBIT_LOG` counter (`775600c`) is not folded. Side note for later:
the game tests VIF1_STAT bit 10 while our interpreter sets bit 11 on irq (unverified).
