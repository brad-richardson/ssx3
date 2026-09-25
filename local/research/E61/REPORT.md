# E61 Part 1 — where menu and loading time goes (Mac)

Worker: Muse Code. Brief: `local/muse/prompts/E61.md`. Fork `~/dev/PS2Recomp`
`ssx3` at `f949ff0` (full `f949ff060d9a0c53f3ab47998068b771f20653e3`),
clean worktree, no source changes in Part 1. Canonical codegen
`~/dev/ssx3-work/codegen-ssx3` (`register_functions.cpp` SHA-256
`8ea8ed43…` matches the E55D16 pin; E56-regenerated, post-E58).

## Result in one paragraph

All four profile windows say **H1 (CPU work)**: GameThread is 88–100%
busy, and 84–97% of its time is host emulation — the GS CPU raster
(`WritePixel`/`SampleTexture`/`Submit`, 42–82%) plus the VU1 interpreter
(`commitReadyPipelines`/`calculatePairReadyCycle`, 2–55%). Recompiled
guest code is <1% everywhere; syscalls/RPC ~0%; audio ~0.3% on its own
thread; GameThread waits are only the scheduler's event-pacing cond wait
(0–12%). Loading is not I/O-paced (0% waits in s4). Menus are slow
because every menu frame is software-rasterized on one CPU thread.

## Build and suite (step 1)

- Configure (rc 0, 114 s incl. FetchContent): `cmake -S ~/dev/PS2Recomp
  -B ~/dev/ssx3-work/E61/build -G Ninja -DCMAKE_BUILD_TYPE=Release
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF
  -DPS2X_ENABLE_DIAG_TAPS=OFF` (homebrew clang 23.1.1, same compiler as
  E57's speed build). Receipt: `~/dev/ssx3-work/E61/cmake.log`.
- Build (rc 0, 2 m 24 s, 575/575 targets, after waiting for competing
  clang jobs to drain): `nice -n 10 cmake --build build --target
  ps2x_tests ps2EntryRunner -j8`. Receipt: `build.log`.
- Runner SHA-256, read twice: `a8fdd222f886eebce60e8a33787b6cca5e577ee03f980c6142767ea7788d15ad`
  (both reads match).
- Suite from the fork root (`cd ~/dev/PS2Recomp;
  /Users/brad/dev/ssx3-work/E61/build/ps2xTest/ps2x_tests`): **596/596
  pass, 0 fail** (taps-off count; E58's era was 537, E56's 548 — tests
  added since). Receipt: `~/dev/ssx3-work/E61/suite.log`.

## Speed runs (step 2)

Two boots, I26-FAST, empty cards, exclusive lease (all 4 slots), stop at
observed tick 1750, `PS2X_VSYNC_RATE_LOG=1`, no frame dump. Script:
`local/research/E61/e61_boot.py --mode speed` (self-check 12/12).

| Boot | Sound | Elapsed | Last tick | Bound | Load start → end |
| --- | --- | --- | --- | --- | --- |
| speed-off (pid 62310) | off | 101.6 s | 1750 | target | 14.83 → 14.47 |
| speed-on (pid 63044) | `PS2X_SOUND=1` | 90.8 s | 1756 | target | 14.35 → 10.48 |

Per-phase guest vsyncs/s ÷ 59.94 (each `[vsync-rate]` line assigned by
its tick; title ≤700, menus 700–1600, loading 1600–1714, race >1714):

| Phase | Sound off | Sound on | E58 (pre-sound, quiet host) |
| --- | --- | --- | --- |
| Title/startup | 22.49/s = **0.375×** (n=6, ticks 237–676) | 26.03/s = **0.434×** (n=5, 257–652) | 0.672× |
| Menus | 19.28/s = **0.322×** (n=9, 790–1545) | 20.31/s = **0.339×** (n=9, 768–1568) | 0.541× |
| Loading / Rival | 9.65/s = **0.161×** (n=3, 1626–1690) | 10.89/s = **0.182×** (n=2, 1637–1677) | 0.166× |
| Early race | 5.99/s = **0.100×** (n=2, 1720–1750) | 7.88/s = **0.131×** (n=2, 1716–1756) | 0.129× |

Notes:

- Sound on ≈ sound off (within one-run noise; "on" ran second as host
  load decayed). Audio is not the menu/loading limiter.
- A menu dip at ticks ~850–1050 reproduces in both runs (off:
  14.79/15.57/16.19; on: 16.97/16.15/16.57 per 5 s) — the Select
  Character / Setup Character screens. The profile boot covers it (s2).
- E61 title/menus are lower than E58's, but loading/race match E58, and
  E61's own profile boot (1 slot, quieter host, load ~4–6) ran menus at
  ~24/s — between the two speed runs (19–20/s, load ~10–15) and E58
  (32/s, load ~2–3). Absolute rates are host-load-sensitive; the
  E58 delta is **not** claimed as a code regression (open question;
  needs a quiet-host A/B, out of Part-1 budget).

## Profile boot (step 3)

One boot, 1 slot (slot 2), `PS2X_SOUND=1`, pid 68375, 90.8 s,
bound=target, last tick 1755, load 3.75 → 6.30. Four `sample <pid>`
windows (brief's three plus the s2 dip window; see dip note above),
triggered by interpolated tick estimates
(last rate-line tick + rate × elapsed, polled every 0.5 s), with `ps -M`
snapshots at each sample start/end. `e61_boot.py --mode profile --samples
"700,8,s1;900,10,s2;1150,10,s3;1640,10,s4"`.

Actual tick coverage, by linear interpolation between the 5 s-spaced
rate lines (line #k lands at wall ≈ 5(k+1) s; verified against all four
sample-event records; ±10 ticks):

| Sample | Wall (s) | Est. tick coverage | Screen |
| --- | --- | --- | --- |
| s1, 8 s, 4844 snaps | 22.3–30.9 | ~705–860 | Main Menu → Select Character |
| s2, 10 s, 6153 snaps | 34.4–45.1 | ~920–1087 | Character dip core → Select Peak |
| s3, 10 s, 6121 snaps | 49.2–59.8 | ~1180–1400 | Select Peak / Mode / Event |
| s4, 10 s, 6481 snaps | 69.0–79.6 | ~1610–1682 | Late menus → loading / Rival card |

(`sample` recorded ~600–650 snaps/s, not the nominal 1 kHz; shares are
unaffected.)

### Per-thread CPU% per window (`ps -M`, pre/post)

`ps -M` prints no thread names; the hot R-state row (UTIME tens of
seconds, rest ≤0.4 s) is GameThread by elimination. ps %CPU is a
lifetime-ish average; window CPU% comes from (ΔUTIME+ΔSTIME)/wall:

| Window | GameThread ps %CPU pre → post | GameThread window CPU% | All other threads |
| --- | --- | --- | --- |
| s1 | 81.0 → 84.0 | 68.7% (5.91 s / 8.6 s) | ≤0.8% each |
| s2 | 83.7 → 83.1 | 69.4% (7.43 s / 10.7 s) | ≤0.8% each |
| s3 | 82.8 → 79.9 | 67.5% (7.16 s / 10.6 s) | ≤0.7% each |
| s4 | 100.0 → 95.7 | 81.5% (8.64 s / 10.6 s) | ≤0.7% each |

One thread does all the work. ps window CPU% runs ~20 points below the
sampled busy% below (88–100%); the consistent gap smells like `sample`'s
own suspend/resume perturbation, so sampled *shares* (not absolute CPU%)
are the decision signal. Receipts: `run/prof1/psm-s{1..4}-{pre,post}.txt`.

### GameThread top 15 self symbols per window

Parsed from the `sample` call-graph trees
(`local/research/E61/e61_sample_parse.py`; self = count − children;
100.0% self-accounted in all four GameThread sections). Symbol names
shortened; `std::__function::__func<…>` = the per-pixel PSM dispatch
(see candidate fix 3).

s1 (~705–860, 4844 snaps):

| # | % | Symbol (caller) | Stage |
| --- | --- | --- | --- |
| 1 | 21.18 | `GSCpuBackend::WritePixel` (← Submit) | GS CPU |
| 2 | 19.92 | `GSCpuBackend::SampleTexture` λ (← SampleTexture) | GS CPU |
| 3 | 9.81 | `__psynch_cvwait` (← _pthread_cond_wait; scheduler pacing, see below) | wait |
| 4 | 8.13 | `GSCpuBackend::Submit` | GS CPU |
| 5 | 7.04 | `VU1Interpreter::commitReadyPipelines` | VU1 |
| 6 | 3.45 | `SampleTexture` (← Submit) | GS CPU |
| 7 | 3.39 | `VU1Interpreter::calculatePairReadyCycle` | VU1 |
| 8 | 1.90 | `VU1Interpreter::run` | VU1 |
| 9 | 1.88 | `SampleTexture` (← Submit) | GS CPU |
| 10 | 1.26 | `VU1Interpreter::calculateFmacExactResult` | VU1 |
| 11 | 1.26 | `VU1Interpreter::execUpper` | VU1 |
| 12 | 1.18 | `GSMem::ReadP8H` (← SampleTexture) | GS CPU |
| 13 | 1.11 | `GSCpuBackend::UploadImage` (← processGIFPacket) | GS CPU |
| 14 | 1.03 | `std::function` PSM-read dispatch (← SampleTexture) | GS CPU |
| 15 | 0.97 | `std::function` PSM-read dispatch (← WritePixel) | GS CPU |

s2 (~920–1087, 6153 snaps): SampleTexture λ 19.34, WritePixel 19.11,
Submit 9.56, cvwait 8.69, commitReadyPipelines 8.65,
calculatePairReadyCycle 4.19, SampleTexture 3.28, VU1 run 2.10, execUpper
1.72, SampleTexture 1.59, calculateFmacExactResult 1.46, markPairWrites
1.07, UploadImage 1.01, PSM-read dispatch 0.96, ReadP8H 0.94.

s3 (~1180–1400, 6121 snaps): WritePixel 26.25, SampleTexture λ 23.56,
Submit 12.66, cvwait 11.37, SampleTexture 3.95, SampleTexture 2.06,
UploadImage 1.60, ReadP8H 1.49, PSM-write dispatch 1.27, PSM-read dispatch
1.24, PSM-write dispatch 1.06, WriteCT32 0.96, WritePixel (← vertexKick)
0.95, SampleTexture (← vertexKick) 0.85, ReadCT32 0.85. (No VU1 symbol in
the top 15; VU1 total is 2.2%.)

s4 (~1610–1682, 6481 snaps): commitReadyPipelines 20.68, SampleTexture λ
14.06, WritePixel 10.91, calculatePairReadyCycle 9.88, Submit 6.76, VU1
run 4.81, execUpper 3.58, SampleTexture 2.98, calculateFmacExactResult
2.41, markPairWrites 2.41, execLower 1.88, SampleTexture 1.23, queueVfWrite
1.20, PSM-read dispatch 0.91, getDecodedInstructionPairForPc 0.82. (No
wait symbol anywhere; waits total 0.0%.)

### Self-time grouped by stage (GameThread)

| Stage | s1 | s2 | s3 | s4 |
| --- | --- | --- | --- | --- |
| GIF/GS CPU backend | 65.0% | 62.2% | 81.6% | 41.8% |
| VU1 | 20.0% | 24.9% | 2.2% | 54.7% |
| waits/sleep/locks | 10.0% | 8.9% | 11.7% | 0.0% |
| EE runtime helpers | 3.9% | 2.8% | 3.7% | 2.5% |
| other (libc/memmove/malloc, guest `sub_*` <1%) | 0.8% | 0.8% | 0.6% | 0.5% |
| VIF/DMA | 0.3% | 0.4% | 0.2% | 0.4% |
| syscalls/RPC/CD | 0.0% | 0.0% | 0.1% | 0.0% |
| GameThread busy (non-wait) | 90.0% | 91.1% | 88.3% | 100.0% |

Other threads (all four windows): Main 92–96% waits (EndDrawing→usleep
pacing 72–85%, `latchHostPresentationFrame` GS-mutex contention 1–10% —
*behind* GameThread's raster — plus present/mach_msg), ~2–3% present, ~1%
GS→host frame copy; audio thread 99.6–99.8% semaphore wait with 0.2–0.4%
miniaudio work; NSEvent + GCD pool threads fully idle.

### Hypothesis marks (step 4)

| Window | Mark | Row that shows it |
| --- | --- | --- |
| s1 Main Menu → Select Character | **H1** | GameThread 90.0% busy; WritePixel 21.2% + SampleTexture 19.9% top two |
| s2 character dip | **H1** | GameThread 91.1% busy; GS 62.2% + VU1 24.9% |
| s3 Select Peak/Mode | **H1** | GameThread 88.3% busy; GS 81.6%, top three all GS raster |
| s4 loading / Rival card | **H1** | GameThread 100.0% busy, 0.0% waits; VU1 54.7% + GS 41.8% |

H2 (waiting) rejected as the primary cause in all windows: GameThread's
only waits are the scheduler's event-pacing `m_eventCv.wait_until`
(`EeScheduler.cpp:2720` / `:3045`; chain `EeScheduler::run →
wait_until → _pthread_cond_wait → __psynch_cvwait` verified in s1), and
the main thread's waits are downstream (pacing sleep + the present latch
behind GameThread). H3 (guest idle spin) rejected: recompiled `sub_*`
code is <1% in every window. H4 (loading I/O) rejected: s4 has 0.0%
waits and no CD symbol above noise (the single `readCdSectors` sample in
s1 is 0.02%).

## Named mechanisms and candidate fixes (step 5; no changes made)

1. **GS CPU raster of full-screen menu layers** (62–82% of GameThread in
   s1–s3): `GSCpuBackend::Submit` (`ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp:616`)
   → `WritePixel` (`:826`) / `SampleTexture` (`:1022`). This is the G
   lane's GPU backend work; on the CPU path there is no cheap fix.
2. **VU1 interpreter pipeline bookkeeping** (55% of GameThread in s4
   loading, 20–25% on character screens):
   `VU1Interpreter::commitReadyPipelines`
   (`ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp:759`) and
   `calculatePairReadyCycle` (`:1013`), called per instruction pair from
   `run`. Candidate: skip or memoize the per-pair ready-cycle scan where
   timing fidelity allows (Part 2 to scope).
3. **Per-pixel `std::function` PSM dispatch** (visible in every top-15):
   `ReadVramFunc = std::function<…>`
   (`ps2xRuntime/include/runtime/gs/gs_cpu_backend.h:71`), dispatched per
   pixel in `ReadVramUnlocked`/`WriteVramUnlocked`. Candidate: replace
   with plain function pointers (small, mechanical; a few percent).

## Gaps and caveats

- One run per condition; no repeats. Absolute vsyncs/s are host-load
  sensitive (see E58 note); shares are the robust signal.
- `ps` window CPU% (68–82%) sits ~20 points below sampled busy%
  (88–100%); attributed to `sample` perturbation, unverified.
- s4 covers loading onset + Rival card start (~1610–1682), not the full
  1640–1714 window; race-start ticks >1714 unsampled.
- Profile is sound-on only (sound-off profile not taken; speed delta is
  noise, so profiles are inferred similar).
- Tick coverage is interpolated between 5 s rate lines (±10 ticks), not
  per-vsync ground truth.

## Budgets and receipts

- 1 build, 3 boots (2 speed ≤300 s wall, 1 profile ≤500 s wall), ~1.5 h.
  Scratch `~/dev/ssx3-work/E61/` 1.8 GB (≤10 GB cap).
- Scripts: `local/research/E61/e61_boot.py` (self-check 12/12),
  `local/research/E61/e61_sample_parse.py`.
- Run dirs: `~/dev/ssx3-work/E61/run/{speed-off,speed-on,prof1}/`
  (`boot.log`, `result.json`, `sample-s{1..4}.txt`, `psm-*.txt`).
  Sample/profile blobs stay in scratch; only text excerpts are committed
  here.
- Exact commands: configure/build/suite in "Build and suite" above;
  boots: `python3 local/research/E61/e61_boot.py --mode speed --runner
  ~/dev/ssx3-work/E61/build/ps2xRuntime/ps2EntryRunner --label speed-off`
  (same + `--sound` → speed-on), `... --mode profile --label prof1
  --samples "700,8,s1;900,10,s2;1150,10,s3;1640,10,s4"`;
  parse: `python3 local/research/E61/e61_sample_parse.py <samples>`.

## Appendix: symbol → stage mapping

`e61_sample_parse.py` STAGES, matched against "leaf ← caller" (first
match wins): guest code `sub_0x…`; syscalls/RPC/CD `handleSyscall`,
`dispatchNumericSyscall`, `Syscall`, `SifRpc`, `CdRead`, `cdrom`, `Cdvd`;
VU1 `VU1`, `Vif1`; GIF/GS CPU backend `GSCpuBackend`, `GSMem::`, `GS::`,
`vertexKick`, `writeRegister`; VIF/DMA `processVIF`, `GifArbiter`,
`GifPath`, `VIF`, `DMA`; present/host render `EndDrawing`,
`swapBuffers`, `CGLFlush`, `glSwap`, `MTLCommand`, `IOGPU`, `raylib`,
`glfw`, `AGXMetal`; audio `HALC_`, `ma_`, `miniaudio`, `AudioUnit`;
EE runtime helpers `PS2Runtime::`, `EeScheduler::`, `PS2Memory::`,
`dispatchGuestBranch`; waits `__semwait_signal`, `semaphore_wait`,
`nanosleep`, `usleep`, `__psynch`, `_pthread_mutex`,
`__workq_kernreturn`, `mach_msg`, `cerror`, `kevent`, `poll`, `select`,
`_pthread_cond`. Hand-verified on the top entries: the `mach_msg2_trap`
self on Main sits under GPU-submit chains (counted as waits; moving it
to present would add ≤5% there and not change any mark); `UploadImage ←
processGIFPacket` counted as GS backend.

## Recommended next action

The orchestrator's Part 2 choice: (a) confirm the G-lane GPU backend
removes the menu GS-raster cost (the 62–82% term) and re-profile menus on
it; (b) scope a VU1 fast path for the loading term (`commitReadyPipelines`
/ `calculatePairReadyCycle` hot pair loop, 55% of s4) — loading was
assumed I/O-paced and is not; (c) optionally fold the mechanical
`std::function` → function-pointer PSM dispatch. No grind on EE,
syscall, audio, or CD paths: all are ≤4% combined.
