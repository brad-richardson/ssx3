# T10 report — outer-driver search: 54-frame modal chain + owner-unit disassembly (no boot, read-only)

Brief `local/muse/prompts/T10.md`. Tables, no verdicts.
Stale-reading guard: `local/research/T8/REPORT.md` full (T8 §T8-7
step 3a's missing input + §T8-8 census + §T8-10 pairing gap are
this brief).

`W=/Volumes/Extreme SSD/ps2recomp-spike`,
`R=$W/PS2Recomp` (fork, branch `ssx3`),
`T=$W/P1/run/ps2_log-p1ag-1.txt` (1.2 GB, 35,916,072
lines). `$R`-relative paths below unless noted. All fork/ISO/
receipt reads read-only; zero fork changes; no boots; no lease;
no `adb`.

Headline readings: the 13,108 rep-bearing depth-0 `376938`
frames sit one-per-cycle in a 54-frame dispatcher cycle (REP +
53-slot modal gap, 13,032/13,107 gaps byte-identical; the 75
non-modal gaps are exactly rep ordinals 0–74); every gap
carries exactly one C3/C7/C1b at fixed offsets +5/+15/+18
(13,107/13,107, zero exceptions, variants included) plus
2×C1a + 1×E with tabled extras; the deeper tree pairs 1:1:1
(C7-3rd-kid→d2, slot-51→d1→d3, 0 collisions). Owner units
`395288`/`232AE0`/`231FC0`/`232328`/`38F300` hold 3/0/0/0/1
loops, none spanning any `376938`-issuing site; all
`376938` issues from owners are indirect (`jalr`, struct-loaded
targets). The per-d0-frame iterator is the host scheduler loop
`EeScheduler::run()` (`while (!stop)`, no trip count).

## T10-0. Fork / lease / time record

| Item | Value |
|---|---|
| ssx3 HEAD at T10 | `4dfcec853fbfe42e466ddc1591cabda802943810` (`T10+T6+M26 briefs written …`) |
| ssx3 working tree | `M docs/numbers-ledger.md`, `M docs/todo.md` (concurrent lanes, untouched by T10) |
| Fork HEAD at T10 | `935a4ebf6db16c4057c30f5dd5cdba23af0ff3b6` (moved since T8's `1a76df4` by peer lanes) |
| Fork branch | `ssx3` |
| Fork working tree | `M ps2xRuntime/src/runner/register_functions.cpp`, `?? tools/__pycache__/` (foreign, untouched) |
| Fork commits by T10 | 0; fork `git pull/push`: never run |
| Lease `/tmp/ssx3-p-lane-lease` | absent (never claimed) |
| `ps2EntryRunner` | absent |
| Boots | 0; `adb`: not used |
| Wall | 2026-09-20 ~06:45–07:15Z (~30 min active), inside the 4 h box |
| ssx3 evidence commit | below (`[T10]`, no push) |

## T10-1. Fixed-count reproduction gate (reproduce or stop)

Pass 1 reproduced every T8 top row; pass 2 (bug-fix re-run:
C1a addr `00364B88`, d0 `363490` resumes included) confirms.
`grep -c` cross-checks agree on all five counters.

| Counter | Observed | T8-fixed | Gate |
|---|---|---|---|
| `362DE8` enters (depth 2) | 13,108 | 13,108 | reproduce |
| `363490` enter / exit | 39,324 / 39,324 | 39,324 / 39,324 | reproduce |
| `376938` enter / exit | 392,030 / 392,029 | 392,030 / 392,029 | reproduce |
| Trace lines | 35,916,072 | 35,916,072 | reproduce |
| Stack mismatches / max depth | 0 / 29 | 0 / 29 | reproduce |
| Live frames at EOF | 2 (`376938` d0 @35916067, `423DC0` d1 @35916072) | 2 | reproduce |
| FRR triplets ≠ FRR | 0 | 0 | reproduce |
| Resume B/E pairs ≠ BE | 0 | 0 | reproduce |
| Rep-bearing depth-0 `376938` | 13,108, kids (`37D090`,`363490`) ×13,108 | 13,108 | reproduce |
| Rep prev-d0-kind census | `395288` ×13,108 (sole) | mode `395288` | reproduce + full |
| Rep next-d0-kind census | `38F300` ×13,108 (sole) | mode `38F300` | reproduce + full |
| Non-rep depth-0 `376938` | 78,709 closed + 1 live | 78,709 + 1 | reproduce |
| … kids (`64B88`,) / () / C3 / C7 / (`361F90`,) | 26,268 / 13,120 / 13,107 / 13,107 / 13,107 | same | reproduce |

Depth-0 frame totals (corrected: pass 1 omitted the 26,216
d0 `363490` resumes from its d0 list; pass 2 includes them):

| Counter | Value |
|---|---|
| Depth-0 frames | 711,362 (= 685,146 + 26,216) |
| Distinct depth-0 kinds | 186 |
| d0 `363490` resumes | 26,216 (= 2×13,107 gaps + 2 post-trace-cut) |
| d0 `38F300` | 26,217 (= 2×13,107 + 2 post + 1 pre) |
| d0 `395288` | 26,216 (= 2×13,107 + 0 post + 2 pre) |
| d0 `376938` | 91,818 (= 13,108 rep + 78,709 non-rep + 1 live) |

## T10-2. Task 1 — continuation pairing in dispatcher order

### T10-2a. Inter-rep gap census (13,107 gaps, 31 patterns)

| Pattern | Gaps | First rep ordinal | Length |
|---|---|---|---|
| modal | 13,032 | 75 | 53 |
| v01 | 14 | 36 | 38 |
| v02 | 11 | 52 | 39 |
| v03 | 11 | 63 | 36 |
| v04 | 9 | 1 | 37 |
| v05 | 4 | 27 | 49 |
| v06 | 2 | 29 | 48 |
| 24 singletons | 1 each | 0, 10–26, 28, 34, 35, 37, 51, 74 | 36–50, 56, 70, 81, 100, 119, 127, 156–176, 320, 328, 539, 548, 607, 1005 |

Non-modal gap ordinals = exactly 0–74 (75/75; the T8
0–74 ramp window). Slots 1–16 are byte-identical in all 31
patterns; slot 53/last = `395288` in all 31 patterns.

### T10-2b. Modal per-call chain (REP + 53 slots, ×13,032)

Full table also in `modal-slots.tsv`. `376938`-slot classes
uniform 13,032/13,032 each.

| Slot | Addr | Slot | Addr | Slot | Addr |
|---|---|---|---|---|---|
| REP | `376938` rep | 19 | `232AE0` ∅ | 37 | `39ECB0` |
| 1 | `38F300` | 20 | `316F00` | 38 | `39F100` |
| 2 | `363490` body | 21 | `3E4AF0` | 39 | `398038` |
| 3 | `38F300` | 22 | `37E120` | 40 | `232AE0` ∅ |
| 4 | `363490` empty | 23 | `C1638` | 41 | `316F00` |
| 5 | `376938` **C3** | 24 | `423DE0` | 42 | `376938` **E** |
| 6 | `423DE0` | 25 | `382760` | 43 | `397DF8` |
| 7 | `382760` | 26 | `31A3C0` | 44 | `3A04F0` |
| 8 | `382650` | 27 | `423DE0` | 45 | `39AE98` |
| 9 | `423DC0` | 28 | `31AAF0` | 46 | `398798` |
| 10 | `382760` | 29 | `423DE0` | 47 | `39E6B8` |
| 11 | `382650` | 30 | `31A6B8` | 48 | `20E8E0` |
| 12 | `423DC0` | 31 | `316F00` | 49 | `39EBE0` |
| 13 | `382760` | 32 | `2C5570` | 50 | `397DF8` |
| 14 | `423DC0` | 33 | `23D660` | 51 | `232AE0` →d1 |
| 15 | `376938` **C7** | 34 | `23D618` | 52 | `376938` **C1a** |
| 16 | `376938` **C1a** | 35 | `1D8DE0` | 53 | `395288` ∅ |
| 17 | `395288` ∅ | 36 | `186A08` | next | `376938` rep |
| 18 | `376938` **C1b** | | | | |

(`∅` = empty frame; `→d1` = owns the d1 `376938` subtree.)

### T10-2c. Class pairing to logical rep calls (exact offsets)

Offsets in depth-0 frames from the preceding rep frame
(`rⱼ`). C3/C7/C1b/C1a#1 offsets are single-valued over ALL
13,107 gaps (variants included).

| Class | Per gap | Offset(s) from `rⱼ` | Coverage |
|---|---|---|---|
| C3 (`423DE0`,`423DC0`,`423DC0`) | 1 in 13,107/13,107 | +5 ×13,107 | every gap |
| C7 (7-kid) | 1 in 13,107/13,107 | +15 ×13,107 | every gap |
| C1b (`361F90`,) | 1 in 13,107/13,107 | +18 ×13,107 | every gap |
| C1a#1 (`364B88`,) | 1 in 13,107/13,107 | +16 ×13,107 | every gap |
| C1a#2 | 1 in 13,107/13,107 | +52 modal (13,032); scattered variants | every gap |
| E () | 1 in 13,107/13,107 | +42 modal (13,032); scattered variants | every gap |
| C1a#3 (extra) | +1 in 51 gaps | scattered | gaps 0–50 exactly |
| E#2 (extra) | +1 in 12 gaps | scattered | gaps 51–62 exactly |

Budget closure: C1a = 2×13,107 + 51 + 3 pre = 26,268;
E = 13,107 + 12 + 1 pre = 13,120.

### T10-2d. Deeper 1:1:1 structure (subtree pairing)

| Structure | Count | Pairing reading |
|---|---|---|
| C7's three d1 `395288` kids | 13,107 triples contained | rank 3rd = (`376938`,) 13,107/13,107; ranks 1–2 empty |
| d2 `376938` under `395288` | 13,108, kids (`395288`×3), 0 reps | preceding-rep distinct 13,108, 0 collisions (= 1/gap + 1 pre) |
| d3 `376938` under `395288` | 13,108, kids (`395288`×3), 0 reps | preceding-rep distinct 13,108, 0 collisions (= 1/gap + 1 pre) |
| d1 `376938` under slot-51 | 13,107 in gaps + 1 pre (empty) | `232AE0` ×13,056 (gaps 51–13106) + `232328` ×52 (gaps 0–50); `231FC0` ×104 variant-only (kids ×6/`37D968`, 0 with-`6938`-kid) |
| d0 `232AE0` empty | 26,088 | modal slots 19 + 40 (13,032 each) + 24 variant |
| d0 `232AE0` →(`376938`,) | 13,056 | modal slot 51 (13,032) + gaps 51–74 (24) |
| d0 `232AE0` →(`397DF8`,) | 12 | preceding reps 51–62 (the E-double gaps) |
| d0 `232AE0` 4-kid | 1 | preceding rep 37 |
| d1/d2 `38F300` (empty) | 13,108 / 13,108 | parents `363490` ×13,108 (resume-body last kid / fresh 5th kid) |
| d1 `395288` under `375A08` | 3 (pre-chain triple) | 3rd has (`376938`,) @17272; = pre-chain d2 extra |
| d2 `395288` →(`376938`,) pre | 1 (@19363) | = pre-chain d3 extra |
| d2 `395288` →(`3691F8`,) pre | 1 (@14107) | sole fire of `395288`'s first JAL |

### T10-2e. Boundaries (pre-first-rep / post-last-rep)

| Region | Frames | Contents |
|---|---|---|
| Pre (`d0idx` 0–293) | 294 | 3×C1a + 1×E; `375A08` cluster (@14107, @17268–81, @19363); full list `chain-prefix.tsv` |
| Post (trace cut mid-chain) | 5 | modal slots 1–5 (`38F300`,`363490`-body,`38F300`,`363490`-empty,C3-live) |
| Live EOF frame | 1 | C3-shaped (`423DE0`,`423DC0`,`423DC0`), exit None |

## T10-3. Task 2 — the issuing loop (disassembly)

### T10-3a. Owner-unit inventories (T7/T8 method; ELF `vaddr − 0xFF000`)

| Unit | Instrs | JAL (direct) | `jalr` | Back-edges (loops) | Spans `376938`-issue? |
|---|---|---|---|---|---|
| `376938` (T8) | 0x376938–0x37a260 | 30 (1→`363490` @`0x377b14`) | 23 | 14 | 0 span `0x377b14` |
| `395288` | 302 | 2 (`3691F8` @294, `3956B0` @3d0; none →`376938`) | 1 (`$a3` @`0x39539c`) | 3 micro | 0 span `0x39539c` |
| `232AE0` | 404 | 33 (none →`376938`) | 6 (`$v0`×2, `$v1`×4) | 0 | n/a (no loops) |
| `231FC0` | 232 | 1 (`31C040`) | 10 | 0 | n/a (no loops) |
| `232328` | 292 | 14 (none →`376938`) | 6 | 0 | n/a (no loops) |
| `38F300` | 102 | 2 (`38F768` @444, `38F7B0` @44c = trace kids) | 0 | 1 (`0x38f410→0x38f3e8`) | JALs outside [0x38f3e8, 0x38f410] |

ELF word spot-checks (JALs + back-edges + first/last):
`395288` 7/7, `232AE0` 35/35, `231FC0` 3/3, `232328`
16/16, `38F300` 5/5 — 66/66 total.

### T10-3b. `395288` loop bounds (all three, readable operands)

| Loop | Counter init | Exit cond | Trips | Body | Spans `0x39539c`? |
|---|---|---|---|---|---|
| `0x3952b0–2c4` | `$v1` = 11 | `$v1` == `$a0` (arg) | 11 − `$a0` | 4 nops | no |
| `0x3952e8–2fc` | `$v0` = 3 | `$v0` == −1 | 4 fixed | 4 nops | no |
| `0x3954d8–4ec` | `$a1`, `$v0` = `$a1`+0xA0 | `$a1` == `$v0` | 5 fixed (32 B ×5) | lq/lq/sq/sq copy | no |

`376938`-issuing site `jalr $a3 @0x39539c`: `$a3` =
`lw 0xBC($v1)`, `$v1` = `lw 0x10D8($a0)` (double-struct-load
from arg; sole indirect call in unit; 26,216/26,216 non-empty
instances show kid (`376938`,)). All six `232AE0` `jalr`
targets likewise `lw 0x10D8`-chain-loaded (offsets 0x7C/0x8C/
0x9C/0xA4/0x164×2). JAL `3956B0` @`0x3953d0`: target
registered (`register_functions.cpp:352198`), 0 visible fires
in 262,493 instances = branch never taken on traced path.

### T10-3c. Host outer-driver loop (read-only source)

| Item | Reading |
|---|---|
| Loop | `EeScheduler::run()` `ps2xRuntime/src/lib/Kernel/EeScheduler.cpp:425` |
| Condition | `while (!m_stopRequested.load(...))` — stop flag only, no trip count |
| Body dispatch | `function(m_rdram, &context, &m_runtime)` (~:752) — one guest dispatch per iteration ≈ one depth-0 `enter` |
| Yield path | `dispatchGuestBranch` `ps2_runtime.cpp:1716` `checkpointDue` → `return false` → C++ unwind → re-dispatch at resume pc (depth-0 `enter`) |
| `checkpointDue` (:815) fires on | stop/checkpoint pending; `m_eeCycle` ≥ deadline; slice end + ready-thread preempt |
| Counters present | `m_eeCycle`, `m_sliceEndCycle` (monotone cycle counts; no trip total `N`) |

### T10-3d. Examined-and-absent (loop-above candidates)

| # | Candidate | Where looked | Killing reading |
|---|---|---|---|
| 1 | Guest loop in `395288` issuing `376938` | Full unit inventory + span check | 3 loops exist; 0 span `jalr @0x39539c`; per-pass issue ≤1 |
| 2 | Guest loop in `232AE0` (slot-51 owner) | Full unit inventory | 0 back-edges in 404 instrs |
| 3 | Guest loop in `231FC0`/`232328` (variant owners) | Full unit inventories | 0 + 0 back-edges |
| 4 | Guest loop in `38F300` (next-frame) | Full unit inventory | 1 loop `0x38f3e8–410`; JALs @444/44c outside it |
| 5 | Guest loop in `376938` spanning slice sites | T8 14-loop table | none spans rep site; other slice pcs not in trace (no pc) |
| 6 | Second static JAL →`376938` in owners | JAL inventories (2+33+1+14+2) | 0 direct JALs →`376938`; all issues via struct-loaded `jalr` |
| 7 | Bounded host loop with trip count | `EeScheduler::run()` + `checkpointDue` | bound = stop flag only; counters monotone, no `N` |
| 8 | Which `jalr` issues `376938` per owner | `$v`/`$a` data-flow | all struct-loaded (`0x10D8` chains); needs arg probe |

## T10-4. Updated step-3 table (T8 §T8-7 + T10 inputs, numbers only)

| Step | Shape | T10 inputs now on disk | Further inputs needed | Output if taken |
|---|---|---|---|---|
| 3a | Loop + site-readable bound → `(i,N)` per `363490` enter | 54-frame modal cycle (REP+53, 13,032/13,107 exact); per-gap class offsets +5/+15/+16/+18/+42/+52; owner loops 3/0/0/0/1, 0 spanning any issue site; host bound = stop flag only | None available in-trace (no guest trip count; slice pcs lack pc) | `(i,N)` series not constructible from these inputs |
| 3b | Recursion depth/arg counter → progress proxy | d2/d3 nesting exact 1:1:1 (13,108, 0 collisions); `m_eeCycle` monotone host counter exists | Cycle→rep calibration (needs run-to-compare) | monotone proxy (no total `N`) |
| 3c | No readable bound → empirical `N` via run-to-exit | In-trace progress counters per cycle (rep ordinal + slot index + gap ordinal 0–13106) | ~10 min P-lane lease, P31-6d 600 s boot shape | `N` empirically; no per-sample `i` |

## T10-5. Exact commands used

From `/Users/bradrichardson/dev/ssx3` unless noted; `W`,
`R`, `T` as above. All receipt/fork/ELF accesses
read-only (`python3` streaming reads, `grep`/`sed`/`awk`);
no builds, no boots, no fork writes, no lease claims:

```
git rev-parse HEAD; git log --oneline -3; git status --porcelain=v1
git -C "$R" rev-parse HEAD; git -C "$R" branch --show-current; git -C "$R" status --porcelain=v1
ls /tmp/ssx3-p-lane-lease (absent); pgrep -x ps2EntryRunner (absent)
head/sed windows of T (format recon); grep -m 376938 sample
read /tmp/t8-attr.py /tmp/t8-gap.py /tmp/t8-cfg.py (T8 scratch, parse/CFG method reuse)
write /tmp/t10-pass.py; python3 /tmp/t10-pass.py (pass 1: gate + pairing; C1a-addr + d0-3490 bugs, superseded)
write /tmp/t10-pass2.py; python3 /tmp/t10-pass2.py (pass 2, fixed: gate + modal slots + persist d0seq/repidx)
write /tmp/t10-pass3.py; python3 /tmp/t10-pass3.py (pass 3: persist 395288-all + 6938d123 + 232AE0-all + 38F300-all)
python3 /tmp/t10-join.py + /tmp/t10-followup.py + /tmp/t10-micro.py (TSV-only joins; evidence TSVs)
grep -c 362DE8/363490/376938 enter/exit T (13108/39324/39324/392030/392029)
write /tmp/t10-cfg.py; python3 /tmp/t10-cfg.py (units 395288/232AE0/231FC0/232328/38F300)
grep windows: 395288 loops + jalr context; 232AE0 jalr loads; register_functions 3956B0/3691F8
sed EeScheduler.cpp run loop + checkpointDue; sed dispatchGuestBranch 1702-1812
(mkdir + write local/research/T10/REPORT.md + 4 TSVs; this file)
git add -f local/research/T10/REPORT.md local/research/T10/modal-slots.tsv local/research/T10/gaps.tsv local/research/T10/chain-prefix.tsv local/research/T10/chain-suffix.tsv
git commit -m "[T10] ..." (trailer Orchestrated-By: Muse Code; NO push)
```

## T10-6. What I could not do (gap rows)

- Name which of the six `232AE0` `jalr`s
  (`0x232b50/d70/e00/e4c $v1`, `0x232ce0/dc8 $v0`) issues
  `376938`: all struct-loaded; needs a `$v0`/`$v1`/arg
  probe at those sites (emitter work, cf. T8-10 row 1).
- Name the resume pcs of the C3/C7/C1a/C1b/E slices inside
  the `376938` unit: trace has no pc; T8's 14-loop table
  cannot be span-checked against them (T8-10 row 2
  carried).
- Count `checkpointDue` firings per cycle or attribute
  individual yields to slice/timer/preempt causes: needs
  host-side counters (not in the log).
- Explain the 75-gap ramp (ordinals 0–74, lens 36–1005):
  variant-region internals, outside the pairing scope.
- Session wall ≈30 min active, inside the 4 h box.

## Evidence files

`modal-slots.tsv` (53 modal slots + uniform classes),
`gaps.tsv` (13,107 gap ordinals × len/pattern/class-counts),
`chain-prefix.tsv` (294 pre-first-rep d0 frames),
`chain-suffix.tsv` (5 post-last-rep d0 frames).
