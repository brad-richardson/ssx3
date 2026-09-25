# F5 Part 1 — fold + Mac check (VB1 stage B, HR1 4×/pipelined, LX1 TZ/x86, PF1 post-race, RP1 carve trail)

Worker: muse. Brief: `local/muse/prompts/F5.md` (Part 1 only; no push).
Fork worktree `~/dev/ssx3-work/F5/PS2Recomp`, branch `f5-fold`, from fork `ssx3` **`74e2df2`**.
Fold tip: **`a3efbfe`** (19 picks, no fixups). Tree clean, never pushed.

**Verdict: Part 1 done, all gates green.** Suite 654/654; B1/B2/B3/B4 det-hash identical;
B1 frames viewed (menu, race start, rider + carve trail at t2100); B4 1024×896 sharper, guest-identical;
B5 finished race + 2 min on the live results screen with no missing target; B6 race 0.470×
(1.33× vs F4 B3); **Android `assembleRelease` green, APK `4ff81032…` kept**.

## Fold (oldest first within each group; `git cherry-pick -x`)

| # | Old | New | Subject |
| --- | --- | --- | --- |
| 1 | `9983169` | `eb6d54e` | [VB1] stage B d1: commit scoreboard-ordered writes at issue |
| 2 | `86509dc` | `70ee4fe` | [VB1] stage B d1b: store step always-inline, no escaping stack array |
| 3 | `fda8364` | `cf75607` | [VB1] direct-commit share counters (hash builds, STATS=1) |
| 4 | `b74d81d` | `06f8f87` | [VB1] d2: VR1 g5 (advanceOneCycle inline, commit gate at call sites) |
| 5 | `09ebafd` | `e7bad8b` | [VB1] d3: direct flag writes past older queued flag entries |
| 6 | `9638b3d` | `ee42c1c` | [VB1] d4: no direct VF write a newer write could retire; differential test |
| 7 | `9b71115` | `e4e1351` | [VB1] VF write direct/queued counters (hash builds only) |
| 8 | `cf7c0df` | `fe8280f` | [HR1] paraLLEl SSAA + hi-res scanout knobs; presenter takes larger frames |
| 9 | `fb3dca0` | `e37710c` | [HR1] zero-copy present on macOS (IOSurface into GL), default off |
| 10 | `4825123` | `f6316a6` | [HR1] PRESENT_PIPELINE=1: deliver previous frame, no per-present GPU drain |
| 11 | `4a591d3` | `cfa5bf4` | [HR1] quality line prints effective SSAA rate |
| 12 | `d929048` | `92b70b3` | [HR1] zero-copy present on iOS (IOSurface→CVOpenGLESTextureCache) |
| 13 | `5f32212` | `18b8f90` | [LX1] deterministic OSD timezone + tm_gmtoff host offset + tests |
| 14 | `20377a3` | `efb7f04` | [LX1] x86_64 GCC/Clang: -msse4.1 for runtime SSE4.1 intrinsics |
| 15 | `b4cb476` | `c8b5f54` | [LX1] E53 FP-mode test: MXCSR RC on x86 instead of fegetround |
| 16 | `fc0cc67` | `607271c` | [LX1] VU1 run: save/restore MXCSR via ps2_fpmode, not fenv |
| 17 | `14ea352` | `6bcee0e` | [LX1] GS replay RTZ scope via ps2_fpmode, not fenv |
| 18 | `3c037ab` | `5cab52c` | [PF1] checkpoint unwinds propagate past a callee at its own entry |
| 19 | `9bfd4aa` | `a3efbfe` | [RP1] VU MAX/MINI compare raw bits (carve trail colours) |

Notes:
- **HR1 order:** the brief lists `cf7c0df 4825123 4a591d3 fb3dca0 d929048` but instructs
  oldest-first; true branch chronology is `cf7c0df < fb3dca0 < 4825123 < 4a591d3 < d929048`
  (all 2026-09-25), so `fb3dca0` went second. All five applied (one mechanical conflict, below).
- **PF1:** `3c037ab` applied cleanly **without** `a1eb9b9` (`a1eb9b9` touches only
  `reportMissingFunction` @2260; the fix's hunks are at 23/2527/2680/3667 — no overlap).
  The dev knob was not picked.
- **RP1:** `9bfd4aa` applied cleanly alone; `edce9dd`/`f233fc5` (dev knobs/probes on other
  files) were not needed and were skipped.
- d2's message carries an inherited `(cherry picked from 8cea160…)` line inside its body
  (VB1's d2 was itself a pick of VR1's g5); the F5 trailer is appended after it.

## Conflicts (3, all mechanical; both sides kept)

1. `9983169` (VB1 d1) in `ps2_vu1_core.cpp` `resetScheduler()`: HEAD has F4's
   `m_xgkick.reset()`, VB1 adds `m_directPendingUntil/Stores/Flags` inits plus the old
   `m_xgkick = {}`. Kept VB1's three inits + HEAD's `reset()` (members verified declared).
2. `9638b3d` (VB1 d4) in `ps2_vu1_tests.cpp`: HEAD's F4-2b musttail regression test and VB1's
   differential test both appended a `tc.Run` after the "reserved opcodes" test. Kept both,
   each with its own `});`. No emitter conflict, so the musttail rule never fired; the
   handoff lines (`PS2X_VU1_MUSTTAIL return next(vu, c);`, `:208`) are intact post-fold.
3. `cf7c0df` (HR1 knobs) in `ps2_runtime.cpp` headers: two independent include blocks
   collided (HEAD's `#if __unix__||__APPLE__` pthread.h vs HR1's `#if __APPLE__`
   mach.h + pthread.h on a base with neither). Merged as a union: Apple-only mach.h,
   then unix-or-Apple pthread.h.

## Codegen (F4 regen PROMOTED to canonical)

- `mv codegen-ssx3 codegen-ssx3-pre-f4; cp -R ~/dev/ssx3-work/F4/codegen ~/dev/ssx3-work/codegen-ssx3`.
- Pre-promotion verify: 9,457 / 9,457 files; `register_functions.cpp` `8ea8ed43…` identical
  both sides; `sub_003FE828_0x3fe828.cpp` F4 `89953ba2…` vs canonical `0352db95…` (F4's
  one predicted vf0 line). Post-promotion counts + SHAs re-read identical.
- `local/tooling/ee/sbr-census.py --self-check`: **5/5 PASS** (total 4466, SBR_LT files 623).

## VU1 images (regen: byte-identical, musttail everywhere)

Dump boot over I26-FAST to t2400 (`PS2X_VU1_RECOMP=0` + `PS2X_VU1_RECOMP_DUMP`, det runner
without images, slot 3, bound=target, t2408, 84.8 s) into `~/dev/ssx3-work/F5/vu1gen`;
SHAs in scratch `vu1gen.sha`.
- **7/7 files byte-identical to current `vu1gen-ssx3`** (`diff -rq` empty; SHAs match
  F4's `vu1gen-2.sha` — VB1 stage B and RP1 live in shared helpers the generated pairs
  call, so the emitter text is unchanged). Same 7 hashes; regen was still required to prove it.
- Every handoff carries musttail: all 7 files `plain=2048 must=2048` for
  `return next(vu, c);`, plus 1 `MUSTTAIL return fn(vu, c);` each.

## Builds (one dir `~/dev/ssx3-work/F5/build`, F4 recipe + promoted codegen + F5 VU1)

Release, Homebrew clang, paraLLEl-GS `19d93b2` (F2 worktree reused read-only; HEAD verified,
clean), `GS_SHADOW_PARALLEL=ON`, runtime/aggressive logs OFF, diag taps OFF, TEST ON.
Sequence: clean configure (no VU1 dir) → build → suite → DET reconfigure → dump runner →
dump boot → VU1-dir reconfigure ("VU1 recomp: 7 images") → det runner → DET-off
reconfigure → clean runner + tests. Every configure/build rc=0 (only the usual
duplicate-library link warnings).

| Runner | Det-hash tap | SHA-256 (two reads match) |
| --- | --- | --- |
| `bin/runner-dump` | ON (imageless) | `15aafed31306044bc77074bee42186639d2176ef02aeba6032b4eec11b8dfff5` |
| `bin/runner-det` | ON (`det-hash:v1` 1×) | `119389a74f857e56460ef448e23563d464528db9a819b249049693e563993c38` |
| `bin/runner-clean` | OFF (0×) | `e1e598c2cdcda4bde8213dd083c27e16170360eb3c0960d93908d3d2efcd43df` |

Det runner is 169.6 MB with 14,343 `VU1RecompImage` symbols (images linked in).
Suite from the worktree root: **654/654/0, rc=0** (`suite.log`; F4's 646 + VB1 differential
+ PF1 unwind + RP1 raw-bits + LX1 tz + VU0 VMAX/VMINI — new-test names grepped `[Passed]`).
Runner-dir check `git diff --stat 14b1e5cb f5-fold -- ps2xRuntime/src/runner`: **empty**.

## Boots (FR1-R1, empty mc0, `PS2X_SKIP_MOVIE=1`, deterministic, paraLLEl + `PGS_HIER_BINNING=force`)

Driver: `f5_boot.py` (committed here; RP1's driver repointed at the promoted codegen,
default route fr1r1, wall cap 1800 s, `--env` also in speed mode, `--dump-every` REMOVED —
RP1's `PS2X_FRAME_DUMP_EVERY` was not folded, so the flag is gone rather than silently
ignored). `[gs-path]` on all boots: `hier_rule=hier-if-large … desc=plain … gpu=Apple M5 Pro`.
Prechecks: two SHA reads match on runner/ISO/ELF/both codegen pins every boot.

| Boot | Runner | Sound | Mode | Bound | Wall | Last tick | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 det | det | on | paced | target | 63.5 s | 2405 | 0 |
| B1b det | det | on | paced | target | 64.4 s | 2409 | 0 |
| B2 det | det | off | unpaced | target | 64.0 s | 2405 | 0 |
| B3 det | det | on | paced, 512 KB stack | target | 63.5 s | 2403 | 0 |
| B4 det | det | on | paced, 4×+hi-res+pipelined | target | 62.9 s | 2402 | 0 |
| B5 det | det | on | unpaced, hash/10, to t27300 | target | 839.9 s | 27310 | 0 |
| B6 speed | clean | on | unpaced, pipelined 1×, exclusive | target | 56.4 s | 2401 | 0 |

Det-hash (`gb8_hashdiff.py`): **B1b/B2/B3/B4 all IDENTICAL to B1, ticks 1..2400, 0 missing**
(B1 2485 lines; settle-overrun tails only). Paced+sound, unpaced+sound-off, 512 KB stack,
and 4×+hi-res+pipelined are all guest-identical.

B1 gates: snd tick `cid0=531 dmq=531 done=531` with the exact F3/F4 guest line
(`cycle=11550757345 ticks=3572`) present; coverage at vsync 2400 `targets=0 ids=0 pairs=4`;
VU1 final `runs=1114112 generated_cycles=1038465761 interpreted_cycles=0
generated_share=1.0000` — **100 % generated** (cycle total differs from F4's only because
FR1-R1 ≠ I26-FAST in the tail). B2: no `[snd-output]`, same guest snd cycles as B1
(`cycle=11846455777 ticks=3666`), `cid0=531`, underruns 0 / overflows as designed.
B3: `PS2X_GAME_THREAD_STACK_KB=512` confirmed in env — the musttail chains stay flat.
B4: `[gs:parallel] quality ssaa=4 (asked 4, device max 4) ssaa_textures=0 hires_scanout=1
present_pipeline=1`.

B1b exists because the runtime keeps only the first two success PNGs (`s_successKeep < 2`):
with `--dump-ticks 1090,1800,2100`, the t2100 frame went only to `upload-latest`. B1b
(`--dump-ticks 2098,2100,2102`) captured t2098/t2100 as keeps; its det-hash is identical
to B1, so all three B1 frames are mutually interchangeable.

B4's t2100 frame shows trick **190** where B1b's shows **220** at the same tick: the
pipelined present delivers the previous frame (HR1's documented one frame of display
latency), while det-hash equality proves the guest is unaffected.

## Frames viewed

All 512×448 fbp 112 (B4: 1024×896), no tiles/stripes/corruption.

| Boot | Tick | File | Verdict |
| --- | --- | --- | --- |
| B1 | 1090 | `run/B1/frames/upload-0.png` (`fnv=5136e0ea`) | Select Peak: Peak 1 photo populated, Peak 1 highlighted, 2/3 locked, correct text, full brightness |
| B1 | 1800 | `run/B1/frames/upload-1.png` (`fnv=26b7c5c7`) | Race 2ND/2 00:00:01 0%, EA Radio "Go / Andy Hunter / Exodus" — same card as F4 (same RNG) |
| B1b | 2100 | `run/B1b/frames/upload-1.png` (`fnv=7ad8f18d`) | Race 2ND/2 00:00:06 1%, trick 220, checkpoint beam; **rider solid and lit at centre; white carve groove + spray trailing the board** (RP1 fix visible, no translucent boxes) |
| B4 | 2100 | `run/B4/frames/upload-1.png` (`fnv=3e5b75ed`) | Same scene at 1024×896, one present behind (trick 190, see above); visibly sharper UI/edges, rider + trail intact, no missing effect |
| B5 | 27414 | `run/B5/frames/upload-latest.png` (`fnv=87310445`) | Happiness – Race, Single Event Results: 1 Mac 03:15, 2 Zoe 04:01, "Sorry, you didn't win." — finished race on the live results screen |

## B5 — the finished race (PF1 fix holds on the fold)

FR1-R1, sound on, unpaced (PF1 V1's shape), `PS2X_DET_HASH_EVERY=10` (2,731 hash lines,
under the 4096-line cap), `--no-snap`, wall 1800 s: bound=target, last tick **27310**
= 20063 + 7247 ticks = **2.01 guest-min past FR1's crash tick**, 839.9 s wall.
Coverage `targets=0 ids=0 pairs=4`; zero "missing function/target" lines; `gs_fatal=null`;
det-hash present through tick 27300. The old crash (jump through a float at `0x39e724`,
control: vsync 18823) is gone — 8,487 ticks past it with no unwind misread. The results
(1 Mac 03:15, 2 Zoe 04:01) match PF1's C1/V1 frames exactly: deterministic.

## B6 — speed (pipelined 1× vs F4 B3)

Exclusive (`both`, no retries needed), `runner-clean`, `PS2X_UNPACED=1`, sound on,
`PS2X_PGS_PRESENT_PIPELINE=1` (1×, confirmed in env; no SSAA/HIRES), FR1-R1:
bound=target, 56.4 s wall (F4 B3 67.1 s), last_tick 2401, HUD 36.13 s (F4 36.71),
load 2.76 (F4 B3 4.7 — quieter host, noted), FATAL 0. Raw 5 s `[vsync-rate]` samples
(F4's authoritative method; trace is stale-row noise here too):

Race samples (1834/1972/2111/2252/2401): 27.56/27.60/27.75/28.16/29.80,
**mean 28.17/s = 0.470×**; fresh-row endpoint 1834@36.57→2401@56.36 = 28.65/s agrees
(within 2 %). F4 B3 raw was 21.18/s (0.353×); **F5÷F4 raw-vs-raw = 1.330×**.
Caveats: single runs, no drift cancellation, quieter host this time; FR1-R1 vs F4's
I26-FAST (in-window inputs identical to ~t2309; excluding the 2401 sample: 27.77/s =
0.463×, ratio 1.311×). The gain combines VB1 stage B with the pipelined present (the
per-present `wait_idle()` HR1 removed); no ABBA was run to separate them.

## Android (bytesize `/home/brad/f5` — GREEN)

Staging (F4 recipe + F5 VU1 images + promoted codegen): `PS2Recomp/` = `git archive a3efbfe`
streamed from the mini (352 files both sides — F4's 346 + 6 new: `ee_guest_unwind.h`,
`ps2_present_share.h`, mac `.cpp`, iOS `.mm`, surface `.inc`, tz tests; tar kept as
scratch `fork-a3efbfe.tar`); `codegen-ssx3/` = real copy of the promoted canonical
(9,457 files both sides, `register_functions.cpp` `8ea8ed43…`, changed file `89953ba2…`,
0 `._*` — `COPYFILE_DISABLE=1`); `vu1gen-f5/` = private F5 copy (7 files, all 7 SHAs match
`vu1gen.sha`); `parallel-gs`/`jniLibs` symlinks to `/home/brad/f2/*` (knob present;
`gs_renderer.cpp` SHA `743fdd99…` identical to the mini's 19d93b2). Tree markers:
`ps2xVu1RecompDir` ×2 in gradle, `JOB_POOL_COMPILE` target + source forms in
`ps2xRuntime/CMakeLists.txt`. Pre-staging safety: HR1's zero-copy sources are Apple-gated
in CMake (mac `.cpp` only on APPLE-non-iOS, `.mm` only on iOS — Android compiles neither),
and LX1's `-msse4.1` is guarded by `CMAKE_SYSTEM_PROCESSOR MATCHES x86_64|AMD64` (Android
is ARM — flag cannot leak). `build.sh` (committed here as `build-android.sh`) SHA
`f587b290…` identical local/remote.

Build: **BUILD SUCCESSFUL in 9m 26s**, 48 tasks (35 executed), zero FAILED,
`--max-workers=2` kept, all 7 vu1 `.o` files built from `vu1gen-f5` (arm64-v8a,
RelWithDebInfo). Success log pulled to scratch (`assembleRelease-remote.log`, 31,547 B).
APK `4ff81032a175689be276819381f5ff52710e37101f99289d76b25a5c95609753`,
186,947,144 B (+5.3 MB over F4's — stage B + HR1 growth) — remote ×2 + pulled ×2, all
four match; kept at `~/dev/ssx3-work/F5/odin/app-release.apk`.

WSL note (G5): two detached launches (`&`, then `setsid`) died mid-clone when bytesize's
WSL stopped the Ubuntu distro ~1–2 min after the last `wsl.exe` client disconnected
(`wsl -l -v` = Stopped; PID 1 restarts; Windows host itself stable, up since 9/23). The
green build ran `./build.sh` in the foreground over one held ssh (mini-side backgrounded
session keeps the connection open). Bytesize was otherwise idle throughout (no java/ninja
before launch; one heavy job at a time honored).

## Budgets and gaps

- Builds: 1 full Mac + 4 incremental reconfigures + 1 dump build (same dir) + 1 Android.
  Boots: dump (85 s) + B1/B1b/B2/B3/B4 (~64 s each, one slot) + B5 (840 s, one slot,
  ≤1800 approved) + B6 (56 s, exclusive ≤5 min). Nothing exceeded its cap.
- Scratch `~/dev/ssx3-work/F5`: **724 MB** (≤20 GB brief cap) — kept: worktree (for the
  push), `bin/` (3 runners), `run/` (dump+B1–B6), `vu1gen`+`.sha`, `odin/app-release.apk`,
  configure/build/suite logs, `fork-a3efbfe.tar`, Android logs. Deleted: `build/` (1.8 GB).
- Disk: global mini usage 133.6 → **134.7 GB of 200 GB** (net +1.1 GB: the codegen
  pre-promotion copy; free 112 Gi).
- Never pushed; fork branch `f5-fold` local-only; text in git (`f5_boot.py`,
  `build-android.sh`, this report); runners signalled only by recorded PID (SIGTERM via
  the driver, all reaped); no lease held at close (slot 3 free; slots 1–2 hold live MC1
  claims — not mine, untouched).
- Gaps:
  - G1. Speed is one run per config, no drift cancellation (same as F4 B3); host-load
    caveat above. No Mac 4×-vs-1× speed pair (deferred to the Odin ABBA in Part 2).
  - G2. The B4 one-present lag (trick 190 vs 220) is expected pipelined behavior, but no
    input-latency measurement was taken (HR1 G6 carries).
  - G3. Zero-copy paths (macOS + iOS) folded but default-off and untested on this fold
    (HR1 tested them on its branch).
  - G4. Frame keeps: only the first two success PNGs persist (`s_successKeep < 2`), which
    forced the B1b second boot for the t2100 keep. A `--dump-ticks` user wanting 3 keeps
    always needs two boots.
  - G5. WSL on bytesize stops the Ubuntu distro within ~1–2 min of the last `wsl.exe`
    client disconnecting (observed: `wsl -l -v` = Stopped; PID 1 restarts), killing
    detached (`setsid`/`&`) builds. The F5 APK build ran over a held foreground ssh
    instead (see Android section). Future bytesize builds must hold the ssh open.

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add -b f5-fold ~/dev/ssx3-work/F5/PS2Recomp fork/ssx3  # 74e2df2
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 9983169  # conflict: keep VB1 inits + m_xgkick.reset()
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 86509dc fda8364 b74d81d 09ebafd
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 9638b3d  # conflict: keep both tc.Run blocks
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 9b71115
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x cf7c0df  # conflict: union the include guards
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x fb3dca0 4825123 4a591d3 d929048
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 5f32212 20377a3 b4cb476 fc0cc67 14ea352
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 3c037ab   # clean without a1eb9b9
git -C ~/dev/ssx3-work/F5/PS2Recomp cherry-pick -x 9bfd4aa
mv ~/dev/ssx3-work/codegen-ssx3 ~/dev/ssx3-work/codegen-ssx3-pre-f4; cp -R ~/dev/ssx3-work/F4/codegen ~/dev/ssx3-work/codegen-ssx3
python3 local/tooling/ee/sbr-census.py --self-check  # 5/5
cmake -S PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd PS2Recomp && ../build/ps2xTest/ps2x_tests)  # 654/654
python3 f5_boot.py --mode det --backend parallel --runner bin/runner-dump --label dump --route i26 --stop-tick 2400 --vu1-dump ~/dev/ssx3-work/F5/vu1gen --no-snap
cmake -S PS2Recomp -B build -DPS2X_VU1_RECOMP_DIR=/Users/brad/dev/ssx3-work/F5/vu1gen  # + DET toggles; rebuild each
python3 f5_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400 --vu1-stats --dump-ticks 1090,1800,2100
python3 f5_boot.py ... --label B1b --dump-ticks 2098,2100,2102   # same otherwise
python3 f5_boot.py ... --label B2 --sound off --unpaced --no-snap
python3 f5_boot.py ... --label B3 --stack-kb 512 --no-snap
python3 f5_boot.py ... --label B4 --dump-ticks 2098,2100,2102 --env PS2X_PGS_SSAA=4 --env PS2X_PGS_HIRES_SCANOUT=1 --env PS2X_PGS_PRESENT_PIPELINE=1
python3 f5_boot.py ... --label B5 --stop-tick 27300 --unpaced --hash-every 10 --no-snap --wall 1800
python3 f5_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B6 --stop-tick 2400 --env PS2X_PGS_PRESENT_PIPELINE=1
python3 ../GB8/gb8_hashdiff.py --base run/B1 --cand run/B<N>  # IDENTICAL x4
```
