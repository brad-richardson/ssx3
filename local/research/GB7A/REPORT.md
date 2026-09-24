# GB7A — title-text producer/state source map (read-only)

## 1. Pins

| Item | Value |
| --- | --- |
| ssx3 HEAD | `b4ab7489034e29bad68ebe14e339339ead046b46` (branch of `[orch] Queue N8D7G replay and parallel source audits`) |
| GB4 worktree `~/dev/ssx3-work/GB4/PS2Recomp` | `f79666938a90b550a4d8f4860e9ec567ad00c48a`, branch `gb4-parallel` — **matches expected `f796669…`** |
| `~/dev/ssx3-work/GB4/parallel-gs` | **absent** (no such directory). Canonical clone `~/dev/parallel-gs` is at `faf6400ee78a2c6169beed7220287420ea0fc14b`; its relation to the GB4 replay build's `PS2X_PARALLEL_GS_SOURCE_DIR=~/dev/ssx3-work/G43/parallel-gs` is **unknown** (not verified in this part). |
| LSP | `goToDefinition`/`findReferences` returned no results in this environment; connections below cite exact caller lines and callee reads instead. |

All line anchors below are in the pinned `f796669` worktree.

## 2. Facts to start from

- GB5D (`local/research/GB5D/REPORT.md`): one matched CPU/paraLLEl replay, 556/556, 1,982,063 packets, 0 null/unsupported. Lower-crop (340,360)-(430,420): ticks 100–200 identical; **copyright damage visible by tick 300** (CPU `02bfd499` vs paraLLEl `f1414a21`); **button labels absent at 600, legible-on-CPU but broken-on-paraLLEl at first sampled appearance tick 700** (`032a9954` vs `d9a35135`), bracket (600,700]. Full-frame diffs 12k–180k px throughout.
- GB6C (`docs/todo.md`): fork `ssx3` pushed `1aaed05→293fd81`; GPU opt-in; **text damage and dark composite persist**.
- Correct-behavior model: if the same texture pixels, clamp/format, alpha and draw coordinates enter both paths, the CPU-visible glyph shape is preserved. Equal predictions cannot discriminate; section 4 names the first observable per alternative plus a null control.

## 3. glyph-packet-p6.txt: what it does and does not identify

**Does:** records tick-950 PATH3 packet index 144266 (1,696 GIF bytes, pklog FNV `cc6dd8df`; capture embedded path=1 is the known metadata defect, corrected by `gb4p4.paths.txt`) as a display-area/composite **candidate**: A+D writes `FRAME_1/TEX0_1/CLAMP_1/SCISSOR_1/XYOFFSET_1/ZBUF_1/TEST_1`, `PRIM=0x006` (sprite), `RGBAQ`, first-strip `XYZ2` pair, and notes a tick-949/950 scan found one full-display sprite packet per tick.

**Does not:** attribute any broken glyph to a unique primitive or texture upload; isolate the observed broken-glyph region from other packets' XYZ positions; name a per-glyph producer; or license a packet-level cause claim. It explicitly requires a packet-level pixel trace or texture-source probe. X5's `packets-949-950.csv` likewise validates stream identity (922/922 rows) without naming a producer. GB5 Part 1 and GB5B further exclude those sampled packets as single-packet CPU-crop writers (zero changed either damaged crop; drop-control leaves final hashes unchanged via repaint).

## 4. Alternatives with first discriminator and null control

| # | Alternative | First exact observable that discriminates it | Null control |
| --- | --- | --- | --- |
| A1 | Guest upload/text source already differs | Per-packet entry log (tick, submit-index, corrected path, byte FNV) at `GS::processGIFPacket` head differs CPU vs parallel replay of the same capture | Same log on two CPU replays must be byte-identical |
| A2 | GS transfer/texture decode differs | Source texel-block dump (TBP0/TBW/PSM/CBP/CPSM/CSM/CSA + pixel FNV) per title-text sprite batch differs while the input packet log (A1) matches | CPU re-run of the dump must reproduce the FNV exactly |
| A3 | Composite/blend state alters correct glyph pixels | Per-batch (TEX0_1, CLAMP_1, TEST_1, ALPHA_1, FRAME_1, XYOFFSET_1, SCISSOR_1, PRIM, sprite rect) log at markers 300/600/700 differs while A1+A2 match | CPU Present vs CPU raw DISPFB1 page-112 read must match (as in p6: 5/5 markers) |

No packet identity is inferred from visual timing anywhere in this report.

## 5. Proposed discriminator: one bounded same-stream diagnostic (not implemented)

Replay the pinned `run/gb4p4.capture.bin` (`a6f75fb3…`, 2,752,955,786 B) with `run/gb4p4.paths.txt` true paths on CPU and paraLLEl backends (`PS2X_GS_REPLAY_BACKEND`), markers 300, 600, 700.
At each marker record: `GB4_FRAME` row (pmode/dispfb/display_fbp/source_fbp), CPU Present hash, CPU raw page-112 hash, paraLLEl Present hash, lower-crop FNV, plus per-sprite-batch state (TEX0_1/CLAMP_1/TEST_1/ALPHA_1/FRAME_1/XYOFFSET_1/SCISSOR_1/PRIM/rect/UV) and source texel-block FNVs for ticks 0–700 transfer census.

Expected values (reproduction of GB5D rows, not new predictions): CPU lower FNV `02bfd499` at 300/600, `032a9954` at 700; paraLLEl `f1414a21` at 300, `d9a35135` at 700 if the defect reproduces; `display_fbp=source_fbp=112`, `dispfb1=9070`, `pmode=ff21`.
Byte/log cap: ≤64 MiB combined new logs (per-batch state lines capped at 20,000 rows; texel dumps capped at 8 MiB; compress closed logs).
Stop rules: stop at the first backend whose A1 packet log differs from the CPU reference (verdict: stream divergence, not a GS defect); else stop at the first marker where A2 texel FNVs differ under equal A1 (verdict: texture/decode stage); else if A1+A2 match but Present differs, verdict is composite/blend/present stage. No source edit, boot, device, or push in this probe. The orchestrator decides which probe to run.

## 6. Source map

Handed back verbatim (`source-map.tsv`, 9 rows):

| step | source_file | line_range | caller_or_data_source | observed_fact | unknown | proposed_probe |
| --- | --- | --- | --- | --- | --- | --- |
| guest-submit | ps2xRuntime/src/lib/ps2_memory.cpp | 2332-2359 | PS2Memory::submitGifPacket; VIF1 XGKICK PATH1, DMA PATH3, PATH2 VIF1 | capture pklog path/length/FNV match live 165/165; path metadata defect corrected by paths.txt | which guest builder emits title-text packets in (600,700] | pklog FNV census ticks 600-700 |
| queue-seam | ps2xRuntime/src/lib/gs/gs_frontend.cpp | 929-958 | GS::processGIFPacket; from executeQueuedCommand, PS2Memory callback, ps2_runtime.cpp:802 | direct=live 59/59; queue=direct 60/60; 556/556 replays | none structural; first instrumentable same-stream point | per-packet entry log at processGIFPacket head, diff CPU vs parallel |
| rawgif-fanout | ps2xRuntime/src/lib/gs/gs_frontend.cpp | 953-958 | m_rawGifBackend → RawGifPacket; shadow ps2_gs_shadow.cpp:448-473 → gif_transfer:461 | parallel replay 1982063 packets, 60 presents, 0 null/unsupported | paraLLEl internal decode of TEX0/CLAMP | hash input bytes at fan-out on both backends |
| register-decode | ps2xRuntime/src/lib/gs/gs_frontend.cpp | 1533-1549 | writeRegisterUnlocked case PRIM; from GIF decode:1003/1088/1235 | p6 packet PRIM=0x006 sprite; no per-glyph primitive | which PRIM/TEX0/CLAMP/TEST/ALPHA draws first damaged glyph | log PRIM+RGBAQ+XYZ per kick, active state per sprite batch 600-700 |
| texture-state | ps2xRuntime/src/lib/gs/gs_frontend.cpp | 1616-1641 | writeRegisterUnlocked TEX0_1/2 + CLAMP_1/2 | p6 TEX0_1=0x0000000268020000, CLAMP_1=0x5 | which pair is active at first damaged glyph | log TEX0/CLAMP/TEX1/FRAME/TEST/ALPHA/XYOFFSET/SCISSOR per batch |
| cpu-raster | ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp | 1126-1185 | DrawSprite from DrawPrimitive:801 | CPU Present = raw page-112 at 5/5 p6 markers; fbp112/dispfb9070 | per-glyph rect/UV/scissor | log sprite rect/UV/TEX0 per DrawSprite 600-700 + crop hash |
| texture-sample | ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp | 1022-1083 | SampleTexture from DrawSprite ~1217/1221, DrawTriangle ~1375; ReadVramUnlocked:646 | GB5B recurring composite cc6dd8df; drop-control unchanged | texel vs wrap vs PSM/CLUT vs TEXA | dump source texel block + FNV per title-text batch on CPU |
| upload-path | ps2xRuntime/src/lib/gs/gs_frontend.cpp | 1111-1158 | uploadImageNative/Unlocked; tryProcessNative:1160+; UploadImage gs_cpu_backend.cpp:1485-1510; capture gs_stream_capture.cpp:192-218 | 66244 transfers, 16264 priv writes, 0 native-upload events | which upload feeds the atlas before 300/700 | transfer-setup + payload-FNV census ticks 0-700 |
| present-read | ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp | 1865-1895 | PresentFromLocalMemory; request gs_frontend.cpp:757-776; latch:778+; replay rows ps2_gs_replay_tests.cpp:698-709 | PMODE ff21; CPU/paraLLEl lower FNVs per §5 | composite vs never-correct | same-stream Present vs raw + state log at 300/600/700 |

Note: 9 data rows plus header (10 TSV lines); the table above renders the same content.

## 7. Gaps stated plainly

- LSP unavailable; connections rest on cited caller/callee lines, not resolved references.
- `~/dev/parallel-gs` pin vs the build's G43 parallel-gs source dir not reconciled (no build or path search budgeted here).
- No per-glyph producer is identified; no GS cause is concluded (per brief).
- `check.py` below validates TSV shape and pinned-path existence only, not semantic correctness.

## 8. Receipts

- `local/research/GB7A/REPORT.md` (this file)
- `local/research/GB7A/source-map.tsv` (9 rows + header)
- `local/research/GB7A/check.py` (TSV header/row-count/path validator)
- Total under 64 KiB. Read-only commands used: `git rev-parse/status/log`, `rg`, reads via editor tool, LSP (no-result). No builds, boots, replays, edits to source, web, upstream contact, or push.
