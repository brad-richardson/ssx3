# T5 report — Analyzer rule: materialized `.text` pointers are function entries

Brief `local/muse/prompts/T5.md`. TOOLING brief: 1 fork commit
(rule + unit tests) + 2 proof boots (max used) + first emitter-vs-emitter
ladder. Tables, no verdicts. Stale-reading guard: review Part 2 §12 row
T5 + `local/research/T1/REPORT.md` (emitter + `ladder_diff`) re-read;
the brief's "P1 Part 11" resolves to the Part 21 §P21-1 receipt (table
below) plus P9 §P9-1a (boundary re-derivation this rule automates).

`R=/Volumes/Extreme SSD/ps2recomp-spike/PS2Recomp` (fork, branch
`ssx3`), `W=/Volumes/Extreme SSD/ps2recomp-spike`, `RUN=$W/P1/run`.
Peer lanes concurrent; shared only the fork remote.

Headline receipts: +172 splits (predicted set == actual set, `diff`
clean); `0x3E3AD8` re-derived at 2 real sites (dedup no-op on the P9
row); suite 439/439/0; D = 1054 exact / 245 tol-ok / 3 sampled /
2 KEY_DELTA / 0 COUNT_DELTA.

## T5-0. Lease record + tree state at start

| Event | Value |
|---|---|
| Waits log | `$W/P1/run/t5-waits.log` (3 lines: start, claim, release; 0 waits) |
| ssx3 HEAD at start | `c8871d9` (T5 brief written); `M docs/todo.md` pre-existing, untouched |
| Fork HEAD at start | `a611702` == required base (no peer commits; HEAD unchanged all session) |
| Fork `M` at start | `ps2xRuntime/src/runner/register_functions.cpp` (pre-existing generated, never staged) |
| Lease at start / pre-claim ×2 / pre-boot-2 | Absent / absent / `T5` held; `pgrep -x` exit 1 at all three |
| Hold | `claim 06:28:08Z` – `release 06:31:29Z` (~3.5 min, both boots back-to-back) |
| `adb` | Not used |

"Part 11" resolution (the `0x3E3AD8` receipt the brief cites):

| Brief text | Finding |
|---|---|
| `P1/REPORT.md` Part 11 (§§P11-0..5, lines 3864–4027) | P1j bit-table cheat; **0** `0x3E3AD8` mentions |
| `0x3E3AD8` in `P1/REPORT.md` | Only lines 6730–7029 = Part 21 §P21-1 (shim receipt used here) |
| Boundary table used for the fixture | P9 §P9-1a (`jr`/`delay`/`nop` above `0x3E3AD8`, body `lui…jr`) |

## T5-1. Placement (where the rule lives)

| Candidate | Evidence | Used |
|---|---|---|
| `ps2xAnalyzer` `analyzeDataUsage` (f2149e7's file) | TOML carries no function entries (stubs/mmio/patches/jump-tables only); recomp's list comes from `ElfParser::extractFunctions`; an analyzer-only change cannot move recomp counts, leaving Task 2 unprovable | No |
| `PS2Recompiler::DiscoverAdditionalEntryPoints` (test-named "split") | Called only from `ps2xTest` (0 pipeline callers); extending it moves no count and no boot | No |
| `ElfParser::extractFunctions` (`ps2xRecomp/src/lib/elf_parser.cpp`) | Shared by `ps2_analyzer` AND `ps2_recomp` (`elf_analyzer.cpp:94`); feeds recomp counts + boots; sibling `ScanJalTargetsFallback` is the discovery-scan precedent | **Yes** |

Fold shape (mirrors f2149e7 + `ScanJalTargetsFallback`):

| Decision | Value | Precedent |
|---|---|---|
| Scan | Every `isCode` section with `data`, `size ≥ 4`, `address != 0`; raw words via `memcpy` | Sibling scan shape |
| LUI | `OPCODE==LUI`, `rt != 0` (`$zero` writes discarded) | f2149e7 opcodes |
| Window | Forward 5 insns, same-register (`RS==RT==reg`) `ORI` (`\|=`) / `ADDIU` (`+=` signed) in program order, no clobber-break | f2149e7 lines, direction flipped |
| Fold requires | ≥1 low-half writer (bare LUI excluded); 4-aligned value | Brief's "LUI+ORI/ADDIU fold" |
| Target must be | In EE code (`isCode`, `address != 0`) AND strictly inside an already-known function range (`start > fn.start && start < fn.end`) | "Split" (brief's noun); excludes the 8 `.vutext` values |
| Merge | `addOrMerge` (dedup + authoritative rules inherited); `end = 0` filled by the existing next-start loop | Zero new merge semantics |
| Name | `MakeAutoFunctionName` (`sub_%08X`) | Sibling/map vocabulary |

## T5-2. Census (lease-free, `/tmp/t5-census.py`, read-only)

| Item | Value |
|---|---|
| Fold sites → code | 376 (367 `.text`, 9 `.vutext`) |
| Distinct / novel (not CSV start) / in-range (predicted splits) | 301 / 180 / **172** |
| Novel but outside any CSV range | 8, all `.vutext` (`0x42e590 0x430a80 0x434990 0x435bd0 0x439a40 0x43b3f0 0x43bd00 0x43cca0`) — excluded by the inside-check |
| Contributing EXEC sections | `.text` only (31 linkonce + `.vutext` + 32 overlays: 0 sites each) |
| Folds with value `< 0x100000` | 0 (addr-0 overlay hazard never fires on this ELF) |
| ELF symbols | 0 (`analyzer.log`: "Extracted 0 symbols") — authoritative set empty, all 172 survive `addOrMerge` |

`0x3E3AD8` materialization (rule re-derives the P9 split):

| Site | Words | Container (CSV) |
|---|---|---|
| `0x3E3FB0` | `lui $a0,0x3E`; `jal 0x4008A0`; (`addiu $a0,$a0,0x3AD8` in delay) | `sub_003E3D78` `0x3e3d78–0x3e4000` |
| `0x3E442C` | `lui $a0,0x3E`; `jal …`; (`addiu $a0,$a0,0x3AD8` in delay) | `sub_003E4040` `0x3e4040–0x3e44b0` |
| Value | `0x3E0000 + 0x3AD8 = 0x3E3AD8`, already a CSV start → dedup no-op, no new file | — |

`0x426230` materialization (the +1 stub, §T5-5):

| Site | Words | Note |
|---|---|---|
| `0x425EA8` | `lui $a1,0x42`; `jal`; `nop`; `lui $a1,0x42`; `addiu $a0,$0,5`; `addiu $a1,$a1,0x6230` (j=5, window edge) | Both sites in `sub_00425D38`; target in `sub_004261F0` `0x4261f0–0x426358` |
| `0x425EB4` | `lui $a1,0x42`; `addiu $a0,$0,5`; `addiu $a1,$a1,0x6230` (j=2) | `$a1` = callback-arg register |

## T5-3. Fixture + unit tests (tests first)

`writeMinimalMipsElfWithMaterializedEntries` (no symtab: container is the
entry-point fallback parent, non-authoritative — SSX3 game code likewise):

| va | word | Role |
|---|---|---|
| `0x100000` | `lui $a0,0x10` | Test-1 site |
| `0x100004` | `ori $a0,$a0,0x20` → `0x100020` | `.text`-interior fold |
| `0x100008` | `lui $a1,0x20` | Test-2 site |
| `0x10000C` | `addiu $a1,$a1,0x10` → `0x200010` | `.data` control (no entry) |
| `0x100010` | `jr $ra` | P9-boundary above split |
| `0x100014` | `addiu $sp,0x10` | Delay |
| `0x100018` | `nop` | Padding |
| `0x10001C` | `lui $v0,0x10` | Split point (callback head, `0x3E3AD8`-class) |
| `0x100020` | `addiu $sp,-0x10` | Test-1 target (mid-function) |
| `0x100024` | `lui $a2,0x10` | Fixture site (`0x3E3FB0`-class, neutral gap filler) |
| `0x100028` | `nop` | Gap |
| `0x10002C` | `addiu $a2,$a2,0x1C` → `0x10001C` | Split-point fold |

| Test (`PS2Recompiler`) | BEFORE | AFTER |
|---|---|---|
| `materialized .text pointer splits its container` (`0x100020` entry + parent `[0x100000,0x100030)` intact) | FAIL | Pass |
| `materialized data pointer creates no entry` (no `0x200010`) | Pass (guard) | Pass |
| `0x3E3AD8-class mid-function callback splits` (`0x10001C`) | FAIL | Pass |

## T5-4. Suite BEFORE / AFTER (per face, total/passed/failed)

| Face | BEFORE | AFTER |
|---|---|---|
| CodeGenerator | 56/56/0 | 56/56/0 |
| ElfAnalyzerHeuristics | 6/6/0 | 6/6/0 |
| PS2GS | 71/71/0 | 71/71/0 |
| PS2IopSubsystem | 7/7/0 | 7/7/0 |
| PS2Memory | 47/47/0 | 47/47/0 |
| **PS2Recompiler** | **20/18/2** | **20/20/0** |
| PS2RuntimeExpansion | 31/31/0 | 31/31/0 |
| PS2RuntimeIO | 11/11/0 | 11/11/0 |
| PS2RuntimeInterrupt | 8/8/0 | 8/8/0 |
| PS2RuntimeKernel | 40/40/0 | 40/40/0 |
| PS2SifDma | 16/16/0 | 16/16/0 |
| PS2SifRpc | 15/15/0 | 15/15/0 |
| PS2VU0Math | 44/44/0 | 44/44/0 |
| PS2VU1 | 40/40/0 | 40/40/0 |
| PadInput | 12/12/0 | 12/12/0 |
| R5900Decoder | 15/15/0 | 15/15/0 |
| **Total** | **439/437/2** | **439/439/0** |

BEFORE binary = tests-only tree (rule not yet written), rc=2; AFTER
binary = rule tree, rc=0. Same `ld` duplicate-library warning as T1
(pre-existing). CWD `$R` both runs.

## T5-5. Fork commit + push

| Item | Value |
|---|---|
| Commit | `1a76df4` (`Analyzer: treat materialized .text pointers as function entries (T5)`, +289/−0, `Orchestrated-By: Muse Code`) |
| Staged set | `ps2xRecomp/src/lib/elf_parser.cpp` (+116), `ps2xTest/src/ps2_recompiler_tests.cpp` (+173) — named files only, verified |
| `._*` purges | Before every build + before staging (ExFAT precedent) |
| `pull --rebase` | Refused on the unstaged generated runner file (P9 §P9-3 precedent); pre-fetch clean (`fork/ssx3 == a611702`, no peer commits) |
| Push | `git push fork ssx3` from the fork clone only (`a611702..1a76df4`, fast-forward); `fork/ssx3 == 1a76df4` |
| NEVER in ssx3 | No `git push` in ssx3 (evidence commit local only, §T5-8) |

## T5-6. Recomp counts (same tree otherwise; isolated TOMLs/outputs)

Binaries: OLD `b462300d…` (worktree @ `a611702`), NEW `4a9fa31a…`
(post-commit). TOML diff = `output` line only; `$W/P1/output` untouched.

| Check | OLD (`recomp-t5-old.log`) | NEW (`recomp-t5-new.log`) | Delta |
|---|---|---|---|
| Ghidra map loaded | 9275 | 9275 | None |
| Discovered / processed | 9274 | 9446 | **+172** |
| Recompiled / stubs / skipped | 9097 / 177 / 0 | 9268 / 178 / 0 | +171 / **+1** / 0 |
| Decode failures / unhandled / errors | 0 / 0 / 0 | 0 / 0 / 0 | None |
| Additional entrypoints | 393728 | 401370 | +7642 (resume targets of the new units) |
| Generated functions | 9274 | 9446 | +172 |
| Indirect fallback promotions (entries) | 3598 (724964) | 3710 (739730) | +112 (+14766) |
| Warnings | 3598 | 3710 | +112 (new units' JR/JALR sites) |
| Output entries | 9277 | 9449 | +172 (files added 172, removed 0) |
| Predicted-vs-actual split set | — | `diff` clean | 172/172 identical |

+1 stub: `sub_00426230_0x426230.cpp` is the `_sceSifCmdIntrHdlr` wrapper
(TOML `"_sceSifCmdIntrHdlr@0x00426230"` bound nothing before — no
function started at `0x426230`; the rule created the entry, the
selector now binds). Sites §T5-2.

`0x3E3AD8`-class coverage: `0x3E3AD8` already emitted (P9 row, present
in OLD output); the rule re-derives it at 2 real sites (§T5-2) and
`addOrMerge` dedups (0 re-added files).

New splits: 172 (full list `local/research/T5/splits.txt`), first 50:

`0x1001d0 0x100204 0x123400 0x195000 0x199940 0x1d5c28 0x1d5f38 0x1d68e8 0x1d7010 0x1d72a8 0x1d7318 0x1d7420 0x1d7548 0x1d7688 0x1d7c68 0x1d8160 0x1ddd38 0x1ddd48 0x1ddd68 0x1ddd78 0x1ddda8 0x1dddb8 0x242978 0x244868 0x244870 0x245e30 0x245e78 0x245ec0 0x2526b8 0x253ad0 0x259390 0x2634c0 0x2668a8 0x268ab8 0x268ae0 0x268b08 0x268b30 0x268b58 0x268b80 0x268ba8 0x268bd0 0x268bf8 0x268c20 0x268c48 0x268c98 0x268cc0 0x268ce8 0x268d10 0x268d38 0x268d60`

## T5-7. Proof boots + emitter-vs-emitter ladder

Binaries (clean worktrees + own recomp outputs): BASE `7250de23…`
163,460,272 B (`a611702` + OLD output); RULE `06eb5cd7…`
165,583,296 B (`1a76df4` + NEW output). Env = `/tmp/t1-boot1.py` +
`PS2X_DIAG_PARK_DIR` isolation (script diffs verified: LOG/BIN/dir
only). `$W/P1/run/park-snapshot.json` untouched (T1's 05:39Z leftover).

| Rung | BASE (`boot-t5-base.log`) | RULE (`boot-t5-rule.log`) | Delta |
|---|---|---|---|
| Lines / bytes | 206,673 / 36,434,915 | 207,108 / 36,589,251 | Throughput +0.2% |
| Run | 90 s foreground, SIGTERM, rc=0 | 90 s foreground, SIGTERM, rc=0 | None |
| `[diag:park]` | `:206666` → `/tmp/t5-park-base/` (111,497 B json) | `:207101` → `/tmp/t5-park-rule/` (111,499 B json) | None |
| Stub lines / thread blocks | 527 / 102 | 527 / 102 | None — exact |
| Threads (snapshot) | 1 WAIT29, 2 WAIT26, 3 WAIT30, 4 WAIT31, 5 Ready, 6 WAIT36 | 1 Running, 2 WAIT26, 3 WAIT30, 4 WAIT31, 5 WAIT32, 6 WAIT36 | t1/t5 sampled phase (D rows) |
| Sched counts | t1 10584, t5 10558, t4 5281 | t1 10603, t5 10577, t4 5291 | TOL_OK ≤1.2% |
| Sema creates | 37 | 37 | None — exact |
| RPC | 4 unclaimed calls, 21 loads, 1 sendcmd | Same | None — exact |
| Drops | 6× `dispatchSyscallOverride/KE_ERROR` (`syscall=0x5b`) | 6× identical bytes | None — exact |
| Hot-pc top | `0x41ea18` @ 953,381 (= T1's count) | `0x41ea18` @ 953,381 | None — exact |
| GS kicks/gif/copy | 1,275,036 / 146,428 / 162,718 | 1,277,232 / 146,680 / 162,997 | TOL_OK 0.2% |
| Crash / FATAL | 0 / 0 | 0 / 0 | None |

D (`tools/ladder_diff.py base rule`, `T5/D.txt`, 1306 lines):
**1054 exact, 245 tol-ok (worst 1.2% `sched.-1`), 3 sampled, 2 deltas
→ DELTA**, rc=1. Section census: thread 12, sema 17, wait-hist 32,
signal-hist 34, hotpc 1188 (966 exact + 222 tol-ok), drop 1 (EXACT),
rpc 5, gs 8, sched 7. COUNT_DELTA: 0.

The 2 KEY_DELTA rows, exactly as printed:

| Row | BASE | RULE | Verdict |
|---|---|---|---|
| `sema.29.table` | `(0, 0, 0, 1)` | `(0, 0, 0, 0)` | KEY_DELTA |
| `sema.32.table` | `(0, 16, 0, 0)` | `(0, 16, 0, 1)` | KEY_DELTA |

Correlated rows from the same diff (tabled, not explained away):

| Row | BASE | RULE | Verdict |
|---|---|---|---|
| `thread.1.status` | `(2, 2, 29)` WAIT29 | `(0, 0, 0)` live | SAMPLED |
| `thread.5.status` | `(1, 0, 0)` live | `(2, 2, 32)` WAIT32 | SAMPLED |
| `sema_wait_hist.29` / `sema_signal_hist.29` | 5281 / 5280 | 5290 / 5290 | TOL_OK 0.2% (balanced both) |
| `sema_wait_hist.32` / signals (`.0x423dc8`+`.0x423dd8`) | 15837 / 15837 | 15865 / 15864 | TOL_OK 0.2% (balanced both) |

**D-verdict: DELTA** (2 waiter-presence KEY_DELTAs; cumulative 29/32
histories balanced and tol-ok both sides).

## T5-8. Gaps

| # | Gap | Why unresolved |
|---|---|---|
| 1 | Waiter-phase attribution for the 2 KEY_DELTAs | Needs a 3rd boot to re-sample SIGTERM phase; box used 2/2 |
| 2 | Rule entries inside authoritative (symbol-sized) ranges are merge-rejected (inherited `addOrMerge`) | Unfired here (0 ELF symbols); no test names it (brief fixes 3 tests) |
| 3 | 8 `.vutext` fold values excluded by the inside-check (VIF-upload address class) | By design (§T5-1); values tabled §T5-2 |
| 4 | N64's data-pointer half (words in `.data` pointing at `.text`) | Out of scope: brief extends the register fold only |
| 5 | `PS2X_DIAG_PARK_TIMEOUT_MS` mid-run path | Implemented by T1, unfired here (unset, as in T1's proof) |

## T5-9. Exact commands

```
# census (lease-free, read-only)
python3 /tmp/t5-census.py                                    # 376 sites / 172 predicted
# tests first (fork clone, lease-free)
cmake -S $R -B /tmp/t5-link/runtime -G Ninja <T1 flags>      # 63 s configure
cmake --build /tmp/t5-link/runtime --target ps2x_tests -j4
cd $R && /tmp/t5-link/runtime/ps2xTest/ps2x_tests            # BEFORE 439/437/2 rc=2
# rule (same tree) + AFTER
(edit ps2xRecomp/src/lib/elf_parser.cpp)
cmake --build /tmp/t5-link/runtime --target ps2x_tests -j4   # 1-file rebuild
cd $R && ps2x_tests                                          # AFTER 439/439/0 rc=0
# fork commit + push (fork clone only)
git add ps2xRecomp/src/lib/elf_parser.cpp ps2xTest/src/ps2_recompiler_tests.cpp
git commit -- <2 files> -m "Analyzer: ... (T5)"              # 1a76df4
git fetch fork ssx3; git pull --rebase fork ssx3             # refused (generated M), pre-fetch clean
git push fork ssx3                                           # a611702..1a76df4
# recomp old/new (isolated TOMLs/outputs; $W/P1/output untouched)
git worktree add --detach /tmp/t5-base a611702
cmake -S /tmp/t5-base -B /tmp/t5-base-link/runtime <T1 flags>
cmake --build /tmp/t5-base-link/runtime --target ps2_recomp -j4     # OLD b462300d
cmake --build /tmp/t5-link/runtime --target ps2_recomp -j4          # NEW 4a9fa31a
sed 's|^output = .*|output = "/tmp/t5-recomp-old/output/"|' $R/games/ssx3/ssx3.toml > /tmp/t5-old.toml
sed 's|^output = .*|output = "/tmp/t5-recomp-new/output/"|' $R/games/ssx3/ssx3.toml > /tmp/t5-new.toml
/tmp/t5-base-link/.../ps2_recomp /tmp/t5-old.toml            # rc=0, 9274
/tmp/t5-link/.../ps2_recomp /tmp/t5-new.toml                 # rc=0, 9446
comm -13 files-old files-new                                 # 172 added, 0 removed
# boot binaries (clean worktrees + own outputs, lease-free)
git worktree add --detach /tmp/t5-rule 1a76df4
cp /tmp/t5-recomp-old/output/*.{cpp,h} /tmp/t5-base/ps2xRuntime/src/runner/
cp /tmp/t5-recomp-new/output/*.{cpp,h} /tmp/t5-rule/ps2xRuntime/src/runner/
cmake -S /tmp/t5-rule -B /tmp/t5-rule-link/runtime <T1 flags>
cmake --build /tmp/t5-base-link/runtime --target ps2EntryRunner -j4 # BASE 7250de23
cmake --build /tmp/t5-rule-link/runtime --target ps2EntryRunner -j4 # RULE 06eb5cd7
# proof (lease T5 held 06:28:08Z-06:31:29Z only; 0 waits)
printf 'T5\n' > /tmp/ssx3-p-lane-lease; python3 /tmp/t5-boot-base.py  # 90 s, rc=0
python3 /tmp/t5-boot-rule.py                                          # 90 s, rc=0
rm /tmp/ssx3-p-lane-lease
# D (lease released)
python3 $R/tools/ladder_diff.py /tmp/t5-park-base/park-snapshot.json \
  /tmp/t5-park-rule/park-snapshot.json --names base,rule             # DELTA (2 KEY_DELTA)
```

Machine-check paste block (every hand computation in T5):

```
python3 -c "print(hex(0x3E0000+0x3AD8), hex(0x420000+0x6230), 9446-9274, 401370-393728)"
→ 0x3e3ad8 0x426230 172 7642
python3 -c "print(hex((0x0C100228&0x03FFFFFF)<<2), hex(0x3e3fb0+8))"
→ 0x4008a0 0x3e3fb8
```

Row 1: `0x3E3AD8` fold; `0x426230` fold; split delta; entrypoint delta.
Row 2: real-site JAL target (`jal` at `0x3E3FB4`, delay ADDIU at `0x3E3FB8`).

Receipt paths: `$W/P1/run/boot-t5-base.log`,
`$W/P1/run/boot-t5-rule.log`, `$W/P1/run/t5-waits.log`,
`/tmp/t5-suite-before.log`, `/tmp/t5-suite-after.log`,
`/tmp/t5-recomp-old.log`, `/tmp/t5-recomp-new.log`,
`/tmp/t5-boot-base.py`, `/tmp/t5-boot-rule.py`, `/tmp/t5-census.py`,
`/tmp/t5-predicted.txt`, `/tmp/t5-old.toml`, `/tmp/t5-new.toml`,
`local/research/T5/{REPORT.md,D.txt,splits.txt,park-snapshot-base.json,park-snapshot-rule.json}`.

## T5-10. What I could not do

- Re-sample the SIGTERM phase (gap 1): 2/2 boots used; lease released.
- Run a 3rd boot (max 2 used; D + ladder both closed).
- Session wall ≈05:50–06:35Z (≈45 min incl. 4 builds + census + 2 boots),
  inside the 4 h box.
