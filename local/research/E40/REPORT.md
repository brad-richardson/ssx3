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

## Part-3 — dest-0 payload source + DMA-reg watch (approved follow-up)

### Change

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `78ed470` | [E40] Part-3: dest-0 MPG payload source (mpgpay) + VIF1 DMA-reg watch |

Base `99b5fd8`. Pushed `99b5fd8..78ed470` (clean); runner-dir gate
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` empty. Suite
**510/510** flags-unset from the fork root (503 + 7 new
`Ps2MpgSrcTrace` tests: chain/normal/window mpgpay, pay-map lookup,
isDmareg, dmareg format+cap, WRITE32 macro tap with a real runtime).

Diff: new `ps2_vif_src_span.h` (cycle-free span struct);
`PendingTransfer.srcSpans`; walker records EE spans per appended range
(VIF1, only when traced); each VIF1 delivery installs the map around
`processVIF1Data` (chain spans / MADR-based normal spans / sourceless
FIFO marker); MPG handler logs `mpgpay vsync=<n> imm=0 num=<n>
src=0x<raw> srcmask=0x<raw&0x1FFFFFFF> mode=<chain:<id>|normal|fifo>
tag_at=0x<…>|-` for dest-0 uploads; WRITE8/16/32/64 macros report the
four VIF1 DMA regs as `dmareg vsync=<n> reg=<CHCR|MADR|QWC|TADR>
value=0x<low32> pc/ra/fn + a0–s7` (first 256 in-window; generated code
has no inlined stores to `0x1000xxxx` codegen-wide, so the macros see
every DMA-reg write; 128-bit stores to 32-bit DMA regs excluded by
construction). `src` is the payload-byte source (`dataAddr+offset` /
`srcAddr+pos`, i.e. 4 past the MPG cmd word); join to MADR by `src-4`.

Test-debug notes (expectation fixes only, no runtime change needed):
`src` includes the 4-byte CMD offset per the brief formula; CNT payload
is inline after the tag; the drain consumes QWC (re-arm MADR+QWC per
kick in tests); a dest-0 TTE MPG emits mpgpay too (Part-1 walker test
now uses slot 4 to stay pure); trailing zero-tag TTE bytes extend chain
buffers (8+16+8=32).

### Boot e40d (Part-3 Boot A; Mac mini, E32-build @ `78ed470`, runner SHA
`9b0a71a7…ab4e4b` two matching reads, E33 route, wall 300, snap 30,
SRC 1300–1320 + MPG control 1300–1320, rc 0 wall-bound 301.1 s, tick
1366, final frame `5aa169f0…` (route-identical, kill-tick differs from
A/B), lease released)

- SRC `mpg-src-e40d.txt` (copied in-repo, SHA `c9b16e0a…3d3d`): **78
  `mpgpay` + 79 `dmareg`** (+1 truncated kill-edge line), 0 mpgsrc / 0
  tagwrite / 0 srcread as before.
- Control `vif-mpg-e40d.txt` (copied in-repo, SHA `a77e7f74…612e`):
  **640/640 `copied`**, vsync 1300–1319; dest-0 signature unchanged
  (`fnv=6a82dc60 slot2=81d26b7c`, 80 lines = 4/vsync). mpgpay attributes
  78/80; the shortfall is the SIGTERM edge (1319 has 2/4 + the truncated
  tail).

### Table 1 — distinct `src` for dest-0 uploads (1300–1319)

| src | srcmask | mode | tag_at | n | vsync | num |
|---|---|---|---|---|---|---|
| 0x00435bf8 | 0x00435bf8 | chain:6 | 0x00435bd0 | 78 | 1300–1319 (20) | 0 |

One value. `mode=chain:6` = CALL tag with inline payload
(`dataAddr = tagAddr+16` in this runtime's walker, matching HW CALL
semantics): a CALL tag at static `0x435bd0` carries the 2048 B upload
inline (`src` = payload head = cmd+4). Uncached/KSEG mirrors need no
separate handling — `srcmask` folds them and the observed raw value is
already the cached alias. No MADR lines exist (chain mode doesn't use
MADR); each upload's MADR-equivalent is `src-4`.

### Table 2 — `dmareg` stores (who kicked the chains)

| reg | n | values | fn | pc | ra |
|---|---|---|---|---|---|
| CHCR | 39+1 cut | 0x185 (const) | sub_00382760_0x382760 | 0x382a0c, 0x382adc | 0x382938 |
| TADR | 40 | 0x708520/0x63b8a0 (site 1, alternating) 0x708a30/0x63bdb0 (site 2, alternating) | sub_00382760_0x382760 | 0x382a04 (site 1), 0x382ad8 (site 2) | 0x382938 |

2 kicks/vsync, 4 uploads/vsync, all through CALL@0x435bd0 (each chain
CALLs the static uploader twice — single `tag_at`, single `src`). No
MADR/QWC stores: chain mode. s0 = 0x61ba60 on all 40 TADR lines; CHCR
always 0x185 (STR|CHAIN|TTE|DIR). Site1–site2 stride within a frame:
0x510; arenas ping-pong per vsync (double-buffered chains).

### Table 3 — address formation (codegen read)

In `sub_00382760_0x382760` (`~/dev/ssx3-work/codegen-ssx3/`):

| Store | Formation | Base | Index × stride | Index source / value at read |
|---|---|---|---|---|
| TADR @ 0x382a04 | `lw $v0, 0x5AA8($s0)` → `sw $v0, 0($s4)` | s0 = a0_entry = struct @ 0x61ba60 (constant, all 40 lines) | none at this site (fixed field +0x5AA8) | field content ping-pongs 0x708520↔0x63b8a0 (double-buffer slot; parity flips/vsync) |
| TADR @ 0x382ad8 | `lw $v0, 0x5A9C($s0)` → `sw $v0, 0($s4)` | same s0 | none (fixed field +0x5A9C) | content ping-pongs 0x708a30↔0x63bdb0 |
| CHCR @ 0x382a0c/0x382adc | `addiu $v0/$v1, $zero, 0x185` (immediate) | — | — | const 0x185 |
| ra @ stores | 0x382938 on all 79 lines | — | — | return into sub_382760 itself after `jal func_424020` (syscall trampoline `addiu $v1,$0,0x64; syscall; jr $ra`), flowing into a D_STAT (0x1000D000 bit 0x100) spin-wait, then kick 1, then kick 2 (`jal func_423DC0` after) |

Producer of field +0x5AA8 (single writer codegen-wide):
`sub_00376938` @ 0x377b50 `sw $s1, 0x5AA8($s3)`, s1 = `*(s3+0x5A00)`
(loaded @ 0x377b10), in the sequence
`v1 = (s3+0x5A90) + (*(s3+0x5A10) << 2); *(v1) = 2` (@ 0x377b28–58)
with the stack-passed index saved at `*(s3+0x5AB4)` — i.e. **base =
s3+0x5A90, index = MEM[s3+0x5A10], stride ×4**. Read conclusion
s3 == s0's struct (0x61ba60): sole writer + value flow into the
reader's ping-pong slots; corroborated by a2 = 0x6214f0 = s0+0x5A90
(the index-table base) on every TADR line. Index *value* at read: not
directly captured (a2 then is the reused table base); parity
alternation ⇒ slot flips each vsync. The +0x5A9C field (site 2) has no
direct store codegen-wide — likely filled via a computed pointer or a
sibling sequence not chased (stated gap).

Reconstruction (read conclusion, no verdict): per frame the game
rebuilds two chains in alternating arenas and kicks each once; both
chains CALL the static uploader CALL@0x435bd0 twice, which carries the
num=0 microcode inline from 0x435bf8 (same bytes re-uploaded 4×/vsync;
E39's dest-0 signature unchanged). Next lanes can key off TADR ∈
{0x708520, 0x63b8a0, 0x708a30, 0x63bdb0} or the static 0x435bd0/0x435bf8.

Bytes: E40-run 32 MB total (4 boots); internal total 27.5/200 GB cap.
Part-3 spend: builds as needed, 1 boot, 0 retries. Exact commands as
Parts 1–2 with `--label e40d --src-from 1300 --src-to 1320 --mpg-from
1300 --mpg-to 1320`; analyze with `e40_analyze.py` (now parses
mpgpay/dmareg).

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

## Part-4 — arenastore watch + ctag kick dump (Boot e40e)

Tracer rev `531c09b` (fork `ssx3`, ff-pushed `78ed470..531c09b`;
runner SHA `86c6be42…0a9d96b`): default-off store watch on chain
arenas `0x63b800–0x63c400` + `0x708400–0x708d00` with per-lane
32-bit fold (`& 0x0FFFFFFF`, covers `0x20/0x30/0x80` mirrors) firing
only for folded values in `0x030000–0x040000`
(`arenastore vsync=<n> addr=0x<> value=0x<> pc ra fn a0..a3 v0 v1
t0..t9 s0..s7`, first 256), plus walker `ctag` dump
(`ctag tag_at=0x<> id=<> qwc=<> addr=0x<> tte=<16hex>`, first 2
kicks, no line cap). Unit tests added (arena predicate incl.
`0x30`-mirror fold, wide-store lane extraction, CNT/REF/END walker
walks with exact `tag_at`/order expectations incl. REF `+16`
advance); suite green `514/514` twice (one `513/514` flake on an
intermediate run, clean on both reruns). Live-path confirmed: guest
SW/SD/SQ lower through the tapped WRITE32/64/128 macros in codegen.

### Boot e40e (Part-4 Boot A; Mac mini, E32-build @ `531c09b`, E33 route, wall 300, snap 30, SRC 1300–1320 + MPG control 1300–1320, rc 0 wall-bound 301.2 s, final frame tick 1377 `fnv1a=129073fb`, lease released)

- SRC `mpg-src-e40e.txt` (copied in-repo, SHA `fa6315f1…ee8f4`):
  **0 `arenastore`**, **1704 `ctag`**, 82 `mpgpay`, 83 `dmareg`,
  0 mpgsrc/tagwrite/srcread.
- Control `vif-mpg-e40e.txt` (copied in-repo, SHA
  `918ac5a4…db6c7d`): **640/640 `copied`**, vsync 1300–1319;
  dest-0 signature unchanged (`fnv=6a82dc60 slot2=81d26b7c`,
  4/vsync) — route-identical to e40d; final-frame SHA differs by
  wall-clock kill drift only (1377 vs 1366 ticks, same variance
  class as A/B).
- `mpgpay`: exactly 4/vsync × 1300–1319 + 2 @1320, ALL
  `src=0x00435bf8 num=0 mode=chain:6 tag_at=0x00435bd0`.

### Table 2 — chain tags walked (first 2 kicks, 1704 lines)

| id | n | reading |
|---|---|---|
| 1 CNT | 571 | inline-payload links |
| 2 NEXT | 221 | sub-chain links (`addr` = next tag, e.g. `0x6326f0→0x632700`) |
| 3 REF | 10 | `0x44b140` (qwc 7) + `0x44b200` (qwc 34) |
| 5 CALL | 450 | 446 sub-chain addrs (`0x62xxxx`, `0xecxxxx–0xf1xxxx`, each ×1) + **`0x435bd0` ×4** |
| 6 RET | 450 | sub-chain returns + `RET@0x435bd0 qwc=998 tte=0100040420000000` ×4 |
| 7 END | 2 | 2 top-level chains = the 2 dumped kicks (cap engaged as designed) |

`0x4349b8` appears **0×** in all 1704 tags. The 4 CALL→uploader
sites (all in `0x63b800–0x63c400`): `0x63b990`, `0x63bbe0`,
`0x63bea0`, `0x63c130` (arena offsets `0x190/0x3e0/0x6a0/0x930`,
non-uniform). One contiguous walk covers `0x63b8a0→0x63c130`
(CNT/CNT/CALL→`0x435bd0`/CNT/REF→`0x44b140`/CNT/
CALL→`0x632460`/…/CALL→`0x435bd0` ×4 total/REF→`0x44b200`/
CALL→`0x6325e0`/END/…). **Zero tags walked in
`0x708400–0x708d00`** (stale Part-3 TADR or out-of-window kick).

### Finding (corrects Part-3's read conclusion)

The Part-3 "rebuilds two chains per frame" wording is wrong for
this window: **no guest store wrote a `0x43xxxx` word into either
watched arena during vsync 1300–1320** (0 `arenastore` lines, live
taps verified), yet the chain is kicked every vsync (4× `mpgpay`
`src=0x435bf8` per vsync, all 20 vsyncs). The 4 CALL→`0x435bd0`
words and the REF words are **baked at chain-build time (before
vsync 1300) and re-kicked per frame, not rewritten per frame**.
The uploader decision (all-`0x435bd0`, never `0x4349b8`) is a
scene-setup-time outcome in this window; catching the write needs
an earlier window (chain build / scene init), not 1300–1320.

### Table 3 — uploader-address formation (codegen read)

No `0x435bd0`/`0x4349b8`/`0x63b800` immediate exists in any of the
9455 codegen files (hex, lui-half, and decimal searched; only
opcode/offset false positives) — the builder does **not**
materialize the uploader address; it loads it. Closest-read
CALL-tag packet builder: `sub_00367DB8` (`0x367db8–0x367f18`,
in the `0x36xxxx–0x38xxxx` graphics-library cluster holding 20 of
22 `lui …,0x5000` CALL-tag builders):

| slot | observed |
|---|---|
| table base | caller-supplied pointer in `a0` (address unknown, no immediates) |
| index | caller-supplied in `a1` |
| stride | **4** (`sll a1,2`; entry = `base + index*4`; entry pointer `lw entry+8`) |
| ADDR source | table-entry data (`ld entry+0x38` → bitfield ops → stored words); never an immediate |
| cursor | `*a2`, advanced `0x60`/packet, written back (`sw a1,0(a2)` in delay slot) |
| packet | CNT(qwc 5) + payload + CALL(qwc 4) + GIF/VIF words |

Caveat (stated plainly): `sub_00367DB8` stamps CALL **qwc=4**;
the observed display-chain CALLs are **qwc=0** — same-library
idiom and strongest candidate read, **not** confirmed as our
chain's stamper. Index source/value (which caller, which index
selects `0x435bd0` over `0x4349b8`) is therefore still open; the
dumping hook to catch it is the `arenastore` watch run against a
scene-build window.

### Gaps / notes

- `ctag` carries no vsync field — the 2 dumped kicks can't be
  attributed to specific vsyncs (add `vsync=<n>` next rev).
- Test-fidelity note (no runtime impact): unit tests built CNT
  tags with id field 0 (actually REFE); HW CNT = id 1 as the live
  dump confirms. Tracer prints the raw id; only test labels were
  off. Rename to REFE-labeled expectations next touch.
- Part-4 spend: test/rebuild cycles as needed, fork commit +
  ff-push, 1 boot, 0 retries. Command: `python3
  local/research/E40/e40_boot.py --label e40e --wall 300 --snap 30
  --src-from 1300 --src-to 1320 --mpg-from 1300 --mpg-to 1320
  --script "<E33 route>"`.

## Recommendation (orchestrator decides)

Next lane: re-run the Part-4 binary with the SRC window moved to
scene/chain-build time (before the first kick of the settled
scene — find it by scanning `mpgpay`/`dmareg` backwards for the
first `src=0x435bf8` vsync, then window ~200 vsyncs earlier) and
read the storing `pc/fn` off the `arenastore` lines; that pc
identifies the true storing function and its index source/value.
Keep the E40 tracer as-is (add `vsync` to `ctag` when next
touched). No per-frame ADDR rewrite exists to chase in 1300–1320.

## Part-5 — scene-build window 1150–1300 (Boot e40f)

Tracer revs `4282b16` (env arenas + uploadload) + `052c16b` (file
cap 2000→8000; pre-existing cap test follows the budget — contract
change surfaced: the briefed 150-vsync window provably exceeds 2000
lines: ~1700 ctag + ~8/vsync per-frame + 320 quarries ≈ 3200+).
Fork `ssx3` ff-pushed twice; runner SHA `86c6be42…` rebuilt 05:49.
Suite green `520/520` twice. `PS2X_MPG_SRC_ARENAS` passes through
the boot env untouched (`dict(os.environ)` + BASE).

### Boot e40f (Part-5 Boot A; E33 route, wall 300, snap 30, SRC
1150–1300 + MPG control 1150–1300, arenas
`0x600000-0x640000,0x700000-0x720000`, rc 0 wall-bound 302.2 s,
final frame tick 1374 `fnv1a=f36e507b`, lease released)

- SRC `mpg-src-e40f.txt` (copied in-repo, SHA
  `32e438c1…3c1dd2`): **0 `arenastore`, 0 `uploadload`**,
  277 `ctag` (first 2 kicks, 2 ENDs), 578 `mpgpay`, 256 `dmareg`,
  0 mpgsrc/tagwrite/srcread. File total 1110 (no global-cap cut).
- `mpgpay`: ALL `src=0x00435bf8 num=0`, spanning vsync
  1150–1293 — the static-uploader chain is already kicking at
  window open. **Build is strictly before vsync 1150.**
- Control `vif-mpg-e40f.txt` (copied in-repo, SHA
  `0a339958…0de723`): full to vsync 1300.

### Table 4 — per-frame kick alternation (dmareg TADR, 1150–1213)

| vsync parity | TADR pair kicked |
|---|---|
| even | `0x6f7f20`, `0x6f83d0` |
| odd | `0x62b2a0`, `0x62b750` |

Two kicks per vsync, alternating chain sets. **The `0x6fxxxx`
set was never watched** — outside the Part-4 defaults AND the
Part-5 ranges (`0x700000` starts above `0x6f83d0`); the `0x62xxxx`
set was watched and is static (zero stores). Whether the `0x6f`
set is rebuilt per frame is untested. `dmareg` hit its own
`kMaxDmLines = 256` cap at vsync 1213 — TADR data truncated there
(raise next time).

### Table 5 — the kick function (codegen read, confirmed live)

`dmareg` gives `pc=0x00382a04/0x00382a0c ra=0x00382938
fn=sub_00382760_0x382760` (`0x382760–0x382af0`,
`codegen-ssx3/sub_00382760_0x382760.cpp`):

| slot | observed |
|---|---|
| TADR write | pc `0x382a04`: `sw v0,0(s4)` ← `v0 = lw(s0+0x5AA8)` @ `0x382a00` (s4 = VIF1 TADR `0x10009030`) |
| CHCR write | pc `0x382a0c`: `sw 0x185,0(s1)` (kick) |
| MADR / QWC | `MADR = lw(s0+0x5AB0)` @ `0x3829c8` (live `a1=0x7e3000`); QWC const `0x105` |
| struct | first arg: `daddu s0,a0,zero` @ entry; live `s0=0x61ba60`, so TADR field = `0x671508`, MADR field = `0x671510` |
| caller | unknown — captured `ra=0x382938` is the inner `jal func_424020` return, not the caller |
| also per kick | `lq v0,0(0x44B9C0)` @ `0x38297c` (READ128 from the library region; lanes checked live, no uploader match) |

### Table 6 — first-2-kick ctag (277 lines, both 0x6f chains)

All walked tags in `0x6f0xxx–0x6f8xxx`; the 4 CALL→uploader
sites: `0x6f8010`, `0x6f8260`, `0x6f84c0`, `0x6f8750` (all
`0x435bd0`; `0x4349b8` 0×). Same 4-site structure as the 0x63b8
chain. The 0x62 set never got dumped (cap reached on the 0x6f
pair).

### Finding

The briefed table (storing function + source load) is unfillable
from this window: **no 0x43xxxx stores into the watched ranges
and no uploader-valued loads anywhere in 1150–1300**. The chain
(and its uploader choice) predates vsync 1150. New nearest
confirmed object: the kick function above — the uploader decision
now reduces to (a) who writes the `0x6f`/`0x62` chains (before
1150; the `0x6f` set additionally needs a watched rebuild test),
and (b) who writes the select struct word `0x671508` per frame.

### Gaps / notes

- Env delivery is unverified post-hoc (no env echo in the boot
  log); the zero stands under either defaults or wide ranges
  (wide ⊃ defaults), but next boot should log the effective
  ranges. `ctag` still lacks vsync attribution (carried over).
- Part-5 spend: builds + 2 fork commits/ff-pushes, 1 boot,
  0 retries. Command: `PS2X_MPG_SRC_ARENAS="0x600000-0x640000,
  0x700000-0x720000" python3 local/research/E40/e40_boot.py
  --label e40f --wall 300 --snap 30 --src-from 1150 --src-to
  1300 --mpg-from 1150 --mpg-to 1300 --script "<E33 route>"`.

## Recommendation (orchestrator decides)

Next lane (1 boot): window **before 1150** (find the first
`src=0x435bf8` vsync with an early-window boot, then bracket the
build), ranges **covering `0x6f0000–0x700000`** (the unwatched
alternating set) plus current wides, `kMaxDmLines` raised past
256, and a one-word store watch on the select struct field
(`0x671508` = TADR source; verify the struct base reproduces —
heap has been address-stable across e40d/e/f). The first
`arenastore`/`uploadload` hits there name the storing function
and its table load directly.

## Part-6 — render-DMA-thread state sequence (Boot e40g)

Tracer rev `338ad99` (fork `ssx3`, ff-pushed `052c16b..338ad99`;
runner rebuilt, SHA noted in boot log): default-off T51-mirror
watches — `st` (guest stores to `0x6214E0–0x62151F` with
scheduler-mirrored `intc`), `sema` (Signal/iSignal/Wait/PollSema
filtered on live RAM at `0x62150C`/`0x621508`), `irq` (every queued
guest handler dispatch), plus existing `dmareg` kicks — one file,
execution order. Suite green `525/525` twice. No sub-caps (5-vsync
window); global cap bounds.

### Boot e40g (Part-6 Boot A; E33 route, wall 300, snap 30, SRC
1300–1304 + MPG control 1300–1304, default arenas, rc 0 wall-bound
302.2 s, final frame tick 1377 `fnv1a=129073fb` = e40e exactly,
lease released)

- SRC `mpg-src-e40g.txt` (copied in-repo, SHA
  `740a57d5…affcd3`): **109 `st`, 0 `sema`, 29 `irq`**,
  20 `dmareg`, 18 `mpgpay`, 1704 `ctag` (first 2 kicks),
  0 arenastore/uploadload. Total 1879 (no cap cut).
- Control `vif-mpg-e40g.txt` (copied in-repo, SHA
  `5a97d752…d20a17`): 128 lines; dest-0 signature unchanged
  (`fnv=6a82dc60 slot2=81d26b7c`).
- `mpgpay`: 4/vsync (2 @1304 edge), ALL `src=0x00435bf8
  num=0`. **`0x434990` appears 0× anywhere in the file.**

### Table 7 — per-vsync sequence (identical all 5 vsyncs)

| # | line |
|---|---|
| 1–2 | `irq` INTC cause `0x2` → `0x3c1980`, then → `0x3825c0` |
| 3 | `irq` timer `0xa` → `0x3e4db8` |
| 4 | `irq` INTC cause `0x3` → `0x31a490` |
| 5–6 | `irq` VIF1-end (cause `0x1`, ch 1) → `0x382650`, **×2** (1304: ×1, window edge) |
| 7–12 | `st` state word `0x6214EC` = **5 → 0 → 1 → 2 → 3 → 4** (writers below) |
| 13+ | `st` chain heads `0x621508`/`0x62150C` (sub_0x377b24, values below) |
| 14+ | `dmareg` kick site 1 (ra `0x382938`) + kick site 2 (ra `0x3827e8`) |

### Table 8 — state-word writers (`0x6214EC`)

| value | pc | fn | ra | intc |
|---|---|---|---|---|
| 5 | `0x382634` | sub_0x3825f8 | `0x3825dc` | 1 |
| 0 | `0x382818` | sub_0x382760 | `0x3827e8` | 0 |
| 1 | `0x382920` | sub_0x382760 | `0x3827e8` | 0 |
| 2 | `0x3826a8` | sub_0x382688 | `0x38266c` | 1 |
| 3 | `0x382acc` | sub_0x382760 | `0x3827e8` | 0 |
| 4 | `0x3826d0` | sub_0x382688 | `0x38266c` | 1 |

The `intc` mirror works: handler-context writers (`0x3825f8`/
`0x382688`, reached from the VIF1-end handler `0x382650`) flag 1;
thread-context writers (`0x382760`) flag 0.

### Table 9 — kicks (both sites fire every vsync)

| vsync | site 1 (ra `0x382938`, pc `0x382a04`) | site 2 (ra `0x3827e8`, pc `0x382ad8`) |
|---|---|---|
| 1300/1302/1304 | TADR `0x63b8a0` = *(0x621508) | TADR `0x63bdb0` = *(0x62150C) |
| 1301/1303 | TADR `0x708520` = *(0x621508) | TADR `0x708a30` = *(0x62150C) |

Chain-head words `0x621508`/`0x62150C` are rewritten per vsync by
`sub_00377b24` (pc `0x377b50`/`0x377b44`), alternating the
`0x63b8`/`0x7085` sets.

### Findings (two premises corrected)

1. **The recomp kicks from BOTH sites every vsync** (ra
   `0x382938` and ra `0x3827e8`) — the "recomp only ever kicks
   with ra `0x382938`" premise is contradicted in this window.
   The missing pass-2 is NOT the kick: both chains' CALLs point
   at `0x435bd0`, and no `0x434990` upload occurs. The divergence
   is the uploader CHOICE in the second chain, not the kick path.
2. **The runtime HAS VIF1 DMAC-end dispatch**: `ps2_memory.cpp`
   queues cause 1 at VIF1 completion (`queueCompletedDmacCause`
   sites for ch 0/1/2/SPR exist), drained via
   `drainCompletedDmacHandlers` → `dispatchIrq(true, 1)` →
   handler `0x382650` (9× in-window). INTC dispatch exists via
   `dispatchIrq(false, …)` (timer/alarm/VSync sites).
3. **The briefed sema words are wrong**: the thread waits on
   `*(s0+0x5AC8)` = `0x621528` and `*(s0+0x5ACC)` = `0x62152C`
   (`lw a0` in the delay slots @`0x3827dc`/`0x3827e4`, `jal
   func_423DE0`), both outside the `st` range and not the watched
   ids — hence `sema = 0`. Worse, `0x621508`/`0x62150C` hold
   **chain-head pointers** in this scene (rewritten per vsync,
   Table 9), not sema ids — the id filter could never match.
   Correct targets: range extended to `0x62152C`, ids from
   `0x621528`/`0x62152C`.

### Gaps / notes

- Whether the thread takes the `state == 5 → func_382AF0` branch
  is not logged (state is set to 5 each vsync; no call trace).
- `iPollSema` not hooked (brief named 4 calls); 8/16-bit stores
  not tapped (documented); `st`/`sema`/`irq` carry no GPR dump
  (brief-literal, T51-parity).
- Part-6 spend: builds + 1 fork commit/ff-push, 1 boot,
  0 retries. Command: `python3 local/research/E40/e40_boot.py
  --label e40g --wall 300 --snap 30 --src-from 1300 --src-to
  1304 --mpg-from 1300 --mpg-to 1304 --script "<E33 route>"`
  (PS2X_MPG_SRC_ARENAS unset).

## Recommendation (orchestrator decides)

The uploader-choice hunt moves to the chain CONTENTS: both
settled chains CALL `0x435bd0`; find who writes the second
chain's CALL ADDR (pre-1150 build, `0x6f`/`0x62` sets) and what
table entry selects `0x435bd0` over `0x434990`. Suggested next
lane (1 boot): corrected `st` range through `0x62152C` + sema-id
filter on `0x621528`/`0x62152C`, window on the build (pre-1150
bracket from Part-5), keeping this binary. Keep the Part-6
tracer (fix the two offsets when next touched).
