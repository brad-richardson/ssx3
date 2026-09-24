# GB7C4 — actual carrier glyph-row sample (OpenCode Go)

Predeclared outcomes (brief): **A** = glyph-row sample whose actual source
address matches a changed packet47176 C1 word and whose unmasked accepted
write changes the carrier destination; **B** = mapping exists but
mask/alpha/TEST blocks or leaves the destination equal; **C** = none of the
four candidates is sampled by the carrier; **OTHER** = incomplete trace,
alignment failure or other path. CPU replay path observations only — not a
displayed-glyph producer or GPU cause. The orchestrator declares the verdict.

Outcome: **B, on all four candidates (A, B, C, D).** The carrier samples
every candidate glyph-row source with exact tap/address/word match, the
write path is fully open, and the destination already holds the glyph RGB:
steady-state rewrite, no observed change.

## 0. Resume history (prior worker stop, kept findings)

The first GB7C4 worker stopped on a tool-permission denial on its first
outside-workspace edit (`../*` deny pattern; REPORT §5 of that version) and
performed no fork edit, build, replay or commit. This pane resumed with the
scoped edit exception, kept its read-only findings (pins: fork `7bd8349`,
capture `a6f75fb3…`, 1,982,063-line paths, GB7C2 inputs present, empty
runner-dir guard, Release/`DIAG_TAPS=OFF` build dir, GB7C2 OFF-control
hashes), re-verified them read-only, and completed the
implementation/build/replays/receipts/commits below. No pixel perturbed by
the probe itself (§3 OFF control).

## 1. Pins (verified before the build)

| Item | Value |
| --- | --- |
| GB4 worktree `~/dev/ssx3-work/GB4/PS2Recomp` | `7bd834900b3e34662f53d5eaba63461d692b6b19`, branch `gb4-parallel` — matches brief pin `7bd8349`; tree clean before edits |
| capture `run/gb4p4.capture.bin` | `a6f75fb34fceccf6fd92ad65950d16f05a140cf38a3cc2f028be32e56ad51851` — matches GB7C2 pin |
| paths `run/gb4p4.paths.txt` | 1,982,063 lines |
| GB7C2 replay inputs | `run/gb7c2/{chain.tsv (321 lines),chain.tsv.crops}` present |
| build config | `CMAKE_BUILD_TYPE=Release`, `PS2X_ENABLE_DIAG_TAPS=OFF` |
| runner-dir guard | `git diff 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty (0 lines) |
| disk | 144.6 GB of 200 GB cap |

## 2. Implementation (private fork, 3 files, default-OFF)

- `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`: `Gb7c4PacketContext`
  (tick/packetIndex/path/batch) + `ps2xGb7c4ProbeOpen/Close/SetPacketContext/Enabled`
  decls + three private hook decls.
- `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`: default-OFF probe.
  `NoteGb7c4BatchBegin` assigns the intra-packet batch id per `DrawPrimitive`
  (same counting as GB7C2, so batch ids are directly comparable) and logs one
  batch row with the clipped rect plus CLAMP/XYOFFSET/TEX0/TEX1/TEXA/FRAME/
  FBMSK/ALPHA/ABE/PABE/vertex color/TEST for C1-state batches
  (tick600/pkt47176/path2/sprite/STQ/fbp0/tbp0-11017) and carrier-state batches
  (tick601/pkt47240/path3/sprite/FST/tme/fbp112/tbp0-0). `DrawSprite`'s
  textured loop matches the exact candidate pixels — C1 sources
  (343,378),(369,381),(382,381),(407,378) and carrier destinations
  (342,377),(368,380),(381,380),(406,377) — takes an independent old read
  immediately before `WritePixel`, then traces after. C1 rows carry
  pre/post-CLAMP UV, raw T4 nibble/CLUT, resolved texel and the swizzled
  destination word address. Carrier rows carry the interpolated and quantized
  float UV, integer pre-CLAMP UV, single-point post-CLAMP UV, all four
  bilinear taps pre- and post-CLAMP recomputed exactly as `SampleTexture`
  does for the FST path (quantized UV minus half texel, floored, per-tap
  wrapped), each tap's swizzled word address from `GSPSMCT32::addrPSMCT32`
  (not a linear offset), each tap's word and TEXA-resolved RGBA, the
  `SampleTexture` blend texel with fx/fy, and the full register/vertex/TEST
  state. The per-row outcome ladder is predeclared in code: tap-miss → C,
  C1-unseen/word-mismatch/addr-mismatch → OTHER variants, accepted change →
  A (sets `aComplete`, which suppresses B/C/D carrier rows only after A has
  yielded), otherwise B. OFF path = one `enabled` branch per batch/pixel;
  rendering untouched (probe adds only `ReadVramUnlocked` calls + log writes).
- `ps2xTest/src/ps2_gs_replay_tests.cpp`: `PS2X_GS_REPLAY_GB7C4_TRACE`
  (direct-CPU only, exclusive with GB5/GB5B/GB7B/GB7C2 both directions),
  per-packet `SetPacketContext`, stop after the marker-700 sample, close +
  `GB7C4 replay reached marker 700` assertion. No crop timeline (GB7C2
  already covers the chain window: 17/17 roi-link-equal, 65/65 crop-clean).
- Address basis: C1 frame block (fbp0<<5 = 0) and carrier tex block (tbp0 = 0)
  are both block 0 at tbw/fbw 8, so carrier tap addresses are directly
  comparable to C1 source addresses; destination block is fbp112<<5 = 3584
  (CT24 shares the C32 page tables with CT32 — same helper applies).
- Caps: 20,000 rows / 8 MiB, stop-writing-at-cap (GB7B/GB7C2 shape).

## 3. Validation (exact commands from `~/dev/ssx3-work/GB4/PS2Recomp`)

| Step | Command | Result |
| --- | --- | --- |
| build (1, incremental) | `cmake --build ../build --target ps2x_tests > ../run/gb7c4/build-1.log 2>&1` | exit 0, first try — no repair, no second build; `ps2x_tests` 8,233,464 B; only pre-existing `-Wswitch` warnings in `ps2_gs_memory.h`; `PS2X_ENABLE_DIAG_TAPS` untouched |
| flag-OFF suite | `../build/ps2xTest/ps2x_tests > ../run/gb7c4/suite-1.log 2>&1` (flag unset) | 556/556 pass |
| ON replay (P-lane slot 1, claimed/released via `local/tooling/p_lane_lease.py`) | `PS2X_GS_REPLAY_CAPTURE=../run/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=../run/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=600,601,700 PS2X_GS_REPLAY_PPM_DIR=../run/gb7c4/ppm PS2X_GS_REPLAY_GB7C4_TRACE=../run/gb7c4/chain.tsv ../build/ps2xTest/ps2x_tests > ../run/gb7c4/replay-1.log 2>&1` | 556/556 pass; `GB7C4_SUMMARY rows=73 bytes=25944 capped=0`; `packets=59904 priv=3989 transfers=624 markers=700 samples=14` (identical counts to GB7B/GB7C2); no GPU replay |
| OFF control replay (slot 1, same env minus the trace flag, `PPM_DIR=../run/gb7c4/ppm-off`) | `... ../build/ps2xTest/ps2x_tests > ../run/gb7c4/replay-off.log 2>&1` | 556/556 pass; no early stop without the probe flag, so it ran the full stream (`packets=1982063 priv=16264 transfers=66244 markers=3000 samples=60`) |

OFF-control equivalence (probe perturbs no pixel): `GB4_FRAME`
tick600 `present=a6948f2`, tick601 `present=582dd887`, tick700
`present=97b4641e` in the ON replay, the OFF replay, and the GB7C2 baseline
— all identical. PPM bytes ON vs OFF identical at all three ticks (sha256:
600 `895856fd…`, 601 `660d38f3…`, 700 `9b02358b…`, each pair matching).
`run/gb7c4/` total ~4.2 MB. No speed claim (diagnostic build run).

## 4. Sample table (authoritative: `chain.tsv`, 73 data rows)

Batch ids reproduce GB7C2 exactly (48 C1 batches 0–47; 17 carrier batches
0–16). C1 pixel rows reproduce the GB7C2 traced-write words exactly.

| cand | C1 src (tick600/pkt47176/batch/old→new/addr) | carrier dst (tick601/pkt47240/batch/old→new/addr) | taps + storage addrs | texel vs taps | state | outcome |
| --- | --- | --- | --- | --- | --- | --- |
| A | (343,378) b39 `50ddd1be`→`63353341` @`000bae74`, nibble f/clut23, traced-write | (342,377) b10 `00353341`→`00353341` @`0019ae38` | pre=(343,378);(344,378);(343,379);(344,379), post identical (CLAMP=0x5 CLAMP/CLAMP, no-op); addrs=(`000bae74`,000baf40,000bae7c,000baf48); words=(`63353341`,66302e3d,8004051d,8004051d); hitTap=0 | texel=`63353341` = tap0 exactly (fx=fy=0.0000); rgba-in=(65,51,53,128) = texel RGB + vertex alpha (tcc0/MODULATE, vrt=128s) | clamp=0x5 xyoff=(28672,29184) tex0=(tbp0=0,tbw8,psm0,tw10,th9,tcc0,tfx0,…) texWH=(1024,512) lin=1 tex1=0x61 texa=(128,0,128) frame=(fbp112,fbw8,psm1,fbmsk=`0xff000000`) alpha=0x8000000064 abe=0 pabe=0 TEST=0x30000 (ATE=0, ZTE ALWAYS) → accepted-write-same | **B** |
| B | (369,381) b42 `52e0d5c2`→`1faaa29a` @`000bbe8c`, nibble 9/clut17, traced-write | (368,380) b11 `00aaa29a`→`00aaa29a` @`0019be80` | taps (369,381);(370,381);(369,382);(370,382); tap0 addr `000bbe8c` = C1 addr, word `1faaa29a` = C1 new; hitTap=0 | texel=`1faaa29a` = tap0 (fx=fy=0); rgba-in=(154,162,170,128) | same register state as A | **B** |
| C | (382,381) b44 `52e5d9c3`→`70201f31` @`000bbfb8`, nibble f/clut23, traced-write | (381,380) b11 `00201f31`→`00201f31` @`0019bfa4` | tap0 addr `000bbfb8` = C1 addr, word `70201f31` = C1 new; hitTap=0 | texel=`70201f31` = tap0; rgba-in=(49,31,32,128) | same register state as A | **B** |
| D | (407,378) b46 `50ede2ce`→`574e4b55` @`000bce74`, nibble f/clut23, traced-write | (406,377) b12 `004e4b55`→`004e4b55` @`0019ce38` | tap0 addr `000bce74` = C1 addr, word `574e4b55` = C1 new; hitTap=0 | texel=`574e4b55` = tap0; rgba-in=(85,75,78,128) | same register state as A | **B** |

UV detail (candidate A; others shift identically): interpF=(343.500,378.500),
quantF=(343.5000,378.5000), preI=(343,378), postSingle=(343,378) — the
observed dst+(1,1) mapping holds exactly at the glyph row. All four
destinations already hold their glyph RGB before the blit (dst old =
src-new with alpha cleared: CT24 has no dest alpha; `fbmsk=0xff000000`
additionally masks alpha, RGB fully open; `abe=0` so no blend).

Predicted vs observed: predeclared A/B/C/OTHER. A required a destination
change — none occurred (4/4 old==new). C required no sampling — all four
were sampled with tap/address/word match. No OTHER condition (trace
complete, alignment exact, batch ids match GB7C2). **Overall: B.**
Candidate A did not yield A, so B/C/D were traced per the brief order
(`aComplete` stayed false); had A yielded, B/C/D rows would have been
suppressed.

## 5. Perturbation prediction for a future one-pixel OFF/ON test

The measured state makes predictions exact and distinct (no missing state):

- Poke: the C1 source word at (343,378) (block-0 addr `000bae74`) to P,
  e.g. `0xDEAD0001` (distinct from every trace word), after packet47176
  completes and before packet47240 opens.
- Predicted changed: carrier dst (342,377) `0x00353341` → `0x00AD0001`
  (P masked to RGB: `abe=0`, TEST always-passes, `fbmsk` alpha-only, CT24
  drops alpha; texel = tap0 exactly since fx=fy=0.0000 measured).
- Predicted unchanged: every other destination word exactly — each dst's
  texel is exactly its own dst+(1,1) tap at zero blend weight to neighbors
  (fx=fy=0), so only (342,377) observes the poked pixel.
- Basis: fx=fy=0.0000 measured at the target pixel (texel==tap0 bit-exact),
  open RGB write path measured, no intervening writer (tap words still equal
  the C1 new words at carrier time). The only uniformity assumption is
  fx=fy=0 at non-measured pixels, supported by 24 GB7C2 background samples
  with the same +1/+1 shift; the changed-word prediction itself rests only
  on the target pixel's own measured state.

## 6. Gaps / recommended next action

- The displayed text was already present before tick601: all four glyph-row
  destinations hold their glyph RGB prior to packet47240, so this blit is a
  steady-state rewrite, not the first composition. The original glyph
  producer (which packet first wrote these RGB values into fbp112) remains
  unidentified — same gap GB7C2 left, now confirmed at glyph rows rather
  than background rows.
- Nothing in this run bears on the paraLLEl-GS damage cause (CPU replay only).
- Recommended next action: run the §5 one-pixel OFF/ON perturbation for
  candidate A (predicted `00353341`→`00AD0001` at (342,377), all else equal).
  A match upgrades the CPU transport path from correlational (B) to causal;
  a mismatch (dst stays `00353341`) would implicate a non-VRAM transport
  (e.g. a transfer path the CPU backend does not route through this blit)
  and is equally discriminating. No further passive tracing of this pair is
  needed.

## 7. Receipts

- ssx3 (this dir): `REPORT.md`, `chain.tsv` (73 data rows, 25,960 B),
  `pins.txt`, `sizes.txt` — to be committed `[GB7C4]`,
  `Orchestrated-By: opencode`, no push.
- `run/gb7c4/` (private, not committed): `build-1.log`, `suite-1.log`,
  `replay-1.log` (ON), `replay-off.log` (OFF control), `chain.tsv`,
  `ppm/vq-00060{0,1}.ppm + vq-000700.ppm`, `ppm-off/` same three.
- Fork: `[GB7C4]` commit on `gb4-parallel` (3 files: replay test cpp,
  gs_cpu_backend.cpp, gs_cpu_backend.h), `Orchestrated-By: opencode`
  trailer, no push.
