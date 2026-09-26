# VR2 — VU1 stage C: per-pair levers + flag liveness (stages 1–2)

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/VR2.md`, 2026-09-25 ~19:20–21:05 EDT,
Mac mini only. Tables and receipts; the orchestrator decides. No push, no Odin.

## Headline

- **All candidates are bit-exact.** Suite 655/655 (F5's 654 + a new generated-vs-interpreter
  differential test). det-hash ticks 1–2400 and snd/coverage are IDENTICAL to the F5 key
  `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d`, with a 512 KB game-thread stack, at the stage-1 tip
  (c3) and the stage-2 tip (c4). Total VU1 cycles stay 1,038,465,761, 100 % generated. No `blr` in
  any of 14,336 pair functions.
- **Speed (mini M5 Pro, paraLLEl, diagnostics off, exclusive, FR1-R1, race window t1800–2400):**
  base F5 27.98 → **c3 30.63 vsyncs/s (0.467× → 0.511× of 59.94, 1.095×)** → c4 30.94 (0.516×,
  1.106×). Per lever: trace skip +5.5 %, `next()` trim +1.6 %, flag-queue/pending-until +2.1 %.
  **Flag liveness (stage 2) is +0.6 % over c3, inside the same-binary noise (~1.5 %). Its ABBA is
  positive in both orders (+0.95 %, +0.35 %), but that is not a demonstrated gain.**
- **Why stage 2 is small:** the status **sticky bits (6–9) accumulate and stay visible**, both to
  later programs and to the full-state differential test. So every FMAC still needs its per-lane
  Z/S/U/O classification and the product sticky of MADD-type ops. Liveness can drop only the MAC
  assembly and store and status bits 0–3. On the route that happens for **70.1 % of all flag writes**
  (91 % of direct ones), and it saves a few instructions each.
- **The new differential test found a real stage-2 bug before any boot.** A dead write in an
  E-bit delay slot was exposed by cut + `resume()`, which runs the next program. It is fixed in the
  analysis (end slots stay live); see "Stage 2".
- Profile (diagnostic): pair functions 43.0 % → 36.1 % of busy samples, VU1 total 60.9 % → 57.3 %.
  What's left in the pairs is the scoreboard and state traffic that stage 4 (block functions) targets.

## Per-commit table

Fork worktree `~/dev/ssx3-work/VR2/PS2Recomp`, local branch `vr2` from `a3efbfe` (not pushed).
Runner-dir guard (`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) is empty at the tip.
ABBA rates come from holds H1–H4 (below). Profile = VU1 share of busy `sample` rows, 15 s from about t1850.

| # | Fork commit | Change | Suite | Diff. test | det-hash + 512 KB | Race vsyncs/s (runs) | ÷59.94 | vs base | VU1 / pair fns |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| base | `a3efbfe` | F5 | 654 (F5) | — | key | 27.98 (4) | 0.467× | 1.000× | 60.9 % / 43.0 % |
| c0 | `9b16870` | differential test (generated vs queued interpreter), test hooks | 655/655 | pass | — | — | — | — | — |
| c1 | `b5ff643` | lever 1: generated pairs skip E36/E37 trace checks (armed runs → interpreter) | 655/655 | pass | (via c3) | 29.52 (2) | 0.493× | 1.055× | 58.6 % / 38.8 % |
| — | `4ae0e47` | test prints its coverage line | — | — | — | — | — | — | — |
| c2 | `0f0c2d5` | lever 2: `next()` keeps only the stop check; constant code size/mask | 655/655 | pass, 0/88,632 | (via c3) | 30.00 (2) | 0.501× | 1.072× | 56.9 % / 37.8 % |
| c3 | `9d7e2a2` | lever 3: flag-queue check at the flag write; plain pending-until store | 655/655 | pass, 0/88,632 | **IDENTICAL** | 30.63 (4) | 0.511× | **1.095×** | 56.9 % / 36.4 % |
| c4 | `639df0f` | stage 2: static flag liveness (regenerated images) | 655/655 | pass, 0/88,632 | **IDENTICAL** | 30.94 (2) | 0.516× | 1.106× | 57.3 % / 36.1 % |

Diff. test = "VR2 generated pairs match the queued interpreter at every budget cut": 231 programs
in 2 synthetic images, 88,632 runs (cut / cut+resume / cut+fresh execute at every budget),
3.67 M generated cycles, 0 mismatches (`suites.txt`). det receipts: `check-c3-det.txt`,
`check-c4-det.txt` (hash IDENTICAL ticks 1..2400, snd/coverage IDENTICAL). VU1 stats (both runs):
`runs=1114112 generated_cycles=1038465761 interpreted_cycles=0` (`stats-flags.txt`).

## Stage 1 — the three levers

| Lever | What changed | Why it is exact |
| --- | --- | --- |
| 1 | `issuePair<true>` drops `m_traceArmed`/`m_entryArmed` and the trace bookkeeping. `run()` sets `recomp = nullptr` when either trace is armed. | Armed runs are dev-only. They now run in the interpreter, which is itself exact, and `m_entryArmed` only turns off mid-run. |
| 2 | `recompChainReady` is now `!m_stopRequested`. `lookupRecompProgram` requires the code size to be 0x4000. `issuePair<true>` uses a constant code size and pc mask. | Budget: `issuePair` stops a pair that starts at or past `budgetEnd` before it changes any state, so `run()` sees the same stop. Commit: a no-op, since `advanceOneCycle` already committed everything ready. Pc: `pc+8` wraps at 0x4000, and branch targets are `(pc+8+imm·8)&0x3FFF` or `VI·8&0x3FFF`, both in range and 8-aligned. |
| 3 | The FSSET-in-queue scan (`directFlagsNow`) moves from every pair to the FMAC/CLIP flag write. `noteDirect` stores `m_cycle+4` without the max. | The flag queue changes only in the stall, before the upper op runs, so the value is the same. Every direct write lands within `kDirectMaxLatency` (every VF write decodes at latency 4, `vfLatency` is never set; direct VI/ACC/stores land in ≤ 1), so `m_cycle+4` is at or past every earlier landing. |

## Stage 2 — flag liveness (`buildFlagLiveness`, emitter)

- **Rule.** The MAC/status write of pair *i* (an FMAC with dest ≠ 0) is dead when, on every path
  from *i* (including as the delay slot of *i*−1), another MAC/status write *k* issues before any of
  these: a flag op (lowers 0x10–0x1C, readers plus FSSET/FCSET), an E/D/T bit, a JR/JALR, an
  out-of-range branch, a branch in a delay slot, a reserved pair, an XGKICK, or 12 pairs. Also, no
  flag op may follow in the 3 pairs after *k*, and *i* must not be an **end slot** (the pair after
  an E/D/T pair, reached sequentially, via a static target, or anywhere when a JR has an
  E-bit delay slot).
- **Budget guard.** The emitter writes `issuePair<true, W>`, where W bounds the cycles from *i*'s
  issue until *k*'s flags land: per pair 1 + worst stall (4; FDIV/WAITQ 13; EFU/WAITP 54), plus 4.
  The dead form applies only when `m_cycle + W ≤ budgetEnd` and the flag commit is direct (no
  queued FSSET). It then skips MAC and status bits 0–3 and still ORs the sticky bits in. Chains of
  dead writes are covered link by link, each by its own guard.
- **Bug the test caught.** In the first c4 build, pair 0x2df8 of fixture image 1 (the delay slot of
  an E-bit pair) was marked dead. Its overwriting write belonged to the next program. After a cut
  at budget 14 and `resume()`, the final MAC was 0x10 against the reference 0x40. Fixed with the
  end-slot rule before commit; 655/655 and 0 mismatches after. The game images were not affected:
  the dump came from the fixed emitter.
- **Liveness stats.** Static: 4,440 of 5,167 MAC/status-writing pairs dead across the 7 images
  (86 %; stale code included). Dynamic (det run to t2400): `flag_dead=369,616,605` of 527,493,855
  flag writes (FMAC + CLIP) = **70.1 %**, and 91.2 % of the 405,176,540 direct ones
  (`stats-flags.txt`).
- **Images regenerated** by a dump boot (runner-c4-dump with old images, `PS2X_VU1_RECOMP=0`,
  `PS2X_VU1_RECOMP_DUMP=~/dev/ssx3-work/VR2/vu1gen`, FR1-R1 to t2493, one slot, speed mode under a
  held slot). The same 7 hashes came back. Diffed against `vu1gen-ssx3`, the only changes are the
  `issuePair<true, W>` arguments and one summary comment per file. SHAs are in `vu1gen.sha`. The
  images stay outside every repo.

## Speed holds (exclusive, ≤ 5 min each, `speed_hold.py`, `speed-all.txt`)

Four holds of about 3–4 min each (238, 230, 178 and 172 s), with at least 1 min between H3 and H4.
The host load at the start fell from 7.6 to 1.3 over the session. Base samples 5 race-window rates;
the faster runners sample 4, because the 5 s windows fall differently.

| Hold | Order | base | c1 | c2 | c3 | c4 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| H1 (20:09) | base c1 c2 c3 | 27.82 | 29.45 | 30.02 | 30.69 | |
| H2 (20:13) | c3 c2 c1 base | 28.07 | 29.60 | 29.98 | 30.34 | |
| H3 (20:37) | base c3 c4 | 27.91 | | | 30.50 | 30.79 |
| H4 (20:41) | c4 c3 base | 28.11 | | | 30.98 | 31.09 |
| **mean** | | **27.98** | **29.52** | **30.00** | **30.63** | **30.94** |

For comparison, F5 B6 (single run, quieter host) read 28.17 on the same base runner.

## VU1 profile (diagnostic, not speed; `vr2_profile.py`, `profile-*.txt`)

| | base | c1 | c2 | c3 | c4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| busy samples (15 s) | 5,372 | 5,593 | 5,684 | 5,752 | 6,024 |
| VU1 total | 60.9 % | 58.6 % | 56.9 % | 56.9 % | 57.3 % |
| generated pair functions | 43.0 % | 38.8 % | 37.8 % | 36.4 % | 36.1 % |
| commitReadyPipelines | 5.9 % | | | 6.6 % | 6.4 % |
| run | 4.5 % | | | 5.2 % | 5.6 % |
| execUpper (VU0 interpreter) | 3.2 % | | | 3.8 % | 4.0 % |
| progressXgkick | 3.0 % | | | 3.4 % | 3.0 % |

## Stage 4 sketch (block functions), for the orchestrator's Part-2 decision

- **What's left per pair (VB1's `xctrace` classes: loads 48 %, ALU 19 %, FP double 12 %).**
  Stage 1 took out the control loads. What remains is the scoreboard: the max over `m_vfReady`
  lanes, the `markPairWrites` stores, the old/new VF copies, the `m_vfLatestWrite`/sequence stores,
  the `m_cycle`/`m_state.cycles` store and `advanceOneCycle` per pair, and pc/branch state. Then the
  FMAC exact arithmetic and flag classification, which liveness cannot remove (sticky).
- **Design.** One host function per basic block, reusing VR1's image keying and fallback. At entry,
  a guard compares the live scoreboard against the block's assumed entry state (for example "all
  ready at `m_cycle`", with no FDIV/EFU/XGKICK in flight, `m_flagValidMask==0` and
  `m_cycle + blockMaxCycles ≤ budgetEnd`). On a hit:
  - VF/VI/ACC stay in locals and stalls are constants (the microVU pass-1 model from Q1).
  - Writes go straight to locals and are stored back at block exit, with the ready cycles only
    for the exit's live-out registers.
  - Flags keep the direct/dead forms.
  - `m_cycle` advances once per block, except that pairs with XGKICK/progressXgkick,
    stores feeding PATH1 and Q/P reads stay per cycle (or end the block).

  On a miss, the stage-A/B pair functions run, and they are already exact.
- **Validation** is now cheap: the synthetic-image differential test (cut/resume/fresh at every
  budget) directly exercises block entry and exit at every cycle. Blocks that end at budget cuts
  inside the block need the guard to fall back.
- **Estimate.** Pair functions are 36 % of busy samples. If blocks remove half of the non-FP work
  (the scoreboard, copies and per-pair cycle stepping), that is about 12–18 % of busy time, which
  would be **≈1.12–1.2× on the Mac race** on top of c3. It's a guess until built; how often the guard
  hits decides it. Cost: 3–5 days (E57's figure), probably at the lower end now that the test
  harness exists. Cheaper side items with visible shares: VU0 still interpreted (4 %),
  `run()` + `commitReadyPipelines` (≈ 12 %, Q/P and queued flags).

## Exact commands

- Builds (10 allowed, 9 used; mini, ccache):
  `local/tooling/build/mac_build.sh ~/dev/ssx3-work/VR2/PS2Recomp ~/dev/ssx3-work/VR2/build-clean [--det --target ps2EntryRunner] [--vu1 ~/dev/ssx3-work/VR2/vu1gen]`
  Build dirs: `build-clean` for 1 c0 tests, 2 c3, 4 c1, 5 c2, 6 c4 (first try), 7 c4 dump runner,
  8 c4 with the new images; `build-det` for 3 c3 det and 9 c4 det.
- Suite: `cd ~/dev/ssx3-work/VR2/PS2Recomp && ../bin/tests-<c>`.
- det gate: `ssx3_boot.py --mode det --backend parallel --runner <abs runner-cN-det> --label vr2-cN-det --out <ABS dir> --vu1-stats --stack-kb 512 --dump-ticks 1090,1800,2100 --route fr1r1`
  then `baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand <dir>`.
  **Pass an absolute `--out`.** With a relative one, the runner resolves `PS2X_SND_LOG` from its own
  cwd and snd.log lands in `<out>/<out>/`. For c3 I moved it up before the compare; the file is
  unchanged.
- Speed: `python3 speed_hold.py H<n> <cands…>`, then `python3 speed_table.py run`.
  Profiles: `python3 vr2_profile.py <cand>`, then `profile_share.py run/p-<cand>/sample.txt`
  (VB1's bucketer).
- Tail-call audit: VB1 `tailcall_audit.sh` (`tailcall-audit.txt`): `with_blr=0` everywhere.
  Stack-guard counts (3,888 base → 2,592 c4) predate VR2 and are not a hand-off call.
- Boots used: 3 one-slot boots (c3 det, dump, c4 det) + 5 profiles = 8 of 20, plus 14 speed boots
  in the 4 exclusive holds.

## Binaries (sha256; two reads match, `binaries-sha.txt`)

| Runner | sha256 |
| --- | --- |
| base F5 `runner-clean` | `e1e598c2cdcd…` |
| c1 clean | `1493c7b98acf…` |
| c2 clean | `54f21f15904f…` |
| c3 clean / det | `d3f358942e05…` / `ceb3741e105b…` |
| c4 clean / det / dump | `fe3f36328253…` / `c1637c3e1680…` / `4dfd0866f69e…` |

## Gaps

- Mac only; no Odin run (the orchestrator schedules one).
- The det-hash gate ran at c3 (stage-1 tip) and c4, not at c1 and c2 alone. Those have the suite
  and the differential test, and c3 contains them.
- The strict CPU-backend GS SHA (VR1/VB1's extra gate) was not re-run. det-hash, snd/coverage, the
  suite and the full-state differential test are the gates here.
- Stage 2's gain is inside the noise. Keeping it adds regenerated images and ≈ 250 lines of
  analysis for ~0.6 %. It's exact and tested, but the orchestrator may prefer to fold stage 1 only
  (c3) and keep stage 2 as the flag-analysis base for stage 4.
- Error-path stop (`m_stopRequested` from a reserved-instruction report mid-program): as VB1
  noted, a dead or direct write could be visible where the queue would still hold it. There are 0
  reserved reports on the route.
- The differential test's instruction mix (VB1's, plus flag-distance programs) has no XGKICK,
  EFU/WAITP, MFP, JR/JALR or I-bit pairs. The liveness rule treats all of these as live or with
  the widest stall, and the whole-game gate covers them on the route.
- Generated images still come from a manual dump boot (unchanged from VR1).
- Scratch: `~/dev/ssx3-work/VR2` is 4.7 GB (cap 15 GB), made up of build dirs, bin/ and run/.

## Orchestrator gate, stages 1–2 (2026-09-26)

**Pass.** Stage 1 (c0–c3) is bit-exact (suite, new generated-vs-interpreter differential test at every
budget cut, det-hash + 512 KB) and worth **1.095× on the Mac race** (4-run ABBA means). Stage 2 (c4,
flag liveness) is exact but +0.6 %, inside noise, and needs regenerated images and a new template
parameter: **held, not folded** (sticky bits keep the FMAC classification alive; block functions in
stage 4 revisit flags anyway). The differential test catching the E-bit delay-slot bug before any
boot is exactly the safety net stage 4 needs.

## Part 2 brief (orchestrator)
**2A — fold prep (then stop for the push):** new branch `vr2-fold` from fork `ssx3` **`5474956`** (SS1
save states landed; it touches VU1 serialization, so expect conflicts in `ps2_vu1.h`/`ps2_vu1_core.cpp`
— resolve by keeping both; if a hunk needs a judgment call, stop and hand back). Cherry-pick `9b16870
b5ff643 4ae0e47 0f0c2d5 9d7e2a2` (not `639df0f`). Suite; differential test; det boot on **bradflix**
(`ssx3_boot.py --host bradflix`, `bradflix_build.sh`) compared against the a3efbfe key (guest is
unchanged by SS1 with its knobs off) and also a save-state round trip (`baseline.py get-state
a3efbfe-fr1r1-t2000-parallel-1x-433cb405` → `--load` → compare from t2001; a VU1 change may bump the VU1
section version — if the load refuses, say which section); 512 KB stack; one Android compile on bytesize
(F5 recipe, hold the ssh). Stop and hand back; I push.
**2B — stage 4 block functions** (after the push, same pane): as sketched above, behind a default-off
knob until proven; exactness bar unchanged; ABBA on the mini vs `vr2-fold`. Budget 6 h, ≤ 12 builds.
