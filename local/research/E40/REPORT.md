# E40 report — MPG source-address trace: zero qualifying REF tags, uploads flow elsewhere

Brief `local/muse/prompts/E40.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/E39/REPORT.md`, `local/research/E38/REPORT.md`.

## Outcome

- **Step-1 table is empty: zero VIF1 REF/REFS/REFE tags qualified in
  vsyncs 1000–1379 (two boots). No `mpgsrc` line, no armed watch, no
  `tagwrite` line.** The trace file is never created (lazy open on first
  in-window emit).
- **This is a controlled negative, not a broken trace.** Retry Boot B ran
  the proven E39 `PS2X_VIF_MPG_LOG` in the same window as an in-situ
  control: **12,160 MPGs, ALL `copied`, vsync 1000–1379** — uploads flow
  while no qualifying REF tag passes the chain walker. Env reaches the
  runner and the walker hook is unit-proven (see Tests), so the game is
  not feeding these uploads through in-range-addr or MPG-led REF chains
  in this window.
- The `dest=0` upload signature is unchanged from E39: `num=0`,
  `fnv=6a82dc60`, `slot2=81d26b7c 000002ff` (1,520 such lines in the
  control) — i.e. still sourced off the EE `0x435bf8` image, still our
  LQI at slot 2, never PCSX2's `40000048`/`400000f2`.
- Delivered: dev-only `PS2X_MPG_SRC_TRACE` (+`_FROM`/`_TO`, 2000-line
  cap) with walker-side `mpgsrc` + macro-side `tagwrite` (pc/ra/fn +
  `$a0–$a3,$v0,$v1,$t0–$t9`). 8 new unit tests; suite **499/499**
  flags-unset from the fork root. One fork commit, ff-pushed.
  Flags-unset behavior is unchanged by construction (see Diff); no
  separate eq boot was run inside the 1+1 boot budget (stated gap).
- No verdict on "state vs codegen" per the brief; inputs are named in
  §Recommendation.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `9b82d35` | [E40] VIF1 MPG source trace: mpgsrc walker log + tag addr-word write watch |

Base `0e9b5d0` (E39 tip). Pushed `0e9b5d0..9b82d35` (`git ls-remote fork ssx3`
= `9b82d35…`); runner-dir gate `git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner` empty. Suite 499/491+8 before commit and before push.

## Diff summary

- `ps2xRuntime/include/ps2_mpg_src_trace.h` (new): header-only dev-only
  tracer modeled on `ps2_vif_mpg_log.h` (env gate, FROM/TO window on GS
  vsyncTick, 2000-line cap, flush-every-128, `configureForTest`/
  `clearForTest`). `noteMpgsrc` logs `mpgsrc vsync=<n> tag_at=0x<…>
  id=<0/3/4> qwc=<n> addr=0x<…> tte_vif=<16 hex>` and arms a watch on
  `tag_at+4` (dedup, max 64). `noteStore`/`noteStoreCtx` log `tagwrite
  vsync=<n> addr=0x<…> value=0x<overlapped word> pc=0x<…> ra=0x<…>
  fn=<…> a0=… t9=…` for every armed watch overlapped by the store.
- `ps2xRuntime/src/lib/ps2_memory.cpp` (walker only): in the VIF1
  chain-mode walk, for ids 0/3/4, log when `addr` ∈
  `[0x430000,0x440000)` or a bounded command-boundary scan
  (`e40PayloadHasMpg`, ≤64 QWs; fixed-size cmds step, MPG hits, DIRECT
  skips, UNPACK/overrun stop conservatively) finds MPG `0x4A` in the
  payload. TTE bytes read from the tag upper half. Copy semantics
  untouched.
- `ps2xRuntime/include/ps2_runtime_macros.h` (tap only): all five
  `WRITE*` macros forward to `noteStoreCtx(runtime, ctx, …, __func__)`
  behind `writeArmed()` — one relaxed atomic check when off, beside the
  existing `ps2DiagWatchEnabled()` / `ps2TraceGuestWrite` taps (the
  reused watch mechanism, cited). Off = zero behavior change.
- `ps2xTest/src/ps2_mpg_src_trace_tests.cpp` (new, `Ps2MpgSrcTrace`, 8
  tests), registered in `src/main.cpp`, listed in
  `ps2xTest/CMakeLists.txt`.

## Tests (`Ps2MpgSrcTrace`, all pass; suite 499/499 = 491 E38 + 8 new)

Off-by-default (no arm, no log); exact `mpgsrc` line format + watch arm;
`tagwrite` carries pc/ra/fn + all 16 GPRs, silent on non-overlap; wide
(8-byte) overlapping store extracts the watched word, adjacent store
silent; FROM/TO filters both line kinds (out-of-window `mpgsrc` does not
arm); cap stops at exactly 2000 lines; walker integration (REF id=3,
addr=`0x435bf8`, TTE bytes → exact one-line file + armed watch);
scan path (MPG-led out-of-range payload logs, NOP-only payload silent,
no arm).

## Boots (Mac mini, E32-build @ fork `9b82d35`, runner SHA
`7b52d70e…83258c` two matching reads, E33 vsync route,
`PS2X_SKIP_MOVIE=1`, lease-claimed, rc 0, lease released)

| Boot | Env | Result |
|---|---|---|
| e40a (A) | wall 300, snap 30, SRC 1000–1400 | wall-bound 301.5 s, tick 1376; **SRC: 0 lines (no file)**; SC frame SHA `41cca09c…` = E39 SC settled |
| e40b (B, retry) | wall 300, snap 30, SRC 1000–1400 + MPG-log 1000–1400 (control) | wall-bound 302.2 s, tick 1379; **SRC: 0 lines (no file)**; control `vif-mpg-e40b.txt` **12,160 lines, all `copied`**, vsync 1000–1379 |

## Step-2 tables

### Distinct REF `addr` values for `MPG addr=0` uploads (1000–1379)

| addr | n | tag_at | storing fn + regs |
|---|---|---|---|
| *(none — zero qualifying tags)* | 0 | — | — |

No `tag_at` was ever seen, so no watch was armed and no `tagwrite`
exists. The store-side path is unit-tested only (stated gap).

### Control: what the uploads look like while SRC stays silent (same window, same boot)

| Upload | n | Signature |
|---|---|---|
| `imm=0 num=0 dest=0-2048` | 1,520 | `outcome=copied fnv=6a82dc60 slot2=81d26b7c 000002ff slot8=8000033c 01d214c5` |
| all other MPGs | 10,640 | `outcome=copied` (zero drop/clip rows of any kind) |

First control line `vsync=1000`, last `vsync=1379`; max `avail=33192`
bytes in the interpreter buffer for a dest=0 upload.

### Codegen computation table (base + index × stride, index source/value)

| Item | Result |
|---|---|
| Storing function for the REF addr word | unknown — no `tagwrite` observed |
| `0x435bf8` / `0x4349b8` as immediates in `~/dev/ssx3-work/codegen-ssx3/sub_*.cpp` | **absent** (hex any-case + decimal `4401400`/`4396216`: zero hits) — the source address is computed at runtime (base + index × stride shape), not stored as a constant |

## Gaps / notes

- The SRC-empty result has three live sub-explanations, not
  discriminated: (a) VIF1 uploads travel via CNT (id 1) chains /
  normal-mode MADR / CPU FIFO — none of which carry a REF addr word
  (my hook sits only on chain-mode ids 0/3/4; `processVIF1Data` has two
  other call sites: FIFO line ~1176, normal-mode lines ~1945/1962);
  (b) REF tags exist but out-of-range with MPGs deeper than 64 QWs or
  behind UNPACK/DIRECT-overrun, which the bounded scan misses by
  design; (c) in-vsync timing (tags logged only when the walker runs).
- No flags-unset eq boot was run (budget 1+1 spent on A + controlled
  retry); parity rests on suite 499/499 + off-state code review (one
  atomic check per tap, no copy-path edits) + healthy boots at
  E39-identical tick/frame.
- `tagwrite` never fired in-situ (no watches armed); the WRITE-macro
  hook is proven by unit tests only. Constant-address inlined
  `ps2TraceGuestWrite(...); FAST_WRITE*(...)` sequences in generated
  code (~7.5k sites, globals) bypass the macros by construction;
  chain-builder tag writes are dynamic (register+offset → macros).
- Bytes: E40-run 17 MB; internal total 27.3/200 GB cap. 2 launches used
  (brief: 1 boot + 1 retry).

## Exact commands

```
cmake --build ~/dev/ssx3-work/E32-build -j8   # fork ssx3 @ 9b82d35
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 499/499 (from ~/dev/PS2Recomp)
python3 local/research/E40/e40_boot.py --label e40a --wall 300 --snap 30 --src-from 1000 --src-to 1400 --script "<route>"
python3 local/research/E40/e40_boot.py --label e40b --wall 300 --snap 30 --src-from 1000 --src-to 1400 --mpg-from 1000 --mpg-to 1400 --script "<route>"
python3 local/research/E40/e40_analyze.py ~/dev/ssx3-work/E40-run/vif-mpg-e40b.txt  # control cut (mpgsrc/tagwrite regexes match 0)
git push fork ssx3  # 0e9b5d0..9b82d35 (runner-dir gate empty)
```

(`<route>` = E33 vsync string, as in E38/E39. `e40_analyze.py` parses
both line kinds; run against a future non-empty SRC trace.)

## Part-2 — guest READ watch on the microcode source heads (approved follow-up)

### Change

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `99b5fd8` | [E40] Part-2: guest READ watch on microcode source heads (srcread) |

Base `9b82d35`. Pushed `9b82d35..99b5fd8` (first attempt rejected with
GitHub `Internal Server Error`; retry succeeded; `git ls-remote fork
ssx3` = `99b5fd8…`); runner-dir gate `git diff --stat 14b1e5cb ssx3 --
ps2xRuntime/src/runner` empty. Suite **503/503** flags-unset from the
fork root (499 + 4 new `Ps2MpgSrcTrace` read tests).

Diff: `ps2_mpg_src_trace.h` gains fixed regions `0x435BF8`/`0x4349B8`
(16 B each), `noteRead`/`noteReadCtx` (`srcread vsync=<n>
addr=0x<read addr> size=<n> pc=0x<…> ra=0x<…> fn=<…> a0..a3 v0 v1
t0..t9 s0..s7`, low 32 bits hex), first-64-hits-per-region in-window
(out-of-window reads consume nothing), shared 2000-line cap.
`ps2_runtime_macros.h`: all five `READ*` macros forward behind
`readArmed()` plus a lock-free address pre-filter (loads are hotter
than stores). **Caught in unit test:** `__func__` inside the READ
expression-lambda is `operator()`, not the host function — fixed with a
lambda init-capture (`ps2xE40Fn = __func__`, evaluated in the enclosing
scope); the macro-tap test asserts the real host name. WRITE taps
(`do…while`, no lambda) were already correct. Reads bypassing the
macros: inlined constant-address `FAST_READ*(0x…)` sequences (691
`FAST_READ32(0x…)` sites vs 124,223 macro `READ32(` uses) — and a
codegen-wide check confirms **zero** dynamic direct `Ps2FastRead*`
calls, so every register-addressed guest load passes the tap. The two
watched heads appear as immediates nowhere in codegen (Part-1 search),
so a constant-address load of exactly these words does not exist
either: the watch has no blind spot for EE CPU loads.

Tests (4 new, all pass): off-by-default; exact `srcread` format incl.
s0–s7; 64-hit cap per region with independence (64+3 lines) and
window non-consumption; `READ32` macro-tap end-to-end (value returned
+ host fn name).

### Boot e40c (Part-2 Boot A; Mac mini, E32-build @ `99b5fd8`, runner SHA
`2db28375…9a4407` two matching reads, E33 route, wall 300, snap 30,
SRC 1000–1400 + MPG control 1000–1400, rc 0 wall-bound 301.5 s, tick
~1376, lease released)

- **SRC trace: 0 lines (no file). Zero EE CPU loads overlapped either
  16-byte source region in vsyncs 1000–1378.**
- Control `vif-mpg-e40c.txt` (copied in-repo, SHA
  `0287e537…a4687ad80`): **12,148 lines on disk, ALL `copied`**, vsync
  1000–1378; dest=0 signature unchanged (`fnv=6a82dc60`,
  `slot2=81d26b7c`, 1,519 lines).
- The tap is unit-proven incl. host-fn capture, env reaches the runner
  (control logged), and no load path bypasses the macros — so the
  microcode bytes reach the VIF interpreter purely via DMA-engine reads
  (host-side memcpys), never via EE loads of these heads, in this window.

### Source-pointer formation table (reading fn + caller via ra)

| Reading function | Caller (via ra) | Pointer formed as | Index source | Index value at read |
|---|---|---|---|---|
| *(none — zero `srcread` hits)* | — | — | — | — |

No storing function either (Part-1 `tagwrite` still empty: no REF tags
⇒ no armed watches). Named inputs for the next step instead of a
verdict: 12,148/12,148 copied control MPGs 1000–1378; SRC + mpgsrc
silence under identical conditions; no source-head immediates in
codegen; no dynamic fast-read bypass. The source address is handed to
the DMA engine without EE code touching these words — the remaining
suspects are MADR/CHCR/TADR register writes and CNT-tagged chains
(T50 covers the PCSX2 side).

Bytes: E40-run 26 MB total (3 boots); internal total 27.5/200 GB
cap. Part-2 spend: builds as needed, 1 boot, 0 retries.

```
cmake --build ~/dev/ssx3-work/E32-build -j8   # fork ssx3 @ 99b5fd8
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 503/503
python3 local/research/E40/e40_boot.py --label e40c --wall 300 --snap 30 --src-from 1000 --src-to 1400 --mpg-from 1000 --mpg-to 1400 --script "<route>"
```

## Recommendation (orchestrator decides)

The REF-addr question as briefed is unanswerable from this window: the
uploads demonstrably arrive without qualifying REF tags. Inputs for the
next lane (no verdict): 12,160/12,160 copied control MPGs 1000–1379
(`local/research/E40/vif-mpg-e40b.txt`, SHA
`02549650…84cee40`); dest=0 signature `fnv=6a82dc60
slot2=81d26b7c`; SRC silence under identical conditions; no
`0x435bf8`/`0x4349b8` immediates anywhere in codegen. Recommended
redirect, in order: (1) widen the walker tap to **all** VIF1 chain tag
ids (log id/qwc/addr + TTE bytes unconditionally for a short window) to
test the CNT-chain hypothesis — one-line change to the E40 hook's id
filter; (2) if chains are absent too, tap normal-mode MADR and the FIFO
site; the chain-builder hunt then becomes a MADR/FIFO-writer hunt, not
a REF-addr hunt. Keep the E40 tracer (zero measured behavior change,
in-situ control clean).
