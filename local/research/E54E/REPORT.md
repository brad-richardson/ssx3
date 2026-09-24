# E54E — signed branch predicate gate

Worker: Codex. Brief: `local/muse/prompts/E54E.md`. The orchestrator decides the verdict. **Stopped at the first failed functional frame gate.** The worker made no second boot, fix iteration, fork commit, report commit, or push. The orchestrator retained this failure report in Git.

| Gate | Evidence | Receipt |
| --- | --- | --- |
| Fork pin | `git ls-remote fork refs/heads/ssx3` returned `1aaed05256bf53881824a9edd96a7cd5b7e8bbcc`; E54E worktree branch `e54-sign-branches` starts there and remains uncommitted. | `~/dev/ssx3-work/E54E/PS2Recomp` |
| Pinned oracle | PCSX2 `9056c0834` interpreter reads `cpuRegs.GPR.r[_Rs_].SD[0]` for BLTZ/BGEZ/BLEZ/BGTZ and all likely/link forms. `GPR_reg::SD[2]` has type `s64`; index 0 is the low 64-bit half. Exact locations: `pcsx2/Interpreter.cpp:355–403,437–514`; `pcsx2/R5900.h:20–29`. Oracle agrees with the 64-bit predicate. | `~/dev/ssx3-work/E54E/PCSX2-Interpreter-9056c0834.cpp` SHA-256 `0580afe6da6c08ce7bb9042c83074ed25b17080fce9be464ba96832cccd2385d`; `PCSX2-R5900-9056c0834.h` SHA-256 `a6ef18e1b646b5ba6c956c10836aa4f75fd8309798f0ac0cf8644faa41cbf323` |
| Affected labels/macros | Emitter `control_flow_emitter.cpp:407–425` covers BLEZ/L, BGTZ/L, BLTZ/L/AL/ALL and BGEZ/L/AL/ALL. Before edit all four families used `GPR_S32`; runtime macros at `ps2_runtime_macros.h:1290–1293` extract low 32 for S32 and low 64 for S64. `isLikelyBranch()` and `emitConditionalBranch()` link/delay-slot logic were not edited. | Fork source and emitter diff |
| Executed before/after truth table | A compiled C++ probe used the actual runtime `GPR_S32` and `GPR_S64` macros with both 64-bit halves seeded. Full 24-row table below. Six vectors include both distinguishing values, zero, sign-extended controls, and a negative upper half with positive low half. `1` means taken. | `~/dev/ssx3-work/E54E/{branch_probe.cpp,before_after_values.csv}` |
| Source and generated expressions | Four `GPR_S32` predicate returns changed to `GPR_S64`; no other emitter change. One regeneration with E54E TOML completed. Existing canonical generated output had 4,466 S32 signed expressions at 4,225 unique guest PCs; E54E output has 4,466 S64 expressions at the same sites. The two TSVs compare byte for byte after replacing `GPR_S32` with `GPR_S64` in the old TSV. Generated code stayed outside Git. Static sites do not prove boot reach. | Fork diff; `~/dev/ssx3-work/E54E/{ssx3-e54e.toml,regen.log,generated-before-expressions.tsv,generated-after-expressions.tsv,codegen/}` |
| Taps OFF Release build/suite | Release, runtime/aggressive logs OFF, taps OFF, E54E codegen. Build passed; `ps2x_tests` run from fork root: **572/572**, zero failed. | `~/dev/ssx3-work/E54E/{cmake-off.log,build-off.log,suite-off.log,build/CMakeCache.txt}` |
| Taps ON Release build/suite | Release, runtime/aggressive logs OFF, taps ON, E54E codegen. Build passed; `ps2x_tests` run from fork root: **667/667**, zero failed. | `~/dev/ssx3-work/E54E/{cmake-on.log,build-on.log,suite-on.log,build-taps/CMakeCache.txt}` |
| I26-FAST diagnostic boot | One mini slot 1 boot, own PID 1811, dev-only skip movie, vsync I26-FAST pad route, 500 s wall cap. The harness recorded `rc=0`, 36.325 s elapsed and host vsync tick 2103; **these are not race progress**. **Frame gate failed:** SC capture is black except for a marker; race captures at ticks 1810 and 1940 are black. All three saved PNGs have identical SHA-256 `557ce59f4f8610dc935b19e732b67e1e19df552f46e75e6b531a1708e013c737`, and the boot log lists frame FNV `4e3914cd`. Prior E54D captures show Zoe and a race HUD. No second boot or fix attempted. | `~/dev/ssx3-work/E54E/run/signed-one/{result.json,boot.log,sc-tick830.png,race_early-tick1810.png,race_late-tick1940.png}`; `~/dev/ssx3-work/E54E/boot-driver.log` |
| Two-read SHAs | Both reads matched: stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`; ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`; generated register file `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`; taps OFF runner `da5aae25590af4dd7cc04feccdffff7269e3f475143826ea9959e51a96f3eadc`. | `~/dev/ssx3-work/E54E/{input-sha-read1.txt,input-sha-read2.txt,gate-sha-read1.txt,gate-sha-read2.txt}` |
| Runner-dir check | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty at worktree HEAD. No runner-dir edits. `git diff --check` clean. | Fork Git commands |
| Budgets | E54E directory 973 MiB, under 9 GiB. Global internal usage 109.2/200 GB; 133 GiB free. Boot log 10,061 B plus PK log 1,498,630 B = 1,508,691 B, under 64 MiB. Lease released by boot script. One regeneration, one boot, no >600 s boot. | `du -sh`, `local/tooling/disk_budget.sh`, `run/signed-one/result.json` |

## Executed predicate table

Values are `before S32 / after S64` for BLTZ, BGEZ, BLEZ, BGTZ, respectively; likely/link variants share their family's predicate.

| Low 64 bits | Upper 64 bits | BLTZ | BGEZ | BLEZ | BGTZ |
| --- | --- | --- | --- | --- | --- |
| `0000000180000000` | `1122334455667788` | 1/0 | 0/1 | 1/0 | 0/1 |
| `ffffffff00000000` | `1122334455667788` | 0/1 | 1/0 | 1/1 | 0/0 |
| `0000000000000000` | `1122334455667788` | 0/0 | 1/1 | 1/1 | 0/0 |
| `000000007fffffff` | `1122334455667788` | 0/0 | 1/1 | 0/0 | 1/1 |
| `ffffffff80000000` | `1122334455667788` | 1/1 | 0/0 | 1/1 | 0/0 |
| `0000000000000001` | `ffffffffffffffff` | 0/0 | 1/1 | 0/0 | 1/1 |

The focused suite decodes all 12 branch encodings and checks emitted S64 expressions, link writes and branch block shape. The four-line emitter diff shows likely, link and delay-slot policy unchanged.

## Commands and stop point

The temporary tool build first configured against an empty E54E codegen directory and CMake rejected `ps2_game_objects` with no sources. One clear repair configured `ps2_recomp` against the existing canonical codegen into a separate E54E tool build. This was before the single E54E regeneration. The failed pre-regeneration configure log is `cmake-tool-attempt1.log`; repaired logs are `cmake-tool.log` and `build-tool.log`.

```sh
git ls-remote fork refs/heads/ssx3
git worktree add ~/dev/ssx3-work/E54E/PS2Recomp -b e54-sign-branches 1aaed05256bf53881824a9edd96a7cd5b7e8bbcc
/opt/homebrew/opt/llvm/bin/clang++ -std=c++20 -O2 -DUSE_SSE2NEON -I PS2Recomp/ps2xRuntime/include -I PS2Recomp/ps2xIOP/include -I ~/dev/ssx3-work/E50/build/_deps/sse2neon-src branch_probe.cpp -o branch_probe
./branch_probe > before_after_values.csv
zsh build-tool.sh off
./build-recomp/ps2xRecomp/ps2_recomp ssx3-e54e.toml > regen.log 2>&1
zsh build.sh off
../build/ps2xTest/ps2x_tests > ../suite-off.log 2>&1  # from fork root
zsh build.sh on
../build-taps/ps2xTest/ps2x_tests > ../suite-on.log 2>&1  # from fork root
python3 e54e_boot.py --label signed-one --capture --target 2050 --wall 500
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
```

## Post-gate path, timeline and capture comparison

The orchestrator confirmed the failed visual gate and requested this read-only comparison. No repair was applied because the compared paths and capture settings agree; one validation boot would not test a named correction.

| Check | E54D reference | E54E candidate | Evidence |
| --- | --- | --- | --- |
| Runner | `/Users/brad/dev/ssx3-work/E54D/build/ps2xRuntime/ps2EntryRunner` | `/Users/brad/dev/ssx3-work/E54E/build/ps2xRuntime/ps2EntryRunner` | Both `result.json` files; E54E runner two-read SHA above. |
| Build codegen | `PS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/E54D/codegen` at E54D build time; subsequently promoted to `/Users/brad/dev/ssx3-work/codegen-ssx3` | `PS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/E54E/codegen` | Both `build/CMakeCache.txt`; E54E `build/build.ninja` includes E54E codegen and fork include paths. No E54D/canonical codegen path appears in E54E runner build source rules. |
| Generated source comparison | 9,457 canonical E54D files | 9,457 E54E files with identical names | 7,521 files byte-identical; 1,936 differ only in `GPR_S32` to `GPR_S64` on signed `branch_taken` lines; zero other file-content changes. E54E `register_functions.cpp` is byte-identical to canonical. |
| Boot inputs and captures | Same stock ELF/ISO, vsync-clock I26-FAST route, `PS2X_FRAME_DUMP_ONCE_TICKS=830,1810,1940` | Same values | Both `result.json` environment records and copied boot scripts. Same frame size 512×448 and `fbp=112/112 fallback=0`. |
| Boot timeline | At tick 830, character screen visible; at ticks 1810/1940, race HUD visible. PK log has 92,728 packets by tick 830 and 536,205 by tick 1810. | Captures at same ticks show black output. PK log has 8,000 packets by tick 830 and 16,820 by tick 1810. | Boot logs, frame PNGs, `ps2_pklog.txt` parsed by packet tick. First differing packet payload is index 352: E54D tick 82, FNV `9ff584f1`; E54E tick 83, FNV `84bd202a`, both 64 B source 2. Packet divergence is observed; its cause is not established. |
| Host vsync progression | Diagnostic rate falls from ~55/s at tick 275 to ~7/s near race captures. | Rate remains ~60/s from tick 300 through tick 2103. | Boot logs. The E54E host tick target and short wall duration do not establish gameplay progress. |

Gaps: The frame gate failed. Exact runner/codegen paths and matching capture settings provide no clear repair. The first packet divergence is not attributed to a particular guest branch or producer. Dynamic reach of a signed branch site is unknown. No validation boot was used after the failed gate. This diagnostic boot provides no clean speed number. Fork source remains uncommitted and unpushed; canonical fork/codegen stay at E54D.
