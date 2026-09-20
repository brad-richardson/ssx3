# T18 report — Brief 2: runtime EE-syscall trace channel + trace_align.py + first boot-phase alignment

Brief `local/muse/prompts/T18.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T4/REPORT.md` (all of it —
Devel PCSX2 v2.9.75 reference, 7,483,481-line 4-channel trace to
language-select, §T4-2 format notes, `samples.txt`, `census-final.txt`)
+ `docs/research/review-2026-09-19-progress.md` §12 T4 row (Brief 2 =
runtime trace channel + `tools/trace_align.py`) + `local/research/P1x/
REPORT.md` (channel survey + capture recipe) + `local/research/T13/
REPORT.md` (ladder style) + `local/research/T16/REPORT.md` (boot recipe,
latest state) + `local/muse/prompts/T17.md` (concurrent deeper trace).

`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`), `REF=/Volumes/Extreme SSD/pcsx2-ref` (PCSX2 source @ `1275b25a`,
read-only). `$R`-relative paths below unless noted. No `adb`.

Headline readings: additive fork channel (`TraceChannel.{h,cpp}` + 1 hook
call, fork `f2b1852`) emits 781,372 EE-syscall events in PCSX2 `Bios call:
NAME (hex)` byte shape over a 240 s proof boot; ladder (channel-off vs
channel-on, T9 `ladder_diff.py` + T13-style log series) shows identical
guest behavior modulo wall-phase samples (1053 exact, 245 tol-ok ≤0.5%,
1 live-counter phase sample, key-sets exact everywhere). `tools/
trace_align.py` (selftest 17/17) aligns the T4 reference with the runtime
stream to first divergence k=2: RFU060/RFU061 agree, then reference
continues BIOS DMA/SIF init while the HLE runtime continues CreateSema;
no 20-shingle re-alignment anywhere (runtime GetThreadId density 37% vs
~0%). T17's deeper trace (`emulog-t17c.txt`) landed mid-run and plugs
into the tool unchanged, reproducing the boot3 alignment byte-exact.

## T18-0. Rule record

| Item | Value |
|---|---|
| ssx3 HEAD at T18 start | `5f881a2`-era tree; first read 15:32Z; T17 (`5f7057e`) + P1ak landed mid-run (offline, no P-lane interaction) |
| ssx3 HEAD at commit | `5f7057e` pre-commit (`[T17] …`) |
| Fork HEAD at T18 start | `7eed783` + `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched throughout) |
| Fork HEAD at boot/commit | `f2b1852` (`Trace: EE-syscall trace channel … (T18)`, this brief; ladder held so committed per brief) |
| Fork commits by T18 | 1 (`f2b1852`, 3 files, +170); fork `git pull/push`: never run |
| Sidecars | 13 before, 13 after (`find $R -name "._*"`; 3 mine created + removed mid-run) |
| Lease | `/tmp/ssx3-p-lane-lease`, held 506 s, zero contention (absent at claim; waits log 4 lines, no WAIT) |
| Boots | 2 of 2 used, 240 s caps (≤600 s), boot-phase only, rc=0/0, script exit 241/241 |
| Builds | 1 (`-j4`, lease-free); no `adb`; `git push` in ssx3: never run |
| Wall | 2026-09-20 ~15:32–15:55Z (~0.5 h active), inside the 6 h box |
| ssx3 evidence commit | below (`[T18]`, trailer `Orchestrated-By: Muse Code`, no push) |

Lease record (`$W/P1/run/t18-waits.log`, 4 lines):

| Event | Value |
|---|---|
| T18 pre-claim checks (15:41:03Z) | Lease absent; `pgrep -x ps2EntryRunner` exit 1; sha `a2a2f660…` 163464224 B; ISO 3005415424 B + ELF 3890784 B present; 515 Gi free; t16-waits tail = released |
| T18 claim | `printf 'T18\n' > /tmp/ssx3-p-lane-lease` 15:41:07Z |
| T18 BOOT-OFF | start ~15:41:10Z end 15:45:12Z (240 s cap, SIGTERM rc=0, script exit 241) |
| T18 BOOT-ON | start ~15:45:15Z end 15:49:23Z (240 s cap, SIGTERM rc=0, script exit 241) |
| T18 release | 15:49:33Z (held 506 s); verified absent; `pgrep -x` exit 1 |

## T18-1. Task 1 — channel + ladder + aligner

### Channel table

| # | Item | Receipt |
|---|---|---|
| 1 | Flag | `PS2X_TRACE_SYSCALLS=<path>`; unset/empty = off (one cached-bool check per dispatch); open-failure prints `[trace:syscalls] open FAILED` to stderr and stays off |
| 2 | Emission point | First statement of `dispatchNumericSyscall` (`Syscalls/Dispatcher.cpp:89`), before override check + diag tick + switch — same order as PCSX2 (log before switch, `R5900OpcodeImpl.cpp:917`) |
| 3 | Single choke | Only production caller is `PS2Runtime::handleSyscall` (`ps2_runtime.cpp:1871`); recompiled SYSCALL instructions all route there (`special_translator.cpp:44`, encoded `(raw>>6)&0xFFFFF` or `$v1`) |
| 4 | Files | New `Syscalls/TraceChannel.h` (14 lines) + `Syscalls/TraceChannel.cpp` (128-name table + gated sink); 1 include + 1 call line in `Dispatcher.cpp` (diff in §T18-0 fork commit; no CMake edit — `KERNEL_SRC_FILES` glob picks it up) |
| 5 | Line format | `[%8.4f] Bios    : Bios call: %s (%x)\n` — ts = seconds since channel open; file opened `"w"`, `_IOLBF` (SIGTERM-safe, no handler); mutex around write |
| 6 | Call derivation | Replicates PCSX2 `SYSCALL()` (`R5900OpcodeImpl.cpp:906-917`): `(int32)id < 0 ? (u8)(-id) : (u8)(id)`; matters: runtime issues negative ids (e.g. `0xffffffbd` = −0x43 → logged `(43)` like PCSX2) |
| 7 | Sink receipt | ON boot log carries `[trace:syscalls] open path=…/syscalls-t18-on.txt`; OFF boot log carries no `trace:syscalls` line |

Name-table mirror (`/tmp/t18-table-check.py` receipt):

| Check | Result |
|---|---|
| Channel `kEeBiosNames[128]` vs PCSX2 `R5900::bios` (`REF pcsx2/R5900OpcodeImpl.cpp:84`) | 128/128 match, 0 mismatches |
| All 42 T4 `census-final.txt` EE names + hex vs channel table | 42/42 match |
| `≥0x80` fallback (`RFU%03d`, decimal PCSX2-RFU convention; PCSX2 table is null there) | Fired 21×, all `RFU252 (fc)` = runtime 0xFC SetAlarm path (diag `id=0xfc` count 21 agrees); no other fallback lines |

Byte-shape vs T4 samples (ts-normalized; ts is host-wall both sides):

| Side | First line (verbatim) |
|---|---|
| Reference (`emulog-boot3.txt:138641`) | `[    0.5503] Bios    : Bios call: RFU060 (3c)` |
| Runtime (`syscalls-t18-on.txt:1`) | `[  0.0000] Bios    : Bios call: RFU060 (3c)` |

Format-checker zeros (`trace_align.py --format-check`: `%x` canon,
`[…] Bios    : Bios call:` prefix, ts monotonicity):

| File | Events | bad_hex | bad_ts_prefix | ts_regressions | Exit |
|---|---|---|---|---|---|
| `emulog-boot3.txt` (T4, 528,683,584 B) | 899,875 (= T4's count) | 0 | 0 | 0 | 0 |
| `syscalls-t18-on.txt` (37,348,669 B) | 781,372 | 0 | 0 | 0 | 0 |
| `emulog-t17c.txt` (T17, 540,313,630 B) | 914,791 | 0 | 0 | 0 | 0 |

### Build table

| # | Item | Receipt |
|---|---|---|
| 1 | Command | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner -j4` (`/tmp/t18-build.log`), exit 0 |
| 2 | Glob pickup | Log line 4 `+…/TraceChannel.cpp`, line 177 `TraceChannel.cpp.o` built (no configure edit) |
| 3 | Binary | `a2a2f660f6ffb2ac2b987982e7dd42cb02912ab08089b033c655a1a8006d724d`, 163,464,224 B (+3,952 B vs T11–T16 `81bee6c5…` 163,460,272 B) |
| 4 | Symbols | `strings` finds `PS2X_TRACE_SYSCALLS` + 2× `trace:syscalls` |
| 5 | Warnings | 29 lines, 0 from new files (pre-existing: runner `-Warray-bounds`, `ps2_gs_memory.h -Wswitch`, CMake dep notices); zero `FAILED`/`error:` |

### Ladder table (channel-off vs channel-on, 240 s caps)

Boot artifacts:

| Item | OFF | ON |
|---|---|---|
| Log | `boot-t18-off.log`, 516,026 lines, 92,549,633 B, sha `19f57bac…b4b1e` | `boot-t18-on.log`, 518,344 lines, 92,943,027 B, sha `3859c699…ef5b08` |
| Snapshot | `park-t18-off/`, 111,627 + 7,613 B, json sha `42519191…92dc4` | `park-t18-on/`, 111,641 + 7,627 B, json sha `549bd1c7…d21f` |
| Trace | n/a (flag unset) | `syscalls-t18-on.txt`, 781,372 lines, 37,348,669 B, sha `88852184…58850` |
| 394ED0 trace | OVERWRITTEN by ON boot (gap G1) | `ps2_log-t18-on.txt`, 1,387,485,353 B |
| `[diag:park]` lines in log | 1 | 1 |

Snapshot ladder (`$R/tools/ladder_diff.py off on`, exit 1, full table in
`ladder.txt`, 1,306 rows):

| Verdict | Count | Detail |
|---|---|---|
| EXACT | 1053 | All parked-thread status/pc; all sema max/init; sema creates 37-row multiset; all key-sets (wait/signal hist keys, hotpc keys, rpc, drops); `rpc.bind/call/load/sendcmd`; `drop.syscall/dispatchSyscallOverride.KE_ERROR` 6/6 |
| TOL_OK (tol 10%) | 245 | ALL ≤0.5%: hotpc 222, sema hists 13, gs 6, sched 4; every pump counter higher on ON by the same ~0.5% (wall-progress, not behavior) |
| SAMPLED | 5 | `thread.1.status/pc`, `thread.5.status` (live-thread SIGTERM phase) + correlated `sema.29/sema.32` waiter presence (off none vs on t1→sema29 / t5→sema32) |
| KEY_DELTA | 1 | `sema.33.table` count 0 vs 1 (max/init/waiters 1/1/0 agree; see row below) |
| COUNT_DELTA / BLIND / missing keys | 0 | — |

`sema.33` row (the single delta): binary pump sema (max 1, init 1).
Cumulative histories agree within wall tolerance (waits 57118/57395,
signals 57117/57395, both TOL_OK 0.5%), and both snapshots are
internally consistent (`count = init + signals − waits`: OFF
1+57117−57118=0, ON 1+57395−57395=1). The 0-vs-1 is the SIGTERM-phase
sample of a live 0/1 counter: OFF caught it post-wait, ON post-signal.

Log ladder (`/tmp/t18-ladder-logs.py`, T13 style):

| Row | OFF | ON | Reading |
|---|---|---|---|
| `[diag:syscalls]` blocks | 47 | 47 | distinct-series identical all 47 (`29,7,6×45`) |
| `[diag:stubs]` blocks | 47 | 47 | series identical all 47 (`b0=973 b1=491 b2–46=222`; 222-phase by block 2 both sides) |
| Syscall id-set | 21 ids | 21 ids | zero one-sided either way |
| Rare ids (≤37 hits, 15 ids) | — | — | ALL ratio exactly 1.0000 (0x10/0x14/0x15/0x20/0x22/0x29/0x3e/0x40/0x41/0x4a/0x4b/0x5b/0x6f/0x74/0xfc) |
| Pump ids (6 ids) | 767,430 agg | 768,726 agg | uniform ratio 1.0017 on every pump id (0x2f/0x42/0x44/0x45/0x64/−0x43) |
| Drops | 6, 1 key | 6, 1 key | keys equal |
| Boot scripts | `/tmp/t18-boot-off.py` | `/tmp/t18-boot-on.py` | both `sed` from `/tmp/t16-boot1.py`: LOG + `SECS 7200→240` + docstring + PARK env (+ TRACE path on ON only); diff-verified |

Diag-vs-trace cross-check: diag aggregate 768,726 vs channel 781,372
(diff 12,646) = per-block top-20 print truncation by source
construction (`Dispatcher.cpp:79` `i < 20u`; block 0 has distinct=29).
The channel is the complete count; the diag is the ladder series.

### Aligner table (`tools/trace_align.py`, committed with evidence)

| # | Item | Receipt |
|---|---|---|
| 1 | Inputs | `REF RT` (streaming; 528 MB reference parses without full copy) + `--ref-after NAME[:OCC]` (default `ExecPS2:2`) + `--rt-after` (default `none`) + `--window/--locate/--census/--context` |
| 2 | Outputs | `ref/rt` event counts → `anchor` table → `name-table` mismatch rows → `divergence` (k, both events, ±context) or `bound` table → optional `locate` + `census` |
| 3 | Key rule | Compare syscall NUMBERS; numbers-equal/names-differ = name-table row, never a divergence (EE lines carry no args/returns either side — order + names + numbers only) |
| 4 | Exit codes | 0 = no divergence in window (bound tabled); 1 = divergence; 2 = usage/anchor-miss/format/selftest failure |
| 5 | Selftest | `--selftest`: t1 identical→0, t2 grafted→1 naming k=3 + both names, t3 anchor-skip→`HIT ev:4`, t4 miss→2 + MISS table, t5 alias-name→0 + mismatch row, t6 format good/bad→0/2, t7 locate→`ref ev:2`, t8 short→0 + `rt-exhausted`; 17/17 PASS |
| 6 | Selftest catch | t7 exposed a real bug (`bytes(array('I'))` reinterprets memory → `IndexError`); fixed via list conversion + naive fallback; selftest re-greened before use |

## T18-2. Task 2 — first boot-phase alignment

Full outputs: `align-boot3.txt` (74 lines, exit 1), `align-t17c.txt`
(25 lines, exit 1).

### Anchor table

| Anchor | Reference (`emulog-boot3.txt`) | Runtime (`syscalls-t18-on.txt`) |
|---|---|---|
| `ExecPS2` ×2 | HIT: file 142369/142465, ev:162 (post-anchor EE events 899,713; next `RFU060 (3c)` @142534) | MISS: 0 occurrences in 781,372 events (HLE kernel: no BIOS/loader executes `ExecPS2`; game boots straight into ELF code) |
| First vblank | HIT: file 417152 `vblank.004: WaitVblankStart` (= T4's number) | Structural miss: vblank is IOP-side (`IOP.Bios`); the EE channel cannot emit it by construction |
| Effective alignment | `--ref-after ExecPS2:2` (game-code start) vs `--rt-after none` (ELF entry) | same |

### Sequence table

| # | Probe | Result |
|---|---|---|
| 1 | Agreement run from alignment start | 2 events: `RFU060 (3c)`, `RFU061 (3d)` (ref file 142534–142535 ev 162–163; rt file 1–2 ev 0–1) |
| 2 | Name-table concordance over 781,372 compared events | 0 mismatches |
| 3 | `--locate 20` rt opening shingle in ref post-start | NOT FOUND |
| 4 | `--locate 20` rt ev-1000 shingle (1.74 s, GetThreadId/SignalSema pump) in ref | NOT FOUND |
| 5 | `--locate 20` rt ev-500000 shingle (153.02 s, steady pump) in ref | NOT FOUND |
| 6 | Mechanism for 3–5 | Runtime GetThreadId density 37% (290,210/781,372) vs reference 2 post-start: any 20-shingle carries a GetThreadId pattern the reference never contains |

### Divergence table (first divergence)

| Item | Reference side | Runtime side |
|---|---|---|
| k | 2 (agreement run before it: 2) | 2 |
| Event | `AddDmacHandler (12)` @file:142536 ev:164 | `CreateSema (40)` @file:3 ev:2 |
| k+1 | `_EnableDmac (16)` @142537 ev:165 | `CreateSema (40)` @file:4 ev:3 |
| k+2 | `sceSifGetReg (7a)` @142538 ev:166 | `GetOsdConfigParam (4b)` @file:5 ev:4 |
| k+3 | `sceSifSetDma_isceSifSetDma (77)` @142539 ev:167 | `SetOsdConfigParam (4a)` @file:6 ev:5 |
| Shape | BIOS DMA/SIF init sequence (continues into the 260k `sceSifGetReg` storm) | HLE kernel skips BIOS init; game allocates semas + reads OSD config |

### Census highlights (post-start; full side-by-side in `align-boot3.txt`)

| Name | Ref | Rt | Note |
|---|---|---|---|
| GetThreadId | 2 | 290,210 | HLE re-queries per dispatch; BIOS-side caches |
| WaitSema / SignalSema | 203,790 / 158,167 | 231,157 / 187,698 | Shared pump shape, both sides' top-3 |
| iSignalSema / PollSema | 68,529 / 45,491 | 43,453 / 14,350 | Shared, different mix |
| sceSifGetReg / +SIF DMA/chain/reg | 260,722 / ~1,900 | 0 / 0 | Reference-only: EE↔IOP SIF storm has no HLE counterpart |
| iReferSemaStatus / RFU005 / iPollSema | 67,629 / 46,042 / 45,104 | 0 / 0 / 0 | Reference-only (BIOS-pump + interrupt-context mix) |
| FlushCache | 0 | 14,356 | Runtime-only (recomp cache maintenance via 0x64) |
| RFU252 (fc) / RFU116 (74) / RFU091 (5b) / RFU090 (5a) | 0 | 21 / 8 / 6
...[truncated 4177 chars]