# PX1 — PCSX2 as the pixel reference for our race frames

**Status: PAUSED 2026-09-25 ~13:50 (Brad needs the machine).** Step 1
(convert + reproduce) is done and root-caused to a lead hypothesis;
the candidate converter fix is implemented but **unvalidated** (bytesize
went busy under F4's build before the validation replay). Step 2
(gallery) is done: all 5 triples viewed, table below. Resume plan at
the bottom with exact commands.

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
`px1_boot.py` (RR1-style 1-slot bounded boot), `px1_cap2gs.py`,
`px1_replay.sh` (quote-safe WSL replay + probe presets), `px1_fetch.sh`,
`px1_mini.py` (tick-list .gs extractor), `px1_vertcheck.py` (per-class
full-state + vertex census), `px1_imgspan.py` (mid-stream label flips).

## 2. Reproduced symptom (variant of RR1's)

- Menus replay **perfectly** through tick 1710 (Select Peak 1091,
  Select Mode 1180, loading 1607/1608/1620, Rival card 1650–1710).
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

## 4. Lead hypothesis (UNCONFIRMED) + candidate fix (UNVALIDATED)

**Mixed-PSM upload/alias:** the race uploads pixels as CT32 (`dpsm=0`)
but samples them as PSMT8/PSMT4 (backdrop TBP 13673 TBW 4, terrain
PSMT4 trilinear), while menus upload native-PSM (PSMT8H→PSMT8H) and
replay correctly. Suspect PCSX2-HW's texture cache misses the
cross-PSM invalidation for these small-width (DBW 1–2 / TBW 1–4)
textures, serving stale-black entries; our backends have no texture
cache (CPU samples VRAM directly) so they stay correct. Consistent
with everything above, including HUD-visible (HUD textures are
direct-color, native-PSM uploads).

**Candidate fix** (`px1_cap2gs.py --texflush-after-upload`, default off):
after every packet containing an IMAGE transfer, append a PATH3
Transfer with one A+D TEXFLUSH (0x3F). TEXFLUSH is a hardware-neutral
cache hint, so it cannot change a correct replay. `--to 1720` test:
6,651 inserted (+252,738 B, exact), output parses (`e51_gif`,
272 prims/50 vsyncs).

**Validation (NOT RUN — bytesize busy under F4's Android build from
~13:07, gsrunner OOM-killed there):**
1. `python3 local/research/PX1/px1_cap2gs.py ~/dev/ssx3-work/PX1/run-b1/gs.cap ~/dev/ssx3-work/PX1/px1b.gs --texflush-after-upload` (~2 min)
2. `gzip -1 -c px1b.gs | scp → bytesize:px1b.gs.gz`, replay:
   `ssh bytesize "wsl -d Ubuntu -- bash /mnt/c/Users/bradr/px1_replay.sh px1b.gs.gz bfull"`
   (check `uptime`/`free -g` first; one heavy job at a time)
3. Fetch frames 1800/2100/2399; **pass = race world visible** (not
   HUD-only). Control if it fails: full-stream `-renderhacks af`
   then `dpi` probes (`px1_replay.sh px1a.gs.gz p-af af`): world
   appears ⟹ cache/invalidation confirmed, fix is on the right track
   but TEXFLUSH placement needs work; still black ⟹ hypothesis dead,
   re-open.

## 5. Gallery (all triples viewed by the worker)

Paths: ours `~/dev/ssx3-work/PX1/run-b1|2/frames/`; PCSX2-on-ours
`~/dev/ssx3-work/PX1/back-afull/px1a_frameNNNNN.png` (2399 stands in
for 2400: 2,400 vsyncs dump 2,399 frames); PCSX2-native: T47 HW shots
`/Volumes/Extreme SSD/ps2x-t47/t47-shot-sp|sm.png`, race
`local/research/{E51/frames/pcsx2-t65-race-0018.png,T65/t65-shot-t65a-race.png}`
(same shot). Frames stay in scratch; numbers below.

| Tick | Ours (paraLLEl) | PCSX2 on our stream | PCSX2 own run | Diff verdict |
|---|---|---|---|---|
| 1091 Select Peak | photo+orange 3+flakes, fnv `790e38b3` | same, complete | T47 SP: same screen (flakes differ: animated) | same-tick mean\|Δ\| **5.44**, p99 59, exact 25% — **ours-GS long tail** (filter/blend precision) |
| 1180 Select Mode | Race map, fnv `accffc8c` | same, complete | T47 SM: same map+selection | mean\|Δ\| **4.12**, p99 33, exact 26% — **ours-GS long tail** |
| 1800 race 00:01 | full world, fnv `44ebc4b0` (both boots) | **HUD-only**, world ×0.01 | E51/T65 00:18 jump: textured world (other moment) | **upstream-side: converter gap** (our stream renders on our GS; PCSX2-HW drops the world) |
| 2100 race 00:06 | full world +220, fnv `97047088` | **HUD-only** | same ref | **same as 1800** |
| 2399/2400 race 00:11 | full world, fnv `758f95a8` | **HUD-only** | same ref | **same as 1800** |

Menu verdict: PCSX2-on-our-stream is already a usable pixel reference
for menus (single-digit mean diff). Race verdict: blocked on §4.

## 6. Resume plan

1. When bytesize is free, run the §4 validation (full-TEXFLUSH replay,
   then af/dpi controls if needed). ~15 min wall.
2. If green: re-run gallery race triples, update this report, done.
   If red: next discriminators are (a) PCSX2 `-dump tex,tr,rt`
   (needs dump-gate debugging — `ShouldDump` never fired; dir never
   created), (b) static footprint check of swizzle32-DBW2 vs
   swizzle8-TBW4 in `GSLocalMemory.h`/`GSTextureCache.cpp`.
3. Workdir `~/dev/ssx3-work/PX1/` ≈ 8.5 GB (gs.cap 2.5 GB, px1a.gs
   2.5 GB, px1a.gs.gz 0.8 GB, truncated .gs ×4, frames, minis). Bytesize
   `~/px1/` holds .gs inputs + frame dirs; `C:\Users\bradr\px1*.gz` +
   `px1back\` hold transfers. Nothing pushed; this commit only.

## 7. Receipts

- `git log -1` before commit: `98e7ae30 [orch] Pause all lanes…`
- Boots: b1 slot 2 rc 0 target vsync 2413 97.9 s; b2 slot 4 rc 0
  target vsync 2421 261.2 s. No lease held at pause. No fork changes.
- Disk: ssx3 internal 70.6 GB / 200 GB cap at start; PX1 added ~8.5 GB.
