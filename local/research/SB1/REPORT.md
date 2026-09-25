# SB1 — signed-branch tripwire: the only live producer is legitimate

Worker: Muse Code. Brief: `local/muse/prompts/SB1.md` (design: `docs/research/review-2026-09-25-fable.md` §2, steps 1–6). The orchestrator decides the verdict. **Stopped per the stop rules: no HLE producer, no fix, no Boot B.**

## Answer

Exactly **one** signed-branch site in 2,403 ticks disagrees between the 32-bit and 64-bit predicates on the F1 base — and its producer is legitimate guest 64-bit arithmetic, not an HLE stub:

| PC | reg | value | tick | cycle | producer class |
|---|---|---|---|---|---|
| `0x411e4c` (`bltz $v0` in `_fpadd_parts`, ee-label verified) | 2 (`$v0`) | `0x1e98aca2908df150` (bit 63 = 0, bit 31 = 1) | 1468 | 7215761751 | legitimate 64-bit guest idiom: `dsubu $v0,$t3,$t2` mantissa difference in software double emulation (callers `dpadd`/`dpsub`, ee-xref verified) |

`ee-at 0x411e4c 12 4` excerpt:

```
0x411e38: 11050024  beq $t0, $a1, ...
0x411e3c: 016a102d  daddu $v0, $t3, $t2  [delay slot]
0x411e40: 15000002  bnez $t0, ...
0x411e44: 014b102f  dsubu $v0, $t2, $t3  [delay slot]
0x411e48: 016a102f  dsubu $v0, $t3, $t2
>> 0x411e4c: 04400005  bltz $v0, ...
0x411e50: 0002182f  dsubu $v1, $zero, $v0  [delay slot]
```

(`ee-func`: `sub_00411CD8 [0x411cd8, 0x411f18)`; `ee-label 0x411cd8` = `_fpadd_parts [ssx3.toml stub list]`; `ee-xref` = `jal` from `0x411f50` (`dpadd`) and `0x411fb4` (`dpsub`). `ee-label 0x411e4c` itself is unknown — described by address.)

Reading: on hardware `bltz` tests bit 63 (PCSX2 oracle, E54E report), so the 64-bit predicate is correct here and today's 32-bit predicate takes the wrong path (taken under s32, not-taken under s64). There is nothing to fix upstream — `$t2`/`$t3` are `ld`-loaded, `dsrl`-aligned 64-bit mantissas, the `dsubu` is exact. Per stop rule 2 this site is where the game truly depends on 64-bit semantics; the cure is the global s64 predicate itself, not a producer patch.

Stop rule that applied: **legitimate-64-bit-producer** (plus no mismatch before tick 90 — in fact none before tick 1468). No candidate fix exists → no Boot B. The E54E tick-82 divergence cannot be this site (it fires 1,386 ticks later); on E54E's base the only early site was the `0x3E3968` comparator, which the folded AU9 override now covers.

## Evidence

| # | Evidence | Result | Receipt |
|---|---|---|---|
| 1 | Tripwire implementation (emitter → `PS2X_SBR_*` macros; release collapses to `GPR_S64`; tripwire dual-evaluates, notes, returns `PS2X_SBR_MODE`) | 7 files, +117/−4; runner-dir check empty; `git diff --check` clean | Fork worktree `~/dev/ssx3-work/SB1/PS2Recomp`, branch `sb1-tripwire` @ `56a5e8a` + uncommitted diff (stat below) |
| 2 | One regen with modified `ps2_recomp` | 9,457 files; 1,936 predicate-only diffs (4,466 swapped lines, exactly E54E's count) + 1 behavior-neutral stub rename (`sceSifSendCmd`→`_sceSifSendCmd` at `0x426078`, overwritten at load by the `ssx3-sif-handshake` game override, `RPC.cpp:171`); `register_functions.cpp` byte-identical (SHA `8ea8ed43…`) | `~/dev/ssx3-work/SB1/{ssx3-sb1.toml,regen.log,codegen/}` |
| 3 | Taps-OFF + tripwire + det-hash build; suite | Build clean; **615/615 pass** (F1's 611 + 4 det-hash tests — F1's `suite.log` came from a det-hash-disabled build; SB1's build has it on) | `~/dev/ssx3-work/SB1/{cmake.log,build.log,suite.log}`; runner SHA `cc3e99f6…` (two reads in run `result.json`s) |
| 4 | Tripwire liveness: `PS2X_ENABLE_SBR_TRIPWIRE=1` in all 296 game-object unity TUs + runtime; generated `PS2X_SBR_LT(ctx, runtime, 2, 0x411E4C)` calls | Confirmed via `compile_commands.json` + generated source | `~/dev/ssx3-work/SB1/build/` |
| 5 | Boot A (`s32`, t400, paraLLEl, I26-FAST, det) | `bound=target`, 10.7 s, **0 `[sbr]` lines**; det-hash ticks 1..403 byte-identical to F1 B1 → s32 behavior verified, tripwire call path + mode selection live | `~/dev/ssx3-work/SB1/run/A-s32/{result.json,boot.log,trace.jsonl}` |
| 6 | Spare boot (`s32`, t2400, paraLLEl, I26-FAST, det + `PS2X_GS_CAPTURE`) | `bound=target`, 98.0 s, **exactly 1 `[sbr]` line** (the table row above); det-hash ticks 1..2402 byte-identical to F1 B1 (B1 skips one tick number in 1..2453, hence 2402 common) | `~/dev/ssx3-work/SB1/run/S-s32-2400-x/{result.json,boot.log,gs.cap(2.5 GB)}` |

One design adaptation: the macros take `runtime` explicitly (`PS2X_SBR_LT(ctx, runtime, rs, pc)`) instead of the sketched `(ctx, rs, pc)`, because tick/cycle/mode live on `PS2Runtime` and implicit scope capture is fragile. All 4 predicate strings and the note signature (`pc, rs, value, tick, cycle`) are otherwise exactly as designed. Log line: `[sbr] pc=0x… rs=… value=0x… tick=… cycle=…`; exit counts under `[sbr:mismatches]` (not observed — SIGTERM at target skips the destructor print).

No Boot B (no fix exists), no frames viewed (no frame gate in this brief; Boot A/spare ran without frame dumps), no fix SHA.

## Commands

```sh
git worktree add ~/dev/ssx3-work/SB1/PS2Recomp -b sb1-tripwire 56a5e8a  # base pin verified: 56a5e8a = F1 fold tip
cp <SSD>/ps2recomp-spike/PS2Recomp/games/ssx3/ssx3-functions.sweep.csv ~/dev/ssx3-work/SB1/  # input staged to internal
# TOML = tracked games/ssx3/ssx3.toml with only input/ghidra_output/output repointed (verified identical otherwise)
cmake -S SB1/PS2Recomp -B SB1/build-recomp -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3
cmake --build SB1/build-recomp
./build-recomp/ps2xRecomp/ps2_recomp ssx3-sb1.toml   # the one regen
cmake -S SB1/PS2Recomp -B SB1/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DET_HASH_TAP=ON -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_SBR_TRIPWIRE=ON -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=~/dev/parallel-gs -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/SB1/codegen
cmake --build SB1/build                             # the one full build
../build/ps2xTest/ps2x_tests                        # 615/615
python3 sb1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label A-s32 --sbr-mode s32 --stop-tick 400
python3 sb1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label S-s32-2400-x --sbr-mode s32 --stop-tick 2400 --gs-cap run/S-s32-2400-x/gs.cap --gs-stop-tick 2400
local/tooling/ee/ee-at 0x411e4c 12 4; local/tooling/ee/ee-func 0x411e4c; local/tooling/ee/ee-xref 0x411cd8; local/tooling/ee/ee-label 0x411cd8
```

Fork diff (uncommitted on `sb1-tripwire`, no push):

```
ps2xRecomp/src/lib/control_flow_emitter.cpp |  8 ++--
ps2xRuntime/CMakeLists.txt                  |  7 +++
ps2xRuntime/include/ps2_runtime.h           | 11 +++++
ps2xRuntime/include/ps2_runtime_macros.h    | 15 ++++++
ps2xRuntime/include/runtime/ee_scheduler.h  |  1 +
ps2xRuntime/src/lib/Kernel/EeScheduler.cpp  |  5 ++
ps2xRuntime/src/lib/ps2_runtime.cpp         | 74 +++++++++++++++++++++++++++++
```

## Budget, pins, gaps

- Pins: fork `ssx3` `56a5e8a`; ELF `1b49d05c…`, ISO `3c2f8eb1…`, SB1 `register_functions.cpp` `8ea8ed43…` (two matching reads per boot); runner `cc3e99f6a9de0dca687e5ca2b23dee861f6571d35a655c1305353e37b042f954`; `ps2_recomp` `eff41b95159605da7bf4fa44ffe70b02c0704b2610acb6d288289eb2ced4c709`; paraLLEl backend via `PS2X_GS_BACKEND=parallel` + `/opt/homebrew/lib/libvulkan.1.dylib` (GB8 env).
- Budgets: 1 regen, 1 tool build + 1 full build (≤2), 2 boots ≤600 s (Boot A + spare; no Boot B per stop rules), one mini slot each (slot 2, released). SB1 scratch 4.8 GB (≤15 GB); global 112.4/200 GB.
- Gaps:
  - G1. The note-print path has no end-to-end positive control on this base: nothing fires before t1468 except the one site, and the `0x3E3968` positive control would need an override-removing rebuild (over budget). Liveness rests on compile evidence (define in all game-object TUs), the generated call text, and the s32 hash-identity (which proves the call path + mode selection execute). The note body itself is straight-line map-insert + `fprintf`.
  - G2. Coverage is executed-branches-only to t2403 on I26-FAST; unreached signed sites (other routes, later ticks) are unobserved.
  - G3. Hit count for `0x411e4c` is unknown (first-sight line only; exit counts skipped by SIGTERM).
  - G4. E54E's work dir is deleted, so its codegen/build pairing cannot be re-checked directly; its report's post-gate table stands. The new datum is that on a base with the comparator override, no other pre-t90 site exists — consistent with the comparator being E54E's whole divergence.
  - G5. Whether the t1468 site's s32-vs-s64 direction flip changes any guest-visible state needs an s64 boot (a follow-up lane, not Boot B — no fix exists here).

## Orchestrator gate (2026-09-25)

**Pass, and it changes the plan.** With the `0x3E3968` override in place, exactly one live site
disagrees on the route: `0x411e4c` `bltz $v0` in `_fpadd_parts` (software double add, callers
`dpadd`/`dpsub`) at t1468, a legitimate 64-bit mantissa difference that today's 32-bit predicate
gets **wrong**. So (a) our current codegen miscomputes some software-double adds; (b) E54E's black
boot was most likely the comparator itself (the correct sort made the sound banks load on a runtime
that then had no SPU voice/cid-0 support), not a hidden non-sign-extended producer. Next (SB1 Part 2,
same pane): s64 boot with this build to t2400 (frames, cid0, first det-hash divergence tick), then a
release build with the 64-bit emitter and the override retired.
