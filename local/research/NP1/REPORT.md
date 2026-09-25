# NP1 Part 1 — Odin race call-graph profile on the F2 APK (done)

Worker: Muse Code, brief `local/muse/prompts/NP1.md` Part 1 + orchestrator
redirect (profile F2's APK `a3d26b56…`, not F1's). One launch, fp call
graph, symbolized with F2's unstripped `.so`.

Outcome: **fp worked** (11-frame GameThread chains; EeScheduler children ≈
GameThread share). Race frame re-split on the folded build: VU1 hazard
70.1 → **25.7 ms** (E57), VU1 execute 48.2 → **62.8 ms**, libc/kernel 24.9 →
**37.9 ms**, PLT 8.5 → **4.4 ms** (intra-`.so`, `-Bsymbolic` still live).
The review's arbiter-copy half looks dead: GIF-path copies total ≈ 0.4 ms;
the 3.9 % memset is VU1/VU0 execute zeroing, not the arbiter.

History: morning attempt blocked (Odin 15 % net-discharging on USB +
keyguard locked; commit `4a9c3d8c`); then waited for F2A (F2 Part 2 gated
`a3d26b56`, race 0.139/0.137×). Resumed on the F2 APK per the redirect.

## Launch P1 (1/1; spare unused)

APK `a3d26b56c3f45f704fede8e03e019597796b267f751d8949e05d3026c38ad294`
(153,753,160 B; local ×2 + installed `base.apk` ×1, all match; installed
again anyway over Brad's play build). Fork `0ed07c4` + pGS `19d93b2` +
promoted SB1 codegen. Driver `launch.py` (F1 launcher, NP1 paths/lease,
profile step `simpleperf record --call-graph fp`, `--profile-after-tick
2400 --profile-secs 30`).

Pre-launch: lease `LEASE_FREE F2 done`, keyguard `showing=false`
(read-only), AC true, 55 %, thermal 0, app not running, device env
`9fb46f85…` (Brad's), mc0 6/6 pins, mc0-test absent→created empty. Env =
F1 env + NP1 label (`PS2X_SOUND=1`, empty mc0-test, I26-FAST vsync,
`PS2X_VSYNC_RATE_LOG=1`); SHA `0c1fdd43…`.

| Item | Result |
| --- | --- |
| Profile window | tick 2419, 30 s (`perf-P1.data` 32.8 MB, `8abfc63f…`), 137,186 samples, 111.75 G cycles |
| Perturbation | race 7.78/s in-window vs 8.28 clean (6.0 %; N11 dwarf was 9 %) |
| Logcat keys | `[snd-output] stream rate=48000`, `[gs-path] … hier-if-large … desc=buffer … Adreno (TM) 830`, 0 FATAL |
| Threads (end) | GameThread 76.9 %, GsWorker 30.7 % (of their cores) |
| Thermal/clocks | status 3 in-run (launch 0); cpu6/7 4.32 GHz in race; GameThread on 6/7 |
| GPU | 22.0 % mean (n=26, whole run) — still CPU-bound |
| sc01 (viewed) | tick 2100: race 2ND/2 00:00:06 1 %, EA Radio Go/Andy Hunter, RECOVER, crash spray, smooth snow, **no stripes** |
| After | Brad env restored (`9fb46f85…` match), mc0 bad=[], force-stop (pid none), lease `LEASE_FREE NP1 done`, 54 % |

## Symbolization (bytesize `/home/brad/np1/`)

Unstripped F2 `.so` (`cxx/RelWithDebInfo/2d621w4k/…`, SHA `bf0686a4…`,
BuildID `7667c2ab…` = APK merged `.so` BuildID) + N11's `libc.so`/`libhardware.so`.
Host NDK simpleperf. Reports in `reports/`: self comm/sym + sym/dso
(≥0.05 %), threads, dso, flat children (≥0.05 %), stage appendix (all 122
rows); full caller/callee forests + full self in scratch (67 MB).
**0 unresolved rows.**

## Per-stage ms per race frame (N11 model)

GameThread-bound (75.30 % of samples); GameThread ms/frame = clean race
wall W = **120.83 ms** (F2 S1/S2 mean: 337.2/2818 + 341.6/2800; brief's F1
value was 119 ms) → k = 1.60465 ms per 1 % (de-perturbs the 6 % slowdown).
87.04 % covered at ≥0.05 %.

| Stage | Share | ms/frame |
| --- | ---: | ---: |
| VU1 execute | 39.13 % | 62.8 |
| libc/kernel/vdso | 23.61 % | 37.9 |
| VU1 hazard bookkeeping | 15.99 % | 25.7 |
| PLT | 2.73 % | 4.4 |
| GIF/GS packet handling | 1.23 % | 2.0 |
| guest code | 1.18 % | 1.9 |
| paraLLEl CPU submit | 0.83 % | 1.3 |
| VIF1/DMA | 0.55 % | 0.9 |
| other | 0.48 % | 0.8 |
| scheduler/sync/waits | 0.47 % | 0.8 |
| profiler unwind overhead | 0.35 % | 0.6 |
| EE runtime helpers | 0.32 % | 0.5 |
| PS2 runtime other | 0.17 % | 0.3 |
| tail (<0.05 %) | 12.96 % | 20.8 |

Threads (CPU per guest frame): GameThread 120.8 (anchor), GsWorker 34.1,
main 5.0, AAudio 0.3. DSO: our `.so` 69.38 %, kernel 21.43 %, libc 7.25 %,
vdso 0.87 %, Adreno GLES 0.34 %, Turnip 0.26 %. Children: `EeScheduler::run`
74.2 % → `sub_00382760` → `Store32` → `processVIF1Data` → `VU1::run` 41.7 %;
GsWorker `threadMain` 21.2 % → `__ioctl` 16.5 % (GPU submit).

## Top 25 self symbols

| # | % | Thread | Symbol |
| --- | ---: | --- | --- |
| 1 | 10.42 | GT | `VU1Interpreter::run(…)` |
| 2 | 8.98 | GT | `VU1Interpreter::commitReadyPipelines()` |
| 3 | 6.35 | GT | `VU1Interpreter::execUpper(unsigned int)` |
| 4 | 5.25 | GT | `VU1Interpreter::calculatePairReadyCycle(…)` |
| 5 | 3.89 | GT | `__memset_aarch64_nt` |
| 6 | 3.60 | GT | `VU1Interpreter::execLower(…)` |
| 7 | 3.58 | GT | `VU1Interpreter::calculateFmacExactResults(…)` |
| 8 | 3.43 | GT | `VU1Interpreter::normalizeFmacResult(…)` |
| 9 | 2.73 | GT | `VU1Interpreter::calculateFmacProductSticky(…)` |
| 10 | 2.58 | GT | `[kernel.kallsyms][+ffffffe761a8e810]` |
| 11 | 2.57 | GT | `@plt` |
| 12 | 2.48 | GT | `VU1Interpreter::getDecodedInstructionPairForPc(…)` |
| 13 | 2.25 | GW | `[kernel.kallsyms][+ffffffe761a8e860]` |
| 14 | 2.16 | GW | `[kernel.kallsyms][+ffffffe761a8e810]` |
| 15 | 1.76 | GT | `VU1Interpreter::markPairWrites(…)` |
| 16 | 1.39 | GT | `VU1Interpreter::updateFmacFlags(…)` |
| 17 | 1.31 | GW | `[kernel.kallsyms][+ffffffe760a47efc]` |
| 18 | 1.15 | main | `clock_gettime` |
| 19 | 1.15 | GT | `VU1Interpreter::broadcast(…)` |
| 20 | 1.00 | GT | `VU1Interpreter::queueVfWrite(…)` |
| 21 | 0.93 | GW | `[kernel.kallsyms][+ffffffe760cfb750]` |
| 22 | 0.85 | main | `__kernel_clock_gettime` |
| 23 | 0.75 | GW | `[kernel.kallsyms][+ffffffe760a21688]` |
| 24 | 0.73 | GW | `[kernel.kallsyms][+ffffffe760a21680]` |
| 25 | 0.70 | GT | `VU1Interpreter::applyDest(…)` |

(`GT` = GameThread, `GW` = GsWorker. `normalizeOperand`, N11's #6 at 3.46 %,
is gone — E57 inlined it.)

## Callers (`-g callee` sections; `callers.py`; absolute % of all samples)

fp chains end at hand-written leaf asm (no frame maintenance), so each leaf
keeps callers for only ~half its samples (verified: @plt's 112 first-level
edges sum to 49.87 % of its section). Attributed + truncated stated
separately; the truncated half is caller-unknown, not caller-free.

| Target (children / self) | Attributed callers (absolute %) | Truncated |
| --- | --- | --- |
| `@plt` 2.78 / 2.77 (**our `.so`** — intra-`.so` PLT confirmed) | syncCoreSubsystems λ 0.75, VU1 run 0.24, execUpper 0.10, VU0 0.05, applyFmacDestAcc 0.03, dispatchGuestBranch 0.03 | 1.39 |
| `__memset_aarch64_nt` 4.05 / 3.93 (libc) | **VU1 execute 0.89, VU1 run 0.54, VU0 0.52**, Turnip 0.05, submitGifPacket 0.01 | 2.00 |
| `__memcpy_aarch64_nt` 0.67 / 0.56 (libc) | writeIORegister λ 0.08, processGIFPacket 0.06, flush_pending_transfer 0.04, processPendingTransfers 0.04, scudo 0.02, latchHost 0.02, submitGifPacket 0.01, releaseOneMasked 0.01, gif_transfer 0.01 | 0.31 |
| `clock_gettime` 1.17 / 1.16 (libc, main) | EndDrawing 0.34, WaitTime 0.24 | 0.58 |
| `__kernel_clock_gettime` 0.87 / 0.87 (main) | WaitTime 0.43 | 0.43 |
| kernel `…8e810` 4.84 (GT 2.58 + GW 2.16) | kernel-only parents (no kallsyms) | 2.42 |
| kernel `…8e860` 2.26 (GW) | kernel-only parents | 1.13 |
| kernel `…a47efc` 1.31 (GW) | single kernel parent | 0.66 |
| kernel `…cfb750` 0.93 (GW) | single kernel parent | 0.47 |

User-space kernel entries (flat children): `__ioctl` 16.47 % (GsWorker GPU
submit), `syscall` 4.06 %, `notify_one` 3.69 % (GameThread→GsWorker handoff).

**Part 2 read:** (a) `-Bsymbolic`/hidden visibility still targets a real
4.4 ms of intra-`.so` PLT on the VU1 hot path. (b) The arbiter
`resize`+`memcpy` half looks dead: all GIF-path copies (submit, release,
processGIFPacket, writeIORegister λ, flush, gif_transfer, latch) total
≈ 0.23 % ≈ 0.4 ms; the memset is VU1/VU0 execute zeroing (≈ 2.0 % attributed
≈ 3.1 ms + a 2.0 % truncated half), an E-lane question about what
`VU1Interpreter::execute` clears per run — not the arbiter.

## N11 S2 row-by-row (share % / ms; N11 k=1.7122, NP1 k=1.60465)

| Stage | N11 S2 | NP1 P1 | Δms | Read |
| --- | --- | --- | ---: | --- |
| VU1 hazard | 40.92 / 70.1 | 15.99 / 25.7 | −44.4 | E57 gate+inlining |
| VU1 execute | 28.17 / 48.2 | 39.13 / 62.8 | +14.6 | E57 moved self into run/execUpper/execLower; possibly more VU1 work/frame on the fold (gap) |
| libc/kernel | 14.53 / 24.9 | 23.61 / 37.9 | +13.0 | RR1 prims → GsWorker submit/ioctl; memset 1.87→3.89 % |
| PLT | 4.94 / 8.5 | 2.73 / 4.4 | −4.1 | fewer out-of-line calls after E57 inlining |
| GIF/GS | 0.80 / 1.4 | 1.23 / 2.0 | +0.6 | more packets (RR1) |
| guest | 0.38 / 0.7 | 1.18 / 1.9 | +1.2 | SB1 64-bit codegen heavier |
| pGS submit | 0.36 / 0.6 | 0.83 / 1.3 | +0.7 | more prims |
| VIF1/DMA | 0.30 / 0.5 | 0.55 / 0.9 | +0.4 | |
| sched/waits | 0.60 / 1.0 | 0.47 / 0.8 | −0.2 | |
| EE helpers | 0.53 / 0.9 | 0.32 / 0.5 | −0.4 | advanceEeTimers 0.41→0.10 % |
| other | 0.30 / 0.5 | 0.48 / 0.8 | +0.3 | |
| unwind | 0.14 / 0.2 | 0.35 / 0.6 | +0.4 | fp still cheap |
| PS2 other | 0.14 / 0.2 | 0.17 / 0.3 | +0.1 | |
| tail | 7.89 / 13.5 | 12.96 / 20.8 | +7.3 | more diffuse (F2 has more threads/symbols) |
| **GameThread W** | **84.92 / 145.4** | **75.30 / 120.8** | **−24.6** | **1.20× — matches F1's 1.19× pair** |
| GsWorker | 12.13 / 20.8 | 21.24 / 34.1 | +13.3 | RR1 prims + ST1 scanout submit |

Top-symbol moves: commitReadyPipelines 24.96→8.98 %, calcPairReady
12.73→5.25 %, markPairWrites 3.23→1.76 %, run 7.34→10.42 %,
execUpper 3.80→6.35 %, execLower 2.02→3.60 %, normalizeOperand 3.46→gone
(inlined), ExactResults 2.44→3.58 %, memset 1.87→3.89 %, PLT 4.84→2.73 %,
clock 0.99→1.15 %.

## fp-vs-dwarf verdict

**fp.** No spare launch needed: 11-frame GameThread chains
(__start→GameThread→EeScheduler→guest→VIF1→VU1→execUpper→applyFmacDestAcc),
EeScheduler children 74.15 % ≈ GameThread 75.30 %, 0 unresolved rows,
6 % perturbation (vs 9 % dwarf). Cost: leaf-asm samples (PLT stubs,
`_aarch64_nt` libc, kernel entries) lose their callers ~50 % of the time;
mid-stack attribution is unaffected. Dwarf only if a future brief needs
the truncated leaf halves.

## Budgets and gaps

1/1 builds (none — F2 APK reused), 1/1 launches (P1 ~197 s wall; spare
unused), ~2.5 h wall incl. the morning discharge block and the F2A wait
(brief box was 1 h of lane time). Scratch `~/dev/ssx3-work/NP1/` 67 MB
(≤ 5 GB); NP1 git dir text-only; bytesize `/home/brad/np1/` holds
`symdir/` (F2 `.so`, ~1 GB) + `prof/` (data + full reports).
Gaps: VU1 execute-ms growth (+14.6) not split between E57 self-motion and
more work/frame (needs per-program VU1 cycle counts Mac-side); truncated
leaf halves caller-unknown; one 30 s window (no drift cancellation);
kernel rows address-only (no kallsyms); SND stage silent (<0.05 %/row).

## Exact commands

```sh
adb -s 622c49b1 install -r ~/dev/ssx3-work/F2/odin/app-release.apk  # a3d26b56
python3 local/research/NP1/launch.py --label P1 --wall 600 --profile-after-tick 2400 --profile-secs 30
python3 local/research/NP1/phases.py local/research/NP1/logs/P1
# bytesize: cp F2 unstripped .so to /home/brad/np1/symdir (BuildID 7667c2ab match)
# bytesize: simpleperf report --symdir ... --sort comm,symbol|symbol,dso|comm|dso [--percent-limit 0.05]
# bytesize: simpleperf report -g callee --full-callgraph --sort symbol [--percent-limit 0.01]
python3 local/research/NP1/buckets.py local/research/NP1/reports/p1-self-comm-sym.txt --appendix
python3 local/research/NP1/callers.py ~/dev/ssx3-work/NP1/p1-callee-full.txt '<regex>...'
```

## Orchestrator gate, Part 1 (2026-09-25)

**Pass.** Odin race frame on F2 (120.8 ms, GameThread-bound): VU1 execute 62.8 + hazard 25.7 ms
(73 %; hazard was 70 ms before E57), libc/kernel 37.9, PLT 4.4 ms (intra-`.so`), guest code 1.9.
The arbiter copies are dead (≈ 0.4 ms). Real targets: `__memset_aarch64_nt` 3.9 % called from
VU1/VU0 execute (≈ 4.7 ms, zeroing per execute), `@plt` 4.4 ms, and GameThread→GsWorker handoff
(`notify_one` 3.7 %, `syscall` 4.1 %). Part 2 released with three bounded changes (below). VU1
execute (63 ms) goes to a VU1 static recompile lane (VR1).

## Part 2 — the cheap host fixes (done, below estimate)

Worker: Muse Code, brief `local/muse/prompts/NP1.md` "Part 2 as released".
Fork branch `np1-link` from `ssx3` `0ed07c4` (local only, no push), three
commits, E57 bit-exact gate on the Mac, one APK, ABBA vs F2.

Outcome: **all three fixes verified in the binary and bit-exact, but the
Odin pair measures only +1.0 %** (8.105 → 8.190 race vsyncs/s ABBA), below
the ~8–11 % the Part 1 shares implied. GameThread CPU/frame fell 3.8 %
ABBA (real reduction), while heavy non-linear heat soak (A1→A2 −7.3 %,
loading phase −13 %) contaminates the wall pair. Recommendation in Gaps.

### Commits (`np1-link` tip `125c9e5`; runner-dir diff empty; no push)

| # | SHA | Change (file) | Before share (Part 1) | After evidence |
| --- | --- | --- | --- | --- |
| 1 | `e5654f3` | `-Wl,-Bsymbolic` on the Android `.so` link (`ps2xRuntime/CMakeLists.txt`, `PS2X_IS_ANDROID` branch) | `@plt` 2.73 % self, intra-`.so`, VU1 hot path | `.so` JUMP_SLOT 3222 → 400 (−88 %; 400 = libc/external); GLOB_DAT 1250 → 5 |
| 2 | `7caf516` | Scalar-only `XgkickPipeline::reset()` (`ps2_vu1.h` + 2 sites in `ps2_vu1_core.cpp`): per-execute `= {}` cleared 64 KiB (94 % of resetScheduler's ~70 KiB); all `packet[]` reads are this-transfer data, no tap covers the buffer | `__memset` 3.93 % from execute/run/VU0 | Mac `sample` top-samples 253 → 40 (−84 %); `startXgkick→bzero` gone |
| 3 | `125c9e5` | `GsWorker::begin/endBatch` + RAII guard on all 4 arbiter `drain()` sites (`gs_worker.h/.cpp`, `gs_frontend.h`, `ps2_memory.cpp`): one wakeup per drain; order/bounds/backpressure unchanged; no batch spans an RPC wait (drain extent has none; `privWrite` async) | `enqueue` 4.02 % (3.58 via `noteGifPath`), `notify_one` 3.69 % | In build (`begin/endBatch` symbols); scenes identical; share unprofiled (gap) |

### Mac gate (E57 `check.py`; base `0ed07c4` vs cand `125c9e5`)

Builds (F1 recipe, Homebrew clang, canonical codegen `8ea8ed43…`, pGS
`19d93b2` — base `0ed07c4` needs the GB9 knob header, canonical `963cb57`
fails): suite **612/612 both**; det runners (`det-hash:v1` in strings).

| Pair | suite | det-hash 1..2400 | GS digest | Verdict |
| --- | --- | --- | --- | --- |
| Direct (default CPU backend) | PASS | 2402/2401 lines, first_diff=None | 1,906,204 recs, SHA equal | **BIT-EXACT** |
| Queued (`PS2X_GS_QUEUE=1`, exercises commit 3) | PASS | 2402/2400 lines, first_diff=None | FAIL @rec 1685 | see control |
| Control base-vs-base queued | PASS | PASS, first_diff=None | FAIL @rec 4760 | **queued capture nondeterministic** |

The queued gs FAIL is a capture artifact (worker-side tick stamping;
base-vs-base fails at a different record), not a behavior change:
det-hash passes in all three pairs and direct gs is byte-identical.
Commit 3's functional risk (hang/missed wakeup) is covered by the queued
det-hash PASS over the full route.

### APK (`836d4bf8…`, bytesize `/home/brad/np1b`, F2 recipe)

Staging: `np1-link` archive from the mini (334 files, runner stub
`cf62c485…`, Bsymbolic present); codegen/parallel-gs/jniLibs `cp -a` from
`/home/brad/f2` and re-verified (9457 files, `8ea8ed43…`, 623 SBR refs,
24314 files, `1b49d27c…`/`717812c3…`); `build.sh` SHA `6e70beda…` both
sides. **BUILD SUCCESSFUL in 6m 5s**, 48 tasks executed. APK
`836d4bf8d5cccbd73ece6ba70bfe495d4f811e7e59b3bed974478c876865543e`,
153,605,704 B (remote ×2, pulled ×2, all match; −147,456 B vs F2's).

### ABBA vs F2 `a3d26b56` (4/4 clean; reinstall + SHA check before each)

Env = Part 1 NP1 env, sound on, empty mc0-test, I26-FAST, `--stop-tick
4500`. Pre-launch: lease free, keyguard false (read-only, never toggled),
thermal ≤ 2 (A1 0, B1 0 after 90 s wait from 3, B2 2 after 90 s, A2 1
after 120 s), battery 50→39 % on AC (≥ 20 throughout), app stopped,
Brad env + mc0 verified before/after every run, force-stop after.

| Run | APK | Race window | Race /s (×) | Battery | In-run soak |
| --- | --- | --- | --- | --- | --- |
| A1 | F2 | 1714→4527, 334.4 s | **8.41 (0.140×)** | 50→48 % | status 3; cpu7 4.32 in 26/36 |
| B1 | NP1B | 1714→4559, 337.8 s | **8.42 (0.141×)** | 47→45 % | 3/4/5; 4.32 in 24/36 |
| B2 | NP1B | 1714→4549, 356.4 s | **7.96 (0.133×)** | 45→42 % | 4/5; 4.32 in 8/38, 2.25 in 10/38 |
| A2 | F2 | 1714→4521, 359.6 s | **7.80 (0.130×)** | 42→39 % | status 5; 4.32 in 22/38 |

0 FATAL all runs; `[snd-output] 48000`, `[gs-path] … hier-if-large …
Adreno 830` all runs; queued path live (`gs:queue` in all logcats).
A mean 8.105, B mean 8.190 → **B÷A = 1.010 (+1.0 %)**. Adjacent pairs:
B1÷A1 +0.1 %, B2÷A2 +2.1 %. GameThread CPU/frame (TIME+ ÷ ticks):
61.5 / 60.1 / 65.3 / 68.8 ms → ABBA **−3.8 %** (real CPU reduction).

Screencaps: viewed B1 sc04 (00:00:47 2ND/2 5 % 42 MPH dark gully) and A1
sc04 (same gully, 44 MPH, Δ32 ticks) — same scene, no stripes, no
regression. All 16 PNGs pulled with SHAs; remaining 14 unviewed.

Play build: reinstalled F2 `a3d26b56` (`Success`, `base.apk` SHA match) +
`deploy-odin.sh` (env `9fb46f85…`, 6/6 saves OK), no launch. Device left:
lease free, app stopped, `/data/local/tmp/np1` + `mc0-test` removed, 39 %.

### Reading the +1.0 %

The commits demonstrably remove GameThread CPU (−3.8 % CPU/frame ABBA;
PLT slots −88 %; Mac zero-fill −84 %), but the wall pair under-reads for
two stated reasons: (1) severe non-linear heat soak (A1→A2 −7.3 %;
loading, which is CD/IO-bound, falls −13 % A1→A2 — pure heat), which the
ABBA linear correction can't fully cancel (B2/A2 heavily throttled);
(2) the profile-share→ms model likely overstates removable wall time
(e.g. 1-packet drains halve rather than eliminate the notify cost).
The cleanest pair (A1/B1, least soaked) shows +0.1 % wall with −2.3 %
CPU — heat masking a small real gain. A same-temperature re-pair (longer
cooldowns) or a B-APK profile would close the gap; both are orchestrator
calls (brief scope was 4 runs, done, no 5th run taken).

### Budgets and gaps

Fork commits 3/3, Mac builds 4 (base+cand × speed+det), Mac boots 7
(2 direct hash + 3 queued hash + 2 profile), 1/1 APK builds, 4/4 Odin
launches (~407–436 s wall each), ~3 h wall (brief box 2 h; overrun is
queue-mode gate + control and the 4-run soak waits). Scratch
`~/dev/ssx3-work/NP1/` 768 MB (≤ 5 GB; peaked 6.1 GB with two build dirs
+ a 2.5 GB capture, reclaimed same session). Gaps: per-commit Odin
after-shares unprofiled (combined ABBA only); commit 3's wakeup
reduction unmeasured (mechanism live, scenes identical); 14/16 caps
unviewed; heat, not code, dominates the pair spread.

### Exact commands (Part 2)

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/NP1/PS2Recomp -b np1-link fork/ssx3  # 0ed07c4
# commit 1: ps2xRuntime/CMakeLists.txt (Android branch += -Wl,-Bsymbolic)
# commit 2: XgkickPipeline::reset() + 2 sites (ps2_vu1.h, ps2_vu1_core.cpp)
# commit 3: GsWorker begin/endBatch + 4 drain guards (gs_worker.h/.cpp, gs_frontend.h, ps2_memory.cpp)
cmake -S PS2Recomp-{base,} -B build-{base,cand} ... (F1 flags, pGS 19d93b2)  # PS2Recomp-base @ 0ed07c4
(cd PS2Recomp{,-base} && ../build-{cand,base}/ps2xTest/ps2x_tests)  # 612/612 both
cmake -S ... -B ... -DPS2X_ENABLE_DET_HASH_TAP=ON; cmake --build ... --target ps2EntryRunner  # x2
python3 local/research/NP1/np1_boot.py --mode hash --runner bin/runner-{base,cand}-hash --label h-{base,cand}
python3 local/research/NP1/np1_boot.py --mode hash --queue --runner bin/runner-base-hash --label hq-base{,2}
python3 local/research/NP1/np1_boot.py --mode hash --queue --runner bin/runner-cand-hash --label hq-cand
python3 local/research/E57/check.py --base .../h-base --cand .../h-cand --base-suite ... --cand-suite ...
python3 local/research/NP1/np1_boot.py --mode profile --runner bin/runner-{base,cand}-speed --label p-{base,cand}
git -C ~/dev/PS2Recomp archive np1-link | ssh bytesize 'wsl ... tar -x -C /home/brad/np1b/PS2Recomp'
ssh bytesize 'wsl ... bash /home/brad/np1b/build.sh'  # SUCCESS 6m05s
adb -s 622c49b1 install -r <apk>  # x5 (A1 F2, B1/B2 NP1B, A2 F2, play F2)
python3 local/research/NP1/launch.py --label {A1,B1,B2,A2} --wall 600 --stop-tick 4500
python3 local/research/NP1/phases.py local/research/NP1/logs/{A1,B1,B2,A2}
bash local/research/I31/deploy-odin.sh  # play restore, no launch
```

## Orchestrator gate, Part 2 (2026-09-25)

**Pass (small win).** Three bit-exact changes: `-Wl,-Bsymbolic` (PLT jump slots 3,222 → 400), a
scalar-only XGKICK pipeline reset (the 64 KiB per-execute memset), one GsWorker wakeup per drain.
GameThread CPU per frame −3.8 % ABBA; the wall pair shows +1.0 % because heat soak dominates
(A1 → A2 −7.3 % on the same APK). Fold `e5654f3 7caf516 125c9e5` in F4. Measurement lesson: Odin
pairs need a longer cool-down (thermal ≤ 1 and a fixed wait) or more alternations; noted in the runbook.
The queued-GS capture isn't deterministic even base vs base; det-hash is the gate there.
