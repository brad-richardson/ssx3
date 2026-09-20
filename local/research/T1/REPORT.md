# T1 report — Park snapshot (PS2X_DIAG_PARK=1) + SIF/RPC tally + ladder_diff

Brief `local/muse/prompts/T1.md`. TOOLING brief: 2 fork commits
(emitter + unit tests, then the diff tool) + 1 proof boot + 1 void boot
(root-caused below). Tables, no verdicts. Stale-reading guard: P1
REPORT Part 28 (the 19k-line hand rebuild this automates) + Part 24
§P24-1f/g (drop-census conventions reused: site×reason grouping, args
stay log-only, census counts printed lines).

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`.
Base `e483d8d` (P1af SPR DMA fix — landed + pushed mid-session at
01:07 EDT, after my build dir was configured; my worktree build is
`e483d8d` + T1 files only). Peer lanes concurrent; shared only the
fork remote. `$R`-relative paths below unless noted.

Headline receipts: snapshot written on SIGTERM (`[diag:park]` at
`boot-t1-2.log:207275`, clean `rc=0` shutdown); JSON parses (111,491 B,
1188 hot pcs, 21 loads, 37 creates); D1 emitter-vs-miner on the same
boot = 97 exact / 8 tol-ok / 0 deltas; D2 two same-tree legacy boots =
116 exact / 11 tol-ok / 0 deltas; suite 436/436/0; 3 hand cross-checks
match.

## T1-0. Lease record

| Event | Value |
|---|---|
| Waits log | `$W/P1/run/t1-waits.log` (6 lines) |
| Start | `start 2026-09-20T05:13:54Z`, lease absent, `pgrep -x ps2EntryRunner` exit 1 |
| Void boot hold | `claim 05:13:57Z` – `release 05:15:32Z` (95 s, binary `d817806f`, stub runner inputs — §T1-5a) |
| Proof-boot wait | `wait1 05:32:38Z lease=P1ag pgrep=1` (5-min poll per the brief; 1 wait) |
| Proof hold | `claim2 05:37:44Z` – `release2 05:39:17Z` (93 s, binary `5e74041f`, full guest sources) |
| `adb` | Not used |
| Second boot | 1 void + 1 proof; the void boot never started the game (committed-stub `register_functions.cpp`, 438 B vs the 32 MB generated file). The re-boot is recorded here, not hidden |

## T1-1. Snapshot format (`ps2x-park-snapshot/1`)

One JSON + one human table, written to `$CWD/park-snapshot.json` +
`park-snapshot.txt` (`PS2X_DIAG_PARK_DIR` overrides the dir). Fields:

| Section | Content | Source |
|---|---|---|
| `threads[]` | id, status (+name), wait_reason (+name), wait_id, pc, ra, sp, entry, priority, scheduled (cumulative), chain (live $ra + stacked invocation pcs, innermost-first; no guest-stack walk) | live `snapshot()` + `thread(id)` |
| `semaphores[]` | id, count, max, init, waiters | live `snapshot()` + `semaphore(id)` |
| `sema_creates[]` | id, tid, pc, init, max (success-only; miner filters `ret>0` the same way) | create hook |
| `sema_wait_hist` / `sema_signal_hist` | `{id: {pc: n}}`, entry tallies covering exactly the `[diag:sema]` calls | wait/signal hooks |
| `hot_pc[]` | pc, count, first_ra, last_ra (cumulative, untruncated, count-desc) | dispatch hook |
| `drops[]` | site, reason, count (§P24-1f/g shape) | `recordDropCensus` after the mute check |
| `sif_rpc[]` | op, sid, fno, send_size, recv_size, tid, claimed, path (per-op map §T1-2) | SIF/RPC hooks, capped 4096 + overflow |
| `gs` | kicks, kicks_drawing, gif_packets, copy_regs (true counts) + dma_starts, gif_copies, gs_writes, vif_writes (live memory counters) | GS hooks + `PS2Memory` |
| `sched_counts` | `{tid: n}` cumulative (negative tids = invocation threads) | schedule hooks |

Example (proof boot, thread-3 row + drops + one call):

```json
{"id": 3, "status": 2, "status_name": "Waiting", "wait_reason": 2,
 "wait_reason_name": "Semaphore", "wait_id": 30, "pc": "0x423de8",
 "ra": "0x31aca4", "sp": "0x6188a0", "entry": "0x31ac60",
 "priority": 101, "scheduled": 152, "chain": ["0x31aca4"]}
{"site": "syscall/dispatchSyscallOverride", "reason": "KE_ERROR", "count": 6}
{"op": "call", "sid": "0x80000211", "fno": "0x1", "send_size": 16,
 "recv_size": 144, "tid": 3, "claimed": false, "path": ""}
```

## T1-2. Emitter (fork commit 1)

Env: `PS2X_DIAG_PARK=1` writes on SIGTERM (clean stop, `rc=0`
observed); `PS2X_DIAG_PARK_TIMEOUT_MS` writes once mid-run without
stopping (unset in proof). Counting is always-on P1c-style (one
increment per event); only the write is gated. All runtime hunks are
purely additive (zero removed lines — verified by diff audit).

| File | Change |
|---|---|
| NEW `ps2xRuntime/include/ps2_park_snapshot.h` | Registries, JSON/table renderers, SIGTERM install/poll, file writer (header-only, `ps2_log.h`-style, zero CMake changes) |
| `ps2xRuntime/include/ps2_log.h` | +40: in-memory drop census (`recordDropCensus` after the mute check, so the census equals the printed lines) |
| `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp` | +189: install before `run()` loop, poll at loop top, fill+write (`parkSnapshotWriteOnce`), sema create/wait/signal + sched tallies (7 sites) |
| `ps2xRuntime/src/lib/ps2_runtime.cpp` | +4: cumulative hot-pc tally at the dispatch hook |
| `ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp` | +74: LoadModule (3 exits), BindRpc (missing-client + claimed=prebound), CallRpc (missing-client + `handled`), SendCmd (claimed=handshake applied) |
| `ps2xRuntime/src/lib/gs/gs_frontend.cpp` | +11: true kick/gif/copy-reg counters outside the aggressive-log caps |
| `ps2xTest/src/ps2_runtime_kernel_tests.cpp` | +115: 2 tests (T1 tallies incl. a live scheduler sema round-trip; JSON/table schema incl. escaping) |

Claimed/unclaimed definitions (SIF/RPC tally = the frontier's T2):

| op | claimed means |
|---|---|
| load | module tracked ok (id > 0) |
| bind | a server was already registered for the sid (vs the dummy allocated so the bind loop proceeds) |
| call | the HLE handled it or a server function ran (same `handled` as the debug event) |
| sendcmd | the host acted on it (the SSX3 sregs handshake write) |

## T1-3. `tools/ladder_diff.py` (fork commit 2) + tolerance story

`tools/ladder_diff.py A.json B.json [--tolerance PCT] [--names A,B]`
(exit 0 iff zero `KEY_DELTA`/`COUNT_DELTA`). Placed at the fork root:
the tree has no `tools/` dir, so "next to the emitter" resolves to a
new top-level `tools/` (call recorded here). No new build references
(Python, stdlib-only).

| Verdict | Meaning |
|---|---|
| EXACT | equal (deterministic rows: parked-thread status/wait, sema table+creates, drops, unhandled-call multiset, quiet sched counts) |
| TOL_OK / COUNT_DELTA | throughput row within / beyond `--tolerance` (default 10%): sched counts, gs true counts, dma/gif/gsw/vif, sema-hist counts, hot-pc counts emitter-vs-emitter |
| SAMPLED | thread pc + live-thread (Running/Ready) status: wall-clock samples, never exact |
| SATURATED | miner hit a log cap (`[gs:kick]`<96, `[gs:copy-reg]`<64, `[gs:gif]`<48, `[sceSifSendCmd]`<5, `[diag:stub]` top-30/block) |
| STALE | tick-derived gs rows across mixed sources (miner reads the last `[run:tick]`, emitter reads live) |
| BLIND / TRUNC | miner-blind fields (loads, binds, claimed calls, sema table, invocation-thread sched, truncated hot-pc tails) |

Tolerance story: throughput rows are documented contended and never
exact — pump semas (sema-31: 5210 vs 5296 across legacy boots),
dispatch counts, GS activity, and the miner's blind tail (final
partial block/tick) all move with wall timing. Default 10% holds D1
(4.1% worst) and D2 (3.8% worst) with margin; the tool prints the
actual percentage on every throughput row.

## T1-4. Miner (`local/research/T1/mine_snapshot.py`, evidence, not fork)

Rebuilds the schema from a raw boot log (the P1ab/P1ac/P1ad manual
rebuild, automated). Fork scope is emitter + diff tool only, so the
miner ships as T1 evidence.

| Miner source | Schema rows |
|---|---|
| last `[diag:threads]` block + `scheduled=` sums | threads (ra/sp/chain blank: unlogged) |
| `[diag:sema-create]` with `ret>0` | sema_creates |
| `[diag:sema]` op/id/pc | wait/signal hists |
| `[diag:stub]` sums per target | hot_pc (top-30/block truncated) |
| `[drop]` lines | drops (exact) |
| `[IOP/RPC trace:unhandled]` | calls, claimed=false, tid unknown |
| `[sceSifSendCmd]` (≤5) + `[sif-handshake]` | sendcmds (claimed iff handshake + cid 0x80000001) |
| `[gs:kick/gif/copy-reg]` counts + last `[run:tick]` | gs (line rows capped; tick rows stale) |

Blind (omitted, ladder reports BLIND): loads, binds, claimed calls,
sema table, invocation-thread sched. Validated: miner on
`boot-p1ad-1.log` reproduces P28's hand counts exactly (creates 37,
drops 6×, 4 RPC sids, 1 sendcmd, gs 96/64/48).

## T1-5. Proof

### a. Builds + suite

| Item | Value |
|---|---|
| Build dir | `/tmp/t1-link/runtime` (fresh configure, flags copied from `/tmp/p1-link/runtime/CMakeCache.txt`), sources from `/tmp/t1-clean` (detached worktree at `e483d8d` + the 8 T1 files + the 9278 ignored generated `runner/` files rsynced from the main clone) |
| Build | `cmake --build … --target ps2x_tests ps2EntryRunner -j4`, exit 0 (same `ld` duplicate-library warning + 3 pre-existing `-Wswitch` warnings as P1ad) |
| Suite | 436/436/0 (`cd /tmp/t1-clean && ps2x_tests`): 431 P1ad baseline + 3 P1af SPR + 2 T1 (one T1 test failed first on a misplaced dot in my own needle — test bug, product correct, fixed, re-greened) |
| Binaries | void `d817806f…` (stub runner), proof `5e74041f…` (full runner); tests `847d675a…` |
| Tree note | P1af `e483d8d` landed + pushed mid-session; my base. Main-clone `register_functions.cpp` (32 MB, ignored-generated, mtime Sep 19 22:50) never staged/touched — build input only |

### b. Proof boot (boot-t1-2.log, 207,282 lines / 36,642,532 B)

Env = `/tmp/p1ad-boot1.py` + `PS2X_DIAG_PARK=1`; CWD `$W/P1/run`;
binary `5e74041f`; ISO 3005415424 B + ELF 3890784 B (match P1ad).

| Check | Receipt |
|---|---|
| Snapshot written | `[diag:park] snapshot written …` at `:207275`; `park-snapshot.json` 111,491 B parses; `park-snapshot.txt` 7,588 B complete (6 threads, 16 semas, hists, top-30 hot-pc, drops, RPC tally + events, gs line) |
| Clean stop | SIGTERM after 90 s, `rc=0` (snapshot path calls `requestStop`) |
| SPR fix live | 394ED0 probe hit the 20000 cap (was stuck at n=136 pre-SPR); thread 1 out of the walk |
| Hand check 1 (drops) | emitter 6× `dispatchSyscallOverride/KE_ERROR` = `grep -c` 6, same bytes |
| Hand check 2 (sema-30) | emitter 4 waits / 3 signals @ `0x423de8/0x423dc8` = `grep -c` 4 / 3 |
| Hand check 3 (RPC) | emitter 4 unclaimed calls (sids `0x80000006/0x237/0x80000211/0x534e44`) + 1 claimed sendcmd = 4 trace lines + 1 SendCmd line + 2 handshake lines |
| Bonus checks | creates 37 = `grep -c` 37; thread 3 WAIT sema-30 both sides; 21 loads = P28's "SIF loads 21" |

New-park catalogue (post-SPR, tables only — diagnosis belongs to a
later brief): thread 1 Ready @ `0x423dc8` ra `0x377b6c` (past
`0x376938`); thread 5 Running; threads 2/3/4/6 WAIT semas 26/30/31/36;
sema-4 pump at 32,046 waits (vs 731 pre-SPR); GS true counts
1,278,452 kicks / 146,819 gif / 163,150 copy (the 96/48/64 log lines
were caps); hot-pc top `0x41ea18` @ 953,381; dma 194,456 / gif 5,297
live (no longer frozen).

### c. Ladders

| Diff | Sides | Result |
|---|---|---|
| D1 (`/tmp/t1-D1.txt`, evidence `T1/D1.txt`) | proof emitter vs proof miner (same boot) | 97 exact, 8 tol-ok (worst 4.1%), 1184 info, **0 deltas → OK** |
| D2 (`/tmp/t1-D2.txt`, evidence `T1/D2.txt`) | miner p1ad1 vs miner p1ad2 (two same-tree boots) | 116 exact, 11 tol-ok (worst 3.8%), 63 info, **0 deltas → OK** |

D1 info-class census: 1188 hot-pc rows TRUNC (miner truncation),
thread-1/5 status SAMPLED (live at SIGTERM), gs caps SATURATED, tick
rows STALE, loads/binds/sema-table/`sched.-1` BLIND. Every info verdict
traces to a named log limitation (§T1-3), not a data mismatch.

## T1-6. Exact commands

```
# worktree + build (lease-free)
git -C $R worktree add --detach /tmp/t1-clean e483d8d
cp $R/{ps2xRuntime/include/ps2_park_snapshot.h,...8 files} /tmp/t1-clean/...
rsync -a --delete $R/ps2xRuntime/src/runner/ /tmp/t1-clean/ps2xRuntime/src/runner/
cmake -S /tmp/t1-clean -B /tmp/t1-link/runtime -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DPS2X_BUILD_ANALYZER=ON -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=ON -DPS2X_BUILD_STUDIO=OFF \
  -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON -DPS2X_ENABLE_DEBUG_UI=ON -DPS2X_ENABLE_FFMPEG=ON \
  -DPS2X_ENABLE_IOP_RPC_TRACE=ON -DPS2X_ENABLE_RUNNER_PCH=ON -DPS2X_ENABLE_RUNNER_UNITY_BUILD=ON \
  -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_SCCACHE=ON -DPS2X_IOP_ENABLE_PLUGINS=OFF \
  -DPS2X_RUNNER_UNITY_BUILD_BATCH_SIZE=32
cmake --build /tmp/t1-link/runtime --target ps2x_tests ps2EntryRunner -j4
cd /tmp/t1-clean && /tmp/t1-link/runtime/ps2xTest/ps2x_tests   # 436/436/0
# tools validation (lease-free)
python3 local/research/T1/mine_snapshot.py $RUN/boot-p1ad-1.log -o /tmp/t1-mined-p1ad1.json
python3 local/research/T1/mine_snapshot.py $RUN/boot-p1ad-2.log -o /tmp/t1-mined-p1ad2.json
python3 $R/tools/ladder_diff.py /tmp/t1-mined-p1ad1.json /tmp/t1-mined-p1ad2.json --names p1ad1,p1ad2  # D2 OK
# proof (lease T1 held 05:37:44Z-05:39:17Z only; 1 P1ag wait before)
printf 'T1\n' > /tmp/ssx3-p-lane-lease; python3 /tmp/t1-boot1.py   # 90 s, SIGTERM, rc=0
rm /tmp/ssx3-p-lane-lease
# D1 (lease released)
python3 local/research/T1/mine_snapshot.py $RUN/boot-t1-2.log -o /tmp/t1-mined-proof.json
python3 $R/tools/ladder_diff.py $RUN/park-snapshot.json /tmp/t1-mined-proof.json --names emitter,miner  # D1 OK
```

Env delta boots vs `/tmp/p1ad-boot1.py`: `+PS2X_DIAG_PARK=1`,
`BIN=/tmp/t1-link/…`, `LOG=boot-t1-2.log`. Source delta: 2 T1 fork
commits on `e483d8d` (proof binary = worktree equivalent).

## T1-7. What I could not do

- Emitter-vs-emitter ladder: needs two proof boots; the box allows one
  (+ the void). D1 (emitter-vs-miner) and D2 (miner-vs-miner) cover the
  tool's verdict paths instead; the first two-emitter diff falls to the
  next park brief.
- In-runtime `PS2X_DIAG_PARK_TIMEOUT_MS` path: implemented, never fired
  (unset in proof). One line could force it in a future boot.
- Guest-stack walk for the ra chain: the chain is live `$ra` +
  invocation pcs only (shallow by design; documented in the schema).
- Miner blind tail: the final partial block/tick (≤5 s) never prints,
  so live-thread status, pump counts, and tick rows carry the last
  window's gap (SAMPLED/TOL_OK/STALE by rule, never hidden).
- `sched.-1` (11,131 invocation schedules) is emitter-only:
  invocation threads never print `[diag:thread]`.
- Session wall time 04:53–05:43Z (≈50 min incl. build/configure,
  one 5-min P1ag wait, and the void-boot rebuild), inside the 4 h box.
