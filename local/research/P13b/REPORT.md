# P13b — Unmatched-selector validation + build identity manifest (read-only)

Brief `local/muse/prompts/P13b.md`. Tables, no verdicts.
Standalone evidence dir `local/research/P13b/` (this report + `receipts/`).
Read-only: fork + SSD touched by `grep`/`sed`/`awk`/reads and read-only
`git`/`python3` miners only; no fork writes, no boots, no lease, no `adb`.
`W=/Volumes/Extreme SSD/ps2recomp-spike`, `R=$W/PS2Recomp` (fork, branch
`ssx3`, HEAD `b6252bb` at read time), `OUT=$W/P1/output`,
`RUN=$W/P1/run`. `R`-relative file:line refs unless noted.

Note on the brief's P13 pointers: P13 `REPORT.md` §F3 names the 4
selectors but carries no separate owners table (§P13-6/11 are command
outputs, not committed text). Owners + containment are re-derived fresh
below (§P13b-2) instead of quoted.

## P13b-0. Experiment contract

| Item | Value |
|---|---|
| Hypothesis | The 4 P13-F3 unmatched stub selectors are still unmatched on the current tree, each mid-function inside a recompiled owner; none fired in the K1-era (T26/K1) committed/boot traces; the CSV↔TOML↔generator↔runtime↔binary chain re-derives with any drift explained |
| Observable | Selector match counts vs both CSVs; owner ranges + selector-in-owner emission lines; pc-census hits in T26/K1/P1ac traces + parks + committed evidence; runtime handler existence per name; sha/mtime/HEAD per manifest column |
| Alternatives | (a) counts drifted (a selector now matches, or a 5th unmatched) → table the delta + causing commit; (b) a selector/owner fired in-window → table counts + lines, disposition changes to boot-blocking; (c) T5 (post-P13 generator change) alters next-regen matching → table predicted flips statically (no regen run, read-only) |
| Stop | 3 h box; stop at first boot/build/lease need (forbidden) and table it as a gap with the pin command |
| Result-shape | Status + evidence + recommended disposition per selector; no PASS/FAIL verdicts |

## P13b-1. Re-derivation of 181→177+4 (current tree)

Headline: **confirmed, zero drift**. Same 181 selectors, same 177 matched,
same 4 unmatched with the same owners, against either CSV copy.

| # | Check | P13 value | P13b value (HEAD `b6252bb`) | Drift |
|---|---|---|---|---|
| 1 | TOML `stubs` entries (fork) | 181 | 181 (`R/games/ssx3/ssx3.toml:27-207`) | None |
| 2 | TOML `stubs` entries (SSD `$W/P1/ssx3.toml`) | 181 | 181 (`:24-204`); block byte-identical to fork (`cmp` clean, receipts `stubs_*.txt`) | None |
| 3 | Fork CSV rows / unique starts | 9275 / 9274 | 9275 / 9274 (1 dup `0x42c1f0`) | None |
| 4 | SSD CSV rows / unique starts | 9274 / 9273 (stale pre-P9) | 9274 / 9273, sha16 still `6d231e815672e79f` = P24-1a | None (still stale, unchanged) |
| 5 | Matched by start (vs fork CSV) | 177 | 177 | None |
| 6 | Unmatched (vs fork CSV) | 4 (same names+addrs) | 4, identical set (§P13b-2) | None |
| 7 | Matched/unmatched vs SSD CSV | — (P13 used fork CSV) | 177 / 4, same set (P9 split touches no selector) | N/A (new check) |
| 8 | Name-half matches for the 4 | 0 | 0 (no CSV row carries any of the 4 SDK names) | None |
| 9 | Output `// Address:` files | 9097 | 9097; sorted range set **diff-empty** vs `P13/receipts/output_ranges.txt` | None |
| 10 | Output stub (non-Address) files | 177 | 177 (`receipts/non_address_files.txt`) | None |
| 11 | Output residue | register + stale `sub_0042C1F0` (F7) | Same 2 files (stale still Sep 18) | None |
| 12 | Output entries / equation | 9278; 9097+177=9274=CSV−dup | Same; `register_functions.cpp` sha16 `05836f4b15579383` = P9 post-split | None |
| 13 | `ps2_recompiled_stubs.h` decls | 177 | 177 `void` decls; none of the 4 names present | None |
| 14 | Skip selectors | 0 | 0 (`skip = []` both TOMLs) | None |

Why the P9 CSV split (post-P13-commit? no — **pre**-P13-HEAD) is not drift:
`4326926` (P9 split, Sep 19 23:15) is an ancestor of P13 HEAD `da6a2d5`
(Sep 20 00:14); P13's 9275-row fork CSV already contains it
(`git show da6a2d5:games/...csv | wc -l` = 9276 lines). P13's "9274"
is unique starts (9275−1 dup), matching the replica receipts
(`range_check.txt` counts unique starts; `jal_replica.txt` counts rows).

## P13b-2. Selector tables ×4 (boot-relevant first)

Shared method: owner = CSV row strictly containing the selector addr;
offset = selector − owner start; emission = `// 0x…` + `ctx->pc` lines in
the owner's recompiled file; JAL/materialization censuses from
`receipts/p13b_sel.py` (output `receipts/selector_context.txt`); trace
censuses over `syscalls-t26-on.txt` (785,356 ev), `syscalls-k1-on.txt`
(783,250 ev), `boot-t26-1.log` (6,739,664 pc values), `boot-k1-1.log`
(492,861), `boot-p1ac-1/2.log` (16,189/16,320), both park snapshots, and
committed `local/research/T26/` + `local/research/K1/` evidence.

### P13b-2a. `_sceSifCmdIntrHdlr@0x426230` (TOML fork `:156`)

| Row | Status + evidence |
|---|---|
| Owner + offset | `sub_004261F0` `[0x4261f0–0x426358)` (CSV + `// Address:` identical); offset **+0x40** (16 insns in) |
| Mid-function evidence | Prev words `addiu $sp,+$0x10; nop` (prior logical fn epilogue); selector = `addiu $sp,−0x90` + reg saves + `jal 0x42c0c0` (COP0-Status reader) — a real SDK entry Ghidra merged; emitted at owner file `:223-225` (`label_426230`, `ctx->pc = 0x426230u`) |
| Indirect entry | **Enterable**: owner has the every-address fallback switch; `case 0x426230u: goto label_426230` (`:38`) |
| Registration (callback source) | `sub_00425D38:0x425ebc/0x425ec0`: `a0=5, a1=0x426230; jal 0x423ab0` = `AddDmacHandler(5, 0x426230)` (syscall `0x12`; DMAC ch 5 = SIF0). Sole materialization of the addr (2 LUI sites `0x425ea8/0x425eb4`, one a JAL delay-slot dup); 0 direct JALs; owner called from 3 sites |
| Boot firing (K1-era) | **Silent in-window**: wrapper-1 pc `0x423ab8` = 0/0 events (T26/K1); the single `AddDmacHandler (12)` in each trace sits at `pc=0x423ac8` = wrapper-**2** +8, i.e. from one of 3 other call sites (`0x375e28/0x408e88/0x40918c`), not the registrant. Owner-range pcs: 0 in both syscall traces, both boot logs, both parks, committed T26/K1 evidence |
| Boot firing (P13-era) | 0 owner pcs in `boot-p1ac-1/2.log`; no syscall channel then (pre-T22), so wrapper-level firing unresolvable there (gap G5) |
| Callback-target validity | Target **valid as code**: real entry + exact dispatch case → a scheduler IRQ dispatch with `ctx->pc=0x426230` enters the handler correctly through the owner. Runtime stores the pair silently (`Interrupt.cpp:addHandler`, no log/park state) |
| Would-be HLE binding | `ps2_stubs::sceSifCmdIntrHdlr` exists but is itself `TODO_NAMED` (`SIF.cpp:14-16`); selector resolves via the leading-underscore alias (`ps2_runtime_calls.h`). If matched, the stub file would trap instead of running guest code |
| Silence consequence today | None observed (handler never registered in-window, never invoked) |
| Silence consequence on next regen | **Regen flips it**: T5 (`1a76df4`, post-P13) splits at materialized addrs strictly inside known functions — `0x426230` qualifies (sole selector of the 4 that does) → new function start → selector **matches** → real handler replaced by the TODO trap. Predicted T5 splits overall: 172 new (replica; gap G3) |
| Recommended disposition | Before the next regen, either (a) drop this selector from TOML `stubs` (T5 split then yields exact table entry + recompiled guest handler), or (b) implement a real `ps2_stubs::sceSifCmdIntrHdlr` HLE first and keep it. Do not regen with selector + trap-HLE as-is |

### P13b-2b. `sceSifLoadIopHeap@0x42AD28` (TOML fork `:184`)

| Row | Status + evidence |
|---|---|
| Owner + offset | `sub_0042AD08` `[0x42ad08–0x42b068)` (CSV = Address header); offset **+0x20** (8 insns) |
| Mid-function evidence | Prev `addiu $sp,+$0x10; nop` (epilogue); selector = `lui $v0,0x45; addiu $sp,−0x30; lw $v1,0x5224($v0); …` + 6× `jal 0x426d18` (`sceSifCallRpc` HLE stub). Real entry; emitted at owner file `:76-77` (no `case`, no `label_` — plain fall-through lines) |
| Indirect entry | **Not enterable**: sparse switch cases `{0x42ad18,…,0x42b044}` skip it; entry path returns at `jr $ra @0x42ad1c` before it. A hypothetical indirect call with `ctx->pc=0x42ad28` hits `default:` → runs the owner **head** (wrong code) and returns |
| Callers | 0 JALs to the selector; 0 materializations; 0 other mid-function JAL targets in the owner; owner start called from 2 sites (`0x3c238c/0x3c4d88`) |
| Boot firing | **0 everywhere**: no owner-range pcs in either syscall trace, any of the 4 boot logs, either park, or committed evidence. (The `pc=0x42b0e8` RPC line firing 1× per boot belongs to the *next* function `sub_0042B068`, not this owner — exact-range census §P13b-5) |
| Callback-target validity | N/A (no registration/call path references this addr); as a would-be indirect target it is **invalid** (no dispatch case → wrong-code entry) |
| Would-be HLE binding | `ps2_stubs::sceSifLoadIopHeap` = canned `setReturnS32(ctx, 0)` (`SIF.cpp:717`) |
| Silence consequence | None in-window (dead code: unreachable head of an unreached region). Latent: any future indirect caller lands on owner-head code silently |
| Next-regen prediction | Stays unmatched (not materialized → no T5 split; replica §P13b-5) |
| Recommended disposition | CSV split at `0x42ad28` (P9 pattern: exact table entry; parent keeps full range harmlessly per P9 §d) **keeping** the stub selector, so the HLE canned-0 serves any future caller. Alternative: split + drop selector to keep the guest RPC worker |

### P13b-2c. `sceSifLoadFileReset@0x42B1F8` (TOML fork `:185`)

| Row | Status + evidence |
|---|---|
| Owner + offset | `sub_0042B168` `[0x42b168–0x42b230)` (CSV = Address header); offset **+0x90** (36 insns) |
| Mid-function evidence | Prev `jr $ra` + delay `addiu $sp,+$0x50` + `nop`; selector = `addiu $sp,−0x10; …; sw −1→0x455228; jal 0x416210` (`memset` HLE stub); returns 0. Real entry; emitted at owner file `:201-202` (no case/label) |
| Indirect entry | **Not enterable**: sparse cases `{0x42b1a4,0x42b1bc,0x42b1d0,0x42b220}` skip it; entry returns at `0x42b1ec` before it. Same wrong-code-on-`default` shape as 2b |
| Callers | 0 JALs; 0 materializations; 0 other mid-function JAL targets; owner start called from 7 nearby sites (`0x42b270…0x42bae0`) |
| Boot firing | **0 everywhere** (same census battery as 2b; all four boot logs + both traces + parks + committed evidence) |
| Callback-target validity | N/A (no reference path); invalid as indirect target (no case) |
| Would-be HLE binding | `ps2_stubs::sceSifLoadFileReset` = canned `setReturnS32(ctx, 0)` (`SIF.cpp:712`) |
| Silence consequence | None in-window (dead); same latent wrong-code hazard as 2b |
| Next-regen prediction | Stays unmatched (not materialized) |
| Recommended disposition | Same as 2b: CSV split at `0x42b1f8` keeping the stub selector (canned-0 serves future callers); alternative split + drop selector |

### P13b-2d. `InitTLB@0x42CD58` (TOML fork `:206`)

| Row | Status + evidence |
|---|---|
| Owner + offset | `sub_0042CCB8` `[0x42ccb8–0x42cd98)` (CSV = Address header); offset **+0xA0** (40 insns). Owner is a run of syscall wrappers (entry = `addiu $v1,0x56; syscall` = WaitEventFlag wrapper) |
| Mid-function evidence | Prev `jr $ra; nop`; selector = `addiu $sp,−0x10; jal 0x424200` (GetMemorySize/`0x7F` wrapper); `bne v0,0x2000000` memsize check; `jal 0x42cd98` (next function). Real SDK InitTLB; emitted at owner file `:266-268` with label |
| Indirect entry | **Enterable**: sparse switch (12 cases) includes `case 0x42cd58u` (`:30`); entry path returns at `0x42ccc0` before it, so the case is the only entry |
| Callers | 0 JALs; 0 materializations; 0 other mid-function JAL targets; owner start called from 5 sites (one, `0x42cce4`, inside the owner) |
| Boot firing | **0 everywhere** (same battery); `(56)` and `(82)` syscall events are 0 in both traces |
| Callback-target validity | N/A (no reference path); valid as indirect target (exact case) if one ever arises |
| Would-be HLE binding | `ps2_syscalls::InitTLB` — the emitter tries syscall names first and it resolves (`System.cpp:647`, real TLB clear + `cop0_index=0`; also live as syscall `0x82` via `Dispatcher.cpp:395`) |
| Silence consequence | None in-window (dormant but correctly enterable) |
| Next-regen prediction | Stays unmatched (not materialized) |
| Recommended disposition | CSV split at `0x42cd58` keeping the stub selector (wire the reviewed HLE TLB clear to any future caller); alternative split + drop selector to keep the guest memsize-probe body |

## P13b-3. Identity manifest (ONE table)

Each column read at fork HEAD `b6252bb` / ssx3 HEAD `f3fd739`
(Sep 20 21:xx EDT) except where the cell names an older pin.

| # | Artifact (role) | Location read | Identity (rev/sha/mtime) | Content head |
|---|---|---|---|---|
| 1 | Fork CSV (canonical) | `R/games/ssx3/ssx3.toml`→`games/ssx3/ssx3-functions.sweep.csv` | `b6252bb` tree; sha16 `b9aae74782fde6ba`; last touch `4326926` (P9 split, Sep 19 23:15); `git diff da6a2d5..HEAD -- games/` empty | 9275 rows / 9274 unique; dup `0x42c1f0`; owns the 4 selectors' ranges |
| 2 | SSD CSV (working copy) | `$W/P1/ssx3-functions.sweep.csv` | sha16 `6d231e815672e79f` = P24-1a; mtime Sep 18 23:32 (stale, untouched since P1w) | 9274 rows / 9273 unique; lacks the P9 `0x3e3ad8` row; fed only `output-p11` |
| 3 | Fork TOML (canonical) | `R/games/ssx3/ssx3.toml` | `b6252bb` tree; sha16 `4974423573dd7db9`; last touch `5b5ac3d` (P1w, Sep 19 20:12); 1622 lines | 181 stubs + 391 untracked + 0 skip; carries the 4 selectors (`:156,184,185,206`) |
| 4 | SSD TOML (working copy) | `$W/P1/ssx3.toml` | sha16 `d97cf95300273e2b` = P24-1a; mtime Sep 18 21:15 (P1h analyzer output, untouched since) | 1619 lines; stubs/untracked blocks `cmp`-identical to fork (only the 4 P1w header/path hunks differ) |
| 5 | Generator sources (behavior) | `R/ps2xRecomp` + `R/ps2xAnalyzer` | `b6252bb`; `git diff da6a2d5..HEAD` = **only** `elf_parser.cpp +116` (T5 `1a76df4`, Sep 20 02:03); `ps2_recompiler.cpp`/`config_manager.cpp`/`toml_generator.cpp`/`sce_symbol_scanner.cpp` byte-identical to P13 HEAD | Stub parse/install/match logic unchanged (F3/F21a sites intact); T5 adds materialized-entry splits (172 predicted, incl. `0x426230`) |
| 6 | Generator binary (actual regen) | `$W/P1/bin/ps2_recomp` | sha256 `7654e7fe…e826f`; mtime Sep 18 12:49 — **predates the ssx3 branch** (first branch commit `c0af340` Sep 18 15:19); source HEAD unrecorded (gap G1) | Drove `recomp-p9-split.log` (rc=0): fork TOML, 9275 CSV rows, 9274 discovered, 9097 recompiled, 177 stubs, 0 err, 393728 entrypoints |
| 7 | Analyzer binary (TOML author) | `$W/P1/bin/ps2_analyzer` | sha256 `4bf4ba2b…3e699f`; mtime Sep 18 12:49 (same pre-branch caveat) | Authored the 181-stub list (P1h era) from embedded SCE DB (all 4 names present: 6/3/3/17 records) |
| 8 | Recompiled output | `$W/P1/output/` (9278 entries) | Regen Sep 19 22:46 (`recomp-p9-split.log`); `register_functions.cpp` sha16 `05836f4b15579383` = P9 (untouched since); range set diff-empty vs P13 receipt | 9097 Address + 177 stub files + register + F7 stale; 4 owners recompiled with selectors mid-body (§P13b-2) |
| 9 | Runner mirror (linked binding) | `R/ps2xRuntime/src/runner/` (9278 entries) | `diff -rq` vs output/ **clean**; `git status` = `M register_functions.cpp` (generated, uncommitted, as in every pane) | Runtime links exactly the §P13b-2 code; per-word table maps each selector addr to its owner fn |
| 10 | T26 boot binary | `/tmp/p1-link/…/ps2EntryRunner` at T26 time | sha `7f155f4c…b377`, 163464560 B (recorded, bytes superseded — gap G6); tree `6359fb6` (T22, no rebuild) | Produced `syscalls-t26-on.txt` + `boot-t26-1.log` (the 1.57M-event / 7.2M-pc censuses above) |
| 11 | K1 boot binary | same path, live now | sha16 `72b2cfc59dbf09de` verified live; 163483200 B; tree `b6252bb` = current HEAD | Produced `syscalls-k1-on.txt` + `boot-k1-1.log`; `[k1]` + P0 capture the only deltas vs T26 |
| 12 | Guest ELF | `$W/P1/SLUS_207.72` (+ `cd/` twin) | sha16 `1b49d05ca2793922`; 3890784 B (both paths, both boots) | All ELF words/JAL/materialization facts read against these bytes |
| 13 | Reference output (pre-split) | `$W/P1/output-p11/` (9276 entries) | Regen Sep 19 23:16 (`recomp-p11-presplit.log`, `/tmp/p11-ssx3.toml`, 9274 rows → 9096 recompiled) | Control: same 177 stubs; lacks only the P9 child; not linked by any boot binary |

## P13b-4. Gaps (with the exact pin command)

| # | What the manifest cannot pin | Exact command that would pin it (not run — read-only / needs boot) |
|---|---|---|
| G1 | `bin/ps2_recomp` source HEAD (pre-branch build, no build log) | `cmake --build /tmp/p13b-build --target ps2_recomp -j4` from `b6252bb` + `cd $W/P1 && /tmp/p13b-build/ps2_recomp $R/games/ssx3/ssx3.toml` to a scratch dir, then `diff -rq` vs `output/` (also pins G3 exactly) |
| G2 | Which of the 3 wrapper-2 sites fired the single `(12)`; registered `(cause,handler)` values (no arg log, no park IRQ state) | One booted brief with an `addHandler` arg line (`cause= handler=`), or a `PS2X_DIAG_PARK` IRQ-table extension; then `grep AddDmacHandler $RUN/syscalls-*.txt` + park diff |
| G3 | T5 split replica is approximate (CSV ranges vs the generator's post-JAL-merge ranges; `addOrMerge` edge absorption) | The G1 regen itself: `grep -c` new `sub_*.cpp` + `Functions discovered` delta in its log |
| G4 | Owner-body execution that issues no syscall and publishes no logged pc is unwitnessed (no block coverage in-window) | A `PS2_FUNCTION_LOG_TRACKER` (or block-census) boot: `grep -c "sub_004261F0\|sub_0042AD08\|sub_0042B168\|sub_0042CCB8" $RUN/boot-*.log` |
| G5 | P13-era wrapper-level firing (P1ac logs predate the T22 `pc=` channel) | Unpinnable historically; T22+ traces (used here) are the earliest resolvable source |
| G6 | T26 binary bytes (path rebuilt by K1; only the sha survives) | Detached worktree at `6359fb6` + copy of `output/` into `runner/` + `cmake --build … --target ps2EntryRunner -j4`, then `shasum` vs `7f155f4c…` |

## P13b-5. Exact commands

From `/Users/bradrichardson/dev/ssx3` unless noted; every SSD step with
`export COPYFILE_DISABLE=1`. All reads; writes only to `local/research/P13b/`
(evidence) and `/tmp/p13b-*` (scratch miners).

```text
# Context reads
sed -n '1,356p' local/research/P13/REPORT.md                      # P13 F3/inventory/receipts
sed -n '7983,8252p' local/research/P1/REPORT.md                   # P24-1f/g census + 12 rules
read local/research/T26/REPORT.md + local/research/K1/REPORT.md   # K1-era trace keys
sed -n '60,130p' local/research/P9/REPORT.md                      # P9 split regen record
# Re-derivation (§P13b-1)
python3 stub-block parse both TOMLs (181/181; 4 found w/ line nos)
python3 csv match vs fork+SSD CSVs (177+4 both; owners; 0 name-hits)
grep -rh "^// Address: 0x" $W/P1/output | sort > /tmp/p13b_ranges_now.txt  # 9097
diff <sorted P13 receipt> /tmp/p13b_ranges_now.txt               # empty
for f in $W/P1/output/*.cpp; do grep -L "^// Address: 0x" $f; done  # 179 = 177 stubs + register + F7 stale
git -C $R log --oneline --follow -- games/ssx3/ssx3-functions.sweep.csv  # 4326926, 5b5ac3d
git -C $R merge-base --is-ancestor 4326926 da6a2d5               # 0 (split predates P13)
git -C $R diff --stat da6a2d5 HEAD -- games/                     # empty
shasum -a 256 {fork,SSD} CSV/TOML + ELF + bin/* + register + runner binary
# Per-selector (§P13b-2)
python3 /tmp/p13b_sel.py > receipts/selector_context.txt         # entry/sel disasm + JAL + T5-mat + mid-JAL
grep -n -i "<seladdr>" $W/P1/output/<owner>.cpp                  # containment (4 files)
grep -n "case 0x" <owner>.cpp (4 files)                          # dispatch entry per selector
sed -n entry/context ranges of the 4 owner files                 # fall-through vs return proof
grep -rn "<4 names>" $R/ps2xRuntime/ --include=*.cpp,*.h         # handler existence
sed -n stub emission $R/ps2xRecomp/src/lib/ps2_recompiler.cpp:1130-1200 + resolve fns
# Boot firing (T26/K1/P1ac)
grep "(12)" $RUN/syscalls-{t26,k1}-on.txt                        # 1 each, pc=0x423ac8 (wrapper2)
python3 pc-range census both traces (owners+registrant+wrappers) # all 0
python3 pc-range census boot-{t26,k1,p1ac-1,p1ac-2}.log           # all 0 (6.7M+493k+16k+16k pcs)
grep -c "pc=0x423ab8" both traces                                # 0/0 (registrant silent)
grep -c "(56) (82) (78)" both traces                             # 0 (all)
grep -rn -i "426230|42ad28|42b1f8|42cd58|…" local/research/T26/ local/research/K1/  # none
grep -i -c "4261f|42ad0|42b16|42ccb" park-*/park-snapshot.txt    # 0/0
# Manifest (§P13b-3)
git -C $R log --oneline da6a2d5..HEAD -- ps2xRecomp ps2xAnalyzer  # 1a76df4 only
git -C $R show 1a76df4 -- ps2xRecomp/src/lib/elf_parser.cpp      # T5 scan+split rule
grep summary lines recomp-{p1w-tracked,p9-split,p11-presplit}.log # regen provenance
cmp stub/untracked blocks fork-vs-SSD TOML                       # identical
diff -rq $W/P1/output/ $R/ps2xRuntime/src/runner/                # clean
python3 T5 replica (mat scan + strictly-inside CSV)              # 301 mat / 172 new / sel∩={0x426230}
# Evidence + commit (NO push)
cp /tmp/p13b_{sel.py,ranges_now.txt,noaddr.txt,stubs_fork.txt,stubs_p1.txt} local/research/P13b/receipts/
git add -f local/research/P13b/; git commit -m "[P13b] …" -m "Orchestrated-By: Muse Code"
```

## P13b-6. Tail receipt

Report written in 4 chunks (`write_file` + 3 `edit_file` appends);
closing 3 lines quoted verbatim below
(`tail -3 local/research/P13b/REPORT.md` at commit):

```text
P13b evidence complete: 181->177+4 confirmed, T5 flips 0x426230 next regen.
Trailer: Orchestrated-By: Muse Code.
End of P13b report.
```

P13b evidence complete: 181->177+4 confirmed, T5 flips 0x426230 next regen.
Trailer: Orchestrated-By: Muse Code.
End of P13b report.
