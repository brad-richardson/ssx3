# G44 report — paraLLEl-GS in shadow mode inside the recomp (Mac, MoltenVK)

## 0. Outcome first

The shadow path builds, inits, and renders in-process, but produced **0 PNG
pairs** across both boots: the game's menu-time SMODE1 (`CMOD=0/LC=0` with
`SMODE2.INT=1`) matches none of paraLLEl scanout's mode branches, so every
`vsync()` returns null (`Unknown video format`). Rendering itself proceeds
(G31 shows animated VRAM regions and a live display buffer at the same
`DISPFB1=112` the CPU presents). One candidate fix was tried (S2) with a
wrong LC assumption; the corrected condition is committed but
**UNVALIDATED** (no boot budget left). **Zoe question: not established** —
no paraLLEl frame was ever read back, so neither H1 (CPU backend fault) nor
H2 (upstream fault) is discriminated.

Recommended next action in §6.

## 1. Pins and receipts

- Fork branch `g44-parallel-shadow` in worktree
  `~/dev/ssx3-work/G44/PS2Recomp`, cut from `ssx3` @ `e57b5f8`; E33's
  `~/dev/PS2Recomp` checkout untouched (only worktree metadata added).
  Adapter commit `460e438` (single commit, §2 seam table; no push).
- paraLLEl/Granite sources: G43 internal working copy
  `~/dev/ssx3-work/G43/parallel-gs` (= `wip/ssx3-snapshot` + G43 hunk, which
  touches `tools/gs_dump_replayer.cpp` only — outside the linked `gs/` +
  `Granite/` trees), wired as a CMake subdirectory from the local path with
  `PARALLEL_GS_STANDALONE=ON`. No network fetch of GS sources (configure log
  `/tmp/g44-configure.log` shows only the fork's own raylib/imgui/rlimgui
  fetches, same HEADs as E32).
- G44 build `~/dev/ssx3-work/G44/build`: Release, ninja,
  `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (E32 recipe + shadow
  flags). One configure total.
- Runner SHAs: S1 binary `4e01e7f3…` (1 read, superseded); S2 binary
  `b8a694c5…` (1 read, superseded); final binary `25bd6450…` (2 matching
  reads, post-S2 LC-condition edit — **not booted**). Suite binary
  `8db3d488…` (1 read).
- Suite from fork root, all flags unset: **470/470** (463 E32 + 7 new G44).
- `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty (verified
  post-commit).
- Disk: `~/dev/ssx3-work/G44` 1.9 GB of 15 GB cap; all-ssx3 27.0/200 GB
  (budget script exit 0, start and end).
- Lease: T48 held the P-lane ~21:32–22:04 (proof/proof2/capB, no runner
  alive), then E33 booted (e33a, runner alive) ~22:04–22:22. G44 claimed at
  22:22 (S1) and 22:27 (S2); both released cleanly. Never preempted.

## 2. Seam points (file:line on g44-parallel-shadow)

Synchronous shadow, no threading: feeds share the game/main threads with the
CPU backend behind one adapter mutex; the CPU backend stays the presenter.

| Tap | File:line | What crosses |
| --- | --- | --- |
| H1 GIF packets (P1–P5) | `ps2xRuntime/include/runtime/gs/ps2_gif_arbiter.h` (ShadowPacketFn + setter), `src/lib/gs/ps2_gif_arbiter.cpp` drain loop (shadow first, path preserved) | `gif_transfer(path, data, size)` |
| H1b native fast paths (P6/P7) | `src/lib/ps2_memory.cpp` tops of `tryProcessNativeGifImageUploadChain` / `tryProcessNativeGifPackedChain` | disabled when shadow feeds → traffic routes via the arbiter in identical order |
| H2 HLE reg writes (W1/W2) | `src/lib/gs/gs_frontend.cpp` `GS::writeRegister` | `write_register(addr, value)`; decode-internal `writeRegisterUnlocked` (W3) deliberately NOT forwarded (paraLLEl decodes the same stream) |
| H3 priv regs (V1/V3/V4) | `src/lib/gs/ps2_gs_shadow.cpp` `syncPrivLocked`, called per shadow vsync from `GSRegisters` | bulk copy of the 15 scanout fields (dump-parser pattern); smode2 is 12 B (3rd word pure pad — probe `/tmp/g44-priv-probe.cpp` sizes) |
| H4 per-vsync compare | `src/lib/ps2_runtime.cpp` `UploadFrame` after `copyLatched…` | `flush()` + `vsync()` + CachedHost readback (G-series P1 pattern), PSNR/diff/bbox vs CPU pixels, `cpu/par/side-<tick>.png` + `pairs.csv` |
| H5 reset | `GS::reset` | backend torn down, lazy re-init on next feed |
| Wiring | `ps2_runtime.cpp` `syncCoreSubsystems` (shadow-fn set) | — |
| Build | `ps2xRuntime/CMakeLists.txt` (`PS2X_GS_SHADOW_PARALLEL` OFF default, local-path subdir, `ps2_gs_shadow` static lib at C++17 for `std::is_pod`) | — |
| Env | `PS2X_GS_SHADOW=parallel`, `_DIR` (pairs/CSV/stats), `_FROM/_TO` window, hard cap 200 | unset = zero behavior change, no Vulkan init |

Register numbering is identical on both sides (`GS_REG_*` == `RegisterAddr`
values, verified field-by-field), so `write_register` is a static_cast.
`VSyncInfo` mirrors the dump-parser defaults (`READ_ONLY_OPTIMAL`,
`adapt_to_internal_horizontal_resolution=true`, `phase=tick&1`).

## 3. Pre-boot probe (no game, no lease, /tmp/g44-probe.cpp)

Standalone probe linked against the built `libparallel-gs.a` + Granite libs:
`init_loader` FAILS with no loader path; with
`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib` → instance ok,
Apple M5 Pro API 1.4.357, `GSInterface::init` ok, `flush()`+`vsync()` on
empty state → null image (expected). Boots set `GRANITE_VULKAN_LIBRARY` in
`local/research/G44/g44_boot.py`; the adapter logs its value at init.

## 4. Boot table

Common: `PS2X_SKIP_MOVIE=1`, pad script
`25000:start:5000,45000:cross:5000` (E32b route), runner per §1.

| Boot | Wall/cap | Window | Ticks reached | Screens (CPU snaps, read by eye) | Shadow log |
| --- | --- | --- | --- | --- | --- |
| S1 g44s1 | 152 s / 150 s, rc 0 wall-bound | 800–1200, cap 200 | 116 → ~1340 | Main Menu (Single Event) + Select Character (Zoe) | init ok; 400 `vsync()` calls (ticks 800–1199), ALL null; `no scanout image` |
| S2 g44s2 | 302 s / 300 s, rc 0 wall-bound | 1050–1400, cap 200 | 235 → ~1160+ | Select Character (Zoe) settled | init ok; ~110 `vsync()` calls, ALL null with `CMOD=0 LC=0 INT=1 FFMD=0` |

Screens: `frames-g44s1-1/snap/snap-0042.11s.png` (Main Menu),
`snap-0082.21s.png` + `snap-0152.38s.png` (Select Character, Zoe);
`frames-g44s2-1/snap/snap-0300.72s.png` (Select Character, Zoe). Riders are
flat white silhouettes on the CPU backend (E33's area, unchanged).

## 5. Per-screen compare table

| Screen | Pairs | PSNR | Diff px | BBox | Side-by-side |
| --- | --- | --- | --- | --- | --- |
| Title | 0 | — | — | — | — |
| Main Menu | 0 | — | — | — | — |
| Select Character (Zoe) | 0 | — | — | — | — |

No pairs exist because scanout never produced an image (§0). Rendering-side
evidence that the feed is alive (S1, 400/400 identical setup lines):
`EN1=1 EN2=0 DISPFB1=112/8/1/0/0 DSP1=2560/447/4/0/641/50 SM=0/1/0`, B-region
(DISPFB1 pages) `nz=769022` with per-frame-varying fnv (animated display
content), A-region fnv changing seq-to-seq (live writes). CPU presents
512×448 from the same `fbp=112` (`upload-*.txt fnv` varies per tick).

## 6. The ONE next action (orchestrator decides)

**One S3 boot (300 s, same S2 script, window 1000–1400) on the committed
head.** It validates the corrected workaround condition
(`CMOD==0 && INT==1 && (LC==0 || LC==32)` → retry as NTSC geometry): expect
`CMOD … workaround fired (scanout recovered)` lines and the first
`pairs.csv` rows + side-by-sides answering Zoe. If scanouts stay null, the
fallback is a no-SKIP boot to movie-park (E32a state) to test the
hypothesis that SMODE1=0 is a SKIP_MOVIE-path artifact (BIOS/game video
init skipped): read the G31 `SM=` fields there — NTSC+ANALOG would confirm
it, and the shadow would likely just work on that path.

## 7. Gaps (stated plainly)

- Zoe/H1-vs-H2 unanswered: 0 readbacks. The cross-check the brief wanted
  needs S3.
- The committed workaround condition is UNVALIDATED (no boot budget left:
  1 configure + 2 boots used; retry clause requires a lease-holder crash,
  which did not happen).
- Feed-volume counters (`gifPacketsFed`/`regWritesFed`) are only persisted
  to `shadow-stats.txt` on pair write — with 0 pairs there is no exact
  packet count, only the G31 per-vsync VRAM deltas. The adapter should log
  feed counts periodically regardless of pairs.
- `presentsSeen` likewise unpersisted with 0 pairs.
- FIFO readback (`read_transfer_fifo`, T3/R1) is not mirrored; scanout-only
  compare does not need it, but a future presenting backend will.
- `GRANITE_VULKAN_LIBRARY` is a mini-specific absolute path in the boot
  wrapper (documented in `local/AGENTS.local.md` spirit, not portable).
- STANDALONE=ON (null platform, shipping, embedded slangmosh) is untested
  vs the G43-tested replayer config for rendering equivalence — moot until
  scanout works, then S3's pairs re-baseline it.
