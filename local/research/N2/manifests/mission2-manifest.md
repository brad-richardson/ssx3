# N2 Mission 2 linkage manifest + APK identity (branch n2-android @695b96e)

Gate note: Mission 1 did not pass (stub link infeasible at the pin — see
`mission1-bars.md`). Mission 2 was attempted under a recorded gate
exception: its mechanism (drop the in-tree table + link all 9,455 C17
sources) is the direct remedy for the Mission-1 link failure, and every
toolchain risk Mission 1 was meant to retire was retired (clean compile of
all runtime sources + raylib under NDK clang). The orchestrator rules on
acceptance.

## Build

`./gradlew assembleRelease -Pps2xBootElf=.../SLUS_207.72
-Pps2xGameCodegenDir=/home/brad/n2/c17-codegen/codegen-output
--max-workers=4 --console=plain` → exit 0, BUILD SUCCESSFUL in 9 m 30 s,
50 tasks (35 executed), zero `error:` lines. Configure:
`-- PS2X: dropped 5 in-tree game sources`,
`-- PS2X: game objects: 9455 sources from …/codegen-output`,
plus the M1 configure lines.

## Delta reconciliation (N1's 9,441 / 9,455 / 9,457)

| Figure | Meaning | Receipt |
|---|---|---|
| 9,441 | distinct `sub_*` symbols (`^void sub_` in C17 set; `nm -g` game-shape `T` in `.so`, all distinct) | `logs/m2a-untar.txt` M2a7, `logs/m2c2-bars.txt` R1/R2 |
| 9,455 | `.cpp` files = 9,441 `sub_*` bodies + 13 named bodies (`sce*`, `_request_*`, `_alarm_*`, …) + `register_functions.cpp` | `logs/m2a-untar.txt` M2a5 |
| 9,457 | census entries = 9,455 `.cpp` + 2 headers | `logs/m2a-untar.txt` M2a3 |

C17 `register_functions.cpp` sha `564acae2…` == in-tree copy (identical
table); M1's 9,436 U + 5 T = 9,441 closes the loop from the stub side.

## Linkage manifest (arm64-v8a)

| Item | Value |
|---|---|
| Game unity objects | 296 (= ceil(9455/32)) |
| Runner unity objects | 1 (in-tree table + 5 bodies dropped) |
| `libps2_game_objects.a` | 1,743,665,830 B, 296 members |
| Game unity_0 includes | `codegen-output/register_functions.cpp` ✓ |
| Runner unity includes in-tree table | absent ✓ |
| Undefined `sub_*` (`nm -D U`) | 0 |
| Defined game-shape `sub_*` (`nm -g T`, distinct) | 9,441 / 9,441 |
| `nm -g ' T .*sub_'` raw count | 9,454 (+13 libc++ `__assoc_sub_state`, substring collision) |
| `ANativeActivity_onCreate` | `T` (statically linked from NDK glue; not an import) |
| `main` | `T` |
| Function-table symbols | `D g_ps2RecompiledFunctionTable`, `R …Base/…End/…SlotCount` |
| `without FFmpeg` string | `[MPEG] runtime built without FFmpeg; MPEG video decode is disabled.` |
| `ps2x` tag string | present |
| Boot path string | `/storage/emulated/0/Android/data/com.ps2x.runner/files/SLUS_207.72` |

Section sizes (unstripped arm64 `.so`, `size -A`):
`.text` 112,830,324, `.rodata` 1,459,264, `.data` 6,706,408,
`.bss` 8,195,880, `.rela.dyn` 9,722,328, `.eh_frame` 1,523,324,
`.debug_*` ~760 MB (RelWithDebInfo), Total 907,467,072.
`size -B`: text 127344066 data 6778888 bss 8197112 (identical stripped).

## APK identity

| Artifact | Bytes | sha256 |
|---|---|---|
| arm64 `.so` unstripped (`intermediates/cxx/…/obj/arm64-v8a/`) | 905,280,184 | `ac8292325e411482ef461216a5521950b0575e994de2bad1551d1ddc6a962fc5` |
| arm64 `.so` stripped (in-APK) | 134,125,832 | `3d69a414329534e848fe90235617923e825070de32192405da0a449d68f887d1` |
| x86_64 `.so` unstripped | 757,742,728 | (path receipted; sha not taken) |
| x86_64 `.so` stripped (in-APK) | 136,800,168 | (path receipted; sha not taken) |
| `app-release.apk` | 270,957,997 | `21a9230c20eaae1e833849e2042d159bcf4b83ff55063cdeb2ef28b1b323131f` |

`file`: arm64 `.so` = `ELF 64-bit LSB shared object, ARM aarch64`
(BuildID `3fa222ee…` both variants); APK = `Android package (APK)`.
APK members: `lib/arm64-v8a/libps2EntryRunner.so`,
`lib/x86_64/libps2EntryRunner.so`, `AndroidManifest.xml`, `classes.dex`,
`resources.arsc`, metadata. APK sha verified on bytesize build tree,
bytesize stage, and Mac SSD ×2 reads. NOT installed (per brief).

Size note: N1's B4 stub budget (`.so` ≤ 80 MB, APK ≤ 100 MB) cannot apply
to a full-title link; actuals (134 MB stripped arm64, 271 MB dual-ABI APK)
are in the expected host/iOS full-link range. No budget verdict is offered.
