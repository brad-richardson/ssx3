# E54C — MMI halfword interleave semantics

Worker: Codex. Brief: `local/muse/prompts/E54C.md`. The orchestrator decides the gate. Remote fork `ssx3` verified at `aa20d4a09305258d1a4b0e4f3defdbb196901cc9` by `git ls-remote fork refs/heads/ssx3`; new worktree `~/dev/ssx3-work/E54C/PS2Recomp` branched from that commit. Local branch `e54-mmi-interleave` has commit `89bec9b7f732f3938c89227927e1531d6fd4c346` with `Orchestrated-By: Codex`. No push.

| Gate | Evidence | Receipt |
| --- | --- | --- |
| Oracle and operand order | PCSX2 `pcsx2/MMI.cpp` at `9056c0834`, lines 1121–1137 and 1498–1514, assigns lanes from saved `Rs`/`Rt` as below. Fork `mmi_translation_helpers.cpp:147-148,201-202` passes `GPR_VEC(ctx, rs)` as macro `a` and `GPR_VEC(ctx, rt)` as `b`. | `~/dev/ssx3-work/E54C/MMI-9056c0834.cpp`; fork source |
| Generated sites | Four `PINTEH` guest instructions at `0x3cb8b0`, `0x3cb8b4`, `0x3cb8b8`, `0x3cb8bc` in each of `sub_003CB538` and `sub_003CB540`; all have `Rs=$zero`. No `PS2_PINTH(` site found by grep in canonical generated `.cpp` files. Static presence does not establish boot reach. | `~/dev/ssx3-work/codegen-ssx3/sub_003CB538_0x3cb538.cpp`, `sub_003CB540_0x3cb540.cpp` |
| Before-fix vectors | Compiled probe against unmodified macro returned wrong lane orders, tabulated below. | `~/dev/ssx3-work/E54C/before_vectors.cpp`, `before_vectors.txt` |
| Source diff | Changed only the two macros: `PINTEH` gathers even halfwords then interleaves; `PINTH` interleaves low `Rt` and high `Rs`. Six focused tests and minimal registration/CMake added. | Fork commit `89bec9b`; `after_vectors.txt` |
| Taps OFF Release | One configure/build attempt passed; runtime/aggressive logs and taps OFF, canonical E56 codegen. `ps2x_tests` from fork root: **566/566**, zero failed, including six new cases. | `~/dev/ssx3-work/E54C/{cmake-off.log,build-off.log,suite-off.log,build/CMakeCache.txt}` |
| Taps ON Release | One configure/build attempt passed; runtime/aggressive logs OFF, taps ON, same codegen. Suite from fork root: **661/661**, zero failed. | `~/dev/ssx3-work/E54C/{cmake-on.log,build-on.log,suite-on.log,build-taps/CMakeCache.txt}` |
| One I26-FAST boot | Mini slot 1, own PID 77247, dev-only `PS2X_SKIP_MOVIE=1`, wall cap 500 s. `bound=target`, `rc=0`, 122.018 s, last tick 2057 (target ≥2050). Boot and PK logs 46,773,721 B, below 64 MiB. Lease released. Functional diagnostic boot only. | `~/dev/ssx3-work/E54C/run/mmi-one/{result.json,boot.log,ps2_pklog.txt}` |
| Frames viewed | Select Character tick 830 shows Zoe. Race tick 1810 shows HUD 00:00:01, 0%; tick 1940 shows HUD 00:00:03, 1%. Known large dark GS composite region remains in both race frames. | `~/dev/ssx3-work/E54C/run/mmi-one/{sc-tick830.png,race_early-tick1810.png,race_late-tick1940.png}` |
| Runner-dir check | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty after commit. Fork worktree clean. No generated sources, game data, or binaries committed. | Fork command output |
| Storage | E54C directory 722 MiB, below 8 GiB. Global ssx3 internal usage 107.2/200 GB; free disk 136 GiB. | `du -sh ~/dev/ssx3-work/E54C`; `local/tooling/disk_budget.sh` |

## Halfword lane vectors

`Rs = [1100,1101,1102,1103,1104,1105,1106,1107]`; `Rt = [2200,2201,2202,2203,2204,2205,2206,2207]` (hex). `Rs=0` means all zero halfwords. Alias cases assign back into the same value used as both operands. Expected lanes come from the pinned PCSX2 source; observed lanes were produced by a host probe through `ps2_runtime_macros.h` with the Mac SSE2NEON path.

| Case | Expected and after-fix observed | Before-fix observed |
| --- | --- | --- |
| PINTEH distinct | `2200 1100 2202 1102 2204 1104 2206 1106` | `2204 1104 2205 1105 2206 1106 2207 1107` |
| PINTH distinct | `2200 1104 2201 1105 2202 1106 2203 1107` | `2200 1100 2201 1101 2202 1102 2203 1103` |
| PINTEH Rs=0 | `2200 0000 2202 0000 2204 0000 2206 0000` | `2204 0000 2205 0000 2206 0000 2207 0000` |
| PINTH Rs=0 | `2200 0000 2201 0000 2202 0000 2203 0000` | `2200 0000 2201 0000 2202 0000 2203 0000` |
| PINTEH alias | `1100 1100 1102 1102 1104 1104 1106 1106` | `1104 1104 1105 1105 1106 1106 1107 1107` |
| PINTH alias | `1100 1104 1101 1105 1102 1106 1103 1107` | `1100 1100 1101 1101 1102 1102 1103 1103` |

## Two-read SHA-256 ledger

Both reads matched before build or boot use. ISO, ELF, and register file reads are in `~/dev/ssx3-work/E54C/input-sha.txt`.

| Item | SHA-256 |
| --- | --- |
| Canonical E56 `codegen-ssx3/register_functions.cpp` | `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3` |
| Stock ELF `E32-inputs/cd/SLUS_207.72` | `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc` |
| Stock ISO `E32-inputs/SSX 3 (USA).iso` | `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5` |
| E54C taps-OFF Release runner `build/ps2xRuntime/ps2EntryRunner` | `77a28b3fa59a5839752252e27358569a3bd84caf5903072ea731886dd31dfac4` |

Frame SHA-256 values (artifact identity only, no cross-run comparison): Select Character tick 830 `43ff22a5f005e629a22ea6d8196dc8f79245ea3587713ccd6955e5905e0a65f3`; race tick 1810 `3f24baee0ada6b0bf8e99d4b75a157fe032afab6515eec3f6509d725cd0956c7`; race tick 1940 `9e86b1cc85b3c5ae9f37ee57b939e94d6d4c30f121cc6a02602eda67aff6fe68`.

## Exact commands

From `~/dev/ssx3-work/E54C/PS2Recomp`, unless noted:

```sh
git worktree add ~/dev/ssx3-work/E54C/PS2Recomp -b e54-mmi-interleave aa20d4a09305258d1a4b0e4f3defdbb196901cc9
zsh ~/dev/ssx3-work/E54C/build.sh off
../build/ps2xTest/ps2x_tests > ../suite-off.log 2>&1
zsh ~/dev/ssx3-work/E54C/build.sh on
../build-taps/ps2xTest/ps2x_tests > ../suite-on.log 2>&1
python3 ~/dev/ssx3-work/E54C/e54c_boot.py --label mmi-one --capture --target 2050 --wall 500
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git commit -m '[E54C] Correct MMI halfword interleave lanes' -m 'Match PCSX2 PINTEH and PINTH lane order and cover distinct, zero Rs, and aliased operands.' -m 'Orchestrated-By: Codex'
```

Gaps: Boot reach of the generated `PINTEH` sites is unknown; no `PINTH` generated site was found by the current grep. The boot checks functional regression through race tick 2057; it does not establish MMI instruction reach or clean speed. No free-running fixed-tick frame-hash comparison was used before E55. No fork or ssx3 push.
