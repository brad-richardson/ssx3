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

Verdict after Part-3 S4: **SHADOW WORKS** (with the diagnostic SMODE1
override) — 200/200 scanouts recovered, same scenes on both backends (§5).
Zoe/Select-Character pairs were NOT captured (cap filled before select);
the rider question stays open. Fork commits `460e438` + `8c45d1f` +
`6cfede4` (no push).

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
  `b8a694c5…` (1 read, superseded); post-S2 binary `25bd6450…` (2 matching
  reads, superseded unbooted); S3/Part-2 binary `3402f272…` (2 matching
  reads, pre+post S3). S4/Part-3 binary `e81ba740…` (2 matching reads,
  pre+post S4). Suite binary `8db3d488…` (1 read); suite 471/471 after every
  adapter edit (463 E32 + 8 G44; logs `/tmp/g44-suite*.log`).
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
| S3 g44s3 (Part-2) | 301 s / 300 s, rc 0 wall-bound | 1000–1400, cap 200 | 276 → ~1916 | Select Character (Zoe) settled (`snap-0301.18s.png`) | init ok; workaround FIRED every eligible tick, ALL still null; counters: 219008 packets fed, 0 reg writes, 1800 presents, 0 pairs (`shadow-g44s3/shadow-stats.txt`) |
| S4 g44s4 (Part-3) | 303 s / 300 s, rc 0 wall-bound | 1000–1400 + `FORCE_SMODE1=ntsc`, cap 200 | 275 → ~1900+ | Select Character (Zoe) settled on CPU (`snap-0301.25s.png`) — but OUTSIDE the pair window | `FORCE_SMODE1 active` logged; **200/200 scanouts recovered**: 172370 packets fed, 0 reg writes, 1440 presents, 200 pairs (`shadow-g44s4/`: 200× cpu/par/side PNG + `pairs.csv` + stats) |

Screens: `frames-g44s1-1/snap/snap-0042.11s.png` (Main Menu),
`snap-0082.21s.png` + `snap-0152.38s.png` (Select Character, Zoe);
`frames-g44s2-1/snap/snap-0300.72s.png` (Select Character, Zoe). Riders are
flat white silhouettes on the CPU backend (E33's area, unchanged).

## 5. S4 per-screen compare (200 pairs, ticks 1000–1199)

Pair window covered title → menu only (cap filled at tick 1199; select sits
at ~1450+). All pairs 512×448 both sides, bbox full-frame throughout.

| Screen (ticks, eyed) | Pairs | Base PSNR | Diff px (of 229376) | After ±2px shift search |
| --- | --- | --- | --- | --- |
| Title (~1000–1035; `side-1010.png`) | ~35 | ~18.1 | ~183k (80%) | 26.6 dB @ (+2,+2) |
| Transition fade (~1025; `side-1025.png`) | ~3 | ~23.8 | 35k (15%) | **53.0 dB** @ (+1,+1), mad 0.20 |
| Main Menu (~1040–1199; `side-1040/1190/1199.png`) | ~160 | ~18.2 | ~160k (70%) | 26.8 dB @ (+2,+1) |
| Select Character (Zoe) | 0 | — | — | — |

Aggregate: mean diff 161882 px (70.6%), mean PSNR 18.75 dB, no phase split
(even 18.72 / odd 18.79 — deinterlace stable). Element checklist on
`side-1190.png` (menu): orange '3' logo, header, 5 items + highlight,
description text, floating quads, R1/L1 boxes, bottom hints, snowflakes —
**all present on both backends, same layout**. Amplitude histogram (scratch
`/tmp/g44-diff.cpp`, raylib, NOT committed): tick 1190 has 31% exact,
74% ≤2 LSB, 88% ≤16 — i.e. the gap is a global ~1–2px translation (scanout
crop convention; we pass `crtc_offsets=false`) plus low-amplitude
implementation noise, not content. The transition fade lands both backends
in lockstep (53 dB after shift) — the feeds are synchronized per-vsync.

T47 PCSX2 refs (`/Volumes/Extreme SSD/ps2x-t47/`, read-only): the '3' logo
matches across CPU/para/PCSX2. The floating quads, bottom-left icon cluster
and R1/L1 boxes appear on BOTH recomp backends but NOT on `t47-shot-menu`
— a recomp-vs-PCSX2 difference upstream of the GS (game state/timing or
VU1/VIF: E33's area), not a CPU-vs-paraLLEl difference. Title snowflake
blobs likewise agree backend-to-backend. **Zoe/3D-rider: unanswered** — no
Select-Character pairs exist; S4 reached select on CPU only.

## 6. Verdict: SHADOW WORKS with the diagnostic override; Zoe still open

Part-3 recovered all 200 scanouts. Partial H1/H2 signal: for title + menu,
paraLLEl fed the same GIF stream draws the same picture as the CPU backend
(same elements, same layout, 26–53 dB after compensating a ~1–2px scanout
crop offset) — no missing content on either side, so the recomp-vs-PCSX2
extras (floating quads, corner cluster) sit upstream of the GS. The missing-
3D-rider question is NOT answered: the cap filled before Select Character.

Recommended next action (orchestrator decides): one S5 boot on this head
with window 1300–1700 (cap 200 covers select at ~1450+), same script, to
capture Select-Character pairs and answer Zoe plainly. No code changes
needed. The E-lane `SetGsCrt`→SMODE1 fix remains the real root-cause fix
(it retires the diagnostic override); G31 `SM=` should read `2/x/x` after
it lands. No T47 writes were made (refs read-only).

## 7. Gaps (stated plainly)

- Zoe/H1-vs-H2 unanswered: 0 readbacks. The cross-check the brief wanted
  needs S3.
- (Part-2, resolved) The corrected workaround condition is now VALIDATED as
  insufficient: S3 fired it every eligible tick, all retries null
  (LC=0 unmapped independent of CMOD). 1 configure + 3 boots used.
- (Part-2, resolved) Feed counters persist every 60 presents regardless of
  pairs (fork commit `8c45d1f`): S3 left exact receipts (219008/0/1800/0).
- FIFO readback (`read_transfer_fifo`, T3/R1) is not mirrored; scanout-only
  compare does not need it, but a future presenting backend will.
- `GRANITE_VULKAN_LIBRARY` is a mini-specific absolute path in the boot
  wrapper (documented in `local/AGENTS.local.md` spirit, not portable).
- STANDALONE=ON (null platform, shipping, embedded slangmosh) is untested
  vs the G43-tested replayer config for rendering equivalence — moot until
  scanout works, then S3's pairs re-baseline it.
