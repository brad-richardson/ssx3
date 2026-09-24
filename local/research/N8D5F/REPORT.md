# N8D5F — PNG writer package gate

Worker receipt. Build and package only. No device or causal verdict.

## Gates recorded before build

| Gate | Required observation | Result |
| --- | --- | --- |
| Base and candidate | Fresh N8D5F snapshot from N8D5D; N8D3 `ps2_runtime.cpp` SHA `358d726bf39e319b906e7e15407e1bf361cd2cdbdd8e79d4a96b25a9588c3f96` twice before copy | PASS; [preflight.txt](preflight.txt), [prepare.txt](prepare.txt), [source-gate.json](source-gate.json) |
| Source isolation | Exactly backend and PNG writer differ from N8B1 in fork; named shader header addition; `jniLibs` unchanged | PASS; exactly those three differences in [source-gate.json](source-gate.json) |
| Writer hunk | Exactly the one hunk in N8D5E `orch-png-diff.txt` | PASS; the diff hunk SHA is `64b584851662ae0ddbdf003cca89057b07ac0f0640bcf22d60497865f44fa4ff`, matching the receipt after its two file-header lines |
| Backend and shader pins | `4e3efc51d8d104ab5d3c537076e85c6cfcd8344c8e6c147de02f5a5015c8f1e5` and `19b9ba5fc747d8fcb70d712b86bd5738c64424ceb15c24d4b5ed58219f71bac9`, two reads | PASS; [preflight.txt](preflight.txt), [source-gate.json](source-gate.json) |
| Build | One arm64 `assembleRelease` with N8D5D flags and private inputs | PASS; `BUILD SUCCESSFUL in 7m 47s`, 48 tasks, no repair retry; [build-tail.txt](build-tail.txt) |
| APK and members | Double SHA reads on WSL and Mac; exactly three arm64 members; Turnip and shim pins | PASS; [apk-gate.json](apk-gate.json), [mac-apk-gate.json](mac-apk-gate.json) |
| Runner | SHA, Build ID, five named strings, cache flags and source paths | PASS; Build ID `f01ab9e6c249f488717eab21f5f3c6cf43130190`; [apk-gate.json](apk-gate.json) |
| Mac fork guard | N8D5L runner-dir diff against `14b1e5cb` empty | PASS; fork at `ab8155bbcbbdd478d17f2cd90a2feff3eb9a865b`, diff empty in [mac-fork-guard.txt](mac-fork-guard.txt) |

## Package table

| Artifact | Size | SHA-256, two reads |
| --- | ---: | --- |
| APK, WSL and Mac | 153,720,348 bytes | `8c101c4824adbda8f2fa7126692791189e4d05df7e450680ff2b6e67d0be66a0` on both hosts |
| `lib/arm64-v8a/libps2EntryRunner.so` | 139,483,288 bytes | `d1916d7bce3cc789c3e25d8e90c4db9cd0d1bcbfb037d27d4b3a6b1932476456` on both hosts |
| `lib/arm64-v8a/libvulkan_freedreno.so` | 14,188,488 bytes | `717812c3c51fd2836931ec22b82d13e805d763ec425f86bafdfa92f54c1ac29d` on both hosts |
| `lib/arm64-v8a/libhardware.so` | 7,112 bytes | `1b49d27c839f25363237d8276c91a401602845ee8eef67de50d6540f4cdfc387` on both hosts |

## Bounds and commands

Prebuild: WSL snapshot 379 MiB (345,753,589 bytes after candidate); `codegen-ssx3/register_functions.cpp` pinned `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`, double read. No bytesize Gradle, Ninja, clang, or PCSX2 job at preflight. Mini global disk usage 136.0 GB / 200 GB cap. The first draft of `source_gate.py` had a mistyped expected shader SHA; the actual file SHA matched the brief, and the corrected gate passed before build.

The private snapshot was copied from `/home/brad/n8d5d/` without `.cxx`, `build`, `.gradle`, or `ps2xRuntime/src/runner/`; the paraLLEl snapshot excluded build caches. N8D5D `jniLibs` copied unchanged. The only candidate replacement was N8D3 `ps2_runtime.cpp`, after two source SHA reads. Its destination SHA was also read twice. The writer diff against N8B1 is one hunk, byte-matched to N8D5E's `orch-png-diff.txt` after its file-header lines. [source-gate-postbuild.json](source-gate-postbuild.json) rechecked source isolation after the build.

The one build used [build.sh](build.sh) with JDK 17 and N8B1 `mem_governor.sh`. It passed `-Pps2xGsShadowParallel=ON`, private `/home/brad/n8d5f/parallel-gs` and `/home/brad/n8d5f/jniLibs`, and external `/home/brad/n8b1/codegen-ssx3`. The sole arm64 `RelWithDebInfo` cache is `/home/brad/n8d5f/PS2Recomp/android/app/.cxx/RelWithDebInfo/3m5x3418/arm64-v8a/CMakeCache.txt`. It records shadow paraLLEl `ON`; diagnostic taps, runtime logs, aggressive logs, IOP RPC trace and debug UI `OFF`; and the expected private paraLLEl and external codegen paths. The package has no x86 member. The runner contains `PS2X_N8D5_TILE_CAPTURE`, `control=`, `sampled_summary`, `raw_summary`, and `PNG write failed path=`.

The APK remains outside Git at `/home/brad/n8d5f/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk` and `/Users/brad/dev/ssx3-work/N8D5F/app-release.apk`. WSL scratch is 7.2 GiB (<10 GiB); Mac scratch 147 MiB (<500 MiB); committed text receipts about 31 KiB (<8 MiB); mini ssx3 usage 136.1 GB (<200 GB). No Odin install or launch, bytesize game/emulator boot, or push occurred. Package gates establish build contents only; the PNG behavior on a device remains untested by this brief.

## Exact commands

```sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5F/preflight.sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5F/prepare.sh
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5F/copy_writer.sh
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D5F/source_gate.py > local/research/N8D5F/source-gate.json
ssh bytesize 'wsl -d Ubuntu -- bash -s' < local/research/N8D5F/build.sh
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D5F/source_gate.py > local/research/N8D5F/source-gate-postbuild.json
ssh bytesize 'wsl -d Ubuntu -- python3 -' < local/research/N8D5F/apk_gate.py > local/research/N8D5F/apk-gate.json
ssh bytesize 'wsl -d Ubuntu -- cat /home/brad/n8d5f/PS2Recomp/android/app/build/outputs/apk/release/app-release.apk' > /Users/brad/dev/ssx3-work/N8D5F/app-release.apk
shasum -a 256 /Users/brad/dev/ssx3-work/N8D5F/app-release.apk /Users/brad/dev/ssx3-work/N8D5F/app-release.apk
python3 local/research/N8D5F/mac_apk_gate.py > local/research/N8D5F/mac-apk-gate.json
```
