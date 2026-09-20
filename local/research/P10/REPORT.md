# P10 REPORT — PollSema miss settled kernel-first: plain `-1`, not `KE_SEMA_ZERO`

Brief `local/muse/prompts/P10.md`. Standalone (no `P1/REPORT.md` append;
a peer brief owns it). Tables. One fork commit (`69bb1ff`, 2 files,
+41/−1, pushed) + 2 boots (both invalid — game-less binary, §P10-4;
no 3rd boot per the cap).

Stale-reading guard: `local/research/P1z/REPORT.md` §P1z-3 (Wait/Poll
essence) + §P1z-7 item 4 (the `-1` vs `-419` divergence) re-read first,
plus `local/research/P1/REPORT.md` Part 23 §P23-1a/b (P1v rule +
PROVISIONAL note), §P23-2c (F6/F7 handshake), Part 25 (P25-boot1 ladder
baseline), and `docs/research/review-2026-09-19-progress.md` §7.5 (the
hardware-first rule). `W=/Volumes/Extreme SSD/ps2recomp-spike`,
`R=$W/PS2Recomp` (fork, branch `ssx3`), `C=/tmp/p10-clean` (detached
verification worktree), `B=/tmp/p10-link/runtime` (its build dir).

## P10-0. Lease record + session facts

| Event | Value |
|---|---|
| Lease at session start (02:48:36Z) | Absent; no polls needed, no waits |
| Waits log | `$W/P1/run/p10-waits.log` (3 lines: start, claim, release) |
| Pre-claim checks (02:54:5xZ) | Absent verified twice; `pgrep -x` exit 1; binary `bd0124bb` (P10 `Fix:` build); fork HEAD `69bb1ff` (pushed); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P10\n' > /tmp/ssx3-host-lease` 02:54:59Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, `boot-p10-1.log` 152 lines, 9,655 B |
| Boot 2 | 90 s foreground, SIGTERM rc=-15, `boot-p10-2.log` 152 lines (same stall) |
| Release | 02:58:09Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |
| Concurrent panes | P9 (shim-split; uncommitted `CD.cpp`+CSV+regen in the shared clone — never staged/touched); P1ab (diagnosis; booted healthy 03:00:57Z, after my release); P7 committed (`e235c4b`, my base) |
| Time used | ≈02:48–03:15Z (~0.5 h of the 4 h box) |

## P10-1. Re-derivation of P1z's two kernel words (lease-free)

Pristine check first, then independent re-decode from the in-repo BIOS
(`local/emulator/course-cleanup/profile/PCSX2/bios/ps2-bios-0200a-20040614-100909.bin`).

| Item | Value |
|---|---|
| sha256 | `6d23d001daf2a0fa8b381a5d49f51753c36e3622d0f04be46af1a0c548be4744` — MATCHES P1z |
| Size / ROMVER @ `0x35ac` | 4194304 B / `0200AC200406…` (matches filename) |
| table[`0x40`] file `0x3b2450` | `0x800049b8` = CreateSema (P1z-1 anchor reproduced) |
| table[`0x45`] file `0x3b2464` | `0x80004dc0` = PollSema worker |
| table[`0x46`] file `0x3b2468` | `0x80004dc0` = iPollSema (same worker) |

Poll worker decode (Capstone MIPS32LE; `daddu` hand-decoded per P1z-0):

| Address | Word | Instruction | Annotation |
|---|---|---|---|
| `0x80004dc0` | `2c820100` | `sltiu v0,a0,0x100` | id < 256? |
| `0x80004dc4` | `14400003` | `bnez v0,0x80004dd4` | valid id continues (delay: `sll v1,a0,5` always runs) |
| `0x80004dcc` | `03e00008` | `jr ra` | **shared miss return (P1z word 1)** |
| `0x80004dd0` | `2402ffff` | `addiu v0,zero,-1` | (delay) **`v0 = -1`** |
| `0x80004dd4` | `3c028002` | `lui v0,0x8002` | pool base … |
| `0x80004dd8` | `2442f240` | `addiu v0,v0,-0xdc0` | … `v0 = 0x8001F240` (P1z node pool) |
| `0x80004ddc` | `00622821` | `addu a1,v1,v0` | `a1` = node |
| `0x80004de0` | `8ca30004` | `lw v1,4(a1)` | `v1` = count |
| `0x80004de4` | `1860fff9` | `blez v1,0x80004dcc` | **count≤0 → miss return (P1z word 2)** |
| `0x80004de8` | `2463ffff` | `addiu v1,v1,-1` | (delay, always) pre-decrement |
| `0x80004dec` | `0080102d` | `daddu v0,a0,zero` | `move v0,a0` = id (R5900 gap, hand-decoded) |
| `0x80004df0` | `03e00008` | `jr ra` | success return |
| `0x80004df4` | `aca30004` | `sw v1,4(a1)` | (delay) count−− stored |

Kernel rule reproduced: valid id + `count>0` → consume, return id;
`count≤0` → plain `-1` via the shared `jr`/`addiu` pair (which also
serves invalid ids). Immediate scan: **no `-419` (`0xFE5D`) or `-408`
(`0xFE68`) immediate** in the wrapper (`0x80003400–40`), create
(`0x800049b8–40`), or sema-op (`0x80004bc0–0x80004f00`) ranges, and **no
`addiu v0,zero,-419` anywhere in KERNEL**. Verdict on P1z: **CONFIRMED**.

## P10-2. Blast-radius table (lease-free)

Every fork + test + guest consumer of a poll-miss return, and what
changes value under `-1` vs `-419`.

### a. Host runtime: zero branchers

| Consumer | Finding |
|---|---|
| `EeScheduler::pollSemaphore` (`EeScheduler.cpp:1279`) | Unknown id → `[drop]` + `KE_UNKNOWN_SEMID` (−408); `count==0` → `KE_SEMA_ZERO` (−419) with **no drop** (the P1w exclusion); else consume, return id. Only change site |
| `Sync.cpp` `PollSema`/`iPollSema` (`:144–153`) | Pure pass-through (`setReturnS32`); no value check, no drop |
| `Dispatcher.cpp` (`:272–276`) | Pure dispatch; zero `KE_ERROR` references in the file |
| Other `pollSemaphore` callers (whole-fork grep) | None besides `Sync.cpp:147` (+ decl/def) |
| `KE_SEMA_ZERO` references (whole fork) | 2 runtime defs (`EeScheduler.cpp:44`, `State.h:37`) + 2 test defs; zero runtime branches |
| Analyzer / call-list / symbol-DB `PollSema` refs | Name tables only (classifier regex, `X()` macro, SDB relocations); no return logic |
| `[drop]` census | Keyed on site+reason; poll-miss emits nothing under both values. The 6-line `dispatchSyscallOverride/KE_ERROR` census fires on a missing override handler (`System.cpp:441`), never on a syscall return value |

### b. Guest (game ELF `$W/P1/cd/SLUS_207.72` = swept copy, byte-identical): 23/23 value-agnostic

Full-ELF sweep for the F6-verified `jal 0x423df0` word (`0x0C109F7C`):
**23 static call sites** (the brief's "one consumer" is the one
*observed* consumer; 22 more exist statically). Sweep validity: the same
sweep for the WaitSema JAL word reproduces P22-1a's **73/73**.

| Group | Sites | Return-value use | `-1` vs `-419` |
|---|---|---|---|
| F6 drain (sole *dynamic* caller: P22-2c sole `ra=0x31aa98`; p1aa traces) | `0x31aa90` | `beq v0,v1(id)` — loops while poll *succeeds* | miss exits identically |
| Id-compare | `0x400eec`, `0x401204`, `0x40151c`, `0x401a48`, `0x401c3c` | `beq`/`bne v1(id),v0` | miss branches identically |
| Sign-test `bgez v0` (10) | `0x409bc4`, `0x409c80`, `0x409ea4`, `0x409f6c`, `0x40a0dc`, `0x40a1f0`, `0x40a4f0`, `0x40a9d4`, `0x40abb4`, `0x40af94` | miss = negative | both `<0` → identical |
| Sign-test `bltz v0` (7) | `0x409d60`, `0x40a6e4`, `0x40a8ac`, `0x40aab0`, `0x40ac90`, `0x40ae50`, `0x40b06c` | miss = negative | both `<0` → identical |

No site compares against a specific miss constant. (`jalr`-indirect
callers are statically invisible; every observed poll in every boot log
flows through F6.)

### c. Tests: one stale expectation, out of scope

| Consumer | Finding |
|---|---|
| `ps2_runtime_kernel_tests.cpp` (in scope) | **No poll-miss assertion** (`KE_SEMA_ZERO` constexpr at `:32` is defined but unreferenced); only poll assertion is unknown-id → `KE_UNKNOWN_SEMID` (`:1159`, unaffected) |
| `ps2_sif_rpc_tests.cpp:949` (**out of scope**) | `"snddrv state RPC …"`: zero-count `PollSema` asserts `KE_SEMA_ZERO` → **fails under `-1`** (named face, §P10-3; 1-line follow-up owns it) |
| Same file `:751/:810/:821/:968/:988` | Poll-success assertions (`== semaId`) — unaffected |

Explicitly out of scope (separate divergence, untouched): kernel also
returns `-1` for invalid ids (`0x80004dc4` falls through to the same
pair); the fork keeps `KE_UNKNOWN_SEMID` (−408) there.

## P10-3. Winner + diff + BEFORE/AFTER

**Winner: `-1` (kernel-first).** The re-derivation (§P10-1) is
unambiguous and the blast radius (§P10-2) shows no game-visible
regression anywhere (23/23 guest consumers identical, zero host
branchers), so the §7.5 rule picks the kernel value with no justified
deviation. The SIF test failure is a stale expectation, not a behavior
regression.

### a. The fix (one fork commit, `69bb1ff`)

File list (brief allowed `Sync.cpp`/`EeScheduler.cpp` poll path +
`ps2_runtime_kernel_tests.cpp`): **2 files touched** — `Sync.cpp`
examined, no change needed (already a pure pass-through).

| # | Location | Change |
|---|---|---|
| F1 | `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:1290` `pollSemaphore` | `count==0` returns `KE_ERROR` (−1) instead of `KE_SEMA_ZERO`, + 4-line kernel-citation comment; no-drop path unchanged (P1w exclusion kept); unknown-id path untouched |
| F2 | `ps2xTest/src/ps2_runtime_kernel_tests.cpp:700` | New `tc.Run("PollSema on a zero-count semaphore returns KE_ERROR like the kernel (P10)")`: miss → `KE_ERROR`, signal → id, poll → id, poll → `KE_ERROR`, `iPollSema` → `KE_ERROR` (+36) |
| — | `EeScheduler.cpp:44` / test `:32` / `State.h:37` `KE_SEMA_ZERO` constexprs | Kept, now unused (P25 precedent kept `KE_SEMA_OVF`; minimal diff; a follow-up may sweep) |

```diff
     if (object->count == 0)
     {
-        return KE_SEMA_ZERO;
+        return KE_ERROR;
     }
```

Numstat: `EeScheduler.cpp` 5+/1− (comment + return), test 36+/0−
(2 files, +41/−1). Staged set verified = the 2 named files only (P9's
`CD.cpp` + sweep-CSV + regenerated runner stayed unstaged/untouched).

### b. Sync + push (shared clone, P9 active)

| Item | Value |
|---|---|
| Pre-edit `fetch fork ssx3` | No drift (`fork/ssx3` == local `e235c4b`, P7) |
| Foreign dirt (recorded, untouched) | `Stubs/CD.cpp` −46 (P9 shim removal), `ssx3-functions.sweep.csv` +2/−1 (P9 split at `0x3E3AD8`), `runner/register_functions.cpp` +398775 (P9 regen) |
| `pull --rebase` | Refused: unstaged changes (same as P25's generated-file refusal — stashing a live peer's work was not an option) |
| Push safety | Re-`fetch`; `fork/ssx3` still `e235c4b` = my parent; `merge-base --is-ancestor` FAST-FORWARD-OK (no rebase needed, no foreign conflict) |
| Push | `git push fork ssx3` from the fork clone only (`e235c4b..69bb1ff`) |

### c. BEFORE/AFTER receipts (clean worktree `C` = `69bb1ff` content exactly)

All suite/build receipts come from the detached worktree `C` (`git diff
69bb1ff` empty — verified), built at `B` (Release/Ninja/LLVM, mirrored
from `/tmp/p1-link`; §P10-4 notes the 2 missed log options — suite
verdicts are unaffected: PASS/FAIL + `[drop]` lines don't go through
`RUNTIME_LOG`). The shared clone was never built by P10 (P9's
uncommitted `CD.cpp` would have contaminated the binaries).

| Receipt | Baseline (`e235c4b`) | BEFORE (test only, unfixed runtime) | AFTER (`69bb1ff`) |
|---|---|---|---|
| Suite | 427 / 427 / 0, rc=0 | 428 / 427 / 1, rc=1 | 428 / 427 / 1, rc=1 |
| Failing face | — | New P10 test (exactly the 3 miss assertions; signal+consume pass) | `snddrv state RPC returns stable buffers and signals sema`: `semaphore should start at zero before nowait rpc` (`ps2_sif_rpc_tests.cpp:949`, stale −419) |
| P10 test | n/a | FAILS (sensitive) | PASSES |
| `[drop]` lines | 12 | 12 | 12 (exclusion holds; only poll drop is the unknown-id probe) |
| Rebuild | `ps2x_tests` exit 0 | `ps2x_tests` exit 0 | `ps2x_tests` exit 0 + `ps2EntryRunner` exit 0, no new warnings in either file |

The AFTER `test_rc=1` is the known out-of-scope face (§P10-2c), named in
the fork commit message so concurrent panes' gate reads aren't confused.

## P10-4. Boots + ladder (2 boots used; both invalid — environmental)

### a. What the boots did

| Rung | boot-p10-1.log | boot-p10-2.log |
|---|---|---|
| Size | 152 lines / 9,655 B | 152 lines |
| First scheduler action | `[guest-branch:missing-target]` DirectJump `0x100008→0x100008` (no table entry) | Same |
| Thread 1 | Dormant at `pc=entry=0x100008`, `scheduled=0`, all 16 blocks | Same |
| Syscalls / stubs / sema lines | 0 / 0 / 0 (`[ee:idle] no runnable thread`) | Same |
| Loader prints (`Loading segment`/`ELF file loaded`/`Starting execution`) | Absent | Absent |

### b. Diagnosis: game-less binary (my build-procedure miss, not the patch)

| # | Cause | Evidence |
|---|---|---|
| 1 | `B`'s runner compiled the **committed 438-byte `register_functions.cpp` stub** (empty `g_ps2RecompiledFunctionTable`), not the 32 MB analyzer output | `C/.../runner/register_functions.cpp` = 438 B, 0 `0x100008` refs; `$W/P1/output/register_functions.cpp` = 32,658,325 B, 8 refs; P-lane builds only work because the shared tree always carries the full copy dirty (P25's "unstageable generated runner file") — tribal step missing from P25-4's commands, which my clean worktree didn't replicate |
| 2 | My `cmake` used default `PS2X_ENABLE_RUNTIME_LOGS=OFF` + `PS2X_ENABLE_AGRESSIVE_LOGS=OFF` (`/tmp/p1-link` has both ON) | `RUNTIME_LOG` compiles to no-op (`ps2_log.h:175`); loader prints + `Starting execution` vanish. `loadELF` still returned true (no `Failed to load ELF`, no exit-1) — the ELF *did* load; only the prints were compiled out |
| 3 | Net effect | Loaded ELF + empty function table → entry lookup misses before any guest instruction → dormant → 90 s idle |

My miss, stated plainly: I assumed committed-`register_functions.cpp`
was the pure pre-split game image and never checked its size (438 B vs
32 MB). A file-size comparison of `C` vs `$R` before building would
have caught it.

### c. Patch exoneration (the failure cannot be the `-1` change)

| # | Evidence |
|---|---|
| 1 | Failure precedes ALL guest execution: zero syscalls, zero sema lines; `pollSemaphore` is unreachable before the first guest `PollSema` |
| 2 | Healthy logs show first sema activity only after ELF load + SIF init — all downstream of my stall point |
| 3 | Suite AFTER delta is exactly the predicted single SIF face; no other behavioral delta |
| 4 | Host healthy: P1ab booted 5,823 lines on the same host at 03:00:57Z (after my 02:58:09Z release) with ELF load + sema creates |
| 5 | The stub table is behaviorally irrelevant to the suite: `ps2x_tests` links it (4 `nm` hits) yet the stub-built baseline is 427/427/0, identical to P25's full-image baseline |

### d. Ladder vs P25-boot1: could not run (cap reached)

No ladder receipts exist — both boots stalled before the first guest
instruction, and the 2-boot cap (P25 precedent: 3rd boot refused) leaves
no room to re-run with a fixed binary. Prediction, recorded unfalsified:
**zero delta on every rung** (§P10-2: F6's drain exits identically on
−1/−419, handshake/census/park all downstream of value-agnostic
consumers). A follow-up boot brief owns the confirmation (§P10-7.1).

## P10-5. Exact commands

From `$R` (fork clone) unless noted; `$W`, `C`, `B` as above;
`LOG=$W/P1/run/boot-p10-1.log`, `LOG2=$W/P1/run/boot-p10-2.log`:

```
# Step 0 (context reads; lease-free)
re-read P1z REPORT P1z-3/P1z-7.4 + P1 REPORT Part 23-25 + review 7.5 (paged reads)
shasum -a 256 <in-repo BIOS> (6d23d001..4744 MATCH); xxd ROMVER; lease absent; capstone 5.0.7
# Step 1 (re-derivation + blast radius; lease-free)
python3 /tmp/p10-rederive.py (table slots + poll decode + -419 scans)
grep KE_SEMA_ZERO/pollSemaphore/PollSema whole fork (lib+tests+games+analyzer)
python3 /tmp/p10-f6.py (F6 drain decode + 23-site JAL census + 73/73 validity)
python3 /tmp/p10-sites.py (all 23 consumer decodes)
read Dispatcher/System/Sync poll path (no value checks; override drops keyed on handler)
grep 423df0 boot-p1aa-1.log (F6-only dynamic polls)
# Step 2 (verification tree; lease-free)
date -u | tee $W/P1/run/p10-waits.log (start line, lease absent)
git fetch fork ssx3 (no drift); git diff --stat (P9 dirt recorded)
git worktree add --detach C e235c4b (clean, verified empty status)
cmake -S C -B B -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=.../clang
  -DCMAKE_CXX_COMPILER=.../clang++ -DBUILD_TESTING=ON (rc=0; MISSED the 2 log opts, P10-4b.2)
cmake --build B --target ps2x_tests -j4 (rc=0)
ps2x_tests CWD C > /tmp/p10-baseline.log (427/427/0, rc=0)
(edit_file: P10 test -> shared-tree kernel tests; patch -> C; FILES-IDENTICAL)
cmake --build B --target ps2x_tests -j4 (rc=0)
ps2x_tests CWD C > /tmp/p10-before.log (428/427/1, P10 face)
(edit_file: pollSemaphore KE_SEMA_ZERO -> KE_ERROR; patch -> C; IDENTICAL)
cmake --build B --target ps2x_tests -j4 (rc=0, no new warnings)
ps2x_tests CWD C > /tmp/p10-after.log (428/427/1, SIF face)
cmake --build B --target ps2EntryRunner -j4 (rc=0); shasum (bd0124bb)
git add <2 NAMED files>; verify staged set; git commit (69bb1ff, 3 trailers)
git pull --rebase fork ssx3 (refused: P9 unstaged dirt); fetch + merge-base (FF-OK)
git push fork ssx3 (e235c4b..69bb1ff)
(write /tmp/p10-boot1.py; sed -> /tmp/p10-boot2.py; diffs = docstring + LOG + BIN)
# Step 3 (lease protocol + boot 1 + boot 2)
lease absent x2; pgrep -x (exit 1); shasum fresh; git log (69bb1ff); ls ISO + ELF
printf 'P10\n' > /tmp/ssx3-host-lease (02:54:59Z) + >> p10-waits.log
python3 /tmp/p10-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 9655 B)
cat lease (P10); pgrep -x (exit 1)
python3 /tmp/p10-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15)
rm -f /tmp/ssx3-host-lease (02:58:09Z); ls (absent); pgrep -x (exit 1); + >> p10-waits.log
# Step 3 (diagnosis, lease already released)
ls -la 3x register_functions.cpp (438 B stub vs 32 MB x2); grep 0x100008 (0 vs 8)
read stub (7 lines); read main.cpp + loadELF + RUNTIME_LOG gate (ps2_log.h:158/175)
diff /tmp/p1-link vs /tmp/p10-link CMakeCache (2 log opts + STUDIO)
head recomp-p9-split.log (P9 regen 02:46:00Z); p9/p1ab waits logs; boot-p1ab-1.log head (healthy)
git -C C diff 69bb1ff --stat (EMPTY: receipts are committed-tree-valid)
nm ps2x_tests | grep RecompiledFunctionTable (4: linked-but-irrelevant, baseline proves)
# Step 4 (this report; lease already released)
(write local/research/P10/REPORT.md)
git -C ssx3 add -f local/research/P10/REPORT.md
git -C ssx3 commit -m "[P10] ..." (trailer; NO push there)
```

Env delta boots vs boot-p1aa-1: none (script diff = docstring + LOG +
BIN only). Source delta: `EeScheduler.cpp` (5+/1−) + 1 test (36+/0−).

## P10-6. Receipt paths

Heavy receipts stay outside the repo (P-lane `/tmp` convention):

| Path | Content |
|---|---|
| `/tmp/p10-rederive.py` | BIOS re-derivation (slots + poll decode + scans) |
| `/tmp/p10-f6.py` | F6 drain decode + JAL census + validity check |
| `/tmp/p10-sites.py` | All 23 consumer decodes |
| `/tmp/p10-test.patch` / `/tmp/p10-fix.patch` | Shared→clean patch transfers (both verified identical) |
| `/tmp/p10-baseline.log` / `-before` / `-after.log` | 427/427/0, 428/427/1 (P10 face), 428/427/1 (SIF face) |
| `/tmp/p10-build-*.log`, `/tmp/p10-configure.log` | rc=0 builds |
| `/tmp/p10-boot1.py` / `/tmp/p10-boot2.py` | Boot scripts (mirror p1aa; BIN=`B` runner) |
| `$W/P1/run/boot-p10-{1,2}.log` | 152-line stall logs (invalid binary — §P10-4) |
| `$W/P1/run/p10-waits.log` | 3-line lease record |
| `C=/tmp/p10-clean` + `B=/tmp/p10-link` | Kept for the follow-up boot brief (worktree == `69bb1ff` content) |

Changed files (this commit): `local/research/P10/REPORT.md` only.
Changed files (fork commit `69bb1ff`): the 2 named poll/test files only.

## P10-7. What I could not do

| # | Limit |
|---|---|
| 1 | **Boot ladder.** Both boots burned on the game-less binary (§P10-4); the 2-boot cap leaves no re-run. Follow-up recipe (no guessing): `cmake B -DPS2X_ENABLE_RUNTIME_LOGS=ON -DPS2X_ENABLE_AGRESSIVE_LOGS=ON` (flip in the existing cache), then get a **pre-split** game image into `C/.../runner/register_functions.cpp` — CAUTION: `$W/P1/output/register_functions.cpp` is currently P9's 02:46Z *split* regen, and the shared tree's copy matches it; regenerate from `69bb1ff`'s CSV with the analyzer (shape: `recomp-p9-split.log` head) or find P9's backup — then `cmake --build B --target ps2EntryRunner -j4` and reuse `/tmp/p10-boot{1,2}.py` (BIN already points at `B`). Predicted result: ladder identical to P25-boot1 on every rung |
| 2 | **`ps2_sif_rpc_tests.cpp:949` is still red.** One-line follow-up in a file outside P10's named list: `:949 t.Equals(getRegS32(env.ctx, 2), KE_SEMA_ZERO, "semaphore should start at zero before nowait rpc");` → expect `KE_ERROR` (and retitle the message's spirit: the kernel misses with −1). Suite left 428/427/1 with that sole named face |
| 3 | Unknown-id `KE_UNKNOWN_SEMID` (−408) vs kernel −1: separate divergence, untouched per the brief |
| 4 | `KE_SEMA_ZERO` constexprs now unused (`EeScheduler.cpp:44`, kernel tests `:32`, `State.h:37`); kept per P25 precedent — a follow-up may sweep them with item 2 |
| 5 | `jalr`-indirect PollSema callers are statically invisible (all *observed* polls flow through F6); the 23-site census covers every direct caller |
| 6 | Time used ≈0.5 h of the 4 h box (single session, no subagents) |

