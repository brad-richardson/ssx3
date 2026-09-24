# N8D7K — independent selected-address oracle (read-only audit)

**State: oracle found (fork CPU table helper, independent of G43 `swizzle_PS2`).
No source edit, build, boot, device, upstream contact or push. No cause verdict.
Table written first: [address-map.tsv](address-map.tsv) (10 rows).**

## 1. Pins

| Item | Pin |
| --- | --- |
| Fork (oracle side) | `~/dev/PS2Recomp` HEAD `eac6cba6677663d25b31d7228d7d08eb3ee1c275` (branch `ssx3`, status `behind 39` vs fork remote — read-only, no fetch) |
| G43 (cross-check side) | `~/dev/parallel-gs` HEAD `faf6400ee78a2c6169beed7220287420ea0fc14b` |
| Repo (receipts only) | `~/dev/ssx3` HEAD `50714ce7aac23a7dd074bd020e86fb6a0da97258`, branch `main`, tree as found |
| Frame under test | N8D7I tick 2050: FBP=112, FBW=8, PSM=1 (PSMCT24), DBX=0, DBY=0, phase=0, stride=2, 512×224, mask 4194303 |
| Inputs read | N8D7I/N8D7J `REPORT.md` + `ORCH-GATE.md`, `docs/todo.md` N8D7K item |

LSP: `findReferences` + `documentSymbol` on the fork header returned "No results
found" (no language server for files outside the repo). Call-edge confirmation
therefore rests on: (a) `grep -rn swizzle_PS2` over `~/dev/PS2Recomp/ps2xRuntime/`
= **zero hits**; (b) `grep -rn ParallelGS` over the fork GS dir = **zero hits**;
(c) the fork GS includes list (`gs_cpu_backend.cpp:1-7`) names only
`runtime/gs/*` headers. The fork helper neither calls nor includes G43 code.

## 2. The independent oracle and why it qualifies

- **Oracle core:** `GSPSMCT32::addrPSMCT32(block, width, x, y)` with literal
  `blockTable32[4][8]` + `columnTable32[8][8]`
  (`ps2xRuntime/include/runtime/gs/ps2_gs_psmct32.h:9-36`).
- **Not a copy of G43:** G43 contains **no literal tables**; `swizzle_PS2`
  (`gs/shaders/swizzle_utils.h:329-380`) computes the same permutation with
  bit-arithmetic (`block_index`/`pixel_index` formulas). Different authors
  (PS2Recomp vs Arntzen Software AS, LGPL-3.0+ header), different encoding of
  the permutation. Residual risk: both implement the same Sony GS spec, so a
  shared spec misreading cannot be excluded — stated, not hand-waved.
- **Fork-internal triplication agrees:** `BlockTableC32` in
  `ps2_gs_memory.cpp:45-51` and `referenceAddrPSMCT32`/`kBlockTable32` in
  `ps2xTest/src/ps2_gs_tests.cpp:279-306` carry identical values; input
  convention `block = fbp<<5` is pinned by `frameBaseToBlock`
  (`ps2_gs_tests.cpp:331-334`) and `addrPSMCT32(0u, fbw, x, y)` callers
  (e.g. `ps2_runtime_expansion_tests.cpp:129`).
- **CT24 coverage (source-proved):** `WriteCT24`/`ReadCT24` use
  `PixelStorageTraits<C24>` with **`PageTableC32`** (`ps2_gs_memory.cpp:228-231,
  302-305`); G43 groups PSMCT24 with PSMCT32 (`swizzle_utils.h:359-360`) and
  with 32-bit stride (`:66`); `Support.h:1702` treats psm 1 "as 32". So the
  CT32 oracle gives CT24 **storage** addresses. CT24 RMW preserves the old
  alpha byte (`ps2_gs_memory.h:485-490`).
- **RGB vs alpha (source-proved):** G43 `vram_readback<PSMCT24>` emits the low
  3 bytes of each word (`gs_util.hpp:76-84`); the circuit sampler forces alpha
  `0x80` for non-CT32 (`sample_circuit.frag:62-67`). Decoded-pixel comparison
  is therefore RGB-only; raw-word comparison uses exact 32-bit words and the
  alpha byte must not gate the verdict.
- **PCSX2 third oracle: gap.** No PCSX2 GS mapping source exists locally (no
  checkout under `~/dev`; T-lane PCSX2 is bytesize-only and `ssh` is denied to
  this worker; ssx3 docs contain no PCSX2 address source). Fork-vs-G43 is the
  only available independent pair.

## 3. Literal golden offsets (derived from the fork tables, then compared)

Convention: `block = 112<<5 = 3584`, `width = 8`; byte address per
`ps2_gs_psmct32.h:29-35`. The brief's four coords are all on the sampled grid:
(31,0)=pixel(31,0), (0,2)=pixel(0,1), (511,446)=pixel(511,223).

| GS (x,y) | Fork-table byte | Word (`>>2`) | G43 word | Match | Note |
| --- | --- | --- | --- | --- | --- |
| (0,0) | 0xE0000 = 917504 | 0x38000 | 0x38000 | yes | FBP base; equals N8D7D2's literal 917504 |
| (31,0) | 0xE0534 = 918836 | 0x3814D | 0x3814D | yes | intra-block |
| (0,2) | 0xE0040 = 917568 | 0x38010 | 0x38010 | yes | column-table step |
| (511,446) | 0x1BFFF4 = 1834996 | 0x6FFFD | 0x6FFFD | yes | far corner |
| (64,0) | 0xE2000 = 925696 | 0x38800 | 0x38800 | yes | **page-column boundary** (page width 64) |
| (0,32) | 0xF0000 = 983040 | 0x3C000 | 0x3C000 | yes | **page-row boundary** (page height 32) |
| (63,31) | 0xE1FFC = 925692 | 0x387FF | 0x387FF | yes | last word before column break |
| (64,32) | 0xF2000 = 991232 | 0x3C800 | 0x3C800 | yes | page corner |

Checks: all 8 distinct, all < 4,194,304 (in-bounds), word offsets =
`byte>>2` with the 4 MiB byte mask. G43 values were computed **after**
derivation with the bit-arithmetic formula and matched 8/8. Recompute script:
two `python3 -c` evaluations (tables pasted from the cited lines); no repo
code was executed.

## 4. Bounded same-run raw-word sample (design only — no run executed)

Requires a source hook (out of scope): emit, next to the `[n8d7f] bytes=` line
(`ps2_gs_parallel_backend.cpp:579-583`), the exact 32-bit words at the six word
offsets `0x38000, 0x3814D, 0x38010, 0x6FFFD, 0x38800, 0x3C000` of the already-mapped
`selected_vram_staging`, plus an 8×4 spot grid over sampled pixels
(px 0..7 × py 0..3, eff y = py*2) and a positive-control read of a known-populated
word (e.g. the texture-page control region used for the occupancy null).

Predeclared on the **same** tick-2050/FBP112/PMODE `ff21` frame, `promoted=0`,
`samples=1`, `control=128`, frame PNG present:

| Category | Exact-word evidence | Decoded `input` census | Decision |
| --- | --- | --- | --- |
| A sparse VRAM | ≥5/6 golden words are 0x00000000 (or RGB-zero with stale alpha) | active ≤100 | bytes absent: loss is upstream of VRAM |
| B address/decode loss | ≥2/6 golden words nonzero while colocated decoded pixels read black | active ≤100 | bytes present, selection/address/PSM loses them |
| OTHER | any promotion/sample/alignment/control miss, missing word line, or 1/6 split | any | not interpretable; no second run from this design |

Positive control must read nonzero or the run is OTHER (read path unproved).
No occupancy window is used anywhere: every condition names exact words.

## 5. Gaps

1. Display-side selection (`coord = px+dbx, py*stride+dby+phase`, `&2047` wrap)
   is documented only by G43 code (`sample_circuit.frag:108-109`,
   `gs_util.hpp:57-66`) — trivial arithmetic, but not second-sourced.
2. No local PCSX2 mapping copy (§2); bytesize-only.
3. The §4 hook does not exist in the pinned tree (N8D7J §5); no run is
   released from this audit. The orchestrator decides on any source hook or
   Odin run.
