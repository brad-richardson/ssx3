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
