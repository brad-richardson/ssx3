# GB7C7P2 — tick259 packet5470 texture-word tap (antomipc Go)

Predeclared outcomes (GB7C7 brief): **A** = executed sample at
packet5470/batch10 has computed tap0 address `0x000bae74`, directly read
CT32 word with RGB `353341`, and the same accepted pixel write changes
`dc302f3b` to `dc353341`; **B** = sample/address/word differs while the
destination write is observed (first differing field named);
**OTHER** = context gap, cap, pin failure, missing write, or ON/OFF
perturbation. A proves this single pixel's sampled word only — not the
word's earlier producer, a whole glyph, or a GPU cause. The orchestrator
gates.

Outcome: **A — all 31 scripted checks pass** (`check.py`,
`RESULT A reason=all-match`). The executed FST sample at tick259 path3
packet5470 batch10 for destination `(342,377)` computed tap0
`(343,378)` at swizzled address `0x000bae74`, directly read CT32 word
`63353341` (RGB `353341`, equal to the `SampleTexture` return argument),
with `fx=fy=0`, and the same accepted write changed the actual storage
word `dc302f3b` → `dc353341` at swizzled destination address
`0x0019ae38` (classification `accepted-write-changed`, uncapped,
ON/OFF frame+PPM equal).

## 0. Scope, sentinel, pins

- Scoped-edit exception verified first: wrote
  `~/dev/ssx3-work/GB7C7/sentinel_GB7C7P2.txt`, then removed it. No
  denial; no other bypass attempted.
- Touched only the three owned fork files, GB7C7 scratch
  (`~/dev/ssx3-work/GB7C7/run/`), this brief's dir
  (`local/research/GB7C7P2/`). No edit to the GB7C7 report/checker,
  shared forks, boards, or global config. No Odin/iOS/upstream/push.
- Pins: ssx3 HEAD `c44d581b` at pin time (tree clean except this
  dir); main has since moved to `47055fd5` (unrelated `[orch] Gate
  N8D7M7` lane commit) and this receipt commit lands on the new HEAD;
  fork `8966b0b` branch `gb4-parallel` at start; capture
  `run/gb4p4.capture.bin` sha256
  `a6f75fb3…ad51851` (matches); sidecar `run/gb4p4.paths.txt`
  1,982,063 lines, line 5471 = `5470 3`; build dir Release,
  `PS2X_ENABLE_DIAG_TAPS=OFF`; binary
  `build/ps2xTest/ps2x_tests`.
- Fork runner-dir guard empty:
  `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` → empty.
- Budgets: scratch 6.3 MiB (cap 2 GiB); trace 7,368 B (cap 1 MiB);
  committed text ≈ 25 KiB (cap 1 MiB); mini internal 147.0/200 GB.
  No speed claim. P-lane: one slot per replay, claimed/released each
  time; slot 1 was briefly held during source inspection with no
  process running and released on the gate's notice (no run overlapped).

## 1. Read-path correction (gate warning, verified at source)

The first ON trace logged destination old/new `00302f3b`→`00353341`
while GB7C5 watched storage `dc302f3b`→`dc353341`. Source cause
(`ps2_gs_memory.h`, `PixelStorageTraits`):

- `Read` for C24/Z24 returns `v & 0x00FFFFFF` — the logical CT24 read
  strips the alpha byte.
- `Write` for C24/Z24 does RMW:
  `value = (old & 0xFF000000) | (value & 0x00FFFFFF)` — the storage
  alpha byte is preserved.
- C24 shares the C32 page tables at 32-bit unpacked width
  (`UnpackedBitWidth` 32 for both), so a CT32 read at the same
  `(base,bw,x,y)` returns the same 4 storage bytes unmasked.

Repair (named gate repair): the probe logs both the logical CT24
old/new and the raw CT32 storage old_raw/new_raw at the same swizzled
address (old_raw captured pre-`WritePixel`, new_raw post-write).
Final trace: old_raw=`dc302f3b`, new_raw=`dc353341` — byte-identical
to GB7C5's independent watch. The tick259 alpha was `dc` all along;
the `00` was the C24 read mask, not VRAM content.

## 2. Implementation (3 files, default-OFF, render-neutral when closed)

- `ps2xRuntime/include/runtime/gs/gs_cpu_backend.h`: `Gb7c7PacketContext`
  + Open/Close/SetPacketContext/Enabled decls; `NoteGb7c7BatchBegin` +
  `TraceGb7c7Pixel` private decls.
- `ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`: `Gb7c7ProbeState`
  (20k rows / 8 MiB caps); batch flag kind=1 iff tick==259 &&
  packet==5470 && path==3 && sprite && fst && tme && fbp==112 &&
  tbp0==0; `DrawPrimitive` hook beside the GB7C5 hook (enabled-only);
  `DrawSprite` FST capture at `x==342 && y==377 && curBatch==10`
  (executed `texel` arg, interp/quant UV, independent CT24 + raw CT32
  old reads); `TraceGb7c7Pixel` recomputes the 4 taps exactly as
  `SampleTexture` (minus-half-texel floor + per-tap
  `wrapTextureCoordinate`), per-tap `ReadVramUnlocked` words,
  `addrPSMCT32` addresses, `applyTexa` rgba, plus the TEST/ALPHA/z
  ladder on the independent old value. Disabled path: one
  enabled-branch per batch/pixel, no extra reads.
- `ps2xTest/src/ps2_gs_replay_tests.cpp`: `PS2X_GS_REPLAY_GB7C7_TRACE`
  (direct-CPU only, mutually exclusive with GB5/GB5B/GB7B/GB7C2/GB7C4/
  GB7C5 in both directions); per-packet `SetPacketContext`; stop at
  first sampled marker ≥301 (tick 350 at STEP=50); close asserts
  `GB7C7 replay reached marker 301`.

Repair history (disclosed): build-1 failed (`TraceGb7c7Pixel` placed
before the file-local texture helpers) → moved after
`TraceGb7c4CarrierPixel`, build-2 clean → ON `tap.tsv` (16 cols,
logical words only) → gate raw-word repair: build-3 failed (a probe
snprintf edit collided with the identical GB7C4 carrier block),
build-4 clean → ON `tap2.tsv` (taps/tap_state columns lost: the
disambiguating edit dropped two snprintf calls; tap0 addr/words still
present in kept `tap.tsv`) → re-added the two calls, build-5 clean →
ON `tap3.tsv` (complete; committed receipt). All three traces kept in
scratch; only `tap3.tsv` is committed as `tap.tsv` here.
Budget note: 5 builds and 3 ON replays exceed the brief's 1+1 build
and 1 ON + 1 OFF shape (gate granted one repair/rebuild + one
validation replay); each extra cycle is logged above with its cause.
A later cap-compliance revert of the taps-snprintf fix was applied
and then undone per the corrected gate via exact inverse edits; the
final fork source was re-verified by inspection (taps snprintf
present in both the carrier and GB7C7 tracers) and matches the
build-5 validated state that produced `tap3.tsv`.
No GPU/device run was added at any point.

## 3. Validation (exact commands from `~/dev/ssx3-work/GB4/PS2Recomp`)

| Step | Command | Result |
| --- | --- | --- |
| build (incremental, ×5 w/ repairs) | `cmake --build ~/dev/ssx3-work/GB4/build --target ps2x_tests > ~/dev/ssx3-work/GB7C7/run/build-N.log 2>&1` | build-5 exit 0; binary 8,252,216 B; only pre-existing `-Wswitch` warnings |
| flag-OFF suite | `env -u PS2X_GS_REPLAY_GB7C7_TRACE …/ps2x_tests > …/suite-1.log 2>&1` | 556/556 pass |
| ON replay (slot 1) | `PS2X_GS_REPLAY_CAPTURE=…/gb4p4.capture.bin PS2X_GS_REPLAY_PATH_FILE=…/gb4p4.paths.txt PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=259,300,301 PS2X_GS_REPLAY_PPM_DIR=…/ppm-on3 PS2X_GS_REPLAY_OUT=…/hashes-on3.txt PS2X_GS_REPLAY_GB7C7_TRACE=…/tap3.tsv …/ps2x_tests > …/replay-on3.log 2>&1` | 556/556; `GB7C7_SUMMARY rows=18 bytes=7368 capped=0`; `packets=16572 priv=1889 transfers=483 markers=350 samples=7` |
| OFF control (slot 1, same env minus trace flag, `PPM_DIR=…/ppm-off`) | `… PS2X_GS_REPLAY_OUT=…/hashes-off.txt …/ps2x_tests > …/replay-off.log 2>&1` | 556/556; full stream (`packets=1982063 priv=16264 transfers=66244 markers=3000 samples=60`) |

ON/OFF equality across adjacent binaries — there is no matched
same-binary ON/OFF pair: the OFF control ran from the build-4 binary
while the final ON3 ran from the build-5 binary. All 7 common
`GB4_FRAME` hash rows are identical (0 mismatches); PPM byte SHAs are
identical at 259/300/301
(83bccb96…/d1967168…/837573f5…). The build-4→build-5 source change is
log formatting only (restored taps/tap_state snprintfs in the GB7C7
tracer; that code early-returns unless the probe is open, so the
render path is untouched by construction) — but same-binary
nonperturbation is unverified, since no OFF replay was run from the
build-5 binary. The single-pixel executed-read result (tap0 address,
tap words, raw dst words, accepted-write classification) is unaffected
by this caveat. PPM dirs were pre-created (`dumpPpm` does not mkdir);
the on2 run's PPMs were lost to a missing dir, so build-2 PPMs are
bridged by row-equal hashes (`hashes-on.txt` build-2 ==
`hashes-on3.txt` build-5).

Frame view: tick259 PPM is 512×448 P6, `display_fbp=112`. Stream
order (independent capture scan, SHA `a6f75fb3…`): marker259 record at
offset 6673264 with 5470 packets already seen (packets 0–5469), and
packet5470 begins at offset 6673427 with 259 markers already seen. The
tick259 PPM is therefore sampled at marker259, *before* the watched
write executes — it cannot show the tapped `353341`. Its pixel
(342,377) reads RGB `3b2f30`; the reason for that exact pre-write
value is unknown (no overwrite is claimed: GB7C5 `watch.tsv` shows no
changed write after packet5470 through packet47240). The evidence for
the write is the executed old/new pair around `WritePixel`, not the
marker-259 frame.

## 4. Observation table (final trace `tap3.tsv` pixel row)

| Field | Value |
| --- | --- |
| tick / packet / path / batch | 259 / 5470 / 3 / 10 |
| dst xy / swizzled addr | (342,377) / `0019ae38` |
| interp / quant UV | (343.500,378.500) / (343.5000,378.5000); preI (343,378), postSingle (343,378) |
| taps pre/post | (343,378);(344,378);(343,379);(344,379) both; fx=fy=0.0000 |
| tap addrs | `000bae74,000baf40,000bae7c,000baf48` |
| tap words (CT32 reads) | `63353341,66302e3d,8004051d,8004051d` |
| tap rgba (TEXA) | identical (CT32 = identity) |
| executed texel arg | `63353341` (RGB `353341` = tap0 word) |
| dst old/new logical (CT24) | `00302f3b` → `00353341` (alpha masked by C24 read) |
| dst old_raw/new_raw (CT32 storage) | `dc302f3b` → `dc353341` |
| TEX0/TEX1/CLAMP/TEXA/FRAME/TEST/ALPHA/PRIM/RGBAQ | tbp0-0,tbw8,psm0(CT32),tw10,th9,tcc0,tfx0 / tex1=0x61 (linear) / clamp=0x5 (CLAMP) / ta0=128,aem=0,ta1=128 / fbp112,fbw8,psm1(CT24),fbmsk=0xff000000 / test=0x30000 / alpha=0x8000000064 / PRIM sprite fst=1,tme=1,abe=0 / vrt=(128,128,128,128), rgba-in=(65,51,53,128), z=0 |
| classification | `accepted-write-changed` |
| batch10 row | rect=(319,0)-(350,445) uv0=(320,0) uv1=(352,447), same state; 17 textured batches (0–16) flagged, pixel traced only at batch10 |

## 5. Gaps / next action

- The sampled word is now directly proved (A for the single pixel).
  Still unproved (unchanged from GB7C6): which earlier
  upload/draw placed `63353341` at `0x000bae74` (glyph ink vs
  coincident RGB), any whole-glyph claim, and any GPU cause.
- `check.py` gates exactly the predeclared A/B/OTHER; result
  `RESULT A reason=all-match` in `check-result.txt`.
- Recommended next action (for the orchestrator): gate this trace,
  then design the same-stream CPU/paraLLEl comparison at
  packet5470/address `0x000bae74` (GB7C6 §6 order: A1 log equality
  first, then texel/pixel diff).

## 6. Receipts

- Fork `~/dev/ssx3-work/GB4/PS2Recomp`: 3-file diff, commit
  `[GB7C7P2]` with `Orchestrated-By: opencode`, no push.
- ssx3 `local/research/GB7C7P2/`: `REPORT.md` (this file),
  `check.py`, `check-result.txt`, `tap.tsv` (bounded `tap3.tsv`
  copy, 7,162 B); commit `[GB7C7P2]` with
  `Orchestrated-By: opencode`, no push.
- Scratch `~/dev/ssx3-work/GB7C7/run/`: build-1..5.log, suite-1.log,
  replay-on/off/on2/on3.log, hashes-on/off/on2/on3.txt,
  tap.tsv/tap2.tsv/tap3.tsv, ppm-on/off/on3/ (ppm-on2/ absent —
  uncreated dir, see §3).
