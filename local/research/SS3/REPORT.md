# SS3 — close RV5's save-state holes

Worker: Muse Code, brief `local/muse/prompts/SS3.md`, 2026-09-26.
Fork worktree `~/dev/ssx3-work/SS3/PS2Recomp`, local branch `ss3` from
`fork/ssx3` `5d5c38211c6c13e5c6fcecf9df8f051469a49445` (never pushed).
paraLLEl worktree `~/dev/ssx3-work/SS3/parallel-gs`, local branch
`ss3-clut` from `origin/ssx3` `1b3a2948cc55e74f975e42b79d08983f31c2dbb6`
(never pushed). No push anywhere. No `docs/` edits.

Note: the E-lane checkout `~/dev/PS2Recomp` sits at `f949ff0` (pre-SS1);
it was not touched. `fork/ssx3` (= `5d5c382`) is the base used here.

## Outcome

All four findings fixed, one commit each, each with a test verified to
fail before its fix. Every gate below ran at the exact final tip (fork
`f0d2d3c` + PGS `3d72467`); the Mac runner SHA is byte-identical before
and after the PGS fixup (`0339265d…`, include-only change), so the
pre-compaction Mac receipts are final-binary results too.

## Finding → fix → test

| Finding | Fix | Test (fails before) | Status |
| --- | --- | --- | --- |
| S2 palette indices | gs v3 tail carries `render_pass.clut_instance/latest_clut_instance` (paraLLEl 6-arg overloads; write drops memoized palettes) + footer | GPU test round-trips patched ring + (1,2,3,4) → (3,3,3,3) after the save-time rewind (skips headless) | done, fails pre-fix (no footer in v2 blob) |
| S3 partial GS input | transfer defers (`gs-transfer` reason); vertex queue serialized in the v3 tail (a vertex deferral could never land: frames often end mid-strip) | GPU tests: split IMAGE upload idle+reason; strip continued across save/load matches the uninterrupted queue (skip headless) | done, both fail pre-fix |
| S4 card dirs/timestamps | mcdir v2: dirs (incl. empty) + file/dir mtimes travel; whole dest tree validated; identical files never rewritten (times restored); traversal errors throw `dir_tree_error` → deferral reason | mkdir/save/load/create; real `sceMcGetDir` tables equal after load; validation matrix; read-only no-rewrite proof; error cases | done, all fail pre-fix |
| S5 Android runner identity | `runtimeModulePath()` via `dladdr` (lib on Android, exe on desktop; no launcher fallback on Android); strict refuses unknown identity | helper unit test (module == dladdr module == executable, hashes) + strict verdict matrix | done; fail-before is compile-level (new API) |

### S2 notes

Every save-time `flush()` runs `flush_render_pass`, which collapses the
cursors to the interface slot (`latest=iface`, `base=next=iface`), so
real saves always carry an empty pending window — but the absolute slot
is run-specific, not normalized: two t2000 saves from the same binary
hold 977 vs 1011 (all four cursors equal in each). The current-palette
slot DATA is byte-identical across the runs (slot-1011-old ==
slot-977-new over 1024 B), so each state is self-consistent — and the
run-specific slot is exactly why the indices must travel: a load that
reset them to (0,0) would mispoint the renderer into a stale ring slot.
A "forgot latest" bug would still be masked by the all-equal collapse
(latest is unobservable after a flush); the set-both-fields code is
symmetric and reviewed. Pre-fix restore left the interface at (0,0):
the test fails pre-fix at the footer parse and (had it parsed) the
load refuses the v3 shape.

### S3 notes

Deferring on the vertex queue was rejected in favour of serializing it
(the brief permits either): a strip left open at end-of-frame keeps
`count > 0` at every vsync, so a vertex deferral might never land within
a boot, while transfers always complete (the guest needs the data).
Real saves carry `vcount=0` (no strip open at t1720/t2000).

### S5 notes

No runtime fail-before is observable on desktop (dladdr and the exe path
name the same file by design; identity is always obtainable here), so
the tests are new-API unit tests; the test TU fails to compile pre-fix
(`no member named 'runtimeModulePath'/'checkRunnerSha'`). On Android the
`/proc/self/exe` fallback is compiled out (`__ANDROID__` first branch);
the one remaining `/proc/self/exe` string in the .so is pre-existing
Granite third-party code (fossilize/SDL3 — F6's pre-SS3 .so has the
identical single occurrence). `equivalent(module, exe)` proves the
desktop identity (and its hash) is unchanged.

## Gates

| Gate | Result |
| --- | --- |
| Mac suite (det) | 689/689, from the worktree (`cd <worktree> && <build>/ps2xTest/ps2x_tests`); runner `0339265d…` (×2) |
| bradflix suite (det) | 689/689, build `SS3-det2` (fork `f0d2d3c`, staged `pgs-3d72467033ce`: HEAD/Granite/29 submodules verified); runner `ad02d821…` (×2) |
| det vs a3efbfe baseline (knobs unset) | IDENTICAL 1..2400 (+snd/coverage IDENTICAL), final tip |
| round trip t2000→t2600 Mac (strict load) | hash IDENTICAL 2001..2600; frames 2300+2600 IDENTICAL, t2100 differs run-to-run (present phase, see below); snd 11/11 common lines |
| round trip t2000→t2600 bradflix (strict load) | hash IDENTICAL 2001..2600; frames 2300+2600 IDENTICAL; t2100: load==straight-B1, straight-B1≠straight-B2 (load faithful); snd 10/10 |
| 4×+hi-res round trip | det-hash IDENTICAL 2001..2200, snd IDENTICAL, t2200 1024×896 frame IDENTICAL; per-tick present FNVs differ on a minority of ticks — pre-existing (SS2-runner controls) |
| Android compile (bytesize) | BUILD SUCCESSFUL in 27m36s; `.so` `be30e311…` (×2); `runtimeModulePath` ×4 in strings (S5 in); `/proc/self/exe` ×1 pre-existing |
| old-state refusal | `section gs version 2 != 3` in ~1 s, rc=0 (intended) |
| runner-dir check | empty, both `5d5c382..ss3` and `14b1e5cb..ss3` |

Suite CWD trap (mine, not a code failure): run from `build-det/`, the
VU0 macro test fails (it reads `ps2xRecomp/include/…` relative to CWD);
from the worktree it is 689/689. The canonical form is SS2's
`cd <worktree> && <build>/ps2xTest/ps2x_tests`.

### Round-trip frame analysis (t2100)

Mac: straight `7ad8f18d` vs load `fdbbd91c` at t2100; 2300/2600 match.
Bradflix: B1 `ccfbda8c`, B2 `68bfa045`, B3(load) `ccfbda8c` at t2100;
2300/2600 match everywhere. Two straight runs (B1 vs B2, no save/load
involved) differ at the same tick, while the load (B3) matches a
straight run exactly — so the variance is run-to-run present phase, not
load corruption. Guest state is identical throughout (det-hash
IDENTICAL incl. t2100). Same class as SS1 §Stage 3 / SS2's t2600
straight-run diff.

### 4× present-cadence analysis

All-frame FNV comparison over 2001..2200 (mine, 4×+hi-res+pipeline):
117 common ticks, 57 same-tick diffs, ~37 ticks per side with a present
only on one side; multiset overlap 112/154. No-pipeline pair: same shape
(102/11/45/44). SS2-runner (pre-SS3) controls: pipeline 58/36/20/17,
no-pipeline 110/16/38/37 — the same pattern without my changes.
Straight-run FNVs match across builds at shared ticks (e.g. t2003
`90830b35`, t2019 `8deb7b75` in both my tip and the control), so my tip
changes nothing about rendering. Mechanism: host-side present
coalescing/timing under SSAA load (guest det-hash identical; pacer and
present timing are host state, not in the savestate). SS1's 4× gate was
det-hash + specific dump ticks for the same reason.

### State byte math (Mac)

t1720/t2000 1× states: 53,898,055 B = SS1's 53,898,015 + 40
(+8 S2 indices, +4 S3 vcount, +12 footer, +16 mcdir v2 empty-dir counts).
4× state: 53,898,057 (+2 SSAA/hires header values, same as SS1's +2).
Saves defer once at t1720/t2000 (`gs: GS backend transfer active`,
then saved); no `gs-transfer` deferral seen (none live at those ticks).
Save writes 39 sections; load reports 38 (trailer section is
save-side-only — identical on both hosts).

### Cross-run state bytes (same binary, same tick)

Two t2000 saves differ in 2 of 39 sections only (section-table diff,
`/tmp/ss3-sectdiff.py`; tail parse `/tmp/ss3-taildiff.py`):

- `scheduler` (14 B): host-deadline rebase ns deltas (wall clock by
  SS1 design, "rebased on load").
- `gs` v3 tail (~984 KB): CLUT ring stale-slot arrangement + monotonic
  slot cursors (977 vs 1011, all four equal); current-palette DATA
  proven identical (slot-1011-old == slot-977-new, 1024/1024 B).
  Pre-existing ring behaviour (v2 saved the same ring + base/next);
  round trips prove it harmless.

37/39 sections — memory, kernel, vu0/1, snd, mcdir, syscalls — are
byte-identical. States were never required to be byte-stable across
runs; loads are proven behaviourally exact.

## New state keys

Mac store (`~/dev/ssx3-work/baselines/states/`):

- `5d5c382-fr1r1-t1720-parallel-1x-c911276d` (race start, HUD t1714)
- `5d5c382-fr1r1-t2000-parallel-1x-1930d9bd` (in race, acceptance tick)

Bradflix store (`~/dev/ssx3-work/baselines-bradflix/states/`, `--store`
flag; same keys — guest pins are host-independent, but cross-STL loads
refuse by design per SS2 B6, so each host needs its own file):

- `5d5c382-fr1r1-t1720-parallel-1x-c911276d` (bradflix-saved)
- `5d5c382-fr1r1-t2000-parallel-1x-1930d9bd` (bradflix-saved)

Pins: `local/research/SS3/pins-state-ss3-fr1r1-1x-mac.json` (key pins:
fork `5d5c382`, pgs `1b3a294`, vu1_images `d28e3fc6…` (current canonical
— F5's `17335933…` predates the VU1 regen), route fr1r1, parallel 1×;
saver: fork `f0d2d3c`, pgs `3d72467`, runner `0339265d…`) and
`…-bradflix.json` (same keys; saver runner `ad02d821…`). State header
`runner_sha` matches the saver on both hosts; `eeCycle` at t2000 is
`9830600296` on both (== a3efbfe manifest: cross-host det parity).
Fetch: `baseline.py get-state <key>` (Mac) /
`baseline.py --store ~/dev/ssx3-work/baselines-bradflix get-state <key>`
(bradflix file; `--load` syncs it for `--host bradflix` boots).

## Commits

Fork `ss3` (from `fork/ssx3` `5d5c382`, unpushed):

- `6e8457b` [SS3] S2
- `25d53b3` [SS3] S3
- `26f3f1f` [SS3] S4
- `f0d2d3c` [SS3] S5 (`f0d2d3cca77d08ecf375682cc3e4f889ef91bf9f`)

paraLLEl `ss3-clut` (from `origin/ssx3` `1b3a294`, unpushed):

- `af87a1a` [SS3] S2 6-arg CLUT overloads
- `18d156a` [SS3] S3 transfer-idle + vertex accessors,
  `PARALLEL_GS_HAS_SAVESTATE_V3`
- `3d72467` [SS3] fixup: `#include <cstring>` for `std::memcpy`
  (libstdc++; `3d72467033ce6c4a8c7319e567880578aca39f6b`)

Fold notes (for the orchestrator, not this commit): this `[SS3]` commit
does NOT move `bradflix_build.sh` `PGS_PIN` — the tip is unpushed and
the script clones from GitHub, so moving it now would break every
lane's bradflix build. The FOLD moves `PGS_PIN` to `3d72467…` after
pushing paraLLEl `ss3-clut`, together with the canonical
`~/dev/ssx3-work/parallel-gs-ssx3` checkout and the fork push.
Bradflix already holds verified `pgs-3d72467033ce` (HEAD, Granite
`166ba21a…`, 29 submodules); it is SHA-addressed, so it stays valid
after the push (identical content). PS2Recomp builds against old
paraLLEl still compile (ifdef'd v2 behaviour) but silently lack the
S2/S3 fixes — the fold must move the pin and the checkout together.

## Gaps

- S2 "forgot latest" is masked by flush normalization in the test (all
  four cursors collapse to one value); covered by review, not by an
  assertion.
- No boot has yet shown a live `gs-transfer` deferral (none live at the
  t1720/t2000 save ticks); the deferral path is unit-tested only.
- 4× all-frame present equality is not established (pre-existing host
  present-timing behaviour; SS1's criterion — det-hash + dump ticks —
  holds).
- S5's Android behaviour (lib path, strict refusal) is compile-verified
  only (no device per brief).
- Mac↔bradflix loads still refuse (SS2 B6 cross-STL rule, by design);
  hence the per-host stores above.

## Exact commands

Setup: `git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/SS3/PS2Recomp
-b ss3 5d5c382` (+ paraLLEl worktree `-b ss3-clut 1b3a294`).

Builds (4/8): `local/tooling/build/mac_build.sh
~/dev/ssx3-work/SS3/PS2Recomp ~/dev/ssx3-work/SS3/build-det --det --pgs
~/dev/ssx3-work/SS3/parallel-gs` (×1; later relinks incremental —
CMakeCache 03:48, binaries 05:29);
`local/tooling/build/bradflix_build.sh f0d2d3c SS3-det2 --det --pgs-pin
3d72467033ce6c4a8c7319e567880578aca39f6b` (+ failed `SS3-det`, the
libstdc++ `<cstring>` build that motivated `3d72467`; the PGS tip
reached bradflix as a bundle into SHA-addressed `pgs-3d72467033ce`,
SS2-recipe); Android `/home/brad/ss3/build.sh assembleRelease` on
bytesize (×1). Incremental `cmake --build` test rebuilds excluded per
SS2 precedent.

Suites: `cd ~/dev/ssx3-work/SS3/PS2Recomp &&
../build-det/ps2xTest/ps2x_tests` → 689/689 (CWD matters: from
`build-det/` the VU0-macro test fails reading `instructions.h`);
`ssh bradflix 'docker run --rm --user 1000:1000 -w /work/PS2Recomp -v
~/dev/ssx3-work/HS1:/work ssx3-hs1 /work/SS3-det2/ps2xTest/ps2x_tests'`
→ 689/689.

Boots (19 total, each < 600 s; 7 final-tip; Mac runner
`…/SS3/build-det/ps2xRuntime/ps2EntryRunner`, bradflix runner
`dev/ssx3-work/HS1/SS3-det2/ps2xRuntime/ps2EntryRunner`):

- `ssx3_boot.py --mode det --backend parallel --runner R --label
  ss3-f-det --out …/run-f-det --save-at 2000 --save-path
  …/ss3-t2000-final.state` (det + t2000 seed)
- `… --label ss3-f-straight --out …/run-f-straight --stop-tick 2600
  --coverage-tick 2600 --dump-ticks 2100,2300,2600 --save-at 1720
  --save-path …/ss3-t1720-final.state` (straight + t1720 seed)
- `… --label ss3-f-load --out …/run-f-load --stop-tick 2600
  --coverage-tick 2600 --dump-ticks 2100,2300,2600 --load
  …/ss3-t2000-final.state --strict`
- bradflix mirrors with `--host bradflix` (`ss3-f-b1`: straight2600 +
  save 1720; `ss3-f-b2`: straight2600 + save 2000; `ss3-f-b3`: strict
  load → 2600; `--save-path` basenames pulled back to the run dir)
- `… --label ss3-f-refuse --stop-tick 2010 --load <a3efbfe t2000>` →
  `section gs version 2 != 3`, 1.0 s

Compares: `baseline.py compare --key
a3efbfe-det-fr1r1-t2400-snd1-1x-a5f2f32d --cand …/run-f-det` →
IDENTICAL; `local/research/SS1/ss1_hashdiff.py --base …/run-f-straight
--cand …/run-f-load --from 2001 --to 2600` (and the `run-f-b2`/`run-f-b3`
pair) → IDENTICAL; `[frame:dump]` FNV lines + `snd.log` guest-counter
lines diffed on common ticks (11/11 Mac, 10/10 bradflix).

Seeds: `baseline.py put-state --state …/ss3-t{1720,2000}-final.state
--pins local/research/SS3/pins-state-ss3-fr1r1-1x-mac.json --tick T`
(mac keys above); same with `--store ~/dev/ssx3-work/baselines-bradflix`
and `…-bradflix.json` for `run-f-b1/ss3-t1720-bf.state` /
`run-f-b2/ss3-t2000-bf.state`.

Checks: `git diff --stat 5d5c382 ss3 -- ps2xRuntime/src/runner` (empty)
and `git diff --stat 14b1e5cb ss3 -- ps2xRuntime/src/runner` (empty);
`strings libps2EntryRunner.so | grep -c proc/self/exe` (SS3 .so: 1, F6
.so: 1); section probes in `/tmp/ss3-sectdiff.py`, `/tmp/ss3-taildiff.py`
(throwaway, not committed).

## Budget

Builds 4/8 (1 Mac + 2 bradflix + 1 Android). Boots 19 (12 Mac
pre-compaction incl. 4× pairs + SS2-runner controls, 4 Mac + 3 bradflix
final-tip). Scratch: `~/dev/ssx3-work/SS3` (~2 GB incl. build dir;
states 6×54 MB + 4 seeds), `~/dev/ssx3-work/baselines-bradflix`
(108 MB, 2 states), bradflix `HS1/SS3-det2` + `pgs-3d72467033ce`
(shared, SHA-addressed).
