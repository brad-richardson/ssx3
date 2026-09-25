# RR1 report: race rendering gaps (missing sky, dark lower region, flat textures)

Exploratory session (Claude Code, Opus 5.5, Brad-approved), 2026-09-24 21:54–23:19 EDT (1 h 25 min of the 3 h box).
Notebook: `NOTEBOOK.md` (append-only). The orchestrator decides; labels below say what is
measured and what is hypothesis.

## Outcome

Three independent runtime bugs, all upstream of the GS, explain the race look on the Mac. Each
has a fix on local fork branch `rr1-sky` (not pushed), with a unit test and a deterministic
Mac boot where I viewed the frames myself.

| # | Mechanism (measured) | Symptom it causes (A/B-attributed) | Fork commit |
|---|---|---|---|
| 1 | **PATH3 masked FIFO released whole on the first MSKPATH3 unmask.** SSX 3 masks PATH3, kicks one GIF chain per frame (337 KB, 20 EOP packets: every texture upload + a depth pass), then opens one-command `MSKPATH3 0; MSKPATH3 1` windows before each object. Hardware/PCSX2 pass one EOP packet per window. We flushed all 20 at the first window. | All uploads land before the first draw, so later textures overwrite the slots of earlier ones (**flat/wrong textures**, and the **G46 menu atlas family**). The depth pass runs at frame start and leaks `TEST 0x70000 / ALPHA 0x1` into the sky draw (**sky blended away**), and its dark result stays under the world (**dark lower region**). | `3bc0449` |
| 2 | **VIF UNPACK V4-5 not expanded.** `ps2_vif1_interpreter.cpp:986-989` stored raw 5-bit/1-bit fields; PCSX2 `UNPACK_V4_5` gives RGB<<3, A<<7. SSX 3 unpacks vertex colours as V4-5. | Every V4-5-coloured prim at 1/8 brightness and 1/128 alpha: **dark backdrop** (0x01101010 vs PCSX2 0x80808080), dim terrain (0x01080504 vs 0x80402820). | `f3dff5b` |
| 3 | **DMA chain walker capped at 4096 tags** (`kMaxChainTags`, upstream sanity limit). The race's per-frame VIF1 list is 5,126 tags; the walker stopped at 4096 and completed the transfer. | About 20% of each frame's object list is never submitted: **missing trees/foliage, particles, the checkpoint beam** (black lines before), and the depth pass one frame late. The cut point moves with list length each frame, so late-listed objects **pop in and out** (measured in the pre-fix stream; iOS not tested). | `4f69c98` |

Combined (boot G): the race shows the mountain panorama backdrop, lit and textured snow, pines
and rocks, snow spray, the pink checkpoint beam, and no dark lower region. Menus show the Peak 1
photo, SSX logo, "3", clean snowflakes and ✕/△/□ glyphs.

## Evidence

| Row | Measurement | Ours (pre-fix) | PCSX2 / hardware model | Receipt |
|---|---|---|---|---|
| E1 | Sky draw state (PSMT8 256² backdrop) at tick 1795 | 76 prims, ALPHA `0x1`, TEST `0x70000` | T65 v0: 81 prims, ALPHA `0x2a`, TEST `0x51143` | `rr1_census.py`, `rr1_cap.py` |
| E2 | Packet order at frame start | #2/#3 PATH2 set TEST1 0x51143/ALPHA1 0x2a → **#5 PATH3 337,216 B** (all uploads + depth pass setting TEST 0x70000/ALPHA 0x1) → sky draws | #3/#4 same setup → #6–#9 one 65,664 B upload → TEX0 → sky draws; depth pass at #1418–1423 of 1537 | `rr1_timeline.py`, `rr1_timeline_pcsx2.py` |
| E3 | VIF1 gating events, frame 1795 (boot B) | MSKPATH3=1, GIF chain kicked (178 tags) and queued whole; 17 windows, each a bare `MSKPATH3 0` then `MSKPATH3 1`; first window flushed all | PCSX2 upload runs between draws are each exactly one of our EOP packets (65,664 or 11,136 B) | `PS2X_RR1_EV`, `rr1_eop.py` |
| E4 | ALPHA=0x1 A+D in DMA memory (tap) | only the depth-pass setup at EE 0x7bf7a0 / 0x7e5da0 (double-buffered GIF chains) | same draw exists in PCSX2 (TBP 0 psm 0x1b, 16 prims) | `PS2X_RR1_ALPHA_SRC` |
| E5 | Backdrop CLUT (CBP 12897, uploaded tick 1608) | channel averages 43.8/84.7/189.5/127.5 | PCSX2 sky CLUT @14473: identical averages | NOTEBOOK 22:52 |
| E6 | Vertex RGBA | backdrop 0x01101010, terrain 0x01080504 | 0x80808080, 0x80402820 (= ours RGB<<3, A<<7) | NOTEBOOK 22:52 |
| E7 | PCSX2 gsrunner on **our** (PATH3-fixed) stream | — | Select Peak 1090 identical to ours; race start 1607 shows the same dark backdrop → backdrop fault in the stream, not our GS | `rr1_cap2gs.py`, `rr1_gsrunner.sh` |
| E8 | VIF1 chain length (boot F, ticks 1800–1830) | 25 of 50 VIF1 chain kicks end at exactly 4096 tags | after the fix (boot G) chains end at 5,126 tags via END; guard never hit | chain-end event |
| E9 | Unmask windows vs queued PATH3 packets per frame | after fix 1 only: 15–27 windows, 5–7 packets left over per frame | after fix 3: 20–31 windows, 0–1 left over (PCSX2 v0: none) | `rr1_windows.py` |
| E10 | Draw classes per drawing tick, 1714–2160 (pre-fix A) | HUD-style (FST) prims 66–83 every tick; large world classes missing on some frames (350-prim class on 80/354, 167-prim class on 132/322) | — | `rr1_flash.py` |
| E11 | Menu VIF1 chains, ticks 1000–1100 | ≤ 320 tags (cap irrelevant in menus) | — | boot H |

### A/B attribution (boot H: final runner, `PS2X_PATH3_EOP_GATE=0`)

Select Peak atlas artifacts come back, and the race's dark lower region and wrong tree textures
come back. The backdrop stays bright (fix 2) and the trees and beam stay present (fix 3).

### G46 artifact rows (orchestrator request)

Frames are from the same deterministic route (I26-FAST). Route ticks: Select Peak ~1099, Select
Mode ~1185 (the G46 ticks ~1700/2100 were on a different route). Before = replay of boot A's
capture; after = boot C/E (PATH3 + V4-5; menu chains never reach the cap).

| G46 # | Artifact | Before (A) | After | Verdict |
|---|---|---|---|---|
| 3 | Snowflakes as striped squares/shards | My Rules 1440: shard fragments at right | clean six-point ❄ | **fixed** |
| 4 | Select Peak photo panel shows PEAK ACCESS/LEVEL icon atlas | atlas (1090) | **Peak 1 mountain photo** (Brad's question) | **fixed** |
| 5 | Ghost LEVEL/icon row behind header, orange "3" missing | present | orange "3", no ghost | **fixed** |
| 6 | SSX logo slot shows PEAK 1/VAL cells | present | SSX logo | **fixed** |
| 7 | Select Mode photo panel shows striped "3" | "3" graphic (1180) | Peak 1 course map with routes | **fixed** |
| 8 | Button glyphs as teal/pink bars | bars (Select Peak, Setup Character 1000) | ✕ △ □ glyphs | **fixed** |
| 9 | Controller diagram / L1/R1 boxes / bottom-left icon cluster | cluster in My Rules 1440 bottom-left | absent | **fixed** (Main Menu itself not viewed) |
| — | Setup Character mountain backdrop | atlas fragments (1000) | mountain | **fixed** |

No row got worse in the frames viewed.

## Fix

- Branch `rr1-sky` in `~/dev/ssx3-work/RR1/PS2Recomp`, from `f949ff0`: `3bc0449`, `f3dff5b`,
  `4f69c98` (tip `4f69c98f07605343aa9eeccb5ab85c01f4adf498`). Not pushed.
  - `3bc0449`: 5 files, +327/−4. It includes a new default-off dev tap header
    (`ps2_rr1_alpha_tap.h`: `PS2X_RR1_ALPHA_SRC`, `PS2X_RR1_EV`). Drop the header and its
    call sites before folding if you want the fix alone. The dev A/B switch
    `PS2X_PATH3_EOP_GATE=0` is also in this commit.
  - `f3dff5b`: 2 files, +38/−5.
  - `4f69c98`: 2 files, +51/−1.
  - Total vs `f949ff0`: 5 files, +416/−10.
- Rebased check: all three cherry-pick cleanly onto fork `ssx3` **`71c952e`** (local branch
  `rr1-rebase-check`, worktree `~/dev/ssx3-work/RR1/rebase-check`: `607d8ec`, `58f5120`,
  `e20844a`). Not built or tested on that base.
- Tests: "PATH3 mask releases one EOP packet per MSKPATH3 unmask window", "VIF UNPACK V4-5
  expands RGBA5551 to 8-bit channels", "DMA chain longer than 4096 tags runs to its END
  tag". The existing "PATH3 mask queues packets until unmask" still passes: an unmask left
  open drains the rest.
- Suite (`ps2x_tests` from the worktree root): **599 passed, 0 failed**, rc 0
  (`~/dev/ssx3-work/RR1/suite-fix3.log`).
- Runner-dir check: `git diff --stat 14b1e5cb 4f69c98 -- ps2xRuntime/src/runner` is empty.
- Runner (final tree, Release, diag taps OFF, gfx-stats/capture env-gated):
  `~/dev/ssx3-work/RR1/build/ps2xRuntime/ps2EntryRunner` sha256
  `c7868bb78127502f0be002b42372a18cebfbbdd18609084a38bfdbac9dd667bc` (two matching reads).
  Codegen `~/dev/ssx3-work/codegen-ssx3`.

## Frames to view (all under `~/dev/ssx3-work/RR1/`)

| What | Path |
|---|---|
| Race 2100, before (dark lower region, no backdrop) | `run-a/frames/upload-latest.png` |
| Race 2100, after all three fixes | `run-g/frames/upload-latest.png` |
| Race 1800, before / after | `run-a/frames/upload-0.png` / `run-g/frames/upload-0.png` |
| PCSX2 race reference (T65, 00:00:18, different moment) | `~/dev/ssx3/local/research/E51/frames/pcsx2-t65-race-0018.png` |
| Select Peak before / after (Peak 1 background) | `replay-a/a-vq-001090.png` / `replay-e/e-vq-001090.png` |
| Select Mode before / after | `replay-a/a-vq-001180.png` / `run-c/frames/upload-1.png` |
| My Rules / Setup Character before / after | `replay-a/a-vq-001440.png`, `a-vq-001000.png` / `replay-e/e-vq-001440.png`, `e-vq-001000.png` |
| A/B, PATH3 gate off (dark region back) | `run-h/frames/upload-latest.png`, `upload-0.png` |
| PCSX2 gsrunner on our PATH3-fixed stream (1090, 1607) | `pcsx2-of-d/f01090.png`, `f01607.png` |

## Boots (Mac mini, deterministic `PS2X_DETERMINISTIC=1`, I26-FAST, `rr1_boot.py`)

| Boot | Runner state | Slot / wall | Purpose |
|---|---|---|---|
| a | base + taps | 1 / 135 s | GS capture to 2160 (kept, 1.3 GB), ALPHA tap, frames |
| b | + events | 1 / 107 s | PATH3 gating events 1794–1795 |
| c | + PATH3 fix (batch-end drain) | 3 / 172 s | frames incl. menus |
| d | + PATH3 fix (final drain) | 1 / 169 s | capture for PCSX2 replay |
| e | + V4-5 | 1 / 147 s | frames, capture (menus replayed) |
| f | + chain-end event | 1 / 120 s | chain lengths 1800–1830 |
| g | + chain cap (final) | 1 / 189 s | frames, capture (kept, 1.3 GB), windows |
| h | final, `PS2X_PATH3_EOP_GATE=0` | 3 / 147 s | A/B; menu chain lengths |

All bounded by the target vsync; runners exit 0. PCSX2 work on bytesize ran under `~/rr1`
(gsrunner only, 32 s each, while bytesize was idle). Scratch is 3.3 GB (cap 20 GB); ssx3
internal total is 90.3/200 GB.

## Gaps

- **No same-scene PCSX2 race frame.** PCSX2 comparisons are against T65 (00:00:18, a different
  race moment) and against PCSX2's GS replaying our stream. Prims per drawing tick went from
  21–24k to 34–36k after fix 3. T65's ~21.9k is a different moment, so whether 34–36k is
  right isn't established.
- PCSX2 gsrunner on our converted stream shows blank frames from tick 1608 onwards (also with
  forced NTSC SMODE1). Cause unknown; converter or replay gap, not investigated.
- The sun/flare wasn't checked (no frame facing it on this route).
- **HUD flashing (Brad, iOS):** not reproduced on the Mac. HUD-style prims are present on
  every drawing tick 1714–2160 before and after. World pop-in fits fix 3 (measured in the Mac
  pre-fix stream). HUD/menu flashing may be the PATH3 wrong-texture effect or host present
  tearing. **Hypothesis; needs an iOS build of the fixes.**
- The Main Menu frame (G46 row 9 proper) wasn't viewed. G46's paraLLEl column wasn't re-run
  (these fixes are upstream of both backends).
- The dev tap header ships in `3bc0449`.
- Speed: fix 3 adds about 50% more prims per frame and fix 1 adds 17–30 small GS submits
  per frame. There are no speed numbers (the boots used capture/stats env).
- Fix 1 models the MSKPATH3 mask as taking effect at the next EOP, with the rest draining
  when a VIF1 delivery ends unmasked. PATH3 queued while unmasked and interleaved with
  PATH1/2 inside one delivery isn't modelled beyond the existing arbiter.

## Next steps (the orchestrator decides)

1. Fold the three commits onto `71c952e` (drop the tap header if preferred), build, suite,
   one deterministic race boot, and view frames. Then an Odin paraLLEl run and an iOS build
   for Brad (sky, textures, pop-in, and whether the HUD flashing is gone).
2. Clean speed re-baseline after the fold (more geometry per frame now).
3. T lane: a same-scene PCSX2 race capture (deterministic moment) to compare prims per vsync
   and object census, now that the stream structure matches PCSX2 (frame start, one upload
   per window, depth pass late).
4. Re-check E51's leads on the new stream: TEX1 K, IMAGE uploads/vsync, capped VU1 programs,
   startPC census.

## Tools (this dir)

`rr1_census.py` (PCSX2 dump census with ALPHA/TEST), `rr1_cap.py` (our PS2XGSC1 capture
census), `rr1_timeline.py` / `rr1_timeline_pcsx2.py` (per-packet state timelines),
`rr1_eop.py` (EOP split), `rr1_uploads.py`, `rr1_flash.py` (per-tick class presence),
`rr1_windows.py` (PATH3 window accounting), `rr1_cap2gs.py` (PS2XGSC1 → PCSX2 .gs),
`rr1_gsrunner.sh`, `rr1_boot.py` (deterministic I26-FAST boot, one lease slot).

## Orchestrator gate (2026-09-25)

**Pass.** I viewed `run-g/frames/upload-latest.png` (race 00:00:06: mountain backdrop, lit textured
snow, pines, snow spray, checkpoint beam, no dark lower region) and `replay-e/e-vq-001090.png`
(Select Peak: Peak 1 photo, orange "3", SSX logo, ✕/△ glyphs). Three independent mechanisms, each
with a unit test and an A/B boot: PATH3 one EOP packet per unmask window (`3bc0449`), V4-5 unpack
expansion (`f3dff5b`), DMA chain tag cap raised to a runaway guard (`4f69c98`). Fold onto fork
`ssx3` in F1. Brad's flicker report stays open until he sees the folded build.
