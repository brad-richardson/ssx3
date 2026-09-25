# VB1 notebook (Claude Code, Opus 5.5, exploratory; box 12:12–15:12 EDT 2026-09-25)

## 12:12 start
Read brief, AGENTS (repo + local), facts, orchestration §3, VR1/E57/NP1 reports, review §3 rank 4.
Q1 report absent (no local-Qwen microVU input). Worktree `~/dev/ssx3-work/VB1/PS2Recomp`,
branch `vb1-stageb` from `1f51e48`. Base binaries = VR1's `runner-g4-{hash,speed}` (built from
`1f51e48` + gen-v2; SHAs re-read, match VR1 `binaries-sha.txt`). `vu1gen-ssx3` SHAs == gen-v2.

## 12:20 design choice
VR1 g4 profile: `commitReadyPipelines` 28 % of busy samples = ~45 % of all VU1 time; pair
functions 26 %. The stall computation (`calculatePairReadyCycle`) is already inlined with
constant usages and is cheap; the cost is the queue→commit round trip (every FMAC queues a VF
write + a flag entry, every cycle then scans them). So stage B starts with VR1 sketch step 2
("replace the queue/commit round trip with direct writes where no one can see the difference"),
not with precomputed stall tables.

Argument per write kind (queue model = stage A, the oracle):
- **VF / VI / ACC**: every read of these registers is in `InstructionUsage` and stalls until
  `m_vfReady/m_viReady/m_accReady` (set by `markPairWrites` to the same readyCycle the queue
  uses), so no VU instruction can read the register between issue and commit. Applying the
  write at issue (with a fresh write sequence, so older queued writes to the same lanes are
  retired exactly as a newer queued write would retire them) is unobservable inside the run.
  Branch VI reads are in `viRead` too; the VI branch backup keeps its old-value capture.
  VI keeps the commit's `int16_t` cast.
- **Stores** (latency 1): the queued store lands in `advanceOneCycle` at the next cycle before
  `progressXgkick`; between the issuing pair's exec and that point nothing reads VU data.
- **Flags** (MAC/status/CLIP, latency 4): readers (FCEQ..FCGET, 0x10–0x1C, incl. FSSET/FCSET)
  do not stall. A static per-pair map says "no flag-op lower in this pair or any pair that can
  issue in the next 4 pairs" (delay slots, static targets, not-taken paths followed; JR/JALR →
  unknown → reader). Runtime guard: flag queue empty (so no older queued entry commits after the
  direct one). The fdiv D/I status commit commutes with FMAC status updates (worked through).
- **Outside the run**: writes land by readyCycle ≤ issue + 4; guard `m_cycle + 4 ≤ budgetEnd`
  per pair, so at a budget exit every direct write would already have committed (a following
  `execute()`'s resetScheduler can't drop one). `pipelinesPending()` counts
  `m_directPendingUntil`, so `flushPipelines()` runs the same number of cycles.
- Known non-exact corner: a reserved-instruction stop (error path) exits with in-flight direct
  writes visible. Check the route has none.
Q/P (FDIV/EFU) stay queued (upper ops read Q/P without stalling).
Toggle: `PS2X_VU1_DIRECT=0`.

## 12:27 d1 (`9983169`) — suite 616/616, but both hash boots SIGBUS at tick 1605
Crash report: stack guard hit inside a chain of `VU1RecompImage<…>::f3cf0/f3cf8/f3d00`
frames. `f3d00` ends in `blr x8` + `__stack_chk_guard` compare: the musttail hand-off became a
real call. Cause: d1's longer `queueStore` was no longer LTO-inlined, so the SQ executors'
local `words[4]` escaped → stack protector in 1,603 pair functions → no tail call. (g4 had
the same call inlined, no canary.)

## 12:36 d1b (`86509dc`): `issueStore` always-inline; queued path copies into a member
`tailcall_audit.sh` (objdump over all 14,336 pair functions): blr in d1 1,603, d1b 0, g4 0.
Suite 616/616. `h-d1b` (paraLLEl): 2,400/2,400 det-hash lines equal to VR1 `h-base-1`;
VU1 cycles 959,411,166 = VR1 (generated_share 1.0000). VR1 pruned its paraLLEl `gs.cap`,
so a fresh base `h-g4` (runner-g4-hash) is booting for the per-path GS compare; CPU strict
check (`h-d1b-cpu`) runs against VR1's kept `run/h-base-cpu/gs.cap`.

## 12:42 d1b gates
- CPU backend strict (`check-d1b-cpu.txt`, vs VR1 `run/h-base-cpu`): suite 616/616, det-hash
  2,400/2,400, GS whole-file SHA `f2233e7e…` equal (1,906,204 records) → **BIT-EXACT**.
- paraLLEl (`check-d1b.txt`, vs fresh `h-g4`): det-hash equal; whole-file GS differs as the
  VR1 null control does; `gs_types.py`: every path's payload sequence (tick stripped) equal.

## 12:45–13:00 speed ABBA g4 vs d1b (holds A, B; Mac mini M5 Pro, paraLLEl, exclusive)
A: s1-g4 20.82, s2-d1b 23.78; B: s11-d1b 22.19, s12-g4 19.63 → g4 20.23, d1b 22.99: **1.14×**.
Load 4–10 during holds (other lanes' unleased work).

## 12:50 d2 = d1b + counters + VR1 g5 cherry-pick (`b74d81d`)
Suite 616/616. `h-d2` (stats): VU1 cycles 959,411,166; **direct_share 1.0000** (the budget
guard never fell back on the route); flag writes direct 250,125,560 / queued 238,415,890
(**51 %** direct). Profile `p-d2` (diagnostic, `profile-d2.txt`) vs VR1 `p-g4`:
VU1 62.5 % → 54.5 % of busy samples; commitReadyPipelines 28.0 % → 6.9 %; pair functions
26.4 % → 36.6 % (their share grows as the rest shrinks). Hot loop: image `f587…` pairs
0x2a10–0x2a50 (LQI/SQI/DIV + FMACs, ~20 % of pair samples).

## 13:02 d3: flags direct past older queued flag entries (demote older to sticky-only OR)
The 49 % queued flags are either near a flag reader (map) or behind a queued entry (the
empty-queue guard cascades for up to 4 cycles after any queued flag write). Order argument in
the d3 commit message; FSSET pending → still queued.

## 13:05–13:30 differential test finds two real gaps in the d1–d3 argument
Added a suite case (`setDirectCommitForTest`): random VU1 programs run direct vs queued, cut
at every budget, compared at the cut, after resume() and after a fresh execute().
1. **Supersede at a cut** (program 1, budget 4): pair 0 FMAC writes vf4.yzw (direct, lands at
   4), pair 3 LQI writes vf4.xy at cycle 3 (queued: 3+4 > budget). The queue retires pair 0's
   y lane (newer sequence), so at the cut the queued path still shows the old vf4.y. A 2×
   budget margin only moved it (program 35, budget 18): a chain of overwrites, each issued
   before the previous lands, keeps the old value for as long as the chain lasts.
   Fix (d4): per-pair static bit "this VF write can't be retired before it lands" (no
   overlapping write in the next 3 pairs without an overlapping read in between; reads stall
   to landing). Writes that fail it stay queued. VI writes direct only at latency 1.
2. **Usage-table gap** (program 56): OPMULA/OPMSUB declare fs lanes = dest but read fs.xyz;
   with a non-xyz dest an FS read isn't stalled. Real code writes .xyz (0 non-xyz OPMULA/
   OPMSUB in the 7 images, stale pairs included), so the test generates .xyz only. Stage A
   has the same gap; noted for the orchestrator, not changed.
d3 (before the fix, for the record): CPU strict BIT-EXACT, paraLLEl per-path equal,
flag_direct_share 0.7694 (d2 0.5119). The route never cuts a program at the budget, which
is why the whole-game gate couldn't see gap 1.

## 13:28 d4 (`9638b3d`): suite 617/617 (200 programs × every cut); audit blr 0

## 13:30–13:57 d4 gates, stats, speed
- d4 CPU strict BIT-EXACT (`check-d4-cpu.txt`), paraLLEl det-hash equal + per-path GS equal
  (`check-d4.txt`, `gs-types-d4.txt`), VU1 cycles 959,411,166.
- `h-d4s` (d4 + VF counters `9b71115`, hash): VF writes direct 98.45 %, flags 76.94 %, det-hash
  equal to `h-g4`.
- Speed C (g4 19.46, d4 22.69), D (d4 23.67, g4 20.88) → d4 23.18 vs g4 20.17 = **1.15×**.
  Hold C waited 19 min for slots/load (PF1, HR1, px1 lanes busy).

## 13:58 PAUSED (Brad needs the machine). Nothing running, no leases held.
State for resume: branch `vb1-stageb` @ `9b71115` in `~/dev/ssx3-work/VB1/PS2Recomp`;
binaries in `~/dev/ssx3-work/VB1/bin` (`binaries-sha.txt`); `run/h-g4/gs.cap` kept as the
paraLLEl base capture (2.5 GB); scratch ~13 GB. REPORT.md is complete for d1–d4. Possible next
steps (not started): profile d4; skip the old/new copy on full-mask direct writes; find which
flag writes stay queued per pc; stage-B stall tables only if a line-level profile shows the stall
max/markPairWrites are worth it.
