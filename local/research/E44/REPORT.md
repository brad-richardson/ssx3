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
| (Boot A: uncommitted worktree @ `a932aff` + spw taps; Part-2: commit TBD) | [E44] Scratchpad write watch (spw) + SPR/VIF0/VU0 taps |

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

## Tests (suite 561/561 = 551 E43 + 10 new, flags-unset, fork root)

```
cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3, uncommitted spw tree
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT \
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 561/561 (Part-2: 567/567)
```

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
- EE-source buffers' own writers unobserved (→ Boot B: EXTRA watch
  on `0x809670` w0/w3 per orchestrator Part-2, + SPR_FROM tap).
- Spend: builds as needed, suites ×4 (559→561), 1 counted boot (+2
  display-asleep crashes, no guest execution). E44-run 7.8 MB of
  2 GB.
- Exact commands:
  `cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ <rev>`
  `env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 561/561`
  `python3 local/research/E44/e44_boot.py --label e44a --wall 300
  --snap 30 --script "<route>"`
  `python3 local/research/E44/e44_analyze.py
  ~/dev/ssx3-work/E44-run/e44-e44a.txt`

## Recommendation (orchestrator decides)

Boot A separates the stagers: the in-window item-0 writers are the
`sub_00376938` pointer-build + SPR_TO EE-quad copies (two transfers,
`0x0c`/`0xcc` class) — not `sub_003629B8`. Next: Boot B per Part-2
(EE-source watch + SPR_FROM + MOD counter, VIF0 census, VU0 calls)
to find the EE-side stager and test the VU0-visibility lane.

## Part-2 (ONE boot: VIF0 census + VU0 calls + EE-source/SPR_FROM/MOD)

TBD.

## Receipts

- Fork rev: Boot A ran uncommitted (@ `a932aff` + spw taps); Part-2 rev TBD.
- Runner SHA ×2 (Boot A): `2ddd59ec27cee4ab6c76953368568ff952787bba`.
- Trace SHA ×2 (Boot A): `d705861ea13dbab1ad8c4a0f4529d3ee72f8f7c2`.
- Runner-dir gate: TBD (before push).
- Lease: claimed/released by `e31_boot.py` (result JSON
  `lease_released: true`); no other runner lives (`pgrep_rc: 1`).
