# N8D7M1 — isolated Android independent-oracle package

Worker receipt. Source/package gate only. **No Odin install/launch, app run,
game boot, replay, iOS, upstream contact or push.** Package contents are
proved; device behavior stays unobserved, so no GS/device-cause verdict
follows. The N8D7L Mac oracle matched G43 input 448/448 on the pinned Mac
stream; this brief only packages that default-OFF oracle for a later
same-run Odin 448-tile test.

Goal: one arm64 APK carrying the Mac-validated default-OFF
`PS2X_N8D7L_ORACLE` probe (on the N8D7F selected-capture path), so a later
single Odin run can compare the independent fork-table census with G43's
selected-input vector and emit the eight literal controls.

## 1. Evidence table

| Item | Value |
| --- | --- |
| WSL root | `/home/brad/n8d7m1` (new); baseline `/home/brad/n8d7h` |
| Mac worktree | `~/dev/ssx3-work/N8D7L/PS2Recomp`, rev `d1ba1d49c6624417c49f6bbb3300b2ebf586231e` |
| Overlay | fork backend only, +138 lines / 0 deletions (`one-file-source.diff`) |
| Overlay source SHA (Mac, 2 reads) | `84a13a80686be8d4ed17750a9399d298ea6b998b98f48d3720b6b5bc839a4645` |
| Header `ps2_gs_psmct32.h` (Mac + N8D7H + N8D7M1) | `9635a40e11bae56189b64d1d9660fb68d0375444d355db43246973adb95e71f7` |
| N8D7H backend (pre-overlay) | `c6135b3ce986504ada7826a56f7a3d411a76690f9ca7dd80d918a3666d4fb41f` (= N8D7F) |
| Prebuild source diff vs N8D7H | `{fork:[backend], parallel:[], jniLibs:[]}` PASS (`source-gate.json`) |
| Postbuild source diff vs N8D7H | identical PASS (`source-gate-postbuild.json`), root 7,451,411,930 B |
| Oracle fence check | compiled under `PS2X_HAS_PARALLEL_SHADOW`, no test-only/Mac-only fence (`oracle-guard.txt`) |
| Build | one `assembleRelease`, `BUILD SUCCESSFUL in 5m 31s`, 48 tasks, no repair (`build-tail.txt`) |
| APK, WSL (2 reads) | `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1`, 153,736,732 B |
| APK, Mac (2 reads) | `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1`, 153,736,732 B |
| arm64 runner | `f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf`, 139,497,400 B |
| arm64 Turnip | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d`, 14,188,488 B (pin unchanged) |
| arm64 HAL shim | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387`, 7,112 B (pin unchanged) |
| Runner Build ID | `73291620f0c62fdc01ac0b603e9e5cca3114d0a5` (new; N8D7H was `1c1bce61bfe6bc21cd2ac86d473da323f480eb7b`) |
| Mac runner guard | `git diff --stat 14b1e5cb -- ps2xRuntime/src/runner` empty (`mac-fork-guard.txt`) |
| Caps | WSL root 6.94 GiB (<10 GiB); Mac `N8D7M1` 160 MiB (<500 MiB); receipts 68 KiB (<8 MiB); global 144.6/200 GB |

## 2. Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M1/preflight.sh > local/research/N8D7M1/preflight.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M1/prepare.sh  > local/research/N8D7M1/prepare.txt  2>&1
# overlay the one fork backend (Mac -> WSL)
ssh bytesize 'wsl -d Ubuntu -- bash -c "cat > /home/brad/n8d7m1/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"' \
  < /Users/brad/dev/ssx3-work/N8D7L/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M1/source_gate.py > local/research/N8D7M1/source-gate.json 2> local/research/N8D7M1/source-gate.err
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D7M1/build.sh > local/research/N8D7M1/build.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M1/source_gate.py > local/research/N8D7M1/source-gate-postbuild.json 2> local/research/N8D7M1/source-gate-postbuild.err
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D7M1/apk_gate.py > local/research/N8D7M1/apk-gate.json 2> local/research/N8D7M1/apk-gate.err
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d7m1/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > /Users/brad/dev/ssx3-work/N8D7M1/app-release.apk
python3 local/research/N8D7M1/mac_apk_gate.py > local/research/N8D7M1/mac-apk-gate.json 2> local/research/N8D7M1/mac-apk-gate.err
```

`build.sh` is N8D7H's command with root `n8d7m1`, preserving the exact
codegen (`/home/brad/n8b1/codegen-ssx3`), Turnip/HAL (`-Pps2xJniLibsDir`),
Gradle (`--max-workers=4`) and five OFF defaults (DIAG_TAPS, RUNTIME_LOGS,
AGRESSIVE_LOGS, IOP_RPC_TRACE, DEBUG_UI).

## 3. One-file source diff (vs N8D7H = N8D7F backend)

```
 ps2_gs_parallel_backend.cpp |  138 ++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 138 insertions(+)
```

The pre-overlay tree copy proved **zero** noncache differences vs N8D7H
(`prepare.txt`: all three `diff -rq` empty, `PRE_CANDIDATE_DIFFS_EMPTY`), then
exactly one file was overlaid. The pre/post source gates recompute the whole
tree: `fork` differs only in `ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp`;
`parallel` (the three G43 selected/stage diagnostics) and `jniLibs` have **zero**
differences. Every overlay/header/codegen/Turnip/HAL pin was double-read
(`source-gate.json`, `source-gate-postbuild.json`, `mac-pins.txt`).

## 4. Package members and cache

| Artifact | Size (bytes) | SHA-256 (two reads each) | Status |
| --- | ---: | --- | --- |
| APK | 153,736,732 | `e077bef8a7ba8aab44f46c515f79fade1ae045cc337bf7285e7b652e739758a1` | PASS |
| arm64 runner | 139,497,400 | `f3de999acc9227b82a9d9fab6a4a0b5b7fb279e6205991c1b3022da781e3c1bf` | PASS |
| arm64 Turnip | 14,188,488 | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | PASS (pin unchanged) |
| arm64 HAL shim | 7,112 | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | PASS (pin unchanged) |

Exactly these three native members, no x86. Runner Build ID
`73291620f0c62fdc01ac0b603e9e5cca3114d0a5` is **new** (≠ N8D7H).

Required packaged strings all present: `PS2X_N8D7F_SELECTED_CAPTURE`,
`PS2X_N8D7L_ORACLE`, `[n8d7f]`, `[n8d7l]`, `vram_sha256=`, `input_sha256=`,
`circuit_sha256=`, `input_circuit_equal=`, `circuit_stage_equal=`,
`PS2X_N8D5_TILE_CAPTURE`, `circuit1`, `pre_deinterlace_merged`, `stage=final`,
`control=`, `sampled_summary`, `raw_summary`, `PNG write failed path=`,
`oracle_controls=`, `oracle_input_equal=`.

Sole arm64 CMake cache:
`/home/brad/n8d7m1/PS2Recomp/android/app/.cxx/RelWithDebInfo/25645y26/arm64-v8a/CMakeCache.txt`.
It records `PS2X_GS_SHADOW_PARALLEL=ON`, G43 source
`/home/brad/n8d7m1/parallel-gs`, external codegen
`/home/brad/n8b1/codegen-ssx3`, and `PS2X_ENABLE_DIAG_TAPS`,
`PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`,
`PS2X_ENABLE_IOP_RPC_TRACE`, `PS2X_ENABLE_DEBUG_UI` all **OFF**.

## 5. Android oracle-path check (no device)

`oracle-guard.txt` records every preprocessor directive of the overlaid
backend. `oracleDecodeCensus`, `kOracleControls` and the invocation are inside
`#ifdef PS2X_HAS_PARALLEL_SHADOW` blocks (42–223 and 286–1025); the only
`__APPLE__` fence (49–61) selects the `selectedSha256` implementation and does
not gate the oracle. `PS2X_HAS_PARALLEL_SHADOW` is defined by Android's
`-Pps2xGsShadowParallel=ON` (cache confirms ON). The N8D7F selected-capture path
that invokes the oracle is likewise under that guard. No test-only or Mac-only
preprocessor fence gates the N8D7L oracle.

## 6. Build tail

```
> Task :app:mergeReleaseNativeDebugMetadata
> Task :app:assembleRelease

BUILD SUCCESSFUL in 5m 31s
48 actionable tasks: 48 executed
```

## 7. Caps

WSL root `/home/brad/n8d7m1` 7,451,411,930 B (6.94 GiB < 10 GiB). Mac scratch
`~/dev/ssx3-work/N8D7M1` 160 MiB (<500 MiB; APK 146.6 MiB). Receipt dir 68 KiB
(<8 MiB). Global mini ssx3 internal usage 144.6/200 GB before and after.
bytesize preflight `HEAVY_JOBS []`, `/dev/sdc` 764 G free.

## 8. Gaps

- The APK remains outside Git at
  `/home/brad/n8d7m1/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk`
  and `/Users/brad/dev/ssx3-work/N8D7M1/app-release.apk`. Its runner SHA/Build
  ID are new and were not compared to any device artifact.
- The oracle-path check is source/preprocessor inspection only; it does not run
  the Android oracle. No Odin install/launch, app run, game boot, replay, push,
  or device-cause verdict. Package contents are proved; device behavior is
  unobserved.
- The static N8D7L fixture and Mac replay are inputs here, not re-run; no
  Odin/Mac stream equality is claimed.

## 9. Receipts

`preflight.sh`/`preflight.txt`, `prepare.sh`/`prepare.txt`,
`source_gate.py`/`source-gate.json`/`source-gate.err`,
`source-gate-postbuild.json`/`source-gate-postbuild.err`,
`build.sh`/`build.txt`/`build-tail.txt`, `apk_gate.py`/`apk-gate.json`/`apk-gate.err`,
`mac_apk_gate.py`/`mac-apk-gate.json`/`mac-apk-gate.err`, `mac-fork-guard.txt`,
`mac-pins.txt`, `oracle-guard.txt`, `one-file-source.diff`.
