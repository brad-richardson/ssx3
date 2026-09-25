# F4 Part 1 — fold VR1 + NP1 + TC1 onto fork `ssx3`, Mac check, Android blocked on OOM

Worker: Muse Code, brief `local/muse/prompts/F4.md` Part 1 only. No push
(orchestrator gates and pushes). **Stopped per the first-failure rule:**
the Android `assembleRelease` was OOM-killed on bytesize (environmental,
not a code defect); B3 and the APK are not done. Everything Mac-side is
green and the fold is guest-bit-exact vs F3.

**Result: fold clean, Mac green, guest-bit-exact vs F3, Android blocked.**
All 9 cherry-picks applied (one mechanical test-registration conflict,
both sides kept); suite 646/646; the F4 regen differs from canonical in
exactly the predicted one line and is NOT promoted; B1 races with sound
on (cid0 531, coverage 0/0/4, 100 % of VU1 cycles in generated code,
rider solid, alpha 255 everywhere); B2 (sound off + unpaced) is
det-hash identical to B1 on all 2,429 common ticks; F4 B1 is det-hash
identical to F3 B4 on all 2,429 common ticks. The bytesize APK build
compiled every game object and runtime file, then SIGKILLed 3 of the 7
giant vu1_*.cpp TUs in parallel on the 9.7 GB box (`Killed`, no compile
errors). Saved the error, stopped, handing back.

## Fold (worktree `~/dev/ssx3-work/F4/PS2Recomp`, branch `f4-fold` from `ec2dbf1`)

`git cherry-pick -x` in brief order. VR1's 5 and NP1's 3 applied clean
(NP1's `ps2_vu1.h` overlap auto-merged; verified both sides present:
NP1's `XgkickPipeline::reset()` at line 265 and VR1 g2's
`m_entryOldVi/m_entryOldVf` members + inline `microAddressMask`).
TC1's pick conflicted mechanically in the two test-registration files
(F3 had added `ps2_vsync_pacer_tests` at the same spot): kept both
registrations in all 3 hunks. Then one new commit of mine (R ctor + test).

| # | Source | New SHA | Subject |
| --- | --- | --- | --- |
| 1 | `00381ff` | `7b1c914d85220852b8f41e91084be59101ba7ffd` | [VR1] VU1 static recompilation stage A |
| 2 | `71fda22` | `40a13ee48c0286dab6e6f76454212ab30bb5bd31` | [VR1] pair step: entry-trace in members, microAddressMask inline |
| 3 | `1b09a49` | `a516946606ecaaf38087d5a520e92fd7f538c44f` | [VR1] FMAC result helpers always-inline |
| 4 | `1f51e48` | `e976045170bbfecda38f6c085c43e599935055f7` | [VR1] chained pairs via musttail |
| 5 | `6c2de6f` | `3aa611f8830f9743302d982f658c8bc80247c2bd` | [VR1] Android `-Pps2xVu1RecompDir` |
| 6 | `e5654f3` | `670453a00f2cf01e4610b5d2d3fd938f2be1222b` | [NP1] Android `-Wl,-Bsymbolic` |
| 7 | `7caf516` | `f7f50491d933891d36ddad21ff018be9751d345a` | [NP1] scalar-only XGKICK reset |
| 8 | `125c9e5` | `30d4f0b291c5896bba907d481cee5313b66ffb0c` | [NP1] one GsWorker wakeup per drain |
| 9 | `e29e4975` | `0938e9f4baa3290875d58e8bb65578e5f5eabd4b` | [TC1] emitter skips writes to VU0 vf0 |
| 10 | new | `46b0c8d6abb223c94012b342817315db33a9b791` | [F4] VU0 R = 1.0-bits in every EE context |

Not picked: VR1 g5 `8cea160` per the brief. Tip:
`46b0c8d6abb223c94012b342817315db33a9b791`. `games/` untouched.
Runner-dir guard `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`:
empty. `git diff --check ec2dbf1 HEAD`: clean. Total: 24 files,
+2663/−1905. Note: TC1's `e29e4975` lived only in the TC1 clone (separate
`.git`, not a worktree of `~/dev/PS2Recomp`), so it was fetched into the
main clone over a local path before the pick (read-only on the source,
no branches created, nothing pushed).

The R commit mirrors RD1's precedent exactly: the same bits main sets
(`ps2_runtime.cpp:878`) move into `R5900Context()` after the `vu0_q`
line, main's patch line stays (as RD1 left vf0's), and the unit test
covers a default-constructed context plus a `StartThread`'d thread
(SSE2-only intrinsics, `uint32_t` bit compare).

## Codegen (regen, NOT promoted)

- TOML: folded tree's tracked `games/ssx3/ssx3.toml` with only the 3 SB1
  paths repointed (`ssx3-f4.toml`; diff vs tracked = the 3 path lines;
  folded TOML otherwise identical to F2's; CSV copy SHA `7c827add…b9ba`
  matches F2's pin).
- Tool build (SB1 recipe flags): configure rc=0, build rc=0
  (`cmake-recomp.log`, `build-recomp.log`). `ps2_recomp`
  `b6c7a1826b55c0df8f299cfaf608b829ab69c515324a125df4ef852c710f77e0`.
- Regen: rc=0, 9,457 files (`regen.log`; only the usual JR/JALR fallback
  warnings).
- **`diff -rq canonical F4/codegen`: exactly 1 file differs**,
  `sub_003FE828_0x3fe828.cpp` (`codegen-diff.txt`), the single predicted
  line (TC1's `lqc2 $vf0` restore at `:405`):
  `- ctx->vu0_vf[0] = _mm_castsi128_ps(READ128(ADD32(GPR_U32(ctx, 16), 0)));`
  `+ (void)READ128(ADD32(GPR_U32(ctx, 16), 0)); // LQC2 to vf0 ignored …`
- `register_functions.cpp` SHA `8ea8ed43…` identical both sides; file
  counts 9,457 / 9,457; SBR files 623 / 623. The changed file's F4 SHA
  is `89953ba2…` (canonical `0352db95…`).
- NOT promoted to canonical per the brief. All F4 builds use
  `PS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/F4/codegen`; the boot driver
  pins the changed file too (the `register_functions.cpp` pin alone
  cannot tell F4 codegen from canonical — F2's G5 lesson in reverse).

## VU1 generated sources

`~/dev/ssx3-work/vu1gen-ssx3`, 7 files, `diff -rq` clean vs VR1's
`gen-v2` (the orchestrator's promotion verified); SHAs in scratch
`vu1gen.sha`. Passed via `-DPS2X_VU1_RECOMP_DIR=` (configure confirms
"VU1 recomp: 7 images"). Game-derived, never in git.

## Builds (one dir `~/dev/ssx3-work/F4/build`, F3 recipe + VU1 dir + F4 codegen)

Release, Homebrew clang, paraLLEl-GS `19d93b2` (reused F2's worktree
read-only; still clean), `GS_SHADOW_PARALLEL=ON`, runtime/aggressive
logs OFF, diag taps OFF. Det runner = incremental reconfigure
(`DET_HASH_TAP=ON`) after copying the clean runner out. Configure +
both builds rc=0 (only the usual duplicate-library link warning; the
one `error` grep hit is the `dwarf_error.c` filename).

| Runner | Det-hash tap | SHA-256 (staged read; boot prechecks re-read ×2) |
| --- | --- | --- |
| `bin/runner-clean` | OFF (`det-hash:v1` 0× in strings) | `7e31b6d2fc3cbc6cda374c4e9b2cc351feaccb9c6d4edac98721935887b9b888` |
| `bin/runner-det` | ON (string present) | `c190da575e74944ff1fa25cbd8292784a3c312af0b984f59ed6b87f03137df6c` |

Clean runner is 162.7 MB (VR1: 135.1 → 162.7 MB with the 7 images) and
carries 14,343 `VU1RecompImage` symbols — the images linked in.

Suite from the worktree root: **646/646/0, rc=0** (`suite.log`; 642 F3
+ 3 TC1 + 1 F4 = 646 exactly). All three TC1 tests and the F4 R test
show `[Passed]`; the RD1 test still passes.

## Boots (I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, deterministic, paraLLEl + `PGS_HIER_BINNING=force`)

Driver: `f4_boot.py` (committed here; F3 driver + F4 codegen pins incl.
the changed file + `--vu1-stats`). `[gs-path]` on both boots:
`hier_rule=hier-if-large … desc=plain … gpu=Apple M5 Pro`. Boot-driver
prechecks: two SHA reads match on runner/ISO/ELF/both codegen pins
every boot; ISO `3c2f8eb1…`, ELF `1b49d05c…` pinned. Mini load was
21→47 during these boots (other lanes busy) — wall times are
diagnostic-only, not speed numbers.

| Boot | Runner | Sound | Paced | Bound | Wall | Last tick | HUD wall | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B1 det | det | on | yes | target | 120.0 s | 2403 | 42.17 s | 0 |
| B2 det | det | off | no (`--unpaced`) | target | 121.0 s | 2400 | 49.63 s | 0 |

B1: `[snd-output] stream rate=48000` live; snd tick line `cid0=531
dmq=531 done=531` with guest cycle counts identical to F3's
(`cycle=11550757345 ticks=3572`); coverage at vsync 2400 =
`targets=0`, `ids=0`, `pairs=4` (the E56 four SIDs). VU1 stats (final):
`runs=1064960 generated_cycles=980203317 interpreted_cycles=0
generated_share=1.0000` — **100 % of VU1 cycles in generated code**.
B2: no `[snd-output]` (host stream off, as designed); same guest snd
cycles as B1; underruns 0 / overflows as designed (sound-off shape
matches F2/F3 B2); `cid0=531`, coverage 0/0/4.

**B1 vs B2 det-hash: 2,429/2,429 common ticks byte-identical, all
fields, 0 differing payloads** (glue-immune regex extract; B1 ticks
1..2429, B2 1..2430 — settle overrun only). Paced+sound-on vs
unpaced+sound-off identical: the FP1 + AU10 properties both hold on
the fold.

**F4 B1 vs F3 B4 (RD1 tip) det-hash: 2,429/2,429 common ticks
byte-identical, 0 differing payloads** (F3 B4 ticks 1..2441 — settle
overrun only). The whole fold (generated VU1, NP1 ×3, vf0 regen, R
ctor) is guest-invisible on this route, as VR1/NP1/TC1 each predicted.

## Frames (B1 snapshotter picks by exact present tick from the sidecar)

All 512×448 fbp 112, no tiles/stripes/corruption. Alpha check
(`/tmp/f3_alpha.py`, all three): **alpha = 255 on 100.0% of pixels**
(229,376/229,376), even-row mean 255.0, odd-row mean 255.0 — DK1 holds.

| Boot | Present tick | File (`run/<B>/frames/snap/`) | Viewed verdict |
| --- | --- | --- | --- |
| B1 | 1096 (sidecar `fnv=5078af61`) | `snap-001097t-0022.85s.png` | Select Peak: Peak 1 mountain photo populated, Peak 1 highlighted, 2/3 locked, correct text, full brightness |
| B1 | 1804 (`fnv=1d5fe968`) | `snap-001800t-0052.28s.png` | Race 2ND/2 00:00:01 0%: gate, lit snow, pines, mountains, EA Radio "Go / Andy Hunter / Exodus" — same card as F3 B1 (same RNG state) |
| B1 | 2102 (`fnv=a3729012`) | `snap-002098t-0084.77s.png` | Race 2ND/2 00:00:06 1%, trick 250, checkpoint beam; **rider solid and lit at screen centre** (dark outfit, arms up, board + shadow) |

## Android (bytesize `/home/brad/f4` — BLOCKED, first failure)

Staging (F3 recipe + `-Pps2xVu1RecompDir=/home/brad/f4/vu1gen-ssx3`):
`PS2Recomp/` = `git archive 46b0c8d` streamed from the mini (346 files
both sides; tar kept as `fork-46b0c8d.tar`); `codegen-ssx3/` = real
copy of the F4 codegen (9,457 files both sides,
`register_functions.cpp` `8ea8ed43…` ×2, changed file `89953ba2…`);
`vu1gen-ssx3/` = private copy (7 files, all 7 SHAs match `vu1gen.sha`);
`parallel-gs`/`jniLibs` symlinks to `/home/brad/f2/*` (knob present).
Tree markers: runner stub `cf62c485…` (1 upstream file), VR1
`ps2_vu1_step_impl.h` + `ps2_vu1_recomp.cpp`, TC1 test file, `Bsymbolic`
×1, `beginBatch` ×2, `ps2xVu1RecompDir` ×2, `0x3F800000` ×1 in
`ps2_runtime.h`. `build.sh` (committed here) SHA `9e89c9c7…` identical
local/remote. Two staging mistakes of mine, both fixed before the
build: the codegen tar landed as `codegen` instead of `codegen-ssx3`
(renamed), and macOS tar sprayed 9,457 `._*` AppleDouble files into it
(deleted; recount 9,457; vu1gen tar used `COPYFILE_DISABLE=1`).

Build: `BUILD FAILED in 9m 10s`. **The NDK killed 3 of the 7
`vu1_*.cpp` TUs with SIGKILL (`Killed`, log lines 706/725/729 — no
compile errors anywhere)**; the other 4 vu1 TUs and every game-unity
and runtime object compiled. Cause: parallel clang++ on the giant TUs
(6.2 k lines / 2,048 musttail-chained functions each, `-O2 -g`)
exhausted bytesize's 9.7 GB WSL RAM. The same TUs compile fine on the
64 GB mini. The fold itself compiles for Android — this is a build-box
resource limit, not a code defect. Remote log pulled to scratch
(`assembleRelease-remote.log`, 58,294 B, SHA `e3e955c0…`); the
`Killed` lines and the `BUILD FAILED` tail are the saved error.

Per the first-failure rule I stopped: no B3, no APK retry, no re-run
with throttled ninja (an orchestrator call — e.g. serialize the vu1
TUs, add swap/ZRAM to the WSL box, or build on a bigger host).

## Budgets and gaps

Builds: 1 tool + 1 full Mac (clean + det reconfigure) + 1 Android
(failed, environmental). Boots 2/3 (B1 120 s, B2 121 s, one slot each;
no B3 per the stop rule), each ≤ 500 s wall cap. Scratch
`~/dev/ssx3-work/F4` 775 MB ≤ 20 GB (build dirs deleted at close per
the brief; worktree kept for the push); global 109.2/200 GB. Never
pushed; fork branch `f4-fold` local-only; text in git (`f4_boot.py`,
`build.sh`, this report); runners signalled only by recorded PID
(SIGTERM via the driver, both reaped); no lease held at close.

Gaps, stated plainly:

- G1. No B3: the Mac ~1.4× number is unmeasured on the fold (VR1's
  1.44× stands from its own branch). The mini was at load 21–47
  during B1/B2, so any speed run in that window would have been void
  anyway; B3 needs a quiet exclusive hold.
- G2. No APK: `assembleRelease` needs a retry with constrained memory
  (see above). No APK kept.
- G3. VU1 total cycles (980,203,317 to t2403+settle, sound on, F4
  codegen) isn't directly comparable to VR1's 959,411,166 (t2400,
  sound off, canonical codegen) — different run shape, not a
  discrepancy. The F4 gate is the 100 % generated share, which holds.
- G4. Frame ticks within Δ7 of target (snapshotter phase, as F2/F3).
- G5. `pgrep -f gradle` on bytesize self-matches its own `bash -lc`
  command line — a false GRADLE-BUSY; check `pgrep -a java/ninja`
  instead (tooling note).
- G6. Share tier (`/Volumes/share`) not mounted: no receipt mirror
  (carries from F3 G7).

## Exact commands

```sh
git -C ~/dev/PS2Recomp fetch /Users/brad/dev/ssx3-work/TC1/PS2Recomp tc1-ctx  # e29e4975 lived only there
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/F4/PS2Recomp -b f4-fold fork/ssx3  # ec2dbf1
git -C ~/dev/ssx3-work/F4/PS2Recomp cherry-pick -x 00381ff 71fda22 1b09a49 1f51e48 6c2de6f
git -C ~/dev/ssx3-work/F4/PS2Recomp cherry-pick -x e5654f3 7caf516 125c9e5
git -C ~/dev/ssx3-work/F4/PS2Recomp cherry-pick -x e29e4975003784493311214b62353f50a8a391e6  # keep both test regs, --continue
# R ctor + test edit, then: git add ps2xRuntime/include/ps2_runtime.h ps2xTest/src/ps2_runtime_kernel_tests.cpp && git commit
git -C ~/dev/ssx3-work/F4/PS2Recomp diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner  # empty
cp ~/dev/ssx3-work/F2/ssx3-functions.sweep.csv ~/dev/ssx3-work/F4/  # SHA 7c827add…b9ba match
# ssx3-f4.toml = folded tracked TOML, 3 paths repointed (diff vs tracked = 3 path lines)
cmake -S F4/PS2Recomp -B F4/build-recomp -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3
cmake --build F4/build-recomp                              # ps2_recomp b6c7a182…
F4/build-recomp/ps2xRecomp/ps2_recomp F4/ssx3-f4.toml       # regen.log, 9457 files
diff -rq ~/dev/ssx3-work/codegen-ssx3 ~/dev/ssx3-work/F4/codegen  # 1 file: sub_003FE828
cmake -S F4/PS2Recomp -B F4/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/F4/codegen -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs -DPS2X_VU1_RECOMP_DIR=/Users/brad/dev/ssx3-work/vu1gen-ssx3 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build F4/build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd F4/PS2Recomp && ../build/ps2xTest/ps2x_tests)           # 646/646
cp F4/build/ps2xRuntime/ps2EntryRunner F4/bin/runner-clean
cmake -S F4/PS2Recomp -B F4/build -DPS2X_ENABLE_DET_HASH_TAP=ON
cmake --build F4/build --parallel 8 --target ps2EntryRunner
cp F4/build/ps2xRuntime/ps2EntryRunner F4/bin/runner-det
python3 local/research/F4/f4_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400 --sound on --coverage-tick 2400 --vu1-stats
python3 local/research/F4/f4_boot.py --mode det --backend parallel --runner bin/runner-det --label B2 --stop-tick 2400 --sound off --coverage-tick 2400 --unpaced
python3 /tmp/f4_hashdiff.py ~/dev/ssx3-work/F4/run/B1/boot.log ~/dev/ssx3-work/F4/run/B2/boot.log  # 2429/2429, 0 diffs
python3 /tmp/f4_hashdiff.py ~/dev/ssx3-work/F3/run/B4/boot.log ~/dev/ssx3-work/F4/run/B1/boot.log  # 2429/2429, 0 diffs
python3 /tmp/f3_alpha.py ~/dev/ssx3-work/F4/run/B1/frames/snap/snap-001097*.png ~/dev/ssx3-work/F4/run/B1/frames/snap/snap-001800*.png ~/dev/ssx3-work/F4/run/B1/frames/snap/snap-002098*.png
git -C ~/dev/ssx3-work/F4/PS2Recomp archive 46b0c8d | ssh bytesize 'wsl -d Ubuntu -- bash -lc "… tar -x … -C /home/brad/f4/PS2Recomp"'
COPYFILE_DISABLE=1 tar -cf - -C ~/dev/ssx3-work vu1gen-ssx3 | ssh bytesize 'wsl … tar -x -C /home/brad/f4'  # 7 files, SHAs match
tar -cf - -C ~/dev/ssx3-work/F4 codegen | ssh bytesize 'wsl … tar -x -C /home/brad/f4'  # rm ._* on arrival, mv to codegen-ssx3
cat local/research/F4/build.sh | ssh bytesize 'wsl ... cat > /home/brad/f4/build.sh'  # SHA 9e89c9c7 both sides
ssh bytesize 'wsl -d Ubuntu -- bash -lc "bash /home/brad/f4/build.sh"'  # BUILD FAILED 9m10s, 3× Killed (OOM)
rm -rf ~/dev/ssx3-work/F4/build ~/dev/ssx3-work/F4/build-recomp
```

## Part 1b (job pool, APK green, B3 1.40×)

Worker: same pane, resumed after a Brad pause (pause notes were
committed as `[F4] Part 1b (paused)`; this section supersedes them).
No push; stopping for the orchestrator gate.

### 1b(1) Job pool commits (done, two commits)

- `6bac3da541d04401900f6bd70fd3f33271f57adb`
  (`ps2xRuntime/CMakeLists.txt`, +4): `JOB_POOLS ps2x_vu1_gen=2` +
  per-source `JOB_POOL_COMPILE`, the orchestrator's sketch.
- `8559ab9b533be8d35b52461369a663147ad71110` (+5): the owning
  target carries the pool too
  (`set_target_properties(ps2EntryRunner PROPERTIES
  JOB_POOL_COMPILE …)`), after the per-source form proved to be
  dropped by Android's CMake (below).

Runner-dir check empty at both; `git diff --check` clean. Mac
configure-only checks (CMake 4.4.3; dirs deleted after): source
form → 7/7 vu1 edges pooled; + target form → 9 edges (7 vu1 + PCH
+ runner unity — the whole small runner target). Build scheduling
only, zero compiled inputs, so `bin/runner-clean` (`7e31b6d2…`,
from `46b0c8d`) is the binary B3 ran. Fold tip is now `8559ab9`.

### 1b(2) APK (green after the target-level fix)

First 1b attempt (from `6bac3da`, box meanwhile upgraded to 11 GiB
RAM + 16 GiB swap): `BUILD FAILED in 31m 20s`, `Killed` on 2 vu1
TUs (log pulled to scratch `assembleRelease-remote-1b.log`, 69,072
B; peak single sample RAM 11,908/11,962 MB + swap 15,751/16,384
MB). Diagnosis: **the pool was defined in the Android
`rules.ninja` but 0 of 7 vu1 edges referenced it** — CMake 3.22.1
(NDK r28) drops per-source `JOB_POOL_COMPILE` from
`set_source_files_properties` while honoring the same call's
`SKIP_UNITY…` (TUs compiled standalone) and honoring nothing else
differently from desktop CMake, which attaches 7/7.

Fix verification on bytesize: after re-archiving `PS2Recomp/` only
from `8559ab9` (346 files both sides, tar kept as
`/home/brad/f4/fork-8559ab9.tar`; codegen/vu1gen/parallel-gs/jniLibs
untouched; both pool lines grepped in the staged tree), the
configure's `build.ninja` carries **9 `pool = ps2x_vu1_gen` edges**
— the target-level form attaches under 3.22.1. No `ninja -j2`
workaround was needed.

Rebuild: **BUILD SUCCESSFUL in 10m 59s**, 48 tasks, zero FAILED,
`--max-workers=2` kept, all 7 vu1 `.o` files built (41–50 MB each,
RelWithDebInfo `-g`). APK `1d711e70…e8f720`, 181,638,728 B (full SHA
`1d711e700754cf170ca263108ed4d855ead58f1c301ac94a21dcb8f5e2e8f720`)
— remote ×2 + pulled ×2,
all four match; kept at `~/dev/ssx3-work/F4/odin/app-release.apk`
(+28 MB over F3's — the 7 images). Success log pulled to scratch
(`assembleRelease-remote-1b2.log`, 31,460 B). Memory during the
successful build (held-ssh 60 s sampler, 15 samples,
`memwatch3-local.log` in scratch): peak **RAM 11,632/11,962 MB +
swap 6,359/16,384 MB** — the pool + swap together did it (pool-only
on 12 GB/no-swap untested; do not assume it fits).

### 1b(3) B3 (done — race 1.40× vs F3 B3)

Exclusive (`both`, 2×30 s lease retries), `runner-clean`,
`PS2X_UNPACED=1`, sound on: bound=target, 67.1 s wall (F3 B3 86.3 s),
last_tick 2430, HUD 36.71 s (F3 36.44 s), load 4.7→4.6 (F3 B3
1.9→1.7 — noisier host, noted), FATAL 0. Run dir
`~/dev/ssx3-work/F4/run/B3/` (`result.json`, `trace.jsonl`,
`boot.log`, 3 `ps-race-*.txt`).

Race number — **raw 5 s windows are authoritative, trace is
stale-row noise here**: trace claims 23.82/s (0.397×) but
`wall_at(1800)` uses the last stale row (1785 stuck 37.0→41.6 s; F3's
G2 mechanism), compressing the window to 25.2 s. Raw in-window
samples (1890/1993/2100/2207/2315): 20.98/20.58/21.38/21.36/21.58,
**mean 21.18/s = 0.353×**; endpoint cross-check 1785@37.0→2430@67.0
= 21.5/s agrees. F3 B3 raw was 15.13 (0.252×); **F4÷F3 raw-vs-raw =
1.400×**, reproducing VR1's own raw-methodology 1.44× (21.45 vs
14.85) within 2 %. Full table (trace | raw): title 37.88 | 59.98
(n=2); menus 76.96 | 59.95 (n=2); loading 28.98 | 47.62 (n=2);
race-start 17.22 | 21.38 (n=1); **race 23.82 | 21.18 (n=5)**. Fast/
short-phase trace values are quantization noise, not regressions
(title/menus likely host-present-capped near 60/s unpaced).

### Part 1b closeout (explicit paths)

- Fork branch `f4-fold` @ `8559ab9`, tree clean
  (`~/dev/ssx3-work/F4/PS2Recomp`). History: `46b0c8d` (Part 1) →
  `6bac3da` (source pool) → `8559ab9` (target pool).
- Scratch `~/dev/ssx3-work/F4` (955 MB with the APK):
  `bin/runner-clean`, `bin/runner-det`, `codegen/` (unpromoted F4
  regen), `run/B1`, `run/B2`, `run/B3`, `odin/app-release.apk`
  (`1d711e70…`), `suite.log`, `*.log`, `memwatch3-local.log`,
  `vu1gen.sha`, `ssx3-f4.toml`, CSV copy. All build dirs deleted;
  worktree kept for the push.
- Bytesize `/home/brad/f4`: `PS2Recomp/` @ `8559ab9` (+ successful
  `.cxx/` outputs), `codegen-ssx3/` (9457, `8ea8ed43…`),
  `vu1gen-ssx3/` (7, SHAs match), symlinks to f2 `parallel-gs`/
  `jniLibs`, `build.sh` (`9e89c9c7…`), all three fork tars,
  `assembleRelease.log` (successful 10m59s run).
- Leases: none held at close (B3 released its exclusive hold;
  no Odin/bradflix involvement). All runners reaped. No background
  sessions left (memwatch terminated after the build).
- Gaps carried: pool-only-without-swap untested (success had both);
  B3 host load 4.7→4.6 vs F3's 1.9→1.7 (one run, no drift
  cancellation); B3 ran `46b0c8d`'s binary (scheduling-only delta
  to tip — no functional difference).

## Recommended next action

The fold itself is ready to push (`f4-fold` `46b0c8d`, fast-forward
from `ec2dbf1`; runner-dir guard empty, suite 646/646, guest-bit-exact
vs F3) — but Part 1's contract (B3 + APK) is unmet for environmental
reasons. Suggested: (1) retry `assembleRelease` on bytesize with the
vu1 TUs serialized or more WSL memory (no code change; staging in
`/home/brad/f4` is verified and reusable — resume is incremental);
(2) run B3 on a quiet exclusive hold; (3) then gate + push. Orchestrator
decides whether the push gates on the APK retry or takes the Mac-only
evidence (the fold compiles for Android up to the OOM point).

## Orchestrator note (2026-09-25)

Mac side accepted (guest-bit-exact vs F3 on 2,429 ticks, 100 % VU1 cycles generated, rider solid, alpha
255, suite 646/646, regen differs by the one predicted vf0 line and stays unpromoted). Android blocked on
bytesize's 9.7 GB WSL memory with 3 giant `vu1_*.cpp` TUs compiling at once. Part 1b: a depth-2 Ninja job
pool for the generated VU1 sources, APK rebuild, and B3.

## Orchestrator note, Part 1b (paused, 2026-09-25)

Accepted as far as it goes: **Mac race 1.40× over F3** (B3). The Android APK still OOMs because
`JOB_POOL_COMPILE` isn't attached by the Android configure (CMake 3.22.1) even though the pool is
defined. Resume options, cheapest first: set the pool as a target property
(`JOB_POOL_COMPILE` on the target that owns the vu1 sources) or pass `-j2` through the native build
(`ninja -j2` on the configured dir); `-O1` for the vu1 TUs; or build the APK on bradflix (62 GB).

## Orchestrator gate, Part 1 + 1b (2026-09-25)

**Pass.** 12 commits on `ec2dbf1` (VR1 stage A, NP1 ×3, TC1 emitter, VU0 R ctor, two VU1 job-pool
commits); guest-bit-exact vs F3 (2,429 ticks), 100 % VU1 cycles generated, suite 646/646, runner-dir diff
empty; **Mac race 1.40× over F3** (B3); APK `1d711e70…` builds on bytesize with the target-level job
pool (Android's CMake dropped the per-source form). Pushed `f4-fold` → fork `ssx3` **`8559ab9`**
(fast-forward from `ec2dbf1`). Codegen: device builds use the F4 regen (`~/dev/ssx3-work/F4/codegen`,
one-line vf0 difference); promotion to canonical waits until the lanes mid-gate on the current codegen
(VB1, HR1, PF1, PX1, LX1) finish. Parts 2 (Odin) and 3 (iPhone) released.

## Part 2 — Odin (BLOCKED: VU1 chain stack-overflow crash on first launch)

Worker: Muse Code, same pane. **Stopped per the first-failure rule on
S1**: the F4 APK crashes 48 s in with a GameThread stack overflow —
512 nested `VU1RecompImage<…>::fXXXX` frames. Single mechanism, root
cause below. No S2, no P1 profile, and deliberately **no F4 play
install** (a crashing build must not replace Brad's working F3 play
build); the device was restored to F3 + deploy-verified instead.

**iOS flag for F4I:** the same chaining ships in the iPhone/iPad
build; secondary-thread stacks there (512 KB) will overflow the same
way. Expect the crash if that pane launches before the fix.

### APK tip (no rebuild needed)

APK `1d711e70…` (181,638,728 B) was built from `8559ab9`: the
re-archive was verified file-by-file (346 both sides, both pool lines
grepped) and its `.cxx` ninja files carry 9 `pool = ps2x_vu1_gen`
edges (the `6bac3da` tree yields 0). Pushed fork `ssx3` = `8559ab9`
= `f4-fold` HEAD (fetched, read-only). Local APK SHA `1d711e70…` ×2
before install; installed `base.apk` reads `1d711e70…` after.

### Launcher

`launch.py` = F3's driver with F3→F4 paths/lease (`sed`, zero `F3`
remnants, docstring fork pin corrected to `8559ab9`) + the main
profile step switched from `-g` to `--call-graph fp` (NP1 verdict;
the `--probe-at-end` probe lines keep `-g`, unused);
`phases.py` verbatim (no lane strings). Env = F3 env incl.
`PS2X_UNPACED=1` (pacing never engages below 1×, so the profile run
would match NP1's paced env exactly in the race window).

### S1 (1/1; crash)

Pre-launch: lease `LEASE_FREE F3 done`, keyguard `showing=false`
(read-only), AC true, 100 %, thermal 0, app not running, Brad env
`9fb46f85…` + mc0 pins verified, mc0-test absent→created empty.
Pair method: thermal 0 pre-wait, 180 s wait, thermal 0 at launch.
Over Wi-Fi (serial from `local/odin-serial`); no drops.

| Item | Result |
| --- | --- |
| Run | t+0→48.2 s, tick~1565 (loading), then `FATAL seen in logcat` |
| Crash | SIGSEGV SEGV_ACCERR `fault addr 0x6d8048efd0`, `stack pointer is not in a rw map; likely due to stack overflow`, **512 total frames**, all `VU1RecompImage<8626389153574412127>::fXXXX(VU1Interpreter&, RunContext&)` (`logcat.txt:789-814+`) |
| sc01 | `sc01-final-t48.png` (`dffdfa51…`, scratch `odin/S1/`): Android home screen — the app was already dead at scap time |
| After | force-stop (pid none), Brad env restored (`9fb46f85…` match), mc0 bad=[], lease `LEASE_FREE F4 done` |

### Root cause (single mechanism)

VR1's chaining (g4) is musttail in only one direction. The emitter
(`ps2xRuntime/src/lib/vu/ps2_vu1_recomp.cpp` @ `8559ab9`):

- line 154: `next()` ends with `PS2X_VU1_MUSTTAIL return fn(vu, c);`
  — guaranteed tail call into the next pair;
- line 187: each pair function ends with a **plain**
  `return next(vu, c);` (0 occurrences of `MUSTTAIL return next` in
  all 7 `vu1gen-ssx3` images).

So the chain is f1 →(ordinary) next →(tail) f2 →(ordinary) next
→(tail) f3 … — every pair parks one ordinary-call frame that only
returns when the chain ends. Up to 2,048 pairs per image run × fat
frames (fully inlined issuePair + FMAC per function) overflows the
~1 MB GameThread stack; here it died 512 frames deep. The Mac
survived on a bigger stack (and/or Apple-clang sibling-call
optimization of the plain tail-position return — either way,
unsound to rely on). The backtrace shows *only* f-frames, no
`next()` frames — exactly this shape, no second bug.

The fix is one line (emitter :187: `PS2X_VU1_MUSTTAIL return
next(vu, c);`) + regen + rebuild; `musttail` then guarantees a
flat chain by construction (compile error otherwise). Not attempted
here — it needs a fork commit + regen + Mac re-verify + APK rebuild
+ Odin re-run, an orchestrator call. Note the pushed `ssx3`
(`8559ab9`) contains the bug.

### Device end state (restored, not F4)

F4 play install blocked (crashing build). Instead: F4 scratch
removed (`/data/local/tmp/f4`, `mc0-test{,_slot1}` — all three
confirmed gone), **F3 APK `d5a94c27…` reinstalled** (`Success`,
local ×2 + `base.apk` ×1 all match) + `deploy-odin.sh` (env
`9fb46f85…` + 6/6 saves OK), no launch. Final: lease free, app
stopped, 100 % on AC.

### Budgets and gaps

Installs 2 (F4 run + F3 restore), launches 1 (~52 s wall, crash).
Scratch `~/dev/ssx3-work/F4` 4.5 GB total, of which F4I's `ios/`
is 3.5 GB — Part 2's own footprint is ~1.0 GB (APK + logs/S1 + 1 PNG).
Text logs (S1, 312 K) + `launch.py` + `phases.py` committed here.
Gaps: no S2 (no speed pair — nothing to compare until the chain is
flat); no P1 profile (same crash would hit at tick 2400); the F4
APK is unusable on-device; F4I (iOS) carries the same bug.

Exact commands:

```sh
shasum -a 256 ~/dev/ssx3-work/F4/odin/app-release.apk  # 1d711e70 x2
sed -e 's/F3/F4/g; s|/data/local/tmp/f3|/data/local/tmp/f4|g' local/research/F3/launch.py > local/research/F4/launch.py
cp local/research/F3/phases.py local/research/F4/phases.py  # verbatim
# + docstring pin + simpleperf --call-graph fp edits
adb -s "$S" install -r ~/dev/ssx3-work/F4/odin/app-release.apk  # Success; base.apk 1d711e70
# S1: thermal 0, sleep 180, thermal 0
python3 local/research/F4/launch.py --label S1 --wall 600 --stop-tick 4500  # FATAL t+48s tick~1565
adb -s "$S" pull /data/local/tmp/f4/sc01-final-t48.png ~/dev/ssx3-work/F4/odin/S1/  # dffdfa51
adb -s "$S" shell 'rm -rf /data/local/tmp/f4 .../files/mc0-test .../files/mc0-test_slot1'
adb -s "$S" install -r ~/dev/ssx3-work/F3/odin/app-release.apk  # F3 restore, no launch
bash local/research/I31/deploy-odin.sh "$S"  # env + 6/6 OK
adb -s "$S" shell 'am force-stop com.ps2x.runner'
```

Recommended next action: one-line emitter fix (`musttail` on the
pair→`next()` call) + regen the 7 images + Mac det/speed re-verify
+ APK rebuild + Part 2 re-run (S1/S2/P1). Warn F4I before it
launches the iPad build. Orchestrator decides fix-forward vs
revert on the pushed `ssx3`.

## Orchestrator gate, Part 2 (2026-09-25)

**Correct stop.** The generated VU1 pair functions end with a plain `return next(vu, c)` (emitter
`ps2_vu1_recomp.cpp:187`), so only `next → pair` is a guaranteed tail call; the chain recurses. Apple
clang on the Mac's 8 MB main stack hid it; Android's GameThread overflowed at 512 frames. Brad's F3 play
build was restored and verified; F4I was stopped before any iPhone install. Part 2b released (below).

## Part 3 (stopped) — iOS: build green, iPad crashes pre-race, iPhone never touched

Worker: Muse Code, brief `local/muse/prompts/F4.md` Part 3 only.
**Stopped by the orchestrator before any iPhone install**: Part 2
found the VU1 pair→`next()` chain is a plain call, not a guaranteed
tail call, so it recurses and overflows small stacks (the Android
GameThread died 512 frames deep); iOS secondary threads (512 KB)
crash the same way. My iPad run independently crashed pre-race
(signal 10 at tick ~1455, below). **The iPhone was never installed,
never launched, never probed** — no `install_iphone` /
`deploy-ios.sh iphone` / launch command targeted it (no
`install-iphone.log` exists).

### Build (device `8559ab9`, F4 codegen + 7 VU1 images)

Source: pushed fork `ssx3` `8559ab9` (fetched `fork/ssx3` =
worktree `HEAD`, tree clean). Script
`~/dev/ssx3-work/F4/ios/build-install.sh` = F3's recipe + W/FORK_WT
repoint, `PIN→8559ab9…`, `CODEGEN→…/F4/codegen`, new
`VU1GEN=…/vu1gen-ssx3` + `-DPS2X_VU1_RECOMP_DIR` in configure,
preflight pins for the changed codegen file + all 7 vu1 SHAs, and a
configure assertion on `PS2X: VU1 recomp: 7 images`. PGS `19d93b2`
+ MoltenVK 1.4.2 + raylib reused read-only from I33's scratch;
bundled env is I33's `ps2x.env` unchanged.

Preflight rc=0 (runner-dir diff empty, PIN ancestor of HEAD, PGS
pin + clean, Granite `166ba21a`, codegen `8ea8ed43…` + changed
file `89953ba2…`, 7/7 vu1 SHAs match Part 1 `vu1gen.sha`, env
`8e0547fc…` = I33's pin, MoltenVK device `6cd58884…` = I33's pin,
profile valid, iPad `connected` + iPhone `available (paired)`).
configure_device rc=0 (`-O3 -DNDEBUG` ×2, `G44 parallel-gs shadow
backend ON`, `VU1 recomp: 7 images`; Xcode ignores
`JOB_POOL_COMPILE` silently — 0 mentions, no warnings).
build_device **BUILD SUCCEEDED**, 0 `error:` lines, 151,472,832 B
binary (+24 MB over F3's 126.8 MB — the 7 images), **14,343
`VU1RecompImage` symbols** (same count as the Mac clean runner —
the images linked in). stage_device rc=0 (ELF `1b49d05c…`, ISO
`3c2f8eb1…`, MVK `6cd58884…` all SHA-match inputs, bundle
`org.ps2x.ps2entryrunner`); sign rc=0 (`codesign --verify --strict`
valid on disk).

| Binary | SHA-256 (two matching reads) |
| --- | --- |
| device unsigned | `90396cb4ed703127c37de75d8789bb0afc1dc16ff698f98d5a56d266d4277709` |
| device signed (installed on iPad) | `6f9f210cb6efd08030e3a188d3f7bce3300d44053a8ce9a95dfdb416578a6fc5` |

### iPad (Air 11" M2): install green, pre-race crash

Install rc=0 (seq 1956, bundle `3EB29373-…`); deploy SKIP + 7
exact-size OKs. Probe (~1 s console): live container `31F72FD9-…`
(a reinstall-new Data container, not F3's `D3C32E8F-…`), bundle
path matches the install URL. Run env = route byte-exact 484
chars (identical to F3's run route) + `PS2X_VSYNC_RATE_LOG=1` +
fresh `mc-f4` under the live container. Bundled env selected
parallel + force as designed: `[gs:parallel] live backend
selected`, `[gs-path] … gpu=Apple M2 GPU`, `init ok`,
`[snd-output] stream rate=48000`, overlay shown.

Run f4: `shot-t1090` at tick 1164 (viewed: Select Event — Snow
Jam / Metro-City / Happiness + Race course map, legible, full
brightness; `628b1785…`), then **`App terminated due to signal
10` at 29 s wall, last tick line 1455** (loading transition),
zero FATAL, presents=1500 at the last periodic line. Retry f4b
(fresh `mc-f4b`, same route): `shot-t1090` at tick 1146, then the
orchestrator stop landed mid-run — killed before any verdict (not
evidence either way). iPad end state: 0 app procs (trap cleanup +
explicit check), F4 build left installed (test device,
orchestrator-approved).

The iOS crash signature (SIGBUS, no guest FATAL) is not the
Android symbolicated 512-frame backtrace — no `.ips` was retrieved
(no libimobiledevice on the mini) — so the recursion is not
independently confirmed on iOS; it is consistent with the
orchestrator's mechanism (small secondary-thread stack + the same
chaining) and hit at a VU1-heavy transition.

### Budgets and gaps

1 device build (~4 min), 1 probe + 1.5 iPad runs, 1 install; ~25
min wall. Scratch `~/dev/ssx3-work/F4/ios` 3.5 GB (build dir kept
for the post-fix incremental rebuild; lane total within the 20 GB
cap; disk 118.4/200 GB at start). No lease held (no mini boots, no
Odin touch). Text in git: this section only (scripts stay in
scratch, as F3 Part 2).

Gaps, stated plainly:

- G1. No race frames, no diagnostic pace: the crash lands before
  t1714 (one completed crash, one run stopped mid-way).
- G2. iPhone deliberately untouched: no install, no env, no
  launch. Brad's iPhone still has the F3 build.
- G3. No iOS backtrace: the SIGBUS mechanism is inferred from
  Part 2's Android root cause, not independently confirmed.
- G4. No post-run deploy re-verify (stopped early); runs used
  `mc-f4`/`mc-f4b` cards only, Brad's `mc0` untouched since the
  pre-run 7/7 OKs.
- G5. Brad's `mc0` on the iPad lives in the new `31F72FD9-…`
  container (reinstall effect); the deploy put it there with
  exact-size OKs.

Exact commands:

```sh
sed -e 's|.../F3/ios|.../F4/ios|' -e 's|.../F3/PS2Recomp|.../F4/PS2Recomp|' \
  -e 's|^PIN=ec2dbf1...|PIN=8559ab9...|' -e 's|^CODEGEN=.../codegen-ssx3|CODEGEN=.../F4/codegen|' \
  ~/dev/ssx3-work/F3/ios/build-install.sh > ~/dev/ssx3-work/F4/ios/build-install.sh
# + VU1GEN var/flag, preflight vu1 + changed-file pins, 7-images assertion
bash ~/dev/ssx3-work/F4/ios/build-install.sh preflight configure_device build_device stage_device sign
bash ~/dev/ssx3-work/F4/ios/build-install.sh install_ipad
bash local/research/I31/deploy-ios.sh ipad
bash ~/dev/ssx3-work/F4/ios/ipad-probe.sh             # live container 31F72FD9-…
bash ~/dev/ssx3-work/F4/ios/ipad-run.sh .../run-ipad-f4 .../run-ipad-env.json "1090 1810 2100"  # signal 10 @29s
bash ~/dev/ssx3-work/F4/ios/ipad-run.sh .../run-ipad-f4b .../run-ipad-env-b.json "1090 1810 2100"  # stopped mid-run
```

Recommended next action: after the one-line emitter fix
(`musttail` on pair→`next()`), regen, and Mac re-verify, rebuild
this same script (incremental) and re-run Part 3 whole: fresh iPad
install + race run to t2100, then iPhone install +
`deploy-ios.sh iphone`, still no iPhone launch.

## Orchestrator gate, Part 3 (2026-09-25)

Correct stop: the iOS build reproduces the chain recursion (iPad signal 10 before the race). The iPhone was
never touched. The iPad is being restored to the F3 build. Part 3 reruns after Part 2b's fix.
