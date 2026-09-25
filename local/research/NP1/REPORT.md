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
