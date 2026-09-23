# E41 report — recomp CD reads + the DMA write that plants the render-chain CALL tags

Brief `local/muse/prompts/E41.md`. Tables + receipts; the orchestrator decides.
Read first: `AGENTS.md`, `local/AGENTS.local.md`,
`local/research/E40/REPORT.md` (Parts 3–7), `local/research/T51/REPORT.md`
§T51-5, `local/muse/prompts/T52.md` (line formats).

## Outcome

- **The four CALL ADDR words ARE written in-boot — by EE CPU stores,
  every even vsync from 1274 while SC is up: 185 `plant` lines, all
  `via=ee-store`, all `value=0x435bd0`.** This contradicts E40 Part-7's
  "never EE-written in 0–1299" — with the mechanism identified: E40's
  word watch compared RAW addresses and tapped the WRITE macros only,
  while the new watch folds the 0x00/0x20/0x30/0x80 mirrors and sits in
  `Ps2FastWrite*` below the macros. The miss is exactly E40 Part-7's two
  stated gaps (unfolded mirrors; inlined `FAST_WRITE` bypass). Which of
  the two fired is NOT discriminated (no pc/fn on the fast path) —
  recommended follow-up below.
- **CD side is fully logged in T52's format: 711 `cdread`, all
  `mode=sceCdRead`, zero of anything else** — no chain, no streaming, no
  unresolved, and **0 `cdsearch` / 0 `cdopen` / 0 `fioread`**: the game
  loads everything through raw sector reads, never searchfile or ioman.
  All 711 reads are raw ISO LBNs (`file=-` throughout: nothing ever
  registers a pseudo-LBN file). 491/711 funnel single sectors through a
  fixed staging buffer at `0x519c80`.
- **Phase split is clean**: title 594 reads / 3185 sectors, main menu 0,
  →SC 117 reads / 142 sectors (vsync 1254–1263, right after the i=1
  cross @~1238), SC settled 0 reads. Transition LBNs are raw-ISO
  `0x4bc3f–0x4ced2` + `0x5c3e6–0x5cc36` (table below).
- **Zero plants from any non-EE path** (CD, SIF DMA, IOP, libc, RPC,
  fio, GS, heap, font/VU/MC/pad stubs): the watch is proven live by the
  185 ee-store hits, so the silence elsewhere is meaningful. Every plant
  is unattributable to a CD read (`seq=-`): the tags are **re-stamped by
  the EE per frame, not planted by DMA/CD data**. E40's "loaded data"
  reading is corrected to: loaded once (before 1274), then re-stamped
  per frame by EE stores.
- Delivered: dev-only `PS2X_CD_READ_TRACE` (+`_FROM`/`_TO`, 40000-line
  cap) with `cdread`/`cdsearch`/`cdopen`/`fioread` + folded-mirror
  `plant` watch on the four words. 8 new unit tests; suite **537/537**
  (529 E40-tip + 8) flags-unset from the fork root. One fork commit,
  ff-pushed (runner-dir gate empty). No verdict.

## Commits

Fork `~/dev/PS2Recomp`, branch `ssx3`:

| Commit | Subject |
|---|---|
| `7d7bbc6` | [E41] CD-read log + host-side CALL plant watch (cdread/cdsearch/cdopen/fioread/plant) |

Base `9840542` (E40 Part-7 tip). Pushed `9840542..7d7bbc6`
(`git ls-remote fork ssx3` = `7d7bbc6…`); runner-dir gate
`git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner` empty. Suite
537/537 before commit and (rebuild) before push. **Gap: the fork commit
lacks the `Orchestrated-By` trailer** (caught after push; history not
rewritten per standing rules). The `[E41]` repo commit carries it.

## Diff summary

- `ps2xRuntime/include/ps2_e41_trace.h` (new): header-only dev-only
  tracer. `noteCdRead` (seq counter, gapless across the window),
  `noteCdSearch`/`noteFioOpen`/`noteFioClose`/`noteFioRead` (fd→path
  map), `notePlantRange` (folded `& 0x0FFFFFFF` overlap against the four
  fixed words, value read back post-write, 256 hits/word),
  `noteFastWrite` (vsync from the VBlank mirror), `noteVsync`,
  `configureForTest`/`clearForTest`. Name sanitizer maps whitespace
  only (`=` kept: `src=` values carry it by construction).
- `ps2_runtime_macros.h`: include + tap in all five `Ps2FastWrite*`
  (both the wrapped and straight paths) — the single chokepoint for
  ALL EE CPU stores (WRITE macros route through FAST_WRITE; inlined
  constant-address FAST_WRITE sequences land here too). Off = one
  relaxed atomic load per store.
- `EeScheduler.cpp`: `noteVsync(m_vsyncTick)` at the VBlankStart site
  (same line as the E3/E33/E36/E37 mirrors).
- `CD.cpp`: cdread+plant at `sceCdRead`/`ReadChain`/`StRead`/unresolved
  zero-fill; cdsearch+plant at `SearchFile`; plant-only at
  GetToc/ReadClock/TrayReq. `Stubs/SIF.cpp`: plant at SetDma loop +
  GetOtherData (range + recvdata descriptor). `ps2_iop_host.cpp`:
  writeGuest/zeroGuest. `LibC.cpp`: all eight ops. `Syscalls/FileIO.cpp`:
  cdopen/fioread+plant/close-drop. `Syscalls/Helpers/Runtime.h`:
  rpcCopy/rpcZero. `Syscalls/System.cpp`: Copy, kernel-word, OSD×2,
  ROM name. `GS.cpp` StoreImage. `ps2_runtime.cpp`: realloc memmove +
  three handler-install sites (fixed low-memory table, disjoint by
  construction, tapped anyway). `DMA.cpp` GetEnv, `Stubs/FileIO.cpp`
  fstat/stat/ioctl, `Pad.cpp` open/read, `Font.cpp` (glyph/kern copies,
  field helpers, flag/close stores), `VU.cpp` three copiers,
  `Compatibility.cpp` char-out, `MemoryCard.cpp` string/dir-table.
  `Ssx3Movie.cpp`/`MPEG.cpp` verified to perform no EE-RAM writes
  (guest reads / host-packet targets only) — no tap, cited.
- `ps2xTest/src/ps2_e41_trace_tests.cpp` (new, `Ps2E41Trace`, 8 tests),
  registered in `src/main.cpp`, listed in `ps2xTest/CMakeLists.txt`.

## Tests (`Ps2E41Trace`, all pass; suite 537/537 = 529 + 8)

Off-by-default; exact `cdread` format + seq 1,2; exact `cdsearch`;
`cdopen`→`fioread` fd join (+ unknown-fd `-`); mirror fold
(`0x2063B994` write logs under canonical `0x0063b994`, adjacent/far
silent); `Ps2FastWrite32` end-to-end with VBlank-mirror vsync;
window filters lines but seq stays gapless; sanitizer keeps `=`.

Test-debug notes (expectation fixes only, no runtime change):
mirror alias is `0x2063B994` (a `0x263B994` typo in the first draft
addressed low RAM and logged nothing — caught by the test);
negative-probe buffer must be full `PS2_RAM_SIZE` (16 MB write into an
8 MB buffer segfaulted once — caught immediately, fixed).

## Boot e41a (Boot A; Mac mini, E32-build @ `7d7bbc6`, runner SHA `b7e63b7a…c864` two matching reads, E33 vsync route, wall 300, snap 30, CD window 0–1400, `PS2X_SKIP_MOVIE=1`, rc 0 wall-bound 302.6 s, tick 1377, final frame `fnv1a=129073fb` = e40e/e40g SC-settled hash, lease released)

- Trace `cdread-e41a.txt` (copied in-repo, SHA
  `826c1e0a…587b7a27`): **711 cdread, 0 cdsearch, 0 cdopen,
  0 fioread, 185 plant**, 896 lines total (no cap cut). Max vsync in
  trace: 1366 (boot ran to 1377; 1367+ silent).
- Route identity: i=0/i=1 fired, i=2 (@~1391) never — same shape as
  E33a; transition reads start vsync 1254, just after the i=1 cross
  @~1238, corroborating the ms→tick phase anchors.

### Table 1 — reads per phase (anchors: start press @~620, cross#1 @~1238, SC snap ~1360)

| phase | reads | sectors | modes |
|---|---|---|---|
| title [0,620) | 594 | 3185 | sceCdRead only |
| main menu [620,1238) | 0 | 0 | — |
| → Select Character [1238,1360) | 117 | 142 | sceCdRead only |
| SC settled [1360,∞) | 0 | 0 | — |

All reads are raw-ISO (`file=-`); dest range `0x519c80–0xF2EA00`,
nowhere near the chain arenas. 491/711 reads target the single-sector
staging buffer `0x519c80` (boot reads start `lbn=0x105,0x106,…`
sequential). Transition dests: `0x519c80`, `0xBBE840`, `0xBC17C0`,
`0xEBFC00`, `0xEC7C00`.

### Table 2 — distinct LBN ranges, menu → SC transition (vsync 620–1360)

| lbn range | sectors | vsync |
|---|---|---|
| 0x4bc3f–0x4bc42 | 3 | 1254 |
| 0x4bc6e–0x4bc72 | 4 | 1255 |
| 0x4cd25–0x4cd29 | 4 | 1256 |
| 0x4cd3a–0x4cd48 | 14 | 1257 |
| 0x4cd81–0x4cd87 | 6 | 1258 |
| 0x4cda6–0x4cda7 | 1 | 1258 |
| 0x4cdc1–0x4cdc7 | 6 | 1259 |
| 0x4ce12–0x4ce22 | 16 | 1259 |
| 0x4cec9–0x4ced2 | 9 | 1260 |
| 0x4cf0a–0x4cf1e | 20 | 1260 |
| 0x5c3e6–0x5c3ee | 8 | 1260 |
| 0x5c445–0x5c44d | 8 | 1260 |
| 0x5c4ad–0x5c4b4 | 7 | 1260 |
| 0x5c547–0x5c54a | 3 | 1261 |
| 0x5c959–0x5c95f | 6 | 1263 |
| 0x5cc1b–0x5cc36 | 27 | 1263 |

All `mode=sceCdRead`, all `file=-`. Two clusters (`0x4bc–0x4cf`,
`0x5c3–0x5cc`): candidates for the T52 healthy-side diff. SC-settled
range table is empty (0 reads ≥1360).

### Table 3 — file names

None: 0 cdsearch, 0 cdopen, no registered `file=` on any read. The
game performs no `sceCdSearchFile` and no ioman opens/reads in this
route (a clean negative for the T52 join: there is no filename key on
the recomp side — join on raw LBN only).

### Table 4 — plant lines (all 185; condensed)

46 complete events on even vsyncs 1274–1364 (all four words,
`value=0x00435bd0`, `via=ee-store`, `seq=-`) + 1 partial at vsync 1366
(`0x63b994` only); nothing on odd vsyncs, nothing before 1274, nothing
after 1366. Per-word totals: `0x63b994`×47, `0x63bbe4`×46,
`0x63bea4`×46, `0x63c134`×46 (no per-word cap cut). No plant from any
other `via=`; no value other than `0x435bd0` (never `0x434990`).

Reading (no verdict): the 0x63b8 chain's CALL words are re-stamped
`0x435bd0` by EE stores every second vsync while SC is up — a per-frame
chain rebuild, not a DMA/CD plant. Even-only cadence plausibly
alternates with the unwatched 0x7085-set rebuild on odd vsyncs (E40
Part-5 alternation), and the 1274 start / 1366 stop bracket the settled
SC scene. E40 Part-7's 0 hits over 0–1299 stand explained (raw-compare
+ macro-only taps vs folded + fast-path taps); mirror vs inlined is
open.

## Gaps / notes

- `via=ee-store` cannot separate WRITE-macro stores from inlined
  `FAST_WRITE` stores, and the line carries no pc/fn (no ctx at the
  fast-write level) and no raw (unfolded) address — so mirror identity
  and storing function are both still open. Both are one small
  follow-up each (see Recommendation).
- Phase boundaries assume the E33 guest-ms→tick mapping holds on this
  build; corroborated by transition-read onset (1254 vs i=1 @~1238)
  and the SC-settled end hash, but not independently re-derived.
- One-off flakes, both green on rerun ×2: a VU0 codegen test failed
  once on `instructions.h` readability (CWD-dependent; passed before
  and after untouched), and the first post-fix suite run segfaulted in
  a new test (8 MB buffer, fixed same session).
- Fork commit `7d7bbc6` lacks the `Orchestrated-By` trailer (see
  Commits). Spend: builds as needed, 1 boot, 0 retries. E41-run 7.7 MB
  total; internal 28.3/200 GB; brief cap 3 GB.
- Exact commands:
  `cmake --build ~/dev/ssx3-work/E32-build -j8  # fork ssx3 @ 7d7bbc6`
  `env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT
  ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 537/537`
  `python3 local/research/E41/e41_boot.py --label e41a --wall 300
  --snap 30 --cd-from 0 --cd-to 1400 --script "<E33 route>"`
  `python3 local/research/E41/e41_analyze.py
  ~/dev/ssx3-work/E41-run/cdread-e41a.txt`

## Recommendation (orchestrator decides)

The storing function is one small lane away: add a **folded-address**
tap to the WRITE32/64 macros (they have runtime+ctx → pc/ra/fn +
GPRs, E40 `tagwrite` shape) and re-run the SC window. If it fires with
the plants' cadence, the path is macro stores via a mirror alias and
the pc names the builder (+ its table load, via the captured regs). If
it stays silent while `plant` still fires, the builder uses inlined
`FAST_WRITE` and the hunt moves to codegen (find the inlined store to
a `0x63Bx` constant/mirror in the chain-builder cluster). Either
outcome discriminates E40's two residual gaps. No further CD-side
capture is queued by this brief; the T52 join keys are Table 2's raw
LBN ranges.
