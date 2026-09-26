# VR3 — VU0 static recompile, stage 1 (profile + design)

Worker: Claude Code (Opus 5.5), brief `local/muse/prompts/VR3.md`, 2026-09-26 ~01:45–02:30 EDT.
Mac mini only, one-slot diagnostic boots. Tables and receipts; the orchestrator decides. No push, no
Odin. **Stopped at the stage-1 gate.**

## Headline

- **Entry overhead does not dominate. Execution does.** In the fork-tip profile, the VU0 subtree
  (`executeVU0Microprogram`) is **633 samples = 8.6 % of GameThread wall samples** (12.9 % of
  process busy samples by VB1's bucketer). Of those samples, **≈ 7 % are per-start fixed cost**:
  memsets, `resetScheduler`, the inlined copies, and `execute()` and `run()` setup. **≈ 93 % is
  per-pair interpretation**: the `run()` issue loop 32 %, `execUpper` 30 %,
  `commitReadyPipelines` 19 %, `execLower` 6 % and decode-cache lookup 6 %. The census's own timers
  agree: entry + exit are **3.4 %** of timed VU0 wall time. Their "run" span still contains `run()`'s
  fixed setup.
- **The VU0 workload is small and stable.** On FR1-R1 there is **one VU0 code image**
  (`40829a098c260b4f`), uploaded once at t1552 and never re-uploaded (1 code-generation change in
  the whole boot). It has **7 entry points**. In the race window t1800–2400 there are **1,243 starts
  per vsync**, averaging **63 VU0 cycles** (max 204). **There are 0 budget hits** (4,096). 33 % of the
  starts come through VCALLMSR, the rest through VCALLMS. Four entry points carry 99.6 % of the
  cycles, and `0xdb8` alone carries 55 %.
- **Recommendation:** skip stage 2 as a standalone stage. Its whole ceiling is ≈ 0.6 % of
  game-thread time, too small to show in an ABBA. Go to stage 3 (recompile) with the design below.
  Estimated gain, *not measured*: VU0 time drops to about 0.44–0.56× of today's. That frees
  **≈ 3.8–4.8 % of game-thread time on the Mac (~1.04–1.05× if the race is game-thread-bound)**.
  On the Odin it is **≈ 2.4–3.1 ms of N12's 68 ms frame**, the low end of RV4's 2–4 model-ms. The
  larger figure also needs direct commit (VB1) enabled for VU0, which is a separate knob and your
  call (see Design, item 6).

## Entry-cost split

Profile: `sample` of the GameThread for 15 s from t1930. Runner `runner-c0-clean` = fork tip `d585e5c`
+ the census commit `69e60e1` (census **off**), with diagnostics compiled out, paraLLEl, canonical VU1
images. **Diagnostic, not a speed number**: one slot, with the census boot running in parallel in a
second slot. `vr3_tree.py` credits each descendant's *self* samples under the outermost VU0 frame
(`profile-c0-vu0-tree.txt`).

| Bucket (self samples under `executeVU0Microprogram`) | samples | % of VU0 subtree | class |
| --- | ---: | ---: | --- |
| `VU1Interpreter::run`: the leaf PCs sit in the inlined `issuePair<false>` loop body (scoreboard, pc/branch step; checked against `llvm-objdump` at +0x404/+0x4d4/+0xa7c/+0xb60/+0x1ea8) | 203 | 32.1 % | per pair |
| `execUpper` | 192 | 30.3 % | per pair |
| `commitReadyPipelines` | 120 | 19.0 % | per pair |
| `execLower` | 36 | 5.7 % | per pair |
| `getDecodedInstructionPairForPc` | 36 | 5.7 % | per pair |
| `queueClip` | 3 | 0.5 % | per pair |
| `_platform_memset` + `bzero` (+ stub): `reset()` zeroes `m_state`, then `copyVu0ContextToState` zeroes it again | 25 | 3.9 % | per start |
| `resetScheduler`: runs twice per start, from `reset()` and from `execute()` | 10 | 1.6 % | per start |
| `executeVU0Microprogram` self (inlined copy in/out) | 4 | 0.6 % | per start |
| `execute`, trace `ensureInit` | 2 | 0.3 % | per start |
| `run()` leaf PCs before the loop (+0x5c, +0x310) | 6 | 0.9 % | per start |
| **Total** | **633** | per start ≈ **7.4 %**, per pair ≈ **92.6 %** | |

- VU0 inclusive = 633 of 7,328 GameThread samples = **8.6 % of game-thread wall** (12.85 % of the
  process busy rows that `profile_share.py` counts, `profile-c0.txt`).
- Census timers (diagnostic build, steady_clock, 41.7 ns ticks, averaged over 745,898 starts,
  `census-c0.txt`): entry (reset + copy in) **50.7 ms**, run **1,832 ms**, exit (copy out)
  **13.0 ms** over the window's 600 vsyncs. Entry + exit = **3.4 %**. Run = 2.46 µs per start, about
  39 ns per VU0 cycle. VU0 spans ≈ 1.90 s of the ≈ 23.3 s window at 25.7 vsyncs/s, **≈ 8.1 % of
  wall**, consistent with the profile's 8.6 %.
- Cheap exact trims exist: drop the duplicate `m_state` memset and the duplicate
  `resetScheduler`. Together they are worth at most ≈ 0.3–0.4 % of game-thread time, below ABBA
  noise (~1.5 %). They can ride along in stage 3 if you want them.

## VU0 program census (FR1-R1, t1800 → t2400)

Runner `runner-c0-clean` with `PS2X_VR3_VU0_CENSUS=1` and `PS2X_VR3_VU0_IMAGE_DUMP` (one slot, stop
t2450). Window = t2400 line minus t1800 line. Image: `vu0_40829a098c260b4f.bin`, 4,096 B, sha256
`21eebd05…b926a6` (two reads), in `~/dev/ssx3-work/vu0gen-vr3/images/` (game-derived, not in git).
It has 488 non-zero pairs (last at 0xf38), 17 E-bit pairs and 1 I-bit pair. Its lowers include
flag ops (opHi 0x12–0x1C) and branches/JR, which matters for direct commit and liveness.

| Entry (startPC) | starts | % starts | VU0 cycles | % cycles | avg cyc | max cyc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0xdb8 | 262,743 | 35.2 % | 25,990,980 | 55.3 % | 98.9 | 204 |
| 0x570 | 221,570 | 29.7 % | 10,192,220 | 21.7 % | 46.0 | 46 |
| 0x948 | 195,933 | 26.3 % | 7,720,315 | 16.4 % | 39.4 | 44 |
| 0xef0 | 57,659 | 7.7 % | 2,795,476 | 6.0 % | 48.5 | 97 |
| 0x828 | 4,232 | 0.6 % | 87,008 | 0.2 % | 20.6 | 30 |
| 0x6e0 | 3,744 | 0.5 % | 168,757 | 0.4 % | 45.1 | 47 |
| 0x0 | 17 | 0.0 % | 12,206 | 0.0 % | 718 | 718 |
| **total** | **745,898** (1,243/vsync) | | **46,966,962** (78,278/vsync) | | **63.0** | 204 |

Max = the cumulative max at t2400. Code-generation changes: 1 (t1552), image changes: 1. VCALLMSR
starts: 244,900 (32.8 %). Budget hits: 0. Callers (the guest `ra` at the start, 39 distinct): the top
two are `0x22a454` (in `sub_0022A408`) with 23.2 % and `0x22a3b4` (in `sub_0022A368`) with 11.7 %.
Eight call sites in `sub_0022A830`, `0x22ace8…0x22adc8`, carry 4.8–6.5 % each; `0x22af90` and
`0x22afa4` in `sub_0022ADD8` carry 2.9 % and 4.8 %. Owners come from `ee-func`; nothing else is
labelled.

## Design: what VR1's emitter needs for VU0

| # | Item | Today (fork `d585e5c`) | Stage-3 change |
| --- | --- | --- | --- |
| 1 | Decoder unit | `emitRecompSource` decodes with a `Unit::VU1` decoder (`ps2_vu1_recomp.cpp:189`) | Pass the unit. The VU0 decode marks 0x64, XGKICK 0x6C, EFU 0x70–0x7E and WAITP 0x7B reserved (`ps2_vu1_core.cpp:1161–1251`), so the table entry is null and the interpreter reports the pair reserved, as it does today. |
| 2 | Code size / pc mask | `issuePair<true>` hard-codes `kRecompCodeSize` 0x4000 for the wrap and branch mask (`ps2_vu1_step_impl.h:463,473`; `ps2_vu1.h:430`) | A per-image constant (template parameter, or `kStatic` split by unit): VU0 0x1000 / 0xFFF, 512 pairs. The interpreter uses `microAddressMask()` (0xFFF for VU0), so this matches it. |
| 3 | Analyses' branch masks | `buildDirectFlagMap`, `planRecompBlocks` and flag liveness compute targets with `& 0x3FFF` | Use `codeSize - 1`. Needed only if direct commit, blocks or liveness are used for VU0. |
| 4 | Keying / lookup | `lookupRecompProgram` returns null for VU0 or when size ≠ 0x4000 (`ps2_vu1_recomp.cpp:100`) | VU0 branch: XXH64 over the 4 KiB, recomputed on `getVU0CodeGeneration()` change (once per boot on this route), registry entry with codeSize 0x1000. `m_vu0` is its own instance, so the cache members are already per unit. Knob `PS2X_VU0_RECOMP` (default **off**, per the brief). Dump `PS2X_VU0_RECOMP_DUMP=<dir>` writes `vu0_<hash>.cpp`. CMake `PS2X_VU0_RECOMP_DIR` globs `vu0_*.cpp` (Gradle later). Distinct template name (`VU0RecompImage<hash>`) so profiles separate it. |
| 5 | Entry / exit | `executeVU0Microprogram`: `reset()`, copy ctx→state, `execute(…, 4096)`, copy back (`ps2_runtime.cpp:3060`, fork `69e60e1`) | Unchanged. Generated pairs run inside `run()` like VU1's; the per-start costs stay (≈ 7 %). No resume path for VU0; every start is a fresh `execute()`. |
| 6 | Direct commit / blocks | `m_directRunOk` and `m_blocksOn` are VU1-only (`ps2_vu1_core.cpp:1457–1459`), so VU0 runs the queued model everywhere | Stage 3 base: stage-A pairs + musttail chaining on the queued model (exact by construction, same `issuePair` body). **Optional, separate commit and knob:** direct commit for VU0, which needs item 3 and a VU0-keyed `directFlagMap`. It is the larger half of the estimated gain; your call whether it is in scope. |
| 7 | Register sharing (COP2 macro mode) | VF/VI/ACC/Q/P/I/R/flags live in `R5900Context` and are copied in and out per start | No change. Generated code touches only `m_vu0.state()`, like the interpreter. The copies measured 3.4 %. |
| 8 | XTOP/XITOP, data mask | top = 0, itop = `ctx->vu0_itop`; data addresses masked to 4 KiB (`dataSize - 1`) in `execLowerImpl` | No change (the same executors, inlined). |
| 9 | Dev traces / hash counters | E36/E37 and the VB1/VR2 counters are guarded by `m_unit == VU1` | No change. |

Emitted size: one image, ≤ 512 pair functions (VU1 images are 2,048), about a quarter of one
VU1 TU's ~8 s compile.

## Exactness plan (stage 3)

1. **Synthetic differential test** (committed; random programs, no game data). A VU0 variant of
   VR2's fixture: 0x1000 images with VU0-legal ops only (VB1's mix of FMAC/ACC/CLIP uppers, LSU, VI,
   flag, FSSET/FCSET, DIV/WAITQ, forward branches, JR/JALR, I-bit pairs; none of item 1's reserved
   ops), plus a few reserved pairs to check the null-entry fallback. Branches wrap at 0xFFF. Run each
   program through generated pairs (`Unit::VU0`) and the queued interpreter, cut at **every budget**
   1…length. After each cut, compare full `VU1State`, VU0 data memory and cycles, then start a fresh
   `execute()` after the cut, which is the only continuation VU0 has. If VU0 direct commit is
   approved, the same matrix runs with it on and off.
2. **Game-image differential** (local only; the image stays out of git). A test case that runs when
   the tests are built with `PS2X_VU0_RECOMP_DIR` and `PS2X_VR3_VU0_IMAGE=<bin>`: seeded random
   VF/VI/ACC/flag states at the 7 census entry points, generated vs interpreter at every cut.
3. **Whole game.** Suite green. det-hash + snd/coverage IDENTICAL vs the current key with
   `PS2X_VU0_RECOMP` on and off (bradflix, 512 KB stack). VU0 coverage: 100 % of VU0 cycles
   generated (a VU0 line in `PS2X_VU1_RECOMP_STATS`). Census cycle totals equal on vs off
   (46,966,962 in the window on this route).
4. **Speed.** Mac ABBA (exclusive, when MT1 allows) of tip vs `PS2X_VU0_RECOMP=1` (same binary, knob
   off vs on), plus a profile. Stop before any device.

Budget for stage 3 as sketched: about 4 builds (tests + dump runner, runner with images, det on
bradflix, one fix), 1 dump boot, 2 det boots, 1–2 profiles, 1 exclusive hold.

## Receipts and commands

- Fork: worktree `~/dev/ssx3-work/VR3/PS2Recomp`, local branch `vr3` from fork `ssx3` `d585e5c`.
  Commit `69e60e1` "[VR3] Dev-only VU0 census" (1 file, +155). Not pushed. Runner-dir guard
  (`git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`) is empty.
- Build 1 of 10: `local/tooling/build/mac_build.sh ~/dev/ssx3-work/VR3/PS2Recomp ~/dev/ssx3-work/VR3/build-clean`
  (3 m 06 s, ccache). Suite: `cd ~/dev/ssx3-work/VR3/PS2Recomp && ../bin/tests-c0` → **674/674**.
- Binaries (sha256, runner read twice): `bin/runner-c0-clean`
  `b8d2b46245e722aa0a6eea6bc94ec4c4f9121c1eabe5c38c0b45fde53f649f8c`; `bin/tests-c0`
  `2412f788730fa53feecf5555dadff1acbd27c8a79c9eac7786c4a2d364350b18`.
- Census boot: `python3 local/research/VR3/vr3_boot.py census-c0 ~/dev/ssx3-work/VR3/bin/runner-c0-clean --stop-tick 2450 --env PS2X_VR3_VU0_CENSUS=1 --env PS2X_VR3_VU0_IMAGE_DUMP=~/dev/ssx3-work/vu0gen-vr3/images`
  (cwd `~/dev/ssx3-work/VR3`), then the `[vr3-vu0*]` lines at t1800/t2400 → `census-c0.txt`.
- Profile boot: `vr3_boot.py prof-c0 <runner> --sample-at 1850 --sample-s 15`, then
  `vr3_tree.py run/prof-c0/sample.txt` → `profile-c0-vu0-tree.txt`, and `local/research/VR1/profile_share.py` →
  `profile-c0.txt`. The GameThread total (7,328) comes from the sample's thread header. The
  `sample.txt` itself (2 MB) is in `~/dev/ssx3-work/VR3/run/prof-c0/`.
- Boots: 2 one-slot diagnostic boots (the two ran at the same time), 0 speed boots, 0 bradflix.
  Disk: `~/dev/ssx3-work/VR3` = 2.0 GB (build dir + 2 runners). The 200 GB check read 70.9 GB before the build.

## Gaps

- The profile is one 15 s sample taken while a second boot ran; the shares are diagnostic. The
  census timers include steady_clock overhead and 41.7 ns quantisation. Both are averages over
  hundreds of thousands of starts and agree with each other (8.1 % vs 8.6 %).
- One route (FR1-R1 to t2400). Other courses may load other VU0 images; a missing image falls back to
  the interpreter.
- The gain estimate transfers VR1's and VB1's measured VU1 per-pair speedups (0.52× stage A,
  0.76× more with direct commit) to VU0's short programs. It is not measured, and Odin numbers scale
  N12's 7 % share.
- Opcode names for the image's lowers are not verified against a decoder; only the opHi ranges
  used by VB1's analyses are quoted.

## Orchestrator gate, stage 1 (2026-09-26)

**Pass.** Entry overhead ≈ 7 % (not dominant), one stable 4 KiB image with 7 entries, 1,243 starts/vsync,
0 budget hits. Approved: skip standalone stage 2; **stage 3 = VU0 recompile** as designed, with (a) the two
exact trims (duplicate `m_state` memset, duplicate `resetScheduler`) as their own commit, (b) stage-A pairs +
musttail on the queued model behind `PS2X_VU0_RECOMP` (default off), and (c) **VU0 direct commit as a
separate commit and knob** (`PS2X_VU0_DIRECT`, default off) — in scope, since VB1's commit-at-issue is exact
by construction and your differential matrix runs it on and off. Exactness plan 1–4 as written (the game-image
differential stays local). Budget ≤ 8 builds. Stop before any device.

# VR3 stage 3 — VU0 recompile (a) trims, (b) stage-A pairs, (c) VU0 direct commit

Worker: Claude Code (Opus 5.5), 2026-09-26 ~02:25–03:00 EDT. Mac mini, plus det boots on bradflix. No
push, no devices. **Stopped before any device.**

## Stage 3 headline

- **Exact on every gate.** Suite **676/676** (+2 tests). Synthetic VU0 differential: 8 images, 237 programs,
  268,848 runs, **0 mismatches**. Game-image differential (local only): 7 entries × 24 seeds, 280,242 runs,
  **0 mismatches**. **det-hash ticks 1–2400 + snd/coverage IDENTICAL** vs
  `a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d` with both knobs off, with `PS2X_VU0_RECOMP=1`, and with
  `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1` (bradflix, 512 KB stack). **VU0 cycles 100 % generated**
  (`[vu0-recomp] … interpreted_cycles=0`). The mini census (VU0 starts, cycles, per-program and per-caller
  rows to t2400) is byte-identical across c0, off, on and on+direct.
- **Speed (mini M5 Pro, paraLLEl, diagnostics off, exclusive, FR1-R1 race window t1800–2400, 3 quiet holds,
  same binary):** off **31.74** → recompile **32.77 vsyncs/s (+3.2 %)** → + direct commit **33.45 vsyncs/s
  (0.530× → 0.558× of 59.94, +5.4 %)**. The order is the same in every hold, including H2, which ran
  under outside load and is excluded from the means.
- **Profile (diagnostic):** VU0's share of GameThread samples goes **8.98 % → 4.71 % (recompile) → 4.10 %
  (+ direct)**, 0.52× / 0.46× of VU0 time. That lands inside stage 1's 0.44–0.56× estimate. What's left under
  VU0 with direct commit on: generated pairs 75 %, `commitReadyPipelines` 11 % (Q/P and queued flags),
  per-start memsets/copies ≈ 10 %.
- **Recommendation (the orchestrator decides):** fold (a)+(b)+(c) as they are (knobs default off). The next
  device build should carry the VU0 image (`-Pps2xVu0RecompDir`; Gradle wiring is not done yet, see Gaps)
  with an Odin pair: off vs `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1`. On the Mac, direct commit is the better
  default candidate. That default is your call once the Odin pair is in.

## Fork commits (`~/dev/ssx3-work/VR3/PS2Recomp`, local branch `vr3` from fork `ssx3` `d585e5c`; not pushed)

| # | Commit | Change | Files | Exactness argument / check |
| --- | --- | --- | --- | --- |
| census | `69e60e1` | dev-only VU0 census (stage 1) | ps2_runtime.cpp +155 | off: one static branch per start |
| (a) | `fe1341e` | `resetForVu0Start()`: VU0 starts drop `reset()`'s dead `m_state` memset and `resetScheduler` | 3 files | `copyVu0ContextToState` memsets and refills all of `m_state`; `execute()` runs `resetScheduler()` before anything reads it. det IDENTICAL (off run) |
| (b) | `1932d63` | VU0 static recompile behind `PS2X_VU0_RECOMP` (default off): emitter unit param (`VU0RecompImage<hash>`, 512 pair functions, no blocks, `issuePair<true,-1,false,0x1000u>`), `issuePair` `kCodeSize` template parameter (default 0x4000 = VU1 unchanged), VU0 keying + `[vu0-recomp]` stats, `PS2X_VU0_RECOMP_DUMP`, CMake `PS2X_VU0_RECOMP_DIR`, VU0 fixture images + both differential tests | 8 files, +417/−41 | VU1 fixture sources byte-identical to c0's; differential 0 mismatches; det IDENTICAL |
| (c) | `d52e7f0` | VU0 direct commit behind `PS2X_VU0_DIRECT` (default off): `m_directRunOk` per unit, blocks stay VU1-only, direct/flag maps use the unit's pc mask (VU1 = 0x3FFF, unchanged), VU0 lookup keys the image for the tracked map; differential adds interpreter+direct and generated+direct | 4 files, +33/−12 | differential 0 mismatches in both direct modes; det IDENTICAL |

Runner-dir guard (`git diff --stat 14b1e5cb vr3 -- ps2xRuntime/src/runner`) is empty. bradflix holds the
commits in the private ref `refs/vr3/tip` (`HS1/PS2Recomp`, via bundle; nothing went to GitHub). Remove that
ref after the fold.

## Gates

| Gate | Result | Receipt |
| --- | --- | --- |
| Suite, no game image (`tests-c3`) | 676/676; `[vr3-diff] vu0 images 8 programs 237 runs 268848 generated_cycles 22656394 mismatches 0`; VR2's VU1 differential unchanged (254,400 runs, 0) | `suites-c3.txt` |
| Suite, game image compiled in (`tests-c3v`, `PS2X_VR3_VU0_IMAGE=…/vu0_40829a098c260b4f.bin PS2X_VR3_VU0_ENTRIES=0,570,6e0,828,948,db8,ef0`) | 676/676; `[vr3-game-diff] … starts 168 runs 280242 generated_cycles 88272906 mismatches 0` | `suites-c3.txt` |
| Modes in each differential run | reference = VU0 interpreter, every write queued; compared: generated queued, interpreter + direct, generated + direct; each at every budget 1…max, then cut / resume / fresh execute; full `VU1State` (flags, cycles, pc) + data memory | test source |
| Tail calls | 512 VU0 pair functions, `with_blr=0` | `tailcall-audit-vu0.txt` |
| det bradflix, 512 KB, knobs off | **IDENTICAL** (hash 1..2400, snd/coverage) | `check-c3-det-off.txt` |
| det, `PS2X_VU0_RECOMP=1` | **IDENTICAL**; `[vu0-recomp] runs=983040 generated_cycles=61659739 interpreted_cycles=0` | `check-c3-det-on.txt` |
| det, `PS2X_VU0_RECOMP=1 PS2X_VU0_DIRECT=1` | **IDENTICAL**; same VU0 coverage line | `check-c3-det-dir.txt` |
| VU0 census, mini (c0 / off / on / dir) | t2400: `calls=933533 cycles=58593197 budget_hits=0` in all four; per-program + per-caller rows hash `8c77e1749b30ee5e` in all four; on/dir `generated_share=1.0000` | `census-c3-*.txt`, `census-c0.txt` |

## Speed (mini M5 Pro, diagnostics off, exclusive lease, FR1-R1, race window t1800–2400)

Same runner `runner-c3-clean` (`ebd1f4c4…`) in every row; the knobs are env only. Holds of 3 boots, orders
ABC / CBA. H3/H4 started only at 1-min load < 3.

| Hold (order) | off | on (`PS2X_VU0_RECOMP=1`) | dir (+ `PS2X_VU0_DIRECT=1`) | on/off | dir/off |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1 (off, on, dir) | 31.64 | 32.00 | 33.14 | 1.011 | 1.047 |
| H2 (dir, on, off) — **excluded, outside load** (1-min load 7–9, desktop WebKit/video) | 26.32 | 26.95 | 27.27 | 1.024 | 1.036 |
| H3 (off, on, dir) | 31.75 | 33.12 | 33.60 | 1.043 | 1.058 |
| H4 (dir, on, off) | 31.82 | 33.18 | 33.60 | 1.043 | 1.056 |
| **mean of H1/H3/H4** | **31.74 (0.530×)** | **32.77 (0.547×)** | **33.45 (0.558×)** | **1.032** | **1.054** |

Same-binary noise in VR2 was ~1.5 %. The +5.4 % for dir is above it in every quiet hold. The +3.2 % for
on is above it in H3/H4, and H1's on run is the low outlier. (a)'s trims were not measured on their own:
the off column includes them, and the profile shows the per-start memset/`resetScheduler` samples going
from 36 (c0) to 20 (c3 off).

## Profile (diagnostic: one slot, 15 s from t1850, sequential; `profile-c3-{off,on,dir}-vu0-tree.txt`)

| | c0 (stage 1) | c3 off | c3 on | c3 dir |
| --- | ---: | ---: | ---: | ---: |
| VU0 inclusive, % of GameThread samples | 8.64 % | 8.98 % | **4.71 %** | **4.10 %** |
| generated VU0 pairs (% of VU0 subtree) | — | — | 56.8 % | 75.1 % |
| `commitReadyPipelines` (% of subtree) | 19.0 % | 19.2 % | 31.2 % | 11.4 % |
| interpreter `run`/`execUpper`/`execLower`/decode | 73.8 % | 76.1 % | ≈ 2 % | ≈ 2 % |

## Exact commands

- Build 2 (tests + dump runner): `local/tooling/build/mac_build.sh ~/dev/ssx3-work/VR3/PS2Recomp ~/dev/ssx3-work/VR3/build-clean` (5 m 06 s).
- Dump: `vr3_boot.py dump-c3 bin/runner-c3-dump --stop-tick 1700 --env PS2X_VU0_RECOMP_DUMP=~/dev/ssx3-work/vu0gen-vr3` →
  `[vu0-recomp] dump …/vu0_40829a098c260b4f.cpp ok generation=3` (512 pair functions, 0 reserved pairs).
- Build 3 (the same dir with the image): `cmake -S PS2Recomp -B build-clean -DPS2X_VU0_RECOMP_DIR=~/dev/ssx3-work/vu0gen-vr3 && cmake --build build-clean --target ps2x_tests ps2EntryRunner` (34 s).
- Build 4 (bradflix det): `local/research/VR3/bradflix_build_vr3.sh d52e7f0 vr3-c3-det --det` (VR2's private-export copy
  + VU0 image sync; 12 min). It re-synced bradflix `HS1/vu1gen` to the canonical `vu1gen-ssx3` set (SHA set verified).
- det: `ssx3_boot.py --host bradflix --mode det --backend parallel --runner ~/dev/ssx3-work/HS1/vr3-c3-det/ps2xRuntime/ps2EntryRunner --label vr3-c3-det-<m> --out ~/dev/ssx3-work/VR3/det/c3-<m> --vu1-stats --stack-kb 512 --dump-ticks 1090,1800,2100 --route fr1r1 [--env PS2X_VU0_RECOMP=1 [--env PS2X_VU0_DIRECT=1]]`,
  then `baseline.py compare --key a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand <dir>`.
- Census: `vr3_boot.py census-c3-<m> bin/runner-c3-clean --stop-tick 2450 --env PS2X_VR3_VU0_CENSUS=1 --env PS2X_VU1_RECOMP_STATS=1 [knobs]`.
- Speed: `speed_hold.py H<n> <cands…>` (cwd `~/dev/ssx3-work/VR3`), `speed_table.py run` → `speed-all.txt`.
- Profiles: `vr3_boot.py prof-c3-<m> bin/runner-c3-clean --sample-at 1850 --sample-s 15 [knobs]`, then `vr3_tree.py`.
- Budget: 3 stage-3 builds (2 mini, 1 bradflix) of the 8 approved, 4 of 10 in total. Mini: 1 dump, 3 census, 3
  profile, 12 speed boots in 4 holds. bradflix: 3 det boots. Disk: `VR3` 2.4 GB, `vu0gen-vr3` 272 KB,
  bradflix `HS1/vr3-c3-det` 2.0 GB; the 200 GB check reads 78.8 GB.

## Binaries (`binaries-sha.txt`; runners read twice)

`runner-c3-clean` `ebd1f4c40a0844c21272c4c632c72506a76fa54845baeb389f8b92c1b628a71c` (VU1 canonical + VU0 image);
`runner-c3-dump` `f31e6fdc…`; `tests-c3` `e655eec6…`; `tests-c3v` `37559e2c…`; bradflix det runner
`37bea7bc219179089f978a2c6b4cfdcf0de79315fa81131a4c1c07a7d04b969f`. VU0 image `vu0_40829a098c260b4f.cpp`
`2652966b…` (from `.bin` `21eebd05…`), in `~/dev/ssx3-work/vu0gen-vr3` (game-derived, outside every repo).

## Gaps

- **Android/Gradle wiring for `PS2X_VU0_RECOMP_DIR` is not done** (no `-Pps2xVu0RecompDir`), so a device
  build needs that small step first. The brief stopped before devices.
- The VU0 direct path is exercised through the test override (`setDirectCommitForTest(1)` on a VU0 unit) and
  the env knob in the whole-game runs. No VU0 direct/queued counters were added, so the report cannot say
  what share of VU0 writes committed directly.
- One route and one VU0 image. Another course with another VU0 image falls back to the interpreter (exact).
- (a) was not timed on its own. Its effect is inside the "off" column (profile: per-start memsets 36 → 20
  samples).
- H2 was run and is reported but excluded (outside load). Excluding it does not change the order.
- **Fork moved during stage 3:** `ssx3` is now `a5e5940` (MT1 threaded-unit hooks + BA1 Android -O3, 8
  commits after `d585e5c`). `git merge-tree fork/ssx3 vr3` is clean, and none of those commits touch the
  VU0 execution path (`executeVU0Microprogram`, `ps2_vu1*`). The fold still needs a rebase plus a
  suite/det recheck on the new tip; **nothing here was rebuilt on `a5e5940`.**
