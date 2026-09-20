# P9 — Shim retired: CSV split at 0x3E3AD8 carries the CD callback (ladder-identical)

Brief `local/muse/prompts/P9.md`. One `fork`-only commit (2 files,
+2/−47) + 2 boots. Tables, no verdicts. Stale-reading guard: P1
REPORT Part 21 §P21-1a (shim-vs-split table) + Part 24 §P24-1 (tracked
CSV/TOML) + Part 25 §P25-2 (ladder baseline) re-read before acting.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork,
branch `ssx3`), `O=$W/P1/output`, `LOG1=$W/P1/run/boot-p9-1.log`,
`LOG2=$W/P1/run/boot-p9-2.log`. STANDALONE evidence dir (this file
only; `P1/REPORT.md` untouched — a peer brief owns it).

## P9-0. Lease record

| Event | Value |
|---|---|
| Lease at session start (02:44:54Z) | Absent; no waits, no polls needed |
| Waits log | `$W/P1/run/p9-waits.log` (3 lines: start, claim, release) |
| Pre-claim checks (03:16:03Z) | Absent verified twice; `pgrep -x` exit 1; binary `950675bb` (P9 build); fork HEAD `4326926` (pushed); ISO 3005415424 B + ELF 3890784 B present |
| Claim | `printf 'P9\n' > /tmp/ssx3-host-lease` 03:16:05Z, immediately before boot 1 |
| Boot 1 | 90 s foreground, SIGTERM rc=-15, LOG1 6,984 lines, 930,883 B, 17 thread + 17 stub blocks |
| Boot 2 | 90 s foreground, SIGTERM rc=-15 (lease still `P9`, verified pre-boot; `pgrep -x` exit 1), LOG2 4,735 lines, 612,986 B, 17 + 17 blocks |
| Release | 03:19:25Z, right after boot 2 (analysis needs no lease); verified absent; `pgrep -x` exit 1 |
| `adb` | Not used |

## P9-1. Split + removal + recomp + tests

### a. Boundary re-derivation (ELF words, `SLUS_207.72`, file-off = va−`0x100000`+`0x1000`)

| va | word | disasm | Role |
|---|---|---|---|
| `0x3e3acc` | `0x03e00008` | `jr $ra` | parent returns |
| `0x3e3ad0` | `0x27bd00b0` | `addiu $sp,+$0xB0` (delay) | — |
| `0x3e3ad4` | `0x00000000` | `nop` | padding — clean boundary above `0x3e3ad8` |
| `0x3e3ad8` | `0x3c020052` | `lui $v0,0x52` | split point = callback body head |
| `0x3e3adc` | `0x27bdfff0` | `addiu $sp,-0x10` | — |
| `0x3e3ae0` | `0x8c449c4c` | `lw $a0,-0x63B4($v0)` | `$a0`=`*(0x519C4C)` |
| `0x3e3ae4` | `0xffbf0000` | `sd $ra,0($sp)` | — |
| `0x3e3ae8` | `0x0c108f74` | `jal 0x423DD0` | `ra`=`0x3e3af0` |
| `0x3e3aec` | `0x00000000` | `nop` (jal delay) | skipped by recompiler and shim alike |
| `0x3e3af0` | `0xdfbf0000` | `ld $ra,0($sp)` | post-call resume |
| `0x3e3af4` | `0x03e00008` | `jr $ra` | body returns |
| `0x3e3af8` | `0x27bd0010` | `addiu $sp,+$0x10` (delay) | — |
| `0x3e3afc` | `0x00000000` | `nop` | padding |
| `0x3e3b00` | `0x27bdff90` | `addiu $sp,-0x70` | next function head (`sub_003E3B00`) |

Clean `jr $ra` / delay / `nop` boundaries both sides, as §P21-1a
claimed. Collision predicate (pre-split enclosing file
`$O/sub_003E39A8_0x3e39a8.cpp`): `case 0x3e3ad8` / `label_3e3ad8` = 0
matches; `register_functions.cpp:380392-380398` slots mirror exactly
the parent entry + 6 switch cases (`0x3e39f0`/`0x3e3a08`/`0x3e3a14`/
`0x3e3a3c`/`0x3e3a7c`/`0x3e3af0`), no `0x3e3ad8` slot. Zero collision.

### b. The two diffs (commit `4326926`, staged set verified = the 2 named files only)

CSV (`games/ssx3/ssx3-functions.sweep.csv:8159`, 9275→9276 lines =
header + 9275 data, LF-only, `0x3e3ad8` ×1, pre-existing `0x42c1f0`
×2 unchanged, contiguity `0x130`+`0x28`=`0x158`):

```diff
-sub_003E39A8,0x3e39a8,0x3e3b00,0x158
+sub_003E39A8,0x3e39a8,0x3e3ad8,0x130
+sub_003E3AD8,0x3e3ad8,0x3e3b00,0x28
```

`Stubs/CD.cpp`: pure deletion, 0 added lines — the P1t comment block
+ `kSsx3CdCallbackPc` + `ssx3CdCallbackSemaSignal` (42 lines) + the
4-line `queueCdCallback` hook. Exact inverse of `58c9144` (+46).
Post-delete grep over `ps2xRuntime/src/lib` for
`3E3AD8`/`3e3ad8`/`ssx3CdCallback`: no matches.

No test added (harness decision, recorded): the split's effect lives
entirely in generated runner code, which `ps2x_tests` does not link
(P13-1d: 0 runner symbols in the test binary); no `ps2xTest/src`
file covers CD HLE; and a test naming `0x3E3AD8` would re-hardcode
the game address this brief removes. Precedent: P7's game-specific
stub shipped with no suite test (`e235c4b`, 2 files). Proof is the
ladder-identical boots (§P9-2).

### c. Recomp from the tracked TOML (`recomp-p9-split.log`, rc=0) vs P24 baseline

`cd $W/P1 && $W/P1/bin/ps2_recomp $R/games/ssx3/ssx3.toml`
(pre-recomp output verified = P24 state: 9277 entries + all four
§P24-1c spot shas match).

| Check | P24 (`recomp-p1w-tracked.log`) | P9 split | Delta |
|---|---|---|---|
| Parsing toml file | `$R/games/ssx3/ssx3.toml` | same (tracked bytes drove the run) | — |
| Ghidra map loaded | 9274 | 9275 | +1 (new row) |
| Extracted / discovered / processed | 9273 | 9274 | +1 |
| Recompiled / stubs / skipped | 9096 / 177 / 0 | 9097 / 177 / 0 | +1 recompiled |
| Additional entrypoints | 393727 | 393728 | +1 (the new `0x3e3ad8` entry) |
| Generated functions | 9273 | 9273→9274 | +1 |
| Indirect fallback promotions | 3598 (724964 entries) | same | None |
| Decode failures / unhandled / errors | 0 / 0 / 0 | same | None |
| Output entries | 9277 | 9278 | +1 |
| `register_functions.cpp` sha16 | `69ae38662d87b121` | `05836f4b15579383` | Changed (new entry; expected) |
| `ps2_recompiled_functions.h` sha16 | `ec05c4d8fd856046` | `1a3de3400a9e58a2` | Changed (new decl; expected) |
| `sub_00425CF0_0x425cf0.cpp` sha16 | `46340e176c229e50` | same | None — determinism |
| `sub_0040B130_0x40b130.cpp` sha16 | `06b879c712a3bed4` | same | None — determinism |

New file `sub_003E3AD8_0x3e3ad8.cpp` (2517 B): header
`0x3e3ad8–0x3e3b00`, entry + `case 0x3e3af0`, body insn-for-insn the
shim's 8 (`lui`/`addiu`/`lw`/`sd`/`jal 0x423DD0` via
`dispatchGuestBranch`/`ld`/`jr $ra`+delay). Registration
(`register_functions.cpp:380398-380399`): slot **757428** =
`757352+(0x3e3ad8−0x3e39a8)/4` (P21's predicted slot) →
`sub_003E3AD8_0x3e3ad8`; `0x3e3af0` remapped parent→child. Header
decl `ps2_recompiled_functions.h:8167`.

### d. Parent non-truncation (finding, proven harmless)

Unlike the P1l splits (parents truncated, e.g.
`sub_00395C70→0x395c70–0x395cf0`), the parent file keeps its full
range (header `0x3e39a8–0x3e3b00`, 6 cases incl. a now-dead
`case 0x3e3af0`). Mechanism (`elf_parser.cpp`): the JAL-target
fallback scan emits `{sub_003E39A8, 0x3e39a8, 0x3e3b00}` (name format
`sub_%08X`, identical to map names); the map/fallback merge sorts
same-start rows end-DESC and `unique`s, keeping the LARGEST end —
the fallback beats the map row's `0x3e3ad8`, so the parent
`Function` never shrinks. JAL census (whole `.text`): `0x3e39a8`
has 1 direct caller (`0x3e4384`); the only JAL target in
(`0x3e39a8`,`0x3e3d00`] is `0x3e3b00` (hence fallback end
`0x3e3b00` exactly); P1l parents `0x395750`/`0x395c70` have 0 JAL
callers (indirectly reached — the P1b saga), so no fallback
competed and their map rows ruled. Harmless: dispatch is
table-driven; table slots `0x3e3ad8`/`0x3e3af0` now point at the
child, the parent's `jr $ra` @ `0x3e3acc` returns past its live
range, and the trailing slice is unreachable (both `jr` paths end
in `return`). The split's goal — an exact table entry for the
callback — is unaffected.

### e. Runner refresh + build + suite

| Item | Value |
|---|---|
| Refresh | `cp -X output/*.{cpp,h}` → `ps2xRuntime/src/runner/` (9277→9278 files), sidecars purged, `diff -rq` clean; only `register_functions.cpp` is tracked (rest git-ignored), never added |
| Rebuild | `cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4`, exit 0 (300 targets; sidecar purge first, P21 lesson) |
| Suite (CWD `$R`) | **428 / 428 / 0**, rc=0 (`/tmp/p9-suite2.log`) — no failure face |
| Baseline walk | 427/427/0 at session start (`e235c4b`, P7 receipt) → 428 total after peer P10's +1 test (`69bb1ff`) → green at `bfa0213`+P9 edits |
| Transient (not mine) | First post-edit run 428/427/1, sole face `snddrv state RPC … signals sema` (`semaphore should start at zero before nowait rpc`): binary built 23:05–23:09, between peer P10's lib change (22:54) and peer P11's test-expectation fix (23:12). Rebuilt after `bfa0213` → 428/428/0. P10's own message names the same stale expectation |
| Peer commits during session | `69bb1ff` P10 (PollSema KE_ERROR + test) 22:54, `bfa0213` P11 (snddrv 1-line test fix) 23:12 — both landed in the shared clone mid-session; my 2-file diff survived intact; P9 commit sits on `bfa0213` |

## P9-2. Boots + dispatch + ladder check (proof, not a diagnosis)

Env = p1aa-boot1 byte-identical except docstring + LOG
(`PS2X_DIAG_SEMA` + `CREATE` + `S0` + WATCH `0x52BE04,0x450de4`,
drops ON). Binary `950675bb…` both boots (= `4326926` tree: lib
sources committed as built; CSV committed as recomped; P11 is
test-only so the runner binary predates it content-identically).

### a. BEFORE/AFTER dispatch tables

BEFORE = P25-boot1 (shim era, `58c9144` in tree):

| Step | BEFORE (shim) |
|---|---|
| Table at init | NO `0x3e3ad8` entry (parent has no such case) |
| `queueCdCallback` | Lazily `registerFunction(0x3e3ad8, ssx3CdCallbackSemaSignal)` iff `!hasFunction` |
| Dispatch of `cb=0x3e3ad8` | Host shim emulates 8 insns, calls `iSignalSema` via `dispatchGuestBranch` |
| Observable | `:614 op=signal id=26 … pc=0x423dd8 ra=0x3e3af0 … cbFunc=43444342… result=26` |

AFTER = P9-boot1 (split, shim deleted):

| Step | AFTER (split) |
|---|---|
| Table at init | Slot 757428 → `sub_003E3AD8_0x3e3ad8` (recomp receipt §P9-1c) |
| `queueCdCallback` | No registration path (hook deleted; grep-clean) |
| Dispatch of `cb=0x3e3ad8` | Recompiled body runs (`lui…jal…ld…jr`), same `dispatchGuestBranch` call shape |
| Observable | `:614`, byte-identical line through the whole `:600–:630` window (`diff` clean) |

With the shim deleted, the `:614` signal line is the dispatch proof
(P21's rule): the ONLY remaining `0x3e3ad8` entry point is the
recompiled table slot. `Missing` / `No exact` = 0/0 both boots (no
fallback resolution involved).

### b. Epoch receipts (LOG1; P25-boot1 line numbers in parens — all same)

| Line | Event |
|---|---|
| :609 | First signal 26 → thread 2 (`ra=0x3e48b8`) |
| :610–:611 | `sceCdRead lbn=0x5f1a3` + `BIGF` payload (`42494746147c1a00`, same bytes) |
| :612–:613 | `[cd:callback] queued` / `start func=1 cb=0x3e3ad8` |
| :614 | **Callback signal** (`ra=0x3e3af0`, `pc=0x423dd8`, `cbFunc=43444342…`, count path — the split body RAN) |
| :615 | Worker wait consumes `1->0`, no park |
| :616–:617 | Worker pump id-5 pair (`waker=2`) |
| :618 | Worker re-parks on 26 |
| :625 | `[diag:driver-entry]` byte-identical (`sp=0x1fffe80 ra=0x3ded88 sourcePc=0x3ded80 checkpointed=0`) |

G6/site-#9: same evidence the baseline carries — epoch shape +
worker pass (`scheduled` 2-then-0) + driver probe. The direct
`0x519c40` store row (P21 :583) is unwatched in this env in BOTH
logs (WATCH = `0x52BE04,0x450de4`); nothing to compare against.

### c. Ladder check vs P25-boot1 (one table)

P25-boot1: 3,507 lines / 443,852 B / 16 thread + 17 stub blocks
(b16 stubs-only = SIGTERM-cut artifact; P25-LOG2 had 17/17). All
rungs re-extracted from all three logs with the same script
(`/tmp/p1aa-ladder.py`).

| Rung | P25-boot1 | LOG1 (boot 1) | Delta |
|---|---|---|---|
| Lines / bytes | 3,507 / 443,852 | 6,984 / 930,883 | Throughput ×2.0 (see note) |
| Stub / thread blocks | 17 / 16 (b0–b15) | 17 / 17 (b0–b16) | Full flush both P9 boots (artifact direction, cf. P25-LOG2 17/17) |
| Thread-1 | WAIT 29 @ `0x423de8` ×16 | WAIT 29 @ `0x423de8` ×17 | Same park |
| Thread-2 | parked 26, sch 2 then 0 | parked 26, sch 2 then 0 | None — exact |
| Thread-3 | running, pc `0x40b1d0`×11/`0x425cf0`×5, sch≈t1 | running, `0x40b1d0`×9/`0x425cf0`×7 + 1 mid-switch sample (`status=1 pc=0x0`) | Same regime; sample artifact has P25-LOG2 precedent |
| Thread-4 | parked 31, sch=t1/2 exact from b1 | parked 31, sch=t1/2 exact from b1 | None (relation holds) |
| Thread-5 | parked 32, sch=t1 (±1) | parked 32, sch=t1 (±1: b9 +1) | None (same jitter) |
| 29-handshake | 86 / 85, F6 `ra=0x31aa8c` / F7 `ra=0x31aae4` | 275 / 274, same ras | Balanced; more iterations (throughput) |
| 30-handshake | 2 / 2 | 2 / 2 | None — exact |
| 31-handshake | 86 / 85 | 275 / 274 | Balanced; more iterations (throughput) |
| Creates / `-1` waits | 33 / 0 | 33 / 0 | None — exact |
| F2 zero-param pair | ret=28/29, same sites/pcs | ret=28/29, same bytes | None — exact |
| Driver-entry | byte-identical (`:625`) | byte-identical (`:625`; same line) | None |
| Watch | 1 line (`:49`, loader init `0x52be00`) | 1 line (`:49`, same bytes) | None — word still never CPU-written |
| `[drop]` census | 6× one site (`:53–:58`, bare) | 6× one site (`:53–:58`, same lines) | None — exact |
| `0x425cf0` spin | 17/17, sole `ra=0x40b1d8`, 373K–591K/block | 17/17, sole `ra=0x40b1d8`, 1.2M–2.3M/block | Same stall; higher counts (throughput) |
| GS kicks / copy-reg / gs:gif / drawing=1 | 96 / 64 / 48 / 96 | 96 / 64 / 48 / 96 | None — exact |
| `run:tick` | 9 ticks, pcs `0x40b1d0`/`0x40b1d8`/`0x3827e0`, dma→1500 gif→84 | 7 ticks, pcs `0x40b1d0`, dma→4650 gif→259 | Same family/climb; sampling + throughput |
| CD `lbn=` / SIF loads | 42 / 18 | 42 / 18 | None — exact |
| Dormant / start-thread | 65 / 4 | 65 / 4 | None — exact |
| Missing / `No exact` | 0 / 0 | 0 / 0 | None |
| Presented frame | None | None | None |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

Throughput note: every absolute count runs ~2× P25 while every
relation, shape, park, and byte-comparable is identical. The split
cannot explain it (the callback fires ONCE per boot; the hot paths
are untouched) — and LOG1 vs LOG2 (same binary) differ ×1.5 from
each other, proving run-to-run environmental variance of this
magnitude. P25 recorded the same phenomenon in reverse (0.3–0.4×
vs P24, P7 concurrent). Recorded as contention, not a regression.

LOG2 steady-state spot check: 17/17 blocks, 33 creates, 0 `-1`
waits, 150/149 balanced 29-handshake, 6-line census (`:54–:59`,
the same 1-line shift P25-LOG2 shows), watch 1 line (`:50`, same
bytes), 17/17 spin with sole `ra`, GS 96/64/48/96, CD 42 / SIF
18, dormant 65, driver `:625` — reproduces. Two artifacts, both
closed: (1) 31-handshake reads 150/148 — the "missing" signal is
`:990`, clobbered by a `[frame:upload]`×`[diag:sema]` stderr
interleave (`…op=signal id= sourceFbp…preferred=031`, the `31`
surviving in the wreckage); thread 4 demonstrably ran at :993
(`signal id=29 waker=4`), so no wakeup was lost — 150/(148+1),
off-by-one = final `:4724` park, same shape as P25's 86/85.
Pre-existing unlocked-stderr race (frame uploads × sema diag),
more likely to collide at higher throughput; out of scope.
(2) `waker=-1` id-31 signals (11×; interrupt-context, no current
thread): same shape present 13× in P25-boot1.

## P9-3. Binaries and commits

| Binary / ref | sha256 / sha | Sources / state |
|---|---|---|
| `/tmp/p1-link/runtime/ps2xRuntime/ps2EntryRunner` (both boots) | `950675bb75585a9ec1fb2f56c906df25293ed669728094b31382190ef2b94d20` (163,380,912 B) | `4326926` tree (P9 on `bfa0213`; `-j4` rebuild, exit 0) |
| `ps2x_tests` (CWD `$R`, rebuilt) | Total 428, Passed 428, Failed 0 | All green (P10 test passes; transient snddrv closed by P11; no failure face) |
| `PS2Recomp` branch `ssx3` HEAD | `4326926` (`Fix: replace the SSX3 CD-callback host shim with a CSV split at 0x3E3AD8 (P9)`, 2 files, +2/−47, three trailers) | Sole P9 fork commit; worktree `M` = generated `runner/register_functions.cpp` only, never added |
| Parent | `bfa0213` (P11 test fix, on P10 `69bb1ff`, on P7 `e235c4b`) | Peer commits landed mid-session; P9 diff survived intact |
| Fork push | `git push fork ssx3` from the fork clone only (`bfa0213..4326926`, fast-forward) | The only push allowed (no push in ssx3); `pull --rebase` refused on the unstageable generated runner file with a clean pre-fetch (`fork/ssx3` == parent), recorded §P9-4 |
| This report | `[P9]` commit (two trailers; local only) | Sole ssx3-repo change; no `runner/`, log, or `._*` added |

Source deltas vs the P25 baseline tree, all ladder-neutral in
combination: P7 (deliberately unwired stub), P10 (PollSema
miss-value; game consumers miss-agnostic per its brief), P11
(test-only), P9 (this split). Isolation of each is not claimed —
the ladder proves the combined tree reproduces P25 exactly.

## P9-4. Exact commands

From `$R` (fork) unless noted; `$W=/Volumes/Extreme SSD/ps2recomp-spike`,
`LOG1=$W/P1/run/boot-p9-1.log`, `LOG2=$W/P1/run/boot-p9-2.log`:

```
# Step 0 (context reads; lease-free)
re-read REPORT Part 21 §P21-1a (shim-vs-split) + Part 24 §P24-1 (tracked CSV) + Part 25 §P25-2 (ladder)
cat /tmp/ssx3-host-lease (absent) + tee p9-waits.log (start line)
git fetch fork ssx3 (e235c4b, clean); mkdir local/research/P9
# Step 1 (boundary re-derivation, lease-free)
grep neighbours in tracked CSV (8159: sub_003E39A8 0x158)
ELF word dump 0x3e39a8-0x3e3b00 (boundary/nop/body/padding/next-head)
grep case/label_3e3ad8 in enclosing file (0) + register slots (entry + 6 cases)
shasum pre-edit CSV (6d231e81…) + CD.cpp (961a3077…); CR count 0
# Step 1 (edits)
(edit_file: CSV row -> 2 rows; CD.cpp shim block + hook delete, -46)
grep shim refs (none); CSV 9276 lines, dup/CR/contiguity checks; git status (2 named + generated M)
# Step 1 (recomp, lease-free)
spot shas pre-recomp (4/4 match P24-1c); cd $W/P1 && bin/ps2_recomp $R/games/ssx3/ssx3.toml (rc=0, recomp-p9-split.log)
counts + spot shas post-recomp; new-file + registration + header greps
parent-nontruncation forensics (elf_parser merge code + whole-.text JAL census x2)
cp -X output/*.{cpp,h} runner/ (9277->9278); sidecar purge; diff -rq clean
find $R -name '._*' -delete; cmake --build /tmp/p1-link/runtime --target ps2EntryRunner ps2x_tests -j4 (exit 0)
ps2x_tests CWD $R > /tmp/p9-suite.log (428/427/1 transient: P10-without-P11 window)
(test-list diff vs /tmp/p1aa-after.log -> the (P10) extra; peer timeline via git log)
cmake --build ... -j4 (4 targets, P11 file only); ps2x_tests > /tmp/p9-suite2.log (428/428/0 rc=0)
git add <2 NAMED files>; staged-set verify; git commit -- <2 files> -m (3 trailers) -> 4326926
git fetch fork ssx3; git pull --rebase fork ssx3 (refused: unstaged generated runner file; pre-fetch clean)
git push fork ssx3 (bfa0213..4326926 fast-forward)
(write /tmp/p9-boot1.py + /tmp/p9-boot2.py; diffs vs p1aa scripts = docstring + LOG only)
# Step 2 (lease protocol + boot 1)
lease absent x2; pgrep -x (exit 1); shasum fresh (950675bb); git log (4326926); ls ISO + ELF
printf 'P9\n' > /tmp/ssx3-host-lease (03:16:05Z) + >> p9-waits.log
python3 /tmp/p9-boot1.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 930883 B)
# Step 2 (smoke + boot 2)
smoke: ra=0x3e3af0 x1 + shape; cd:callback pair; census 6x1 site; creates 33/-1 0
cat lease (P9); pgrep -x (exit 1)
python3 /tmp/p9-boot2.py (CWD $W/P1/run, 90 s, SIGTERM rc=-15, 612986 B)
rm -f /tmp/ssx3-host-lease (03:19:25Z); ls (absent); pgrep -x (exit 1); + >> p9-waits.log
# Step 2 (log analysis, lease already released)
(p1aa-ladder.py same-script rungs x3: P25-boot1 + boot1 + boot2)
epoch :600-630 byte-diff (IDENTICAL); watch/drop line numbers; tick dma/gif endpoints
31 off-by-2 forensics (running balance, waker census, :990 clobber, :993 wake proof, 4-log corruption census)
# Step 3 (this report; lease already released)
(write local/research/P9/REPORT.md)
git -C /Users/bradrichardson/dev/ssx3 add -f local/research/P9/REPORT.md
git -C /Users/bradrichardson/dev/ssx3 commit -m "[P9] ..." (two trailers; NO push there)
```

Machine-check paste block (every hand computation in P9):

```
python3 -c "print(hex(0x130+0x28), hex(0x3e3ad8-0x3e39a8), hex(0x3e3b00-0x3e3ad8), 757352+(0x3e3ad8-0x3e39a8)//4)"
→ 0x158 0x130 0x28 757428
```

Contiguity (`0x130`+`0x28`=`0x158`); row sizes; table slot of
`0x3e3ad8` (slot(`0x3e39a8`)=757352 from `register_functions.cpp`,
+76 words = 757428, matches `:380398`).

Receipt paths: `$W/P1/run/recomp-p9-split.log`,
`$W/P1/run/boot-p9-1.log`, `$W/P1/run/boot-p9-2.log`,
`$W/P1/run/p9-waits.log`, `/tmp/p9-suite.log` (transient),
`/tmp/p9-suite2.log` (green), `/tmp/p9-boot1.py`,
`/tmp/p9-boot2.py`, `/tmp/p9-ladder-p25b1.txt`,
`/tmp/p9-ladder-b1.txt`, `/tmp/p9-ladder-b2.txt`,
`/tmp/p9-tests-p1aa.txt`, `/tmp/p9-tests-now.txt`.

## P9-5. What I could not do

- Truncate the parent's emitted range via the CSV (recompiler
  map/fallback merge keeps the largest end per start; §P9-1d):
  proven unreachable dead code, left standing — changing the
  merge rule is a recompiler-behavior brief, not this one.
- Show the direct `0x519c40` site-#9 store row: unwatched in the
  P25 WATCH env in both baseline and P9 logs; the G6/#9 proof is
  the identical epoch shape + driver probe, same as P25 carries.
- Fix the `[frame:upload]`×`[diag:sema]` unlocked-stderr race
  (§P9-2c LOG2 note): pre-existing, 1 clobbered line in 4 logs,
  forensically closed; a locking brief owns it.
- Isolate P7/P10/P11 effects from P9's in the ladder (all four
  ship in the boot binary): the combined tree is ladder-identical
  to P25-boot1, which is the brief's bar; per-commit boots would
  exceed the 2-boot box.
- Run a 3rd boot (max 2 used; ladder + repro both closed).
- Session wall time ≈ 02:44–03:30Z (~45 min), inside the 4 h box.

