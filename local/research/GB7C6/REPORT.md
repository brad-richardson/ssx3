# GB7C6 — packet5470 sampled-source design (read-only)

## Predeclared outcomes (brief) and verdict

- **A** = packet+preceding-state evidence yields an exact sampled texel/CLUT value and actual GS address that explains RGB `353341`.
- **B** = packet confirmed as the pixel writer, but sampled source/shape still unproved (dynamic state or texture bytes missing).
- **OTHER** = pin/parser/packet identity failure.

**Verdict: B.** Packet5470/batch10 is proved a *sampling* writer (not a constant fill): the in-packet textured-MODULATE-white path forces
`new_RGB == sampled_texel_RGB`, the observed GB7C5 changed write (`dc302f3b`→`dc353341`) pins the sampled RGB to `353341`,
and code+bytes yield the exact tap quad `(343,378);(344,378);(343,379);(344,379)` with `fx=fy=0` (texel = tap0) at swizzled address
`0x000bae74`. What is **not** recovered without execution is the texel's own preceding-state value: VRAM block-0 content at tick259 is
assembled from 483 IMAGE transfers plus all prior draws, so which upload/draw placed `353341` at `0x000bae74` — i.e. whether the sampled
texel is glyph ink or coincidentally equal RGB — is unproved. No CLUT is involved (CT32 source, `tcc=0`). Single-pixel scope only:
nothing here proves the sprite draws the whole glyph. No OTHER condition (pins, parser, packet identity all verify).

## 0. Pins (all verified read-only)

| Item | Value |
| --- | --- |
| ssx3 HEAD | `1074cad2` (`[orch] Gate GB7C5 watched pixel provenance`); tree clean except new `local/research/GB7C6/` |
| GB4 fork `~/dev/ssx3-work/GB4/PS2Recomp` | `8966b0be` (`[GB7C5]`), branch `gb4-parallel`; all line cites below are at this rev |
| capture `run/gb4p4.capture.bin` | sha256 `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` (two reads agree; `check.py` re-verifies) |
| sidecar `run/gb4p4.paths.txt` | 1,982,063 lines; file line 5471 = `5470 3` (packet index 5470 → corrected path 3) |
| scope | read-only: source reads + capture parsing only. No build, replay, boot, device action, push, board edit (N8D7M5 holds the Mac) |

## 1. Packet5470 identity (packet/field table: `packet-table.tsv`)

| field | value | how verified |
| --- | --- | --- |
| packet index | 5470 (kind-1 ordinal = replay `packets` counter; zero kind-5 in stream so no skew) | independent scan §6; replay `ps2_gs_replay_tests.cpp:575-590,967` |
| tick | 259 | record header bytes |
| embedded path | 1 (known metadata defect) | record bytes; corrected by sidecar |
| corrected path | 3 | `paths.txt` `5470 3`; replay `:582-583` prefers sidecar |
| GIF size | 1696 B | `size == length-14`; replay `:586` same check |
| record offset / length | 6673427 / 1710 | independent scan |
| GIF sha256 | `79f3582fce45dc36a25c454003206a43bbfd001c340a92459a8726fbd0512e31` | in-memory hash (raw bytes never committed) |
| GIF FNV32 | `cc6dd8df` | matches replay `fnv()` (`:20-29`) |
| byte-identity | **identical** to tick950 packet144266 (same SHA) | direct read at X5 offset 158919448 (`X5/packets-949-950.csv`) |
| neighbours | pkt5469 tick258 144 B; pkt5471 tick259 144 B | scan (rules out off-by-one) |

Record layout used: `PS2XGSC1` magic + `u32 len` + `kind u8 + tick u64` + kind-1 body `path u8 + size u32 + GIF bytes`
(`gs_stream_capture.cpp:86-121,154-162`; replay `:280-286,575-590`).

## 2. Decoder parsing of the 1696 bytes (mirrors `GS::processGIFPacket`, `gs_frontend.cpp:983-1049`)

Tag walk consumes exactly 1696 B; 6 tags, `pre=0` throughout, no `FLG=IMAGE` (no in-packet image data):

| tag | FLG/NLOOP/NREG | content |
| --- | --- | --- |
| 0 | PACKED A+D ×11 | FRAME_1, TEX1_1, TEX0_1, ALPHA_1, CLAMP_1, SCISSOR_1/2, XYOFFSET_1, ZBUF_1, TEST_1, TEXFLUSH(0x3F) |
| 1 | REGLIST (PRIM,RGBAQ) ×1 | PRIM=`0x11e`, RGBAQ=`0x3f80000080808080` |
| 2 | REGLIST (UV,XYZ2,UV,XYZ2) ×17 | 34 XYZ2 kicks = **17 sprite batches (0–16)**; last group ends with the bottom-row strip |
| 3 | PACKED A+D ×16 | FRAME_1/2, ZBUF_1/2, XYOFFSET_1/2, FBA_1/2, TEXA, PRMODECONT=1, SCANMSK, COLCLAMP, DTHE, DIMX, PABE, FOGCOL, TEXFLUSH |
| 4 | PACKED A+D ×36 | TEST_1, PRIM=`0x06`, RGBAQ, 32 XYZ2 (= **16 batches 17–32**, untextured, fbp0), TEST_1=`0x500ad` |
| 5 | PACKED A+D ×2 | SCISSOR_1/2 restore |

Batch accounting: sprite needs 2 vertices per `Submit` (`vertexKick`, `:1984-1986,1994-1998`, reset `:2027-2033`); REGLIST XYZ2 always draws
(`writeRegisterUnlocked` `:1596-1615` → `vertexKick(true)`). Probe batch = one `DrawPrimitive` call, counter reset per packet
(`gs_cpu_backend.cpp:529-535,574-578`). So **batch10 = tag2 group10 (11th pair), the only batch that can touch (342,377)**.
Tag3/4/5 postdate batch10: their register writes are *prior-packet state* at batch10 time (values cross-checked in §4).

Batch10 vertices (exact raw GIF fields): v0 `UV=(5120,8) XYZ=(33784,29176,0)`; v1 `UV=(5632,7160) XYZ=(34296,36328,0)`.
With `XYOFFSET_1=(28672,29184)` (`:1665-1672`): unclipped rect `(319,-1)-(350,445)`, scissor-clipped `(319,0)-(350,445)` —
bit-exact with GB7C4's logged carrier batch10 rect (`chain.tsv` tick601/batch10). Contains (342,377). ✓

## 3. GS state at batch10

### 3a. Directly encoded in packet5470 (tags 0–2), decoded per `:1616-1746` field positions

| reg | raw | decoded meaning |
| --- | --- | --- |
| PRIM | `0x11e` | sprite, IIP=1, **TME=1**, FGE=0, ABE=0, AA1=0, **FST=1**, CTXT=0 (`decodePrimRegister` `:24-37`) |
| RGBAQ | `0x3f80000080808080` | vertex (128,128,128,128), Q=1.0 (`:1237-1242` PACKED / `:1550-1561` RGBAQ) |
| TEX0_1 | `0x0000000268020000` | tbp0=0, tbw=8, psm=0 (CT32), tw=10 (1024), th=9 (512), tcc=0, tfx=0 (MODULATE), cbp=0, cpsm/csm/csa/cld=0 |
| TEX1_1 | `0x61` | MMAG=1, MMIN=1 → `linearFilter=true` (`buildDrawBatch` `:2227-2231`) |
| CLAMP_1 | `0x5` | wrapU=1 (CLAMP to size-1), wrapV=1; MIN/MAX=0, unused in mode 1 (`wrapTextureCoordinate` `:770-789`) |
| FRAME_1 | `0xff00000001080070` | fbp=112, fbw=8, psm=1 (CT24), fbmsk=`0xff000000` (`:1721-1730`) |
| SCISSOR_1 | `0x01bf000001ff0000` | (0,0)-(511,447) (`:1697-1706`) |
| XYOFFSET_1 | `0x0000720000007000` | ofx=28672, ofy=29184 (`:1665-1672`) |
| ZBUF_1 | `0x00000001010000e0` | zbp=224, zpsm=Z32, **zmask=1 → no Z write** (`:1731-1739`; `WritePixel` `:2572-2575`) |
| TEST_1 | `0x0000000000030000` | ATE=0 → alpha test passes (`passesAlphaTest` `:791-794`); ZTE decodes to `zpass=true` (`WritePixel` `:2443,2475-2493`); DATE=0 → dest-alpha passes (`:864-884`) |
| ALPHA_1 | `0x0000008000000064` | unused: `prim.abe=0` skips blend (`WritePixel` `:2506-2544`) |

### 3b. Prior-packet state at batch10 time (last writes in packets 0–5469, independent scan)

| reg | value at batch10 | last writer | in-packet later value (tag3) |
| --- | --- | --- | --- |
| PRMODECONT | **1** → `m_prim` = full PRIM reg, so tag1 `0x11e` is effective TME/FST/ABE | pkt5348 tick258 | 1 (same) |
| TEXA | `0x8000000080` (ta0=128,aem=0,ta1=128) | pkt5348 tick258 | same (anyway ignored: CT32 `applyTexa` = identity, `:718-721`) |
| PABE | 0 | pkt5348 tick258 | same (anyway moot: ABE=0) |
| FBA_1 | 0 | pkt5348 tick258 | same (anyway moot: CT24 frame skips FBA, `:2546`) |
| DTHE / COLCLAMP / DIMX / SCANMSK | 0 / 1 / `0x2637405137265140` / 0 | pkt5348 tick258 | same (`scanmsk` never gates sprite pixels; FGE=0 so fog/DIMX/DTHE unused on this path) |
| PRIM (m_primRegister) | `0x4b` (type 3) | pkt5469 tick258 (A+D) | `0x11e` (tag1, effective since PRMODECONT=1) |
| FOG / FOGCOL / TEXCLUT / PRMODE | never written in prefix → init defaults (`:307,323-325`) | — | unused (FGE=0; CT32 needs no CLUT; AC=1) |

Init `m_prmodecont=true` (`:323`); the last pre-5470 write is 1, and no `0x1A` write exists in 5349–5469, so the effective-attribute
question is settled without execution. The one piece of *dynamic register state* that differs from GB7C4's tick601 measurement is none:
every effective value above equals GB7C4's logged carrier row (fst=1,tme=1,abe=0,tex0,tbw8,clamp 5,xyoff,tex1 0x61,texa,frame,alpha,test,pabe,vrt).

### 3c. Computed state (code + §2/§3 values, no execution needed)

`DrawSprite` (`:2719-2738,2762-2785,2810-2818`) at dst (342,377):
`tx=(342-319+0.5)/32`, `ty=(377-(-1)+0.5)/447` → `texUf=343.5`, `texVf=378.5` (= GB7C4 `interpF`, bit-exact).
FST quant (`:2829-2839`) → `sampleU/V=(5496,6056)`; `SampleTexture` linear (`:2666-2678`): minus-half-texel + floor →
taps `(343,378);(344,378);(343,379);(344,379)`, `fx=fy=0.0000` → **texel = tap0 exactly**; CLAMP mode 1 is a no-op in-range.
Tap0 storage address `GSPSMCT32::addrPSMCT32(0,8,343,378)` = **`0x000bae74`** (`ps2_gs_psmct32.h:27-36`); block basis `fbp<<5`
(`ps2_gs_common.h:42-45`): frame word `addrPSMCT32(3584,8,342,377)` = **`0x0019ae38`** = GB7C5 watch address. ✓

### 3d. Not recoverable without execution (explicit unknowns)

- **VRAM texture bytes at tick259** (hence the tap0 *word* at `0x000bae74`): prefix holds 483 kind-3 host→local transfers
  (all dir 0; 478 spsm/dpsm-CT32-class, 5 T8H-class incl. tick256 dbp5760 = GB7C5 seq1) and 483 IMAGE groups (5,101,824 B), plus every
  prior draw — reassembling block-0 content is emulation, not parsing. Zero kind-5/6/7 records in prefix (audit matches GB7C5 §1).
- Which upload/draw first placed `353341` at `0x000bae74` (the true glyph-ink producer) — same reason.
- GPU-side behaviour — CPU replay path only (as in GB7C4/GB7C5).

## 4. Writer proof (why the sprite *samples* rather than fills)

With `tcc=0/tfx=0` MODULATE and vertex (128,128,128,128): `combineTexture` (`:894-914`) gives
`color.RGB = texel.RGB` exactly (`(tr*128)>>7 = tr`), `color.A = 128`. `WritePixel`: TEST/Z/DATE pass (§3a), no blend (ABE=0),
CT24 skips FBA, `fbmsk` keeps dest alpha: stored word = `(old_alpha<<24) | texel_RGB`. GB7C5 measured
`dc302f3b`→`dc353341` — alpha `dc` preserved, RGB replaced — so the path forces **sampled texel RGB = `353341`** at tick259.
A constant fill would have written vertex grey `808080` (TME=0) or tag4-style flat blue; the observed `353341` refutes both.
This confirms B's premise (packet = the pixel's writer *by sampling*) while leaving the texel's own producer open.

## 5. Why B, not A or OTHER

- Not OTHER: pins verify (capture SHA ×2, sidecar line, fork rev); the GIF walk consumes exactly 1696 B with 6 well-formed tags;
  batch10 identity is over-determined (probe counting + vertex rect + GB7C4 rect match + watched-pixel containment).
- Not A: A demands the texel/CLUT value *from packet+preceding-state evidence*. The value `353341` here is inferred **backwards**
  from GB7C5's destination measurement through the path equations — the forward direction (which preceding upload/draw wrote
  `0x000bae74`, i.e. glyph ink vs coincidentally equal RGB) is unexecuted by design of this part. No CLUT exists to resolve
  (CT32/TCC=0), so the remaining "sampled source/shape" gap is purely the texture-byte history.
- B matches exactly: confirmed writer + missing texture-byte history. One matching RGB at one pixel proves nothing about the whole
  glyph (brief scope rule); tag4's 16 fbp0 batches and the other 16 strips are untouched by this verdict.

## 6. Recommended next action (brief asks for exactly this)

**Next one-replay default-OFF tap** (settles B→A by directly observing the tick259 texel):
GB7C4-style probe on the direct-CPU replay of `gb4p4.capture.bin` + `paths.txt`, stopping after the marker-301 sample
(tick259 + margin; STEP=50): per-packet context; on packet **5470**, batch **10**, dst pixel **(342,377)** log TEX0_1/CLAMP_1/TEX1_1/
FRAME_1/TEST_1/ALPHA_1/XYOFFSET_1/PRIM/RGBAQ, both vertex UV/XYZ, interp/quant UV, the four tap coords + swizzled addresses +
`ReadVramUnlocked` words, TEXA-resolved texel, and TEST/ALPHA/fbmsk verdict with old/new words. Predicted (from §3c):
taps `(343,378)..`, tap0 addr `000bae74`, texel RGB `353341`, new word `dc353341`.
OFF control: identical env minus the trace flag through the same stop marker; `GB4_FRAME`/PPM hashes must equal ON
(GB7C5 §3 pattern), otherwise the run is void. No pixel poke in this step.
**Later gate, only after the source is established:** matched CPU/GPU comparison at this exact packet/address
(same-stream A1 log equality first per GB7A §4, then texel/pixel diff) — not before.

## 7. Receipts and budget

- This dir: `REPORT.md`, `packet-table.tsv` (identity + tag + state tables, machine-readable), `check.py`, `check-result.txt`.
  Raw GIF/capture bytes never committed (hashes + offsets + bounded fields only). Total new text ≈ 40 KiB (cap 512 KiB).
- `check.py` verifies: capture SHA; independent scan (index/tick/embedded-path/size/GIF-SHA/record-offset of packet5470;
  `paths.txt` `5470 3`; neighbour ticks); X5-offset read of packet144266 and SHA equality; exact 1696-B/6-tag walk with the
  batch-33 accounting and batch10 rect/tap/address recomputation; presence of every §3 table field or explicit `UNKNOWN`.
  It asserts no semantic glyph or GPU cause. Result: see `check-result.txt`.
- Commit `[GB7C6]` with `Orchestrated-By: opencode`, no push. The orchestrator gates.
