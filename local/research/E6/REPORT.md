# E6 — Source-trace display-config struct S: S+0x5a88 writers + advance logic

Standalone evidence. Phase 1 (no boot): static source-trace below + decision
in §4. Phase 2: NOT RUN (§5 — static names allocation + join + gate).

## 0. Steering inputs (recorded verbatim per instruction)

Task brief: tables + hypothesis + next-action recommendation, no verdicts;
read `local/research/E5/REPORT.md` first (all of it: outcome (i) via J2 —
per-frame guest-direct display re-assert `0x382af0` (~59/s, thread 5,
caller `0x38281c`) sources every field from config struct S (`$s0` at the
call); display-FBP variable `S+0x5a88` stuck at 112 while production draws
at fbp0; G6: S's allocation + writers + producer-side field + advance/copy
logic are this brief). This brief executes E5 §7's prescribed next action.
Reuse E5's watch-capture shape (`PS2X_DIAG_WATCH`, E4 taps at fork `a13b66a`,
pushed) — extend, do not rebuild.
Facts you start from: the located join: `S+0x5a88` 112→0 advance (J2a,
favored: the select is a loaded variable, not an immediate) or, if
`S+0x5a88` proves intentionally constant, re-fire of the boot blit (J2b,
not dead). The question: WHERE S lives, WHO writes `S+0x5a88`, and WHAT
advance/copy logic should join production (fbp0) to display. Phase 1 (no
boot): static source-trace from the steady call (`$s0` @ `0x38281c`, `$a0`
@ `0x382af0`) + boot caller `0x37c160` + `0x3827e0`: find S's allocation
site/address, the writer(s) of `S+0x5a88`, the producer-side FBP field, and
the advance/copy logic. If static evidence names the allocation + the join
(or its gate), NO boot runs. Phase 2 (ONE bounded capture, only if a
missing observation requires it): observation-only taps at EXISTING
interfaces (ONE new watch allowed: `PS2X_DIAG_WATCH` on `S+0x5a88`'s
runtime address once located, same zero-code capture shape, same named
boundary tick 600→601). Preserve the writer series + the joined chain. No
new global tracer, no regen, no backend swap, semantics UNCHANGED. Cap all
log streams by bytes AND wall time. Outcomes (tabled, not verdicts): (i) S
+ writers + advance/gate named → the ONE next action that finding
prescribes (fix brief ONLY if the join is a named emulator gap — a
guest-side gate is a finding, tabled with the parking evidence); (ii)
allocation/writers need a receipt this box cannot take → exact probe
recipe, stop; (iii) observation truncated/unalignable → repair that
measurement gap, nothing else. No SIF/CD promotion unless that dependency
names it; no raster/Present fix follows from this window (Present faithful,
two boundaries). Fork `$R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp`,
branch `ssx3`. Plain commits, pushed to the FORK remote only, never
upstream. Generated runner sources never staged. ONE P-lane mutator:
coordinate via the lease, never parallel boots. NO regen (still gated on
the 0x426230 DROP disposition — observation taps only).
Gates and rules: capture boot (Phase 2, if needed) ONLY while holding
`/tmp/ssx3-p-lane-lease` (SHARED P-lane) — poll every 5 min + log waits to
`$W/P1/run/e6-waits.log` if taken. Max 1 boot ≤600 s (Part 4 budget); wall
+ progress + BYTE caps recorded, abort past any cap. Builds `-j4` any time.
No `adb`. `export COPYFILE_DISABLE=1` on every SSD step. Retain: the capture
+ receipts that prove the finding (compress closed raws; single canonical
copies). Evidence dir `local/research/E6/` (STANDALONE). Commit with
`git add -f`, prefix `[E6]`, trailer `Orchestrated-By: Muse Code`. Do not
push ssx3 (orchestrator pushes at poll when the tree is clean). Fork commits
pushed to fork remote (table SHAs; none if Phase 1 suffices). Experiment
contract up front (hypothesis/observable/alternatives/stop + which outcome
each selects). Time box: 6 h. Hygiene: report in chunks + tail receipt
(truncated tail fails the gate).

## 1. Experiment contract

Hypothesis H-S1 (static closure): S is one heap object (vtable-dispatched
class); its factory, pointer-global, vtable, all `S+0x5a88` writers, and
the advance/gate logic are enumerable from the ELF, and they force the
stuck mechanism without a boot. H-S2 (values needed): static names sites
but the stuck-cause (gate-vs-mode-vs-equal-slots) needs live field values.
Observable (Phase 1): exhaustive whole-segment scans (imm16 offset refs,
JAL callers, stored function-words, lui-materializations) + disassembly of
every hit's function + ELF section/`.reginfo` reads. Alternatives: J2a-live
(parity ping-pong runs but never lands 0 — needs equal slots 112/112);
J2a-fixed (mode forces single-slot pick — needs `S+0x59e8`≠0 with no
clearer); J2a-gated (skip path every call — needs gate set at every call);
J2b (blit re-fire is the join — needs the display-consuming blit named).
Stop: allocation + writers + advance/gate named with receipts (§2), or the
ONE missing observation identified with its exact probe recipe (§4). Outcome
each selects: §4 table (exactly one of i–iii); (i) + emulator gap → fix
brief, (i) + guest gate → tabled finding + parking evidence, no fix brief.

Fork HEAD at inspect: `a13b66a` (E4 taps, pushed fork `ssx3`; only the
pre-existing generated `M ps2xRuntime/src/runner/register_functions.cpp`).
ssx3 HEAD at inspect: `d123665`. ELF
`P1/SLUS_207.72` = `P1/cd/SLUS_207.72`, md5 `9e64f3df7ed6e898061411ce43fe75eb`,
single PT_LOAD (vaddr `0x100000`, filesz 3820532).

## 2. Phase-1 trace (all static; receipts in-evidence)

### 2a. WHERE S lives — identity, allocation, pointer global

S = the `PS2GraphicsMan` heap object: 0x75e0 (30,176) bytes, one factory
call, pointer kept in a static `.sdata` global. Chain (every link
sliced; `e6-dis-slices.txt`, `e6-tables.txt`):

| # | Link | Address | Instruction / value | Receipt |
|---|---|---|---|---|
| A1 | factory | `0x375a08` | `jal 0x317d70` with `$a0=0x75e0` (delay), `$a1=0x492878`, `$a2=$a3=0`; then `jal 0x395288` (ctor-2, `$a0=$v0`) | slice `0x375A08+12` |
| A2 | arena/name | `0x492878` | bytes `PS2GraphicsMan\0…` (cstr) | `e6-tables.txt` data read |
| A3 | factory caller | `0x226970` | `jal 0x375a08` (sole JAL; fn entry `0x226900`, itself vtable/jalr-driven: 0 JAL) | `e6-scans.txt` JAL census |
| A4 | S-ptr global write | `0x22697c` | `sw $v0, -0x854($gp)` where `$v0`=factory ret, after `lw $v1,0x10d8($v0)` sanity | slice `0x226940+70` |
| A5 | S-ptr global re-reads | `0x226a04`/`0x226a20`/`0x27a944` | `lw $x, -0x854($gp)` then S-protocol use (vtable2 dispatch / gate store) | same slices |
| A6 | `$gp` value | `.reginfo+20` | `0x4a30f0` (loader reads it: `Loader.h:179-218,353-360`) → global = **`0x4a289c`** (in `.sdata` `0x4a0e80+0x3d74` ✓) | ELF section read + fork source |
| A7 | ctor-2 | `0x395288` | `jal 0x3691f8` (base-ctor, `$a0`=this) then `sw $v0=0x493260, 0x10d8($s0)`; returns this | slice `0x395288+20` |
| A8 | base-ctor | `0x3691f8` | installs transient `0x493950`@`+0x10d8`, inits `0xe88–0xf50` fields, **clears gate** (`0x369370`) | slice `0x3691F8+20`, §2e |
| A9 | ctor-1 | `0x385290` | `sw $v0=0x493208, 4($s0)` (vtable@+4), `jal 0x385260` sub-ctor (sole JAL caller) | slice `0x385290+25` |
| A10 | vtable | `0x493208…` | one continuous table, func words at base+8k+4 (86+ slots; `e6-tables.txt`) | data read `0x493208–0x493600` |
| A11 | key slots | `+0x6C/+0x7C/+0x244`, v2`+0x14` | `0x493274`=bring-up `0x375a40`, `0x493284`=init-caller `0x3764c0`, `0x49344c`=fp-user `0x37cc98`, `0x4935f4`=get-counter | `e6-tables.txt` + word scan |
| A12 | bring-up call | `0x226988` | `jalr` via vtable2 slot `+0x14` (`lh`-adjust 0 + `lw`-method), `$a0`=S — straight-line after factory | slice `0x226940+70` |
| A13 | S size fit | — | max S-field offset `0x5af8` < `0x75e0` ✓; `+0x10d8` vtable + `0x18f4`/`0x59xx–0x5axx` fields all in range | `e6-sfield-map.txt` |

Consequence: S's runtime address = the word at static `0x4a289c`
(one live word-read); `S+0x5a88`'s runtime addr = that word + `0x5a88`.
Whole-segment
imm16==`0xf7ac` (`-0x854`): 401 hits = 399 `lw`-loads (singleton read
~everywhere) + **2 writers**: install `0x22697c` (factory ret) and
teardown-null `0x2280ac` (`sw $zero`, delay-slot of a `beqz`, inside a
dtor→null→`0x3dedc0`-free cascade — unfired in the boot→steady window by
the liveness evidence: E5's 1,466 display bursts all source S).

### 2b. WHO writes S+0x5a88 — exhaustive writer table (CLOSED)

Whole-segment imm16==`0x5a88` scan: 10 hits (`e6-scans.txt`).

| # | Addr | Insn | Class | Disposition |
|---|---|---|---|---|
| W1 | `0x382b68` | `sw $v1, 0x5a88($t9)` (`$t9`:=`$a0`=S) | **THE store** | Sole S-writer; value = advance pick (§2c) |
| R1 | `0x382cd8` | `lwu $v0, 0x5a88($t9)` | DISPFB1 compose | E5-known ✓ |
| R2 | `0x382ebc` | `lwu $v0, 0x5a88($t9)` | second display-fn load (tail path) | in-`0x382af0` |
| R3 | `0x37cd54` | `lw $s3, 0x5a88($fp)` (`$fp`:=`$a0`=S) | fp-user packet build (TEX0/SBP source, `sll 5` + FBW<<14 + `0x4c/0x4e` packet) | slice `0x37CD40+70` |
| R4 | `0x39554c` | `lw $v0, 0x5a88($a0)` | get-display-FBP trampoline (`jr`+delay-load) | slice `0x3954CC+75` |
| X1–X2 | `0x21697c`/`0x216f50` | `addiu $a0,$a0,0x5a88` after `lui $a0,0x47` | string refs `0x475a88`=`kT_MSGBCWIN2Zoe`… | data read; NOT S |
| X3–X5 | `0x316a7c/a0/b04` | `jal 0x316a20` | low-16 coincidence | not mem refs |

Closure notes: no other `addiu`-lea materializes `0x5a88` (X1–X2 are the
only two; both `lui 0x47` strings), so no computed-pointer (`sw 0($ptr)`)
writer can target the field without a literal the scan would catch (residual:
multi-step constant synthesis — no evidence; tabled §8 G3). R5900 `sq`
(opcode `0x1F`) WAS in the scan's store set (none hit).

### 2c. WHAT advance logic — display-fn head `0x382b20–0x382b68` (DECODED)

(`e6-dis-slices.txt` slice `0x382B20+80`; `$t9`:=S.)

```
0x382b20 lw   $v0, 0x5a74($t9)     # counter C
0x382b24 lw   $v1, 0x0f44($t9)     # gate G
0x382b28 addiu $a0, $v0, 1         # C+1
0x382b2c beqz $v1, ADVANCE
0x382b30 sw   $a0, 0x5a74($t9)     # (delay, ALWAYS) C = C+1
0x382b34 b    MMIO-WAITS           # G≠0: SKIP pick (S+0x5a88 keeps value)
0x382b38 sw   $zero, 0x0f44($t9)   # (delay, ALWAYS) G = 0
ADVANCE:
0x382b3c lw   $v0, 0x59e8($t9)     # mode M
0x382b40 bnel $v0,$zero, PICK2     # M≠0 → fixed pick (likely; delay if taken)
0x382b44 lw   $v0, 0x5a78($t9)     # (delay) v0 = PAIR-A
0x382b48 andi $v0, $a0, 1          # (C+1) parity
0x382b4c bnel $v0,$zero, PICK2     # odd → PICK2
0x382b50 lw   $v0, 0x5a78($t9)     # (delay) v0 = PAIR-A
0x382b54 lw   $v0, 0x5a7c($t9)     # even: v0 = PAIR-B
0x382b58 b    JOIN
0x382b5c lw   $v1, 0x5a78($t9)     # (delay) v1 = PAIR-A
PICK2:
0x382b60 lw   $v1, 0x5a7c($t9)     # v1 = PAIR-B
JOIN:
0x382b64 sw   $v0, 0x5a84($t9)     # SHADOW = v0
0x382b68 sw   $v1, 0x5a88($t9)     # DISPLAY-FBP = v1   ← W1
```

Truth table (per display call):

| Gate G (`+0xf44`) | Mode M (`+0x59e8`) | Counter C+1 | S+0x5a84 (shadow) | S+0x5a88 (display) |
|---|---|---|---|---|
| ≠0 | any | C+1 (G→0) | unchanged | **unchanged** (skip) |
| 0 | ≠0 | C+1 | PAIR-A (`+0x5a78`) | **PAIR-B (`+0x5a7c`) — fixed** |
| 0 | 0 | C+1, odd | PAIR-A | PAIR-B |
| 0 | 0 | C+1, even | PAIR-B | **PAIR-A (the ONLY 112→other path)** |

So the J2a 112→0 advance exists ONLY as: G=0 ∧ M=0 ∧ even (C+1).
§2d forces M=1 (boot receipt) → the even-parity path is dead while M=1.

### 2d. Mode field S+0x59e8 — boot-forced 1, no static clearer

| # | Addr | Insn / value | Conditions | Receipt |
|---|---|---|---|---|
| M1 | `0x375fbc` | `sw $s1, 0x59e8($s2)`; `$s2`:=`$a0`=S (sole write @entry, all other uses reads); `$s1`=**1** (`addiu` @`0x375d38`; no `$s1` write in `0x375d38–0x375fbc`: all 13 `$s1` mentions audited; `$s1` callee-saved across the in-range `jal`s) | fall-through FORCED: every conditional branch in `0x375a40–0x375fbc` targets `<0x375d38` (8/8 local loops); no `jr` before the write (branch census, §7) | `e6-bringup-dis.txt` (full 380-insn fn) |
| M2 | `0x395568` | set-1 trampoline (`$v0`=1; delay-store) | **no static callers**: 0 JAL + 0 stored words + 0 lui-`0x39` materializations (whole-segment) | `e6-scans.txt` + §7 scans |
| M3 | `0x395578` | set-0 trampoline (ONLY clearer) | same triple-zero unreachability as M2 | same |
| X6 | `0x294890` | `sw $a2, 0x59e8($v0)`, `$v0`=`$a0`+(`$a1`<<2), `$a1`<6 | DIFFERENT struct: array-indexed ×6 (S is a singleton; S-flows never index); sibling getter `0x29487c` + lea `0x2947c4` same shape | `e6-dis-slices2.txt` slice `0x294860+45` |
| X7–X8 | `0x21661c`/`0x216bec` | `lui 0x47`+`addiu 0x59e8` | string refs (`0x4759e8`), same pattern as X1–X2 | `e6-dis-slices2.txt` slice `0x2165F4+36` |

Order inference (tabled, not receipted): factory (`0x226970`) → bring-up
call (`0x226988`, straight-line) → display-init (`0x37bd98`, must precede
burst 1 whose S-values are already valid) → burst 1 (tick ~38–40, thread
1). Corroboration: burst 2 already re-selects 112 (E5 ln 501) — under M=0
+ clear gate, call 2 (C+1=2, even) would have picked PAIR-A; it picked
PAIR-B ⇒ M≠0 ∨ G≠0 at burst 2.

### 2e. Gate field S+0xf44 — writers + conditions (CLOSED)

Whole-segment imm16==`0x0f44`: 22 hits; S-real vs other-struct:

| # | Addr | Insn | Value/cond | Fn / role | Receipt |
|---|---|---|---|---|---|
| G1 | `0x369370` | `sw $zero, 0xf44($s2)` (`$s2`:=this) | 0, boot | base-ctor `0x3691f8` (called by ctor-2) |
| G2 | `0x37d050` | `sw $a0=1, 0xf44($fp)` (`$fp`:=S) | **1, UNCONDITIONAL**: single-exit fn (sole `jr` @`0x37d088` in `0x37cc98–0x37d08c`); also `S+0x5a00+=0x10`, `S+0xe84-=0x14` | fp-user `0x37cc98` exit slice |
| G3 | `0x382b38` | `sw $zero, 0xf44($t9)` | 0, every display call (delay slot) | §2c |
| G4 | `0x3946e0` | set-1 trampoline (`$v0`=1; `$a0`=S by `0xe84`/`0x10d8`-neighbor protocol) | callers: 0 JAL + 0 stored words (unreached, like M2/M3) | slice `0x3946C8+20` |
| G5 | `0x27a950` | `sw $a1=1, 0xf44($v1)`, `$v1`=[`0x4a289c`]=S | 1, straight-line in `0x27a860`-fn (boot/UI flow) | slice `0x27A944+10` |
| R5 | `0x382b24` | `lw $v1, 0xf44($t9)` | the §2c gate read | §2c |
| X9–X20 | `0x100xxx` ×12 | `sdr *, 0xf44($s0/$s1)` + `lh` ×2 | OTHER struct: crt0/memcpy-shaped unaligned stores, `0x100000–0x1012d4` | scan rows (shape-ruled) |
| X21 | `0x14405c` | `sdr` (table-copy accessor, small-struct neighbors) | OTHER struct | slice `e6-dis-slices2.txt` |
| X22 | `0x2f9e70` | `swc1` (float-block bulk init `0xed8–0xf64`) | OTHER struct | slice `e6-dis-slices2.txt` |

Dynamics note (tabled): under M=1 the gate only DELAYS first convergence
(skip keeps old value; first clear-gate call fixed-picks PAIR-B) — stuck-112
holds whether G is always set or always clear. G-rate (fp-user rate vs
display rate) matters only if M ever clears.

### 2f. Pair slots + producer-side fields

| Field | Writer(s) | Value source | Readers | Receipt |
|---|---|---|---|---|
| PAIR-A `+0x5a78` | init `0x37c004` ONLY (`sw $v0`=alloc-ret; delay slot) | VRAM-alloc `0x3673d8` ret, size `S+0x5a6c<<13` | init `0x37c054`, advance ×3 (§2c) | imm scan (5 hits +1 R-type coincidence); NO lea |
| PAIR-B `+0x5a7c` | init `0x37c018` ONLY | VRAM-alloc ret, size `S+0x5a68<<13` | init `0x37c090`, advance ×2 | imm scan (4+1 jal coincidence); NO lea |
| THIRD `+0x5a80` | init `0x37c03c` ONLY (delay) | VRAM-alloc ret, size `S+0x5a70<<13` | 22 incl. render `0x36ad48`→`$a2` of `0x36ae20`, fp-user `0x37cd78`, display-tail | `e6-sfield-map.txt` group |
| SHADOW `+0x5a84` | advance `0x382b64` ONLY | PAIR-A (M=1 path) | 16: render ×6 (`0x36ad5c…0x390b0c`), display-tail, fp-user-sibs, get-trampoline `0x395518` | imm scan (17 +1 jal coincidence); NO lea |
| COUNTER `+0x5a74` | init `0x37be38` (=0), advance `0x382b30` (++) | — | advance `0x382b20`, get-trampoline `0x395510` (**vtable slot** `0x4935f4` — the only counter accessor exposed) | imm scan (4 hits, closed) |
| DISP-FBP `+0x5a88` | §2b W1 only | PAIR-B (M=1 path) | §2b R1–R4 | §2b |

Producer flow (receipted): render method `0x36ae20`(`$a0`=S→`$s4`,
`$a1`, `$a2`=S+0x5a80→`$s5`, `$a3`=S+0x5a84→`$s6`) — called @`0x36ad74`
with exactly those S-loads (`0x36ad48`/`0x36ad5c`); body = vtable
dispatches + GIF-packet `sd` builds (tag `0xe` + composed words).
Prediction (tabled H-pair, §3): `S+0x5a78`=`S+0x5a84`=fbp0-block (first
VRAM alloc) — consistent with E4's 122/122 fbp0 draws; value receipt is E7's.
FBW/PSM/display-shape fields (`+0x5a38/44/46/4c/54/58/5c`): single init
stores each (`0x37be04–0x37bed4`, `$s1`-base) + display-fn loads — all in
`e6-sfield-map.txt`; values 1/8 observed via MMIO (E5).

Init detail (`0x37bd98`, `$s1`:=`$a0`=S; called once via JAL @`0x376538`
from init-caller `0x3764c0`, itself vtable slot `+0x7C`): dims→FBW/size
derivation (`srl 5/6` PSM switch), three `0x3673d8` VRAM allocs
(FBP-returning: `(entry\|0x22)>>13`), `0x367340` setup calls, CSR event
gate, then the BOOT display call `0x37c158: jal 0x382af0` (`$a0`=`$s1`=S,
`$a1`=0 ⇒ PMODE `0xff20` ✓ E5 burst 1, `$a2`=1 ⇒ wait path).

### 2g. Display-fn callers + steady driver + state machine

| # | Site | Shape | Args | Receipt |
|---|---|---|---|---|
| C1 | `0x37c158` (boot; ra `0x37c160` ✓ E5) | JAL from init `0x37bd98` | `$a0`=S, `$a1`=0, `$a2`=1 | §2f |
| C2 | `0x38281c` (steady; ra `0x382824` ✓ E5) | JAL from steady `0x382760` (`$s0`:=`$a0`=S @entry) | `$a0`=`$s0`=S, `$a1`=1, `$a2`=0; pre: `S+0x5a98`-indexed array clear + `S+0x5a8c`=0 | slice `0x382760+55` |
| C3 | `0x3960f0` (wrap; ra `0x3960f8`) | JAL from wrapper `0x3960e8` (pass-through `$a0`/`$a1`, `$a2`=1) | caller of wrapper: 0 JAL + 0 stored words (jalr-driven) | slice `0x3960E8+15` |
| D1 | steady `0x382760` | JAL'd once by wrap `0x382740` (0 JAL callers itself) | S in `$a0` | `e6-scans.txt` |
| D2 | fp-user `0x37cc98` (`$fp`:=S) | 0 JAL; vtable slot `+0x244` | jalr-driven; rate = dynamics (§4) | word scan + slice |

`S+0x5a8c` state machine (gates the steady display call: fires iff ==5):

| Transition | Site | Base | Receipt |
|---|---|---|---|
| 4→5 (when `++S+0x5abc` ≥ `S+0x5ab8`=1; clears counter) | `0x382634` | `$a1` (S-protocol; method entry unsliced, above `0x382600`) | slice `0x382600+50` |
| 5→0 (fires display C2) | `0x382818` | `$s0`=S | §2g C2 |
| 0→1 (after MMIO/CSR waits + `S+0x5a98`=`S+0x5aa4` copy) | `0x382920` | `$s0`=S | `e6-dis-slices2.txt` slice `0x382900+140` |
| 1→2 | `0x3826a8` | `$a1`:=`$a0`=S (entry `0x382688`) | slice `0x382600+50` |
| 3→4 | `0x3826d0` | `$a1`=S (same method) | slice `0x3826B0+45` |
| 2→3 | `0x382acc` (=3: `addiu $v0,3` @`0x382ac8`, after CSR wait) | `$s0`=S | `e6-dis-slices2.txt` slice `0x382900+140` |
| boot | `0x375d2c` (=0), `0x375d4c` (`S+0x5aa4`=1), `0x375d54` (`S+0x5ab8`=1) | `$s2`=S (bring-up) | `e6-bringup-dis.txt` |

Liveness join: E5's 1,466 bursts (~59/s) ⟹ the machine completes
5→…→5 every frame — the driver chain works; only the DISPLAY-side pick
is stuck (mode-fixed, §2c–2d). Steady tail loops (`0x382ae8: b 0x3827d8`,
in-slice) — self-driving loop. The 0x382600/0x382688 methods' own callers
are jalr-driven (dynamics, §8 G4).

_fp-user role (J2b carrier, tabled):_ `0x37cc98` reads the DISPLAYED FBP
(R3) into a GIF packet (FBP<<5 \| FBW<<14 \| PSM-ish, `FRAME_1`/`TEX0_1`
tags `0x4c`/`0x4e`, `0x38f460` packet calls) — the display-consuming
blit/texture path exists and its exit sets G=1 (G2). Its per-frame rate
vs the display rate + the boot-blit (`tbp0=0→fbp112`, E5 P4) non-refire
are dynamics (§4 recipe observes the gate sequence, not fp-user's PC).

## 3. Hypothesis update

H-S1 HOLDS for mechanism; H-S2 holds for five values. Forced static chain:

1. M=`S+0x59e8`=1 from bring-up (M1 fall-through proof) with no static
   clearer (M3 triple-zero unreachability) → EVERY clear-gate display call
   takes PICK2: `S+0x5a88`:=`S+0x5a7c`, `S+0x5a84`:=`S+0x5a78` (§2c truth
   table). The parity-alternation path (the only 112→other route) is dead
   while M=1.
2. Observed `DISPFB1`=`0x9070` = FBP 112 on all 1,466 bursts (E5) ⇒
   `S+0x5a7c`=112 (fixed-pick + observed value; boot-fixed allocator ret).
3. Gate G only delays first convergence under M=1 (§2e dynamics note):
   stuck-112 holds whether fp-user runs every frame (G always set) or never
   (G always clear). J2a-gated is demoted to a second-order effect; J2a-live
   needs equal 112/112 slots (untestable statically); J2a-fixed (M=1) is
   the favored stuck mechanism; J2b stays open as the ALTERNATE join (the
   boot blit fired once; its re-fire condition is not in this window).

H-pair (prediction, tabled): `S+0x5a78`=`S+0x5a84`=fbp0-block — first of
three consecutive VRAM allocs (empty-heap inference, UNRECEIPTED) feeds
the producer's fixed fbp0 draws (E4 122/122). H0 (present-drops): stays
falsified (E4/E5). H2 (HLE flip): stays falsified (E5 W3/W4).

## 4. Decision table (Phase 2: is any observation missing?)

| Question | Needs | Have | Selectable? |
|---|---|---|---|
| WHERE S lives | factory + size + pointer path | heap `0x75e0` B, factory `0x375a08`←`0x226970`, global `0x4a289c`, vtable `0x493208` (§2a) | YES — named |
| WHO writes `S+0x5a88` | exhaustive writer scan | exactly W1 (§2b, closed) | YES — named |
| WHAT advance/gate joins production to display | advance decode + mode/gate writers | §2c truth table + §§2d–2e (closed) + producer fields §2f | YES — named |
| WHY stuck at 112 (mechanism) | M/G/slot forcing | M=1 boot-forced ⇒ fixed pick of slot=112; G immaterial under M=1 (§3) | YES — forced |
| S numeric addr + 5 field values (`0x5a78/7c/84`, G-sequence, M-confirm) + fp-user rate | live reads | MISSING (heap; values never on MMIO except the pick) | NO — dynamics |

DECISION: allocation + join + gate all named statically ⇒ **NO boot runs**
(brief §Phase-1 rule). E6's single boot could at most learn S's address
(one word) — it cannot take the S-relative value series (watch addrs need
S upfront, fixed at boot), so it cannot close the values question; burning
it buys nothing the finding needs. The values question goes to E7 with the
exact recipe below (two 1-boot briefs: locate-S, then value-series).

E7 probe recipe (exact; zero-code, existing interfaces only):
- E7a (1 boot ≤600 s, same caps/shape as E5): `PS2X_DIAG_WATCH=0x4a289c`
  (+ E5 display set for the join) → the factory store's `value=` field IS
  S's runtime address (heap determinism ⇒ stable across boots; verify by
  the teardown-null absence + display series re-match).
- E7b (1 boot, addrs computed as S+off): `PS2X_DIAG_WATCH=S+0x5a78,
  S+0x5a7c,S+0x5a84,S+0x5a88,S+0x5a74,S+0x0f44,S+0x59e8` at 600→601 (+ boot
  window free, as in E5) → slot values (H-pair test), G-sequence at display
  calls (fp-user-rate inference: skip-vs-pick per burst), M-confirm (=1?),
  counter rate. Miner: join vs `e5-watch-series.txt` by burst count.
- Reachability residual for E7 (only if values surprise): pointer-chase
  dispatch to M3/G4 (all DIRECT refs ruled out §2d/§2e; scan recipe:
  `jalr` sites whose target reg traces to a `0x3955xx`/`0x3946xx` load —
  state as open, §8 G5).

## 5. Capture record

No Phase-2 capture (decision §4). Boots used: 0/1. Lease never claimed
(no `$W/P1/run/e6-waits.log` — nothing to poll; verified absent at close,
§7). No E4/E5 tap modifications, no fork diff (zero source changes).

## 6. Finding table (exactly one of i–iii) + prescribed next action

| Outcome | Test | Result |
|---|---|---|
| (i) S + writers + advance/gate named → ONE next action | §§2a–2g tables complete + stuck mechanism forced (§3) | **MET — full static naming; stuck = M1-fixed pick of PAIR-B=112 (J2a-fixed favored; J2a-gated demoted; J2b open as alternate join)** |
| (ii) needs an off-box receipt | — | NO — all remaining values takable on-box (E7a+E7b recipe, §4) |
| (iii) truncated/unalignable | — | NO — no observation taken, none truncated |

CLASSIFICATION: **(i) via J2a-fixed** (new refinement of E5's J2).
NEXT ACTION (prescribed; NOT a fix brief — no emulator gap is named: the
display re-assert, MMIO path, gate/mode logic, and Present all execute
faithfully; the stuck select is guest state): run the §4 E7a+E7b value
series to confirm slot values (H-pair), the G-sequence, and M=1 — then the
parking question is answerable (what SHOULD clear M / re-fire the blit).
No SIF/CD promotion (nothing names that dependency); no raster/Present fix
follows (faithful, two boundaries). Guest-gate parking evidence: G2 (fp-user
sets G unconditionally) + G5 (boot/UI sets G) + G4/M3 unreached — tabled
above, not verdicts.

## 7. Exact commands (abridged; scratch in /tmp, canonicals in-evidence)

Setup: `mkdir local/research/E6`; ELF md5 both copies
`9e64f3df…`; fork HEAD `a13b66a` + status (pre-existing generated `M`
only) re-verified at commit; ssx3 HEAD `d123665`.
Scans (all whole-LOAD-segment, `/tmp/e6-scan.py`): `--imm`
{`0x5a88`,`0x5a78`,`0x5a7c`,`0x5a84`,`0x5a74`,`0x0f44`,`0x59e8`,`0xf7ac`}
→ `e6-scans.txt` (+ `e6-sfield-map.txt` for `--range 0x5a00,0x5aff`);
`--jal` ×16 targets → `e6-scans.txt`; stored-word scan (11 + 13 targets);
J-opcode scan (6 targets, 0 hits); lui-materialization scans
(`0x48/0x49/0x4a`→vtable range: 2 hits; `0x39`→accessor range: 0 hits).
Slices (`/tmp/e6-dis.py --at`; prologue-backtrack + jr-census helpers
inline): 24 canonical (`e6-dis-slices.txt`, 1036 lines) + 5 tail/
attribution (`e6-dis-slices2.txt`, 282 lines) + full bring-up fn
(`e6-bringup-dis.txt`, 380 insn) + `$s1` audit (13 mentions) + branch
census (8/8 local) + fp-user jr census (1 exit). Data reads: vtable
`0x493208–0x493600` nonzero dump, arena cstr `0x492878`, `.reginfo+20`
gp, ELF sh 43/44 (`e6-tables.txt`, 128 lines). Counts: `S+0x5a88` 10 scan
hits; `0xf7ac` 401 (399 loads + 2 stores); vtable 86+ slots. Lease absent
+ `pgrep` exit 1 verified at close. No boot, no lease claim, no fork commit.
Evidence commit `[E6]` (this report + 6 receipt files), unpushed.

## 8. Gaps / errata

G1 (values open → E7): S numeric addr + `0x5a78/0x5a7c/0x5a84`/G-sequence/
M-confirm/fp-user rate are dynamics; exact recipe §4 (E7a+E7b). Nothing in
E6's window substitutes (heap values never on MMIO except the pick).
G2 (order inference): factory→bring-up→init→burst-1 ordering is logical
necessity (S-values valid at burst 1) + straight-line adjacency
(`0x226970`→`0x226988`), not a traced thread schedule; burst-2
corroboration tabled §2d. Thread of factory/bring-up unreceipted (bursts:
thread 1 boot / thread 5 steady, E5).
G3 (writer-closure residuals): multi-step constant synthesis for field
offsets (no evidence; imm/lea/R5900-`sq` all scanned); `0x382600`-method
entry unsliced (above slice start; `$a1`-base S-protocol receipted
in-slice).
G4 (jalr dynamics): post-factory callers of init-caller/steady/fp-user/
wrapper/mode-trampolines are vtable/jalr-driven; rates and secondary
dispatch sites need dynamics (E7b G-sequence infers fp-user rate free).
G5 (computed-dispatch residual): M3/G4/unreached-accessor reachability via
pointer-chase/index-arithmetic `jalr` is NOT ruled out (all DIRECT refs
— JAL, stored words, lui-bases — are); E7 follow-up scan recipe §4.
G6 (E5 G6, CLOSED for mechanism): S allocation + writers + producer fields
+ advance/copy logic all named statically; REMAINS for values (§4 recipe).
Box: ~4.3 h wall (23:45→04:05Z), inside 6 h. Lease never held.

---
Tail receipt: REPORT.md §§0–8 complete; e6-dis-slices.txt (1036 ln) +
e6-dis-slices2.txt (282 ln) + e6-scans.txt (153 ln) + e6-sfield-map.txt
(502 ln) + e6-bringup-dis.txt (382 ln) + e6-tables.txt (128 ln) +
REPORT.md in-evidence (7 files incl. REPORT). Fork: NO commit (zero diff).
Evidence `[E6]` committed, unpushed (orchestrator pushes). Lease verified
absent at close. Outcome: (i) via J2a-fixed — M=1 boot-forced fixed pick
of PAIR-B=112; next: E7a+E7b value series (§4 recipe).


