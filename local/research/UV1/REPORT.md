# UV1 — VIF UNPACK formats vs PCSX2 + DMA stall/REFS probe

Worker: Muse Code, brief `local/muse/prompts/UV1.md`. Base fork `ssx3` `0ed07c4`,
worktree `~/dev/ssx3-work/UV1/PS2Recomp`, branch `uv1-unpack` (one commit, local only,
no push). Runner `938cce16…0c94f5` (two matching SHA reads), suite 612/612.
Route I26-FAST, `PS2X_DETERMINISTIC=1`, `PS2X_SKIP_MOVIE=1` (dev-only), empty mc0/mc1,
`PS2X_SOUND=1`, paraLLEl (`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`,
`[gs-path]` = flat-always Mac line), `PS2X_MISSING_FUNCTION_POLICY=stop`.

Code change (default-off logging only, no behaviour change; new header
`ps2xRuntime/include/ps2_uv1_counters.h` + 3 call sites, runner dir untouched):
`PS2X_VIF_FMT_LOG=1` → one `[uv1-vif]` line per guest vsync (UNPACK count, per-format
counts, usn/mask/tops/num0/mode/fill/skip/(cl,wl)/raw-zero flags);
`PS2X_DMA_STALL_LOG=1` → one `[uv1-dma]` line per vsync (per-channel chain kicks,
REFS tags, kicks with D_CTRL STS/STD set, raw D_CTRL values). Lag-one emission, so a
SIGTERM-stopped boot loses only its last active vsync; idle vsyncs print as `idle`.

Boot B1 (one mini slot): `bound=target`, last_tick 2404, 116.4 s wall, `gs_fatal=null`.
Mini load was 60–100 during the run (other lanes active); this is a det correctness
census, not a speed number, so load is irrelevant. Census covers vsync 92–2403 (VIF)
and 38–2403 (DMA); vsync 2404 lost to SIGTERM by design.

## 1. Static: our UNPACK vs PCSX2 (used/unused from §2)

Ours: `ps2xRuntime/src/lib/ps2_vif1_interpreter.cpp` L802–1086 @ `0ed07c4`.
PCSX2: `pcsx2-t4/pcsx2` @ `9056c0834` (clean): `pcsx2/Vif_Unpack.cpp`,
`pcsx2/x86/Vif_UnpackSSE.cpp` (hardware-tested V2/V3 rules), `pcsx2/x86/Vif_Dynarec.cpp`
(fill), `pcsx2/Vif_Codes.cpp` (STCYCL).

| # | Behaviour | Ours | PCSX2 | Verdict |
|---|---|---|---|---|
| 1 | V2 z/w | stale VU mem (`:885-887`, only x/y written) | z=v0 always; w=v1 (`UNPACK_V2`, `Vif_Unpack.cpp:76-83`); V2-32 aligned w=0 (`Vif_UnpackSSE.cpp:139-151`, "tested on ps2") | **DIFFERENT, used** (31%) |
| 2 | V3 w | stale VU mem | next vector's x, or 0 at a QW boundary (`xUPK_V3_*`, `:203-238`, hw-tested) | **DIFFERENT, used** (22%) |
| 3 | V3 z / V4-32/16/8 / S-32/16/8 | z=v2; full write; scalar broadcast (`:917-980`) | same (`UNPACK_V4`, `UNPACK_S`, `:62-95`) | same |
| 4 | V4-5 values + USN/MODE ignore | `(5-bit<<3, A<<7)`, no extend/add (`:981-990`, `:1005`) | bit-identical (`:97-107`; SSE `:264-284`; "act as mode==0") | same |
| 5 | vl=3,vn≠3 (invalid: S_5/V2_5/V3_5) | 16-bit components + raw-copy fallback when modeless+unmasked (`:998-1003`) | 0 source bytes (`nVifT`, `:268-285`), warn + no-op (C `:109-112`); dynarec "TODO: Needs hardware testing" | DIFFERENT, unused |
| 6 | MODE 3 | ignored (only 1/2 add, `:1029`) | row=data and dest=data (`:51`) | DIFFERENT, unused |
| 7 | fill (CL<WL) no-data cycles | ROW-fill on data lanes (`:1019-1021`, from upstream PR #87, uncited) | re-unpack unadvanced pointer = read-ahead (`_nVifUnpackLoop`, `:503-510`; dynarec "doesnt increment the source", `Vif_Dynarec.cpp:374-385`) | DIFFERENT, unused (fill=0) |
| 8 | WL=0 alone / CL=0 alone | both clamp to 1 (`:834-837`) | WL=0→256 (`:221`, dynarec `:248` "(KH2)"); CL used raw | DIFFERENT, unused (only the 0/0 pair occurs) |
| 9 | CL=WL=0 pair | effective 1x1 stream | repeat-first-vector NUM times | DIFFERENT, used (1.6%, boot/menu) — see §3 |
| 10 | sign/zero ext, +TOPS, NUM 0→256, skip/fill addressing, mask row/col select + write-protect, MODE 1/2 (data-lane-gated), size accounting | as implemented | same (`writeXYZW` `:24-59`, setup `:184-250`, loop `:483-522`) | same |

Row 8 detail: CL=0 and WL=0 always co-occur on the route (every `raw0=a/b` line has
a==b), so the WL=0-alone and CL=0-alone corners never execute.

## 2. Dynamic: what SSX 3 actually uses (B1, 3,850,530 UNPACKs)

Formats (commands; sums to n exactly):

| Format | Count | Share | Format | Count | Share |
|---|---|---|---|---|---|
| V4_32 | 1,198,491 | 31.1% | V2_32 | 319,738 | 8.3% |
| V3_16 | 616,527 | 16.0% | V3_32 | 236,395 | 6.1% |
| V2_16 | 444,459 | 11.5% | V4_16 | 112,137 | 2.9% |
| V2_8 | 444,459 | 11.5% | V4_8 | 54,793 | 1.4% |
| V4_5 | 384,534 | 10.0% | S_32 | 38,997 | 1.0% |

Never used: S_16, S_8, V3_8, S_5/V2_5/V3_5. Flags: mask 40.1%, tops 95.6%,
usn 0.21%, num0=0, mode always 0, fill=0, skip 8.7% (all `3x1`); (cl,wl) only
`1x1`/`3x1`/`4x4`; raw CL=WL=0 on 62,456 (1.6%, vsync 92–802, boot/menu only,
overwhelmingly V4_32).

DMA (suspect 7): 9,334 chain-mode kicks (vif1 4,666 + gif 4,666 + vif0 2),
**REFS=0, stall-kicks=0**; D_CTRL unwritten on the first active vsync, then
always exactly `0x1` (DMAE, no STS/STD) on all 2,333 active vsyncs.

Statics confirmed for suspect 7: REFS handled as REF (`ps2_memory.cpp:1736-1740`);
CHCR reads clear STR (`:2893-2898`); only D_CTRL bit 0 consulted (kick gate
`:1546-1551`, GIF paths); no STADR handling anywhere in the fork (Fable's
`DMA.cpp` is upstream layout — no such file here); chains complete synchronously
inside the CHCR-store walk. Coverage note: the GIF fast paths are currently dead
code (`kickGifDmaChainFromMMIO` has no callers), so the hooked walker sees every
kicked chain including any REFS (both fast paths also bail to the walker on
non-REF/CNT tags).

Verdict: **close suspect 7 (M9/M10) for this route** — no REFS, no stall control.
No Part 2 needed unless another route uses them.

## 3. Used-and-different: one-line fixes (not applied, per brief)

1. **V2_32/V2_16/V2_8 (1.21M, 31%)** — after the component loop, replicate the pair:
   `decompressed[2] = decompressed[0]; decompressed[3] = decompressed[1];`
   (matches PCSX2's C path and hardware v1v0v1v0; the V2-32 QW-aligned w=0
   refinement needs position tracking — optional follow-up.)
2. **V3_32/V3_16 (853K, 22%)** — w takes the next source vector's first element,
   0 when the read crosses a source QW boundary (PCSX2 `xUPK_V3_*` rule). Minimal
   one-line form: read the overlapped 4th word as PCSX2's C path does; the
   boundary-0 rule is the refinement. Not quite one line — Part 2 owns the shape.
3. **CL=WL=0 pair (62K, boot/menu)** — no fix proposed: models differ in theory
   (ours streams 1x1; PCSX2 would repeat the first vector), but rendering is
   correct under ours, so either hardware-0/0 == 1x1 (our clamp right) or these
   unpacks have NUM==1 (models coincide). NUM distribution was not captured; if
   Part 2 pursues this, add NUM to the census first.

Different-but-unused (no action): invalid-combo raw copy, MODE 3, fill ROW-vs-read-ahead,
WL=0/CL=0-alone corners.

## Gaps and recommended next actions

1. Last active vsync (2404) lost to SIGTERM by design (lag-one emission); all
   totals cover 92–2403 / 38–2403.
2. No flag cross-tabs (e.g. usn-per-format, mask-per-format) — totals only. The
   §3 verdicts don't depend on them.
3. NUM distribution not captured (matters only for §3 item 3).
4. Fill-cycle hardware truth is open on both sides (our ROW-fill is uncited
   upstream inheritance; PCSX2's read-ahead is uncommented). Moot for this route
   (fill=0).
5. Route-scoped (I26-FAST single-race); menu/online paths may use other formats.

Recommended: Part 2 fixes V2 (item 1) first — one line, 31% of unpacks, hardware rule
unambiguous — with the det-hash + GS-digest gate; V3 (item 2) second with the
alignment rule from `Vif_UnpackSSE.cpp:203-238`.

## Receipts

- Build: `0ed07c4` + `uv1-unpack` (new `ps2_uv1_counters.h`, 3 call sites),
  Release/HB-clang, `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3`
  (`register_functions.cpp` `8ea8ed43…62d688a3` ✓ two reads, matches CT1's pin),
  `BUILD_TEST=ON`, runtime/aggressive logs OFF, diag taps OFF, det-hash OFF,
  `GS_SHADOW_PARALLEL=ON`, parallel-gs `19d93b2` (F2 clone; `~/dev/parallel-gs`
  @ `963cb57` lacks the GB9 knob this base needs — reconfigure, same build).
  Configure rc=0, build rc=0, suite **612/612 rc=0**. Runner
  `938cce166129961db6810b47c49c62f03d0fe4e13c5cba2e3be75f111b0c94f5`
  (two reads match).
- Header probe (throwaway `/tmp/uv1_hdr_check.cpp`, kept out of git): aggregation,
  gap-fill, stall-bit decode, invalid-name print all correct; default-off silent.
- B1: `bound=target`, last_tick 2404, 116.4 s, `gs_fatal=null`, `[gs-path]` =
  flat-always Mac line. ISO/ELF/codegen pins verified twice per boot (all match CT1).
- Scratch: `~/dev/ssx3-work/UV1/` (build, `uv1_boot.py`, `uv1_agg.py`, `run/B1`,
  `pcsx2-ref/` read-only PCSX2 sources @ `9056c0834`). Disk 168/200 GB at build.
- Runner-dir guard: change is `src/lib/*` + `include/*` only (no `src/runner/`
  files touched). Never pushed.
- Budgets: 1 build / 1 (+1 reconfigure against pinned GS source), 1 boot / 1 (+0
  spare used), ~25 min wall of the 1.5 h box.

Exact commands:

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/UV1/PS2Recomp -b uv1-unpack 0ed07c4
# new ps2xRuntime/include/ps2_uv1_counters.h; hooks in ps2_vif1_interpreter.cpp + ps2_memory.cpp
cd ~/dev/ssx3-work/UV1
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)
python3 uv1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label B1 --stop-tick 2400
python3 uv1_agg.py run/B1/boot.log
```

## Part 2 — V2/V3 fix, unit tests, A/B det comparison

Same worktree/branch `uv1-unpack`. One commit: the V2/V3 lane rules in
`ps2_vif1_interpreter.cpp` + 10 unit tests in `ps2xTest/src/ps2_memory_tests.cpp`
(all cite PCSX2 file:line). CL=WL=0, invalid combos, MODE 3 and fill untouched.

Rule as implemented (brief spec): V2 writes z=v0; w=v1 except V2-32 with a
QW-aligned unpack data start gives w=0 (`Vif_UnpackSSE.cpp:139-151`). V3 w =
next source vector's first element (width-appropriate, USN-extended), 0 when
the read crosses a source QW boundary or runs past the buffer (`:203-238`).
Stream phase comes from the buffer offset (buffers concatenate whole QW
payloads; first payload assumed guest-QW-aligned — noted in code). Mask/mode
logic untouched and applies to the new lanes as PCSX2's `writeXYZW` does.

Two findings while implementing (both in code comments + report, no spec change):
1. PCSX2 hardcodes the aligned case for every non-V3-16 type (`Vif_Dynarec.cpp`
   key1 `&= 0xFFFF01FF`, `:471-473`), i.e. its mode-0 paths zero V2-32 w
   unconditionally. The brief's conditional rule is implemented with the real
   phase instead — a deliberate, documented generalization.
2. The V3 QW-cross clause is unreachable through the interpreter: `pos` advances
   only in multiples of 4 (every command/data length is 4-aligned), and with a
   4-aligned data start no V3 w-read (4/2/1 bytes at vec+12/6/3) can span a QW
   boundary. Effective V3 rule: always next-x (0 past buffer end). The check is
   implemented per spec anyway; tests cover the reachable boundaries (next-read,
   trailer/pad-read, buffer-end-0).

Tests (10, sentinel-prefilled VU1 data): V2_32 unaligned replicate + aligned w=0
(NUM=2 both); V2_16 signed replicate on an aligned start (locks the w=0 rule as
V2-32-only); V2_8 signed replicate; V3_32 next-read + trailer-word + buffer-end-0;
V3_16 next-read signed + trailer-u16 + buffer-end-0; V3_8 next-read signed +
pad-read + buffer-end-0 (NUM=4). Red phase observed: all 10 fail on unfixed code
(616/626 pass); green: **626/626 rc=0** from the worktree root (612 prior + 10
new + 4 tap-gated det-hash tests newly compiled in).

Boots (det, paraLLEl + `PGS_HIER_BINNING=force`, SOUND=1, I26-FAST, empty mc0,
one slot each): A = base + counters-off + det-tap runner
(`d1a62f31…138fd12`), B = fix (`2e4dcd0f…60485fa`). The frame knob takes 3 ticks
per boot, so each config ran twice: A1/P2B1 (`ONCE_TICKS=1090,1800,2100` +
GS capture) and A2/P2B2 (no once-ticks; `upload-latest` ≈ t2400). Fifth boot A3
(A binary, stop 2470, once-ticks 2451–2453, no capture) pins the late-race
comparison: A3@2451 fnv `a77cb1e7` = P2B2@2451, and A3-vs-P2B2 det-hash differs
only at 1606 over ticks 1–2451. All five `bound=target`, `gs_fatal=null`,
hier-if-large path line. A1-vs-A2 det-hash: 0 diffs over 2,425 common ticks
(frame-dump mode doesn't perturb guest state).

- **First det-hash differing tick: 1606** (the only one of 2,452 common ticks);
  fields differing: `vu1Data` (+`combined`) only — RDRAM, scratch, VU1 code,
  eeCycle and program count identical everywhere.
- **GS stream digest: differs** (`4bc97c2c…` vs `a6ed1cf4…`, same 2,510,683,433
  bytes, same 1,906,204 records). Record-multiset diff: 3,055 small Packet
  records differ across 42 ticks (461…2245, incl. 1606); all other records
  (incl. every VBlank marker) identical. Raw byte diff (1.7M bytes) overstates it:
  part is record-interleave shift at one VBlank boundary.
- **Frames, viewed side by side, all pixel-identical** (fnv + byte-identical
  PNGs): t1091 Select Peak menu (`f86140f2`), t1800 race start (`298c446a`),
  t2100 race 1% (`6f164015`), t2422–2424 (`5b14b861`/`fda2ce0`/`3b0c492d`) and
  t2451 (`a77cb1e7`, via follow-up A3 boot below). At t2425 the two final-frame
  boots show different presents (A2 repeats the 2424 frame, P2B2 presents a fresh
  `fee99ed6`) — a host present-phase artifact where SIGTERM landed, not a render
  difference: det-hash matches at 2424 and 2425, and frames match at 2422–2424
  and again at 2451.
- **Player rider, close-looked (for RD1):** t1800 rider at the start gate (right,
  partly behind the gate pole; dark outfit + red board, countdown overlaid);
  t2100 rider centre-frame, a complete dark snowboarder (torso, spread arms,
  board) carving with spray trail; t2425 rider distant-centre, almost fully
  buried in snow spray (only faint dark fragments — reads as "missing" at a
  glance); t2451 rider mid-air tumbling (limbs spread, board separate, 3 MPH) —
  normal race evolution in both runs (A3 proves it), not a fix-induced crash.
  Every compared tick is pixel-identical A/B: V2/V3 z/w change nothing about
  the rider's rendering; Brad's missing-model issue reproduces identically with
  and without the fix.
- **cid0 = 531 in B** (P2B1; A1/A2 also 531 — sound pacing unaffected).

Reading: V2/V3 z/w flow into a few small GS packets but are dead lanes for
rasterization on this route (no presented frame changes); the tick-1606 blip is
a row that survives to VBLANK sampling while all other ticks' rows are
overwritten in-tick. The fix matches hardware on lanes the game doesn't consume.
No render regression; foldable on the orchestrator's call.

Part 2 receipts: suite red log `suite-red.log` (10 UV1 fail), green `suite-green.log`
(626/626); runners `runners/ps2EntryRunner-{A,B}` (two SHA reads each); boots
`run/{A1,A2,P2B1,P2B2,A3}` with `result.json` (det lines, frame fnvs, snd cid0,
GS sha), `frames/`, `snd.log` (`gs.stream` A1/P2B1 moved SHA-verified to SSD
scratch `/Volumes/Extreme SSD/ssx3-uv1/`, internal copies deleted under the cap).
Rider crops are throwaway (`/tmp/uv1_rider/`). Disk 61.6/200 GB at close (briefly
201 during the captures; mine moved off, other lanes cleaned). Never pushed.
Budgets: 2 rebuilds of one dir (A tap rebuild + B fix rebuild; +1 red-phase
incremental), 5 boots (4 planned + A3 late-race pin), ~1.5 h box kept.

```sh
# A runner: reconfigure the Part 1 build dir (source still base+counters)
cmake -S PS2Recomp -B build -DPS2X_ENABLE_DET_HASH_TAP=ON
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
cp build/ps2xRuntime/ps2EntryRunner runners/ps2EntryRunner-A
# implement fix + tests (one commit), rebuild, suite from worktree root
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)   # 626/626
cp build/ps2xRuntime/ps2EntryRunner runners/ps2EntryRunner-B
python3 uv1p2_boot.py --runner runners/ps2EntryRunner-A --label A1 --stop-tick 2400
python3 uv1p2_boot.py --runner runners/ps2EntryRunner-A --label A2 --stop-tick 2400 --no-once-ticks --no-capture
python3 uv1p2_boot.py --runner runners/ps2EntryRunner-B --label P2B1 --stop-tick 2400
python3 uv1p2_boot.py --runner runners/ps2EntryRunner-B --label P2B2 --stop-tick 2400 --no-once-ticks --no-capture
python3 uv1p2_boot.py --runner runners/ps2EntryRunner-A --label A3 --stop-tick 2470 --once-ticks 2451,2452,2453 --no-capture
```

## Orchestrator gate (2026-09-25)

**Pass.** Suspect 7 (REFS/stall) closed for this route. **V2/V3 z/w differ from PCSX2 and are used by
53 % of the route's UNPACKs** (V2: we leave z/w stale, PCSX2 z=v0 w=v1, V2-32 QW-aligned w=0; V3: we
leave w stale, PCSX2 w = next vector's x or 0 at a QW boundary). Whether the VU1 programs read those
lanes decides visibility; stale VU memory is a candidate for intermittent pop-in. Part 2 released:
implement both rules as PCSX2 does (hardware-tested SSE rules), unit tests, one A/B det boot.

## Orchestrator gate, Part 2 (2026-09-25)

**Pass.** PCSX2's V2/V3 lane rules with 10 tests (red → green); only `vu1Data` differs from tick 1606
on, and every compared frame is pixel-identical. Correct per the reference, invisible on this route;
not the player-rider bug (RD1 told). Fold `8545eb2` (default-off counters) + `6acf5bb` in F3.
