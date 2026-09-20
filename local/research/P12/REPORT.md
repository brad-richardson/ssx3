# P12 REPORT — Unknown sema ids settled kernel-first: plain `-1`, not `KE_UNKNOWN_SEMID`

Brief `local/muse/prompts/P12.md`. Standalone (no `P1/REPORT.md` append;
a peer brief owns it). Tables. One fork commit (`da6a2d5`, 5 files,
+61/−13, pushed; suite 432/432/0) + 0 boots (divergence unreachable in
the current boot path — 16-boot census receipt instead, §P12-4).

Stale-reading guard: `local/research/P10/REPORT.md` §P10-7 item 3 (the
carried -408 divergence) + §P10-2/§P10-4 (blast-radius shape, boot
procedure), `local/research/P11/REPORT.md` §P11-7 item 2 (the 4 dead
`-419` constexprs), `local/research/P1z/REPORT.md` §P1z-1/§P1z-3 (BIOS
re-derivation method), `local/research/P1/REPORT.md` Part 20/22
(P20-1 the `id=-1` spin, P22-2 the F6 drain analysis), and
`docs/research/review-2026-09-19-progress.md` §7.5 (hardware-from-kernel
rule). `W=/Volumes/Extreme SSD/ps2recomp-spike`,
`R=$W/PS2Recomp` (fork, branch `ssx3`), `C=/tmp/p12-clean` (detached
verification worktree at `45da174`), `B=/tmp/p12-link/runtime` (its
build dir).

## P12-0. Lease record + session facts

| Event | Value |
|---|---|
| Lease at session start | Absent; no polls, no waits |
| Lease at session end | `M16` holder-idle (`pgrep -x` exit 1) |
| Waits log | `$W/P1/run/p12-waits.log` (2 lines: start, no-claim record) |
| Boots attempted | 0 (unreachable — §P12-4 census decides per the brief) |
| `adb` | Not used |
| Concurrent panes | P1ad/M16 (share only the fork remote); peer dirt in the shared clone (`ps2_runtime.cpp` +143, generated `register_functions.cpp`) — never staged/touched |
| Time used | ≈03:55–04:20Z (~0.5 h of the 4 h box) |

## P12-1. Re-derivation: kernel unknown-id returns (lease-free)

Work copy `/tmp/p12-bios.bin` only; in-repo BIOS read twice
(`cp` + pre-copy `shasum`), never written.

| Item | Value |
|---|---|
| sha256 (in-repo = copy) | `6d23d001daf2a0fa8b381a5d49f51753c36e3622d0f04be46af1a0c548be4744` — MATCHES P1z/P10 |
| Size / ROMVER @ `0x35ac` | 4194304 B / `0200AC200406…` |
| Syscall table slots `0x40`–`0x49` | All 10 re-verified, agree with P1z-1 (`0x40→0x800049b8`, `0x41→0x80003540`, `0x42→0x800034c0`, `0x43→0x80004bc0`, `0x44→0x80003440`, `0x45/0x46→0x80004dc0`, `0x47/0x48→0x80004df8`, `0x49→0x80004a40`) |
| KERNEL `-408` (`0xFE68`) immediates | **0** I-type hits in all of KERNEL |
| KERNEL `-419` (`0xFE5D`) immediates | **0** (re-confirms P10) |
| KERNEL `addiu v0,zero,-1` words | 75 |

Every sema worker funnels unknown ids — out-of-range AND freed slots
(free nodes carry `count=-1`) — to one `-1`:

| Syscall | Worker | Unknown-id check | Miss words |
|---|---|---|---|
| DeleteSema | `0x80004a40` | `0x80004a54 sltiu v0,s5,0x100` + `0x80004a70 beqz→0x80004a94`; `0x80004a8c bgezl a0(count)` falls to `0x80004a94` when free | `0x80004a94 1000003d` (`b` epilogue) / `0x80004a98 2402ffff` (`addiu v0,zero,-1`) |
| SignalSema | `0x80004bc0` | `0x80004bd4 sltiu v0,s3,0x100` + `0x80004be0 beqz→0x80004c04`; `0x80004bfc bgezl v1(count)` falls through when free | `0x80004c04 10000032` / `0x80004c08 2402ffff` |
| WaitSema | `0x80004cf0` | `0x80004d04 sltiu` + `0x80004d0c beqz→0x80004d30`; `0x80004d28 bgez v1(count)` falls through when free | `0x80004d30 1000001b` / `0x80004d34 2402ffff` |
| PollSema/iPoll | `0x80004dc0` | `0x80004dc0 sltiu` + `0x80004dc4 bnez` (invalid falls to `0x80004dcc`); freed slots (`count=-1`) join via `0x80004de4 blez` | `0x80004dcc 03e00008` (`jr ra`) / `0x80004dd0 2402ffff` (reproduces P10-1 exactly) |
| ReferSema/iRefer | `0x80004df8` | `0x80004df8 sltiu` + `0x80004dfc bnez` (invalid → `0x80004e04`); freed slots via `0x80004e1c bltz→0x80004e04` | `0x80004e04 03e00008` / `0x80004e08 2402ffff` |

Wrapper passthrough (the `-1` reaches the guest unchanged):

| Wrapper | Words | Effect on `-1` |
|---|---|---|
| Signal `0x800034c0` | `0x800034d0 bltz v0,0x8000350c` | Negative skips reschedule, value passes to `eret` |
| Delete `0x80003540` | `0x80003550 bltz v0,0x8000358c` | Same |
| Wait `0x80003440` | `0x80003450 addiu v1,zero,-2` + `0x80003454 bne v0,v1,0x80003494` | Only `-2` parks; `-1` returns with no park |

## P12-2. Blast-radius table (lease-free)

### a. Host runtime: zero value-branchers

| Consumer | Finding |
|---|---|
| 5 return sites | `EeScheduler::deleteSemaphore` (`:1190`), `::signalSemaphore` (`:1232`), `::pollSemaphore` (`:1288`), `::waitSemaphore` (`:1312`, via `setReturnS32`), `Sync.cpp ReferSemaStatus` (`:162`) — all changed, §P12-3 |
| `Sync.cpp` impls | Pure pass-through (`setReturnS32` + `transferIfRequested(interruptSafe)` — no result check) |
| `RPC.cpp:149 signalRpcCompletionSema` | Sole host consumer: `signalSemaphore(semaId, true) >= 0` — a sign test; `-1` and `-408` both `<0` → identical |
| `KE_UNKNOWN_SEMID` comparisons | Zero `==`/`!=` against the value anywhere in runtime, tests, games, or analyzer |
| `[drop]` census | Unknown-id drops are keyed on site+reason (condition labels, kept); zero unknown-id drops in any current boot log |

### b. Guest (game ELF `$W/P1/SLUS_207.72`, 3890784 B): 311 static sites

Wrapper map decoded from the ELF (each `addiu v1,zero,#; syscall; jr ra; nop`):

| Wrapper | Syscall | JAL sites |
|---|---|---|
| `0x423db0` | DeleteSema `+0x41` | 109 |
| `0x423dc0` | SignalSema `+0x42` | 86 |
| `0x423dd0` | iSignalSema `-0x43` | 20 |
| `0x423de0` | WaitSema `+0x44` | 73 (matches P22-1a; see P10-validity note below) |
| `0x423df0` | PollSema `+0x45` | 23 (matches P10 exactly) |
| `0x423e00`/`0x423e10`/`0x423e20`/`0x423e30` | iPoll/Refer/iRefer/iDelete | 0 each (game never calls them directly) |

First-read-of-`v0` classification per site (delay slot skipped — it runs
before the call; method reproduces P10's poll table address-for-address:
same 6 REGCMP + 17 SIGN sites):

| Class | Sites | `-1` vs `-408` |
|---|---|---|
| Clobbered / never read in window | 199 + 78 | Return discarded → identical |
| Sign/zero test (`bgez/bltz/blez/bgezl/bnez/bnel`) | 21 genuine + 9 false-window | Both `<0`, both `≠0` → identical |
| Stored/propagated, no branch | 0 genuine (5 apparent FLOWs all read a *later* call's result past a `b`/`jal`/`jr`) | identical |
| `beq/bne v0` vs requested id (all 6 PollSema) | F6 drain `0x31aa90` + `0x400eec`, `0x401204`, `0x40151c`, `0x401a48`, `0x401c3c` — `a0` and compared reg proven loaded from the SAME slot at all 6 | Identical EXCEPT when requested id ≡ `-1` exactly (kernel `-1` loops/taken, fork `-408` exits/not-taken) |
| Whole-ELF `-408` immediates | 2 hits, both unrelated (`addiu a3,a3,-0x198` pointer math @`0x250550`; backward `b` @`0x418174`) | No guest code can name `-408` |

The 6-site conditional is stale-only: the requested id has been valid in
every boot since p1u (§P12-4). (`jalr`-indirect callers are statically
invisible, P10-7.5 carried; every *observed* unknown-id return flows
through F6/F7, which ignore the wait return — F6 falls through to
`sw zero,0x1c(s0)` @`0x31aa8c` without reading `v0`.)

P10-validity note: `/tmp/p10-f6.py` sweeps `jal 0x423de8` (the `jr` word
*inside* the WaitSema wrapper) and prints **0**, so P10 REPORT L92's
"reproduces P22-1a's 73/73" is a wrong-address claim. The true entry is
`0x423de0` → 73 hits (this report). The sweep method itself is sound
(23 poll hits reproduced exactly); only P10's validity sentence is off.
(Diag `pc=0x423de8`/`0x423dc8` values are the wrappers' `jr`
instructions, consistent with this map.)

### c. Tests: one stale expectation, in scope

| Consumer | Finding |
|---|---|
| `ps2_runtime_kernel_tests.cpp:1203` | `PollSema should reject unknown semaphore ids` asserted `KE_UNKNOWN_SEMID` — updated to `KE_ERROR` (§P12-3) |
| Rest of suite | No other `-408` assertion; no drop-string assertions on unknown-id reasons |

## P12-3. Winner + diff + BEFORE/AFTER

**Winner: `-1` (kernel-first).** The re-derivation (§P12-1) is
unambiguous across all five workers, and the blast radius (§P12-2) shows
no game-visible regression in current behavior: zero host value-branchers,
no `-408` constant in the game, 305/311 guest sites value-agnostic, the 6
conditional sites gated on a requested id of exactly `-1` (unseen since
p1u), and zero unknown-id returns across the 16 most recent boots. The
stale-era hang-vs-limp shape (P22: with `-1` in the slot the fork's
`-408` made F6's drain exit after one poll instead of looping) is not a
current regression — on hardware that broken-ids boot spins either way —
so §7.5 picks the kernel value with no justified deviation.

### a. The fix (one fork commit, `da6a2d5`)

File list (brief allowed unknown-id paths + 4 constexpr sites + tests):
**5 files touched**, all named.

| # | Location | Change |
|---|---|---|
| F1 | `EeScheduler.cpp:1191` `deleteSemaphore` | Unknown id returns `KE_ERROR` + 2-line kernel cite; `[drop]` condition label kept |
| F2 | `EeScheduler.cpp:1233-1235` `signalSemaphore` | Unknown id returns `KE_ERROR` + cite; diag `result=` now prints `KE_ERROR` (was lying-by-constant); drop kept |
| F3 | `EeScheduler.cpp:1291-1294` `pollSemaphore` | Unknown id returns `KE_ERROR` + cite; P10 comment's `Unknown ids stay KE_UNKNOWN_SEMID` tail removed; drop kept, P1w no-drop-on-miss kept |
| F4 | `EeScheduler.cpp:1318-1322,1332` `waitSemaphore` | Unknown id `setReturnS32(KE_ERROR)` + cite (no park, like the kernel); diag `result=` prints `KE_ERROR`; no drop (unchanged — wait path never had one) |
| F5 | `Sync.cpp:162-166` `ReferSemaStatus` | Unknown id `setReturnS32(KE_ERROR)` + cite; drop kept |
| S1–S4 | `EeScheduler.cpp:44`, `State.h:37`, kernel tests `:40`, SIF test `:31` | The 4 dead `KE_SEMA_ZERO` constexprs deleted (P11-7.2 closed) |
| T1 | kernel tests `:1241` | Stale `:1203` poll-unknown assertion → `KE_ERROR` |
| T2 | kernel tests `:743-782` | New P12 test: all 5 paths × never-created id + deleted-id signal/poll → `KE_ERROR` (+40) |
| — | `KE_UNKNOWN_SEMID` constexprs (`EeScheduler.cpp:37`, `State.h:30`, tests `:38`) | Kept, now unused (P25 precedent; a follow-up may sweep); drop reason strings keep the name (they label the condition, still true) |

Numstat: 5 files, +61/−13. Staged set verified = the 5 named files only
(peer's `ps2_runtime.cpp` +143 and generated runner stayed
unstaged/untouched).

### b. Sync + push (shared clone, P1ad/M16 active)

| Item | Value |
|---|---|
| Pre-edit `fetch fork ssx3` | No drift (`fork/ssx3` == local `45da174`, P1ac) |
| Foreign dirt (recorded, untouched) | `lib/ps2_runtime.cpp` +143 (peer), `runner/register_functions.cpp` +398779 (generated) |
| `pull --rebase` | Refused: unstaged changes (same as P10/P11/P25 — stashing a live peer's work was not an option) |
| Push safety | Re-`fetch`; `fork/ssx3` still `45da174` = my parent; `merge-base --is-ancestor` FAST-FORWARD-OK (no rebase needed, no foreign conflict) |
| Push | `git push fork ssx3` from the fork clone only (`45da174..da6a2d5`) |

### c. BEFORE/AFTER receipts (clean worktree `C` = `da6a2d5` content exactly)

Configure mirrors `/tmp/p1-link` exactly (Release/Ninja/LLVM,
`BUILD_TESTING=ON`, both log opts ON, `STUDIO=OFF`; `rc=0`). The shared
clone was never built by P12 (peer's `ps2_runtime.cpp` would have
contaminated the binaries). `git -C C diff da6a2d5` empty — verified.

| Receipt | Baseline (`45da174`) | BEFORE (test only, unfixed runtime) | AFTER (`da6a2d5`) |
|---|---|---|---|
| Suite | 431 / 431 / 0, rc=0 | 432 / 430 / 2, rc=2 | 432 / 432 / 0, rc=0 |
| Faces | — | Updated `:1203` + new P12 test (exactly the 8 miss assertions; create/delete-success pass) | — (P10 + P12 + snddrv tests all `[Passed]`) |
| `[drop]` lines | 12 | 18 | 18 (12 baseline + 6 P12 probes; labels kept by design) |
| Rebuild | `ps2x_tests` exit 0 | `ps2x_tests` exit 0 | `ps2x_tests` exit 0, no new warnings |

Current suite total counted, per the brief: 431 at base (peers added 3
since P11's 428), 432 with the P12 test.

## P12-4. Boots-or-why-not: unreachable — census receipt, 0 boots

Per-log census for unknown-id returns (`-408` / `KE_UNKNOWN_SEMID` /
`diag:sema … count=-1->-1`) across all 42 `boot-*.log` under `$W/P1/run`
(delete/signal/poll/refer unknown-ids emit `[drop]`s, wait unknown-ids
emit `diag:sema` lines — drops are ON in every current boot, so any
firing on any path would be visible):

| Log era | Unknown-id returns |
|---|---|
| 16 boots p1v→p11 (`p1v-1/2`, `p1w-1/2`, `p9-1/2`, `p1aa-1/2`, `p1ab-1/2`, `p1ac-1/2`, `p10-1/2` trivially-0 stall logs, `p11-1/2`) | **0** |
| `boot-p1u-1.log` (stale) | 257,125 waits + 4 signals, all `id=-1 → -408` (F6 `ra=0x31aa8c` / F7 `ra=0x31aae4`) |
| `boot-p1t-1.log` (stale) | 1,387,579 waits + 24 signals, all `id=-1 → -408` (matches P1 Part 20's 1,387,579+24 exactly) |
| All other logs (p1b–p1s era) | 0 |

The stale firings are P22's diagnosed broken-ids spin (game passing
`id=-1` from an unset slot; fixed by the p1v-era handshake work —
zero occurrences in every boot since). The divergence fires nowhere in
the current boot path, so no boots were attempted and the lease was never
claimed. No ladder table exists; prediction, recorded unfalsified: **zero
delta on every rung** (no boot-log line can change when the touched paths
never execute).

## P12-5. Exact commands

From `$R` (fork) unless noted; `$W`, `C`, `B` as above:

```
# Step 0 (context reads; lease-free)
re-read P10 REPORT P10-7.3 + P11 REPORT P11-7.2 + P1z REPORT P1z-1/P1z-3
shasum -a 256 <in-repo BIOS> (6d23d001..4744 MATCH)
cp <in-repo BIOS> /tmp/p12-bios.bin (work copy) + re-shasum (identical)
# Step 1 (re-derivation + blast radius; lease-free)
python3 /tmp/p12-rederive.py (table slots + poll/refer decode + KERNEL scans)
python3 /tmp/p12-rederive2.py (word-by-word delete/signal/wait/wrapper decode)
grep KE_UNKNOWN_SEMID/KE_SEMA_ZERO/-408 whole fork (sites + zero branchers)
grep -c -408/UNKNOWN_SEMID/count=-1 per boot log (find -print0 loop, quoted)
python3 /tmp/p12-sites.py (ELF wrapper map + JAL sweeps + F6 decode + -408 census)
python3 /tmp/p12-classify{,2,3}.py (v0-use classifier x3: strings/detail/fixed)
python3 /tmp/p12-flow{,2}.py + /tmp/p12-a0.py (FLOW windows + poll a0 provenance)
date -u | tee $W/P1/run/p12-waits.log (start line, lease absent)
# Step 2 (verification tree; lease-free)
git fetch fork ssx3 (no drift); git diff --stat (peer dirt recorded)
git worktree add --detach C 45da174 (clean)
cmake -S C -B B -G Ninja (Release/LLVM/BUILD_TESTING=ON/both log opts ON/STUDIO=OFF; rc=0)
cmake --build B --target ps2x_tests -j4 (rc=0)
ps2x_tests CWD C > /tmp/p12-baseline.log (431/431/0, rc=0, drops 12)
(edit_file: P12 test + :1203 update, in C)
cmake --build B --target ps2x_tests -j4 (rc=0)
ps2x_tests CWD C > /tmp/p12-before.log (432/430/2, rc=2, drops 18)
(edit_file x9: 5 return sites + diag prints + comments + 4 const deletions, in C)
cmake --build B --target ps2x_tests -j4 (rc=0, no new warnings)
ps2x_tests CWD C > /tmp/p12-after.log (432/432/0, rc=0, drops 18)
git -C C diff > /tmp/p12.patch; git -C R apply --check + apply (5x cmp IDENTICAL)
git add <5 NAMED files>; verify staged set; git commit (da6a2d5, 3 trailers)
git pull --rebase fork ssx3 (refused: peer unstaged dirt); fetch + merge-base (FF-OK)
git push fork ssx3 (45da174..da6a2d5)
git -C C diff da6a2d5 --stat (EMPTY: receipts are committed-tree-valid)
# Step 3 (reachability; lease never claimed)
lease absent at start; M16 holder-idle at end; 0 polls; no-claim line >> p12-waits.log
# Step 4 (this report)
(write local/research/P12/REPORT.md)
git -C ssx3 add -f local/research/P12/REPORT.md
git -C ssx3 commit -m "[P12] ..." (trailer; NO push there)
```

No runner build was needed (no boots); no boot scripts were written.

## P12-6. Receipt paths

Heavy receipts stay outside the repo (P-lane `/tmp` convention):

| Path | Content |
|---|---|
| `/tmp/p12-bios.bin` | BIOS work copy (sha-identical to in-repo) |
| `/tmp/p12-rederive.py` / `.log` | Table slots + poll/refer decode + KERNEL `-408`/`-419`/`-1` scans |
| `/tmp/p12-rederive2.py` / `.log` | Word-by-word delete/signal/wait/wrapper decode (362 lines) |
| `/tmp/p12-sites.py` / `.log` | ELF wrapper map + JAL sweeps + F6 decode + ELF `-408` census |
| `/tmp/p12-classify3.py` / `.log` | Fixed v0-use classifier + all branch/compare windows |
| `/tmp/p12-classify{,2}.py` | Superseded classifier passes (kept: method audit trail) |
| `/tmp/p12-flow{,2}.py`, `/tmp/p12-a0.py` | FLOW windows + poll `a0` provenance (same-slot proof) |
| `/tmp/p12-configure.log` | `rc=0` configure (p1-link mirror) |
| `/tmp/p12-build-{base,before,after}.log` | `rc=0` test builds (no new warnings) |
| `/tmp/p12-baseline.log` / `-before` / `-after.log` | 431/431/0, 432/430/2 (8 miss assertions), 432/432/0 |
| `/tmp/p12.patch` | `C`→`R` transfer (185 lines; 5× `cmp` IDENTICAL) |
| `$W/P1/run/p12-waits.log` | 2-line lease record (start + no-claim) |
| `C=/tmp/p12-clean` + `B=/tmp/p12-link` | Kept (worktree content == `da6a2d5`) |

Changed files (this commit): `local/research/P12/REPORT.md` only.
Changed files (fork commit `da6a2d5`): the 5 named runtime/test files only.

## P12-7. What I could not do

| # | Limit |
|---|---|
| 1 | **No boots / no ladder.** The divergence is unreachable in the current boot path (16-boot census 0), so per the brief no boots were attempted. Prediction unfalsified: zero delta on every rung. If unknown-id paths ever fire again in a boot, a follow-up boot brief owns the ladder |
| 2 | `KE_UNKNOWN_SEMID` constexprs now unused (`EeScheduler.cpp:37`, `State.h:30`, kernel tests `:38`); kept per P25 precedent + brief scope (only the 4 `-419` consts were named) — a follow-up may sweep them |
| 3 | `jalr`-indirect sema callers are statically invisible (P10-7.5 carried); the 311-site direct census + the all-paths dynamic census (any firing would log) cover the boot |
| 4 | P10 REPORT L92's "73/73 reproduced" validity sentence is a wrong-address claim (`0x423de8` sweeps 0 hits; true WaitSema entry `0x423de0` gives the 73) — noted in §P12-2b, not fixed (another brief's report) |
| 5 | First-read-of-`v0` windows are linear (12 insns, no CFG): ~15 attributions ran past a `b`/`jal`/`jr` into other calls' results — each was hand-checked and resolved identical (§P12-2b); a CFG pass would remove the hand step |
| 6 | Time used ≈0.5 h of the 4 h box (single session, no subagents) |
