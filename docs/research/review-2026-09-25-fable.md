# Frontier review 3 (2026-09-25, Fable, read-only) — steering the next phase

Brief `local/muse/prompts/RV3.md`. Read: `AGENTS.md`, status/todo/facts/ledger/orchestration,
the two prior reviews, the RR1/AU9/E57/GB8/N11/E61/AU8/TL1/I31/I32/E54E reports with their gates,
fork `~/dev/PS2Recomp` `ssx3` @ `f949ff0` (+ worktrees `rr1-sky`, `au9-spu`, `e57-vu1`,
`n11-prof`, `f1-fold` @ `56a5e8a`), `~/dev/parallel-gs` @ `963cb57`, the canonical codegen.
While this was written, F1 Part 1 passed and the fold was pushed (fork `ssx3` → `56a5e8a`).
Every claim below cites a file:line or a report row; "census" rows come from a one-off script
I ran over `~/dev/ssx3-work/codegen-ssx3` (described in §2). Tags: **do now / queue / park**.
The orchestrator decides.

## Executive summary

1. **The fold is right and the next correctness lever is structural, not another symptom.** All
   four of yesterday's root causes sit in two models: *batch-then-reorder* (GIF/DMA/PATH3
   ordering) and *width-and-extension* (32 vs 64 bit). The GIF arbiter still sorts every
   pending packet by path at drain time (`ps2_gif_arbiter.cpp:95-107`), so a PATH3 upload
   submitted before a PATH1 draw can still land after it inside one drain window
   (`ps2_memory.cpp:2245`). That is the same class as RR1's fix and the best fit for Brad's iOS
   flicker. **Do now** (§1, suspect 1).
2. **The sign-extension hunt is one deterministic boot away.** The codegen's own 32-bit
   producers are clean (LWU zero-extends at `instruction_translator.cpp:196`; MULT/DIV/SLT/
   MFHI are right, `special_translator.cpp:59-125`); the HLE return helpers sign-extend
   (`ps2_runtime.h:200-217`). So the value the correct 64-bit predicate exposes is *inherited*
   through 64-bit moves (`daddu rd, rs, zero`: 686 of the 4,466 signed sites have a 64-bit add
   as nearest writer) from a producer we have not named. A dev-build tripwire that evaluates
   both predicates and logs the first disagreement (PC, register, value, tick) names it on the
   E54E route before tick 90. **Do now** (§2).
3. **Speed: measure E57 on the Odin before choosing between recompiling VU1 and reworking the
   hazard model.** Odin race 145 ms/frame, VU1 118 ms (N11 S2). E57 removed the commit-scan
   term that is 25 % of Odin samples; expect 1.4–1.8× on the Odin (F1 Part 2 measures it).
   After that the order is: link flags + packet copies (cheap, ~10 ms), VU1 static recompile
   stage A then B (~40–60 ms), menu-side Turnip churn (G/N). Real time needs *all* of VU1 ≲ 5 ms,
   host overhead ≲ 10 ms and one more core; say so now (§3).
4. **What must stay Odin-only shrank to four things:** wave64 hierarchical binning (Apple's
   subgroup is 32 and `gs_renderer.cpp:1822` forces flat binning), descriptor-buffer path,
   Turnip driver CPU cost/thermals, Adreno bilinear rounding. Everything above the GS stream is
   already Mac-provable (GB8: det-hash identical CPU vs paraLLEl). Two knobs are worth adding;
   one (flat descriptors on the Odin) costs an env line (§4).
5. **Process: the 6 h 40 min stall was a single point of failure**, not a worker problem. Four
   passed lanes (RR1 23:18, N11 23:38, GB8 00:01, E57 00:10) waited for the 06:50 gate because
   `watch.sh` exits on every event and nothing re-armed it. Fix: a wakeup is part of every
   orchestrator turn that leaves a pane running, and a gate deadline is a blocker (§5).
6. **Lease contention is a scheduling gap, not a capacity gap.** Speed pairs need all four
   slots and are polled (`gb8_watch.py 1500`); E61's speed pair ran at host load 10–15 and is
   uncomparable. Queue exclusive claims; block builds while an exclusive lease is held (§5).
7. **Silent caps and fallbacks are the third class.** 65,536 VU1 cycles (`ps2_runtime.cpp:1045`),
   4,096 VU0 cycles, the unknown-UNPACK raw copy (`ps2_vif1_interpreter.cpp:975-980`),
   `ContinueToTarget` as the release default (`ps2_runtime.cpp:811`), unknown syscall → 0.
   Each needs a counter that is read at the gate; two already exist and are not read (§1, §6).
8. **The AU9 comparator override also makes five other files findable**, one of them
   `SLUSOVF.BIG`. If that is a code overlay, the static recomp has no functions for it and the
   release policy hides the miss. Ten-minute check on the F1 build (§6).
9. **The CPU GS backend is no longer a pixel reference** (no dither, mipmap/LOD, COLCLAMP, AA1,
   SCANMSK in `gs_cpu_backend.cpp`); PCSX2 gsrunner on our stream is (RR1 E7). Stop quoting
   CPU-vs-paraLLEl pixel diffs as correctness; fix the converter's blank race frames (§4, §6).
10. **Keep the explorer/executor split.** RR1, AU9, E57 and AU8 each named a mechanism in
    ≈1.5 h of free-rein Opus time; muse executed folds and device runs without incident. That is
    the 09-24 remedy working; the remaining process cost is on the orchestrator's side (§5).

## 1. Bug classes, not bugs — top 10 suspects

Classes: **A** batch-then-reorder (we run guest work to completion, then submit in a sorted or
whole batch where hardware interleaves); **B** width/extension; **C** silent cap or fallback;
**D** never-raised event. Ranked by expected player-visible impact.

| # | Suspect (class) | Evidence | Observable for a bounded brief | Tag |
|---|---|---|---|---|
| 1 | **GIF arbiter drain sort** (A). `drain()` stable-sorts all queued packets by `pathPriority` (PATH1<2<3), only exempting DIRECTHL vs IMAGE, then processes them; drain runs once per pending-transfer pass. Any PATH3 packet released by RR1's window that is queued in the same pass as a later PATH1 kick is processed *after* it. | `ps2_gif_arbiter.cpp:91-129`, `ps2_memory.cpp:2245`, `:2332`, `:2361`; RR1 gap "PATH3 … interleaved with PATH1/2 inside one delivery isn't modelled" | Log submit index vs process index per packet (`ps2_pk::noteSubmit` already exists, `ps2_memory.cpp:2355`); count inversions per vsync on the F1 det boot. PCSX2 order from `rr1_timeline_pcsx2.py`. Gate: inversions → 0 and Select Peak/race frames unchanged; then the iOS flicker check. | **do now** |
| 2 | **VU1 cycle cap truncation** (C). `execute(..., 65536)`; a program that exhausts the budget leaves draws unissued; MSCNT after a cut resumes at the cut PC. Todo already records 9 vsyncs with 33 capped programs; PCSX2's healthy race max is 23,540 cycles (T48), so any cap hit is our VU1 looping on a wrong flag or branch. | `ps2_runtime.cpp:1045,1063,2647`; `ps2_vu1_core.cpp:1689-1744,1953`; facts.md T48 row | `ps2_gfx_stats::noteVuRun(budgetExhausted)` count per vsync on the F1 build (counter exists, `ps2_vu1_core.cpp:1954`); dump VU1 code+data and PC at the first cap hit; compare that program's first 2,000 cycles against PCSX2's VU1 register trace at the same startPC. | **do now** |
| 3 | **Missing-target continue in release** (C). Release default is `ContinueToTarget`; Brad's builds silently return with stale `$v0` on every unrecompiled target. `[coverage:missing-functions]` prints at exit, but no Odin/iOS run pulls it. | `ps2_runtime.cpp:809-824,1811` | Pull the exit coverage line from the F1 Odin/iOS runs; zero targets = close; else `extra_function_starts`. Add "coverage line read" to every device gate. | **do now** |
| 4 | **INTC 5/7 never dispatched, DI/EI ignored** (D). `dispatchIrq` is called only for VBlank 2/3 and timers 9–12. If SSX 3 registers a VIF1 or VU1 handler, its pacing/double-buffer logic never runs. | `EeScheduler.cpp:2655,2860,2869`; `Interrupt.cpp:26-38` registers without logging the cause | One-line log of the cause argument in `addHandler`; one boot. No 5/7 handler = close H10 for this game. | **do now** (cheap) |
| 5 | **VIF UNPACK modes beyond V4-5** (A/B). V2 leaves z/w as stale VU memory; V3 the same for w; unknown formats fall back to a raw copy when mode is 0 or 3; fill cycles (`cl<wl`) rewrite `maskSpec` to row-fill. | `ps2_vif1_interpreter.cpp:870-1010` | Per-MSCAL XXH64 of VU1 data memory vs PCSX2 VU1 memory dumps at the same startPC (T65 dumps exist); first differing qword names the format. | queue |
| 6 | **Unhandled RPC / unknown syscall paths now reached** (D). The override makes `NETCNF.IRX`, `EZMIDI.IRX`, `SLUSOVF.BIG`, two grunt banks loadable; unhandled RPC is echoed (`RPC.cpp:724-735` counts it), unknown syscalls return 0. | AU9 row 6 and hypotheses; `RPC.cpp:731` `noteUnhandledRpc` | Diff the unhandled-RPC counter set on the F1 build vs the E56 baseline (4 pairs); any new pair gets named. | **do now** (read the F1 logs) |
| 7 | **DMA completes at the CHCR store; no stall control; REFS = REF** (A). Chain tag id 4 (REFS) is handled with REF; `D_CTRL` STS/STD are never consulted; CHCR reads clear STR. A stall-controlled VIF1 chain reads producer data at the wrong time. | `ps2_memory.cpp:1730`, `:2766-2774`; `DMA.cpp:152-195` writes STADR only | Count REFS tags and non-zero `D_CTRL` STS/STD on the route (one counter). Zero = close M9/M10 for this game. | queue (cheap probe) |
| 8 | **SPU2 model gaps** (A/D): reverb, pitch modulation, noise, IRQ, volume sweep approximated by a one-tick ramp. | AU9 "Not modelled" | Diff PCSX2's register log (`AU9/pcsx2/spureg.txt`) against our driver's register writes per tick when Brad hears a difference. | queue (after Brad's listen) |
| 9 | **CD read failure zero-fills and returns 0; callback semantics** (C). Snow Jam 99 % stall candidate. | `CD.cpp:403-411,452`; E31/T47 | Re-test Snow Jam on the F1 build with `g_lastCdError` logged; then the CD/SIF trace vs T47. | queue (already in todo) |
| 10 | **Timers GATE/HOLD, 60.00 vs 59.94 Hz, GS CSR field rules** (D). | `ps2_memory.cpp:268-305`; E54B landed CSR W1C/FIELD | Only if a pacing symptom appears. | park |

Brief sketch, suspect 1 (`GA1`, muse, 2 h, Mac only): build the F1 tip with `PS2X_BUILD_TEST=ON`;
add a default-off env `PS2X_PK_ORDER=<file>` that writes `(vsync, submitIdx, processIdx, path,
bytes)` per packet from `noteSubmit`/`drain`; one det boot to t2400; a 30-line script counts
inversions per vsync and prints the first ten with their EE tick; compare against the PCSX2
order for tick 1795 (RR1 E2). Stop rule: zero inversions on the route → close and record in
`facts.md`; inversions present → Part 2 replaces the sort with submission order plus the two
hardware rules (PATH3 IMAGE not preempted by DIRECTHL; PATH1 wins only when both request at an
EOP boundary), suite, det boot, frames viewed, then the iOS build for Brad's flicker.

Brief sketch, suspect 2 (`VU2`, muse, 1.5 h): F1 build, `PS2X_GFX_STATS` on, one det boot to
t2400; table capped programs per vsync with startPC and cycles; at the first cap, dump VU1 code
and data (existing tap) and the pair PC; hand back the table. No fix in Part 1.

## 2. The sign-extension hunt

What is already established (this review, read-only):

| Row | Fact | Where |
|---|---|---|
| S1 | All 32-bit result setters sign-extend: `SET_GPR_U32/S32` cast through `int32_t` | `ps2_runtime_macros.h:1304-1323` |
| S2 | LWU zero-extends (E54D); LWL/LWR follow PCSX2 (LWR keeps the upper 32 when offset ≠ 0) | `instruction_translator.cpp:196-197,270-292` |
| S3 | MULT/MULTU/DIV/DIVU (+ pipeline 1) write LO/HI sign-extended; MFHI/MFLO copy 64; SLT/SLTU compare 64; ADDU/SUBU/shifts sign-extend | `special_translator.cpp:51-125`, `mmi_translator.cpp:28-64` |
| S4 | HLE returns sign-extend (`setReturnU32/S32`); `setReturnU64` is used only for genuine 64-bit values (`__divdi3`, IMR) | `ps2_runtime.h:200-217`, `LibC.cpp:1362-1377`, `System.cpp:115,142` |
| S5 | Only 4 predicate expressions differ between E54D and E54E codegen (1,936 files, `GPR_S32`→`GPR_S64`), yet the first GS packet differs at tick 82–83, packet 352 | E54E post-gate table |
| S6 | Census of 4,466 signed sites in the canonical codegen, nearest preceding writer of `rs` in the same function: 3,231 `SET_GPR_S32` (safe by construction), 686 `SET_GPR_U64` 64-bit add (mostly `daddu rd, rs, zero` moves of an argument or return value), 176 no writer within 400 lines, 151 live-in at function entry, 53 `SET_GPR_VEC`, 51 `SET_GPR_U32`, 34 and/or/xor, 28 `S64` adds, 25 SLT, 24 MFHI/MFLO, 7 LD | script over `~/dev/ssx3-work/codegen-ssx3` (regex on `branch_taken_0x… = (GPR_S32(ctx, N) …)` and `SET_GPR_*`) |

Reading: the exposed value is not produced by a mis-extending instruction in our codegen; it is
inherited through 64-bit moves from a caller, an HLE stub, a guest 64-bit idiom, or from context
state we initialise (thread start `r[4]/r[5]` are zero, `r[29]` is fine, `ps2_runtime.cpp:3696-3698`).
Static slicing across calls is the slow way; the dynamic tripwire is the fast one.

**Design (`SB1`, one lane, ≤ 3 h, Mac only) — do now:**

1. Emitter: replace the four predicate strings (`control_flow_emitter.cpp:407-425`) with a
   macro `PS2X_SBR_LT(ctx, rs, pc)` etc. In release the macro is the 64-bit predicate (the
   validated E54E/AU9 change). Under `PS2X_ENABLE_SBR_TRIPWIRE` it computes both, and on
   disagreement calls `runtime->noteSignedBranchMismatch(pc, rs, GPR_U64, tick, eeCycle)`, then
   returns the predicate selected by `PS2X_SBR_MODE` (`s32` = today's behaviour, `s64` = correct).
2. Runtime: the note logs the first 64 distinct PCs once each with `[sbr] pc reg value tick
   cycle` and keeps a per-PC count printed at exit; zero cost in release (macro collapses).
3. One regen (E54E did one inside its budget), one taps-OFF build with the tripwire on.
4. Boot A: `PS2X_SBR_MODE=s32`, deterministic, I26-FAST, to t400. Identical to today's frames by
   construction; the log lists every PC where the predicates disagree, in order, with the
   register value. The first line before tick 90 is the E54E divergence.
5. For each of the first few PCs: `ee-at <pc> 12 4` and `ee-func`; classify the producer
   (HLE return → which stub; guest idiom → is the value legitimately 64-bit on hardware; context
   init). One candidate fix at most, then Boot B with `s64` to t2400 and the E55 hash + GS
   digest against a baseline.
6. Stop rules: no mismatch before tick 90 → the E54E black frame was not the predicate (re-check
   the E54E codegen/build pairing); mismatch with a legitimate 64-bit producer → our model is
   right and the game truly depends on 64-bit semantics there, so the fix is elsewhere upstream
   of that register; mismatch with an HLE producer → fix the stub. Then regen, retire the
   `0x3E3968` override (it stays harmless until then), fold.

Cheaper companion (queue): the census script as `local/tooling/ee/sbr-census.py`, run after each
regen, so the "safe by construction" count is tracked.

## 3. Speed plan to real time on the Odin

Baseline (N11 S2, race, GameThread-bound, 145.4 ms/frame): VU1 hazard bookkeeping 70.1, VU1
execute 48.2, libc/kernel 24.9, PLT 8.5, tail 13.5, everything else < 3. GsWorker 20.8 ms/frame
on another core; GPU 11–17 % busy. Real time = 16.7 ms; needed factor 8.7×; 120 Hz sim ≈ 17×.
Non-VU1 host cost alone (≈ 47 ms) is already 2.8× real time, so **VU1 work alone cannot reach
real time on one thread**; the plan must cut all three terms.

| Rank | Lever | Est. Odin ms saved (of 145) | Risk | What to measure first | Tag |
|---|---|---|---|---|---|
| 1 | **E57 (folded).** Removes most of `commitReadyPipelines` (25.0 % of Odin samples) and part of `calculatePairReadyCycle` (12.7 %). Mac gain 1.35× with VU1 at 46 %; Odin VU1 is 81 %. | 35–55 | done | F1 Part 2 Odin pair (running). Quote only that number. | — |
| 2 | **Host overhead: PLT + copies + clocks.** `@plt` 4.84 % = intra-`.so` calls through the PLT (no `-Bsymbolic`/hidden visibility in the CMake or Gradle config); `__memset_aarch64_nt` 1.87 % (the arbiter zero-fills then copies every packet, `ps2_gif_arbiter.cpp:84-85`; the masked FIFO copies again); `clock_gettime` 1.7 % + `advanceEeTimers` 0.4 %. | 8–15 | low | Android simpleperf `--call-graph` on the F1 APK (the profileable manifest is folded) to attribute the PLT and kernel rows; then `-Wl,-Bsymbolic` (or `-fvisibility=hidden` + `-fno-plt`) as a one-line A/B pair. | **do now** |
| 3 | **VU1 static recompile, stage A** (E57 sketch: one C++ function per program, `case` per pair PC, scoreboard kept). Removes decode, usage lookups, opcode switches: `run` 7.3 %, decode 1.3 %, exec dispatch ≈ 4 %. | 10–18 | medium; det-hash + GS digest gate proven by E57 | Only after rank 1's number: if Odin VU1 is still ≥ 60 ms. | queue |
| 4 | **Stage B, static schedules per basic block** (subsumes "a cheaper hazard model"): precompute stalls from block-entry state with a guard; interpreter fallback on mismatch. Preserves flag pipeline, Q/P latencies, XGKICK progress, E-bit delay slots. | 20–35 (what remains of the 70 ms bookkeeping after E57) | high; 3–5 days; the gate is the same | A per-program differential test (VU state + data memory + GIF bytes) before the first block is scheduled. | queue |
| 5 | **Menu-side Turnip CPU/allocator churn** (N11 S3: driver 61.9 + libc 28.2 of a 41.9 ms menu frame across 4 GsWorkers; `HybridMutex`, scudo, memset). RR1 adds 17–30 small submits per frame. | menus 0.5× → ~0.8× | low | paraLLEl's own per-frame counters (submits, descriptor sets, allocations) Mac vs Odin; batch small PATH3 submits; Granite allocator reuse. A G/N brief, can ride with GB9. | queue |
| 6 | **VU1 on its own thread** (parked by Brad). Moves 80–110 ms off the critical thread; the only lever that gets below ~35 ms without stage B. EE↔VU1 handoff ordering is exactly class A. | ~2× | high | Size it with F1 Part 2 numbers only. | park |

Order of measurement: F1 Part 2 pair → one call-graph profile on the F1 APK (30 s, race) → the
rank-2 A/B pair → decide rank 3/4 scope. Report each as a clean Odin pair with thermal ≤ 2 before
each launch (N11's recipe). Honest ceiling with 1–5 done: ≈ 40–55 ms/frame (0.3–0.4×); real
time needs rank 6 or a GS-submit offload plus rank 4.

Brief sketch, rank 2 (`NP1`, muse, 2 h, Odin): F1 APK already installed → one `simpleperf record
--call-graph fp --app` 30 s from tick 2400 (N11 driver `--profile-after-tick`), symbolize on
bytesize, hand back the callers of `@plt`, `__memset_aarch64_nt`, `clock_gettime` and the top
kernel rows. Part 2 (after the orchestrator reads it): add `-Wl,-Bsymbolic` to the Android link
(and, if the callers say so, replace the arbiter's `resize`+`memcpy` with `assign`), one APK, two
clean race runs ABBA vs the F1 APK, thermal ≤ 2 before each.

## 4. Mac ↔ Odin alignment (GB9)

Path facts (`[gs-path]` lines, TL1 Part 1b/2; code in the paraLLEl fork):

| Field | Mac | Odin | Cause |
|---|---|---|---|
| `hier_rule` | flat-always | hier-if-large (t2=2, t4=4) | `gs_renderer.cpp:1822` `#ifdef __APPLE__ return 1` ("broken Metal drivers") |
| subgroups | free 4..128, vk11 subgroup 32 | wave64 / wave64-fixed, subgroup 128 | `gs_renderer.cpp:2094-2127` (fork commit `495cb69`); Apple max subgroup 32 |
| descriptors | plain | buffer | MoltenVK lacks descriptor buffer/heap; Granite disables push descriptors on Apple (`device.cpp:881`) |
| events | emulated as barriers | native | `device.cpp:881-886` |
| sampler feedback | on | on | same |

- **Stays Odin-only:** the wave64 hierarchical binner (the Mac cannot run a 64-wide subgroup),
  the descriptor-buffer code path, Turnip driver CPU cost and thermals, Adreno bilinear rounding
  (±1–2 LSB), adrenotools loading. Gate these with `odin_replay.py` on the Mac's stream (TL1).
- **Moves to the Mac:** everything upstream of the GS stream (already: GB8 det-hash identical);
  the *binning logic itself* at wave32 (knob 1 below); descriptor-path bugs (knob 2, run on the
  Odin); shader math (exact bilinear makes Mac vs Odin a byte gate instead of ±2).
- **Knobs worth adding:**
  1. `PGS_HIER_BINNING=force|auto|off` — remove the Apple early return behind the env; test on
     M5/MoltenVK whether "broken Metal drivers" still holds (one replay of the N8X1 stream,
     compare to CPU path). Covers the tile-assignment logic the Odin runs. **do now** (GB9 P1).
  2. `PGS_DESC_PATH=plain|buffer` on the Odin — Granite supports plain everywhere; one Odin
     replay rules descriptor buffers in or out of any future Odin-only defect. **do now** (an
     env line + one replay).
  3. Exact bilinear in `ubershader.comp` (todo) — turns every Mac/Odin replay into a byte
     compare. queue.
  4. `subgroup` forcing — not feasible either way (Apple ≤ 32, Adreno ≥ 64). park, and record
     it in `facts.md` so nobody briefs it.
- **Reference correction:** the CPU backend lacks dither, mipmap/LOD, COLCLAMP, AA1, SCANMSK
  (`gs_cpu_backend.cpp` has no such tokens), so CPU-vs-paraLLEl pixel diffs (GB8 Q3: 24–68 %
  pixels equal) are not a correctness signal. The reference for pixels is PCSX2 gsrunner on our
  stream (RR1 E7); its blank frames from tick 1608 in `rr1_cap2gs.py` are a converter gap to fix
  before the next GS correctness brief. queue.

## 5. Process

Evidence (git log, `~/dev/ssx3`): lane reports RR1 23:18, N11 Part 2 23:38, GB8 00:01, E57 00:10;
next `[orch]` commit 06:50. Six hours forty minutes with four passed lanes, an idle Odin and an
idle fold. `watch.sh` exits on the first commit/blocked pane/heartbeat and must be restarted by
the orchestrator; the orchestrator's turn ended without a wakeup (memory note 09-25).

| # | Cost | Change | Tag |
|---|---|---|---|
| 1 | Overnight stall (~7 h of device and fold time) | Rule: an orchestrator turn that leaves any pane `working` ends with a scheduled wakeup ≤ 30 min, always. Tooling: `watch.sh` loops (`while :; do … done`) and appends events to `local/orch-events.log` instead of exiting; a second dead-man (cron or `herdr`) flags "lane report ≥ 45 min ungated" as a blocker. | **do now** |
| 2 | Speed-pair contention: exclusive claims are polled (`gb8_watch.py 1500`), E57 ran ~8 speed boots per session, E61's pair ran at load 10–15 and is uncomparable to E58 | `p_lane_lease.py claim --exclusive --wait` with a FIFO queue file and a max hold; builds run through a wrapper that waits while an exclusive lease exists (`nice` alone did not protect E57 session 1); briefs say "queue, don't poll". | **do now** (30-min tooling item) |
| 3 | Two lanes stopped on build/config facts knowable in advance (TL1 word-watch symbols, N11 non-profileable APK) | The permission/build preflight already in todo; add "manifest/CMake flags the brief depends on" to the brief template's Facts section. | queue |
| 4 | 236 gates in three days, each hand-assembled | The `gate` helper (todo). | queue |
| 5 | Explorer sessions worked (4 mechanisms in ~6 h total) | Keep: unknown-cause → explorer with device + notebook; named mechanism → muse. Cap explorers at one per lane at a time so the mini stays quiet for speed windows. | keep |

## 6. Things we are getting wrong that were not asked

1. **`SLUSOVF.BIG`.** The override makes it loadable (AU9 row 6). "SLUS overflow" is the naming
   of an EE code overlay; if the game loads code from it and jumps in, the static recomp has no
   functions and release policy `ContinueToTarget` hides it. Check: read the file header on the
   ISO (`AU9/isofiles.py`), and the `[coverage:missing-functions]` line of the F1 B1 boot. If it
   is code, it needs its own recompile pass (large) and must be scheduled, not discovered.
   **do now** (10 min + the F1 log).
2. **Release builds hide misses.** Ship with the coverage counter written to a file on exit (Odin
   pull), and read it at every device gate (§1 suspect 3). **do now**.
3. **The tripwire comes before more overrides.** The `0x3E3968` override is right as a bridge; a
   second per-function patch would be the wrong habit. After SB1 lands and the regen validates,
   retire the override.
4. **Speed labels.** F1 B2 menus read 1.287× real time: speed boots are unpaced, so ratios above
   1 mean "headroom", and the ledger should say so once. Odin presents (55–59/s) versus guest
   vsyncs (7/s) are already separated; keep it that way.
5. **Two counters exist and are not read at gates:** `noteVuRun(budgetExhausted)` and
   `noteUnhandledRpc`. Add both lines to the F1/N11 gate template.
6. **`facts.md` should carry the models, not only the fixes:** the arbiter drain sort, the PATH3
   window model and its stated limit (RR1 gap), the DMA-at-CHCR-store completion, the 65,536 and
   4,096 cycle caps, the INTC lines that are dispatched (2, 3, 9–12). Briefs keep re-deriving them.
7. **Hash + stream digest is the standard gate for every runtime change** (E57 set it; GB8 used
   the hash half). Frames viewed by the orchestrator remain the human check, not the gate.
8. **iOS flicker** stays a hypothesis until F1 Part 3; if it survives the fold, §1 suspect 1 is
   the next mechanism to test, not a new symptom hunt.

## Verification status

Verified by reading code: the arbiter sort and drain sites; all integer emitters named in §2
(S1–S4); the branch emitter; the DMA chain walker cap and tag handling; the CHCR read; the IRQ
dispatch sites; the VU1/VU0 budgets; the `__APPLE__` sites in paraLLEl-GS and Granite; the
`watch.sh` loop; the commit timeline. Census (S6) is a regex pass, not a dataflow analysis: the
"nearest writer" can be on a non-dominating path, so its counts bound the problem, they do not
prove a site safe. Not verified: whether `SLUSOVF.BIG` holds code; the PLT callers; whether
PCSX2's UNPACK V2/V3 write z/w (check `Vif_Unpack.cpp` before briefing suspect 5).

## Orchestrator adoption (2026-09-25)

Adopted as written. Do-now items launched: SB1 (§2), GA1 (§1 suspect 1, Part 1), CT1 (§1 suspects
2–4 + §6 items 1, 2, 5; the orchestrator confirmed `SLUSOVF.BIG` holds `overlay.dat`, a relocatable
MIPS ELF), GB9 Part 1 (§4 knob 1). NP1 (§3 rank 2) and knob 2 wait for the Odin (F1 Part 2 holds
it). Process §5 #1: the watcher is restarted every turn and "never end a turn with panes working
and no watcher" is in the runbook and memory; the looping watcher + dead-man is queued with the
lease FIFO. Models from §6 item 6 are now in `docs/facts.md`.
