# GB7B — spatial title-glyph candidate probe

## 1. Pins

| Item | Value |
| --- | --- |
| GB4 worktree `~/dev/ssx3-work/GB4/PS2Recomp` | `f79666938a90b550a4d8f4860e9ec567ad00c48a`, branch `gb4-parallel` — matches expected |
| `~/dev/ssx3-work/G43/parallel-gs` | `3a66c1976170cbc2cb53a3593fabbc7c4b2ccfbd` |
| capture `run/gb4p4.capture.bin` (2,752,955,786 B) | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` via `shasum -a 256` and `sha256sum` (two independent reads, match) |
| path sidecar | reused `run/gb4p4.paths.txt` (1,982,063 lines); capture not copied |
| runner-dir diff `git diff 14b1e5cb gb4-parallel -- ps2xRuntime/src/runner` | empty (0 lines) |
| ssx3 HEAD at work | `388ff9ed` |

## 2. Probe (default-OFF, bounded)

Three-file scope only (brief path correction accepted: the GS CPU header
lives at `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`):

- `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`: `Gb7bPacketContext`
  plus `ps2xGb7bProbeOpen/Close/SetPacketContext/Enabled` declarations and
  one private `NoteGb7bCandidate` method.
- `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`: probe state (20,000-row /
  8 MiB caps, stop-writing-at-cap), `DrawPrimitive` hook gated on
  `enabled` (early return otherwise — rendering byte-identical), exact
  clipped rect for sprites (mirrors `DrawSprite`), clamped vertex bbox for
  other prims (marked `bbox`), overlap pixel counts vs
  `(320,120)-(420,205)` and `(340,360)-(430,420)`, effective
  FRAME/TEX0/CLAMP/TEST/ALPHA + UV/STQ, and a ≤4-sample `SampleTexture`
  fingerprint (`texel4=%08x`; `none(untextured)` when `tme==0`). No packet
  tracer, no render-output change.
- `ps2xTest/src/ps2_gs_replay_tests.cpp`: `PS2X_GS_REPLAY_GB7B_TRACE`
  setup (direct-CPU only, exclusive with GB5/GB5B), per-packet context set
  before `processGIFPacket`, stop after the marker-700 sample, close +
  `GB7B replay reached marker 700` assertion.

Fork commit: `09d583a` `[GB7B]` on `gb4-parallel` with `Orchestrated-By: opencode`
(see §6).

## 3. Budget: 1 build, 1 taps-OFF suite, 1 CPU replay

| Step | Command (from `~/dev/ssx3-work/GB4/PS2Recomp`) | Result |
| --- | --- | --- |
| build | `cmake --build ../build --target ps2x_tests > ../run/gb7b/build-1.log 2>&1` | exit 0; `ps2x_tests` 8,197,880 B; `PS2X_ENABLE_DIAG_TAPS=OFF` untouched |
| taps-OFF suite | `../build/ps2xTest/ps2x_tests > ../run/gb7b/suite-1.log 2>&1` (flag unset) | 556/556 pass |
| CPU replay | `PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=300,600,700 PS2X_GS_REPLAY_PPM_DIR=../run/gb7b/ppm PS2X_GS_REPLAY_GB7B_TRACE=../run/gb7b/candidates-full.tsv ../build/ps2xTest/ps2x_tests > ../run/gb7b/replay-1.log 2>&1` | 556/556 pass; `GB4_REPLAY_SUMMARY mode=direct backend=cpu packets=59904 priv=3989 transfers=624 markers=700 samples=14`; `GB4_FRAME` 300/600/700 all `pmode=ff21 dispfb1=9070 display_fbp=112 source_fbp=112`, presents `282ce22d/a6948f2/97b4641e` |

Probe yield: `candidates-full.tsv` 17,898 rows / 7,414,101 B — under both
caps (20,000 rows, 8 MiB); capping never triggered. Classification split:
11,563 overlap-candidate / 4,671 untextured-overwrite / 1,664
full-crop-overwrite; prims 10,108 sprite / 7,790 triangle; ticks 40–699;
paths 1/2/3 all present. Render path unperturbed: lower-crop FNVs from the
three PPMs reproduce GB5D CPU values exactly (`02bfd499` at 300/600,
`032a9954` at 700).

## 4. Candidate table (16 of 17,898 rows; full log private in `run/gb7b/`)

`candidates.tsv` columns:
`tick,packet_index,path,rect,crop,texture_state,source_fingerprint,classification,reason`.
Selection: earliest display writer per shape, first small textured batches
per crop, full-cover composites, T4-atlas glyph-sized runs at 600/650/699,
one untextured representative. No glyph identity is inferred from overlap.

| tick | packet_index | path | rect | crop | texture_state (short) | source_fingerprint | classification | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 1 | 3 | (319,0)-(350,445) | upper=2635;lower=660 | sprite/exact, frame fbp=112, tex CT32 tbp0=0 | texel4=69691905 | overlap-candidate | first display column blit touching both crops; full-height resample, not a glyph producer |
| 43 | 15 | 3 | (351,0)-(382,445) | upper=2720;lower=1920 | sprite/exact, frame fbp=112, tex CT32 tbp0=0 | texel4=babad785 | overlap-candidate | repeat display blit, different texels; resample |
| 40 | 1 | 3 | (320,0)-(351,447) | upper=2720;lower=720 | sprite/exact, untextured, frame fbp=112 | none(untextured) | untextured-overwrite | fade/composite overwrite, not a glyph producer |
| 247 | 2858 | 1 | (416,383)-(432,447) | lower=518 | triangle/bbox, frame fbp=0, tex CT32 tbp0=13257 | texel4=69691905 | overlap-candidate | first small textured batch touching lower crop; off-screen column, constant vertex-texel fp |
| 247 | 2866 | 1 | (416,0)-(432,256) | upper=340 | triangle/bbox, frame fbp=0, tex CT32 tbp0=13449 | texel4=69691905 | overlap-candidate | first small textured batch touching upper crop; off-screen column |
| 256 | 5151 | 1 | (55,20)-(465,345) | upper=8500 | triangle/bbox, frame fbp=0, tex T8 tbp0=5760 cbp=10764 | texel4=c3fc27a6 | full-crop-overwrite | upper full-cover composite to off-screen; composite candidate only |
| 256 | 5145 | 1 | (252,202)-(511,447) | lower=5400 | triangle/bbox, frame fbp=0, tex T8 tbp0=4736 cbp=10760 | texel4=af10936f | full-crop-overwrite | lower full-cover composite to off-screen; composite candidate only |
| 600 | 47176 | 2 | (343,378)-(350,387) + 3 sibl. | lower≤80 each | sprite/exact, frame fbp=0, tex T4 tbp0=11017 cbp=11016 | texel4=e856e77a… | overlap-candidate | glyph-sized T4-atlas sprites to off-screen; glyph-composition candidates, need pixel-trace proof |
| 600 | 47117 | 3 | (319,0)-(350,445) | upper=2635;lower=660 | sprite/exact, frame fbp=112, tex CT32 tbp0=0 | texel4=05ee73ca | overlap-candidate | contemporary display blit; resamples off-screen composite |
| 601 | 47240 | 3 | (383,0)-(414,445) | upper=2720;lower=1920 | sprite/exact, frame fbp=112, tex CT32 tbp0=0 | texel4=050b15f1 | overlap-candidate | contemporary display blit; resample |
| 650 | 53328 | 2 | (343,378)-(350,387) | lower=80 | sprite/exact, frame fbp=0, tex T4 tbp0=11017 | texel4=e856e77a | overlap-candidate | identical repeat of tick-600 glyph run; recomposition |
| 699 | 59894 | 2 | (393,405)-(398,411),(400,405)-(405,411) | lower=42 each | sprite/exact, frame fbp=0, tex T4 tbp0=11017 | texel4=825eecf6/67fec805 | overlap-candidate | last pre-700 glyph-sized runs, different text row |

Key negative result: **zero** display-buffer (`fbp=112`) writes with
rect area < 2000 px touch either crop at any tick ≤ 700. All glyph-sized
textured batches target the off-screen buffer (`fbp=0`); all
full-cover composites also target `fbp=0`; the display crops are written
only by full-height column resamples (`tbp0=0` CT32 → `fbp=112`). So no
unique display-side glyph batch exists to isolate under this cap — the
visible text arrives via off-screen composition plus resampling blits.

## 5. Viewed frames (`run/gb7b/frame-*.png`, `crop-*-*.png`)

| Tick | Evidence |
| --- | --- |
| 300 | `crop-lower-300.png`: `Reserved.` copyright glyphs legible on CPU (lower FNV `02bfd499` = GB5D CPU value); `crop-upper-300.png`: large logo graphic, no small glyphs |
| 600 | `crop-lower-600.png`: `Reserved.` unchanged (`02bfd499`); no button labels |
| 700 | `crop-lower-700.png`: `Select / Previous / Options` + pad icons legible on CPU (lower FNV `032a9954` = GB5D CPU value); `crop-upper-700.png`: transition bar (`nt` / `he Mountai`) |

## 6. Receipts

- `local/research/GB7B/REPORT.md` (this file), `candidates.tsv` (16 rows),
  `pins.txt`, `sizes.txt` — all < 256 KiB combined.
- `run/gb7b/` (private, not committed): `build-1.log`, `suite-1.log`,
  `replay-1.log`, `candidates-full.tsv` (17,898 rows, 7,414,101 B),
  `ppm/vq-000300,000600,000700.ppm`, `frame-*.png`, `crop-*-*.png` —
  ~10 MB total (< 64 MiB).
- Fork: `[GB7B]` commit on `gb4-parallel` (files: replay test cpp,
  gs_cpu_backend.cpp, gs_cpu_backend.h), `Orchestrated-By: opencode`
  trailer, no push. ssx3: `[GB7B]` commit of this dir + brief, no push.

## 7. Gaps / next observable (no cause verdict per brief)

- No per-packet proof of which batch changes display-crop pixels: the
  probe logs spatial overlap + state, not pixel deltas. Overlap alone was
  not used to name a glyph producer.
- STQ-mapped triangle fingerprints sample shared vertex texels
  (repeated `texel4=69691905`); they discriminate poorly for that shape —
  reported honestly, not relied upon.
- T4-atlas (`tbp0=11017/cbp=11016`) glyph-sized runs at 600–699 are the
  strongest composition-side candidates but remain unproved.
- Named next observable: a per-packet display-crop hash trace (GB5-style
  before/after crop hash per packet in (600,700] plus a source-texel dump
  of atlas `tbp0=11017`) to prove which composite packet first changes
  lower-crop pixels and which texels feed it. No second probe added here.
