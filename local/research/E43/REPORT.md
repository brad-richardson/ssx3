# E43 report — who submits the mode-6 draw records (recomp side)

Brief `local/muse/prompts/E43.md` (+ orchestrator refocus 2026-09-23:
per-call h394 log at `0x362f68` over settled vsyncs to separate
"different input items" vs "different hash/bucket", census kept).
Tables + receipts; the orchestrator decides. Read first: `AGENTS.md`,
`local/AGENTS.local.md`, `local/research/T53/REPORT.md`,
`local/research/E42/REPORT.md`, `local/research/E41/REPORT.md`,
T54 (PCSX2 settled: 6 records/vsync — 4 mode-3 `w0=0xcc` @`0x85ac24..`,
2 mode-6 `w0=0x1b0` @`0x85aabc`/`0x85aaac`; mode-6 records written by
stores @`0x394fdc–0x394fe8` in `func_394ED0`, called from
`sub_00362DE8` @`0x362f68` with `(a0=s6, a1=s1, a2=hash)`).

## Outcome

- **Census: the recomp walker NEVER walks a mode-6 record — transition
  and settled.** `sub_00363C20` @`0x363cf4` walks exactly 4 mode-3
  records/vsync (`w0=0xcc` @`0x85ab4c/7c/c4/64`, `wmode==mode` on all
  200+324 drecs lines); the second `func_364CD0` caller
  (`sub_00364360` @`0x364460`) makes 3 mode-0 calls/vsync with
  `s3=0x61ba60` (struct, not draw records). PCSX2 settled walks
  4 mode-3 + 2 mode-6. Divergence confirmed in-window, both windows.
- **Hypothesis (B) is dead for the fold: the recomp's hash is bit-exact.**
  Independent python reimplementation of the `0x362f00–0x362f64` fold
  (xor, sra 8/16/24, sll 5, addu, 32-bit wrap throughout) matches all
  **10280/10280** logged `(w0..w3, hash)` pairs. No 32/64-bit
  shift/sign semantics bug in this path.
- **Hypothesis (A) stands: the input item stream has no mode-6 items.**
  All 10280 h394 input words have `w0 ∈ {0x0c, 0x30, 0xcc}` —
  **zero `w0=0x1b0` rows**. Bucket output `w0` mirrors input `w0`
  (join: `0x85aabc←0x30` ×29, `0x85ab34←0xcc` ×29), so a `w0=0x1b0`
  bucket record requires a `w0=0x1b0` scratchpad item that never arrives.
  The slots that hold mode-6 on PCSX2 (`0x85aabc`/`0x85abac`) receive
  mode-0 items here instead.
- **Bucket mechanics work**: 12 hash values → 12 bucket rets
  (`0x85aaXX`, stride `0x18`); `stores=1` exactly once per
  (tick, bucket) (532 groups, all single) = per-frame refill with
  same-frame dedup; each of the 112 scratchpad items (`s1` stride
  `0x80`) is hashed twice per vsync (224 calls/tick).
- **Producers: only `func_394ED0`'s own stores** (4068/4096 dprod:
  pcs `0x394fb4/d8/dc/e0/e4/e8/ff4`) **plus 28 delay-slot `sw`s from
  `sub_00362CC8` @`0x362d14`** (`sw $v1,0x1480($v0)` → `0x85aa70`
  head word); **zero fast-path lines** (no inlined producers missed).
  Modes seen in bucket pages: 0,2,3,4,5,7,8,9,10,11,15 — never 6.
- Delivered: E43 tracer rev 1 (drec/drecs/dprod/h394) + rev 2 (three
  Boot-A-found fixes). 9 new unit tests; suite **551/551** flags-unset
  from the fork root. Two fork commits, ff-pushed (runner-dir gate
  empty, trailers present). Two boots (budget). No verdict.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `e4083c1` | [E43] Draw-record census + h394 hash-call log + mode-6 producer watch |
| `a932aff` | [E43] Boot-B fixes: scratchpad-aware record reads, per-source drec, h394 cap 16K |

Base `25cde0f` (E42 tip). Pushed `25cde0f..a932aff` in two ff-pushes
(`git ls-remote fork ssx3` = `a932aff…`); runner-dir gate
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` empty both
times. Suite 549/549 at rev 1, 551/551 at rev 2 (rebuild before push).

## Diff summary (rev 1 + rev 2)

- `ps2xRuntime/include/ps2_e43_trace.h` (new): dev-only tracer behind
  `PS2X_E43_TRACE` (+`_FROM`/`_TO` census/producer window,
  `PS2X_E43_H394_FROM`/`_TO` default 1270/1400,
  `PS2X_E43_PROD_MODE` default 6). `drec` (per-tick per-source per-mode
  counts, flush-on-advance), `drecs` (first 8 per (tick,mode,source)
  with `wmode` self-check), `dprod` (learned 4 KB record-page watch,
  macro ctx + fast dladdr, suppress guard, 4096 cap), `h394`
  (`s1`/words/hash/`ret`/stores flag, 16384 cap). Vsync = shared E41
  VBlank mirror throughout.
- `ps2xRuntime/src/lib/ps2_runtime.cpp`: one-compare census tap at
  `dispatchGuestBranch` top (`target==0x364CD0`); h394 pre/post wrap
  around the synchronous `targetFn` call (`source==0x362F68 &&
  target==0x394ED0`, window-gated).
- `ps2xRuntime/include/ps2_runtime_macros.h`: all five `WRITE*` macros
  hold an E43 suppress guard across the inner store and report
  `noteWriteCtx` (producer page+mode test; h394 pc-range flag
  `[0x394FDC,0x394FEC)`); all nine `Ps2FastWrite*` sites report
  `noteProdSite` (dladdr fn, no ctx).
- Rev 2 fixes for three Boot-A findings: record reads go through the
  registered scratchpad backing for `0x70xxxx` (Boot A logged rdram
  filler `0x80000000`); drec counts are per dispatch source (Boot A
  hardcoded the walker and mixed the 3 mode-0 calls into its rows);
  h394 cap 1024→16384 (Boot A capped at 5 vsyncs).
- `ps2xTest/src/ps2_e43_trace_tests.cpp` (new, `Ps2E43Trace`, 9 tests),
  registered in `src/main.cpp` + `CMakeLists.txt`: off-by-default;
  drec aggregation/flush incl. X bucket; drecs first-8 cap with count
  integrity; page learn + mirror fold + macro-once-guard + mode filter;
  fast-path dladdr line; h394 arm/hash/ret/stores + window end;
  out-of-window silence; scratchpad backing read; per-source drec rows.

## Tests (suite 551/551 = 542 E42 + 9 new, flags-unset, fork root)

```
cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ a932aff
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT \
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 551/551
```

## Boots (Mac mini, E32-build, E33 vsync route, `PS2X_SKIP_MOVIE=1`, lease-claimed/released, rc 0)

| Boot | Rev | Wall/snap | Census+dprod window | h394 window | prod-mode | Result |
|---|---|---|---|---|---|---|
| e43a (A) | `e4083c1`, runner SHA `fadf2daa…9369` ×2 | 300/30, 301.6 s wall-bound | 1270–1300 | 1270–1400 | 6 | drec=56 drecs=200 **dprod=0** h394=1024 (**cap**) +1 torn; reach ~1297 |
| e43b (B) | `a932aff`, runner SHA `dff88c5d…88aa` ×2 | 360/30, 361.3 s wall-bound | 1355–1400 | 1355–1400 | any | drec=88 drecs=324 dprod=4096 (**cap**) h394=10280 +1 torn; reach ~1385 |

Traces in-repo: `e43-e43a.txt` (SHA `ee2f83eb…38f`), `e43-e43b.txt`
(SHA `149d880d…1b6f`). i=0/i=1 fired both boots, i=2 never (route shape
as E33a). Tick rate ~4.3/s wall (diagnostic build; never quoted as
speed — settled needed the 360 s wall).

### Table 1 — records walked per vsync (both boots; stable every vsync)

| src | mode | count/vsync | record addrs (drecs) |
|---|---|---|---|
| `0x00363cf4` (walker) | 3 | 4 | `0x85ab4c/7c/c4/64`, all `w0=0xcc`, `w1=0x01414294` const, `w2` per-site |
| `0x00363cf4` (walker) | 6 | **0** | — (PCSX2 settled: 2 @`0x85aabc`/`0x85aaac` `w0=0x1b0`) |
| `0x00364460` (`sub_00364360`) | 0 | 3 | `s3=0x61ba60` struct, words zero (not draw records) |

`mode!=wmode`: 0 rows (both boots). Walker `s3` strides `0x30`
(`…1c/34/4c/64/7c/94/b4/c4` across E42+E43); E42's stamp-descriptor
`s3`s (`0x85ab4c/64/7c/c4`) coincide with walked record bases.

### Table 2 — h394 hash calls (Boot B, settled 1355–1382, 10280 rows)

- 224 calls/vsync = 112 scratchpad items (`s1` stride `0x80`,
  `0x70000000…`) × 2 passes (every `s1` appears exactly 2×/vsync).
- Input `w0 ∈ {0x0c, 0x30, 0xcc}`; **`w0=0x1b0`: 0 rows**.
- 12 hashes (`10/30/33/50/53/66/70/91/95/b3/d0/f0`) → 12 bucket rets
  (`0x85aabc/aad4/aaec/ab04/ab1c/ab34/ab4c/ab64/ab7c/ab94/abac/abc4`);
  hash→ret is item-dependent (e.g. `0x10` → 4 buckets), stable per item.
- `stores=1`: 532 = exactly one per (tick, bucket) — first call per
  bucket per vsync writes, repeats skip (per-frame refill + dedup).
- Independent fold reimplementation matches **10280/10280** hashes.
- Sample (vsync 1355; all 46 ticks share the shape):

| s1 | w0 | w1 | w2 | hash | ret | stores |
|---|---|---|---|---|---|---|
| 0x70000000 | 0x30 | 0x00814884 | 0x2a0 | 0x66 | 0x85aabc | 1 then 0 |
| 0x70000480 | 0x0c | 0x01414294 | 0x2a0 | 0x10 | 0x85aaec | 1 then 0 |
| 0x70000580 | 0xcc | 0x01414294 | 0x220 | 0x50 | 0x85ab04 | 1 then 0s |
| 0x70001900 | 0xcc | 0x01414294 | 0x2a0 | 0xd0 | 0x85ab34 | 1 then 0s |

### Table 3 — bucket-record producers (Boot B, any-mode, 4096 lines = cap)

| fn | n | pcs | meaning |
|---|---|---|---|
| `sub_00394ED0_0x394ed0` | 4068 | `0x394fb4` (`sw`), `0x394fd8/e0/e4` (SDL/SDR → WRITE64), `0x394fdc/e4` (SDR), `0x394fe8/ff4` (`sw`) | the bucket-record stores themselves |
| `sub_00362CC8_0x362cc8` | 28 | `0x362d14` (`sw $v1,0x1480($v0)` delay slot) | bucket-list head word @`0x85aa70` |

`src=macro` 4096/4096, `src=fast` 0 → no inlined producers on bucket
pages. Lane modes present: 0,2,3,4,5,7,8,9,10,11,15 — **never 6**.
Join: bucket `w0` mirrors input `w0` (`0x85aabc←0x30`,
`0x85ab34←0xcc`), i.e. records are copied through, not recomputed.

### Table 4 — value/mode formation (codegen read)

| Site | Formation | Table/index? |
|---|---|---|
| `0x362f00–0x362f64` hash | `v0=w0^w1^w2^w3` (s1+0/4/8/12), sra 8/16/24 + sll 5 + addu/xor fold, `a2&0xFF` in the jal delay slot | no table; pure function of the 4 words (verified bit-exact) |
| `0x394fdc–0x394fe8` bucket writes | LDL/LDR record words from `(t3)` → SDL/SDR `v0/v1` @`(a1+0..15)` + `sw a2` @`(a1+16)` + `sw v1` @`(a1+20)` | copies input words; `w0` preserved ⇒ mode preserved |
| `sub_00362DE8` loop | `bnez $s7`, `s1+=0x80`, unconditional `jal func_394ED0` per item; `s3=v0(ret)` after | item count = `s7` entry value; items pre-staged in scratchpad |
| mode-6 decision | **upstream of `0x362f00`**: no `w0=0x1b0` item exists in the scratchpad list, so the `0x1b0`-stamping path in `func_394ED0`'s caller chain is never fed | next lane: who stages `0x7000xx` items (0x80 stride) and where `0x1b0` items are culled (E43 brief's VU0-visibility candidate stands) |

## Gaps / notes

- Boot-A defects (all fixed in rev 2, proven by new tests + Boot B):
  h394 words were rdram filler for scratchpad records; drec rows mixed
  sources; h394 capped at 5 vsyncs. Boot-A `dprod=0` (mode-6 filter)
  stands as the trigger for Boot B's any-mode fallback per the brief.
- Caps hit (by design, stated): dprod 4096 (any-mode floods heap
  pages), file total 14788 < 40000, one torn tail line per boot
  (wall-kill mid-flush).
- `s1` double-processing (2×/vsync) unexplained — two passes or two
  loops in `sub_00362DE8`; visible in the trace, not chased (no verdict).
- `sub_00362CC8`'s 28 head-word stores unexamined beyond the delay-slot
  attribution (bucket-list maintenance, presumably).
- Hash→ret is not a pure function of the hash (same hash → several
  buckets across items); the bucket picker reads more than `a2`
  (likely `a0=s6` base + probe) — not decoded, not needed for the two
  hypotheses.
- Spend: builds as needed, suites ×3 (549/549/551), 2 boots, 0 retries.
  E43-run 18 MB; brief byte cap not stated (E42-class: well inside).
- Exact commands:
  `cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ a932aff`
  `env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 551/551`
  `python3 local/research/E43/e43_boot.py --label e43a --wall 300
  --snap 30 --cd-from 1270 --cd-to 1300 --h394-from 1270 --h394-to 1400
  --script "<E33 route>"`
  `python3 local/research/E43/e43_boot.py --label e43b --wall 360
  --snap 30 --cd-from 1355 --cd-to 1400 --h394-from 1355 --h394-to 1400
  --prod-mode any --script "<E33 route>"`
  `python3 local/research/E43/e43_analyze.py
  ~/dev/ssx3-work/E43-run/e43-e43b.txt`

## Recommendation (orchestrator decides)

E43 separates the two hypotheses: **different input items (A)** — the
hash fold is bit-exact and the bucket machinery works, but no
`w0=0x1b0` item ever enters `func_394ED0`. Next lane: the scratchpad
item-list stager — who writes the `0x7000xx`/`0x80`-stride items that
`sub_00362DE8` loops over (112/vsync here), and where the `0x1b0`
class is dropped (object-type iteration vs visibility cull). Inputs:
h394 `s1` ranges per vsync above + bucket rets `0x85aaXX`.
