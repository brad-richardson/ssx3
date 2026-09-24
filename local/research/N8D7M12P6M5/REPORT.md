# N8D7M12 Part 6M5 — clean staged source inputs for next package (worker receipt)

Worker receipt. Owns only ignored `local/research/N8D7M12P6M5/` (stage,
checker, private manifest, receipts). Brief:
`local/muse/prompts/N8D7M12P6M5.md`. Prior:
`local/research/N8D7M12P6M4/{REPORT.md,ORCH-GATE.md}`, P6M1 inventory,
P3 `build.sh` + `source-gate.json` + `apk-gate.json`. No board/ledger,
fork, renderer, codegen, collector or config edit. No build, network/ssh,
device/emulator, lease, package or push. No subagents.

Goal: a clean, reproducible source-byte staging root for the next Android
package. Hypothesis: P6M4's real-fork probe includes untracked receipts
while P3 lacked compiled-input pins; a clean export plus an all-root
manifest distinguishes exact next-package input bytes from historical
old-APK guesses. Correct model: only bytes in the staged roots can be
claimed for the next build; no claim that the old APK used them.

## 1. Source pins (independently re-read, all match)

| Input | Pin | Re-read |
| --- | --- | --- |
| Fork `/Users/brad/dev/ssx3-work/N8D7M12P5F4/PS2Recomp` HEAD | `4fa0df1` | `4fa0df1811df4381aa3ba95aa3fcd1310afd1d25` |
| Fork tracked mods | none | status `?? local/` only |
| Fork runner diff vs `14b1e5cb` | empty | `git diff --stat` empty; `ls-tree` names only blob `85cc2e348d60cfae0a4f220fc2a0535f7a756fa2` |
| Renderer file `gs_renderer.cpp` | `85c29cb0…3de77e` | `85c29cb01b04c8fefdf4fffba8dbbd953293c9de682d0443437e0b91de3de77e` |
| Interface file `gs_interface.hpp` | `3a1751b4…05954d9d` | `3a1751b4a708a56827af3e97ef32034349311d0c7fa2f59e4691700f05954d9d` |
| Codegen `register_functions.cpp` | `8ea8ed43…662d688a3` | same full SHA in stage + manifest |
| Turnip source `G43/inputs/libvulkan_freedreno.so` | `717812c3…54c1ac29d` | two reads agree, staged copy agrees |
| HAL packaged member `lib/arm64-v8a/libhardware.so` from `N8D7M12P3/app-release.apk` | `1b49d27c…cdfc387`, 7,112 B | two APK reads agree, staged extract agrees |

Renderer checkout `N8D7F/parallel-gs` is dirty (G-lane patch stack:
`gs_interface.cpp`, `gs_renderer.cpp/.hpp`, `gs_interface.hpp`,
`tools/*`, modified `Granite` submodule + untracked `n8d5_tile.comp/.spv`
and `n8d5_tile_spirv.hpp`); all of it is staged deliberately as the exact
next-package input. The historical HAL *source* (`d7add7e8…`) is unproved
and is NOT staged; the known packaged member starts the new baseline.

## 2. Input → stage method and SHA proof

Stage root: `local/research/N8D7M12P6M5/stage/` (ignored, 645 MiB total,
≤1 GiB cap; project total 157.5/200 GB after, `disk_budget.sh` RC=0 both
ends).

| Root | Method | Proof |
| --- | --- | --- |
| `stage/PS2Recomp` | `git -C <fork> archive HEAD \| tar -x -C stage/PS2Recomp` (no `.git`, untracked `local/receipts` absent by construction) | `local/` absent, `.git` absent, runner dir holds only `register_functions.cpp` 438 B `cf62c485…f068` |
| `stage/parallel-gs` | `rsync -a --exclude=.git --exclude=build --exclude=.cxx --exclude=.gradle --exclude=__pycache__ <N8D7F/parallel-gs>/ stage/parallel-gs/` (dirty + untracked shader sources kept, incl. Granite) | `rsync --checksum --dry-run` with identical exclusions: empty (byte-identical); staged `gs_renderer.cpp`/`gs_interface.hpp` SHAs equal pins |
| `stage/codegen-ssx3` | same rsync form from `/Users/brad/dev/ssx3-work/codegen-ssx3/` | dry-run empty; staged `register_functions.cpp` SHA `8ea8ed43…` equals P3 pin |
| `stage/jniLibs/arm64-v8a/` | Turnip `cp` from pinned source; HAL `zipfile.read('lib/arm64-v8a/libhardware.so')` from pinned APK | source double-read, APK double-read and staged SHAs all agree (`717812c3…`, `1b49d27c…`); scope holds exactly the two members |

## 3. Manifest snapshot + verify (explicit `--max-files 30000 --max-bytes 2000000000`)

```sh
python3 local/tooling/orch/source_manifest.py snapshot --fork local/research/N8D7M12P6M5/stage/PS2Recomp --parallel local/research/N8D7M12P6M5/stage/parallel-gs --codegen local/research/N8D7M12P6M5/stage/codegen-ssx3 --jni local/research/N8D7M12P6M5/stage/jniLibs --out local/research/N8D7M12P6M5/source-manifest.json --max-files 30000 --max-bytes 2000000000
python3 local/tooling/orch/source_manifest.py verify --manifest local/research/N8D7M12P6M5/source-manifest.json --fork <same four roots> --max-files 30000 --max-bytes 2000000000
```

Snapshot `status: ok`, verify `status: match` (added/missing/changed all
empty), aggregate `6877de873b197bf915d068d1b03331e6488c529e6bdac64273513f338080316a`
both runs. Manifest stays ignored/private; only the aggregate, counts,
mapping, exclusions and checker receipt are committed here.

| Scope → staged root | Files | Bytes |
| --- | --- | --- |
| fork → `stage/PS2Recomp` | 323 | 22,310,491 |
| parallel → `stage/parallel-gs` | 16,429 | 309,239,028 |
| codegen → `stage/codegen-ssx3` | 9,457 | 266,831,289 |
| jni → `stage/jniLibs` | 2 | 14,195,600 |
| total | 26,211 / 30,000 cap | 612,576,408 / 2,000,000,000 cap |

Fork file count (323) is 13 below the P6M4 live-probe count (336): the
untracked `local/receipts` (~336 KiB) are absent from the export, as
designed. Exclusions: zero skips in every scope (no `.git`/`build`/`.cxx`/
`.gradle`/`__pycache__` components reached the stage). Runner entries in
manifest: exactly one —
`fork:ps2xRuntime/src/runner/register_functions.cpp`, file, 438 B,
`cf62c485…f068`. No `local/receipts` entries. Required entries confirmed
present: fork frontend/worker/backend (`gs_frontend.cpp` `3f408c8396a0`,
`gs_worker.cpp` `3300f41deae9`, backend `84a13a80686b` = P3 oracle pin,
`main.cpp` `7ab53178547e` = P3 pin), parallel `gs_interface.cpp`
(`5ccc962f080b`, 201,434 B), `page_tracker.cpp`, `n8d5_tile_spirv.hpp`
(`19b9ba5f…` = P3 pin), `gs/shaders/n8d5_tile.comp/.spv`,
`Granite/vulkan/memory_allocator.cpp`, codegen `register_functions.cpp`
(`8ea8ed43…`, 32,744,715 B = P3 pin), both JNI members.

## 4. Checker (`check.py`, 24/24, verdict A)

```sh
python3 local/research/N8D7M12P6M5/check.py   # re-verifies pins, parity, manifest verify; writes check-result.json
```

Rows: 4 fork-pin rows, 4 stage-export rows, 5 parity-vs-pin rows, 3 HAL/JNI
rows, 8 manifest rows (aggregate, caps, exact counts, required paths,
runner-stub-only, no receipts, pinned SHAs, CLI verify match). 24 pass,
0 failing.

## 5. Receipts

- `local/research/N8D7M12P6M5/{REPORT.md,check.py,check-result.json}`
  (committed with `git add -f`, `[N8D7M12] Part 6M5` /
  `Orchestrated-By: opencode`; no push).
- Private/ignored: `stage/` (645 MiB), `source-manifest.json`. Not in git;
  no game/codegen/APK/binary bytes committed.
- Base commit `8e3d4b80` (`[orch] Queue clean Android source staging`).

## 6. Gaps (hand-back, no package/GPU verdict)

1. The source manifest pins input bytes only; it does not prove what
   compiled. The package worker must still capture CMake/Gradle flags,
   the build-system file list, native-member SHA/Build ID and APK SHA.
2. HAL staged baseline is the packaged member (`1b49d27c…`); the
   source→member transform from the historical `d7add7e8…` source remains
   unexplained (carried P6M1 gap H2).
3. Staged renderer is the dirty G-lane patch stack, not upstream-clean;
   its exact dirty patch set is pinned by hash here but not reviewed for
   correctness in this part.
4. No claim is made that the old `caa11102…` APK used these bytes; equal
   pins (renderer, interface, shader header, codegen register, Turnip)
   are byte-equality observations against P3 receipts, not provenance.
5. `check.py` parity covers pinned files by SHA; full-tree parity rests on
   the empty `rsync --checksum --dry-run` outputs (recorded, not
   re-executed by the checker) plus manifest `verify: match`.
