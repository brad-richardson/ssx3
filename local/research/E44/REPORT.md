# E44 report — who writes scratchpad item 0x70000000 (recomp side)

Brief `local/muse/prompts/E44.md` (+ orchestrator Part-2, 2026-09-23:
VIF0 unknown-opcode census, VU0 call trace, Boot-B EE-source watch on
`0x809670` w0/w3 with SPR_FROM tapped and an SPR MOD!=0 counter).
Tables + receipts; the orchestrator decides. Read first: `AGENTS.md`,
`local/AGENTS.local.md`, `local/research/E43/REPORT.md`,
`local/research/T55/REPORT.md`.

## Outcome (Boot A)

- **Both watched items are multi-producer staging slots, refilled every
  vsync.** Item `0x70000000` w0 is written in-window only by `store64`
  pointer-builds in `sub_00376938` (`0x100000xx` values) and by SPR_TO
  DMA copies of EE quads (`w0=0x0c/0xcc`, src `0x0080b270`/`0x0080ea70`).
  Item `0x70000500` w0 cycles per vsync through `store64` floats
  (`sub_00376938`), two SPR_TO copies (`0x0c`/`0xcc`), then a
  `store32` zero (`sub_00364050@0x364178`) — and from vsync 1273 a
  `store128` vertex-data phase (`sub_00386128@0x386cc0`, ra
  `sub_00310640`) plus a third DMA copy.
- **The candidate writer `sub_003629B8` never fires in-window: zero
  `pc=0x362xxxx` lines, zero `w0=0x30` values in 510 rows.** E43's
  hash-time `w0=0x30` (window 1355–1400) is therefore staged after
  vsync 1280, or after the per-word-64 cap closed (low words capped
  inside vsync 1270). The final-writer identity for the `0x30` class is
  NOT established by Boot A.
- **No fast-path, mem-write, 8/16-bit, or host-copy lines**: all
  in-window watched-word writes are guest `Store32/64/128` or SPR_TO
  DMA. The fast path never touches a watched word (as constructed);
  no host-side `PS2Memory::write*` bypassed `Store*`.
- Direct-backing audit (code search, no tap): ELF segment loads
  (`ps2_runtime.cpp:1001`, `Loader.h:299`, boot-time only) and the GS
  gparam cookie (`Support.h:1952`, scratch offset `0x100`, outside the
  watch). Neither can hit watched words in-window.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3` (base `a932aff`, E43 tip):

| Commit | Subject |
|---|---|
| `571579e` | [E44] Part-2 scratchpad/VIF0/VU0/SPR watch taps + Boot-C readout |

Runner-dir gate (`git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner`) verified empty before push (see §Receipts).

## Diff summary

- `ps2xRuntime/include/ps2_e44_trace.h` (new): dev-only watch behind
  `PS2X_E44_TRACE=<file>` (+`PS2X_E44_FROM`/`_TO`, default 1270/1280;
  `PS2X_E44_EXTRA` up to 8 extra EE words for Boot B). `spw` lines
  carry `vsync addr value via src pc ra fn` + full `a0..a3 v0 v1
  t0..t9 s0..s7` (value = word read-back post-store). First 64 per
  watched word, then quiet for that word. `via ∈ {store8/16/32/64/128,
  fast, mem-write, spr-dma, spr-from, ...}` (Part-2 kinds below).
- `ps2xRuntime/src/lib/ps2_runtime.cpp`: `Store8/16/32/64/128` arm the
  watch, hold the mem-suppress guard across `m_memory.write`, and log
  post-store with full regs (`__func__` as fn). Single choke point:
  static-resolved special stores emit `runtime->Store*` directly and
  dynamic stores route through the WRITE macros into `Store*`, so all
  guest CPU stores (incl. all SDL/SDR/SWL/SWR merges) are covered.
- `ps2xRuntime/include/ps2_runtime_macros.h`: `Ps2FastWrite*` log
  `via=fast` on watched words (expected zero; any line is a codegen
  bug) + the `ps2_e44_trace.h` include.
- `ps2xRuntime/src/lib/ps2_memory.cpp`: `PS2Memory::write*`
  scratchpad branches log `via=mem-write` unless a `Store*` tap holds
  the guard (no double lines); SPR_TO memcpy logs `via=spr-dma` with
  per-word EE `src` (wrap-aware, last-hit source on multi-wrap).
- Part-2 (one boot): VIF0 unknown-opcode census + kick counts,
  `executeVU0Microprogram` call trace (first 2000), SPR_FROM memcpy
  tap + SPR MOD!=0 kick counter (details in §Part-2).
- `ps2xTest/src/ps2_e44_trace_tests.cpp` (new, `Ps2E44Trace`, 10+
  tests), registered in `src/main.cpp` + `CMakeLists.txt`:
  off-by-default; store32 regs/pc/ra/fn; sub-word containing-word
  read-back; unwatched silence; 64/word cap; window gating; spr-dma
  per-word src (4+4 overlap); extra EE word (Boot-B shape);
  mem-write guard suppression; fast-path via.

## Tests (suite 570/570 = 551 E43 + 19 new, flags-unset, fork root)

```
cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ 571579e
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT \
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 570/570
```

Suite history: 561/561 (Boot-A tree, 10 E44 tests) → 567/567
(+6 Part-2 tests) → 570/570 (+3 Boot-C readout tests), flags-unset,
fork root. Pre-existing `System.cpp` format warning untouched.
A use-before-definition of `trackLastWriter` (Boot-C block placed
after its callers) was caught by a standalone header probe before
the build and fixed (moved above `noteStore`).

Build notes: a `-Wformat-truncation` on the first DMA line buffer
(256 B vs ~450 B lines) was caught before booting and fixed (1024 B);
zero warnings after. One mid-build overlap off-by-one (extra word
past 16-byte stores) was caught by self-review and fixed before any
boot (covered by the sub-word test).

## Boots (Mac mini, E32-build, E33 vsync route, `PS2X_SKIP_MOVIE=1`, lease-claimed/released)

Route string (E33 §Vsync-clock script):
`10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000`

| Boot | Rev / runner SHA ×2 | Wall/snap | Window | Result |
|---|---|---|---|---|
| e44a (A) | uncommitted spw-only tree, runner `2ddd59ec…87bba` ×2 | 300/30, 302.5 s wall-bound | 1270–1280 (+no EXTRA) | rc 0, reach ~1378; 510 spw +1 torn; low words capped in vsync 1270 |
| e44b (B) | +Part-2 taps tree, runner `1580db6a…8bab` ×2 | 300/30, 301.6 s wall-bound | 1270–1280 (+EXTRA `0x809670,0x80967c`) | rc 0, reach ~1378; 510 spw +1 torn, 0 Part-2 lines, 0 EXTRA lines |
| e44c (C) | +Boot-C readout tree, runner `dec5464a…0520b` ×2 | 360/30, 361.3 s wall-bound | 1355–1400 (+same EXTRA) | rc 0, reach 1430; 512 spw + 39 spwlast (2/vsync 1355–1373, 1 at 1374); 0x30 stager found |

Infra: two launch attempts crashed in raylib `InitWindow`
(`rlLoadTexture`, pc=0) — the JetKVM display was asleep
(`system_profiler`: `Display Asleep: Yes`); E43's log shows display
init succeeding. Woke it with `caffeinate -u -t 10` (asleep line
gone), third launch booted clean. No code change involved.

Traces in-repo: `e44-e44a.txt` (225,280 B; SHA in §Receipts).

### Table 1 — writers per watched word (Boot A, 510 rows, vsyncs 1270–1277)

| addr | n (vsyncs) | via | value classes | pc (fn → func) |
|---|---|---|---|---|
| `0x70000000` (w0) | 64 (1270, capped) | store64, spr-dma | `0x100000xx` (ptr-build); `0x0c`, `0xcc` (DMA) | `0x3796b4/0x379a48` (`Store64` → `sub_00376938`); DMA src `0x0080b270`→`0x0c`, `0x0080ea70`→`0xcc` |
| `0x70000004` (w1) | 64 (1270, capped) | store64, spr-dma | `0x0`, `0x01414294` (DMA) | same pcs; DMA src `+4` of the same transfers |
| `0x70000008` (w2) | 64 (1270, capped) | store64, spr-dma | `0x0`, `0x2a0` (DMA) | `0x3796dc/0x3799f0` (→`sub_00376938`); DMA src `+8` |
| `0x7000000c` (w3) | 64 (1270, capped) | store64, spr-dma | `0x0` | same pcs; DMA src `+12` |
| `0x70000500` (w0) | 64 (1270–1277) | store64, spr-dma, store32, store128 | floats; `0x0c`/`0xcc` (DMA); `0x0` (zeroing) | `0x3792f8` (→`sub_00376938`); `0x3e64c8` (→`sub_003E6448`); `0x364178` (→`sub_00364050`); `0x386cc0` (→`sub_00386128`, ra `sub_00310640`) |
| `0x70000504/08/0c` | 63–64 (1270–1277) | same 4 | floats/`0x01414294`/vertex words | same pcs (+`0x379330`, +`0x3e64d0`) |

Zero lines with `via=fast|mem-write|store8|store16`; zero
`pc=0x362xxxx`; zero `value=0x30`.

### Table 2 — per-vsync producer order, `0x70000500` (stable 1270–1272; 1273+ adds a phase)

| step | via/pc | value | meaning |
|---|---|---|---|
| 1–3 | store64 `0x3792f8` | floats (`0x3e2c0000`, `0x3ead0000` ×2) | `sub_00376938` staging |
| 4–5 | spr-dma | `0x0c` ← `0x0080b770`, then `0xcc` ← `0x0080ef70` | two EE-quad copies overwrite the slot |
| 6 | store64 `0x3e64c8` | `0x0` | `sub_003E6448` clears |
| 7 (last) | store32 `0x364178` | `0x0` | `sub_00364050` clears w0 — last observed writer each vsync 1270–1272 |

From vsync 1273: a `store128 0x386cc0` vertex phase (values
`0xbfa4…`, ra `sub_00310640`) runs first, then the float/store
sequence, then **three** DMA copies (`0x0c` ← `0x00809b70`,
`0xcc` ← `0x0080d370`, `0xcc` ← `0x00810b70`).

### Table 3 — word-0 cap tail (vsync 1270, file order = time order)

`store64` storm (`0x3796b4`/`0x379a48`, values `0x100000xx`) …
then `spr-dma 0x0c ← 0x0080b270`, then `spr-dma 0xcc ←
0x0080ea70` as the last two logged lines. Writes after the 64th are
unlogged (cap), so the true last-writer-before-walk is unknown.

### Table 4 — value/mode formation (codegen read, `sub_003629B8`)

The candidate copies a 20 B record with `ldl/ldr/sdl/sdr` pairs +
`sw` from `*(a2+0xE84)` to the item pointer, then stamps w0 through
a mask/OR chain: `(w0&t1)|0x100`, `(w0&s2)|0x14`,
**`(w0&t1)|0x180`** ← sets mode bits 7–8, `(w0&s3)|0x1`,
`(w0&t3)|s4`, `(w0&t4)|s5`, `(w0&t5)|t6`. Mode 6 needs the `0x180`
OR to survive the later masks with bits 6/9 clear. The spw format
logs every chain input (`t1 s2 s3 s4 s5 t3 t4 t5 t6`) at each
scratchpad store — but no `0x3629B8` store fired in-window, so the
chain inputs are unobserved.

**Correction (Part 3, codegen-verified, orchestrator-gated):**
`sub_003629B8 @0x362be4`'s `ori 0x180` feeds `sw` to word **+4** of
the struct at `*(…)->0xE84` — one of three and/ori pairs on the same
word (`s2/0x14`, `t1/0x180`, `s3/0x1`), i.e. flag surgery, not the
item's w0. Sole cross-function call site is `sub_00375A08 @0x375e78`
(`jal func_3629B8`; the only other reference is fall-through from
`sub_00362978`), consistent with once-at-renderer-init. **Dropped as
the w0 candidate.**

## Gaps / notes (Boot A)

- Low-word caps (64) closed inside vsync 1270: the true
  last-writer-before-walk per vsync is unobserved for item 0.
- `w0=0x30` (E43 hash-time value, window 1355–1400) never appears in
  1270–1280; `sub_003629B8` never fires there. The `0x30` stager runs
  later (menu-state evolution: the 0x500 slot visibly changes class
  at vsync 1273).
- EE-source buffers' own writers unobserved in 1270–1280 (Boot B)
  and 1355–1400 (Boot C) despite a proven-live EXTRA watch + SPR_FROM
  tap: staged pre-1270. (An earlier-window EXTRA watch is the direct
  next step; not done — 3-boot budget spent: A + B + C.)
- VIF0-kick trailing-tick gap: kick lines flush on tick advance, so a
  hypothetical kicks-only-in-the-final-tick would be missed. Zero
  kicks over ~68 covered vsyncs make this negligible.
- Spend: builds as needed, suites ×6 (559→561→567→570), 3 counted
  boots (+2 display-asleep crashes, no guest execution). E44-run
  22 MB of 2 GB (frames dominate).
- Exact commands:
  `cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ 571579e`
  `env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 570/570`
  `python3 local/research/E44/e44_boot.py --label e44a --wall 300
  --snap 30 --script "<route>"`
  `python3 local/research/E44/e44_analyze.py
  ~/dev/ssx3-work/E44-run/e44-e44a.txt`

## Recommendation (orchestrator decides)

Boots A–C close the item-0 writer question: the `0x30` quad is DMA'd
from EE `0x00809670` every vsync (pass 1 consumes it, pass 2 the
`0xcc ← 0x0080ce70` overwrite); `sub_003629B8` never stores to item 0
in any window. Open: who writes EE `0x00809670` (pre-1270 staging;
an earlier-window EXTRA watch is the direct next step), and where
the healthy `0x1b0` (+`w3` ping-pong) is produced on the PCSX2 side
(T-lane join). VIF0/VCALLMS/MOD-SPR are clean negatives in-window.

## Part-2 (ONE boot: VIF0 census + VU0 calls + EE-source/SPR_FROM/MOD)

Boot B (e44b, same route/window as A + `EXTRA=0x809670,0x80967c`):
**all Part-2 line kinds are zero and no EXTRA word is ever written.**
The taps were verified live (Part-2 strings in the Boot-B runner;
EXTRA env-parse proven by a standalone probe: `armed9670=1`,
`armedOther=0`). Findings in-window 1270–1280:

- 0 VIF0 kicks, 0 unknown opcodes — VIF0 DMA never fires (game uses VIF1).
- 0 `executeVU0Microprogram` calls — no VCALLMS-path VU0 run.
- 0 MOD!=0 SPR kicks — all SPR transfers are normal mode.
- 0 writes to EE `0x809670`/`0x80967c` — the buffer is staged pre-1270
  and re-DMA'd without rewrite (see Boot C).

spw in Boot B is statistically identical to Boot A (same 8×64-ish
distribution, same via mix 378/80/40/12, same pcs) — determinism check
passed. Still zero `w0=0x30` and zero `pc=0x362xxxx` in 1270–1280.

## Boot C (addendum: last-writer readout, 1355–1400) — the 0x30 stager

Per-word last-writer records (ungated: every watched store updates,
no window, no cap) for `0x70000000..0x7000000c`, emitted as one
`spwlast vsync item w0..w3 <via,pc,ra,fn,value,src,wtick per word>`
at each `sub_00362DE8@0x362f68 → func_394ED0` dispatch with
`s1=0x70000000` (first 40 lines). 39 lines over vsyncs 1355–1374
(2/vsync = the two passes; the 40th died to the wall-kill
mid-flush).

### Table 5 — item-0 last-writer at every walk (stable all 20 vsyncs)

| walk | w0 | w1 | w2 | w3 |
|---|---|---|---|---|
| pass 1 | `spr-dma … 0x00000030 ← 0x00809670` | `… 0x00814884 ← 0x00809674` | `… 0x000002a0 ← 0x00809678` | `… 0x00000000 ← 0x0080967c` |
| pass 2 | `spr-dma … 0x000000cc ← 0x0080ce70` | `… 0x01414294 ← 0x0080ce74` | `… 0x00000240 ← 0x0080ce78` | `… 0x00000000 ← 0x0080ce7c` |

(Full fields per record: `via=spr-dma,pc=0,ra=0,fn=spr-to` + the
value/src above, `wtick` = same vsync.)

**The `0x30` stager is an SPR_TO DMA copy of the EE quad at
`0x00809670` (`w0=0x30, w1=0x814884, w2=0x2a0, w3=0`) — exactly
E43's hash-time item-0 words.** Between the two walks of each vsync
a second DMA copy (`0xcc, 0x01414294, 0x240, 0` ← `0x0080ce70`)
overwrites item 0, so pass 1 consumes the `0x30` quad and pass 2 the
`0xcc` quad. `sub_003629B8` contributes zero stores to item 0 in
1355–1374 either (no `0x362xxx` pc in spw or records).

Who writes EE `0x00809670` is still open: no EXTRA lines in Boot B
(1270–1280) or Boot C (1355–1400) despite a proven-live watch, and
no SPR_FROM to it — staged pre-1270 (menu build) and DMA'd
read-only every vsync. The divergence from PCSX2 (`0x1b0` there)
lives in that EE buffer's contents (`0x30` here, `w3=0` static here
vs ping-pong there).

Boot-C spw (fresh first-64 at 1355): word-0 caps close on
`store128 sub_00386128` vertex storms + `store64 sub_00376938`
pointer storms — the slot's heavy reuse is why the readout
(spwlast), not first-N, was needed.

## Part-3 (ONE boot: whole-boot EE watch + SPR quads + 0x30 origin)

Boot D (e44d, wall 300 s, bound=wall, elapsed 300.85 s, rc 0, tick
reach **1372** — past the ~1300 Select-Character edge and the
1301–1354 gap): watched EE `0x809670..0x80967c` +
`0x809b70..0x809b7c` and SPR `0x70000000..0x7000000c` +
`0x70000500..0x7000050c`, first-64 spw/word, ebwlast (first 400),
spwlast (per-word last-writer of the `0x809670` quad). Slot-1 lease
claimed/released (`lease_released: true`, `pgrep_rc: 1`, own-PID
check). Yield: **520 spw + 8 ebwlast + 31 complete spwlast** (file
ends mid-line `spwlast vsync=` with no newline — a 32nd walk dispatch
(tick ≤1300 per the window gate) left a torn prefix at shutdown (the
window closed cleanly at tick 1372); its vsync number is
unrecoverable).

### Table 6 — EE last-writer (ebwlast): the ONLY EE writes in 0–1372

All 8 words identical: `vsync=41 addr=<word> value=0 via=memset
pc=0x394db8 fn=memset` (a 16 B `memset(0x809670,0,0x10)`-class zero;
regs: `a0=0x809670 a1=0 a2=0x10`). **Zero EE-writer lines after
vsync 41 through tick 1372** — EE coverage is complete (1 row/word,
cap 64 never approached), so no EE write in the whole boot escaped
the tap set.

### Table 7 — EE `0x809670` content evolution (proven by SPR-side reads)

| vsync | w0 | w1 | w2 | w3 | how we know |
|---|---|---|---|---|---|
| 41 | 0 | 0 | 0 | 0 | memset + ebwlast |
| 43 | 0 | `0x01014294` | `0x3e0` | 0 | spr-dma EE→SPR copies (`0x70000000/04/08/0c`; `0x7000000c` all-zero) |
| 260–290 | `0x0c` | `0x01414294` | `0x240` | 0 | spwlast, one line per item-0 walk dispatch (≈1/vsync; no item-0 walks 291–1372 although cap 40 and window 0–1300 are not the cause) |

The quad was **rewritten 43→260** (`w0 0→0x0c`, `w1` bit 22 set,
`w2 0x3e0→0x240`) by a writer that emitted zero lines through the
full Boot-D tap set (recompiled stores, LibC struct+bulk, SIF, CD
sync reads, ELF load, fio, rpc, GS image, mem-write, host
load/store, SPR/DMA). The 0x0c stager is therefore in the gap set.

### Table 8 — SPR quad first writers

| addr | writers (first per via/pc) |
|---|---|
| `0x70000000` | zero `store64` @41 (`pc 0x375c10 ra 0x375b74`); spr-dma EE-copy @43; `store128 0x10000006` @43 (`pc 0x3683a4 ra 0x3687d0`); `store64 0x10000010` @94 (`pc 0x379a48 ra 0x37993c`) |
| `0x70000004` | zero `store64` @41; spr-dma @43; `store64` @94 (`ra 0x37993c`) |
| `0x70000008` | zero `store64` @41 (`pc 0x375c08`); spr-dma @43; zeroing stores @43/94 |
| `0x7000000c` | all zero |
| `0x70000500..0c` | all zero (spr-dma of still-zero EE `0x809b70` @43 + zeroing `store64` @106, `pc 0x3e64c8/d0 ra 0x3640b8`) — the `0x809b70` quad is never staged this boot |

(The `0x10000006/0x10000010` SPR stores are direct-CPU VIF-packet
staging in scratchpad; pcs given for the codegen join — game fn
names are unresolved for inline stores in this tap version.)

### Codegen read: final `w0=0x30` writer / where `0x30` comes from

- **No `0x30` sighting in Boot D**: EE untouched 41→1372, SPR
  records static after 290. The only sighting remains E43's
  hash-time `0x30` at vsyncs 1355–1400.
- **Static**: zero `0x30` literals on the writer path; mode-word
  producers are modeReg assignment sites plus a mode-indexed vessel
  array (array read verified) — the value is looked up, not
  materialized, so the stager is a bulk/table copy, not an
  immediate store.
- **Unified conclusion**: BOTH the 0x0c stager (43–260, in-window)
  and the 0x30 stager (post-290, E43 1355–1400) evaded the complete
  Boot-D tap set. Single remaining hypothesis: one untapped bulk
  path stages both quads. `sceCdReadChain` / `sceCdReadStreaming` /
  `sceMcRead` / small GS-state writes got taps **only after Boot D**
  (implemented, suite-green, never booted); residuals are CD small
  out-params, TTY/Deci2, Pad small (semantically excluded: no quads)
  and VU identity (floats only). **Prime suspect: CD streaming**
  (menu assets 43–260, later assets 1300+). Next lane: boot the
  post-Boot-D tree over 0–1400.

## Part-4 (ONE boot: append/template watch + T60–T63 parity streams)

Boot E (e44e, wall 540 s, elapsed 540.16, bound=wall, rc 0, tick
reach **6180**): E33 route script, window 1255–1450, extras = the 8
EE words, `PS2X_E44_APPEND=1`. Slot 2 via `p_lane_lease.py`
(peers=[42832], GB2 in slot 1), own-PID kill (driver Popen handle),
lease released. Trace 7,282,688 B, SHA
`3fbeb23b8a727948c7dafa5b973aef2e2fbcd485` (two matching reads),
in-repo copy `local/research/E44/e44-e44e.txt`, analyzer extended
with the `tw` section. Fold fix + T60 model (raw ra, post-increment
count, T60-exact grammars verified byte-identical by unit test)
applied before boot.

Stream census: app 300 (1255–1266) / tpl 300 (1255–1259+1264–1288)
/ tplrearm 0 / tplm 0 / appsum 3000 (117–3125) / apc 165096
(41–6177, 3.4M stores) / appx 300 (1270–1572) / v1b0 200 (0–53) /
tw 2000 (40–191) / spw 1024 (16 words × 64) / ebwlast 400 /
spwlast 40.

### Table 9 — appx verdict (most important)

| site | trigger | runs? | rows | t0 | tw0 | count (v1) | ra |
|---|---|---|---|---|---|---|---|
| 0 (0x3797EC) | 0x3797E8 | yes | 170, 1270–1572 | 0x61c8fc const | 0xc const (mode 3) | 1–77 (38 distinct) | 0x379780 const |
| 1 (0x37AD44) | 0x37AD40 | yes, from 1273 | 130, 1273–1438 | 0x61c910 const | 0x30 const (mode 3) | all 1 | 0x37a958 const |
| 2 (0x37B474) | 0x37B470 | yes, from 1273 (apc 0x37b488–ac) | 0 | unobserved | unobserved | never ≤ 1 in-window (shared/continued counter) | — |

Const words: site 0 (0x1414294, 0x2a0, 0, 0xffff05dd);
site 1 (0x814884, 0x2a0, 0, 0x6040676). Item 0 at SC comes from
site 1 at count 1 (T62 parity on the count; tw0=0x30 here vs
T62's 0x1b0 — the divergence, at template level). Site 2 does 4
full copies + 5 tail-only (+0x1C/+0x1E) touches per vsync
(0x37b488 count=4, 0x37b4ac count=9).

### Table 10 — apc census (62 pcs, 7 loops + memset, 3.4M stores)

| cluster | first vsync | per-pc total |
|---|---|---|
| 0x378148–68 (9) | 43 | 55 |
| 0x379800–20 (9, site-0 stores) | 117 | 81,154 |
| 0x379b44–68 (9, T59 pcs; 0x379b58 is a branch, no store) | 94 | 247,724 |
| 0x37a204–24 (9) | 256 | ~49,294 |
| 0x37ad58–74 (7, site-1 stores; 0x37ad70 is a branch) | 1273 | 650 |
| 0x37b488–ac (9, site-2 stores) | 1273 | 520 (quad) / 1170 (tail pair) |
| 0x37d628–4c (9) | 43 | 211 |
| 0x394d90 (memset-ish) | 41 | 128 |

SC appenders (sites 1+2) come online at 1273 (~10 ticks after
E33's 1260–1263 transition — route-script drift).

### Table 11 — tw template-1 (0x61c910) history

- `0 → 0xc` @94, store64 pc 0x399670 (sub_00398A60, ra 0x398cc8)
  — INIT (with tw1=0x1414294, tw2 0x80→0x2a0 @0x3996c8,
  tw4=0xffff05df @0x399680).
- MENU churn 94–191: `→0xcc` @0x3798d4 (ra 0x3996e0),
  `→0xc` @0x379b9c (ra 0x379ac8). 195 rows, only 0xc/0xcc.
- `0x30` first sampled at 1273 (appx) → setter in (191,1273],
  UNOBSERVED (tw cap burned at 191 by MENU churn ~10/vsync).
- tw address spread: 0x61c900×730, 0x61c90c×374, 0x61c904×276,
  0x61c8fc×219, 0x61c918×195, 0x61c910×195, rest ~10.

### Table 12 — tpl parity with T60 Table 2

Same 10-write cycle, same setters at −4 pc (E44 pc = the store
insn; T60 pc = +4/next): tw0 `0x0`@0x1a2614, `0xc`@0x397fc0,
`0xcc`@0x379c24; tw1 `0xb00294`@0x1a2610+0x397e28,
`0xb0d294`@0x1a26cc, `0xf00294`@0x397f54, `0x1700294`@0x397f74,
`0x1400294`@0x397f84, `0x1414294`@0x397f98. 30/vsync.
Silence 1260–1263 (entry transition — template quiet). T60's
ra=pc note resolved: their pc == our ra (next-insn convention).

### Misses + lessons

- tplm=0 (1255–1450): no exact-mode-6 tw0 change in-window.
  (Validates the amendment-2 filter: the old 0x3C0 mask would
  have flooded on the 0xcc churn.)
- appsum (117–3125): site-0 38→39 appends/vsync at 1273; hist
  m∈{0,3} only. No mode 6 at site 0 across 3000 vsyncs (cap hit
  at 3125; later boot uncovered).
- v1b0 (0–53, burned): all pointer-pattern false positives
  (0x364ce8 stack 0x1fffdb0 ×33, heap ptrs). Lesson: a value
  watch needs a window or addr scope (T61 take note).
- tw cap (40–191): missed the 0x30 setter. Round-2 proposal:
  addr-scoped 0x61c910 + window 1000–1300 (~2 changes/vsync →
  2000 lines ≈ 1000 vsyncs).
- Fold-fix proof: `spw … addr=0x30809670 value=0x0000000c
  via=fast`; per-addr analysis keyed by UCAB spellings;
  ebwlast canonical addrs with UCAB values.
- spwlast 40 (1255–1278): item-0 walk DMA records (Boot-D
  format).

### Line grammars (T61/T62/T63 diffing)

app/tpl/tplrearm: T60-exact. appx:
`appx vsync=%llu site=%d count=%u t0=0x%x tw0..tw4 ra`
(site 0=0x3797EC, 1=0x37AD44, 2=0x37B474; count=v1
post-increment). tplm:
`tplm vsync addr tw0old tw0new tw1old tw1new pc ra fn` + 14
regs. appsum: `appsum vsync n_app n_tpl mode_hist=m:count,…|-`
(m=(tw0>>6)&0xF over site-0 appends; n_tpl = tpl-watch word
changes). apc: `apc vsync pc count` (uncapped). v1b0:
`v1b0 vsync addr lane value pc ra fn` + 14 regs. tw:
`tw vsync addr old new via pc ra fn` + 14 regs (addr
canonical; via=store8/16/32/64/128).

Open cross-lane questions: T62's 0x1b0-from-K+66 vs our
0x30-at-SC (when does PCSX2's template-1 diverge?); site-2
t0/tw0 (needs a relaxed appx filter); the 0x30 setter pc
(needs round 2).

## Receipts

- Fork rev: `571579e` (pushed `a932aff..571579e`, `git ls-remote fork ssx3` = `571579e…`).
- Runner SHAs ×2: A `2ddd59ec27cee4ab6c76953368568ff952787bba`
  (uncommitted spw-only tree); B `1580db6a353f7290ff098e4ebd38758b600d8bab`;
  C `dec5464a77ae1e2ec250f6b44722a0adba30520b`.
- Trace SHAs ×2: A `d705861ea13dbab1ad8c4a0f4529d3ee72f8f7c2`;
  B `82877f60bf8d0d0714ddca6270a2acaa5c74cfa4`;
  C `c1c2f80ea39c6b8191050dc391e7e5a13e6ed9b2`.
  In-repo copies: `local/research/E44/e44-e44{a,b,c}.txt`.
- Runner-dir gate: `git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` empty (verified pre-commit and pre-push).
- Lease: claimed/released by `e31_boot.py` (result JSON
  `lease_released: true`); no other runner lives (`pgrep_rc: 1`).
- Boot D: `e44d`, rc 0, wall 300.85 s, tick 1372 (= vsync 1372;
  1345 ticks / 300 s wall ≈ 4.6 guest-vsync/s on the tap-laden
  build); trace SHA
  `52f839618eacfc38f282f8dec9ba0d8fb0ec3628` (two matching reads);
  in-repo copy `local/research/E44/e44-e44d.txt`; result JSON +
  `boot-e44d-1.log` in `ssx3-work/E44-run/`. Boot-D runner SHA not
  captured (binary rebuilt post-boot for the gap taps — gap stated).
  Slot-1 lease claimed/released, own-PID pgrep check.
- Suite: 573/573 green on the final tree (run from the fork root;
  the VU0-macro test reads `instructions.h` via a relative path and
  fails from any other CWD — environmental, pre-existing).
