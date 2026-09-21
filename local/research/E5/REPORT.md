# E5 — Producer buffer/flip contract + display-register writes

Standalone evidence. Phase 1 (no boot): existing-receipt survey + decision
below. Phase 2 (one bounded capture): §6+ (only the named gap is captured).

## 0. Steering inputs (recorded verbatim per instruction)

Task brief: tables + hypothesis + next-action recommendation, no verdicts;
read `local/research/E4/REPORT.md` first (all of it: branch (c) — steady
tick-600 production is 122 draws ALL into fbp0, fbp0 holds a 12,563-px icon,
DISPFB1 holds fbp112 which is truly black, Present is faithful; G1: priv-reg
write history missing — history records GS regs, not PMODE/DISPFB/DISPLAY
writes). This brief executes E4 §7's prescribed next action. Reuse E4's taps
(`ps2_e4.h` arm/freeze/history/VRAM/Present at fork `a13b66a`, pushed) —
extend, do not rebuild.
Facts you start from: the located gap (steady production targets fbp0 while
DISPFB1 holds fbp112, no flip/preferred path feeds fbp112); the question WHY
— what producer buffer/flip contract is in force, and what flip/select
sequence (guest display-reg writes? missing SetGsCrt/completion?) would join
production to display. Phase 1 (no boot): inspect EXISTING receipts for the
flip contract; if existing receipts name the contract + the missing join, NO
boot runs. Phase 2 (ONE bounded capture, only if a missing observation
requires it): observation-only taps at EXISTING interfaces (E4 taps reused;
ONE new tap allowed: a PMODE/DISPFB/DISPLAY write series, per-tick or
PC-anchored, at the same named boundary tick 600→601); preserve the write
series + the joined production→display chain. No new global tracer, no
regen, no backend swap, semantics UNCHANGED. Cap all log streams by bytes
AND wall time. Outcomes (tabled, not verdicts): (i) contract + missing join
named → the ONE next action that join prescribes; (ii) contract named but
join needs a receipt this box cannot take → exact probe recipe, stop;
(iii) observation truncated/unalignable → repair that measurement gap,
nothing else. No SIF/CD promotion unless that dependency names it; no
raster/Present fix follows from a flip-contract window. Fork
`$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`, branch `ssx3`. Plain
commits, pushed to the FORK remote only, never upstream. Generated runner
sources never staged. ONE P-lane mutator: coordinate via the lease, never
parallel boots. NO regen (still gated on the 0x426230 DROP disposition —
observation taps only).
Gates and rules: capture boot (Phase 2, if needed) ONLY while holding
`/tmp/ssx3-p-lane-lease` (SHARED P-lane) — poll every 5 min + log waits to
`$W/P1/run/e5-waits.log` if taken. Max 1 boot ≤600 s (Part 4 budget);
wall + progress + BYTE caps recorded, abort past any cap. Builds `-j4`
any time. No `adb`. `export COPYFILE_DISABLE=1` on every SSD step. Retain:
the capture + receipts that prove the finding (compress closed raws; single
canonical copies). Evidence dir `local/research/E5/` (STANDALONE). Commit
with `git add -f`, prefix `[E5]`, trailer `Orchestrated-By: Muse Code`. Do
not push ssx3 (orchestrator pushes at poll when the tree is clean). Fork
commits pushed to fork remote (table SHAs; none if Phase 1 suffices).
Experiment contract up front (hypothesis/observable/alternatives/stop +
which outcome each selects). Time box: 6 h. Hygiene: report in chunks +
tail receipt (truncated tail fails the gate).

## 1. Experiment contract

Hypothesis H (disjunction over the join mechanism): the game's producer
buffer/flip contract is direct-register management by the game engine (no
libgraph/HLE path — zero `sceGs*` calls, zero EE#2 `SetGsCrt` on the
runtime across 3 boots vs REF 2–4×, §3); scanout is fixed at fbp112 since
the boot display-init burst (~tick 40→49, §3) while production is fixed at
fbp0. J1 (never-reached): the game's per-frame display-update step never
executes in steady state — zero PMODE/DISPFB/DISPLAY writes in the
tick-600 window on every channel. J2 (stuck-index): the display-update
executes but re-selects the same buffer — same-value DISPFB1 rewrites
visible in the write series (GIF half of J2 already excluded: 0 `0x59–0x5C`
events in E4's complete tick-600 history, §3; only MMIO can carry J2).
Observable: ONE steady window (tick N=600 → M=601, E4 taps reused verbatim)
+ the PMODE/DISPFB/DISPLAY/SMODE2/BGCOLOR MMIO write series from boot
through freeze — PC-anchored, all widths — via the EXISTING P1f watchpoint
(`PS2X_DIAG_WATCH`, no new tap needed, §5); the series covers the boot
display-init burst (~40→49) for free since the watch is not tick-gated.
Alternatives: J1 → the ONE next action is the gate analysis (locate the
guest present/flip code statically + receipt what parks the frame loop
before it); J2 → follow the buffer-index/completion state that never
toggles (+ the flip-code PCs come free from the watch). Stop:
span-complete (freeze dumps written) + the write series joins to the
E4-shape chain at 600→601, or any cap binds (partial tabled as gap →
outcome (iii) repair only). Outcome each selects: §7 table (exactly one of
i–iii). SIF/CD promotion only if the series names that dependency (it
cannot — a write series names code addresses, not upstream waits).

## 2. Phase-1 survey — what exists vs what the join needs

Fork HEAD at inspect: `a13b66a` (E4 taps, pushed fork `ssx3`; only
`M ps2xRuntime/src/runner/register_functions.cpp`, pre-existing generated,
untouched). ssx3 HEAD at inspect: `ec68653`.

### 2a. Display-register write-path inventory (verified in source)

| # | Path | Writes which regs | Receipt-or-rule-out |
|---|---|---|---|
| W1 | Guest MMIO stores → `PS2Memory::write32/write64` GS-priv branches (`ps2_memory.cpp:974/1034`; `write128` funnels to `write64` ×2) | PMODE SMODE2 DISPFB1/2 DISPLAY1/2 BGCOLOR + rest | NO RECEIPT at any tick, any boot (G1 stands for writes; §3). `write8/16` have NO GS-priv branch — `sb/sh` to `0x1200…` are silently lost (drop mechanism, noted, not evidenced) |
| W2 | GIF A+D emulator mirror (`gs_frontend.cpp:1509-1527`: `0x59/0x5A/0x5B/0x5C/0x5F`) | DISPFB1/2 DISPLAY1/2 BGCOLOR only (NO PMODE/SMODE2 alias) | Steady: RULED OUT (0 events in E4's complete 228/228 tick-600 window, §3). Boot burst: UNKNOWN (`[gs:reg]` 128-cap spent on `0x05/0x03` before the ~40→49 transition) |
| W3 | HLE EE#2 `SetGsCrt` (`System.cpp:7-34`) | SMODE2 + PMODE-bit0 ONLY (never DISPFB/DISPLAY) | RULED OUT on runtime: 0 calls across K1+E3b+E4 (no `id=0x2` in `[diag:syscall]` census; 0 `PS2 GsSetCrt:` lines, unconditional when called). REF issues it 2×/boot-window (T18), 2–4×/full-run (T17/T27/T28/T29) |
| W4 | HLE `sceGs*` libgraph stubs (`Stubs/GS.cpp`: `PutDispEnv→applyGsDispEnv` writes PMODE/DISPFB/DISPLAY; `SwapDBuff→applyGsDispEnv` + draw-env pairs + clear packet) | PMODE DISPFB DISPLAY + draw envs | RULED OUT: 0 `sceGs*`/`swapdbuff` lines in all 3 boot logs (the `[gs:swapdbuff]` emitter is cap-32 but the call itself is unlogged-capped nowhere else; `SwapDBuff` non-Dc has NO log line — see gap G2) |
| W5 | `writeIORegister` GS-priv branch (`ps2_memory.cpp:1166-1184`) | same set as W1 | UNREACHABLE per in-code NB (all `write*` funnel through `PS2_IO_BASE`-disjoint handling); its `gsw=` counter reads 0 at every sample on every boot — VACUOUS, proves nothing about W1 traffic (E5 finding F5) |

### 2b. Display-select state series (all existing, all constant)

| # | Receipt | Ticks covered | Value | Reads as |
|---|---|---|---|---|
| R1 | `[frame:dump]` transition (K1: last fallback tick 40 → first success tick 49; E4 same shape, first upload ~47) | 0→49 | `640×512 fbp=0/0 fallback=1` → `512×448 fbp=112/112` | Boot display-init burst lands strictly inside ~40→49; its PATH (W1 vs W2) + PCs + values are unreceipted (G1) |
| R2 | `[frame:dump]` success lines (K1: 3,465+ clean; E3b/E4: all) | 49→14,422 | every line `512×448 fbp=112/112 preferred=0` (spliced-line exceptions dispositioned in E4) | No select change on the read side for the whole settled run |
| R3 | `[run:tick]` priv samples (K1: 31 samples host-tick 120→3720 + E3b/E4) | host 120→3720 | `dispfb1=0x9070 display1=0x1bfa0002032281` CONSTANT (FBP112/FBW8/CT24) | Same, coarser; host-tick (present-loop) cadence, not vsync |
| R4 | E4 T5 `e4-present.txt` (tick 601) | 601 | `pmode=0xff21 smode2=0x1 dispfb1=0x9070 … preferred has=0` | Full Present inputs; CRT1-only; `dispfb2=0x1400` still the emulator default (W-path never touched circuit 2) |
| R5 | Emulator defaults (`ps2_memory.cpp:390-393`) | boot | `dispfb=0x1400` (FBP0/FBW10/CT32), `display1=0x1BF0000027F0000` | Observed R1–R4 values ≠ defaults ⇒ SOMETHING wrote the burst (W1 and/or W2); HLE (W3/W4) ruled out ⇒ guest-direct |

### 2c. Producer-side contract (all existing)

| # | Receipt | Finding |
|---|---|---|
| P1 | E4 history (complete window, 228/512, T6 census match 122=122) | 122/122 steady draws → fbp0; real bounds; textures T4/T8H nonzero; ZERO `0x59–0x5C` reg events (W2 ruled out steady) |
| P2 | E4 T5 ctx rows | `FRAME_1 = FRAME_2 = fbp0/fbw8/CT32` in BOTH contexts — no draw-buffer ping-pong |
| P3 | E4 history reg census (`0x4C` ×1, `0x4D` ×0) | One `FRAME_1` write in-window (keeps fbp0); `FRAME_2` never touched in-window |
| P4 | K1/E3b `[gs:copy-reg]` (`ctx0fbp=112` → `ctx0fbp=0` transitions) + E4 R4b (17 fullscreen `tbp0=0→fbp112` blits + 47 degenerate fbp0 sprites in first-64) | Boot-time join was a BLIT (draws into fbp112, wrote black — empty source), then draw target returned to fbp0 and never left |
| P5 | Zero-copy-pattern + preferred (`[gs:copy-prim]` 0 whole-run ×3 boots; `preferred has=0`; E4 `transfer total=0 copied=16`) | No preferred-source path; no ctxt=1/fbp=150 copy pattern; transfer snapshot shows a 16-px historical copy, no live copy traffic evidenced |
| P6 | Per-frame engine rate (E3b: `362DE8` 1706/1706 balanced ≈55/s; E4: park GS rate matches; 6 active threads) | The game's per-frame function RUNS at full rate — the loop is not globally parked; only the display-update step is missing |

### 2d. Findings (tabled, not verdicts)

| # | Finding | Forcing receipts |
|---|---|---|
| F1 | Scanout contract = FIXED single-buffer fbp112 (no flip traffic on any observed channel, 3 boots, ticks 49→14,422+) | R2 R3 R4 + W3/W4/W2-steady rule-outs |
| F2 | Producer contract = FIXED draw target fbp0 in both contexts (no FRAME ping-pong) | P1 P2 P3 |
| F3 | Boot display-init (PMODE/SMODE2/DISPFB1/DISPLAY1) fired once ~tick 40→49 via guest-direct writes (W1 and/or W2); path/PCs/values unreceipted | R1 R5 |
| F4 | Boot join was a blit (tbp0=0→fbp112, wrote black), fired once, never again in steady state | P4 + P1 (0 steady fbp112 draws) |
| F5 | `gsw=` (GS MMIO-write counter) is vacuous — counts only the unreachable `writeIORegister` GS branch; `gsw=0` constrains NOTHING | `ps2_memory.cpp:1166-1184` NB + R3 samples |
| F6 | REF-vs-runtime syscall divergence receipted: `SetGsCrt` REF 2–4×/run, runtime 0× (T18 `ref=2 rt=0`; K1/E3b/E4 censuses lack `0x2`; 0 HLE log lines) — but the runtime HLE sets SMODE2+PMODE-bit0 only, so SetGsCrt is NOT the join (it cannot select DISPFB) | T18/T17/T27/T28/T29 censuses + W3 source |
| F7 | J1-vs-J2 (never-reached vs stuck-index) is NOT splittable from existing receipts: the MMIO write series (W1) is missing at ALL ticks — no boot ever watched `0x12…` (watch census §3: `0x50…/0x70…/0x8007…` only), history omits priv by construction (E4 G1), HLE logs cover only HLE | §3 watch scan + E4 G1 |

## 3. Hypothesis (Phase-1 form)

H (contract, favored): SSX3's engine manages display registers directly
(W1 and/or W2); its steady contract is FIXED draw-at-fbp0 + FIXED
scanout-of-fbp112 with NO per-frame display update executing through any
observed channel (F1 F2). The missing join is the game's own per-frame
display-update step — either a DISPFB1 select of the completed buffer
(`0x12000070 ← FBP0/FBW8/CT32`-shaped value, or GIF A+D `0x59`) or a
re-fire of the boot blit (fbp0-content → fbp112). J1 vs J2 (never-reached
vs same-value stuck-index) selects the next action but needs the write
series (§4). H0 (present-drops): already falsified for this window by E4
(Present faithful, fbp112 truly black). H2 (HLE/libgraph flip):
falsified — W3/W4 zero-call across 3 boots, and W3 cannot select DISPFB
anyway (F6).

## 4. Decision table (Phase 2: the ONE missing observation)

| Question | Needs | Have | Selectable? |
|---|---|---|---|
| Contract in force (fixed fbp0 produce / fixed fbp112 scanout, guest-direct) | R1–R5 + P1–P6 + W1–W5 inventory | all committed above | YES — named (F1 F2) |
| Join sequence that WOULD join production to display | inverse of observed select + boot-blit shape | `DISPFB1 ← fbp0-select` (MMIO `0x12000070` / GIF `0x59`) or `tbp0=0-region → fbp112` blit re-fire | YES — named |
| J1 (never-reached) vs J2 (stuck-index) | W1 write series at 600→601 (PC-anchored, all widths) | MISSING at every tick (F7) | NO — THE gap |
| Boot-burst path (W1 vs W2) + PCs + values | same series over boot → freeze | MISSING (R1 bounds it to ~40→49 only) | NO — same gap, same capture |

DECISION: contract + join named (§§2–3); J1/J2 + boot-burst path require
the ONE missing observation = the PC-anchored `0x12000000`-block MMIO
write series (addr+value+width+tick+pc/thread/ra/sp) from boot through the
named 600→601 boundary. No existing receipt substitutes (F7). Phase 2 runs
with the exact plan in §5 — ZERO fork changes (the P1f watchpoint is an
existing interface and covers MMIO stores pre-split at all widths,
`ps2_runtime_macros.h:361-427` + `Store8/16/32/64/128`).

## 5. Phase-2 capture plan (exact; observation-only, existing interfaces)

Boundary: VBlankStart tick N=600 (arm) → M=601 (freeze), E4-identical.
Watch: `PS2X_DIAG_WATCH=0x12000000,0x12000020,0x12000070,0x12000080,0x12000090,0x120000A0,0x120000E0`
(PMODE SMODE2 DISPFB1 DISPLAY1 DISPFB2 DISPLAY2 BGCOLOR; 8-B overlap match
catches `sw`/`sd` halves; `sq` spans two lines via `write128→write64` ×2 —
plus the W-macro/Store double-report: each MMIO store emits TWO identical
`[diag:watch]` lines, `e3src=0/1` — miner dedupes).
Env otherwise E4-lean verbatim (PARK + FRAMES + TRACE + E4 vars; no
394ED0/sema spam). Boot: `e5-boot1.py` modeled on `e4-boot1.py`:
BOUND=span (`[e4:span-complete]` + 10 s grace) else wall 600 s / 1M trace
lines / 800 MB LOG / E4 12 MB; CWD `$W/P1/run`; foreground under lease;
SIGTERM→release at once. Miner `e5-mine.py`: determinism re-verify (R4
prefix + first-upload tick + E4-history shape match) → watch-series table
(boot burst + steady window, deduped) → GIF `0x59–0x5C` re-check in the
frozen history → J1/J2/outcome table (§7).
Semantics UNCHANGED: watch + E4 taps read + write side files/lines only;
no draw/present/scheduler behavior touched; no regen; no backend swap; no
global tracer; no fork diff at all (binary `e21ab707…` reused).

## 6. Capture record (boot-e5-1, BOUND=span, 1/1 boots)

Pre-claim (T13 §T13-0 verbatim + E4 binary shas): lease absent; `pgrep -x
ps2EntryRunner` exit 1; E4 binary `e21ab707…` 160817056 B (rebuild no-op,
`ninja: no work to do`); ISO 3005415424 + ELF 3890784 (both paths match);
SSD 452 Gi + internal 14 Gi free; suite 448/448/0 from fork root (re-green;
note: run from any other CWD one test fails on a working-directory
assumption — `instructions.h should be readable from the test working
directory` — E4-identical gate, recorded); k1/e3b/e4-waits tails released;
caps recorded (wall 600 s / progress 1M trace lines / 800 MB LOG /
E5-dir 12 MB); sidecars E4-identical (pre-existing `._ps2_log.h` + `.git`
internals only). Claim/release in `$W/P1/run/e5-waits.log` (2 lines).

| Cap | Bind | Hit? |
|---|---|---|
| Wall | 600 s | No (25 s: span-complete ~15 s + 10 s grace, SIGTERM rc=0) |
| Progress | 1M trace lines | No (85,690) |
| Bytes (LOG) | 800 MB | No (4.2 MB) |
| E5 bytes | 12 MB | No (8,483,975 B: 2×4 MB VRAM + 73 KB history + texts) |

Fork diff: NONE (zero source changes; P1f watch is pre-existing;
`a13b66a` untouched + pre-existing generated `M register_functions.cpp`).
Lease held 03:32:50–03:33:24Z (34 s), verified absent at close (pgrep 1).
Determinism re-verify: `[gs:prim]` 64/64 byte-identical to K1; transition
last-fallback (seq 15, tick 41) → first-success (seq 16, tick 53), same
shape as K1/E3b/E4; VRAM arm+freeze sha `77eb48d9…` both = E4's canonical
bytes (NOT duplicated in E5 evidence — pointer to E4); T5 present-inputs
byte-identical to E4's (§7). History 227/228 vs E4 (off-by-one = the
`kind=present` event absent; all content counts identical: 122 draws
fbp0=122, 46 gif, 59 reg, coverage seq 1→227 tick 600 — watch-per-store
overhead shifted the Present-vs-freeze interleave; immaterial: Present
inputs separately captured identical).

## 7. Finding table (exactly one of i–iii) + hypothesis update

Steady tick-600 join (all receipts in-evidence):

| Link | Finding | Receipt |
|---|---|---|
| MMIO write series | 1,465 display-update bursts whole-run (~59/s ≈ game-frame rate); EXACTLY ONE 5-write burst inside 600→601 (PMODE 0xff21, SMODE2 0x1, DISPFB1 0x9070, DISPLAY1 …, BGCOLOR 0 — all same-as-steady) | `e5-watch-series.txt` (7,329 deduped; 13,171 raw, PMODE ×1/store via direct-Store path, rest ×2 W-macro+Store) |
| DISPFB1 values | 1,466/1,466 = 0x9070 (ZERO non-steady); SMODE2/DISPLAY1/BGCOLOR likewise constant; PMODE 1,464× 0xff21 + 1× 0xff20 (first boot write only) | miner value census |
| Write PCs | PMODE←0x382cac, SMODE2←0x382cd0, DISPFB1←0x382cf0, DISPLAY1←0x382e5c, BGCOLOR←0x382e70; entry 0x382af0; steady ra=0x382824 (thread 5), boot ra=0x37c160 (thread 1, first burst only) | miner pc/thread census |
| Value provenance | PMODE = `0xff20‖$a1` (caller param; steady $a1=1); SMODE2/DISPFB1/DISPLAY1/BGCOLOR composed from config-struct loads `$t9+0x5aXX` with `$t9:=$a0` in prologue — FBP var @ S+0x5a88 (=112, stuck), FBW @ +0x5a5c (=8), PSM @ +0x5a38 (=1); static-$t9 refuted (entry+off = code) | `e5-flip-dis.txt` |
| Boot burst | First burst ln 208–215 @tick ~38–40 (thread 1, PMODE 0xff20); enable 0xff21 from burst 2 (ln 501, tick ~40, thread 5); first success presented tick 53 (P0 cadence gap 42–52 unattributed, no dumps) | series head + dump brackets |
| GIF path | 0 `0x59–0x5C` events in E5 history (second window) | `e5-history.txt` |
| HLE paths | 0 EE#2 + 0 `sceGs*` (4th boot confirming) | `boot-e5-1.log` census |
| Joined chain | T5 + VRAM + history + dumps identical to E4 at the boundary | `e5-present.txt` (= E4 byte-identical), `e5-history.txt`, `upload-latest.*` (tick 1508, black 112/112) |

| Outcome | Test | Result |
|---|---|---|
| (i) contract + missing join named → ONE next action | J1 (zero in-window writes) vs J2 (same-value in-window burst) | J2 — exactly one same-value 5-write burst in 600→601; the display-update RUNS and re-selects fbp112 every frame while production targets fbp0 |
| (ii) contract named but join needs an off-box receipt | — | NO — the series was takable on this box (existing watch, zero code) |
| (iii) truncated/unalignable | coverage complete? | NO — span-complete, 227/512 full window, census match, series joins by line-order markers |

CLASSIFICATION: (i) via J2 (stuck-index). Hypothesis update: the flip
contract is a per-frame guest-direct display re-assert
(`0x382af0`, ~59/s, thread 5, caller `0x38281c`) sourcing every field from
a config struct S (`$s0` at the call) — PMODE from an enable param,
all other fields from `S+0x5aXX` loads — and the display-FBP variable
(`S+0x5a88`) never advances from 112 while the producer (draw contexts +
FRAME, fixed fbp0) never meets it. The missing join is the advance of
`S+0x5a88` 112→0 (J2a, favored: the select is a loaded variable, not an
immediate) or, if S+0x5a88 proves intentionally constant, the re-fire of
the boot blit (J2b, not dead — the copy mechanism exists and fired once).
NEXT ACTION (prescribed by the join, takable on this box): source-trace S
from the steady call (`$s0` @ `0x38281c`, `$a0` @ `0x382af0`): find S's
allocation + the writer(s) of `S+0x5a88` (PS2X_DIAG_WATCH on its runtime
address once located — same zero-code capture shape) + the producer-side
FBP field and the advance/copy logic that should join them. If `S+0x5a88`
is never written after boot-init → follow the gate parking the advance;
if written-but-never-0 → follow the producer index/completion. No SIF/CD
promotion (the series names code addresses, not upstream waits — nothing
names that dependency); no raster/Present fix follows from this window
(Present faithful, second boundary).

## 8. Exact commands (abridged; full scripts in-evidence)

Phase 1 (inspect, no boot): read E4 REPORT + `e4-present/history/samples`
+ fork `ps2_memory.cpp` (W1 paths + `gsw` vacuity) + `gs_frontend.cpp`
(W2 mirror `0x59–0x5C`, map enum) + `System.cpp` (W3 body) + `Stubs/GS.cpp`
(W4 bodies) + `ps2_runtime_macros.h` + `Store*` (watch MMIO coverage +
double-report) + `diagWatchAddrs` (base-0 parse) + T18/T17/T27/T28/T29
censuses (REF `SetGsCrt` 2–4× vs runtime 0×) + `grep` censuses over
`boot-k1/e3b/e4-1.log` (watch addrs — never `0x12`; `[diag:syscall]` ids —
never `0x2`; `sceGs`/`swapdbuff` — zero; `[run:tick]` constancy;
`[gs:reg]`/`[gs:copy-reg]` addrs — never `0x59+`).
Phase 2: wrote `e5-boot1.py` (E4 verbatim + `PS2X_DIAG_WATCH` display
block) → pre-claim checks → `cmake --build … --target ps2x_tests -j4`
(noop exit 0) → suite from fork root 448/448/0 → `ps2EntryRunner -j4`
noop (binary reuse `e21ab707…`) → claim 03:32:50Z → `python3
/tmp/e5-boot1.py` (BOUND=span 25 s) → release 03:33:24Z + verify →
`python3 local/research/E5/e5-mine.py` (exit 0) → rate/provenance/`$t9`
follow-ups → bounded static slices (`/tmp/e5-dis.py`, capstone +
`/tmp/a0_elf.py`) → keeps + report → evidence commit `[E5]` (no push; no
fork commit — zero diff).

## 9. Gaps / errata

G1 (E4 G1, CLOSED for writes): the priv-reg write series existed nowhere;
E5 took it (boot→freeze, PC-anchored, all widths) with zero new code. The
`tick~` column is nearest-preceding-dump (sparse-P0 artifact — clumps and
zero-count ticks are unattributed, not real); line-order windowing
(armed/frozen markers) is exact and carries the finding.
G2 (W4 logging hole, noted): non-Dc `sceGsSwapDBuff` has NO log line, so
"0 `sceGs*` lines" rules out Dc-flavored + error paths strongly but the
plain-`SwapDBuff` call itself only via absence of its unlogged body —
IMMATERIAL to the finding (the game's actual flip path is receipted direct
at `0x382af0`, and any HLE-applied DISPFB change would still show on the
read side, which is constant).
G3 (PMODE single-report): PMODE stores emit ONE `[diag:watch]` line vs
TWO for the other six watched regs — consistent with the recompiler's
constant-MMIO-store direct-`Store64` path (bypasses the W-macro
pre-report); coverage is unaffected (≥1 line per store on every path).
22/5,864 non-PMODE singleton pairs (0.4%) attributed to log interleave;
dedupe is by consecutive-identity, tolerant to both. Line accounting:
13,188 `addr=0x12` grep-hits = 13,171 fully-formed (mined) + 17
interleave-shredded (`[frame:upload]`/`FILEIO` spliced mid-line,
pre-existing behavior; visible values all steady); the single shredded
PMODE line explains the 1465-vs-1466 PMODE count.
G4 (E5 history off-by-one): 227 vs E4's 228 (`kind=present` absent) —
watch-per-store overhead shifted the Present-vs-freeze interleave; all
content counts + T5 + VRAM identical, finding unaffected.
G5 (P0 cadence gap): no `[frame:dump]` ticks 42–52, so the first-success
transition (regs set ~40, presented 53) is unattributed inside the gap —
bounds only, immaterial (steady window is the finding).
G6 (struct-S hunt remains): `$t9:=$a0:=$s0` chain receipted through the
steady call; S's allocation address + `S+0x5a88` writer(s) + producer-side
field + advance/copy logic are the prescribed next action's Task 1 (static
from `0x3827e0`/`0x37c160` + `PS2X_DIAG_WATCH` once located).
Box: ~2.5 h active, inside 6 h. Lease held 03:32:50–03:33:24Z (34 s),
verified absent at close (pgrep 1).

---
Tail receipt: REPORT.md §§0–9 complete; e5-boot1.py + e5-mine.py +
e5-watch-series.txt (7,329 deduped / 13,171 raw) + e5-history.txt (227 ev)
+ e5-present.txt (= E4 byte-identical) + e5-samples.txt + e5-flip-dis.txt +
upload-latest.png/.txt (tick 1508, black 112/112) + e5-liveness.log
in-evidence (11 files incl. REPORT). VRAM bins NOT duplicated (sha `77eb48d9…` both =
E4 canonicals). Fork: NO commit (zero diff; binary `e21ab707…` reused).
Evidence `[E5]` committed, unpushed (orchestrator pushes). Lease verified
absent at close. Outcome: (i) via J2 — display re-assert runs per-frame,
`S+0x5a88` stuck at 112; next: source-trace S + its advance logic.
