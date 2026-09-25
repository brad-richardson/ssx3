# CT1 — silent counters on the F1 fold (coverage, VU1 caps, INTC, overlay)

Worker: Muse Code, brief `local/muse/prompts/CT1.md`. Base fork `ssx3` `56a5e8a`,
worktree `~/dev/ssx3-work/CT1/PS2Recomp`, branch `ct1-counters` (one commit, local only,
no push). Runner `c098adc1…69d7235` (two matching SHA reads), suite 611/611.
Route I26-FAST, `PS2X_DETERMINISTIC=1`, `PS2X_SKIP_MOVIE=1` (dev-only), empty mc0/mc1,
`PS2X_SOUND=1`, paraLLEl (`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`,
`[gs-path]` = GB8/F1 line), `PS2X_MISSING_FUNCTION_POLICY=stop` (as F1).

Code change (default-off logging only, no behaviour change; `+66` in
`ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, runner dir untouched):
`PS2X_INTC_LOG=1` → `[intc:add]` per registration + `[intc:dispatch]` per dispatch call;
`PS2X_COVERAGE_TICK=<n>` → `[coverage:tick]` + the `[coverage:*]` lines at that vsync
(SIGTERM-stopped boots never reach the destructor print). Reused existing knobs:
`PS2X_GFX_STATS`, `PS2X_VU1_TRACE`, `PS2X_CD_READ_TRACE`, `PS2X_DIAG_REPORT_ALL=1`.

Boots (one mini slot each): B1 hit the 16 MiB log cap at t1842 (`[intc:dispatch]` is
~150 lines/vsync — DMAC drains per transfer, see Q4); B2 with a 64 MiB cap reached
`bound=target`, last_tick 2444, 90.8 s wall. All tables below are B2 (full route) unless
noted; B1's partial data agrees everywhere (same 7 `[intc:add]`, same 4 RPC pairs,
zero cap hits, 1 SLUSOVF header read).

## Q1 — the SLUSOVF.BIG overlay: probed once, never loaded, never executed

`DATA/CONFIG/SLUSOVF.BIG` (LBN `0x41bb5`, 833 sectors, 1,704,940 bytes) is a BIGF archive
(size field LE, entries BE, 2 files). Extracted in scratch only (`~/dev/ssx3-work/CT1/iso`,
never in git):

| File | Offset | Size | Contents |
| --- | --- | --- | --- |
| `overlay.dat` | `0x40` | `0x1903ac` (1,639,340) | relocatable MIPS ELF (`e_type=1`, `EM_MIPS`, flags 5900/mips3) |
| `config.dat` | `0x1903ec` | `0x10000` (65,536) | opaque bytes (no magic; likely DNAS auth blob) |

ELF sections (`llvm-readelf`, host):

| Section | Type | Address | Size | Notes |
| --- | --- | --- | --- | --- |
| `.text` | PROGBITS | `0x100000` | `0x7e8b0` | ~519 KB EE code |
| `.data` | PROGBITS | `0x17e900` | `0x9ba18` | ~633 KB |
| `.rodata` | PROGBITS | `0x21a380` | `0x173f0` | ~95 KB |
| `.heap` | PROGBITS | `0x231780` | `0x28000` | |
| `.rel.text/.rel.data/.rel.rodata` | REL | — | 12,271 / ~1.3k / ~0.4k entries | full relocation |
| `.symtab` | SYMTAB | — | 3,218 symbols (2,088 GLOBAL) | |

Symbols name it: the **DNAS/online module** — `_DirtyDnasRel*`, `sceDNAS2*`,
`SSL*/RSA/BN/des_*` (crypto), `sceLibnet*`/`sceInsock*`/`inet_ntop*`/socket code.
Relocations import EE stubs (`GetThreadId`, `ChangeThreadPriority`, `memset`, …).

CD reads on the route (1,583 `cdread` lines, all raw-LBN `sceCdRead`; no `cdsearch`/`cdopen`
— the game reads by LBN through its own table):

| Extent | Reads | Detail |
| --- | --- | --- |
| SLUSOVF.BIG `0x41bb5–0x41ef5` | **1** | vsync 52, LBN `0x41bb5` (first sector = BIGF header/TOC), 1 sector, dest `0x009d6f80` |
| BANKS.INF `0x41b98` (positive control) | 2 | vsync 230 + 1554, dest `0x00519c80` — AU9's override loads banks on this route |

The vsync-52 read is one of ~20 single-sector header probes across many archives in a
boot-time scan — not a load: sectors 2–833 (all of `overlay.dat`) are never read, so there
is no overlay load address. Execution never enters it either: Q2 `targets=0`, and with
`policy=stop` any missing-target hit would have aborted the boot (it reached t2444).

Loader (main ELF, recompiled code; all labels unknown, addresses only): `0x256188` passes
`data/config/slusovf.big` (str @ `0x4803d0`) to `0x3DED50`, reached via
`0x232328 → 0x2282d0 → 0x256188`; `0x256258` passes `OVERLAY.DAT` (str @ `0x4803e8`) to
`0x3DF748` (buffer/size consts `0x195000`/`0x4a2ee0`), reached via `0x1b55b0 → 0x1b6288`
and `0x17b1b0 → 0x2560b0`. The route never calls them (no payload reads).

Verdict: the fold's route does not reach un-recompiled overlay code. `extra_function_starts`
needs nothing for this route. (The online menu path that would load it is out of scope.)

## Q2 — coverage: zero missing targets, zero unknown syscalls

`[coverage:tick] vsync=2400` print from B2 (also the first-ever read of these counters on a
fold boot):

```
[coverage:missing-functions] targets=0
[coverage:unknown-syscalls] ids=0
[coverage:unhandled-rpcs] pairs=4
```

Missing-target table (with caller PC): empty — zero `[guest-branch:missing-target]` lines
with `PS2X_DIAG_REPORT_ALL=1`, and `policy=stop` would abort on the first hit.
Verdict: close review suspect 3 for this route; add "coverage line read" to device gates
(the `PS2X_COVERAGE_TICK` env makes it available without clean exit).

## Q3 — VU1 cap hits: zero on the full route

2,447 `PS2X_GFX_STATS` lines (vsync 0–2444), **all `vu_exhausted=0`**; no `vu1_trace.log`
was created (first write happens on the first exhausted program). Totals:
1,091,636 VU1 programs, 1,248,072,605 VU1 cycles, max single program 27,360 cycles
(vsync 1745, race start — 42% of the 65,536 budget). Per-vsync capped-program table: empty.

Verdict: the E53-era "9 vsyncs with 33 capped programs" (todo) does not reproduce on the F1
fold — resolved somewhere in RR1/E57/AU9 or the route differs. Review suspect 2 needs no
Part-1 follow-up on this route. (The 27,360 max exceeds PCSX2's healthy race max of 23,540
(T48) — closest approach only, no truncation.)

## Q4 — INTC: game registers 5 (VIF1) and 7 (VU1); we never dispatch them

Registrations (`[intc:add]`, complete — same 7 in B1 and B2, none later):

| id | dmac | Cause | Handler | Dispatched? |
| --- | --- | --- | --- | --- |
| 1 | 0 | 10 (timer 1) | `0x3e4db8` | yes, match=1, 2,447× |
| 2 | 0 | 3 (VBlank end) | `0x31a490` | yes, match=1, 2,410× (+38 pre-registration match=0) |
| 3 | 0 | 2 (VBlank start) | `0x3825c0` | yes, match=2 with id 6, 2,385× (+25 match=1, +38 match=0 early) |
| 1 | 1 | 1 (VIF1 ch) | `0x382650` | yes, match=1, 4,754× (+1 match=0) |
| 4 | 0 | **5 (VIF1)** | `0x362340` | **never (0 dispatch rows)** |
| 5 | 0 | **7 (VU1)** | `0x3623a8` | **never (0 dispatch rows)** |
| 6 | 0 | 2 (VBlank start) | `0x3c1980` | yes, with id 3 |

Dispatch cause set (398,451 `[intc:dispatch]` rows; zero `masked=1` rows):

| dmac | Cause | Count | Matched | Source |
| --- | --- | --- | --- | --- |
| 0 | 2, 3, 10 | 2,448 / 2,448 / 2,447 | yes (above) | `EeScheduler` VBlank/timer sites |
| 1 | 8 (SPR from), 9 (SPR to) | 235,520 / 143,350 | 0 (no handlers) | `ps2_memory.cpp:2017` per-transfer drain |
| 1 | 2 (GIF ch) | 5,080 | 0 | `ps2_memory.cpp:2300,2725,2816` |
| 1 | 1 (VIF1 ch) | 4,755 | 4,754 | `ps2_memory.cpp:2316` |
| 1 | 5 (SIF) | 4,321 | 0 | `SIF.cpp:987` `sceSifSetDma` |
| 1 | 0 (VIF0 ch) | 2 | 0 | `ps2_memory.cpp:2309` |

Verdicts: (a) H10/review suspect 4 is **live** — the VIF1/VU1 handlers (pacing/double-buffer
logic) never run; (b) the review's "dispatchIrq is called only for VBlank 2/3 and timers
9–12" holds for the INTC half only — the DMAC half fires per completed transfer
(`drainCompletedDmacHandlers`, `ps2_runtime.cpp:2709`), ~160/vsync, almost all unmatched.

## Q5 — unhandled RPC: exactly the E56 four, one hit each

```
[coverage:unhandled-rpc] sid=0x80000211 function=0x1 hits=1
[coverage:unhandled-rpc] sid=0x237 function=0x0 hits=1
[coverage:unhandled-rpc] sid=0x534e44 function=0x0 hits=1
[coverage:unhandled-rpc] sid=0x80000006 function=0xff hits=1
```

Live `[IOP/RPC trace:unhandled]` lines (compiled in) add caller PCs: `0x40c34c`, `0x3f6a04`,
`0x3c0bc4`, `0x42b0e8` respectively. Verdict: no new pairs vs E56 on the fold — the five
newly loadable files (AU9 row 6) introduce no new unhandled RPC traffic on this route.

## Gaps and recommended next actions

1. DMAC-8/9 volume (~155 SPR completions/vsync, all unmatched) is reported as observed;
   whether that is genuine guest scratchpad streaming or a drain artifact (e.g. zero-length
   transfers queueing causes) needs a MADR/QWC peek — one counter, not briefed here.
2. `PS2X_COVERAGE_TICK`/`PS2X_INTC_LOG` live only on branch `ct1-counters` (local, unpushed);
   fold or drop per orchestrator call. The `[intc:dispatch]` line is ~150 rows/vsync — future
   boots should keep the 64 MiB log cap or sample it.
3. `596× [drop] stub/sceSifDmaStat error -` and `35× [WARN] Unknown video format` observed;
   pre-existing, not CT1 questions.
4. Overlay verdict is route-scoped (I26-FAST single-race). The Multi Play/Online menu path
   (enabled in our build, greyed out in PCSX2) is the one that would load `overlay.dat` —
   untested.

## Receipts

- Build: `56a5e8a` + `ct1-counters` (66-line logging diff), Release/HB-clang,
  `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3` (`register_functions.cpp`
  `8ea8ed43…62d688a3` ✓), `BUILD_TEST=ON`, runtime/aggressive logs OFF, diag taps OFF,
  det-hash OFF, `GS_SHADOW_PARALLEL=ON`, parallel-gs `963cb57`. Configure rc=0, build
  rc=0, suite **611/611 rc=0**. Runner `c098adc1dc5cde0fe6d22b794164f233cf52508846e7ea86f1ea7409d69d7235`
  (two reads match).
- B1: `bound=log_cap`, last_tick 1842, 59.6 s. B2: `bound=target`, last_tick 2444, 90.8 s,
  `gs_fatal=null`, `[gs-path]` = F1 line. Pins (ISO/ELF/codegen SHA) verified twice per boot.
- Scratch: `~/dev/ssx3-work/CT1/` (build, `ct1_boot.py`, `run/B1`, `run/B2`, `iso/` with
  extracted BIGF members — game data stays in scratch, not in git). Disk 109.5/200 GB.
- Runner-dir guard: `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner` empty (change
  is in `src/lib/Kernel/` only). Never pushed.
- Budgets: 1 build / 1, 2 boots / 2, ~1 h of 2 h.

Exact commands:

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/CT1/PS2Recomp -b ct1-counters fork/ssx3  # 56a5e8a
# edit ps2xRuntime/src/lib/Kernel/EeScheduler.cpp (+66: PS2X_INTC_LOG, PS2X_COVERAGE_TICK)
cd ~/dev/ssx3-work/CT1
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)
COPYFILE_DISABLE=1 bsdtar -xf "/Users/brad/dev/ssx3-work/E32-inputs/SSX 3 (USA).iso" -C iso "DATA/CONFIG/SLUSOVF.BIG"
python3 ct1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label B1 --stop-tick 2400 --coverage-tick 2400
python3 ct1_boot.py --runner build/ps2xRuntime/ps2EntryRunner --label B2 --stop-tick 2400 --coverage-tick 2400
```
