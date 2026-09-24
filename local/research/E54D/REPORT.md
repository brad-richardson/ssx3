# E54D — LWU zero-extension gate

Worker: Codex. Brief: `local/muse/prompts/E54D.md`. The orchestrator decides the gate.

Remote fork `ssx3` was verified at `89bec9b7f732f3938c89227927e1531d6fd4c346` by `git ls-remote fork refs/heads/ssx3`. Local worktree `~/dev/ssx3-work/E54D/PS2Recomp` branched from that pin. Local fork commit: `1aaed05` (`[E54D] Zero extend LWU loads`, `Orchestrated-By: Codex`). No push.

| Gate | Evidence | Receipt |
| --- | --- | --- |
| Fork pin | `fork/ssx3` verified by `git ls-remote` at `89bec9b7f732f3938c89227927e1531d6fd4c346`; worktree `~/dev/ssx3-work/E54D/PS2Recomp`, branch `e54-lwu` from that pin. | `git ls-remote fork refs/heads/ssx3`; `git worktree add` output |
| Oracle/emitter | Pinned PCSX2 `9056c0834`, `pcsx2/R5900OpcodeImpl.cpp:592–623`: `LW` assigns `(s32)temp` to `SD[0]`; `LWU` assigns `u32 temp` to `UD[0]`, returning for `$zero`. Old fork emitter used `SET_GPR_U32`, whose macro casts through `int32_t`; `SET_GPR_U64` preserves the existing low-64 write behavior. | `~/dev/ssx3-work/E54D/PCSX2-R5900OpcodeImpl-9056c0834.cpp`; fork translator and runtime macro |
| Before/after tests | Before fix, new generated-snippet suite: 569/570, only LWU high-bit case failed. The same probe, compiled against the new generated snippet, gives the expected zero-extended values below. Final suites pass. | `~/dev/ssx3-work/E54D/{suite-baseline.log,before_values.txt,after_values.txt,build-baseline/ps2xTest/e54d_generated/e54d_lwu_snippets.h,build/ps2xTest/e54d_generated/e54d_lwu_snippets.h}` |
| Source diff | One emitter change: `LWU` now emits `SET_GPR_U64(..., (uint64_t)(uint32_t)READ32(...))`; `LW`, `LBU`, `LHU` and runtime macros untouched. Focused generated-snippet test/registration added. | Fork diff |
| Generated sites | One regeneration from E56-fold TOML retargeted to E54D produced 96 LWU occurrences at **92 unique guest addresses**; all 96 have the new expression. Static count only; boot reach unknown. | `~/dev/ssx3-work/E54D/{ssx3-e54d.toml,regen.log,generated-sites.txt,codegen/sub_003E3968_0x3e3968.cpp}` |
| Taps OFF build/suite | Release; runtime/aggressive logs OFF, taps OFF, E54D codegen. One gate configure/build passed; suite **570/570**, zero failed. | `~/dev/ssx3-work/E54D/{cmake-off.log,build-off.log,suite-off.log,build/CMakeCache.txt}` |
| Taps ON build/suite | Release; runtime/aggressive logs OFF, taps ON, E54D codegen. One gate configure/build passed; suite **665/665**, zero failed. | `~/dev/ssx3-work/E54D/{cmake-on.log,build-on.log,suite-on.log,build-taps/CMakeCache.txt}` |
| I26-FAST boot/frames | One mini slot 1 diagnostic boot with dev-only `PS2X_SKIP_MOVIE=1`, I26-FAST vsync pad route, own PID 89216, 500 s wall cap. `bound=target`, `rc=0`, elapsed 112.006 s, last tick 2069 (target ≥2050). Boot log 10,674 B + PK log 47,754,516 B = 47,765,190 B, under 64 MiB. Lease released; both slots free afterward. Frames viewed: Select Character tick 830 shows Zoe; race tick 1810 shows HUD 00:00:01 and 0%; race tick 1940 shows 00:00:03 and 1%, with the known dark GS composite region in both race frames. Functional regression boot only. | `~/dev/ssx3-work/E54D/run/lwu-one/{result.json,boot.log,ps2_pklog.txt,sc-tick830.png,race_early-tick1810.png,race_late-tick1940.png}` |
| Two-read SHAs | All pairs match: stock ISO `3c2f8eb182c9c6208a6e8172a41e61c98f420abe3f42c845f6829aeb9761ebf5`, stock ELF `1b49d05ca2793922180851b9e1ce9ae2291d61a7863565ac4e71f12e967af7bc`, E54D codegen register file `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`, taps-OFF runner `ed5dcfbe77e1e8b50c92e3749ea06ecc55aeb6a3ea6c98cc447524888265cc5f`. | `~/dev/ssx3-work/E54D/{input-sha.txt,gate-sha.txt}` |
| Runner-dir check | `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty before and after fork commit. Worktree clean. No generated sources, game data or binaries committed. | Fork command output and commit diff |
| Budget | E54D dir 1.1 GiB, under 9 GiB. Global ssx3 internal usage 108.2/200 GB; free disk 134 GiB after boot. | `du -sh ~/dev/ssx3-work/E54D`; `local/tooling/disk_budget.sh` |

## Before-fix executed values

The probe compiled the **old translator's generated snippets** from `build-baseline/ps2xTest/e54d_generated/e54d_lwu_snippets.h` against the real runtime macros. It seeded upper GPR half `1122334455667788` and compared the same word loaded by `LWU` and `LW`.

| Word | Old LWU low 64 | New LWU low 64 | LW low 64 | Upper 64 after both |
| --- | --- | --- | --- | --- |
| `80000000` | `ffffffff80000000` | `0000000080000000` | `ffffffff80000000` | `1122334455667788` |
| `ffffffff` | `ffffffffffffffff` | `00000000ffffffff` | `ffffffffffffffff` | `1122334455667788` |
| `12345678` | `0000000012345678` | `0000000012345678` | `0000000012345678` | `1122334455667788` |

## Source and artifact pins

The pinned [PCSX2 interpreter source](https://github.com/PCSX2/pcsx2/blob/9056c0834/pcsx2/R5900OpcodeImpl.cpp#L592-L623) was fetched as `PCSX2-R5900OpcodeImpl-9056c0834.cpp`, SHA-256 `6ae749a7e3a297a291f1844d2f96a17bf7c53a9c6f6f4ab4ddab27781a78c2b4`. The E56-fold source TOML was copied to `ssx3-e54d.toml`; its function map and codegen output paths point into the E54D worktree/output. The sole regeneration completed successfully with the new `build-baseline/ps2xRecomp/ps2_recomp`.

All two-read SHA-256 pairs match and are recorded in `input-sha.txt` and `gate-sha.txt`. The generated register file hash matches the prior canonical E56 file because the LWU change affects function bodies, not registration. Frame hashes identify only these artifacts: SC `43ff22a5f005e629a22ea6d8196dc8f79245ea3587713ccd6955e5905e0a65f3`; race early `65c382a6edf0124eeb064702a35bf3e474aa2134777fd94ec958dc6e04f383af`; race late `b43c46df6384c3a73534da48964e55757ac71e24a1a600002a55dcf121c2bdcd`. No fixed-tick cross-run hash comparison was made.

## Exact commands

Run `git ls-remote` and `git worktree add` from `~/dev/PS2Recomp`; build, suite, and fork Git commands from `~/dev/ssx3-work/E54D/PS2Recomp`; regeneration and boot from `~/dev/ssx3-work/E54D` (all TOML paths are absolute):

```sh
git ls-remote fork refs/heads/ssx3
git worktree add ~/dev/ssx3-work/E54D/PS2Recomp -b e54-lwu 89bec9b7f732f3938c89227927e1531d6fd4c346
zsh ~/dev/ssx3-work/E54D/build.sh baseline
../build-baseline/ps2xTest/ps2x_tests > ../suite-baseline.log 2>&1  # expected LWU pre-fix failure
cmake --build ~/dev/ssx3-work/E54D/build-baseline --parallel 8 --target ps2_recomp
~/dev/ssx3-work/E54D/build-baseline/ps2xRecomp/ps2_recomp ~/dev/ssx3-work/E54D/ssx3-e54d.toml > ~/dev/ssx3-work/E54D/regen.log 2>&1
zsh ~/dev/ssx3-work/E54D/build.sh off
../build/ps2xTest/ps2x_tests > ../suite-off.log 2>&1
zsh ~/dev/ssx3-work/E54D/build.sh on
../build-taps/ps2xTest/ps2x_tests > ../suite-on.log 2>&1
python3 ~/dev/ssx3-work/E54D/e54d_boot.py --label lwu-one --capture --target 2050 --wall 500
git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner
git commit -m '[E54D] Zero extend LWU loads' -m 'Emit a zero-extended 64-bit write for LWU and execute decoded load snippets against high-bit word values.' -m 'Orchestrated-By: Codex'
```

The initial baseline compile found a test-only macro call syntax error; one correction rebuilt the baseline suite, which then failed only the expected pre-fix LWU case. Both post-fix gate modes configured and built on the first attempt. No tuning loop or additional boot.

Gaps: The 92 static LWU guest addresses have unknown boot reach. This diagnostic boot does not provide a clean speed number. The known GS composite occlusion remains. No fork or ssx3 push.
