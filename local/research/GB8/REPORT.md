# GB8 Part 1 — paraLLEl-GS as the Mac's standard backend: speed, determinism, parity

Worker: Muse Code, brief `local/muse/prompts/GB8.md` Part 1 only. Mac only, no
source changes (none needed; no flags missing).

## Pins and inputs

| Item | Pin | Receipt |
| --- | --- | --- |
| Fork `~/dev/PS2Recomp` (read-only source, clean) | `ssx3` `f949ff060d9a0c53f3ab47998068b771f20653e3` | `git log -1`, empty `status --porcelain` before build |
| paraLLEl-GS `~/dev/parallel-gs` (clean) | `ssx3` `963cb57503245e31efb2df89a4740cd4da66513b` | `git log -1`, empty `status --porcelain` |
| Granite submodule of the above | `166ba21a247a681903cc9d0bb6562fe50a554c85` | `git submodule status` |
| Canonical codegen | `register_functions.cpp` SHA-256 `8ea8ed43…e662d688a3` (×2, matches E54F2) | boot-driver precheck reads |
| Stock ISO / ELF | `3c2f8eb1…ae3f5` / `1b49d05c…67af7bc` (×2 per boot) | boot-driver precheck reads |
| Route | I26-FAST (`local/research/I26/ROUTES.md`), race HUD ~t1714 | `ROUTE` in `gb8_boot.py` |
| Base note | fork `ssx3` moved to `71c952e` (I32) mid-task; GB8 stays on `f949ff0` per orchestrator FYI | — |

Runners (both from one build dir, `~/dev/ssx3-work/GB8/build`, Release, Homebrew
clang, `PS2X_GS_SHADOW_PARALLEL=ON`, `BUILD_TEST=OFF`, `BUILD_STUDIO=OFF`,
`DEBUG_UI=OFF`, runtime/aggressive logs OFF, diag taps OFF):

| Runner | Det-hash tap | SHA-256 (two matching reads) |
| --- | --- | --- |
| `bin/runner-clean` (Build 1, speed) | OFF (`det-hash:v1` absent from strings) | `1882e36e…d7f3c34` |
| `bin/runner-det` (Build 2, reconfigure + rebuild) | ON (string present) | `72a0d1d0…05ddef4` |

Build 2 was an incremental reconfigure (`cmake -S … -B build
-DPS2X_ENABLE_DET_HASH_TAP=ON`, 353 steps) after copying Build 1's runner out;
first reconfigure attempt failed with rc=1 (`cmake -B build` without `-S`
looks for CMakeLists in the cwd — no build consumed, cache untouched) and was
retried with `-S`. Build logs: `configure-clean.log`, `build-clean.log`,
`configure-det.log`, `build-det.log` in scratch. GB8 tree 1.9 GB (< 10 GB).

Backend selection: `PS2X_GS_BACKEND=parallel` + `GRANITE_VULKAN_LIBRARY=
/opt/homebrew/lib/libvulkan.1.dylib` (GB6/TL1 recipe); CPU = var unset, same
binary. All boots: `PS2X_SKIP_MOVIE=1` (dev-only), `PS2X_DETERMINISTIC=1`,
vsync pad clock, empty mc0/mc1, own cwd, own PID, wall 500 s / progress 120 s /
log 16 MiB caps. `[gs-path]` on parallel boots: `hier_rule=flat-always …
desc=plain … gpu=Apple M5 Pro` (matches the TL1 baseline; Mac ≠ Odin binning
noted, unchanged). No `[gs:parallel] FATAL` in any boot.

## Q2 determinism — CPU vs parallel: IDENTICAL; parallel repeats exactly

Det-hash build, `PS2X_DET_HASH_EVERY=1`, to t2400, one slot each (E57-style
`[det-hash:v1]` gate, no GS capture):

| Boot | Label | Ticks 1..2400 | vs |
| --- | --- | --- |
| det-cpu vs det-parallel | `det-cpu`, `det-parallel` | IDENTICAL, 0 missing, first_diff=None | CPU backend |
| det-parallel vs det-parallel2 | `det-parallel`, `det-parallel2` | IDENTICAL, 0 missing, first_diff=None | repeatability |

Det-hash streams are exactly ticks 1..N consecutive, no duplicate ticks
(N = 2416/2431/2429 — boots ran a few ticks past 2400 during poll/settle).
The guest never reads GS memory back in any guest-visible way on this route:
EE/RDRAM/scratch/VU1 state is bit-identical whether the GS rasterizer is CPU
or paraLLEl. (Full lines: `run/det-*/boot.log` in scratch.)

## Q3 parity — same scenes; pervasive small shading diffs; race visually identical

Frames are 0.5 s snapshotter copies of `upload-latest.png` from the Q2 boots,
selected by exact present tick from the `.txt` sidecar (closest to target).
512×448 throughout. I viewed all 7 pairs; pixel stats from `gb8_pngdiff.py`
(stdlib PNG decoder, self-diff 1.0000).

| Screen | CPU tick | Par tick | Viewed verdict |
| --- | --- | --- | --- |
| Title (~600) | 598 | 587 | Same layout; parallel small text marginally rougher (mild; far less severe than the GB5C tick-300 damage) |
| Main Menu (~750) | 748 | 750 | Same; parallel menu glyphs slightly less crisp, all legible |
| Select Peak (~1090) | 1090 | 1094 | Same phase (both pre-press); parallel text slightly fuzzier |
| Select Event (target 1180*) | 1190 | 1193 | Same; parallel bottom hint text slightly rougher |
| Race 1810 | 1811 | 1811 | No visible difference (Δ0) |
| Race 2100 | 2100 | 2102 | Identical except trick counter 210 vs 250 — a 2-tick animation delta, not a backend difference |
| Race 2400 | 2401 | 2401 | No visible difference (Δ0) |

\* The 1180 target lands post-transition: the tick-1185 press advances Select
Mode → Select Event within ~5 ticks, so both frames show Select Event
(Snow Jam highlighted), same phase, Δ3.

Pixel stats (CPU vs parallel; all pairs differ — no pixel-identical pair):

| Pair | Δtick | equal_px | within±2 | within±8 | meanabs | maxdiff |
| --- | --- | --- | --- | --- | --- | --- |
| Title | 11 | 0.2370 | 0.5972 | 0.7358 | 12.94 | 254 |
| MainMenu | 2 | 0.3202 | 0.7512 | 0.8346 | 12.42 | 254 |
| SelPeak | 4 | 0.3898 | 0.6516 | 0.7060 | 19.69 | 254 |
| SelEvent | 3 | 0.4966 | 0.7915 | 0.8353 | 13.51 | 254 |
| Race1810 | 0 | 0.6726 | 0.7797 | 0.8520 | 8.51 | 255 |
| Race2100 | 2 | 0.5491 | 0.7149 | 0.8251 | 9.09 | 255 |
| Race2400 | 0 | 0.6758 | 0.7883 | 0.8827 | 6.36 | 255 |

Controls and ruling-out (all in scratch logs, this section's receipts):
- Same file vs itself: 1.0000/1.0000 (decoder validated).
- Same backend + same tick across runs (parallel vs parallel2): tick 2396 =
  1.0000 pixel-identical; tick 1293 = 0.9967; tick 2286 = 0.9053. Present
  content at a fixed vsync tick is *almost* deterministic; the 2286 outlier
  (≈9.5 % on a race frame) is present-phase noise (which guest frame the
  host present picks up), far smaller than the 33 % CPU-vs-parallel race
  diffs.
- Best-match search: CPU race-1811 vs parallel snaps at ticks
  1800/1806/1811/1817/1822 — the Δ0 pair scores best (0.6726), neighbors
  worse. No phase artifact inflates the race numbers.
- 1-px shift test on the Title pair: (0,0) 0.2370 vs (1,0) 0.2289, (−1,0)
  0.2481, (0,1) 0.2024, (0,−1) 0.2930 — no alignment artifact.
- Title diff histogram: 72 % of pixels within 7, then a long tail; pixels
  with diff > 32 are 9.9 %, spread over all rows 0–447 (scattered text/logo
  edges + shading noise, not one wrong region).

Reading: the CPU and paraLLEl rasterizers shade the same scenes with
systematic small-amplitude differences (rounding/dither on gradients,
crisper CPU text edges) — visually negligible in the race, mild glyph
softness in menus. The known large dark terrain region and the missing
sky/sun render **identically on both backends** (present in both race
frames) — they are not paraLLEl-vs-CPU differences. No stripes, no black
tiles, no missing HUD on either backend at these ticks.

Frame paths (scratch, orchestrator-viewable):
`~/dev/ssx3-work/GB8/run/det-{cpu,parallel}/frames/snap/` —
Title `snap-000588t-0023.44s` / `snap-000587t-0010.19s`,
MainMenu `snap-000736t-0030.04s` / `snap-000749t-0012.72s`,
SelPeak `snap-001081t-0048.82s` / `snap-001093t-0021.84s`,
SelEvent `snap-001180t-0053.38s` / `snap-001193t-0023.36s`,
Race1810 `snap-001809t-0103.13s` / `snap-001806t-0048.26s`,
Race2100 `snap-002098t-0149.30s` / `snap-002097t-0073.64s`,
Race2400 `snap-002401t-0213.83s` / `snap-002396t-0100.50s` (.png + .txt each).

## Q1 speed — parallel 1.7–2.3× faster in every phase (Mac mini M5 Pro)

Clean build (`runner-clean`, diagnostics compiled out), I26-FAST to t2400,
same binary both backends, exclusive lease (all 4 slots), quiet host (load
1.4 at claim, no other runner/build; `run/speedpair-ps-at-claim.txt`).
`speed-parallel` then `speed-cpu2` back-to-back under one contiguous hold
(`gb8_watch.py`), 90.4 s + 160.5 s wall. Per-phase guest vsyncs/s ÷ 59.94
from the 0.5 s (wall, tick) trace by interpolation at phase boundaries
(`gb8_rates.py`; trace is authoritative — raw 5 s means smear at phase
edges, e.g. parallel title raw n=2 mean 59.9 vs trace 43.0 from one fast
early sample). **Mini numbers; not comparable to laptop or Odin.**

| Phase (ticks) | CPU vs/s (×) | Parallel vs/s (×) | Parallel ÷ CPU |
| --- | --- | --- | --- |
| Title [0,636) | 31.27 (0.522×) | 43.00 (0.717×) | 1.37× |
| Menus [636,1440) | 23.20 (0.387×) | 52.54 (0.877×) | 2.26× |
| Loading [1440,1714) | 13.60 (0.227×) | 27.05 (0.451×) | 1.99× |
| Race-start [1714,1800] | 8.40 (0.140×) | 16.46 (0.275×) | 1.96× |
| **Race (1800,2400]** | **8.02 (0.134×)** | **13.43 (0.224×)** | **1.67×** |
| Wall launch → race HUD (~t1714) | 75.1 s | 40.2 s | 1.87× |
| Wall launch → t2400 | 160.5 s | 90.4 s | 1.78× |

Raw 5 s `[vsync-rate]` cross-check (race window): CPU n=15 mean 7.98,
parallel n=9 mean 13.51 — agrees with trace (8.02 / 13.43). One run per
backend (brief budget); no drift cancellation — treat the second decimal as
noise. Sync shader compiles on the parallel boot: 4 stalls, 106 ms total
(0.1 % of the boot) — no cold-start concern on this Mac.

An early `speed-cpu` boot ran under foreign load (two other lanes' runners
alive at launch, load 11.8→6.0) and is diagnostic-only, excluded above;
`speed-cpu2` is the clean rerun. Det-boot walls (diagnostic, frame-dump
overhead, not speed numbers) tell the same story: det-cpu 216.8 s vs
det-parallel 103.6 s / parallel2 100.0 s to t2400.

## Q4 host cost — GameThread stays saturated; GPU path adds ~6 % on one thread

`ps -M` every 10 s in the race (tick ≥ 1750) on the quiet speed boots.
macOS `ps -M` prints no thread names; attribution by elimination (the ~100 %
thread on CPU is GameThread — E57: all busy samples on the one game thread
with the CPU rasterizer). A libproc-ctypes named-thread prober was attempted
and dropped (`PROC_PIDLISTTHREADS` entries are not plain uint64 tids — ESRCH
on query; script deleted, not committed).

| Boot | Samples | Hottest thread | 2nd thread | Rest | Threads |
| --- | --- | --- | --- | --- | --- |
| speed-cpu2 | 9 | 97.9–100.0 % | ≤ 0.1 % | ~0 | 6–7 |
| speed-parallel | 5 | 98.8–100.0 % | 5.7–5.9 % | ≤ 0.4 % | 8–9 |

GameThread does **not** drop below saturation on parallel — it stays ~99 %,
but each guest tick costs less (no CPU rasterization), hence the 1.67× race
rate. The bottleneck remains the one game thread (now VU1-heavy, per E57's
offload reasoning: GS was 47–60 % of GameThread; Amdahl leaves VU1 + rest).
The GPU worker path (GsWorker/Granite submission) uses ~6 % of one core; the
raster work itself is on the Apple GPU (invisible to CPU %). Process totals:
~100 % (CPU) vs ~106 % (parallel). Fewer parallel samples (5 vs 9) because
its race window is shorter in wall time. Full samples: `run/speed-*/ps-race-*.txt`.

## Recommendation (orchestrator decides)

Switch the Mac default to paraLLEl via **env in boot tooling**
(`PS2X_GS_BACKEND=parallel` + `GRANITE_VULKAN_LIBRARY` in the shared boot
drivers), not a build default. Reasons: 1.7–2.3× faster in every phase with
zero guest-state change (Q2 bit-identical) and race frames visually
identical (Q3); env keeps CPU as the no-GPU fallback and lets any lane opt
out with one variable; no fork edit or rebuild needed anywhere. Do not flip
the CMake default: the build must keep working where Vulkan is absent, and
the Odin already selects its backend explicitly (unaffected either way).
Caveats to carry: (1) the Mac runs `hier_rule=flat-always` + `desc=plain`
while the Odin uses hierarchical binning at wave64 + descriptor buffers —
Mac boots do not cover binning-path bugs; (2) menu glyphs are mildly softer
on parallel (and worse at other ticks per GB5C/GB7C7P2 — the glyph-producer
hunt continues regardless of default); (3) one run per backend — rerun the
race window if a second decimal matters.

## Exact commands

```sh
# Build 1 (clean) — from ~/dev/ssx3-work/GB8
cmake -S ~/dev/PS2Recomp -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm/bin/clang \
  -DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm/bin/clang++ \
  -DPS2X_GAME_CODEGEN_DIR=/Users/brad/dev/ssx3-work/codegen-ssx3 \
  -DPS2X_BUILD_TEST=OFF -DPS2X_BUILD_STUDIO=OFF -DPS2X_ENABLE_DEBUG_UI=OFF \
  -DPS2X_ENABLE_RUNTIME_LOGS=OFF -DPS2X_ENABLE_AGRESSIVE_LOGS=OFF \
  -DPS2X_ENABLE_DIAG_TAPS=OFF -DPS2X_ENABLE_DET_HASH_TAP=OFF \
  -DPS2X_GS_SHADOW_PARALLEL=ON \
  -DPS2X_PARALLEL_GS_SOURCE_DIR=/Users/brad/dev/parallel-gs \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON            # configure-clean.log, rc=0
cmake --build build --parallel 8 --target ps2EntryRunner   # build-clean.log, rc=0 (455 steps)
cp build/ps2xRuntime/ps2EntryRunner bin/runner-clean
# Build 2 (det-hash): same dir, copy-out first, then
cmake -S ~/dev/PS2Recomp -B build -DPS2X_ENABLE_DET_HASH_TAP=ON  # configure-det.log, rc=0
cmake --build build --parallel 8 --target ps2EntryRunner        # build-det.log, rc=0 (353 steps)
cp build/ps2xRuntime/ps2EntryRunner bin/runner-det
# Boots (all: gb8_boot.py --stop-tick 2400; det = one slot, speed = exclusive)
python3 gb8_boot.py --mode det --backend cpu --runner bin/runner-det --label det-cpu
python3 gb8_boot.py --mode det --backend parallel --runner bin/runner-det --label det-parallel
python3 gb8_boot.py --mode det --backend parallel --runner bin/runner-det --label det-parallel2
python3 gb8_boot.py --mode speed --backend cpu --runner bin/runner-clean --label speed-cpu  # loaded, diagnostic
python3 gb8_watch.py 1500   # quiet window -> speed-parallel + speed-cpu2 back-to-back, one hold
# Analysis
python3 gb8_hashdiff.py --base run/det-cpu --cand run/det-parallel
python3 gb8_hashdiff.py --base run/det-parallel --cand run/det-parallel2
python3 gb8_rates.py run/speed-cpu2 run/speed-parallel
python3 gb8_pngdiff.py A.png B.png   # per pair; Title shift/histogram/best-match were one-offs in shell
```

Scripts committed here: `gb8_boot.py` (bounded driver: speed/det × cpu/parallel,
snapshotter, ps sampling, tick trace, held-slot support), `gb8_watch.py`
(quiet-window trigger + contiguous exclusive hold), `gb8_rates.py`
(per-phase rates), `gb8_hashdiff.py` (det-hash gate), `gb8_pngdiff.py`
(stdlib PNG differ). Scratch: `~/dev/ssx3-work/GB8/` (build, bin, run,
`*.log`, 2.0 GB).

## Budgets and gaps

Builds 2/2, boots 6/6 (3 det + 3 speed), each ≤ 500 s wall, ~80 min of the
2 h box. Host contention handled: builds ran `nice -n 10 -j8` during other
lanes' diagnostic boots only (no build during E57's speed session); speed
pair waited for a verified-quiet exclusive window. Gaps stated plainly: one
speed run per backend (no drift cancellation); thread attribution by
elimination (no macOS thread names from `ps`); the tick-1185 press means no
Select Mode frame was captured (Select Event instead, same phase both
backends); det boots carry frame-dump overhead (excluded from speed);
`speed-cpu` (loaded) excluded from Q1/Q4; present-phase noise (≤ ~10 % on
one control) bounds pixel-diff precision.

## Orchestrator gate (2026-09-25)

**Pass; adopt paraLLEl as the Mac default via env in boot tooling** (`PS2X_GS_BACKEND=parallel`,
`GRANITE_VULKAN_LIBRARY=/opt/homebrew/lib/libvulkan.1.dylib`, builds with
`PS2X_GS_SHADOW_PARALLEL=ON`). Det-hash CPU vs parallel identical (the guest never reads GS back),
parallel repeats exactly; launch → race HUD 75.1 s → 40.2 s; race 0.134× → 0.224×. The CPU backend
stays available for reference A/B. GB9 (align the Mac paths with the Odin) is next in the G lane.
