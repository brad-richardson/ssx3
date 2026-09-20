# P11 REPORT — SIF poll-expectation fix + ladder-confirm boots vs the post-split baseline

Brief `local/muse/prompts/P11.md`. Standalone (no `P1/REPORT.md` append;
a peer brief owns it). Tables. One fork commit (`bfa0213`, 1 file,
+2/−1, pushed; suite 428/428/0) + 2 boots (both healthy — pre-split
`bfa0213` binary, full game image, log opts ON).

Stale-reading guard: `local/research/P10/REPORT.md` §P10-2c (the stale
`:949` expectation), §P10-4 (why both P10 boots were invalid), and
§P10-7 items 1–2 (recovery recipe + one-liner) re-read first, plus
`local/research/P1/REPORT.md` Part 25 (P25-boot1 rungs) and
`local/research/P9/REPORT.md` §P9-2c/§P9-3 (the post-split ladder —
the brief's triggered baseline, §P11-3).
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `C=/tmp/p11-clean` (detached worktree at `bfa0213`),
`B=/tmp/p11-link/runtime` (its build dir).

## P11-0. Lease record + session facts

| Event | Value |
|---|---|
| Lease at session start (03:08:31Z) | Absent; `P11 start` line to waits log |
| Poll 1 (03:36:15Z) | `P1ac` holder-boot-running (pid 93402), waiting (logged) |
| Poll 2 (03:41:27Z) | `M15` holder-idle (`pgrep` 1), waiting (logged) |
| Poll 3 (03:46:33Z) | `M15` holder-idle (`pgrep` 1), waiting (logged) |
| Poll 4 (03:51:33Z) | Absent; `pgrep -x` exit 1 |
| Pre-claim checks (03:51:42Z) | Absent verified twice; `pgrep -x` exit 1; binary `178bf452` (P11 `Test:` build); `fork/ssx3` `45da174` (P1ac diag, §P11-3 note); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P11\n' > /tmp/ssx3-host-lease` 03:51:42Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, `boot-p11-1.log` 7,740 lines, 1,037,723 B |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, `boot-p11-2.log` 7,956 lines, 1,068,248 B |
| Release | 03:55:07Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| Waits log | `$W/P1/run/p11-waits.log` (6 lines: start, 3 polls, claim, release) |
| `adb` | Not used |
| Concurrent panes | P9 (split `4326926` committed+pushed mid-session on top of `bfa0213`; booted 03:16–03:19Z, released before my polls); P1ac (held lease at poll 1; pushed `45da174` diag ride-along); M15 (held lease idle at polls 2–3); new shared-clone dirt (`RPC.cpp`/`System.cpp`/kernel tests) appeared mid-session — never staged/touched |
| Time used | ≈03:08–03:58Z (~1 h of the 4 h box) |

## P11-1. SIF one-liner + suite receipts

Exact path (`R`-relative): `ps2xTest/src/ps2_sif_rpc_tests.cpp`.

| # | Location | Change |
|---|---|---|
| S1 | `:29–30` constexprs | Added `constexpr int KE_ERROR = -1;` (mirrors `ps2_runtime_kernel_tests.cpp` convention) |
| S2 | `:949`→`:950` | `KE_SEMA_ZERO` → `KE_ERROR`; message retitled to the kernel-miss spirit: `"zero-count poll must miss with KE_ERROR (-1), like the kernel"` |
| — | `:31` `KE_SEMA_ZERO` constexpr | Kept, now unused in this file (its sole use was `:949`; P25 precedent) |

```diff
     constexpr int KE_OK = 0;
+    constexpr int KE_ERROR = -1;
     constexpr int KE_SEMA_ZERO = -419;
```

```diff
-            t.Equals(getRegS32(env.ctx, 2), KE_SEMA_ZERO, "semaphore should start at zero before nowait rpc");
+            t.Equals(getRegS32(env.ctx, 2), KE_ERROR, "zero-count poll must miss with KE_ERROR (-1), like the kernel");
```

### a. Suite receipts (clean worktree `C`, `B` build, CWD `C`)

| Receipt | Baseline (`69bb1ff` tree) | AFTER (SIF fix) |
|---|---|---|
| Suite | 428 / 427 / 1, rc=1 (`/tmp/p11-baseline.log`) | 428 / 428 / 0, rc=0 (`/tmp/p11-after.log`) |
| Failing face | `snddrv state RPC returns stable buffers and signals sema`: `semaphore should start at zero before nowait rpc` (the named P10-2c face) | — (P10 test + snddrv test both `[Passed]`) |
| `[drop]` lines | 12 | 12 (P1w exclusion holds) |
| Rebuild | `ps2x_tests` exit 0 | `ps2x_tests` exit 0, no new warnings in the SIF file |

### b. Sync + push (shared clone, P9 active)

| Item | Value |
|---|---|
| Pre-commit `fetch fork ssx3` | No drift (`fork/ssx3` == local `69bb1ff`, P10) |
| Staged set | The 1 NAMED file only (`git add ps2xTest/src/ps2_sif_rpc_tests.cpp`; cached stat 2+/1−; P9's CSV+`CD.cpp`+runner dirt unstaged/untouched) |
| Commit | `bfa0213` (`Test: expect kernel-true KE_ERROR poll miss in snddrv SIF test (P11)`, 3 trailers) |
| `pull --rebase` | Refused: unstaged changes (same as P10/P25 — stashing a live peer's work was not an option) |
| Push safety | Re-`fetch`; `fork/ssx3` still `69bb1ff` = my parent; `merge-base --is-ancestor` FAST-FORWARD-OK (no rebase needed, no foreign conflict) |
| Push | `git push fork ssx3` from the fork clone only (`69bb1ff..bfa0213`) |

## P11-2. Boot binary, with the check P10 missed

Configure mirrors `/tmp/p1-link` exactly (the P10-4b miss, closed):
Release/Ninja/LLVM `clang`, `BUILD_TESTING=ON`,
`PS2X_ENABLE_RUNTIME_LOGS=ON` + `PS2X_ENABLE_AGRESSIVE_LOGS=ON`
(verified in `B`'s `CMakeCache.txt`), `PS2X_BUILD_STUDIO=OFF`
(`rc=0`, `/tmp/p11-configure.log`).

### a. Regen from the CURRENT tree's CSV (pre-split)

`C` was reset to the pushed `bfa0213` (`status` clean,
`diff bfa0213` empty; CSV byte-identical to `69bb1ff`'s — the SIF
commit is test-only). `/tmp/p11-ssx3.toml` = tracked TOML with
exactly 2 lines changed (`ghidra_output` → `C`'s CSV,
`output` → `$W/P1/output-p11/` — P9 owns `$W/P1/output/`).
Tool: `$W/P1/bin/ps2_recomp` (`7654e7fe…`, Sep 18, the P-lane
binary). `cd $W/P1 && ps2_recomp /tmp/p11-ssx3.toml`,
03:13:37–03:16:01Z, `rc=0` (`$W/P1/run/recomp-p11-presplit.log`).

| Receipt | P11 regen | P1w tracked (pre-split) | P9 split regen |
|---|---|---|---|
| Ghidra map loaded | 9274 | 9274 | 9275 (+1 split row) |
| Functions discovered / recompiled / stubs | 9273 / 9096 / 177 | 9273 / 9096 / 177 — exact | 9274 / 9097 / 177 |
| Resumable entrypoints | 393727 | (same image; counts match) | 393728 (+1) |
| Skipped / decode failures / errors | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Output files | 9276 | — | 9278 (+`sub_003E3AD8` split file + P9-side `sub_0042C1F0` dup; both images carry `InitSystemCallTableAddress_0x42c1f0`) |

The P11 image matches P1w's tracked pre-split regen on every count;
the +1-vs-P9 delta is exactly the split function.

### b. Receipt BEFORE booting (all three held)

Image copied `output-p11/*.cpp,*.h` → `C/.../runner/` (9276 files;
`C` status = `M register_functions.cpp` only — the tracked-image
convention). `cmake --build B --target ps2EntryRunner -j4` (`rc=0`).

| # | Receipt (P10-4b) | P11 value |
|---|---|---|
| 1 | `register_functions.cpp` size | 32,658,243 B (~32 MB, not 438 B) |
| 2 | `0x100008` ref count | 8, not 0 (`sub_003E3AD8` refs 0 — pre-split confirmed) |
| 3 | Log opts in `CMakeCache.txt` | `RUNTIME_LOGS=ON`, `AGRESSIVE_LOGS=ON` (loader prints present in both boots) |

Binary: `B/ps2xRuntime/ps2EntryRunner`, 163,381,168 B,
`178bf452675b080eca079dbda83025b6f0d2f37f1d3d9a2623f947024f4af72a`.
No boot was attempted until all three held.

## P11-3. Baseline decision (brief's unless-clause triggered)

Rule: P25-boot1 (`boot-p1aa-1.log`) UNLESS P9's split commit is on
`fork/ssx3` when I boot, in which case the baseline is the
post-split ladder. At boot time `fork/ssx3` was `4326926` (P9's
split, landed 03:15:47Z on top of `bfa0213`; my boots 03:51–03:55Z)
→ **baseline = post-split ladder (`boot-p9-1.log`, P9-LOG1)**,
key rungs re-derived below with `/tmp/p1aa-ladder.py` (agreeing
with P9 §P9-2c on every rung).

Why the ladder still closes P10's carried item: P9 §P9-3 laddered
post-split+(−1) ≡ P25 on every rung; P11 ladders pre-split+(−1)
vs post-split — the two tables jointly imply pre-split+(−1) ≡ P25
(P10-7.1's prediction, via the one transitive hop the baseline
clause required). Step-3 receipts are absolute (33/0/balanced/
watch/census) and hold under both baselines.

| Baseline rung (re-derived) | boot-p9-1.log | (P25-boot1 reference, re-derived) |
|---|---|---|
| Lines / bytes / blocks | 6,984 / 930,883 / 17 stub + 17 thread (b0–b16) | 3,507 / 443,852 / 17 stub + 16 thread (b16 SIGTERM-cut) |
| Thread-1 | WAIT 29 @ `0x423de8` ×17 | WAIT 29 @ `0x423de8` ×16 |
| 29 / 30 / 31 handshakes | 275/274 / 2/2 / 275/274, F6 `ra=0x31aa8c` / F7 `ra=0x31aae4` | 86/85 / 2/2 / 86/85, same ras |
| Creates / `-1` waits | 33 / 0 | 33 / 0 |
| Watch / census / driver | 1 line `:49` / 6× one site `:53–:58` bare / `:625` | 1 line `:49`, same bytes / same 6 lines / `:625`, same bytes |
| `0x425cf0` spin | 17/17, sole `ra=0x40b1d8`, 1.2M–2.3M/block | 17/17, sole `ra`, 373K–591K/block |
| GS / CD / SIF / dormant | 96/64/48/96 / 42 / 18 / 65+4 | identical |

Note: `fork/ssx3` moved again to `45da174` (P1ac "attribute
`dispatchSyscallOverride` drops" diag ride-along) before my claim.
The clause names P9's split specifically, so the baseline stands;
P1ac's commit postdates both my binary and P9's boots, and both
sides of my census comparison use the same (pre-attribution) drop
format.

## P11-4. Boots + ladder (one table vs the post-split baseline)

Both boots: ELF loaded (`Loading segment … Entry point: 0x100008`,
`Starting execution`), CWD `$W/P1/run`, env = p1aa-boot1
unchanged (`PS2X_DIAG_SEMA` + `CREATE` + `S0` + WATCH
`0x52BE04,0x450de4`, drops ON; script diffs vs p10-boot =
docstring + LOG + BIN only). Binary `178bf452` both boots.

### a. Step-3 receipts: the `0x52BE04` stall steady state

| Receipt | boot-p11-1.log |
|---|---|
| Creates / `-1` waits | 33 / 0 |
| F6/F7 handshake | 317 waits / 316 signals, F6 `ra=0x31aa8c` / F7 `ra=0x31aae4` (boot 2: 329/328, same ras) — balanced |
| F6's drain exits identically (P10-2b exact line) | Static: `0x31aa90` + `beq v0,v1(id)` — loops while poll *succeeds*, miss exits identically (P10 REPORT L96); dynamic exact line byte-identical vs baseline: | `[diag:sema] op=wait id=29 count=0->0 parked=1 waker=1 pc=0x423de8 ra=0x31aa8c inInt=0 waiters=0->1 result=park` (F7 signal line likewise byte-identical; no `op=poll` lines exist on the diag channel) |
| Watch line | 1 line, `:49`, byte-identical to baseline (loader init `0x52be00`; word still never CPU-written) |
| `[drop]` census | 6× one site (`syscall/dispatchSyscallOverride` `KE_ERROR`, bare `-`), `:53–:58`, same lines as baseline |

### b. Ladder vs post-split baseline (all rungs same-script)

| Rung | Post-split baseline (boot-p9-1) | P11-boot1 | Delta |
|---|---|---|---|
| Lines / bytes | 6,984 / 930,883 | 7,740 / 1,037,723 | Throughput ×1.11 (env; P9 same-binary ×1.5 precedent) |
| Stub / thread blocks | 17 / 17 (b0–b16) | 17 / 17 (b0–b16) | None |
| Thread-1 | WAIT 29 @ `0x423de8` ×17 | WAIT 29 @ `0x423de8` ×17 | Same park |
| Thread-2 | parked 26, sch 2 then 0 | parked 26, sch 2 then 0 | None — exact |
| Thread-3 | running, `0x40b1d0`×9/`0x425cf0`×7 + 1 mid-switch (`status=1 pc=0x0`) | running, 8/8 + 1 mid-switch | Same regime; same artifact |
| Thread-4 | parked 31, sch=t1/2 exact from b1 | parked 31, sch=t1/2 exact from b1 | None (relation holds) |
| Thread-5 | parked 32, sch=t1 (±1: b9 +1) | parked 32, sch=t1 (±1: b16 +1) | None (same jitter) |
| 29-handshake | 275 / 274, same ras | 317 / 316, same ras | Balanced; more iterations (throughput) |
| 30-handshake | 2 / 2 | 2 / 2 | None — exact |
| 31-handshake | 275 / 274 | 317 / 316 | Balanced (throughput) |
| Creates / `-1` waits | 33 / 0 | 33 / 0 | None — exact |
| F2 zero-param pair | ret=28/29, same bytes | ret=28/29, same bytes | None — exact |
| Driver-entry | byte-identical (`:625`) | byte-identical (`:625`; same line) | None |
| Watch | 1 line (`:49`, loader init `0x52be00`) | 1 line (`:49`, same bytes) | None |
| `[drop]` census | 6× one site (`:53–:58`, bare) | 6× one site (`:53–:58`, same lines) | None — exact |
| `0x425cf0` spin | 17/17, sole `ra=0x40b1d8`, 1.2M–2.3M/block | 17/17, sole `ra=0x40b1d8`, 1.4M–2.3M/block | Same stall (throughput band) |
| GS kicks / copy-reg / gs:gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None — exact |
| `run:tick` | 7 ticks, pc `0x40b1d0`, dma→4650 gif→259 | 7 ticks, pcs `0x40b1d0`/`0x3827e0`/`0x40b1d8`, dma→5532 gif→308 | Same family/climb; sampling + throughput |
| CD `lbn=` / SIF loads | 42 / 18 | 42 / 18 | None — exact |
| Dormant / start-thread | 65 / 4 | 65 / 4 | None — exact |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |
| Epoch `:600–:630` (`:614` callback) | Split dispatch bytes | `diff` clean (shim dispatch, byte-identical — and identical vs P25 too) | None — shim≡split on the wire |

Throughput note: absolute counts run ×1.11 of P9-LOG1 while every
relation, shape, park, and byte-comparable is identical. P9
documented ×1.5 same-binary run-to-run variance; direction-free
contention, not a regression.

Boot 2 steady-state spot check: 7,956 lines / 1,068,248 B, 17/17
blocks, 33 creates, 0 `-1` waits, 329/328 + 329/328 balanced
29/31-handshakes (same ras), 2/2 on 30, 6-line census (`:54–:59`,
the same 1-line shift P25-LOG2/P9-LOG2 show), watch 1 line (`:50`,
same bytes), 17/17 spin with sole `ra`, GS 96/64/48/96, CD 42 /
SIF 18, dormant 65, driver `:625` — reproduces.

## P11-5. Exact commands

From `$R` (fork) unless noted; `$W`, `C`, `B` as above;
`LOG=$W/P1/run/boot-p11-1.log`, `LOG2=$W/P1/run/boot-p11-2.log`:

```
# Step 0 (context reads; lease-free)
re-read P10 REPORT P10-2c/P10-4/P10-7.1-2 + P1 REPORT Part 25 + P9 REPORT P9-2c/P9-3
date -u | tee $W/P1/run/p11-waits.log (start line, lease absent)
git fetch fork ssx3 (no drift: fork == local 69bb1ff); record P9 dirt (CSV+CD.cpp+runner)
# Step 1 (SIF fix; lease-free)
(edit_file x2: KE_ERROR constexpr + :949 expect/retitle, in $R)
git diff --stat (4 files: P9's 3 + SIF 2+/1-); git diff -- <SIF file> > /tmp/p11-sif.patch
git worktree add --detach C 69bb1ff (clean); cmake -S C -B B (Release/Ninja/LLVM,
  BUILD_TESTING=ON, both log opts ON, STUDIO=OFF; rc=0, /tmp/p11-configure.log)
cmake --build B --target ps2x_tests -j4 (rc=0)
ps2x_tests CWD C > /tmp/p11-baseline.log (428/427/1, SIF face, drops 12)
git -C C apply /tmp/p11-sif.patch (cmp FILES-IDENTICAL)
cmake --build B --target ps2x_tests -j4 (rc=0, no new warnings)
ps2x_tests CWD C > /tmp/p11-after.log (428/428/0, rc=0, drops 12)
git add <1 NAMED SIF file>; verify staged set; git commit (bfa0213, 3 trailers)
git pull --rebase fork ssx3 (refused: P9 unstaged dirt); fetch + merge-base (FF-OK)
git push fork ssx3 (69bb1ff..bfa0213)
# Step 2 (boot binary; lease-free)
git -C C reset --hard bfa0213 (status clean, diff empty; CSV == 69bb1ff's)
sed tracked TOML -> /tmp/p11-ssx3.toml (exactly 2 lines: csv -> C, output -> output-p11/)
cd $W/P1 && $W/P1/bin/ps2_recomp /tmp/p11-ssx3.toml (rc=0, recomp-p11-presplit.log)
verify recomp counts == P1w tracked (9274/9273/9096/177/393727, 0 errors)
cp output-p11/*.{cpp,h} C/.../runner/ (9276 files)
verify 32658243 B + 8x 0x100008 + 0x split refs + CMakeCache log opts (ALL HELD)
cmake --build B --target ps2EntryRunner -j4 (rc=0); shasum (178bf452)
(write /tmp/p11-boot1.py + /tmp/p11-boot2.py from p10 scripts; diffs = docstring + LOG + BIN)
(re-derive P25-boot1 + boot-p9-1 rungs with /tmp/p1aa-ladder.py)
# Step 3 (lease protocol + boot 1 + boot 2)
lease P1ac (boot running) -> log poll; lease M15 (idle) -> log poll x2; lease absent
lease absent x2; pgrep -x (exit 1); shasum fresh; git log (45da174 noted); ISO + ELF present
printf 'P11\n' > /tmp/ssx3-host-lease (03:51:42Z) + >> p11-waits.log
python3 /tmp/p11-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 1037723 B)
cat lease (P11); pgrep -x (exit 1)
python3 /tmp/p11-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 1068248 B)
rm -f /tmp/ssx3-host-lease (03:55:07Z); ls (absent); pgrep -x (exit 1); + >> p11-waits.log
# Step 3 (analysis, lease already released)
(/tmp/p1aa-ladder.py x2: boot1 + boot2; watch/census line numbers; :600-:630 diffs x2;
  F6/F7/watch byte-diffs; tick totals; thread-relation checks)
# Step 4 (this report; lease already released)
(write local/research/P11/REPORT.md)
git -C ssx3 add -f local/research/P11/REPORT.md
git -C ssx3 commit -m "[P11] ..." (trailer; NO push there)
```

Env delta boots vs boot-p9-1: none (script diff = docstring + LOG +
BIN only). Source delta vs P9's tree: none in the runner (my
binary predates the split content-identically on the runtime side
except the shim-vs-split pair, which §P11-4b shows byte-identical
on the wire).

## P11-6. Receipt paths

Heavy receipts stay outside the repo (P-lane `/tmp` convention):

| Path | Content |
|---|---|
| `/tmp/p11-head.csv` | `69bb1ff` CSV (byte-identical to `bfa0213`'s; the regen input) |
| `/tmp/p11-ssx3.toml` | Regen config (tracked TOML + exactly 2 path lines) |
| `/tmp/p11-configure.log` | `rc=0` configure (log opts ON, STUDIO OFF) |
| `/tmp/p11-build-tests-baseline.log` / `-after.log` | `rc=0` test builds (no new warnings) |
| `/tmp/p11-baseline.log` / `/tmp/p11-after.log` | 428/427/1 (SIF face) → 428/428/0 (drops 12 both) |
| `/tmp/p11-sif.patch` | Shared→clean SIF transfer (verified identical) |
| `/tmp/p11-build-runner.log` | `rc=0` runner build (`-j4`) |
| `$W/P1/output-p11/` | 9276-file pre-split regen (kept; P9's `output/` untouched) |
| `$W/P1/run/recomp-p11-presplit.log` | 03:13:37–03:16:01Z, `rc=0`, P1w-matching counts |
| `/tmp/p11-boot1.py` / `/tmp/p11-boot2.py` | Boot scripts (mirror p10; BIN=`B` runner) |
| `$W/P1/run/boot-p11-{1,2}.log` | 7,740 / 7,956-line healthy boots |
| `$W/P1/run/p11-waits.log` | 6-line lease record |
| `C=/tmp/p11-clean` + `B=/tmp/p11-link` | Kept (worktree == `bfa0213` + standard dirty game image) |

Changed files (this commit): `local/research/P11/REPORT.md` only.
Changed files (fork commit `bfa0213`): the 1 named SIF test file only.

## P11-7. What I could not do

| # | Limit |
|---|---|
| 1 | No direct single-table my-vs-P25 ladder: the brief's unless-clause + one-table rule put the table against the post-split baseline. P25 rungs were still re-derived (§P11-3) and P9's table closes the transitive hop, so P10-7.1's prediction is confirmed either way |
| 2 | `KE_SEMA_ZERO` constexprs now unused in 4 places (SIF test `:31`, `EeScheduler.cpp:44`, kernel tests `:32`, `State.h:37`); kept per P25 precedent — a follow-up may sweep them |
| 3 | Unknown-id `KE_UNKNOWN_SEMID` (−408) vs kernel −1: separate divergence, untouched (P10-7.3 carried) |
| 4 | `jalr`-indirect PollSema callers are statically invisible (P10-7.5 carried); the 23-site direct census + all observed polls cover the boot |
| 5 | P1ac's `45da174` drop-attribution diag commit landed before my claim — postdates both my binary and the baseline; both census sides use the same format, so no action was needed |
| 6 | ~15 min of the session spent on lease polls (P1ac/M15 held); time used ≈1 h of the 4 h box (single session, no subagents) |
