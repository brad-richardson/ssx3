# GB7C1 — off-screen text pixel-trace design (source audit, read-only)

## 1. Pins and scope

| Item | Value |
| --- | --- |
| GB4 worktree `~/dev/ssx3-work/GB4/PS2Recomp` | `09d583a36ee62c165ce9e0473b945821a7a128f7`, branch `gb4-parallel`, clean (`git status --short` empty) — matches brief |
| G43 `~/dev/ssx3-work/G43/parallel-gs` | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` — matches brief |
| Null-control inputs | pinned stream SHA `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` + `run/gb4p4.paths.txt`; neither read nor copied in this part |
| GB7B inputs | `local/research/GB7B/REPORT.md`, `ORCH-GATE.md`, `candidates.tsv` (16 rows); GB7A gate + `source-map.tsv` (9 rows) |
| Actions taken | reads + `git`/`rg` only; LSP probed 5 ways, no server responded (see §5). No source edit, build, replay, device, web, upstream, or push |

All line anchors below are in the pinned `09d583a` worktree.

## 2. Question and answer in one paragraph

A default-OFF CPU diagnostic **can** sample a pixel's old/new value around an
`fbp=0` T4-atlas sprite and track it into the `fbp=112` blit and the displayed
crop without changing render output, because every needed value is already in
hand on the direct-CPU path: the old value is read at
`gs_cpu_backend.cpp:1181`, the new value is computed just above
`:1294`, the source texel chain is pure reads (`:1366` + `:1385` +
`:1319`), and the crop read already exists as `readGb5Crops`
(`ps2_gs_replay_tests.cpp:191-218`), which aliases live VRAM (`:400`) and is
proven per-packet by GB5B (`:518-528` before, `:569-576` after). Two gaps must
be closed by the implementation brief: no intra-packet batch sequence exists
(4 sprites share packet 47176), and the exact post-glyph same-column display
blit is not in the 16-row table (the named exemplar `p47117` precedes the
glyph draw) — it is a lookup in the private `candidates-full.tsv`, not a
guess. `trace-map.tsv` (10 rows) is the evidence table.

## 3. The two concrete candidates

- **C1 — tick600 packet47176, path 2.** Four `sprite/exact` batches to
  `fbp=0`, `T4 tbp0=11017/tbw=8/cbp=11016`, `TEST=0x31143 ALPHA=0x44`,
  rects `(343,378)-(350,387)` + `(352,381)-(358,387)` +
  `(382,381)-(390,387)` + `(401,378)-(407,387)`; texel4
  `e856e77a/67fec805/3d26b932/e7ff9185` (`candidates.tsv` rows 8–11).
- **C2 — tick699 packet59894, path 2.** Same atlas/state, rects
  `(393,405)-(398,411)` + `(400,405)-(405,411)`; texel4
  `825eecf6/67fec805` (rows 15–16). Last pre-700 glyph-sized runs,
  different text row.
- **Display-blit exemplars (resamples, not producers).** Tick600 `p47117`
  path 3, `(319,0)-(350,445)` → `fbp=112` from `CT32 tbp0=0` (row 12);
  tick601 `p47240` path 3, `(383,0)-(414,445)` (row 13). `p47117` covers
  C1's x-range but precedes the glyph packet, so C1's carrier is the
  **next** same-column blit after 47176 (full-TSV lookup).

## 4. Chain walk (each site -> trace-map row)

1. **Packet seam** (`packet-seam`): `GS::processGIFPacket`
   (`gs_frontend.cpp:929`; tick/index/path latched `:947-949`); the replay
   harness sets GB7B context at `ps2_gs_replay_tests.cpp:532` before calling
   `:541`. True path comes from `paths.txt` (`pathId`), correcting the known
   embedded-path defect.
2. **Draw entry** (`draw-entry`): `GSCpuBackend::Submit` (`:715-721`) calls
   `DrawPrimitive(batch)` at `:720`; the GB7B hook at `:999-1000` returns
   early unless enabled, so OFF is byte-identical.
3. **Sprite rect**: `DrawSprite` (`:1437`) subtracts XYOFFSET (`:1444-1450`),
   clips to scissor (`:1470-1473`), interpolates UV per pixel (`:1512-1533`);
   FST sampling calls `SampleTexture` at `:1528`. The GB7B probe mirrors this
   rect exactly (`:820-843`).
4. **Texture sample** (`texture-sample-C1`): `SampleTexture` (`:1333`)
   computes FST texels (`:1351-1352`), wraps per CLAMP (`:1363-1364`; `0x5`
   = CLAMP/CLAMP), reads the T4 nibble at `:1366`, resolves the CLUT entry
   at `:1385` via `resolveClutIndex` (`:403-437`; T4 CSM1 =
   `(csa&0xF)<<4 | idx&0xF`, swizzled `:426`) and `GSMem::ReadCT32` (`:1319`).
5. **Raster write** (`raster-write-C1`): `WritePixel` (`:1137`) classifies
   TEST (`:1162`), reads the old framebuffer value only when needed (`frmw`,
   `:1175`) at `:1181`, blends under ABE (`:1231-1269`), packs the new pixel
   (`:1276`) and writes it at `:1294`. Frame address: `fbp<<5`
   (`ps2_gs_common.h:42-45`), so `fbp=0` → block 0; T4 `tbp0=11017`,
   `cbp=11016` stay in block units.
6. **VRAM mapping** (`vram-map`): `ReadVramUnlocked` (`:745-750`) /
   `WriteVramUnlocked` (`:758-763`) dispatch `m_readVramFuncs` /
   `m_writeVramFuncs[psm&0x3F]`; the unlocked variants are what `:1181`,
   `:1294`, `:1366` already call, so a hook must use them (the locked
   wrappers would deadlock under `Submit`'s mutex at `:717`).
7. **Display blit** (`display-blit`): same `DrawSprite` path with
   `tex tbp0=0` (block 0 = the glyph page) → `fbp=112` (block 3584); per-pixel
   srcUV→dst mapping observable at `:1528` with old/new at `:1181`/`:1294`.
8. **Present crop** (`present-crop`): `PresentFromLocalMemory` (`:2176`) →
   `CopyFrameToHostRgba` (`:2215`, reads via `:2115`) → `readGb5Crops`
   lower-crop hash (`:215-216`). GB5B proves the per-packet before/after
   pattern on live VRAM.
9. **C2** (`glyph-C2-rect-write`): same sites as C1; watch the `:779`
   stop-after-700, which may cut C2's following blit.
10. **Null control** (`null-control`): GB7B §3 receipts (lower FNV
    `02bfd499` at 600, `032a9954` at 700; `pmode=ff21 dispfb1=9070
    fbp=112`).

Single-pixel traceability without output change: yes — the hook only adds
`ReadVramUnlocked` calls (side-effect-free) and reads values already computed
(`:1294` pixel, `:1366` texel); gated on a default-OFF flag exactly like the
GB7B hook at `:999-1000`, the OFF path is one branch per batch.

## 5. Call-edge confirmation

LSP `goToDefinition` (×2), `findReferences`, `hover`, and `documentSymbol`
against `gs_cpu_backend.cpp` all returned no results in this environment —
the same LSP absence GB7A §7 records. Edges below are confirmed by exact
caller lines paired with callee reads: `Submit:720` → `DrawPrimitive:997`;
`DrawPrimitive:999-1000` → `NoteGb7bCandidate:787`; `:1111-1112` →
`DrawSprite:1437`; `DrawSprite:1528/1532` → `SampleTexture:1333`;
`:1541` → `WritePixel:1137`; `WritePixel:1181/1294` →
`Read/WriteVramUnlocked:745/758`; `SampleTexture:1366/1385` →
`ReadVramUnlocked` / `LookupCLUT:1303` → `GSMem::ReadCT32:1319`;
replay `:532` → `ps2xGb7bSetPacketContext` → `:541`
`processGIFPacket:929`; `:400` aliasing makes `:522`/`:571` true live
before/after reads.

## 6. Proposed next brief (GB7C implementation, bounded)

- **Builds/suite/replay:** at most one incremental build (GB7C probe on
  `gb4-parallel`, default OFF, exclusive with GB5/GB5B like GB7B), one
  flag-unset suite gate (556/556, `PS2X_ENABLE_DIAG_TAPS` untouched), one
  direct-CPU replay of the pinned stream + `paths.txt` through tick 700
  (`PS2X_GS_REPLAY_GB7B_TRACE`-style env, stop extended to the first
  post-59894 same-column blit or the tick-701 sample).
- **Caps:** hard log caps ≤8 MiB and ≤20,000 rows (GB7B shape:
  stop-writing-at-cap, `capped` flag).
- **Pixel/ROI bounds:** trace ≤8 pixels total — one interior pixel per C1
  sibling sprite (4) + one per C2 sprite (2) + 2 spares; off-screen ROI log
  `(340,375)-(410,415)` old/new only for traced pixels.
- **Source-texel evidence:** per traced pixel, log `(sampleU,sampleV)`,
  T4 nibble + parity, `linearFilter` bit, CLUT index + resolved RGBA, and
  the `combineTexture` inputs (`:1540`).
- **Before/after crop evidence:** `readGb5Crops` lower-crop hash +
  `changedPixels` per packet in ticks [600,601] and [699,700] only
  (~170 Presents); plus the off-screen ROI hash per packet in the same
  windows.
- **Preregister:** PASS iff (a) a traced C1/C2 pixel's old→new change is
  logged with its texel chain, (b) the off-screen ROI diff is glyph-shaped
  (`changedPixels` > 0 clustered inside a candidate rect, not full-crop),
  and (c) the first following same-column `fbp=112` blit preserves it
  (post-blit lower-crop hash moves toward the ROI content, no intervening
  full-screen overwrite). OTHER iff the hook misses the change, two
  same-tick writers make ordering ambiguous, or a full-cover composite
  lands between the glyph draw and the crop change.
- **Cause discipline:** name the glyph *producer* (packet/batch/pixel)
  only; no paraLLEl cause claim follows from CPU-only data (GB7A A2/A3
  need the texel/state diff against the parallel replay, a later brief).
- **Missing-hook check:** no stop needed — the only additions are an
  intra-packet batch counter in `Gb7bPacketContext`, TEST/ALPHA/blend-input
  logging at traced pixels, and wiring the existing `readGb5Crops`
  per-packet pattern to the new flag. If the traced-pixel count or the
  windowed Presents threaten the caps, cut C2 first (C1 alone answers the
  question).

## 7. Gaps stated plainly

- Exact post-47176 same-column blit index unresolved here (16-row table
  only; full TSV is private to `run/gb7b/` and was not searched under the
  time box). The mechanism (next column blit in tick order) is certain; the
  index is a lookup.
- Whether C1/C2 batches are FST (`prim.fst`) or STQ is not recorded in
  `candidates.tsv`; it decides the `:1528` vs `:1532` sample path and must
  be logged by the probe (state is in hand at `DrawSprite`).
- T4 nibble unpack internals live in the PSM handler table (`:631`); cited
  by dispatch, not re-read line by line.
- No statement is made about paraLLEl behavior, glyph identity beyond
  rectangles, or which texel bits differ across backends — all reserved for
  later briefs.
