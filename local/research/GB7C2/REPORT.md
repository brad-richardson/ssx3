# GB7C2 — title-text pixel chain p47176→p47240 (source patch + one validation replay)

Predeclared single chain only. No glyph or backend verdict — the orchestrator decides.

## 1. Pins

| Item | Value |
| --- | --- |
| GB4 worktree `~/dev/ssx3-work/GB4/PS2Recomp` base | `09d583a36ee62c165ce9e0473b945821a7a128f7`, branch `gb4-parallel` (patch uncommitted at build; committed `[GB7C2]` after validation, see §7) |
| G43 `~/dev/ssx3-work/G43/parallel-gs` | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` (untouched) |
| capture `run/gb4p4.capture.bin` | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` via `shasum -a 256` AND `sha256sum` (two reads, match) |
| path sidecar | `run/gb4p4.paths.txt`, 1,982,063 lines (true GIF path; capture not copied) |
| ssx3 HEAD at work | (see ssx3 `[GB7C2]` receipt commit) |
| runner-dir diff `git diff 14b1e5cb gb4-parallel -- ps2xRuntime/src/runner` | empty (0 lines) |
| disk | `local/tooling/disk_budget.sh`: 144.4 GB of 200 GB cap |

Chain pin (independent full-TSV lookup before implementation): tick600 path2 packet47176 holds
9 off-screen `fbp=0`/`T4 tbp0=11017` glyph-run sprites at x343–407/y378–387 (plus a 1px tail at
x410); packet47117 (tick600) precedes it and cannot carry it; zero candidate packets exist in
(47176,47240]; the first following `fbp=112`/`tbp0=0` display blit is tick601 path3 packet47240.

## 2. Source patch (3 files, +675/−1, no build until N8D7L release)

- `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`: `Gb7c2PacketContext`
  (tick/packetIndex/path/batch) + `ps2xGb7c2ProbeOpen/Close/SetPacketContext/Enabled` decls +
  three private hook decls.
- `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`: default-OFF probe. `NoteGb7c2BatchBegin`
  assigns the intra-packet batch id per `DrawPrimitive`, logs one batch row for C1-state
  (tick600/pkt47176/path2/sprite/STQ/fbp0/tbp0-11017) and carrier-state
  (tick601/pkt47240/path3/sprite/FST/tme/fbp112/tbp0-0) batches, snapshots the off-screen ROI
  `(340,375)-(410,415)` before each C1 batch, and re-checks the ROI against the last C1
  after-image at each carrier batch. `NoteGb7c2BatchEnd` diffs the ROI (changed count +
  bounding box + first 8 coords; ≥90% changed = `full-cover-intervened-unknown`).
  `DrawSprite` textured loop traces a fixed interior set per C1 sprite (4 corners+center,
  deduped, ≤4) and, per carrier batch, the first ≤8 scan-order destination pixels inside the
  displayed lower crop whose source falls in the ROI. Each traced pixel gets an independent
  unconditional old read immediately before `WritePixel`, the resolved texel/RGBA + raw
  T4-nibble/CLUT (or raw CT32) + FST/lin/TEST/ALPHA state, and a post-write new read with a
  TEST/ALPHA/z outcome evaluated on the independent old value. The `WritePixel`-internal
  conditional old read is never used as proof. OFF path = one branch per batch/pixel;
  rendering untouched (probe adds only `ReadVramUnlocked` calls + log writes).
- `ps2xTest/src/ps2_gs_replay_tests.cpp`: `PS2X_GS_REPLAY_GB7C2_TRACE` (direct-CPU only,
  exclusive with GB5/GB5B/GB7B), per-packet `SetPacketContext`, per-packet display-crop
  before/after via the existing `readGb5Crops` helper for packet indices 47176–47240
  (`<trace>.crops`, 1000-row cap, >2775 lower-changed pixels from a non-47240 packet =
  `full-cover-intervened-unknown`), stop after the marker-700 sample, close +
  `GB7C2 replay reached marker 700` assertion.
- Caps: 20,000 rows / 8 MiB, stop-writing-at-cap (same shape as GB7B).

## 3. Validation (exact commands from `~/dev/ssx3-work/GB4/PS2Recomp`)

| Step | Command | Result |
| --- | --- | --- |
| build (1, incremental) | `cmake --build ../build --target ps2x_tests > ../run/gb7c2/build-1.log 2>&1` | exit 0, first try — **no compile repair, no second build**; `ps2x_tests` 8,215,368 B; only pre-existing `-Wswitch` warnings in `ps2_gs_memory.h`; `PS2X_ENABLE_DIAG_TAPS` untouched |
| flag-OFF suite | `../build/ps2xTest/ps2x_tests > ../run/gb7c2/suite-1.log 2>&1` (flag unset) | **556/556 pass** |
| direct-CPU replay | `PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=600,601,700 PS2X_GS_REPLAY_PPM_DIR=../run/gb7c2/ppm PS2X_GS_REPLAY_GB7C2_TRACE=../run/gb7c2/chain.tsv ../build/ps2xTest/ps2x_tests > ../run/gb7c2/replay-1.log 2>&1` | **556/556 pass**; `GB7C2_SUMMARY rows=320 bytes=51529 capped=0`; `packets=59904 priv=3989 transfers=624 markers=700 samples=14` (identical counts to GB7B §3); no GPU replay |

Same-stream OFF-control hashes: `GB4_FRAME` tick600 `present=a6948f2` and tick700
`present=97b4641e` reproduce the GB7B OFF-control values exactly (trace-ON replay is
render-identical); tick601 `present=582dd887` (new sample, no control). Saved-PPM lower-crop
hashes recomputed independently from PPM bytes: 600 → `02bfd499`, 601 → `02bfd499`,
700 → `032a9954` (all match the live crop trace and GB7B/GB5D CPU values). Frames/crops were
hash-checked, not viewed, by this worker.

`run/gb7c2/` total 2.2 MB (<64 MiB). Committed text (this dir) <256 KiB combined.

## 4. Predeclared PASS/OTHER and outcome

- PASS iff (a) a traced C1 pixel old→new change is logged with its texel chain, (b) the
  off-screen ROI diff is glyph-shaped (changed>0 clustered inside a candidate rect, not
  full-crop), and (c) the first following same-column `fbp=112` blit preserves it
  (post-blit lower-crop hash moves toward the ROI content, no intervening full-screen
  overwrite). OTHER iff the hook misses the change, ordering is ambiguous, or a full-cover
  composite lands between the glyph draw and the crop change.
- Outcome: **OTHER**. (a) met: 166 `traced-write` C1 pixels with full texel chains.
  (b) met: 9 `roi-changed` rows, 21–80 px each, bboxes exactly the sprite rects, no
  full-cover. ROI→carrier link stable: 17/17 `roi-link-equal`, and 65/65 chain-window crop
  rows `crop-clean`. But (c) is NOT met: packet47240's blit is a steady-state rewrite —
  24/24 traced carrier pixels are **write attempts with no observed change**
  (`write-same-value-unknown`, old==new), the lower-crop hash never moves (`02bfd499`→
  `02bfd499`), so transfer of the C1 pixels into the displayed crop is not observed.
  Contributing scope limit: the 8-per-batch scan-order cap filled with ROI-top background
  rows (src y=375) before reaching the glyph rows (src y≥378).

## 5. What the trace proves (and does not)

- Packet47176 holds **48** C1-state sprite batches (batches 0–47), a full T4 text line
  x95–411/y377–389; GB7B's TSV captured only the 9 crop-overlapping ones (batches 39–47).
  Batch ids count every `DrawPrimitive` batch in the packet in stream order.
- The 8 glyph-run sprites (batches 39–46) each make **traced successful framebuffer
  changes** with full texel chains (`fst=0 lin=1` STQ, T4 nibble + CLUT index + resolved RGBA,
  `test=0x31143 alpha=0x44`). Stroke pixels (nibble 9/f/a, CLUT 17/18/23, e.g.
  `rgba=63808080`) show full-RGBA changes (e.g. old `50ddd1be` → new `63353341`); background
  pixels (nibble=0, clut=0, `rgba=00808080`) show alpha-zeroing writes (e.g. `50e0d4c0` →
  `00e0d4c0`); RGB-preserved cases also occur outside the glyph run (batch 0: `50dfd3b9` →
  `00dfd3b9`). fbmsk/ABE/PABE were not logged, so the mask mechanism behind RGB-preserved
  cases is a gap, not a finding. Zero TEST/ALPHA/z rejections on any of the 190 traced
  pixels (both TEST regs take pass paths on the traced inputs).
- 24 further C1 pixels are `write-same-value-unknown` (tests pass, new==old) — recorded as
  ambiguous, not as changes.
- Packet47240 holds 17 textured carrier batches (0–16, 32px columns x0–510 + bottom row;
  its 4 untextured fbp=0 batches are excluded by the tme filter). Same-column batches
  10–13 match the GB7B rows.
- No full-cover writer intervenes anywhere in the chain window (ROI or crop).
- This identifies CPU-side off-screen text composition + a stable off-screen→display link
  with no observed crop transfer; it does **not** name a glyph producer for the displayed
  text and proves nothing about the paraLLEl damage cause.

## 6. Selected chain table (30/30 rows; full logs private in `run/gb7c2/`)

`chain-selected.tsv` columns:
`tick,packet,path,batch,src_xy,dst_xy,old,new,texel,roi_diff,crop_diff,classification`.
`crop_diff` for 47240 rows is merged from `chain.tsv.crops` (chain.tsv carries `-`; the crop
timeline lives in the `.crops` file by design).

| tick | packet | path | batch | src_xy | dst_xy | old | new | texel | roi_diff | crop_diff | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 600 | 47176 | 2 | 39 | - | - | - | - | rect=(343,378)-(350,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 40 | - | - | - | - | rect=(352,381)-(358,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 41 | - | - | - | - | rect=(361,381)-(366,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 42 | - | - | - | - | rect=(369,381)-(375,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 43 | - | - | - | - | rect=(378,381)-(380,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 44 | - | - | - | - | rect=(382,381)-(390,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 45 | - | - | - | - | rect=(391,381)-(398,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 46 | - | - | - | - | rect=(401,378)-(407,387) fst=0 tme=1 frame=fbp0,fbw8,psm0 tex=tbp0-11017,tbw8,psm20,tw9,th8,tcc1,tfx0,cbp11016,cpsm0,csm0,csa0 test=0x31143 alpha=0x44 | - | - | batch-c1 |
| 600 | 47176 | 2 | 39 | - | - | - | - | - | changed=80 bbox=(343,378)-(350,387) coords=(343,378);(344,378);(345,378);(346,378);(347,378);(348,378);(349,378);(350,378) | - | roi-changed |
| 600 | 47176 | 2 | 40 | - | - | - | - | - | changed=49 bbox=(352,381)-(358,387) coords=(352,381);(353,381);(354,381);(355,381);(356,381);(357,381);(358,381);(352,382) | - | roi-changed |
| 600 | 47176 | 2 | 41 | - | - | - | - | - | changed=42 bbox=(361,381)-(366,387) coords=(361,381);(362,381);(363,381);(364,381);(365,381);(366,381);(361,382);(362,382) | - | roi-changed |
| 600 | 47176 | 2 | 42 | - | - | - | - | - | changed=49 bbox=(369,381)-(375,387) coords=(369,381);(370,381);(371,381);(372,381);(373,381);(374,381);(375,381);(369,382) | - | roi-changed |
| 600 | 47176 | 2 | 43 | - | - | - | - | - | changed=21 bbox=(378,381)-(380,387) coords=(378,381);(379,381);(380,381);(378,382);(379,382);(380,382);(378,383);(379,383) | - | roi-changed |
| 600 | 47176 | 2 | 44 | - | - | - | - | - | changed=63 bbox=(382,381)-(390,387) coords=(382,381);(383,381);(384,381);(385,381);(386,381);(387,381);(388,381);(389,381) | - | roi-changed |
| 600 | 47176 | 2 | 45 | - | - | - | - | - | changed=56 bbox=(391,381)-(398,387) coords=(391,381);(392,381);(393,381);(394,381);(395,381);(396,381);(397,381);(398,381) | - | roi-changed |
| 600 | 47176 | 2 | 46 | - | - | - | - | - | changed=70 bbox=(401,378)-(407,387) coords=(401,378);(402,378);(403,378);(404,378);(405,378);(406,378);(407,378);(401,379) | - | roi-changed |
| 600 | 47176 | 2 | 39 | (281,18) | (343,378) | 50ddd1be | 63353341 | fst=0 lin=1 wrap=(281,18) raw=0000000f nibble=f clut=23 rgba=63808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,99) |
| 600 | 47176 | 2 | 39 | (297,18) | (350,378) | 50e0d4c0 | 00e0d4c0 | fst=0 lin=1 wrap=(297,18) raw=00000000 nibble=0 clut=0 rgba=00808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,0) |
| 600 | 47176 | 2 | 42 | (491,2) | (369,381) | 52e0d5c2 | 1faaa29a | fst=0 lin=1 wrap=(491,2) raw=00000009 nibble=9 clut=17 rgba=1f808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,31) |
| 600 | 47176 | 2 | 42 | (505,2) | (375,381) | 52e4d8c2 | 3489827e | fst=0 lin=1 wrap=(505,2) raw=0000000f nibble=f clut=23 rgba=34808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,52) |
| 600 | 47176 | 2 | 44 | (377,2) | (382,381) | 52e5d9c3 | 70201f31 | fst=0 lin=1 wrap=(377,2) raw=0000000f nibble=f clut=23 rgba=70808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,112) |
| 600 | 47176 | 2 | 44 | (393,2) | (390,381) | 52e1d6c2 | 701f1f31 | fst=0 lin=1 wrap=(393,2) raw=0000000f nibble=f clut=23 rgba=70808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,112) |
| 600 | 47176 | 2 | 46 | (483,39) | (401,378) | 50ece1ce | 00ece1ce | fst=0 lin=1 wrap=(483,39) raw=00000000 nibble=0 clut=0 rgba=00808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,0) |
| 600 | 47176 | 2 | 46 | (497,39) | (407,378) | 50ede2ce | 574e4b55 | fst=0 lin=1 wrap=(497,39) raw=0000000f nibble=f clut=23 rgba=57808080 test=0x31143 alpha=0x44 | - | - | traced-write;rgba-in=(29,5,4,87) |
| 601 | 47240 | 3 | 10 | - | - | - | - | rect=(319,0)-(350,445) fst=1 tme=1 frame=fbp112,fbw8,psm1 tex=tbp0-0,tbw8,psm0,tw10,th9,tcc0,tfx0,cbp0,cpsm0,csm0,csa0 test=0x30000 alpha=0x8000000064 | - | lower 02bfd499→02bfd499 changed=0 | batch-carrier |
| 601 | 47240 | 3 | 12 | - | - | - | - | rect=(383,0)-(414,445) fst=1 tme=1 frame=fbp112,fbw8,psm1 tex=tbp0-0,tbw8,psm0,tw10,th9,tcc0,tfx0,cbp0,cpsm0,csm0,csa0 test=0x30000 alpha=0x8000000064 | - | lower 02bfd499→02bfd499 changed=0 | batch-carrier |
| 601 | 47240 | 3 | 10 | (341,375) | (340,374) | 00dbd0bc | 00dbd0bc | fst=1 lin=1 wrap=(341,375) raw=4edbd0bc rgba=4edbd0bc test=0x30000 alpha=0x8000000064 | - | lower 02bfd499→02bfd499 changed=0 | write-same-value-unknown;rgba-in=(188,208,219,128) |
| 601 | 47240 | 3 | 10 | (342,375) | (341,374) | 00dcd0bc | 00dcd0bc | fst=1 lin=1 wrap=(342,375) raw=4edcd0bc rgba=4edcd0bc test=0x30000 alpha=0x8000000064 | - | lower 02bfd499→02bfd499 changed=0 | write-same-value-unknown;rgba-in=(188,208,220,128) |
| 601 | 47240 | 3 | 10 | - | - | - | - | - | c1hash=c7374e64 equal=1 changed=0 | lower 02bfd499→02bfd499 changed=0 | roi-link-equal |
| 601 | 47240 | 3 | 12 | - | - | - | - | - | c1hash=c7374e64 equal=1 changed=0 | lower 02bfd499→02bfd499 changed=0 | roi-link-equal |

This table is a rendering of `chain-selected.tsv` (30 rows, authoritative).

Row-class totals in `chain.tsv` (320 data rows): `traced-write` 166, `batch-c1` 48,
`roi-clean` 39, `write-same-value-unknown` 24, `batch-carrier` 17, `roi-link-equal` 17,
`roi-changed` 9, capped=0. `chain.tsv.crops`: 65/65 `crop-clean`.

## 7. Receipts

- ssx3 (this dir): `REPORT.md`, `chain-selected.tsv` (30 rows), `pins.txt`, `sizes.txt` —
  committed `[GB7C2]`, `Orchestrated-By: opencode`, no push.
- `run/gb7c2/` (private, not committed): `build-1.log`, `suite-1.log`, `replay-1.log`,
  `chain.tsv` (320 rows, 51,530 B), `chain.tsv.crops` (65 rows), `ppm/vq-000600,000601,000700.ppm`.
- Fork: `[GB7C2]` commit on `gb4-parallel` (3 files: replay test cpp, gs_cpu_backend.cpp,
  gs_cpu_backend.h), `Orchestrated-By: opencode` trailer, no push.

## 8. Gaps stated plainly

- fbmsk, FBA, ABE/PABE and the Z-buffer state are not logged; the RGB-preserved cases
  among the C1 writes are observed but their mask register cause is not captured.
- Carrier sampling stopped at ROI-top background rows (8/batch scan-order cap); no traced
  carrier pixel reaches the glyph rows (src y≥378). A glyph-row-targeted carrier sample
  needs a follow-up probe, not a re-read of this one.
- `write-same-value-unknown` is ambiguous by construction (masked/same-value write vs
  skipped write with passing tests); none were counted as changes.
- The `raw=` value under `lin=1` is a point sample at the wrapped integer coords while the
  resolved `rgba=` may be a 4-point blend; agreement is not asserted per pixel.
- `readGb5Crops` in the chain window assumes the display stays `fbp=112`/`512×448`; a
  mid-window dispfb change would have failed the replay (it did not).
- Batch ids count every `DrawPrimitive` batch in a packet in stream order (not just
  sprites); C1 batches 0–38 lie outside the ROI/crops and were roi-clean.
- Saved frames/crops were hash-checked, not viewed, by this worker; no GPU replay was run.
