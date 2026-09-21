# I19 — DIAG_SEMA census (config-only relaunch) + MPEG feeder audit + completion-fix PROPOSAL (no implementation)

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I18/REPORT.md` read first (all of it: P1c sampler + `[diag:frame]` tap prove liveness and NAME the layer — H-c, guest WAITING: main frozen in `sceMpegGetPicture` @`0x3b1028` (`waitReason=Mpeg`, 0 decoded frames, none of the 7 `completeExternalWait` sites fired), workers parked in `WaitSema` on semas 26/30/32/36 (thread 4's vsync pump on 31 the only execution), ALL GS/DMA counters frozen since boot, CD reads + callbacks ALL in the first ~15 s then 75+ s silence; gap 1 = this brief).
- `local/research/E13/NEXT-BRIEF.md` read (all of it: §2 forcing receipts + `stream=false` candidate, §3 probe table, §4 graphics alignment, §5 conditional implementation shape — one generic runtime fix in `MPEG.cpp`, no guest-PC special case, no MPEG-mutex-held delivery, regressions in `ps2_runtime_expansion_tests.cpp`, stop at the next missing link). `local/muse/prompts/E15.md` read (concurrent fork-side probe: checkpoint re-verify + §3 taps + actual-binding fixture + ONE guarded boot; E15 has NOT landed — no `local/research/E15/` dir — so §E15 below tables comparison points, not agreement).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I18; the I18 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4365, I18's bundle UUID — relaunched after I18's cleanup by an unknown launcher, same pattern as I16→I17→I18; state tabled in Task 1).
- BASE: NO MOVE — `83fb4d6` (remote `fork/ssx3` = `83fb4d60904abb016522c477cce704c52118f95f` at recon AND end; E-lane advanced zero commits — E14 stopped at admission, E15 not landed). Separate fork worktree at `83fb4d6` + ZERO ports (no build ⇒ no ports needed) + ZERO commits (read-only audit; `status` clean at end, tabled).
- Product: NO build, NO install — the INSTALLED I18 app relaunched config-only with `PS2X_DIAG_SEMA=1` ADDED (`PS2X_DIAG_PERIOD_MS=15000` kept), probed 90 s.
- Rules honored: no build/codegen/install/commits (reads + ONE config-only probe); all trees under `/Volumes/Extreme SSD/ps2x-i19/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; shared clone touched once (`worktree add`) + read-only inspection (E-lane live and MID-BRIEF ACTIVE: recon `M register_functions.cpp` + `?? ps2_log.txt`; end-of-brief peek `M ps2_e4.h, ps2_e7.h, EeScheduler.cpp, ps2_runtime.cpp, register_functions.cpp` + `?? ps2_log.txt, ps2_e15.h` — E15 tap work landing in the shared tree, remote unmoved); app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before staging evidence; evidence `local/research/I19/` standalone, `[I19]` commit, no push.
- Outcome shape: DIAG_SEMA census NAMES sema 26/30/31/32/36 signalers + counts + sites + timing (creator thread NOT observed — exact obstacle tabled: `[diag:sema-create]` needs the separate `PS2X_DIAG_SEMA_CREATE` env, `Sync.cpp:16-23`, unset in this probe); I18 steady state re-confirmed byte-identical (thread rows, stub/syscall sets, frame counters — this time ALL FIVE `[diag:frame]` lines readable, counters identical to I18's); feeder audit complete with file/line receipts (non-stream callbacks have ZERO readers; the ONLY feeder is the guest via generated wrappers; device runs the no-FFmpeg STUB decoder whose `feed()` returns false and enqueues nothing; `decoderFailed` is never set true anywhere; CD EOF notification comes ONLY from the `sceCdSt*` path which the guest NEVER enters on device — 0 `sceCdSt` lines); fix PROPOSAL written (exact files/functions, delivery semantics, regression tests, E15 preconditions). No code changed anywhere.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i19/`, `WT` = `W/fork-wt` (fork worktree @`83fb4d6`, read-only), `C17` = `/Volumes/Extreme SSD/ps2x-i17/codegen-output/` (reused read-only for wrapper receipts; map byte-identical per I18), `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned), `M` = `WT/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`, `S` = `WT/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `CD` = `WT/ps2xRuntime/src/lib/Kernel/Stubs/CD.cpp`.

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | ONE config-only relaunch (`PS2X_DIAG_SEMA=1` added, no rebuild) censuses sema 26/30/31/32/36 ownership (signalers, counts, sites — what P1c's `waitId` cannot answer), and a read-only source audit of the MPEG feeder path (AddBs callers, CD-stream EOF path, decoder wake sites, `stream=false` vs selecting reader, userdata/ABI shapes) yields a completion-fix PROPOSAL with file/line receipts |
| Observable | Sema-ownership census tables (per-id waits/signals × waker × site × timing + wake decisions); I18 steady-state re-confirmation (thread pcs/status, stub/syscall sets, frame counters, CD timing, boot prefix, crash-log record, screenshot); audit tables with file:line receipts for every claim + named gaps for every unanswered question; fix proposal (files/functions/semantics/tests/preconditions); E15 comparison (agreement table if landed, else comparison points) |
| Alternatives | H-a census complete incl. creators (create lines present). H-b census partial — signalers named but creators unobserved (exact obstacle tabled: separate create-gate env). H-c probe blind (no `[diag:sema]` lines — obstacle receipted, audit-only report). H-d audit contradicts E13/E15 mechanism (disagreement tabled with both receipts, no reconciliation by fiat) |
| Stop | All bars tabled (census/probe/audit/proposal) or any cap (partial tabled as gap). Contract outcome + comparison points in the proposal section |
| Time box | 4 h (used ~75 min wall: recon → worktree → probe 90 s → census → audit reads → extracts → report) |
| One gap | NO implementation in this brief (proposal only); creator census needs a second config-only relaunch the brief does not authorize |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 10 GB | 713 MB (7%: WT 674M + logs ~39M; NO build tree, NO signed app, NO codegen dir) | `du -sh W` after evidence step |
| Evidence `local/research/I19/` | ≤ 5 MB | ~3.9 MB + REPORT, 9 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i19-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | N/A (no build) | no compiler invoked | no build log exists |
| Fork writes | worktree add + read-only inspection, zero commits, remote never moved | 1 `worktree add`, 0 commits, 0 pushes, remote `83fb4d6` at recon AND end | `status` clean, §Task 2 |
| Host codegen runs | 0 | 0 (no build ⇒ no codegen question) | — |
| Probe console committed | complete-or-extract | deterministic 2660-line non-sema extract (184 KB) + 11847-line sema extract (1.6 MB: all non-31 sema complete + id-31 samples + full-log counts) + dormant samples + frame lines + full-log shas (full 45764-line/17.2 MB console on SSD — over cap, tabled) | `logs/*.log` headers |
| Probes (device launches) | 1 config-only | 1 (`PS2X_DIAG_SEMA=1` added; exit 2 = alive, PID 4387) | §Task 1 |

## Task 1 — DIAG_SEMA census probe (iPad, config-only; NO rebuild)

### iPad state before launch (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-launch — no `Locked` failure |
| Running processes | 583-line list pre-launch (`logs/processes-pre.log`); 1 `ps2` match: PID 4365 = the I18 build STILL RUNNING (I18's bundle UUID `33603E5F-…`; relaunched after I18's cleanup by an unknown launcher — I18 reported 0 `ps2` at its cleanup, same pattern as I16→I17→I18). Untouched before launch (reaped BY the launch via `--terminate-existing`) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) — I18 app present, NO reinstall path taken |
| Post-brief state | Only OUR PIDs ever signaled (4365 reaped BY the launch itself; 4387 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I18 build + ISO; MF1/I8–I18 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, lock/processes/files/screenshot 60, launch 90, terminate 30) |

### Launch (I18 recipe + `PS2X_DIAG_SEMA=1`; same bundle UUID, same ISO+ELF paths)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1"}'` + argv ELF path → exit 2 (alive, PID 4387), 45764 lines / 17.2 MB (sha `a4d7bfcd…`; delta vs I18's 23245 lines = the 22395 `[diag:sema]` lines) |
| DIAG_SEMA liveness (RECEIPT — H-c of the contract excluded) | **22395 `[diag:sema]`** (11200 `op=wait` + 11195 `op=signal`) + full P1c set (5 `[diag:frame]` + 5 `[diag:threads]` + 30 `[diag:thread]` + 5 `[diag:stubs]` + 82 `[diag:stub]` + 5 `[diag:syscalls]` + 28 `[diag:syscall]` + 1103 `[diag:cd]` + 1062 `[cd:callback]` + 15676 `[diag:dormant]`) — every predicted line class present |
| `[diag:sema-create]` | **0 lines** — needs the SEPARATE `PS2X_DIAG_SEMA_CREATE` env (`Sync.cpp:16-23`), unset in this probe; creator thread NOT observed (obstacle tabled, §census; H-b of the contract) |
| I18 wall | **Still gone — zero refs anywhere**: `guest-branch` 0, `missing-target` 0 |
| Boot prefix | K1 `armed` + `install#1–8` + `lookup#1–6`; TEXTURE lines; 12 IRX modules; `[sif-handshake] sregs[1]=1`; same 4 unhandled RPC sids (byte-identical); `ee:idle` 0; open-fail 0; `sceCdRead unresolved` 0; no teardown |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11–I15's own spin reports, 01:54–05:00 AM) — **NO new `.ips` for I19 AND no late filing for I18** (four briefs running with no filing; tabled, not root-caused) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i19-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content (viewed from the landed copy) |
| Evidence-size handling | Full console 45764 lines / 17.2 MB EXCEEDS the 5 MB evidence cap → full log + 24975-line dedup stay complete on SSD (`W/logs/`, shas in the extract headers + `logs/launch-sema-console.sizes`); evidence commits the deterministic 2660-line non-sema extract + 11847-line sema extract (all non-31 sema complete + id-31 head/tail samples + full-log per-id counts) + dormant head/tail samples + the 5 frame lines. Reproducible by the exact commands in §Exact commands |

### Census I — per-sema waits/signals × waker (FULL-log counts; the ownership table)

Line formats (read from `S:1411/1441/1459/1519/1542/1555`): wait = `op=wait id=N count=a->b parked=0/1 waker=T pc ra inInt result`; signal = `op=signal id=N count=a->b waiters=a->b waker=T pc ra inInt iSafe invKind invDepth cbFunc target tStatus tSusp … result`. `waker` = `m_currentThreadId` at the call (`-1` = interrupt context, `inInt=1`). `target` = woken thread (`-` = waiter-less signal).

| Sema | Waits (total × waker) | Signals (total × waker) | Wake decisions (signal `target`) | Timing (line span; block-0 dump @18942) |
|---|---|---|---|---|
| 26 | 737 (736 waker=2 + 1 DPI-spliced waker field) | 736 (531 waker=2 + 183 waker=3 + 22 waker=1) | 204 → `target=2` (182 from waker=3 + 22 from waker=1); 531 → `target=-` (all waker=2 self-signals); 1 spliced | 269–15066 — BOOT ONLY (ends before block 0) |
| 30 | 5 (5 waker=3) | 4 (4 waker=1) | 3 → `target=3`; 1 → `target=-` (pre-post `count=0->1`) | 424–14185 — BOOT ONLY (full 9-line transcript in the sema extract) |
| 31 | 5306 (5303 waker=4 + 2 spliced-waker + 1 DPI-truncated) | 5306 (5269 waker=`-1` + 29 waker=3 + 1 waker=1 + 6 spliced-waker + 1 DPI-truncated) | 5271+ → `target=4` (remainder spliced tails) | FULL RUN — steady 60/s pump (all non-`-1` signals are boot-phase, ≤ line 14564) |
| 32 | 616 (616 waker=5) | 615 (206 waker=1 + 205 waker=5 + 175 waker=`-1` + 29 waker=3) | 410 → `target=5` (206 from waker=1 + 175 from waker=`-1` + 29 from waker=3); 205 → `target=-` (all waker=5 self-signals) | 293–14506 — BOOT ONLY |
| 36 | 1 (waker=6, `parked=1`, line 4646) | **0 — NEVER signaled in 90 s** | — | single boot-phase park |

Other sema ids observed (full-log `id=` census; boot-phase lock traffic, not the I18 wait set): 1, 4 (3584), 5 (2823), 6–25 (2 each), 29 (414), 33 (1640), 34 (4), 35 (404), 39 (154). Exact per-id counts in the sema extract Part C.

### Census II — waiter/signaler sites (guest pcs; gateways decoded by I18)

All waits park at `pc=0x423de8` (WaitSema-gateway resume label). Signal `pc` distinguishes the syscall used: `0x423dc8` = SignalSema path, `0x423dd8` = iSignalSema path (interrupt-safe; `inInt=1 iSafe=1` on the `-1`/boot-`3`/`1` rows).

| Sema | Waiter thread (ra = waiter call site) | Signaler rows (waker × count × pc × ra = signaler call site) |
|---|---|---|
| 26 | t2 (ra `0x3e3c20`, CD-callback region) | t2 ×531 `0x423dd8`/`0x3e3af0` (self, `count=0->1`, wakes nobody); t3 ×183 + t1 ×22 `0x423dc8`/`0x3e48b8` (wake t2; `count=0->0`) |
| 30 | t3 (ra `0x31aca4`) | t1 ×4 `0x423dc8`/`0x31acf4` (1 pre-post + 3 wake t3) |
| 31 | t4 (ra `0x31ac30`) — ALL 5306 waits `parked=1` | vsync interrupt ×5269 `0x423dd8`/`0x31abf8` (`waker=-1 inInt=1`, `waiters=1->0 target=4`); same site ×29 (waker=3) + ×1 (waker=1) boot-phase (`inInt=1`, a thread was current) |
| 32 | t5 (ra `0x3827e0`) — 616 waits = 205 takes + 411 parks | t1 ×206 `0x423dc8`/`0x377b6c` (wake t5); t5 ×205 `0x423dd8`/`0x3826b4`-region (self, `count=0->1`, `target=-`); interrupt ×175 `0x423dd8`/`0x382640`-region (`waker=-1`, wake t5); waker=3 ×29 (wake t5) |
| 36 | t6 (ra `0x3c19f0`, `count=0->0 parked=1 waiters=0->1 result=park`) | NONE |

### Census III — creator thread (NOT observed; exact obstacle + next config)

| Item | Receipt |
|---|---|
| Obstacle | `[diag:sema-create]` (creator tid + pc/ra + init/max/attr/option + returned id) is gated on `PS2X_DIAG_SEMA_CREATE` (`Sync.cpp:16-23`), a DIFFERENT env var from `PS2X_DIAG_SEMA` — 0 such lines in this probe (var unset) |
| Next config (no rebuild) | Relaunch the installed app with `PS2X_DIAG_SEMA_CREATE=1` ADDED to this probe's env; creators for all 33 observed ids (incl. 26/30/31/32/36) print at boot |
| Not inferred | No creator is guessed from waker traffic (first-signaler ≠ creator); the census above names signalers only |

### Steady-state re-confirmation (I18, byte-identical unless noted)

| Check | I19 receipt | vs I18 |
|---|---|---|
| Thread rows (30) | 6/6 `status=2` all 5 blocks; t1 `waitReason=6 waitId=0 pc=0x3b1028 scheduled=8255→0,0,0,0`; t2/t3/t5/t6 `waitReason=2` waitIds 26/30/32/36 `pc=0x423de8`; t4 `waitId=31 scheduled=860→900,900,900,900` | IDENTICAL except t4 block-0 `scheduled` 860 vs 859 (1-count variance, tabled) |
| Stub sets | block-0 `distinct=1482`; blocks 1–4 `distinct=13` each, sets identical ×4 (same 13 targets + counts: 3×1800, 10×900; `0x423de0`/`0x423dd0` ra `0x31ac30`/`0x31abf8`) | IDENTICAL (block-0 top target `0x41ea18` ×953385 vs ×953382 — 3-count variance, tabled) |
| Syscall sets | block-0 `distinct=30`; blocks 1–4 `distinct=2` each (`0x44` WaitSema ×900 + `-0x43` iSignalSema ×900) | IDENTICAL |
| Frame counters | ALL FIVE `[diag:frame]` readable (no interleave this probe): vsync 900→4500 (+900/block); kicks=43708 kicksDrawing=43356 gif=2795 copyRegs=4655 dma=4542 gifCopy=210 gsWrites=0 vifWrites=2 BIT-IDENTICAL blocks 0–4 | IDENTICAL values to I18's blocks 0–3 (deterministic boot; submission frozen) |
| CD timing | ALL 1102 `sceCdRead` (lines 96–15059) + ALL 1062 callbacks (531 `queued`/`start func=1 cb=0x3e3ad8` pairs) precede block-0 dump (18942); first `lbn=0x10` PVD, last `lbn=0x13bb13 sectors=16`; +1 `sceCdInitEeCB` | IDENTICAL shape (I19 has 1102 vs I18's 1102 reads; same first/last lbn) |
| MPEG dispatch | Dormant tails: `0x402c08` (AddCallback) ×6 lines, `0x402a10` (GetPicture) ×6 lines, `0x4029d0` (AddBs) ×0, `0x3b0b10`/`0x3b0b40`/`0x3b06b0` (guest producer) ×0; e.g. line 15115 tail `…→0x402c08→0x3b1050→0x402b38→0x3b10d0→0x402a10→…` (registration then GetPicture during boot) | NEW receipt class (I18 did not census these); consistent with E13 fork-side (registration once, producer never) — tails are ~40-deep idle samples, NOT a census (caveat tabled) |
| Stub decoder tripwire | `without FFmpeg` ×0, `mpeg` (any case) ×0 in 45764 lines | NEW: no sequence header ever reached the stub `feed()` (its warning is ungated stderr — would print once on first fed header; §Task 2) |
| St-streaming tripwire | `sceCdSt` ×0 (StStart/StRead logs are ungated stderr) | NEW: guest NEVER enters the St-streaming path — the ONLY CD→MPEG EOF notifier (§Task 2) |

## Task 2 — feeder audit (read-only sources @`83fb4d6`) + fix PROPOSAL

### Worktree record (read-only; zero commits expected, zero made)

| Item | Receipt |
|---|---|
| Pin (UNMOVED) | `83fb4d6` = `83fb4d60904abb016522c477cce704c52118f95f` |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `83fb4d6` at recon AND at end (E-lane advanced zero commits: E14 stopped at admission, E15 probe-only/not landed) |
| E-lane owner | Live AND mid-brief active — recon: shared `ssx3` @`83fb4d6` with `M register_functions.cpp` + `?? ps2_log.txt`; end: `M ps2_e4.h, ps2_e7.h, EeScheduler.cpp, ps2_runtime.cpp, register_functions.cpp` + `?? ps2_log.txt, ps2_e15.h` (E15 tap work; remote + checkout still `83fb4d6`; I19 worktree unaffected — detached, clean) |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 83fb4d6` → `HEAD is now at 83fb4d6` (exit 0); ZERO ports (no build ⇒ no ports); ZERO commits; `status` clean at end |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / status / worktree list`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree; the `non-monotonic index` stderr noise tabled, outputs unaffected) |
| Base move? | NO — audit reads `83fb4d6` directly; C17 reused read-only for wrapper receipts (map byte-identical per I18 §Task 1) |

### Audit 1 — AddBs callers: the ONLY feeder is the guest, via its undelivered callback

| # | Claim | Receipt |
|---|---|---|
| 1 | `sceMpegAddBs` (M:1889-1922: a0=mpeg, a1=data, a2=count; copies guest bytes → `feedElementaryStream`; wakes the picture waiter iff frames grew OR `streamEnded` OR `decoderFailed`, M:1914-1919; returns bytes copied) has ZERO runtime-side callers | `grep sceMpegAddBs` over `ps2xRuntime/src` (non-test, excl. `MPEG.cpp`): 0 hits; `Ssx3Movie.cpp` (155 lines): 0 MPEG refs of any kind |
| 2 | The guest reaches AddBs ONLY through the generated wrapper `0x4029d0` | C17 `sub_004029D0_0x4029d0.cpp`: `ctx->pc = ra; ps2_stubs::sceMpegAddBs(…)`; registered in `register_functions.cpp:390246` (actual binding, as E13 states) |
| 3 | The guest calls `0x4029d0` ONLY from its callback-fed producer `0x3b0b40` (:73 `jal func_4029D0` with a0=s4, a1=`[s1+0x78]`, a2=s2) | `local/research/E13/mpeg-callback-raw-dis.txt:63-74` (ELF `1b49d05c…`, same bytes as the device ELF) |
| 4 | The producer is driven ONLY by the registered callback `0x3b0b10` (reorders `(a0,a1,a2)→(a2,a0,a1)` into `0x3b0b40`, returns 1) | Same file :2-13; `0x3b0b40` pulls its object from its a0 (= callback a2) and its mpeg handle from its a1 (= callback a0) |
| 5 | The callback is registered by `0x402c08` → `sceMpegAddCallback` (M:1924-1943: a0=mpeg, a1=type, a2=func, a3=data; records `stream=false`, M:1939-1940; returns handle) | C17 `sub_00402C08_0x402c08.cpp` + `register_functions.cpp:390254`; E13: type 1, func `0x3b0b10`, userdata=s2 (NEXT-BRIEF §2 — I19 does not re-derive) |
| 6 | Device-side, the producer chain NEVER runs: `0x4029d0`/`0x3b0b10`/`0x3b0b40`/`0x3b06b0` ×0 in 45764 console lines; the stub-decoder tripwire (`without FFmpeg`) ×0 | I19 probe console census (tails are samples — caveat tabled in Task 1; the ungated-warning absence is the stronger receipt: no sequence header was ever fed) |
| 7 | `sceMpegFlush` (M:1865-1887) also feeds no input (flushes the decoder queue only) and has the same zero-runtime-caller status | Same grep as #1 (0 hits); guest wrapper `0x4029d0`-adjacent — NOT traced in console (no `mpeg` mentions at all) |

### Audit 2 — `stream=false` vs the selecting reader: non-stream callbacks have ZERO readers

| # | Claim | Receipt |
|---|---|---|
| 1 | `MpegRegisteredCallback` carries `stream` (default `false`, M:472-480); `sceMpegAddCallback` records `false` (M:1939-1940), `sceMpegAddStrCallback` records `true` (M:1958-1959) | M:472-480, M:1924-1961 (two registration entry points, one flag apart) |
| 2 | The ONLY selecting reader is `matchingStreamCallbacks` (M:1141-1158), which requires `callback.stream && callback.type == streamType` | M:1152; the ONLY other `callbacksByMpeg` touches are insert (M:1939/1958), clear-on-reset (M:1773), erase-on-delete (M:2095) — no second reader exists |
| 3 | Queued stream events reach the guest ONLY via `dispatchStreamCallbacksUnlocked`, called from exactly two sites: `sceMpegDemuxPss` (M:2167) and `sceMpegDemuxPssRing` (M:2261) | `grep dispatchStreamCallbacks` over M: defs at 1632/1651/1661 + call sites at 2167/2261 only |
| 4 | The type-1 callback therefore has NO selection path and NO dispatch path: it is recorded, then never read | Follows from #1–#3 (E13's §2 candidate, confirmed in source at `83fb4d6`) |
| 5 | The existing stream dispatch ABI (MUST NOT be assumed for type-1 per E13 §2): cbData = guestMalloc(`0x20`) with +0x00 streamType, +0x08 dataAddr, +0x0C len, +0x10 pts, +0x18 dts (M:1567-1589/1582-1586); regs a0=mpeg, a1=cbData, a2=userdata, a3=0, sp=0→async-stack, ra=0 (M:1613-1620); queued as `GuestInvocationKind::RpcCallback` via `queueInvocation` (M:1622-1629; `S:1743-1749` appends to `m_pendingInvocations` + sets checkpoint flag); cbData freed in `onComplete` (M:1625-1628) | M:1567-1662, S:1743-1749; `sp=0` is backfilled to a reserved 16 KB async stack by `invokeCurrent` (S:1751-1764) |

### Audit 3 — GetPicture wait + the 8 wake lines (none fired on device)

| # | Claim | Receipt |
|---|---|---|
| 1 | `sceMpegGetPicture` (M:2306-2346: a0=mpeg, a1=image) parks the caller iff `decodedFrames.empty() && !currentCdStreamEofSeen && !streamEnded && !decoderFailed` (M:2318-2321); unlocks the MPEG mutex BEFORE `waitExternal` (M:2333-2334); the resume completion re-invokes `sceMpegGetPicture` (M:2338-2345) | M:2306-2346; `waitExternal` is `[[noreturn]]` (S:2099-2106 → `blockCurrent`), so the M:2348+ fall-through never runs on the park path |
| 2 | `sceMpegGetPicture` is the SOLE `waitExternal(Mpeg,…)` issuer (token = mpegAddr, type `kMpegPictureWaitType=1`) | `grep waitExternal` over M: sole hit M:2334; `Ssx3Movie.cpp`: no waits (I18 receipt, re-verified: 0 MPEG refs) |
| 3 | The 8 `completeExternalWait(kMpegPictureWaitType,…)` lines: M:1860 (`notifyMpegCdStreamEof`, per completed id), M:1884 (`sceMpegFlush`, frames-grew/end/fail), M:1919 (`sceMpegAddBs`, frames-grew/end/fail), M:2098 (`sceMpegDelete`, `KE_WAIT_DELETE`), M:2144/2150 (`sceMpegDemuxPss`, decoded/end + completed others), M:2237/2243 (`sceMpegDemuxPssRing`, same) | `grep completeExternalWait` over M (I18's "7 sites" listed these same 8 line numbers) |
| 4 | Completion scans Waiting/WaitingSuspended threads for reason External/Mpeg + type+token match and readies each with the result; unknown tokens are a silent no-op | S:2071-2097 (`completeExternalWait`); `sceMpegDelete` erases callbacks+playback BEFORE completing with `KE_WAIT_DELETE` (M:2092-2099), and the GetPicture resume treats negative `v0` as terminal (M:2340-2343) — the in-tree cancellation shape |
| 5 | On device, NONE fired for the parked stream: main still `waitReason=6` with `scheduled=0` blocks 1–4, 0 frames served | Task 1 thread rows; `decoderFailed` can never be the breaker (Audit 4 #3); EOF can never be the breaker (Audit 5 #4) |

### Audit 4 — why 0 frames decode on device (TWO stacked causes, ordered)

| # | Claim | Receipt |
|---|---|---|
| 1 | Cause A (first): NO input ever arrives — AddBs/Demux are never called (Audit 1 #6), so `sawInput` stays false and `decodedFrames` stays empty | Task 1 tripwires + E13 fork-side zero-dispatch receipt |
| 2 | Cause B (second, behind A): the DEVICE decoder is the no-FFmpeg STUB — `feed()` prints one ungated warning and returns `false`, enqueuing NOTHING (M:447-469); `feedElementaryStream` treats `false` as retry-later (decoder reset + wait-for-header again, M:1107-1114), NOT failure | M:447-469, M:1102-1114; iOS default `PS2X_ENABLE_FFMPEG=OFF` (`ps2xRuntime/CMakeLists.txt:271-277`); I18 device `CMakeCache.txt:429` = `OFF`; the `[MPEG] runtime built without FFmpeg…` string IS in the installed binary (1 `strings` hit; 0 `nm` ffmpeg syms) |
| 3 | `decoderFailed` is NEVER set `true` anywhere (init `false` M:498; reset `false` M:1091/1112) — the GetPicture `!decoderFailed` breaker and the IsEnd `decoderFailed && sawInput` ender are dead code paths | `grep "decoderFailed = "` over M: exactly 3 hits, all `false` |
| 4 | `sceMpegIsEnd` (M:2475-2515) can return 1 ONLY via producer-EOF + (`streamEnded` OR (`decoderFailed && sawInput`)) + presentation-complete — unreachable on device while Audit 5 #4 holds | M:2486-2514 |

### Audit 5 — why the CD-stream pump stops before EOF (guest never enters streaming mode)

| # | Claim | Receipt |
|---|---|---|
| 1 | CD→MPEG EOF notification comes ONLY from the St-streaming path: `continueCdStRead` end-of-stream (CD:890), non-blocking StRead at end (CD:1039), `sceCdStStop` (CD:1112); plus `notifyMpegCdStreamStart` on `sceCdStStart` (CD:1089) and per-chunk `DataProduced` (CD:967) | `grep notifyMpeg` tree-wide: exactly CD:890/967/1039/1089/1112 + `MPEG.h:9-11` decls |
| 2 | Plain `sceCdRead` (what the device probe shows, 1102/1102 reads) NEVER notifies MPEG — no EOF, no byte accounting | Same grep (no `sceCdRead`-path notifier); `finalizeCdStreamEofUnlocked` (M:1387-1402) is reachable only via `notifyMpegCdStreamEof` or demux-byte catch-up (M:1423-1434, needs produced>0) |
| 3 | On device the guest NEVER enters streaming mode: `sceCdSt` ×0 in 45764 lines (StStart/StRead logs are UNGATED stderr — would print) | Task 1 tripwire; CD:971/1091 confirm the logs are ungated |
| 4 | Therefore `currentCdStreamEofSeen` stays `false`, `cdStreamBytesProduced` stays 0, and `finalizeCdStreamEofUnlocked` never runs FOR THIS STREAM — the GetPicture `!sawEof` breaker (M:2319) and the Demux catch-up path (M:1429-1433) never engage | Follows from #1–#3 + M:1387-1402/1419/1423-1434 |
| 5 | The CD layer itself is faithful: all issued reads served (`unresolved` 0, no error park, PVD + IRX loads prove ISO parsing); the pump stops because the GUEST stops issuing reads once parked (last read `lbn=0x13bb13` pre-block-0, then main parks in GetPicture and feeders park in never-signaled semas) | Task 1 CD timing + thread rows; NOT a CD bug — one layer above (MPEG/sema completion) |

### Audit 6 — userdata/ABI shapes (what the fix must be given; E15 owns the type-1 receipt)

| # | Claim | Receipt |
|---|---|---|
| 1 | Registration stores a1=type, a2=func, a3=data(userdata) per mpeg (M:1929-1940); dispatch (stream path) passes userdata as a2 (M:1616) | M:1924-1943, M:1591-1630 |
| 2 | E13's guest-side contract (NOT re-derived here): registration type 1 + func `0x3b0b10` + userdata=s2; producer `0x3b0b10→0x3b0b40→0x3b06b0` + `AddBs(mpeg=a1_in, data=[s1+0x78], count=s2)`; helper fields +0x78/+0x7c | E13 NEXT-BRIEF §2 + `local/research/E13/mpeg-callback-raw-dis.txt` (I19-verified: AddBs call at :73, field loads at :25/:32/:44/:70, reorder at :2-9) |
| 3 | UNANSWERED (named gap, not a guess): the type-1 callback's register contract (which of a0–a3 carries mpeg/userdata/cbdata on ENTRY), its cbData layout (if any — stream uses `0x20` bytes at M:1582-1586, but E13 §2 forbids assuming it), its return-value semantics (the guest producer returns 1 — expected? valid-no-input? shape unknown), and its re-entry contract (may it call AddBs synchronously? the stream path CAN — dispatch happens outside the MPEG lock at M:2167/2261) | Gap G2 (needs E15's ABI receipt before the fix brief binds these) |

### Fix PROPOSAL (no implementation in this brief; E13 NEXT-BRIEF §5 shape, I19-pinned)

Preconditions (ALL must hold before the fix brief binds the ABI): P1 E15's ABI receipt (register contract + cbData layout + return semantics + re-entry contract for type-1 — Audit 6 #3); P2 E15's delivery-gap confirmation (request path demonstrably omits delivery — I19's source audit says the reader is missing; E15 must confirm the DYNAMIC request path reaches the point where delivery should occur); P3 fix-brief owner confirms the type-1 trigger point (which guest call arms/delivers: GetPicture-entry? Demux-entry? vsync? — I19 does not name it; E15's §3 probes do).

| # | Element | Proposal (file/line-pinned) |
|---|---|---|
| F1 | Files | ONE generic runtime fix in `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp` (new `matchingNonStreamCallbacks` selector beside M:1141-1158 + new `dispatchGuestNonStreamCallback` beside M:1591-1630 + trigger call at the E15-named point); decl changes in `Stubs/MPEG.h` ONLY if the trigger needs a cross-TU entry (else none); NO guest-PC special case, NO handwritten leaf, NO generated-source edit, NO map change (per E13 §5) |
| F2 | Selection | Mirror `matchingStreamCallbacks` with `!callback.stream && callback.type == requestedType`; the requested type comes from the trigger's context (NOT hardcoded 1 — generic across non-stream types) |
| F3 | Delivery semantics | Mirror `dispatchGuestStreamCallback` (M:1591-1630): `hasFunction` guard, guestMalloc cbData (SIZE+LAYOUT from P1 — not `0x20`-assumed), regs per P1, `sp=0` async-stack backfill, `ra=0`, queue as `GuestInvocationKind::RpcCallback` via `queueInvocation` (S:1743-1749); cbData freed in `onComplete`; return value consumed per P1 (distinguish delivery vs valid-no-input vs error) |
| F4 | Locking / re-entrancy (E13 §5) | NEVER invoke while holding `g_mpeg_stub_mutex` (the callback re-enters via AddBs → same mutex: M:1898): collect-then-dispatch — build the event list under the lock (as Demux does, M:2108-2128), dispatch AFTER unlock (as M:2167/2261 do). Preserve request ordering (dispatch in registration order); dedupe: `hasInvocation(RpcCallback, tag)` (S:1785-1797) or a pending-delivery flag per (mpeg,type) with the tag = callback handle — no duplicate/reentrant deliveries while one is queued |
| F5 | Cancellation / deletion (E13 §5) | `sceMpegDelete` (M:2088-2100) MUST invalidate pending non-stream deliveries for the erased mpeg (erase-then-complete-`KE_WAIT_DELETE` already exists — extend the erase to the pending-delivery set); the GetPicture resume's negative-`v0` terminal path (M:2340-2343) already handles the post-delete wake; teardown (reset/init) clears the pending set with the callbacks (M:1773) |
| F6 | No sema change | The sema waits (26/30/32/36) are GUEST-orchestrated producer/consumer handshakes (Task 1 census: threads 1/3/interrupt ARE the signalers during boot) — they stall because the producers stall on the SAME undelivered MPEG input, not because the sema implementation is wrong; no `EeScheduler` sema change is proposed (if a parked thread's producer is itself MPEG-blocked, unblocking MPEG unblocks the sema chain — the fix brief re-probes to confirm) |
| F7 | Cause-B sequencing (Audit 4 #2 is BEHIND the fix, not in it) | The fix brief does NOT flip `PS2X_ENABLE_FFMPEG` for iOS and does NOT change the stub decoder: per E13 §5's stop rule, if delivery now occurs but decode fails (stub `feed()` → `false` → silent retry, M:1107-1114), the fix brief names "no on-device MPEG decode" as the first demonstrated missing link and STOPS (its own brief: FFmpeg-for-iOS build? stub-frame completion? — not this proposal's call) |
| F8 | Regression tests (extend `ps2xTest/src/ps2_runtime_expansion_tests.cpp`, MiniTest — existing MPEG cases at :484/:525/:723/:756 + fixtures at :176-196/:225-287) | T1 non-stream register→trigger→delivery (fail-before: callback never invoked); T2 AddBs re-entry from inside the delivered callback (no deadlock — F4); T3 wait completion via delivered-input frames (GetPicture resumes); T4 valid-no-input return (producer returns without AddBs → waiter NOT spuriously completed, or completed-per-P1 — bound by P1); T5 teardown during pending delivery (delete/reset → no dispatch, no use-after-free, waiter completes `KE_WAIT_DELETE`); T6 stream-callback behavior RETAINED (existing :525 case green, unmodified) |
| F9 | Re-probe (device, I-lane) | Rebuild + reinstall + 90 s `PS2X_DIAG_PERIOD_MS` probe: expect main past `0x3b1028` (or a NAMED successor state), `0x4029d0`/`0x3b0b10` in stub sets, stub-decoder warning present (Cause B now the wall — F7), sema 26/30/32 traffic past boot; re-census creators with `PS2X_DIAG_SEMA_CREATE=1` in the SAME probe (Census III next config — combinable, still config-only) |
| F10 | Stop | First demonstrated missing link AFTER delivery (decode? EOF? a later guest edge?) names the next brief; NO stacking a second fix, NO routing around a guest-side gate (E13 §5) |

### E15 comparison (E15 NOT landed — comparison points for the next brief, not agreement)

| # | Comparison point | I19 receipt (this report) | E15 receipt needed (per `local/muse/prompts/E15.md`) |
|---|---|---|---|
| C1 | Mechanism: non-stream callback recorded-but-never-delivered | Audit 2 #1–#4 (no selecting reader; dispatch only from Demux ×2) | §3 callback selection/delivery probes: eligibility + scheduling + actual dispatch (or its demonstrated absence) at `0x402c08`-registered type-1 |
| C2 | Request path: does the guest's GetPicture request REACH the delivery point? | I19 does NOT observe the dynamic request path (AGRESSIVE-gated; device shows only registration + GetPicture dispatch in tails) | §3 picture-request probe at `0x402a10` (a0/a1, RA/SP, queue, flags, selected callbacks, wait registration) |
| C3 | Type-1 ABI: regs + cbData + userdata + return | Audit 6 (registration stores a1/a2/a3; stream ABI tabled as NOT-assumed; gap G2) | §3 selection/delivery + guest-data-source probes (original a0/a1/a2, cbData bytes, userdata, return value/destination; `0x3b0b10→0x3b0b40→0x3b06b0` join; helper +0x78/+0x7c) |
| C4 | Input/completion join: AddBs bytes → decoder → frames → wake | Audit 1/3/4 (source paths + wake conditions; device shows zero input) | §3 input/completion probe at `0x4029d0` (bytes/hash, copied count, decoder result, queued frames, wake op → resumed GetPicture) |
| C5 | Lifetime: removal/deletion/exhaustion vs never-dispatched | Audit 3 #4 (delete path exists; device shows no delete — waiter still parked) | §3 lifetime probe (removal/deletion/reset/terminal event) |
| C6 | Decoder on the E-lane host (ffmpeg ON?) vs device stub | Audit 4 #2 (device = stub; host flag default ON non-iOS/Android — E-lane host value NOT verified by I19) | Checkpoint re-verify (§1): host build identity — if E15's host HAS ffmpeg, its decode observations do NOT transfer to device (Cause B stays device-open) |
| Disagreement rule | If any C-row disagrees, the next brief tables BOTH receipts and does NOT reconcile by fiat (brief Coordination) | — | — |

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i19"
git -C "$FORK" ls-remote fork ssx3          # 83fb4d6 at recon AND end (zero E-lane advances)
git -C "$FORK" log --oneline -3             # 83fb4d6 at top (non-monotonic ._* idx noise on stderr)
git -C "$FORK" status --short               # recon: M register_functions.cpp + ?? ps2_log.txt; end: + M ps2_e4.h, ps2_e7.h, EeScheduler.cpp, ps2_runtime.cpp + ?? ps2_e15.h (E15 tap work)
git -C "$FORK" worktree list                # shared @83fb4d6 [ssx3] + all prior I-lane WTs
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60  # 583 lines, PID 4365 = I18 leftover
# --- Worktree at HEAD (NO ports, NO commits) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I19/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 83fb4d6
WT="$W/fork-wt"; git -C "$WT" status --short  # clean (at add AND end)
# --- Task 1: ONE config-only probe (installed I18 app, DIAG_SEMA added) ---
B="/private/var/containers/Bundle/Application/33603E5F-978B-4D3D-A06B-6270872BC82A/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-sema-console.log" 2>&1    # exit 2 (alive, PID 4387), 45764 lines / 17.2 MB
L="$W/logs/launch-sema-console.log"
grep -c "diag:sema" "$L"                     # 22395 (liveness receipt)
grep -c "diag:sema-create" "$L"              # 0 (creator obstacle)
grep -c "guest-branch\|missing-target" "$L"  # 0 (no wall)
for id in 26 30 31 32 36; do echo "== $id"; grep -c "op=wait id=$id " "$L"; grep -c "op=signal id=$id " "$L"; done
grep "op=signal id=26 " "$L" | grep -oE "waker=-?[0-9]+" | sort | uniq -c   # per-id waker census shape (×5 ids ×wait/signal)
grep "op=signal id=31 " "$L" | grep -v "waker=-1" | cut -c1-120             # boot-phase non--1 signals
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i19 -s ps2EntryRunner --no-recurse  # 5 files, all priors
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i19-shot1.png
mv /tmp/i19-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4387  # cleanup only
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i19 -s ps2EntryRunner --no-recurse  # still 5
# --- Task 1: steady-state + tripwire census ---
grep -h "\[diag:thread\]" "$L"               # 30 rows (byte-identical to I18 ±1 count)
grep -h "diag:frame" "$L"                    # 5 lines, all readable, counters frozen
grep -c "sceCdSt" "$L"; grep -c "without FFmpeg" "$L"; grep -ciE "mpeg" "$L"  # 0/0/0 tripwires
for a in 0x4029d0 0x402a10 0x402c08 0x3b0b10 0x3b0b40 0x3b06b0; do printf "%s: " "$a"; grep -c "$a" "$L"; done
# --- Task 2: feeder audit reads (all read-only; M=MPEG.cpp S=EeScheduler.cpp CD=CD.cpp) ---
grep -n "completeExternalWait\|waitExternal" "$WT/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp"
grep -n "EofSeen\|notifyMpeg\|sawEof\|streamEnded\|decoderFailed\|sawInput" M | head -40
grep -rn "notifyMpegCdStream" "$WT/ps2xRuntime/src"   # CD.cpp ×5 + MPEG.h decls only
grep -rn "sceMpegAddBs\|sceMpegDemuxPss\|sceMpegGetPicture\|sceMpegAddCallback" "$WT/ps2xRuntime/src" --include="*.cpp" | grep -v Stubs/MPEG.cpp  # 0 (no runtime-side feeder)
grep -n "decoderFailed = " M                          # 3 hits, all false
grep -n "PS2X_ENABLE_FFMPEG" "$WT/ps2xRuntime/CMakeLists.txt"  # iOS/Android default OFF (:271-277)
grep -n "PS2X_ENABLE_FFMPEG" /Volumes/Extreme\ SSD/ps2x-i18/ios-runtime-device/CMakeCache.txt  # OFF
strings -a I18-APP-BINARY | grep -c "without FFmpeg"  # 1 (stub compiled into the installed app)
grep -n "0x4029d0\|0x402a10\|0x402c08" C17/register_functions.cpp  # actual bindings (:390246/47/54)
grep -n "tc.Run" F | grep -i mpeg                     # existing MPEG MiniTest cases (:484/:525/:723/:756)
# --- Evidence extracts (deterministic) ---
grep -v "GetWindowScaleDPI" "$L" | grep -v "diag:dormant" > "$W/logs/launch-sema-dedup.log"  # 24975 lines
grep -v "diag:sema" "$W/logs/launch-sema-dedup.log" >> diag-extract (2660 lines + header)
grep "diag:sema" dedup | grep -v "id=31 " >> sema-extract Part A (complete non-31)
id=31 head/tail-10 ×wait/signal >> Part B; full-log per-id counts >> Part C
shasum -a 256 "$L" "$W/logs/launch-sema-dedup.log"
find local/research/I19 -name "._*" -delete; find local/research/I19 -name "._*" | wc -l  # 0
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | Sema creator threads (26/30/31/32/36 + 28 others) unobserved — `[diag:sema-create]` needs `PS2X_DIAG_SEMA_CREATE` (unset) | 0 create lines in 45764; gate read at `Sync.cpp:16-23` | Fold into the fix brief's re-probe (F9): add `PS2X_DIAG_SEMA_CREATE=1` to the same config-only env — no separate brief |
| G2 | Type-1 callback ABI unbound (entry regs, cbData layout, return semantics, re-entry contract) | Audit 6 #3 (stream ABI exists but is NOT-assumed per E13 §2) | E15's ABI receipt (C3) — the fix brief's P1 precondition; I19 binds nothing without it |
| G3 | Type-1 trigger point unnamed (which call arms/delivers) | I19 audits the static reader gap only; no dynamic request-path observation (AGRESSIVE-gated) | E15's §3 request/delivery probes (C1/C2) — the fix brief's P2/P3 preconditions |
| G4 | No on-device MPEG decode (stub `feed()` → `false`, silent retry; `decoderFailed` never true) sits BEHIND the delivery fix | Audit 4 #2–#3 (flag OFF, stub in binary, 0-warning tripwire) | The fix brief STOPS here per F7/E13 §5 if delivery lands but decode fails — its own follow-up brief (FFmpeg-for-iOS? stub-frame completion?) |
| G5 | E15 not landed at I19 close (no `local/research/E15/`; shared tree shows E15 tap work in progress: `?? ps2_e15.h` + 5 modified files) | End-of-brief shared-clone peek | No brief — the fix brief runs the C1–C6 comparison once E15 lands |
| G6 | NO new `.ips` four briefs running (5 files, all priors' — I11–I15 each filed one spin report; I16–I19 file none) | `logs/crashlog-check.log` (sleep + re-`ls` AND post-terminate re-`ls`: still 5) | Informational — consistent with a non-spinning waiter; next brief's first `ls` confirms I19; no brief unless a later probe shows action-taken |
| G7 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest still in movie/sema wait | Data-container brief (only if a later probe fails on file I/O) |

## Receipt paths

- `local/research/I19/REPORT.md` (this file)
- `local/research/I19/logs/launch-sema-console.diag-extract.log` (2660-line deterministic non-sema extract + header with full-log sha)
- `local/research/I19/logs/launch-sema-console.sema-extract.log` (11847-line sema extract: complete non-31 + id-31 samples + full-log counts)
- `local/research/I19/logs/launch-sema-frame.log` (5 frame lines), `launch-sema-dormant-samples.log` (head/tail), `launch-sema-console.sizes` (counts + shas)
- `local/research/I19/logs/processes-pre.log` (583 lines, PID 4365), `logs/crashlog-check.log` (check1 + check2, still 5 priors), `logs/screenshot.log`
- `local/research/I19/logs/i19-shot1.png` (iPad window, black content)
- `W/logs/` (same + full 45764-line console + full dedup on SSD); `W/fork-wt/` (worktree @ `83fb4d6`, clean, 0 local commits, 0 pushes); NO build tree, NO signed app, NO codegen dir
- No fork push this brief (nothing to push — zero commits by design)

## What I could not do

- Name the sema creator threads — `[diag:sema-create]` needs `PS2X_DIAG_SEMA_CREATE=1`, a second config-only relaunch this brief's ONE-probe rule does not authorize (G1; exact next config tabled).
- Observe the dynamic MPEG request path — all `[MPEG:*]` stub logs are `PS2_IF_AGRESSIVE_LOGS`-gated (compiled out, `AGRESSIVE_LOGS 0`); device shows only wrapper dispatches in dormant tails (G3; E15 owns the fork-side dynamic receipt).
- Bind the type-1 ABI — no authoritative contract in-tree; the stream ABI is tabled as explicitly NOT-assumed (G2; E15's §3 receipt is the fix brief's P1).
- Implement or test the fix — explicitly out of brief (proposal F1–F10 only, zero code changed anywhere).
- Verify E15 agreement — E15 has not landed (G5; C1–C6 comparison points tabled for the next brief).
- Read ~60 DPI-spliced sema lines' tail fields (2 hard-truncated at `id=31`) — the vsync-pump census carries ±splice caveats; counts use full-log numbers with the damage quantified (2 truncated + ~57 field-spliced).
- Present a guest frame — window stays black with the guest in MPEG/sema waits and GS submission frozen since boot; first presented content awaits the completion fix + Cause-B sequencing (F7).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I19); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; paths re-proven by the same-UUID relaunch working (exit 2 + full console).
- Test `mc0`/CD-write/file-I/O behavior — the guest never observably reached file I/O past the boot CD reads (G7).
- Explain why no `.ips` filed four briefs running — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); the non-spinning waiter profile is consistent but not proven causal (G6).
- Re-run a second probe for determinism (e.g. with `PS2X_DIAG_SEMA_CREATE=1`) — single 90 s probe per the brief's recipe and I-series precedent; blocks 1–4 identical steady sets are the in-probe determinism receipt.
- Name the launcher of pre-launch PID 4365 — the I18 bundle was running though I18 reported 0 `ps2` at its cleanup (fourth brief running with a relaunched occupant); it was reaped by the launch without investigation.

## TAIL RECEIPT

Report written in 5 chunks (header + contract + caps; Task 1 probe + census I–III + steady-state; Task 2 worktree + audits 1–6; proposal F1–F10 + E15 C1–C6; commands + gaps + receipts + could-not-do). Pre-receipt measure: 318 lines total, sha256 `4cbfbd0aac6487da7f3883fbf1e6e5881c88b7cec2371fb4881e3e087af4f360` over lines 1–314 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Name the launcher of pre-launch PID 4365 — the I18 bundle was running though I18 reported 0 `ps2` at its cleanup (fourth brief running with a relaunched occupant); it was reaped by the launch without investigation." This receipt line ends the report. END-I19-REPORT.
