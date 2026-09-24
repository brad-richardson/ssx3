# N8D7M5 — executed FBP112 word provenance on the Mac (OpenCode Go)

**State: VALIDATED Mac-only. One incremental Release build, one flag-OFF suite
(585/585), one OFF + one ON CPU replay through marker2050 on lease slot 1
(released). No device/Android/iOS action, no push. The orchestrator gates.**

Fork commit `a8cfefa` (`Orchestrated-By: opencode`); binary
`d06ff1aa…0b77f`. GB7C5's replay had exited before any clang/ninja or mini
replay from this worker (its PID 79634 gone, no build procs at configure).

## 0. Pins

| Item | Value |
| --- | --- |
| Fork worktree | `/Users/brad/dev/ssx3-work/N8D7L/PS2Recomp`, branch `n8d7l-oracle`, diagnostic commit `a8cfefa` (base `d1ba1d4`, N8D7L gate PASS) |
| Scratch | `~/dev/ssx3-work/N8D7M5/` (created; empty until build) |
| Input stream | `~/dev/ssx3-work/N8D4/n8d4.gs`, SHA-256 `38ace1a3e8e99e1d5d7d24e611dfa9cedd6e6d44a45c800223991401cd93f97d` (verified, two-read equivalent: single read 2026-09-24, second read at replay time) |
| N8D7L baseline | ON tick2050 `present=7bf5c012` (parallel), `off.hashes==on.hashes` SHA `f038cde9…`, PPM SHA `8c85489e…`, oracle controls §3 |

## 1. Queue/execution order (observed source lines)

CPU replay is the only mode this diagnostic uses
(`PS2X_GS_REPLAY_BACKEND` unset → `queued=false`,
`ps2_gs_replay_tests.cpp:170-171`; `setQueueEnabled(true)` at `:215-216`
not taken, so `GS::m_worker==nullptr`).

| Fact | Observed line |
| --- | --- |
| Kind-1 enqueue happens ONLY when a worker exists | `gs_frontend.cpp:931` `if (m_worker && !t_inGsWorker)` → enqueue `:935-939`, else synchronous body `:942-1048` |
| Kind-5 (native upload) same split | `gs_frontend.cpp:1118-1131` enqueue vs direct `:1132-1140` |
| Kind-7 (clear) is synchronous in BOTH modes | `gs_frontend.cpp:2063-2074`: queued path enqueues an RPC **and waits** (`rpc->wait()`), direct path `:2075-2078` |
| `drainQueue` is a provable no-op without a worker | `gs_frontend.cpp:178-183` (`if (!m_worker …) return`) |
| Marker handling drains then stores the tick | `ps2_gs_replay_tests.cpp:327-328` (`gs.drainQueue(); regs.vsyncTick.store(tick)`) |
| Executed-packet counter increments ONLY at execution | `gs_frontend.cpp:947` (kind-1, after the queue check) and `:1133` (kind-5); enqueue paths never touch `m_submitCount` |
| Replay ordinal == executed index (CPU-direct) | kinds 1+5 each do exactly one `fetch_add` at execution; kinds 2/3/4/6/7 never do; replay `packets` (`:292`,`:430`) counts exactly kinds 1+5 in stream order → lockstep |

**Execution-order witness for every logged word:** the tap snapshots
watched LE32 words from the replay-owned `vram[]` (the same bytes
`GS::init` hands the CPU backend; `WriteVramUnlocked` writes land there
synchronously via `GSMem::WriteCT32` page/block/column tables,
`ps2_gs_memory.cpp:223-226`) immediately before and after the harness
call, and reads `gs.submitCount()` after. Because `m_worker==nullptr`,
the call cannot enqueue; because `m_submitCount` advanced by exactly one,
the packet executed between the two reads. No `drainQueue` is added
(zero drains over all 862,993 packets); the N8D7M4-proposed bare
before/after read is therefore valid **in CPU-direct mode only** and
would be invalid for a parallel-backend replay (queued, `:929-939`).

Operation-kind attribution (draw/transfer/clear) cannot be read from the
harness: a kind-1 packet may draw (`DrawPrimitive` → `WritePixel` →
`WriteVramUnlocked`, `gs_cpu_backend.cpp:688,826,983,988`), transfer
(`UploadImage` `:1485` / `PerformLocalToLocalTransfer` `:1592` → same
sink `:1528-1620`), or touch no watched word at all. Four entry-point
counters (test-only, static atomics, default-OFF flag) disambiguate:
a changed word is attributed to whichever of draw/transfer/clear
advanced during that packet (`draw+transfer` if both).

## 2. Diagnostic design (written, not yet built)

- `PS2X_GS_REPLAY_WORDS=0xE0000,0xE0534,…` (≤8 GS-storage byte addrs,
  4-aligned, `<PS2_GS_VRAM_SIZE`); unset/empty = zero behavior change.
  Invalid list = test failure (no silent wrong-watch).
- Kind-1/5/7 branches: snapshot words + op counters before, run op,
  snapshot after, `submit=gs.submitCount()`; emit
  `[n8d7m5] word idx=<replay ordinal> submit=<executed> tick=<tick>
  path=<1..3|native|clear> kind=<draw|transfer|clear|combo|none>
  addr=<hex> old=<hex> new=<hex>` **only on change**.
- End of stream (== post-marker2050; N8D4 capture ends at marker 2050):
  `[n8d7m5] final addr=<hex> word=<hex>` for every watched addr.
- Emission cap 4096 lines with truncation note (trace ≪8 MiB by
  construction: 6 addrs × finite transitions).

## 3. Candidate addresses (6, three VRAM pages)

All are N8D7L-validated literals (fork-table oracle == G43 input on this
stream, 448/448; Mac words observed `replay-excerpt.txt:14`). Mac tile
counts from the same receipt (`:5`). Odin RGBA column is the N8D4 viewed
image (`REPORT.md` §Viewed regions: black/sparse), not a word claim.
Page = byte>>13.

| # | GS byte | Pixel | Tile (Mac cnt) | Mac word (this stream) | Page | Odin RGBA region |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `0x0E0000` | (0,0) | 0 (256) | `0x00260803` | 0x70 | black (HUD corner frag) |
| 2 | `0x0E0534` | (31,0) | 1 (256) | `0x00260802` | 0x70 | black |
| 3 | `0x0E0040` | (0,2) | 0 (256) | `0x00260804` | 0x70 | black |
| 4 | `0x0E2000` | (64,0) | 2 (256) | `0x00260802` | 0x71 | black |
| 5 | `0x0F0000` | (0,32) | 32 (256) | `0xFF230401` | 0x78 | black |
| 6 | `0x0F2000` | (64,32) | 34 (256) | `0x00604400` | 0x79 | black |

Excluded: N8D7M4 row 4 (`0x1BFFF4`, tile 447 count 0 — weak/dark,
page-extent only) and row 7 (`0x0E1FFC`, odd-y non-census — read-path
check only). No row is nonzero-at-capture-start until the trace proves
it: the FIRST transition per addr must be `old==0x00000000` or the row
is flagged weak (already-nonzero) in the table, never silently kept.

## 4. Word/packet table (from ON trace, `trace-excerpt.txt`)

All six watched words change; every first transition is `0x00000000→nonzero`
(no weak rows). Full trace: 1980 transitions (1706 draw, 274 transfer,
0 clear — the stream has zero kind-7 clears; no `kind=none`, no truncation).
Every line satisfies `submit==idx+1`, tick≤2050, monotonic idx
(`check-result.json`: PASS). First/last executed writes per address:

| Addr | First executed write (idx/submit/tick/path/kind/old→new) | Last executed write ≤2050 (old→new) | Post-marker2050 |
| --- | --- | --- | --- |
| `0x0E0000` (p0x70) | 5223/5224/257/3/draw `0→0xa88b60` | 861291/861292/2049/3/draw `0x260703→0x260803` | `0x260803` |
| `0x0E0534` (p0x70) | 5223/5224/257/3/draw `0→0xa88b60` | 861291/861292/2049/3/draw `0x270903→0x260803` | `0x260803` |
| `0x0E0040` (p0x70) | 5223/5224/257/3/draw `0→0xa88b60` | 854440/854441/2044/3/draw `0x240703→0x260703` | `0x260703` |
| `0x0E2000` (p0x71) | 5223/5224/257/3/draw `0→0xa88b60` | 852725/852726/2042/3/draw `0x140607→0x260a04` | `0x260a04` |
| `0x0F0000` (p0x78) | 5223/5224/257/3/draw `0→0xa88b60` | 861291/861292/2049/3/draw `0xff230501→0xff230401` | `0xff230401` |
| `0x0F2000` (p0x79) | 460/461/92/3/transfer `0→0xea000000` | 477762/477763/1768/3/draw `0xa87601→0xb17d00` | `0xb17d00` |

Changed words span four VRAM pages (0x70/0x71/0x78/0x79). The stream therefore
contains executed FBP112 writes to all six probed words on the Mac CPU replay,
via both draw and host→local transfer paths, up to tick 2049.

## 5. Validation (done)

1. Incremental Release build of `ps2x_tests` (`build.log`, 322 targets,
   exit 0; only warning is ld duplicate-library, also present pre-change).
2. Flag-OFF suite exit 0, **585/585** (`suite.log`; must run from the fork
   worktree — one unrelated VU0 test reads `instructions.h` by relative path).
3. OFF control CPU replay (slot 1): `mode=direct backend=cpu`,
   862993/11499/25485/2050/0/0/41 — counts identical to N8D4; tick2050 row
   `vram=d7b84050 priv=6621fe06 present=a1834096` byte-identical to the N8D4
   `cpu.hashes` baseline; zero `[n8d7m5]` lines (flag-off clean).
4. ON CPU replay (`PS2X_GS_REPLAY_WORDS` = six §3 addrs): same counts,
   `off.hashes==on.hashes` byte-identical, tick2050 PPM SHAs identical
   (`c39c40e0…`), 1980 trace lines (< 4096 cap), 6 finals, no truncation.
5. `check.py` → `check-result.json` verdict **PASS** (10/10: input SHA,
   runner guard empty, suite, ON/OFF hashes+PPM, OFF==N8D4 CPU2050,
   mode=direct both, trace ordering+witness, finals, ≥2 pages).

Caps honored: 1 build + 1 suite + 2 CPU replays (each ≪600 s); trace
~200 KiB (≤8 MiB); receipts ~30 KiB text; scratch = build (~1 GiB) +
logs/PPMs (few MiB); runner-dir diff vs `14b1e5cb` empty. No speed claim.

## 6. Gaps / handback

- CPU-vs-parallel backend divergence (consistency info, not a gate): CPU
  finals at `0xE0534/0xE0040/0xE2000/0xF2000` differ from the N8D7L
  parallel-snapshot controls in low bytes (e.g. CPU `0x260803` vs parallel
  `0x00260802` at `0xE0534`); `0xE0000` and `0xF0000` agree exactly. This
  matches the known CPU-vs-parallel present difference (`a1834096` vs
  `7bf5c012`). Provenance (which executed packets/ticks/kinds touch each
  word) is a stream fact and stands; word *values* are backend-specific.
- No parallel-backend word tap exists (would need the bounded drainQueue
  design; not built — CPU-direct needed none).
- Recommended next action (orchestrator decision): the §4 table supplies
  the executed-packet inputs the S-STREAM/S-MISSING gate needs — six
  FBP112 words with proven Mac-stream writes across four pages, latest at
  tick 2049. A same-run Odin capture+snapshot can now beat exact
  packet/tick/kind rows instead of sparse-image impressions.

## 7. Receipts

- ssx3 (this dir): `REPORT.md`, `check.py`, `check-result.json`,
  `trace-excerpt.txt` — commit `[N8D7M5]`,
  `Orchestrated-By: opencode`, no push.
- Scratch `~/dev/ssx3-work/N8D7M5/`: build/suite/replay logs, trace,
  PPMs (not committed).
- Fork: `[N8D7M5]` commit (3 files, test-only + counters), no push.
