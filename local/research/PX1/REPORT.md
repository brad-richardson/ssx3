# PX1 — PCSX2 as the pixel reference for our race frames

**Status: DONE 2026-09-25 (post-resume).** TEXFLUSH hypothesis REFUTED by
full-stream replay (byte-identical HUD-only). Probe campaign isolates the
gap: menus + textured sprites + HUD render correctly in PCSX2-on-our-stream;
race-world tristrips neither sample nor rasterize there (invisible even with
texturing forced off), while the same bytes render fully on paraLLEl. No
converter change is indicated for this symptom — the "converter gap" is a
world-geometry rasterization gap inside PCSX2-GL, not data loss in the
converter. Follow-up brief recommended (PX2): per-draw STATE probe
(ZTEST/SCISSOR/FOG/ABE) against PCSX2-SW or instrumented GL.

## 1. Repro inputs (all pinned)

- Runner: `~/dev/ssx3-work/F2/bin/runner-det`
  sha256 `54789f9a…96542ba0` (matches F2 REPORT pin), source `92f9991`
  (= fork `ssx3` `0ed07c4` minus the Android-only lambda fix; functionally
  the pinned tip on Mac). Taps OFF, `PS2X_GS_SHADOW_PARALLEL=ON`.
- Boots (I26-FAST, vsync clock, det, `PS2X_SKIP_MOVIE=1`, paraLLEl env
  `GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`,
  `PGS_HIER_BINNING=force`, sound on):
  - b1: `--dump-ticks 1090,1180,1800 --capture 1`, slot 2, 97.9 s,
    vsync 2413, `run-b1/gs.cap` 2,510,683,433 B, ticks 1..2400.
    Dumps: tick 1091 fnv `790e38b3`, 1180 `accffc8c`, 1800 `44ebc4b0`.
  - b2: `--dump-ticks 1800,2100,2400 --capture 0`, slot 4, 261.2 s,
    vsync 2421. Dumps: 1800 `44ebc4b0`, 2100 `97047088`, 2400 `758f95a8`.
  - Cross-boot determinism: b1-1800 == b2-1800 byte-identical
    (PNG md5 `88294deb…5e4153`).
- Converter start: `rr1_cap2gs.py` copied verbatim to
  `local/research/PX1/px1_cap2gs.py`. Full conversion `px1a.gs`
  2,509,843,217 B (1,832,797 packets, 2,400 vsyncs).
- Replay: T48-pinned gsrunner `8e446ff1…0bc8a56` (= G13 pin, T48's
  pre-patch stash) staged at bytesize `~/px1/run/` with
  resources/translations symlinks, ini `g10-uncorrected.ini`
  (only `ScreenshotSize=2`), `-renderer vulkan -surfaceless` under
  Xvfb. Full replay: 2,399 frames, ~104 s, log shows only benign
  warnings. Frame N = tick N (verified via `.ticks`).
- Healthy oracle: `t48b-dump.gs.zst` sha `377ca2f1…` (matches T48 pin),
  8 race vsyncs, fetched to `~/dev/ssx3-work/PX1/`.

Tool scripts (all in `local/research/PX1/`, text, committed here):
`px1_boot.py` (RR1-style 1-slot bounded boot), `px1_cap2gs.py`
(+ `--texflush-after-upload`, default off, kept as a diagnostic flag),
`px1_replay.sh` (quote-safe WSL replay + probe presets), `px1_fetch.sh`,
`px1_mini.py` (tick-list .gs extractor), `px1_vertcheck.py` (per-class
full-state + vertex census), `px1_imgspan.py` (mid-stream label flips),
`px1_notex.py` (force TME=0 in PRIM reg + PRE TAG PRMODE — BOTH paths,
see §6), `px1_qone.py` (force Q=1.0 in RGBAQ/ST).

## 2. Reproduced symptom (variant of RR1's)

- Menus replay **perfectly** through tick 1710 (Select Peak 1091,
  Select Mode 1180, loading 1607/1608/1620, Rival card 1650–1710,
  including the textured Rival-card header photo at 1700).
- From the **first race frame (1711/1712)** PCSX2 shows **HUD-only on
  near-black**: timer/MPH/score/EA panel all live (00:00:01→06→11),
  world at ×0.01 (center mean (1.3,1.3,13.2), max 81) vs ours
  (142,162,233). Same at 1800/2100/2399.
- RR1's "blank from 1608" is the same loading→race transition in their
  ticks (their race started ~1607, ours ~1711; timing shifted by the
  fold). Their `--force-smode1-ntsc` also stayed blank — SMODE is out.

## 3. Elimination log (all local except where noted)

| # | Hypothesis | Evidence | Verdict |
|---|---|---|---|
| 1 | Dropped record type (NativeUpload/LocalToHost/ClearContext) | Capture has **zero** kind-5/6/7 records, all ticks | DEAD |
| 2 | VSync/field mapping, SMODE forcing | HUD+composite positioned correctly; menus share SMODE2=0x1/PMODE | DEAD |
| 3 | Priv/Regs wrong | Same DISPFB/DISPLAY at 1091 and 1800 (sidecars); scanout correct | DEAD |
| 4 | NaN/Inf vertices (VU1 bug masked by our GS) | `px1_vertcheck`: **zero** bad verts in 78 classes at 1800 | DEAD |
| 5 | MIPTBP garbage (TBW invalid) | Script decode: all sane (TBW=1, +32 chains); our values include healthy's exact `0x7a6907a4907a29` | DEAD |
| 6 | TEX1 garbage upper bits | Healthy dump has identical `0xffffffXX…168` pattern (game-normal) | DEAD |
| 7 | Upload params garbage | BITBLTBUF/TRXPOS/TRXREG sane at 1605/1711 (DBP=dest, DBW∈{1,2,4}, pos 0,0) | DEAD |
| 8 | Capture order ≠ live order | Capture is in the process path (post-arbiter); menus pixel-agree | DEAD |
| 9 | Multi-packet IMAGE split across path labels | `px1_imgspan` 1795–1805: **zero** mid-stream label flips | DEAD |
| 10 | Missing uploads / missing CLUT | All present: pixels (13673@1605/1608/1711-in-frame), CLUTs (12897@1607, 15465@1605, terrain CBPs@1605), mip levels (1608 chains) | DEAD |
| 11 | Depth pass clears FBP 0 after world | #1905 = 1 KB upload + 48 blend-average strips (×0.5 max); measured ×0.01 | DEAD |
| 12 | Black vertex colors × MODULATE | RGBAQ buckets mid-gray (128s/32s); predicts ×0.5, measured ×0.01 | DEAD |
| 13 | Composite broken | Only FBP-112 draws = the TBP0→112 composite; HUD (via FBP 0) proves it works | DEAD |
| 14 | Stale-boot cache entries | First-use tick == first-upload tick for every race TBP (1605) | DEAD |
| 15 | Clobbering write 1605–1711 | 4,049 uploads into race VRAM, all dpsm=CT32 legit texture/mip/CLUT shapes; no clear pattern | DEAD |
| 16 | PCSX2-SW would discriminate | SW renderer fails in WSL (`Failed to create any context`, needs GL) | BLOCKED |
| 17 | Texture-cache staleness (TEXFLUSH fix) | Full-stream `--texflush-after-upload` replay `bfull` **byte-identical** to unpatched `afull` at 1800/2100/2399 (HUD-only, PNG md5 `41d7b61f…` both) | **DEAD (§4)** |
| 18 | Auto-flush / conservative-buffer renderhacks | Full-span `af` and `dpi` probes: still HUD-only at 1800 | DEAD |
| 19 | In-frame upload timing (terrain TEX available late) | `mini1711-notex` broken-patch control + frame-span probes: HUD sprites + text appear, world still absent | DEAD (as timing) |
| 20 | Tiny-Q kills sampling (Q≈0.02 perspective divide) | `ntq2` = NOTEX-fixed + Q→1.0: only UI re-colors (gray→magenta band); world still absent | DEAD |
| 21 | World verts off-screen / degenerate / bad Z | PC decode of 1711 stream: terrain XY on-screen full-frame, RGB valid, Z full-range; A broad 0–255 | DEAD (as vertex data) |

## 4. TEXFLUSH validation (REFUTED post-resume)

- `px1b.gs` = full 0–2400 conversion with `--texflush-after-upload`
  (6,651 TEXFLUSH inserted, +252,738 B exact), replayed as `bfull`.
- `bfull` vs `afull` at 1800/2100/2399: **byte-identical PNGs**
  (md5 `41d7b61f…`), HUD-only. A cache hint cannot change a correct
  replay — and here it changed nothing at all, so cache staleness is
  not the mechanism. Mixed-PSM lead (§4 of paused report) is dead.
- `af`/`dpi` renderhack full-span probes: still HUD-only. SW renderer
  and `-dump tex` gate both unavailable in bytesize WSL (no GL
  context; dump dir never created).

## 5. Gallery (all triples viewed by the worker)

Paths: ours `~/dev/ssx3-work/PX1/run-b1|2/frames/upload-*.png`
(sidecar `.txt` pins tick+fnv); PCSX2-on-ours
`~/dev/ssx3-work/PX1/back-afull/px1a_frameNNNNN.png` (2399 stands in
for 2400: 2,400 vsyncs dump 2,399 frames); PCSX2-native: T47 HW shots
`/Volumes/Extreme SSD/ps2x-t47/t47-shot-sp|sm.png`, race
`local/research/{E51/frames/pcsx2-t65-race-0018.png,T65/t65-shot-t65a-race.png}`
(same shot). Frames stay in scratch; numbers below.

| Tick | Ours (paraLLEl) | PCSX2 on our stream | PCSX2 own run | Diff verdict |
|---|---|---|---|---|
| 1091 Select Peak | photo+orange 3+flakes, fnv `790e38b3` | same, complete | T47 SP: same screen (flakes differ: animated) | same-tick mean\|Δ\| **5.44**, p99 59, exact 25% — **ours-GS long tail** (filter/blend precision) |
| 1180 Select Mode | Race map, fnv `accffc8c` | same, complete | T47 SM: same map+selection | mean\|Δ\| **4.12**, p99 33, exact 26% — **ours-GS long tail** |
| 1700 Rival card | card + textured header photo | same, header photo textured+visible | — | **textured sprites work** in PCSX2-on-ours |
| 1800 race 00:01 | full world, fnv `44ebc4b0` (both boots) | **HUD-only**, world ×0.01 | E51/T65 00:18 jump: textured world (other moment) | **world-tristrip rasterization gap** (not converter data loss) |
| 2100 race 00:06 | full world +220, fnv `97047088` | **HUD-only** | same ref | **same as 1800** |
| 2399/2400 race 00:11 | full world, fnv `758f95a8` | **HUD-only** | same ref | **same as 1800** |

Menu verdict: PCSX2-on-our-stream is already a usable pixel reference
for menus (single-digit mean diff) and textured sprites. Race verdict:
world geometry never rasterizes in PCSX2-GL (§6).

## 6. Isolation probes (the positive result)

Span used: `mini1711.gs` (race vsync 1711, 9,370,783 B), unpatched
replay = blue panel wireframe only, no text, no world
(`back-mini1711/mini1711_frame00001.png`).

- **NOTEX-broken** (`px1_notex.py` v1, PRIM-reg only, 38 patches):
  identical to unpatched — control showing the PRIM register write is
  NOT what these packets use (they carry PRMODE in the PRE TAG).
- **NOTEX-fixed** (`ntx2`, PRIM reg + PRE-TAG PRMODE TME=0, ~2.6k
  patches): UI appears flat — white/cyan text rows, gray band (HUD
  bar sprite), small gray box (PNG md5 `6ae50bd8…`). **World
  tristrips still absent.** Proves (a) the patch path works, (b) UI
  sprites were black-*sampling* (now flat-visible), (c) world
  tristrips don't rasterize even untextured.
- **NOTEX-fixed + Q→1.0** (`ntq2`, 184,507 Q patches): band goes
  gray→magenta (Q scales vertex color), text unchanged, **world
  still absent** (md5 `b1d582aa…`). Q is out.
- PC-side decode of the same bytes: terrain/backdrop classes have
  valid on-screen XY, valid RGB, full-range Z, broad alpha; strip
  structure decodes with early breaks (RESTART-heavy) but sibling
  UI geometry with similar packing renders, so the bytes are sane
  and the divergence is in PCSX2-GL's per-draw state handling.

**Root cause (best supported):** the converter faithfully transmits
the world tristrip draws (same path as working menus/sprites); the
PCSX2-GL renderer on bytesize drops them before/without
rasterization. Not tested per-draw: ZTEST vs ZBUF, SCISSOR, FOG,
ABE/ALPHA, DATE/PABE. Recommended next brief (PX2): force
ABE=0 / ZTE=0 / FGE=0 / SCISSOR-full variants of `mini1711.gs`
against PCSX2-SW (needs a GL-capable host) or instrumented GL, one
variant each.

## 7. Workdir inventory + receipts

- Workdir `~/dev/ssx3-work/PX1/` ≈ 12 GB: `run-b1/gs.cap` 2.5 GB,
  `px1a.gs`/`px1b.gs`/`px1c.gs` 2.5 GB each, `.gz` ×4 (~0.8 GB ea),
  truncated `.gs` ×4, `mini*.gs` ×9, `back-*/` frame dirs (14),
  `t48b-dump.gs`. Bytesize `~/px1/` holds inputs + frame dirs;
  `C:\Users\bradr\px1*.gz` + `px1back\` hold transfers.
- Bytesize replays this brief: afull, bfull, cfull, pf-af, pf-dpi,
  probes (glyphs/sky/terr/terr360/full360), mini1608, mini1711,
  mntx (broken), mntx2 (fixed), mntq2 (fixed+Q). ~15 WSL runs,
  all inside the run budget as device-adjacent replays; no extra
  PS2 boots beyond b1/b2.
- `git log -1` before commit: see commit parent. No fork changes.
  No lease held at stop. No push (worker rule).
- Disk: ssx3 internal 70.6 GB / 200 GB cap at start; PX1 ≈ 12 GB.
- Gaps stated plainly: (1) PCSX2-SW oracle unavailable (WSL has no
  GL context); (2) `-dump tex` gate never fired — no VRAM-level
  confirmation of what PCSX2 uploaded; (3) exact per-draw blocker
  (Z/SCISSOR/FOG/BLEND) not yet isolated — PX2.
