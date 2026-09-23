# E42 report — the EE function that re-stamps the chain CALL tags (recomp)

Brief `local/muse/prompts/E42.md` (+ orchestrator narrowing 2026-09-23:
keep minimal — one boot confirming the recomp stamper is `sub_00364CD0`
@0x3651d8, never 0x365994 — then E43). Tables + receipts; the
orchestrator decides. Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/E41/REPORT.md`, `local/research/E40/REPORT.md` Part-6/7,
plus T53's PCSX2 stampers (0x434990 @pc 0x365994, 0x435bd0 @pc 0x3651d8,
both in `sub_00364CD0` ← `sub_00363C20` @0x363cf4, mode
`a1=(*(s3)&0x3C0)>>6`).

## Outcome

- **The recomp's stamper is `sub_00364CD0` @ the 0x3651d4 `sd` (pc at the
  store; T53's 0x3651d8 is the next instruction — same site), 50/50
  attributed hits, value always `0x435bd0`. `pc=0x365990` (the 0x434990
  site) fired 0×.** Caller `ra=0x00363cfc` on all 50 lines = return past
  the delay slot of the `jal` @0x363cf4 in `sub_00363C20` — the same
  caller T53 names on the PCSX2 side.
- **Path discriminated (E40 Part-7 gap closed): all 50 lines are
  `via=ee-store-macro` (WRITE-macro stores with full ctx), 0 lines
  `via=ee-store` (inlined FAST_WRITE).** The suppress guard held: no
  double-logging (exactly 1 line per store, proven by unit test).
- **Mirror discriminated (E40 Part-7 gap closed): all 50 raw addrs are
  the `0x30` alias** (`0x3063b990/0x3063bbe0/0x3063bea0/0x3063c130`).
  The builder stores the CALL packet through the uncached `0x30` mirror;
  E40's raw-compare word watch could never see it.
- **Value formation (codegen read): immediates, no table.** Set A
  (`0x3651b0–0x3651d4`): `lui $v0,0x43` + `addiu $v0,0x5bd0` +
  `lui $v1,0x5000` → `sd $v0,0($a0)` writes `0x50000000@(a0)` +
  `0x435bd0@(a0+4)`. Set B (`0x365968–0x365990`): same shape with
  `addiu 0x4990` → `0x434990@(v1+4)`. **There is no table base/index/
  stride behind the value and no index memory word to log** — site
  selection (mode) is the only state, and mode census is E43's brief.
- Delivered: E42 tracer rev (dladdr `fn/fn1` on the fast-write path,
  `pc/ra/a0–s7` + `fn=__func__` on the WRITE-macro path, shared
  256/word caps, one line per store). 5 new unit tests; suite **542/542**
  flags-unset from the fork root. One fork commit, ff-pushed
  (runner-dir gate empty, trailer present). One boot. No verdict.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `25cde0f` | [E42] CALL plant attribution: dladdr fn at fast-write tap + ctx at WRITE macros |

Base `7d7bbc6` (E41 tip). Pushed `7d7bbc6..25cde0f`
(`git ls-remote fork ssx3` = `25cde0f…`); runner-dir gate
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` empty. Suite
542/542 before commit and (incremental rebuild) before push.

## Diff summary

- `ps2xRuntime/include/ps2_e41_trace.h`: `isPlantWatched` lock-free
  fold pre-filter; `detail::ScopedFastSuppress` thread-local guard;
  `notePlantRangeX` (`extra` suffix; null keeps the E41 line format
  byte-identical, existing mirror test untouched); `resolveHostSym`
  (`dladdr` → `name+0x<off>`, `-` when stripped); `noteFastWriteSite`
  (`noinline`, `__builtin_return_address(0)` + best-effort level-up,
  raw `hra0/hra1` kept so a bad guess is checkable via `+off`);
  `notePlantCtx` (`raw/fn/__func__/pc/ra` + E40-shaped 24-reg dump,
  `via=ee-store-macro`, same VBlank-mirror clock as the fast path).
- `ps2xRuntime/include/ps2_runtime_macros.h`: all five `Ps2FastWrite*`
  call `noteFastWriteSite`; all five `WRITE*` macros compute
  `_e42plant` (one atomic + fold check when off), hold the guard across
  the inner store, and log `notePlantCtx` after (post-write read-back).
- `ps2xTest/src/ps2_e41_trace_tests.cpp`: 5 new `Ps2E41Trace` tests
  (mirror-fold pre-filter; dladdr self-resolution incl. null→`-`;
  guard silences fast-write tap; ctx line exact fields + 4 regs;
  WRITE32-macro probe logs exactly once with host fn/pc/ra); the
  existing fast-write test now asserts the E41 prefix + resolved `fn`
  (this build is not stripped) instead of an exact line.

## Tests (suite 542/542 = 537 E41 + 5 new, flags-unset, fork root)

```
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT \
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 542/542
```

## Boot e42a (Boot A; Mac mini, E32-build @ `25cde0f`, runner SHA
## `d803646f…f38a` two matching reads, E33 vsync route, wall 300, snap 30,
## CD window 1270–1300, `PS2X_SKIP_MOVIE=1`, rc 0 wall-bound 302.4 s,
## i=0/i=1 fired, i=2 never (same shape as E33a), lease released)

- Trace `cdread-e42a.txt` (copied in-repo, SHA `0869b38b…9685a`):
  **50 complete `plant` lines + 1 torn tail line** (wall kill
  mid-flush at vsync 1297: `plant vsync=1297 addr=0x00`, stated gap —
  the 50 complete lines stand). 0 cdread/cdsearch/cdopen/fioread
  (none in-window by construction).
- 13 events on **odd** vsyncs 1273–1297, 4 words each (12 complete +
  torn tail). Parity vs E41's even-1274–1364 is run-to-run tick-phase
  variance (this run was killed mid-SC at ~1300 ticks; SC unsettled at
  kill, final-frame hashes differ) — cadence is every-2-vsyncs in both.
  No anomaly claimed beyond the phase note.

### Table 1 — attribution (all 50 complete lines)

| via | fn | pc | n | vsyncs | addrs | values |
|---|---|---|---|---|---|---|
| ee-store-macro | sub_00364CD0_0x364cd0 | 0x003651d4 | 50 | 1273..1297 (13) | 0063b994,0063bbe4,0063bea4,0063c134 | 00435bd0 |

`fn1=-` 50/50 (macro path carries no host-level-up by design);
`ra=0x00363cfc` 50/50; `pc=0x365990` 0/50; `value != 0x435bd0` 0/50;
`via=ee-store` 0/50. Per-word: `0x63b994`×13, `0x63bbe4`×13,
`0x63bea4`×12, `0x63c134`×12 (+ torn `0x63bea4` tail).

Sample (first event, vsync 1273; all 13 events byte-identical modulo vsync):

| vsync | addr | raw | a0 | s2 | s3 |
|---|---|---|---|---|---|
| 1273 | 0x0063b994 | 0x3063b990 | 0x3063b990 | 0x00000000 | 0x0085ab4c |
| 1273 | 0x0063bbe4 | 0x3063bbe0 | 0x3063bbe0 | 0x00000001 | 0x0085ab7c |
| 1273 | 0x0063bea4 | 0x3063bea0 | 0x3063bea0 | 0x00000002 | 0x0085abc4 |
| 1273 | 0x0063c134 | 0x3063c130 | 0x3063c130 | 0x00000004 | 0x0085ab64 |

(a1=a2=a3=0, v0=v1=0x50000000, s0=0, s1=1 on all 50.)

### Table 2 — register constancy over the 50 macro-path hits

| reg | distinct | values |
|---|---|---|
| a0 | 4 | per-site tag base (0x30 alias) |
| a1/a2/a3 | 1 | 0 (packet words, consumed before the store) |
| v0/v1 | 1 | 0x50000000 (low half of the sd pair) |
| t0 | 1 | 0x00069cd0 |
| t1 | 4 | per-site tag base (mirrors a0) |
| t2 | 1 | 0x00000180 |
| s0/s1 | 1 | 0 / 1 |
| s2 | 4 | 0,1,2,4 (site loop index) |
| s3 | 4 | 0x0085ab4c,0x0085ab64,0x0085ab7c,0x0085abc4 (per-site descriptors) |
| s4/s5 | 1 | 0x008095f0 / 0x01fffcc0 |
| s6 | 4 | 1,2,3,4 (1-based site counter) |
| s7 | 3 | 0x00000001,0x00000002,0x00000018 |
| pc/ra | 1 | 0x003651d4 / 0x00363cfc |

### Table 3 — value formation (codegen read, `sub_00364CD0_0x364cd0.cpp`)

| Site | Instrs | Value | Base / index × stride | Index source at store |
|---|---|---|---|---|
| A @0x3651d4 `sd $v0,0($a0)` | `lui $v0,0x43; addiu $v0,0x5bd0; lui $v1,0x5000; dsll32 $v0; or $v0,$v0,$v1` | `0x435bd0@(a0+4)` | immediates only — no table | n/a (mode selected the site upstream) |
| B @0x365990 `sd $v0,0($v1)` | `lui $v0,0x43; addiu $v0,0x4990; lui $t4,0x5000; …` | `0x434990@(v1+4)` | immediates only — no table | never taken in-boot |

Store addr `a0` = `lw 0xF0(sp)` per iteration (stack-passed tag base,
0x30 alias). The brief's "index memory word" does not exist at the
value level; the mode word (`*(s3)&0x3C0)>>6`, T53) selects the site —
its census is E43's brief, not a second E42 boot (per orchestrator
narrowing: one boot only).

## Gaps / notes

- Torn tail line (kill mid-flush) — cosmetic, counted as `other`.
- `fn1` is `-` by construction on the macro path; the inlined
  (`ee-store`) path that would exercise dladdr `fn/fn1` never fired
  in-boot (its unit test proves the mechanism; symbols resolve —
  this build is not stripped: `nm -g` shows 9442 `sub_` symbols).
- This run reached only ~1300 ticks at the wall kill (slower than
  e41a's 1377 — extra per-store taps on a diagnostic build; not a
  speed number, never quoted as one). Window 1270–1300 fully covered
  up to the kill edge.
- Spend: builds as needed, suite ×2, 1 boot, 0 retries. E42-run 7.6 MB
  total; brief cap 2 GB.
- Exact commands:
  `cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ 25cde0f`
  `env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 542/542`
  `python3 local/research/E42/e42_boot.py --label e42a --wall 300
  --snap 30 --cd-from 1270 --cd-to 1300 --script "<E33 route>"`
  `python3 local/research/E42/e42_analyze.py
  ~/dev/ssx3-work/E42-run/cdread-e42a.txt`
  (`<route>` = E33 script string.)

## Recommendation (orchestrator decides)

E42's question is answered: recomp stamper = `sub_00364CD0` @0x3651d4
(set A, `0x435bd0`), never set B — matching T53's PCSX2 side exactly,
via WRITE-macro `sd` through the `0x30` mirror. No second E42 boot
needed (value is immediate-formed). Hand mode census to E43 as briefed.
