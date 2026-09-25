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
