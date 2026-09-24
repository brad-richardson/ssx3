# GB7C3 — glyph-row carrier discriminator design (read-only, no run)

Pinned rev: GB4 private fork `~/dev/ssx3-work/GB4/PS2Recomp` @
`7bd834900b3e34662f53d5eaba63461d692b6b19` (verified `git rev-parse HEAD`).
Trace: `../run/gb7c2/chain.tsv` (320 data rows) + `chain.tsv.crops`
(65 rows) + `ppm/vq-00060{0,1}.ppm` (P6 512x448). No fork edit, build,
replay, device, push, or glyph-cause verdict in this part.

## 1. What the full trace establishes (source rows, not rectangles)

- C1 packet47176/tick600/path2: 48 sprite batches; every traced pixel is
  `fst=0 lin=1` STQ, `test=0x31143 alpha=0x44`, frame fbp0/fbw8/psm0(CT32),
  tex tbp0-11017/tbw8/psm20(T4). TEST decode: ATE=1, ATST=1 (ALWAYS),
  AFAIL=FB_ONLY, DATE=0, ZTE=1 (ALWAYS) — pass paths on traced inputs.
- Carrier packet47240/tick601/path3: batches 0–16; textured batches are
  `fst=1 lin=1 tme=1`, frame fbp112/fbw8/psm1(CT24),
  tex tbp0-0/tbw8/psm0(CT32, 1024x512), `test=0x30000 alpha=0x8000000064`
  (ATE=0, ZTE=1 ALWAYS, DATE=0 — always writes, modulo fbmsk/blend).
- All 24 carrier samples satisfy src_xy == dst_xy + (1,1) with wrap == src
  (checker-verified); sampled rows are ROI-top background (src y=375) only.
  Glyph rows (src y>=378) were never carrier-sampled — the GB7C2 gap.
- 65/65 crop rows clean; tick600/601 lower-crop hash `02bfd499` both sides.

## 2. Source connections (pinned rev, exact lines)

- `framePageBaseToBlock: fbp << 5` —
  `ps2xRuntime/include/runtime/gs/ps2_gs_common.h:42-45`. C1 block = 0;
  carrier frame block = 112<<5 = 3584; carrier tex block = 0.
- `DrawSprite`: display offset subtract `xyoffset>>4` (`gs_cpu_backend.cpp:1927-1933`);
  FST sprite UV interpolation (`:1970-1986`) and per-pixel loop (`:2011-2037`).
- `SampleTexture`: FST path `u/16` (`:1831-1836`); bilinear `texUf-0.5`,
  4 taps, `lround` blend (`:1879-1917`). Trace `raw=` is the point sample at
  wrapped coords, `rgba=` the blend (GB7C2 §8 gap: agreement not asserted).
- TEST/alpha/mask: `passesAlphaTest`/`classifyAlphaTest` (`:384-455`),
  `passesDestinationAlphaTest` (`:457-477`), blend + `fbmsk` + FBA
  (`WritePixel :1708-1777`). C1/carrier TEST regs both take pass paths;
  `fbmsk`, ABE/PABE, vertex RGB (matters: carrier `tcc0`+MODULATE uses
  vertex color, `:487-506`), CLAMP register, and `xyoffset` values are
  NOT in the trace — ambiguities, not findings. (LSP hover on DrawSprite
  returned no result; connections confirmed by direct read at pinned rev.)

## 3. Candidate pairs (`candidate-pairs.tsv`, authoritative)

Linear offsets assume fbw8/CT32 row stride 2048 B (`fbStride`, same header
`:36-40`); the swizzled VRAM word address is marked unknown (address
function not read — deliberately, per budget).

| cand | C1 src (post-47176 word) | carrier dst + batch | neighborhood if transported |
| --- | --- | --- | --- |
| A | (343,378) `63353341` nibble f/clut23, lin off 0xBD55C | (342,377) batch 10 (319,0)-(350,445) | taps (342,377),(343,377),(342,378),(343,378-poked), fx=fy=0.5 |
| B | (369,381) `1faaa29a` nibble 9/clut17, lin off 0xBEDC4 | (368,380) batch 11 (351,0)-(382,445) | taps (368,380),(369,380),(368,381),(369,381-poked) |
| C | (382,381) `70201f31` nibble f/clut23, lin off 0xBEDF8 | (381,380) batch 11 | taps (381,380),(382,380),(381,381),(382,381-poked) |
| D | (407,378) `574e4b55` nibble f/clut23, lin off 0xBD65C | (406,377) batch 12 (383,0)-(414,445) | taps (406,377),(407,377),(406,378),(407,378-poked) |

dst = src-(1,1) follows the observed carrier shift; every dst lies inside
its batch rect (checker PASS). Prior dst word at each glyph-row dst is
**unknown** (trace sampled only the y=374 dst row); exact post-transport
word is additionally unknown (vertex RGB, CLAMP mode, fbmsk/ABE, 4-tap
reads not logged). Predictions below are directional for this reason.

## 4. Single perturbation design (candidate A; OFF control; no run here)

- Injection: env-gated private replay-harness poke of fbp0-block word for
  (343,378) to a unique value (e.g. `0xDEAD0000`-family, distinct from all
  trace words) applied after packet47176 completes and before packet47240
  opens; reversible (hook removed/flag off = restore); no other writer
  (no broad writer; OFF control = identical replay without the poke).
- Observable: carrier dst (342,377) word in fbp112-block + its 4-tap
  neighborhood, logged with the GB7C2 independent-old/new shape.
- (a) Carrier transports: dst (342,377) moves ~1/4 per channel toward the
  poked texel (one of four bilinear taps changed; `lround` per channel),
  RGB only directionally (carrier TCC0/MODULATE folds unknown vertex RGB;
  dest is CT24 so no dest-alpha preserve; fbmsk unknown). OFF control dst
  equals base.
- (b) Carrier does not transport: dst (342,377) equals the OFF-control word
  exactly; neighborhood taps excluding (343,378) unchanged.
- PSM24/32 note: texel CT32 passes `applyTexa` unchanged (`:311-314`);
  dest CT24 keeps 32-bit store path without alpha-preserve (`:1653`,
  `:1772-1777`); a nonzero fbmsk would make (a)==(b) for masked channels —
  if fbmsk is found nonzero at 47240, this pixel is withdrawn and the table
  is handed back with OTHER (do not propose a masked pixel).
- Caps/budget/stop: bounded log <= 20,000 rows / 8 MiB (GB7C2 shape), one
  build + one replay; stop after marker-700 sample. PASS = (a) with OFF
  control clean; OTHER = equal predictions (mask/filter), ambiguous write,
  or intervening full-cover writer. No GPU claim follows either way.

## 5. Gaps (missing evidence, plainly)

Prior glyph-row dst words; carrier STQ/vertex RGB per batch; CLAMP,
xyoffset, fbmsk, ABE/PABE at 47240; swizzled VRAM word addresses;
4-tap neighbor reads around each candidate src. Checker
(`check_provenance.py`, output `check_provenance.out`): OVERALL PASS on
trace provenance, rects, shift, offsets, PPM dims — it does not prove
transport.

Receipts (this dir): `REPORT.md`, `candidate-pairs.tsv` (4 data rows),
`check_provenance.py`, `check_provenance.out`. No implementation or run.
