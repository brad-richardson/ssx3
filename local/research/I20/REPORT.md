# I20 — E15-ABI agreement + sema-creator census + MPEG-fix-ready spec (no implementation)

- Date: 2026-09-21. Tables, no verdicts.
- `local/research/I19/REPORT.md` read first (all of it: DIAG_SEMA census — 26/30/31/32/36 signalers named, creators UNOBSERVED (H-b: separate `PS2X_DIAG_SEMA_CREATE` env unset); feeder audit — non-stream callbacks ZERO readers, guest-only feeder, no-FFmpeg STUB decoder, `decoderFailed` never true, CD EOF only via the unentered St path; fix PROPOSAL F1–F10 with P1–P3 preconditions on E15).
- `local/research/E15/REPORT.md` + `local/research/E15/ABI.md` + `local/research/E15/NEXT-BRIEF.md` read (all of them: E15 LANDED — host-side type-1 request/delivery probe with original-ELF ABI receipt (register/select/invoke/type-1-data/trigger/ownership/callback/source shapes), measurement-incomplete ONLY on shutdown footers; NEXT-BRIEF imposes closure-repair-before-any-implementation + §4 parked design constraints).
- Target: Brad's iPad, iPad Air 11-inch (M2) (`iPad14,9`), UDID `P` — same device as I18/I19; the I18 app (`org.ps2x.ps2entryrunner`) STILL INSTALLED at brief start AND RUNNING (PID 4396, I18's bundle UUID — relaunched after I19's cleanup by an unknown launcher, same pattern as I16→I17→I18→I19; state tabled in Task 1).
- BASE: MOVED `83fb4d6` → `67c0a632` (E-lane advanced exactly 1 commit — E15's observation commit, pushed to `fork/ssx3`; verified by `ls-remote` at recon). Worktree pins `67c0a632` because the agreement table and fix-ready spec must bind against the tree the E-lane MPEG brief will consume; `MPEG.cpp`/`MPEG.h`/`Sync.cpp`/`ps2_runtime_expansion_tests.cpp` are byte-identical across the move (all I19 `M:` pins carry verbatim), the move touches exactly E15's 5 observation files, and `EeScheduler.cpp`'s 16 added lines are pure gated observation calls (all `S:` pins re-pinned +3, tabled). ZERO ports (no build ⇒ no ports) + ZERO commits (read-only audit; `status` clean at end, tabled).
- Product: NO build, NO install — the INSTALLED I18 app relaunched config-only with `PS2X_DIAG_SEMA_CREATE=1` ADDED (`PS2X_DIAG_SEMA=1` + `PS2X_DIAG_PERIOD_MS=15000` kept), probed 90 s.
- Rules honored: no build/codegen/install/commits (reads + ONE config-only probe); all trees under `/Volumes/Extreme SSD/ps2x-i20/`; caps declared up front + tracked; no PS2 boots → no lease; no `adb`; shared clone touched once (`worktree add`) + read-only inspection (E-lane live: recon `M register_functions.cpp` + `?? ps2_log.txt` @`67c0a63`, preexisting generated-registry dirt per E15 §8; E-lane pane never prompted/steered); app fate from console + `.ips`, never exit code; screenshot to internal path first, then `mv`; every `devicectl` with explicit `--timeout`; `._*` purge before staging evidence; evidence `local/research/I20/` standalone, `[I20]` commit, no push.
- Outcome shape: agreement table complete (13 ABI/mechanism edges, both receipts — 9 agree, 1 E15-closes-I19-gap, 1 constraint-carry, 1 split-by-config, 1 host-only; ZERO disagreements); creator census complete (all 39 creators named: 26/30/31/32 by main-thread boot, 36 by thread-3 boot, all `init=0`); steady state re-confirmed (all sets identical; drift = id-31 pump wall variance + ±1 boot-phase counts + 39 create lines, tabled); P1–P3 ALL have E15 receipts (table that binding, the fix brief does the binding); fix-ready spec S1–S10 written (E15-bound: word0-only cbData, v0 discarded, caller-thread ownership audit, type-1-only trigger, no invented layouts) + handoff table (E-lane MPEG brief consumes / stays device-side / E16-must-deliver-first). No code changed anywhere.

Path shorthands: `W` = `/Volumes/Extreme SSD/ps2x-i20/`, `WT` = `W/fork-wt` (fork worktree @`67c0a632`, read-only), `P` = iPad UDID `00008112-001224302184A01E`, `FORK` = shared clone (E-lane-owned), `M` = `WT/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`, `S` = `WT/ps2xRuntime/src/lib/Kernel/EeScheduler.cpp`, `SY` = `WT/ps2xRuntime/src/lib/Kernel/Syscalls/Sync.cpp`, `ER` = `local/research/E15/REPORT.md`, `ABI` = `local/research/E15/ABI.md`, `NB` = `local/research/E15/NEXT-BRIEF.md`, `T` = `WT/ps2xTest/src/ps2_runtime_expansion_tests.cpp`. Line pins below are @`67c0a632` unless noted.

## Experiment contract

| Item | Content |
|---|---|
| Hypothesis H | E15's ABI receipt closes I19's gaps G2/G3 (type-1 ABI + trigger) edge-by-edge with both receipts agreeing; ONE config-only relaunch (`PS2X_DIAG_SEMA_CREATE=1` added, no rebuild) censuses sema creators (I19's exact tabled obstacle — gate commit `de7ff17` is an ancestor of the I18 build base `83fb4d6`, so the installed binary carries the gate); F1–F10 refine into an E15-bound fix-ready spec the E-lane MPEG brief can consume |
| Observable | Agreement table (every ABI edge, host + device receipts, standings); creator census (creators × all ids incl. 26/30/31/32/36, or receipted obstacle); steady-state re-confirmation (thread/stub/syscall/frame/CD/dispatch/tripwire rows vs I19); P1–P3 receipt status; spec S1–S10 with file/line + tests + handoff |
| Alternatives | H-a full census + full agreement (creators observed, every edge receipted). H-b create gate yields nothing (0 create lines — obstacle receipted, stop at one probe, no second shape). H-c an edge disagrees (both receipts tabled, never reconciled by fiat). H-d steady-state drift vs I19 (drift tabled per-id, not smoothed) |
| Stop | All bars tabled (agreement/census/re-confirmation/spec/handoff) or any cap (partial tabled as gap). Contract outcome: H-a on census, H-a on agreement (zero disagreements), H-d on pump counts (wall variance, tabled) |
| Time box | 4 h (used ~2 h wall: recon → worktree → pins → probe 90 s → census → extracts → agreement/spec → report) |
| One gap | NO implementation in this brief (spec only); E-lane owns the fork and NB closure-repair-first orders E16 before any MPEG brief |

## Caps (declared up front, tracked)

| Cap | Declared | Used | Receipt |
|---|---|---|---|
| `W` SSD allocated bytes (ExFAT) | ≤ 10 GB | 709 MB (7%: WT ~670M + logs ~39M; NO build tree, NO signed app, NO codegen dir) | `du -sh W` after evidence step |
| Evidence `local/research/I20/` | ≤ 5 MB | ~3.9 MB + REPORT, 9 files + REPORT | `du -sh` + file count |
| Screenshots committed | 1 | 1 (`i20-shot1.png`, 2.0 MB) | logs dir |
| Build parallelism | N/A (no build) | no compiler invoked | no build log exists |
| Fork writes | worktree add + read-only inspection, zero commits, remote never moved | 1 `worktree add`, 0 commits, 0 pushes, remote `67c0a632` at recon AND end | `status` clean, §Task 2 |
| Host codegen runs | 0 | 0 (no build ⇒ no codegen question) | — |
| Probe console committed | complete-or-extract | deterministic 2708-line non-sema extract (184 KB) + COMPLETE 39-line create extract + 11851-line sema extract (all non-31 complete + id-31 samples + full-log counts) + frame lines + sizes (full 44620-line/16.6 MB console on SSD — over cap, tabled) | `logs/*.log` headers |
| Probes (device launches) | 1 config-only | 1 (`PS2X_DIAG_SEMA_CREATE=1` added; exit 2 = alive, PID 4511) | §Task 1 |

## Task 1a — agreement table (E15-host × I19-device, every ABI edge, both receipts)

Common join first: all three lanes run the SAME ELF bytes — E15 pins ELF SHA `1b49d05c…67af7bc` (ER §1) and I19's callback disassembly is cut from that same ELF (I19 Audit 1 #3/Audit 6 #2, "same bytes as the device ELF"). Wrapper addresses below are therefore directly comparable. `S:` pins re-pinned @`67c0a632` (E15's 16 added lines are gated `ps2_e15::selection/event` calls only — `git show 67c0a632 -- EeScheduler.cpp`; I19's `S:1411/1441/1459/1519/1542/1555` → `S:1414/1444/1462/1522/1545/1558`; `S:1743-1749` → `S:1746-1753`; `S:1751-1764` → `S:1755-1769`; `S:1785-1797` → `S:1791-1803`; `S:2071-2097` → `S:2077-2106`; `S:2099-2106` → `S:2108-2122`). All `M:` pins carry verbatim (file byte-identical across the base move — `diff --quiet 83fb4d6 67c0a632 -- MPEG.cpp MPEG.h Sync.cpp` clean).

| # | ABI edge | E15-host receipt | I19-device receipt (+ I20 re-confirm) | Standing |
|---|---|---|---|---|
| A1 | Registration type word | `0x402c08` loads `[mpeg+0x40]`, type<<3, stores func @+0x0c + userdata @+0x10 (ABI:10); dynamic seq6404/6405: same a0, type **1**, func `0x3b0b10`, userdata `0x587b00`, handle 1, RA `0x3b0f6c` (ER §5) | `0x402c08` dispatched during boot (dormant tails ×6, I19 Task 1; I20: ×6 again); E13 static: type 1 + func `0x3b0b10` + userdata=s2 (I19 Audit 6 #2); HLE records a1/a2/a3 + `stream=false`, returns handle (M:1929-1943) | AGREE (same wrapper, same type/func; userdata VALUE host-only — device AGRESSIVE-gated) |
| A2 | Select/invoke shape | `0x402c4c` reads cbData word 0, type<<3, tests slot func (ABI:11); `jalr` @`0x402c64`, delay slot loads stored userdata→a2, a0/a1 unchanged ⇒ `(mpeg,cbdata,userdata)` (ABI:12) | HLE has NO non-stream select/invoke: only selecting reader `matchingStreamCallbacks` requires `callback.stream` (M:1152); `GetPicture` parks without selecting (M:2318-2334); E15 names the same current-wrapper shape (ER §4 row 9) | AGREE-ON-GAP (both lanes name the missing selector; E15 §4 row 9 == I19 Audit 2 #1–#4) |
| A3 | Type-1 data + forced v0 | `0x402c84/94` init ONLY stack word 0 = 1; selector call; v0=1 FORCED, callback return discarded — NOT an EOF flag (ABI:13) | Stream cbData `0x20` layout tabled as explicitly NOT-assumed; type-1 layout/return named gap G2 (I19 Audit 6 #3) | E15-CLOSES-G2 (fix brief binds: word0=type only; v0 ignored; no `0x20` assumption) |
| A4 | IPU trigger | Picture route `0x402a44→0x402e10→0x407520→0x4072e8`; busy poll `(MMIO[0x10002010]&0x80004000)==0x80000000`, threshold `0x1389`, invokes `0x402c80` @`0x407344` (ER §4 + ABI:14-15) | Main parked AT the request point: `waitReason=6 waitId=0 pc=0x3b1028` (I19 Task 1; I20: identical); E15 dynamic seq6407-6409: source `0x3b1020`, supplied RA `0x3b1028`, waitReason6 PC/RA `0x3b1028` (ER §5) — SAME park point both lanes | AGREE (same park pc; trigger = GetPicture→IPU-busy route, closes G3/P3) |
| A5 | Caller-thread ownership | Original `jalr` runs within the GetPicture caller's thread/stack; stream RPC-callback queue equivalence must be AUDITED, not assumed (ER §4 + §7; NB §4) | HLE stream dispatch = `queueInvocation` as `RpcCallback` (M:1622-1629; S:1746-1753) with `sp=0`→async-stack backfill (S:1761-1764) — a different ownership shape (I19 Audit 2 #5) | CONSTRAINT-CARRY (I19 F3's mirror-dispatch now gated on E15's ownership audit — spec S3) |
| A6 | Guest callback reorder | `0x3b0b10` reorders `(mpeg,cbdata,userdata)` → helper `(userdata,mpeg,cbdata)` @`0x3b0b40`, returns 1 (ABI:16; ER §4) | Same reorder from E13 dis :2-13; producer pulls object from a0 (= callback a2), mpeg from a1 (= callback a0) (I19 Audit 1 #4) | AGREE (same ELF bytes) |
| A7 | Source path | Helper via `0x3b06b0` using userdata+0x28; descriptor+4/+8 + userdata+0x78/+0x7c feed the AddBs path (ABI:17; ER §4) | Producer `AddBs(mpeg=a1_in, data=[s1+0x78], count=s2)` @dis :73; helper fields +0x78/+0x7c (I19 Audit 1 #3 + Audit 6 #2) | AGREE (same ELF bytes; userdata+0x78 AddBs path both sides) |
| A8 | No-source branch | `0x3b0bdc..0x3b0c00` builds four LE `00 00 01 b7` words, count 16; common call `0x3b0c2c→0x4029d0` STILL fires (ABI:18; ER §4) | NEVER invoked on device: `0x3b0b10`/`0x3b0b40`/`0x4029d0` ×0 in 45764 lines (I19 Task 1; I20: ×0 in 44620) | AGREE-ON-UNEXERCISED (E15's own caveat: uninvoked callback ≠ this branch — ABI:18) |
| A9 | Mechanism: recorded-never-delivered | Selection/dispatch/source/AddBs/completion events ALL zero; park hot-PC census: no `0x3b0b10/0x3b0b40/0x4029d0`; actual-wrapper fixtures `no-input` + `input` rc1 FAIL-BEFORE (ER §3/§5) | No selecting reader + dispatch only from Demux ×2 (M:2167/2261) in source; device tripwires `0x4029d0` ×0 + `without FFmpeg` ×0 (I19 Audits 1/2/4; I20: both ×0 again) | AGREE (same gap: static source + host dynamic + device tripwires converge) |
| A10 | Request reach (P2) | GetPicture enters typed wait type1/token=`0x587b30` (seq6409, `ended=0 failed=0 sawInput=0`); exit seq6410 = C++ UNWIND, v0=`0x3800` not a frame result (ER §5) | `sceMpegGetPicture` sole `waitExternal(Mpeg,…)` issuer (M:2334); main `waitReason=6` `scheduled=0` blocks 1–4, 0 frames (I19 Audit 3; I20: identical) | AGREE (request REACHES the park where delivery should occur — closes P2) |
| A11 | Decoder: host FFmpeg-ON vs device stub | Host cache FFmpeg-ON, libraries pinned — UNEXERCISED (zero input delivered, ER §7); E15 names the device edge downstream, not projected | Device = no-FFmpeg STUB: `feed()`→`false`, enqueues nothing (M:447-469); `PS2X_ENABLE_FFMPEG=OFF` (I18 `CMakeCache.txt:429`); `decoderFailed` never true (3× `= false`, M:498/1091/1112); warning tripwire ×0 (I19 Audit 4; I20: ×0 again) | SPLIT-BY-CONFIG (host-ON unexercised vs device-OFF stub; stub residual stays a SEPARATE device-side edge — spec S7) |
| A12 | Shutdown closure | Measurement-incomplete: `main.cpp:252 run()` → `:259 _Exit(0)` bypasses the destructor footer hook (`runtime.cpp:698-699` unreachable); BOTH source footers absent; NB orders closure-repair-first (ER §7; NB §§1-3) | I-lane probes never observe teardown (no teardown lines I18–I20; app terminated by us at cleanup) | HOST-ONLY GAP (no device receipt either way; not projected onto device) |
| A13 | Return-value semantics | Guest sets v0=1 regardless of helper outcome (ABI:19); no-input return vs AddBs delivery need SEPARATE measurements (ABI:19-20); original forces v0=1 (ABI:13) | I19 F8-T4 (valid-no-input) explicitly bound by P1 (I19 proposal) | E15-BINDS-P1-HALF (fix brief: discard v0; test no-input separately — spec S8) |

Disagreement count: ZERO rows. Device-blind-but-consistent: A1 (userdata value), A8 (branch bytes). E15-closes-I19-gap: A3 (G2), A4 (G3). Constraint-carry: A5. Split: A11. Host-only: A12.

### P1–P3 precondition status (I19 proposal → E15 receipts; the FIX brief does the binding)

| Precondition | I19 need | E15 receipt now on the table | Still for the fix brief |
|---|---|---|---|
| P1 ABI (register + cbData + return + re-entry) | Audit 6 #3 / G2 | Register: (mpeg,cbdata,userdata) + supplied-RA continuation (A1/A2); cbData: word0=type ONLY (A3); return: v0 discarded/forced-1, no-input measured separately (A3/A13); re-entry: guest calls AddBs synchronously from the callback path (A8 common call) + NB §4 (mutex-free dispatch) | Bind exact HLE cbData allocation + invocation shape subject to the A5 ownership audit |
| P2 delivery-gap confirmation | Audit 2 static-only / C1 | Dynamic zeros (selection/dispatch/source/AddBs/completion) + park census + BOTH actual-wrapper fixtures rc1 FAIL-BEFORE (A9) | Re-run fixtures at fix-brief checkpoint (must still be rc1 before the fix) |
| P3 trigger point | G3 (GetPicture-entry? Demux-entry? vsync?) | Architectural trigger = GetPicture→IPU-busy route invoking `0x402c80` (A4); Demux-entry and vsync NOT the type-1 trigger in the original | Place the HLE trigger on the GetPicture-entry path (type-1-only per NB §4); name the exact call site in the fix diff |

## Task 1b — creator-census probe (iPad, config-only; NO rebuild)

### iPad state before launch (user sessions reported, not killed; leftover PID named)

| Item | Receipt |
|---|---|
| Reachability | `connected` at every check; no stall, no substitution (iPhone + 4 shutdown simulators also listed, untouched) |
| Lock state | `passcodeRequired: false`, `unlockedSinceBoot: true` pre-launch — no `Locked` failure |
| Running processes | 581-line list pre-launch (`logs/processes-pre.log`); 1 `ps2` match: PID 4396 = the I18 build STILL RUNNING (I18's bundle UUID `33603E5F-…`; relaunched after I19's cleanup by an unknown launcher — I19 reported 0 `ps2` at its cleanup, same pattern as I16→I17→I18→I19). Untouched before launch (reaped BY the launch via `--terminate-existing`) |
| Installed apps | Occupied target confirmed: `ps2EntryRunner org.ps2x.ps2entryrunner` + `MF1Probe` (never launched/touched) — I18 app present, NO reinstall path taken |
| Post-brief state | Only OUR PIDs ever signaled (4396 reaped BY the launch itself; 4511 via `process terminate` at cleanup); nothing else touched; post-cleanup grep = 0; app left installed (I18 build + ISO; MF1/I8–I19 precedent) |
| Timeout discipline | Every device-scoped `devicectl` carried explicit `--timeout` (list 30, lock 30, apps/processes/files/screenshot 60, launch 90, terminate 30) |

### Launch (I19 recipe + `PS2X_DIAG_SEMA_CREATE=1`; same bundle UUID, same ISO+ELF paths)

Fate from console + `.ips`, never exit code (exit 2 = timeout-abort with the app alive).

| Item | Receipt |
|---|---|
| Shape | `--console --timeout 90 --terminate-existing -e '{"PS2X_CD_IMAGE":"…/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1"}'` + argv ELF path → exit 2 (alive, PID 4511), 44620 lines / 16.6 MB (sha `eb5191fd…`; delta vs I19's 45764 lines = −394 net sema + 39 creates) |
| CREATE-gate liveness (RECEIPT — H-b of the contract excluded) | **39 `[diag:sema-create]`** (ret=1..39 in order, 0 failures, 0 `noparam` drops) + full P1c set (5 `[diag:frame]` + 5 `[diag:threads]` + 30 `[diag:thread]` + 5 `[diag:stubs]` + 82 `[diag:stub]` + 5 `[diag:syscalls]` + 28 `[diag:syscall]` + 1103 `[diag:cd]` + 1062 `[cd:callback]` + 15083 `[diag:dormant]` + 22001 `[diag:sema]`) — every predicted line class present |
| Gate prior (why the probe was well-founded) | `diagSemaCreateEnabled()` gate @SY:16-23, emitters @SY:95-117; gate commit `de7ff17` IS an ancestor of the I18 build base `83fb4d6` (`merge-base --is-ancestor` clean) — the installed binary carries the gate compiled in |
| I19 wall | **Still gone — zero refs anywhere**: `guest-branch` 0, `missing-target` 0 |
| Boot prefix | K1 `armed` + `install#1–8` + `lookup#1–6` + `[sif-handshake]`; block-0 dump @line 18981 (I19: 18942 — shifted by the 39 create lines, as expected); no teardown |
| Crash-log record | Sleep + re-`ls` AND post-terminate re-`ls` (sleep 15): **5 files, all priors'** (I11–I15's own spin reports, 01:54–05:00 AM) — **NO new `.ips` for I20 AND no late filing for I19** (five briefs running with no filing; tabled, not root-caused) |
| Screenshot | 1 capture (cap), internal `/tmp` path first then `mv` (ExFAT owner warning only, file landed): `i20-shot1.png`, 2360×1640, 2.0 MB, app window foreground, status bar names `ps2EntryRunner`, full-black content (viewed from the landed copy) |
| Evidence-size handling | Full console 44620 lines / 16.6 MB EXCEEDS the 5 MB evidence cap → full log + 24622-line dedup stay complete on SSD (`W/logs/`, shas in the extract headers + `logs/launch-create-console.sizes`); evidence commits the deterministic 2708-line non-sema extract + COMPLETE 39-line create extract + 11851-line sema extract (all non-31 complete + id-31 head/tail samples + full-log per-id counts) + the 5 frame lines. Reproducible by the exact commands in §Exact commands |

### Census I — creators × ALL 39 sema ids (COMPLETE; the wait-set five starred)

All creates run through `pc=0x423da8` (CreateSema-gateway label). `ret` = assigned id (1..39 sequential, no gaps, no failures). Full 39-line transcript with line numbers in `logs/launch-create-console.create-extract.log`.

| Sema id | Creator tid | Creator ra (call site) | max / init | Console line | Traffic note (this probe) |
|---|---|---|---|---|---|
| 1 | 1 | `0x42c0fc` | 1 / 1 | 59 | 4 lines (take/release ×2, boot) |
| 2 | 1 | `0x42c10c` | 1 / 1 | 60 | SILENT (no wait/signal all run) |
| 3 | 1 | `0x3e56c4` | 1 / 1 | 75 | SILENT |
| 4 | 1 | `0x3e56c4` | 1 / 1 | 80 | 3584 lines (boot lock) |
| 5 | 1 | `0x3e56c4` | 1 / 1 | 97 | 2824 lines (boot lock) |
| 6–25 (×20) | 1 (all) | `0x3e35dc` (all) | 1 / 0 (all; #24 attr=263, rest attr=0) | 102–278 | 2 lines each (single take/release) |
| ★ 26 | 1 | `0x3e43c4` (CD-callback region: waiter ra `0x3e3c20` nearby) | 32 / 0 | 287 | 1473 lines; waiter t2, signalers t2/t3/t1 (Census II) |
| 27 | 1 | `0x3e56c4` | 1 / 1 | 293 | SILENT |
| 28 | 1 | `0x31a780` | 0 / 0 | 296 | SILENT |
| 29 | 1 | `0x31a7a0` | 0 / 0 | 297 | 413 lines (boot) |
| ★ 30 | 1 | `0x31a7c8` (thread-lib region: waiter `0x31aca4`, signaler `0x31acf4` nearby) | 1024 / 0 | 298 | 9 lines; waiter t3, signaler t1 (Census II) |
| ★ 31 | 1 | `0x31a858` (same region: waiter `0x31ac30`, vsync ra `0x31abf8` nearby) | 1024 / 0 | 300 | 10216 lines; waiter t4, vsync pump (Census II) |
| ★ 32 | 1 | `0x375d74` (signaler `0x377b6c` same `0x37xxxx` module) | 16 / 0 | 317 | 1231 lines; waiter t5, signalers t1/t5/int/t3 (Census II) |
| 33 | 1 | `0x375d88` | 1 / 1 | 318 | 1640 lines (boot lock) |
| 34 | 3 | `0x40c0c0` | 1 / 1 | 692 | 4 lines (boot) |
| 35 | 3 | `0x3c3344` | 20 / 1 | 4674 | 404 lines (boot) |
| ★ 36 | 3 | `0x3c1e04` (waiter ra `0x3c19f0` same module) | 1 / 0 | 4679 | 1 wait, NEVER signaled (Census II) |
| 37 | 3 | `0x3e56c4` | 1 / 1 | 5129 | SILENT |
| 38 | 3 | `0x3e56c4` | 1 / 1 | 14217 | SILENT |
| 39 | 1 | `0x3e56c4` | 1 / 1 | 14711 | 154 lines (boot) |

Creator-shape notes (tabled, not root-caused): 33 of 39 created by tid 1 (main) at lines 59–318, 6 more (5× tid 3 + 1× tid 1) through line 14711 — ALL before the block-0 dump (18981); the wait-set five are ALL `init=0` (start un-signaled — consistent with waiter parks); six ids never transact (2/3/27/28/37/38 — created, then silent); `count`/`attr` fields on the `0x3e56c4`-site rows carry large values (e.g. #4 `attr=4294972`, #34 `count=536870912`) — guest-passed struct bytes, tabled as-is.

### Census II — wait-set traffic re-confirmation + drift vs I19 (FULL-log counts)

| Sema | I20 waits / signals (× waker) | vs I19 | Standing |
|---|---|---|---|
| 26 | 737 / 736 (531 waker=2 + 183 waker=3 + 22 waker=1) | 737/736, IDENTICAL split | IDENTICAL |
| 30 | 5 / 4 (4 waker=1; full 9-line transcript in sema extract Part A) | 5/4 | IDENTICAL |
| 31 | 5109 / 5107-loose (5104 strict; 5041 waker=`-1` + 29 waker=3 + 1 waker=1 + damaged rest) | 5306/5306 (5269 `-1` + 29 w3 + 1 w1 + damaged rest) | DRIFT: −396 pump lines (wall variance — fewer vsync ticks in this probe's window); boot-phase non-`-1` split IDENTICAL (29+1) |
| 32 | 616 / 615 (206 waker=1 + 205 waker=5 + 175 waker=`-1` + 29 waker=3) | 616/615, IDENTICAL split | IDENTICAL |
| 36 | 1 / 0 (single t6 park) | 1/0 | IDENTICAL |
| Other ids | 1:4, 4:3584, 5:2824, 6–25:2 ea, 29:413, 33:1640, 34:4, 35:404, 39:154 (Part C) | 1:4, 4:3584, 5:2823, 6–25:2 ea, 29:414, 33:1640, 34:4, 35:404, 39:154 | DRIFT: id-5 +1 / id-29 −1 (opposite-sign ±1 on boot-phase lock traffic — tabled, not root-caused) |
| Totals | 11003 waits + 10998 signals = 22001 | 11200 + 11195 = 22395 | Δ −394 = −396 (pump) +1 (id-5) −1 (id-29) +2 (damaged-line delta: 4 unparseable `[diag:sema]` lines vs I19's 2 — DPI-splice class, quantified in Part B) |

### Steady-state re-confirmation (I19, identical sets unless noted)

| Check | I20 receipt | vs I19 |
|---|---|---|
| Thread rows (30) | 6/6 `status=2` all 5 blocks; t1 `waitReason=6 waitId=0 pc=0x3b1028 scheduled=8255→0,0,0,0`; t2/t3/t5/t6 `waitReason=2` waitIds 26/30/32/36 `pc=0x423de8`; t4 `waitId=31 scheduled=861→900,900,900,900` | IDENTICAL except t4 block-0 `scheduled` 861 vs 860 (1-count variance, tabled — third value in the I18 859 / I19 860 / I20 861 walk) |
| Stub sets | block-0 `distinct=1482`; blocks 1–4 `distinct=13` each, sets identical ×4 (same 13 targets + counts: 3×1800, 10×900) | IDENTICAL |
| Syscall sets | block-0 `distinct=30` (incl. `id=0x40 count=39` — the 39 CreateSema calls); blocks 1–4 `distinct=2` each (`0x44` WaitSema ×900 + `-0x43` iSignalSema ×900) | IDENTICAL shape (block-0 `0x40` row now cross-checks the create census) |
| Frame counters | ALL FIVE `[diag:frame]` readable: vsync 900→4500 (+900/block); kicks=43708 kicksDrawing=43356 gif=2795 copyRegs=4655 dma=4542 gifCopy=210 gsWrites=0 vifWrites=2 BIT-IDENTICAL blocks 0–4 | IDENTICAL values (deterministic boot; submission frozen) |
| CD timing | ALL 1102 `sceCdRead` (lines 96–15094) + ALL 1062 callbacks precede block-0 dump (18981); first `lbn=0x10`, last `lbn=0x13bb13` | IDENTICAL |
| MPEG dispatch | `0x402c08` ×6, `0x402a10` ×6 (dormant tails); `0x4029d0`/`0x3b0b10`/`0x3b0b40`/`0x3b06b0` ×0 | IDENTICAL (registration + GetPicture dispatched; producer never) |
| Tripwires | `without FFmpeg` ×0, `mpeg` (any case) ×0, `sceCdSt` ×0 in 44620 lines | IDENTICAL (no header fed; St path never entered) |

## Task 2 — fix-ready spec S1–S10 (F1–F10, E15-bound) + handoff

Consumes: the agreement table above (A1–A13), E15 §4 parked constraints (NB §4), E13 §5 shape (one generic runtime fix, no guest-PC special case, no MPEG-mutex-held delivery, stop at next missing link). Pins @`67c0a632`. This spec BINDS nothing itself — the E-lane MPEG brief owns the fork and the implementation.

| # | Element (from) | Implementation spec (file/line-pinned) |
|---|---|---|
| S1 | Files (F1) | ONE generic runtime fix in `ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp`: new `matchingNonStreamCallbacks` selector beside M:1141-1158 + new `dispatchGuestNonStreamCallback` beside M:1591-1630 + trigger call on the GetPicture-entry path (A4/P3 — the exact call site named in the fix diff, NOT Demux-entry, NOT vsync); decl changes in `Stubs/MPEG.h` ONLY if the trigger needs a cross-TU entry (else none); NO guest-PC special case, NO handwritten leaf, NO generated-source edit, NO map change (E13 §5) |
| S2 | Selection (F2) | Mirror `matchingStreamCallbacks` with `!callback.stream && callback.type == requestedType`; the requested type comes from the trigger's context (the OBSERVED cbData word0 — A3 — not hardcoded 1, generic across non-stream types, but per NB §4 other types/layouts must NOT be invented: only types actually observed with registered callbacks are serviced) |
| S3 | Delivery semantics (F3, E15-bound) | Mirror `dispatchGuestStreamCallback` (M:1591-1630) with E15-bound ABI: `hasFunction` guard (null slot = no invocation — A2); guestMalloc cbData carrying word0=type ONLY (A3 — do NOT assume the `0x20` stream layout M:1582-1586); regs a0=mpeg a1=cbdata a2=userdata (A2), supplied-RA = selector continuation; `sp=0` async-stack backfill iff the invocation path needs it (S:1761-1764); queue kind + ownership SUBJECT TO THE A5 AUDIT (NB §4: prove `queueInvocation`/`RpcCallback` preserves caller-thread ownership, or deliver synchronously in the GetPicture caller — matching arguments alone is insufficient); cbData freed in `onComplete` (M:1625-1628 pattern); callback v0 DISCARDED (A3/A13 — no EOF inference, no branch) |
| S4 | Locking / re-entrancy (F4) | NEVER invoke while holding `g_mpeg_stub_mutex` (the callback re-enters via AddBs → same mutex, M:1898; the original calls AddBs synchronously from the callback path — A8): collect-then-dispatch — build the event list under the lock (Demux pattern, M:2108-2128), dispatch AFTER unlock (M:2167/2261 pattern). Preserve request ordering (registration order); dedupe: `hasInvocation(RpcCallback, tag)` (S:1791-1803) or a pending-delivery flag per (mpeg,type) with tag = callback handle — no duplicate/reentrant deliveries while one is queued |
| S5 | Cancellation / deletion (F5) | `sceMpegDelete` (M:2088-2100) MUST invalidate pending non-stream deliveries for the erased mpeg (erase-then-complete-`KE_WAIT_DELETE` exists — extend the erase to the pending-delivery set); the GetPicture resume's negative-`v0` terminal path (M:2340-2343) already handles the post-delete wake; teardown (reset/init) clears the pending set with the callbacks (M:1773) |
| S6 | No sema change (F6, census-closed) | The sema waits are GUEST-orchestrated producer/consumer handshakes — creators now NAMED (26/30/31/32 by tid-1 boot @ras `0x3e43c4`/`0x31a7c8`/`0x31a858`/`0x375d74`; 36 by tid-3 boot @`0x3c1e04`; all `init=0` — Census I): threads 1/3/interrupt ARE the signalers during boot; they stall because the producers stall on the SAME undelivered MPEG input, not because the sema implementation is wrong. NO `EeScheduler` sema change. The fix brief re-probes to confirm the sema chain unblocks with MPEG |
| S7 | Cause-B sequencing (F7, split-carried) | The fix brief does NOT flip `PS2X_ENABLE_FFMPEG` for iOS and does NOT change the stub decoder: per E13 §5's stop rule, if delivery now occurs but decode fails (stub `feed()` → `false` → silent retry, M:1107-1114), the fix brief names "no on-device MPEG decode" as the first demonstrated missing link and STOPS (its own brief: FFmpeg-for-iOS build? stub-frame completion? — not this spec's call). The host FFmpeg-ON side (A11) is unexercised and stays out of the device verdict |
| S8 | Regression tests (F8, extended) | Extend `ps2xTest/src/ps2_runtime_expansion_tests.cpp` (MiniTest; file identical @`67c0a632`; existing MPEG cases T:484/:525/:723/:756 + fixtures T:176-196/:225-287): R1 non-stream register→trigger→delivery (fail-before: never invoked); R2 AddBs re-entry from inside the delivered callback (no deadlock — S4); R3 wait completion via delivered-input frames (GetPicture resumes); R4 valid-no-input return (producer returns without AddBs → waiter NOT spuriously completed — v0 discarded per S3); R5 teardown during pending delivery (delete/reset → no dispatch, no use-after-free, waiter completes `KE_WAIT_DELETE`); R6 stream-callback behavior RETAINED (existing :525 case green, unmodified). PLUS: E15's actual-wrapper `no-input` + `input` cases (ER §3) must be rc1 fail-before at the fix brief's checkpoint and flip green with the fix (NB §4: request order, no-input, delivery, completion, cancellation/lifetime); E13 §5 regressions stay green; E16's teardown/duplicate-exit closure cases (NB §2) must remain green (closure repair lands FIRST — handoff row H3) |
| S9 | Re-probe (device, I-lane; F9 minus census) | Rebuild + reinstall + 90 s `PS2X_DIAG_PERIOD_MS` probe: expect main past `0x3b1028` (or a NAMED successor state), `0x4029d0`/`0x3b0b10` in stub sets, stub-decoder warning present (Cause B now the wall — S7), sema 26/30/32 traffic past boot. Creator re-census NOT needed (CLOSED in I20 — Census I); keep `PS2X_DIAG_SEMA_CREATE=1` in the env anyway (zero-cost cross-check) |
| S10 | Stop (F10) | First demonstrated missing link AFTER delivery (decode? EOF? a later guest edge?) names the next brief; NO stacking a second fix, NO routing around a guest-side gate (E13 §5); NO MPEG work inside E16 (NB orders closure repair only) |

### Handoff table (what the E-lane MPEG brief consumes / stays / E16-first)

| # | Item | Disposition |
|---|---|---|
| H1 | This spec S1–S10 + agreement A1–A13 + P1–P3 receipts | CONSUMED by the E-lane MPEG brief (a LATER E brief per NB + the no-stacking precedent — tabled here, not jumped) |
| H2 | E15's actual-wrapper fixtures (`no-input`/`input`, ER §3) + NB §4 parked constraints | CONSUMED as the fix brief's fail-before gate + design constraints (ownership audit, mutex-free dispatch, type-1-only trigger, no invented layouts) |
| H3 | E16's closure repair (NB §§1-3: run-exit closure, idempotent destructor fallback, non-title fixture, guarded closure probe) | MUST LAND FIRST — the MPEG brief starts only after E16's closure + probe complete; no MPEG behavior edit inside E16 |
| H4 | FFmpeg-OFF stub residual (A11/S7) + `decoderFailed`-never-true + St-path-never-entered | STAYS device-side (separate edge; the fix brief STOPS here per S7 if delivery lands but decode fails) |
| H5 | Sema creator census (Census I) + steady-state baselines (Census II + re-confirmation) | STAYS as the I-lane device baseline the fix brief's re-probe (S9) diffs against |
| H6 | E-lane fork ownership + remote moves | E-lane ONLY — I20 moved nothing (remote `67c0a632` at recon AND end; 0 commits, 0 pushes) |

### Worktree record (read-only; zero commits expected, zero made)

| Item | Receipt |
|---|---|
| Pin (MOVED with cause) | `67c0a632` = `67c0a632d44cad8c0e47b4e2c0ee3782b22fd467` (E15 observation commit; cause = agreement + spec must bind the tree the E-lane MPEG brief consumes) |
| Remote HEAD (tabled, never moved) | `git ls-remote fork ssx3` = `67c0a632` at recon AND at end (E-lane advanced exactly 1 commit before I20: E15 landed/pushed) |
| Move delta | `diff --stat 83fb4d6 67c0a632` = exactly 5 files (ps2_e15.h +115, ps2_e4.h +3, ps2_e7.h +33/-5, EeScheduler.cpp +16, ps2_runtime.cpp +17/-1); `MPEG.cpp`/`MPEG.h`/`Sync.cpp`/expansion-tests byte-identical (`diff --quiet` clean) |
| E-lane owner | Live — shared `ssx3` @`67c0a63` with `M register_functions.cpp` (398971 insertions — preexisting generated-registry dirt per ER §8, untouched) + `?? ps2_log.txt`; pane never prompted/steered |
| Worktree | `git -C FORK worktree add --detach W/fork-wt 67c0a632` → `HEAD is now at 67c0a63` (exit 0); ZERO ports (no build ⇒ no ports); ZERO commits; `status` clean at end |
| Shared-clone contact | One `worktree add` + read-only `ls-remote / log / status / worktree list / diff / show / merge-base`; no checkout/pull/stash/build; the `._pack-*.idx` sidecars inside shared `.git` left alone (owner's tree; the `non-monotonic index` stderr noise tabled, outputs unaffected) |

## Exact commands

```sh
# --- Recon (E-lane live; read-only) ---
FORK="/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp"; W="/Volumes/Extreme SSD/ps2x-i20"
git -C "$FORK" ls-remote fork ssx3          # 67c0a632 at recon AND end (E15 landed/pushed)
git -C "$FORK" log --oneline -3 2>/dev/null # 67c0a63 at top (Diagnostics: trace MPEG requests...)
git -C "$FORK" status --short 2>/dev/null   # M register_functions.cpp + ?? ps2_log.txt (preexisting dirt)
git -C "$FORK" worktree list 2>/dev/null    # shared @67c0a63 [ssx3] + all prior I-lane WTs
P="00008112-001224302184A01E"
xcrun devicectl list devices --timeout 30   # iPad connected, UDID confirmed
xcrun devicectl device info lockState --device "$P" --timeout 30
xcrun devicectl device info apps --device "$P" --timeout 60 | grep -iE "ps2|MF1"
xcrun devicectl device info processes --device "$P" --timeout 60  # 581 lines, PID 4396 = I18 leftover
# --- Worktree at HEAD (NO ports, NO commits) ---
export COPYFILE_DISABLE=1; mkdir -p "$W/logs" local/research/I20/logs
git -C "$FORK" worktree add --detach "$W/fork-wt" 67c0a632
WT="$W/fork-wt"; git -C "$WT" status --short  # clean (at add AND end)
git -C "$FORK" diff --stat 83fb4d6 67c0a632 # exactly E15's 5 files
git -C "$FORK" diff --quiet 83fb4d6 67c0a632 -- ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp ps2xRuntime/src/lib/Kernel/Stubs/MPEG.h ps2xRuntime/src/lib/Kernel/Syscalls/Sync.cpp && echo MPEG-IDENTICAL
git -C "$FORK" log --oneline -S'PS2X_DIAG_SEMA_CREATE' --all  # de7ff17 (gate commit)
git -C "$FORK" merge-base --is-ancestor de7ff17 83fb4d6 && echo GATE-IN-83FB4D6
# --- Task 1b: ONE config-only probe (installed I18 app, CREATE added) ---
B="/private/var/containers/Bundle/Application/33603E5F-978B-4D3D-A06B-6270872BC82A/ps2EntryRunner.app"
xcrun devicectl device process launch --device "$P" --timeout 90 --console --terminate-existing \
  -e '{"PS2X_CD_IMAGE":"'"$B"'/SSX3.iso","PS2X_DIAG_PERIOD_MS":"15000","PS2X_DIAG_SEMA":"1","PS2X_DIAG_SEMA_CREATE":"1"}' org.ps2x.ps2entryrunner "$B/SLUS_207.72" \
  >"$W/logs/launch-create-console.log" 2>&1    # exit 2 (alive, PID 4511), 44620 lines / 16.6 MB
L="$W/logs/launch-create-console.log"
grep -c "diag:sema-create" "$L"              # 39 (creator census: H-a)
grep -c "diag:sema]" "$L"                    # 22001 (ownership re-confirmation)
grep -c "guest-branch\|missing-target" "$L"  # 0 (no wall)
grep -n "diag:sema-create" "$L"              # full 39-line creator transcript
for id in 26 30 31 32 36; do echo "== $id"; grep -c "op=wait id=$id " "$L"; grep -c "op=signal id=$id " "$L"; done
grep "op=signal id=26 " "$L" | grep -oE "waker=-?[0-9]+" | sort | uniq -c   # per-id waker splits (x5 ids)
grep -oE "op=(wait|signal) id=[0-9]+" "$L" | grep -oE "id=[0-9]+" | sort -t= -k2 -n | uniq -c  # Part C
sleep 10; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i20 -s ps2EntryRunner --no-recurse  # 5 files, all priors
xcrun devicectl device capture screenshot --device "$P" --timeout 60 --destination /tmp/i20-shot1.png
mv /tmp/i20-shot1.png "$W/logs/"
xcrun devicectl device process terminate --device "$P" --timeout 30 --pid 4511  # cleanup only
sleep 15; xcrun devicectl device info files --device "$P" --timeout 60 \
  --domain-type systemCrashLogs --domain-identifier ps2x-i20 -s ps2EntryRunner --no-recurse  # still 5
# --- Task 1b: steady-state census ---
grep -h "\[diag:thread\]" "$L"               # 30 rows (t4 block-0 861 vs I19 860)
grep -h "diag:frame" "$L"                    # 5 lines, counters bit-identical
grep -c "sceCdSt" "$L"; grep -c "without FFmpeg" "$L"; grep -ciE "mpeg" "$L"  # 0/0/0 tripwires
for a in 0x4029d0 0x402a10 0x402c08 0x3b0b10 0x3b0b40 0x3b06b0; do printf "%s: " "$a"; grep -c "$a" "$L"; done
# --- Tasks 1a+2: pin verification (all read-only; M=MPEG.cpp S=EeScheduler.cpp SY=Sync.cpp) ---
git -C "$FORK" show 67c0a632 -- ps2xRuntime/src/lib/Kernel/EeScheduler.cpp  # +16 gated observation calls
sed -n '472,480p;1141,1158p;1929,1943p;2318,2346p' M   # A2/A1/A10 ranges @67c0a632
sed -n '1746,1803p;2077,2122p' S                       # S: re-pins @67c0a632
grep -n "tc.Run" T | grep -i mpeg                       # T:484/:525/:723/:756 (unchanged)
# --- Evidence extracts (deterministic) ---
grep -v "GetWindowScaleDPI" "$L" | grep -v "diag:dormant" > "$W/logs/launch-create-dedup.log"  # 24622 lines
grep -v "diag:sema" dedup >> diag-extract (2708 lines + header)
grep -n "diag:sema-create" full >> create-extract (COMPLETE 39 + header)
grep "diag:sema]" dedup | grep -v "id=31" >> sema-extract Part A (complete non-31)
id=31 head/tail-10 xwait/signal >> Part B; full-log per-id counts >> Part C
shasum -a 256 "$L" "$W/logs/launch-create-dedup.log"
find local/research/I20 -name "._*" -delete; find local/research/I20 -name "._*" | wc -l  # 0
```

## New gap rows (each with the exact next brief it needs)

| # | Gap | Proving line | Exact next brief needed |
|---|---|---|---|
| G1 | E16's closure repair unlanded at I20 close (remote still `67c0a632`; shared tree shows no E16 files yet — only preexisting dirt) | End-of-brief `ls-remote` + shared-clone `status` | No brief — E16 (already briefed per `[orch]` commit) lands closure repair first; the MPEG brief follows |
| G2 | Fix-brief ownership audit (A5): whether `queueInvocation`/`RpcCallback` preserves caller-thread ownership is UNPROVEN either way | NB §4 demands the audit; I20 tables both shapes, proves neither | The E-lane MPEG brief (spec S3 gates dispatch shape on it) |
| G3 | No on-device MPEG decode (stub `feed()` → `false`, silent retry; `decoderFailed` never true) sits BEHIND the delivery fix | Census II + tripwires (warning ×0 again — no header ever fed) | The fix brief STOPS here per S7/E13 §5 if delivery lands but decode fails — its own follow-up brief |
| G4 | NO new `.ips` five briefs running (5 files, all priors' — I11–I15 each filed one spin report; I16–I20 file none) | `logs/crashlog-check.log` (sleep + re-`ls` AND post-terminate re-`ls`: still 5; no late I19 filing) | Informational — consistent with a non-spinning waiter; next brief's first `ls` confirms I20; no brief unless a later probe shows action-taken |
| G5 | id-5 +1 / id-29 −1 opposite-sign boot-phase variance vs I19 | Census II drift row (Part C both probes) | Informational — no brief; the fix brief's re-probe (S9) either reproduces or washes it out |
| G6 | Bundle-resource ELF dir is read-only; derived `mc0`/hostRoot writes untested | `configureIoPathsFromElf` (I9); guest still in movie/sema wait | Data-container brief (only if a later probe fails on file I/O) |

## Receipt paths

- `local/research/I20/REPORT.md` (this file)
- `local/research/I20/logs/launch-create-console.diag-extract.log` (2708-line deterministic non-sema extract + header with full-log sha)
- `local/research/I20/logs/launch-create-console.create-extract.log` (COMPLETE 39-line creator transcript + header)
- `local/research/I20/logs/launch-create-console.sema-extract.log` (11851-line sema extract: complete non-31 + id-31 samples + full-log counts)
- `local/research/I20/logs/launch-create-frame.log` (5 frame lines), `launch-create-console.sizes` (counts + shas)
- `local/research/I20/logs/processes-pre.log` (581 lines, PID 4396), `logs/crashlog-check.log` (check1 + check2, still 5 priors), `logs/screenshot.log`
- `local/research/I20/logs/i20-shot1.png` (iPad window, black content)
- `W/logs/` (same + full 44620-line console + full dedup on SSD); `W/fork-wt/` (worktree @ `67c0a632`, clean, 0 local commits, 0 pushes); NO build tree, NO signed app, NO codegen dir
- No fork push this brief (nothing to push — zero commits by design)

## What I could not do

- Implement or test the fix — explicitly out of brief (spec S1–S10 only, zero code changed anywhere; E-lane owns the fork and NB orders E16 first).
- Prove the A5 ownership audit either way — `queueInvocation`/`RpcCallback` vs caller-thread delivery is tabled as the fix brief's gating audit (G2).
- Bind the HLE cbData allocation or invocation shape — A1–A3/A13 give the fix brief every receipt it needs, but the binding is the fix brief's (P1 row).
- Name the exact HLE trigger call site — A4/P3 narrow it to the GetPicture-entry path (not Demux-entry, not vsync); the fix diff names the line.
- Observe the dynamic MPEG request path on device — all `[MPEG:*]` stub logs are `PS2_IF_AGRESSIVE_LOGS`-gated (compiled out); the host side (E15 dynamic) now covers it.
- Verify E16 agreement — E16 has not landed (G1; H3 handoff tabled for the MPEG brief that follows it).
- Read ~40 DPI-spliced sema lines' tail fields (4 unparseable `[diag:sema]` lines + ~34 id-31 lines lacking waker digits) — the vsync-pump census carries ±splice caveats; counts use full-log numbers with the damage quantified.
- Present a guest frame — window stays black with the guest in MPEG/sema waits and GS submission frozen since boot; first presented content awaits the MPEG fix + Cause-B sequencing (S7).
- Symbolicate to source lines — Release without `-g`/dSYM (unchanged from I8–I20); no crash occurred anyway.
- Verify on-device bytes directly — `devicectl` has no bundle-listing domain; paths re-proven by the same-UUID relaunch working (exit 2 + full console).
- Test `mc0`/CD-write/file-I/O behavior — the guest never observably reached file I/O past the boot CD reads (G6).
- Explain why no `.ips` filed five briefs running — sleep + re-`ls` AND post-terminate re-`ls` both show 5 files (all priors'); the non-spinning waiter profile is consistent but not proven causal (G4).
- Re-run a second probe for determinism — single 90 s probe per the brief's recipe and I-series precedent; blocks 1–4 identical steady sets are the in-probe determinism receipt.
- Name the launcher of pre-launch PID 4396 — the I18 bundle was running though I19 reported 0 `ps2` at its cleanup (fifth brief running with a relaunched occupant); it was reaped by the launch without investigation.

## TAIL RECEIPT

Report written in 5 chunks (header + contract + caps; agreement A1–A13 + P1–P3; probe + census I–II + steady-state; spec S1–S10 + handoff H1–H6; worktree + commands + gaps + receipts + could-not-do). Pre-receipt measure: 288 lines total, sha256 `e43385c231f20b8b2c76a92d63ef93b25e0b4f4f03a5280ce859bb94395450aa` over lines 1–288 (everything before this `## TAIL RECEIPT` section).
Tail content line: "Name the launcher of pre-launch PID 4396 — the I18 bundle was running though I19 reported 0 `ps2` at its cleanup (fifth brief running with a relaunched occupant); it was reaped by the launch without investigation." This receipt line ends the report. END-I20-REPORT.
