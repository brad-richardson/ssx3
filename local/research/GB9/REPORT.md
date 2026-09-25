# GB9 Part 1 — Mac takes the Odin's binning path (report)

Worker: Muse Code, brief `local/muse/prompts/GB9.md`. Mac only. Fable review
§4 knob 1: `PGS_HIER_BINNING=force|auto|off` on the Mac; knob 2 (Odin
descriptor path) waits for the Odin.

**Verdict: force works.** Hierarchical binning engages heavily on
M5/MoltenVK and produces bit-identical output to flat binning on the
N8X1/TL1 race stream. The "broken Metal drivers" comment does not hold on
this hardware/driver for this stream.

## Pins and inputs

| Item | Pin | Receipt |
| --- | --- | --- |
| paraLLEl-GS worktree `~/dev/ssx3-work/GB9/parallel-gs`, branch `gb9-hier` | `963cb57` + knob `19d93b2d0bb0172c2ab4c057de4adbd6ed566eba` + local-only probe `63cd7de7268f0388d409f4ae4bca7dccdc64be2e` | `git log`, below |
| Granite submodule in that worktree | `166ba21a247a681903cc9d0bb6562fe50a554c85` (matches pin) | `submodule status` |
| PS2Recomp worktree `~/dev/ssx3-work/GB9/PS2Recomp`, branch `gb9-gs-path` | `56a5e8a` + local-only logger `5706858db4145f1ea84cf3bfd4ae338255023cdc` | `git log`, below |
| Stream `~/dev/ssx3-work/N8D7M6/n8d7m6.gs` | SHA `f6a78f71…a593` ×2, 1100696462 B (matches TL1 pin) | two `shasum` reads |
| Codegen / ISO / ELF | `8ea8ed43…e662d688a3` / `3c2f8eb1…ae3f5` / `1b49d05c…67af7bc` (boot-driver precheck, two reads) | `run/det-force/result.json` |
| `ps2x_tests` (build-tests, TL1 flags) | SHA `8d2dfa52…89cbbb8` ×2 (pre-probe binary; probe rebuild re-verified rows equal) | two `shasum` reads |
| `ps2EntryRunner` det (build-run, GB8/F1 flags + tap) | SHA `ac40cbc2…271716eb0` ×2 | two `shasum` reads |

Nothing pushed (either fork). Runner-dir check:
`git diff --stat 14b1e5cb gb9-gs-path -- ps2xRuntime/src/runner` is empty.

## Knob diff (parallel-gs fork, branch `gb9-hier`)

Commit `19d93b2` (2 files, +55/−1; the shippable diff):

- New `gs/pgs_env_knobs.hpp`: `pgs_hier_binning_mode()` parses
  `PGS_HIER_BINNING` (`force` / `off`, everything else incl. unset and
  `auto` = `Auto` = today's platform behavior); single source of truth
  shared by the renderer and the `[gs-path]` logger.
- `gs/gs_renderer.cpp` `get_target_hierarchical_binning`: `off` returns 1
  (flat everywhere); on Apple the early return is skipped only for `force`,
  which then runs the standard hier-if-large rule (≥256 prims, >4×4 tiles,
  target 2/4 clamped by `maxComputeWorkGroupInvocations`) — exactly the
  Odin's rule. Unset/auto = today's behavior on every platform.

PS2Recomp side, commit `5706858` (1 file, +13/−12, local-only): `logGpuPath`
includes `pgs_env_knobs.hpp` (resolves via the `parallel-gs` target's PUBLIC
`gs/` include dir) and prints the effective rule at runtime instead of the
`#ifdef __APPLE__` constant. This commit is why the build is "56a5e8a + 1
print-only commit" rather than bare 56a5e8a: `[gs-path]` hardcodes
`flat-always` on Apple at that pin, so the brief's "`[gs-path]` must print
the effective rule" is unsatisfiable without it. Zero guest effect (print
only; the det-hash gate below confirms it).

Local-only probe, commit `63cd7de` (+42, do not push): `PGS_HIER_PROBE=1`
counts hier-target (>1) passes — first-occurrence line with parameters plus
a line every 4096 passes. (A destructor summary was tried first; `ps2x_tests`
exits via `std::_Exit`, so it never prints there. Kept for normal-exit
processes.)

## `[gs-path]` lines (effective rule printed)

Unset (byte-identical to the TL1 baseline line):

```text
[gs-path] hier_rule=flat-always hier_t2=1 hier_t4=1 subgroup_flat=free-4..128 subgroup_hier=free-4..128 vk11_subgroup=32 max_wg_inv=1024 desc=plain desc_req=push+heap+buffer sampler_feedback=on feedback_rt=off gpu=Apple M5 Pro
```

`PGS_HIER_BINNING=force` (t2/t4 match the Odin's 2/4):

```text
[gs-path] hier_rule=hier-if-large hier_t2=2 hier_t4=4 subgroup_flat=free-4..128 subgroup_hier=free-4..128 vk11_subgroup=32 max_wg_inv=1024 desc=plain desc_req=push+heap+buffer sampler_feedback=on feedback_rt=off gpu=Apple M5 Pro
```

`off` and `auto` both print the `flat-always` line.

## Replays: `n8d7m6.gs` through `ps2x_tests` (no boots, no lease)

TL1 Part 1b recipe (`STEP=50`, `PPM_TICKS=2050`, `PKTSEQ=1`,
MoltenVK loader), workdir = PS2Recomp worktree. All runs rc=0, 41
GB4_REPLAY rows each, zero FATAL.

| Run | `[gs-path]` rule | Rows vs unset | tick-2050 row | tick-2050 PPM SHA |
| --- | --- | --- | --- | --- |
| unset (= today's behavior) | flat-always | — (`cmp`-clean vs TL1's `replay-1b/parallel.hashes`) | `vram=c883a705 priv=6621fe06 present=d19b96fe` | `9490484c…` (= TL1 Mac ON pin) |
| force | hier-if-large t2=2 t4=4 | 41/41 equal (`diff` rc=0, no first differing tick) | identical | `9490484c…` (identical file) |
| off | flat-always | 41/41 equal | identical | `9490484c…` |
| auto | flat-always | 41/41 equal | identical | `9490484c…` |

Hier engagement (probe, force replay): first hier pass `target=2 prims=371
tiles=32x28`; `hier_passes=4096 max_target=4` (≥4096 hier passes incl.
target-4). So the equality above is "hier engaged and correct", not "hier
never engaged".

Frame viewed: `replay-force/frames/vq-002050.png` (converted from the PPM):
race 00:00:05, 2ND/2, rider, snow/terrain, EA Radio card — the same race
frame TL1 describes, no black tiles, no corruption. (The unset PPM is the
identical file, so one view covers both. The dark lower region is the known
rendering gap, present in both.)

## Live det boot with force (one slot, to t2400)

`gb9_boot.py --mode det --backend parallel --runner
build-run/ps2xRuntime/ps2EntryRunner --label det-force --stop-tick 2400`
(F1 driver + `PGS_HIER_BINNING=force`, `PGS_HIER_PROBE=1`; else F1-B1-identical
env incl. `PS2X_SOUND=1`): bound=target, 84.3 s wall, last_tick 2402, HUD at
35.1 s wall, zero FATAL, slot released. `cid0 = 531` (matches F1/AU9/PCSX2).
Probe on the live route: same first hier pass; `hier_passes=8192
max_target=4` (≥8192 hier passes). Host load 11 at launch (another lane
busy) — noted, not a speed boot, no speed quoted.

Det-hash vs F1 B1 (`~/dev/ssx3-work/F1/run/B1/boot.log`, 56a5e8a,
knob unset): **ticks 1..2450 byte-identical, all fields** (glue-immune
extract+sort+`cmp`). Base runs 3 ticks further (2451–2453, settle overrun —
the documented GB8 run-to-run variance). Note: `gb8_hashdiff.py` reports
DIFFER with `first_diff=None` because one det line per log is glued to a
`[frame:dump]` line (missing newline between threads) and its parser is
line-anchored; both glued lines verified byte-identical by field extract.
The backend cannot change guest state: confirmed on the folded tip.

Frames viewed (`run/det-force/frames/snap/`): race tick 2100
(`snap-002100t-0061.48s.png`: rider, spray, mountains, pines, checkpoint
beam, HUD 2ND/2 00:00:06 1 %, trick 210, EA Radio) and title tick 614
(SSX 3 logo, Press START, © 2003 EA) — both healthy, no tiles/stripes/
corruption.

## Exact commands

```sh
# Worktrees (never push either)
git -C ~/dev/parallel-gs worktree add ~/dev/ssx3-work/GB9/parallel-gs 963cb57
git -C ~/dev/ssx3-work/GB9/parallel-gs checkout -b gb9-hier
git -C ~/dev/ssx3-work/GB9/parallel-gs submodule update --init --recursive Granite
git -C ~/dev/PS2Recomp worktree add ~/dev/ssx3-work/GB9/PS2Recomp 56a5e8a
git -C ~/dev/ssx3-work/GB9/PS2Recomp checkout -b gb9-gs-path
# Build 1: ps2x_tests (TL1 flags; PS2X_PARALLEL_GS_SOURCE_DIR = knob worktree)
cmake -S .../GB9/PS2Recomp -B .../GB9/build-tests -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DPS2X_BUILD_TEST=ON -DPS2X_ENABLE_DIAG_TAPS=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON -DPS2X_PARALLEL_GS_SOURCE_DIR=.../GB9/parallel-gs \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3
cmake --build build-tests --parallel 8 --target ps2x_tests   # rc=0 (327 steps)
# Replays (workdir = PS2Recomp worktree; PGS_HIER_BINNING=force|off|auto|unset)
PGS_HIER_BINNING=<v> PS2X_GS_REPLAY_CAPTURE=.../N8D7M6/n8d7m6.gs PS2X_GS_REPLAY_BACKEND=parallel \
PS2X_GS_REPLAY_STEP=50 PS2X_GS_REPLAY_PPM_TICKS=2050 PS2X_GS_REPLAY_PPM_DIR=.../replay-<v>/frames \
PS2X_GS_REPLAY_OUT=.../replay-<v>/parallel.hashes PS2X_GS_REPLAY_PKTSEQ=1 \
GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib ../build-tests/ps2xTest/ps2x_tests  # rc=0 ×4
# Build 2: det runner (GB8/F1 flags + DET_HASH_TAP=ON, TEST=OFF)
cmake -S .../GB9/PS2Recomp -B .../GB9/build-run -G Ninja ... -DPS2X_BUILD_TEST=OFF ... \
  -DPS2X_ENABLE_DET_HASH_TAP=ON ...   # configure-run.log, rc=0
cmake --build build-run --parallel 8 --target ps2EntryRunner  # rc=0 (456 steps)
# Live boot (driver claims/releases one slot itself)
python3 gb9_boot.py --mode det --backend parallel --runner build-run/ps2xRuntime/ps2EntryRunner --label det-force --stop-tick 2400
# Gates
cmp TL1/replay-1b/parallel.hashes replay-unset/parallel.hashes  # identical (knob unset = no-op)
diff replay-unset/parallel.hashes replay-force/parallel.hashes   # rc=0, 41/41
python3 local/research/GB8/gb8_hashdiff.py --base .../F1/run/B1 --cand .../GB9/run/det-force  # line-anchored caveat, see above
grep -o '\[det-hash:v1\] tick=[0-9]* .*' ... | sort -t= -k2 -n | cmp  # shared ticks byte-identical
```

Scripts committed here: `gb9_boot.py` (F1 driver + `PGS_HIER_BINNING=force`,
`PGS_HIER_PROBE=1`, `PGS_*` in the recorded env). Scratch
`~/dev/ssx3-work/GB9/` 3.5 GB (≤ 10 GB); ssx3 internal 112.4/200 GB.

## Budgets and gaps

Builds: 2 configures (tests + runner); tests binary incrementally rebuilt
2× for the probe (1 TU + link each). Boots: 1 live det boot (84 s, one
slot). Replays: 5 (unset/force/probe/off/auto), no lease. ~1 h of the 2 h
box. First-failure rule never triggered.

Gaps stated plainly: hier correctness is proven on one stream (the
N8X1/TL1 race stream); no menu/title-only replay with force (the live
force boot covers those routes visually only). `off`/`auto` are covered by
replay; unknown knob values fall back to `auto` by code (not run). The
`gb8_hashdiff.py` glued-line caveat above is a tooling note for the next
det gate. The `63cd7de` probe commit is diagnostic scaffolding, not part of
the knob.

## Recommendation (orchestrator decides)

Fold knob `19d93b2` to the paraLLEl fork `ssx3` and the `5706858` logger
line to PS2Recomp fork `ssx3` (drop the probe). Keep the default unset
(flat-always on Apple — no behavior change anywhere); Mac lanes that want
Odin binning-logic coverage boot/replay with `PGS_HIER_BINNING=force`.
Remaining Mac↔Odin gaps for GB9 Part 2 / knob 2: descriptor-buffer path
(Odin-only until `PGS_DESC_PATH`), wave64 vs wave32 subgroups (stays
Odin-only per Fable §4), Turnip CPU/thermals, Adreno bilinear rounding.
