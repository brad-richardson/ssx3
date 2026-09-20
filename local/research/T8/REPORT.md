# T8 report — repetition-driver attribution: 13,108/13,108 via depth-0 376938 frame entry (no boot, read-only)

Brief `local/muse/prompts/T8.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T7/REPORT.md` full (T7
§T7-7 steps 1+2 are this brief) + P1 REPORT Part 31 §P31-2
(the single-caller census refined one frame up).

`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`R=$W/PS2Recomp` (fork, branch `ssx3`),
`T=$W/P1/run/ps2_log-p1ag-1.txt` (1.2 GB, 35,916,072
lines, 100% enter/exit). `$R`-relative paths below unless
noted. All fork/ISO/receipt reads read-only; zero fork
changes; no boots; no lease; no `adb`.

Headline readings: every `0x362DE8` enter is at depth 2
inside a fresh depth-1 `363490` frame (13,108/13,108, prologue
JAL fired, first child) inside a depth-0 `376938` frame;
repetitions per `376938` frame are exactly 1 (13,108 frames)
or 0 (378,922 frames) — 0 intra-frame repeats, 0 nested
`376938` frames; the issuing edge is frame entry from above
for 13,108/13,108. The single static site is `0x377b14`
(JAL `363490`), unspanned by any of the 14 loops; the 3
self-JALs compile to trace-invisible `goto` function-top.
The 26,216 resumes are all depth-0 dispatcher frames in
exact FRR lockstep (gaps 8/7 lines, intervening `38F300`
frames), with 75 ramp-window body variants.

## T8-0. Fork / lease / time record

| Item | Value |
|---|---|
| ssx3 HEAD at T8 | `11f368b80e2ff5c1f869863b6fba7cf5bfb58c2c` (`M24 gate read passes`) |
| ssx3 working tree | clean (no output) |
| Fork HEAD at T8 | `1a76df4614c241b3f22a0baabe79a84671408639` (= T7-end HEAD; T5 landed) |
| Fork branch | `ssx3` |
| Fork working tree | `M ps2xRuntime/src/runner/register_functions.cpp` (foreign, untouched) |
| Fork commits by T8 | 0; fork `git pull/push`: never run |
| Lease `/tmp/ssx3-p-lane-lease` | absent (never claimed) |
| `ps2EntryRunner` | absent |
| Boots | 0; `adb`: not used |
| Wall | 2026-09-20 ~06:05–06:40Z (≈35 min active), inside the 4 h box |
| ssx3 evidence commit | below (`[T8]`, no push) |

## T8-1. Fixed-count reproduction gate (reproduce or stop)

Single streaming pass (`/tmp/t8-attr.py`, stack mismatch
counter = 0, max depth 29); `grep -c` cross-checks agree.

| Counter | Observed | T7-fixed | Gate |
|---|---|---|---|
| `362DE8` enters | 13,108 | 13,108 | reproduce |
| `363490` enter / exit | 39,324 / 39,324 | 39,324 / 39,324 | reproduce |
| `376938` enter / exit | 392,030 / 392,029 | 392,030 / 392,029 | reproduce |
| Trace lines | 35,916,072 | 35,916,072 | reproduce |
| Live frames at EOF | 2 (`376938` d0 @35916067, `423DC0` d1 @35916072) | deficit 1 = live frame | reproduce (live frame + its open child) |

## T8-2. Task 1 Table 1 — repetitions per `376938` frame

Repetition = one `0x362DE8` enter (depth 2, §T8-3).
Enclosing `376938` frame = innermost open `376938` frame.

| Reps in frame | `376938` frames |
|---|---|
| 0 | 378,922 (incl. the 1 live EOF frame) |
| 1 | 13,108 |
| ≥2 | 0 |
| Total frames | 392,030 |
| Reps with no enclosing `376938` | 0 |
| Sum of reps | 13,108 |

Distribution reading: 1:1 (every rep-bearing frame carries
exactly 1; no N:1). Direct-`363490`-children per `376938`
frame: `{0: 378922, 1: 13108}` (same 13,108 frames).
Direct-`376938`-children per `376938` frame: `{0: 392030}`.
Frames with parent = `376938`: 0.

## T8-3. Task 1 Table 2 — issuing-edge census (sums to 13,108)

Per-repetition edge classes (mutually exclusive; rank = order
of the rep among its frame's reps; ancestry = enclosing
frame's ancestry):

| # | Edge class | Reps |
|---|---|---|
| E1 | Frame entry, re-entry from above (rank 1, no `376938` ancestor) | 13,108 |
| E2 | Intra-frame repeat, back-edge class (rank ≥ 2) | 0 |
| E3 | Frame entry under direct recursion (rank 1, parent = `376938`) | 0 |
| E4 | Frame entry under indirect recursion (rank 1, `376938` ancestor, parent ≠ `376938`) | 0 |
| — | SUM | 13,108 |

Enclosing-`376938`-frame signature (all 13,108 rep-bearing frames):

| Attribute | Value (×13,108 unless noted) |
|---|---|
| Frame depth | 0 (all; parent = none) |
| Children (exact, in order) | (`37D090`, `363490`), nkids = 2 |
| Enclosing `363490` frame | fresh (prologue JAL fired: `362DE8` is child #1) |
| `362DE8` depth / child position | 2 / 1 |
| Previous depth-0 enter (dispatcher order) | `395288` |
| Next depth-0 enter after frame exit | `38F300` (the gap-8 intervening frame, §T8-4) |

One-frame-up census (P31-2 refined): `362DE8` parents =
`363490` ×13,108 (0 other); `363490` parents = `376938`
×13,108 (all depth 1, all fresh) + none ×26,216 (all depth
0, all resume); fresh frames with parent ≠ `376938`: 0;
resume frames with parent = `376938`: 0.

`376938` parent census, all 392,030 frames (12 distinct):

| Parent | Frames |
|---|---|
| `391E30` | 234,594 |
| none (depth 0) | 91,818 |
| `395288` | 26,216 |
| `397DF8` | 13,056 |
| `398A60` | 13,056 |
| `232AE0` | 13,056 |
| `231FC0` | 156 |
| `232328` | 52 |
| `231D60` | 12 |
| `38EC40` | 12 |
| `375A08` | 1 |
| `228C08` | 1 |

Depth distribution: `{0: 91818, 1: 13213, 2: 247727,
3: 39249, 7: 23}`. No `376938` frame at any depth has a
`376938` parent (row count 0 above), so no `376938`
nesting exists in the trace at any depth.

## T8-4. Task 1 Table 3 — resume-frame signature (26,216 non-fresh `363490`)

Enter-order pattern over all 39,324 `363490` frames: `FRR`
× 13,108, 0 deviations (F = fresh, R = resume). Resume
pair order: body then empty (`BE` × 13,108, 0 deviations).

| Attribute | Resume-body (13,108) | Resume-empty (13,108) |
|---|---|---|
| Depth / parent | 0 / none | 0 / none |
| `362DE8` children | 0 | 0 |
| nkids | 12 (13,033 std) / 12 (12 var) / 10 (63 var) | 0 |
| First-6 kids (std) | (`396128`,`365F68`,`363C20`,`368660`,`364360`,`363C20`) ×13,033 | — |
| First-6 kids (var) | (`396128`,`365F68`,`363C20`,`368660`,`363C20`,`368660`) ×75 | — |
| Full kids (std12) | +(`363C20`,`368660`,`363C20`,`368660`,`364360`,`365FA8`,`38F300`) ×13,033 | — |
| Full kids (var10) | (`…`,`364360`,`364360`,`365FA8`,`38F300`) ×63 | — |
| Full kids (var12) | (`…`,`364360`,`363C20`,`368660`,`364360`,`365FA8`,`38F300`) ×12 | — |

Variant-window correlation: first-6-variant bodies sit at
logical-call indices 0–74 exactly (75/75); nkids-10 bodies
at 63 of 0–74 — the P31-1e ramp window (inv 0–74: 2/3/2
then 20/inv). Post-ramp bodies (calls 75–13107) are
uniform std12.

Fresh-frame uniformity (13,108): nkids = 5; kids =
(`362DE8`,`364360`,`364050`,`3666F8`,`38F300`) = T7-2
JALs #1–5 in order; `362DE8` always child #1.

Gap micro-structure (exact, all 13,108 logical calls):

| Gap | Lines | Intervening depth-0 events |
|---|---|---|
| Fresh exit → resume-body enter | 8 | `376938` exit, `38F300` enter+exit |
| Resume-body exit → resume-empty enter | 7 | `38F300` enter+exit |

T7 resume-theory confirm/kill table:

| T7 prediction | Observed | Reading |
|---|---|---|
| Resumes skip prologue (`ctx->pc` switch) | 0 `362DE8` children in 26,216/26,216; resume-body kids = JALs #6–16 | confirm |
| Resumes emit `enter` (counted in 3×) | 26,216 = 2× fresh, FRR ×13,108 exact | confirm |
| (Unspecified) resume ancestry | All depth 0, parent none (no `376938` nesting) | refine: stronger than stated |
| 2 resumes per logical call | body + empty, `BE` ×13,108 | confirm + split typed |

Mechanism note (read-only source): every guest dispatch
is a deterministic safe point —
`ps2xRuntime/src/lib/ps2_runtime.cpp:1714-1725`
(`checkpointDue` → `return false` → C++ frame returns);
post-call `return ctx->pc == fallthroughPc` (:1800-1812)
unwinds the yield up the C++ stack; dispatcher re-enters
the yielded frame at its resume pc (depth-0 `enter`).
Stub/missing targets with `SkipCallDebug` set
`pc = fallthroughPc`, `return true` (:1738-1745) —
invisible in the trace (no `enter`/`exit`).

## T8-5. Task 2.1 — winning-edge disassembly (edge E1, site `0x377b14`)

Unit: `ps2xRuntime/src/runner/sub_00376938_0x376938.cpp`
(`0x376938–0x37a260`); 30 direct JALs (single JAL to
`363490` @`0x377b14`); 23 `jalr` (22 `$v0`, 1 `$v1`);
20 `jr $ra`; 225 control-flow comment rows. ELF column
from `$W/P1/SLUS_207.72` (offset = vaddr − `0xFF000`);
comment words match ELF in all 33 sampled words.

Issuing window (`0x377ae0–0x377b1c`, straight-line: no
branch, no `jr`, between the rows):

| Addr | Word (comment) | Instr | ELF word |
|---|---|---|---|
| `0x377ae0` | `0x40f809` | `jalr $v0` | `0x0040f809` |
| `0x377ae4` | `0x36106600` | `ori $s0,$s0,0x6600` (delay) | `0x36106600` |
| `0x377ae8` | `0x8e6310d8` | `lw $v1,0x10D8($s3)` | `0x8e6310d8` |
| `0x377aec` | `0x846401b0` | `lh $a0,0x1B0($v1)` | `0x846401b0` |
| `0x377af0` | `0x8c6201b4` | `lw $v0,0x1B4($v1)` | `0x8c6201b4` |
| `0x377af4` | `0x40f809` | `jalr $v0` | `0x0040f809` |
| `0x377af8` | `0x2642021` | `addu $a0,$s3,$a0` (delay) | `0x02642021` |
| `0x377afc` | `0x8e6418f0` | `lw $a0,0x18F0($s3)` | `0x8e6418f0` |
| `0x377b00` | `0x26675a14` | `addiu $a3,$s3,0x5A14` | `0x26675a14` |
| `0x377b04` | `0x27a80014` | `addiu $t0,$sp,0x14` | `0x27a80014` |
| `0x377b08` | `0x27a60010` | `addiu $a2,$sp,0x10` | `0x27a60010` |
| `0x377b0c` | `0x26655a00` | `addiu $a1,$s3,0x5A00` | `0x26655a00` |
| `0x377b10` | `0x8e715a00` | `lw $s1,0x5A00($s3)` | `0x8e715a00` |
| `0x377b14` | `0xc0d8d24` | `jal func_363490` | `0x0c0d8d24` |
| `0x377b18` | `0x8e725a14` | `lw $s2,0x5A14($s3)` (delay) | `0x8e725a14` |
| `0x377b1c` | `0xc108f78` | `jal func_423DE0` | `0x0c108f78` |
| `0x377b20` | `0x8e645acc` | `lw $a0,0x5ACC($s3)` (delay) | `0x8e645acc` |

JAL target check: `0x0c0d8d24` → `(0x000d8d24<<2)` =
`0x363490`; return addr `0x377b18`.

Loop structure around the site (14 MIPS back-edges =
14 C++ loop `goto`s 1:1; ELF spot-checks match):

| # | Back-edge | Target | Loop range | Spans `0x377b14`? |
|---|---|---|---|---|
| 1 | `0x3779b4 b` | `0x377994` | `0x377994–0x3779b4` | no (ends `0x13C` below run-up) |
| 2 | `0x37871c bnez $t2` | `0x378698` | `0x378698–0x37871c` | no (above) |
| 3 | `0x378964 bnez $v0` | `0x378938` | `0x378938–0x378964` | no (above) |
| 4 | `0x378b20 bnel $v0` | `0x3788e0` | `0x3788e0–0x378b20` | no (above) |
| 5 | `0x378bdc bnez $v0` | `0x378bb0` | `0x378bb0–0x378bdc` | no (above) |
| 6 | `0x378e48 bnel $v0` | `0x378b58` | `0x378b58–0x378e48` | no (above) |
| 7 | `0x379194 bnez $v0` | `0x379168` | `0x379168–0x379194` | no (above) |
| 8 | `0x379350 bnel $v0` | `0x379110` | `0x379110–0x379350` | no (above) |
| 9 | `0x37940c bnez $v0` | `0x3793e0` | `0x3793e0–0x37940c` | no (above) |
| 10 | `0x379678 bnel $v0` | `0x379388` | `0x379388–0x379678` | no (above) |
| 11 | `0x379a88 bne $a2,$a3` | `0x379a68` | `0x379a68–0x379a88` | no (above) |
| 12 | `0x379ab0 beqz $v0` | `0x379978` | `0x379978–0x379ab0` | no (above) |
| 13 | `0x379fa0 bnez $a2` | `0x379e60` | `0x379e60–0x379fa0` | no (above) |
| 14 | `0x37a178 bnez $a2` | `0x37a060` | `0x37a060–0x37a178` | no (above) |

Per-frame issue bound: 0 of 14 loops span the site, so
the site executes at most once per pass from unit top
(or region entry) to the `363490` dispatch; trace bound
is exactly once (§T8-3: nkids = 2, one `363490` child).

Recursion structure (3 self-JALs; ELF word `0x0c0dda4e`
→ `0x376938` at all three):

| Site | Delay slot (ELF) | Emission | Trace signature |
|---|---|---|---|
| `0x376b5c` | `swc1 $f21,0x6D2C($v0)` (`0xe4556d2c`) | `ra=ret; goto label_376938` (no dispatch, no log) | invisible |
| `0x377208` | `swc1 $f0,0x5858($v0)` (`0xe6005858`) | same shape | invisible |
| `0x3778e4` | `swc1 $f1,0x5854($v0)` (`0xe6015854`) | same shape | invisible |

Guards above the sites are straight-line FP/store runs
(no branch within 6 instrs: `0x376b44–58` mult/addu/
stores; `0x3771f0–208` stores; `0x3778cc–e4` `swc1` run)
— reachability is decided by earlier forward branches
(not enumerated: trace-invisible either way).

Region entry (run-up approach `0x377a08–0x377ae0`):

| Addr | Word | Instr | Note |
|---|---|---|---|
| `0x377a08` | `0x3e00008` | `jr $ra` | ELF `0x03e00008`; no fall-through |
| `0x377a0c` | `0x0` | `nop` (delay) | ELF `0x00000000` |
| `0x377a10` | `0x27bdff80` | `addiu $sp,$sp,-0x80` | fresh prologue (`sq $s0/s1/s3/s2`, `sd $ra` follow) |
| `0x377a48` | `0x40f809` | `jalr $v0` | `$v0` = struct-loaded (all 4 `jalr` in region likewise) |
| `0x377a88` | `0x40f809` | `jalr $v0` | — |

Direct-CFG entry check: no forward branch from below
`0x377a08` lands in `[0x377a08,0x377b14]`; the only 4
branches landing there are internal ifs
(`0x377a50→68`, `0x377a60→80`, `0x377a90→a8`,
`0x377aa0→c0`); none skips a `jalr`. So the region
executes its 4 `jalr`s (`0x377a48/a88/ae0/af4`) whenever
entered — while rep frames show exactly one visible
`jalr` child (`37D090`): 3 of the 4 must hit
stub/missing targets on the rep path (§T8-6 row 5).

## T8-6. Task 2.2 — examined-and-absent (losing candidates)

| # | Candidate (T7 lead) | Where looked | Reading |
|---|---|---|---|
| 1 | Recursion via self-JAL `0x376b5c` | Emission (~L4525) + full-trace parent census | `goto` top, no log; 0 `376938`-parented frames |
| 2 | Recursion via self-JAL `0x377208` | Emission (~L6840) + same census | same as #1 |
| 3 | Recursion via self-JAL `0x3778e4` | Emission (~L9078) + same census | same as #1 |
| 4 | Loop issuing ≥2 reps in one frame | §T8-5 14-loop span column + Table 1 | 0 loops span site; 0 frames with ≥2 reps (E2 = 0) |
| 5 | Indirect recursion via `395288` (26,216 `376938` frames parented under it) | Rep-bearing-frame parent census | 0 rep-bearing frames have parent `395288` (all depth 0) |
| 6 | `363490`-internal loop issuing `362DE8` | T7 §T7-2–3 (carried) + fresh nkids = 5 uniform | sole JAL `0x3634cc`, once per fresh entry |
| 7 | Second static JAL to `363490` | Full 30-JAL inventory (§T8-5) | absent: only `0x377b14` |
| 8 | Resume frames issuing reps | 26,216 resumes, `nde8` = 0 all | absent: reps only from fresh frames |
| 9 | Which of 4 region `jalr`s issues `37D090` | `$v0` data-flow (all struct-loaded) | unresolvable statically; arg probe needed (§T8-7) |
| 10 | Direct-CFG path entry-top → `0x377a10` | All fwd-branch targets + `jr $ra` @`0x377a08` | absent: indirect-or-resume entry only (§T8-10) |

## T8-7. Task 2.3 — step-3 recommendation TABLE (inputs each needs)

| Step | Shape | T8 inputs already on disk | Further inputs needed | Output if taken |
|---|---|---|---|---|
| 3a | Loop + site-readable bound → emitter samples `(i,N)` per `363490` enter | No loop spans `0x377b14` (14-row table); per-frame issue = 1; rep frames uniform (prev `395288`) | A loop above depth-0 `376938` with a readable bound (unidentified; the outer dispatcher sequence is the search area) | `(i,N)` series → `N−i` + P31-1b rate = projection |
| 3b | Recursion depth/arg counter → progress proxy | 0 nested `376938` frames; self-JALs are trace-invisible gotos; pre-call self-cycles bounded to call-free-or-stub-only by exact-2-kid frames | pc probe firing counts for the 3 self-`goto` sites (trace cannot see them) | monotone proxy (no total `N`) |
| 3c | No readable bound → empirical `N` via run-to-exit | P31-6c exit signatures (carried); uniform per-rep microstructure (FRR + gaps 8/7 + prev/next rows) as in-trace progress counters | ~10 min P-lane lease, P31-6d 600 s boot shape | `N` empirically; no per-sample `i` |

## T8-8. Supporting — non-rep depth-0 `376938` census (78,709 + 1 live)

| Kids signature (exact) | Frames | nkids |
|---|---|---|
| (`64B88`,) | 26,268 | 1 |
| () | 13,120 | 0 |
| (`423DE0`,`423DC0`,`423DC0`) | 13,107 | 3 |
| (`4247D8`,`4247D8`,`362CC8`,`3673D0`,`395288`×3) | 13,107 | 7 |
| (`361F90`,) | 13,107 | 1 |
| live EOF frame (open `423DC0` child) | 1 | — |

Count relations (observed, no verdict): three classes at
exactly 13,107 (= reps − 1); empty frames 13,120
(= reps + 12); `64B88` frames 26,268 (= 2 × 13,134).
nkids distribution: `{0: 13120, 1: 39375, 3: 13107,
7: 13107}`. Pairing of these frames to logical
rep-bearing calls (continuation chains) is not
established (§T8-10).

## T8-9. Exact commands used

From `/Users/bradrichardson/dev/ssx3` unless noted; `W`,
`R`, `T` as above. All receipt/fork/ELF accesses
read-only (`grep`/`sed`/`python3` reads, `head`/`tail`/
`wc`); no builds, no boots, no fork writes, no lease
claims:

```
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" log --oneline -3; git -C "$R" status --porcelain=v1; git -C "$R" branch --show-current
ls /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (absent)
head/sed windows of T (format recon: tab indent + >>/<< + sub_ADDR enter/exit)
grep -c sub_00362DE8/00363490/00376938 enter/exit T (13108/39324/39324/392030/392029)
grep -n 363490/376938 enter/exit T (first-frame structure: fresh d1 + 2 resumes d0)
write /tmp/t8-attr.py; python3 /tmp/t8-attr.py (single streaming pass: Tables 1+2+3)
write /tmp/t8-gap.py; python3 /tmp/t8-gap.py (gaps/intervening/variants/context)
grep JAL/jalr/jr inventories in sub_00376938 file (30/23/20)
write /tmp/t8-cfg.py; python3 /tmp/t8-cfg.py (branch targets; 14 back-edges; span check)
backward-goto census via python (17 = 3 self + 14 loop, 1:1 with MIPS)
sed windows: self-JAL emission; loop-goto emission; run-up approach; jalr emission
grep -n dispatchGuestBranch def; sed ps2_runtime.cpp:1702-1812 (checkpoint/stub/call/return-false)
python3 ELF word reads SLUS_207.72 (33 words: 17 window + 6 self-JAL + 6 loop + 4 boundary)
(mkdir + write local/research/T8/REPORT.md + 2 TSVs; this file)
git add -f local/research/T8/REPORT.md local/research/T8/reps-per-frame.tsv local/research/T8/issuing-edge.tsv
git commit -m "[T8] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T8-10. What I could not do (gap rows)

- Name which of the 4 region `jalr`s (`0x377a48/a88/ae0/
  af4`) issues `37D090`: all `$v0` are struct-loaded;
  needs a `$v0`/arg probe at those sites (emitter work).
- Name the entry mechanism into the `0x377a10` region
  (indirect jump vs resume pc): no direct CFG edge
  exists; needs a pc probe (trace has no pc).
- Count self-`goto` firings (`0x376b5c/0x377208/0x3778e4`):
  trace-invisible by construction (no dispatch, no log);
  needs a pc probe; rep frames bound pre-call cycles to
  call-free-or-stub-only (§T8-5).
- Explain the intervening depth-0 `38F300` frames (gaps
  8/7, ×26,216): scheduler/dispatcher internals, outside
  the attribution scope.
- Pair continuation frames (§T8-8) to logical rep-bearing
  calls: needs an ordering/chain pass (not run).
- Identify the outer driver loop above depth-0 `376938`:
  prev-frame `395288` is uniform but the issuing
  loop/condition is not located (step-3a search area).
- Session wall ≈35 min active, inside the 4 h box.

