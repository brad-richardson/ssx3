# E36 report — why 498/583 VU1 programs never reach their end on Select Character

Brief `local/muse/prompts/E36.md`. Tables + receipts; the orchestrator decides.

## Outcome

- Reverted `03d6549` as `0d40e2a` (`git revert`, no rewrite); suite green.
- New DEV-ONLY `PS2X_VU1_TRACE` (+`_FROM`/`_TO`, cap 40 distinct startPCs)
  with per-stuck-program detail blocks; three commits; suite **476/476**.
- Three Boot-A runs (e36a/b/c): stats reproduce E33 bit-identically
  (583 MSCAL, 498 exhausted, mscnt=0, xgkick=85 every settled vsync).
- Only **8 distinct stuck startPCs**, stable every vsync, all converging
  into **one loop**: `IBNE vi03,vi13,-39` at 0x548 → 0x418. The loop's
  limit/start pair never meets (29k–64k more iters needed ≈ 1.2M–2.6M
  cycles); programs issue **zero XGKICKs** and are dropped each vsync.
- **B ruled out** (exit is pure IBNE on VI; no flag/status reads in the
  span). **C's stated variants ruled out** (delay slot NOP; no VI write
  in the 8 pairs before the branch; three walkers' end values fit
  start+iters×step; 85 healthy programs complete through the same
  interpreter each vsync). **A leads** (wild limit/start inputs) but the
  init provenance (entry-path loads) was not captured → **no fix**,
  per the brief's single-mechanism bar. Recommended next action below.

## Commits (fork `~/dev/PS2Recomp`, branch `ssx3`, no push)

| Commit | Subject |
|---|---|
| `0d40e2a` | Revert "[E33] Resume budget-exhausted VU1 programs to their end marker (H1 fix)" |
| `02bab15` | [E36] DEV-ONLY per-program VU1 trace behind PS2X_VU1_TRACE (default off) |
| `8a0cc10` | [E36] Count trace XGKICKs on every enabled run, not just armed ones |
| `018f56b` | [E36] Trace body keeps branch context; add entry-path line, EFU names |

Runner-dir gate: `git diff --stat 14b1e5cb ssx3 -- ps2xRuntime/src/runner`
is empty. Suite runs (flags-unset, fork root): first post-change run
474/475 — the single failure was a test-side expectation (IBNE placed
immediately after its counter increment reads the stale VI under the
interpreter's write→branch hazard model; test corrected to insert a
NOP), no production-code failure. Final **476/476, rc 0** (472 E33 base
− 1 reverted fix test + 5 trace tests, the 5th added with the counter
fix).

## Trace design (what `PS2X_VU1_TRACE` records)

Header-only `ps2xRuntime/include/ps2_vu1_trace.h` (gfx-stats pattern):
`PS2X_VU1_TRACE=<file>`, `PS2X_VU1_TRACE_FROM/_TO` vsync window
(inclusive), hard caps (40 distinct detail startPCs, 100k lines).
VIF1 stashes a snapshot at each MSCAL/MSCALF/MSCNT (pre-update TOPS/DBF);
`execute()`/`resume()` consume it (VU1 unit only). Per run: one `census`
line if budget-exhausted (startPC, cycles, own XGKICK count); if armed
(first 40 distinct) a `detail` block: MSCAL snapshot (startPC, TOP/ITOP,
BASE/OFST/TOPS/ITOPS/DBF), 8 qwords at TOP + 8 at ITOP (program-start
snapshot), end-of-slice vi[16]/mac/status/clip/endpc, PC-visit top 10,
branch-taken top 10, hottest backward branch (PC, op, operands, target,
taken/visits, end VI values, flag ops in span), 32-PC loop-body
disassembly (span ending at the branch delay slot; interpreter decoded
cache for E/D/T/I flags + a mini lower-op decoder), and an `entry` line
(visited PCs outside the body). Default off = one relaxed check per tap
plus one member branch per issued pair; no guest-visible change
(proven: e36a vs e36b stats lines byte-identical everywhere overlapped).

Self-found bug, fixed as `8a0cc10`: the first build counted XGKICKs only
on histogram-armed runs, so disarmed census lines carried the previous
program's count (visible as all-`xgkick=1` from vsync 1301 in e36a while
stats stayed at 85). Now reset+counted on every enabled run; regression
test included. e36a census xgkick values are superseded (detail blocks
were always exact); e36b/e36c show all-zero.

## Boots (all Mac mini, E32-build, script-claimed lease, rc 0, wall-bound)

| Boot | Env | Result |
|---|---|---|
| e36a | vsync route, wall 300, stats 1200–1500, trace 1300–1320 | tick 1375; 498/vsync; trace 10,770 lines (census xgkick stale, see above) |
| e36b | same, fixed counter | tick 1373; stats byte-identical to e36a everywhere overlapped; 10,458 census lines, all xgkick=0 |
| e36c | same, body/entry refinement | tick 1359 (wall variance; window 1300–1320 fully covered); 8 detail blocks with branch context + entry paths |

Vsync-clock route and tick rate as E33 (char-idle ~0.4 tick/s). Lease
released after every boot (`lease_released: true`).

## Per-startPC table (e36c, vsyncs 1300–1320; counts identical every vsync)

Counts/vsync sum to 195+177+51+37+16+16+4+2 = 498. All: cycles=65536,
xgkick=0, ctx=mscal, base=38, ofst=438, itop=itops=0. TOP/tops alternate
476 (dbf=1) / 38 (dbf=0): healthy double-buffer cycling.

| startPC | n/vsync | Exit VI (end of slice) | Iters still needed* | TOP header qwords (first 4 words) |
|---|---|---|---|---|
| 0x40 | 195 | vi03=-15836, vi13=-7658 | 57,358 | 00008039 302e4000 00000412 … |
| 0x10 | 177 | vi03=-15836, vi13=-9296 | 58,996 | 00008038 302e4000 00000412 … |
| 0x0 | 51 | vi03=10490, vi13=12114 | 63,912 | 00008039 + small-int table (7,11,75,39,…) |
| 0x398 | 37 | vi03=-15836, vi13=20203 | 29,497 | all zero |
| 0x80 | 16 | vi03=257, vi13=8840 | 56,953 | 00008004 302e4000 00000412 … |
| 0x70 | 16 | vi03=257, vi13=10478 | 55,315 | 0x000000ff-pattern words |
| 0x50 | 4 | vi03=21881, vi13=25143 | 62,274 | 00008038 302e4000 00000412 … |
| 0x30 | 2 | vi03=-15836, vi13=8749 | 40,951 | all zero |

\* `(vi03 − vi13) mod 65536` at +1 iter-walk each ≈ 1.2M–2.6M cycles
(18–40 budgets). E33's 16-slice resume (~1M cycles, zero new kicks) is
explained: the loop needs more than 16 continuations AND issues no
XGKICK inside, so extra slices burn cycles for nothing.

Loop body in plain words (identical all 8): at 0x418 a ~40-pair
vertex-stream loop — `LQI` load through vi13 (post-increment, +1/iter),
`IADDIU vi14,+3`, `LQI` load through vi11, `SQ` store through vi14, VF
moves, `RSQRT`/`ESIN` epilogue — then `IBNE vi03,vi13,−39` back to
0x418. Exit needs vi13 == vi03 (16-bit compare). Nothing in the loop
writes vi03; vi13 walks +1/iter from a start already past the limit, so
equality never lands inside the budget. No E/D/T bit, no XGKICK, no
flag-op reads anywhere in the 0x418–0x548 span (`bodyflags=none` all 8).
Delay slot 0x550 is NOP; the 8 pairs before the branch are NOP/RSQRT —
no VI writers. Entry paths are straight-line setup (~105–190 PCs, 1×
each; 0x0's entry shows 2×, unexplained minor) from each startPC into
0x418; the entry disassembly itself was not captured (only PCs+counts).

## A/B/C read-out (evidence, not verdict)

- **A. Bad input → runaway counted loop: SUPPORTED, leads.** The walker
  (vi13, +1/iter via LQI) starts thousands past the limit (vi03): e.g.
  257 vs ~7205; −15836 vs −9296. As VI-row pointers both are wild
  (sane rows are 0–1023; effective addresses wrap in 16 KB and the loop
  mass-processes wrapped memory). T48's healthy side (same game code,
  PCSX2 interp: 100% end=ebit, SC max 2,090 cycles) proves the code
  terminates on sane inputs. VIF double-buffer state cycles healthily,
  so a buffer-pointer mixup is disfavored; the header content/indexing
  or UNPACK placement behind the entry loads is the open question.
- **B. Wait on unmodeled state: RULED OUT for this loop.** The exit is a
  pure integer compare; the span holds no FCAND/FSAND/FMAND/FMEQ/FCEQ/
  FSEQ/FCSET/FSSET/FCOR/FSOR/FCGET and no XTOP/XITOP (bodyflags=none,
  full-span scan, all 8 blocks).
- **C. Interpreter semantics: stated variants RULED OUT.** Delay slot is
  NOP (no VI write in delay slot); no VI write in the 8 pairs before
  IBNE, so the write→branch hazard model reads fresh values; the LQI
  +1 walk is corroborated three ways (vi11/vi13/vi14 end values all fit
  start+iters×step; 85 healthy programs complete through the same
  interpreter every vsync; LQI is unit-tested). The loop is
  arithmetically infinite for its inputs under any read model.

T48 cross-check limits: T48 SC startPCs (0x8/0x2/0x257/0x0/0x73, all
ending ≤2,090 cycles; race max 23,540) vs ours — different scene state
(Zoe rendered vs missing rider), so the startPC sets are not directly
comparable; the only reading taken from it is that healthy programs stay ~3–31× below the
65,536 budget while ours needs ~18–40 budgets more.

## Fix verdict: none (brief's single-mechanism bar not met)

A leads, but no code change is named: the entry-path loads that set
vi03/vi13 (ILW rows? immediates?) were not captured, so any edit would
be a tuning hack (e.g. iteration caps), out of scope. No A' boot.

Recommended next action (orchestrator): a follow-up lane to capture the
entry-path disassembly (startPC→0x418: which ILW/XTOP rows feed vi03/
vi13) and audit VIF1 UNPACK→VU-row placement for those rows — or dump
VU data memory at a stuck MSCAL for direct comparison. The tracer
(`PS2X_VU1_TRACE`) is committed and reusable for it.

## Frames (path + SHA, viewed by eye)

| Point | File | Bytes | SHA256 | Shows |
|---|---|---|---|---|
| C Select Character settled | `E36-run/frames-e36c-1/snap/snap-0300.82s.png` (= `upload-latest.png`) | 208372 | `9c693ee8…955f60` | Zoe name+bars+silhouettes, **no 3D rider model** (same as E33) |

## Gaps / notes

- e36a census `xgkick` column is stale-contaminated (counter bug, fixed
  `8a0cc10`); e36b/e36c supersede it. Detail blocks were always exact.
- Entry-path disassembly not captured (PCs+counts only); vi03/vi13
  provenance unproven — the reason no fix is named.
- 0x0-block entry PCs from 0x20 on visited 2×/program (vs 1× elsewhere);
  its `taken` line shows two taken-once branches (0x6f8, 0x8a0), so the
  entry has real control flow; shape not disassembled (entry PCs only).
- 0x30/0x398 headers at TOP are all-zero while other entries' are not;
  not investigated (their vi03/vi13 are equally wild, same loop).
- `itopq` for 0x80 shows mid-size floats + ints (268, 706); not mapped
  to the loop bounds.
- Unit-test side finding (kept in test comment): the interpreter models
  a VI write→branch hazard (`readBranchVi` returns the pre-write value
  when the previous pair wrote the tested VI) — relevant context if the
  entry path ever places IBcc immediately after its counter update.
- Bytes: E36-run 110 MB; internal total 26.7/200 GB. Boot log
  `boot-e36c-1.log` 4.0 MB retained; no compression needed.

## Exact commands

```
git revert --no-edit 03d6549  # fork ssx3 -> 0d40e2a
cmake --build ~/dev/ssx3-work/E32-build -j4
env -u PS2X_SKIP_MOVIE -u PS2X_PAD_SCRIPT ~/dev/ssx3-work/E32-build/ps2xTest/ps2x_tests  # 476/476 from ~/dev/PS2Recomp
python3 local/research/E36/e36_boot.py --label e36a --wall 300 --snap 2.0 --stats-from 1200 --stats-to 1500 --trace-from 1300 --trace-to 1320 --script "<route>"
python3 local/research/E36/e36_boot.py --label e36b ...  # same args, fixed counter
python3 local/research/E36/e36_boot.py --label e36c ...  # same args, body/entry refinement
python3 local/research/E36/e36_analyze.py ~/dev/ssx3-work/E36-run/vu1-trace-e36c.txt
```

(`<route>` = `10350:start:2500,20650:cross:2000,23200:cross:400,24000:cross:400,30890:cross:1700,39560:cross:1750,47240:down:4200,55450:cross:1800,64920:cross:2000,113340:cross:800,118270:cross:700,122510:cross:700,113340:down:20000`;
no push on either repo.)
