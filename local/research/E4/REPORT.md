# E4 — First-missing-visible-result locator (steady-frame boundary)

Standalone evidence. Phase 1 (no boot): existing-receipt survey + decision
below. Phase 2 (one bounded capture): §5+ (only the named gap is captured).

## 0. Steering inputs (recorded verbatim per instruction)

Task brief: tables + hypothesis + next-action recommendation, no verdicts;
read the review's "Follow-up at poll 57487ca" first-frame-successor section
(branch-outcome table = classifier) + E3b REPORT (403,224 kicks / 399,892
drawing-enabled, black upload) + K1 P0 (verified black frame) +
`getDebugSnapshot`/`getDebugHistory` + backend
`SnapshotVram`/`ReadVram`/`Present`; question = does useful nonblack content
reach the active display buffer, and if so where does it disappear
(Guest/GIF → Submit → framebuffer → Present); NOT another 0x501420 census
(G1 closed, G3 dormant); NOT an assumed resource-load wait (retired).
Fork `$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`;
plain commits to FORK remote only; generated runner sources never staged;
ONE P-lane mutator via `/tmp/ssx3-p-lane-lease`; max 1 boot ≤600 s;
builds `-j4` any time; no `adb`; `COPYFILE_DISABLE=1` on every SSD step;
evidence `local/research/E4/` standalone, `[E4]` prefix, no ssx3 push;
experiment contract up front; time box 6 h; report in chunks + tail receipt.

## 1. Experiment contract

Hypothesis H (disjunction over the frontier branches): the steady park loop
issues drawing-enabled kicks that Submit textured batches, yet every
returned presentation image is uniform black; exactly one link of
Guest/GIF → Submit → framebuffer → Present is the first to carry no useful
nonblack result. H1 (surface-black): steady draws target the selected
display FBP but write only black (empty/black texture source, or fully
rejected/cleared) — splits into (b)/(d) by batch census + texture samples.
H0 (present-drops): the display surface holds nonblack but Present returns
black — branch (a). H2 (never-selected): steady content lands only in
non-display buffers — branch (c).
Observable: ONE complete steady vsync-tick window (tick N=600, freeze
M=601; §5): armed GS history (GIF/draw/reg/transfer/present events with
tick/seq), per-tick submitted-draw census incl. per-FBP counts, VRAM
snapshots at N and M (before/after), ReadVram grid samples of every
surviving distinct draw/display surface, full Present-request inputs
(pmode/smode2/dispfb1/display1/dispfb2/display2/bgcolor/tick/context
frames/preferred), P0 presentation PNGs at N..M.
Alternatives: H1→(b) minimize the named batch vs clip/alpha/depth/mask/
texture/CPU-raster, or (d) follow the reached producer branch (clear or
correct reject ≠ bug); H0→(a) follow presentation/address/decode/field/
PMODE; H2→(c) follow producer buffer/flip contract + display-reg writes.
Stop: span-complete (freeze dumps written) + miner joins the chain at one
named boundary, or any cap binds (partial tabled as gap → (e) repair only).
Branch each outcome selects: §6 table (exactly one of a–e).

## 2. Phase-1 survey — what exists vs what the branch table needs

Fork HEAD at inspect: `b34b4818e2c4a75f625d2063bcc43f9fa988fdbd`
(branch `ssx3`; only `M ps2xRuntime/src/runner/register_functions.cpp`,
pre-existing generated, untouched). ssx3 HEAD at inspect: `a9a52a5`.

### 2a. Kick/Submit semantics (verified in source, not assumed)

| # | Claim | Verification |
|---|---|---|
| S1 | Kicks tally BEFORE batch completion/Submit | `gs_frontend.cpp:1533-1539`: `vertexKick` tallies first; `Submit` only at `:1586-1589` after `needed`-vertex assembly + `drawing` gate |
| S2 | drawing=0 kicks never Submit | Same function: `if (drawing && m_backend)` guards batch build + Submit + draw-event record |
| S3 | History defaults PAUSED, cap 512, terminal tail ≠ frame | `gs_frontend.h:235-244` (`m_debugHistoryPaused=true`, `kDebugHistoryCapacity=512`); `recordDebugEventUnlocked` overwrites ring (`:324-351`) |
| S4 | History omits color/texture contents | `GSDebugHistoryEntry` (`gs_frontend.h:53-103`): vertex bounds + `aMin/aMax` only; no RGB, no texels |
| S5 | Only history arming path is the debug-panel UI | `setDebugHistoryPaused` callers: definition + `ps2_debug_panel.cpp:1575` only (scoped grep); no env arming exists |
| S6 | Present decodes DISPFB/DISPLAY/PMODE/SMODE2 + preferred/context fallbacks | `gs_cpu_backend.cpp:1774-1894` (`decodePmode/decodeSMode2/decodeDisplayFrame/decodeDisplaySize/hasDisplaySetup`, preferred-source + fbp==0→context scan + field interlace + alpha normalize) |
| S7 | CPU backend implements textured sprites across PSM families | `DrawSprite` (`:1076+`) + `SampleTexture` (`:972+`: CT32/24/16 + T8/T4 + CLUT; unknown PSM → magenta `0xFFFF00FF`) |
| S8 | No ctxt=1 or fbp=150 draw can hide (whole-run detector) | `[gs:copy-prim]` fires for ANY such draw, cap 32 (`:706-747`); 0 lines in both boots = none occurred |

### 2b. Existing-receipt inventory (K1 + E3b canonical SSD artifacts)

| # | Receipt | K1 | E3b | Boundary signal |
|---|---|---|---|---|
| R1 | Park GS totals (kicks/drawing/gif/copy/dma/gifcpy/gsw/vif) | 3496412/3467726/401340/444942/530791/14388/0/2 | 403224/399892/46384/51955/61741/1710/0/2 | Pre-Submit tallies only (S1); (b)/(d) need submits, not kicks |
| R2 | First 96 kicks (`drawing/prim/vtxCount`) | 96 `[gs:kick]` | 96, same shape | Boot-only; all sampled `drawing=1 prim=6` (sprite) |
| R3 | First 48 GIF packets | 48 `[gs:gif]` | 48 | Boot-only; `ctx0fbp=0 ctx1fbp=0` at boot |
| R4 | First 64 SUBMITTED batches, full state+verts | 64 `[gs:prim]` | 64 byte-IDENTICAL (`cmp` clean) | Boot-only but determinism proof; all sprite/ctxt=0; 17→fbp=112, 47→fbp=0 (§3) |
| R5 | First 128 reg writes / 64 copy-regs / 24 texa | 128/64/24 | same counts | Boot-only; TRX regs (0x50-0x53) configured early (R5b) |
| R6 | Zero display-copy-pattern draws, whole run | 0 `[gs:copy-prim]` | 0 | Preferred-source path never fed (consistent with `preferred=0` on every upload) |
| R7 | Presentation images: first-success + settled | `upload-latest.png` black | `upload-16/17.png` black, byte-identical | Returned pixels black at tick 53/54 AND 1748/14422 (R7b) |
| R8 | Presentation params per upload | 128 `[frame:upload]` + 3641 `[frame:dump]` | 128 + 444 | Always 512×448, fbp 112/112, `preferred=0` (R8b) |
| R9 | PMODE/SMODE2 at kept frames | sidecar `0xff21/0x1` | sidecar `0xff21/0x1` | CRT1-only + interlaced field presentation (R9b) |
| R10 | GS history at any boundary | 0 lines (S5: paused whole run) | 0 lines | MISSING — the joined batch/state record |
| R11 | Steady-frame submitted batches | none (R4 cap spent at boot) | none | MISSING — steady destinations/states unknown |
| R12 | VRAM / surface contents at any boundary | none (`SnapshotVram` callers: Present-internal + unused `snapshotVRAM` + backend swap) | none | MISSING — display-surface blackness unproven |
| R13 | DISPFB/DISPLAY/BGCOLOR/tick/contextFrames at Present | none (P0 logs only result fbps) | none | MISSING — full Present inputs |
| R14 | Transfer/image-upload bytes, texture contents | none (no transfer diagnostics; history S4) | none | MISSING — texture-blackness unproven |

### 2c. Readings that sharpen (but do not close) the question

R4b (early batches target the SELECTED buffer): the 17 fbp=112 prims are
textured sprites (`tme=1 fst=1`, `fbw=8 psm=0x1`, scissor full 512×448,
`tex0 tbp0=0 tbw=8 psm=0x0 tw=10 th=9`) sweeping 32-px strips
(`v0=(1791.5+32k,1823.5)→v1=(+32,2270.5)`, `uv=(32k,0)→(32k+32,447)`,
minus `ofx/ofy=1792/1824` = fullscreen cover) — i.e. a fullscreen textured
blit FROM tbp0=0 INTO the display buffer fbp=112. The 47 fbp=0 prims are
tiny degenerate sprites (`v0≈v1`, `fst=0`, `tbp0=3584 psm=0x1b/T8H`).
R5b: `[gs:reg]` tail shows BITBLTBUF/TRXPOS/TRXREG/TRXDIR writes — image
transfer IS configured early, but zero bytes are receipted (R14).
R7b (E4 re-verified): proper PNG-unfilter decode gives exactly one color
per kept image: uploads `000000ff` (opaque black), fallback `ff00ffff`
(magenta); `upload-16/17.png` byte-identical (9448 B); settled K1/E3b
sidecars share `fnv1a=fd889dc5` at ticks 14422/1748.
R8b: every `[frame:upload]`/`[frame:dump]` success line reads 512×448
fbp=112/112 `preferred=0`; the only exceptions are K1-G5 spliced lines
(`fbp=70/70 size=200x1c0` — concurrent-log interleave, impossible values,
already dispositioned, not a second buffer).
R9b: `pmode=0xff21` decodes (S6) to CRT1-only (`en1=1 en2=0`), `slbg=0`;
`smode2=0x1` = interlaced field mode (`applyFieldPresentation` by tick
parity). Single-CRT path with `usedPreferred=false` throughout.
Determinism note: R4 byte-identical across K1 (242 s) and E3b (31 s) boots
⇒ early GS stream is deterministic; steady-tick choice (§5) is portable,
re-verified on the E4 boot by R4-prefix + first-upload-tick match.

## 3. Hypothesis (Phase-1 form)

H1 (surface-black, favored): the display surface fbp=112 itself holds only
black at presentation — either steady draws sample empty/black textures
(R4b's tbp0=0 source has no receipted upload, R14; `tfx=0` modulate × black
texel = black regardless of grey vertex color), or steady work is
clears/rejects. Present then faithfully returns black (S6 single-CRT path,
R9b). Splits into (b)/(d) ONLY with the steady batch census + texture
samples (§5). H0 (present-drops): fbp=112 holds nonblack but decode/field/
address drops it — needs R12+R13, both missing. H2 (never-selected):
steady content lands only outside fbp=112 — needs R11, missing; early
evidence leans away (R4b draws INTO 112) but early≠steady. No branch is
selectable from Phase-1 receipts alone (§4).

## 4. Decision table (branch selectable vs the ONE missing observation)

| Branch | Needs | Have | Selectable? |
|---|---|---|---|
| (a) nonblack in display surface, black returned | R12 (surface nonblack) + R7 (black out) | R7 only | NO — R12 missing |
| (b) submitted batch, destination gains nothing | R11 (steady batch+state) + R12 before/after | neither steady | NO — R11/R12 missing |
| (c) drawn elsewhere, never selected | R11 destinations + R13 display-reg writes | neither | NO — R11/R13 missing |
| (d) only clears/empty/clipped/no-useful-batches | R11 steady census | pre-Submit kicks (R1) only | NO — R11 missing |
| (e) truncated/unalignable | — | — | NOT terminal: the gap is repairable by the contracted capture |

DECISION: no branch selectable; Phase 2 runs with the exact plan in §5.
The ONE missing observation = the joined steady-frame chain
(submitted batches + states + destination before/after + texture samples +
full Present inputs + returned image) at ONE named boundary (tick 600→601).
Early-boot receipts (R2–R6) cannot substitute: caps spent at boot, and the
review contracts a complete STEADY frame, expanding to a second field/frame
only for display latching.

## 5. Phase-2 capture plan (exact; observation-only, existing interfaces)

Boundary: VBlankStart tick N=600 (arm) → M=601 (freeze). Rationale: uploads
steady since tick ~50 (R8b); 362DE8 park loop ≈55/s from early boot; 600 ≈
10 s is safely steady and safely inside a short run. Expands to M=602 ONLY
if no Present for tick 601 is observed (display-latching rule).
Hook: `EeScheduler::processEvent` VBlankStart (`EeScheduler.cpp:2577-2579`,
exact tick boundary, same site as E3b's `noteVBlank`).

| # | Tap (env-gated; unset = zero behavior change) | Interface | Cap |
|---|---|---|---|
| T1 | `PS2X_E4_ARM_TICK=N`: at tick==N → `clearDebugHistory` + `setDebugHistoryPaused(false)`; stderr `[e4:armed]` | EXISTING history arm | — |
| T2 | `PS2X_E4_FREEZE_TICK=M`: at tick==M → `setDebugHistoryPaused(true)` + dump `getDebugHistory()` text (`e4-history.txt`: seq/tick/frame/kind + full state per entry) + stderr `[e4:frozen]` + `[e4:span-complete]` | EXISTING history read | 512 lines, ≤1 MB |
| T3 | `PS2X_E4_DIR`: `SnapshotVram` at arm (`e4-vram-N.bin`) and freeze (`e4-vram-M.bin`) | EXISTING snapshot | 2×4 MB |
| T4 | ReadVram 32×32 grids over every distinct draw/display surface surviving in the frozen history + the presented display frame (`e4-samples.txt`: per-surface nonblack count, first-nonblack coord, head hex) | EXISTING readback | ≤16 surfaces, ≤64 KB |
| T5 | Present-request inputs at freeze (`e4-present.txt`: pmode/smode2/dispfb1/display1/dispfb2/display2/bgcolor/vsyncTick + `getDebugSnapshot` ctx frames/preferred/transfer + `getPreferredDisplaySource`) | EXISTING snapshot | ≤64 KB |
| T6 | Per-tick submitted-draw census since arm (tick → draws, per-FBP draws) in `e4-history.txt` header/trailer (overflow accounting: history first/last seq vs census) | record-site counters | ≤4 KB |
| T7 | P0 (existing, unchanged): presentation PNG + sidecar every tick; miner joins ticks N..M | EXISTING P0 | existing caps |

Semantics UNCHANGED: taps read + write side files only; no draw/present/
scheduler behavior touched; no regen; no backend swap; no global tracer.
New code: one header `ps2xRuntime/include/ps2_e4.h` + 2-line VBlank hook +
unit tests for env parse + dump formatting (lib-only, no shared headers).
Boot: `e4-boot1.py` modeled on `e3b-boot1.py`: BOUND=span (`[e4:span-
complete]` + 10 s grace) else wall 600 s / 1M trace lines / 800 MB LOG /
E4 12 MB; lean env (PARK + FRAMES + TRACE + E4 vars; no WATCH/394ED0/sema
spam); CWD `$W/P1/run`; foreground under lease; SIGTERM→release at once.
Miner `e4-mine.py`: determinism re-verify (R4 prefix + first-upload tick) →
coverage verdict (history spans whole tick-600 window? census match?) →
join (batches→surfaces→samples→Present→PNG) → branch table (§6).

## 6. Capture record (boot-e4-1, BOUND=span, 1/1 boots)

Pre-claim (T13 §T13-0 verbatim + binary shas): lease absent; `pgrep -x
ps2EntryRunner` exit 1; E4 binary `e21ab707…` 160817056 B (K1 `72b2cfc5…`
163483200 B, E3b `607a3399…` 160795872 B, recorded); ISO 3005415424 +
ELF 3890784 (match); SSD 454 Gi + internal 14 Gi free; selftest ALL PASS;
k1/e3b-waits tails released; suite 448/448/0 (445 E3b baseline + 3 E4).
Claim/release in `$W/P1/run/e4-waits.log` (2 lines).

| Cap | Bind | Hit? |
|---|---|---|
| Wall | 600 s | No (25 s: span-complete ~15 s + 10 s grace, SIGTERM rc=0) |
| Progress | 1M trace lines | No (81,532) |
| Bytes (LOG) | 800 MB | No (2.8 MB; trace 4.9 MB) |
| E4 bytes | 12 MB | No (8,484,282 B: 2×4 MB VRAM + 74 KB history + 1.5 KB texts) |

Fork taps (lib-only, env-gated, unset = zero behavior change): new
`ps2xRuntime/include/ps2_e4.h` (env binds, VBlank arm/freeze, history/
VRAM/ReadVram/Present dumps, T6 census) + 1-line VBlank hook in
`EeScheduler.cpp:2580` + 4-line T6 hook in `gs_frontend.cpp:346-349` +
3 unit tests in `ps2_gs_tests.cpp`. Semantics unchanged (read + side
files only). Build `-j4`: tests exit 0, suite 448/448/0, runner exit 0.
Sidecar trap (K1-shaped): edit tooling created 4 `._*` files, globbed as
sources on first build; removed mine only (pre-existing `._ps2_log.h`
left), rebuilt clean.
Determinism re-verify: R4 `[gs:prim]` byte-identical to K1 (64 lines);
first upload tick 47 (K1 49, E3b 53 — same epoch); park GS rate matches
(327096 kicks / 25 s). Steady window is portable.
Coverage: 228/512 entries, seq 1→228, all tick 600; T6 census 122 draws
== 122 draw events (no overwrite, complete tick-600 window). Present for
tick 601 observed (`[frame:dump] seq=90 tick=601`), so no M=602 expansion.

## 7. Branch classification (exactly one) + hypothesis update

Steady tick-600 join (all receipts in-evidence):

| Link | Finding | Receipt |
|---|---|---|
| GIF production | 46 packets feed the window | history kinds |
| Submit | 122 draws, ALL fbp=0 (120 sprites tme=1/abe=1/fst=0/ctxt=0 + 2 degenerate tristrips), real on-screen bounds x −0.5..252.8 y −0.5..529.2, scissor open, fbmsk=0; textures T4@10760 + T8H@3712 both nonzero (156 + 312 grid hits) | history + e4-samples (texture rows valid) |
| Destination fbp0 | 12,563 rgb-nonblack px (4.8%), bbox (0,2)-(251,438), 279/512 rows; thumbnail shows a small coherent colored icon | VRAM-bin decode (miner P3) + e4-fbp0.png |
| Display select | CRT1-only PMODE 0xff21, DISPFB1 = fbp112/fbw8/psm1, 512×448, preferred=0 (0 ctxt=1 draws ever, hasPreferred=0) | e4-present.txt + 0 `[gs:copy-prim]` |
| Display surface fbp112 | rgbNz = 0/229,376 (20,753 alpha-only words, CT24-ignored) — BLACK | VRAM-bin decode (miner P3) + e4-disp1.png |
| Returned image | ticks 600+601 hash `fd889dc5` (black), settled PNG verified black | `[frame:dump]` + upload-latest.png |
| Frame delta | VRAM byte-identical arm→freeze (sha `77eb48d9…` both) — steady loop redraws identical pixels | both bins |

| Branch | Test | Result |
|---|---|---|
| (a) nonblack in display surface, black returned | fbp112 rgbNz>0? | NO — 0 (E1-corrected; initial 50-sample hit was misaddressed, §9) |
| (b) submitted batch, destination gains nothing | fbp0 holds content? | NO — 12,563 rgb px; identical-VRAM = same-value steady rewrite, not rejection (bounds real, scissor open, fbmsk=0) |
| (c) drawn elsewhere, never selected | steady→fbp0, display→fbp112? | YES — all 122 steady draws target fbp0; display reads black fbp112; no flip/preferred path feeds it |
| (d) only clears/empty/clipped/no-useful | 120 real textured sprites + icon content? | NO — genuine production, wrong buffer |
| (e) truncated/unalignable | coverage complete? | NO — 228/512 full window, census match, E1 repaired miner-side |

CLASSIFICATION: (c). Hypothesis update: H1 (surface-black) holds for the
SELECTED surface (fbp112 is truly black — Present is faithful, not the
first loss); H2 (never-selected) is the located first-missing-result: the
game's current visible production lands in fbp0 and no display path
selects it. H0 (present-drops) falsified for this window.
NEXT ACTION (prescribed by the branch table, not this brief): follow the
producer buffer/flip contract + actual display-register writes — why does
steady production target fbp0 while DISPFB1 holds fbp112, and what flip/
select sequence (guest writes? missing SetGsCrt/completion?) would join
them. No SIF/CD promotion (no dependency names it); no raster/Present fix
follows from this window.

## 8. Exact commands (abridged; full scripts in-evidence)

Phase 1 (inspect, no boot): read review §follow-up-57487ca + E3b/K1
REPORTs + fork `gs_frontend.h`/`gs_backend.h`/`gs_frontend.cpp:1533-1589,
267-300, 528-630`/`gs_cpu_backend.cpp:1774-1894` + park snapshots +
`grep -c/-o` censuses over `boot-k1-1.log`/`boot-e3b-1.log` + `cmp`
R4-identical + PNG-unfilter verify + `ps2_park_snapshot.h` tally sites.
Phase 2: wrote `ps2_e4.h` + 2 hooks + 3 tests → purged 4 `._*` sidecars →
`cmake --build /tmp/p1-link/runtime --target ps2x_tests -j4` (exit 0) →
suite at fork root 448/448/0 → `--target ps2EntryRunner -j4` (exit 0,
`e21ab707…` 160817056 B) → pre-claim checks → claim → `python3
/tmp/e4-boot1.py` (BOUND=span 25 s) → release + verify → `python3
local/research/E4/e4-mine.py` (miner exit 0) → keeps + report → fork
commit + push (fork remote) → evidence commit `[E4]` (no push).

## 9. Gaps / errata

E1 (T4 frame-surface base units — REPAIRED miner-side, no new capture):
`ps2_e4.h` T4 passed FBP pages to `GS::ReadVram`, which takes BLOCKS
(frame path converts via `framePageBaseToBlock`, fbp<<5; texture TBP0 is
already blocks). Effect: `e4-samples.txt` disp1 row read block 112
instead of 3584 (the "50 nonblack" was fbp0-region content) — DISCARDED;
draw-tex rows (156/312) and fbp0-base rows (base 0, unaffected) stand.
Repair: miner P3 decodes both frame surfaces from the retained VRAM bins
with correct addressing; branch rests on the repair, which the
misaddressed row cannot overturn (it never read fbp112).
G1 (priv-reg write history): history records GS regs, not PMODE/DISPFB/
DISPLAY writes — the successor's flip-contract work needs that series
(display-reg tap or PC-anchored write log); E4's window bounds the
question (select=112 vs produce=0) without answering it.
G2 (numbered keeps): P0 keeps first-2 + latest PNGs only, so ticks
600/601 join by hash (`fd889dc5` = black), not kept PNGs — same proxy
K1 used, collision-implausible over 917,504 B, settled PNG verified.
G3 (texture full decode): T4 grids prove textures nonzero; full texel
maps (T4/T8H swizzle) left to the successor's minimize-batch step.
Box: ~3 h active, inside 6 h. Lease held 03:04:32–03:05:05Z, verified
absent at close (pgrep 1).

---
Tail receipt: REPORT.md §§0–9 complete; e4-boot1.py + e4-mine.py +
e4-history.txt (228 ev) + e4-present.txt + e4-samples.txt (E1-caveated) +
e4-vram-{arm,freeze}.bin.gz (sha 77eb48d9… both) + e4-{disp1,fbp0}.png +
upload-latest.png/.txt + e4-liveness.log in-evidence (13 files).
Fork: `a13b66a` pushed fork ssx3 (`b34b481..a13b66a`; 4 files, +649:
ps2_e4.h new + EeScheduler + gs_frontend + gs_tests;
register_functions.cpp untouched). Evidence
`[E4]` committed, unpushed (orchestrator pushes). Lease verified absent
at close. Branch: (c) — drawn to fbp0, display reads black fbp112.
