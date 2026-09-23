# G45 report — fix-only `ssx3` branches for the paraLLEl-GS and Granite forks

## 0. Outcome first

Both `ssx3` branches exist as local commits in fresh offline clones under
`~/dev/ssx3-work/G45/parallel-gs` (Granite nested inside), holding **only**
the Brad-approved keep list: G26, G28, the env-gated Turnip HAL loader
(G42 + G43 layout fix), and build shims. Proof: `ssx3` vs `wip/ssx3-snapshot`
differs exclusively by the tabled diagnostics (§2), and the Mac F0 shape on
the G13 dump reproduces G43's 10 scanout SHAs **10/10** (§4). Android
(NDK r30) compiles `[458/458]` (§5). Nothing pushed; push commands for the
orchestrator in §6. `~/dev/parallel-gs` and `~/dev/ssx3-work/G43` untouched.

No hunk met the stop rule: every hunk's class is unambiguous (in-code
`G<num>` tags + committed per-brief diffs). Two judgment calls, both
disclosed: (a) the G43 pointer/`.so`-range LOGI lines ride in the loader
commit — they execute only when `PGS_G42_TURNIP` is set (§2, row L3);
(b) the F0 proof run used an **uncommitted** save-only overlay
(`proof-overlay.diff`, removed afterwards, trees verified clean) because
upstream saves no scanouts — §4.

## 1. Pins, clones, commits

- Fresh clone: `git clone ~/dev/parallel-gs ~/dev/ssx3-work/G45/parallel-gs`
  (local, no network); `git checkout -b ssx3 3a66c19`.
- Granite: submodule URL overridden to `/Users/brad/dev/parallel-gs/Granite`,
  `submodule update --init` → `16e7395f`, `checkout -b ssx3`; 18 nested
  `third_party` submodules initialized from
  `/Users/brad/dev/parallel-gs/Granite/<path>` at the recorded gitlinks
  (18/18 `submodule status` clean, no `-` prefix).
- `git -c user.name='Muse Code'` commits (no identity configured on the mini).

paraLLEl-GS `ssx3` (from `3a66c19`):

| # | SHA | subject |
| --- | --- | --- |
| 1 | `0e538d84614e95eae137f23073a87725605df45a` | G26: deliver only disable_sampler_feedback, drop G24 ride-along |
| 2 | `c815d1b3d3a63c819a56401ae04e0b6e5d45f9be` | Turnip HAL loader (env-gated, default off) + reserved-block layout fix |
| 3 | `1ecc801d472b3609ca22a1609595e453ddad6482` | Build shims (local, not upstream) + Granite gitlink to ssx3 head |

Granite `ssx3` (from `16e7395f`):

| # | SHA | subject |
| --- | --- | --- |
| 1 | `be8bea900e1e04adbaa86759f30600dc5b287b6a` | G28: guard descriptorBuffer branch on supports_descriptor_buffer_or_heap |
| 2 | `8e07c361cd13c38d2f2c44d290214a0ba6d5e94b` | Build shims (local, not upstream): Android null platform + macOS timer |

`ssx3` head gitlink: `160000 commit 8e07c361cd13c38d2f2c44d290214a0ba6d5e94b`.
No binaries, dumps, or generated files committed (source-only; `git status`
clean in both repos after the proof run).

## 2. Hunk table (snapshot + G43 hunk vs upstream pins)

Ground truth: `git diff 3a66c19 faf6400` (main, 1451+/5-) and
`git diff 16e7395f aaeee97` (Granite, 57+/3-) in `~/dev/parallel-gs`, plus
`local/research/G43/g43-hunk.diff`. New-file line numbers are vs `faf6400`.

paraLLEl-GS main tree:

| file:lines | introducing brief | class | disposition + evidence |
| --- | --- | --- | --- |
| `CMakeLists.txt` ~50–62 | G14 | BUILD-SHIM | KEPT (commit 3). `g14-shims.diff` S1; G14 REPORT |
| `tools/CMakeLists.txt` ~8–13 | G14 | BUILD-SHIM | KEPT (commit 3). `g14-shims.diff` S3 (liblog link) |
| `tools/gs_dump_replayer.cpp` ~14–24 | G42 | LOADER (includes incl. `<dlfcn.h>`) | KEPT (commit 2). `g42-loader.diff` @@ -14 |
| `tools/gs_dump_replayer.cpp` ~37–122 | G42 | LOADER (HMI structs + `g42_init_loader`, default system) | KEPT (commit 2). G42 REPORT + CHECKPOINT (one-symbol HMI decode) |
| `tools/gs_dump_replayer.cpp` ~157–163 | G42 | LOADER (`init_loader` call swap) | KEPT (commit 2) |
| `tools/gs_dump_replayer.cpp` ~177–191 | G26 | FIX (flag-only delivery, ride-along removed) | KEPT (commit 1). `g26-narrowing.diff`; G39 §2b D-G26-1..4 |
| `tools/gs_dump_replayer.cpp` ~197–435 | G8/G10/G29/G30 | DIAGNOSTIC (save fn + G29 ladder + loop series + G30 vpage) | wip only. G8/G10 dirs; `g29-ladder.diff`; `g30-content.diff` |
| `tools/gs_dump_replayer.cpp` ~456–478 | G10 | DIAGNOSTIC (tail series emission) | wip only. `g10-hook.py`, G10 REPORT |
| `tools/gs_dump_replayer.cpp` G43 hunk | G43 | FIX (reserved[12] + 4 static_asserts) + LOADER-path logging (maps + 4-pointer line, Turnip path only) | KEPT (commit 2). G43 REPORT §3 |
| `gs/gs_interface.cpp` ~12–117 | G40/G41 | DIAGNOSTIC (wall + canary statics) | wip only. `g40-wall-apply.py`; `g41-canary-apply.py` |
| `gs/gs_interface.cpp` ~234–342 | G40/G41 | DIAGNOSTIC (flush entry, census LOGI) | wip only, same source |
| `gs/gs_interface.cpp` ~506–524 | G11 | DIAGNOSTIC (G11b record hook) | wip only. `local/research/G11/` (g11-hook2.py) |
| `gs/gs_interface.cpp` ~572–1178 | G40/G41 | DIAGNOSTIC (wall end O1/O5/O4m/O2/O3/O3b/O4 + canary body) | wip only, same source |
| `gs/gs_interface.cpp` texture-path ×2, kick ×3, prim ×1 | G40/G41 | DIAGNOSTIC (O4m/O1 counters, kick-time snap) | wip only, same source |
| `gs/gs_interface.cpp` FRAME_1/2, flush() | G11 | DIAGNOSTIC (draw-target + census LOGI) | wip only. G11 REPORT |
| `gs/gs_interface.cpp` vsync() | G31 | DIAGNOSTIC (state + A/B bytes probe) | wip only. `g31-state.diff` |
| `gs/gs_renderer.cpp` ~1591–1706 + hpp | G40 | DIAGNOSTIC (probe record/finish + staging members) | wip only. `g40-wall-apply.py` |
| `gs/gs_renderer.cpp` ~3606–3620 | G22 | DIAGNOSTIC (env-gated sampler-feedback skip; superseded by G26 flag path, not in keep list) | wip only. `g22-workaround.diff`; G39 §2a HUNK_MATCH |

Granite:

| file:lines | introducing brief | class | disposition + evidence |
| --- | --- | --- | --- |
| `application/platforms/CMakeLists.txt` ~1–8 | G14 | BUILD-SHIM (null/headless guard) | KEPT (Granite commit 2). `g14-shims.diff` S2 |
| `util/timer.cpp` ~141–151 | G7 | BUILD-SHIM (Apple nanosleep fallback) | KEPT (Granite commit 2). G7 REPORT L28, L75–77 |
| `vulkan/command_buffer.cpp` ~1198–1215 | G20 | DIAGNOSTIC (pre-create LOGI) | wip only. `g20-capture.diff` |
| `vulkan/memory_allocator.cpp` ~1424–1430 + 1472–1482 | G28 | FIX (supports guard + once-only skip receipt) | KEPT (Granite commit 1). `g28-writer-fix.diff`; G39 §2b D-G28-1..5 |
| `vulkan/shader.cpp` ~531–537 | G18 | FIX but **excluded** (not in the approved keep list; no Mac-F0 effect — MoltenVK reports no descriptorBuffer feature, predicate takes the same arm either way) | wip only. `g18-fix.diff` |

No surviving G24 hunk (ride-along removed in place by G26; only comment
mentions remain). G25/G27 introduced no code hunks. Committed per-brief
diffs are blob-identical to the snapshot hunks (spot-checked indexes:
`980583d..46e9846`, `13b9dcb..77c2ea9`, `9f2534d..16599ce`,
`f272816..39c6a4b`; `g26-narrowing.diff` has wrong `@@` counts — content
applied by hand, 7+/1- verified line-equal).

Structural verification (after all commits, before builds):
`git diff ssx3 faf6400 -- . ':!Granite'` = only gs_interface/gs_renderer/
gs_renderer.hpp + replayer G8/G10/G29/G30 blocks; every snapshot-only `+`
marker ∈ {G11, G11b, G22, G29, G30, G31, G40, G41}; minus-side in `gs/`
empty. Granite `git diff ssx3 aaeee97` = G20 + G18 only. Kept files
(CMakeLists ×2, memory_allocator, timer, platforms) zero-diff vs snapshot.

## 3. Budgets

2 Mac builds (clean + proof-overlay), 1 Android build, ~1 h of 3 h.
`~/dev/ssx3-work/G45` 7.4 GB of 12 GB; all-ssx3 internal 26.6 GB of
200 GB (budget script exit 0) at start and end. No Odin run (per brief).
No device, no lease, no network (all clones/submodules from local paths).

## 4. F0 proof — 10/10 scanout SHAs equal G43's Mac run

- Clean build A: `VULKAN_SDK=/opt/homebrew cmake -S parallel-gs
  -B mac-build -G Ninja` (CONFIG 0) + `cmake --build mac-build --target
  parallel-gs-replayer -j8` (BUILD 0, `[457/458]`).
  Binary 51,868,168 B,
  `e6b37f279cfbdee06f588dc959561b0daabdf95336ea18da07a61b0249bffaf8`.
  G43 `static_assert`s compiled on Mac arm64 → LP64 offsets proven on
  both ABIs at compile time.
- Proof build B: same recipe in `mac-build-proof` with the uncommitted
  `proof-overlay.diff` applied (P1-only save, G10-style last-pass
  collection; rendering path untouched). Binary 51,882,136 B,
  `463ed36246d12a2b6b3e77b4a56f3640a5de7818e3b81a97058f6c165e0f5a7c`.
- F0 run (no wall envs, no Turnip env): `VK_ICD_FILENAMES=…/MoltenVK_icd.json
  DYLD_LIBRARY_PATH=/opt/homebrew/lib parallel-gs-replayer g13-dump.gs
  --iterations 2 --disable-sampler-feedback` on pinned dump
  `154d9d8577a210fb…` (matches `~/dev/ssx3-inputs/g13`). RUN_EXIT 0,
  `Done!`, 10 PPMs. First stderr lines: `(system)` loader + G26
  `(=1,=0,=0)` — identical shape to G43's.
- Overlay removed after the run: `git checkout --`, `git status` clean in
  both repos; `ssx3` SHAs unchanged (§1).

| scanout | G45 proof | G43 mac-run | verdict |
| --- | --- | --- | --- |
| g10-vsync0 | `99418f1b1a94ed9f` | `99418f1b1a94ed9f` | MATCH |
| g10-vsync1 | `7e9daa21a6a94377` | `7e9daa21a6a94377` | MATCH |
| g10-vsync2 | `5d4ff853e8315ce4` | `5d4ff853e8315ce4` | MATCH |
| g10-vsync3 | `11370e59558148a5` | `11370e59558148a5` | MATCH |
| g10-vsync4 | `6aa54f3b7e178902` | `6aa54f3b7e178902` | MATCH |
| g10-vsync5 | `6aa54f3b7e178902` | `6aa54f3b7e178902` | MATCH |
| g10-vsync6 | `bc5ca6de986aa39c` | `bc5ca6de986aa39c` | MATCH |
| g10-vsync7 | `bc5ca6de986aa39c` | `bc5ca6de986aa39c` | MATCH |
| g8-first | `99418f1b1a94ed9f` | `99418f1b1a94ed9f` | MATCH |
| g8-last | `bc5ca6de986aa39c` | `bc5ca6de986aa39c` | MATCH |

Values independently corroborate G42's documented Mac set (blank first,
`7e9daa21/5d4ff853/11370e59/6aa54f3b/bc5ca6de`). `PGS_SKIP_COMPILATION_TASKS`
was not needed. Receipts: `~/dev/ssx3-work/G45/mac-run/` (10 PPMs +
stdout/stderr); overlay text: `local/research/G45/proof-overlay.diff`.

## 5. Android build receipt (compile only, no Odin run)

`cmake -S parallel-gs -B android-build -G Ninja
-DCMAKE_TOOLCHAIN_FILE=/opt/homebrew/share/android-ndk/build/cmake/android.toolchain.cmake
-DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-35` (CONFIG 0) +
`cmake --build android-build --target parallel-gs-replayer -j8`
(BUILD 0, `[458/458]`). Binary 265,976,176 B,
`5a5552296bcb672829bdc9b95a181096a9306022a96ffb5c3cb17d3108df8504`.
`strings` census: `G28: create_image_view` ×1, `G26: debug_mode` ×1,
`G42: Vulkan loader` ×1, `G43: HAL dev` ×1; `G40:`/`G41:`/`G29: ladder`/
`G31: state` ×0.

## 6. Push commands for the orchestrator (NOT run)

Submodule `origin` is upstream Themaister — never push there. From
`~/dev/ssx3-work/G45/parallel-gs` (Granite nested at `Granite/`):

```sh
cd ~/dev/ssx3-work/G45/parallel-gs/Granite
git remote add fork https://github.com/brad-richardson/Granite.git
git push fork ssx3   # expect new-branch head be8bea90..8e07c361
cd ~/dev/ssx3-work/G45/parallel-gs
git remote add fork https://github.com/brad-richardson/parallel-gs.git
git push fork ssx3   # expect new-branch head 3a66c19..1ecc801 (gitlink -> 8e07c361)
```

Verify after push: fork `ssx3` logs match §1 SHAs; paraLLEl `ssx3` gitlink
resolves to the pushed Granite `ssx3` head.

## 7. Recommended next action

Push both `ssx3` branches (§6), then point the G44 Android/Odin build at
the fork `ssx3` heads instead of the G43 working copy + carried diffs.
Suggested follow-up brief: G44 rebuild from pushed `ssx3` + Odin
F0-shape run to confirm on-device fate (exit 0, `Done!`) is unchanged
minus diagnostics.
