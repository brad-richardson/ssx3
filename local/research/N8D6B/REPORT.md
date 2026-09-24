# N8D6B — Android stage probe source and package gate

Worker receipt. Build/package scope only. No Odin or app run.

## Source gate

| Check | Required | Observed |
| --- | --- | --- |
| N8D5F snapshot | Fresh copy, build caches and runner excluded | PASS; 379 MiB initial, [prepare.txt](prepare.txt) |
| Fork backend | Only backend differs; SHA `e730b9f05994c9887f9c5605f9a34b2fe6f4ac1c239bb964f17cdfc515b1fb5c` | PASS; two reads, [source-gate.json](source-gate.json) |
| G43 patch | Exactly three named files; normalized hunks match `g43-stage.patch` | PASS; zero-fuzz apply and reverse dry run, [patch-context.json](patch-context.json) |
| Other inputs | PNG writer, shader header, Turnip, HAL, codegen and all other files unchanged | PASS; full-tree comparison and double pins, [source-gate.json](source-gate.json) |
| Mac fork runner guard | Diff from `14b1e5cb` empty | PASS; `git diff --stat` gave empty output |

## Build gate

| Check | Required | Observed |
| --- | --- | --- |
| Host jobs | No other heavy bytesize job | PASS; [preflight.sh](preflight.sh) printed `HEAVY_JOBS []` |
| Build | One arm64 `assembleRelease`, specified OFF flags | PASS; `BUILD SUCCESSFUL in 5m 31s`, 48 tasks, no retry; [build-tail.txt](build-tail.txt) |
| Postbuild source isolation | Same source gate passes | PASS; [source-gate-postbuild.json](source-gate-postbuild.json) |

## Package table

| Artifact | Size | SHA-256, two reads | Status |
| --- | ---: | --- | --- |
| APK, WSL | 153,720,348 bytes | `6839a0a48ed1b55affb6e6bd952a269ba3736200255bb6628270bb11a874a611` | PASS |
| APK, Mac | 153,720,348 bytes | `6839a0a48ed1b55affb6e6bd952a269ba3736200255bb6628270bb11a874a611` | PASS |
| arm64 runner | 139,486,520 bytes | `4e6c056dc48683ab725e16792748b83a122421d865f523d6d37c4bbb27fa0efd` | PASS |
| arm64 Turnip | 14,188,488 bytes | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` | PASS |
| arm64 HAL shim | 7,112 bytes | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` | PASS |

Every SHA in the table was read twice on WSL and twice on Mac where applicable; [WSL gate](apk-gate.json), [Mac gate](mac-apk-gate.json). The APK has exactly these three native members, with no x86.

Runner Build ID: `8d19e78d5e5eb7cb547be96b9ebb1a72b31a99f0`. Required packaged strings all present: `circuit1`, `pre_deinterlace_merged`, `stage=final`, `PS2X_N8D5_TILE_CAPTURE`, `control=`, `sampled_summary`, `raw_summary`, and `PNG write failed path=`. The sole arm64 CMake cache is `/home/brad/n8d6b/PS2Recomp/android/app/.cxx/RelWithDebInfo/4a2gj6c3/arm64-v8a/CMakeCache.txt`. It records shadow paraLLEl ON, source `/home/brad/n8d6b/parallel-gs`, external codegen `/home/brad/n8b1/codegen-ssx3`, and `PS2X_ENABLE_DIAG_TAPS`, `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE`, and `PS2X_ENABLE_DEBUG_UI` all OFF.

## Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D6B/preflight.sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D6B/prepare.sh > local/research/N8D6B/prepare.txt 2>&1
ssh bytesize 'wsl -d Ubuntu -- bash -c "cat > /home/brad/n8d6b/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp"' < /Users/brad/dev/ssx3-work/N8D6A/PS2Recomp/ps2xRuntime/src/lib/gs/ps2_gs_parallel_backend.cpp
ssh bytesize 'wsl -d Ubuntu -- bash -c "cat > /home/brad/n8d6b/g43-stage.patch"' < local/research/N8D6A/g43-stage.patch
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D6B/apply_stage.py > local/research/N8D6B/patch-context.json
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D6B/source_gate.py > local/research/N8D6B/source-gate.json
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D6B/build.sh
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D6B/source_gate.py > local/research/N8D6B/source-gate-postbuild.json
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D6B/apk_gate.py > local/research/N8D6B/apk-gate.json
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d6b/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > /Users/brad/dev/ssx3-work/N8D6B/app-release.apk
python3 local/research/N8D6B/mac_apk_gate.py > local/research/N8D6B/mac-apk-gate.json
```

The package commands will be appended after the build. The first draft of the source gate used the packaged HAL SHA as a source-file pin. The N8D5F and N8D6B source files both read `d7add7e8e2e31f3c49b83941c6686fa66ab3d844c650e8d70c93b026f90cafa0`; the corrected source gate passed. The packaged HAL SHA remains a separate package check.

## Gaps

The APK remains outside Git at `/home/brad/n8d6b/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk` and `/Users/brad/dev/ssx3-work/N8D6B/app-release.apk`. WSL scratch is 7,590,215,121 bytes (<10 GiB); Mac scratch is 160 MiB (<500 MiB); receipts are 60 KiB (<8 MiB); global mini ssx3 usage is 138.7/200 GB. No Odin install/launch, app run, game boot, push, or device/causal verdict. Package contents are proved; device behavior remains unobserved.
