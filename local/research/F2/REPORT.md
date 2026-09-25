# F2 Part 1 — fold SB1 + AU10 + CT1 + GB9 onto fork `ssx3`, codegen promotion, Mac check

Worker: Muse Code, brief `local/muse/prompts/F2.md` Part 1 only. No push
(orchestrator gates and pushes). First-failure rule never triggered.

**Result: fold clean, codegen promoted, Mac green.** All 5 cherry-picks applied
with no conflicts; the folded tree's regen is byte-identical to SB1's codegen
(`diff -rq` empty) and is now the canonical `codegen-ssx3`; suite 612/612;
B1 races with sound on (cid0 531, coverage 0/0/4), B2 races with sound off
(det-hash identical to B1), B3 clean speed matches F1 B2 phase-for-phase
(race 0.250× both).

## Fold (worktree `~/dev/ssx3-work/F2/PS2Recomp`, branch `f2-fold` from `56a5e8a`)

`git cherry-pick -x` in brief order, all clean (CT1 auto-merged
`EeScheduler.cpp`, which SB1 also touched, nearby but disjoint lines).

| # | Source | New SHA | Subject |
| --- | --- | --- | --- |
| 1 | `a64ba5e` | `51ac2da7344a999c6dff00db8e53bbd5fb3d41ee` | [SB1] signed-branch tripwire: 64-bit predicates + dev-only 32/64 mismatch note |
| 2 | `90df7e0` | `2695df0b2d557ee3ae170262f480d9faf0adaa29` | [SB1] retire the 0x3E3968 file-key comparator override |
| 3 | `2fb2003` | `09a95d96c5db48f45e27a4a0bb05659378d89969` | [AU10] SND HLE: run the guest-time tick unconditionally, gate only host output on PS2X_SOUND |
| 4 | `3344013` | `b975fb22b664ecb498d341079ef5db12edf1ec10` | [CT1] EeScheduler: default-off PS2X_INTC_LOG + PS2X_COVERAGE_TICK counters |
| 5 | `5706858` | `96e9f45b5dca49e6cc1297d5984b506a61d1b369` | [GB9] [gs-path] prints the effective hier rule via PGS_HIER_BINNING (local-only) |

Old full SHAs: `a64ba5e94383505570628c43cee537e82d07ade7`,
`90df7e0c8afb9e48abd6ae8981bd81e5d5f5833a`,
`2fb200391a739088a10b16b5f7154de4d0d96837`,
`3344013bd17387e8e547b3534166220f12968580`,
`5706858db4145f1ea84cf3bfd4ae338255023cdc`.
Tip: `96e9f45`. `games/` untouched by the fold
(`git diff 56a5e8a HEAD --stat -- games/` empty).
Runner-dir guard `git diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner`:
empty. `git diff --check 56a5e8a HEAD`: clean.

## Codegen (regen + equality + promotion)

- TOML: folded tree's tracked `games/ssx3/ssx3.toml` with only the 3 SB1
  paths repointed (`ssx3-f2.toml`; diff vs SB1's TOML = the 2 expected
  path lines; CSV copy SHA `7c827add…b9ba` matches SB1's).
- Tool build (SB1 recipe flags): configure rc=0, build rc=0
  (`cmake-recomp.log`, `build-recomp.log`). `ps2_recomp`
  `ccc2d8cc0b7c90aa89f0c72bd946323e9fd9b6b163095a80a4809c85c1dfe755`
  (differs from SB1's tool binary — embedded paths; the output is the gate).
- Regen: rc=0, 9,457 files (`regen.log`).
- **Equality: `diff -rq ~/dev/ssx3-work/SB1/codegen ~/dev/ssx3-work/F2/codegen`
  rc=0, 0 bytes of diff** (`codegen-diff.txt`).
- Promotion: `mv codegen-ssx3 codegen-ssx3-pre-sb1` + `cp -R F2/codegen
  codegen-ssx3`, rc=0; post-copy `diff -rq` rc=0 (exact copy).
  `register_functions.cpp` SHA `8ea8ed436b78fee0156e37a972924645d8a7f4041cb90cab1a6b2ae662d688a3`
  (two matching reads; unchanged by the promotion — the SBR change touches
  predicate lines in function files only). File counts 9,457 / 9,457.
  New canonical: 623 files reference `PS2X_SBR_LT` (pre-promotion: 0).
- Never committed: generated code lives only in scratch + the canonical dir.

## Builds (one dir `~/dev/ssx3-work/F2/build`, GB8/F1 recipe + `BUILD_TEST=ON`)

Release, Homebrew clang, `PS2X_GAME_CODEGEN_DIR=` promoted canonical,
`PS2X_GS_SHADOW_PARALLEL=ON`, paraLLEl-GS worktree
`~/dev/ssx3-work/F2/parallel-gs` at `19d93b2` (detached HEAD on
`origin/ssx3`; Granite `166ba21a247a681903cc9d0bb6562fe50a554c85`, matches
pin), runtime/aggressive logs OFF, diag taps OFF, tripwire default OFF
(release collapses to `GPR_S64`). Det runner = incremental reconfigure
(`DET_HASH_TAP=ON`, 353 steps) after copying the clean runner out.
Configure + both builds rc=0.

| Runner | Det-hash tap | SHA-256 (staged read + 2 boot-precheck reads match) |
| --- | --- | --- |
| `bin/runner-clean` | OFF (`det-hash:v1` 0× in strings) | `62d56f268afffdcd40bc488090c05dfa47ffcf4d7e3f8038955b85602055ddaf` |
| `bin/runner-det` | ON (string present) | `54789f9afadd4a87a79138e1663fd47d2e9ca9dfc4a1dbde9ce958b296542ba0` |

Suite from the worktree root: **612/612 pass, 0 fail, rc=0** (`suite.log`;
611 + AU10's "keyed-off voice ENVX decays to zero with no output device,
then retriggers" `[Passed]`; the SB1/AU10 4 extra det-hash tests compile
in only with the tap on, and this build has it off).

## Boots (I26-FAST, empty mc0, `PS2X_SKIP_MOVIE=1`, deterministic, paraLLEl + `PGS_HIER_BINNING=force`)

Driver: `f2_boot.py` (committed here; F1 driver + force-binning in the
parallel env and recorded env + `PS2X_COVERAGE_TICK` in det mode + `--sound
on|off` in det mode; speed mode always sound-on per F1). `[gs-path]` on all
three boots: `hier_rule=hier-if-large hier_t2=2 hier_t4=4 … desc=plain …
gpu=Apple M5 Pro` (the GB9 effective-rule print + Odin binning rule live).
Boot-driver prechecks: two SHA reads match on runner/ISO/ELF/codegen every
boot; ISO `3c2f8eb1…`, ELF `1b49d05c…`, codegen `8ea8ed43…` all pinned.

| Boot | Sound | Bound | Wall | Last tick | HUD wall | cid0/dmq/done | FATAL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 det | on | target | 85.9 s | 2403 | 35.44 s | 531/531/531 | 0 |
| B2 det | off | target | 83.9 s | 2400 | 34.49 s | 531/531/531 | 0 |
| B3 speed | on | target | 81.3 s | 2418 | 35.92 s | — | 0 |

B1: `[snd-output] stream rate=48000` live; coverage at vsync 2400 =
`targets=0`, `ids=0`, `pairs=4` (the E56 four SIDs, one hit each —
identical list to CT1 B2). B2: no `[snd-output]` (host stream off, as
designed); B2's snd tick serials carry identical guest cycle counts to B1's
(e.g. `cycle=11550757345 ticks=3572` both); B1 underruns = 2.1M (consumer
starved on a loaded mini, same AU8/AU9/AU10 symptom, diagnostic build —
not a speed number), B2 underruns = 0 / overflows as designed.

**B1 vs B2 det-hash: 2,448/2,448 common ticks byte-identical, all fields,
0 differing payloads** (glue-immune regex extract; B1 ticks 1..2450, B2
1..2448 — 2-tick settle overrun, the documented GB8 variance).
`gb8_hashdiff.py` reports DIFFER only because of the GB9 glued-line
artifact (`[frame:dump]...[det-hash:v1]` sharing one line, no newline
between threads; line-anchored parser misses 1 tick in B1, 3 in B2 — all
verified present by field extract). AU10's property holds on the fold.

## Frames (0.5 s snapshotter, picked by exact present tick from the sidecar)

All viewed, all 512×448 fbp 112, no tiles/stripes/corruption:

| Boot | Present tick | File (`run/<B>/frames/snap/`) | Viewed verdict |
| --- | --- | --- | --- |
| B1 | 1094 | `snap-001052t-0019.30s.png` (`fnv1a=e9825b18`) | Select Peak: Peak 1 mountain photo, Peak 1 highlighted, 2/3 locked, correct text |
| B1 | 1800 | `snap-001793t-0041.65s.png` (`fnv1a=44ebc4b0`) | Race 00:00:01 2ND/2: rider, lit snow, pines, mountains, EA Radio card |
| B1 | 2096 | `snap-002090t-0062.47s.png` (`fnv1a=a5a4bd9f`) | Race 00:00:06 2ND/2, 1%, checkpoint beam, trick 160 |
| B1 | 2392 | `snap-002387t-0082.27s.png` (`fnv1a=ecc2ff82`) | Race 00:00:11 2ND/2, 2%, 14 MPH, slope/trees/spray |
| B2 | 2103 | `snap-002097t-0061.47s.png` (`fnv1a=e710d8d5`) | Sound-off race 00:00:06 2ND/2, 1%, beam, trick 270 (animation Δ vs B1's 160 across ~7 ticks, not a state diff — det-hash identical) |

## B3 per-phase vs F1 B2 (trace authoritative; guest vsyncs/s ÷ 59.94)

Exclusive lease ("both" slots), quiet host (load 1.9 at claim, quieter than
F1's 2.2). The fold is speed-neutral on the Mac.

| Phase (ticks) | F2 B3 vs/s (×) | F1 B2 vs/s (×) | F2 ÷ F1 |
| --- | --- | --- | --- |
| Title [0,636) | 40.32 (0.673×) | 40.29 (0.672×) | 1.00× |
| Menus [636,1440) | 76.96 (1.284×) | 77.13 (1.287×) | 1.00× |
| Loading [1440,1714) | 28.26 (0.472×) | 28.30 (0.472×) | 1.00× |
| Race-start [1714,1800] | 16.61 (0.277×) | 16.69 (0.278×) | 1.00× |
| **Race (1800,2400]** | **14.98 (0.250×)** | **15.01 (0.250×)** | **1.00×** |
| Wall launch → race HUD (~t1714) | 35.92 s | 35.9 s | 1.00× |
| Wall launch → t2400 | 81.3 s | 81.3 s | 1.00× |

Raw 5 s cross-check (race window): n=8 mean 15.13 vs trace 14.98 — agrees.
One run (brief budget); no drift cancellation.

## Budgets and gaps

Builds: 1 tool + 1 full (clean + det reconfigure). Boots 3/3 (B1 86 s, B2
84 s one slot each; B3 81 s exclusive), each ≤ 500 s wall cap. ~1 h of the
1.5 h box. Scratch `~/dev/ssx3-work/F2` 3.2 GB (≤ 20 GB); global 122.0/200 GB.
Never pushed; fork branch `f2-fold` local-only; text in git (`f2_boot.py`,
this report); no runners signalled except by recorded PID.

Gaps, stated plainly:

- G1. One speed run (no drift cancellation); B3's force-binning-vs-flat
  cost split is unmeasured (GB9 proved force correct, not its Mac cost —
  the F2÷F1 1.00× is fold+force combined vs F1's flat-always).
- G2. Frame ticks within Δ8 of target (snapshotter phase, not exact-tick
  dumps — `PS2X_FRAME_DUMP_ONCE_TICKS` takes only 3 ticks).
- G3. B2's S-on pixels not separately diffed (one B2 frame viewed; the gate
  is det-hash identity, which passed on all 2,448 common ticks).
- G4. `gb8_hashdiff.py` remains line-anchored and trips on the glued
  `[frame:dump]`/`[det-hash]` lines (tooling note, also seen in GB9);
  the glue-immune extract is the authoritative gate here.
- G5. The promoted canonical codegen changes every downstream build: lanes
  that built against `codegen-ssx3-pre-sb1` must rebuild (the old tree is
  preserved at that path; `register_functions.cpp` SHA is unchanged, so
  SHA-pinned prechecks still pass — they do not detect the promotion).

## Exact commands

```sh
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/F2/PS2Recomp -b f2-fold fork/ssx3  # 56a5e8a
git -C ~/dev/ssx3-work/F2/PS2Recomp cherry-pick -x a64ba5e 90df7e0 2fb2003 3344013 5706858
git -C ~/dev/ssx3-work/F2/PS2Recomp diff --stat 14b1e5cb HEAD -- ps2xRuntime/src/runner  # empty
git -C ~/dev/parallel-gs worktree add ~/dev/ssx3-work/F2/parallel-gs origin/ssx3  # 19d93b2
git -C ~/dev/ssx3-work/F2/parallel-gs submodule update --init --recursive Granite  # 166ba21
cp ~/dev/ssx3-work/SB1/ssx3-functions.sweep.csv ~/dev/ssx3-work/F2/  # SHA 7c827add…b9ba match
# ssx3-f2.toml = folded tracked TOML, 3 paths repointed (diff vs SB1's = 2 path lines)
cmake -S F2/PS2Recomp -B F2/build-recomp -G Ninja -DCMAKE_BUILD_TYPE=Release -DPS2X_BUILD_RECOMP=ON -DPS2X_BUILD_RUNTIME=OFF -DPS2X_BUILD_ANALYZER=OFF -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_GAME_CODEGEN_DIR=~/dev/ssx3-work/codegen-ssx3
cmake --build F2/build-recomp                              # ps2_recomp ccc2d8cc…
F2/build-recomp/ps2xRecomp/ps2_recomp F2/ssx3-f2.toml       # regen.log, 9457 files
diff -rq ~/dev/ssx3-work/SB1/codegen ~/dev/ssx3-work/F2/codegen  # rc=0, empty
mv ~/dev/ssx3-work/codegen-ssx3 ~/dev/ssx3-work/codegen-ssx3-pre-sb1
cp -R ~/dev/ssx3-work/F2/codegen ~/dev/ssx3-work/codegen-ssx3
cmake -S F2/PS2Recomp -B F2/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 -DPS2X_BUILD_TEST=ON -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/ssx3-work/F2/parallel-gs -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build F2/build --parallel 8 --target ps2x_tests ps2EntryRunner
(cd F2/PS2Recomp && ../build/ps2xTest/ps2x_tests)           # 612/612
cp F2/build/ps2xRuntime/ps2EntryRunner F2/bin/runner-clean
cmake -S F2/PS2Recomp -B F2/build -DPS2X_ENABLE_DET_HASH_TAP=ON
cmake --build F2/build --parallel 8 --target ps2EntryRunner
cp F2/build/ps2xRuntime/ps2EntryRunner F2/bin/runner-det
python3 f2_boot.py --mode det --backend parallel --runner bin/runner-det --label B1 --stop-tick 2400 --sound on --coverage-tick 2400
python3 f2_boot.py --mode det --backend parallel --runner bin/runner-det --label B2 --stop-tick 2400 --sound off --coverage-tick 2400
python3 f2_boot.py --mode speed --backend parallel --runner bin/runner-clean --label B3 --stop-tick 2400
python3 gb8_rates.py run/B3
python3 local/research/GB8/gb8_hashdiff.py --base ~/dev/ssx3-work/F2/run/B1 --cand ~/dev/ssx3-work/F2/run/B2  # glued-line caveat, see above
```
